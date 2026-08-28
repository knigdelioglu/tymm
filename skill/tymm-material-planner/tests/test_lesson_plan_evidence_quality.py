#!/usr/bin/env python3
"""Regression tests for concrete prior assessment-evidence references."""
import json
import tempfile
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lesson_plan_evidence_quality as evidence_quality

ROOT = Path(__file__).parents[3] / "courses" / "TDE_9"


class LessonPlanEvidenceQualityTests(unittest.TestCase):
    def read(self, relative: str):
        path = ROOT / relative
        return path, json.loads(path.read_text(encoding="utf-8"))

    def test_package_range_materials_expand_to_specific_evidence(self):
        path, plan = self.read(
            "generated/lesson_plans/TEMA_01/BLOCK_T1_01_OKUMA/"
            "BLOCK_T1_01_OKUMA_P06.json"
        )
        projected = evidence_quality.project_specific_assessment_evidence(
            plan,
            plan_path=path,
        )
        lesson = projected["lessons"][1]
        materials = "\n".join(lesson["materials"])
        opening = lesson["opening"]

        self.assertNotIn("P01-P06", materials)
        self.assertNotIn("çalışma ürünleri", materials.casefold())
        self.assertIn("anlama/çözümleme cevapları ve zihin haritası", materials)
        self.assertIn("ses bilgisi uygulama tablosu", materials)
        self.assertIn("Kontrol Noktası", materials)
        self.assertNotIn("P01-P06", opening)
        self.assertIn("somut ölçme kanıtlarından", opening)
        # The second lesson must not treat its own not-yet-produced comparison
        # table as prior evidence in the opening.
        self.assertNotIn("üç ölçütlü karşılaştırma tablosu", opening)

    def test_generic_previous_products_are_expanded_from_prior_assessments(self):
        path, plan = self.read(
            "generated/lesson_plans/TEMA_02/BLOCK_T2_01_OKUMA/"
            "BLOCK_T2_01_OKUMA_P08.json"
        )
        projected = evidence_quality.project_specific_assessment_evidence(
            plan,
            plan_path=path,
        )
        lesson = projected["lessons"][0]
        text = "\n".join(
            [lesson["objective"], lesson["opening"], *lesson["teacher_actions"], *lesson["materials"]]
        )
        self.assertNotIn("çalışma ürünleri", text.casefold())
        self.assertNotIn("önceki ürün", text.casefold())
        self.assertIn("somut ölçme kanıt", text)
        self.assertTrue(
            any(
                marker in text
                for marker in (
                    "ilk anlamlandırma",
                    "zaman/mekân",
                    "karşılaştırma",
                    "Kontrol Noktası",
                )
            ),
            text,
        )

    def test_singular_previous_product_is_also_resolved(self):
        path, plan = self.read(
            "generated/lesson_plans/TEMA_01/BLOCK_T1_01_OKUMA/"
            "BLOCK_T1_01_OKUMA_P04.json"
        )
        projected = evidence_quality.project_specific_assessment_evidence(
            plan,
            plan_path=path,
        )
        lesson = projected["lessons"][0]
        text = "\n".join(
            [
                lesson["objective"],
                *lesson["teacher_actions"],
                *lesson["student_actions"],
                lesson["assessment"],
            ]
        )
        self.assertNotIn("önceki ürün", text.casefold())
        self.assertNotIn("çalışma ürün", text.casefold())
        self.assertIn("somut ölçme kanıt", text)

    def test_generator_quality_gate_detects_vague_prior_products(self):
        plan = {
            "plan_summary": "Önceki dersin somut kanıtı kullanılır.",
            "lessons": [
                {
                    "title": "Tahlil",
                    "materials": ["P01-P06 öğrenci çalışma ürünleri"],
                    "teacher_actions": ["Önceki çalışma ürünlerinden kanıt seçtir."],
                    "assessment": "Önceki ürün ile karşılaştır.",
                }
            ],
        }
        errors = evidence_quality.vague_evidence_errors(plan)
        self.assertGreaterEqual(len(errors), 3)
        self.assertTrue(all(error.startswith("VAGUE_PRIOR_EVIDENCE:") for error in errors))

    def test_bare_work_product_phrase_is_rejected_for_new_teacher_prose(self):
        plan = {
            "lessons": [
                {
                    "materials": ["Çalışma ürünleri"],
                }
            ]
        }
        errors = evidence_quality.vague_evidence_errors(plan)
        self.assertEqual(len(errors), 1)
        self.assertIn("VAGUE_PRIOR_EVIDENCE", errors[0])

    def test_unresolvable_prior_product_fails_closed(self):
        plan = {
            "plan_summary": "Önceki çalışma ürünlerinden bir kanıt seç.",
            "lessons": [
                {
                    "lesson_no": 1,
                    "assessment": "Bu dersin kanıtı daha sonra oluşur.",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "BLOCK_TEST_P01.json"
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(
                evidence_quality.EvidenceResolutionError,
                "SPECIFIC_ASSESSMENT_EVIDENCE_NOT_FOUND",
            ):
                evidence_quality.project_specific_assessment_evidence(
                    plan,
                    plan_path=path,
                )

    def test_named_evidence_is_not_rejected(self):
        plan = {
            "lessons": [
                {
                    "materials": [
                        "Ders kitabı s. 37 Kontrol Noktası ve düzeltme kaydı",
                        "Tamamlanmış ses bilgisi uygulama tablosu",
                    ]
                }
            ]
        }
        self.assertEqual(evidence_quality.vague_evidence_errors(plan), [])


if __name__ == "__main__":
    unittest.main()
