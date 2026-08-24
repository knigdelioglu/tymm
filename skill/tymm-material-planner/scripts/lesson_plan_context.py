#!/usr/bin/env python3
"""Build a minimal, source-bound context pack for AI lesson-plan generation."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from build_runtime_course_package import compiler_state

CONTEXT_VERSION = "1.1.0"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def require_runtime_fresh(root: Path) -> dict[str, Any]:
    manifest_path = root / "runtime/runtime_manifest.json"
    db_path = root / "runtime/course_runtime.sqlite"
    if not manifest_path.exists() or not db_path.exists():
        raise ValueError("LESSON_PLAN_RUNTIME_MISSING")
    manifest = read_json(manifest_path)
    if manifest.get("validation_status") != "PASS":
        raise ValueError(f"LESSON_PLAN_RUNTIME_NOT_VALIDATED: {manifest.get('validation_status')}")
    current_fingerprint = compiler_state(root)[1]
    if current_fingerprint != manifest.get("canonical_content_fingerprint"):
        raise ValueError("LESSON_PLAN_RUNTIME_STALE")
    if manifest.get("timeline_resolution") != "BLOCK_TIME_RESOLVED":
        raise ValueError(f"LESSON_PLAN_BLOCK_TIME_UNRESOLVED: {manifest.get('timeline_resolution')}")
    if (root / "curriculum_process_component_resolution.json").exists() and manifest.get("process_component_resolution_status") != "PASS":
        raise ValueError(f"LESSON_PLAN_PROCESS_COMPONENTS_UNRESOLVED: {manifest.get('process_component_resolution_status')}")
    return manifest


def assemble(root: Path, block_id: str, requested_lesson_hours: int | None = None) -> dict[str, Any]:
    root = root.resolve()
    manifest = require_runtime_fresh(root)
    db = sqlite3.connect(root / "runtime/course_runtime.sqlite")
    db.row_factory = sqlite3.Row
    try:
        block = db.execute(
            """
            SELECT c.course_id,c.grade,c.title AS course_title,
                   t.theme_id,t.theme_order,t.title AS theme_title,t.planned_hours AS theme_instruction_hours,
                   b.block_id,b.block_order,b.title AS block_title,b.skill_domain,b.learning_area,
                   b.planned_hours,b.time_status,b.source_locators_json,
                   tt.school_based_hours,tt.school_based_hours_status,
                   tb.source_locators_json AS timeline_source_locators
            FROM blocks b
            JOIN themes t ON t.theme_id=b.theme_id
            JOIN courses c ON c.course_id=t.course_id
            JOIN timeline_themes tt ON tt.theme_id=t.theme_id
            JOIN timeline_blocks tb ON tb.block_id=b.block_id
            WHERE b.block_id=?
            """,
            (block_id,),
        ).fetchone()
        if block is None:
            raise ValueError(f"LESSON_PLAN_BLOCK_NOT_FOUND: {block_id}")
        planned_hours = block["planned_hours"]
        if planned_hours is None:
            raise ValueError(f"LESSON_PLAN_BLOCK_HOURS_UNRESOLVED: {block_id}")
        if requested_lesson_hours is None:
            requested_lesson_hours = planned_hours
        if not isinstance(requested_lesson_hours, int) or isinstance(requested_lesson_hours, bool) or requested_lesson_hours <= 0:
            raise ValueError("LESSON_PLAN_REQUESTED_HOURS_INVALID")
        if requested_lesson_hours > planned_hours:
            raise ValueError(
                f"LESSON_PLAN_REQUESTED_HOURS_EXCEED_BLOCK: requested={requested_lesson_hours}, block={planned_hours}"
            )

        outcomes = [dict(row) for row in db.execute(
            """
            SELECT o.outcome_id,o.outcome_code,o.official_text,o.process_components,o.process_component_origin,
                   o.source_locator,o.verification_status
            FROM block_outcomes bo
            JOIN outcomes o ON o.outcome_id=bo.outcome_id
            WHERE bo.block_id=?
            ORDER BY o.outcome_code
            """,
            (block_id,),
        )]
        for outcome in outcomes:
            outcome["process_components"] = parse_json(outcome.get("process_components"), [])
            if manifest.get("process_component_resolution_status") == "PASS" and not outcome["process_components"]:
                raise ValueError(f"LESSON_PLAN_EFFECTIVE_PROCESS_COMPONENTS_EMPTY: {outcome.get('outcome_id')}")

        activities = [dict(row) for row in db.execute(
            """
            SELECT a.activity_id,a.title,a.activity_type,a.student_action,a.expected_evidence,
                   a.printed_page,a.pdf_page,a.verification_status,
                   s.section_id,s.title AS section_title,s.genre,s.printed_page_range,s.pdf_page_range,s.source_id
            FROM block_activities ba
            JOIN activities a ON a.activity_id=ba.activity_id
            LEFT JOIN textbook_sections s ON s.section_id=a.section_id
            WHERE ba.block_id=?
            ORDER BY COALESCE(CAST(a.printed_page AS INTEGER),99999),a.activity_id
            """,
            (block_id,),
        )]

        forms = [dict(row) for row in db.execute(
            """
            SELECT DISTINCT f.form_id,f.title,f.structural_type,f.assessment_type,
                   f.printed_page,f.pdf_page,f.evaluator,f.source_id,f.verification_status
            FROM block_activities ba
            JOIN activity_forms af ON af.activity_id=ba.activity_id
            JOIN forms f ON f.form_id=af.form_id
            WHERE ba.block_id=?
            ORDER BY f.form_id
            """,
            (block_id,),
        )]

        resources = [dict(row) for row in db.execute(
            """
            SELECT resource_plan_id,need_id,resource_type,decision_code,app_category,priority,
                   purpose,expected_evidence,textbook_coverage,locator,teacher_review_required
            FROM resource_decisions
            WHERE theme_id=?
            ORDER BY priority,resource_plan_id
            """,
            (block["theme_id"],),
        )]

        assessment_bindings = [dict(row) for row in db.execute(
            """
            SELECT atb.artifact_id,aa.title AS artifact_title,aa.assessment_family,aa.reuse_policy,
                   atb.gap_instance_id,atb.activity_id,atb.targeted_outcomes_json,atb.task_title,
                   atb.evidence,atb.textbook_locator,atb.curriculum_locator
            FROM assessment_task_bindings atb
            JOIN assessment_artifacts aa ON aa.artifact_id=atb.artifact_id
            WHERE atb.block_id=?
            ORDER BY atb.artifact_id,atb.gap_instance_id
            """,
            (block_id,),
        )]
        for item in assessment_bindings:
            item["targeted_outcomes"] = parse_json(item.pop("targeted_outcomes_json", None), [])

        form_ids = {f["form_id"] for f in forms}
        activity_ids = {a["activity_id"] for a in activities}
        outcome_codes = {o["outcome_code"] for o in outcomes}
        source_locators = sorted(set(
            parse_json(block["source_locators_json"], [])
            + parse_json(block["timeline_source_locators"], [])
            + [o["source_locator"] for o in outcomes if o.get("source_locator")]
        ))

        return {
            "context_type": "TYMM_LESSON_PLAN_CONTEXT",
            "context_version": CONTEXT_VERSION,
            "resolution_status": "RESOLVED",
            "course": {
                "course_id": block["course_id"],
                "grade": block["grade"],
                "title": block["course_title"],
            },
            "theme": {
                "theme_id": block["theme_id"],
                "theme_order": block["theme_order"],
                "title": block["theme_title"],
                "instruction_hours": block["theme_instruction_hours"],
                "school_based_hours": block["school_based_hours"],
                "school_based_hours_status": block["school_based_hours_status"],
            },
            "block": {
                "block_id": block["block_id"],
                "block_order": block["block_order"],
                "title": block["block_title"],
                "skill_domain": block["skill_domain"],
                "learning_area": block["learning_area"],
                "planned_hours": planned_hours,
                "time_status": block["time_status"],
            },
            "planning_request": {
                "requested_lesson_hours": requested_lesson_hours,
                "block_planned_hours": planned_hours,
                "remaining_block_hours_after_this_plan": planned_hours - requested_lesson_hours,
                "partial_block_plan": requested_lesson_hours < planned_hours,
                "calendar_binding_used": False,
            },
            "official_outcomes": outcomes,
            "textbook_activities": activities,
            "assessment_forms": forms,
            "theme_resource_decisions": resources,
            "assessment_task_bindings": assessment_bindings,
            "allowed_references": {
                "outcome_codes": sorted(outcome_codes),
                "activity_ids": sorted(activity_ids),
                "form_ids": sorted(form_ids),
            },
            "generation_contract": {
                "official_fact_fields_are_immutable": True,
                "effective_process_components_are_immutable": True,
                "process_component_origin_must_be_preserved": True,
                "do_not_invent_outcome_codes": True,
                "do_not_invent_textbook_pages_or_activity_ids": True,
                "do_not_claim_generated_pedagogy_is_MEB_approved": True,
                "calendar_dates_are_out_of_scope": True,
                "lesson_duration_must_equal_requested_lesson_hours": True,
                "partial_block_sequence_is_pedagogical_generation_not_official_subhour_sequence": True,
                "prefer_reuse_of_textbook_activities_before_new_material": True,
            },
            "provenance": {
                "runtime_validation_status": manifest.get("validation_status"),
                "runtime_fingerprint": manifest.get("canonical_content_fingerprint"),
                "timeline_resolution": manifest.get("timeline_resolution"),
                "process_component_resolution_status": manifest.get("process_component_resolution_status"),
                "process_component_counts": manifest.get("process_component_counts"),
                "source_locators": source_locators,
            },
        }
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", required=True)
    parser.add_argument("--block-id", required=True)
    parser.add_argument("--lesson-hours", type=int)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        context = assemble(Path(args.knowledge_root), args.block_id, args.lesson_hours)
    except (ValueError, sqlite3.Error, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    payload = json.dumps(context, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
