from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

finalizer = importlib.import_module("finalize_lesson_plan_production")
validation_binding = importlib.import_module("validation_binding")

COMMIT_A = "a" * 40
COMMIT_B = "b" * 40


class ValidationBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.root = self.repo / "courses/TDE_9"
        (self.root / "planning").mkdir(parents=True)
        (self.root / "production").mkdir(parents=True)
        (self.root / "themes/TEMA_01").mkdir(parents=True)
        (self.root / "generated/lesson_plans/TEMA_01/BLOCK_01").mkdir(parents=True)
        (self.repo / "skill/tymm-material-planner/schemas").mkdir(parents=True)

        self.production_plan = self.root / "planning/lesson_plan_production_plan.json"
        self.production_plan.write_text(
            json.dumps(
                {
                    "course_id": "TDE_9",
                    "status": "IN_PROGRESS",
                    "progress": {
                        "total_packages": 1,
                        "completed_packages": 1,
                        "core_instruction_hours": 2,
                        "completed_instruction_hours": 2,
                        "next": None,
                        "last_completed": {"package_id": "P01"},
                    },
                }
            ),
            encoding="utf-8",
        )
        (self.root / "planning/block_hour_bindings.json").write_text("{\"hours\":2}\n", encoding="utf-8")
        (self.root / "planning/course_timeline.json").write_text("{\"generated\":true}\n", encoding="utf-8")
        (self.root / "production/manifest.json").write_text("{\"version\":1}\n", encoding="utf-8")
        (self.root / "themes/TEMA_01/theme.json").write_text("{\"theme\":1}\n", encoding="utf-8")
        self.plan_json = self.root / "generated/lesson_plans/TEMA_01/BLOCK_01/P01.json"
        self.plan_json.write_text("{\"lesson_hours\":2}\n", encoding="utf-8")
        self.plan_json.with_suffix(".md").write_text("# P01\n", encoding="utf-8")
        self.schema = self.repo / "skill/tymm-material-planner/schemas/lesson_plan.schema.json"
        self.schema.write_text("{\"type\":\"object\"}\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def binding(self, commit: str = COMMIT_A) -> dict:
        return validation_binding.build_validation_binding(
            [self.root], self.schema, commit_sha=commit, repo_root=self.repo
        )

    def report(self, binding: dict) -> Path:
        path = self.repo / "report.json"
        path.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "binding": binding,
                    "courses": [{"course_id": "TDE_9", "status": "PASS"}],
                    "summary": {"failure_records": 0, "warning_records": 0},
                }
            ) + "\n",
            encoding="utf-8",
        )
        return path

    def test_finalizer_accepts_exact_report_binding(self) -> None:
        report = self.report(self.binding())
        original_git_head = finalizer.git_head
        finalizer.git_head = lambda: COMMIT_A
        try:
            verified = finalizer.verify_report(report, [self.root], self.schema, COMMIT_A)
        finally:
            finalizer.git_head = original_git_head
        self.assertEqual(verified["commit_sha"], COMMIT_A)
        self.assertTrue(verified["content_fingerprint"].startswith("sha256:"))
        self.assertTrue(verified["report_sha256"].startswith("sha256:"))

    def test_mutated_validated_content_is_rejected(self) -> None:
        report = self.report(self.binding())
        self.plan_json.write_text("{\"lesson_hours\":1}\n", encoding="utf-8")
        original_git_head = finalizer.git_head
        finalizer.git_head = lambda: COMMIT_A
        try:
            with self.assertRaisesRegex(ValueError, "VALIDATION_BINDING_MISMATCH:content_fingerprint"):
                finalizer.verify_report(report, [self.root], self.schema, COMMIT_A)
        finally:
            finalizer.git_head = original_git_head

    def test_report_from_different_commit_is_rejected(self) -> None:
        report = self.report(self.binding(COMMIT_B))
        original_git_head = finalizer.git_head
        finalizer.git_head = lambda: COMMIT_A
        try:
            with self.assertRaisesRegex(ValueError, "VALIDATION_COMMIT_MISMATCH"):
                finalizer.verify_report(report, [self.root], self.schema, COMMIT_A)
        finally:
            finalizer.git_head = original_git_head

    def test_checkout_head_mismatch_is_rejected(self) -> None:
        report = self.report(self.binding())
        original_git_head = finalizer.git_head
        finalizer.git_head = lambda: COMMIT_B
        try:
            with self.assertRaisesRegex(ValueError, "CHECKOUT_HEAD_MISMATCH"):
                finalizer.verify_report(report, [self.root], self.schema, COMMIT_A)
        finally:
            finalizer.git_head = original_git_head

    def test_finalizer_metadata_does_not_invalidate_content_fingerprint(self) -> None:
        before = self.binding()["content_fingerprint"]
        payload = json.loads(self.production_plan.read_text(encoding="utf-8"))
        payload["status"] = "COMPLETED"
        payload["engineering_validation"] = {"status": "PASS", "validation_binding": {"x": 1}}
        payload["progress"]["last_completed"]["validation_status"] = "PASS"
        self.production_plan.write_text(json.dumps(payload), encoding="utf-8")
        after = self.binding()["content_fingerprint"]
        self.assertEqual(before, after)

    def test_generated_timeline_is_not_part_of_validation_fingerprint(self) -> None:
        before = self.binding()["content_fingerprint"]
        (self.root / "planning/course_timeline.json").write_text("{\"generated\":false}\n", encoding="utf-8")
        after = self.binding()["content_fingerprint"]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
