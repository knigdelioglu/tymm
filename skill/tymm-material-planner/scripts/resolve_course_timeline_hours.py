#!/usr/bin/env python3
"""Resolve calendar-neutral block hours into planning/course_timeline.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve(root: Path) -> dict[str, Any]:
    root = root.resolve()
    timeline_path = root / "planning/course_timeline.json"
    binding_path = root / "planning/block_hour_bindings.json"
    topic_path = root / "planning/official_topic_hour_distribution.json"
    if not timeline_path.exists():
        raise ValueError(f"COURSE_TIMELINE_MISSING: {timeline_path}")
    if not binding_path.exists():
        raise ValueError(f"BLOCK_HOUR_BINDINGS_MISSING: {binding_path}")
    if not topic_path.exists():
        raise ValueError(f"TOPIC_HOUR_DISTRIBUTION_MISSING: {topic_path}")

    timeline = read_json(timeline_path)
    bindings_doc = read_json(binding_path)
    topics = read_json(topic_path)
    if bindings_doc.get("status") != "BLOCK_TIME_RESOLVED":
        raise ValueError(f"BLOCK_HOUR_BINDINGS_NOT_RESOLVED: {bindings_doc.get('status')}")
    if topics.get("status") != "READY":
        raise ValueError(f"TOPIC_HOUR_DISTRIBUTION_NOT_READY: {topics.get('status')}")
    if topics.get("calendar_exclusion_policy", {}).get("calendar_fields_ingested") is not False:
        raise ValueError("CALENDAR_NEUTRALITY_VIOLATION: calendar fields must remain excluded")

    topic_theme_by_id = {theme.get("theme_id"): theme for theme in topics.get("themes", [])}
    if len(topic_theme_by_id) != len(topics.get("themes", [])):
        raise ValueError("DUPLICATE_TOPIC_THEME_ID")

    # Canonical hour envelope is curriculum-defined, not calendar-derived.
    # Annual-plan week/date placement may contain residual rows, but those rows
    # must be excluded before this artifact reaches the timeline resolver.
    time_semantics = topics.get("time_semantics", {})
    normative_instruction_per_theme = time_semantics.get("normative_instruction_hours_per_theme")
    normative_school_based_per_theme = time_semantics.get("normative_school_based_planning_hours_per_theme")
    normative_total_per_theme = time_semantics.get("normative_total_hours_per_theme")
    if not isinstance(normative_instruction_per_theme, int) or isinstance(normative_instruction_per_theme, bool) or normative_instruction_per_theme <= 0:
        raise ValueError(f"INVALID_NORMATIVE_INSTRUCTION_HOURS_PER_THEME: {normative_instruction_per_theme}")
    if not isinstance(normative_school_based_per_theme, int) or isinstance(normative_school_based_per_theme, bool) or normative_school_based_per_theme < 0:
        raise ValueError(f"INVALID_NORMATIVE_SCHOOL_BASED_HOURS_PER_THEME: {normative_school_based_per_theme}")
    expected_outer_total = normative_instruction_per_theme + normative_school_based_per_theme
    if normative_total_per_theme != expected_outer_total:
        raise ValueError(f"INVALID_NORMATIVE_THEME_TOTAL: {normative_total_per_theme}!={expected_outer_total}")

    for topic_theme in topics.get("themes", []):
        tid = topic_theme.get("theme_id")
        theme_instruction = topic_theme.get("normative_instruction_hours")
        school_based = topic_theme.get("school_based_planning_hours")
        official_total = topic_theme.get("official_total_hours")
        declared_topic_total = topic_theme.get("source_planning_weight_total")
        if theme_instruction != normative_instruction_per_theme:
            raise ValueError(
                f"THEME_NORMATIVE_INSTRUCTION_HOURS_MISMATCH: {tid} {theme_instruction}!={normative_instruction_per_theme}"
            )
        if school_based != normative_school_based_per_theme:
            raise ValueError(
                f"THEME_SCHOOL_BASED_HOURS_MISMATCH: {tid} {school_based}!={normative_school_based_per_theme}"
            )
        if official_total != expected_outer_total:
            raise ValueError(f"THEME_OFFICIAL_TOTAL_HOURS_MISMATCH: {tid} {official_total}!={expected_outer_total}")

        allocation_total = 0
        for allocation in topic_theme.get("topic_allocations", []):
            hours = allocation.get("source_planning_weight_hours")
            if not isinstance(hours, int) or isinstance(hours, bool) or hours <= 0:
                raise ValueError(f"INVALID_TOPIC_ALLOCATION_HOURS: {tid} {allocation}")
            allocation_total += hours
        if declared_topic_total != allocation_total:
            raise ValueError(
                f"TOPIC_ALLOCATION_TOTAL_MISMATCH: {tid} {allocation_total}!={declared_topic_total}"
            )
        if allocation_total != normative_instruction_per_theme:
            raise ValueError(
                f"CALENDAR_RESIDUAL_NOT_EXCLUDED: {tid} {allocation_total}!={normative_instruction_per_theme}"
            )

    binding_by_id: dict[str, dict[str, Any]] = {}
    theme_binding: dict[str, dict[str, Any]] = {}
    for theme in bindings_doc.get("themes", []):
        tid = theme.get("theme_id")
        theme_binding[tid] = theme
        expected = theme.get("normative_total_hours")
        actual = 0
        for binding in theme.get("bindings", []):
            bid = binding.get("block_id")
            hours = binding.get("planned_hours")
            if not bid or not isinstance(hours, int) or isinstance(hours, bool) or hours <= 0:
                raise ValueError(f"INVALID_BLOCK_HOUR_BINDING: {tid} {binding}")
            if bid in binding_by_id:
                raise ValueError(f"DUPLICATE_BLOCK_HOUR_BINDING: {bid}")
            binding_by_id[bid] = {**binding, "theme_id": tid}
            actual += hours
        if expected is not None and actual != expected:
            raise ValueError(f"THEME_HOUR_TOTAL_MISMATCH: {tid} {actual} != {expected}")

    instructional_total = bindings_doc.get("validation", {}).get("annual_instruction_hours")
    if instructional_total is None:
        instructional_total = sum(int(x.get("normative_total_hours") or 0) for x in bindings_doc.get("themes", []))

    # School-based planning hours belong to the official topic-hour distribution,
    # not block_hour_bindings. The previous resolver incorrectly expected this
    # field on binding themes and therefore failed closed even though the source
    # artifact already contained the verified 2h/theme distribution.
    school_based_by_theme: dict[str, int] = {}
    for binding_theme in bindings_doc.get("themes", []):
        tid = binding_theme.get("theme_id")
        topic_theme = topic_theme_by_id.get(tid)
        if topic_theme is None:
            raise ValueError(f"TOPIC_THEME_MISSING_FOR_BINDING: {tid}")
        value = topic_theme.get("school_based_planning_hours")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"INVALID_SCHOOL_BASED_HOUR_DISTRIBUTION: {tid}={value}")
        school_based_by_theme[tid] = value

    school_based_values = list(school_based_by_theme.values())
    school_based_total = sum(school_based_values)
    school_based_unique = set(school_based_values)
    school_based_per_theme = next(iter(school_based_unique)) if len(school_based_unique) == 1 else None
    annual_total = instructional_total + school_based_total

    timeline["timeline_version"] = "1.1.3"
    timeline["timeline_resolution"] = "BLOCK_TIME_RESOLVED"
    semantics = timeline.setdefault("timeline_semantics", {})
    semantics["calendar_neutral_topic_hour_distribution"] = True
    semantics["calendar_fields_intentionally_excluded"] = True
    semantics["calendar_residual_hours_excluded_before_resolution"] = True

    source_basis = timeline.setdefault("source_basis", {})
    authority = list(source_basis.get("authority_order", []))
    for source in ["planning/block_hour_bindings.json", "planning/official_topic_hour_distribution.json"]:
        if source not in authority:
            authority.append(source)
    source_basis["authority_order"] = authority
    source_basis["hours_source"] = "curriculum_map.json + planning/block_hour_bindings.json"
    source_basis["block_hours_source"] = "planning/block_hour_bindings.json"
    source_basis["calendar_source"] = None
    source_basis["provenance_status"] = "PASS_CALENDAR_NEUTRAL_BLOCK_TIME_RESOLVED"
    audit = source_basis.setdefault("temporal_fact_audit", {})
    audit["annual_instructional_hours"] = {
        "value": instructional_total,
        "source": "curriculum_map.json + planning/block_hour_bindings.json",
        "source_locator": "43 saat x 4 tema",
        "status": "EXPLICIT_OFFICIAL_AND_RECONCILED",
    }
    audit["annual_school_based_hours"] = {
        "value": school_based_total,
        "source": "planning/official_topic_hour_distribution.json",
        "source_locator": "Her temadaki okul temelli planlama satırları; takvim alanları hariç",
        "status": "OFFICIAL_DRAFT_ANNUAL_PLAN_PLANNING_GUIDANCE",
    }
    audit["annual_total_hours"] = {
        "value": annual_total,
        "source": "curriculum_map.json + planning/official_topic_hour_distribution.json",
        "source_locator": f"{instructional_total}+{school_based_total}",
        "status": "DETERMINISTIC_RECONCILIATION",
    }
    audit["school_based_hours_per_theme"] = {
        "value": school_based_per_theme,
        "source": "planning/official_topic_hour_distribution.json",
        "source_locator": "Tema bazlı okul temelli planlama satırları",
        "status": "OFFICIAL_DRAFT_ANNUAL_PLAN_PLANNING_GUIDANCE" if school_based_per_theme is not None else "UNRESOLVED",
    }
    if school_based_per_theme is not None:
        audit["outer_theme_total_hours"] = {
            "value": normative_instruction_per_theme + school_based_per_theme,
            "source": "curriculum_map.json + planning/official_topic_hour_distribution.json",
            "status": "DETERMINISTIC_RECONCILIATION",
        }
    audit["block_specific_official_hours"] = {
        "value": {bid: binding["planned_hours"] for bid, binding in sorted(binding_by_id.items())},
        "source": "planning/block_hour_bindings.json",
        "source_locator": "MEB taslak yıllık plan konu/saat dağılımı; takvim alanları ve haftalık yerleşim artıkları hariç",
        "status": "OFFICIAL_DRAFT_ANNUAL_PLAN_DERIVED_CALENDAR_NEUTRAL",
    }
    audit["weekly_lesson_hours"] = {
        "value": None,
        "source": None,
        "source_locator": None,
        "status": "UNRESOLVED",
        "note": "Haftalık/tarihsel takvim yerleşimi bu canonical katmana alınmaz.",
    }
    audit["academic_year_week_mapping"] = {
        "value": None,
        "source": None,
        "source_locator": None,
        "status": "UNRESOLVED",
        "note": "Ara tatil, yarıyıl, resmî tatil ve tarih aralıkları bilinçli olarak dışarıda tutulur.",
    }

    timeline["annual_hours"] = {
        "core_instruction_hours": instructional_total,
        "school_based_hours": school_based_total,
        "official_total_hours": annual_total,
        "time_status": "CALENDAR_NEUTRAL_RECONCILED",
        "source_locators": [
            "curriculum_map.json",
            "planning/official_topic_hour_distribution.json",
            "planning/block_hour_bindings.json",
        ],
    }

    seen: set[str] = set()
    for theme in timeline.get("themes", []):
        tid = theme.get("theme_id")
        source_theme = theme_binding.get(tid)
        if source_theme is None:
            raise ValueError(f"TIMELINE_THEME_WITHOUT_BINDINGS: {tid}")
        expected_total = source_theme.get("normative_total_hours")
        school_based = school_based_by_theme.get(tid)
        if school_based is None:
            raise ValueError(f"TIMELINE_THEME_WITHOUT_SCHOOL_BASED_HOURS: {tid}")
        theme["official_total_hours"] = expected_total
        theme["core_instruction_hours"] = expected_total
        theme["block_resolution_status"] = "BLOCK_TIME_RESOLVED"
        theme["school_based_hours"] = school_based
        theme["school_based_hours_status"] = "OFFICIAL_DRAFT_ANNUAL_PLAN_PLANNING_GUIDANCE"
        theme["outer_total_hours"] = expected_total + school_based
        locators = list(theme.get("source_locators", []))
        for locator in [
            f"planning/block_hour_bindings.json#{tid}",
            f"planning/official_topic_hour_distribution.json#{tid}",
        ]:
            if locator not in locators:
                locators.append(locator)
        theme["source_locators"] = locators

        actual_total = 0
        for block in theme.get("blocks", []):
            bid = block.get("block_id")
            binding = binding_by_id.get(bid)
            if binding is None:
                raise ValueError(f"TIMELINE_BLOCK_WITHOUT_BINDING: {bid}")
            if binding.get("theme_id") != tid:
                raise ValueError(f"TIMELINE_BLOCK_THEME_MISMATCH: {bid}")
            block["planned_hours"] = binding["planned_hours"]
            block["time_status"] = "OFFICIAL_ANNUAL_PLAN_DERIVED"
            block["skill_domain"] = binding.get("domain")
            block["hour_resolution"] = binding.get("resolution")
            locators = list(block.get("source_locators", []))
            locator = f"planning/block_hour_bindings.json#{tid}.{bid}"
            if locator not in locators:
                locators.append(locator)
            block["source_locators"] = locators
            actual_total += binding["planned_hours"]
            seen.add(bid)
        if actual_total != expected_total:
            raise ValueError(f"TIMELINE_THEME_TOTAL_MISMATCH: {tid} {actual_total} != {expected_total}")

    unknown = set(binding_by_id) - seen
    if unknown:
        raise ValueError(f"UNUSED_BLOCK_HOUR_BINDINGS: {sorted(unknown)}")

    calendar = timeline.setdefault("calendar_binding", {})
    calendar["status"] = "UNRESOLVED"
    calendar["academic_year"] = None
    calendar["weekly_lesson_hours"] = None
    calendar["calendar_specific_fields_ingested"] = False
    calendar["excluded_fields"] = [
        "ay",
        "hafta/tarih aralığı",
        "ara tatil",
        "yarıyıl tatili",
        "belirli gün ve haftalar",
        "resmî tatil yerleşimi",
        "haftalık yerleşimden doğan artık ders saati satırları",
    ]

    write_json(timeline_path, timeline)
    return {
        "status": "PASS",
        "course_id": timeline.get("course_id"),
        "timeline_resolution": timeline.get("timeline_resolution"),
        "resolved_blocks": len(seen),
        "theme_totals": {
            theme.get("theme_id"): sum(block.get("planned_hours", 0) for block in theme.get("blocks", []))
            for theme in timeline.get("themes", [])
        },
        "annual_instructional_hours": instructional_total,
        "annual_school_based_hours": school_based_total,
        "annual_total_hours": annual_total,
        "calendar_binding": calendar.get("status"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", required=True)
    args = parser.parse_args()
    try:
        result = resolve(Path(args.knowledge_root))
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
