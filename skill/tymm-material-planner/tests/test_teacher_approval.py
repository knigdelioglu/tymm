#!/usr/bin/env python3
"""Regression tests for persistent explicit teacher approval records."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from artifact_generation import ArtifactGenerationError, PILOT_ARTIFACT_ID
from teacher_approval import approval_path, build_record, status, validate_record

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = REPO_ROOT / "courses" / "TDE_9"
COURSE_ROOT = Path(os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_ROOT)).resolve()


class TeacherApprovalRecordTests(unittest.TestCase):
    def test_01_missing_record_is_reported_without_implicit_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = status(root, PILOT_ARTIFACT_ID)
            self.assertEqual(result["approval_record"], "MISSING")

    def test_02_record_is_bound_to_current_generation_context(self):
        record = build_record(COURSE_ROOT, PILOT_ARTIFACT_ID, "Test Teacher", "Reviewed")
        self.assertEqual(record["artifact_id"], PILOT_ARTIFACT_ID)
        self.assertTrue(record["approved"])
        self.assertEqual(record["approval_kind"], "EXPLICIT_TEACHER_APPROVAL")
        self.assertTrue(record["generation_context_hash"])
        self.assertEqual(record["reviewer"], "Test Teacher")

    def test_03_empty_reviewer_is_rejected(self):
        with self.assertRaises(ArtifactGenerationError):
            build_record(COURSE_ROOT, PILOT_ARTIFACT_ID, "   ")

    def test_04_stale_context_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            # Use the real course root for canonical context but temporarily place
            # a stale record at the canonical approval path, then restore state.
            target = approval_path(COURSE_ROOT, PILOT_ARTIFACT_ID)
            target.parent.mkdir(parents=True, exist_ok=True)
            original = target.read_text(encoding="utf-8") if target.exists() else None
            try:
                record = build_record(COURSE_ROOT, PILOT_ARTIFACT_ID, "Test Teacher")
                record["generation_context_hash"] = "0" * 64
                target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                with self.assertRaises(ArtifactGenerationError) as ctx:
                    validate_record(COURSE_ROOT, PILOT_ARTIFACT_ID)
                self.assertIn("TEACHER_APPROVAL_CONTEXT_STALE", str(ctx.exception))
            finally:
                if original is None:
                    target.unlink(missing_ok=True)
                else:
                    target.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main(verbosity=2)
