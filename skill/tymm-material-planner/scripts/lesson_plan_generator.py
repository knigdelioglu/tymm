#!/usr/bin/env python3
"""TYMM AI Lesson Generator V1.

The generator is intentionally transport-agnostic. It builds an immutable,
source-bound model request, accepts a model response through a callable or a
stdin/stdout provider command, validates the candidate, and allows at most a
small number of repair rounds. Canonical course facts are never repaired or
mutated by the model.
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any, Callable

import lesson_plan_context
import validate_lesson_plan

GENERATOR_VERSION = "1.0.0"
PLAN_SCHEMA_VERSION = "1.0.0"
DEFAULT_MAX_REPAIRS = 2
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SCHEMA_PATH = SKILL_DIR / "schemas" / "lesson_plan.schema.json"


class LessonPlanGenerationError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise LessonPlanGenerationError(f"JSON_OBJECT_REQUIRED: {path}")
    return data


def load_schema() -> dict[str, Any]:
    if not SCHEMA_PATH.exists():
        raise LessonPlanGenerationError(f"LESSON_PLAN_SCHEMA_MISSING: {SCHEMA_PATH}")
    return read_json(SCHEMA_PATH)


def _clean_preferences(value: dict[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise LessonPlanGenerationError("TEACHER_PREFERENCES_MUST_BE_OBJECT")
    forbidden = {
        "course_id", "theme_id", "block_id", "lesson_hours", "outcome_codes",
        "activity_ids", "form_ids", "date", "date_range", "week", "academic_year",
    }
    collision = sorted(forbidden.intersection(value))
    if collision:
        raise LessonPlanGenerationError(f"TEACHER_PREFERENCES_OVERRIDE_CANONICAL_FIELDS:{collision}")
    return value


def _clean_continuation(value: dict[str, Any] | None, context: dict[str, Any]) -> dict[str, Any]:
    if value is None:
        return {
            "completed_hours_before_this_plan": 0,
            "previously_used_activity_ids": [],
            "previously_covered_outcome_codes": [],
            "previous_plan_summary": "",
        }
    if not isinstance(value, dict):
        raise LessonPlanGenerationError("CONTINUATION_STATE_MUST_BE_OBJECT")
    allowed_activities = set(context.get("allowed_references", {}).get("activity_ids", []))
    allowed_outcomes = set(context.get("allowed_references", {}).get("outcome_codes", []))
    completed = value.get("completed_hours_before_this_plan", 0)
    if not isinstance(completed, int) or isinstance(completed, bool) or completed < 0:
        raise LessonPlanGenerationError("CONTINUATION_COMPLETED_HOURS_INVALID")
    block_hours = context.get("block", {}).get("planned_hours")
    requested = context.get("planning_request", {}).get("requested_lesson_hours")
    if isinstance(block_hours, int) and completed + requested > block_hours:
        raise LessonPlanGenerationError(
            f"CONTINUATION_EXCEEDS_BLOCK: completed={completed}, requested={requested}, block={block_hours}"
        )
    activities = value.get("previously_used_activity_ids", [])
    outcomes = value.get("previously_covered_outcome_codes", [])
    if not isinstance(activities, list) or not all(isinstance(x, str) for x in activities):
        raise LessonPlanGenerationError("CONTINUATION_ACTIVITY_IDS_INVALID")
    if not isinstance(outcomes, list) or not all(isinstance(x, str) for x in outcomes):
        raise LessonPlanGenerationError("CONTINUATION_OUTCOME_CODES_INVALID")
    bad_activities = sorted(set(activities) - allowed_activities)
    bad_outcomes = sorted(set(outcomes) - allowed_outcomes)
    if bad_activities:
        raise LessonPlanGenerationError(f"CONTINUATION_UNKNOWN_ACTIVITY_IDS:{bad_activities}")
    if bad_outcomes:
        raise LessonPlanGenerationError(f"CONTINUATION_UNKNOWN_OUTCOME_CODES:{bad_outcomes}")
    summary = value.get("previous_plan_summary", "")
    if not isinstance(summary, str):
        raise LessonPlanGenerationError("CONTINUATION_SUMMARY_INVALID")
    return {
        "completed_hours_before_this_plan": completed,
        "previously_used_activity_ids": sorted(set(activities)),
        "previously_covered_outcome_codes": sorted(set(outcomes)),
        "previous_plan_summary": summary,
    }


def build_model_request(
    context: dict[str, Any],
    teacher_preferences: dict[str, Any] | None = None,
    continuation_state: dict[str, Any] | None = None,
    *,
    repair_errors: list[str] | None = None,
    previous_candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if context.get("resolution_status") != "RESOLVED":
        raise LessonPlanGenerationError("LESSON_PLAN_CONTEXT_NOT_RESOLVED")
    preferences = _clean_preferences(teacher_preferences)
    continuation = _clean_continuation(continuation_state, context)
    schema = load_schema()
    repair = bool(repair_errors)

    system_instruction = (
        "Sen TYMM için ders planı üreten pedagojik bir planlama modelisin. "
        "CANONICAL_CONTEXT içindeki resmî bilgiler değiştirilemez. Yalnız verilen kazanım kodlarını, "
        "etkinlik kimliklerini, form kimliklerini ve süreyi kullan. Kitap sayfası veya MEB onayı uydurma. "
        "Takvim, hafta, tarih, ara tatil ve akademik yıl bilgisi üretme. "
        "Öğretim akışını pedagojik öneri olarak tasarla; bunu resmî MEB alt-ders sıralaması gibi sunma. "
        "Yanıt yalnız RESPONSE_SCHEMA ile uyumlu tek bir JSON nesnesi olmalıdır."
    )
    if repair:
        system_instruction += (
            " Bu bir onarım turudur. Önceki adayın yalnız belirtilen hatalarını düzelt; "
            "canonical kimlikleri, süreyi ve izin verilen referans kümesini değiştirme."
        )

    request: dict[str, Any] = {
        "request_type": "TYMM_AI_LESSON_PLAN_GENERATION",
        "generator_version": GENERATOR_VERSION,
        "mode": "REPAIR" if repair else "GENERATE",
        "system_instruction": system_instruction,
        "immutable_identity": {
            "course_id": context["course"]["course_id"],
            "theme_id": context["theme"]["theme_id"],
            "block_id": context["block"]["block_id"],
            "lesson_hours": context["planning_request"]["requested_lesson_hours"],
        },
        "canonical_context": context,
        "teacher_preferences": preferences,
        "continuation_state": continuation,
        "response_schema": schema,
        "generation_rules": [
            "Top-level course_id/theme_id/block_id/lesson_hours immutable_identity ile birebir aynı olmalı.",
            "outcome_codes yalnız canonical_context.allowed_references.outcome_codes içinden seçilmeli.",
            "used_activity_ids ve lessons[].activity_ids yalnız izin verilen activity_ids içinden seçilmeli.",
            "used_form_ids ve lessons[].form_ids yalnız izin verilen form_ids içinden seçilmeli.",
            "lessons[].duration_lesson_hours toplamı lesson_hours değerine eşit olmalı.",
            "Mümkün olduğunda kitap etkinliklerini yeni materyal üretmekten önce kullan.",
            "Önceki devam durumunda kullanılmış etkinlikleri pedagojik gerekçe yoksa tekrarlama.",
            "continuation_summary.remaining_block_hours, blok toplamından önceki tamamlanan saatler ve bu plan düşülerek hesaplanmalı.",
            "Takvim alanları üretme.",
        ],
    }
    if repair:
        request["repair"] = {
            "validation_errors": list(repair_errors or []),
            "previous_candidate": previous_candidate or {},
            "instruction": "Yalnız hataları düzelt ve tam, geçerli JSON planı yeniden döndür.",
        }
    return request


def _extract_json_from_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise LessonPlanGenerationError("MODEL_RESPONSE_JSON_NOT_FOUND")
        try:
            data = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError as exc:
            raise LessonPlanGenerationError(f"MODEL_RESPONSE_JSON_INVALID:{exc.msg}") from exc
    if not isinstance(data, dict):
        raise LessonPlanGenerationError("MODEL_RESPONSE_OBJECT_REQUIRED")
    return data


def extract_candidate(raw: Any) -> dict[str, Any]:
    if isinstance(raw, str):
        return _extract_json_from_text(raw)
    if not isinstance(raw, dict):
        raise LessonPlanGenerationError("MODEL_RESPONSE_UNSUPPORTED_TYPE")
    if "course_id" in raw and "lessons" in raw:
        return raw
    for key in ("plan", "output", "result"):
        value = raw.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return _extract_json_from_text(value)
    for key in ("content", "text", "response"):
        value = raw.get(key)
        if isinstance(value, str):
            return _extract_json_from_text(value)
    raise LessonPlanGenerationError("MODEL_RESPONSE_PLAN_NOT_FOUND")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list_errors(value: Any, path: str, *, min_items: int = 0) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, list):
        return [f"SCHEMA_TYPE:{path}:array"]
    if len(value) < min_items:
        errors.append(f"SCHEMA_MIN_ITEMS:{path}:{min_items}")
    if not all(_is_nonempty_string(x) for x in value):
        errors.append(f"SCHEMA_ITEM_TYPE:{path}:nonempty_string")
    try:
        if len(value) != len(set(value)):
            errors.append(f"SCHEMA_UNIQUE_ITEMS:{path}")
    except TypeError:
        pass
    return errors


def validate_candidate_shape(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = [
        "schema_version", "course_id", "theme_id", "block_id", "lesson_hours",
        "plan_title", "plan_summary", "outcome_codes", "used_activity_ids",
        "used_form_ids", "lessons", "teacher_notes", "continuation_summary",
    ]
    for key in required:
        if key not in plan:
            errors.append(f"SCHEMA_REQUIRED:{key}")
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        errors.append(f"SCHEMA_VERSION:{plan.get('schema_version')}!={PLAN_SCHEMA_VERSION}")
    for key in ("course_id", "theme_id", "block_id", "plan_title", "plan_summary"):
        if key in plan and not _is_nonempty_string(plan.get(key)):
            errors.append(f"SCHEMA_TYPE:{key}:nonempty_string")
    if "teacher_notes" in plan and not isinstance(plan.get("teacher_notes"), str):
        errors.append("SCHEMA_TYPE:teacher_notes:string")
    hours = plan.get("lesson_hours")
    if not isinstance(hours, int) or isinstance(hours, bool) or hours <= 0:
        errors.append("SCHEMA_TYPE:lesson_hours:positive_integer")
    errors += _string_list_errors(plan.get("outcome_codes"), "outcome_codes", min_items=1)
    errors += _string_list_errors(plan.get("used_activity_ids"), "used_activity_ids")
    errors += _string_list_errors(plan.get("used_form_ids"), "used_form_ids")

    lessons = plan.get("lessons")
    lesson_activity_union: set[str] = set()
    lesson_form_union: set[str] = set()
    lesson_outcome_union: set[str] = set()
    if not isinstance(lessons, list) or not lessons:
        errors.append("SCHEMA_TYPE:lessons:nonempty_array")
        lessons = []
    allowed_lesson_keys = {
        "lesson_no", "duration_lesson_hours", "title", "objective", "outcome_codes",
        "opening", "teacher_actions", "student_actions", "activity_ids", "form_ids",
        "assessment", "closure", "materials",
    }
    for index, lesson in enumerate(lessons, 1):
        prefix = f"lessons[{index - 1}]"
        if not isinstance(lesson, dict):
            errors.append(f"SCHEMA_TYPE:{prefix}:object")
            continue
        extra = sorted(set(lesson) - allowed_lesson_keys)
        if extra:
            errors.append(f"SCHEMA_ADDITIONAL_PROPERTIES:{prefix}:{extra}")
        missing = sorted(allowed_lesson_keys - set(lesson))
        if missing:
            errors.append(f"SCHEMA_REQUIRED:{prefix}:{missing}")
        no = lesson.get("lesson_no")
        duration = lesson.get("duration_lesson_hours")
        if not isinstance(no, int) or isinstance(no, bool) or no <= 0:
            errors.append(f"SCHEMA_TYPE:{prefix}.lesson_no:positive_integer")
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            errors.append(f"SCHEMA_TYPE:{prefix}.duration_lesson_hours:positive_integer")
        for key in ("title", "objective", "opening", "assessment", "closure"):
            if not _is_nonempty_string(lesson.get(key)):
                errors.append(f"SCHEMA_TYPE:{prefix}.{key}:nonempty_string")
        errors += _string_list_errors(lesson.get("outcome_codes"), f"{prefix}.outcome_codes", min_items=1)
        errors += _string_list_errors(lesson.get("teacher_actions"), f"{prefix}.teacher_actions", min_items=1)
        errors += _string_list_errors(lesson.get("student_actions"), f"{prefix}.student_actions", min_items=1)
        errors += _string_list_errors(lesson.get("activity_ids"), f"{prefix}.activity_ids")
        errors += _string_list_errors(lesson.get("form_ids"), f"{prefix}.form_ids")
        errors += _string_list_errors(lesson.get("materials"), f"{prefix}.materials")
        if isinstance(lesson.get("activity_ids"), list):
            lesson_activity_union.update(x for x in lesson["activity_ids"] if isinstance(x, str))
        if isinstance(lesson.get("form_ids"), list):
            lesson_form_union.update(x for x in lesson["form_ids"] if isinstance(x, str))
        if isinstance(lesson.get("outcome_codes"), list):
            lesson_outcome_union.update(x for x in lesson["outcome_codes"] if isinstance(x, str))

    top_activities = set(x for x in plan.get("used_activity_ids", []) if isinstance(x, str)) if isinstance(plan.get("used_activity_ids"), list) else set()
    top_forms = set(x for x in plan.get("used_form_ids", []) if isinstance(x, str)) if isinstance(plan.get("used_form_ids"), list) else set()
    top_outcomes = set(x for x in plan.get("outcome_codes", []) if isinstance(x, str)) if isinstance(plan.get("outcome_codes"), list) else set()
    if lesson_activity_union != top_activities:
        errors.append(f"SCHEMA_REFERENCE_UNION:used_activity_ids:{sorted(lesson_activity_union)}!={sorted(top_activities)}")
    if lesson_form_union != top_forms:
        errors.append(f"SCHEMA_REFERENCE_UNION:used_form_ids:{sorted(lesson_form_union)}!={sorted(top_forms)}")
    if not lesson_outcome_union.issubset(top_outcomes):
        errors.append(f"SCHEMA_REFERENCE_UNION:lesson_outcomes_not_top_level:{sorted(lesson_outcome_union - top_outcomes)}")

    summary = plan.get("continuation_summary")
    if not isinstance(summary, dict):
        errors.append("SCHEMA_TYPE:continuation_summary:object")
    else:
        required_summary = {
            "planned_now_hours", "remaining_block_hours", "covered_outcome_codes",
            "used_activity_ids", "next_step_hint",
        }
        extra = sorted(set(summary) - required_summary)
        missing = sorted(required_summary - set(summary))
        if extra:
            errors.append(f"SCHEMA_ADDITIONAL_PROPERTIES:continuation_summary:{extra}")
        if missing:
            errors.append(f"SCHEMA_REQUIRED:continuation_summary:{missing}")
        for key, allow_zero in (("planned_now_hours", False), ("remaining_block_hours", True)):
            value = summary.get(key)
            invalid = not isinstance(value, int) or isinstance(value, bool) or value < (0 if allow_zero else 1)
            if invalid:
                errors.append(f"SCHEMA_TYPE:continuation_summary.{key}:integer")
        errors += _string_list_errors(summary.get("covered_outcome_codes"), "continuation_summary.covered_outcome_codes")
        errors += _string_list_errors(summary.get("used_activity_ids"), "continuation_summary.used_activity_ids")
        if not isinstance(summary.get("next_step_hint"), str):
            errors.append("SCHEMA_TYPE:continuation_summary.next_step_hint:string")
    return errors


def validate_generated_plan(
    context: dict[str, Any],
    plan: dict[str, Any],
    continuation_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    shape_errors = validate_candidate_shape(plan)
    grounding = validate_lesson_plan.validate(context, plan)
    errors = list(shape_errors) + list(grounding.get("errors", []))
    warnings = list(grounding.get("warnings", []))

    allowed = context.get("allowed_references", {})
    allowed_outcomes = set(allowed.get("outcome_codes", []))
    allowed_activities = set(allowed.get("activity_ids", []))
    allowed_forms = set(allowed.get("form_ids", []))
    for idx, lesson in enumerate(plan.get("lessons", []) if isinstance(plan.get("lessons"), list) else [], 1):
        if not isinstance(lesson, dict):
            continue
        bad_outcomes = sorted(set(lesson.get("outcome_codes", [])) - allowed_outcomes) if isinstance(lesson.get("outcome_codes"), list) else []
        bad_activities = sorted(set(lesson.get("activity_ids", [])) - allowed_activities) if isinstance(lesson.get("activity_ids"), list) else []
        bad_forms = sorted(set(lesson.get("form_ids", [])) - allowed_forms) if isinstance(lesson.get("form_ids"), list) else []
        if bad_outcomes:
            errors.append(f"UNKNOWN_LESSON_OUTCOME_CODES:{idx}:{bad_outcomes}")
        if bad_activities:
            errors.append(f"UNKNOWN_LESSON_ACTIVITY_IDS:{idx}:{bad_activities}")
        if bad_forms:
            errors.append(f"UNKNOWN_LESSON_FORM_IDS:{idx}:{bad_forms}")

    continuation = _clean_continuation(continuation_state, context)
    summary = plan.get("continuation_summary") if isinstance(plan.get("continuation_summary"), dict) else {}
    requested = context.get("planning_request", {}).get("requested_lesson_hours")
    block_hours = context.get("block", {}).get("planned_hours")
    completed_before = continuation.get("completed_hours_before_this_plan", 0)
    expected_remaining = block_hours - completed_before - requested
    if summary.get("planned_now_hours") != requested:
        errors.append(f"CONTINUATION_PLANNED_HOURS_MISMATCH:{summary.get('planned_now_hours')}!={requested}")
    if summary.get("remaining_block_hours") != expected_remaining:
        errors.append(f"CONTINUATION_REMAINING_HOURS_MISMATCH:{summary.get('remaining_block_hours')}!={expected_remaining}")
    if isinstance(summary.get("covered_outcome_codes"), list):
        bad = sorted(set(summary["covered_outcome_codes"]) - allowed_outcomes)
        if bad:
            errors.append(f"CONTINUATION_UNKNOWN_COVERED_OUTCOMES:{bad}")
    if isinstance(summary.get("used_activity_ids"), list):
        bad = sorted(set(summary["used_activity_ids"]) - allowed_activities)
        if bad:
            errors.append(f"CONTINUATION_UNKNOWN_USED_ACTIVITIES:{bad}")

    deduped_errors = list(dict.fromkeys(errors))
    deduped_warnings = list(dict.fromkeys(warnings))
    return {
        "status": "PASS" if not deduped_errors else "FAIL",
        "errors": deduped_errors,
        "warnings": deduped_warnings,
        "shape_error_count": len(shape_errors),
        "grounding_status": grounding.get("status"),
    }


def generate(
    context: dict[str, Any],
    invoke_model: Callable[[dict[str, Any]], Any],
    teacher_preferences: dict[str, Any] | None = None,
    continuation_state: dict[str, Any] | None = None,
    *,
    max_repairs: int = DEFAULT_MAX_REPAIRS,
) -> dict[str, Any]:
    if not isinstance(max_repairs, int) or isinstance(max_repairs, bool) or max_repairs < 0 or max_repairs > 5:
        raise LessonPlanGenerationError("MAX_REPAIRS_OUT_OF_RANGE:0..5")
    preferences = _clean_preferences(teacher_preferences)
    continuation = _clean_continuation(continuation_state, context)
    previous_candidate: dict[str, Any] | None = None
    errors: list[str] | None = None
    trace: list[dict[str, Any]] = []

    for attempt in range(max_repairs + 1):
        request = build_model_request(
            context,
            preferences,
            continuation,
            repair_errors=errors,
            previous_candidate=previous_candidate,
        )
        try:
            raw = invoke_model(request)
            candidate = extract_candidate(raw)
            validation = validate_generated_plan(context, candidate, continuation)
        except LessonPlanGenerationError as exc:
            candidate = previous_candidate or {}
            validation = {"status": "FAIL", "errors": [str(exc)], "warnings": []}

        trace.append({
            "attempt": attempt + 1,
            "mode": request["mode"],
            "validation_status": validation.get("status"),
            "errors": validation.get("errors", []),
        })
        if validation.get("status") == "PASS":
            return {
                "status": "PASS",
                "generator_version": GENERATOR_VERSION,
                "attempts": attempt + 1,
                "repair_count": attempt,
                "plan": candidate,
                "validation": validation,
                "trace": trace,
            }
        previous_candidate = candidate
        errors = list(validation.get("errors", []))

    return {
        "status": "BLOCKED",
        "generator_version": GENERATOR_VERSION,
        "attempts": max_repairs + 1,
        "repair_count": max_repairs,
        "plan": None,
        "validation": {"status": "FAIL", "errors": errors or [], "warnings": []},
        "trace": trace,
        "block_reason": "LESSON_PLAN_VALIDATION_FAILED_AFTER_REPAIRS",
    }


def invoke_provider_command(command: str, request: dict[str, Any], timeout_seconds: int = 180) -> Any:
    if not _is_nonempty_string(command):
        raise LessonPlanGenerationError("PROVIDER_COMMAND_REQUIRED")
    if not isinstance(timeout_seconds, int) or timeout_seconds <= 0 or timeout_seconds > 900:
        raise LessonPlanGenerationError("PROVIDER_TIMEOUT_OUT_OF_RANGE")
    argv = shlex.split(command)
    if not argv:
        raise LessonPlanGenerationError("PROVIDER_COMMAND_EMPTY")
    try:
        proc = subprocess.run(
            argv,
            input=json.dumps(request, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LessonPlanGenerationError(f"PROVIDER_COMMAND_FAILED:{exc}") from exc
    if proc.returncode != 0:
        stderr = proc.stderr.strip()[-1000:]
        raise LessonPlanGenerationError(f"PROVIDER_COMMAND_EXIT_{proc.returncode}:{stderr}")
    if not proc.stdout.strip():
        raise LessonPlanGenerationError("PROVIDER_COMMAND_EMPTY_STDOUT")
    return proc.stdout


def _load_optional_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return read_json(Path(path))


def main() -> int:
    parser = argparse.ArgumentParser(description="TYMM AI Lesson Generator V1")
    parser.add_argument("--knowledge-root", required=True)
    parser.add_argument("--block-id", required=True)
    parser.add_argument("--lesson-hours", type=int, required=True)
    parser.add_argument("--preferences")
    parser.add_argument("--continuation")
    sub = parser.add_subparsers(dest="command", required=True)

    request_parser = sub.add_parser("request")
    request_parser.add_argument("--output")

    generate_parser = sub.add_parser("generate")
    generate_parser.add_argument("--provider-command", required=True)
    generate_parser.add_argument("--max-repairs", type=int, default=DEFAULT_MAX_REPAIRS)
    generate_parser.add_argument("--timeout-seconds", type=int, default=180)
    generate_parser.add_argument("--output")
    generate_parser.add_argument("--trace-output")

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--plan", required=True)
    validate_parser.add_argument("--output")

    args = parser.parse_args()
    try:
        root = Path(args.knowledge_root).resolve()
        context = lesson_plan_context.assemble(root, args.block_id, args.lesson_hours)
        preferences = _load_optional_json(args.preferences)
        continuation = _load_optional_json(args.continuation)

        if args.command == "request":
            payload = build_model_request(context, preferences, continuation)
            text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
            if args.output:
                Path(args.output).write_text(text, encoding="utf-8")
            else:
                print(text, end="")
            return 0

        if args.command == "validate":
            plan = read_json(Path(args.plan))
            result = validate_generated_plan(context, plan, continuation)
            text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
            if args.output:
                Path(args.output).write_text(text, encoding="utf-8")
            else:
                print(text, end="")
            return 0 if result["status"] == "PASS" else 1

        def provider(request: dict[str, Any]) -> Any:
            return invoke_provider_command(args.provider_command, request, args.timeout_seconds)

        result = generate(
            context,
            provider,
            preferences,
            continuation,
            max_repairs=args.max_repairs,
        )
        if result["status"] == "PASS" and args.output:
            Path(args.output).write_text(
                json.dumps(result["plan"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        if args.trace_output:
            Path(args.trace_output).write_text(
                json.dumps({k: v for k, v in result.items() if k != "plan"}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        print(json.dumps({
            "status": result["status"],
            "attempts": result["attempts"],
            "repair_count": result["repair_count"],
            "validation": result["validation"],
            "block_reason": result.get("block_reason"),
            "output": args.output if result["status"] == "PASS" else None,
        }, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 2
    except (LessonPlanGenerationError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
