#!/usr/bin/env python3
"""Persist and re-apply explicit teacher approvals for generated assessment artifacts.

Approval is bound to both the canonical generation context and the exact deterministic
pre-approval artifact content. If source knowledge, contracts, generator behavior, or
rendered rubric content changes, the record becomes stale and cannot be applied.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

from artifact_generation import (
    ArtifactGenerationError,
    approve_artifact,
    build_generation_context,
    generate_draft,
    generate_to_directory,
    stable_hash,
)

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
DEFAULT_COURSE_ROOT = REPO_ROOT / "courses" / "TDE_9"
APPROVAL_SCHEMA_VERSION = "1.1"
APPROVAL_DIRNAME = "teacher_approvals"


def approval_path(course_root: Path, artifact_id: str) -> Path:
    return course_root / "production" / APPROVAL_DIRNAME / f"{artifact_id}.json"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ArtifactGenerationError(f"TEACHER_APPROVAL_RECORD_MISSING: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ArtifactGenerationError(f"TEACHER_APPROVAL_RECORD_ROOT_MUST_BE_OBJECT: {path}")
    return data


def _current_draft_identity(course_root: Path, artifact_id: str) -> Dict[str, str]:
    context = build_generation_context(course_root, artifact_id)
    draft = generate_draft(context)
    return {
        "generation_context_hash": context["context_hash"],
        "artifact_content_hash": stable_hash(draft),
    }


def build_record(course_root: Path, artifact_id: str, reviewer: str, note: str = "") -> Dict[str, Any]:
    reviewer = reviewer.strip()
    if not reviewer:
        raise ArtifactGenerationError("TEACHER_APPROVAL_REVIEWER_REQUIRED")
    identity = _current_draft_identity(course_root, artifact_id)
    return {
        "schema_version": APPROVAL_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "generation_context_hash": identity["generation_context_hash"],
        "artifact_content_hash": identity["artifact_content_hash"],
        "approved": True,
        "reviewer": reviewer,
        "review_note": note.strip() or None,
        "approval_kind": "EXPLICIT_TEACHER_APPROVAL",
        "reproducibility_rule": (
            "Approval is valid only while both generation_context_hash and the deterministic "
            "pre-approval artifact_content_hash match the current canonical generator output."
        ),
    }


def write_record(course_root: Path, artifact_id: str, reviewer: str, note: str = "") -> Path:
    record = build_record(course_root, artifact_id, reviewer, note)
    path = approval_path(course_root, artifact_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def validate_record(course_root: Path, artifact_id: str) -> Dict[str, Any]:
    path = approval_path(course_root, artifact_id)
    record = _read_json(path)
    if record.get("schema_version") != APPROVAL_SCHEMA_VERSION:
        raise ArtifactGenerationError("TEACHER_APPROVAL_SCHEMA_VERSION_UNSUPPORTED")
    if record.get("artifact_id") != artifact_id:
        raise ArtifactGenerationError("TEACHER_APPROVAL_ARTIFACT_ID_MISMATCH")
    if record.get("approved") is not True:
        raise ArtifactGenerationError("TEACHER_APPROVAL_RECORD_NOT_APPROVED")
    if record.get("approval_kind") != "EXPLICIT_TEACHER_APPROVAL":
        raise ArtifactGenerationError("TEACHER_APPROVAL_KIND_INVALID")
    reviewer = str(record.get("reviewer") or "").strip()
    if not reviewer:
        raise ArtifactGenerationError("TEACHER_APPROVAL_REVIEWER_REQUIRED")

    identity = _current_draft_identity(course_root, artifact_id)
    if record.get("generation_context_hash") != identity["generation_context_hash"]:
        raise ArtifactGenerationError("TEACHER_APPROVAL_CONTEXT_STALE")
    if record.get("artifact_content_hash") != identity["artifact_content_hash"]:
        raise ArtifactGenerationError("TEACHER_APPROVAL_ARTIFACT_CONTENT_STALE")
    return record


def apply_record(course_root: Path, output_root: Path, artifact_id: str) -> Dict[str, Any]:
    record = validate_record(course_root, artifact_id)

    # Recreate the exact canonical draft in this checkout. Approval is applied only
    # after the persisted record has matched both context and deterministic content.
    context, draft, _ = generate_to_directory(course_root, artifact_id, output_root)
    if context.get("context_hash") != record.get("generation_context_hash"):
        raise ArtifactGenerationError("TEACHER_APPROVAL_CONTEXT_STALE")
    if stable_hash(draft) != record.get("artifact_content_hash"):
        raise ArtifactGenerationError("TEACHER_APPROVAL_ARTIFACT_CONTENT_STALE")

    artifact = approve_artifact(
        course_root,
        artifact_id,
        output_root,
        str(record["reviewer"]),
        str(record.get("review_note") or ""),
    )
    return artifact


def status(course_root: Path, artifact_id: str) -> Dict[str, Any]:
    path = approval_path(course_root, artifact_id)
    if not path.exists():
        return {
            "artifact_id": artifact_id,
            "approval_record": "MISSING",
            "path": str(path),
        }
    try:
        record = validate_record(course_root, artifact_id)
        return {
            "artifact_id": artifact_id,
            "approval_record": "CURRENT",
            "reviewer": record.get("reviewer"),
            "generation_context_hash": record.get("generation_context_hash"),
            "artifact_content_hash": record.get("artifact_content_hash"),
            "path": str(path),
        }
    except ArtifactGenerationError as exc:
        return {
            "artifact_id": artifact_id,
            "approval_record": "INVALID_OR_STALE",
            "error": str(exc),
            "path": str(path),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="TYMM explicit teacher approval persistence helper")
    parser.add_argument("--course-root")
    parser.add_argument("--output-root")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("status")
    p.add_argument("--artifact-id", required=True)

    p = sub.add_parser("record")
    p.add_argument("--artifact-id", required=True)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--note", default="")

    p = sub.add_parser("apply")
    p.add_argument("--artifact-id", required=True)

    args = parser.parse_args()
    course_root = Path(args.course_root or os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_COURSE_ROOT)).resolve()
    output_root = Path(args.output_root).resolve() if args.output_root else course_root / "generated"

    try:
        if args.command == "status":
            print(json.dumps(status(course_root, args.artifact_id), ensure_ascii=False, indent=2))
        elif args.command == "record":
            path = write_record(course_root, args.artifact_id, args.reviewer, args.note)
            print(json.dumps({
                "artifact_id": args.artifact_id,
                "approval_record": "CREATED",
                "path": str(path),
            }, ensure_ascii=False, indent=2))
        elif args.command == "apply":
            artifact = apply_record(course_root, output_root, args.artifact_id)
            print(json.dumps({
                "artifact_id": args.artifact_id,
                "lifecycle_status": artifact.get("lifecycle_status"),
                "teacher_review_status": artifact.get("teacher_review_status"),
            }, ensure_ascii=False, indent=2))
    except ArtifactGenerationError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
