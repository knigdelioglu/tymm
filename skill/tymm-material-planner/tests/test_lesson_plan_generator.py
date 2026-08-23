#!/usr/bin/env python3
"""Regression tests for TYMM AI Lesson Generator V1."""
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_runtime_course_package as compiler
import lesson_plan_context
import lesson_plan_generator as generator

ROOT = Path(__file__).parents[3] / "courses" / "TDE_9"


class LessonPlanGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "TDE_9"
        shutil.copytree(ROOT, self.tmp, ignore=shutil.ignore_patterns("runtime", "*.sqlite"))
        self.assertEqual(compiler.build(self.tmp)["status"], "PASS")
        self.context = lesson_plan_context.assemble(self.tmp, "BLOCK_T1_01_OKUMA", 2)

    def tearDown(self):
        shutil.rmtree(self.tmp.parent, ignore_errors=True)

    def valid_plan(self, *, remaining=13):
        activities = self.context["allowed_references"]["activity_ids"][:2]
        forms = self.context["allowed_references"]["form_ids"][:1]
        return {
            "schema_version": "1.0.0",
            "course_id": "TDE_9",
            "theme_id": "TEMA_01",
            "block_id": "BLOCK_T1_01_OKUMA",
            "lesson_hours": 2,
            "plan_title": "Şiir ve deneme okuma çalışması",
            "plan_summary": "İki ders saatinde kaynak metin ve kitap etkinliklerine dayalı okuma/tahlil akışı.",
            "outcome_codes": ["TDE2.1", "TDE2.2"],
            "used_activity_ids": activities,
            "used_form_ids": forms,
            "lessons": [
                {
                    "lesson_no": 1,
                    "duration_lesson_hours": 1,
                    "title": "Hazırlık ve ilk okuma",
                    "objective": "Metne yönelik okuma amacı oluşturmak ve ilk tahlil verilerini toplamak.",
                    "outcome_codes": ["TDE2.1"],
                    "opening": "Ön bilgileri kısa sorularla harekete geçir.",
                    "teacher_actions": ["Kitaptaki ilgili etkinliğe yönlendir."],
                    "student_actions": ["Metni amaçlı biçimde oku ve not al."],
                    "activity_ids": activities[:1],
                    "form_ids": [],
                    "assessment": "Öğrenci notlarını çıkış sorusuyla kontrol et.",
                    "closure": "Bir sonraki tahlil adımını özetle.",
                    "materials": ["Ders kitabı"],
                },
                {
                    "lesson_no": 2,
                    "duration_lesson_hours": 1,
                    "title": "Tahlil ve değerlendirme",
                    "objective": "Metindeki anlam ilişkilerini gerekçeli biçimde değerlendirmek.",
                    "outcome_codes": ["TDE2.1", "TDE2.2"],
                    "opening": "İlk dersteki öğrenci notlarından iki bulguyu hatırlat.",
                    "teacher_actions": ["İkinci kitap etkinliğini yapılandırılmış sorularla yürüt."],
                    "student_actions": ["Metne dayalı çıkarımlarını gerekçelendir."],
                    "activity_ids": activities[1:2],
                    "form_ids": forms,
                    "assessment": "Varsa canonical değerlendirme formunu kullan; yoksa sözlü kontrol sorusu uygula.",
                    "closure": "Öğrenilenleri iki maddede özetlet.",
                    "materials": ["Ders kitabı"],
                },
            ],
            "teacher_notes": "Bu iki saat, 15 saatlik bloğun pedagojik bir kesitidir; resmî alt-saat sırası değildir.",
            "continuation_summary": {
                "planned_now_hours": 2,
                "remaining_block_hours": remaining,
                "covered_outcome_codes": ["TDE2.1", "TDE2.2"],
                "used_activity_ids": activities,
                "next_step_hint": "Sonraki planda kullanılmamış kitap etkinliklerinden devam et.",
            },
        }

    def test_request_locks_identity_and_exposes_schema(self):
        request = generator.build_model_request(
            self.context,
            {"class_profile": "orta", "emphasis": "etkinlik ağırlıklı"},
        )
        self.assertEqual(request["mode"], "GENERATE")
        self.assertEqual(request["immutable_identity"]["lesson_hours"], 2)
        self.assertEqual(request["response_schema"]["title"], "TYMM AI Lesson Plan V1")
        self.assertFalse(request["canonical_context"]["planning_request"]["calendar_binding_used"])

    def test_preferences_cannot_override_canonical_fields(self):
        with self.assertRaises(generator.LessonPlanGenerationError):
            generator.build_model_request(self.context, {"lesson_hours": 99})

    def test_first_pass_generation_succeeds(self):
        calls = []
        def model(request):
            calls.append(request)
            return self.valid_plan()
        result = generator.generate(self.context, model)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(result["repair_count"], 0)
        self.assertEqual(calls[0]["mode"], "GENERATE")

    def test_invalid_first_candidate_is_repaired(self):
        calls = []
        def model(request):
            calls.append(request)
            if request["mode"] == "GENERATE":
                bad = self.valid_plan()
                bad["used_activity_ids"] = ["ACT_FAKE"]
                bad["lessons"][0]["activity_ids"] = ["ACT_FAKE"]
                bad["lessons"][1]["activity_ids"] = []
                return bad
            self.assertTrue(request["repair"]["validation_errors"])
            self.assertIn("previous_candidate", request["repair"])
            return self.valid_plan()
        result = generator.generate(self.context, model, max_repairs=2)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(result["repair_count"], 1)
        self.assertEqual([x["mode"] for x in calls], ["GENERATE", "REPAIR"])
        self.assertTrue(any("ACT_FAKE" in err for err in result["trace"][0]["errors"]))

    def test_generator_blocks_after_repair_budget(self):
        def model(_request):
            bad = self.valid_plan()
            bad["course_id"] = "TDE_FAKE"
            return bad
        result = generator.generate(self.context, model, max_repairs=1)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(result["block_reason"], "LESSON_PLAN_VALIDATION_FAILED_AFTER_REPAIRS")
        self.assertIsNone(result["plan"])

    def test_continuation_state_changes_remaining_hours(self):
        continuation = {
            "completed_hours_before_this_plan": 4,
            "previously_used_activity_ids": self.context["allowed_references"]["activity_ids"][:1],
            "previously_covered_outcome_codes": ["TDE2.1"],
            "previous_plan_summary": "İlk dört saatte temel okuma ve ilk tahlil yapıldı.",
        }
        plan = self.valid_plan(remaining=9)
        result = generator.generate(self.context, lambda _request: plan, continuation_state=continuation)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["plan"]["continuation_summary"]["remaining_block_hours"], 9)

    def test_continuation_cannot_exceed_block(self):
        with self.assertRaises(generator.LessonPlanGenerationError):
            generator.build_model_request(
                self.context,
                continuation_state={
                    "completed_hours_before_this_plan": 14,
                    "previously_used_activity_ids": [],
                    "previously_covered_outcome_codes": [],
                    "previous_plan_summary": "",
                },
            )

    def test_fenced_json_response_is_parsed(self):
        import json
        text = "```json\n" + json.dumps(self.valid_plan(), ensure_ascii=False) + "\n```"
        result = generator.generate(self.context, lambda _request: text)
        self.assertEqual(result["status"], "PASS", result)


if __name__ == "__main__":
    unittest.main()
