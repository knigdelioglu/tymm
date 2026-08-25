#!/usr/bin/env python3
"""Build the P8 exact lesson-package topology manifest.

The manifest is calendar-neutral and covers only the 172 core instruction hours.
It cross-checks canonical block order, block-hour bindings, production package
partitioning, and the committed generated JSON packages before writing output.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
EXPECTED_THEMES = 4
EXPECTED_BLOCKS = 16
EXPECTED_PACKAGES = 88
EXPECTED_CORE_HOURS = 172
EXPECTED_THEME_CORE_HOURS = 43


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fail(code: str, detail: Any | None = None) -> None:
    suffix = "" if detail is None else f":{detail}"
    raise ValueError(f"{code}{suffix}")


def _range(start: int, hours: int) -> dict[str, int]:
    if hours <= 0:
        _fail("NON_POSITIVE_HOUR_RANGE", hours)
    return {"start": start, "end": start + hours - 1}


def _expected_partition(hours: int) -> list[int]:
    if hours <= 0:
        _fail("BLOCK_HOURS_INVALID", hours)
    return [2] * (hours // 2) + ([1] if hours % 2 else [])


def _generated_json_paths(knowledge_root: Path) -> set[str]:
    generated = knowledge_root / "generated" / "lesson_plans"
    if not generated.is_dir():
        _fail("GENERATED_LESSON_PLAN_DIR_MISSING", generated)
    return {path.relative_to(knowledge_root).as_posix() for path in generated.rglob("*.json")}


def build_manifest(knowledge_root: Path) -> dict[str, Any]:
    course_id = knowledge_root.name
    production_plan_path = knowledge_root / "planning" / "lesson_plan_production_plan.json"
    bindings_path = knowledge_root / "planning" / "block_hour_bindings.json"
    teaching_blocks_path = knowledge_root / "production" / "teaching_blocks.json"

    for path, code in (
        (production_plan_path, "PRODUCTION_PLAN_MISSING"),
        (bindings_path, "BLOCK_HOUR_BINDINGS_MISSING"),
        (teaching_blocks_path, "TEACHING_BLOCKS_MISSING"),
    ):
        if not path.exists():
            _fail(code, path)

    production_plan = read_json(production_plan_path)
    bindings = read_json(bindings_path)
    teaching_blocks = read_json(teaching_blocks_path)

    if production_plan.get("course_id") != course_id:
        _fail("PRODUCTION_PLAN_COURSE_MISMATCH", production_plan.get("course_id"))
    if bindings.get("course_id") != course_id:
        _fail("BLOCK_BINDINGS_COURSE_MISMATCH", bindings.get("course_id"))
    if teaching_blocks.get("course_id") != course_id:
        _fail("TEACHING_BLOCKS_COURSE_MISMATCH", teaching_blocks.get("course_id"))

    policy = production_plan.get("production_policy")
    if not isinstance(policy, dict):
        _fail("PRODUCTION_POLICY_MISSING")
    if policy.get("default_package_hours") != 2:
        _fail("PACKAGE_POLICY_NOT_TWO_HOURS", policy.get("default_package_hours"))
    if production_plan.get("calendar_policy", {}).get("calendar_neutral") is not True:
        _fail("PRODUCTION_PLAN_NOT_CALENDAR_NEUTRAL")

    binding_themes = bindings.get("themes")
    plan_themes = production_plan.get("themes")
    block_rows = teaching_blocks.get("blocks")
    if not isinstance(binding_themes, list) or not isinstance(plan_themes, list) or not isinstance(block_rows, list):
        _fail("TOPOLOGY_SOURCE_LIST_MISSING")
    if len(binding_themes) != EXPECTED_THEMES or len(plan_themes) != EXPECTED_THEMES:
        _fail("THEME_COUNT_INVALID", {"bindings": len(binding_themes), "plan": len(plan_themes)})

    plan_theme_index = {item.get("theme_id"): item for item in plan_themes if isinstance(item, dict)}
    binding_theme_ids = [item.get("theme_id") for item in binding_themes if isinstance(item, dict)]
    plan_theme_ids = [item.get("theme_id") for item in plan_themes if isinstance(item, dict)]
    if binding_theme_ids != plan_theme_ids:
        _fail("THEME_ORDER_MISMATCH", {"bindings": binding_theme_ids, "plan": plan_theme_ids})

    teaching_by_theme: dict[str, list[dict[str, Any]]] = {}
    seen_blocks: set[str] = set()
    for block in block_rows:
        if not isinstance(block, dict):
            _fail("TEACHING_BLOCK_NOT_OBJECT")
        block_id = block.get("block_id")
        theme_id = block.get("theme_id")
        sequence = block.get("block_sequence")
        if not isinstance(block_id, str) or not block_id or block_id in seen_blocks:
            _fail("TEACHING_BLOCK_ID_INVALID_OR_DUPLICATE", block_id)
        if not isinstance(theme_id, str) or not theme_id:
            _fail("TEACHING_BLOCK_THEME_INVALID", block_id)
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence <= 0:
            _fail("TEACHING_BLOCK_SEQUENCE_INVALID", block_id)
        seen_blocks.add(block_id)
        teaching_by_theme.setdefault(theme_id, []).append(block)

    if len(seen_blocks) != EXPECTED_BLOCKS:
        _fail("TEACHING_BLOCK_COUNT_INVALID", len(seen_blocks))

    actual_paths = _generated_json_paths(knowledge_root)
    expected_paths: set[str] = set()
    packages: list[dict[str, Any]] = []
    themes_out: list[dict[str, Any]] = []
    course_cursor = 1
    package_ordinal = 1

    for theme_sequence, binding_theme in enumerate(binding_themes, start=1):
        if not isinstance(binding_theme, dict):
            _fail("BINDING_THEME_NOT_OBJECT")
        theme_id = binding_theme.get("theme_id")
        if not isinstance(theme_id, str) or theme_id not in plan_theme_index:
            _fail("BINDING_THEME_ID_INVALID", theme_id)
        if binding_theme.get("normative_total_hours") != EXPECTED_THEME_CORE_HOURS:
            _fail("THEME_CORE_HOURS_INVALID", {theme_id: binding_theme.get("normative_total_hours")})
        if binding_theme.get("school_based_planning_hours") != 2:
            _fail("THEME_SCHOOL_BASED_HOURS_INVALID", {theme_id: binding_theme.get("school_based_planning_hours")})

        plan_theme = plan_theme_index[theme_id]
        if plan_theme.get("core_instruction_hours") != EXPECTED_THEME_CORE_HOURS:
            _fail("PLAN_THEME_CORE_HOURS_INVALID", {theme_id: plan_theme.get("core_instruction_hours")})
        if plan_theme.get("school_based_planning_in_default_queue") is not False:
            _fail("SCHOOL_BASED_HOURS_LEAK_INTO_CORE_QUEUE", theme_id)

        binding_blocks = binding_theme.get("bindings")
        plan_blocks = plan_theme.get("blocks")
        canonical_blocks = sorted(teaching_by_theme.get(theme_id, []), key=lambda item: item["block_sequence"])
        if not isinstance(binding_blocks, list) or not isinstance(plan_blocks, list):
            _fail("THEME_BLOCK_LIST_MISSING", theme_id)
        canonical_ids = [item["block_id"] for item in canonical_blocks]
        binding_ids = [item.get("block_id") for item in binding_blocks if isinstance(item, dict)]
        plan_ids = [item.get("block_id") for item in plan_blocks if isinstance(item, dict)]
        if canonical_ids != binding_ids or canonical_ids != plan_ids:
            _fail(
                "BLOCK_ORDER_MISMATCH",
                {"theme_id": theme_id, "canonical": canonical_ids, "bindings": binding_ids, "plan": plan_ids},
            )
        if [item["block_sequence"] for item in canonical_blocks] != list(range(1, len(canonical_blocks) + 1)):
            _fail("BLOCK_SEQUENCE_NOT_CONTIGUOUS", theme_id)

        theme_start = course_cursor
        theme_cursor = 1
        blocks_out: list[dict[str, Any]] = []

        for block_position, (canonical, binding, plan_block) in enumerate(
            zip(canonical_blocks, binding_blocks, plan_blocks), start=1
        ):
            block_id = canonical["block_id"]
            if not isinstance(binding, dict) or not isinstance(plan_block, dict):
                _fail("BLOCK_SOURCE_NOT_OBJECT", block_id)
            planned_hours = binding.get("planned_hours")
            if not isinstance(planned_hours, int) or isinstance(planned_hours, bool) or planned_hours <= 0:
                _fail("BLOCK_PLANNED_HOURS_INVALID", block_id)
            if plan_block.get("planned_hours") != planned_hours:
                _fail("PLAN_BINDING_BLOCK_HOURS_MISMATCH", block_id)
            if plan_block.get("domain") != binding.get("domain"):
                _fail("PLAN_BINDING_BLOCK_DOMAIN_MISMATCH", block_id)

            package_hours = plan_block.get("package_hours")
            if not isinstance(package_hours, list) or any(
                not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in package_hours
            ):
                _fail("PACKAGE_HOURS_INVALID", block_id)
            expected_partition = _expected_partition(planned_hours)
            if package_hours != expected_partition:
                _fail(
                    "PACKAGE_PARTITION_MISMATCH",
                    {"block_id": block_id, "expected": expected_partition, "actual": package_hours},
                )
            if plan_block.get("package_count") != len(package_hours):
                _fail("PACKAGE_COUNT_FIELD_MISMATCH", block_id)
            if sum(package_hours) != planned_hours:
                _fail("PACKAGE_HOURS_DO_NOT_SUM_TO_BLOCK", block_id)

            rule = plan_block.get("package_id_rule")
            if not isinstance(rule, str) or "{package_no" not in rule:
                _fail("PACKAGE_ID_RULE_INVALID", block_id)

            block_course_start = course_cursor
            block_theme_start = theme_cursor
            block_cursor = 1
            block_package_ids: list[str] = []

            for package_no, hours in enumerate(package_hours, start=1):
                try:
                    package_id = rule.format(package_no=package_no)
                except (KeyError, ValueError) as exc:
                    _fail("PACKAGE_ID_RULE_FORMAT_ERROR", f"{block_id}:{exc}")
                expected_id = f"{block_id}_P{package_no:02d}"
                if package_id != expected_id:
                    _fail("PACKAGE_ID_RULE_NON_CANONICAL", {"expected": expected_id, "actual": package_id})
                relative_path = f"generated/lesson_plans/{theme_id}/{block_id}/{package_id}.json"
                expected_paths.add(relative_path)
                block_package_ids.append(package_id)

                absolute_path = knowledge_root / relative_path
                if not absolute_path.exists():
                    _fail("EXPECTED_PACKAGE_MISSING", relative_path)
                plan = read_json(absolute_path)
                if plan.get("course_id") != course_id:
                    _fail("PACKAGE_COURSE_ID_MISMATCH", package_id)
                if plan.get("theme_id") != theme_id:
                    _fail("PACKAGE_THEME_ID_MISMATCH", package_id)
                if plan.get("block_id") != block_id:
                    _fail("PACKAGE_BLOCK_ID_MISMATCH", package_id)
                if plan.get("lesson_hours") != hours:
                    _fail(
                        "PACKAGE_LESSON_HOURS_MISMATCH",
                        {"package_id": package_id, "expected": hours, "actual": plan.get("lesson_hours")},
                    )
                lessons = plan.get("lessons")
                if not isinstance(lessons, list) or not lessons:
                    _fail("PACKAGE_LESSONS_MISSING", package_id)
                duration_sum = sum(
                    lesson.get("duration_lesson_hours", 0) for lesson in lessons if isinstance(lesson, dict)
                )
                if duration_sum != hours:
                    _fail(
                        "PACKAGE_INTERNAL_DURATION_MISMATCH",
                        {"package_id": package_id, "expected": hours, "actual": duration_sum},
                    )

                packages.append(
                    {
                        "ordinal": package_ordinal,
                        "theme_id": theme_id,
                        "theme_sequence": theme_sequence,
                        "block_id": block_id,
                        "block_sequence": block_position,
                        "package_no": package_no,
                        "package_id": package_id,
                        "path": relative_path,
                        "lesson_hours": hours,
                        "course_hour_range": _range(course_cursor, hours),
                        "theme_hour_range": _range(theme_cursor, hours),
                        "block_hour_range": _range(block_cursor, hours),
                    }
                )
                package_ordinal += 1
                course_cursor += hours
                theme_cursor += hours
                block_cursor += hours

            if block_cursor != planned_hours + 1:
                _fail("BLOCK_CURSOR_END_MISMATCH", block_id)
            blocks_out.append(
                {
                    "block_id": block_id,
                    "block_sequence": block_position,
                    "domain": binding.get("domain"),
                    "planned_hours": planned_hours,
                    "package_count": len(package_hours),
                    "package_ids": block_package_ids,
                    "course_hour_range": _range(block_course_start, planned_hours),
                    "theme_hour_range": _range(block_theme_start, planned_hours),
                }
            )

        if theme_cursor != EXPECTED_THEME_CORE_HOURS + 1:
            _fail("THEME_CURSOR_END_MISMATCH", theme_id)
        themes_out.append(
            {
                "theme_id": theme_id,
                "theme_sequence": theme_sequence,
                "core_instruction_hours": EXPECTED_THEME_CORE_HOURS,
                "school_based_planning_hours_excluded": 2,
                "course_hour_range": _range(theme_start, EXPECTED_THEME_CORE_HOURS),
                "theme_hour_range": {"start": 1, "end": EXPECTED_THEME_CORE_HOURS},
                "blocks": blocks_out,
            }
        )

    if actual_paths != expected_paths:
        _fail(
            "GENERATED_PACKAGE_SET_MISMATCH",
            {"missing": sorted(expected_paths - actual_paths), "extra": sorted(actual_paths - expected_paths)},
        )
    if len(packages) != EXPECTED_PACKAGES:
        _fail("PACKAGE_TOTAL_INVALID", len(packages))
    if course_cursor != EXPECTED_CORE_HOURS + 1:
        _fail("COURSE_CURSOR_END_MISMATCH", course_cursor)

    progress = production_plan.get("progress", {})
    for key, expected in (
        ("core_instruction_hours", EXPECTED_CORE_HOURS),
        ("queued_instruction_hours", EXPECTED_CORE_HOURS),
        ("total_packages", EXPECTED_PACKAGES),
        ("completed_packages", EXPECTED_PACKAGES),
        ("completed_instruction_hours", EXPECTED_CORE_HOURS),
    ):
        if progress.get(key) != expected:
            _fail("PRODUCTION_PROGRESS_MISMATCH", {key: progress.get(key), "expected": expected})

    return {
        "schema_version": SCHEMA_VERSION,
        "course_id": course_id,
        "policy": {
            "calendar_neutral": True,
            "interval_semantics": "ONE_BASED_INCLUSIVE",
            "core_instruction_hours_only": True,
            "school_based_planning_hours_excluded": True,
            "default_package_hours": 2,
            "odd_block_remainder_hours": 1,
            "source_contract": {
                "block_order": "production/teaching_blocks.json:block_sequence",
                "block_hours": "planning/block_hour_bindings.json:planned_hours",
                "package_partition": "planning/lesson_plan_production_plan.json:package_hours",
                "actual_packages": "generated/lesson_plans/**/*.json",
            },
        },
        "summary": {
            "themes": EXPECTED_THEMES,
            "blocks": EXPECTED_BLOCKS,
            "packages": EXPECTED_PACKAGES,
            "core_instruction_hours": EXPECTED_CORE_HOURS,
            "theme_core_instruction_hours": EXPECTED_THEME_CORE_HOURS,
            "gaps": 0,
            "overlaps": 0,
        },
        "themes": themes_out,
        "packages": packages,
    }


def apply(knowledge_root: Path, *, write: bool) -> dict[str, Any]:
    manifest = build_manifest(knowledge_root)
    manifest_path = knowledge_root / "production" / "lesson_package_topology.json"
    existing = read_json(manifest_path) if manifest_path.exists() else None
    changed = existing != manifest
    if write and changed:
        write_json(manifest_path, manifest)
    return {
        "status": "PASS",
        "course_id": knowledge_root.name,
        "packages": manifest["summary"]["packages"],
        "core_instruction_hours": manifest["summary"]["core_instruction_hours"],
        "manifest_changed": changed,
        "manifest_path": manifest_path.as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        results = [apply(Path(root), write=args.write) for root in args.knowledge_root]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    print(json.dumps({"status": "PASS", "courses": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
