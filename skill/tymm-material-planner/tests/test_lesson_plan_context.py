#!/usr/bin/env python3
"""Regression tests for source-bound lesson-plan context assembly and validation."""
import json, shutil, tempfile, unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build_runtime_course_package as compiler
import lesson_plan_context
import validate_lesson_plan

ROOT = Path(__file__).parents[3] / "courses" / "TDE_9"


class LessonPlanContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "TDE_9"
        shutil.copytree(ROOT, self.tmp, ignore=shutil.ignore_patterns("runtime", "*.sqlite"))
        self.assertEqual(compiler.build(self.tmp)["status"], "PASS")

    def tearDown(self):
        shutil.rmtree(self.tmp.parent, ignore_errors=True)

    def test_context_resolves_source_bound_two_hour_slice(self):
        context = lesson_plan_context.assemble(self.tmp, "BLOCK_T1_01_OKUMA", 2)
        self.assertEqual(context["resolution_status"], "RESOLVED")
        self.assertEqual(context["context_version"], "1.2.0")
        self.assertEqual(context["course"]["course_id"], "TDE_9")
        self.assertEqual(context["block"]["planned_hours"], 15)
        self.assertEqual(context["planning_request"]["requested_lesson_hours"], 2)
        self.assertEqual(context["planning_request"]["remaining_block_hours_after_this_plan"], 13)
        self.assertTrue(context["planning_request"]["partial_block_plan"])
        self.assertFalse(context["planning_request"]["calendar_binding_used"])
        self.assertEqual(set(context["allowed_references"]["outcome_codes"]), {"TDE2.1", "TDE2.2"})
        self.assertGreater(
            len(context["allowed_references"]["theme_outcome_codes"]),
            len(context["allowed_references"]["outcome_codes"]),
        )
        self.assertTrue(context["theme_outcomes"])
        self.assertTrue(context["textbook_activities"])
        self.assertTrue(all("text_body" not in item for item in context["textbook_activities"]))
        self.assertEqual(context["provenance"]["timeline_resolution"], "BLOCK_TIME_RESOLVED")

    def test_context_rejects_hours_beyond_block(self):
        with self.assertRaises(ValueError):
            lesson_plan_context.assemble(self.tmp, "BLOCK_T1_01_OKUMA", 16)

    def test_context_rejects_unknown_block(self):
        with self.assertRaises(ValueError):
            lesson_plan_context.assemble(self.tmp, "BLOCK_UNKNOWN", 1)

    def test_validator_accepts_grounded_plan(self):
        context = lesson_plan_context.assemble(self.tmp, "BLOCK_T1_01_OKUMA", 2)
        activities = context["allowed_references"]["activity_ids"][:2]
        forms = context["allowed_references"]["form_ids"][:1]
        plan = {
            "course_id": "TDE_9",
            "theme_id": "TEMA_01",
            "block_id": "BLOCK_T1_01_OKUMA",
            "lesson_hours": 2,
            "outcome_codes": ["TDE2.1", "TDE2.2"],
            "used_activity_ids": activities,
            "used_form_ids": forms,
            "lessons": [
                {"lesson_no": 1, "duration_lesson_hours": 1, "title": "Hazırlık ve okuma"},
                {"lesson_no": 2, "duration_lesson_hours": 1, "title": "Tahlil ve değerlendirme"},
            ],
            "continuation_summary": {
                "planned_now_hours": 2,
                "covered_outcome_codes": ["TDE2.1", "TDE2.2"],
                "used_activity_ids": activities,
            },
        }
        result = validate_lesson_plan.validate(context, plan)
        self.assertEqual(result["status"], "PASS", result)

    def test_validator_rejects_invented_reference_and_calendar_field(self):
        context = lesson_plan_context.assemble(self.tmp, "BLOCK_T1_01_OKUMA", 1)
        plan = {
            "course_id": "TDE_9",
            "theme_id": "TEMA_01",
            "block_id": "BLOCK_T1_01_OKUMA",
            "lesson_hours": 1,
            "outcome_codes": ["TDE_FAKE"],
            "used_activity_ids": ["ACT_FAKE"],
            "used_form_ids": [],
            "date_range": "8-12 Eylül",
            "lessons": [{"lesson_no": 1, "duration_lesson_hours": 1, "title": "x"}],
        }
        result = validate_lesson_plan.validate(context, plan)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any(x.startswith("UNKNOWN_OUTCOME_CODES") for x in result["errors"]))
        self.assertTrue(any(x.startswith("UNKNOWN_ACTIVITY_IDS") for x in result["errors"]))
        self.assertTrue(any(x.startswith("CALENDAR_FIELDS_OUT_OF_SCOPE") for x in result["errors"]))

    def _theme_assessment_fixture(self):
        context = lesson_plan_context.assemble(self.tmp, "BLOCK_T1_04_KONUSMA", 2)
        theme_activity = next(
            activity_id
            for activity_id in context["allowed_references"]["activity_ids"]
            if "TEMA_SONU_OLCME" in activity_id
        )
        block_outcomes = context["allowed_references"]["outcome_codes"]
        theme_outcomes = context["allowed_references"]["theme_outcome_codes"]
        return context, theme_activity, block_outcomes, theme_outcomes

    def test_learning_diary_is_theme_scope_signal(self):
        context = lesson_plan_context.assemble(self.tmp, "BLOCK_T1_04_KONUSMA", 2)
        diary_id = next(
            activity_id
            for activity_id in context["allowed_references"]["activity_ids"]
            if "OGRENME_GUNLUGU" in activity_id
        )
        self.assertIn(diary_id, validate_lesson_plan._theme_assessment_activity_ids(context))

    def test_theme_assessment_requires_explicit_theme_scope(self):
        context, theme_activity, block_outcomes, _ = self._theme_assessment_fixture()
        plan = {
            "course_id": "TDE_9",
            "theme_id": "TEMA_01",
            "block_id": "BLOCK_T1_04_KONUSMA",
            "lesson_hours": 2,
            "outcome_codes": block_outcomes,
            "used_activity_ids": [theme_activity],
            "used_form_ids": [],
            "lessons": [
                {"lesson_no": 1, "duration_lesson_hours": 1, "outcome_codes": block_outcomes, "activity_ids": [], "form_ids": []},
                {"lesson_no": 2, "duration_lesson_hours": 1, "outcome_codes": block_outcomes, "activity_ids": [theme_activity], "form_ids": []},
            ],
            "continuation_summary": {
                "planned_now_hours": 2,
                "covered_outcome_codes": block_outcomes,
                "used_activity_ids": [theme_activity],
            },
        }
        result = validate_lesson_plan.validate(context, plan)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("THEME_ASSESSMENT_SCOPE_REQUIRED", result["errors"])
        self.assertIn("LESSON_2_THEME_ASSESSMENT_SCOPE_REQUIRED", result["errors"])

    def test_theme_assessment_accepts_theme_outcome_scope(self):
        context, theme_activity, block_outcomes, theme_outcomes = self._theme_assessment_fixture()
        plan = {
            "course_id": "TDE_9",
            "theme_id": "TEMA_01",
            "block_id": "BLOCK_T1_04_KONUSMA",
            "lesson_hours": 2,
            "instruction_scope": "BLOCK",
            "assessment_scope": "THEME",
            "assessed_outcome_codes": theme_outcomes,
            "outcome_codes": block_outcomes,
            "used_activity_ids": [theme_activity],
            "used_form_ids": [],
            "lessons": [
                {
                    "lesson_no": 1,
                    "duration_lesson_hours": 1,
                    "outcome_codes": block_outcomes,
                    "activity_ids": [],
                    "form_ids": [],
                },
                {
                    "lesson_no": 2,
                    "duration_lesson_hours": 1,
                    "instruction_scope": "BLOCK",
                    "assessment_scope": "THEME",
                    "assessed_outcome_codes": theme_outcomes,
                    "outcome_codes": block_outcomes,
                    "activity_ids": [theme_activity],
                    "form_ids": [],
                },
            ],
            "continuation_summary": {
                "planned_now_hours": 2,
                "covered_outcome_codes": block_outcomes,
                "used_activity_ids": [theme_activity],
            },
        }
        result = validate_lesson_plan.validate(context, plan)
        self.assertEqual(result["status"], "PASS", result)

    def test_theme_assessment_cannot_claim_only_last_block_outcomes(self):
        context, theme_activity, block_outcomes, _ = self._theme_assessment_fixture()
        plan = {
            "course_id": "TDE_9",
            "theme_id": "TEMA_01",
            "block_id": "BLOCK_T1_04_KONUSMA",
            "lesson_hours": 2,
            "assessment_scope": "THEME",
            "assessed_outcome_codes": block_outcomes,
            "outcome_codes": block_outcomes,
            "used_activity_ids": [theme_activity],
            "used_form_ids": [],
            "lessons": [
                {"lesson_no": 1, "duration_lesson_hours": 1, "outcome_codes": block_outcomes, "activity_ids": [], "form_ids": []},
                {
                    "lesson_no": 2,
                    "duration_lesson_hours": 1,
                    "assessment_scope": "THEME",
                    "assessed_outcome_codes": block_outcomes,
                    "outcome_codes": block_outcomes,
                    "activity_ids": [theme_activity],
                    "form_ids": [],
                },
            ],
            "continuation_summary": {
                "planned_now_hours": 2,
                "covered_outcome_codes": block_outcomes,
                "used_activity_ids": [theme_activity],
            },
        }
        result = validate_lesson_plan.validate(context, plan)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("THEME_ASSESSMENT_OUTCOMES_TOO_NARROW", result["errors"])
        self.assertIn("LESSON_2_THEME_ASSESSMENT_OUTCOMES_TOO_NARROW", result["errors"])


if __name__ == "__main__":
    unittest.main()
