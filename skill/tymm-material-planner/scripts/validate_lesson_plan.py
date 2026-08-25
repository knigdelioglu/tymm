#!/usr/bin/env python3
"""Validate an AI-generated lesson plan against a resolved TYMM lesson-plan context."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_string_list(value: Any, error_code: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(error_code)
        return []
    invalid = [item for item in value if not isinstance(item, str) or not item]
    if invalid:
        errors.append(f"{error_code}_ITEMS_INVALID")
        return [item for item in value if isinstance(item, str) and item]
    return value


def _check_allowed(
    values: list[str], allowed: set[str], prefix: str, errors: list[str]
) -> None:
    unknown = sorted(set(values) - allowed)
    if unknown:
        errors.append(f"{prefix}:{unknown}")


def _theme_assessment_activity_ids(context: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    markers = ("OLCME", "DEGERLENDIR", "GUNLUK", "YANSIT")
    for activity in context.get("textbook_activities", []):
        if not isinstance(activity, dict):
            continue
        activity_id = str(activity.get("activity_id") or "")
        title = str(activity.get("title") or "")
        signal = f"{activity_id} {title}".upper()
        theme_labeled = "TEMA" in signal and any(marker in signal for marker in markers)
        learning_diary = "OGRENME_GUNLUGU" in signal or "ÖĞRENME GÜNLÜĞÜ" in signal
        if theme_labeled or learning_diary:
            result.add(activity_id)
    return result


def _validate_assessment_scope(
    *,
    scope: Any,
    assessed_outcomes: list[str],
    block_outcomes: set[str],
    theme_outcomes: set[str],
    theme_signal: bool,
    prefix: str,
    errors: list[str],
) -> None:
    if scope is None:
        if assessed_outcomes:
            errors.append(f"{prefix}ASSESSMENT_SCOPE_REQUIRED")
        if theme_signal:
            errors.append(f"{prefix}THEME_ASSESSMENT_SCOPE_REQUIRED")
        return
    if scope not in {"BLOCK", "THEME"}:
        errors.append(f"{prefix}ASSESSMENT_SCOPE_INVALID:{scope}")
        return
    if not assessed_outcomes:
        errors.append(f"{prefix}ASSESSED_OUTCOME_CODES_REQUIRED")
        return

    allowed = theme_outcomes if scope == "THEME" else block_outcomes
    _check_allowed(assessed_outcomes, allowed, f"{prefix}UNKNOWN_ASSESSED_OUTCOME_CODES", errors)

    if theme_signal and scope != "THEME":
        errors.append(f"{prefix}THEME_ASSESSMENT_SCOPE_REQUIRED")
    if scope == "THEME":
        if not theme_signal:
            errors.append(f"{prefix}THEME_ASSESSMENT_WITHOUT_SOURCE_SIGNAL")
        if theme_outcomes - block_outcomes and not (set(assessed_outcomes) - block_outcomes):
            errors.append(f"{prefix}THEME_ASSESSMENT_OUTCOMES_TOO_NARROW")


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
    if plan.get("instruction_scope") not in (None, "BLOCK"):
        errors.append(f"INSTRUCTION_SCOPE_INVALID:{plan.get('instruction_scope')}")

    allowed = context.get("allowed_references", {})
    allowed_outcomes = set(allowed.get("outcome_codes", []))
    allowed_theme_outcomes = set(allowed.get("theme_outcome_codes", allowed.get("outcome_codes", [])))
    allowed_activities = set(allowed.get("activity_ids", []))
    allowed_forms = set(allowed.get("form_ids", []))
    theme_assessment_ids = _theme_assessment_activity_ids(context)

    outcome_codes = _as_string_list(plan.get("outcome_codes", []), "OUTCOME_CODES_NOT_LIST", errors)
    activity_ids = _as_string_list(plan.get("used_activity_ids", []), "ACTIVITY_IDS_NOT_LIST", errors)
    form_ids = _as_string_list(plan.get("used_form_ids", []), "FORM_IDS_NOT_LIST", errors)
    _check_allowed(outcome_codes, allowed_outcomes, "UNKNOWN_OUTCOME_CODES", errors)
    _check_allowed(activity_ids, allowed_activities, "UNKNOWN_ACTIVITY_IDS", errors)
    _check_allowed(form_ids, allowed_forms, "UNKNOWN_FORM_IDS", errors)

    assessed_outcomes: list[str] = []
    if "assessed_outcome_codes" in plan:
        assessed_outcomes = _as_string_list(
            plan.get("assessed_outcome_codes"), "ASSESSED_OUTCOME_CODES_NOT_LIST", errors
        )
    _validate_assessment_scope(
        scope=plan.get("assessment_scope"),
        assessed_outcomes=assessed_outcomes,
        block_outcomes=allowed_outcomes,
        theme_outcomes=allowed_theme_outcomes,
        theme_signal=bool(set(activity_ids) & theme_assessment_ids),
        prefix="",
        errors=errors,
    )

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
        if lesson.get("instruction_scope") not in (None, "BLOCK"):
            errors.append(f"LESSON_{index}_INSTRUCTION_SCOPE_INVALID:{lesson.get('instruction_scope')}")

        lesson_outcomes = _as_string_list(
            lesson.get("outcome_codes", []), f"LESSON_{index}_OUTCOME_CODES_NOT_LIST", errors
        )
        lesson_activities = _as_string_list(
            lesson.get("activity_ids", []), f"LESSON_{index}_ACTIVITY_IDS_NOT_LIST", errors
        )
        lesson_forms = _as_string_list(
            lesson.get("form_ids", []), f"LESSON_{index}_FORM_IDS_NOT_LIST", errors
        )
        _check_allowed(lesson_outcomes, allowed_outcomes, f"LESSON_{index}_UNKNOWN_OUTCOME_CODES", errors)
        _check_allowed(lesson_activities, allowed_activities, f"LESSON_{index}_UNKNOWN_ACTIVITY_IDS", errors)
        _check_allowed(lesson_forms, allowed_forms, f"LESSON_{index}_UNKNOWN_FORM_IDS", errors)

        lesson_assessed: list[str] = []
        if "assessed_outcome_codes" in lesson:
            lesson_assessed = _as_string_list(
                lesson.get("assessed_outcome_codes"),
                f"LESSON_{index}_ASSESSED_OUTCOME_CODES_NOT_LIST",
                errors,
            )
        _validate_assessment_scope(
            scope=lesson.get("assessment_scope"),
            assessed_outcomes=lesson_assessed,
            block_outcomes=allowed_outcomes,
            theme_outcomes=allowed_theme_outcomes,
            theme_signal=bool(set(lesson_activities) & theme_assessment_ids),
            prefix=f"LESSON_{index}_",
            errors=errors,
        )

    if lesson_numbers and lesson_numbers != list(range(1, len(lesson_numbers) + 1)):
        errors.append(f"LESSON_SEQUENCE_INVALID:{lesson_numbers}")
    if expected_hours is not None and duration_total != expected_hours:
        errors.append(f"LESSON_DURATION_TOTAL_MISMATCH:{duration_total}!={expected_hours}")

    continuation = plan.get("continuation_summary", {})
    if isinstance(continuation, dict):
        continuation_outcomes = _as_string_list(
            continuation.get("covered_outcome_codes", []), "CONTINUATION_OUTCOME_CODES_NOT_LIST", errors
        )
        continuation_activities = _as_string_list(
            continuation.get("used_activity_ids", []), "CONTINUATION_ACTIVITY_IDS_NOT_LIST", errors
        )
        _check_allowed(
            continuation_outcomes, allowed_outcomes, "CONTINUATION_UNKNOWN_OUTCOME_CODES", errors
        )
        _check_allowed(
            continuation_activities, allowed_activities, "CONTINUATION_UNKNOWN_ACTIVITY_IDS", errors
        )
        planned_now = continuation.get("planned_now_hours")
        if planned_now != plan.get("lesson_hours"):
            errors.append(
                f"CONTINUATION_PLANNED_HOURS_MISMATCH:{planned_now}!={plan.get('lesson_hours')}"
            )
    else:
        errors.append("CONTINUATION_SUMMARY_NOT_OBJECT")

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
            "assessed_outcomes": len(set(assessed_outcomes)),
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
