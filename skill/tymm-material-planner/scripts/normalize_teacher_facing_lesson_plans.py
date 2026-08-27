#!/usr/bin/env python3
"""Normalize teacher-facing prose in generated TYMM lesson plans.

Structured canonical ID fields are preserved byte-for-value at the JSON model
level. Only prose fields intended for teachers are rewritten, using the
verified course metadata as the label source. Paired Markdown is regenerated
deterministically from the resulting authoritative JSON.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import render_lesson_plan_markdown
import teacher_facing_text


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def normalize_course(root: Path, *, write: bool) -> dict[str, Any]:
    root = root.resolve()
    generated = root / "generated/lesson_plans"
    catalog = teacher_facing_text.TeacherReferenceCatalog.from_knowledge_root(root)
    scanned = 0
    changed: list[str] = []
    failures: list[dict[str, Any]] = []

    for block_dir in sorted(path for path in generated.glob("*/*") if path.is_dir()):
        try:
            ranges = teacher_facing_text.package_ranges_for_block(block_dir)
        except (OSError, json.JSONDecodeError, teacher_facing_text.TeacherFacingTextError) as exc:
            failures.append({"path": block_dir.relative_to(root).as_posix(), "error": str(exc)})
            continue

        for json_path in sorted(block_dir.glob("*_P*.json")):
            scanned += 1
            relative = json_path.relative_to(root).as_posix()
            try:
                original = teacher_facing_text.read_json(json_path)
                normalized = teacher_facing_text.normalize_teacher_facing_text(
                    original,
                    catalog=catalog,
                    package_ranges=ranges,
                )
            except (OSError, json.JSONDecodeError, teacher_facing_text.TeacherFacingTextError) as exc:
                failures.append({"path": relative, "error": str(exc)})
                continue

            if normalized != original:
                changed.append(relative)
                if write:
                    _write_json(json_path, normalized)
                    json_path.with_suffix(".md").write_text(
                        render_lesson_plan_markdown.render(normalized),
                        encoding="utf-8",
                    )

    status = "PASS" if not failures and (write or not changed) else "FAIL"
    return {
        "course_id": root.name,
        "status": status,
        "scanned": scanned,
        "changed": len(changed),
        "changed_paths": changed,
        "failures": failures,
        "write": write,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    reports = [normalize_course(Path(root), write=args.write) for root in args.knowledge_root]
    payload = {
        "status": "PASS" if all(report["status"] == "PASS" for report in reports) else "FAIL",
        "courses": reports,
        "summary": {
            "courses": len(reports),
            "scanned": sum(report["scanned"] for report in reports),
            "changed": sum(report["changed"] for report in reports),
            "failures": sum(len(report["failures"]) for report in reports),
            "write": bool(args.write),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
