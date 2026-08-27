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
import teacher_facing_text

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

    def _build(self, course_id: str) -> tuple[Path, dict]:
        root = self._copy_course(course_id)
        result = compiler.build(root)
        self.assertEqual(result["status"], "PASS")
        manifest = json.loads(
            (root / "runtime/runtime_manifest.json").read_text(encoding="utf-8")
        )
        return root, manifest

    def test_01_tde9_build_projects_88_packages_and_172_hours(self) -> None:
        root, manifest = self._build("TDE_9")
        self.assertEqual(manifest["schema_version"], "1.2.0")
        self.assertEqual(manifest["runtime_package_version"], "1.3.0")
        self.assertEqual(manifest["lesson_plan_payload_projection_version"], "1.2.0")
        self.assertEqual(manifest["lesson_plan_package_count"], 88)
        self.assertEqual(manifest["lesson_plan_instruction_hours"], 172)
        self.assertTrue(manifest["lesson_plan_capabilities"]["available"])
        self.assertTrue(manifest["lesson_plan_capabilities"]["calendar_neutral"])
        self.assertTrue(manifest["lesson_plan_capabilities"]["validation_bound"])
        self.assertFalse(manifest["lesson_plan_capabilities"]["source_payload_parity"])
        self.assertTrue(manifest["lesson_plan_capabilities"]["teacher_facing_projection"])
        self.assertTrue(
            manifest["lesson_plan_capabilities"]["teacher_projection_source_bound"]
        )
        self.assertEqual(manifest["lesson_plan_validation"]["status"], "VERIFIED")
        self.assertEqual(manifest["lesson_plan_validation"]["scope"], "COURSE")
        self.assertEqual(
            manifest["lesson_plan_validation"]["seal_path"],
            "planning/lesson_plan_validation_seal.json",
        )
        self.assertEqual(manifest["row_counts"]["lesson_plan_packages"], 88)
        self.assertIn(
            "planning/lesson_plan_production_plan.json",
            manifest["canonical_source_hashes"],
        )
        self.assertNotIn(
            "planning/lesson_plan_validation_seal.json",
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
            source_payload = json.loads(source.read_text(encoding="utf-8"))
            self.assertEqual(payload["block_id"], source_payload["block_id"])
            self.assertEqual(payload["theme_id"], source_payload["theme_id"])
            self.assertEqual(payload["course_id"], source_payload["course_id"])
            self.assertEqual(payload["used_activity_ids"], source_payload["used_activity_ids"])
            self.assertEqual(payload["used_form_ids"], source_payload["used_form_ids"])
            self.assertEqual(payload["lesson_hours"], hours)
            self.assertFalse(teacher_facing_text.teacher_facing_validation_errors(payload))

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

    def test_02_tde10_build_projects_same_runtime_contract(self) -> None:
        root, manifest = self._build("TDE_10")
        self.assertEqual(manifest["lesson_plan_package_count"], 88)
        self.assertEqual(manifest["lesson_plan_instruction_hours"], 172)
        self.assertEqual(manifest["lesson_plan_validation"]["status"], "VERIFIED")
        self.assertTrue(manifest["lesson_plan_capabilities"]["teacher_facing_projection"])
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

    def test_03_missing_generated_package_fails_compiler_closed(self) -> None:
        root = self._copy_course("TDE_9")
        plans = sorted((root / "generated/lesson_plans").glob("*/*/*.json"))
        self.assertEqual(len(plans), 88)
        plans[-1].unlink()
        with self.assertRaises(ValueError):
            compiler.build(root)

    def test_04_projection_is_idempotent_after_compiler_build(self) -> None:
        root, before = self._build("TDE_9")
        result = lesson_payload.project_runtime_lesson_plan_payload(root)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["teacher_facing_projection"])
        after = json.loads(
            (root / "runtime/runtime_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            before["canonical_content_fingerprint"],
            after["canonical_content_fingerprint"],
        )
        self.assertEqual(after["row_counts"]["lesson_plan_packages"], 88)

    def test_05_source_mutation_without_new_seal_fails_closed(self) -> None:
        root = self._copy_course("TDE_9")
        plan_path = sorted((root / "generated/lesson_plans").glob("*/*/*.json"))[0]
        payload = json.loads(plan_path.read_text(encoding="utf-8"))
        payload["plan_summary"] = payload["plan_summary"] + " "
        plan_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            ValueError,
            "RUNTIME_LESSON_PLAN_COURSE_VALIDATION_BINDING_MISMATCH:content_fingerprint",
        ):
            compiler.build(root)

    def test_06_engineering_validation_counts_must_match_runtime_contract(self) -> None:
        root = self._copy_course("TDE_9")
        production_path = root / "planning/lesson_plan_production_plan.json"
        production = json.loads(production_path.read_text(encoding="utf-8"))
        production["engineering_validation"]["validated_packages"] = 87
        production_path.write_text(
            json.dumps(production, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            ValueError,
            "RUNTIME_LESSON_PLAN_ENGINEERING_PACKAGE_COUNT_MISMATCH",
        ):
            compiler.build(root)

    def test_07_missing_validation_seal_fails_closed(self) -> None:
        root = self._copy_course("TDE_10")
        (root / "planning/lesson_plan_validation_seal.json").unlink()
        with self.assertRaisesRegex(
            ValueError,
            "RUNTIME_LESSON_PLAN_VALIDATION_SEAL_MISSING",
        ):
            compiler.build(root)


if __name__ == "__main__":
    unittest.main()
