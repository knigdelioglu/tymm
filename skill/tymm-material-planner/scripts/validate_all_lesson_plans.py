#!/usr/bin/env python3
"""Validate all generated TYMM lesson plans for schema, grounding, display projection, parity and package completeness."""
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
import lesson_plan_evidence_quality  # noqa: E402
import teacher_facing_text  # noqa: E402
import validate_lesson_plan  # noqa: E402
import validate_lesson_plan_markdown  # noqa: E402
import validation_binding  # noqa: E402


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path) or "$"
    return f"{location}: {error.message}"


def validate_course(root: Path, schema_validator: Draft202012Validator) -> dict[str, Any]:
    root = root.resolve()
    plan_meta_path = root / "planning/lesson_plan_production_plan.json"
    production = read_json(plan_meta_path)
    generated_root = root / "generated/lesson_plans"
    json_files = sorted(generated_root.glob("**/*.json"))
    markdown_files = sorted(generated_root.glob("**/*.md"))

    expected_packages = production.get("progress", {}).get("total_packages")
    expected_hours = production.get("progress", {}).get("core_instruction_hours")
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    total_hours = 0

    teacher_catalog = teacher_facing_text.TeacherReferenceCatalog.from_knowledge_root(root)
    package_range_cache: dict[str, dict[int, teacher_facing_text.PackageRange]] = {}

    json_stems = {path.with_suffix("").relative_to(generated_root).as_posix() for path in json_files}
    markdown_stems = {path.with_suffix("").relative_to(generated_root).as_posix() for path in markdown_files}
    for orphan in sorted(markdown_stems - json_stems):
        failures.append(
            {
                "path": (generated_root / (orphan + ".md")).relative_to(root).as_posix(),
                "stage": "markdown_parity",
                "errors": ["ORPHAN_MARKDOWN_WITHOUT_JSON"],
            }
        )

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

        # Canonical source prose may retain audit-oriented package references.
        # Teacher-facing consumers must resolve those references to actual prior
        # assessment evidence before technical-ID humanization/rendering.
        try:
            ranges = package_range_cache.get(block_id)
            if ranges is None:
                ranges = teacher_facing_text.package_ranges_for_block(plan_path.parent)
                package_range_cache[block_id] = ranges
            evidence_projection = lesson_plan_evidence_quality.project_specific_assessment_evidence(
                plan,
                plan_path=plan_path,
            )
            teacher_projection = teacher_facing_text.normalize_teacher_facing_text(
                evidence_projection,
                catalog=teacher_catalog,
                package_ranges=ranges,
            )
            projection_errors = teacher_facing_text.teacher_facing_validation_errors(
                teacher_projection
            )
            projection_errors += lesson_plan_evidence_quality.vague_evidence_errors(
                teacher_projection
            )
            if projection_errors:
                failures.append(
                    {
                        "path": relative,
                        "stage": "teacher_facing_projection",
                        "errors": projection_errors,
                    }
                )
        except (
            OSError,
            json.JSONDecodeError,
            lesson_plan_evidence_quality.EvidenceResolutionError,
            teacher_facing_text.TeacherFacingTextError,
        ) as exc:
            failures.append(
                {
                    "path": relative,
                    "stage": "teacher_facing_projection",
                    "errors": [str(exc)],
                }
            )

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

        parity = validate_lesson_plan_markdown.validate_pair(plan_path)
        if parity.get("status") != "PASS":
            failures.append(
                {
                    "path": relative,
                    "stage": "markdown_parity",
                    "errors": parity.get("errors", []),
                }
            )

    count_ok = len(json_files) == expected_packages
    hours_ok = total_hours == expected_hours
    markdown_count_ok = len(markdown_files) == expected_packages
    if not count_ok:
        failures.append(
            {
                "path": plan_meta_path.relative_to(root).as_posix(),
                "stage": "course_totals",
                "errors": [f"PACKAGE_COUNT_MISMATCH:{len(json_files)}!={expected_packages}"],
            }
        )
    if not markdown_count_ok:
        failures.append(
            {
                "path": plan_meta_path.relative_to(root).as_posix(),
                "stage": "course_totals",
                "errors": [f"MARKDOWN_PACKAGE_COUNT_MISMATCH:{len(markdown_files)}!={expected_packages}"],
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
        "markdown_package_count": len(markdown_files),
        "expected_package_count": expected_packages,
        "lesson_hours": total_hours,
        "expected_lesson_hours": expected_hours,
        "teacher_facing_projection": "PASS" if not any(
            failure.get("stage") == "teacher_facing_projection" for failure in failures
        ) else "FAIL",
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
    parser.add_argument("--commit-sha")
    args = parser.parse_args()

    schema_path = Path(args.schema)
    schema = read_json(schema_path)
    schema_validator = Draft202012Validator(schema)
    knowledge_roots = [Path(root) for root in args.knowledge_root]
    reports = [validate_course(root, schema_validator) for root in knowledge_roots]
    for root, report in zip(knowledge_roots, reports):
        report["binding"] = validation_binding.build_validation_binding(
            [root],
            schema_path,
            commit_sha=args.commit_sha,
        )
    payload = {
        "status": "PASS" if all(report["status"] == "PASS" for report in reports) else "FAIL",
        "binding": validation_binding.build_validation_binding(
            knowledge_roots,
            schema_path,
            commit_sha=args.commit_sha,
        ),
        "courses": reports,
        "summary": {
            "courses": len(reports),
            "packages": sum(report["package_count"] for report in reports),
            "markdown_packages": sum(report["markdown_package_count"] for report in reports),
            "lesson_hours": sum(report["lesson_hours"] for report in reports),
            "teacher_facing_projection_pass": all(
                report["teacher_facing_projection"] == "PASS" for report in reports
            ),
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
