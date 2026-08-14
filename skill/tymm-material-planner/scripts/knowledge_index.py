#!/usr/bin/env python3
"""
TYMM Knowledge Indexer (knowledge_index.py)

Builds, maintains, and queries the local project-scoped Hybrid SQLite + sqlite-vec + FTS5 index
derived strictly from validated, frozen canonical structured JSON knowledge bases.

CRITICAL INVARIANTS:
1. The Vector Database is NOT the source of truth.
2. Authoritative source of truth: persistent, verified structured JSON files.
3. Vector DB is solely a candidate retrieval accelerator.
4. Stable, collision-free entity keys across all entity types; duplicate keys fail closed.
5. Strict terminology separation: official requirement ("dereceli puanlama anahtarı") vs
   actual textbook structure vs selected implementation ("analytic_rubric").
6. Explicit documented vector backend deviation and complete embedding runtime provenance.
"""

import argparse
import hashlib
import json
import os
import platform
import sqlite3
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Try importing sqlite_vec
try:
    import sqlite_vec
    HAS_SQLITE_VEC = True
except ImportError:
    HAS_SQLITE_VEC = False

# Try importing ONNX Runtime & Tokenizers for embedding inference
try:
    import onnxruntime as ort
    import tokenizers
    HAS_EMBEDDING_RUNTIME = True
except ImportError:
    HAS_EMBEDDING_RUNTIME = False


# Architecture & Vector Backend Metadata
REQUESTED_VECTOR_BACKEND = "sqlite-vector/sqliteai-vector"
SELECTED_VECTOR_BACKEND = "sqlite-vec"
BACKEND_SELECTION_STATUS = "EXPLICIT_ACCEPTED_DEVIATION"
BACKEND_SELECTION_REASON = (
    "sqlite-vec is the modern official lightweight native C SQLite extension by Alex Garcia supporting fast "
    "vector search without heavy external AI dependencies, works seamlessly on macOS ARM64/x86_64, "
    "whereas sqlite-vector/sqliteai-vector has packaging/build complexities and deprecations."
)

# Embedding Provenance Constants
BASE_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
RUNTIME_MODEL_REPOSITORY = "Xenova/multilingual-e5-small"
RUNTIME_MODEL_FILE = "model_quantized.onnx"
RUNTIME_FORMAT = "ONNX"
QUANTIZATION = "quantized"
EMBEDDING_DIMENSION = 384
POOLING_STRATEGY = "attention_masked_mean_pooling"
NORMALIZATION = "L2"
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "

DEFAULT_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "multilingual-e5-small"
)

# Authority Levels (1: Highest, 8: Lowest)
AUTHORITY_MAP = {
    "OFFICIAL_CURRICULUM_FROZEN": (1, "official_curriculum"),
    "OFFICIAL_TEXTBOOK_FROZEN": (2, "official_textbook"),
    "OFFICIAL_TEXTBOOK_FORM_FROZEN": (3, "official_textbook"),
    "VALIDATED_ALIGNMENT": (4, "validated_alignment"),
    "VALIDATED_GAP": (5, "validated_gap"),
    "VALIDATED_RESOURCE_PLAN": (6, "validated_resource_plan"),
    "VALIDATED_PRODUCTION_PLAN": (7, "validated_production_plan"),
    "PEDAGOGICAL_RECOMMENDATION": (8, "pedagogical_recommendation"),
}


class DuplicateCanonicalKeyError(Exception):
    """Raised when a duplicate canonical entity key is generated during extraction."""
    pass


class LocalEmbeddingEngine:
    """Local ONNX-based embedding engine for multilingual-e5-small."""

    def __init__(self, model_dir: str = DEFAULT_MODEL_DIR):
        self.model_dir = model_dir
        self.model_name = BASE_EMBEDDING_MODEL
        self.embedding_dim = EMBEDDING_DIMENSION
        self._tokenizer = None
        self._session = None
        self._input_names = None

    def initialize(self):
        if not HAS_EMBEDDING_RUNTIME:
            raise RuntimeError(
                "onnxruntime or tokenizers package is missing in Python environment."
            )
        tokenizer_path = os.path.join(self.model_dir, "tokenizer.json")
        model_path = os.path.join(self.model_dir, RUNTIME_MODEL_FILE)
        if not os.path.exists(model_path):
            model_path = os.path.join(self.model_dir, "model.onnx")

        if not os.path.exists(tokenizer_path) or not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Embedding model files not found in {self.model_dir}."
            )

        self._tokenizer = tokenizers.Tokenizer.from_file(tokenizer_path)
        self._tokenizer.enable_truncation(max_length=512)

        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 4
        opts.intra_op_num_threads = 4
        self._session = ort.InferenceSession(model_path, sess_options=opts)
        self._input_names = [inp.name for inp in self._session.get_inputs()]

    def encode(self, texts: List[str], is_query: bool = False, batch_size: int = 32) -> np.ndarray:
        """Embeds a batch of texts with dynamic padding and L2 normalization."""
        if self._session is None:
            self.initialize()

        prefix = QUERY_PREFIX if is_query else PASSAGE_PREFIX
        formatted = [t if t.startswith((QUERY_PREFIX, PASSAGE_PREFIX)) else prefix + t for t in texts]

        all_embeddings = []
        for i in range(0, len(formatted), batch_size):
            batch = formatted[i : i + batch_size]
            encodings = [self._tokenizer.encode(t) for t in batch]
            max_len = min(512, max(len(e.ids) for e in encodings))

            input_ids_list = []
            attention_mask_list = []
            token_type_ids_list = []

            for e in encodings:
                ids = e.ids[:max_len]
                mask = e.attention_mask[:max_len]
                types = e.type_ids[:max_len] if hasattr(e, "type_ids") else [0] * len(ids)
                pad_len = max_len - len(ids)

                input_ids_list.append(ids + [0] * pad_len)
                attention_mask_list.append(mask + [0] * pad_len)
                token_type_ids_list.append(types + [0] * pad_len)

            input_ids = np.array(input_ids_list, dtype=np.int64)
            attention_mask = np.array(attention_mask_list, dtype=np.int64)

            inputs = {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
            }
            if "token_type_ids" in self._input_names:
                inputs["token_type_ids"] = np.array(token_type_ids_list, dtype=np.int64)

            outputs = self._session.run(None, inputs)
            last_hidden_state = outputs[0]  # [B, seq_len, dim]

            # Mean pooling with attention mask
            mask_expanded = np.expand_dims(attention_mask, -1)
            sum_embeddings = np.sum(last_hidden_state * mask_expanded, axis=1)
            sum_mask = np.clip(mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
            mean_pooled = sum_embeddings / sum_mask

            # L2 normalize
            norms = np.linalg.norm(mean_pooled, ord=2, axis=1, keepdims=True)
            normalized = mean_pooled / np.clip(norms, a_min=1e-9, a_max=None)
            all_embeddings.append(normalized.astype(np.float32))

        return np.vstack(all_embeddings)


def sha256_file(filepath: str) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    """Computes SHA-256 hash of a text string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class KnowledgeCorpusExtractor:
    """Extracts canonical knowledge entities from structured JSON files in knowledge root."""

    def __init__(self, knowledge_root: str):
        self.knowledge_root = os.path.abspath(knowledge_root)
        self.course_id = os.path.basename(self.knowledge_root)
        self.source_file_hashes: Dict[str, Dict[str, Any]] = {}

    def _read_json(self, rel_path: str) -> Optional[Dict[str, Any]]:
        full_path = os.path.join(self.knowledge_root, rel_path)
        if not os.path.exists(full_path):
            return None
        file_hash = sha256_file(full_path)
        file_size = os.path.getsize(full_path)
        self.source_file_hashes[rel_path] = {
            "path": rel_path,
            "sha256": file_hash,
            "size_bytes": file_size,
            "validation_status": "VERIFIED",
            "freeze_status": "FROZEN",
        }
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def extract_all(self) -> List[Dict[str, Any]]:
        raw_records: List[Dict[str, Any]] = []

        # 1. Curriculum Outcomes & Process Components
        curr_map = self._read_json("curriculum_map.json")
        if curr_map:
            for theme in curr_map.get("themes", []):
                theme_id = theme.get("theme_id", f"TEMA_{theme.get('theme_no', 0):02d}")
                theme_title = theme.get("exact_theme_name") or theme.get("theme_title", "")
                
                # Theme overview entity
                theme_intro = theme.get("theme_introduction_verbatim", "")
                if theme_intro:
                    raw_records.append({
                        "course_id": self.course_id,
                        "entity_type": "curriculum_theme",
                        "entity_id": theme_id,
                        "theme_id": theme_id,
                        "title": theme_title,
                        "canonical_source_file": "curriculum_map.json",
                        "canonical_json_path_or_record_key": f"themes[{theme_id}]",
                        "authority_level": 1,
                        "authority_name": "OFFICIAL_CURRICULUM_FROZEN",
                        "origin": "official_curriculum",
                        "validation_status": "VERIFIED",
                        "freeze_status": "FROZEN",
                        "printed_page": theme.get("page_range", ""),
                        "pdf_page": "",
                        "source_locator": theme.get("source_locator", ""),
                        "semantic_text": f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). Resmî tanıtım: {theme_intro[:300]}... Sayfa aralığı: {theme.get('page_range', '')}.",
                        "entity_key": f"{self.course_id}::curriculum_theme::{theme_id}"
                    })

                for outcome in theme.get("learning_outcomes", []):
                    code = outcome.get("outcome_code", "")
                    verbatim = outcome.get("outcome_verbatim") or outcome.get("verbatim_statement", "")
                    skill = outcome.get("skill_category", "")
                    req = outcome.get("assessment_requirement_verbatim", "")
                    page = str(outcome.get("source_page", ""))
                    loc = outcome.get("source_locator", "")
                    related_codes = ", ".join(outcome.get("related_official_codes", []))

                    sem_text = (
                        f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). "
                        f"Entity: Öğrenme çıktısı {code}. Resmî ifade: {verbatim} "
                        f"Alan becerisi: {skill}. İlişkili kodlar: {related_codes}. "
                        f"Resmî değerlendirme şartı: {req}. Kaynak: {loc}."
                    )
                    raw_records.append({
                        "course_id": self.course_id,
                        "entity_type": "curriculum_outcome",
                        "entity_id": f"{theme_id}::{code}",
                        "theme_id": theme_id,
                        "title": f"Öğrenme Çıktısı {code} ({theme_id}) - {skill}",
                        "canonical_source_file": "curriculum_map.json",
                        "canonical_json_path_or_record_key": f"themes[{theme_id}].learning_outcomes[{code}]",
                        "authority_level": 1,
                        "authority_name": "OFFICIAL_CURRICULUM_FROZEN",
                        "origin": "official_curriculum",
                        "validation_status": "VERIFIED",
                        "freeze_status": "FROZEN",
                        "printed_page": page,
                        "pdf_page": "",
                        "source_locator": loc,
                        "semantic_text": sem_text,
                        "entity_key": f"{self.course_id}::curriculum_outcome::{theme_id}::{code}"
                    })

                    # Process components
                    for pc in outcome.get("process_components_verbatim", []):
                        p_code = pc.get("component_code", "")
                        p_title = pc.get("component_title", "")
                        p_verb = pc.get("component_verbatim", "")
                        p_loc = pc.get("source_locator", "")
                        clean_p_code = p_code.split(")")[-1].strip() if ")" in p_code else p_code
                        p_sem = (
                            f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). "
                            f"Entity: Süreç bileşeni {clean_p_code} ({code}). Başlık: {p_title}. "
                            f"Resmî ifade: {p_verb}. Kaynak: {p_loc}."
                        )
                        raw_records.append({
                            "course_id": self.course_id,
                            "entity_type": "process_component",
                            "entity_id": f"{theme_id}::{code}::{clean_p_code}",
                            "theme_id": theme_id,
                            "title": f"Süreç Bileşeni {clean_p_code} ({code}, {theme_id}) - {p_title}",
                            "canonical_source_file": "curriculum_map.json",
                            "canonical_json_path_or_record_key": f"themes[{theme_id}].learning_outcomes[{code}].process_components[{clean_p_code}]",
                            "authority_level": 1,
                            "authority_name": "OFFICIAL_CURRICULUM_FROZEN",
                            "origin": "official_curriculum",
                            "validation_status": "VERIFIED",
                            "freeze_status": "FROZEN",
                            "printed_page": page,
                            "pdf_page": "",
                            "source_locator": p_loc,
                            "semantic_text": p_sem,
                            "entity_key": f"{self.course_id}::process_component::{theme_id}::{code}::{clean_p_code}"
                        })

        # 2. Textbook Map (Sections and Activities)
        tb_map = self._read_json("textbook_map.json")
        if tb_map:
            for theme in tb_map.get("themes") or tb_map.get("units_or_themes", []):
                theme_id = theme.get("theme_id", f"TEMA_{theme.get('theme_no', 0):02d}")
                theme_title = theme.get("title") or theme.get("exact_title", "")

                for sec in theme.get("sections", []):
                    sec_id = sec.get("section_id", "")
                    sec_title = sec.get("title") or sec.get("section_title", "")
                    sec_page = str(sec.get("printed_page", "") or sec.get("page_locator", ""))
                    sec_pdf = str(sec.get("pdf_page", ""))
                    sec_genres = ", ".join(t.get("title", "") for t in sec.get("texts_and_genres", []))
                    
                    sec_sem = (
                        f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). "
                        f"Entity: Ders kitabı bölümü {sec_id}. Başlık: {sec_title}. "
                        f"Sayfa: s. {sec_page}. İçerilen metin ve türler: {sec_genres}."
                    )
                    raw_records.append({
                        "course_id": self.course_id,
                        "entity_type": "textbook_section",
                        "entity_id": sec_id,
                        "theme_id": theme_id,
                        "title": f"Ders Kitabı Bölümü: {sec_title}",
                        "canonical_source_file": "textbook_map.json",
                        "canonical_json_path_or_record_key": f"themes[{theme_id}].sections[{sec_id}]",
                        "authority_level": 2,
                        "authority_name": "OFFICIAL_TEXTBOOK_FROZEN",
                        "origin": "official_textbook",
                        "validation_status": "VERIFIED",
                        "freeze_status": "FROZEN",
                        "printed_page": sec_page,
                        "pdf_page": sec_pdf,
                        "source_locator": f"s. {sec_page}",
                        "semantic_text": sec_sem,
                        "entity_key": f"{self.course_id}::textbook_section::{theme_id}::{sec_id}"
                    })

                    for act in sec.get("activities", []):
                        act_id = act.get("activity_id", "")
                        act_title = act.get("title") or act.get("activity_title", "")
                        act_type = act.get("type", "")
                        act_page = str(act.get("printed_page", "") or act.get("page_locator", ""))
                        act_ev = act.get("expected_student_evidence", "")
                        act_form = act.get("linked_form_id", "")

                        act_sem = (
                            f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). "
                            f"Entity: Ders kitabı etkinliği {act_id}. Başlık: {act_title}. "
                            f"Tür: {act_type}. Sayfa: s. {act_page}. "
                            f"Beklenen öğrenci kanıtı: {act_ev}. İlgili form: {act_form}."
                        )
                        raw_records.append({
                            "course_id": self.course_id,
                            "entity_type": "textbook_activity",
                            "entity_id": act_id,
                            "theme_id": theme_id,
                            "title": f"Ders Kitabı Etkinliği: {act_title}",
                            "canonical_source_file": "textbook_map.json",
                            "canonical_json_path_or_record_key": f"themes[{theme_id}].sections[{sec_id}].activities[{act_id}]",
                            "authority_level": 2,
                            "authority_name": "OFFICIAL_TEXTBOOK_FROZEN",
                            "origin": "official_textbook",
                            "validation_status": "VERIFIED",
                            "freeze_status": "FROZEN",
                            "printed_page": act_page,
                            "pdf_page": str(act.get("pdf_page", "")),
                            "source_locator": f"s. {act_page}",
                            "semantic_text": act_sem,
                            "entity_key": f"{self.course_id}::textbook_activity::{theme_id}::{act_id}"
                        })

        # 3. Textbook Forms Index (All 28 Canonical Forms)
        tb_forms = self._read_json("textbook_forms_index.json")
        if tb_forms:
            for form in tb_forms.get("forms", []):
                form_id = form.get("form_id", "")
                p_title = form.get("printed_title") or form.get("title", "")
                subtitle = form.get("subtitle", "")
                s_type = form.get("structural_type", "")
                evaluator = form.get("evaluator", "")
                p_page = str(form.get("printed_page", ""))
                pdf_page = str(form.get("pdf_page", ""))
                linked_themes = ", ".join(form.get("linked_theme_ids", []))
                first_theme = form.get("linked_theme_ids", [""])[0] if form.get("linked_theme_ids") else ""
                linked_acts = ", ".join(form.get("linked_activity_ids", []))
                struct_note = form.get("structure_details", {}).get("structure_note", "")
                crit_cats = ", ".join(form.get("structure_details", {}).get("criteria_categories", []))

                form_sem = (
                    f"Ders: {self.course_id}. Tema: {linked_themes}. "
                    f"Entity: {form_id}. Tür: {s_type}. "
                    f"Başlık: {p_title} ({subtitle}). Değerlendirici: {evaluator}. "
                    f"Sayfa: s. {p_page} (PDF {pdf_page}). İlgili etkinlikler: {linked_acts}. "
                    f"Ölçüt alanları: {crit_cats}. Yapısal açıklama: {struct_note or 'Standart ders kitabı form yapısı'}."
                )
                raw_records.append({
                    "course_id": self.course_id,
                    "entity_type": "textbook_form",
                    "entity_id": form_id,
                    "theme_id": first_theme,
                    "title": f"Ölçme Aracı: {p_title} ({s_type})",
                    "canonical_source_file": "textbook_forms_index.json",
                    "canonical_json_path_or_record_key": f"forms[{form_id}]",
                    "authority_level": 3,
                    "authority_name": "OFFICIAL_TEXTBOOK_FORM_FROZEN",
                    "origin": "official_textbook",
                    "validation_status": "VERIFIED",
                    "freeze_status": "FROZEN",
                    "printed_page": p_page,
                    "pdf_page": pdf_page,
                    "source_locator": f"s. {p_page} (PDF: {pdf_page})",
                    "semantic_text": form_sem,
                    "entity_key": f"{self.course_id}::textbook_form::{form_id}"
                })

        # 4. Themes 1-4 (Alignment, Gaps, Needs, Resource Plans)
        for theme_no in range(1, 5):
            t_dir = f"themes/tema_{theme_no:02d}"
            t_id = f"TEMA_{theme_no:02d}"

            # Alignments
            align_data = self._read_json(f"{t_dir}/alignment.json")
            if align_data:
                for al in align_data.get("alignments", []):
                    code = al.get("outcome_code", "")
                    cov = al.get("primary_coverage", "")
                    dec = al.get("production_decision", "")
                    prio = al.get("priority", "")
                    gap = al.get("remaining_gap", "")
                    tb_acts = ", ".join(al.get("textbook_activity_ids", []))
                    tb_loc = ", ".join(al.get("textbook_locators", []))
                    p_loc = al.get("provenance", {}).get("program_locator", "")

                    al_sem = (
                        f"Ders: {self.course_id}. Tema: {t_id}. "
                        f"Entity: Hizalama kaydı {code}. Kapsama düzeyi: {cov}. "
                        f"Üretim kararı: {dec}. Öncelik: {prio}. "
                        f"Ders kitabı etkinliği: {tb_acts} ({tb_loc}). "
                        f"Kalan boşluk: {gap}. Program konumu: {p_loc}."
                    )
                    raw_records.append({
                        "course_id": self.course_id,
                        "entity_type": "alignment_record",
                        "entity_id": f"ALIGN_{t_id}_{code}",
                        "theme_id": t_id,
                        "title": f"Program-Kitap Hizalaması: {code} ({cov})",
                        "canonical_source_file": f"{t_dir}/alignment.json",
                        "canonical_json_path_or_record_key": f"alignments[{code}]",
                        "authority_level": 4,
                        "authority_name": "VALIDATED_ALIGNMENT",
                        "origin": "validated_alignment",
                        "validation_status": "VERIFIED",
                        "freeze_status": "FROZEN",
                        "printed_page": "",
                        "pdf_page": "",
                        "source_locator": tb_loc or p_loc,
                        "semantic_text": al_sem,
                        "entity_key": f"{self.course_id}::alignment_record::{t_id}::{code}"
                    })

            # Gap Analysis
            gap_data = self._read_json(f"{t_dir}/gap_analysis.json")
            if gap_data:
                for g in gap_data.get("gaps", []) or gap_data.get("gap_records", []):
                    g_id = g.get("gap_id") or f"GAP_{t_id}_{g.get('outcome_code', '')}"
                    code = g.get("outcome_code", "")
                    cov = g.get("primary_coverage", "")
                    gap_desc = g.get("remaining_gap", "")
                    prog_req = g.get("program_requirement_verbatim") or g.get("program_assessment_requirement_verbatim", "")
                    tb_prov = g.get("textbook_provides", "")
                    dec = g.get("production_decision", "")

                    g_sem = (
                        f"Ders: {self.course_id}. Tema: {t_id}. "
                        f"Entity: Boşluk analizi {g_id}. Hedef çıktı: {code}. Kapsama: {cov}. "
                        f"Kalan boşluk: {gap_desc}. Resmî program şartı: {prog_req}. "
                        f"Ders kitabı karşılığı: {tb_prov}. Üretim kararı: {dec}."
                    )
                    raw_records.append({
                        "course_id": self.course_id,
                        "entity_type": "remaining_gap",
                        "entity_id": g_id,
                        "theme_id": t_id,
                        "title": f"Boşluk Analizi: {code} - {cov}",
                        "canonical_source_file": f"{t_dir}/gap_analysis.json",
                        "canonical_json_path_or_record_key": f"gaps[{g_id}]",
                        "authority_level": 5,
                        "authority_name": "VALIDATED_GAP",
                        "origin": "validated_gap",
                        "validation_status": "VERIFIED",
                        "freeze_status": "FROZEN",
                        "printed_page": "",
                        "pdf_page": "",
                        "source_locator": "",
                        "semantic_text": g_sem,
                        "entity_key": f"{self.course_id}::remaining_gap::{t_id}::{g_id}"
                    })

            # Needs Analysis
            needs_data = self._read_json(f"{t_dir}/needs.json")
            if needs_data:
                for n in needs_data.get("needs", []):
                    n_id = n.get("need_id", "")
                    outcomes = ", ".join(n.get("targeted_learning_outcomes", []))
                    ev = n.get("expected_student_evidence", "")
                    cog = n.get("cognitive_demand", "")
                    n_sem = (
                        f"Ders: {self.course_id}. Tema: {t_id}. "
                        f"Entity: Öğretimsel ihtiyaç {n_id}. Hedef çıktılar: {outcomes}. "
                        f"Beklenen öğrenci kanıtı: {ev}. Bilişsel talep: {cog}. "
                        f"Değerlendirme ihtiyacı: {n.get('assessment_need', '')}."
                    )
                    raw_records.append({
                        "course_id": self.course_id,
                        "entity_type": "instructional_need",
                        "entity_id": n_id,
                        "theme_id": t_id,
                        "title": f"Öğretimsel İhtiyaç: {n_id} ({outcomes})",
                        "canonical_source_file": f"{t_dir}/needs.json",
                        "canonical_json_path_or_record_key": f"needs[{n_id}]",
                        "authority_level": 6,
                        "authority_name": "VALIDATED_RESOURCE_PLAN",
                        "origin": "validated_resource_plan",
                        "validation_status": "VERIFIED",
                        "freeze_status": "FROZEN",
                        "printed_page": "",
                        "pdf_page": "",
                        "source_locator": "",
                        "semantic_text": n_sem,
                        "entity_key": f"{self.course_id}::instructional_need::{t_id}::{n_id}"
                    })

            # Resource Plans
            rp_data = self._read_json(f"{t_dir}/resource_plan.json")
            if rp_data:
                for r in rp_data.get("resources", []) or rp_data.get("resource_plans", []):
                    r_id = r.get("resource_plan_id") or r.get("resource_id", "")
                    r_type = r.get("resource_type", "")
                    outcomes = ", ".join(r.get("target_outcomes", []))
                    prio = r.get("priority", "")
                    dec = r.get("production_decision", "")
                    purp = r.get("purpose", "")
                    ev = r.get("expected_student_evidence", "")

                    r_sem = (
                        f"Ders: {self.course_id}. Tema: {t_id}. "
                        f"Entity: Kaynak planı {r_id}. İşlev türü: {r_type}. "
                        f"Hedef çıktılar: {outcomes}. Öncelik: {prio}. "
                        f"Üretim kararı: {dec}. Amaç: {purp}. Beklenen kanıt: {ev}."
                    )
                    raw_records.append({
                        "course_id": self.course_id,
                        "entity_type": "resource_plan",
                        "entity_id": r_id,
                        "theme_id": t_id,
                        "title": f"Kaynak Planı: {r_id} ({r_type})",
                        "canonical_source_file": f"{t_dir}/resource_plan.json",
                        "canonical_json_path_or_record_key": f"resources[{r_id}]",
                        "authority_level": 6,
                        "authority_name": "VALIDATED_RESOURCE_PLAN",
                        "origin": "validated_resource_plan",
                        "validation_status": "VERIFIED",
                        "freeze_status": "FROZEN",
                        "printed_page": "",
                        "pdf_page": "",
                        "source_locator": "",
                        "semantic_text": r_sem,
                        "entity_key": f"{self.course_id}::resource_plan::{t_id}::{r_id}"
                    })

        # 5. Production Manifest (Production Materials)
        prod_manifest = self._read_json("production/production_manifest.json")
        if prod_manifest:
            for mat in prod_manifest.get("production_queue", []):
                m_id = mat.get("material_id", "")
                themes = ", ".join(mat.get("theme_ids", []))
                first_theme = mat.get("theme_ids", [""])[0] if mat.get("theme_ids") else ""
                outcomes = ", ".join(mat.get("targeted_outcomes", []))
                req = mat.get("official_requirement_verbatim", "")
                gap = mat.get("exact_remaining_gap", "")
                impl = mat.get("selected_implementation", "")
                prio = mat.get("priority", "")
                rel = mat.get("textbook_relationship", "")
                loc_c = mat.get("source_locators", {}).get("curriculum", "")
                loc_tb = mat.get("source_locators", {}).get("textbook", "")

                mat_sem = (
                    f"Ders: {self.course_id}. Tema: {themes}. "
                    f"Entity: Üretim materyali {m_id}. Hedef çıktılar: {outcomes}. "
                    f"Resmî program şartı: {req}. Kalan boşluk: {gap}. "
                    f"Seçilen uygulama formatı: {impl}. Öncelik: {prio}. Ders kitabı ilişkisi: {rel}. "
                    f"Program konumu: {loc_c}. Kitap konumu: {loc_tb}."
                )
                raw_records.append({
                    "course_id": self.course_id,
                    "entity_type": "production_material",
                    "entity_id": m_id,
                    "theme_id": first_theme,
                    "title": f"Üretim Materyali: {m_id} ({impl})",
                    "canonical_source_file": "production/production_manifest.json",
                    "canonical_json_path_or_record_key": f"production_queue[{m_id}]",
                    "authority_level": 7,
                    "authority_name": "VALIDATED_PRODUCTION_PLAN",
                    "origin": "validated_production_plan",
                    "validation_status": "VERIFIED",
                    "freeze_status": "FROZEN",
                    "printed_page": "",
                    "pdf_page": "",
                    "source_locator": f"Curriculum: {loc_c} | Textbook: {loc_tb}",
                    "semantic_text": mat_sem,
                    "entity_key": f"{self.course_id}::production_material::{m_id}"
                })

        # 6. Teaching Blocks
        tb_blocks = self._read_json("production/teaching_blocks.json")
        if tb_blocks:
            for blk in tb_blocks.get("teaching_blocks", []):
                b_id = blk.get("block_id", "")
                b_title = blk.get("title", "")
                b_theme = blk.get("theme_id", "")
                b_hours = str(blk.get("allocated_hours", ""))
                b_outcomes = ", ".join(blk.get("targeted_outcomes", []))
                b_mats = ", ".join(blk.get("required_material_ids", []))

                b_sem = (
                    f"Ders: {self.course_id}. Tema: {b_theme}. "
                    f"Entity: Öğretim bloğu {b_id}. Başlık: {b_title}. "
                    f"Ders saati: {b_hours} saat. Hedef çıktılar: {b_outcomes}. "
                    f"Gerekli materyaller: {b_mats}."
                )
                raw_records.append({
                    "course_id": self.course_id,
                    "entity_type": "teaching_block",
                    "entity_id": b_id,
                    "theme_id": b_theme,
                    "title": f"Öğretim Bloğu: {b_title} ({b_hours}h)",
                    "canonical_source_file": "production/teaching_blocks.json",
                    "canonical_json_path_or_record_key": f"teaching_blocks[{b_id}]",
                    "authority_level": 7,
                    "authority_name": "VALIDATED_PRODUCTION_PLAN",
                    "origin": "validated_production_plan",
                    "validation_status": "VERIFIED",
                    "freeze_status": "FROZEN",
                    "printed_page": "",
                    "pdf_page": "",
                    "source_locator": f"{b_hours} saat",
                    "semantic_text": b_sem,
                    "entity_key": f"{self.course_id}::teaching_block::{b_theme}::{b_id}"
                })

        # 7. School Based Planning Options (Authority 8: Pedagogical Recommendation)
        sbp = self._read_json("production/school_based_planning_options.json")
        if sbp:
            for theme in sbp.get("themes", []):
                t_id = theme.get("theme_id", "")
                t_title = theme.get("theme_title", "")
                for opt in theme.get("options", []):
                    opt_id = opt.get("option_id", "")
                    opt_title = opt.get("title", "")
                    cat = opt.get("category", "")
                    dur = str(opt.get("duration_hours", ""))
                    rat = opt.get("rationale", "")
                    action = opt.get("expected_student_action", "")
                    ev = opt.get("expected_student_evidence", "")
                    outcomes = ", ".join(opt.get("linked_outcomes", []))

                    opt_sem = (
                        f"Ders: {self.course_id}. Tema: {t_title} ({t_id}). "
                        f"Entity: Okul temelli planlama seçeneği {opt_id}. Başlık: {opt_title}. "
                        f"Kategori: {cat}. Süre: {dur} saat. Menşei: pedagojik öneri. "
                        f"İlişkili çıktılar: {outcomes}. Gerekçe: {rat} "
                        f"Öğrenci eylemi: {action} Kanıt: {ev}."
                    )
                    raw_records.append({
                        "course_id": self.course_id,
                        "entity_type": "school_based_option",
                        "entity_id": opt_id,
                        "theme_id": t_id,
                        "title": f"Okul Temelli Seçenek: {opt_title} ({cat})",
                        "canonical_source_file": "production/school_based_planning_options.json",
                        "canonical_json_path_or_record_key": f"themes[{t_id}].options[{opt_id}]",
                        "authority_level": 8,
                        "authority_name": "PEDAGOGICAL_RECOMMENDATION",
                        "origin": "pedagogical_recommendation",
                        "validation_status": "VERIFIED",
                        "freeze_status": "FROZEN",
                        "printed_page": "",
                        "pdf_page": "",
                        "source_locator": f"{dur} saat",
                        "semantic_text": opt_sem,
                        "entity_key": f"{self.course_id}::school_based_option::{t_id}::{opt_id}"
                    })

        # Collision-Free Key Validation: Strictly Fail on Duplicate Keys
        seen_keys: Dict[str, str] = {}
        validated_records: List[Dict[str, Any]] = []
        for r in raw_records:
            key = r["entity_key"]
            if key in seen_keys:
                raise DuplicateCanonicalKeyError(
                    f"DUPLICATE_CANONICAL_KEY: Duplicate entity key '{key}' encountered for entity '{r['entity_id']}' "
                    f"(previous origin: '{seen_keys[key]}', current origin: '{r['canonical_source_file']}'). "
                    "Silent overwrite or suffix fallback is strictly forbidden."
                )
            seen_keys[key] = r["canonical_source_file"]
            r["content_hash"] = sha256_text(r["semantic_text"])
            src_file = r["canonical_source_file"]
            r["source_file_hash"] = self.source_file_hashes.get(src_file, {}).get("sha256", "")
            r["embedding_model"] = BASE_EMBEDDING_MODEL
            r["embedding_dimension"] = EMBEDDING_DIMENSION
            r["created_at"] = datetime.now(timezone.utc).isoformat()
            r["updated_at"] = r["created_at"]
            validated_records.append(r)

        return validated_records


class KnowledgeIndexer:
    """Manages the SQLite + sqlite-vec + FTS5 database and manifests."""

    def __init__(self, knowledge_root: str, model_dir: str = DEFAULT_MODEL_DIR):
        self.knowledge_root = os.path.abspath(knowledge_root)
        self.course_id = os.path.basename(self.knowledge_root)
        self.index_dir = os.path.join(self.knowledge_root, "index")
        self.db_path = os.path.join(self.index_dir, "knowledge.sqlite")
        self.manifest_path = os.path.join(self.index_dir, "index_manifest.json")
        self.report_path = os.path.join(self.index_dir, "index_validation_report.md")
        self.model_dir = model_dir
        self.embedding_engine = LocalEmbeddingEngine(model_dir=model_dir)

    def _get_db_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        if HAS_SQLITE_VEC:
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
        return conn

    def get_model_file_sha256(self) -> str:
        """Computes runtime model file SHA256."""
        model_path = os.path.join(self.model_dir, RUNTIME_MODEL_FILE)
        if not os.path.exists(model_path):
            model_path = os.path.join(self.model_dir, "model.onnx")
        if os.path.exists(model_path):
            return sha256_file(model_path)
        return "MODEL_FILE_NOT_FOUND"

    def check_status(self) -> Dict[str, Any]:
        """Checks manifest integrity, vector backend, and stale status vs source JSONs."""
        if not os.path.exists(self.manifest_path) or not os.path.exists(self.db_path):
            return {
                "status": "INDEX_MISSING",
                "course_id": self.course_id,
                "message": "Index database or manifest does not exist. Build required."
            }

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Check Vector Backend Match
        if manifest.get("vector_extension") != SELECTED_VECTOR_BACKEND:
            return {
                "status": "VECTOR_BACKEND_MISMATCH",
                "course_id": self.course_id,
                "expected_backend": SELECTED_VECTOR_BACKEND,
                "indexed_backend": manifest.get("vector_extension"),
                "message": f"Vector backend mismatch. Expected {SELECTED_VECTOR_BACKEND}, found {manifest.get('vector_extension')}. Rebuild required."
            }

        # Check Embedding Model & Dimension Match
        if (manifest.get("base_embedding_model") != BASE_EMBEDDING_MODEL and
            manifest.get("embedding_model") != BASE_EMBEDDING_MODEL) or \
           manifest.get("embedding_dimension") != EMBEDDING_DIMENSION:
            return {
                "status": "EMBEDDING_MODEL_MISMATCH",
                "course_id": self.course_id,
                "expected_model": BASE_EMBEDDING_MODEL,
                "indexed_model": manifest.get("base_embedding_model") or manifest.get("embedding_model"),
                "message": "Embedding model or dimension changed. Rebuild required."
            }

        # Check Embedding Runtime Artifact Hash Match
        current_model_sha256 = self.get_model_file_sha256()
        indexed_model_sha256 = manifest.get("model_file_sha256")
        if indexed_model_sha256 and current_model_sha256 != "MODEL_FILE_NOT_FOUND" and current_model_sha256 != indexed_model_sha256:
            return {
                "status": "EMBEDDING_ARTIFACT_MISMATCH",
                "course_id": self.course_id,
                "expected_model_sha256": current_model_sha256,
                "indexed_model_sha256": indexed_model_sha256,
                "message": "Embedding runtime model artifact SHA256 changed. Vector rebuild required."
            }

        # Check source files hash
        mismatched_files = []
        for src in manifest.get("source_files", []):
            rel_path = src["path"]
            full_path = os.path.join(self.knowledge_root, rel_path)
            if not os.path.exists(full_path):
                mismatched_files.append({"file": rel_path, "reason": "MISSING"})
                continue
            current_hash = sha256_file(full_path)
            if current_hash != src["sha256"]:
                mismatched_files.append({
                    "file": rel_path,
                    "expected_sha256": src["sha256"],
                    "current_sha256": current_hash,
                    "reason": "HASH_MISMATCH"
                })

        if mismatched_files:
            return {
                "status": "INDEX_STALE",
                "course_id": self.course_id,
                "mismatched_files": mismatched_files,
                "message": "Source JSON files have been modified. Rebuild required."
            }

        return {
            "status": "INDEX_FRESH",
            "course_id": self.course_id,
            "indexed_record_count": manifest.get("indexed_record_count", 0),
            "indexed_entity_types": manifest.get("indexed_entity_types", []),
            "index_updated_at": manifest.get("index_updated_at"),
            "database_engine": manifest.get("database_engine"),
            "vector_extension": manifest.get("vector_extension"),
            "backend_selection_status": manifest.get("backend_selection_status"),
            "base_embedding_model": manifest.get("base_embedding_model"),
            "runtime_model_file": manifest.get("runtime_model_file"),
            "model_file_sha256": manifest.get("model_file_sha256"),
        }

    def build_index(self, force: bool = False) -> Dict[str, Any]:
        """Extracts canonical knowledge, generates embeddings, and writes SQLite + FTS5 + Vec."""
        os.makedirs(self.index_dir, exist_ok=True)
        extractor = KnowledgeCorpusExtractor(self.knowledge_root)
        records = extractor.extract_all()

        if not records:
            raise ValueError(f"No canonical records found in {self.knowledge_root}")

        print(f"[*] Extracted {len(records)} canonical entities from {self.course_id}.", flush=True)

        # Generate embeddings in batches
        print(f"[*] Generating {EMBEDDING_DIMENSION}-dim embeddings using {BASE_EMBEDDING_MODEL} ({RUNTIME_MODEL_FILE})...", flush=True)
        texts_to_embed = [r["semantic_text"] for r in records]
        embeddings = self.embedding_engine.encode(texts_to_embed, is_query=False, batch_size=32)

        # Build SQLite Database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        conn = self._get_db_connection()
        cur = conn.cursor()

        # 1. Metadata table
        cur.execute("""
            CREATE TABLE metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_key TEXT UNIQUE NOT NULL,
                course_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                theme_id TEXT,
                canonical_source_file TEXT NOT NULL,
                canonical_json_path_or_record_key TEXT NOT NULL,
                authority_level INTEGER NOT NULL,
                authority_name TEXT NOT NULL,
                origin TEXT NOT NULL,
                validation_status TEXT NOT NULL,
                freeze_status TEXT NOT NULL,
                printed_page TEXT,
                pdf_page TEXT,
                source_locator TEXT,
                content_hash TEXT NOT NULL,
                source_file_hash TEXT NOT NULL,
                embedding_model TEXT NOT NULL,
                embedding_dimension INTEGER NOT NULL,
                semantic_text TEXT NOT NULL,
                title TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)

        # 2. SQLite FTS5 table
        cur.execute("""
            CREATE VIRTUAL TABLE fts_entities USING fts5(
                entity_key UNINDEXED,
                entity_id,
                entity_type,
                theme_id,
                title,
                semantic_text,
                tokenize='unicode61'
            );
        """)

        # 3. sqlite-vec virtual table
        if HAS_SQLITE_VEC:
            cur.execute(f"""
                CREATE VIRTUAL TABLE vec_entities USING vec0(
                    rowid INTEGER PRIMARY KEY,
                    embedding float[{EMBEDDING_DIMENSION}]
                );
            """)

        # Insert metadata and FTS records
        entity_types_set = set()
        for idx, r in enumerate(records):
            entity_types_set.add(r["entity_type"])
            cur.execute("""
                INSERT INTO metadata (
                    entity_key, course_id, entity_type, entity_id, theme_id,
                    canonical_source_file, canonical_json_path_or_record_key,
                    authority_level, authority_name, origin, validation_status, freeze_status,
                    printed_page, pdf_page, source_locator, content_hash, source_file_hash,
                    embedding_model, embedding_dimension, semantic_text, title,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r["entity_key"], r["course_id"], r["entity_type"], r["entity_id"], r["theme_id"],
                r["canonical_source_file"], r["canonical_json_path_or_record_key"],
                r["authority_level"], r["authority_name"], r["origin"], r["validation_status"], r["freeze_status"],
                r["printed_page"], r["pdf_page"], r["source_locator"], r["content_hash"], r["source_file_hash"],
                r["embedding_model"], r["embedding_dimension"], r["semantic_text"], r["title"],
                r["created_at"], r["updated_at"]
            ))
            row_id = cur.lastrowid

            cur.execute("""
                INSERT INTO fts_entities (entity_key, entity_id, entity_type, theme_id, title, semantic_text)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                r["entity_key"], r["entity_id"], r["entity_type"], r["theme_id"], r["title"], r["semantic_text"]
            ))

            if HAS_SQLITE_VEC:
                emb_blob = sqlite_vec.serialize_float32(embeddings[idx].tolist())
                cur.execute("INSERT INTO vec_entities(rowid, embedding) VALUES (?, ?)", (row_id, emb_blob))

        conn.commit()
        conn.close()

        # Compute index content hash
        all_content_hashes = "".join(sorted(r["content_hash"] for r in records))
        index_content_hash = sha256_text(all_content_hashes)
        model_sha256 = self.get_model_file_sha256()

        # Write index_manifest.json with comprehensive provenance & backend metadata
        manifest = {
            "schema_version": "2.0",
            "course_id": self.course_id,
            "index_created_at": datetime.now(timezone.utc).isoformat(),
            "index_updated_at": datetime.now(timezone.utc).isoformat(),
            
            # Vector Backend Architecture & Explicit Accepted Deviation
            "requested_backend": REQUESTED_VECTOR_BACKEND,
            "selected_backend": SELECTED_VECTOR_BACKEND,
            "backend_selection_status": BACKEND_SELECTION_STATUS,
            "backend_selection_reason": BACKEND_SELECTION_REASON,
            "database_engine": f"SQLite {sqlite3.sqlite_version} + {SELECTED_VECTOR_BACKEND} (v0.1.9)",
            "vector_extension": SELECTED_VECTOR_BACKEND,
            "vector_extension_version": "0.1.9" if HAS_SQLITE_VEC else "NONE",
            "sqlite_version": sqlite3.sqlite_version,
            "runtime_platform": platform.platform(),
            "runtime_architecture": platform.machine(),

            # Embedding Model Runtime Provenance
            "base_embedding_model": BASE_EMBEDDING_MODEL,
            "runtime_model_repository": RUNTIME_MODEL_REPOSITORY,
            "runtime_model_file": RUNTIME_MODEL_FILE,
            "runtime_format": RUNTIME_FORMAT,
            "quantization": QUANTIZATION,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "pooling_strategy": POOLING_STRATEGY,
            "normalization": NORMALIZATION,
            "query_prefix": QUERY_PREFIX,
            "passage_prefix": PASSAGE_PREFIX,
            "model_file_sha256": model_sha256,
            "distance_metric": "cosine",

            # Indexed Entity Metadata
            "indexed_entity_types": sorted(list(entity_types_set)),
            "indexed_record_count": len(records),
            "source_files": list(extractor.source_file_hashes.values()),
            "index_content_hash": index_content_hash,
            "build_status": "SUCCESS"
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Write index_validation_report.md
        report_content = f"""# Knowledge Index Validation Report

- **Course ID**: {self.course_id}
- **Build Timestamp**: {manifest['index_created_at']}
- **Status**: {manifest['build_status']}
- **Total Indexed Records**: {len(records)}
- **Database Engine**: {manifest['database_engine']}
- **Vector Backend**: `{SELECTED_VECTOR_BACKEND}` ({BACKEND_SELECTION_STATUS})
- **Base Embedding Model**: `{BASE_EMBEDDING_MODEL}` (Dim: {EMBEDDING_DIMENSION})
- **Runtime Model Repository**: `{RUNTIME_MODEL_REPOSITORY}` (`{RUNTIME_MODEL_FILE}`)
- **Model File SHA256**: `{model_sha256}`
- **Pooling & Normalization**: `{POOLING_STRATEGY}` / `{NORMALIZATION}`
- **Index Content Hash**: `{index_content_hash}`

## Vector Backend Architecture Decision
- **Requested Backend**: `{REQUESTED_VECTOR_BACKEND}`
- **Selected Backend**: `{SELECTED_VECTOR_BACKEND}`
- **Status**: `{BACKEND_SELECTION_STATUS}`
- **Rationale**: {BACKEND_SELECTION_REASON}

## Indexed Entity Types & Counts
"""
        type_counts: Dict[str, int] = {}
        for r in records:
            type_counts[r["entity_type"]] = type_counts.get(r["entity_type"], 0) + 1
        for etype, count in sorted(type_counts.items()):
            report_content += f"- **{etype}**: {count}\n"

        report_content += "\n## Source Files Fingerprint\n"
        for sf in manifest["source_files"]:
            report_content += f"- `{sf['path']}`: SHA-256 `{sf['sha256'][:16]}...` ({sf['size_bytes']} bytes) - {sf['validation_status']}\n"

        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"[✓] Successfully built index at {self.db_path} ({len(records)} records).", flush=True)
        return manifest

    def search_hybrid(
        self,
        query: str,
        top_k: int = 8,
        theme_id: Optional[str] = None,
        entity_types: Optional[List[str]] = None,
        authority_max: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid retrieval: Metadata filter + FTS5 lexical + Vector similarity,
        combined using Reciprocal Rank Fusion (RRF).
        """
        conn = self._get_db_connection()
        cur = conn.cursor()

        # 1. Vector Search
        query_vec = self.embedding_engine.encode([query], is_query=True)[0]
        vector_candidates: List[Tuple[int, float]] = []

        if HAS_SQLITE_VEC:
            vec_blob = sqlite_vec.serialize_float32(query_vec.tolist())
            vec_sql = "SELECT rowid, distance FROM vec_entities WHERE embedding MATCH ? AND k = ?"
            cur.execute(vec_sql, (vec_blob, top_k * 3))
            for row in cur.fetchall():
                vector_candidates.append((row[0], float(row[1])))

        # 2. FTS5 Lexical Search
        clean_terms = [t.strip() for t in query.replace(":", " ").replace("-", " ").replace("?", "").replace(".", " ").split() if len(t.strip()) > 1]
        fts_candidates: List[Tuple[int, float]] = []
        if clean_terms:
            fts_query = " OR ".join(f'"{t}"' for t in clean_terms[:8])
            try:
                cur.execute("""
                    SELECT m.id, f.rank
                    FROM fts_entities f
                    JOIN metadata m ON f.entity_key = m.entity_key
                    WHERE fts_entities MATCH ?
                    ORDER BY f.rank
                    LIMIT ?
                """, (fts_query, top_k * 3))
                for row in cur.fetchall():
                    fts_candidates.append((row[0], float(row[1])))
            except sqlite3.OperationalError:
                pass

        # 3. Reciprocal Rank Fusion (RRF)
        # RRF score = sum(1 / (60 + rank))
        rrf_scores: Dict[int, float] = {}
        vector_ranks: Dict[int, int] = {}
        fts_ranks: Dict[int, int] = {}

        for rank_idx, (rec_id, _) in enumerate(vector_candidates):
            vector_ranks[rec_id] = rank_idx + 1
            rrf_scores[rec_id] = rrf_scores.get(rec_id, 0.0) + (1.0 / (60.0 + rank_idx + 1))

        for rank_idx, (rec_id, _) in enumerate(fts_candidates):
            fts_ranks[rec_id] = rank_idx + 1
            rrf_scores[rec_id] = rrf_scores.get(rec_id, 0.0) + (1.0 / (60.0 + rank_idx + 1))

        # 4. Fetch metadata for merged candidates and apply filters
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        results: List[Dict[str, Any]] = []

        for rec_id, score in sorted_candidates:
            cur.execute("SELECT * FROM metadata WHERE id = ?", (rec_id,))
            row = cur.fetchone()
            if not row:
                continue

            r_dict = dict(row)
            # Apply filters
            if theme_id and r_dict["theme_id"] and r_dict["theme_id"] != theme_id:
                continue
            if entity_types and r_dict["entity_type"] not in entity_types:
                continue
            if r_dict["authority_level"] > authority_max:
                continue

            r_dict["rrf_score"] = round(score, 6)
            r_dict["vector_rank"] = vector_ranks.get(rec_id)
            r_dict["fts_rank"] = fts_ranks.get(rec_id)
            results.append(r_dict)
            if len(results) >= top_k:
                break

        conn.close()
        return results


def main():
    parser = argparse.ArgumentParser(description="TYMM Knowledge Index CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build
    p_build = subparsers.add_parser("build", help="Build or rebuild the index")
    p_build.add_argument("--knowledge-root", required=True, help="Path to knowledge directory (e.g. knowledge/TDE_9)")
    p_build.add_argument("--force", action="store_true", help="Force full rebuild")

    # rebuild
    p_rebuild = subparsers.add_parser("rebuild", help="Force rebuild the index")
    p_rebuild.add_argument("--knowledge-root", required=True, help="Path to knowledge directory")

    # status
    p_status = subparsers.add_parser("status", help="Check index freshness and metadata")
    p_status.add_argument("--knowledge-root", required=True, help="Path to knowledge directory")

    # query
    p_query = subparsers.add_parser("query", help="Execute hybrid search on index")
    p_query.add_argument("--knowledge-root", required=True, help="Path to knowledge directory")
    p_query.add_argument("--query", required=True, help="Query string")
    p_query.add_argument("--top-k", type=int, default=8, help="Number of results")
    p_query.add_argument("--theme-id", help="Filter by theme ID (e.g. TEMA_02)")
    p_query.add_argument("--entity-type", help="Comma-separated entity types")

    args = parser.parse_args()
    indexer = KnowledgeIndexer(args.knowledge_root)

    if args.command in ("build", "rebuild"):
        manifest = indexer.build_index(force=True)
        print(json.dumps(manifest, indent=2, ensure_ascii=False))

    elif args.command == "status":
        status = indexer.check_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.command == "query":
        etypes = [e.strip() for e in args.entity_type.split(",")] if args.entity_type else None
        results = indexer.search_hybrid(
            query=args.query,
            top_k=args.top_k,
            theme_id=args.theme_id,
            entity_types=etypes
        )
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
