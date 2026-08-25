#!/usr/bin/env python3
"""Regression tests for lesson-plan projection into runtime SQLite."""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import build_runtime_course_package as compiler
import runtime_lesson_plan_payload as lesson_payload

COURSES_ROOT = Path(__file__).parents[3] / "courses"


class RuntimeLessonPlanPayloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def _copy_course(self, course_id: str) -> Path:
        source = COURSES_ROOT / course_id
        target = self.temp_root / course_id
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("runtime", "*.sqlite"),
        )
        return target

    def _build_and_project(self, course_id: str) -> tuple[Path, dict, dict]:
        root = self._copy_course(course_id)
        self.assertEqual(compiler.build(root)["status"], "PASS")
        before = json.loads(
            (root / "runtime/runtime_manifest.json").read_text(encoding="utf-8")
        )
        result = lesson_payload.project_runtime_lesson_plan_payload(root)
        self.assertEqual(result["status"], "PASS")
        after = json.loads(
            (root / "runtime/runtime_manifest.json").read_text(encoding="utf-8")
        )
        return root, before, after

    def test_01_tde9_projects_88_packages_and_172_hours(self) -> None:
        root, before, manifest = self._build_and_project("TDE_9")
        self.assertNotEqual(
            before["canonical_content_fingerprint"],
            manifest["canonical_content_fingerprint"],
        )
        self.assertEqual(manifest["schema_version"], "1.2.0")
        self.assertEqual(manifest["runtime_package_version"], "1.3.0")
        self.assertEqual(manifest["lesson_plan_package_count"], 88)
        self.assertEqual(manifest["lesson_plan_instruction_hours"], 172)
        self.assertTrue(manifest["lesson_plan_capabilities"]["available"])
        self.assertTrue(manifest["lesson_plan_capabilities"]["calendar_neutral"])
        self.assertEqual(manifest["row_counts"]["lesson_plan_packages"], 88)
        self.assertIn(
            "planning/lesson_plan_production_plan.json",
            manifest["canonical_source_hashes"],
        )

        db = sqlite3.connect(root / "runtime/course_runtime.sqlite")
        try:
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM lesson_plan_packages").fetchone()[0],
                88,
            )
            self.assertEqual(
                db.execute("SELECT SUM(lesson_hours) FROM lesson_plan_packages").fetchone()[0],
                172,
            )
            row = db.execute(
                """
                SELECT package_id,block_id,package_no,lesson_hours,source_path,
                       payload_sha256,payload_json
                FROM lesson_plan_packages
                ORDER BY theme_id,block_id,package_no
                LIMIT 1
                """
            ).fetchone()
            self.assertIsNotNone(row)
            package_id, block_id, package_no, hours, source_path, payload_hash, payload_json = row
            self.assertTrue(package_id.endswith("_P01"))
            self.assertEqual(package_id, f"{block_id}_P{package_no:02d}")
            self.assertIn(hours, (1, 2))
            source = root / source_path
            self.assertTrue(source.exists())
            self.assertEqual(
                payload_hash,
                hashlib.sha256(source.read_bytes()).hexdigest(),
            )
            payload = json.loads(payload_json)
            self.assertEqual(payload["block_id"], block_id)
            self.assertEqual(payload["lesson_hours"], hours)

            course_row = db.execute(
                "SELECT schema_version,source_manifest_fingerprint FROM courses LIMIT 1"
            ).fetchone()
            self.assertEqual(course_row[0], manifest["schema_version"])
            self.assertEqual(
                course_row[1], manifest["canonical_content_fingerprint"]
            )
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            db.close()

    def test_02_tde10_projects_same_runtime_contract(self) -> None:
        root, _, manifest = self._build_and_project("TDE_10")
        self.assertEqual(manifest["lesson_plan_package_count"], 88)
        self.assertEqual(manifest["lesson_plan_instruction_hours"], 172)
        db = sqlite3.connect(root / "runtime/course_runtime.sqlite")
        try:
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(DISTINCT theme_id) FROM lesson_plan_packages"
                ).fetchone()[0],
                4,
            )
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(DISTINCT block_id) FROM lesson_plan_packages"
                ).fetchone()[0],
                16,
            )
        finally:
            db.close()

    def test_03_missing_generated_package_fails_closed(self) -> None:
        root = self._copy_course("TDE_9")
        plans = sorted((root / "generated/lesson_plans").glob("*/*/*.json"))
        self.assertEqual(len(plans), 88)
        plans[-1].unlink()
        self.assertEqual(compiler.build(root)["status"], "PASS")
        with self.assertRaises(ValueError):
            lesson_payload.project_runtime_lesson_plan_payload(root)


if __name__ == "__main__":
    unittest.main()
