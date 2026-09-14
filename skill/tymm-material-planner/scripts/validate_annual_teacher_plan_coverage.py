#!/usr/bin/env python3
"""Validate teacher-facing annual coverage without merging SBP into the core queue."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class AnnualTeacherPlanError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(code: str, detail: str = "") -> None:
    raise AnnualTeacherPlanError(f"{code}:{detail}" if detail else code)


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    plan = read_json(root / "planning/lesson_plan_production_plan.json")
    teacher = read_json(root / "planning/annual_teacher_plan.json")
    options = read_json(root / "production/school_based_planning_options.json")
    placements = read_json(root / "production/school_based_planning_placements.json")
    timeline = read_json(root / "planning/course_timeline.json")

    course_id = plan.get("course_id")
    if course_id != "TDE_11":
        fail("UNSUPPORTED_COURSE", str(course_id))
    for name, payload in (("annual_teacher_plan", teacher), ("options", options), ("placements", placements), ("timeline", timeline)):
        if payload.get("course_id") != course_id:
            fail("COURSE_ID_MISMATCH", name)

    progress = plan.get("progress", {})
    expected_progress = {
        "core_instruction_hours": 172,
        "school_based_planning_hours": 8,
        "queued_instruction_hours": 172,
        "total_packages": 88,
        "completed_packages": 88,
        "completed_instruction_hours": 172,
    }
    for key, expected in expected_progress.items():
        if progress.get(key) != expected:
            fail("CORE_PRODUCTION_ACCOUNTING_MISMATCH", f"{key}={progress.get(key)!r},expected={expected}")

    annual = teacher.get("annual_hours", {})
    expected_annual = {
        "core_instruction_hours": 172,
        "school_based_planning_capacity_hours": 8,
        "official_total_hours": 180,
    }
    for key, expected in expected_annual.items():
        if annual.get(key) != expected:
            fail("TEACHER_ANNUAL_HOURS_MISMATCH", f"{key}={annual.get(key)!r},expected={expected}")

    package_accounting = teacher.get("package_accounting", {})
    if package_accounting.get("core_packages") != 88:
        fail("TEACHER_CORE_PACKAGE_COUNT_MISMATCH", str(package_accounting.get("core_packages")))
    if package_accounting.get("core_packages_status") != "COMPLETED":
        fail("TEACHER_CORE_PACKAGE_STATUS_MISMATCH", str(package_accounting.get("core_packages_status")))
    if package_accounting.get("school_based_generated_packages") != 0:
        fail("SBP_MUST_NOT_BE_PREGENERATED", str(package_accounting.get("school_based_generated_packages")))
    if package_accounting.get("school_based_generation_status") != "NOT_REQUESTED":
        fail("SBP_GENERATION_STATUS_MISMATCH", str(package_accounting.get("school_based_generation_status")))

    policy = teacher.get("school_based_policy", {})
    expected_policy = {
        "teacher_selection_required": True,
        "max_selected_hours_per_theme": 2,
        "selection_mode": "ONE_2H_OR_TWO_1H",
        "default_selection": "NONE",
        "default_generation": False,
        "default_queue_includes_school_based_hours": False,
    }
    for key, expected in expected_policy.items():
        if policy.get(key) != expected:
            fail("TEACHER_SBP_POLICY_MISMATCH", f"{key}={policy.get(key)!r},expected={expected!r}")

    plan_themes = {theme.get("theme_id"): theme for theme in plan.get("themes", [])}
    option_themes = {theme.get("theme_id"): theme for theme in options.get("themes", [])}
    teacher_themes = {theme.get("theme_id"): theme for theme in teacher.get("themes", [])}
    timeline_themes = {theme.get("theme_id"): theme for theme in timeline.get("themes", [])}
    expected_theme_ids = {"TEMA_01", "TEMA_02", "TEMA_03", "TEMA_04"}
    for name, mapping in (("plan", plan_themes), ("options", option_themes), ("teacher", teacher_themes), ("timeline", timeline_themes)):
        if set(mapping) != expected_theme_ids:
            fail("THEME_SET_MISMATCH", f"{name}={sorted(mapping)}")

    option_ids_all: set[str] = set()
    candidate_hours = 0
    for theme_id in sorted(expected_theme_ids):
        plan_theme = plan_themes[theme_id]
        if plan_theme.get("core_instruction_hours") != 43 or plan_theme.get("school_based_planning_hours") != 2:
            fail("PLAN_THEME_HOUR_ENVELOPE_MISMATCH", theme_id)
        if plan_theme.get("school_based_planning_in_default_queue") is not False:
            fail("PLAN_THEME_SBP_DEFAULT_QUEUE_MUST_BE_FALSE", theme_id)
        core_packages = sum(int(block.get("package_count") or 0) for block in plan_theme.get("blocks", []))
        core_hours = sum(int(block.get("planned_hours") or 0) for block in plan_theme.get("blocks", []))
        if core_packages != 22 or core_hours != 43:
            fail("PLAN_THEME_CORE_ACCOUNTING_MISMATCH", f"{theme_id}:packages={core_packages},hours={core_hours}")

        option_theme = option_themes[theme_id]
        raw_options = option_theme.get("options", [])
        durations = sorted(option.get("duration_hours") for option in raw_options if isinstance(option, dict))
        if durations != [1, 1, 2]:
            fail("OPTION_THEME_SELECTION_SHAPE_MISMATCH", f"{theme_id}:{durations}")
        option_ids = []
        for option in raw_options:
            option_id = option.get("option_id")
            if not isinstance(option_id, str) or not option_id:
                fail("OPTION_ID_MISSING", theme_id)
            if option_id in option_ids_all:
                fail("DUPLICATE_OPTION_ID", option_id)
            option_ids_all.add(option_id)
            option_ids.append(option_id)
            candidate_hours += int(option.get("duration_hours") or 0)
            if option.get("selection_status") != "NOT_SELECTED":
                fail("OPTION_PRESELECTED", option_id)
            if option.get("generation_status") != "NOT_REQUESTED":
                fail("OPTION_PREGENERATED", option_id)
            if option.get("teacher_choice_required") is not True:
                fail("OPTION_TEACHER_CHOICE_NOT_REQUIRED", option_id)
            if option.get("is_curriculum_gap") is not False:
                fail("OPTION_MISCLASSIFIED_AS_GAP", option_id)

        teacher_theme = teacher_themes[theme_id]
        expected_theme_values = {
            "core_instruction_hours": 43,
            "core_packages": 22,
            "school_based_capacity_hours": 2,
            "official_total_hours": 45,
            "selection_status": "TEACHER_SELECTION_PENDING",
            "selected_hours": 0,
            "generated_school_based_packages": 0,
        }
        for key, expected in expected_theme_values.items():
            if teacher_theme.get(key) != expected:
                fail("TEACHER_THEME_ACCOUNTING_MISMATCH", f"{theme_id}:{key}={teacher_theme.get(key)!r},expected={expected!r}")
        if teacher_theme.get("option_ids") != option_ids:
            fail("TEACHER_THEME_OPTION_IDS_MISMATCH", theme_id)

        time_theme = timeline_themes[theme_id]
        if time_theme.get("core_instruction_hours") != 43:
            fail("TIMELINE_THEME_CORE_HOURS_MISMATCH", theme_id)
        if time_theme.get("school_based_hours") != 2:
            fail("TIMELINE_THEME_SBP_HOURS_MISMATCH", theme_id)
        if time_theme.get("official_total_hours") != 45:
            fail("TIMELINE_THEME_OFFICIAL_TOTAL_MISMATCH", f"{theme_id}:{time_theme.get('official_total_hours')}")
        if time_theme.get("outer_total_hours") != 45:
            fail("TIMELINE_THEME_OUTER_TOTAL_MISMATCH", theme_id)
        if sum(int(block.get("planned_hours") or 0) for block in time_theme.get("blocks", [])) != 43:
            fail("TIMELINE_THEME_BLOCK_HOURS_MISMATCH", theme_id)

    placement_ids = [entry.get("option_id") for entry in placements.get("placements", []) if isinstance(entry, dict)]
    if len(placement_ids) != 12 or set(placement_ids) != option_ids_all:
        fail("PLACEMENT_OPTION_COVERAGE_MISMATCH", f"placements={len(placement_ids)},options={len(option_ids_all)}")
    placement_policy = placements.get("policy", {})
    if placement_policy.get("default_queue_includes_school_based_hours") is not False:
        fail("PLACEMENT_DEFAULT_QUEUE_MUST_BE_FALSE")
    if placement_policy.get("max_selected_hours_per_theme") != 2:
        fail("PLACEMENT_MAX_SELECTED_HOURS_MISMATCH")

    timeline_annual = timeline.get("annual_hours", {})
    for key, expected in {
        "core_instruction_hours": 172,
        "school_based_hours": 8,
        "official_total_hours": 180,
    }.items():
        if timeline_annual.get(key) != expected:
            fail("TIMELINE_ANNUAL_HOURS_MISMATCH", f"{key}={timeline_annual.get(key)!r},expected={expected}")

    totals = teacher.get("totals_check", {})
    expected_totals = {
        "theme_count": 4,
        "core_package_count": 88,
        "core_instruction_hours": 172,
        "school_based_capacity_hours": 8,
        "official_total_hours": 180,
    }
    for key, expected in expected_totals.items():
        if totals.get(key) != expected:
            fail("TEACHER_TOTALS_CHECK_MISMATCH", f"{key}={totals.get(key)!r},expected={expected}")

    if len(option_ids_all) != 12 or candidate_hours != 16:
        fail("OPTION_POOL_TOTAL_MISMATCH", f"options={len(option_ids_all)},candidate_hours={candidate_hours}")

    return {
        "status": "PASS",
        "course_id": course_id,
        "core_packages": 88,
        "core_instruction_hours": 172,
        "school_based_candidate_options": 12,
        "school_based_candidate_hours": 16,
        "school_based_selectable_capacity_hours": 8,
        "school_based_generated_packages": 0,
        "official_annual_hours": 180,
        "theme_hours": {theme_id: {"core": 43, "school_based": 2, "official_total": 45} for theme_id in sorted(expected_theme_ids)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", required=True)
    args = parser.parse_args()
    try:
        result = validate(Path(args.knowledge_root))
    except (OSError, json.JSONDecodeError, AnnualTeacherPlanError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
