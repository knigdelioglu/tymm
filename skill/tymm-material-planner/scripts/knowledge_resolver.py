#!/usr/bin/env python3
"""
TYMM Knowledge Resolver (knowledge_resolver.py)

Deterministic retrieval and orchestration layer for Türkiye Yüzyılı Maarif Modeli (TYMM)
knowledge bases.

Production schema invariant (1.1):
- canonical production identity = artifact_id
- covered_themes / covered_outcomes define aggregate artifact scope
- covered_gap_instances contains historical MAT_* gap aliases only
- theme/outcome bindings come from gap-instance provenance, never a themes×outcomes cross product
- MAT_* aliases may resolve to an artifact, but never become artifact identity
"""

import argparse
import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from knowledge_index import KnowledgeIndexer
    from production_schema import build_artifact_maps
except ImportError:
    from .knowledge_index import KnowledgeIndexer
    from .production_schema import build_artifact_maps


class KnowledgeResolver:
    """Orchestrates structured lookup, hybrid search, graph expansion, and fail-closed gates."""

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
        self.curriculum_map = self._read_json("curriculum_map.json") or {}
        self.textbook_map = self._read_json("textbook_map.json") or {}
        self.textbook_forms = self._read_json("textbook_forms_index.json") or {}
        self.production_manifest = self._read_json("production/production_manifest.json") or {}
        self.teaching_blocks = self._read_json("production/teaching_blocks.json") or {}
        self.school_based_options = self._read_json("production/school_based_planning_options.json") or {}

        (
            self.production_artifacts,
            self.artifact_by_id,
            self.gap_alias_to_artifact_id,
            self.gap_provenance_by_id,
        ) = build_artifact_maps(self.production_manifest)

        self.themes_data: Dict[str, Dict[str, Any]] = {}
        for theme in self.curriculum_map.get("themes", []):
            t_id = theme.get("theme_id", f"TEMA_{theme.get('theme_no', 0):02d}")
            match = re.search(r"(\d+)$", t_id)
            if not match:
                continue
            t_dir = f"themes/tema_{int(match.group(1)):02d}"
            self.themes_data[t_id] = {
                "alignment": self._read_json(f"{t_dir}/alignment.json") or {},
                "gap_analysis": self._read_json(f"{t_dir}/gap_analysis.json") or {},
                "needs": self._read_json(f"{t_dir}/needs.json") or {},
                "resource_plan": self._read_json(f"{t_dir}/resource_plan.json") or {},
            }

    def detect_intent(self, query: str) -> str:
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
        if "üretim" in q or "kuyruk" in q or "manifest" in q or "artifact" in q:
            return "PRODUCTION_LOOKUP"
        if "denetim" in q or "audit" in q or "qa" in q or "doğrulama" in q:
            return "AUDIT"
        if "nerede" in q or "sayfa" in q or "locator" in q:
            return "SOURCE_LOOKUP"
        if re.search(r"tde\d\.\d", q) or "nedir" in q or "ifadesi" in q or "tanım" in q:
            return "FACT_LOOKUP"
        return "GENERAL_SEMANTIC_QUERY"

    def extract_exact_identifiers(self, query: str) -> Dict[str, List[str]]:
        identifiers = {
            "outcomes": [],
            "themes": [],
            "forms": [],
            "artifacts": [],
            "materials": [],
            "resources": [],
            "blocks": [],
            "options": [],
        }

        for m in re.findall(r"\b(TDE\s*[1-4]\.[1-4](?:\.[1-4a-z])?)\b", query, re.IGNORECASE):
            normalized = m.upper().replace(" ", "")
            if normalized not in identifiers["outcomes"]:
                identifiers["outcomes"].append(normalized)

        for m in re.findall(r"\b(TEMA_0[1-9]|TEMA\s*[1-9]|[1-9]\.\s*TEMA)\b", query, re.IGNORECASE):
            digits = re.findall(r"[1-9]", m)
            if digits:
                t_id = f"TEMA_{int(digits[0]):02d}"
                if t_id not in identifiers["themes"]:
                    identifiers["themes"].append(t_id)

        for m in re.findall(r"\b(FORM_[A-Z0-9_]+)\b", query, re.IGNORECASE):
            u_m = m.upper()
            if u_m not in identifiers["forms"]:
                identifiers["forms"].append(u_m)

        for m in re.findall(r"\b(TDE\d+_[A-Z0-9_]+)\b", query, re.IGNORECASE):
            u_m = m.upper()
            if u_m in self.artifact_by_id and u_m not in identifiers["artifacts"]:
                identifiers["artifacts"].append(u_m)

        for m in re.findall(r"\b(MAT_[A-Z0-9_]+)\b", query, re.IGNORECASE):
            u_m = m.upper()
            if u_m not in identifiers["materials"]:
                identifiers["materials"].append(u_m)

        for key, pattern in (
            ("resources", r"\b(RES_[A-Z0-9_]+)\b"),
            ("blocks", r"\b(BLOCK_[A-Z0-9_]+)\b"),
            ("options", r"\b(OPT_[A-Z0-9_]+)\b"),
        ):
            for m in re.findall(pattern, query, re.IGNORECASE):
                u_m = m.upper()
                if u_m not in identifiers[key]:
                    identifiers[key].append(u_m)

        return identifiers

    def find_all_themes_for_outcome(self, outcome_code: str) -> List[Tuple[str, str, Dict[str, Any]]]:
        results = []
        for theme in self.curriculum_map.get("themes", []):
            t_id = theme.get("theme_id", f"TEMA_{theme.get('theme_no', 0):02d}")
            t_title = theme.get("exact_theme_name") or theme.get("theme_title", "")
            for out in theme.get("learning_outcomes", []):
                if out.get("outcome_code") == outcome_code:
                    results.append((t_id, t_title, out))
                    break
        return results

    def _artifact_bindings(self, artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
        bindings: List[Dict[str, Any]] = []
        for gap_alias in artifact.get("covered_gap_instances", []):
            provenance = self.gap_provenance_by_id.get(gap_alias)
            if provenance:
                bindings.append(provenance)
        return bindings

    def _artifact_matches_scope(self, artifact: Dict[str, Any], outcome_code: str, theme_id: str) -> bool:
        """Match a real gap binding, not the aggregate covered_themes×covered_outcomes cross product."""
        for binding in self._artifact_bindings(artifact):
            if theme_id and binding.get("theme_id") != theme_id:
                continue
            if outcome_code in binding.get("targeted_outcomes", []):
                return True
        return False

    def _teaching_block_rows(self) -> List[Dict[str, Any]]:
        return self.teaching_blocks.get("blocks", []) or self.teaching_blocks.get("teaching_blocks", [])

    def expand_outcome_graph(self, outcome_code: str, theme_id: str) -> Dict[str, Any]:
        graph = {
            "outcome_code": outcome_code,
            "curriculum_outcome": None,
            "theme_id": theme_id,
            "theme_title": None,
            "alignments": [],
            "gaps": [],
            "needs": [],
            "resource_plans": [],
            "assessment_artifacts": [],
            "textbook_sections": [],
            "textbook_activities": [],
            "textbook_forms": [],
            "teaching_blocks": [],
            "school_based_options": [],
        }

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
            for al in t_data.get("alignment", {}).get("alignments", []):
                if al.get("outcome_code") == outcome_code:
                    graph["alignments"].append(al)
            for g in t_data.get("gap_analysis", {}).get("gaps", []) or t_data.get("gap_analysis", {}).get("gap_records", []):
                if g.get("outcome_code") == outcome_code:
                    graph["gaps"].append(g)
            for n in t_data.get("needs", {}).get("needs", []):
                if outcome_code in n.get("targeted_learning_outcomes", []):
                    graph["needs"].append(n)
            for rp in t_data.get("resource_plan", {}).get("resources", []) or t_data.get("resource_plan", {}).get("resource_plans", []):
                if outcome_code in rp.get("target_outcomes", []):
                    graph["resource_plans"].append(rp)

        for artifact in self.production_artifacts:
            if self._artifact_matches_scope(artifact, outcome_code, theme_id):
                graph["assessment_artifacts"].append(artifact)

        for blk in self._teaching_block_rows():
            outcomes = blk.get("curriculum_outcomes", []) or blk.get("targeted_outcomes", [])
            if outcome_code in outcomes and (not theme_id or blk.get("theme_id") == theme_id):
                graph["teaching_blocks"].append(blk)

        for theme in self.school_based_options.get("themes", []):
            if not theme_id or theme.get("theme_id") == theme_id:
                for opt in theme.get("options", []):
                    if outcome_code in opt.get("linked_outcomes", []):
                        graph["school_based_options"].append(opt)

        linked_form_ids: Set[str] = set()
        for al in graph["alignments"]:
            for f_id in al.get("textbook_form_ids", []):
                linked_form_ids.add(f_id)
        for form in self.textbook_forms.get("forms", []):
            if form.get("form_id") in linked_form_ids:
                graph["textbook_forms"].append(form)

        return graph

    def _append_artifact(
        self,
        artifact: Dict[str, Any],
        production_context: List[Dict[str, Any]],
        resolved_entities: List[Dict[str, Any]],
        matched_alias: Optional[str] = None,
    ) -> None:
        artifact_id = artifact["artifact_id"]
        if not any(item.get("artifact_id") == artifact_id for item in production_context):
            production_context.append(artifact)
        key = f"{self.course_id}::assessment_artifact::{artifact_id}"
        existing = next((item for item in resolved_entities if item.get("entity_key") == key), None)
        if existing is None:
            existing = {
                "entity_key": key,
                "entity_type": "assessment_artifact",
                "entity_id": artifact_id,
                "theme_id": artifact.get("covered_themes", [None])[0] if len(artifact.get("covered_themes", [])) == 1 else None,
                "covered_themes": artifact.get("covered_themes", []),
                "authority_level": 7,
                "authority_name": "VALIDATED_PRODUCTION_PLAN",
            }
            resolved_entities.append(existing)
        if matched_alias:
            existing["matched_gap_alias"] = matched_alias

    def resolve(self, query: str, theme_id_override: Optional[str] = None) -> Dict[str, Any]:
        retrieval_trace: List[str] = []
        resolution_mode: List[str] = []
        conflicts: List[Dict[str, Any]] = []
        ambiguity_status = "UNAMBIGUOUS"
        ambiguity_reason: Optional[str] = None
        resolved_candidates: List[Dict[str, Any]] = []

        retrieval_trace.append(f"1 COURSE_RESOLVED {self.course_id}")
        status_info = self.indexer.check_status()
        index_freshness = status_info.get("status", "UNKNOWN")
        semantic_index_status = "FRESH" if index_freshness == "INDEX_FRESH" else "STALE"
        retrieval_trace.append(f"2 CACHE_CHECK {index_freshness}")

        intent = self.detect_intent(query)
        retrieval_trace.append(f"3 INTENT_CLASSIFIED {intent}")

        extracted_ids = self.extract_exact_identifiers(query)
        target_theme = theme_id_override or (extracted_ids["themes"][0] if extracted_ids["themes"] else None)
        if target_theme:
            retrieval_trace.append(f"4 THEME_FILTER_SET {target_theme}")

        resolved_entities: List[Dict[str, Any]] = []
        curriculum_context: List[Dict[str, Any]] = []
        textbook_context: List[Dict[str, Any]] = []
        assessment_context: List[Dict[str, Any]] = []
        alignment_context: List[Dict[str, Any]] = []
        production_context: List[Dict[str, Any]] = []
        remaining_gaps: List[Dict[str, Any]] = []
        pedagogical_recommendations: List[Dict[str, Any]] = []
        exact_matched = False

        if extracted_ids["outcomes"]:
            resolution_mode.extend(["EXACT", "STRUCTURED"])
            exact_matched = True
            for code in extracted_ids["outcomes"]:
                matching_theme_records = self.find_all_themes_for_outcome(code)
                if not target_theme and len(matching_theme_records) > 1:
                    ambiguity_status = "AMBIGUOUS_ENTITY"
                    ambiguity_reason = (
                        f"Learning outcome code '{code}' is ambiguous and exists across multiple themes "
                        f"({', '.join(t[0] for t in matching_theme_records)}). Explicit theme context required."
                    )
                    retrieval_trace.append(f"5 AMBIGUOUS_OUTCOME_DETECTED {code} -> {len(matching_theme_records)} candidates")
                    for t_id, t_title, out_record in matching_theme_records:
                        resolved_candidates.append({
                            "candidate_key": f"{t_id}::{code}",
                            "entity_key": f"{self.course_id}::curriculum_outcome::{t_id}::{code}",
                            "theme_id": t_id,
                            "theme_title": t_title,
                            "outcome_code": code,
                            "verbatim_statement": out_record.get("outcome_verbatim") or out_record.get("verbatim_statement"),
                            "skill_category": out_record.get("skill_category"),
                            "source_locator": out_record.get("source_locator"),
                        })
                        resolved_entities.append({
                            "entity_key": f"{self.course_id}::curriculum_outcome::{t_id}::{code}",
                            "entity_type": "curriculum_outcome",
                            "entity_id": code,
                            "theme_id": t_id,
                            "authority_level": 1,
                            "authority_name": "OFFICIAL_CURRICULUM_FROZEN",
                            "ambiguity": "CANDIDATE",
                        })
                    continue

                selected_theme_id = target_theme or (matching_theme_records[0][0] if matching_theme_records else "")
                retrieval_trace.append(f"5 EXACT_OUTCOME_LOOKUP {code} in {selected_theme_id}")
                graph = self.expand_outcome_graph(code, selected_theme_id)
                if graph["curriculum_outcome"]:
                    c_out = graph["curriculum_outcome"]
                    resolved_entities.append({
                        "entity_key": f"{self.course_id}::curriculum_outcome::{selected_theme_id}::{code}",
                        "entity_type": "curriculum_outcome",
                        "entity_id": code,
                        "theme_id": selected_theme_id,
                        "authority_level": 1,
                        "authority_name": "OFFICIAL_CURRICULUM_FROZEN",
                    })
                    curriculum_context.append({
                        "outcome_code": code,
                        "theme_id": selected_theme_id,
                        "theme_title": graph["theme_title"],
                        "verbatim_statement": c_out.get("outcome_verbatim") or c_out.get("verbatim_statement"),
                        "skill_category": c_out.get("skill_category"),
                        "assessment_requirement_verbatim": c_out.get("assessment_requirement_verbatim"),
                        "source_locator": c_out.get("source_locator"),
                    })
                alignment_context.extend(graph["alignments"])
                remaining_gaps.extend(graph["gaps"])
                for artifact in graph["assessment_artifacts"]:
                    self._append_artifact(artifact, production_context, resolved_entities)
                for form in graph["textbook_forms"]:
                    assessment_context.append({
                        "form_id": form.get("form_id"),
                        "title": form.get("printed_title"),
                        "structural_type": form.get("structural_type"),
                        "evaluator": form.get("evaluator"),
                        "printed_page": form.get("printed_page"),
                        "pdf_page": form.get("pdf_page"),
                        "structure_details": form.get("structure_details"),
                    })
                pedagogical_recommendations.extend(graph["school_based_options"])

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
                            "authority_name": "PEDAGOGICAL_RECOMMENDATION",
                        })

        elif extracted_ids["forms"] or extracted_ids["artifacts"] or extracted_ids["materials"]:
            resolution_mode.extend(["EXACT", "STRUCTURED"])
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
                            "authority_name": "OFFICIAL_TEXTBOOK_FORM_FROZEN",
                        })

            for artifact_id in extracted_ids["artifacts"]:
                retrieval_trace.append(f"5 EXACT_ARTIFACT_LOOKUP {artifact_id}")
                artifact = self.artifact_by_id.get(artifact_id)
                if artifact:
                    self._append_artifact(artifact, production_context, resolved_entities)

            for gap_alias in extracted_ids["materials"]:
                artifact_id = self.gap_alias_to_artifact_id.get(gap_alias)
                retrieval_trace.append(f"5 GAP_ALIAS_LOOKUP {gap_alias} -> {artifact_id or 'NOT_FOUND'}")
                if artifact_id:
                    self._append_artifact(
                        self.artifact_by_id[artifact_id], production_context, resolved_entities, matched_alias=gap_alias
                    )

        exact_identity_query = bool(
            extracted_ids["artifacts"] or extracted_ids["materials"] or extracted_ids["forms"]
        )
        should_hybrid = (
            not exact_matched
            or (
                intent in ("GENERAL_SEMANTIC_QUERY", "ASSESSMENT_LOOKUP", "ALIGNMENT_LOOKUP")
                and not exact_identity_query
            )
        )
        if should_hybrid and ambiguity_status != "AMBIGUOUS_ENTITY" and index_freshness == "INDEX_FRESH":
            retrieval_trace.append("6 HYBRID_RETRIEVAL_INVOKED")
            resolution_mode.extend(["FTS", "VECTOR"])
            entity_type_filters = None
            q_lower = query.lower()
            if any(term in q_lower for term in ("rubrik", "ölçme", "form", "öz değerlendirme", "değerlendir")):
                entity_type_filters = [
                    "textbook_form", "assessment_artifact", "curriculum_outcome", "remaining_gap", "alignment_record"
                ]
            elif any(term in q_lower for term in ("okul temelli", "seçenek", "miras", "sözlü tarih")):
                entity_type_filters = ["school_based_option", "curriculum_outcome", "assessment_artifact"]

            hybrid_results = self.indexer.search_hybrid(
                query=query, top_k=8, theme_id=target_theme, entity_types=entity_type_filters
            )
            retrieval_trace.append(f"7 HYBRID_CANDIDATES_FOUND ({len(hybrid_results)} candidates)")

            for cand in hybrid_results[:5]:
                e_type = cand["entity_type"]
                e_id = cand["entity_id"]
                t_id = cand["theme_id"]
                cand_key = cand["entity_key"]

                if e_type == "assessment_artifact":
                    artifact = self.artifact_by_id.get(e_id)
                    if not artifact:
                        continue
                    if target_theme and target_theme not in artifact.get("covered_themes", []):
                        continue

                if not any(r.get("entity_key") == cand_key for r in resolved_entities):
                    resolved_entities.append({
                        "entity_key": cand_key,
                        "entity_type": e_type,
                        "entity_id": e_id,
                        "theme_id": t_id,
                        "authority_level": cand["authority_level"],
                        "authority_name": cand["authority_name"],
                        "rrf_score": cand.get("rrf_score"),
                    })

                if e_type == "curriculum_outcome":
                    clean_code = e_id.split("::")[-1]
                    graph = self.expand_outcome_graph(clean_code, t_id or target_theme or "TEMA_01")
                    if graph["curriculum_outcome"] and not any(c.get("outcome_code") == clean_code for c in curriculum_context):
                        curriculum_context.append({
                            "outcome_code": clean_code,
                            "theme_id": graph["theme_id"],
                            "theme_title": graph["theme_title"],
                            "verbatim_statement": graph["curriculum_outcome"].get("outcome_verbatim") or graph["curriculum_outcome"].get("verbatim_statement"),
                            "skill_category": graph["curriculum_outcome"].get("skill_category"),
                            "assessment_requirement_verbatim": graph["curriculum_outcome"].get("assessment_requirement_verbatim"),
                            "source_locator": graph["curriculum_outcome"].get("source_locator"),
                        })
                    for artifact in graph["assessment_artifacts"]:
                        self._append_artifact(artifact, production_context, resolved_entities)
                    for g in graph["gaps"]:
                        if not any(x.get("gap_id") == g.get("gap_id") and x.get("outcome_code") == g.get("outcome_code") for x in remaining_gaps):
                            remaining_gaps.append(g)

                elif e_type == "assessment_artifact":
                    artifact = self.artifact_by_id[e_id]
                    self._append_artifact(artifact, production_context, resolved_entities)
                    for binding in self._artifact_bindings(artifact):
                        binding_theme = binding.get("theme_id")
                        if target_theme and binding_theme != target_theme:
                            continue
                        for out_c in binding.get("targeted_outcomes", []):
                            if not binding_theme:
                                continue
                            graph = self.expand_outcome_graph(out_c, binding_theme)
                            for g in graph["gaps"]:
                                if not any(x.get("gap_id") == g.get("gap_id") and x.get("outcome_code") == g.get("outcome_code") for x in remaining_gaps):
                                    remaining_gaps.append(g)

                elif e_type == "textbook_form":
                    for form in self.textbook_forms.get("forms", []):
                        if form.get("form_id") == e_id and not any(f.get("form_id") == e_id for f in assessment_context):
                            assessment_context.append(form)

                elif e_type == "school_based_option":
                    for theme in self.school_based_options.get("themes", []):
                        for opt in theme.get("options", []):
                            if opt.get("option_id") == e_id and not any(o.get("option_id") == e_id for o in pedagogical_recommendations):
                                pedagogical_recommendations.append(opt)

        elif should_hybrid and index_freshness != "INDEX_FRESH":
            retrieval_trace.append(f"6 HYBRID_RETRIEVAL_BLOCKED {index_freshness}")

        if "analitik rubrik" in query.lower() and ("var mı" in query.lower() or "kitapta" in query.lower()):
            retrieval_trace.append("8 CANONICAL_FACT_VERIFICATION (analytic_rubric count check)")
            analytic_rubric_count = sum(
                1 for f in self.textbook_forms.get("forms", []) if f.get("structural_type") == "analytic_rubric"
            )
            resolved_entities.insert(0, {
                "entity_key": f"{self.course_id}::fact_verification::analytic_rubric_in_textbook",
                "entity_type": "fact_verification",
                "entity_id": "analytic_rubric_in_textbook",
                "authority_level": 3,
                "authority_name": "OFFICIAL_TEXTBOOK_FORM_FROZEN",
            })
            assessment_context.insert(0, {
                "fact_query": "analytic_rubric_in_textbook",
                "textbook_has_analytic_rubric": analytic_rubric_count > 0,
                "canonical_count": analytic_rubric_count,
                "official_requirement_verbatim": "dereceli puanlama anahtarı",
                "selected_implementation": "analytic_rubric",
                "fact_statement": (
                    f"Ders kitabında yapısal olarak analitik rubrik (analytic_rubric) sayısı: {analytic_rubric_count}. "
                    "Resmî öğretim programındaki 'dereceli puanlama anahtarı' gereksinimi ile ders kitabındaki form yapısı ayrı tutulur."
                ),
                "authority_rank": 3,
                "authority_name": "OFFICIAL_TEXTBOOK_FORM_FROZEN",
            })

        for al in alignment_context:
            cov = al.get("primary_coverage")
            gap_text = al.get("remaining_gap", "")
            code = al.get("outcome_code")
            for artifact in production_context:
                if (
                    self._artifact_matches_scope(artifact, code, target_theme or al.get("theme_id", ""))
                    and cov == "COVERED"
                    and ("Yok" in gap_text or "NONE" in gap_text.upper())
                ):
                    conflicts.append({
                        "conflict_type": "KNOWLEDGE_CONFLICT",
                        "outcome_code": code,
                        "details": (
                            f"Alignment specifies COVERED with no gap, yet production artifact "
                            f"'{artifact.get('artifact_id')}' is bound to that theme/outcome requirement."
                        ),
                        "resolution": "REVIEW_REQUIRED",
                    })

        for g in remaining_gaps:
            g_code = g.get("outcome_code")
            g_cov = g.get("primary_coverage")
            for al in alignment_context:
                if al.get("outcome_code") == g_code and al.get("primary_coverage") != g_cov:
                    conflicts.append({
                        "conflict_type": "KNOWLEDGE_CONFLICT",
                        "outcome_code": g_code,
                        "details": (
                            f"Coverage mismatch for {g_code}: Alignment says '{al.get('primary_coverage')}', "
                            f"Gap analysis says '{g_cov}'."
                        ),
                        "resolution": "REVIEW_REQUIRED",
                    })

        if ambiguity_status == "AMBIGUOUS_ENTITY":
            resolution_status = "PARTIALLY_RESOLVED"
            retrieval_trace.append("9 AMBIGUITY_DETECTED -> PARTIALLY_RESOLVED (generation blocked)")
        elif conflicts:
            resolution_status = "REVIEW_REQUIRED"
            retrieval_trace.append(f"9 CONFLICT_DETECTED ({len(conflicts)} conflicts) -> REVIEW_REQUIRED")
        elif index_freshness != "INDEX_FRESH":
            resolution_status = "REVIEW_REQUIRED"
            retrieval_trace.append(f"9 INDEX_GATE_BLOCKED {index_freshness} -> REVIEW_REQUIRED")
        else:
            resolution_status = "RESOLVED"
            retrieval_trace.append("9 CONFLICT_CHECK_PASSED (0 conflicts)")

        canonical_resolution_verified = len(resolved_entities) > 0 and ambiguity_status != "AMBIGUOUS_ENTITY"
        material_generation_allowed = (
            index_freshness == "INDEX_FRESH"
            and resolution_status == "RESOLVED"
            and not conflicts
            and ambiguity_status != "AMBIGUOUS_ENTITY"
            and canonical_resolution_verified
        )

        block_reason = None
        if not material_generation_allowed:
            if ambiguity_status == "AMBIGUOUS_ENTITY":
                block_reason = "AMBIGUOUS_ENTITY"
            elif conflicts:
                block_reason = "KNOWLEDGE_CONFLICT"
            elif index_freshness != "INDEX_FRESH":
                block_reason = index_freshness
            elif not canonical_resolution_verified:
                block_reason = "CANONICAL_RESOLUTION_UNVERIFIED"

        retrieval_trace.append(
            f"10 MATERIAL_GENERATION_GATE (Allowed: {material_generation_allowed}, Reason: {block_reason or 'PASSED'})"
        )
        retrieval_trace.append("11 CONTEXT_PACK_ASSEMBLED")

        return {
            "course_id": self.course_id,
            "query": query,
            "query_intent": intent,
            "resolution_status": resolution_status,
            "resolution_mode": sorted(set(resolution_mode)),
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
            "retrieval_trace": retrieval_trace,
        }


def main():
    parser = argparse.ArgumentParser(description="TYMM Knowledge Resolver CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_res = subparsers.add_parser("resolve", help="Resolve query to canonical Knowledge Context Pack")
    p_res.add_argument("--knowledge-root", required=True, help="Path to course knowledge directory (e.g. courses/TDE_9)")
    p_res.add_argument("--query", required=True, help="User query string")
    p_res.add_argument("--theme-id", help="Optional theme ID override (e.g. TEMA_02)")
    args = parser.parse_args()

    resolver = KnowledgeResolver(args.knowledge_root)
    if args.command == "resolve":
        print(json.dumps(resolver.resolve(args.query, args.theme_id), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
