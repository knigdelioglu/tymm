#!/usr/bin/env python3
"""CLI for TYMM Artifact Generation Engine V1."""
import argparse
import json
import os
from pathlib import Path

from artifact_generation import (
    ArtifactGenerationError,
    approve_artifact,
    build_generation_context,
    freeze_artifact,
    generate_to_directory,
    load_current_artifact,
    validate_generated_artifact,
)

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
DEFAULT_COURSE_ROOT = REPO_ROOT / "courses" / "TDE_9"


def main() -> int:
    parser = argparse.ArgumentParser(description="TYMM Artifact Generation Engine V1")
    parser.add_argument("--course-root")
    parser.add_argument("--output-root")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("context", "generate", "validate", "freeze"):
        p = sub.add_parser(name)
        p.add_argument("--artifact-id", required=True)
        if name == "generate":
            p.add_argument("--no-order-gate", action="store_true")
    p = sub.add_parser("approve")
    p.add_argument("--artifact-id", required=True)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--note", default="")
    args = parser.parse_args()

    course_root = Path(args.course_root or os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_COURSE_ROOT)).resolve()
    output_root = Path(args.output_root).resolve() if args.output_root else course_root / "generated"
    try:
        if args.command == "context":
            print(json.dumps(build_generation_context(course_root, args.artifact_id), ensure_ascii=False, indent=2))
        elif args.command == "generate":
            context, artifact, changed = generate_to_directory(
                course_root, args.artifact_id, output_root, enforce_order=not args.no_order_gate
            )
            print(json.dumps({
                "artifact_id": args.artifact_id,
                "changed": changed,
                "revision": artifact.get("artifact_revision"),
                "context_hash": context.get("context_hash"),
                "lifecycle_status": artifact.get("lifecycle_status"),
                "output_dir": str(output_root / args.artifact_id),
            }, ensure_ascii=False, indent=2))
        elif args.command == "validate":
            context = build_generation_context(course_root, args.artifact_id)
            artifact = load_current_artifact(output_root, args.artifact_id)
            if artifact is None:
                raise ArtifactGenerationError(f"GENERATED_ARTIFACT_MISSING: {args.artifact_id}")
            validate_generated_artifact(artifact, context)
            print(json.dumps({"artifact_id": args.artifact_id, "validation": "PASS"}, ensure_ascii=False, indent=2))
        elif args.command == "approve":
            artifact = approve_artifact(course_root, args.artifact_id, output_root, args.reviewer, args.note)
            print(json.dumps({
                "artifact_id": args.artifact_id,
                "lifecycle_status": artifact.get("lifecycle_status"),
                "teacher_review_status": artifact.get("teacher_review_status"),
            }, ensure_ascii=False, indent=2))
        elif args.command == "freeze":
            artifact = freeze_artifact(course_root, args.artifact_id, output_root)
            print(json.dumps({
                "artifact_id": args.artifact_id,
                "lifecycle_status": artifact.get("lifecycle_status"),
            }, ensure_ascii=False, indent=2))
    except ArtifactGenerationError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
