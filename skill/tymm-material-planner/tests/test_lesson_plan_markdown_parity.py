#!/usr/bin/env python3
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

import render_lesson_plan_markdown  # noqa: E402
import validate_lesson_plan_markdown  # noqa: E402


def fixture_plan() -> dict:
    return {
        "schema_version": "1.0.0",
        "course_id": "TDE_9",
        "theme_id": "TEMA_01",
        "block_id": "BLOCK_T1_01_OKUMA",
        "lesson_hours": 1,
        "plan_title": "Parity Fixture",
        "plan_summary": "Özet.",
        "outcome_codes": ["TDE2.1"],
        "used_activity_ids": ["T1_ACT_01_OKUMA_ONCESI_SIIR"],
        "used_form_ids": [],
        "lessons": [
            {
                "lesson_no": 1,
                "duration_lesson_hours": 1,
                "title": "Ders",
                "objective": "Hedef.",
                "outcome_codes": ["TDE2.1"],
                "opening": "Giriş.",
                "teacher_actions": ["Öğretmen eylemi."],
                "student_actions": ["Öğrenci eylemi."],
                "activity_ids": ["T1_ACT_01_OKUMA_ONCESI_SIIR"],
                "form_ids": [],
                "assessment": "Kanıt.",
                "closure": "Kapanış.",
                "materials": ["Ders kitabı"],
            }
        ],
        "teacher_notes": "Not.",
        "continuation_summary": {
            "planned_now_hours": 1,
            "remaining_block_hours": 14,
            "covered_outcome_codes": ["TDE2.1"],
            "used_activity_ids": ["T1_ACT_01_OKUMA_ONCESI_SIIR"],
            "next_step_hint": "Devam.",
        },
    }


class LessonPlanMarkdownParityTests(unittest.TestCase):
    def write_pair(self, root: Path, plan: dict) -> tuple[Path, Path]:
        folder = root / "generated/lesson_plans/TEMA_01/BLOCK_T1_01_OKUMA"
        folder.mkdir(parents=True, exist_ok=True)
        json_path = folder / "BLOCK_T1_01_OKUMA_P01.json"
        md_path = json_path.with_suffix(".md")
        json_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(render_lesson_plan_markdown.render(plan), encoding="utf-8")
        return json_path, md_path

    def test_exact_render_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            json_path, _ = self.write_pair(Path(temp), fixture_plan())
            self.assertEqual(validate_lesson_plan_markdown.validate_pair(json_path)["status"], "PASS")

    def test_json_change_without_markdown_regeneration_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            json_path, _ = self.write_pair(root, fixture_plan())
            changed = copy.deepcopy(fixture_plan())
            changed["plan_summary"] = "JSON değişti, Markdown değişmedi."
            json_path.write_text(json.dumps(changed, ensure_ascii=False), encoding="utf-8")
            result = validate_lesson_plan_markdown.validate_pair(json_path)
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("MARKDOWN_PARITY_MISMATCH", result["errors"][0])

    def test_manual_markdown_edit_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            json_path, md_path = self.write_pair(Path(temp), fixture_plan())
            md_path.write_text(md_path.read_text(encoding="utf-8") + "ELLE EK\n", encoding="utf-8")
            self.assertEqual(validate_lesson_plan_markdown.validate_pair(json_path)["status"], "FAIL")

    def test_unknown_json_field_fails_closed(self) -> None:
        plan = fixture_plan()
        plan["future_unrendered_field"] = "sessizce kaybolmamalı"
        with self.assertRaisesRegex(ValueError, "UNRENDERED_FIELDS"):
            render_lesson_plan_markdown.render(plan)

    def test_orphan_markdown_fails_course(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "TDE_9"
            self.write_pair(root, fixture_plan())
            orphan = root / "generated/lesson_plans/TEMA_01/BLOCK_T1_01_OKUMA/ORPHAN.md"
            orphan.write_text("# orphan\n", encoding="utf-8")
            result = validate_lesson_plan_markdown.validate_course(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("ORPHAN_MARKDOWN_WITHOUT_JSON" in item["errors"] for item in result["failures"]))


if __name__ == "__main__":
    unittest.main()
