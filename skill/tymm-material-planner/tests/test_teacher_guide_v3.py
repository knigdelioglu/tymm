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
        cls.inventory = read_json(COURSE_DIR / "textbook_question_inventory.json")
        cls.inventory_records = {row["question_id"]: row for row in cls.inventory["questions"]}
        cls.textbook_map = read_json(COURSE_DIR / "textbook_map.json")
        cls.validation = validator.validate_course(REPO_ROOT)

    @classmethod
    def guide_questions(cls) -> dict[str, dict]:
        return {
            task["task_id"]: task
            for theme_id in THEMES
            for task in read_json(COURSE_DIR / "teacher_guide" / theme_id / "teacher_guide_v3.json")["tasks"]
            if task["task_type"] == "QUESTION"
        }

    @classmethod
    def index_questions(cls) -> dict[str, dict]:
        return {
            question["task_id"]: question
            for theme in cls.index["themes"]
            for question in theme["questions"]
        }

    @classmethod
    def map_activity_ids(cls) -> set[str]:
        return {
            activity["activity_id"]
            for theme in cls.textbook_map["themes"]
            for section in theme["sections"]
            for activity in section["activities"]
        }

    @staticmethod
    def semantic_task(task_id: str, field: str, value: str, profile: str = "text_analysis", heading: str = "Karagöz çatışması") -> dict:
        return {
            "task_id": task_id,
            "generation_profile": profile,
            "book_heading": heading,
            field: value,
        }

    def assert_semantic_failure(self, field: str) -> None:
        value = (
            "Karagöz ve Hacivat arasındaki çatışma, tip, diyalog, söz varlığı, "
            "anlatıcı, imge, tema, iletişim, mektup ve kanıt ilişkisini görünür kılar."
        )
        tasks = [
            self.semantic_task("TEMA_01::Q01", field, value, heading="Karagöz çatışması"),
            self.semantic_task("TEMA_02::Q02", field, value, heading="Karagöz çatışması"),
        ]
        failures: list[dict] = []
        warnings: list[dict] = []
        validator.validate_repetition(tasks, failures, warnings)
        self.assertTrue(
            any(item.get("code") == "SEMANTIC_BOILERPLATE_REPETITION" and item.get("field") == field for item in failures),
            f"{field} anchor-only repetition was not detected: {failures}",
        )

    def test_index_has_all_textbook_questions_and_activities(self) -> None:
        self.assertEqual(self.index["counts"]["themes"], self.inventory["counts"]["themes"])
        self.assertEqual(self.index["counts"]["questions"], self.inventory["counts"]["questions"])
        self.assertEqual(self.index["counts"]["activities"], len(self.map_activity_ids()))
        self.assertEqual(set(THEMES), {theme["theme_id"] for theme in self.index["themes"]})
        for theme_id in THEMES:
            guide = read_json(COURSE_DIR / "teacher_guide" / theme_id / "teacher_guide_v3.json")
            indexed = next(theme for theme in self.index["themes"] if theme["theme_id"] == theme_id)
            self.assertEqual(len(indexed["questions"]), sum(task["task_type"] == "QUESTION" for task in guide["tasks"]))
            self.assertEqual(len(indexed["activities"]), len(indexed["activity_ids"]))

    def test_inventory_schema_is_valid(self) -> None:
        errors = validator.schema_errors(
            self.inventory,
            SCRIPTS / "../schemas/textbook_question_inventory.schema.json",
        )
        if validator.SCHEMA_VALIDATOR_AVAILABLE is False:
            self.skipTest("jsonschema is installed in CI but unavailable in this local environment")
        self.assertEqual(errors, [])

    def test_inventory_pdf_sha_is_exact(self) -> None:
        pdf = COURSE_DIR / "source_docs" / "turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf"
        self.assertEqual(self.inventory["source_pdf"]["sha256"], builder.sha256_file(pdf))
        self.assertEqual(self.inventory["source_pdf"]["sha256"], self.textbook_map["primary_source"]["sha256"])

    def test_inventory_question_ids_are_unique(self) -> None:
        question_ids = [row["question_id"] for row in self.inventory["questions"]]
        self.assertEqual(len(question_ids), len(set(question_ids)))

    def test_inventory_counts_are_internally_consistent(self) -> None:
        self.assertEqual(self.inventory["counts"]["questions"], len(self.inventory["questions"]))
        self.assertEqual(self.inventory["counts"]["themes"], len({row["theme_id"] for row in self.inventory["questions"]}))
        self.assertEqual(
            self.inventory["counts"]["review_required"],
            sum(row["review_status"] == "REVIEW_REQUIRED" for row in self.inventory["questions"]),
        )

    def test_inventory_mirror_exact_question_set_parity(self) -> None:
        mirror_ids: set[str] = set()
        for theme_id in THEMES:
            mirror_ids.update(validator.mirror_question_records(REPO_ROOT, theme_id)[0])
        self.assertEqual(mirror_ids, set(self.inventory_records))

    def test_inventory_guide_exact_question_set_parity(self) -> None:
        self.assertEqual(set(self.guide_questions()), set(self.inventory_records))

    def test_inventory_index_exact_question_set_parity(self) -> None:
        self.assertEqual(set(self.index_questions()), set(self.inventory_records))

    def test_inventory_projection_page_and_source_locator_parity(self) -> None:
        projection_failures = [
            item
            for item in self.validation["failures"]
            if "PAGE" in item.get("code", "") or "SOURCE" in item.get("code", "") or "DRIFT" in item.get("code", "")
        ]
        self.assertEqual(projection_failures, [])

    def test_no_locator_only_questions(self) -> None:
        questions = self.guide_questions().values()
        self.assertEqual([task["task_id"] for task in questions if task["prompt_mode"] == "LOCATOR_ONLY"], [])

    def test_no_unresolved_question_prompts(self) -> None:
        questions = self.guide_questions().values()
        self.assertEqual(
            [task["task_id"] for task in questions if not task.get("book_prompt") or task.get("prompt_status") == "REVIEW_REQUIRED"],
            [],
        )

    def test_activity_coverage_matches_textbook_map(self) -> None:
        index_activity_ids = {activity["activity_id"] for theme in self.index["themes"] for activity in theme["activities"]}
        guide_activity_refs = {
            ref
            for theme_id in THEMES
            for task in read_json(COURSE_DIR / "teacher_guide" / theme_id / "teacher_guide_v3.json")["tasks"]
            for ref in task.get("activity_refs", [])
        }
        self.assertEqual(index_activity_ids, self.map_activity_ids())
        self.assertEqual(guide_activity_refs & self.map_activity_ids(), self.map_activity_ids())

    def test_v3_validation_has_no_failures_and_reports_fallbacks(self) -> None:
        self.assertEqual(self.validation["failures"], [])
        self.assertEqual(self.validation["counts"]["generic_fallback_tasks"], 0)
        self.assertEqual(self.validation["generic_fallback_details"], [])

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

    def test_prompt_overrides_data_file_is_consumed(self) -> None:
        override_document = read_json(COURSE_DIR / "textbook_prompt_overrides.json")
        self.assertEqual(builder.load_grouped_prompt_overrides(REPO_ROOT), override_document["overrides"])
        mirror_path = COURSE_DIR / "teacher_guide" / "TEMA_01" / "book_mirror_v23.json"
        mirror = builder.merge_mirrors(builder.discover_mirror_paths(mirror_path))
        source = next(entry for entry in mirror["entries"] if entry["mirror_id"] == "T1V23_P28_INTERPRET")
        expanded = builder.expand_mirror_entry(source, override_document["overrides"])
        self.assertEqual(expanded[0]["prompt_mode"], "VERBATIM_SHORT")
        self.assertEqual(expanded[0]["prompt_display"], "Soru 1 — " + override_document["overrides"]["T1V23_P28_INTERPRET"][0]["prompt"])

    def test_builder_contains_no_textbook_prompt_literals(self) -> None:
        source = (SCRIPTS / "build_teacher_guide_v3.py").read_text(encoding="utf-8")
        override_document = read_json(COURSE_DIR / "textbook_prompt_overrides.json")
        for parts in override_document["overrides"].values():
            for part in parts:
                self.assertNotIn(part["prompt"], source)

    def test_anchor_only_changes_do_not_evade_semantic_guard(self) -> None:
        self.assert_semantic_failure("follow_up_questions")

    def test_different_pedagogical_explanations_do_not_false_positive(self) -> None:
        left = self.semantic_task(
            "TEMA_01::Q01",
            "teacher_background",
            "Karagöz Hacivat ortaoyunu tip diyalog çatışma söz varlığı sahne mizahı.",
        )
        right = self.semantic_task(
            "TEMA_01::Q02",
            "teacher_background",
            "Anlatıcı imge tema mektup alıcı iletişim biçim üslup kanıtı.",
        )
        failures: list[dict] = []
        warnings: list[dict] = []
        validator.validate_repetition([left, right], failures, warnings)
        self.assertFalse(any(item.get("code") == "SEMANTIC_BOILERPLATE_REPETITION" for item in failures))
        self.assertEqual(warnings, [])

    def test_exact_repetition_same_profile_theme_fails(self) -> None:
        value = (
            "Karagöz ve Hacivat arasındaki çatışma, tip, diyalog, söz varlığı, "
            "anlatıcı, imge, tema, iletişim, mektup ve kanıt ilişkisini görünür kılar."
        )
        tasks = [
            self.semantic_task("TEMA_01::Q01", "teacher_background", value, profile="text_analysis", heading="Karagöz çatışması"),
            self.semantic_task("TEMA_01::Q02", "teacher_background", value, profile="text_analysis", heading="Karagöz çatışması"),
        ]
        failures: list[dict] = []
        warnings: list[dict] = []
        validator.validate_repetition(tasks, failures, warnings)
        self.assertTrue(
            any(item.get("code") == "SEMANTIC_BOILERPLATE_REPETITION" and item.get("field") == "teacher_background" for item in failures),
            f"Expected SEMANTIC_BOILERPLATE_REPETITION failure for exact repetition: {failures}",
        )
        self.assertEqual(warnings, [])

    def test_same_profile_theme_similarity_warning_range(self) -> None:
        shared = (
            "karagöz hacivat tiyatro oyun sahne perde diyalog çatışma mizah güldürü hiciv "
            "geleneksel temsil kostüm dekor kukla musiki tasvir"
        )
        tasks = [
            self.semantic_task("TEMA_01::Q01", "teacher_background", shared + " ustalık", profile="text_analysis"),
            self.semantic_task("TEMA_01::Q02", "teacher_background", shared + " çıraklık", profile="text_analysis"),
        ]
        failures: list[dict] = []
        warnings: list[dict] = []
        validator.validate_repetition(tasks, failures, warnings)
        self.assertEqual(failures, [])
        self.assertEqual(len(warnings), 1)
        self.assertGreaterEqual(warnings[0]["similarity"], 0.88)
        self.assertLessEqual(warnings[0]["similarity"], 0.92)

    def test_same_profile_theme_similarity_ge_095_fails(self) -> None:
        shared = (
            "karagöz hacivat tiyatro oyun sahne perde diyalog çatışma mizah güldürü hiciv "
            "geleneksel temsil kostüm dekor kukla musiki tasvir ahenk"
        )
        tasks = [
            self.semantic_task("TEMA_01::Q01", "teacher_background", shared + " ustalık", profile="text_analysis"),
            self.semantic_task("TEMA_01::Q02", "teacher_background", shared, profile="text_analysis"),
        ]
        failures: list[dict] = []
        warnings: list[dict] = []
        validator.validate_repetition(tasks, failures, warnings)
        self.assertEqual(warnings, [])
        self.assertTrue(
            any(item.get("code") == "SEMANTIC_BOILERPLATE_REPETITION" and item.get("similarity", 0) >= 0.95 for item in failures),
            f"Expected SEMANTIC_BOILERPLATE_REPETITION for similarity >= 0.95: {failures}",
        )

    def test_cross_theme_similarity_ge_085_fails(self) -> None:
        shared = (
            "karagöz hacivat tiyatro oyun sahne perde diyalog çatışma mizah güldürü hiciv "
            "geleneksel temsil kostüm dekor kukla musiki tasvir"
        )
        tasks = [
            self.semantic_task("TEMA_01::Q01", "teacher_background", shared + " ustalık", profile="text_analysis"),
            self.semantic_task("TEMA_02::Q02", "teacher_background", shared + " çıraklık", profile="text_analysis"),
        ]
        failures: list[dict] = []
        warnings: list[dict] = []
        validator.validate_repetition(tasks, failures, warnings)
        self.assertEqual(warnings, [])
        self.assertTrue(
            any(item.get("code") == "SEMANTIC_BOILERPLATE_REPETITION" for item in failures),
            f"Expected cross-theme 0.85+ similarity failure: {failures}",
        )

    def test_teacher_moves_same_profile_no_exception_fails(self) -> None:
        shared = (
            "karagöz hacivat tiyatro oyun sahne perde diyalog çatışma mizah güldürü hiciv "
            "geleneksel temsil kostüm dekor kukla musiki tasvir"
        )
        tasks = [
            self.semantic_task("TEMA_01::Q01", "teacher_moves", shared + " ustalık", profile="text_analysis"),
            self.semantic_task("TEMA_01::Q02", "teacher_moves", shared + " çıraklık", profile="text_analysis"),
        ]
        failures: list[dict] = []
        warnings: list[dict] = []
        validator.validate_repetition(tasks, failures, warnings)
        self.assertEqual(warnings, [])
        self.assertTrue(
            any(item.get("code") == "SEMANTIC_BOILERPLATE_REPETITION" and item.get("field") == "teacher_moves" for item in failures),
            f"Expected teacher_moves similarity failure: {failures}",
        )

    def test_real_v3_validation_repetition_warnings_below_095(self) -> None:
        self.assertEqual(self.validation["status"], "PASS_WITH_REVIEW")
        self.assertEqual(self.validation["failures"], [])
        self.assertEqual(len(self.validation["warnings"]), 6)
        for warning in self.validation["warnings"]:
            self.assertEqual(warning["code"], "SEMANTIC_COMMON_DOMAIN_DEFINITION")
            self.assertGreaterEqual(warning["similarity"], 0.85)
            self.assertLess(warning["similarity"], 0.95)

    def test_teacher_background_similarity_guard(self) -> None:
        self.assert_semantic_failure("teacher_background")

    def test_student_explanation_similarity_guard(self) -> None:
        self.assert_semantic_failure("student_explanation")

    def test_teacher_moves_similarity_guard(self) -> None:
        self.assert_semantic_failure("teacher_moves")

    def test_answer_explanation_similarity_guard(self) -> None:
        self.assert_semantic_failure("answer_explanation")


if __name__ == "__main__":
    unittest.main()
