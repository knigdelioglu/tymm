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
from teacher_approval import APPROVAL_SCHEMA_VERSION, approval_path, build_record, status, validate_record

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = REPO_ROOT / "courses" / "TDE_9"
COURSE_ROOT = Path(os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_ROOT)).resolve()


class TeacherApprovalRecordTests(unittest.TestCase):
    def test_01_missing_record_is_reported_without_implicit_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = status(root, PILOT_ARTIFACT_ID)
            self.assertEqual(result["approval_record"], "MISSING")

    def test_02_record_is_bound_to_context_review_snapshot_and_generator_source(self):
        record = build_record(COURSE_ROOT, PILOT_ARTIFACT_ID, "Test Teacher", "Reviewed")
        self.assertEqual(record["schema_version"], APPROVAL_SCHEMA_VERSION)
        self.assertEqual(record["artifact_id"], PILOT_ARTIFACT_ID)
        self.assertTrue(record["approved"])
        self.assertEqual(record["approval_kind"], "EXPLICIT_TEACHER_APPROVAL")
        self.assertTrue(record["generation_context_hash"])
        self.assertEqual(len(record["generation_context_hash"]), 64)
        self.assertTrue(record["review_snapshot_git_blob_sha"])
        self.assertEqual(len(record["review_snapshot_git_blob_sha"]), 40)
        self.assertTrue(record["generator_source_git_blob_sha"])
        self.assertEqual(len(record["generator_source_git_blob_sha"]), 40)
        self.assertEqual(record["reviewer"], "Test Teacher")

    def test_03_empty_reviewer_is_rejected(self):
        with self.assertRaises(ArtifactGenerationError):
            build_record(COURSE_ROOT, PILOT_ARTIFACT_ID, "   ")

    def _write_record(
        self,
        root: Path,
        *,
        context_hash: str,
        review_sha: str,
        generator_sha: str,
    ) -> None:
        target = approval_path(root, PILOT_ARTIFACT_ID)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({
            "schema_version": APPROVAL_SCHEMA_VERSION,
            "artifact_id": PILOT_ARTIFACT_ID,
            "generation_context_hash": context_hash,
            "review_snapshot_git_blob_sha": review_sha,
            "generator_source_git_blob_sha": generator_sha,
            "approved": True,
            "reviewer": "Test Teacher",
            "review_note": None,
            "approval_kind": "EXPLICIT_TEACHER_APPROVAL",
            "reproducibility_rule": "test",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def test_04_stale_context_hash_is_rejected_without_touching_repo_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_record(root, context_hash="0" * 64, review_sha="2" * 40, generator_sha="3" * 40)
            with patch(
                "teacher_approval._current_approval_identity",
                return_value={
                    "generation_context_hash": "1" * 64,
                    "review_snapshot_git_blob_sha": "2" * 40,
                    "generator_source_git_blob_sha": "3" * 40,
                },
            ):
                with self.assertRaises(ArtifactGenerationError) as ctx:
                    validate_record(root, PILOT_ARTIFACT_ID)
            self.assertIn("TEACHER_APPROVAL_CONTEXT_STALE", str(ctx.exception))

    def test_05_changed_review_snapshot_is_rejected_even_when_context_matches(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_record(root, context_hash="1" * 64, review_sha="2" * 40, generator_sha="3" * 40)
            with patch(
                "teacher_approval._current_approval_identity",
                return_value={
                    "generation_context_hash": "1" * 64,
                    "review_snapshot_git_blob_sha": "4" * 40,
                    "generator_source_git_blob_sha": "3" * 40,
                },
            ):
                with self.assertRaises(ArtifactGenerationError) as ctx:
                    validate_record(root, PILOT_ARTIFACT_ID)
            self.assertIn("TEACHER_APPROVAL_REVIEW_SNAPSHOT_STALE", str(ctx.exception))

    def test_06_changed_generator_source_is_rejected_even_when_review_and_context_match(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_record(root, context_hash="1" * 64, review_sha="2" * 40, generator_sha="3" * 40)
            with patch(
                "teacher_approval._current_approval_identity",
                return_value={
                    "generation_context_hash": "1" * 64,
                    "review_snapshot_git_blob_sha": "2" * 40,
                    "generator_source_git_blob_sha": "5" * 40,
                },
            ):
                with self.assertRaises(ArtifactGenerationError) as ctx:
                    validate_record(root, PILOT_ARTIFACT_ID)
            self.assertIn("TEACHER_APPROVAL_GENERATOR_SOURCE_STALE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
