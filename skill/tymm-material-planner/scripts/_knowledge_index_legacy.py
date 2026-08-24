#!/usr/bin/env python3
"""TYMM canonical knowledge indexer.

Builds a project-scoped SQLite + FTS5 + sqlite-vec index derived from frozen
canonical JSON. The index is never the source of truth.

Production schema 1.1 invariant:
- assessment artifact identity is ``artifact_id``
- ``covered_themes`` and ``covered_outcomes`` define reusable artifact scope
- ``covered_gap_instances`` contains historical MAT_* aliases/provenance only
"""

import argparse
import hashlib
import json
import os
import platform
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import sqlite_vec
    HAS_SQLITE_VEC = True
except ImportError:
    HAS_SQLITE_VEC = False

try:
    import onnxruntime as ort
    import tokenizers
    HAS_EMBEDDING_RUNTIME = True
except ImportError:
    HAS_EMBEDDING_RUNTIME = False

try:
    from production_schema import PRODUCTION_SCHEMA_VERSION, ProductionSchemaError, build_artifact_maps
except ImportError:
    from .production_schema import PRODUCTION_SCHEMA_VERSION, ProductionSchemaError, build_artifact_maps


REQUESTED_VECTOR_BACKEND = "sqlite-vector/sqliteai-vector"
SELECTED_VECTOR_BACKEND = "sqlite-vec"
BACKEND_SELECTION_STATUS = "EXPLICIT_ACCEPTED_DEVIATION"
BACKEND_SELECTION_REASON = (
    "sqlite-vec is the lightweight native SQLite vector extension selected for local TYMM retrieval; "
    "the canonical JSON layer remains authoritative."
)
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
    "multilingual-e5-small",
)


class DuplicateCanonicalKeyError(Exception):
    pass


class LocalEmbeddingEngine:
    def __init__(self, model_dir: str = DEFAULT_MODEL_DIR):
        self.model_dir = model_dir
        self._tokenizer = None
        self._session = None
        self._input_names = None

    def initialize(self):
        if not HAS_EMBEDDING_RUNTIME:
            raise RuntimeError("onnxruntime or tokenizers package is missing in Python environment.")
        tokenizer_path = os.path.join(self.model_dir, "tokenizer.json")
        model_path = os.path.join(self.model_dir, RUNTIME_MODEL_FILE)
        if not os.path.exists(model_path):
            model_path = os.path.join(self.model_dir, "model.onnx")
        if not os.path.exists(tokenizer_path) or not os.path.exists(model_path):
            raise FileNotFoundError(f"Embedding model files not found in {self.model_dir}.")
        self._tokenizer = tokenizers.Tokenizer.from_file(tokenizer_path)
        self._tokenizer.enable_truncation(max_length=512)
        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 4
        opts.intra_op_num_threads = 4
        self._session = ort.InferenceSession(model_path, sess_options=opts)
        self._input_names = [inp.name for inp in self._session.get_inputs()]

    def encode(self, texts: List[str], is_query: bool = False, batch_size: int = 32) -> np.ndarray:
        if self._session is None:
            self.initialize()
        prefix = QUERY_PREFIX if is_query else PASSAGE_PREFIX
        formatted = [t if t.startswith((QUERY_PREFIX, PASSAGE_PREFIX)) else prefix + t for t in texts]
        all_embeddings = []
        for i in range(0, len(formatted), batch_size):
            batch = formatted[i:i + batch_size]
            encodings = [self._tokenizer.encode(t) for t in batch]
            max_len = min(512, max(len(e.ids) for e in encodings))
            input_ids_list, attention_mask_list, token_type_ids_list = [], [], []
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
            inputs = {"input_ids": input_ids, "attention_mask": attention_mask}
            if "token_type_ids" in self._input_names:
                inputs["token_type_ids"] = np.array(token_type_ids_list, dtype=np.int64)
            last_hidden_state = self._session.run(None, inputs)[0]
            mask_expanded = np.expand_dims(attention_mask, -1)
            sum_embeddings = np.sum(last_hidden_state * mask_expanded, axis=1)
            sum_mask = np.clip(mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
            mean_pooled = sum_embeddings / sum_mask
            norms = np.linalg.norm(mean_pooled, ord=2, axis=1, keepdims=True)
            all_embeddings.append((mean_pooled / np.clip(norms, a_min=1e-9, a_max=None)).astype(np.float32))
        return np.vstack(all_embeddings)


def sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class KnowledgeCorpusExtractor:
    """Extract canonical entities and enforce collision-free keys before embedding."""

    def __init__(self, knowledge_root: str):
        self.knowledge_root = os.path.abspath(knowledge_root)
        self.course_id = os.path.basename(self.knowledge_root)
        self.source_file_hashes: Dict[str, Dict[str, Any]] = {}

    def _read_json(self, rel_path: str) -> Optional[Dict[str, Any]]:
        full_path = os.path.join(self.knowledge_root, rel_path)
        if not os.path.exists(full_path):
            return None
        self.source_file_hashes[rel_path] = {
            "path": rel_path,
            "sha256": sha256_file(full_path),
            "size_bytes": os.path.getsize(full_path),
            "validation_status": "VERIFIED",
            "freeze_status": "FROZEN",
        }
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _record(
        self,
        records: List[Dict[str, Any]],
        *,
        entity_type: str,
        entity_id: str,
        entity_key: str,
        theme_id: str,
        title: str,
        source_file: str,
        source_key: str,
        authority_level: int,
        authority_name: str,
        origin: str,
        semantic_text: str,
        source_locator: str = "",
        printed_page: str = "",
        pdf_page: str = "",
    ) -> None:
        records.append({
            "course_id": self.course_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "theme_id": theme_id,
            "title": title,
            "canonical_source_file": source_file,
            "canonical_json_path_or_record_key": source_key,
            "authority_level": authority_level,
            "authority_name": authority_name,
            "origin": origin,
            "validation_status": "VERIFIED",
            "freeze_status": "FROZEN",
            "printed_page": printed_page,
            "pdf_page": pdf_page,
            "source_locator": source_locator,
            "semantic_text": semantic_text,
            "entity_key": entity_key,
        })

    def _theme_dirs(self, curr_map: Dict[str, Any]) -> List[Tuple[str, str]]:
        result = []
        for theme in curr_map.get("themes", []):
            t_id = theme.get("theme_id", f"TEMA_{theme.get('theme_no', 0):02d}")
            m = re.search(r"(\d+)$", t_id)
            if m:
                result.append((t_id, f"themes/tema_{int(m.group(1)):02d}"))
        return result

    def extract_all(self) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []

        curr_map = self._read_json("curriculum_map.json") or {}
        for theme in curr_map.get("themes", []):
            theme_id = theme.get("theme_id", f"TEMA_{theme.get('theme_no', 0):02d}")
            theme_title = theme.get("exact_theme_name") or theme.get("theme_title", "")
            theme_intro = theme.get("theme_introduction_verbatim") or theme.get("theme_introduction_summary", "")
            if theme_intro:
                self._record(
                    records,
                    entity_type="curriculum_theme",
                    entity_id=theme_id,
                    entity_key=f"{self.course_id}::curriculum_theme::{theme_id}",
                    theme_id=theme_id,
                    title=theme_title,
                    source_file="curriculum_map.json",
                    source_key=f"themes[{theme_id}]",
                    authority_level=1,
                    authority_name="OFFICIAL_CURRICULUM_FROZEN",
                    origin="official_curriculum",
                    semantic_text=f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). Resmî tanıtım: {theme_intro}",
                    source_locator=str(theme.get("source_locator", "")),
                    printed_page=str(theme.get("page_range", "")),
                )

            for outcome in theme.get("learning_outcomes", []):
                code = outcome.get("outcome_code", "")
                verbatim = outcome.get("outcome_verbatim") or outcome.get("verbatim_statement", "")
                skill = outcome.get("skill_category", "")
                req = outcome.get("assessment_requirement_verbatim", "")
                loc = outcome.get("source_locator", "")
                related_codes = ", ".join(outcome.get("related_official_codes", []))
                self._record(
                    records,
                    entity_type="curriculum_outcome",
                    entity_id=f"{theme_id}::{code}",
                    entity_key=f"{self.course_id}::curriculum_outcome::{theme_id}::{code}",
                    theme_id=theme_id,
                    title=f"Öğrenme Çıktısı {code} ({theme_id}) - {skill}",
                    source_file="curriculum_map.json",
                    source_key=f"themes[{theme_id}].learning_outcomes[{code}]",
                    authority_level=1,
                    authority_name="OFFICIAL_CURRICULUM_FROZEN",
                    origin="official_curriculum",
                    semantic_text=(
                        f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). Öğrenme çıktısı {code}. "
                        f"Resmî ifade: {verbatim}. Alan becerisi: {skill}. İlişkili kodlar: {related_codes}. "
                        f"Resmî değerlendirme şartı: {req}. Kaynak: {loc}."
                    ),
                    source_locator=str(loc),
                    printed_page=str(outcome.get("source_page", "")),
                )
                for pc in outcome.get("process_components_verbatim", []):
                    p_code = pc.get("component_code", "")
                    clean_p_code = p_code.split(")")[-1].strip() if ")" in p_code else p_code
                    self._record(
                        records,
                        entity_type="process_component",
                        entity_id=f"{theme_id}::{code}::{clean_p_code}",
                        entity_key=f"{self.course_id}::process_component::{theme_id}::{code}::{clean_p_code}",
                        theme_id=theme_id,
                        title=f"Süreç Bileşeni {clean_p_code} ({code}, {theme_id}) - {pc.get('component_title', '')}",
                        source_file="curriculum_map.json",
                        source_key=f"themes[{theme_id}].learning_outcomes[{code}].process_components[{clean_p_code}]",
                        authority_level=1,
                        authority_name="OFFICIAL_CURRICULUM_FROZEN",
                        origin="official_curriculum",
                        semantic_text=(
                            f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). Süreç bileşeni {clean_p_code} ({code}). "
                            f"Başlık: {pc.get('component_title', '')}. Resmî ifade: {pc.get('component_verbatim', '')}."
                        ),
                        source_locator=str(pc.get("source_locator", "")),
                    )

        tb_map = self._read_json("textbook_map.json") or {}
        for theme in tb_map.get("themes") or tb_map.get("units_or_themes", []):
            theme_id = theme.get("theme_id", f"TEMA_{theme.get('theme_no', 0):02d}")
            theme_title = theme.get("title") or theme.get("exact_title", "")
            for sec in theme.get("sections", []):
                sec_id = sec.get("section_id", "")
                sec_title = sec.get("title") or sec.get("section_title", "")
                sec_page = str(sec.get("printed_page", "") or sec.get("printed_page_range", "") or sec.get("page_locator", ""))
                sec_pdf = str(sec.get("pdf_page", "") or sec.get("pdf_page_range", ""))
                text_rows = sec.get("texts_and_genres", []) or sec.get("main_texts", [])
                sec_genres = ", ".join(t.get("title", "") for t in text_rows)
                self._record(
                    records,
                    entity_type="textbook_section",
                    entity_id=sec_id,
                    entity_key=f"{self.course_id}::textbook_section::{theme_id}::{sec_id}",
                    theme_id=theme_id,
                    title=f"Ders Kitabı Bölümü: {sec_title}",
                    source_file="textbook_map.json",
                    source_key=f"themes[{theme_id}].sections[{sec_id}]",
                    authority_level=2,
                    authority_name="OFFICIAL_TEXTBOOK_FROZEN",
                    origin="official_textbook",
                    semantic_text=(
                        f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). Ders kitabı bölümü {sec_id}. "
                        f"Başlık: {sec_title}. Sayfa: {sec_page}. Metin ve türler: {sec_genres}."
                    ),
                    source_locator=f"s. {sec_page}",
                    printed_page=sec_page,
                    pdf_page=sec_pdf,
                )
                for act in sec.get("activities", []):
                    act_id = act.get("activity_id", "")
                    act_title = act.get("title") or act.get("exact_title") or act.get("activity_title") or act_id
                    act_page = str(act.get("printed_page", "") or act.get("page_locator", ""))
                    self._record(
                        records,
                        entity_type="textbook_activity",
                        entity_id=act_id,
                        entity_key=f"{self.course_id}::textbook_activity::{theme_id}::{act_id}",
                        theme_id=theme_id,
                        title=f"Ders Kitabı Etkinliği: {act_title}",
                        source_file="textbook_map.json",
                        source_key=f"themes[{theme_id}].sections[{sec_id}].activities[{act_id}]",
                        authority_level=2,
                        authority_name="OFFICIAL_TEXTBOOK_FROZEN",
                        origin="official_textbook",
                        semantic_text=(
                            f"Ders: {self.course_id}. Tema: {theme_title} ({theme_id}). Ders kitabı etkinliği {act_id}. "
                            f"Başlık: {act_title}. Tür: {act.get('type', '')}. Sayfa: {act_page}. "
                            f"Beklenen öğrenci kanıtı: {act.get('expected_student_evidence', '')}. "
                            f"İlgili form: {act.get('linked_form_id', '')}."
                        ),
                        source_locator=f"s. {act_page}",
                        printed_page=act_page,
                        pdf_page=str(act.get("pdf_page", "")),
                    )

        tb_forms = self._read_json("textbook_forms_index.json") or {}
        for form in tb_forms.get("forms", []):
            form_id = form.get("form_id", "")
            linked_themes = form.get("linked_theme_ids", [])
            first_theme = linked_themes[0] if linked_themes else ""
            p_page = str(form.get("printed_page", ""))
            pdf_page = str(form.get("pdf_page", ""))
            struct = form.get("structure_details", {})
            self._record(
                records,
                entity_type="textbook_form",
                entity_id=form_id,
                entity_key=f"{self.course_id}::textbook_form::{form_id}",
                theme_id=first_theme,
                title=f"Ölçme Aracı: {form.get('printed_title') or form.get('title', '')} ({form.get('structural_type', '')})",
                source_file="textbook_forms_index.json",
                source_key=f"forms[{form_id}]",
                authority_level=3,
                authority_name="OFFICIAL_TEXTBOOK_FORM_FROZEN",
                origin="official_textbook",
                semantic_text=(
                    f"Ders: {self.course_id}. Temalar: {', '.join(linked_themes)}. Form {form_id}. "
                    f"Tür: {form.get('structural_type', '')}. Başlık: {form.get('printed_title') or form.get('title', '')}. "
                    f"Değerlendirici: {form.get('evaluator', '')}. Sayfa: {p_page}. "
                    f"Ölçüt alanları: {', '.join(struct.get('criteria_categories', []))}. "
                    f"Yapı: {struct.get('structure_note', '')}."
                ),
                source_locator=f"s. {p_page} (PDF: {pdf_page})",
                printed_page=p_page,
                pdf_page=pdf_page,
            )

        for t_id, t_dir in self._theme_dirs(curr_map):
            align_data = self._read_json(f"{t_dir}/alignment.json") or {}
            for al in align_data.get("alignments", []):
                code = al.get("outcome_code", "")
                cov = al.get("primary_coverage", "")
                tb_loc = ", ".join(al.get("textbook_locators", []))
                p_loc = al.get("provenance", {}).get("program_locator", "")
                self._record(
                    records,
                    entity_type="alignment_record",
                    entity_id=f"ALIGN_{t_id}_{code}",
                    entity_key=f"{self.course_id}::alignment_record::{t_id}::{code}",
                    theme_id=t_id,
                    title=f"Program-Kitap Hizalaması: {code} ({cov})",
                    source_file=f"{t_dir}/alignment.json",
                    source_key=f"alignments[{code}]",
                    authority_level=4,
                    authority_name="VALIDATED_ALIGNMENT",
                    origin="validated_alignment",
                    semantic_text=(
                        f"Ders: {self.course_id}. Tema: {t_id}. Hizalama {code}. Kapsama: {cov}. "
                        f"Üretim kararı: {al.get('production_decision', '')}. Öncelik: {al.get('priority', '')}. "
                        f"Ders kitabı etkinlikleri: {', '.join(al.get('textbook_activity_ids', []))}. "
                        f"Kalan boşluk: {al.get('remaining_gap', '')}."
                    ),
                    source_locator=tb_loc or p_loc,
                )

            gap_data = self._read_json(f"{t_dir}/gap_analysis.json") or {}
            for g in gap_data.get("gaps", []) or gap_data.get("gap_records", []):
                g_id = g.get("gap_id") or f"GAP_{t_id}_{g.get('outcome_code', '')}"
                code = g.get("outcome_code", "")
                self._record(
                    records,
                    entity_type="remaining_gap",
                    entity_id=g_id,
                    entity_key=f"{self.course_id}::remaining_gap::{t_id}::{g_id}",
                    theme_id=t_id,
                    title=f"Boşluk Analizi: {code} - {g.get('primary_coverage', '')}",
                    source_file=f"{t_dir}/gap_analysis.json",
                    source_key=f"gaps[{g_id}]",
                    authority_level=5,
                    authority_name="VALIDATED_GAP",
                    origin="validated_gap",
                    semantic_text=(
                        f"Ders: {self.course_id}. Tema: {t_id}. Boşluk {g_id}. Hedef çıktı: {code}. "
                        f"Kapsama: {g.get('primary_coverage', '')}. Kalan boşluk: {g.get('remaining_gap', '')}. "
                        f"Resmî şart: {g.get('program_requirement_verbatim') or g.get('program_assessment_requirement_verbatim', '')}. "
                        f"Ders kitabı karşılığı: {g.get('textbook_provides', '')}. "
                        f"Üretim kararı: {g.get('production_decision', '')}."
                    ),
                )

            needs_data = self._read_json(f"{t_dir}/needs.json") or {}
            for n in needs_data.get("needs", []):
                n_id = n.get("need_id", "")
                outcomes = ", ".join(n.get("targeted_learning_outcomes", []))
                self._record(
                    records,
                    entity_type="instructional_need",
                    entity_id=n_id,
                    entity_key=f"{self.course_id}::instructional_need::{t_id}::{n_id}",
                    theme_id=t_id,
                    title=f"Öğretimsel İhtiyaç: {n_id} ({outcomes})",
                    source_file=f"{t_dir}/needs.json",
                    source_key=f"needs[{n_id}]",
                    authority_level=6,
                    authority_name="VALIDATED_RESOURCE_PLAN",
                    origin="validated_resource_plan",
                    semantic_text=(
                        f"Ders: {self.course_id}. Tema: {t_id}. Öğretimsel ihtiyaç {n_id}. Hedef çıktılar: {outcomes}. "
                        f"Beklenen öğrenci kanıtı: {n.get('expected_student_evidence', '')}. "
                        f"Bilişsel talep: {n.get('cognitive_demand', '')}. Değerlendirme ihtiyacı: {n.get('assessment_need', '')}."
                    ),
                )

            rp_data = self._read_json(f"{t_dir}/resource_plan.json") or {}
            for r in rp_data.get("resources", []) or rp_data.get("resource_plans", []):
                r_id = r.get("resource_plan_id") or r.get("resource_id", "")
                outcomes = ", ".join(r.get("target_outcomes", []))
                self._record(
                    records,
                    entity_type="resource_plan",
                    entity_id=r_id,
                    entity_key=f"{self.course_id}::resource_plan::{t_id}::{r_id}",
                    theme_id=t_id,
                    title=f"Kaynak Planı: {r_id} ({r.get('resource_type', '')})",
                    source_file=f"{t_dir}/resource_plan.json",
                    source_key=f"resources[{r_id}]",
                    authority_level=6,
                    authority_name="VALIDATED_RESOURCE_PLAN",
                    origin="validated_resource_plan",
                    semantic_text=(
                        f"Ders: {self.course_id}. Tema: {t_id}. Kaynak planı {r_id}. Tür: {r.get('resource_type', '')}. "
                        f"Hedef çıktılar: {outcomes}. Öncelik: {r.get('priority', '')}. "
                        f"Üretim kararı: {r.get('production_decision', '')}. Amaç: {r.get('purpose', '')}. "
                        f"Beklenen kanıt: {r.get('expected_student_evidence', '')}."
                    ),
                )

        prod_manifest = self._read_json("production/production_manifest.json") or {}
        artifacts, _, gap_alias_to_artifact_id, provenance_by_gap = build_artifact_maps(prod_manifest)
        for artifact in artifacts:
            artifact_id = artifact["artifact_id"]
            themes = artifact.get("covered_themes", [])
            outcomes = artifact.get("covered_outcomes", [])
            aliases = artifact.get("covered_gap_instances", [])
            # Multi-theme reusable artifacts intentionally have empty metadata theme_id so a theme filter cannot hide them.
            metadata_theme = themes[0] if len(themes) == 1 else ""
            reqs, gaps = [], []
            for alias in aliases:
                prov = provenance_by_gap.get(alias, {})
                req = prov.get("official_requirement_verbatim")
                gap = prov.get("exact_remaining_gap")
                if req and req not in reqs:
                    reqs.append(req)
                if gap and gap not in gaps:
                    gaps.append(gap)
            loc_c = artifact.get("source_locators", {}).get("curriculum", "")
            loc_tb = artifact.get("source_locators", {}).get("textbook", "")
            self._record(
                records,
                entity_type="assessment_artifact",
                entity_id=artifact_id,
                entity_key=f"{self.course_id}::assessment_artifact::{artifact_id}",
                theme_id=metadata_theme,
                title=artifact.get("title", f"Assessment Artifact: {artifact_id}"),
                source_file="production/production_manifest.json",
                source_key=f"production_queue[{artifact_id}]",
                authority_level=7,
                authority_name="VALIDATED_PRODUCTION_PLAN",
                origin="validated_production_plan",
                semantic_text=(
                    f"Ders: {self.course_id}. Assessment artifact {artifact_id}. Başlık: {artifact.get('title', '')}. "
                    f"Temalar: {', '.join(themes)}. Hedef çıktılar: {', '.join(outcomes)}. "
                    f"Gap aliasları: {', '.join(aliases)}. Alan: {artifact.get('skill_domain', '')}. "
                    f"Assessment family: {artifact.get('assessment_family', '')}. Uygulama: {artifact.get('selected_implementation', '')}. "
                    f"Reuse policy: {artifact.get('reuse_policy', '')}. Resmî gereksinimler: {' | '.join(reqs)}. "
                    f"Kalan boşluklar: {' | '.join(gaps)}."
                ),
                source_locator=f"Curriculum: {loc_c} | Textbook: {loc_tb}",
            )

        tb_blocks = self._read_json("production/teaching_blocks.json") or {}
        for blk in tb_blocks.get("blocks", []) or tb_blocks.get("teaching_blocks", []):
            b_id = blk.get("block_id", "")
            b_theme = blk.get("theme_id", "")
            outcomes = blk.get("curriculum_outcomes", []) or blk.get("targeted_outcomes", [])
            required = blk.get("required_resource_ids", []) or blk.get("required_material_ids", [])
            hours = blk.get("approximate_lesson_hours", blk.get("allocated_hours"))
            self._record(
                records,
                entity_type="teaching_block",
                entity_id=b_id,
                entity_key=f"{self.course_id}::teaching_block::{b_theme}::{b_id}",
                theme_id=b_theme,
                title=f"Öğretim Bloğu: {blk.get('title', '')}",
                source_file="production/teaching_blocks.json",
                source_key=f"blocks[{b_id}]",
                authority_level=7,
                authority_name="VALIDATED_PRODUCTION_PLAN",
                origin="validated_production_plan",
                semantic_text=(
                    f"Ders: {self.course_id}. Tema: {b_theme}. Öğretim bloğu {b_id}. Başlık: {blk.get('title', '')}. "
                    f"Ders saati: {hours if hours is not None else 'UNSPECIFIED_BY_SOURCE'}. "
                    f"Hedef çıktılar: {', '.join(outcomes)}. Gerekli kaynaklar: {', '.join(required)}."
                ),
                source_locator=str(blk.get("lesson_hours_status", "")),
            )

        sbp = self._read_json("production/school_based_planning_options.json") or {}
        for theme in sbp.get("themes", []):
            t_id = theme.get("theme_id", "")
            t_title = theme.get("theme_title", "")
            for opt in theme.get("options", []):
                opt_id = opt.get("option_id", "")
                self._record(
                    records,
                    entity_type="school_based_option",
                    entity_id=opt_id,
                    entity_key=f"{self.course_id}::school_based_option::{t_id}::{opt_id}",
                    theme_id=t_id,
                    title=f"Okul Temelli Seçenek: {opt.get('title', '')}",
                    source_file="production/school_based_planning_options.json",
                    source_key=f"themes[{t_id}].options[{opt_id}]",
                    authority_level=8,
                    authority_name="PEDAGOGICAL_RECOMMENDATION",
                    origin="pedagogical_recommendation",
                    semantic_text=(
                        f"Ders: {self.course_id}. Tema: {t_title} ({t_id}). Okul temelli seçenek {opt_id}. "
                        f"Başlık: {opt.get('title', '')}. Kategori: {opt.get('category', '')}. "
                        f"Süre: {opt.get('duration_hours', '')} saat. İlişkili çıktılar: {', '.join(opt.get('linked_outcomes', []))}. "
                        f"Gerekçe: {opt.get('rationale', '')}. Öğrenci eylemi: {opt.get('expected_student_action', '')}. "
                        f"Kanıt: {opt.get('expected_student_evidence', '')}."
                    ),
                    source_locator=f"{opt.get('duration_hours', '')} saat",
                )

        seen_keys: Dict[str, str] = {}
        validated: List[Dict[str, Any]] = []
        for record in records:
            key = record["entity_key"]
            if key in seen_keys:
                raise DuplicateCanonicalKeyError(
                    f"DUPLICATE_CANONICAL_KEY: '{key}' from '{seen_keys[key]}' and '{record['canonical_source_file']}'."
                )
            seen_keys[key] = record["canonical_source_file"]
            record["content_hash"] = sha256_text(record["semantic_text"])
            record["source_file_hash"] = self.source_file_hashes.get(record["canonical_source_file"], {}).get("sha256", "")
            record["embedding_model"] = BASE_EMBEDDING_MODEL
            record["embedding_dimension"] = EMBEDDING_DIMENSION
            now = datetime.now(timezone.utc).isoformat()
            record["created_at"] = now
            record["updated_at"] = now
            validated.append(record)
        return validated


class KnowledgeIndexer:
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
        model_path = os.path.join(self.model_dir, RUNTIME_MODEL_FILE)
        if not os.path.exists(model_path):
            model_path = os.path.join(self.model_dir, "model.onnx")
        return sha256_file(model_path) if os.path.exists(model_path) else "MODEL_FILE_NOT_FOUND"

    def _current_production_info(self) -> Dict[str, Any]:
        path = os.path.join(self.knowledge_root, "production", "production_manifest.json")
        if not os.path.exists(path):
            return {"status": "PRODUCTION_MANIFEST_MISSING"}
        try:
            with open(path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            artifacts, _, alias_map, _ = build_artifact_maps(manifest)
        except (json.JSONDecodeError, ProductionSchemaError) as exc:
            return {"status": "PRODUCTION_SCHEMA_MISMATCH", "message": str(exc)}
        return {
            "status": "PASS",
            "schema_version": str(manifest.get("schema_version")),
            "fingerprint": sha256_file(path),
            "artifact_count": len(artifacts),
            "gap_alias_count": len(alias_map),
        }

    def check_status(self) -> Dict[str, Any]:
        prod_info = self._current_production_info()
        if prod_info.get("status") != "PASS":
            return {"course_id": self.course_id, **prod_info}

        if not os.path.exists(self.manifest_path) or not os.path.exists(self.db_path):
            return {"status": "INDEX_MISSING", "course_id": self.course_id, "message": "Index database or manifest does not exist. Build required."}
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            return {"status": "INDEX_MANIFEST_INVALID", "course_id": self.course_id, "message": str(exc)}

        if manifest.get("vector_extension") != SELECTED_VECTOR_BACKEND:
            return {"status": "VECTOR_BACKEND_MISMATCH", "course_id": self.course_id}
        if (
            (manifest.get("base_embedding_model") or manifest.get("embedding_model")) != BASE_EMBEDDING_MODEL
            or manifest.get("embedding_dimension") != EMBEDDING_DIMENSION
        ):
            return {"status": "EMBEDDING_MODEL_MISMATCH", "course_id": self.course_id}
        current_model_sha = self.get_model_file_sha256()
        indexed_model_sha = manifest.get("model_file_sha256")
        if indexed_model_sha and current_model_sha != "MODEL_FILE_NOT_FOUND" and current_model_sha != indexed_model_sha:
            return {"status": "EMBEDDING_ARTIFACT_MISMATCH", "course_id": self.course_id}

        if manifest.get("production_schema_version") != PRODUCTION_SCHEMA_VERSION:
            return {"status": "INDEX_STALE", "course_id": self.course_id, "message": "Production schema version changed; rebuild required."}
        if manifest.get("production_schema_fingerprint") != prod_info["fingerprint"]:
            return {"status": "INDEX_STALE", "course_id": self.course_id, "message": "Production manifest fingerprint changed; rebuild required."}
        if manifest.get("artifact_identity_field") != "artifact_id":
            return {"status": "INDEX_STALE", "course_id": self.course_id, "message": "Legacy artifact identity detected; rebuild required."}

        mismatched_files = []
        for src in manifest.get("source_files", []):
            rel_path = src["path"]
            full_path = os.path.join(self.knowledge_root, rel_path)
            if not os.path.exists(full_path):
                mismatched_files.append({"file": rel_path, "reason": "MISSING"})
                continue
            current_hash = sha256_file(full_path)
            if current_hash != src["sha256"]:
                mismatched_files.append({"file": rel_path, "reason": "HASH_MISMATCH"})
        if mismatched_files:
            return {"status": "INDEX_STALE", "course_id": self.course_id, "mismatched_files": mismatched_files, "message": "Canonical source files changed; rebuild required."}

        try:
            conn = self._get_db_connection()
            artifact_rows = conn.execute("SELECT entity_id, entity_key FROM metadata WHERE entity_type='assessment_artifact'").fetchall()
            duplicate_key_count = conn.execute("SELECT COUNT(*) FROM (SELECT entity_key FROM metadata GROUP BY entity_key HAVING COUNT(*) > 1)").fetchone()[0]
            conn.close()
        except sqlite3.Error as exc:
            return {"status": "INDEX_DB_INVALID", "course_id": self.course_id, "message": str(exc)}
        if len(artifact_rows) != prod_info["artifact_count"] or duplicate_key_count != 0:
            return {"status": "INDEX_DB_INVALID", "course_id": self.course_id, "message": "Assessment artifact row count or unique-key gate failed."}
        if any(str(row[0]).startswith("MAT_") for row in artifact_rows):
            return {"status": "INDEX_DB_INVALID", "course_id": self.course_id, "message": "Historical MAT_* gap ID used as artifact identity."}

        return {
            "status": "INDEX_FRESH",
            "course_id": self.course_id,
            "indexed_record_count": manifest.get("indexed_record_count", 0),
            "indexed_entity_types": manifest.get("indexed_entity_types", []),
            "index_updated_at": manifest.get("index_updated_at"),
            "database_engine": manifest.get("database_engine"),
            "vector_extension": manifest.get("vector_extension"),
            "base_embedding_model": manifest.get("base_embedding_model"),
            "model_file_sha256": manifest.get("model_file_sha256"),
            "production_schema_version": manifest.get("production_schema_version"),
            "production_artifact_count": manifest.get("production_artifact_count"),
            "production_gap_alias_count": manifest.get("production_gap_alias_count"),
        }

    def build_index(self, force: bool = False) -> Dict[str, Any]:
        os.makedirs(self.index_dir, exist_ok=True)
        prod_info = self._current_production_info()
        if prod_info.get("status") != "PASS":
            raise ProductionSchemaError(prod_info.get("message") or prod_info.get("status"))

        extractor = KnowledgeCorpusExtractor(self.knowledge_root)
        records = extractor.extract_all()
        if not records:
            raise ValueError(f"No canonical records found in {self.knowledge_root}")

        print(f"[*] Extracted {len(records)} canonical entities from {self.course_id}.", flush=True)
        texts = [r["semantic_text"] for r in records]
        embeddings = self.embedding_engine.encode(texts, is_query=False, batch_size=32)

        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        conn = self._get_db_connection()
        cur = conn.cursor()
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
            )
        """)
        cur.execute("""
            CREATE VIRTUAL TABLE fts_entities USING fts5(
                entity_key UNINDEXED, entity_id, entity_type, theme_id, title, semantic_text,
                tokenize='unicode61'
            )
        """)
        if not HAS_SQLITE_VEC:
            raise RuntimeError("sqlite-vec is required for production index rebuild.")
        cur.execute(f"CREATE VIRTUAL TABLE vec_entities USING vec0(rowid INTEGER PRIMARY KEY, embedding float[{EMBEDDING_DIMENSION}])")

        entity_types = set()
        for idx, r in enumerate(records):
            entity_types.add(r["entity_type"])
            cur.execute("""
                INSERT INTO metadata (
                    entity_key, course_id, entity_type, entity_id, theme_id,
                    canonical_source_file, canonical_json_path_or_record_key,
                    authority_level, authority_name, origin, validation_status, freeze_status,
                    printed_page, pdf_page, source_locator, content_hash, source_file_hash,
                    embedding_model, embedding_dimension, semantic_text, title, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r["entity_key"], r["course_id"], r["entity_type"], r["entity_id"], r["theme_id"],
                r["canonical_source_file"], r["canonical_json_path_or_record_key"], r["authority_level"],
                r["authority_name"], r["origin"], r["validation_status"], r["freeze_status"],
                r["printed_page"], r["pdf_page"], r["source_locator"], r["content_hash"], r["source_file_hash"],
                r["embedding_model"], r["embedding_dimension"], r["semantic_text"], r["title"], r["created_at"], r["updated_at"],
            ))
            row_id = cur.lastrowid
            cur.execute(
                "INSERT INTO fts_entities(entity_key, entity_id, entity_type, theme_id, title, semantic_text) VALUES (?, ?, ?, ?, ?, ?)",
                (r["entity_key"], r["entity_id"], r["entity_type"], r["theme_id"], r["title"], r["semantic_text"]),
            )
            cur.execute(
                "INSERT INTO vec_entities(rowid, embedding) VALUES (?, ?)",
                (row_id, sqlite_vec.serialize_float32(embeddings[idx].tolist())),
            )
        conn.commit()

        duplicate_keys = conn.execute("SELECT entity_key FROM metadata GROUP BY entity_key HAVING COUNT(*) > 1").fetchall()
        artifact_ids = [row[0] for row in conn.execute("SELECT entity_id FROM metadata WHERE entity_type='assessment_artifact' ORDER BY entity_id").fetchall()]
        conn.close()
        if duplicate_keys:
            raise DuplicateCanonicalKeyError(f"Duplicate keys persisted after build: {duplicate_keys}")
        if len(artifact_ids) != prod_info["artifact_count"] or any(a.startswith("MAT_") for a in artifact_ids):
            raise ProductionSchemaError("Assessment artifact identity gate failed after index build.")

        index_content_hash = sha256_text("".join(sorted(r["content_hash"] for r in records)))
        model_sha256 = self.get_model_file_sha256()
        now = datetime.now(timezone.utc).isoformat()
        manifest = {
            "schema_version": "2.1",
            "course_id": self.course_id,
            "index_created_at": now,
            "index_updated_at": now,
            "requested_backend": REQUESTED_VECTOR_BACKEND,
            "selected_backend": SELECTED_VECTOR_BACKEND,
            "backend_selection_status": BACKEND_SELECTION_STATUS,
            "backend_selection_reason": BACKEND_SELECTION_REASON,
            "database_engine": f"SQLite {sqlite3.sqlite_version} + {SELECTED_VECTOR_BACKEND}",
            "vector_extension": SELECTED_VECTOR_BACKEND,
            "vector_extension_version": getattr(sqlite_vec, "__version__", "unknown"),
            "sqlite_version": sqlite3.sqlite_version,
            "runtime_platform": platform.platform(),
            "runtime_architecture": platform.machine(),
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
            "production_schema_version": PRODUCTION_SCHEMA_VERSION,
            "production_schema_fingerprint": prod_info["fingerprint"],
            "artifact_identity_field": "artifact_id",
            "production_artifact_count": prod_info["artifact_count"],
            "production_gap_alias_count": prod_info["gap_alias_count"],
            "indexed_entity_types": sorted(entity_types),
            "indexed_record_count": len(records),
            "source_files": list(extractor.source_file_hashes.values()),
            "index_content_hash": index_content_hash,
            "build_status": "SUCCESS",
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        type_counts: Dict[str, int] = {}
        for r in records:
            type_counts[r["entity_type"]] = type_counts.get(r["entity_type"], 0) + 1
        report = [
            "# Knowledge Index Validation Report",
            "",
            f"- **Course ID**: {self.course_id}",
            f"- **Build Timestamp**: {now}",
            "- **Status**: SUCCESS",
            f"- **Total Indexed Records**: {len(records)}",
            f"- **Production Schema**: {PRODUCTION_SCHEMA_VERSION}",
            "- **Artifact Identity**: `artifact_id`",
            f"- **Canonical Assessment Artifacts**: {prod_info['artifact_count']}",
            f"- **Historical Gap Aliases**: {prod_info['gap_alias_count']}",
            f"- **Production Manifest Fingerprint**: `{prod_info['fingerprint']}`",
            f"- **Database Engine**: {manifest['database_engine']}",
            f"- **Vector Backend**: `{SELECTED_VECTOR_BACKEND}`",
            f"- **Base Embedding Model**: `{BASE_EMBEDDING_MODEL}` (Dim: {EMBEDDING_DIMENSION})",
            f"- **Model File SHA256**: `{model_sha256}`",
            f"- **Index Content Hash**: `{index_content_hash}`",
            "",
            "## Indexed Entity Types & Counts",
        ]
        for etype, count in sorted(type_counts.items()):
            report.append(f"- **{etype}**: {count}")
        report += ["", "## Source Files Fingerprint"]
        for sf in manifest["source_files"]:
            report.append(f"- `{sf['path']}`: SHA-256 `{sf['sha256']}` ({sf['size_bytes']} bytes) - VERIFIED")
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report) + "\n")

        final_status = self.check_status()
        if final_status.get("status") != "INDEX_FRESH":
            raise RuntimeError(f"Post-build index gate failed: {final_status}")
        print(f"[✓] Built fresh index at {self.db_path} ({len(records)} records).", flush=True)
        return manifest

    def search_hybrid(
        self,
        query: str,
        top_k: int = 8,
        theme_id: Optional[str] = None,
        entity_types: Optional[List[str]] = None,
        authority_max: int = 8,
    ) -> List[Dict[str, Any]]:
        if self.check_status().get("status") != "INDEX_FRESH":
            raise RuntimeError("Hybrid retrieval requires INDEX_FRESH.")
        conn = self._get_db_connection()
        cur = conn.cursor()
        query_vec = self.embedding_engine.encode([query], is_query=True)[0]
        vec_blob = sqlite_vec.serialize_float32(query_vec.tolist())
        cur.execute("SELECT rowid, distance FROM vec_entities WHERE embedding MATCH ? AND k = ?", (vec_blob, top_k * 3))
        vector_candidates = [(row[0], float(row[1])) for row in cur.fetchall()]

        clean_terms = [
            t.strip() for t in query.replace(":", " ").replace("-", " ").replace("?", "").replace(".", " ").split()
            if len(t.strip()) > 1
        ]
        fts_candidates: List[Tuple[int, float]] = []
        if clean_terms:
            fts_query = " OR ".join(f'"{t}"' for t in clean_terms[:8])
            try:
                cur.execute("""
                    SELECT m.id, f.rank
                    FROM fts_entities f JOIN metadata m ON f.entity_key = m.entity_key
                    WHERE fts_entities MATCH ? ORDER BY f.rank LIMIT ?
                """, (fts_query, top_k * 3))
                fts_candidates = [(row[0], float(row[1])) for row in cur.fetchall()]
            except sqlite3.OperationalError:
                pass

        rrf_scores: Dict[int, float] = {}
        vector_ranks, fts_ranks = {}, {}
        for rank, (rec_id, _) in enumerate(vector_candidates, 1):
            vector_ranks[rec_id] = rank
            rrf_scores[rec_id] = rrf_scores.get(rec_id, 0.0) + 1.0 / (60.0 + rank)
        for rank, (rec_id, _) in enumerate(fts_candidates, 1):
            fts_ranks[rec_id] = rank
            rrf_scores[rec_id] = rrf_scores.get(rec_id, 0.0) + 1.0 / (60.0 + rank)

        results = []
        for rec_id, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
            row = cur.execute("SELECT * FROM metadata WHERE id=?", (rec_id,)).fetchone()
            if not row:
                continue
            item = dict(row)
            if theme_id and item["theme_id"] and item["theme_id"] != theme_id:
                continue
            if entity_types and item["entity_type"] not in entity_types:
                continue
            if item["authority_level"] > authority_max:
                continue
            item["rrf_score"] = round(score, 6)
            item["vector_rank"] = vector_ranks.get(rec_id)
            item["fts_rank"] = fts_ranks.get(rec_id)
            results.append(item)
            if len(results) >= top_k:
                break
        conn.close()
        return results


def main():
    parser = argparse.ArgumentParser(description="TYMM Knowledge Index CLI")
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "rebuild"):
        p = subs.add_parser(name)
        p.add_argument("--knowledge-root", required=True, help="Path to course knowledge directory (e.g. courses/TDE_9)")
    p_status = subs.add_parser("status")
    p_status.add_argument("--knowledge-root", required=True)
    p_query = subs.add_parser("query")
    p_query.add_argument("--knowledge-root", required=True)
    p_query.add_argument("--query", required=True)
    p_query.add_argument("--top-k", type=int, default=8)
    p_query.add_argument("--theme-id")
    p_query.add_argument("--entity-type")
    args = parser.parse_args()
    indexer = KnowledgeIndexer(args.knowledge_root)
    if args.command in ("build", "rebuild"):
        print(json.dumps(indexer.build_index(force=True), indent=2, ensure_ascii=False))
    elif args.command == "status":
        print(json.dumps(indexer.check_status(), indent=2, ensure_ascii=False))
    else:
        etypes = [e.strip() for e in args.entity_type.split(",")] if args.entity_type else None
        print(json.dumps(indexer.search_hybrid(args.query, args.top_k, args.theme_id, etypes), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
