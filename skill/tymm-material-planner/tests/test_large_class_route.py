#!/usr/bin/env python3
"""Regression tests for large-class speaking-performance execution routes."""
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build_runtime_course_package as compiler
import lesson_plan_context
import validate_lesson_plan

ROOT = Path(__file__).parents[3] / "courses" / "TDE_9"


class LargeClassRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "TDE_9"
        shutil.copytree(ROOT, self.tmp, ignore=shutil.ignore_patterns("runtime", "*.sqlite"))
        self.assertEqual(compiler.build(self.tmp)["status"], "PASS")

    def tearDown(self):
        shutil.rmtree(self.tmp.parent, ignore_errors=True)

    def _fixture(self):
        context = lesson_plan_context.assemble(self.tmp, "BLOCK_T2_02_KONUSMA", 2)
        performance_id = next(
            activity_id
            for activity_id in context["allowed_references"]["activity_ids"]
            if "KONUSMA_SIRASI" in activity_id
        )
        outcomes = context["allowed_references"]["outcome_codes"]
        plan = {
            "course_id": "TDE_9",
            "theme_id": "TEMA_02",
            "block_id": "BLOCK_T2_02_KONUSMA",
            "lesson_hours": 2,
            "outcome_codes": outcomes,
            "used_activity_ids": [performance_id],
            "used_form_ids": [],
            "lessons": [
                {
                    "lesson_no": 1,
                    "duration_lesson_hours": 1,
                    "outcome_codes": outcomes,
                    "activity_ids": [performance_id],
                    "form_ids": [],
                },
                {
                    "lesson_no": 2,
                    "duration_lesson_hours": 1,
                    "outcome_codes": outcomes,
                    "activity_ids": [],
                    "form_ids": [],
                },
            ],
            "continuation_summary": {
                "planned_now_hours": 2,
                "covered_outcome_codes": outcomes,
                "used_activity_ids": [performance_id],
            },
        }
        return context, plan

    def test_speaking_performance_requires_large_class_route(self):
        context, plan = self._fixture()
        result = validate_lesson_plan.validate(context, plan)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("LARGE_CLASS_ROUTE_REQUIRED", result["errors"])

    def test_parallel_group_route_is_accepted(self):
        context, plan = self._fixture()
        plan["large_class_route"] = {
            "mode": "PARALLEL_GROUPS",
            "activation_condition": "Tek sıra sunum rotası ders süresine sığmıyorsa kullan.",
            "applies_to_lesson_numbers": [1],
            "parallel_group_count": 5,
            "grouping_strategy": "Sınıfı 4-6 kişilik paralel performans gruplarına ayır.",
            "teacher_rotation_strategy": "Öğretmen gruplar arasında döner ve her öğrenciden en az bir doğrudan kanıt toplar.",
            "peer_observer_strategy": "Her grupta akran gözlemci tek güçlü davranış ve tek geliştirme kanıtı kaydeder.",
            "performance_time_limit_seconds": 120,
            "evidence_equivalence": "Standart rotadaki aynı konuşma ölçütleri ve aynı öğrenci kanıtı korunur.",
            "core_hours_independent_of_school_based_extension": True,
            "optional_school_based_extension": {
                "allowed": True,
                "purpose": "Yalnız hedefli ek prova veya yeniden performans; çekirdek planın tamamlanması buna bağlı değildir.",
            },
        }
        result = validate_lesson_plan.validate(context, plan)
        self.assertEqual(result["status"], "PASS", result)

    def test_route_must_cover_every_performance_lesson(self):
        context, plan = self._fixture()
        performance_id = plan["used_activity_ids"][0]
        plan["lessons"][1]["activity_ids"] = [performance_id]
        plan["large_class_route"] = {
            "mode": "PARALLEL_GROUPS",
            "activation_condition": "Kalabalık sınıf.",
            "applies_to_lesson_numbers": [1],
            "parallel_group_count": 4,
            "grouping_strategy": "Paralel gruplar.",
            "teacher_rotation_strategy": "Öğretmen dönüşümlü gözlem yapar.",
            "peer_observer_strategy": "Akranlar kanıt kaydeder.",
            "performance_time_limit_seconds": 120,
            "evidence_equivalence": "Aynı ölçüt ve kanıt korunur.",
            "core_hours_independent_of_school_based_extension": True,
        }
        result = validate_lesson_plan.validate(context, plan)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("LARGE_CLASS_ROUTE_MISSING_PERFORMANCE_LESSONS:[2]", result["errors"])

    def test_core_route_cannot_depend_on_school_based_extension(self):
        context, plan = self._fixture()
        plan["large_class_route"] = {
            "mode": "PARALLEL_GROUPS",
            "activation_condition": "Kalabalık sınıf.",
            "applies_to_lesson_numbers": [1],
            "parallel_group_count": 4,
            "grouping_strategy": "Paralel gruplar.",
            "teacher_rotation_strategy": "Öğretmen dönüşümlü gözlem yapar.",
            "peer_observer_strategy": "Akranlar kanıt kaydeder.",
            "performance_time_limit_seconds": 120,
            "evidence_equivalence": "Aynı ölçüt ve kanıt korunur.",
            "core_hours_independent_of_school_based_extension": False,
        }
        result = validate_lesson_plan.validate(context, plan)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(
            "LARGE_CLASS_ROUTE_CORE_MUST_NOT_DEPEND_ON_SCHOOL_BASED_EXTENSION",
            result["errors"],
        )


if __name__ == "__main__":
    unittest.main()
