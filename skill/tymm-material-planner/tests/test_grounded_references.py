from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import apply_grounded_references as apply_refs
import validate_grounded_references as validate_refs


class GroundedReferencesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "TDE_9"
        (self.root / "production").mkdir(parents=True)
        (self.root / "generated" / "lesson_plans" / "TEMA_02" / "BLOCK_T2_04_YAZMA").mkdir(parents=True)
        (self.root / "textbook_forms_index.json").write_text(json.dumps({
            "forms": [{"form_id": "FORM_IN_T2_YAZMA_CRITERIA"}]
        }), encoding="utf-8")
        (self.root / "production" / "assessment_artifact_registry.json").write_text(json.dumps({
            "annual_artifacts": [{
                "artifact_id": "TDE9_YAZMA_RUBRIC",
                "task_bindings": [{
                    "gap_instance_id": "MAT_T2_YAZMA_RUBRIC",
                    "theme_id": "TEMA_02",
                    "block_id": "BLOCK_T2_04_YAZMA",
                    "source_equivalence_status": "CANONICAL"
                }]
            }]
        }), encoding="utf-8")
        (self.root / "production" / "consolidated_resource_plan.json").write_text(json.dumps({
            "resources": [{
                "resource_id": "RES_T2_12",
                "resource_plan_ids": ["RES_T2_12"],
                "themes": ["TEMA_02"]
            }]
        }), encoding="utf-8")
        self.catalogs = apply_refs.load_catalogs(self.root)
        self.plan = {
            "course_id": "TDE_9",
            "theme_id": "TEMA_02",
            "block_id": "BLOCK_T2_04_YAZMA",
            "used_form_ids": ["FORM_IN_T2_YAZMA_CRITERIA"],
            "teacher_notes": (
                "FORM_IN_T2_YAZMA_CRITERIA bu derste kullanılır. "
                "RES_T2_12 ve TDE9_YAZMA_RUBRIC sonraki değerlendirme paketine bırakılır."
            ),
            "lessons": [],
        }
        self.plan["grounded_references"] = apply_refs.build_grounding(self.plan, self.catalogs)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_valid_grounding_passes(self) -> None:
        self.assertEqual([], validate_refs.validate_plan(self.root, self.plan, self.catalogs))
        grounding = self.plan["grounded_references"]
        self.assertEqual("USED", grounding["form_refs"][0]["usage"])
        self.assertEqual("DEFERRED", grounding["assessment_artifact_refs"][0]["usage"])
        self.assertEqual("DEFERRED", grounding["resource_refs"][0]["usage"])

    def test_used_form_without_structured_ref_fails(self) -> None:
        broken = copy.deepcopy(self.plan)
        broken["grounded_references"]["form_refs"] = []
        errors = validate_refs.validate_plan(self.root, broken, self.catalogs)
        self.assertTrue(any(error.startswith("FORM_REFERENCE_NOT_GROUNDED") for error in errors), errors)

    def test_artifact_prose_without_structured_ref_fails(self) -> None:
        broken = copy.deepcopy(self.plan)
        broken["grounded_references"]["assessment_artifact_refs"] = []
        errors = validate_refs.validate_plan(self.root, broken, self.catalogs)
        self.assertTrue(any(error.startswith("ARTIFACT_REFERENCE_NOT_GROUNDED") for error in errors), errors)

    def test_unknown_canonical_looking_id_fails(self) -> None:
        broken = copy.deepcopy(self.plan)
        broken["teacher_notes"] += " RES_T2_DOES_NOT_EXIST kullanılacak."
        errors = validate_refs.validate_plan(self.root, broken, self.catalogs)
        self.assertTrue(any(error.startswith("UNRESOLVED_CANONICAL_REFERENCE_TOKENS") for error in errors), errors)

    def test_wrong_artifact_binding_key_fails(self) -> None:
        broken = copy.deepcopy(self.plan)
        broken["grounded_references"]["assessment_artifact_refs"][0]["binding_key"] = "MAT_WRONG"
        errors = validate_refs.validate_plan(self.root, broken, self.catalogs)
        self.assertTrue(any(error.startswith("ARTIFACT_BINDING_KEY_MISMATCH") for error in errors), errors)

    def test_unverified_eba_equivalence_claim_fails(self) -> None:
        catalogs = copy.deepcopy(self.catalogs)
        catalogs["artifacts"]["TDE9_YAZMA_RUBRIC"]["task_bindings"][0]["source_equivalence_status"] = (
            "DERIVED_CANONICAL_SUPPORT_EXTERNAL_EBA_EXACT_EQUIVALENCE_UNVERIFIED"
        )
        broken = copy.deepcopy(self.plan)
        broken["teacher_notes"] = "TDE9_YAZMA_RUBRIC EBA ile aynı rubriktir ve bu derste kullanılır."
        broken["grounded_references"] = apply_refs.build_grounding(broken, catalogs)
        errors = validate_refs.validate_plan(self.root, broken, catalogs)
        self.assertIn("UNVERIFIED_EXTERNAL_ASSESSMENT_EQUIVALENCE_CLAIM", errors)


if __name__ == "__main__":
    unittest.main()
