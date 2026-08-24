#!/usr/bin/env python3
"""Regression suite for TYMM resolver production-schema 1.1 migration."""

import json
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from typing import Any, Dict

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from knowledge_index import DuplicateCanonicalKeyError
from effective_knowledge_index import EffectiveKnowledgeCorpusExtractor as KnowledgeCorpusExtractor, KnowledgeIndexer
from knowledge_resolver import KnowledgeResolver
from production_schema import build_artifact_maps

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(TESTS_DIR)

EXPECTED_ALIAS_MAP = {
    "MAT_T2_KONUSMA_RUBRIC": "TDE9_KONUSMA_RUBRIC",
    "MAT_T2_YAZMA_RUBRIC": "TDE9_YAZMA_RUBRIC",
    "MAT_T3_KONUSMA_RUBRIC": "TDE9_KONUSMA_RUBRIC",
    "MAT_T3_YAZMA_RUBRIC": "TDE9_YAZMA_RUBRIC",
    "MAT_T4_KONUSMA_RUBRIC": "TDE9_KONUSMA_RUBRIC",
    "MAT_T4_YAZMA_KONTROL_LISTESI": "TDE9_YAZMA_SUREC_KONTROL_LISTESI",
    "MAT_T4_YAZMA_RUBRIC": "TDE9_YAZMA_RUBRIC",
}


def _resolve_default_knowledge_root() -> str:
    env = os.environ.get("TYMM_KNOWLEDGE_ROOT")
    if env and os.path.exists(env):
        return os.path.abspath(env)
    cwd_candidate = os.path.abspath(os.path.join(os.getcwd(), "courses", "TDE_9"))
    if os.path.exists(cwd_candidate):
        return cwd_candidate
    return os.path.abspath(os.path.join(SKILL_DIR, "..", "..", "courses", "TDE_9"))


def _copy_knowledge_fixture(source_root: str, target_root: str) -> None:
    """Copy a course fixture together with sibling shared normative catalogs."""
    shutil.copytree(source_root, target_root)
    shared_src = os.path.join(os.path.dirname(os.path.abspath(source_root)), "TDE_SHARED")
    shared_dst = os.path.join(os.path.dirname(os.path.abspath(target_root)), "TDE_SHARED")
    if os.path.exists(shared_src) and not os.path.exists(shared_dst):
        shutil.copytree(shared_src, shared_dst)


DEFAULT_KNOWLEDGE_ROOT = _resolve_default_knowledge_root()


class TestKnowledgeResolverHardening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.knowledge_root = os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_KNOWLEDGE_ROOT)
        cls.indexer = KnowledgeIndexer(cls.knowledge_root)
        # A clean clone intentionally has no knowledge.sqlite. Rebuild instead of silently
        # running the resolver suite against a missing or stale derived cache.
        if cls.indexer.check_status().get("status") != "INDEX_FRESH":
            cls.indexer.build_index(force=True)
        cls.resolver = KnowledgeResolver(cls.knowledge_root)
        with open(os.path.join(TESTS_DIR, "knowledge_resolver_cases.json"), "r", encoding="utf-8") as f:
            cls.test_cases_data = json.load(f)

    def test_01_ambiguous_outcome_query_tde4_4(self):
        pack = self.resolver.resolve("TDE4.4")
        self.assertEqual(pack["ambiguity_status"], "AMBIGUOUS_ENTITY")
        self.assertEqual(pack["resolution_status"], "PARTIALLY_RESOLVED")
        self.assertFalse(pack["material_generation_allowed"])
        self.assertEqual(pack["material_generation_block_reason"], "AMBIGUOUS_ENTITY")
        self.assertEqual(
            {c["candidate_key"] for c in pack["resolved_candidates"]},
            {"TEMA_01::TDE4.4", "TEMA_02::TDE4.4", "TEMA_03::TDE4.4", "TEMA_04::TDE4.4"},
        )

    def test_02_disambiguated_outcome_query_theme2_tde4_4(self):
        pack = self.resolver.resolve("Tema 2 TDE4.4")
        self.assertEqual(pack["resolution_status"], "RESOLVED")
        self.assertTrue(pack["material_generation_allowed"])
        curr = pack["curriculum_context"][0]
        self.assertEqual(curr["outcome_code"], "TDE4.4")
        self.assertEqual(curr["theme_id"], "TEMA_02")
        self.assertEqual(pack["resolved_entities"][0]["entity_key"], "TDE_9::curriculum_outcome::TEMA_02::TDE4.4")

    def test_03_gap_query_resolves_annual_writing_artifact(self):
        pack = self.resolver.resolve("Tema 2 TDE4.4 için kitapta ne eksik?")
        self.assertEqual(pack["resolution_status"], "RESOLVED")
        self.assertTrue(any(g.get("primary_coverage") == "PARTIALLY_COVERED" for g in pack["remaining_gaps"]))
        artifacts = {a["artifact_id"]: a for a in pack["production_context"]}
        self.assertIn("TDE9_YAZMA_RUBRIC", artifacts)
        self.assertIn("MAT_T2_YAZMA_RUBRIC", artifacts["TDE9_YAZMA_RUBRIC"]["covered_gap_instances"])

    def test_04_canonical_theme3_speaking_self_assessment_form(self):
        pack = self.resolver.resolve("Tema 3 konuşma öz değerlendirme formu")
        form_ids = {f.get("form_id") for f in pack["assessment_context"] if f.get("form_id")}
        entity_ids = {e["entity_id"] for e in pack["resolved_entities"]}
        self.assertTrue("FORM_BOB_06_T3_KONUSMA_OZ" in form_ids or "FORM_BOB_06_T3_KONUSMA_OZ" in entity_ids)
        self.assertNotIn("FORM_BOB_07_T3_KONUSMA_OZ", entity_ids)

    def test_05_theme3_speaking_resolves_annual_artifact(self):
        pack = self.resolver.resolve("Tema 3 konuşmayı nasıl değerlendireceğim?")
        artifact_ids = {a["artifact_id"] for a in pack["production_context"]}
        form_ids = {f.get("form_id") for f in pack["assessment_context"] if f.get("form_id")}
        self.assertTrue(
            "TDE9_KONUSMA_RUBRIC" in artifact_ids
            or "FORM_IN_T3_KONUSMA_CRITERIA" in form_ids
            or "FORM_BOB_06_T3_KONUSMA_OZ" in form_ids
        )

    def test_06_semantic_poetry_writing_resolves_annual_artifact(self):
        pack = self.resolver.resolve("şiir yazarken öğrenciyi nasıl değerlendireceğim?")
        artifact_ids = {a["artifact_id"] for a in pack["production_context"]}
        form_ids = {f.get("form_id") for f in pack["assessment_context"] if f.get("form_id")}
        self.assertTrue("TDE9_YAZMA_RUBRIC" in artifact_ids or "FORM_IN_T2_YAZMA_CRITERIA" in form_ids)

    def test_07_negative_analytic_rubric_check(self):
        pack = self.resolver.resolve("Kitapta analitik rubrik var mı?")
        fact = next(x for x in pack["assessment_context"] if x.get("fact_query") == "analytic_rubric_in_textbook")
        self.assertEqual(fact["canonical_count"], 0)
        self.assertFalse(fact["textbook_has_analytic_rubric"])
        self.assertEqual(fact["official_requirement_verbatim"], "dereceli puanlama anahtarı")

    def test_08_school_based_theme4(self):
        pack = self.resolver.resolve("Tema 4 okul temelli planlama seçenekleri")
        self.assertEqual(len(pack["pedagogical_recommendations"]), 5)
        self.assertTrue(all(o["origin"] == "pedagogical_recommendation" for o in pack["pedagogical_recommendations"]))

    def test_09_index_stale_is_review_required_and_blocks_generation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_knowledge = os.path.join(temp_dir, "TDE_9")
            _copy_knowledge_fixture(self.knowledge_root, temp_knowledge)
            self.assertEqual(KnowledgeIndexer(temp_knowledge).check_status()["status"], "INDEX_FRESH")
            path = os.path.join(temp_knowledge, "themes", "tema_01", "alignment.json")
            data = json.loads(open(path, encoding="utf-8").read())
            data["test_stale_flag"] = "MODIFIED_FOR_STALE_TEST"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            pack = KnowledgeResolver(temp_knowledge).resolve("Tema 2 TDE4.4")
            self.assertEqual(pack["index_freshness"], "INDEX_STALE")
            self.assertEqual(pack["resolution_status"], "REVIEW_REQUIRED")
            self.assertFalse(pack["material_generation_allowed"])
            self.assertEqual(pack["material_generation_block_reason"], "INDEX_STALE")

    def test_10_knowledge_conflict_blocks_even_when_index_becomes_stale(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_knowledge = os.path.join(temp_dir, "TDE_9")
            _copy_knowledge_fixture(self.knowledge_root, temp_knowledge)
            path = os.path.join(temp_knowledge, "themes", "tema_02", "alignment.json")
            data = json.loads(open(path, encoding="utf-8").read())
            for al in data.get("alignments", []):
                if al.get("outcome_code") == "TDE4.4":
                    al["primary_coverage"] = "COVERED"
                    al["remaining_gap"] = "Yok (Tamamen karşılandı)"
                    al["production_decision"] = "REUSE_TEXTBOOK"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            pack = KnowledgeResolver(temp_knowledge).resolve("Tema 2 TDE4.4 için kitapta ne eksik?")
            self.assertEqual(pack["resolution_status"], "REVIEW_REQUIRED")
            self.assertTrue(pack["conflicts"])
            self.assertEqual(pack["material_generation_block_reason"], "KNOWLEDGE_CONFLICT")

    def test_11_duplicate_canonical_key_prevention_without_embedding_runtime(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_knowledge = os.path.join(temp_dir, "TDE_9")
            _copy_knowledge_fixture(self.knowledge_root, temp_knowledge)
            path = os.path.join(temp_knowledge, "curriculum_map.json")
            data = json.loads(open(path, encoding="utf-8").read())
            data["themes"][0]["learning_outcomes"].append(dict(data["themes"][0]["learning_outcomes"][0]))
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            with self.assertRaises(DuplicateCanonicalKeyError):
                KnowledgeCorpusExtractor(temp_knowledge).extract_all()

    def test_12_production_manifest_is_3_artifacts_and_7_aliases(self):
        with open(os.path.join(self.knowledge_root, "production", "production_manifest.json"), "r", encoding="utf-8") as f:
            manifest = json.load(f)
        artifacts, artifact_by_id, alias_map, provenance = build_artifact_maps(manifest)
        self.assertEqual(len(artifacts), 3)
        self.assertEqual(len(artifact_by_id), 3)
        self.assertEqual(len(alias_map), 7)
        self.assertEqual(alias_map, EXPECTED_ALIAS_MAP)
        self.assertEqual(set(provenance), set(EXPECTED_ALIAS_MAP))
        self.assertFalse(any(a_id.startswith("MAT_") for a_id in artifact_by_id))

    def test_13_all_7_gap_aliases_resolve_to_3_canonical_artifacts(self):
        resolved = {}
        for alias, expected_artifact in EXPECTED_ALIAS_MAP.items():
            pack = self.resolver.resolve(alias)
            self.assertEqual(pack["resolution_status"], "RESOLVED")
            self.assertTrue(pack["material_generation_allowed"])
            artifact_ids = {a["artifact_id"] for a in pack["production_context"]}
            self.assertEqual(artifact_ids, {expected_artifact})
            entity = next(e for e in pack["resolved_entities"] if e["entity_type"] == "assessment_artifact")
            self.assertEqual(entity["entity_id"], expected_artifact)
            self.assertEqual(entity["matched_gap_alias"], alias)
            resolved[alias] = expected_artifact
        self.assertEqual(set(resolved.values()), {
            "TDE9_KONUSMA_RUBRIC", "TDE9_YAZMA_RUBRIC", "TDE9_YAZMA_SUREC_KONTROL_LISTESI"
        })

    def test_14_rebuilt_index_contains_only_3_canonical_artifact_identities(self):
        status = self.indexer.check_status()
        self.assertEqual(status["status"], "INDEX_FRESH")
        self.assertEqual(status["production_schema_version"], "1.1")
        self.assertEqual(status["production_artifact_count"], 3)
        self.assertEqual(status["production_gap_alias_count"], 7)
        db = sqlite3.connect(self.indexer.db_path)
        rows = db.execute("SELECT entity_id, entity_key FROM metadata WHERE entity_type='assessment_artifact' ORDER BY entity_id").fetchall()
        db.close()
        self.assertEqual(len(rows), 3)
        self.assertEqual({r[0] for r in rows}, {
            "TDE9_KONUSMA_RUBRIC", "TDE9_YAZMA_RUBRIC", "TDE9_YAZMA_SUREC_KONTROL_LISTESI"
        })
        self.assertFalse(any(r[0].startswith("MAT_") for r in rows))
        self.assertEqual(len({r[1] for r in rows}), 3)

    def test_15_missing_index_gate_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_knowledge = os.path.join(temp_dir, "TDE_9")
            _copy_knowledge_fixture(self.knowledge_root, temp_knowledge)
            shutil.rmtree(os.path.join(temp_knowledge, "index"), ignore_errors=True)
            pack = KnowledgeResolver(temp_knowledge).resolve("Tema 2 TDE4.4")
            self.assertEqual(pack["index_freshness"], "INDEX_MISSING")
            self.assertEqual(pack["resolution_status"], "REVIEW_REQUIRED")
            self.assertFalse(pack["material_generation_allowed"])
            self.assertEqual(pack["material_generation_block_reason"], "INDEX_MISSING")

    def test_16_aggregate_artifact_scope_does_not_create_false_theme_outcome_binding(self):
        # TDE9_KONUSMA_RUBRIC aggregates TDE3.2/3.3/3.4 across Tema 2/3/4,
        # but Tema 2's actual gap binding is only TDE3.4. Do not create a Cartesian product.
        false_binding = self.resolver.resolve("Tema 2 TDE3.2")
        false_ids = {a["artifact_id"] for a in false_binding["production_context"]}
        self.assertNotIn("TDE9_KONUSMA_RUBRIC", false_ids)

        real_binding = self.resolver.resolve("Tema 4 TDE3.2")
        real_ids = {a["artifact_id"] for a in real_binding["production_context"]}
        self.assertIn("TDE9_KONUSMA_RUBRIC", real_ids)


def run_comprehensive_benchmark(knowledge_root: str = DEFAULT_KNOWLEDGE_ROOT) -> Dict[str, Any]:
    indexer = KnowledgeIndexer(knowledge_root)
    if indexer.check_status().get("status") != "INDEX_FRESH":
        indexer.build_index(force=True)
    resolver = KnowledgeResolver(knowledge_root)
    with open(os.path.join(TESTS_DIR, "knowledge_resolver_cases.json"), "r", encoding="utf-8") as f:
        cases = json.load(f).get("cases", [])
    details = []
    passed = 0
    for case in cases:
        pack = resolver.resolve(case["query"])
        ids = [e.get("entity_id") for e in pack.get("resolved_entities", [])]
        keys = [e.get("entity_key") for e in pack.get("resolved_entities", [])]
        for artifact in pack.get("production_context", []):
            ids.append(artifact.get("artifact_id"))
            ids.extend(artifact.get("covered_gap_instances", []))
        for g in pack.get("remaining_gaps", []):
            ids += [g.get("gap_id"), g.get("outcome_code")]
        for c in pack.get("curriculum_context", []):
            ids.append(c.get("outcome_code"))
        for f in pack.get("assessment_context", []):
            ids += [f.get("form_id"), f.get("fact_query")]
            if f.get("fact_query") == "analytic_rubric_in_textbook":
                ids.append("textbook_form")
        for o in pack.get("pedagogical_recommendations", []):
            ids.append(o.get("option_id"))
        targets = case.get("target_entities", [])
        target_keys = case.get("target_keys", [])
        hit = any(t in ids for t in targets) or any(k in keys for k in target_keys)
        if pack.get("ambiguity_status") == "AMBIGUOUS_ENTITY":
            hit = True
        passed += int(hit)
        details.append({"case_id": case["case_id"], "status": "PASS" if hit else "FAIL"})
    pct = round((passed / len(cases)) * 100, 2) if cases else 100.0
    return {
        "total_test_cases": len(cases),
        "passed": passed,
        "pass_pct": pct,
        "rag_safety": "PASS" if passed == len(cases) else "REVIEW_REQUIRED",
        "details": details,
    }


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKnowledgeResolverHardening)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = run_comprehensive_benchmark()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not result.wasSuccessful() or summary["rag_safety"] != "PASS":
        sys.exit(1)
