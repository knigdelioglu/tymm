#!/usr/bin/env python3
"""Validate optional school-based planning placement contracts.

The placement layer is deliberately separate from the 172-hour core lesson-plan
queue. It may recommend where a teacher could spend the 2 school-based hours in
each theme, but it must never change canonical core hours or auto-select an
option. Grade 10 additionally requires career-guidance evidence. Grade 11
requires teacher-adaptable options to remain source-grounded in the verified
teaching-block/textbook registry and to support both one-2h and two-1h selection
routes without entering the default queue.
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


def _require_string_list(value: Any, code: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        _fail(code)
    if not all(isinstance(item, str) and item.strip() for item in value):
        _fail(code)
    return value


def _validate_grade10_career_option(option: dict[str, Any], option_id: str) -> None:
    if option.get("category") != "CAREER_GUIDANCE":
        _fail("TDE10_OPTION_NOT_CAREER_GUIDANCE", option_id)

    linked_outcomes = option.get("linked_outcomes")
    if not isinstance(linked_outcomes, list) or not linked_outcomes or not all(
        isinstance(code, str) and code.strip() for code in linked_outcomes
    ):
        _fail("TDE10_LINKED_OUTCOMES_MISSING", option_id)

    alignment = option.get("career_guidance_alignment")
    if not isinstance(alignment, dict):
        _fail("TDE10_CAREER_ALIGNMENT_MISSING", option_id)
    if alignment.get("career_guidance_required") is not True:
        _fail("TDE10_CAREER_ALIGNMENT_REQUIRED_FALSE", option_id)

    domains = alignment.get("career_domains")
    if not isinstance(domains, list) or not domains or not all(
        isinstance(domain, str) and domain.strip() for domain in domains
    ):
        _fail("TDE10_CAREER_DOMAINS_MISSING", option_id)

    for key, code in {
        "tde_skill_bridge": "TDE10_SKILL_BRIDGE_MISSING",
        "career_exploration_action": "TDE10_CAREER_EXPLORATION_MISSING",
        "student_career_evidence": "TDE10_CAREER_EVIDENCE_MISSING",
        "self_awareness_prompt": "TDE10_SELF_AWARENESS_MISSING",
        "decision_support_question": "TDE10_DECISION_SUPPORT_MISSING",
    }.items():
        _require_nonempty(alignment.get(key), f"{code}:{option_id}")


def _build_tde11_source_registry(teaching_blocks: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(teaching_blocks, dict):
        _fail("TDE11_TEACHING_BLOCKS_MISSING")
    if teaching_blocks.get("course_id") != "TDE_11":
        _fail("TDE11_TEACHING_BLOCKS_COURSE_MISMATCH", str(teaching_blocks.get("course_id")))

    blocks: dict[str, dict[str, Any]] = {}
    sections: set[str] = set()
    activities: set[str] = set()
    forms: set[str] = set()
    outcomes: set[str] = set()
    for raw in teaching_blocks.get("blocks", []):
        block = raw if isinstance(raw, dict) else {}
        block_id = block.get("block_id")
        if not isinstance(block_id, str) or not block_id:
            _fail("TDE11_TEACHING_BLOCK_ID_MISSING")
        if block_id in blocks:
            _fail("TDE11_DUPLICATE_TEACHING_BLOCK_ID", block_id)
        blocks[block_id] = block
        sections.update(_require_string_list(block.get("textbook_sections", []), f"TDE11_BLOCK_SECTIONS_INVALID:{block_id}", allow_empty=True))
        activities.update(_require_string_list(block.get("textbook_activity_ids", []), f"TDE11_BLOCK_ACTIVITIES_INVALID:{block_id}", allow_empty=True))
        forms.update(_require_string_list(block.get("textbook_form_ids", []), f"TDE11_BLOCK_FORMS_INVALID:{block_id}", allow_empty=True))
        outcomes.update(_require_string_list(block.get("curriculum_outcomes", []), f"TDE11_BLOCK_OUTCOMES_INVALID:{block_id}", allow_empty=True))
    if not blocks:
        _fail("TDE11_TEACHING_BLOCKS_EMPTY")
    return {
        "blocks": blocks,
        "sections": sections,
        "activities": activities,
        "forms": forms,
        "outcomes": outcomes,
    }


def _validate_tde11_option(
    option: dict[str, Any],
    option_id: str,
    *,
    expected_theme: str,
    registry: dict[str, Any],
) -> None:
    if option.get("origin") != "pedagogical_recommendation":
        _fail("TDE11_OPTION_ORIGIN_INVALID", option_id)
    if option.get("teacher_choice_required") is not True:
        _fail("TDE11_TEACHER_CHOICE_REQUIRED_FALSE", option_id)
    if option.get("selection_status") != "NOT_SELECTED":
        _fail("TDE11_OPTION_MUST_START_UNSELECTED", option_id)
    if option.get("generation_status") != "NOT_REQUESTED":
        _fail("TDE11_OPTION_MUST_NOT_AUTO_GENERATE", option_id)
    if option.get("is_curriculum_gap") is not False:
        _fail("TDE11_OPTION_MUST_NOT_BE_CURRICULUM_GAP", option_id)

    for key, code in {
        "title": "TDE11_OPTION_TITLE_MISSING",
        "category": "TDE11_OPTION_CATEGORY_MISSING",
        "rationale": "TDE11_OPTION_RATIONALE_MISSING",
        "expected_student_action": "TDE11_EXPECTED_ACTION_MISSING",
        "expected_student_evidence": "TDE11_EXPECTED_EVIDENCE_MISSING",
        "pedagogical_function": "TDE11_PEDAGOGICAL_FUNCTION_MISSING",
        "textbook_relationship": "TDE11_TEXTBOOK_RELATIONSHIP_MISSING",
        "source_basis": "TDE11_SOURCE_BASIS_MISSING",
    }.items():
        _require_nonempty(option.get(key), f"{code}:{option_id}")

    linked_outcomes = set(_require_string_list(option.get("linked_outcomes"), f"TDE11_LINKED_OUTCOMES_MISSING:{option_id}"))
    unknown_outcomes = sorted(linked_outcomes - registry["outcomes"])
    if unknown_outcomes:
        _fail("TDE11_LINKED_OUTCOME_UNKNOWN", f"{option_id}:{','.join(unknown_outcomes)}")

    derived = option.get("derived_from")
    if not isinstance(derived, dict):
        _fail("TDE11_DERIVED_FROM_MISSING", option_id)
    block_ids = _require_string_list(derived.get("teaching_block_ids"), f"TDE11_DERIVED_BLOCKS_MISSING:{option_id}")
    section_ids = _require_string_list(derived.get("textbook_section_ids"), f"TDE11_DERIVED_SECTIONS_MISSING:{option_id}")
    activity_ids = _require_string_list(derived.get("textbook_activity_ids"), f"TDE11_DERIVED_ACTIVITIES_MISSING:{option_id}")
    form_ids = _require_string_list(derived.get("textbook_form_ids", []), f"TDE11_DERIVED_FORMS_INVALID:{option_id}", allow_empty=True)
    derived_outcomes = set(_require_string_list(derived.get("curriculum_outcomes"), f"TDE11_DERIVED_OUTCOMES_MISSING:{option_id}"))

    for block_id in block_ids:
        block = registry["blocks"].get(block_id)
        if block is None:
            _fail("TDE11_DERIVED_BLOCK_UNKNOWN", f"{option_id}:{block_id}")
        if block.get("theme_id") != expected_theme:
            _fail("TDE11_DERIVED_BLOCK_THEME_MISMATCH", f"{option_id}:{block_id}")
    for entity_id, known, code in (
        (section_ids, registry["sections"], "TDE11_DERIVED_SECTION_UNKNOWN"),
        (activity_ids, registry["activities"], "TDE11_DERIVED_ACTIVITY_UNKNOWN"),
        (form_ids, registry["forms"], "TDE11_DERIVED_FORM_UNKNOWN"),
    ):
        unknown = sorted(set(entity_id) - known)
        if unknown:
            _fail(code, f"{option_id}:{','.join(unknown)}")
    unknown_derived_outcomes = sorted(derived_outcomes - registry["outcomes"])
    if unknown_derived_outcomes:
        _fail("TDE11_DERIVED_OUTCOME_UNKNOWN", f"{option_id}:{','.join(unknown_derived_outcomes)}")

    # Linked IDs are the teacher-facing projection of the source-grounded derived_from set.
    linked_sections = set(_require_string_list(option.get("linked_textbook_section_ids"), f"TDE11_LINKED_SECTIONS_MISSING:{option_id}"))
    linked_activities = set(_require_string_list(option.get("linked_textbook_activity_ids"), f"TDE11_LINKED_ACTIVITIES_MISSING:{option_id}"))
    linked_forms = set(_require_string_list(option.get("linked_textbook_form_ids", []), f"TDE11_LINKED_FORMS_INVALID:{option_id}", allow_empty=True))
    if not linked_sections.issubset(set(section_ids)):
        _fail("TDE11_LINKED_SECTION_NOT_DERIVED", option_id)
    if not linked_activities.issubset(set(activity_ids)):
        _fail("TDE11_LINKED_ACTIVITY_NOT_DERIVED", option_id)
    if not linked_forms.issubset(set(form_ids)):
        _fail("TDE11_LINKED_FORM_NOT_DERIVED", option_id)
    if not linked_outcomes.issubset(derived_outcomes):
        _fail("TDE11_LINKED_OUTCOME_NOT_DERIVED", option_id)

    safeguards = option.get("privacy_safeguards")
    if not isinstance(safeguards, dict):
        _fail("TDE11_PRIVACY_SAFEGUARDS_MISSING", option_id)
    if safeguards.get("no_sensitive_personal_data") is not True:
        _fail("TDE11_SENSITIVE_DATA_SAFEGUARD_MISSING", option_id)
    if safeguards.get("audio_video_recording_mandatory") is not False:
        _fail("TDE11_RECORDING_MUST_NOT_BE_MANDATORY", option_id)
    if safeguards.get("public_sharing_mandatory") is not False:
        _fail("TDE11_PUBLIC_SHARING_MUST_NOT_BE_MANDATORY", option_id)
    _require_nonempty(safeguards.get("alternative_provided"), f"TDE11_SAFE_ALTERNATIVE_MISSING:{option_id}")


def validate_payloads(
    options: dict[str, Any],
    placements: dict[str, Any],
    production_plan: dict[str, Any],
    teaching_blocks: dict[str, Any] | None = None,
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
    if course_id == "TDE_10":
        expected_policy["career_guidance_required"] = True
    if course_id == "TDE_11":
        expected_policy["selection_mode"] = "ONE_2H_OR_TWO_1H"
    for key, expected in expected_policy.items():
        if policy.get(key) != expected:
            _fail("PLACEMENT_POLICY_MISMATCH", f"{key}={policy.get(key)!r},expected={expected!r}")

    if course_id == "TDE_10":
        career_policy = options.get("career_guidance_policy")
        if not isinstance(career_policy, dict):
            _fail("TDE10_CAREER_POLICY_MISSING")
        if career_policy.get("required") is not True:
            _fail("TDE10_CAREER_POLICY_REQUIRED_FALSE")
        if career_policy.get("scope") != "ALL_SELECTED_SBP_HOURS":
            _fail("TDE10_CAREER_POLICY_SCOPE_MISMATCH", str(career_policy.get("scope")))
        if career_policy.get("school_based_planning_hours_per_theme") != 2:
            _fail("TDE10_CAREER_THEME_HOURS_MISMATCH")
        if career_policy.get("school_based_planning_hours_annual") != 8:
            _fail("TDE10_CAREER_ANNUAL_HOURS_MISMATCH")
        basis = career_policy.get("official_basis")
        if not isinstance(basis, list) or not basis:
            _fail("TDE10_CAREER_POLICY_BASIS_MISSING")

    tde11_registry = _build_tde11_source_registry(teaching_blocks) if course_id == "TDE_11" else None
    if course_id == "TDE_11":
        annual = options.get("annual_hours", {})
        expected_annual = {"structured_program": 172, "school_based_planning": 8, "official_total": 180}
        for key, expected in expected_annual.items():
            if annual.get(key) != expected:
                _fail("TDE11_OPTION_ANNUAL_HOURS_MISMATCH", f"{key}={annual.get(key)!r},expected={expected}")
        theme_policy = options.get("theme_policy", {})
        expected_theme_policy = {
            "official_theme_hours": 45,
            "structured_program_hours": 43,
            "school_based_planning_hours": 2,
            "max_selected_hours_per_theme": 2,
            "default_selection": "NONE",
            "default_generation": "NOT_REQUESTED",
        }
        for key, expected in expected_theme_policy.items():
            if theme_policy.get(key) != expected:
                _fail("TDE11_OPTION_THEME_POLICY_MISMATCH", f"{key}={theme_policy.get(key)!r},expected={expected!r}")

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
    theme_durations: dict[str, list[int]] = {theme_id: [] for theme_id in plan_themes}
    option_theme_records: set[str] = set()
    career_option_count = 0
    tde11_option_count = 0
    for theme in options.get("themes", []):
        theme_id = theme.get("theme_id")
        if theme_id not in plan_themes:
            _fail("OPTION_THEME_UNKNOWN", str(theme_id))
        if theme_id in option_theme_records:
            _fail("DUPLICATE_OPTION_THEME", str(theme_id))
        option_theme_records.add(theme_id)
        if course_id in {"TDE_10", "TDE_11"} and theme.get("allocated_hours") != 2:
            _fail(f"{course_id}_THEME_ALLOCATED_HOURS_MISMATCH", str(theme_id))
        if course_id == "TDE_11":
            if theme.get("structured_program_hours") != 43 or theme.get("school_based_planning_hours") != 2:
                _fail("TDE11_THEME_HOUR_ENVELOPE_MISMATCH", str(theme_id))
        for option in theme.get("options", []):
            option_id = option.get("option_id")
            duration = option.get("duration_hours")
            if not isinstance(option_id, str) or not option_id:
                _fail("OPTION_ID_MISSING", str(theme_id))
            if option_id in option_index:
                _fail("DUPLICATE_OPTION_ID", option_id)
            if not isinstance(duration, int) or isinstance(duration, bool) or duration < 1 or duration > 2:
                _fail("OPTION_DURATION_OUT_OF_RANGE", f"{option_id}={duration!r}")
            if option.get("theme_id") != theme_id:
                _fail("OPTION_THEME_MISMATCH", option_id)
            if course_id == "TDE_10":
                _validate_grade10_career_option(option, option_id)
                career_option_count += 1
            elif course_id == "TDE_11":
                assert tde11_registry is not None
                _validate_tde11_option(option, option_id, expected_theme=theme_id, registry=tde11_registry)
                tde11_option_count += 1
            option_index[option_id] = (theme_id, duration)
            theme_option_hours[theme_id] += duration
            theme_durations[theme_id].append(duration)

    if option_theme_records != set(plan_themes):
        _fail("OPTION_THEME_SET_MISMATCH", repr(sorted(option_theme_records)))

    for theme_id, available_hours in theme_option_hours.items():
        if course_id == "TDE_10":
            if available_hours != 2:
                _fail("TDE10_CAREER_OPTION_HOURS_MUST_EQUAL_THEME_ALLOCATION", f"{theme_id}={available_hours}")
        elif course_id == "TDE_11":
            if sorted(theme_durations[theme_id]) != [1, 1, 2]:
                _fail("TDE11_SELECTION_MODES_MUST_BE_ONE_2H_OR_TWO_1H", f"{theme_id}={sorted(theme_durations[theme_id])}")
            # Capacity is deliberately 4 candidate-hours; selectable capacity remains 2h.
            if available_hours != 4:
                _fail("TDE11_OPTION_POOL_CANDIDATE_HOURS_MISMATCH", f"{theme_id}={available_hours}")
        elif available_hours < 2:
            _fail("INSUFFICIENT_SBP_OPTION_CAPACITY", f"{theme_id}={available_hours}")

    if course_id == "TDE_10" and sum(theme_option_hours.values()) != 8:
        _fail("TDE10_CAREER_OPTION_ANNUAL_HOURS_MISMATCH", str(sum(theme_option_hours.values())))
    if course_id == "TDE_11" and (tde11_option_count != 12 or sum(theme_option_hours.values()) != 16):
        _fail("TDE11_OPTION_POOL_SHAPE_MISMATCH", f"options={tde11_option_count},candidate_hours={sum(theme_option_hours.values())}")

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

    result = {
        "course_id": course_id,
        "status": "PASS",
        "themes": 4,
        "options": len(option_index),
        "placements": len(placement_index),
        "core_instruction_hours": 172,
        "school_based_planning_hours": 8,
        "official_total_hours": 180,
    }
    if course_id == "TDE_10":
        result["career_guidance_options"] = career_option_count
        result["career_guidance_hours"] = sum(theme_option_hours.values())
    if course_id == "TDE_11":
        result["teacher_adaptable_options"] = tde11_option_count
        result["candidate_option_hours"] = sum(theme_option_hours.values())
        result["selectable_school_based_hours"] = 8
        result["selection_mode"] = "ONE_2H_OR_TWO_1H"
    return result


def validate_course(root: Path) -> dict[str, Any]:
    teaching_blocks_path = root / "production/teaching_blocks.json"
    teaching_blocks = read_json(teaching_blocks_path) if teaching_blocks_path.exists() else None
    return validate_payloads(
        read_json(root / "production/school_based_planning_options.json"),
        read_json(root / "production/school_based_planning_placements.json"),
        read_json(root / "planning/lesson_plan_production_plan.json"),
        teaching_blocks,
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
