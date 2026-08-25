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

    def test_real_courses_pass(self):
        expected_counts = {"TDE_9": 20, "TDE_10": 8}
        for course, expected_count in expected_counts.items():
            with self.subTest(course=course):
                result = validator.validate_course(ROOT / "courses" / course)
                self.assertEqual(result["status"], "PASS")
                self.assertEqual(result["options"], expected_count)
                self.assertEqual(result["placements"], expected_count)
                self.assertEqual(result["core_instruction_hours"], 172)
                self.assertEqual(result["school_based_planning_hours"], 8)
                self.assertEqual(result["official_total_hours"], 180)

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


if __name__ == "__main__":
    unittest.main()
