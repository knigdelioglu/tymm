#!/usr/bin/env python3
"""Validate an AI-generated lesson plan against a resolved TYMM lesson-plan context."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(context: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if context.get("resolution_status") != "RESOLVED":
        errors.append("CONTEXT_NOT_RESOLVED")
    expected_course = context.get("course", {}).get("course_id")
    expected_theme = context.get("theme", {}).get("theme_id")
    expected_block = context.get("block", {}).get("block_id")
    expected_hours = context.get("planning_request", {}).get("requested_lesson_hours")

    if plan.get("course_id") != expected_course:
        errors.append(f"COURSE_ID_MISMATCH:{plan.get('course_id')}!={expected_course}")
    if plan.get("theme_id") != expected_theme:
        errors.append(f"THEME_ID_MISMATCH:{plan.get('theme_id')}!={expected_theme}")
    if plan.get("block_id") != expected_block:
        errors.append(f"BLOCK_ID_MISMATCH:{plan.get('block_id')}!={expected_block}")
    if plan.get("lesson_hours") != expected_hours:
        errors.append(f"LESSON_HOURS_MISMATCH:{plan.get('lesson_hours')}!={expected_hours}")

    allowed = context.get("allowed_references", {})
    allowed_outcomes = set(allowed.get("outcome_codes", []))
    allowed_activities = set(allowed.get("activity_ids", []))
    allowed_forms = set(allowed.get("form_ids", []))

    outcome_codes = plan.get("outcome_codes", [])
    activity_ids = plan.get("used_activity_ids", [])
    form_ids = plan.get("used_form_ids", [])
    if not isinstance(outcome_codes, list):
        errors.append("OUTCOME_CODES_NOT_LIST")
        outcome_codes = []
    if not isinstance(activity_ids, list):
        errors.append("ACTIVITY_IDS_NOT_LIST")
        activity_ids = []
    if not isinstance(form_ids, list):
        errors.append("FORM_IDS_NOT_LIST")
        form_ids = []

    invented_outcomes = sorted(set(outcome_codes) - allowed_outcomes)
    invented_activities = sorted(set(activity_ids) - allowed_activities)
    invented_forms = sorted(set(form_ids) - allowed_forms)
    if invented_outcomes:
        errors.append(f"UNKNOWN_OUTCOME_CODES:{invented_outcomes}")
    if invented_activities:
        errors.append(f"UNKNOWN_ACTIVITY_IDS:{invented_activities}")
    if invented_forms:
        errors.append(f"UNKNOWN_FORM_IDS:{invented_forms}")

    lessons = plan.get("lessons", [])
    if not isinstance(lessons, list) or not lessons:
        errors.append("LESSONS_MISSING")
        lessons = []
    lesson_numbers: list[int] = []
    duration_total = 0
    for index, lesson in enumerate(lessons, 1):
        if not isinstance(lesson, dict):
            errors.append(f"LESSON_NOT_OBJECT:{index}")
            continue
        number = lesson.get("lesson_no")
        duration = lesson.get("duration_lesson_hours", 1)
        if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
            errors.append(f"LESSON_NUMBER_INVALID:{index}")
        else:
            lesson_numbers.append(number)
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            errors.append(f"LESSON_DURATION_INVALID:{index}")
        else:
            duration_total += duration
    if lesson_numbers and lesson_numbers != list(range(1, len(lesson_numbers) + 1)):
        errors.append(f"LESSON_SEQUENCE_INVALID:{lesson_numbers}")
    if expected_hours is not None and duration_total != expected_hours:
        errors.append(f"LESSON_DURATION_TOTAL_MISMATCH:{duration_total}!={expected_hours}")

    if not outcome_codes:
        warnings.append("NO_OUTCOME_CODE_REFERENCED")
    if context.get("textbook_activities") and not activity_ids:
        warnings.append("TEXTBOOK_ACTIVITIES_AVAILABLE_BUT_NONE_REFERENCED")

    forbidden_calendar_keys = {"date", "date_range", "week", "academic_year", "holiday", "ara_tatil"}
    found_calendar_keys: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if str(key).lower() in forbidden_calendar_keys:
                    found_calendar_keys.add(str(key))
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(plan)
    if found_calendar_keys:
        errors.append(f"CALENDAR_FIELDS_OUT_OF_SCOPE:{sorted(found_calendar_keys)}")

    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "validated_identity": {
            "course_id": expected_course,
            "theme_id": expected_theme,
            "block_id": expected_block,
            "lesson_hours": expected_hours,
        },
        "reference_counts": {
            "outcomes": len(set(outcome_codes)),
            "activities": len(set(activity_ids)),
            "forms": len(set(form_ids)),
            "lessons": len(lessons),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = validate(read_json(Path(args.context)), read_json(Path(args.plan)))
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
