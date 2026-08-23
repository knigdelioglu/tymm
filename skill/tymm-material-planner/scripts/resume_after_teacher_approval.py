#!/usr/bin/env python3
"""Resume blocked TDE9 production after explicit teacher approval.

This helper never creates or infers teacher approval. It consumes only a current,
tracked approval record created by teacher_approval.py. When the pilot approval is
current, it recreates/applies the approved pilot artifact in the checkout, opens the
Generator V1 order gate, generates the annual writing rubric as REVIEW_REQUIRED,
and validates that draft so lesson-plan production can continue to T2 Writing P05.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

from artifact_generation import (
    ArtifactGenerationError,
    LIFECYCLE_REVIEW,
    PILOT_ARTIFACT_ID,
    build_generation_context,
    generate_to_directory,
    validate_generated_artifact,
)
from teacher_approval import apply_record, status as approval_status

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
DEFAULT_COURSE_ROOT = REPO_ROOT / "courses" / "TDE_9"
WRITING_RUBRIC_ID = "TDE9_YAZMA_RUBRIC"
EXPECTED_CURSOR = "BLOCK_T2_04_YAZMA_P05"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ArtifactGenerationError(f"REQUIRED_FILE_MISSING: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ArtifactGenerationError(f"JSON_ROOT_MUST_BE_OBJECT: {path}")
    return data


def require_current_approval(state: Dict[str, Any]) -> None:
    if state.get("approval_record") != "CURRENT":
        reason = state.get("error") or state.get("approval_record") or "UNKNOWN"
        raise ArtifactGenerationError(
            f"EXPLICIT_TEACHER_APPROVAL_REQUIRED: {PILOT_ARTIFACT_ID} ({reason})"
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
    approval = approval_status(course_root, PILOT_ARTIFACT_ID)
    return {
        "pipeline": "TDE9_POST_TEACHER_APPROVAL_RESUME",
        "lesson_cursor": cursor,
        "pilot_approval": approval,
        "ready": approval.get("approval_record") == "CURRENT",
        "next_artifact_when_ready": WRITING_RUBRIC_ID,
    }


def run(course_root: Path, output_root: Path) -> Dict[str, Any]:
    state = preflight(course_root)
    require_current_approval(state["pilot_approval"])

    pilot = apply_record(course_root, output_root, PILOT_ARTIFACT_ID)

    context, writing_rubric, changed = generate_to_directory(
        course_root, WRITING_RUBRIC_ID, output_root, enforce_order=True
    )
    validate_generated_artifact(writing_rubric, context)

    if writing_rubric.get("lifecycle_status") != LIFECYCLE_REVIEW:
        raise ArtifactGenerationError(
            f"WRITING_RUBRIC_UNEXPECTED_LIFECYCLE: {writing_rubric.get('lifecycle_status')}"
        )

    return {
        "pipeline": "TDE9_POST_TEACHER_APPROVAL_RESUME",
        "status": "READY_FOR_T2_WRITING_P05",
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
            "output_dir": str(output_root / WRITING_RUBRIC_ID),
        },
        "important_note": (
            "TDE9_YAZMA_RUBRIC generation/validation does not equal teacher approval; "
            "its lifecycle remains REVIEW_REQUIRED until separately reviewed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume TDE9 production after explicit pilot teacher approval")
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
        if args.command == "preflight" and not result.get("ready"):
            return 2
        return 0
    except ArtifactGenerationError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
