#!/usr/bin/env python3
"""Acceptance gate for Artifact Generation Engine V1 pilot."""
import argparse
import json
import os
import tempfile
from pathlib import Path

from artifact_generation import (
    ArtifactGenerationError,
    LIFECYCLE_APPROVED,
    LIFECYCLE_FROZEN,
    LIFECYCLE_REVIEW,
    PILOT_ARTIFACT_ID,
    assert_generation_order,
    build_generation_context,
    generate_to_directory,
    load_current_artifact,
    stable_hash,
    validate_generated_artifact,
)

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
DEFAULT_ROOT = REPO_ROOT / "courses" / "TDE_9"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactGenerationError(message)


def run_gate(course_root: Path, output_root: Path, require_approved: bool = False) -> dict:
    context = build_generation_context(course_root, PILOT_ARTIFACT_ID)
    artifact = load_current_artifact(output_root, PILOT_ARTIFACT_ID)
    require(artifact is not None, "PILOT_ARTIFACT_MISSING")
    validate_generated_artifact(artifact, context)
    require(artifact["generation_context_hash"] == context["context_hash"], "PILOT_CONTEXT_STALE")
    require(len(artifact.get("criteria_table", [])) == 5, "PILOT_EXPECTED_5_CORE_CRITERIA")
    require(all(len(row.get("descriptors", [])) == 4 for row in artifact.get("criteria_table", [])),
            "PILOT_DESCRIPTOR_MATRIX_INCOMPLETE")
    require(
        set(artifact.get("provenance", {}).get("covered_gap_instances", [])) == {
            "MAT_T2_KONUSMA_RUBRIC", "MAT_T3_KONUSMA_RUBRIC", "MAT_T4_KONUSMA_RUBRIC"
        },
        "PILOT_3_GAP_PROVENANCE_INVALID",
    )

    with tempfile.TemporaryDirectory() as td:
        temp_out = Path(td) / "generated"
        c1, a1, changed1 = generate_to_directory(course_root, PILOT_ARTIFACT_ID, temp_out)
        c2, a2, changed2 = generate_to_directory(course_root, PILOT_ARTIFACT_ID, temp_out)
        require(changed1 is True, "FIRST_GENERATION_MUST_CREATE_DRAFT")
        require(changed2 is False, "SECOND_GENERATION_MUST_BE_IDEMPOTENT")
        require(c1["context_hash"] == c2["context_hash"], "IDEMPOTENT_CONTEXT_HASH_CHANGED")
        require(a1["artifact_revision"] == a2["artifact_revision"] == 1, "IDEMPOTENT_REVISION_CHANGED")
        require(stable_hash(a1) == stable_hash(a2), "IDEMPOTENT_ARTIFACT_CONTENT_CHANGED")

    lifecycle = artifact.get("lifecycle_status")
    if lifecycle == LIFECYCLE_REVIEW:
        blocked = False
        try:
            assert_generation_order(output_root, "TDE9_YAZMA_RUBRIC")
        except ArtifactGenerationError:
            blocked = True
        require(blocked, "NON_PILOT_GENERATION_OPENED_BEFORE_PILOT_APPROVAL")
        if require_approved:
            raise ArtifactGenerationError("GENERATOR_V1_GATE_REQUIRES_TEACHER_APPROVAL")
        final = "ENGINEERING_PASS_REVIEW_REQUIRED"
    elif lifecycle in {LIFECYCLE_APPROVED, LIFECYCLE_FROZEN}:
        assert_generation_order(output_root, "TDE9_YAZMA_RUBRIC")
        final = "PASS"
    else:
        raise ArtifactGenerationError(f"UNEXPECTED_PILOT_LIFECYCLE: {lifecycle}")

    report = {
        "generator_gate_version": "1.0",
        "pilot_artifact_id": PILOT_ARTIFACT_ID,
        "pilot_revision": artifact.get("artifact_revision"),
        "generation_context_hash": context["context_hash"],
        "structural_validation": "PASS",
        "pedagogical_contract_validation": "PASS",
        "provenance_validation": "PASS",
        "idempotency_validation": "PASS",
        "teacher_review_status": artifact.get("teacher_review_status"),
        "final": final,
    }
    report_path = output_root / PILOT_ARTIFACT_ID / "generator_v1_gate_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="TYMM Generator V1 pilot gate")
    parser.add_argument("--course-root")
    parser.add_argument("--output-root")
    parser.add_argument("--require-approved", action="store_true")
    args = parser.parse_args()
    course_root = Path(args.course_root or os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_ROOT)).resolve()
    output_root = Path(args.output_root).resolve() if args.output_root else course_root / "generated"
    try:
        report = run_gate(course_root, output_root, require_approved=args.require_approved)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        print(f"GENERATOR V1 GATE: {report['final']}")
        return 0
    except ArtifactGenerationError as exc:
        print(json.dumps({"final": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
