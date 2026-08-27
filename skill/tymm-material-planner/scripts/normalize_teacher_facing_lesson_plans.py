#!/usr/bin/env python3
"""Normalize teacher-facing prose in generated TYMM lesson plans.

Structured canonical ID fields remain unchanged. Only prose intended for
teachers is rewritten from verified metadata, and paired Markdown is rendered
deterministically from the authoritative JSON.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import render_lesson_plan_markdown
import teacher_facing_text


def _write_json(path: Path, value: dict[str, Any]) -> None:
    source = path.read_text(encoding="utf-8")
    pretty = "\n" in source.rstrip("\n")
    if pretty:
        rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    else:
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
        ) + "\n"
    path.write_text(rendered, encoding="utf-8")


def _canonical_reference_snapshot(plan: dict[str, Any]) -> dict[str, Any]:
    lessons = plan.get("lessons")
    lesson_refs: list[dict[str, Any]] = []
    if isinstance(lessons, list):
        for lesson in lessons:
            if not isinstance(lesson, dict):
                continue
            lesson_refs.append(
                {
                    "lesson_no": lesson.get("lesson_no"),
                    "duration_lesson_hours": lesson.get("duration_lesson_hours"),
                    "assessment_scope": lesson.get("assessment_scope"),
                    "assessed_outcome_codes": lesson.get("assessed_outcome_codes"),
                    "outcome_codes": lesson.get("outcome_codes"),
                    "activity_ids": lesson.get("activity_ids"),
                    "form_ids": lesson.get("form_ids"),
                }
            )

    continuation = plan.get("continuation_summary")
    continuation_refs = None
    if isinstance(continuation, dict):
        continuation_refs = {
            "planned_now_hours": continuation.get("planned_now_hours"),
            "remaining_block_hours": continuation.get("remaining_block_hours"),
            "covered_outcome_codes": continuation.get("covered_outcome_codes"),
            "used_activity_ids": continuation.get("used_activity_ids"),
        }

    return {
        "schema_version": plan.get("schema_version"),
        "course_id": plan.get("course_id"),
        "theme_id": plan.get("theme_id"),
        "block_id": plan.get("block_id"),
        "lesson_hours": plan.get("lesson_hours"),
        "assessment_scope": plan.get("assessment_scope"),
        "assessed_outcome_codes": plan.get("assessed_outcome_codes"),
        "outcome_codes": plan.get("outcome_codes"),
        "used_activity_ids": plan.get("used_activity_ids"),
        "used_form_ids": plan.get("used_form_ids"),
        "lessons": lesson_refs,
        "continuation_summary": continuation_refs,
        "grounded_references": plan.get("grounded_references"),
    }


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
        except (
            OSError,
            json.JSONDecodeError,
            teacher_facing_text.TeacherFacingTextError,
        ) as exc:
            failures.append(
                {"path": block_dir.relative_to(root).as_posix(), "error": str(exc)}
            )
            continue

        for json_path in sorted(block_dir.glob("*_P*.json")):
            scanned += 1
            relative = json_path.relative_to(root).as_posix()
            try:
                original = teacher_facing_text.read_json(json_path)
                before_refs = _canonical_reference_snapshot(original)
                normalized = teacher_facing_text.normalize_teacher_facing_text(
                    original,
                    catalog=catalog,
                    package_ranges=ranges,
                )
                after_refs = _canonical_reference_snapshot(normalized)
                if before_refs != after_refs:
                    raise teacher_facing_text.TeacherFacingTextError(
                        "STRUCTURED_REFERENCE_DRIFT"
                    )
            except (
                OSError,
                json.JSONDecodeError,
                teacher_facing_text.TeacherFacingTextError,
            ) as exc:
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

    reports = [
        normalize_course(Path(root), write=args.write)
        for root in args.knowledge_root
    ]
    payload = {
        "status": "PASS"
        if all(report["status"] == "PASS" for report in reports)
        else "FAIL",
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
