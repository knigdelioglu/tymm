#!/usr/bin/env python3
"""Deterministic binding helpers for lesson-plan validation and finalization."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Iterable

BINDING_SCHEMA_VERSION = "1.0.0"
FINGERPRINT_ALGORITHM = "TYMM_LESSON_PLAN_VALIDATION_SCOPE_V1"
VALIDATION_SEAL_FILENAME = "lesson_plan_validation_seal.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_commit_sha(explicit: str | None = None) -> str:
    candidate = explicit or os.environ.get("GITHUB_SHA")
    if candidate:
        candidate = candidate.strip()
        if len(candidate) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in candidate):
            raise ValueError(f"INVALID_COMMIT_SHA:{candidate}")
        return candidate.lower()
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("COMMIT_SHA_UNAVAILABLE") from exc
    if len(value) != 40:
        raise ValueError(f"INVALID_COMMIT_SHA:{value}")
    return value.lower()


def _normalized_production_plan_bytes(path: Path) -> bytes:
    payload = copy.deepcopy(read_json(path))
    payload.pop("status", None)
    payload.pop("engineering_validation", None)
    progress = payload.get("progress")
    if isinstance(progress, dict):
        last_completed = progress.get("last_completed")
        if isinstance(last_completed, dict):
            last_completed.pop("validation_status", None)
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _iter_course_entries(root: Path) -> Iterable[tuple[str, bytes]]:
    root = root.resolve()
    prefixes = [
        root / "generated/lesson_plans",
        root / "production",
        root / "themes",
    ]
    for base in prefixes:
        if not base.exists():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            yield path.relative_to(root).as_posix(), path.read_bytes()

    planning = root / "planning"
    if planning.exists():
        for path in sorted(p for p in planning.rglob("*") if p.is_file()):
            # Generated calendar output and the validation seal are derived
            # metadata. Including either would make validation self-referential.
            if path.name in {"course_timeline.json", VALIDATION_SEAL_FILENAME}:
                continue
            relative = path.relative_to(root).as_posix()
            if path.name == "lesson_plan_production_plan.json":
                yield relative, _normalized_production_plan_bytes(path)
            else:
                yield relative, path.read_bytes()

    for name in ("textbook_map.json", "textbook_forms_index.json"):
        path = root / name
        if path.exists():
            yield name, path.read_bytes()


def compute_content_binding(
    knowledge_roots: list[Path],
    schema_path: Path,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    # repo_root is retained for backward-compatible callers, but logical keys are
    # intentionally independent of the checkout's absolute filesystem path.
    del repo_root
    entries: list[tuple[str, bytes]] = []
    for root in knowledge_roots:
        logical_root = f"courses/{root.name}"
        entries.extend((f"{logical_root}/{relative}", data) for relative, data in _iter_course_entries(root))
    schema = schema_path.resolve()
    entries.append((f"skill/tymm-material-planner/schemas/{schema.name}", schema.read_bytes()))

    seen: set[str] = set()
    normalized: list[tuple[str, str]] = []
    for key, data in sorted(entries, key=lambda item: item[0]):
        if key in seen:
            raise ValueError(f"DUPLICATE_FINGERPRINT_ENTRY:{key}")
        seen.add(key)
        normalized.append((key, hashlib.sha256(data).hexdigest()))

    aggregate = hashlib.sha256()
    for key, digest in normalized:
        aggregate.update(key.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\n")

    return {
        "schema_version": BINDING_SCHEMA_VERSION,
        "algorithm": FINGERPRINT_ALGORITHM,
        "content_fingerprint": f"sha256:{aggregate.hexdigest()}",
        "fingerprinted_files": len(normalized),
    }


def build_validation_binding(
    knowledge_roots: list[Path],
    schema_path: Path,
    commit_sha: str | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    binding = compute_content_binding(knowledge_roots, schema_path, repo_root=repo_root)
    return {
        **binding,
        "commit_sha": resolve_commit_sha(commit_sha),
    }
