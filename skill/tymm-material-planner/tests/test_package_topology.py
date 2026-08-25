from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "skill" / "tymm-material-planner" / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("topology_builder_test", SCRIPTS / "build_package_topology_manifest.py")
validator = load_module("topology_validator_test", SCRIPTS / "validate_package_topology.py")


class PackageTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tde9 = builder.build_manifest(REPO_ROOT / "courses" / "TDE_9")
        cls.tde10 = builder.build_manifest(REPO_ROOT / "courses" / "TDE_10")

    def test_exact_course_totals_and_ranges(self) -> None:
        for manifest in (self.tde9, self.tde10):
            self.assertEqual(manifest["summary"]["themes"], 4)
            self.assertEqual(manifest["summary"]["blocks"], 16)
            self.assertEqual(manifest["summary"]["packages"], 88)
            self.assertEqual(manifest["summary"]["core_instruction_hours"], 172)
            self.assertEqual(manifest["summary"]["gaps"], 0)
            self.assertEqual(manifest["summary"]["overlaps"], 0)
            self.assertEqual(manifest["packages"][0]["course_hour_range"], {"start": 1, "end": 2})
            self.assertEqual(manifest["packages"][-1]["course_hour_range"]["end"], 172)
            self.assertEqual([theme["course_hour_range"] for theme in manifest["themes"]], [
                {"start": 1, "end": 43},
                {"start": 44, "end": 86},
                {"start": 87, "end": 129},
                {"start": 130, "end": 172},
            ])

    def test_odd_reading_blocks_end_with_one_hour_package(self) -> None:
        for manifest in (self.tde9, self.tde10):
            reading_blocks = [
                block
                for theme in manifest["themes"]
                for block in theme["blocks"]
                if block["planned_hours"] == 15
            ]
            self.assertEqual(len(reading_blocks), 4)
            for block in reading_blocks:
                last_id = block["package_ids"][-1]
                package = next(item for item in manifest["packages"] if item["package_id"] == last_id)
                self.assertEqual(package["lesson_hours"], 1)
                self.assertEqual(package["block_hour_range"], {"start": 15, "end": 15})

    def test_missing_package_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.tde9)
        mutated["packages"].pop(10)
        errors = validator.validate_manifest_payload(self.tde9, mutated)
        self.assertTrue(any(item.startswith("TOPOLOGY_PACKAGE_SET_MISMATCH") for item in errors), errors)

    def test_course_hour_overlap_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.tde9)
        mutated["packages"][1]["course_hour_range"]["start"] = 2
        errors = validator.validate_manifest_payload(self.tde9, mutated)
        self.assertTrue(
            any("COURSE_RANGE_START_MISMATCH" in item for item in errors),
            errors,
        )

    def test_package_reordering_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.tde10)
        mutated["packages"][0], mutated["packages"][1] = mutated["packages"][1], mutated["packages"][0]
        errors = validator.validate_manifest_payload(self.tde10, mutated)
        self.assertIn("TOPOLOGY_PACKAGE_ORDER_MISMATCH", errors)

    def test_wrong_path_and_hour_are_rejected(self) -> None:
        mutated = copy.deepcopy(self.tde10)
        mutated["packages"][0]["path"] = "generated/lesson_plans/WRONG.json"
        mutated["packages"][0]["lesson_hours"] = 1
        errors = validator.validate_manifest_payload(self.tde10, mutated)
        self.assertTrue(any(item.startswith(mutated["packages"][0]["package_id"] + ":PATH_MISMATCH") for item in errors), errors)
        self.assertTrue(any(item.startswith(mutated["packages"][0]["package_id"] + ":LESSON_HOURS_MISMATCH") for item in errors), errors)


if __name__ == "__main__":
    unittest.main()
