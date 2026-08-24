#!/usr/bin/env python3
"""Regression tests for the TDE9 annual writing rubric descriptor profile."""
import os
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from artifact_generation import build_generation_context, generate_draft, validate_generated_artifact
from writing_rubric_generation import (
    WRITING_DESCRIPTORS,
    WRITING_RUBRIC_ID,
    apply_writing_descriptors,
    render_review,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = REPO_ROOT / "courses" / "TDE_9"
COURSE_ROOT = Path(os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_ROOT)).resolve()


class WritingRubricGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = build_generation_context(COURSE_ROOT, WRITING_RUBRIC_ID)
        cls.generic = generate_draft(cls.context)
        cls.artifact = apply_writing_descriptors(cls.generic)

    def test_01_canonical_four_criteria_are_preserved(self):
        ids = [row["criterion_id"] for row in self.artifact["criteria_table"]]
        self.assertEqual(ids, [
            "CRT_WRT_CORE_01",
            "CRT_WRT_CORE_02",
            "CRT_WRT_CORE_03",
            "CRT_WRT_CORE_04",
        ])
        self.assertEqual(set(ids), set(WRITING_DESCRIPTORS))

    def test_02_each_criterion_has_four_distinct_observable_descriptors(self):
        for row in self.artifact["criteria_table"]:
            descriptors = row["descriptors"]
            self.assertEqual(len(descriptors), 4)
            texts = [x["descriptor"] for x in descriptors]
            self.assertEqual(len(set(texts)), 4)
            self.assertTrue(all(x["origin"] == "pedagogical_recommendation" for x in descriptors))
            self.assertFalse(any("yönlendirmeye ihtiyaç" in text for text in texts))
            self.assertFalse(any("yoğun yönlendirme" in text for text in texts))

    def test_03_specialized_artifact_still_passes_canonical_validator(self):
        validate_generated_artifact(self.artifact, self.context)
        scoring = self.artifact["scoring_instructions"]
        self.assertEqual(scoring["criterion_count"], 4)
        self.assertEqual(scoring["min_raw_total"], 4)
        self.assertEqual(scoring["max_raw_total"], 16)
        self.assertEqual(scoring["primary_model"], "RAW_MEAN_1_TO_4")

    def test_04_review_snapshot_exposes_lifecycle_criteria_and_task_bindings(self):
        text = render_review(self.context, self.artifact)
        self.assertIn("TDE9_YAZMA_RUBRIC — Teacher Review", text)
        self.assertIn("REVIEW_REQUIRED", text)
        for row in self.artifact["criteria_table"]:
            self.assertIn(row["criterion_name"], text)
        self.assertIn("TEMA_02", text)
        self.assertIn("Ben Şair Olsaydım", text)
        self.assertIn("TEMA_03", text)
        self.assertIn("TEMA_04", text)
        self.assertIn("BLOCK_T2_04_YAZMA_P05", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
