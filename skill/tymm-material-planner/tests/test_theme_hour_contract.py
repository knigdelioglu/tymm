#!/usr/bin/env python3
"""Regression contract for the 45-hour TYMM theme model.

Each TDE theme is represented as 43 core instructional hours plus 2 hours
of school-based planning. Calendar/weekly placement residuals from an annual
plan must never be promoted into canonical block-hour totals.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[3]
COURSES = ("TDE_9", "TDE_10")


class ThemeHourContractTests(unittest.TestCase):
    def _read(self, course: str, relative: str) -> dict:
        return json.loads((ROOT / "courses" / course / relative).read_text(encoding="utf-8"))

    def test_all_themes_are_43_core_plus_2_school_based(self):
        for course in COURSES:
            with self.subTest(course=course):
                distribution = self._read(course, "planning/official_topic_hour_distribution.json")
                semantics = distribution["time_semantics"]
                self.assertEqual(semantics["normative_instruction_hours_per_theme"], 43)
                self.assertEqual(semantics["normative_school_based_planning_hours_per_theme"], 2)
                self.assertEqual(semantics["normative_total_hours_per_theme"], 45)
                self.assertEqual(semantics["normative_annual_instruction_hours"], 172)
                self.assertEqual(semantics["normative_annual_school_based_planning_hours"], 8)
                self.assertEqual(semantics["normative_annual_total_hours"], 180)

                self.assertEqual(len(distribution["themes"]), 4)
                for theme in distribution["themes"]:
                    topic_total = sum(item["source_planning_weight_hours"] for item in theme["topic_allocations"])
                    self.assertEqual(topic_total, 43, (course, theme["theme_id"], topic_total))
                    self.assertEqual(theme["normative_instruction_hours"], 43)
                    self.assertEqual(theme["source_planning_weight_total"], 43)
                    self.assertEqual(theme["school_based_planning_hours"], 2)
                    self.assertEqual(theme["official_total_hours"], 45)

    def test_block_bindings_do_not_use_normalization_to_reach_43(self):
        forbidden_keys = {"normalization_status", "source_planning_weight_hours"}
        for course in COURSES:
            with self.subTest(course=course):
                bindings = self._read(course, "planning/block_hour_bindings.json")
                semantics = bindings["semantics"]
                self.assertEqual(semantics["normative_instruction_hours_per_theme"], 43)
                self.assertEqual(semantics["school_based_planning_hours_per_theme"], 2)
                self.assertEqual(semantics["official_total_hours_per_theme"], 45)

                for theme in bindings["themes"]:
                    self.assertEqual(theme["normative_total_hours"], 43)
                    self.assertEqual(theme["school_based_planning_hours"], 2)
                    self.assertEqual(theme["official_total_hours"], 45)
                    self.assertEqual(sum(item["planned_hours"] for item in theme["bindings"]), 43)
                    self.assertTrue(forbidden_keys.isdisjoint(theme.keys()), (course, theme["theme_id"]))
                    for item in theme["bindings"]:
                        self.assertNotIn("NORMALIZED", item.get("resolution", "").upper())

    def test_calendar_residuals_are_explicitly_excluded_not_normalized(self):
        for course in COURSES:
            with self.subTest(course=course):
                distribution = self._read(course, "planning/official_topic_hour_distribution.json")
                theme4 = next(theme for theme in distribution["themes"] if theme["theme_id"] == "TEMA_04")
                excluded = theme4.get("calendar_residual_source_rows_excluded", [])
                self.assertTrue(excluded, course)
                self.assertEqual(theme4["reconciliation_status"], "EXACT_AFTER_CALENDAR_RESIDUAL_EXCLUSION")

                bindings = self._read(course, "planning/block_hour_bindings.json")
                bound_theme4 = next(theme for theme in bindings["themes"] if theme["theme_id"] == "TEMA_04")
                self.assertEqual(bound_theme4.get("calendar_residual_source_rows_excluded"), excluded)
                self.assertEqual(sum(item["planned_hours"] for item in bound_theme4["bindings"]), 43)


if __name__ == "__main__":
    unittest.main()
