#!/usr/bin/env python3
"""Validate P5 theme-closure time budgets against generated lesson plans."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

NOMINAL_LESSON_MINUTES = 40


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_activity(activity_id: str) -> set[str]:
    signal = activity_id.upper()
    kinds: set[str] = set()
    is_theme = "TEMA" in signal
    if is_theme and ("OLCME" in signal or "TEST" in signal or "DEGERLENDIR" in signal):
        kinds.add("THEME_ASSESSMENT")
    if (is_theme and ("GUNLUK" in signal or "YANSIT" in signal)) or "OGRENME_GUNLUGU" in signal:
        kinds.add("REFLECTION")
    return kinds


def lesson_signals(lesson: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for activity_id in lesson.get("activity_ids", []):
        if isinstance(activity_id, str):
            result.update(classify_activity(activity_id))
    return result


def discover_closures(knowledge_root: Path) -> dict[str, dict[str, Any]]:
    discovered: dict[str, dict[str, Any]] = {}
    generated = knowledge_root / "generated" / "lesson_plans"
    for path in sorted(generated.rglob("*.json")):
        plan = read_json(path)
        if plan.get("assessment_scope") != "THEME":
            continue
        closure_lessons: dict[int, dict[str, Any]] = {}
        for lesson in plan.get("lessons", []):
            if not isinstance(lesson, dict) or lesson.get("assessment_scope") != "THEME":
                continue
            signals = lesson_signals(lesson)
            if not signals:
                continue
            lesson_no = lesson.get("lesson_no")
            if not isinstance(lesson_no, int) or isinstance(lesson_no, bool):
                continue
            closure_lessons[lesson_no] = {
                "signals": signals,
                "duration_lesson_hours": lesson.get("duration_lesson_hours", 1),
                "teacher_actions": lesson.get("teacher_actions", []),
            }
        if not closure_lessons:
            continue
        relative = path.relative_to(knowledge_root).as_posix()
        discovered[path.stem] = {
            "path": relative,
            "theme_id": plan.get("theme_id"),
            "block_id": plan.get("block_id"),
            "lessons": closure_lessons,
        }
    return discovered


def error(errors: list[str], code: str, detail: Any | None = None) -> None:
    errors.append(code if detail is None else f"{code}:{detail}")


def validate_course(knowledge_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    contract_path = knowledge_root / "production" / "closure_time_budgets.json"
    if not contract_path.exists():
        return {
            "status": "FAIL",
            "course_id": knowledge_root.name,
            "errors": ["CLOSURE_TIME_BUDGET_CONTRACT_MISSING"],
            "theme_closure_packages": 0,
        }

    contract = read_json(contract_path)
    discovered = discover_closures(knowledge_root)

    if contract.get("schema_version") != "1.0.0":
        error(errors, "CLOSURE_TIME_BUDGET_SCHEMA_VERSION_INVALID", contract.get("schema_version"))
    if contract.get("course_id") != knowledge_root.name:
        error(errors, "CLOSURE_TIME_BUDGET_COURSE_ID_MISMATCH", contract.get("course_id"))
    if contract.get("nominal_lesson_minutes") != NOMINAL_LESSON_MINUTES:
        error(errors, "NOMINAL_LESSON_MINUTES_MISMATCH", contract.get("nominal_lesson_minutes"))

    policy = contract.get("policy")
    if not isinstance(policy, dict):
        error(errors, "CLOSURE_TIME_BUDGET_POLICY_MISSING")
        policy = {}
    if policy.get("core_completion_independent_of_school_based_extension") is not True:
        error(errors, "CLOSURE_CORE_MUST_NOT_DEPEND_ON_SCHOOL_BASED_EXTENSION")
    if policy.get("school_based_extension_is_teacher_selected") is not True:
        error(errors, "SCHOOL_BASED_EXTENSION_MUST_BE_TEACHER_SELECTED")
    expected_split = {
        "theme_assessment": 25,
        "reflection": 10,
        "closure": 3,
        "buffer": 2,
    }
    if policy.get("mixed_closure_split_minutes") != expected_split:
        error(errors, "MIXED_CLOSURE_SPLIT_POLICY_MISMATCH", policy.get("mixed_closure_split_minutes"))
    if policy.get("single_focus_buffer_minutes") != 3:
        error(errors, "SINGLE_FOCUS_BUFFER_POLICY_MISMATCH", policy.get("single_focus_buffer_minutes"))

    packages = contract.get("packages")
    if not isinstance(packages, list):
        error(errors, "CLOSURE_PACKAGES_NOT_LIST")
        packages = []
    indexed: dict[str, dict[str, Any]] = {}
    for package in packages:
        if not isinstance(package, dict):
            error(errors, "CLOSURE_PACKAGE_NOT_OBJECT")
            continue
        package_id = package.get("package_id")
        if not isinstance(package_id, str) or not package_id:
            error(errors, "CLOSURE_PACKAGE_ID_INVALID")
            continue
        if package_id in indexed:
            error(errors, "CLOSURE_PACKAGE_ID_DUPLICATE", package_id)
            continue
        indexed[package_id] = package

    if set(indexed) != set(discovered):
        error(
            errors,
            "CLOSURE_PACKAGE_SET_MISMATCH",
            {
                "missing": sorted(set(discovered) - set(indexed)),
                "extra": sorted(set(indexed) - set(discovered)),
            },
        )
    if len(discovered) != 4:
        error(errors, "EXPECTED_FOUR_THEME_CLOSURES", len(discovered))

    for package_id, actual in discovered.items():
        package = indexed.get(package_id)
        if not package:
            continue
        prefix = f"{package_id}:"
        if package.get("path") != actual["path"]:
            error(errors, prefix + "PATH_MISMATCH", package.get("path"))
        if package.get("theme_id") != actual["theme_id"]:
            error(errors, prefix + "THEME_ID_MISMATCH", package.get("theme_id"))
        if package.get("block_id") != actual["block_id"]:
            error(errors, prefix + "BLOCK_ID_MISMATCH", package.get("block_id"))

        budgets = package.get("lesson_budgets")
        if not isinstance(budgets, list):
            error(errors, prefix + "LESSON_BUDGETS_NOT_LIST")
            continue
        budget_index: dict[int, dict[str, Any]] = {}
        for budget in budgets:
            if not isinstance(budget, dict):
                error(errors, prefix + "LESSON_BUDGET_NOT_OBJECT")
                continue
            lesson_no = budget.get("lesson_no")
            if not isinstance(lesson_no, int) or isinstance(lesson_no, bool) or lesson_no <= 0:
                error(errors, prefix + "LESSON_BUDGET_NUMBER_INVALID", lesson_no)
                continue
            if lesson_no in budget_index:
                error(errors, prefix + "LESSON_BUDGET_NUMBER_DUPLICATE", lesson_no)
                continue
            budget_index[lesson_no] = budget

        actual_lessons = actual["lessons"]
        if set(budget_index) != set(actual_lessons):
            error(
                errors,
                prefix + "LESSON_BUDGET_SET_MISMATCH",
                {
                    "missing": sorted(set(actual_lessons) - set(budget_index)),
                    "extra": sorted(set(budget_index) - set(actual_lessons)),
                },
            )

        for lesson_no, actual_lesson in actual_lessons.items():
            budget = budget_index.get(lesson_no)
            if not budget:
                continue
            lp = f"{package_id}:L{lesson_no}:"
            actual_signals = set(actual_lesson["signals"])
            declared_signals = budget.get("signals")
            if not isinstance(declared_signals, list) or set(declared_signals) != actual_signals:
                error(errors, lp + "SIGNALS_MISMATCH", declared_signals)

            required = budget.get("required_segments")
            if not isinstance(required, list) or not required:
                error(errors, lp + "REQUIRED_SEGMENTS_MISSING")
                required = []
            required_sum = 0
            by_kind: dict[str, int] = {}
            for segment in required:
                if not isinstance(segment, dict):
                    error(errors, lp + "REQUIRED_SEGMENT_NOT_OBJECT")
                    continue
                kind = segment.get("kind")
                minutes = segment.get("minutes")
                purpose = segment.get("purpose")
                if kind not in {"THEME_ASSESSMENT", "REFLECTION", "CLOSURE"}:
                    error(errors, lp + "REQUIRED_SEGMENT_KIND_INVALID", kind)
                if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes <= 0:
                    error(errors, lp + "REQUIRED_SEGMENT_MINUTES_INVALID", minutes)
                    continue
                if not isinstance(purpose, str) or not purpose.strip():
                    error(errors, lp + "REQUIRED_SEGMENT_PURPOSE_MISSING", kind)
                required_sum += minutes
                if isinstance(kind, str):
                    by_kind[kind] = by_kind.get(kind, 0) + minutes

            if budget.get("required_minutes_total") != required_sum:
                error(
                    errors,
                    lp + "REQUIRED_TOTAL_MISMATCH",
                    f"{budget.get('required_minutes_total')}!={required_sum}",
                )
            buffer_minutes = budget.get("buffer_minutes")
            if not isinstance(buffer_minutes, int) or isinstance(buffer_minutes, bool) or buffer_minutes < 2:
                error(errors, lp + "BUFFER_MINUTES_INVALID", buffer_minutes)
                buffer_minutes = 0
            duration = actual_lesson.get("duration_lesson_hours", 1)
            if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
                duration = 1
            period_capacity = NOMINAL_LESSON_MINUTES * duration
            if required_sum + buffer_minutes != period_capacity:
                error(
                    errors,
                    lp + "PERIOD_BUDGET_MISMATCH",
                    f"{required_sum}+{buffer_minutes}!={period_capacity}",
                )

            if "THEME_ASSESSMENT" in actual_signals and by_kind.get("THEME_ASSESSMENT", 0) < 20:
                error(errors, lp + "THEME_ASSESSMENT_TIME_TOO_SHORT", by_kind.get("THEME_ASSESSMENT", 0))
            if "REFLECTION" in actual_signals and by_kind.get("REFLECTION", 0) < 5:
                error(errors, lp + "REFLECTION_TIME_TOO_SHORT", by_kind.get("REFLECTION", 0))
            if actual_signals == {"THEME_ASSESSMENT", "REFLECTION"}:
                expected_minutes = {"THEME_ASSESSMENT": 25, "REFLECTION": 10, "CLOSURE": 3}
                if by_kind != expected_minutes or buffer_minutes != 2:
                    error(errors, lp + "MIXED_CLOSURE_REQUIRED_SPLIT_MISMATCH", {"segments": by_kind, "buffer": buffer_minutes})

            optional = budget.get("optional_extensions")
            if not isinstance(optional, list):
                error(errors, lp + "OPTIONAL_EXTENSIONS_NOT_LIST")
                optional = []
            optional_kinds: set[str] = set()
            for extension in optional:
                if not isinstance(extension, dict):
                    error(errors, lp + "OPTIONAL_EXTENSION_NOT_OBJECT")
                    continue
                kind = extension.get("kind")
                optional_kinds.add(str(kind))
                if extension.get("placement") != "SCHOOL_BASED_IF_SELECTED":
                    error(errors, lp + "OPTIONAL_EXTENSION_PLACEMENT_INVALID", extension.get("placement"))
                if extension.get("required_for_core_completion") is not False:
                    error(errors, lp + "OPTIONAL_EXTENSION_MUST_NOT_BE_REQUIRED", kind)
                minutes = extension.get("minutes")
                if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes <= 0:
                    error(errors, lp + "OPTIONAL_EXTENSION_MINUTES_INVALID", minutes)
                for key in ("activation_condition", "purpose"):
                    value = extension.get(key)
                    if not isinstance(value, str) or not value.strip():
                        error(errors, lp + f"OPTIONAL_EXTENSION_{key.upper()}_MISSING", kind)

            if actual_signals == {"THEME_ASSESSMENT", "REFLECTION"}:
                for required_optional in ("ANSWER_CORRECTION", "EXTENDED_REFLECTION"):
                    if required_optional not in optional_kinds:
                        error(errors, lp + "MIXED_CLOSURE_OPTIONAL_ROUTE_MISSING", required_optional)
                theme_id = str(actual["theme_id"])
                transition_kind = "YEAR_PORTFOLIO_REVIEW" if theme_id == "TEMA_04" else "NEXT_THEME_PREP"
                if transition_kind not in optional_kinds:
                    error(errors, lp + "MIXED_CLOSURE_TRANSITION_ROUTE_MISSING", transition_kind)

            actions = actual_lesson.get("teacher_actions")
            marker = actions[0] if isinstance(actions, list) and actions else ""
            if not isinstance(marker, str) or not marker.startswith("Süre bütçesi:"):
                error(errors, lp + "PLAN_TIME_BUDGET_MARKER_MISSING")
            if actual_signals == {"THEME_ASSESSMENT", "REFLECTION"}:
                if "25 dk" not in marker or "10 dk" not in marker or "çekirdek tamamlanma koşulu değildir" not in marker:
                    error(errors, lp + "PLAN_MIXED_BUDGET_MARKER_INCOMPLETE")

    return {
        "status": "PASS" if not errors else "FAIL",
        "course_id": knowledge_root.name,
        "errors": errors,
        "theme_closure_packages": len(discovered),
        "budgeted_lessons": sum(len(item["lessons"]) for item in discovered.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    args = parser.parse_args()
    try:
        courses = [validate_course(Path(root)) for root in args.knowledge_root]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    status = "PASS" if all(item["status"] == "PASS" for item in courses) else "FAIL"
    payload = {
        "status": status,
        "courses": courses,
        "summary": {
            "courses": len(courses),
            "theme_closure_packages": sum(item["theme_closure_packages"] for item in courses),
            "budgeted_lessons": sum(item.get("budgeted_lessons", 0) for item in courses),
            "errors": sum(len(item["errors"]) for item in courses),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
