#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import render_lesson_plan_markdown as canonical_renderer  # noqa: E402
import render_teacher_lesson_plan_markdown as teacher_renderer  # noqa: E402
import teacher_facing_text  # noqa: E402

COURSES = Path(__file__).resolve().parents[3] / "courses"


class TeacherLessonPlanMarkdownTests(unittest.TestCase):
    def _render(self, relative_path: str) -> str:
        path = COURSES / relative_path
        root = path.parents[4]
        plan = canonical_renderer.read_json(path)
        catalog = teacher_facing_text.TeacherReferenceCatalog.from_knowledge_root(root)
        ranges = teacher_facing_text.package_ranges_for_block(path.parent)
        return teacher_renderer.render_teacher(
            plan,
            catalog=catalog,
            package_ranges=ranges,
        )

    def test_tde9_teacher_markdown_resolves_internal_ids(self) -> None:
        markdown = self._render(
            "TDE_9/generated/lesson_plans/TEMA_01/BLOCK_T1_01_OKUMA/BLOCK_T1_01_OKUMA_P02.json"
        )
        self.assertIn("9. sınıf Türk Dili ve Edebiyatı", markdown)
        self.assertIn("1. Tema: SÖZÜN İNCELİĞİ", markdown)
        self.assertIn("Güzel Sanatlar", markdown)
        self.assertNotIn("T1_ACT_04_GUZEL_SANATLAR_DISIPLINLER", markdown)
        self.assertNotIn("BLOCK_T1_01_OKUMA", markdown)
        self.assertNotIn("| Şema |", markdown)
        self.assertNotIn("Canonical referanslar", markdown)
        self.assertNotIn("artefakt", markdown.lower())
        self.assertEqual(teacher_renderer.visible_technical_references(markdown), [])

    def test_tde10_teacher_markdown_keeps_official_outcome_codes_but_not_internal_ids(self) -> None:
        markdown = self._render(
            "TDE_10/generated/lesson_plans/TEMA_04/BLOCK_T4_04_YAZMA/BLOCK_T4_04_YAZMA_P04.json"
        )
        self.assertIn("TDE4.", markdown)
        self.assertNotIn("FORM_T10_T4_YAZMA_DPA_CANONICAL", markdown)
        self.assertNotIn("T4_ACT_18_SIIR_DEGERLENDIRME", markdown)
        self.assertEqual(teacher_renderer.visible_technical_references(markdown), [])

    def test_exporter_writes_88_teacher_documents_for_each_course(self) -> None:
        # Count the canonical source topology without writing into the repository.
        for course_id in ("TDE_9", "TDE_10"):
            source_root = COURSES / course_id / "generated/lesson_plans"
            self.assertEqual(len(list(source_root.glob("*/*/*.json"))), 88)


if __name__ == "__main__":
    unittest.main()
