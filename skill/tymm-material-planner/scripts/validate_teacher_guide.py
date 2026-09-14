#!/usr/bin/env python3
"""Validate a TYMM teacher-guide manifest and its section sources.

The validator treats the official curriculum as normative for outcomes and the
local official textbook PDF/textbook_map pair as authoritative for textbook
structure. Implementation lesson plans are checked against textbook activity
outcomes, but explicitly registered upstream conflicts are emitted as warnings
rather than silently accepted or allowed to corrupt the guide.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - CI dependency gate
    raise SystemExit("jsonschema is required: pip install jsonschema==4.23.0") from exc


PAGE_RANGE_RE = re.compile(r"^\s*(\d+)\s*(?:[-–—]\s*(\d+)\s*)?$")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path) or "$"
    return f"{location}: {error.message}"


def parse_page_range(value: str) -> tuple[int, int]:
    match = PAGE_RANGE_RE.match(value)
    if not match:
        raise ValueError(f"invalid printed_page_range: {value!r}")
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        raise ValueError(f"descending printed_page_range: {value!r}")
    return start, end


def iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def collect_textbook_activities(textbook_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    activities: dict[str, dict[str, Any]] = {}
    for node in iter_dicts(textbook_map):
        activity_id = node.get("activity_id")
        if not isinstance(activity_id, str) or not activity_id:
            continue
        outcomes = set(normalize_string_list(node.get("related_outcomes")))
        outcomes.update(normalize_string_list(node.get("outcome_codes")))
        pages = node.get("printed_page_range") or node.get("printed_page")
        existing = activities.setdefault(activity_id, {"outcomes": set(), "pages": set()})
        existing["outcomes"].update(outcomes)
        if isinstance(pages, (str, int)):
            existing["pages"].add(str(pages))
    return activities


def add_problem(target: list[dict[str, Any]], code: str, message: str, *, path: str | None = None) -> None:
    problem: dict[str, Any] = {"code": code, "message": message}
    if path:
        problem["path"] = path
    target.append(problem)


def validate_provenance_sources(
    section: dict[str, Any],
    source_ids: set[str],
    failures: list[dict[str, Any]],
    section_path: str,
) -> None:
    for node in iter_dicts(section):
        provenance = node.get("provenance")
        if not isinstance(provenance, dict):
            continue
        for source_id in normalize_string_list(provenance.get("source_ids")):
            if source_id not in source_ids:
                add_problem(
                    failures,
                    "UNKNOWN_PROVENANCE_SOURCE",
                    f"provenance source_id {source_id!r} is not declared in source_manifest",
                    path=section_path,
                )


def validate_page_nesting(
    section: dict[str, Any],
    failures: list[dict[str, Any]],
    section_path: str,
) -> None:
    try:
        section_start, section_end = parse_page_range(str(section["printed_page_range"]))
    except (KeyError, ValueError) as exc:
        add_problem(failures, "INVALID_SECTION_PAGE_RANGE", str(exc), path=section_path)
        return

    for unit in section.get("guide_units", []):
        try:
            unit_start, unit_end = parse_page_range(str(unit["printed_page_range"]))
        except (KeyError, ValueError) as exc:
            add_problem(failures, "INVALID_UNIT_PAGE_RANGE", str(exc), path=section_path)
            continue
        if unit_start < section_start or unit_end > section_end:
            add_problem(
                failures,
                "UNIT_OUTSIDE_SECTION_PAGE_RANGE",
                f"unit {unit.get('unit_id')} pages {unit_start}-{unit_end} outside section {section_start}-{section_end}",
                path=section_path,
            )
        for item in unit.get("items", []):
            item_range = item.get("printed_page_range")
            if not isinstance(item_range, str):
                continue
            try:
                item_start, item_end = parse_page_range(item_range)
            except ValueError as exc:
                add_problem(failures, "INVALID_ITEM_PAGE_RANGE", str(exc), path=section_path)
                continue
            if item_start < unit_start or item_end > unit_end:
                add_problem(
                    failures,
                    "ITEM_OUTSIDE_UNIT_PAGE_RANGE",
                    f"item {item.get('item_id')} pages {item_start}-{item_end} outside unit {unit_start}-{unit_end}",
                    path=section_path,
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--manifest",
        default="courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json",
    )
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest_path = (repo_root / args.manifest).resolve()
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    manifest = read_json(manifest_path)
    manifest_schema_path = repo_root / "skill/tymm-material-planner/schemas/teacher_guide.schema.json"
    section_schema_path = repo_root / manifest["content_storage"]["section_schema_path"]
    manifest_validator = Draft202012Validator(read_json(manifest_schema_path))
    section_validator = Draft202012Validator(read_json(section_schema_path))

    for error in sorted(manifest_validator.iter_errors(manifest), key=lambda e: list(e.absolute_path)):
        add_problem(failures, "MANIFEST_SCHEMA", format_schema_error(error), path=args.manifest)

    source_manifest = manifest.get("source_manifest", [])
    source_ids = {
        source.get("source_id")
        for source in source_manifest
        if isinstance(source, dict) and isinstance(source.get("source_id"), str)
    }
    source_ids.discard(None)

    textbook_pdf_source = next(
        (source for source in source_manifest if source.get("source_id") == "official_textbook_pdf"),
        None,
    )
    if not textbook_pdf_source:
        add_problem(failures, "OFFICIAL_TEXTBOOK_PDF_SOURCE_MISSING", "official_textbook_pdf source is required")
    else:
        pdf_path = repo_root / textbook_pdf_source["path"]
        if not pdf_path.is_file():
            add_problem(failures, "OFFICIAL_TEXTBOOK_PDF_FILE_MISSING", str(pdf_path.relative_to(repo_root)))

    for source in source_manifest:
        if not isinstance(source, dict):
            continue
        source_path = source.get("path")
        if not isinstance(source_path, str) or source_path.startswith("library:"):
            continue
        if not (repo_root / source_path).exists():
            add_problem(
                failures,
                "SOURCE_REFERENCE_MISSING",
                f"source path does not exist: {source_path}",
                path=args.manifest,
            )

    textbook_map_source = next(
        (source for source in source_manifest if source.get("source_id") == "textbook_map"),
        None,
    )
    if not textbook_map_source:
        add_problem(failures, "TEXTBOOK_MAP_SOURCE_MISSING", "textbook_map source is required")
        textbook_activities: dict[str, dict[str, Any]] = {}
    else:
        textbook_map = read_json(repo_root / textbook_map_source["path"])
        textbook_activities = collect_textbook_activities(textbook_map)

    try:
        theme_start, theme_end = parse_page_range(manifest["theme_overview"]["printed_page_range"])
    except (KeyError, ValueError) as exc:
        add_problem(failures, "INVALID_THEME_PAGE_RANGE", str(exc), path=args.manifest)
        theme_start, theme_end = 0, 10**9

    known_issues = manifest.get("known_issues", [])
    registered_conflict_refs: set[str] = set()
    for issue in known_issues:
        if not isinstance(issue, dict):
            continue
        if issue.get("status") == "OPEN" and "OUTCOME_MISMATCH" in str(issue.get("issue_id", "")):
            registered_conflict_refs.update(normalize_string_list(issue.get("source_refs")))

    item_ids: set[str] = set()
    unit_ids: set[str] = set()
    all_outcomes: set[str] = set()
    block_hours: dict[str, int] = {}
    loaded_plan_paths: set[str] = set()
    sections_checked = 0

    for section_index in manifest.get("sections", []):
        content_ref = section_index.get("content_ref")
        if not isinstance(content_ref, str):
            add_problem(failures, "SECTION_CONTENT_REF_INVALID", repr(content_ref), path=args.manifest)
            continue
        section_path = repo_root / content_ref
        if not section_path.is_file():
            add_problem(failures, "SECTION_CONTENT_REF_MISSING", content_ref, path=args.manifest)
            continue

        section = read_json(section_path)
        sections_checked += 1
        for error in sorted(section_validator.iter_errors(section), key=lambda e: list(e.absolute_path)):
            add_problem(failures, "SECTION_SCHEMA", format_schema_error(error), path=content_ref)

        for field in ("section_id", "title", "section_type", "printed_page_range", "content_status"):
            if section.get(field) != section_index.get(field):
                add_problem(
                    failures,
                    "SECTION_MANIFEST_MISMATCH",
                    f"{field}: manifest={section_index.get(field)!r}, section={section.get(field)!r}",
                    path=content_ref,
                )
        for field in ("outcome_refs", "activity_refs", "lesson_plan_refs"):
            if set(normalize_string_list(section.get(field))) != set(normalize_string_list(section_index.get(field))):
                add_problem(
                    failures,
                    "SECTION_MANIFEST_SET_MISMATCH",
                    f"{field} differs between manifest and section source",
                    path=content_ref,
                )

        validate_provenance_sources(section, source_ids, failures, content_ref)
        validate_page_nesting(section, failures, content_ref)

        try:
            section_start, section_end = parse_page_range(section["printed_page_range"])
            if section_start < theme_start or section_end > theme_end:
                add_problem(
                    failures,
                    "SECTION_OUTSIDE_THEME_PAGE_RANGE",
                    f"section pages {section_start}-{section_end} outside theme {theme_start}-{theme_end}",
                    path=content_ref,
                )
        except (KeyError, ValueError):
            pass

        section_outcomes = set(normalize_string_list(section.get("outcome_refs")))
        all_outcomes.update(section_outcomes)
        for activity_id in normalize_string_list(section.get("activity_refs")):
            official = textbook_activities.get(activity_id)
            if not official:
                add_problem(failures, "UNKNOWN_TEXTBOOK_ACTIVITY", activity_id, path=content_ref)
                continue
            official_outcomes = set(official["outcomes"])
            if official_outcomes and not official_outcomes.issubset(section_outcomes):
                add_problem(
                    failures,
                    "SECTION_ACTIVITY_OUTCOME_MISMATCH",
                    f"{activity_id}: official={sorted(official_outcomes)}, section={sorted(section_outcomes)}",
                    path=content_ref,
                )

        for unit in section.get("guide_units", []):
            unit_id = unit.get("unit_id")
            if isinstance(unit_id, str):
                if unit_id in unit_ids:
                    add_problem(failures, "DUPLICATE_UNIT_ID", unit_id, path=content_ref)
                unit_ids.add(unit_id)
            unit_outcomes = set(normalize_string_list(unit.get("outcome_refs")))
            for activity_id in normalize_string_list(unit.get("activity_refs")):
                official = textbook_activities.get(activity_id)
                if not official:
                    add_problem(failures, "UNKNOWN_UNIT_ACTIVITY", activity_id, path=content_ref)
                    continue
                official_outcomes = set(official["outcomes"])
                if official_outcomes and unit_outcomes and not unit_outcomes.issubset(official_outcomes):
                    add_problem(
                        failures,
                        "UNIT_ACTIVITY_OUTCOME_MISMATCH",
                        f"{unit_id}/{activity_id}: unit={sorted(unit_outcomes)}, official={sorted(official_outcomes)}",
                        path=content_ref,
                    )
            for item in unit.get("items", []):
                item_id = item.get("item_id")
                if isinstance(item_id, str):
                    if item_id in item_ids:
                        add_problem(failures, "DUPLICATE_ITEM_ID", item_id, path=content_ref)
                    item_ids.add(item_id)

        block_id = section_index.get("block_id")
        hours = section_index.get("block_hours")
        if isinstance(block_id, str) and isinstance(hours, int):
            existing = block_hours.get(block_id)
            if existing is not None and existing != hours:
                add_problem(
                    failures,
                    "BLOCK_HOUR_CONFLICT",
                    f"{block_id}: {existing} vs {hours}",
                    path=args.manifest,
                )
            block_hours[block_id] = hours

        for plan_ref in normalize_string_list(section.get("lesson_plan_refs")):
            if plan_ref in loaded_plan_paths:
                continue
            loaded_plan_paths.add(plan_ref)
            plan_path = repo_root / plan_ref
            if not plan_path.is_file():
                add_problem(failures, "LESSON_PLAN_REF_MISSING", plan_ref, path=content_ref)
                continue
            plan = read_json(plan_path)
            plan_outcomes = set(normalize_string_list(plan.get("outcome_codes")))
            for activity_id in normalize_string_list(plan.get("used_activity_ids")):
                official = textbook_activities.get(activity_id)
                if not official or not official["outcomes"]:
                    continue
                official_outcomes = set(official["outcomes"])
                if plan_outcomes.isdisjoint(official_outcomes):
                    message = (
                        f"{plan_ref}: {activity_id} plan outcomes={sorted(plan_outcomes)} "
                        f"official outcomes={sorted(official_outcomes)}"
                    )
                    if plan_ref in registered_conflict_refs:
                        add_problem(warnings, "REGISTERED_LESSON_PLAN_OUTCOME_MISMATCH", message, path=plan_ref)
                    else:
                        add_problem(failures, "UNREGISTERED_LESSON_PLAN_OUTCOME_MISMATCH", message, path=plan_ref)

    expected_section_count = manifest.get("theme_overview", {}).get("target_section_count")
    if isinstance(expected_section_count, int) and sections_checked != expected_section_count:
        add_problem(
            failures,
            "SECTION_COUNT_MISMATCH",
            f"expected {expected_section_count}, loaded {sections_checked}",
            path=args.manifest,
        )

    expected_outcome_count = manifest.get("theme_overview", {}).get("outcome_count")
    if isinstance(expected_outcome_count, int) and len(all_outcomes) != expected_outcome_count:
        add_problem(
            failures,
            "OUTCOME_COVERAGE_COUNT_MISMATCH",
            f"expected {expected_outcome_count} unique outcomes, found {len(all_outcomes)}: {sorted(all_outcomes)}",
            path=args.manifest,
        )

    expected_hours = manifest.get("theme_overview", {}).get("core_instruction_hours")
    actual_hours = sum(block_hours.values())
    if isinstance(expected_hours, int) and actual_hours != expected_hours:
        add_problem(
            failures,
            "CORE_HOUR_TOTAL_MISMATCH",
            f"expected {expected_hours}, unique block total {actual_hours}: {block_hours}",
            path=args.manifest,
        )

    for issue in known_issues:
        if not isinstance(issue, dict) or issue.get("status") != "OPEN":
            continue
        severity = issue.get("severity")
        if severity in {"WARNING", "ERROR"}:
            add_problem(
                warnings,
                "OPEN_KNOWN_ISSUE",
                f"{issue.get('issue_id')}: {issue.get('description')}",
                path=args.manifest,
            )

    status = "FAIL" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    report = {
        "schema_version": "1.0",
        "manifest": args.manifest,
        "status": status,
        "sections_checked": sections_checked,
        "unique_item_ids": len(item_ids),
        "unique_unit_ids": len(unit_ids),
        "outcomes_covered": sorted(all_outcomes),
        "unique_block_hours": block_hours,
        "core_instruction_hours": actual_hours,
        "failures": failures,
        "warnings": warnings,
    }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
