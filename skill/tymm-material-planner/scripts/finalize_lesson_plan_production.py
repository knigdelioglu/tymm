#!/usr/bin/env python3
"""Mark lesson-plan production complete only from a SHA/fingerprint-bound PASS report."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validation_binding  # noqa: E402


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git_head() -> str:
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip().lower()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("GIT_HEAD_UNAVAILABLE") from exc
    return validation_binding.resolve_commit_sha(value)


def verify_report(
    report_path: Path,
    roots: list[Path],
    schema_path: Path,
    expected_head: str,
) -> dict[str, Any]:
    raw = report_path.read_bytes()
    report = json.loads(raw.decode("utf-8"))
    if report.get("status") != "PASS":
        raise ValueError("VALIDATION_REPORT_NOT_PASS")

    summary = report.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("VALIDATION_REPORT_SUMMARY_MISSING")
    if summary.get("failure_records") != 0:
        raise ValueError("VALIDATION_REPORT_HAS_FAILURES")
    if summary.get("warning_records") != 0:
        raise ValueError("VALIDATION_REPORT_HAS_WARNINGS")

    courses = report.get("courses")
    if not isinstance(courses, list) or len(courses) != len(roots):
        raise ValueError("VALIDATION_REPORT_COURSE_COUNT_MISMATCH")
    requested_course_ids = [read_json(root / "planning/lesson_plan_production_plan.json").get("course_id") for root in roots]
    report_course_ids = [course.get("course_id") if isinstance(course, dict) else None for course in courses]
    if report_course_ids != requested_course_ids:
        raise ValueError(f"VALIDATION_REPORT_COURSE_MISMATCH:{report_course_ids}!={requested_course_ids}")
    if any(not isinstance(course, dict) or course.get("status") != "PASS" for course in courses):
        raise ValueError("VALIDATION_REPORT_COURSE_NOT_PASS")

    expected_head = validation_binding.resolve_commit_sha(expected_head)
    actual_head = git_head()
    if actual_head != expected_head:
        raise ValueError(f"CHECKOUT_HEAD_MISMATCH:{actual_head}!={expected_head}")

    required_keys = (
        "schema_version",
        "algorithm",
        "content_fingerprint",
        "fingerprinted_files",
        "commit_sha",
    )

    report_binding = report.get("binding")
    if not isinstance(report_binding, dict):
        raise ValueError("VALIDATION_BINDING_MISSING")
    if report_binding.get("commit_sha") != expected_head:
        raise ValueError(
            f"VALIDATION_COMMIT_MISMATCH:{report_binding.get('commit_sha')}!={expected_head}"
        )

    current_binding = validation_binding.build_validation_binding(
        roots,
        schema_path,
        commit_sha=expected_head,
    )
    for key in required_keys:
        if report_binding.get(key) != current_binding.get(key):
            raise ValueError(
                f"VALIDATION_BINDING_MISMATCH:{key}:{report_binding.get(key)}!={current_binding.get(key)}"
            )

    course_bindings: dict[str, dict[str, Any]] = {}
    for root, course in zip(roots, courses):
        course_id = read_json(root / "planning/lesson_plan_production_plan.json").get("course_id")
        report_course_binding = course.get("binding") if isinstance(course, dict) else None
        if not isinstance(report_course_binding, dict):
            raise ValueError(f"COURSE_VALIDATION_BINDING_MISSING:{course_id}")
        current_course_binding = validation_binding.build_validation_binding(
            [root],
            schema_path,
            commit_sha=expected_head,
        )
        for key in required_keys:
            if report_course_binding.get(key) != current_course_binding.get(key):
                raise ValueError(
                    "COURSE_VALIDATION_BINDING_MISMATCH:"
                    f"{course_id}:{key}:{report_course_binding.get(key)}!={current_course_binding.get(key)}"
                )
        course_bindings[str(course_id)] = current_course_binding

    return {
        **current_binding,
        "report_sha256": f"sha256:{hashlib.sha256(raw).hexdigest()}",
        "course_bindings": course_bindings,
    }


def _write_validation_seal(
    root: Path,
    course_id: str,
    binding: dict[str, Any],
    course_binding: dict[str, Any],
    total_packages: int,
    expected_hours: int,
) -> Path:
    seal_path = root / "planning" / validation_binding.VALIDATION_SEAL_FILENAME
    validation_set_binding = {
        key: binding[key]
        for key in (
            "schema_version",
            "algorithm",
            "content_fingerprint",
            "fingerprinted_files",
            "commit_sha",
        )
    }
    write_json(
        seal_path,
        {
            "schema_version": "1.0.0",
            "seal_type": "LESSON_PLAN_COURSE_VALIDATION_SEAL",
            "course_id": course_id,
            "status": "PASS",
            "scope": "FULL_GENERATED_LESSON_PLAN_SET",
            "validated_packages": total_packages,
            "validated_instruction_hours": expected_hours,
            "failure_records": 0,
            "warning_records": 0,
            "validation_binding": course_binding,
            "validation_set_binding": validation_set_binding,
        },
    )
    return seal_path


def finalize(
    root: Path,
    binding: dict[str, Any],
    course_binding: dict[str, Any],
) -> dict[str, Any]:
    path = root / "planning/lesson_plan_production_plan.json"
    plan = read_json(path)
    progress = plan.get("progress", {})
    total_packages = progress.get("total_packages")
    completed_packages = progress.get("completed_packages")
    expected_hours = progress.get("core_instruction_hours")
    completed_hours = progress.get("completed_instruction_hours")

    if completed_packages != total_packages:
        raise ValueError(f"PACKAGE_COMPLETION_MISMATCH:{completed_packages}!={total_packages}")
    if completed_hours != expected_hours:
        raise ValueError(f"HOUR_COMPLETION_MISMATCH:{completed_hours}!={expected_hours}")
    if progress.get("next") is not None:
        raise ValueError("NEXT_PACKAGE_MUST_BE_NULL_BEFORE_FINALIZATION")
    last_completed = progress.get("last_completed")
    if not isinstance(last_completed, dict):
        raise ValueError("LAST_COMPLETED_MISSING")
    if not isinstance(total_packages, int) or not isinstance(expected_hours, int):
        raise ValueError("FINALIZATION_TOTALS_INVALID")

    course_id = str(plan.get("course_id") or "")
    if not course_id:
        raise ValueError("FINALIZATION_COURSE_ID_MISSING")

    plan["status"] = "COMPLETED"
    last_completed["validation_status"] = "PASS"
    plan["engineering_validation"] = {
        "status": "PASS",
        "scope": "FULL_GENERATED_LESSON_PLAN_SET",
        "validator": "skill/tymm-material-planner/scripts/validate_all_lesson_plans.py",
        "grounding_validator": "skill/tymm-material-planner/scripts/validate_lesson_plan.py",
        "schema": "skill/tymm-material-planner/schemas/lesson_plan.schema.json",
        "checks": [
            "JSON_SCHEMA_DRAFT_2020_12",
            "SOURCE_BOUND_GROUNDING",
            "NESTED_REFERENCE_GROUNDING",
            "CALENDAR_SCOPE",
            "DETERMINISTIC_JSON_MARKDOWN_PARITY",
            "PACKAGE_TOPOLOGY",
            "PACKAGE_COUNT",
            "LESSON_HOUR_TOTAL",
            "FRESH_RUNTIME_CONTEXT",
            "VALIDATION_REPORT_PASS",
            "VALIDATED_COMMIT_SHA",
            "VALIDATED_CONTENT_FINGERPRINT",
            "COURSE_SCOPED_CONTENT_FINGERPRINT",
        ],
        "validated_packages": total_packages,
        "validated_instruction_hours": expected_hours,
        "failure_records": 0,
        "warning_records": 0,
        "validation_binding": binding,
        "course_validation_binding": course_binding,
    }
    write_json(path, plan)
    seal_path = _write_validation_seal(
        root,
        course_id,
        binding,
        course_binding,
        total_packages,
        expected_hours,
    )
    return {
        "course_id": course_id,
        "status": plan.get("status"),
        "validated_packages": total_packages,
        "validated_instruction_hours": expected_hours,
        "validated_commit_sha": binding.get("commit_sha"),
        "content_fingerprint": binding.get("content_fingerprint"),
        "course_content_fingerprint": course_binding.get("content_fingerprint"),
        "validation_seal": seal_path.as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument(
        "--schema",
        default="skill/tymm-material-planner/schemas/lesson_plan.schema.json",
    )
    parser.add_argument("--validation-report", required=True)
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args()
    roots = [Path(root) for root in args.knowledge_root]
    try:
        verified = verify_report(
            Path(args.validation_report),
            roots,
            Path(args.schema),
            args.expected_head,
        )
        course_bindings = verified.pop("course_bindings")
        binding = verified
        results = []
        for root in roots:
            course_id = read_json(root / "planning/lesson_plan_production_plan.json").get("course_id")
            course_binding = course_bindings.get(str(course_id))
            if not isinstance(course_binding, dict):
                raise ValueError(f"COURSE_VALIDATION_BINDING_UNAVAILABLE:{course_id}")
            results.append(finalize(root, binding, course_binding))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    print(json.dumps({"status": "PASS", "binding": binding, "courses": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
