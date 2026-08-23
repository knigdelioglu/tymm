#!/usr/bin/env python3
"""Regression tests for the two-stage post-approval resume flow."""
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from artifact_generation import ArtifactGenerationError, PILOT_ARTIFACT_ID
from resume_after_teacher_approval import EXPECTED_CURSOR, WRITING_RUBRIC_ID, require_current_approval


class ResumeAfterTeacherApprovalTests(unittest.TestCase):
    def test_01_missing_speaking_approval_never_counts_as_consent(self):
        state = {
            "artifact_id": PILOT_ARTIFACT_ID,
            "approval_record": "MISSING",
        }
        with self.assertRaises(ArtifactGenerationError) as ctx:
            require_current_approval(state, PILOT_ARTIFACT_ID)
        self.assertIn("EXPLICIT_TEACHER_APPROVAL_REQUIRED", str(ctx.exception))
        self.assertIn(PILOT_ARTIFACT_ID, str(ctx.exception))

    def test_02_stale_approval_never_opens_gate(self):
        state = {
            "artifact_id": PILOT_ARTIFACT_ID,
            "approval_record": "INVALID_OR_STALE",
            "error": "TEACHER_APPROVAL_CONTEXT_STALE",
        }
        with self.assertRaises(ArtifactGenerationError) as ctx:
            require_current_approval(state, PILOT_ARTIFACT_ID)
        self.assertIn("TEACHER_APPROVAL_CONTEXT_STALE", str(ctx.exception))

    def test_03_current_explicit_approval_opens_only_that_artifact_gate(self):
        state = {
            "artifact_id": PILOT_ARTIFACT_ID,
            "approval_record": "CURRENT",
            "reviewer": "Test Teacher",
        }
        require_current_approval(state, PILOT_ARTIFACT_ID)

    def test_04_missing_writing_approval_is_independently_blocking(self):
        state = {
            "artifact_id": WRITING_RUBRIC_ID,
            "approval_record": "MISSING",
        }
        with self.assertRaises(ArtifactGenerationError) as ctx:
            require_current_approval(state, WRITING_RUBRIC_ID)
        self.assertIn(WRITING_RUBRIC_ID, str(ctx.exception))

    def test_05_resume_pipeline_is_bound_to_current_lesson_cursor(self):
        self.assertEqual(EXPECTED_CURSOR, "BLOCK_T2_04_YAZMA_P05")


if __name__ == "__main__":
    unittest.main(verbosity=2)
