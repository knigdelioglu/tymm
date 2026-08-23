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

    timeline["timeline_version"] = "1.1.0"
    timeline["timeline_resolution"] = "BLOCK_TIME_RESOLVED"
    semantics = timeline.setdefault("timeline_semantics", {})
    semantics["calendar_neutral_topic_hour_distribution"] = True
    semantics["calendar_fields_intentionally_excluded"] = True

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
    audit["block_specific_official_hours"] = {
        "value": {bid: binding["planned_hours"] for bid, binding in sorted(binding_by_id.items())},
        "source": "planning/block_hour_bindings.json",
        "source_locator": "MEB taslak yıllık plan konu/saat dağılımı; takvim alanları hariç",
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

    seen: set[str] = set()
    for theme in timeline.get("themes", []):
        tid = theme.get("theme_id")
        source_theme = theme_binding.get(tid)
        if source_theme is None:
            raise ValueError(f"TIMELINE_THEME_WITHOUT_BINDINGS: {tid}")
        expected_total = source_theme.get("normative_total_hours")
        theme["official_total_hours"] = expected_total
        theme["core_instruction_hours"] = expected_total
        theme["block_resolution_status"] = "BLOCK_TIME_RESOLVED"
        if source_theme.get("school_based_planning_hours") is not None:
            theme["school_based_hours"] = source_theme.get("school_based_planning_hours")
            theme["school_based_hours_status"] = "OFFICIAL_DRAFT_ANNUAL_PLAN_PLANNING_GUIDANCE"
            theme["outer_total_hours"] = expected_total + source_theme.get("school_based_planning_hours")
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
