#!/usr/bin/env python3
"""Fail-closed deterministic parity validation for TYMM lesson-plan JSON/Markdown pairs."""
from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import render_lesson_plan_markdown  # noqa: E402


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def first_diff(expected: str, actual: str) -> str:
    diff = difflib.unified_diff(
        expected.splitlines(),
        actual.splitlines(),
        fromfile="expected-from-json",
        tofile="committed-markdown",
        lineterm="",
        n=2,
    )
    preview = []
    for line in diff:
        preview.append(line)
        if len(preview) >= 12:
            break
    return "\n".join(preview) or "content differs"


def validate_pair(json_path: Path) -> dict[str, Any]:
    md_path = json_path.with_suffix(".md")
    errors: list[str] = []
    try:
        plan = read_json(json_path)
        expected = render_lesson_plan_markdown.render(plan)
    except Exception as exc:
        return {"status": "FAIL", "errors": [f"MARKDOWN_RENDER_ERROR:{exc}"]}

    if not md_path.exists():
        return {"status": "FAIL", "errors": [f"MARKDOWN_MISSING:{md_path.name}"]}

    actual = md_path.read_text(encoding="utf-8")
    if actual != expected:
        errors.append("MARKDOWN_PARITY_MISMATCH\n" + first_diff(expected, actual))

    return {
        "status": "PASS" if not errors else "FAIL",
        "json_sha256": render_lesson_plan_markdown.canonical_digest(plan),
        "errors": errors,
    }


def validate_course(root: Path) -> dict[str, Any]:
    generated = root / "generated/lesson_plans"
    json_files = sorted(generated.glob("**/*.json"))
    md_files = sorted(generated.glob("**/*.md"))
    failures: list[dict[str, Any]] = []

    json_stems = {path.with_suffix("").relative_to(generated).as_posix() for path in json_files}
    md_stems = {path.with_suffix("").relative_to(generated).as_posix() for path in md_files}

    for orphan in sorted(md_stems - json_stems):
        failures.append({"path": orphan + ".md", "errors": ["ORPHAN_MARKDOWN_WITHOUT_JSON"]})

    for json_path in json_files:
        result = validate_pair(json_path)
        if result["status"] != "PASS":
            failures.append(
                {
                    "path": json_path.relative_to(root).as_posix(),
                    "errors": result["errors"],
                }
            )

    return {
        "course_id": root.name,
        "status": "PASS" if not failures else "FAIL",
        "json_packages": len(json_files),
        "markdown_packages": len(md_files),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()

    courses = [validate_course(Path(root)) for root in args.knowledge_root]
    payload = {
        "status": "PASS" if all(course["status"] == "PASS" for course in courses) else "FAIL",
        "courses": courses,
        "summary": {
            "courses": len(courses),
            "json_packages": sum(course["json_packages"] for course in courses),
            "markdown_packages": sum(course["markdown_packages"] for course in courses),
            "failure_records": sum(len(course["failures"]) for course in courses),
        },
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        report = Path(args.report)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
