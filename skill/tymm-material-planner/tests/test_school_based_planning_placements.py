#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[3]
SCRIPTS = ROOT / "skill/tymm-material-planner/scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_school_based_planning_placements as validator


class SchoolBasedPlanningPlacementTests(unittest.TestCase):
    def _payloads(self, course: str):
        root = ROOT / "courses" / course
        options = json.loads((root / "production/school_based_planning_options.json").read_text(encoding="utf-8"))
        placements = json.loads((root / "production/school_based_planning_placements.json").read_text(encoding="utf-8"))
        plan = json.loads((root / "planning/lesson_plan_production_plan.json").read_text(encoding="utf-8"))
        return options, placements, plan

    def _teaching_blocks(self, course: str):
        root = ROOT / "courses" / course
        return json.loads((root / "production/teaching_blocks.json").read_text(encoding="utf-8"))

    def _first_tde10_option(self, options):
        return options["themes"][0]["options"][0]

    def _first_tde11_option(self, options):
        return options["themes"][0]["options"][0]

    def test_real_courses_pass(self):
        expected_counts = {"TDE_9": 20, "TDE_10": 8, "TDE_11": 12}
        for course, expected_count in expected_counts.items():
            with self.subTest(course=course):
                result = validator.validate_course(ROOT / "courses" / course)
                self.assertEqual(result["status"], "PASS")
                self.assertEqual(result["options"], expected_count)
                self.assertEqual(result["placements"], expected_count)
                self.assertEqual(result["core_instruction_hours"], 172)
                self.assertEqual(result["school_based_planning_hours"], 8)
                self.assertEqual(result["official_total_hours"], 180)
                if course == "TDE_10":
                    self.assertEqual(result["career_guidance_options"], 8)
                    self.assertEqual(result["career_guidance_hours"], 8)
                if course == "TDE_11":
                    self.assertEqual(result["teacher_adaptable_options"], 12)
                    self.assertEqual(result["candidate_option_hours"], 16)
                    self.assertEqual(result["selectable_school_based_hours"], 8)
                    self.assertEqual(result["selection_mode"], "ONE_2H_OR_TWO_1H")

    def test_unknown_anchor_fails_closed(self):
        options, placements, plan = self._payloads("TDE_10")
        mutated = copy.deepcopy(placements)
        mutated["placements"][0]["recommended_insertion_point"]["anchor_package_id"] = "BLOCK_T1_01_OKUMA_P99"
        with self.assertRaisesRegex(validator.PlacementValidationError, "PLACEMENT_ANCHOR_UNKNOWN"):
            validator.validate_payloads(options, mutated, plan)

    def test_missing_option_placement_fails_closed(self):
        options, placements, plan = self._payloads("TDE_10")
        mutated = copy.deepcopy(placements)
        mutated["placements"].pop()
        with self.assertRaisesRegex(validator.PlacementValidationError, "PLACEMENT_MISSING_FOR_OPTION"):
            validator.validate_payloads(options, mutated, plan)

    def test_school_based_hours_cannot_enter_default_queue(self):
        options, placements, plan = self._payloads("TDE_10")
        mutated = copy.deepcopy(plan)
        mutated["progress"]["queued_instruction_hours"] = 180
        with self.assertRaisesRegex(validator.PlacementValidationError, "SBP_MUST_NOT_ENTER_DEFAULT_QUEUE"):
            validator.validate_payloads(options, placements, mutated)

    def test_policy_cannot_mutate_core_hours(self):
        options, placements, plan = self._payloads("TDE_9")
        mutated = copy.deepcopy(placements)
        mutated["policy"]["core_instruction_hours_per_theme"] = 45
        with self.assertRaisesRegex(validator.PlacementValidationError, "PLACEMENT_POLICY_MISMATCH"):
            validator.validate_payloads(options, mutated, plan)

    def test_tde10_option_cannot_fall_back_to_generic_school_based_activity(self):
        options, placements, plan = self._payloads("TDE_10")
        mutated = copy.deepcopy(options)
        self._first_tde10_option(mutated)["category"] = "SCHOOL_BASED_PLANNING"
        with self.assertRaisesRegex(validator.PlacementValidationError, "TDE10_OPTION_NOT_CAREER_GUIDANCE"):
            validator.validate_payloads(mutated, placements, plan)

    def test_tde10_career_alignment_is_required(self):
        options, placements, plan = self._payloads("TDE_10")
        mutated = copy.deepcopy(options)
        self._first_tde10_option(mutated).pop("career_guidance_alignment")
        with self.assertRaisesRegex(validator.PlacementValidationError, "TDE10_CAREER_ALIGNMENT_MISSING"):
            validator.validate_payloads(mutated, placements, plan)

    def test_tde10_career_evidence_is_required(self):
        options, placements, plan = self._payloads("TDE_10")
        mutated = copy.deepcopy(options)
        self._first_tde10_option(mutated)["career_guidance_alignment"]["student_career_evidence"] = ""
        with self.assertRaisesRegex(validator.PlacementValidationError, "TDE10_CAREER_EVIDENCE_MISSING"):
            validator.validate_payloads(mutated, placements, plan)

    def test_tde10_option_must_remain_grounded_in_tde_outcomes(self):
        options, placements, plan = self._payloads("TDE_10")
        mutated = copy.deepcopy(options)
        self._first_tde10_option(mutated)["linked_outcomes"] = []
        with self.assertRaisesRegex(validator.PlacementValidationError, "TDE10_LINKED_OUTCOMES_MISSING"):
            validator.validate_payloads(mutated, placements, plan)

    def test_tde10_all_eight_hours_are_career_guidance_hours(self):
        options, placements, plan = self._payloads("TDE_10")
        mutated = copy.deepcopy(options)
        mutated["themes"][0]["options"][0]["duration_hours"] = 2
        with self.assertRaisesRegex(
            validator.PlacementValidationError,
            "TDE10_CAREER_OPTION_HOURS_MUST_EQUAL_THEME_ALLOCATION",
        ):
            validator.validate_payloads(mutated, placements, plan)

    def test_tde10_placement_policy_cannot_disable_career_guidance(self):
        options, placements, plan = self._payloads("TDE_10")
        mutated = copy.deepcopy(placements)
        mutated["policy"]["career_guidance_required"] = False
        with self.assertRaisesRegex(validator.PlacementValidationError, "PLACEMENT_POLICY_MISMATCH"):
            validator.validate_payloads(options, mutated, plan)

    def test_tde11_options_must_not_auto_generate(self):
        options, placements, plan = self._payloads("TDE_11")
        blocks = self._teaching_blocks("TDE_11")
        mutated = copy.deepcopy(options)
        self._first_tde11_option(mutated)["generation_status"] = "GENERATED"
        with self.assertRaisesRegex(validator.PlacementValidationError, "TDE11_OPTION_MUST_NOT_AUTO_GENERATE"):
            validator.validate_payloads(mutated, placements, plan, blocks)

    def test_tde11_options_must_start_unselected(self):
        options, placements, plan = self._payloads("TDE_11")
        blocks = self._teaching_blocks("TDE_11")
        mutated = copy.deepcopy(options)
        self._first_tde11_option(mutated)["selection_status"] = "SELECTED"
        with self.assertRaisesRegex(validator.PlacementValidationError, "TDE11_OPTION_MUST_START_UNSELECTED"):
            validator.validate_payloads(mutated, placements, plan, blocks)

    def test_tde11_source_reference_must_exist(self):
        options, placements, plan = self._payloads("TDE_11")
        blocks = self._teaching_blocks("TDE_11")
        mutated = copy.deepcopy(options)
        self._first_tde11_option(mutated)["derived_from"]["textbook_activity_ids"][0] = "T1_ACT_DOES_NOT_EXIST"
        with self.assertRaisesRegex(validator.PlacementValidationError, "TDE11_DERIVED_ACTIVITY_UNKNOWN"):
            validator.validate_payloads(mutated, placements, plan, blocks)

    def test_tde11_derived_block_cannot_cross_theme(self):
        options, placements, plan = self._payloads("TDE_11")
        blocks = self._teaching_blocks("TDE_11")
        mutated = copy.deepcopy(options)
        self._first_tde11_option(mutated)["derived_from"]["teaching_block_ids"][0] = "BLOCK_T2_01_OKUMA"
        with self.assertRaisesRegex(validator.PlacementValidationError, "TDE11_DERIVED_BLOCK_THEME_MISMATCH"):
            validator.validate_payloads(mutated, placements, plan, blocks)

    def test_tde11_each_theme_supports_one_2h_or_two_1h_routes(self):
        options, placements, plan = self._payloads("TDE_11")
        blocks = self._teaching_blocks("TDE_11")
        mutated = copy.deepcopy(options)
        mutated["themes"][0]["options"][2]["duration_hours"] = 1
        with self.assertRaisesRegex(
            validator.PlacementValidationError,
            "TDE11_SELECTION_MODES_MUST_BE_ONE_2H_OR_TWO_1H",
        ):
            validator.validate_payloads(mutated, placements, plan, blocks)

    def test_tde11_school_based_option_is_not_a_curriculum_gap(self):
        options, placements, plan = self._payloads("TDE_11")
        blocks = self._teaching_blocks("TDE_11")
        mutated = copy.deepcopy(options)
        self._first_tde11_option(mutated)["is_curriculum_gap"] = True
        with self.assertRaisesRegex(validator.PlacementValidationError, "TDE11_OPTION_MUST_NOT_BE_CURRICULUM_GAP"):
            validator.validate_payloads(mutated, placements, plan, blocks)


if __name__ == "__main__":
    unittest.main()
