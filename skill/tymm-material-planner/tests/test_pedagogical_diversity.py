#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[3]
SCRIPTS = ROOT / "skill/tymm-material-planner/scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_pedagogical_diversity as validator


class PedagogicalDiversityTests(unittest.TestCase):
    def test_identical_lessons_are_insufficient_delta(self):
        lesson = {
            "title": "Anlam Oluşturabilme: kanıt üretme ve geliştirme",
            "opening": "Aynı görev açıklanır ve beklenen kanıt belirtilir.",
            "teacher_actions": ["Görevi uygulat.", "Kanıtı topla."],
            "student_actions": ["Görevi yapar.", "Kanıtı kontrol eder."],
            "assessment": "Aynı kanıt üzerinden geri bildirim verilir.",
            "closure": "Bir güçlü yön ve bir gelişim adımı yazılır.",
        }
        metrics = validator.analyze_pair(lesson, dict(lesson), validator.DEFAULT_THRESHOLDS)
        self.assertTrue(metrics["insufficient_delta"])
        self.assertEqual(metrics["duplicate_dimensions"], 5)

    def test_meaningful_second_lesson_delta_is_not_structural_duplicate(self):
        first = {
            "title": "Mektupta konu ve iletiyi belirleme",
            "opening": "Metnin bağlamı hatırlatılır ve ilk okuma amacı belirlenir.",
            "teacher_actions": ["Öğrenciden konu ve ileti için metin kanıtı seçmesini iste."],
            "student_actions": ["Metinden konu ve iletiyi destekleyen iki kanıt seçer."],
            "assessment": "Seçilen iki kanıtın konu ve iletiyle ilişkisi kontrol edilir.",
            "closure": "En güçlü kanıtını tek cümleyle açıklar.",
        }
        second = {
            "title": "Mektuptan dilekçeye amaç ve anlatım karşılaştırması",
            "opening": "İlk dersteki mektup kanıtlarıyla dilekçenin iletişim amacı karşılaştırmaya açılır.",
            "teacher_actions": ["İki metni ortak amaç, muhatap ve anlatım ölçütleriyle karşılaştırma tablosuna yönlendir."],
            "student_actions": ["Mektup ve dilekçeyi üç ortak ölçütle karşılaştırır ve bir farkı metin kanıtıyla savunur."],
            "assessment": "Karşılaştırma tablosundaki ölçüt tutarlılığı ve kanıtla savunulan fark değerlendirilir.",
            "closure": "Metin türü değiştiğinde anlatımın neden değiştiğini gerekçeli bir sonuç cümlesiyle yazar.",
        }
        metrics = validator.analyze_pair(first, second, validator.DEFAULT_THRESHOLDS)
        self.assertFalse(metrics["insufficient_delta"])
        self.assertLess(metrics["duplicate_dimensions"], 4)

    def test_catalog_requires_unique_routes(self):
        route = {
            "route_id": "R1",
            "label": "Rota",
            "lesson_1_pattern": "İlk görev",
            "lesson_2_delta": "İkinci görev farkı",
            "student_evidence_pattern": "Kanıt",
        }
        catalog = {"routes": [dict(route) for _ in range(8)]}
        errors = validator.validate_catalog(catalog)
        self.assertIn("DUPLICATE_ROUTE_ID:R1", errors)

    def test_invalid_overlay_fails_in_strict_mode(self):
        overlay = {
            "course_id": "TDE_11",
            "packages": [
                {
                    "package_id": "P01",
                    "route_id": "UNKNOWN",
                    "lesson_progression": [],
                }
            ],
        }
        failures, warnings, designed = validator.validate_overlay(
            overlay,
            known_packages={"P01"},
            valid_routes={"VALID"},
            strict=True,
            expected_lesson_nos={"P01": {1, 2}},
        )
        self.assertTrue(failures)
        self.assertFalse(warnings)
        self.assertEqual(designed, {"P01"})
        self.assertIn("ROUTE_ID_UNKNOWN", failures[0]["details"])
        self.assertIn("LESSON_PROGRESSION_MISSING", failures[0]["details"])
        self.assertTrue(any(detail.startswith("PROGRESSION_LESSON_SET_MISMATCH") for detail in failures[0]["details"]))

    def test_cross_overlay_duplicate_is_rejected(self):
        progression = [
            {
                "lesson_no": 1,
                "role": "INITIAL_CONSTRUCTION",
                "cognitive_operation": "İlk işlem",
                "student_evidence": "İlk kanıt",
                "delta_from_previous": "İlk adım",
            }
        ]
        shared_seen: set[str] = set()
        first = {"packages": [{"package_id": "P01", "route_id": "VALID", "lesson_progression": progression}]}
        second = {"packages": [{"package_id": "P01", "route_id": "VALID", "lesson_progression": progression}]}
        failures1, _, _ = validator.validate_overlay(
            first,
            known_packages={"P01"},
            valid_routes={"VALID"},
            strict=True,
            expected_lesson_nos={"P01": {1}},
            global_seen=shared_seen,
            source_path="first.json",
        )
        failures2, _, _ = validator.validate_overlay(
            second,
            known_packages={"P01"},
            valid_routes={"VALID"},
            strict=True,
            expected_lesson_nos={"P01": {1}},
            global_seen=shared_seen,
            source_path="second.json",
        )
        self.assertFalse(failures1)
        self.assertTrue(failures2)
        self.assertIn("PACKAGE_ID_DUPLICATE_ACROSS_OVERLAYS", failures2[0]["details"])

    def test_real_tde11_strict_final_state_is_complete_and_clean(self):
        result = validator.validate_course(ROOT / "courses/TDE_11", strict=True)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["packages"], 88)
        self.assertEqual(result["design_overlays"], 4)
        self.assertEqual(result["designed_packages"], 88)
        self.assertTrue(result["design_coverage_complete"])
        self.assertEqual(result["adjacent_lesson_pairs"], 84)
        self.assertEqual(result["insufficient_delta_pairs"], 0)
        self.assertEqual(result["lesson_titles"], 172)
        self.assertEqual(result["generic_title_count"], 0)
        self.assertEqual(result["generic_title_share"], 0.0)
        self.assertFalse(result["failures"])


if __name__ == "__main__":
    unittest.main()
