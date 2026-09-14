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
            "packages": [
                {
                    "package_id": "P01",
                    "route_id": "UNKNOWN",
                    "lesson_progression": [],
                }
            ]
        }
        failures, warnings = validator.validate_overlay(
            overlay,
            known_packages={"P01"},
            valid_routes={"VALID"},
            strict=True,
        )
        self.assertTrue(failures)
        self.assertFalse(warnings)
        self.assertIn("ROUTE_ID_UNKNOWN", failures[0]["details"])
        self.assertIn("LESSON_PROGRESSION_MISSING", failures[0]["details"])

    def test_real_tde11_advisory_baseline_is_measurable(self):
        result = validator.validate_course(ROOT / "courses/TDE_11", strict=False)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["packages"], 88)
        self.assertGreater(result["adjacent_lesson_pairs"], 0)
        self.assertGreater(result["insufficient_delta_pairs"], 0)
        self.assertGreater(result["generic_title_count"], 0)
        self.assertTrue(any(item["code"] == "GENERIC_TITLE_OVERUSE" for item in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
