#!/usr/bin/env python3
"""Regression tests for persistent explicit teacher approval records."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_04_stale_context_hash_is_rejected_without_touching_repo_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = approval_path(root, PILOT_ARTIFACT_ID)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps({
                "schema_version": "1.0",
                "artifact_id": PILOT_ARTIFACT_ID,
                "generation_context_hash": "0" * 64,
                "approved": True,
                "reviewer": "Test Teacher",
                "review_note": None,
                "approval_kind": "EXPLICIT_TEACHER_APPROVAL",
                "reproducibility_rule": "test",
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            with patch("teacher_approval.build_generation_context", return_value={"context_hash": "1" * 64}):
                with self.assertRaises(ArtifactGenerationError) as ctx:
                    validate_record(root, PILOT_ARTIFACT_ID)
            self.assertIn("TEACHER_APPROVAL_CONTEXT_STALE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
