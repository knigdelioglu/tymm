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
    SOURCE_SHAS = {
        "production_manifest": "a" * 40,
        "assessment_artifact_registry": "b" * 40,
        "assessment_design_contract": "c" * 40,
    }

    def test_01_missing_record_is_reported_without_implicit_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = status(root, PILOT_ARTIFACT_ID)
            self.assertEqual(result["approval_record"], "MISSING")

    def test_02_record_is_bound_to_review_generator_and_canonical_sources(self):
        record = build_record(COURSE_ROOT, PILOT_ARTIFACT_ID, "Test Teacher", "Reviewed")
        self.assertEqual(record["schema_version"], APPROVAL_SCHEMA_VERSION)
        self.assertEqual(record["artifact_id"], PILOT_ARTIFACT_ID)
        self.assertTrue(record["approved"])
        self.assertEqual(record["approval_kind"], "EXPLICIT_TEACHER_APPROVAL")
        self.assertEqual(len(record["review_snapshot_git_blob_sha"]), 40)
        self.assertEqual(len(record["generator_source_git_blob_sha"]), 40)
        self.assertEqual(
            set(record["canonical_source_git_blob_shas"]),
            {"production_manifest", "assessment_artifact_registry", "assessment_design_contract"},
        )
        self.assertTrue(all(len(x) == 40 for x in record["canonical_source_git_blob_shas"].values()))
        self.assertEqual(record["reviewer"], "Test Teacher")

    def test_03_empty_reviewer_is_rejected(self):
        with self.assertRaises(ArtifactGenerationError):
            build_record(COURSE_ROOT, PILOT_ARTIFACT_ID, "   ")

    def _write_record(
        self,
        root: Path,
        *,
        review_sha: str,
        generator_sha: str,
        source_shas: dict,
    ) -> None:
        target = approval_path(root, PILOT_ARTIFACT_ID)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({
            "schema_version": APPROVAL_SCHEMA_VERSION,
            "artifact_id": PILOT_ARTIFACT_ID,
            "review_snapshot_git_blob_sha": review_sha,
            "generator_source_git_blob_sha": generator_sha,
            "canonical_source_git_blob_shas": source_shas,
            "approved": True,
            "reviewer": "Test Teacher",
            "review_note": None,
            "approval_kind": "EXPLICIT_TEACHER_APPROVAL",
            "reproducibility_rule": "test",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _identity(self, *, review_sha="2" * 40, generator_sha="3" * 40, source_shas=None):
        return {
            "review_snapshot_git_blob_sha": review_sha,
            "generator_source_git_blob_sha": generator_sha,
            "canonical_source_git_blob_shas": source_shas or dict(self.SOURCE_SHAS),
        }

    def test_04_changed_review_snapshot_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_record(root, review_sha="2" * 40, generator_sha="3" * 40, source_shas=self.SOURCE_SHAS)
            with patch("teacher_approval._current_approval_identity", return_value=self._identity(review_sha="4" * 40)), \
                 patch("teacher_approval.build_generation_context", return_value={}):
                with self.assertRaises(ArtifactGenerationError) as ctx:
                    validate_record(root, PILOT_ARTIFACT_ID)
            self.assertIn("TEACHER_APPROVAL_REVIEW_SNAPSHOT_STALE", str(ctx.exception))

    def test_05_changed_generator_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_record(root, review_sha="2" * 40, generator_sha="3" * 40, source_shas=self.SOURCE_SHAS)
            with patch("teacher_approval._current_approval_identity", return_value=self._identity(generator_sha="5" * 40)), \
                 patch("teacher_approval.build_generation_context", return_value={}):
                with self.assertRaises(ArtifactGenerationError) as ctx:
                    validate_record(root, PILOT_ARTIFACT_ID)
            self.assertIn("TEACHER_APPROVAL_GENERATOR_SOURCE_STALE", str(ctx.exception))

    def test_06_changed_canonical_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_record(root, review_sha="2" * 40, generator_sha="3" * 40, source_shas=self.SOURCE_SHAS)
            changed = dict(self.SOURCE_SHAS)
            changed["assessment_design_contract"] = "d" * 40
            with patch("teacher_approval._current_approval_identity", return_value=self._identity(source_shas=changed)), \
                 patch("teacher_approval.build_generation_context", return_value={}):
                with self.assertRaises(ArtifactGenerationError) as ctx:
                    validate_record(root, PILOT_ARTIFACT_ID)
            self.assertIn("TEACHER_APPROVAL_CANONICAL_SOURCE_STALE", str(ctx.exception))

    def test_07_current_identity_still_requires_semantic_context_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_record(root, review_sha="2" * 40, generator_sha="3" * 40, source_shas=self.SOURCE_SHAS)
            with patch("teacher_approval._current_approval_identity", return_value=self._identity()), \
                 patch("teacher_approval.build_generation_context", side_effect=ArtifactGenerationError("P0_GATE_NOT_READY")):
                with self.assertRaises(ArtifactGenerationError) as ctx:
                    validate_record(root, PILOT_ARTIFACT_ID)
            self.assertIn("P0_GATE_NOT_READY", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
