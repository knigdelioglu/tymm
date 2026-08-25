#!/usr/bin/env python3
"""Regression tests for P5 theme-closure time-budget contracts."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import apply_closure_time_budgets
import validate_closure_time_budgets

ROOT = Path(__file__).parents[3] / "courses" / "TDE_9"


class ClosureTimeBudgetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "TDE_9"
        shutil.copytree(ROOT, self.tmp, ignore=shutil.ignore_patterns("runtime", "*.sqlite"))
        result = apply_closure_time_budgets.apply(self.tmp, write=True)
        self.assertEqual(result["status"], "PASS")
        self.contract_path = self.tmp / "production" / "closure_time_budgets.json"

    def tearDown(self):
        shutil.rmtree(self.tmp.parent, ignore_errors=True)

    def _contract(self):
        return json.loads(self.contract_path.read_text(encoding="utf-8"))

    def _write_contract(self, payload):
        self.contract_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _mixed_budget(self, contract):
        for package in contract["packages"]:
            for budget in package["lesson_budgets"]:
                if set(budget["signals"]) == {"THEME_ASSESSMENT", "REFLECTION"}:
                    return package, budget
        self.fail("mixed closure budget not found")

    def test_real_tde9_closures_pass(self):
        result = validate_closure_time_budgets.validate_course(self.tmp)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["theme_closure_packages"], 4)
        self.assertEqual(result["budgeted_lessons"], 5)

    def test_mixed_closure_cannot_overbook_period(self):
        contract = self._contract()
        _, budget = self._mixed_budget(contract)
        assessment = next(
            item for item in budget["required_segments"] if item["kind"] == "THEME_ASSESSMENT"
        )
        assessment["minutes"] = 30
        self._write_contract(contract)
        result = validate_closure_time_budgets.validate_course(self.tmp)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("REQUIRED_TOTAL_MISMATCH" in item for item in result["errors"]))
        self.assertTrue(any("PERIOD_BUDGET_MISMATCH" in item for item in result["errors"]))

    def test_optional_extension_cannot_be_required_for_core(self):
        contract = self._contract()
        _, budget = self._mixed_budget(contract)
        budget["optional_extensions"][0]["required_for_core_completion"] = True
        self._write_contract(contract)
        result = validate_closure_time_budgets.validate_course(self.tmp)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(
            any("OPTIONAL_EXTENSION_MUST_NOT_BE_REQUIRED" in item for item in result["errors"])
        )

    def test_contract_must_cover_every_theme_closure_package(self):
        contract = self._contract()
        contract["packages"].pop()
        self._write_contract(contract)
        result = validate_closure_time_budgets.validate_course(self.tmp)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("CLOSURE_PACKAGE_SET_MISMATCH" in item for item in result["errors"]))

    def test_plan_must_surface_time_budget_to_teacher(self):
        contract = self._contract()
        package, budget = self._mixed_budget(contract)
        plan_path = self.tmp / package["path"]
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        lesson = next(item for item in plan["lessons"] if item["lesson_no"] == budget["lesson_no"])
        lesson["teacher_actions"] = [
            item for item in lesson["teacher_actions"] if not item.startswith("Süre bütçesi:")
        ]
        plan_path.write_text(
            json.dumps(plan, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        result = validate_closure_time_budgets.validate_course(self.tmp)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("PLAN_TIME_BUDGET_MARKER_MISSING" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
