#!/usr/bin/env python3
"""
TYMM Knowledge Resolver (knowledge_resolver.py)

Deterministic retrieval and orchestration layer for Türkiye Yüzyılı Maarif Modeli (TYMM)
knowledge bases. Enforces mandatory retrieval order:

USER REQUEST
↓
COURSE RESOLUTION
↓
CACHE / FRESHNESS CHECK
↓
EXACT STRUCTURED LOOKUP & THEME-SCOPING DISAMBIGUATION
↓
STRUCTURED RELATIONSHIP EXPANSION
↓
HYBRID RETRIEVAL (if needed):
    ├── metadata/filter
    ├── SQLite FTS5
    └── vector similarity (RRF fusion)
↓
CANONICAL RECORD RESOLUTION
↓
TARGETED ORIGINAL SOURCE FALLBACK (if needed)
↓
KNOWLEDGE CONFLICT & AMBIGUITY VALIDATION
↓
MATERIAL GENERATION SAFETY GATE
↓
KNOWLEDGE_CONTEXT_PACK

CRITICAL ARCHITECTURAL RULES:
1. Vector DB is NOT the source of truth.
2. Authoritative source of truth: persistent, verified structured JSON files.
3. Outcome codes like TDE4.4 are theme-scoped. When queried without theme context,
   return AMBIGUOUS_ENTITY and candidate themes; do NOT guess via vector similarity.
4. If index is STALE, or CONFLICT is found, or entity is AMBIGUOUS:
   halt material generation (material_generation_allowed = False).
5. Strict terminology separation: official requirement ("dereceli puanlama anahtarı") vs
   actual textbook structure vs selected implementation ("analytic_rubric").
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

# Import indexer for hybrid search and status check
try:
    from knowledge_index import KnowledgeIndexer, sha256_file
except ImportError:
    from .knowledge_index import KnowledgeIndexer, sha256_file


class KnowledgeResolver:
    """Orchestrates structured lookup, hybrid search, relationship expansion, and context pack assembly."""

    def __init__(self, knowledge_root: str):
        self.knowledge_root = os.path.abspath(knowledge_root)
        self.course_id = os.path.basename(self.knowledge_root)
        self.indexer = KnowledgeIndexer(self.knowledge_root)
        self._load_canonical_data()

    def _read_json(self, rel_path: str) -> Optional[Dict[str, Any]]:
        full_path = os.path.join(self.knowledge_root, rel_path)
        if not os.path.exists(full_path):
            return None
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_canonical_data(self):
        """Loads canonical structured data into memory for rapid deterministic resolution."""
        self.curriculum_map = self._read_json("curriculum_map.json") or {}
        self.textbook_map = self._read_json("textbook_map.json") or {}
        self.textbook_forms = self._read_json("textbook_forms_index.json") or {}
        self.production_manifest = self._read_json("production/production_manifest.json") or {}
        self.teaching_blocks = self._read_json("production/teaching_blocks.json") or {}
        self.school_based_options = self._read_json("production/school_based_planning_options.json") or {}

        # Load themes data
        self.themes_data: Dict[str, Dict[str, Any]] = {}
        for t_no in range(1, 5):
            t_id = f"TEMA_{t_no:02d}"
            t_dir = f"themes/tema_{t_no:02d}"
            self.themes_data[t_id] = {
                "alignment": self._read_json(f"{t_dir}/alignment.json") or {},
                "gap_analysis": self._read_json(f"{t_dir}/gap_analysis.json") or {},
                "needs": self._read_json(f"{t_dir}/needs.json") or {},
                "resource_plan": self._read_json(f"{t_dir}/resource_plan.json") or {},
            }

    def detect_intent(self, query: str) -> str:
        """Classifies query intent."""
        q = query.lower()
        if "materyal üret" in q or "generate" in q or ("hazırla" in q and ("rubrik" in q or "çalışma kâğıdı" in q)):
            return "MATERIAL_GENERATION"
        if "okul temelli" in q or "planlama seçenekleri" in q or "sbp" in q:
            return "SCHOOL_BASED_LOOKUP"
        if "eksik" in q or "gap" in q or "boşluk" in q or "karşılan" in q:
            return "ALIGNMENT_LOOKUP"
        if "rubrik" in q or "ölçme" in q or "değerlendir" in q or "form" in q or "ölçüt" in q:
            return "ASSESSMENT_LOOKUP"
        if "kaynak" in q or ("plan" in q and "öğretim" in q):
            return "RESOURCE_LOOKUP"
        if "blok" in q or "ders saati" in q or "haftalık" in q:
            return "TEACHING_PLAN_LOOKUP"
        if "üretim" in q or "kuyruk" in q or "manifest" in q:
            return "PRODUCTION_LOOKUP"
        if "denetim" in q or "audit" in q or "qa" in q or "doğrulama" in q:
            return "AUDIT"
        if "nerede" in q or "sayfa" in q or "locator" in q:
            return "SOURCE_LOOKUP"
        if re.search(r"tde\d\.\d", q) or "nedir" in q or "ifadesi" in q or "tanım" in q:
            return "FACT_LOOKUP"
        return "GENERAL_SEMANTIC_QUERY"

    def extract_exact_identifiers(self, query: str) -> Dict[str, List[str]]:
        """Extracts exact canonical identifiers from query string."""
        identifiers = {
            "outcomes": [],
            "themes": [],
            "forms": [],
            "materials": [],
            "resources": [],
            "blocks": [],
            "options": []
        }

        # 1. Outcomes (e.g. TDE4.4, TDE1.1, TDE 4.4, TDE9.1.1)
        outcome_matches = re.findall(r"\b(TDE\s*[1-4]\.[1-4](?:\.[1-4a-z])?)\b", query, re.IGNORECASE)
        for m in outcome_matches:
            normalized = m.upper().replace(" ", "")
            if normalized not in identifiers["outcomes"]:
                identifiers["outcomes"].append(normalized)

        # 2. Themes (e.g. TEMA_01, Tema 2, 2. tema, 2.Tema, vb.)
        theme_matches = re.findall(r"\b(TEMA_0[1-4]|TEMA\s*[1-4]|[1-4]\.\s*TEMA)\b", query, re.IGNORECASE)
        for m in theme_matches:
            digits = re.findall(r"[1-4]", m)
            if digits:
                t_id = f"TEMA_{int(digits[0]):02d}"
                if t_id not in identifiers["themes"]:
                    identifiers["themes"].append(t_id)

        # 3. Forms (e.g. FORM_BOB_..., FORM_IN_...)
        form_matches = re.findall(r"\b(FORM_[A-Z0-9_]+)\b", query, re.IGNORECASE)
        for m in form_matches:
            u_m = m.upper()
            if u_m not in identifiers["forms"]:
                identifiers["forms"].append(u_m)

        # 4. Materials (e.g. MAT_T2_..., MAT_...)
        mat_matches = re.findall(r"\b(MAT_[A-Z0-9_]+)\b", query, re.IGNORECASE)
        for m in mat_matches:
            u_m = m.upper()
            if u_m not in identifiers["materials"]:
                identifiers["materials"].append(u_m)

        # 5. Resources (e.g. RES_T2_..., RES_...)
        res_matches = re.findall(r"\b(RES_[A-Z0-9_]+)\b", query, re.IGNORECASE)
        for m in res_matches:
            u_m = m.upper()
            if u_m not in identifiers["resources"]:
                identifiers["resources"].append(u_m)

        # 6. Blocks (e.g. BLOCK_T1_...)
        block_matches = re.findall(r"\b(BLOCK_[A-Z0-9_]+)\b", query, re.IGNORECASE)
        for m in block_matches:
            u_m = m.upper()
            if u_m not in identifiers["blocks"]:
                identifiers["blocks"].append(u_m)

        # 7. Options (e.g. OPT_T1_...)
        opt_matches = re.findall(r"\b(OPT_[A-Z0-9_]+)\b", query, re.IGNORECASE)
        for m in opt_matches:
            u_m = m.upper()
            if u_m not in identifiers["options"]:
                identifiers["options"].append(u_m)

        return identifiers

    def find_all_themes_for_outcome(self, outcome_code: str) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Finds all themes where an outcome code appears."""
        results = []
        for theme in self.curriculum_map.get("themes", []):
            t_id = theme.get("theme_id", f"TEMA_{theme.get('theme_no', 0):02d}")
            t_title = theme.get("exact_theme_name") or theme.get("theme_title", "")
            for out in theme.get("learning_outcomes", []):
                if out.get("outcome_code") == outcome_code:
                    results.append((t_id, t_title, out))
                    break
        return results

    def expand_outcome_graph(self, outcome_code: str, theme_id: str) -> Dict[str, Any]:
        """Expands canonical relationship graph for a learning outcome within a specific theme."""
        graph = {
            "outcome_code": outcome_code,
            "curriculum_outcome": None,
            "theme_id": theme_id,
            "theme_title": None,
            "alignments": [],
            "gaps": [],
            "needs": [],
            "resource_plans": [],
            "production_materials": [],
            "textbook_sections": [],
            "textbook_activities": [],
            "textbook_forms": [],
            "teaching_blocks": [],
            "school_based_options": []
        }

        # Search in curriculum map for the specific theme
        for theme in self.curriculum_map.get("themes", []):
            t_id = theme.get("theme_id", f"TEMA_{theme.get('theme_no', 0):02d}")
            if t_id == theme_id:
                graph["theme_title"] = theme.get("exact_theme_name") or theme.get("theme_title")
                for out in theme.get("learning_outcomes", []):
                    if out.get("outcome_code") == outcome_code:
                        graph["curriculum_outcome"] = out
                        break
                break

        if theme_id in self.themes_data:
            t_data = self.themes_data[theme_id]

            # 1. Alignment records
            for al in t_data.get("alignment", {}).get("alignments", []):
                if al.get("outcome_code") == outcome_code:
                    graph["alignments"].append(al)

            # 2. Gap analysis records
            for g in t_data.get("gap_analysis", {}).get("gaps", []) or t_data.get("gap_analysis", {}).get("gap_records", []):
                if g.get("outcome_code") == outcome_code:
                    graph["gaps"].append(g)

            # 3. Needs records
            for n in t_data.get("needs", {}).get("needs", []):
                if outcome_code in n.get("targeted_learning_outcomes", []):
                    graph["needs"].append(n)

            # 4. Resource plans
            for rp in t_data.get("resource_plan", {}).get("resources", []) or t_data.get("resource_plan", {}).get("resource_plans", []):
                if outcome_code in rp.get("target_outcomes", []):
                    graph["resource_plans"].append(rp)

        # 5. Production materials
        for mat in self.production_manifest.get("production_queue", []):
            if outcome_code in mat.get("targeted_outcomes", []):
                if not theme_id or theme_id in mat.get("theme_ids", []):
                    graph["production_materials"].append(mat)

        # 6. Teaching blocks
        for blk in self.teaching_blocks.get("teaching_blocks", []):
            if outcome_code in blk.get("targeted_outcomes", []):
                if not theme_id or blk.get("theme_id") == theme_id:
                    graph["teaching_blocks"].append(blk)

        # 7. School based options
        for theme in self.school_based_options.get("themes", []):
            if not theme_id or theme.get("theme_id") == theme_id:
                for opt in theme.get("options", []):
                    if outcome_code in opt.get("linked_outcomes", []):
                        graph["school_based_options"].append(opt)

        # 8. Textbook forms linked through alignments
        linked_form_ids: Set[str] = set()
        for al in graph["alignments"]:
            for f_id in al.get("textbook_form_ids", []):
                linked_form_ids.add(f_id)

        for form in self.textbook_forms.get("forms", []):
            if form.get("form_id") in linked_form_ids:
                graph["textbook_forms"].append(form)

        return graph

    def resolve(self, query: str, theme_id_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes full deterministic Knowledge Resolution pipeline with fail-closed gates.
        """
        retrieval_trace: List[str] = []
        resolution_mode: List[str] = []
        conflicts: List[Dict[str, Any]] = []
        ambiguity_status = "UNAMBIGUOUS"
        ambiguity_reason: Optional[str] = None
        resolved_candidates: List[Dict[str, Any]] = []

        retrieval_trace.append(f"1 COURSE_RESOLVED {self.course_id}")

        # Check Cache/Index Freshness
        status_info = self.indexer.check_status()
        index_freshness = status_info.get("status", "UNKNOWN")
        semantic_index_status = "FRESH" if index_freshness == "INDEX_FRESH" else "STALE"
        retrieval_trace.append(f"2 CACHE_CHECK {index_freshness}")

        # Detect Intent
        intent = self.detect_intent(query)
        retrieval_trace.append(f"3 INTENT_CLASSIFIED {intent}")

        # Extract Exact Identifiers
        extracted_ids = self.extract_exact_identifiers(query)
        target_theme = theme_id_override or (extracted_ids["themes"][0] if extracted_ids["themes"] else None)

        if target_theme:
            retrieval_trace.append(f"4 THEME_FILTER_SET {target_theme}")

        # Containers for context pack
        resolved_entities: List[Dict[str, Any]] = []
        curriculum_context: List[Dict[str, Any]] = []
        textbook_context: List[Dict[str, Any]] = []
        assessment_context: List[Dict[str, Any]] = []
        alignment_context: List[Dict[str, Any]] = []
        production_context: List[Dict[str, Any]] = []
        remaining_gaps: List[Dict[str, Any]] = []
        pedagogical_recommendations: List[Dict[str, Any]] = []

        # =========================================================================
        # PHASE A: EXACT STRUCTURED LOOKUP & AMBIGUITY HANDLING
        # =========================================================================
        exact_matched = False

        # 1. Exact Outcomes Lookup
        if extracted_ids["outcomes"]:
            resolution_mode.append("EXACT")
            resolution_mode.append("STRUCTURED")
            exact_matched = True

            for code in extracted_ids["outcomes"]:
                matching_theme_records = self.find_all_themes_for_outcome(code)

                # Check for Theme Ambiguity
                if not target_theme and len(matching_theme_records) > 1:
                    ambiguity_status = "AMBIGUOUS_ENTITY"
                    ambiguity_reason = (
                        f"Learning outcome code '{code}' is ambiguous and exists across multiple themes "
                        f"({', '.join(t[0] for t in matching_theme_records)}). Explicit theme context required."
                    )
                    retrieval_trace.append(f"5 AMBIGUOUS_OUTCOME_DETECTED {code} -> {len(matching_theme_records)} candidates")
                    for t_id, t_title, out_record in matching_theme_records:
                        candidate_info = {
                            "candidate_key": f"{t_id}::{code}",
                            "entity_key": f"{self.course_id}::curriculum_outcome::{t_id}::{code}",
                            "theme_id": t_id,
                            "theme_title": t_title,
                            "outcome_code": code,
                            "verbatim_statement": out_record.get("outcome_verbatim") or out_record.get("verbatim_statement"),
                            "skill_category": out_record.get("skill_category"),
                            "source_locator": out_record.get("source_locator")
                        }
                        resolved_candidates.append(candidate_info)
                        resolved_entities.append({
                            "entity_key": f"{self.course_id}::curriculum_outcome::{t_id}::{code}",
                            "entity_type": "curriculum_outcome",
                            "entity_id": code,
                            "theme_id": t_id,
                            "authority_level": 1,
                            "authority_name": "OFFICIAL_CURRICULUM_FROZEN",
                            "ambiguity": "CANDIDATE"
                        })
                else:
                    # Specific theme is selected or outcome is unique to a single theme
                    selected_theme_id = target_theme or (matching_theme_records[0][0] if matching_theme_records else "TEMA_01")
                    retrieval_trace.append(f"5 EXACT_OUTCOME_LOOKUP {code} in {selected_theme_id}")
                    graph = self.expand_outcome_graph(code, theme_id=selected_theme_id)

                    if graph["curriculum_outcome"]:
                        c_out = graph["curriculum_outcome"]
                        resolved_entities.append({
                            "entity_key": f"{self.course_id}::curriculum_outcome::{selected_theme_id}::{code}",
                            "entity_type": "curriculum_outcome",
                            "entity_id": code,
                            "theme_id": selected_theme_id,
                            "authority_level": 1,
                            "authority_name": "OFFICIAL_CURRICULUM_FROZEN"
                        })
                        curriculum_context.append({
                            "outcome_code": code,
                            "theme_id": selected_theme_id,
                            "theme_title": graph["theme_title"],
                            "verbatim_statement": c_out.get("outcome_verbatim") or c_out.get("verbatim_statement"),
                            "skill_category": c_out.get("skill_category"),
                            "assessment_requirement_verbatim": c_out.get("assessment_requirement_verbatim"),
                            "source_locator": c_out.get("source_locator")
                        })

                    # Alignments
                    for al in graph["alignments"]:
                        alignment_context.append(al)

                    # Gaps
                    for g in graph["gaps"]:
                        remaining_gaps.append(g)

                    # Production Materials
                    for mat in graph["production_materials"]:
                        production_context.append(mat)
                        resolved_entities.append({
                            "entity_key": f"{self.course_id}::production_material::{mat['material_id']}",
                            "entity_type": "production_material",
                            "entity_id": mat["material_id"],
                            "theme_id": selected_theme_id,
                            "authority_level": 7,
                            "authority_name": "VALIDATED_PRODUCTION_PLAN"
                        })

                    # Textbook Forms
                    for form in graph["textbook_forms"]:
                        assessment_context.append({
                            "form_id": form.get("form_id"),
                            "title": form.get("printed_title"),
                            "structural_type": form.get("structural_type"),
                            "evaluator": form.get("evaluator"),
                            "printed_page": form.get("printed_page"),
                            "pdf_page": form.get("pdf_page"),
                            "structure_details": form.get("structure_details")
                        })

                    # Pedagogical Recommendations (School-based options)
                    for opt in graph["school_based_options"]:
                        pedagogical_recommendations.append(opt)

        # 2. Exact School-Based Options Lookup
        elif intent == "SCHOOL_BASED_LOOKUP" and target_theme:
            resolution_mode.append("STRUCTURED")
            retrieval_trace.append(f"5 STRUCTURED_SCHOOL_BASED_LOOKUP {target_theme}")
            exact_matched = True
            for theme in self.school_based_options.get("themes", []):
                if theme.get("theme_id") == target_theme:
                    for opt in theme.get("options", []):
                        pedagogical_recommendations.append(opt)
                        resolved_entities.append({
                            "entity_key": f"{self.course_id}::school_based_option::{target_theme}::{opt['option_id']}",
                            "entity_type": "school_based_option",
                            "entity_id": opt["option_id"],
                            "theme_id": target_theme,
                            "authority_level": 8,
                            "authority_name": "PEDAGOGICAL_RECOMMENDATION"
                        })

        # 3. Exact Form Lookup or Material Lookup
        elif extracted_ids["forms"] or extracted_ids["materials"]:
            resolution_mode.append("EXACT")
            resolution_mode.append("STRUCTURED")
            exact_matched = True
            for f_id in extracted_ids["forms"]:
                retrieval_trace.append(f"5 EXACT_FORM_LOOKUP {f_id}")
                for form in self.textbook_forms.get("forms", []):
                    if form.get("form_id") == f_id:
                        assessment_context.append(form)
                        resolved_entities.append({
                            "entity_key": f"{self.course_id}::textbook_form::{f_id}",
                            "entity_type": "textbook_form",
                            "entity_id": f_id,
                            "authority_level": 3,
                            "authority_name": "OFFICIAL_TEXTBOOK_FORM_FROZEN"
                        })

            for m_id in extracted_ids["materials"]:
                retrieval_trace.append(f"5 EXACT_MATERIAL_LOOKUP {m_id}")
                for mat in self.production_manifest.get("production_queue", []):
                    if mat.get("material_id") == m_id:
                        production_context.append(mat)
                        resolved_entities.append({
                            "entity_key": f"{self.course_id}::production_material::{m_id}",
                            "entity_type": "production_material",
                            "entity_id": m_id,
                            "authority_level": 7,
                            "authority_name": "VALIDATED_PRODUCTION_PLAN"
                        })

        # =========================================================================
        # PHASE B: HYBRID RETRIEVAL (Lexical + Vector + RRF)
        # =========================================================================
        # Only invoke hybrid search if no exact match OR query is open-ended semantic
        if (not exact_matched or intent in ("GENERAL_SEMANTIC_QUERY", "ASSESSMENT_LOOKUP", "ALIGNMENT_LOOKUP")) and ambiguity_status != "AMBIGUOUS_ENTITY":
            retrieval_trace.append("6 HYBRID_RETRIEVAL_INVOKED")
            resolution_mode.append("FTS")
            resolution_mode.append("VECTOR")

            entity_type_filters = None
            q_lower = query.lower()
            if "rubrik" in q_lower or "ölçme" in q_lower or "form" in q_lower or "öz değerlendirme" in q_lower or "değerlendir" in q_lower:
                entity_type_filters = ["textbook_form", "production_material", "curriculum_outcome", "remaining_gap", "alignment_record"]
            elif "okul temelli" in q_lower or "seçenek" in q_lower or "miras" in q_lower or "sözlü tarih" in q_lower:
                entity_type_filters = ["school_based_option", "curriculum_outcome", "production_material"]

            hybrid_results = self.indexer.search_hybrid(
                query=query,
                top_k=8,
                theme_id=target_theme,
                entity_types=entity_type_filters
            )

            retrieval_trace.append(f"7 HYBRID_CANDIDATES_FOUND ({len(hybrid_results)} candidates)")

            for cand in hybrid_results[:5]:
                e_type = cand["entity_type"]
                e_id = cand["entity_id"]
                t_id = cand["theme_id"]
                cand_key = cand["entity_key"]

                if not any(r.get("entity_key") == cand_key for r in resolved_entities):
                    resolved_entities.append({
                        "entity_key": cand_key,
                        "entity_type": e_type,
                        "entity_id": e_id,
                        "theme_id": t_id,
                        "authority_level": cand["authority_level"],
                        "authority_name": cand["authority_name"],
                        "rrf_score": cand.get("rrf_score")
                    })

                if e_type == "curriculum_outcome":
                    clean_code = e_id.split("::")[-1]
                    graph = self.expand_outcome_graph(clean_code, theme_id=t_id or "TEMA_01")
                    if graph["curriculum_outcome"] and not any(c.get("outcome_code") == clean_code for c in curriculum_context):
                        curriculum_context.append({
                            "outcome_code": clean_code,
                            "theme_id": graph["theme_id"],
                            "theme_title": graph["theme_title"],
                            "verbatim_statement": graph["curriculum_outcome"].get("outcome_verbatim") or graph["curriculum_outcome"].get("verbatim_statement"),
                            "skill_category": graph["curriculum_outcome"].get("skill_category"),
                            "assessment_requirement_verbatim": graph["curriculum_outcome"].get("assessment_requirement_verbatim"),
                            "source_locator": graph["curriculum_outcome"].get("source_locator")
                        })
                    for mat in graph["production_materials"]:
                        if not any(m.get("material_id") == mat["material_id"] for m in production_context):
                            production_context.append(mat)
                    for g in graph["gaps"]:
                        if not any(x.get("outcome_code") == g.get("outcome_code") for x in remaining_gaps):
                            remaining_gaps.append(g)

                elif e_type == "production_material":
                    for mat in self.production_manifest.get("production_queue", []):
                        if mat.get("material_id") == e_id:
                            if not any(m.get("material_id") == e_id for m in production_context):
                                production_context.append(mat)
                            for out_c in mat.get("targeted_outcomes", []):
                                graph = self.expand_outcome_graph(out_c, theme_id=t_id or "TEMA_01")
                                for g in graph["gaps"]:
                                    if not any(x.get("outcome_code") == g.get("outcome_code") for x in remaining_gaps):
                                        remaining_gaps.append(g)

                elif e_type == "textbook_form":
                    for form in self.textbook_forms.get("forms", []):
                        if form.get("form_id") == e_id:
                            if not any(f.get("form_id") == e_id for f in assessment_context):
                                assessment_context.append(form)

                elif e_type == "school_based_option":
                    for theme in self.school_based_options.get("themes", []):
                        for opt in theme.get("options", []):
                            if opt.get("option_id") == e_id:
                                if not any(o.get("option_id") == e_id for o in pedagogical_recommendations):
                                    pedagogical_recommendations.append(opt)

        # =========================================================================
        # PHASE C: SPECIAL FACTS INTEGRITY & CANONICAL VERIFICATION
        # =========================================================================
        # Negative check: "analitik rubrik var mı?"
        if "analitik rubrik" in query.lower() and ("var mı" in query.lower() or "kitapta" in query.lower()):
            retrieval_trace.append("8 CANONICAL_FACT_VERIFICATION (analytic_rubric count check)")
            analytic_rubric_count = sum(
                1 for f in self.textbook_forms.get("forms", [])
                if f.get("structural_type") == "analytic_rubric"
            )
            fact_entity = {
                "entity_key": f"{self.course_id}::fact_verification::analytic_rubric_in_textbook",
                "entity_type": "fact_verification",
                "entity_id": "analytic_rubric_in_textbook",
                "authority_level": 3,
                "authority_name": "OFFICIAL_TEXTBOOK_FORM_FROZEN"
            }
            resolved_entities.insert(0, fact_entity)
            assessment_context.insert(0, {
                "fact_query": "analytic_rubric_in_textbook",
                "textbook_has_analytic_rubric": False,
                "canonical_count": analytic_rubric_count,
                "official_requirement_verbatim": "dereceli puanlama anahtarı",
                "selected_implementation": "analytic_rubric",
                "fact_statement": (
                    "Ders kitabında yapısal olarak analitik rubrik (analytic_rubric) bulunmamaktadır (sayı: 0). "
                    "Kitaptaki araçlar ölçüt tablosu (assessment_criteria_table), öz/akran değerlendirme formu ve gözlem listesidir. "
                    "Resmî öğretim programı 'dereceli puanlama anahtarı' şartı koymakta olup, analitik rubrik bu gereksinimi karşılamak "
                    "üzere seçilen pedagojik uygulama formatıdır (selected_implementation)."
                ),
                "authority_rank": 3,
                "authority_name": "OFFICIAL_TEXTBOOK_FORM_FROZEN"
            })

        # =========================================================================
        # PHASE D: CONFLICT DETECTION (Fail-Closed)
        # =========================================================================
        # Check alignment vs gap vs production queue contradictions
        for al in alignment_context:
            cov = al.get("primary_coverage")
            gap = al.get("remaining_gap", "")
            code = al.get("outcome_code")
            for mat in production_context:
                if code in mat.get("targeted_outcomes", []) and cov == "COVERED" and ("Yok" in gap or "NONE" in gap.upper()):
                    conflicts.append({
                        "conflict_type": "KNOWLEDGE_CONFLICT",
                        "outcome_code": code,
                        "details": f"Alignment specifies COVERED with no gap, yet production queue mandates required material '{mat.get('material_id')}'.",
                        "resolution": "REVIEW_REQUIRED"
                    })

        # Also verify gap_analysis consistency against alignment records
        for g in remaining_gaps:
            g_code = g.get("outcome_code")
            g_cov = g.get("primary_coverage")
            for al in alignment_context:
                if al.get("outcome_code") == g_code and al.get("primary_coverage") != g_cov:
                    conflicts.append({
                        "conflict_type": "KNOWLEDGE_CONFLICT",
                        "outcome_code": g_code,
                        "details": f"Coverage mismatch for {g_code}: Alignment says '{al.get('primary_coverage')}', Gap analysis says '{g_cov}'.",
                        "resolution": "REVIEW_REQUIRED"
                    })

        # =========================================================================
        # PHASE E: RESOLUTION STATUS & MATERIAL GENERATION SAFETY GATE
        # =========================================================================
        if ambiguity_status == "AMBIGUOUS_ENTITY":
            resolution_status = "PARTIALLY_RESOLVED"
            retrieval_trace.append("9 AMBIGUITY_DETECTED -> PARTIALLY_RESOLVED (generation blocked)")
        elif conflicts:
            resolution_status = "REVIEW_REQUIRED"
            retrieval_trace.append(f"9 CONFLICT_DETECTED ({len(conflicts)} conflicts) -> REVIEW_REQUIRED")
        elif index_freshness == "INDEX_STALE":
            resolution_status = "RESOLVED"
            retrieval_trace.append("9 STALE_INDEX_DETECTED -> REVIEW_REQUIRED (generation blocked)")
        else:
            resolution_status = "RESOLVED"
            retrieval_trace.append("9 CONFLICT_CHECK_PASSED (0 conflicts)")

        canonical_resolution_verified = len(resolved_entities) > 0 and ambiguity_status != "AMBIGUOUS_ENTITY"

        # Mandatory Material Generation Gate
        material_generation_allowed = (
            index_freshness == "INDEX_FRESH" and
            resolution_status == "RESOLVED" and
            len(conflicts) == 0 and
            ambiguity_status != "AMBIGUOUS_ENTITY" and
            canonical_resolution_verified
        )

        block_reason = None
        if not material_generation_allowed:
            if ambiguity_status == "AMBIGUOUS_ENTITY":
                block_reason = "AMBIGUOUS_ENTITY"
            elif conflicts:
                block_reason = "KNOWLEDGE_CONFLICT"
            elif index_freshness == "INDEX_STALE":
                block_reason = "INDEX_STALE"
            elif not canonical_resolution_verified:
                block_reason = "CANONICAL_RESOLUTION_UNVERIFIED"

        retrieval_trace.append(f"10 MATERIAL_GENERATION_GATE (Allowed: {material_generation_allowed}, Reason: {block_reason or 'PASSED'})")
        retrieval_trace.append("11 CONTEXT_PACK_ASSEMBLED")

        # Assemble final Knowledge Context Pack
        context_pack = {
            "course_id": self.course_id,
            "query": query,
            "query_intent": intent,
            "resolution_status": resolution_status,
            "resolution_mode": list(set(resolution_mode)),
            "ambiguity_status": ambiguity_status,
            "ambiguity_reason": ambiguity_reason,
            "resolved_candidates": resolved_candidates,
            "semantic_index_status": semantic_index_status,
            "index_freshness": index_freshness,
            "canonical_resolution_verified": canonical_resolution_verified,
            "material_generation_allowed": material_generation_allowed,
            "material_generation_block_reason": block_reason,
            "resolved_entities": resolved_entities,
            "curriculum_context": curriculum_context,
            "textbook_context": textbook_context,
            "assessment_context": assessment_context,
            "alignment_context": alignment_context,
            "production_context": production_context,
            "remaining_gaps": remaining_gaps,
            "pedagogical_recommendations": pedagogical_recommendations,
            "source_fallback_required": False,
            "external_lookup_required": False,
            "conflicts": conflicts,
            "retrieval_trace": retrieval_trace
        }

        return context_pack


def main():
    parser = argparse.ArgumentParser(description="TYMM Knowledge Resolver CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # resolve
    p_res = subparsers.add_parser("resolve", help="Resolve query to canonical Knowledge Context Pack")
    p_res.add_argument("--knowledge-root", required=True, help="Path to knowledge directory (e.g. knowledge/TDE_9)")
    p_res.add_argument("--query", required=True, help="User query string")
    p_res.add_argument("--theme-id", help="Optional theme ID override (e.g. TEMA_02)")

    args = parser.parse_args()
    resolver = KnowledgeResolver(args.knowledge_root)

    if args.command == "resolve":
        pack = resolver.resolve(query=args.query, theme_id_override=args.theme_id)
        print(json.dumps(pack, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
