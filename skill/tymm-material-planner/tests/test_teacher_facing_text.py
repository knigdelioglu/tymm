#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import teacher_facing_text  # noqa: E402

COURSES = Path(__file__).resolve().parents[3] / "courses"
ROOT9 = COURSES / "TDE_9"
ROOT10 = COURSES / "TDE_10"


class TeacherFacingTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog9 = teacher_facing_text.TeacherReferenceCatalog.from_knowledge_root(ROOT9)
        cls.catalog10 = teacher_facing_text.TeacherReferenceCatalog.from_knowledge_root(ROOT10)
        cls.ranges = {1: (1, 2), 2: (3, 4), 3: (5, 6)}

    def fixture_plan(self) -> dict:
        return {
            "course_id": "TDE_9",
            "theme_id": "TEMA_01",
            "block_id": "BLOCK_T1_01_OKUMA",
            "plan_title": "Okuma çalışması",
            "plan_summary": "İki derslik okuma çalışması.",
            "used_activity_ids": ["T1_ACT_04_GUZEL_SANATLAR_DISIPLINLER"],
            "used_form_ids": [],
            "lessons": [
                {
                    "title": "Ders",
                    "objective": "Hedef.",
                    "opening": "Giriş.",
                    "teacher_actions": ["T1_ACT_04 üzerinden tartışmayı yürüt."],
                    "student_actions": ["Çalışmayı tamamlar."],
                    "assessment": "Kanıtı kontrol et.",
                    "closure": "Dersi kapat.",
                    "materials": ["Ders kitabı"],
                    "activity_ids": ["T1_ACT_04_GUZEL_SANATLAR_DISIPLINLER"],
                    "form_ids": [],
                    "outcome_codes": ["TDE2.1"],
                }
            ],
            "teacher_notes": "Bu plan BLOCK_T1_01_OKUMA bloğunun bir kesitidir.",
            "continuation_summary": {
                "next_step_hint": "P02'de T1_ACT_04 ve T1_ACT_05 ile devam et.",
                "used_activity_ids": ["T1_ACT_04_GUZEL_SANATLAR_DISIPLINLER"],
                "covered_outcome_codes": ["TDE2.1"],
            },
        }

    def test_catalog_resolves_real_titles_pages_and_package_range(self) -> None:
        text = teacher_facing_text.humanize_teacher_text(
            "P02'de T1_ACT_04, T1_ACT_05 ve BLOCK_T1_01_OKUMA ile devam et.",
            plan=self.fixture_plan(),
            catalog=self.catalog9,
            package_ranges=self.ranges,
        )
        self.assertIn("3–4. ders saatlerinde", text)
        self.assertIn(
            "Güzel Sanatlar ve Diğer Disiplinlerle İlişki Tahlili (ders kitabı s. 21-26)",
            text,
        )
        self.assertIn(
            "Dil Bilgisi: Türkçenin Ses Bilgisi ve Ses Olayları (ders kitabı s. 27-36)",
            text,
        )
        self.assertIn("1. Tema Okuma Bloğu: Şiir ve Deneme Metin Tahlili", text)
        self.assertIsNone(teacher_facing_text.TECHNICAL_REFERENCE_RE.search(text))

    def test_package_range_is_one_readable_lesson_hour_reference(self) -> None:
        text = teacher_facing_text.humanize_teacher_text(
            "P01-P02 notlarını karşılaştır.",
            plan=self.fixture_plan(),
            catalog=self.catalog9,
            package_ranges=self.ranges,
        )
        self.assertEqual(text, "1–4. ders saatlerinin notlarını karşılaştır.")

    def test_cross_block_package_reference_resolves_from_generated_catalog(self) -> None:
        text = teacher_facing_text.humanize_teacher_text(
            "BLOCK_T1_02_DINLEME_P01 ile devam et.",
            plan=self.fixture_plan(),
            catalog=self.catalog9,
            package_ranges=self.ranges,
        )
        self.assertNotIn("BLOCK_", text)
        self.assertIn("ders saat", text)

    def test_tde10_activity_title_schema_and_canonical_form_registry_are_supported(self) -> None:
        plan = {
            "course_id": "TDE_10",
            "theme_id": "TEMA_01",
            "block_id": "BLOCK_T1_01_OKUMA",
        }
        text = teacher_facing_text.humanize_teacher_text(
            "T1_ACT_01_KOSUK_HAZIRLIK ve FORM_T10_T1_KONUSMA_DPA_CANONICAL kullanılır.",
            plan=plan,
            catalog=self.catalog10,
            package_ranges=self.ranges,
        )
        self.assertIn("Sıra Sizde (ders kitabı s. 13-16)", text)
        self.assertIn("Şiir Dinletisi değerlendirme formu", text)
        self.assertIsNone(teacher_facing_text.TECHNICAL_REFERENCE_RE.search(text))

    def test_normalization_changes_prose_but_preserves_structured_ids(self) -> None:
        plan = self.fixture_plan()
        original = copy.deepcopy(plan)
        normalized = teacher_facing_text.normalize_teacher_facing_text(
            plan,
            catalog=self.catalog9,
            package_ranges=self.ranges,
        )
        self.assertEqual(normalized["course_id"], original["course_id"])
        self.assertEqual(normalized["theme_id"], original["theme_id"])
        self.assertEqual(normalized["block_id"], original["block_id"])
        self.assertEqual(normalized["used_activity_ids"], original["used_activity_ids"])
        self.assertEqual(
            normalized["lessons"][0]["activity_ids"],
            original["lessons"][0]["activity_ids"],
        )
        self.assertIn("1. Tema Okuma Bloğu", normalized["teacher_notes"])
        self.assertIn("3–4. ders saatlerinde", normalized["continuation_summary"]["next_step_hint"])
        self.assertFalse(teacher_facing_text.teacher_facing_validation_errors(normalized))

    def test_validator_reports_raw_id_in_teacher_prose(self) -> None:
        plan = self.fixture_plan()
        errors = teacher_facing_text.teacher_facing_validation_errors(plan)
        self.assertTrue(any("teacher_notes:BLOCK_T1_01_OKUMA" in item for item in errors))
        self.assertTrue(any("continuation_summary.next_step_hint:P02" in item for item in errors))

    def test_unknown_technical_reference_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            teacher_facing_text.TeacherFacingTextError,
            "UNRESOLVED_TEACHER_REFERENCES",
        ):
            teacher_facing_text.humanize_teacher_text(
                "T9_ACT_99_BILINMEYEN etkinliğini uygula.",
                plan=self.fixture_plan(),
                catalog=self.catalog9,
                package_ranges=self.ranges,
            )


if __name__ == "__main__":
    unittest.main()
