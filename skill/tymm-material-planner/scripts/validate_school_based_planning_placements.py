#!/usr/bin/env python3
"""Validate optional school-based planning placement contracts.

The placement layer is deliberately separate from the 172-hour core lesson-plan
queue. It may recommend where a teacher could spend the 2 school-based hours in
each theme, but it must never change canonical core hours or auto-select an
option.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class PlacementValidationError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fail(code: str, detail: str = "") -> None:
    suffix = f":{detail}" if detail else ""
    raise PlacementValidationError(f"{code}{suffix}")


def _require_nonempty(value: Any, code: str) -> None:
    if not isinstance(value, str) or not value.strip():
        _fail(code)


def validate_payloads(
    options: dict[str, Any],
    placements: dict[str, Any],
    production_plan: dict[str, Any],
) -> dict[str, Any]:
    course_id = production_plan.get("course_id")
    if options.get("course_id") != course_id or placements.get("course_id") != course_id:
        _fail("COURSE_ID_MISMATCH", str(course_id))

    progress = production_plan.get("progress", {})
    if progress.get("core_instruction_hours") != 172:
        _fail("CORE_ANNUAL_HOURS_MISMATCH", str(progress.get("core_instruction_hours")))
    if progress.get("school_based_planning_hours") != 8:
        _fail("SBP_ANNUAL_HOURS_MISMATCH", str(progress.get("school_based_planning_hours")))
    if progress.get("queued_instruction_hours") != 172:
        _fail("SBP_MUST_NOT_ENTER_DEFAULT_QUEUE", str(progress.get("queued_instruction_hours")))

    policy = placements.get("policy", {})
    expected_policy = {
        "calendar_neutral": True,
        "placement_is_recommendation": True,
        "teacher_selection_required": True,
        "core_instruction_hours_immutable": 172,
        "school_based_planning_hours_annual": 8,
        "core_instruction_hours_per_theme": 43,
        "school_based_planning_hours_per_theme": 2,
        "official_total_hours_per_theme": 45,
        "max_selected_hours_per_theme": 2,
        "default_queue_includes_school_based_hours": False,
    }
    for key, expected in expected_policy.items():
        if policy.get(key) != expected:
            _fail("PLACEMENT_POLICY_MISMATCH", f"{key}={policy.get(key)!r},expected={expected!r}")

    plan_themes: dict[str, dict[str, Any]] = {}
    package_ids: dict[tuple[str, str], set[str]] = {}
    for theme in production_plan.get("themes", []):
        theme_id = theme.get("theme_id")
        if theme.get("core_instruction_hours") != 43:
            _fail("THEME_CORE_HOURS_MISMATCH", str(theme_id))
        if theme.get("school_based_planning_hours") != 2:
            _fail("THEME_SBP_HOURS_MISMATCH", str(theme_id))
        if theme.get("school_based_planning_in_default_queue") is not False:
            _fail("THEME_SBP_DEFAULT_QUEUE_MUST_BE_FALSE", str(theme_id))
        plan_themes[theme_id] = theme
        for block in theme.get("blocks", []):
            block_id = block.get("block_id")
            count = block.get("package_count")
            if not isinstance(count, int) or count < 1:
                _fail("INVALID_PACKAGE_COUNT", f"{theme_id}/{block_id}")
            package_ids[(theme_id, block_id)] = {
                f"{block_id}_P{number:02d}" for number in range(1, count + 1)
            }

    if set(plan_themes) != {"TEMA_01", "TEMA_02", "TEMA_03", "TEMA_04"}:
        _fail("THEME_SET_MISMATCH", repr(sorted(plan_themes)))

    option_index: dict[str, tuple[str, int]] = {}
    theme_option_hours: dict[str, int] = {theme_id: 0 for theme_id in plan_themes}
    for theme in options.get("themes", []):
        theme_id = theme.get("theme_id")
        if theme_id not in plan_themes:
            _fail("OPTION_THEME_UNKNOWN", str(theme_id))
        for option in theme.get("options", []):
            option_id = option.get("option_id")
            duration = option.get("duration_hours")
            if not isinstance(option_id, str) or not option_id:
                _fail("OPTION_ID_MISSING", str(theme_id))
            if option_id in option_index:
                _fail("DUPLICATE_OPTION_ID", option_id)
            if not isinstance(duration, int) or duration < 1 or duration > 2:
                _fail("OPTION_DURATION_OUT_OF_RANGE", f"{option_id}={duration!r}")
            if option.get("theme_id") != theme_id:
                _fail("OPTION_THEME_MISMATCH", option_id)
            option_index[option_id] = (theme_id, duration)
            theme_option_hours[theme_id] += duration

    for theme_id, available_hours in theme_option_hours.items():
        if available_hours < 2:
            _fail("INSUFFICIENT_SBP_OPTION_CAPACITY", f"{theme_id}={available_hours}")

    placement_index: dict[str, dict[str, Any]] = {}
    for entry in placements.get("placements", []):
        option_id = entry.get("option_id")
        if option_id in placement_index:
            _fail("DUPLICATE_PLACEMENT", str(option_id))
        placement_index[option_id] = entry

    missing = sorted(set(option_index) - set(placement_index))
    extra = sorted(set(placement_index) - set(option_index))
    if missing:
        _fail("PLACEMENT_MISSING_FOR_OPTION", ",".join(missing))
    if extra:
        _fail("PLACEMENT_WITHOUT_OPTION", ",".join(extra))

    for option_id, entry in placement_index.items():
        expected_theme, expected_duration = option_index[option_id]
        if entry.get("theme_id") != expected_theme:
            _fail("PLACEMENT_THEME_MISMATCH", option_id)
        if entry.get("duration_hours") != expected_duration:
            _fail("PLACEMENT_DURATION_MISMATCH", option_id)
        _require_nonempty(entry.get("identified_need"), f"IDENTIFIED_NEED_MISSING:{option_id}")
        _require_nonempty(entry.get("activation_condition"), f"ACTIVATION_CONDITION_MISSING:{option_id}")

        point = entry.get("recommended_insertion_point")
        if not isinstance(point, dict):
            _fail("INSERTION_POINT_MISSING", option_id)
        block_id = point.get("target_block_id")
        if point.get("relation") != "AFTER_PACKAGE":
            _fail("UNSUPPORTED_PLACEMENT_RELATION", option_id)
        if (expected_theme, block_id) not in package_ids:
            _fail("PLACEMENT_BLOCK_UNKNOWN", f"{option_id}:{block_id}")
        anchor = point.get("anchor_package_id")
        if anchor not in package_ids[(expected_theme, block_id)]:
            _fail("PLACEMENT_ANCHOR_UNKNOWN", f"{option_id}:{anchor}")

        impact = entry.get("impact_evaluation")
        if not isinstance(impact, dict):
            _fail("IMPACT_EVALUATION_MISSING", option_id)
        _require_nonempty(impact.get("method"), f"IMPACT_METHOD_MISSING:{option_id}")
        _require_nonempty(impact.get("success_indicator"), f"IMPACT_INDICATOR_MISSING:{option_id}")

    return {
        "course_id": course_id,
        "status": "PASS",
        "themes": 4,
        "options": len(option_index),
        "placements": len(placement_index),
        "core_instruction_hours": 172,
        "school_based_planning_hours": 8,
        "official_total_hours": 180,
    }


def validate_course(root: Path) -> dict[str, Any]:
    return validate_payloads(
        read_json(root / "production/school_based_planning_options.json"),
        read_json(root / "production/school_based_planning_placements.json"),
        read_json(root / "planning/lesson_plan_production_plan.json"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    args = parser.parse_args()
    try:
        results = [validate_course(Path(root)) for root in args.knowledge_root]
    except (OSError, json.JSONDecodeError, PlacementValidationError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    print(json.dumps({"status": "PASS", "courses": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
