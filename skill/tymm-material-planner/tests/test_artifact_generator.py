#!/usr/bin/env python3
"""Regression tests for Artifact Generation Engine V1."""
import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from artifact_generation import (
    ArtifactGenerationError,
    LIFECYCLE_APPROVED,
    LIFECYCLE_FROZEN,
    LIFECYCLE_REVIEW,
    PILOT_ARTIFACT_ID,
    approve_artifact,
    assert_generation_order,
    build_generation_context,
    freeze_artifact,
    generate_draft,
    generate_to_directory,
    stable_hash,
    validate_generated_artifact,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = REPO_ROOT / "courses" / "TDE_9"
COURSE_ROOT = Path(os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_ROOT)).resolve()


class ArtifactGeneratorV1Tests(unittest.TestCase):
    def test_01_context_requires_canonical_artifact_id(self):
        with self.assertRaises(ArtifactGenerationError):
            build_generation_context(COURSE_ROOT, "MAT_T2_KONUSMA_RUBRIC")

    def test_02_pilot_context_maps_3_gap_aliases_to_one_artifact(self):
        context = build_generation_context(COURSE_ROOT, PILOT_ARTIFACT_ID)
        self.assertEqual(context["artifact_id"], PILOT_ARTIFACT_ID)
        self.assertEqual(context["source_versions"]["knowledge_index_status"], "INDEX_FRESH")
        self.assertEqual(
            set(context["artifact"]["covered_gap_instances"]),
            {"MAT_T2_KONUSMA_RUBRIC", "MAT_T3_KONUSMA_RUBRIC", "MAT_T4_KONUSMA_RUBRIC"},
        )
        self.assertTrue(all(x["resolved_artifact_id"] == PILOT_ARTIFACT_ID for x in context["gap_provenance"]))
        self.assertFalse(context["artifact_id"].startswith("MAT_"))

    def test_03_pilot_rubric_matrix_is_5_by_4_and_contract_valid(self):
        context = build_generation_context(COURSE_ROOT, PILOT_ARTIFACT_ID)
        artifact = generate_draft(context)
        validate_generated_artifact(artifact, context)
        self.assertEqual(len(artifact["criteria_table"]), 5)
        self.assertTrue(all(len(row["descriptors"]) == 4 for row in artifact["criteria_table"]))
        self.assertEqual(artifact["lifecycle_status"], LIFECYCLE_REVIEW)
        self.assertFalse(artifact["teacher_review_status"]["approved"])
        self.assertEqual(artifact["scoring_instructions"]["min_raw_total"], 5)
        self.assertEqual(artifact["scoring_instructions"]["max_raw_total"], 20)

    def test_04_descriptor_provenance_and_forbidden_language(self):
        context = build_generation_context(COURSE_ROOT, PILOT_ARTIFACT_ID)
        artifact = generate_draft(context)
        forbidden = {
            x.casefold()
            for x in context["contract_profile"]["descriptor_writing_standards"]["forbidden_phrasing_patterns"]
        }
        texts = []
        for row in artifact["criteria_table"]:
            for descriptor in row["descriptors"]:
                self.assertEqual(descriptor["origin"], "pedagogical_recommendation")
                text = descriptor["descriptor"]
                texts.append(text)
                self.assertFalse(any(pattern in text.casefold() for pattern in forbidden))
        self.assertEqual(len(texts), 20)
        self.assertEqual(len(set(texts)), 20)

    def test_05_same_context_generation_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "generated"
            c1, a1, changed1 = generate_to_directory(COURSE_ROOT, PILOT_ARTIFACT_ID, out)
            c2, a2, changed2 = generate_to_directory(COURSE_ROOT, PILOT_ARTIFACT_ID, out)
            self.assertTrue(changed1)
            self.assertFalse(changed2)
            self.assertEqual(c1["context_hash"], c2["context_hash"])
            self.assertEqual(a1["artifact_revision"], a2["artifact_revision"])
            self.assertEqual(stable_hash(a1), stable_hash(a2))

    def test_06_generation_does_not_equal_approval(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "generated"
            _, artifact, _ = generate_to_directory(COURSE_ROOT, PILOT_ARTIFACT_ID, out)
            self.assertEqual(artifact["lifecycle_status"], LIFECYCLE_REVIEW)
            self.assertFalse(artifact["teacher_review_status"]["approved"])
            with self.assertRaises(ArtifactGenerationError):
                freeze_artifact(COURSE_ROOT, PILOT_ARTIFACT_ID, out)

    def test_07_explicit_teacher_approval_then_freeze(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "generated"
            generate_to_directory(COURSE_ROOT, PILOT_ARTIFACT_ID, out)
            approved = approve_artifact(COURSE_ROOT, PILOT_ARTIFACT_ID, out, "Test Teacher", "Pilot reviewed")
            self.assertEqual(approved["lifecycle_status"], LIFECYCLE_APPROVED)
            self.assertTrue(approved["teacher_review_status"]["approved"])
            frozen = freeze_artifact(COURSE_ROOT, PILOT_ARTIFACT_ID, out)
            self.assertEqual(frozen["lifecycle_status"], LIFECYCLE_FROZEN)

    def test_08_next_artifacts_are_blocked_before_pilot_approval(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "generated"
            generate_to_directory(COURSE_ROOT, PILOT_ARTIFACT_ID, out)
            with self.assertRaises(ArtifactGenerationError):
                assert_generation_order(out, "TDE9_YAZMA_RUBRIC")
            with self.assertRaises(ArtifactGenerationError):
                generate_to_directory(COURSE_ROOT, "TDE9_YAZMA_RUBRIC", out)

    def test_09_next_artifact_selection_opens_only_after_pilot_approval(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "generated"
            generate_to_directory(COURSE_ROOT, PILOT_ARTIFACT_ID, out)
            approve_artifact(COURSE_ROOT, PILOT_ARTIFACT_ID, out, "Test Teacher")
            assert_generation_order(out, "TDE9_YAZMA_RUBRIC")
            context, artifact, changed = generate_to_directory(COURSE_ROOT, "TDE9_YAZMA_RUBRIC", out)
            self.assertTrue(changed)
            self.assertEqual(context["artifact_id"], "TDE9_YAZMA_RUBRIC")
            self.assertEqual(artifact["lifecycle_status"], LIFECYCLE_REVIEW)
            self.assertFalse(artifact["teacher_review_status"]["approved"])

    def test_10_context_hash_detects_relevant_context_change(self):
        context = build_generation_context(COURSE_ROOT, PILOT_ARTIFACT_ID)
        mutated = copy.deepcopy(context)
        original_hash = mutated.pop("context_hash")
        mutated["artifact"]["title"] = mutated["artifact"]["title"] + " TEST"
        self.assertNotEqual(original_hash, stable_hash(mutated))


if __name__ == "__main__":
    unittest.main(verbosity=2)
