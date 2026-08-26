#!/usr/bin/env python3
"""Regression tests for the dependency-free runtime projection compiler."""
import json, shutil, sqlite3, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import build_runtime_course_package as compiler
import runtime_lesson_plan_payload as lesson_payload

ROOT = Path(__file__).parents[3] / "courses" / "TDE_9"

class RuntimePackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "TDE_9"
        shutil.copytree(ROOT, self.tmp, ignore=shutil.ignore_patterns("runtime", "*.sqlite"))
    def tearDown(self): shutil.rmtree(self.tmp.parent, ignore_errors=True)
    def mutate(self, rel, fn):
        p=self.tmp/rel; d=json.loads(p.read_text()); fn(d); p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
    def build(self): return compiler.build(self.tmp)
    def test_01_unknown_outcome_relation_fails_closed(self):
        self.mutate("production/teaching_blocks.json", lambda d:d["blocks"][0]["curriculum_outcomes"].append("TDE9_UNKNOWN"))
        with self.assertRaises(ValueError): self.build()
    def test_02_duplicate_canonical_id_fails(self):
        def add(d): d["themes"][0]["learning_outcomes"].append(dict(d["themes"][0]["learning_outcomes"][0]))
        self.mutate("curriculum_map.json", add)
        with self.assertRaises((sqlite3.IntegrityError, ValueError)): self.build()
    def test_03_block_hours_resolve_and_project(self):
        self.assertEqual(self.build()["status"], "PASS")
        db=sqlite3.connect(self.tmp/"runtime/course_runtime.sqlite")
        self.assertEqual(db.execute("SELECT COUNT(*) FROM blocks WHERE planned_hours IS NOT NULL").fetchone()[0], 16)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM timeline_blocks WHERE planned_hours IS NOT NULL").fetchone()[0], 16)
        self.assertEqual(db.execute("SELECT planned_hours FROM blocks WHERE block_id='BLOCK_T1_01_OKUMA'").fetchone()[0], 15)
        self.assertEqual(db.execute("SELECT planned_hours FROM blocks WHERE block_id='BLOCK_T1_02_DINLEME'").fetchone()[0], 8)
        self.assertEqual(db.execute("SELECT planned_hours FROM blocks WHERE block_id='BLOCK_T1_03_YAZMA'").fetchone()[0], 10)
        self.assertEqual(db.execute("SELECT planned_hours FROM blocks WHERE block_id='BLOCK_T1_04_KONUSMA'").fetchone()[0], 10)
        self.assertEqual(dict(db.execute("SELECT theme_id,SUM(planned_hours) FROM timeline_blocks GROUP BY theme_id")), {"TEMA_01":43,"TEMA_02":43,"TEMA_03":43,"TEMA_04":43})
        manifest=json.loads((self.tmp/"runtime/runtime_manifest.json").read_text())
        self.assertEqual(manifest["runtime_package_version"], lesson_payload.RUNTIME_PACKAGE_VERSION)
        self.assertEqual(manifest["compiler_version"], compiler.COMPILER_VERSION)
        self.assertEqual(manifest["schema_version"], lesson_payload.RUNTIME_SCHEMA_VERSION)
        self.assertEqual(manifest["timeline_resolution"], "BLOCK_TIME_RESOLVED")
        self.assertIsNone(manifest["timeline_unresolved_fields"]["block_hours"])
        self.assertEqual(manifest["block_hour_binding_status"], "BLOCK_TIME_RESOLVED")
        self.assertEqual(manifest["row_counts"]["lesson_plan_packages"], 88)
    def test_04_textbook_body_not_projected(self):
        self.assertEqual(self.build()["status"], "PASS")
        db=sqlite3.connect(self.tmp/"runtime/course_runtime.sqlite")
        names={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertNotIn("text_body", names)
    def test_05_gap_mapping_resolves_artifact(self):
        self.assertEqual(self.build()["status"], "PASS")
        db=sqlite3.connect(self.tmp/"runtime/course_runtime.sqlite")
        self.assertEqual(db.execute("SELECT COUNT(*) FROM assessment_gap_mappings g JOIN assessment_artifacts a ON a.artifact_id=g.artifact_id").fetchone()[0], 7)
    def test_06_theme_block_order_preserved(self):
        self.assertEqual(self.build()["status"], "PASS")
        db=sqlite3.connect(self.tmp/"runtime/course_runtime.sqlite")
        self.assertEqual(db.execute("SELECT COUNT(*) FROM timeline_blocks WHERE block_order IS NULL").fetchone()[0], 0)
        self.assertEqual(db.execute("SELECT GROUP_CONCAT(theme_id, ',') FROM timeline_themes ORDER BY theme_order").fetchone()[0], "TEMA_01,TEMA_02,TEMA_03,TEMA_04")
    def test_07_source_change_is_stale(self):
        self.assertEqual(self.build()["status"], "PASS")
        self.mutate("curriculum_map.json", lambda d:d.update({"course_title": d["course_title"] + " "}))
        self.assertNotEqual(compiler.compiler_state(self.tmp)[1], json.loads((self.tmp/"runtime/runtime_manifest.json").read_text())["canonical_content_fingerprint"])
    def test_08_user_state_table_absent(self):
        self.assertEqual(self.build()["status"], "PASS")
        db=sqlite3.connect(self.tmp/"runtime/course_runtime.sqlite")
        self.assertFalse(any(any(x in r[0].lower() for x in ("teacher","student","user","progress","notes")) for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")))
    def test_09_five_query_entity_classes_present(self):
        self.assertEqual(self.build()["status"], "PASS")
        db=sqlite3.connect(self.tmp/"runtime/course_runtime.sqlite")
        for sql in ["SELECT * FROM blocks WHERE theme_id='TEMA_02'", "SELECT * FROM timeline_blocks", "SELECT * FROM assessment_artifacts", "SELECT * FROM forms", "SELECT * FROM source_references"]: self.assertTrue(db.execute(sql).fetchone())
    def test_10_vector_model_dependencies_absent(self):
        self.assertEqual(self.build()["status"], "PASS")
        db=sqlite3.connect(self.tmp/"runtime/course_runtime.sqlite")
        self.assertFalse(any(any(x in r[0].lower() for x in ("vector","embedding","onnx","model")) for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")))
    def test_11_invalid_block_hour_total_fails_closed(self):
        self.mutate("planning/block_hour_bindings.json", lambda d:d["themes"][0]["bindings"][0].update({"planned_hours":14}))
        with self.assertRaises(ValueError): self.build()
    def test_12_effective_process_components_are_projected(self):
        self.assertEqual(self.build()["status"], "PASS")
        db=sqlite3.connect(self.tmp/"runtime/course_runtime.sqlite")
        self.assertEqual(db.execute("SELECT COUNT(*) FROM outcomes WHERE process_components IS NULL OR process_components='' OR process_components='[]'").fetchone()[0], 0)
        self.assertEqual(dict(db.execute("SELECT process_component_origin,COUNT(*) FROM outcomes GROUP BY process_component_origin")), {"ROOF_INHERITED":52,"THEME_EXPLICIT":2})
        inherited=db.execute("SELECT process_components,process_component_origin FROM outcomes WHERE outcome_id='TDE9_T1_D1'").fetchone()
        self.assertEqual(inherited[1], "ROOF_INHERITED")
        self.assertEqual(len(json.loads(inherited[0])), 2)
        explicit=db.execute("SELECT process_components,process_component_origin FROM outcomes WHERE outcome_id='TDE9_T1_D2'").fetchone()
        self.assertEqual(explicit[1], "THEME_EXPLICIT")
        self.assertEqual(len(json.loads(explicit[0])), 4)
        db.close()
    def test_13_process_component_sources_participate_in_fingerprint(self):
        self.assertEqual(self.build()["status"], "PASS")
        manifest=json.loads((self.tmp/"runtime/runtime_manifest.json").read_text())
        self.assertEqual(manifest["process_component_resolution_status"], "PASS")
        self.assertEqual(manifest["process_component_counts"]["inherited_component_outcomes"], 52)
        self.assertIn("curriculum_process_component_resolution.json", manifest["canonical_source_hashes"])
        self.assertIn("../TDE_SHARED/curriculum_process_component_catalog.json", manifest["canonical_source_hashes"])

if __name__ == "__main__": unittest.main()
