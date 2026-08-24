#!/usr/bin/env python3
"""Resume blocked TDE9 production through explicit teacher approval gates.

The pipeline has two independent human-review gates:
1) TDE9_KONUSMA_RUBRIC must have a current explicit teacher approval before the
   Generator V1 order gate may create TDE9_YAZMA_RUBRIC.
2) TDE9_YAZMA_RUBRIC itself is teacher-review-required. Its specialized 4x4 draft
   and REVIEW.md snapshot are generated first; P05 opens only after a separate,
   current explicit approval record for that reviewed snapshot exists.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

from artifact_generation import (
    ArtifactGenerationError,
    LIFECYCLE_APPROVED,
    LIFECYCLE_FROZEN,
    LIFECYCLE_REVIEW,
    PILOT_ARTIFACT_ID,
)
from teacher_approval import apply_record, status as approval_status
from writing_rubric_generation import WRITING_RUBRIC_ID, generate_writing_to_directory

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
DEFAULT_COURSE_ROOT = REPO_ROOT / "courses" / "TDE_9"
EXPECTED_CURSOR = "BLOCK_T2_04_YAZMA_P05"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ArtifactGenerationError(f"REQUIRED_FILE_MISSING: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ArtifactGenerationError(f"JSON_ROOT_MUST_BE_OBJECT: {path}")
    return data


def require_current_approval(state: Dict[str, Any], artifact_id: str) -> None:
    if state.get("approval_record") != "CURRENT":
        reason = state.get("error") or state.get("approval_record") or "UNKNOWN"
        raise ArtifactGenerationError(
            f"EXPLICIT_TEACHER_APPROVAL_REQUIRED: {artifact_id} ({reason})"
        )


def check_lesson_cursor(course_root: Path) -> Dict[str, Any]:
    plan_path = course_root / "planning" / "lesson_plan_production_plan.json"
    plan = _read_json(plan_path)
    nxt = (plan.get("progress") or {}).get("next") or {}
    package_id = nxt.get("package_id")
    if package_id != EXPECTED_CURSOR:
        raise ArtifactGenerationError(
            f"LESSON_CURSOR_NOT_AT_EXPECTED_GATE: expected {EXPECTED_CURSOR}, got {package_id}"
        )
    return {
        "package_id": package_id,
        "completed_packages": (plan.get("progress") or {}).get("completed_packages"),
        "completed_instruction_hours": (plan.get("progress") or {}).get("completed_instruction_hours"),
    }


def preflight(course_root: Path) -> Dict[str, Any]:
    cursor = check_lesson_cursor(course_root)
    pilot_approval = approval_status(course_root, PILOT_ARTIFACT_ID)
    writing_approval = approval_status(course_root, WRITING_RUBRIC_ID)

    pilot_current = pilot_approval.get("approval_record") == "CURRENT"
    writing_current = writing_approval.get("approval_record") == "CURRENT"

    if not pilot_current:
        stage = "AWAITING_SPEAKING_RUBRIC_APPROVAL"
    elif not writing_current:
        stage = "READY_TO_GENERATE_OR_REVIEW_WRITING_RUBRIC"
    else:
        stage = "READY_TO_APPLY_WRITING_RUBRIC_APPROVAL"

    return {
        "pipeline": "TDE9_POST_TEACHER_APPROVAL_RESUME",
        "lesson_cursor": cursor,
        "pilot_approval": pilot_approval,
        "writing_rubric_approval": writing_approval,
        "stage": stage,
        "ready_for_p05": pilot_current and writing_current,
    }


def run(course_root: Path, output_root: Path) -> Dict[str, Any]:
    state = preflight(course_root)
    require_current_approval(state["pilot_approval"], PILOT_ARTIFACT_ID)

    pilot = apply_record(course_root, output_root, PILOT_ARTIFACT_ID)
    if pilot.get("lifecycle_status") not in {LIFECYCLE_APPROVED, LIFECYCLE_FROZEN}:
        raise ArtifactGenerationError("PILOT_APPROVAL_APPLICATION_FAILED")

    context, writing_rubric, changed = generate_writing_to_directory(course_root, output_root)

    writing_approval = approval_status(course_root, WRITING_RUBRIC_ID)
    if writing_approval.get("approval_record") != "CURRENT":
        if writing_rubric.get("lifecycle_status") != LIFECYCLE_REVIEW:
            raise ArtifactGenerationError(
                f"WRITING_RUBRIC_UNEXPECTED_LIFECYCLE: {writing_rubric.get('lifecycle_status')}"
            )
        return {
            "pipeline": "TDE9_POST_TEACHER_APPROVAL_RESUME",
            "status": "AWAITING_WRITING_RUBRIC_TEACHER_APPROVAL",
            "lesson_cursor": state["lesson_cursor"],
            "pilot_artifact": {
                "artifact_id": PILOT_ARTIFACT_ID,
                "lifecycle_status": pilot.get("lifecycle_status"),
                "teacher_review_status": pilot.get("teacher_review_status"),
            },
            "writing_rubric": {
                "artifact_id": WRITING_RUBRIC_ID,
                "changed": changed,
                "revision": writing_rubric.get("artifact_revision"),
                "generation_context_hash": context.get("context_hash"),
                "lifecycle_status": writing_rubric.get("lifecycle_status"),
                "validation": "PASS",
                "descriptor_profile": "TDE9_WRITING_OBSERVABLE_4X4_V1",
                "review_path": str(output_root / WRITING_RUBRIC_ID / "REVIEW.md"),
            },
            "ready_for_p05": False,
            "important_note": (
                "Writing-rubric generation/validation is not teacher approval. "
                "Review the generated REVIEW.md snapshot before recording approval."
            ),
        }

    approved_writing = apply_record(course_root, output_root, WRITING_RUBRIC_ID)
    if approved_writing.get("lifecycle_status") not in {LIFECYCLE_APPROVED, LIFECYCLE_FROZEN}:
        raise ArtifactGenerationError("WRITING_RUBRIC_APPROVAL_APPLICATION_FAILED")

    return {
        "pipeline": "TDE9_POST_TEACHER_APPROVAL_RESUME",
        "status": "READY_FOR_T2_WRITING_P05",
        "lesson_cursor": state["lesson_cursor"],
        "pilot_artifact": {
            "artifact_id": PILOT_ARTIFACT_ID,
            "lifecycle_status": pilot.get("lifecycle_status"),
        },
        "writing_rubric": {
            "artifact_id": WRITING_RUBRIC_ID,
            "lifecycle_status": approved_writing.get("lifecycle_status"),
            "teacher_review_status": approved_writing.get("teacher_review_status"),
            "validation": "PASS",
            "descriptor_profile": "TDE9_WRITING_OBSERVABLE_4X4_V1",
        },
        "ready_for_p05": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume TDE9 production through explicit teacher approval gates")
    parser.add_argument("--course-root")
    parser.add_argument("--output-root")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight")
    sub.add_parser("run")
    args = parser.parse_args()

    course_root = Path(args.course_root or os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_COURSE_ROOT)).resolve()
    output_root = Path(args.output_root).resolve() if args.output_root else course_root / "generated"

    try:
        result = preflight(course_root) if args.command == "preflight" else run(course_root, output_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == "preflight" and not result.get("ready_for_p05"):
            return 2
        if args.command == "run" and not result.get("ready_for_p05"):
            return 2
        return 0
    except ArtifactGenerationError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
