#!/usr/bin/env python3
"""Persist and re-apply explicit teacher approvals for generated assessment artifacts.

Human approval is bound to the exact review surface the teacher saw plus the exact
canonical source files and generator implementation that define the artifact. The
runtime still rebuilds and validates the generation context before applying approval;
tracked source identities make the approval independently auditable in Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict

from artifact_generation import (
    ArtifactGenerationError,
    approve_artifact,
    build_generation_context,
    generate_to_directory,
)

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
DEFAULT_COURSE_ROOT = REPO_ROOT / "courses" / "TDE_9"
APPROVAL_SCHEMA_VERSION = "1.3"
APPROVAL_DIRNAME = "teacher_approvals"
GENERATOR_SOURCE_PATH = SCRIPT_DIR / "artifact_generation.py"
SOURCE_IDENTITY_PATHS = {
    "production_manifest": Path("production/production_manifest.json"),
    "assessment_artifact_registry": Path("production/assessment_artifact_registry.json"),
    "assessment_design_contract": Path("production/assessment_design_contract.json"),
}


def approval_path(course_root: Path, artifact_id: str) -> Path:
    return course_root / "production" / APPROVAL_DIRNAME / f"{artifact_id}.json"


def review_snapshot_path(course_root: Path, artifact_id: str) -> Path:
    return course_root / "generated" / artifact_id / "REVIEW.md"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ArtifactGenerationError(f"TEACHER_APPROVAL_RECORD_MISSING: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ArtifactGenerationError(f"TEACHER_APPROVAL_RECORD_ROOT_MUST_BE_OBJECT: {path}")
    return data


def _git_blob_sha(path: Path) -> str:
    if not path.exists():
        raise ArtifactGenerationError(f"APPROVAL_IDENTITY_FILE_MISSING: {path}")
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def _current_approval_identity(course_root: Path, artifact_id: str) -> Dict[str, Any]:
    review_path = review_snapshot_path(course_root, artifact_id)
    if not review_path.exists():
        raise ArtifactGenerationError(
            f"TEACHER_REVIEW_SNAPSHOT_MISSING: generate and inspect REVIEW.md before approving {artifact_id}"
        )

    source_shas = {
        key: _git_blob_sha(course_root / relative)
        for key, relative in SOURCE_IDENTITY_PATHS.items()
    }
    return {
        "review_snapshot_git_blob_sha": _git_blob_sha(review_path),
        "generator_source_git_blob_sha": _git_blob_sha(GENERATOR_SOURCE_PATH),
        "canonical_source_git_blob_shas": source_shas,
    }


def build_record(course_root: Path, artifact_id: str, reviewer: str, note: str = "") -> Dict[str, Any]:
    reviewer = reviewer.strip()
    if not reviewer:
        raise ArtifactGenerationError("TEACHER_APPROVAL_REVIEWER_REQUIRED")

    # This is deliberately executed before recording approval. It verifies that the
    # current sources still resolve to a valid, fresh canonical generation context.
    build_generation_context(course_root, artifact_id)
    identity = _current_approval_identity(course_root, artifact_id)
    return {
        "schema_version": APPROVAL_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "review_snapshot_git_blob_sha": identity["review_snapshot_git_blob_sha"],
        "generator_source_git_blob_sha": identity["generator_source_git_blob_sha"],
        "canonical_source_git_blob_shas": identity["canonical_source_git_blob_shas"],
        "approved": True,
        "reviewer": reviewer,
        "review_note": note.strip() or None,
        "approval_kind": "EXPLICIT_TEACHER_APPROVAL",
        "reproducibility_rule": (
            "Approval is valid only while the reviewed REVIEW.md snapshot, artifact_generation.py, "
            "production_manifest.json, assessment_artifact_registry.json, and "
            "assessment_design_contract.json retain the recorded Git-blob identities."
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

    identity = _current_approval_identity(course_root, artifact_id)
    if record.get("review_snapshot_git_blob_sha") != identity["review_snapshot_git_blob_sha"]:
        raise ArtifactGenerationError("TEACHER_APPROVAL_REVIEW_SNAPSHOT_STALE")
    if record.get("generator_source_git_blob_sha") != identity["generator_source_git_blob_sha"]:
        raise ArtifactGenerationError("TEACHER_APPROVAL_GENERATOR_SOURCE_STALE")
    if record.get("canonical_source_git_blob_shas") != identity["canonical_source_git_blob_shas"]:
        raise ArtifactGenerationError("TEACHER_APPROVAL_CANONICAL_SOURCE_STALE")

    # Source hashes above are the persisted identity; context construction below is
    # the runtime semantic gate (registry/production consistency + fresh index).
    build_generation_context(course_root, artifact_id)
    return record


def apply_record(course_root: Path, output_root: Path, artifact_id: str) -> Dict[str, Any]:
    record = validate_record(course_root, artifact_id)

    # Recreate and validate the canonical machine artifact only after the exact
    # reviewed snapshot and canonical source identities have matched.
    generate_to_directory(course_root, artifact_id, output_root)
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
            "review_snapshot_git_blob_sha": record.get("review_snapshot_git_blob_sha"),
            "generator_source_git_blob_sha": record.get("generator_source_git_blob_sha"),
            "canonical_source_git_blob_shas": record.get("canonical_source_git_blob_shas"),
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
