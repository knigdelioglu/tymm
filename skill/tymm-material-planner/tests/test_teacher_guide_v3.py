#!/usr/bin/env python3
"""Regression tests for the textbook-first TDE 11 Teacher Guide V3 chain."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "skill" / "tymm-material-planner" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_teacher_guide_v3 as builder
import validate_teacher_guide_v3 as validator


COURSE_DIR = REPO_ROOT / "courses" / "TDE_11"
THEMES = [f"TEMA_{number:02d}" for number in range(1, 5)]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TeacherGuideV3ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = read_json(COURSE_DIR / "teacher_guide_v3" / "textbook_task_index.json")

    def test_index_has_all_textbook_questions_and_activities(self) -> None:
        self.assertEqual(self.index["counts"], {"themes": 4, "questions": 407, "activities": 84})
        self.assertEqual(set(THEMES), {theme["theme_id"] for theme in self.index["themes"]})
        for theme_id in THEMES:
            guide = read_json(COURSE_DIR / "teacher_guide" / theme_id / "teacher_guide_v3.json")
            indexed = next(theme for theme in self.index["themes"] if theme["theme_id"] == theme_id)
            self.assertEqual(len(indexed["questions"]), sum(task["task_type"] == "QUESTION" for task in guide["tasks"]))
            self.assertEqual(len(indexed["activities"]), len(indexed["activity_ids"]))

    def test_grouped_prompts_are_split_with_faithful_short_text(self) -> None:
        mirror_path = COURSE_DIR / "teacher_guide" / "TEMA_01" / "book_mirror_v23.json"
        mirror = builder.merge_mirrors(builder.discover_mirror_paths(mirror_path))

        interpret = next(entry for entry in mirror["entries"] if entry["mirror_id"] == "T1V23_P28_INTERPRET")
        expanded = builder.expand_mirror_entry(interpret)
        self.assertEqual([entry["mirror_id"] for entry in expanded], ["T1V23_P28_INTERPRET#Q1", "T1V23_P28_INTERPRET#Q2", "T1V23_P28_INTERPRET#Q3"])
        self.assertEqual(expanded[0]["prompt_display"], "Soru 1 — Yazıcı metnindeki tiplerin söz varlıklarının onların sosyal statülerine ve eğitim durumlarına uygunluğu hakkındaki düşüncelerinizi metinden örneklerle ifade ediniz.")
        self.assertTrue(all(entry["split_from_group"] and entry["prompt_mode"] == "VERBATIM_SHORT" for entry in expanded))

        friendship = next(entry for entry in mirror["entries"] if entry["mirror_id"] == "T1V23_P29_FRIENDSHIP")
        friendship_expanded = builder.expand_mirror_entry(friendship)
        self.assertEqual(len(friendship_expanded), 2)
        self.assertEqual(friendship_expanded[1]["answer_keys"], ["q2"])

    def test_prompt_and_answer_projection_parity(self) -> None:
        for theme_id in THEMES:
            theme_dir = COURSE_DIR / "teacher_guide" / theme_id
            guide = read_json(theme_dir / "teacher_guide_v3.json")
            manifest = read_json(theme_dir / "teacher_guide.json")
            _sections, canonical = builder.index_canonical(REPO_ROOT, manifest)
            builder.apply_component_registries(REPO_ROOT, theme_id, canonical)
            mirror = builder.merge_mirrors(builder.discover_mirror_paths(theme_dir / "book_mirror_v23.json"))
            mirror_questions = {
                f"{theme_id}::{entry['mirror_id']}": entry
                for source in mirror["entries"]
                for entry in builder.expand_mirror_entry(source)
                if entry.get("presentation_type") == "QUESTION"
            }
            guide_questions = {task["task_id"]: task for task in guide["tasks"] if task["task_type"] == "QUESTION"}
            self.assertEqual(set(mirror_questions), set(guide_questions))
            for task_id, source in mirror_questions.items():
                task = guide_questions[task_id]
                self.assertEqual(task["book_prompt"], source["prompt_display"])
                expected, errors = builder.project_answer(canonical, task["canonical_item_refs"], task["answer_component_keys"])
                self.assertEqual(errors, [], task_id)
                self.assertEqual(task["expected_answer"], expected, task_id)
                self.assertNotEqual(task["prompt_mode"], "LOCATOR_ONLY")
                self.assertNotEqual(task["prompt_status"], "REVIEW_REQUIRED")

    def test_explanations_are_not_answer_only_paraphrases(self) -> None:
        for theme_id in THEMES:
            guide = read_json(COURSE_DIR / "teacher_guide" / theme_id / "teacher_guide_v3.json")
            for task in guide["tasks"]:
                self.assertGreaterEqual(len(task["answer_explanation"].strip()), 40, task["task_id"])
                if task.get("expected_answer") is not None:
                    self.assertFalse(
                        validator.answer_paraphrase_guard(task["expected_answer"], task["answer_explanation"]),
                        task["task_id"],
                    )

    def test_provenance_page_and_review_boundaries(self) -> None:
        review_count = 0
        task_ids: set[str] = set()
        for theme_id in THEMES:
            guide = read_json(COURSE_DIR / "teacher_guide" / theme_id / "teacher_guide_v3.json")
            for task in guide["tasks"]:
                self.assertNotIn(task["task_id"], task_ids)
                task_ids.add(task["task_id"])
                self.assertIn(builder.TEXTBOOK_SOURCE_ID, task["provenance"]["source_ids"])
                self.assertTrue(task["source_locators"])
                self.assertIn("basılı s.", task["source_locator"])
                if task["content_status"] == "REVIEW_REQUIRED":
                    review_count += 1
                    self.assertTrue(task.get("review_reasons"), task["task_id"])
        self.assertEqual(review_count, 8)

    def test_renderer_is_deterministic_and_materialized(self) -> None:
        for theme_id in THEMES:
            guide_path = COURSE_DIR / "teacher_guide" / theme_id / "teacher_guide_v3.json"
            guide = read_json(guide_path)
            rendered = builder.render_markdown(guide)
            materialized = (guide_path.parent / "TEACHER_GUIDE_V3.md").read_text(encoding="utf-8")
            self.assertEqual(rendered, builder.render_markdown(guide))
            self.assertEqual(rendered, materialized)
            self.assertIn("### Kitaptaki görev", rendered)
            self.assertIn("### Açıklama ve gerekçe", rendered)
            self.assertNotIn("LOCATOR_ONLY", rendered)

    def test_schema_and_common_teacher_fields_are_present(self) -> None:
        schema = read_json(SCRIPTS / "../schemas/teacher_guide_v3.schema.json")
        self.assertEqual(schema["properties"]["schema_version"]["const"], "3.0.0")
        required = set(schema["$defs"]["task"]["required"])
        for theme_id in THEMES:
            guide = read_json(COURSE_DIR / "teacher_guide" / theme_id / "teacher_guide_v3.json")
            for task in guide["tasks"]:
                self.assertTrue(required <= set(task), task["task_id"])
                if task["task_type"] == "QUESTION":
                    for field in ["teacher_background", "student_explanation", "teacher_moves", "assessment_look_fors"]:
                        self.assertTrue(task.get(field), f"{task['task_id']}: {field}")


if __name__ == "__main__":
    unittest.main()
