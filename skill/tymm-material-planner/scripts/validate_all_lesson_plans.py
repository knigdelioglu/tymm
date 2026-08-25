#!/usr/bin/env python3
"""Validate all generated TYMM lesson plans for schema, grounding and package completeness."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - CI dependency gate
    raise SystemExit("jsonschema is required: pip install jsonschema==4.23.0") from exc

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import lesson_plan_context  # noqa: E402
import validate_lesson_plan  # noqa: E402


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path) or "$"
    return f"{location}: {error.message}"


def validate_course(root: Path, schema_validator: Draft202012Validator) -> dict[str, Any]:
    plan_meta_path = root / "planning/lesson_plan_production_plan.json"
    production = read_json(plan_meta_path)
    generated_root = root / "generated/lesson_plans"
    json_files = sorted(generated_root.glob("**/*.json"))

    expected_packages = production.get("progress", {}).get("total_packages")
    expected_hours = production.get("progress", {}).get("core_instruction_hours")
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    total_hours = 0

    for plan_path in json_files:
        relative = plan_path.relative_to(root).as_posix()
        try:
            plan = read_json(plan_path)
        except (OSError, json.JSONDecodeError) as exc:
            failures.append({"path": relative, "stage": "json", "errors": [str(exc)]})
            continue

        total_hours += plan.get("lesson_hours", 0) if isinstance(plan.get("lesson_hours"), int) else 0

        schema_errors = sorted(schema_validator.iter_errors(plan), key=lambda e: list(e.absolute_path))
        if schema_errors:
            failures.append(
                {
                    "path": relative,
                    "stage": "schema",
                    "errors": [format_schema_error(error) for error in schema_errors],
                }
            )

        block_id = plan.get("block_id")
        lesson_hours = plan.get("lesson_hours")
        if not isinstance(block_id, str) or not isinstance(lesson_hours, int):
            failures.append(
                {
                    "path": relative,
                    "stage": "context",
                    "errors": ["block_id and lesson_hours must be available before context assembly"],
                }
            )
            continue

        try:
            context = lesson_plan_context.assemble(root, block_id, lesson_hours)
            grounding = validate_lesson_plan.validate(context, plan)
        except Exception as exc:  # fail closed: runtime/context/compiler errors are validation failures
            failures.append({"path": relative, "stage": "context", "errors": [str(exc)]})
            continue

        if grounding.get("status") != "PASS":
            failures.append(
                {
                    "path": relative,
                    "stage": "grounding",
                    "errors": grounding.get("errors", []),
                }
            )
        if grounding.get("warnings"):
            warnings.append(
                {
                    "path": relative,
                    "warnings": grounding.get("warnings", []),
                }
            )

        markdown_path = plan_path.with_suffix(".md")
        if not markdown_path.exists():
            failures.append(
                {
                    "path": relative,
                    "stage": "paired_markdown",
                    "errors": [f"missing {markdown_path.relative_to(root).as_posix()}"],
                }
            )

    count_ok = len(json_files) == expected_packages
    hours_ok = total_hours == expected_hours
    if not count_ok:
        failures.append(
            {
                "path": plan_meta_path.relative_to(root).as_posix(),
                "stage": "course_totals",
                "errors": [f"PACKAGE_COUNT_MISMATCH:{len(json_files)}!={expected_packages}"],
            }
        )
    if not hours_ok:
        failures.append(
            {
                "path": plan_meta_path.relative_to(root).as_posix(),
                "stage": "course_totals",
                "errors": [f"LESSON_HOUR_TOTAL_MISMATCH:{total_hours}!={expected_hours}"],
            }
        )

    return {
        "course_id": production.get("course_id"),
        "status": "PASS" if not failures else "FAIL",
        "package_count": len(json_files),
        "expected_package_count": expected_packages,
        "lesson_hours": total_hours,
        "expected_lesson_hours": expected_hours,
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument(
        "--schema",
        default="skill/tymm-material-planner/schemas/lesson_plan.schema.json",
    )
    parser.add_argument("--report")
    args = parser.parse_args()

    schema = read_json(Path(args.schema))
    schema_validator = Draft202012Validator(schema)
    reports = [validate_course(Path(root), schema_validator) for root in args.knowledge_root]
    payload = {
        "status": "PASS" if all(report["status"] == "PASS" for report in reports) else "FAIL",
        "courses": reports,
        "summary": {
            "courses": len(reports),
            "packages": sum(report["package_count"] for report in reports),
            "lesson_hours": sum(report["lesson_hours"] for report in reports),
            "failure_records": sum(len(report["failures"]) for report in reports),
            "warning_records": sum(len(report["warnings"]) for report in reports),
        },
    }

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
