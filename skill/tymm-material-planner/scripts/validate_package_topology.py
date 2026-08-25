#!/usr/bin/env python3
"""Validate committed P8 lesson-package topology manifests fail-closed."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
BUILDER_PATH = SCRIPT_DIR / "build_package_topology_manifest.py"
_spec = importlib.util.spec_from_file_location("build_package_topology_manifest", BUILDER_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Cannot import topology builder: {BUILDER_PATH}")
_builder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_builder)
build_manifest = _builder.build_manifest


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def error(errors: list[str], code: str, detail: Any | None = None) -> None:
    errors.append(code if detail is None else f"{code}:{detail}")


def _validate_range(
    errors: list[str],
    *,
    prefix: str,
    hour_range: Any,
    expected_start: int,
    expected_hours: int,
) -> None:
    if not isinstance(hour_range, dict):
        error(errors, prefix + "RANGE_NOT_OBJECT")
        return
    start = hour_range.get("start")
    end = hour_range.get("end")
    if start != expected_start:
        error(errors, prefix + "RANGE_START_MISMATCH", f"{start}!={expected_start}")
    expected_end = expected_start + expected_hours - 1
    if end != expected_end:
        error(errors, prefix + "RANGE_END_MISMATCH", f"{end}!={expected_end}")


def validate_manifest_payload(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if actual.get("schema_version") != expected.get("schema_version"):
        error(errors, "TOPOLOGY_SCHEMA_VERSION_MISMATCH", actual.get("schema_version"))
    if actual.get("course_id") != expected.get("course_id"):
        error(errors, "TOPOLOGY_COURSE_ID_MISMATCH", actual.get("course_id"))
    if actual.get("policy") != expected.get("policy"):
        error(errors, "TOPOLOGY_POLICY_MISMATCH")
    if actual.get("summary") != expected.get("summary"):
        error(errors, "TOPOLOGY_SUMMARY_MISMATCH", actual.get("summary"))

    expected_packages = expected.get("packages", [])
    actual_packages = actual.get("packages")
    if not isinstance(actual_packages, list):
        error(errors, "TOPOLOGY_PACKAGES_NOT_LIST")
        actual_packages = []

    expected_by_id = {
        item["package_id"]: item for item in expected_packages if isinstance(item, dict) and isinstance(item.get("package_id"), str)
    }
    actual_by_id: dict[str, dict[str, Any]] = {}
    for package in actual_packages:
        if not isinstance(package, dict):
            error(errors, "TOPOLOGY_PACKAGE_NOT_OBJECT")
            continue
        package_id = package.get("package_id")
        if not isinstance(package_id, str) or not package_id:
            error(errors, "TOPOLOGY_PACKAGE_ID_INVALID", package_id)
            continue
        if package_id in actual_by_id:
            error(errors, "TOPOLOGY_PACKAGE_ID_DUPLICATE", package_id)
            continue
        actual_by_id[package_id] = package

    if set(actual_by_id) != set(expected_by_id):
        error(
            errors,
            "TOPOLOGY_PACKAGE_SET_MISMATCH",
            {
                "missing": sorted(set(expected_by_id) - set(actual_by_id)),
                "extra": sorted(set(actual_by_id) - set(expected_by_id)),
            },
        )

    course_cursor = 1
    theme_cursor_by_id: dict[str, int] = {}
    block_cursor_by_id: dict[str, int] = {}
    expected_order = [item["package_id"] for item in expected_packages]
    actual_order = [item.get("package_id") for item in actual_packages if isinstance(item, dict)]
    if actual_order != expected_order:
        error(errors, "TOPOLOGY_PACKAGE_ORDER_MISMATCH")

    for ordinal, expected_package in enumerate(expected_packages, start=1):
        package_id = expected_package["package_id"]
        actual_package = actual_by_id.get(package_id)
        if actual_package is None:
            continue
        prefix = f"{package_id}:"
        for key in (
            "ordinal",
            "theme_id",
            "theme_sequence",
            "block_id",
            "block_sequence",
            "package_no",
            "path",
            "lesson_hours",
        ):
            if actual_package.get(key) != expected_package.get(key):
                error(errors, prefix + key.upper() + "_MISMATCH", actual_package.get(key))
        if actual_package.get("ordinal") != ordinal:
            error(errors, prefix + "ORDINAL_NOT_CONTIGUOUS", actual_package.get("ordinal"))

        hours = expected_package["lesson_hours"]
        theme_id = expected_package["theme_id"]
        block_id = expected_package["block_id"]
        theme_cursor = theme_cursor_by_id.setdefault(theme_id, 1)
        block_cursor = block_cursor_by_id.setdefault(block_id, 1)
        _validate_range(
            errors,
            prefix=prefix + "COURSE_",
            hour_range=actual_package.get("course_hour_range"),
            expected_start=course_cursor,
            expected_hours=hours,
        )
        _validate_range(
            errors,
            prefix=prefix + "THEME_",
            hour_range=actual_package.get("theme_hour_range"),
            expected_start=theme_cursor,
            expected_hours=hours,
        )
        _validate_range(
            errors,
            prefix=prefix + "BLOCK_",
            hour_range=actual_package.get("block_hour_range"),
            expected_start=block_cursor,
            expected_hours=hours,
        )
        course_cursor += hours
        theme_cursor_by_id[theme_id] = theme_cursor + hours
        block_cursor_by_id[block_id] = block_cursor + hours

    if course_cursor != 173:
        error(errors, "TOPOLOGY_COURSE_RANGE_NOT_172_HOURS", course_cursor - 1)
    for theme_id, cursor in sorted(theme_cursor_by_id.items()):
        if cursor != 44:
            error(errors, "TOPOLOGY_THEME_RANGE_NOT_43_HOURS", f"{theme_id}:{cursor - 1}")

    expected_themes = expected.get("themes", [])
    actual_themes = actual.get("themes")
    if not isinstance(actual_themes, list):
        error(errors, "TOPOLOGY_THEMES_NOT_LIST")
        actual_themes = []
    if actual_themes != expected_themes:
        error(errors, "TOPOLOGY_THEME_BLOCK_STRUCTURE_MISMATCH")

    if actual != expected and not errors:
        error(errors, "TOPOLOGY_MANIFEST_NON_DETERMINISTIC_DIFFERENCE")
    return errors


def validate_course(knowledge_root: Path) -> dict[str, Any]:
    manifest_path = knowledge_root / "production" / "lesson_package_topology.json"
    if not manifest_path.exists():
        return {
            "status": "FAIL",
            "course_id": knowledge_root.name,
            "errors": ["TOPOLOGY_MANIFEST_MISSING"],
            "packages": 0,
            "core_instruction_hours": 0,
        }
    try:
        expected = build_manifest(knowledge_root)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "status": "FAIL",
            "course_id": knowledge_root.name,
            "errors": [f"TOPOLOGY_SOURCE_INVALID:{exc}"],
            "packages": 0,
            "core_instruction_hours": 0,
        }
    actual = read_json(manifest_path)
    errors = validate_manifest_payload(expected, actual)
    return {
        "status": "PASS" if not errors else "FAIL",
        "course_id": knowledge_root.name,
        "errors": errors,
        "packages": expected["summary"]["packages"],
        "core_instruction_hours": expected["summary"]["core_instruction_hours"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    args = parser.parse_args()
    courses = [validate_course(Path(root)) for root in args.knowledge_root]
    status = "PASS" if all(item["status"] == "PASS" for item in courses) else "FAIL"
    payload = {
        "status": status,
        "courses": courses,
        "summary": {
            "courses": len(courses),
            "packages": sum(item["packages"] for item in courses),
            "core_instruction_hours": sum(item["core_instruction_hours"] for item in courses),
            "errors": sum(len(item["errors"]) for item in courses),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
