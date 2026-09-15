#!/usr/bin/env python3
"""Validate a pedagogy-first TYMM teacher-guide overlay.

The legacy teacher-guide validator protects source/page/outcome integrity. This
validator protects the teacher-facing layer: every canonical guide item must be
covered, teacher moves must be actionable, board notes must be explicitly
marked, and no dangling source item/section references are allowed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover
    raise SystemExit("jsonschema is required: pip install jsonschema==4.23.0") from exc

PAGE_RANGE_RE = re.compile(r"^\s*(\d+)\s*(?:[-–—]\s*(\d+)\s*)?$")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_range(value: str) -> tuple[int, int]:
    match = PAGE_RANGE_RE.match(value)
    if not match:
        raise ValueError(value)
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        raise ValueError(value)
    return start, end


def intersects(a: str, b: str) -> bool:
    a0, a1 = parse_range(a)
    b0, b1 = parse_range(b)
    return max(a0, b0) <= min(a1, b1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--overlay",
        default="courses/TDE_11/teacher_guide/TEMA_01/pedagogy_v2.json",
    )
    parser.add_argument(
        "--manifest",
        default="courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json",
    )
    parser.add_argument(
        "--schema",
        default="skill/tymm-material-planner/schemas/teacher_guide_pedagogy_overlay.schema.json",
    )
    args = parser.parse_args()

    root = args.repo_root.resolve()
    overlay_path = root / args.overlay
    manifest_path = root / args.manifest
    schema_path = root / args.schema

    failures: list[str] = []
    warnings: list[str] = []

    for path, label in (
        (overlay_path, "overlay"),
        (manifest_path, "manifest"),
        (schema_path, "schema"),
    ):
        if not path.is_file():
            failures.append(f"MISSING_{label.upper()}: {path}")

    if failures:
        print(json.dumps({"status": "FAIL", "failures": failures}, ensure_ascii=False, indent=2))
        return 1

    overlay = read_json(overlay_path)
    manifest = read_json(manifest_path)
    schema = read_json(schema_path)

    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(overlay), key=lambda e: list(e.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        failures.append(f"SCHEMA:{location}: {error.message}")

    if overlay.get("course_id") != manifest.get("course_id"):
        failures.append("COURSE_ID_MISMATCH")
    if overlay.get("theme_id") != manifest.get("theme_id"):
        failures.append("THEME_ID_MISMATCH")

    canonical_items: dict[str, dict[str, Any]] = {}
    canonical_sections: set[str] = set()

    for section_index in manifest.get("sections", []):
        section_id = section_index.get("section_id")
        content_ref = section_index.get("content_ref")
        if not isinstance(section_id, str) or not isinstance(content_ref, str):
            failures.append(f"INVALID_MANIFEST_SECTION: {section_index!r}")
            continue
        section_path = root / content_ref
        if not section_path.is_file():
            failures.append(f"MISSING_SECTION: {content_ref}")
            continue
        section = read_json(section_path)
        canonical_sections.add(section_id)
        for unit in section.get("guide_units", []):
            for item in unit.get("items", []):
                item_id = item.get("item_id")
                if not isinstance(item_id, str) or not item_id:
                    failures.append(f"ITEM_WITHOUT_ID: {content_ref}")
                    continue
                if item_id in canonical_items:
                    failures.append(f"DUPLICATE_CANONICAL_ITEM: {item_id}")
                    continue
                canonical_items[item_id] = {
                    "section_id": section_id,
                    "printed_page_range": item.get("printed_page_range"),
                    "item_type": item.get("item_type"),
                }

    refs: list[str] = []
    blocks = overlay.get("blocks", []) if isinstance(overlay.get("blocks"), list) else []
    block_ids: set[str] = set()

    for block in blocks:
        if not isinstance(block, dict):
            failures.append("INVALID_BLOCK_OBJECT")
            continue
        block_id = block.get("block_id")
        section_id = block.get("section_id")
        page_range = block.get("printed_page_range")
        if isinstance(block_id, str):
            if block_id in block_ids:
                failures.append(f"DUPLICATE_BLOCK_ID: {block_id}")
            block_ids.add(block_id)
        if section_id not in canonical_sections:
            failures.append(f"UNKNOWN_SECTION_REF:{block_id}:{section_id}")

        teacher_moves = block.get("teacher_moves", [])
        if not isinstance(teacher_moves, list) or not teacher_moves:
            failures.append(f"TEACHER_MOVES_REQUIRED:{block_id}")
        followups = block.get("follow_up_questions", [])
        if not isinstance(followups, list) or not followups:
            warnings.append(f"NO_FOLLOW_UP_QUESTIONS:{block_id}")
        interventions = block.get("misconception_interventions", [])
        if not isinstance(interventions, list) or not interventions:
            warnings.append(f"NO_MISCONCEPTION_INTERVENTION:{block_id}")
        board_notes = block.get("board_notes", [])
        if isinstance(board_notes, list):
            for note in board_notes:
                if not isinstance(note, str) or not note.startswith("Tahtaya yaz:"):
                    failures.append(f"INVALID_BOARD_NOTE:{block_id}:{note!r}")

        source_refs = block.get("source_item_refs", [])
        if not isinstance(source_refs, list) or not source_refs:
            failures.append(f"SOURCE_ITEM_REFS_REQUIRED:{block_id}")
            continue
        for item_id in source_refs:
            if not isinstance(item_id, str):
                failures.append(f"INVALID_SOURCE_ITEM_REF:{block_id}:{item_id!r}")
                continue
            refs.append(item_id)
            canonical = canonical_items.get(item_id)
            if canonical is None:
                failures.append(f"UNKNOWN_SOURCE_ITEM_REF:{block_id}:{item_id}")
                continue
            if canonical["section_id"] != section_id:
                failures.append(
                    f"SOURCE_ITEM_SECTION_MISMATCH:{block_id}:{item_id}:"
                    f"{canonical['section_id']}!={section_id}"
                )
            item_pages = canonical.get("printed_page_range")
            if isinstance(page_range, str) and isinstance(item_pages, str):
                try:
                    if not intersects(page_range, item_pages):
                        failures.append(
                            f"SOURCE_ITEM_PAGE_MISMATCH:{block_id}:{item_id}:"
                            f"block={page_range}:item={item_pages}"
                        )
                except ValueError:
                    failures.append(f"INVALID_PAGE_RANGE:{block_id}:{page_range}:{item_pages}")

    counts = Counter(refs)
    missing = sorted(set(canonical_items) - set(refs))
    duplicated = sorted(item_id for item_id, count in counts.items() if count > 1)
    unknown = sorted(set(refs) - set(canonical_items))

    if missing:
        failures.append("UNCOVERED_CANONICAL_ITEMS: " + ", ".join(missing))
    if duplicated:
        failures.append("MULTI_COVERED_CANONICAL_ITEMS: " + ", ".join(duplicated))
    if unknown:
        failures.append("UNKNOWN_REFERENCED_ITEMS: " + ", ".join(unknown))

    # Quality gates: the overlay is intended to be a teacher guide, not merely
    # a content summary. Every block must contain assessment look-fors and both
    # support/enrichment arrays. Schema checks the shape; here we reject empty
    # values where they would make the guide pedagogically hollow.
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_id = block.get("block_id", "<unknown>")
        if not block.get("assessment_look_fors"):
            failures.append(f"ASSESSMENT_LOOK_FORS_REQUIRED:{block_id}")
        differentiation = block.get("differentiation")
        if not isinstance(differentiation, dict):
            failures.append(f"DIFFERENTIATION_REQUIRED:{block_id}")
            continue
        if not differentiation.get("support"):
            failures.append(f"SUPPORT_SCAFFOLD_REQUIRED:{block_id}")
        if not differentiation.get("enrichment"):
            failures.append(f"ENRICHMENT_REQUIRED:{block_id}")

    status = "FAIL" if failures else "PASS_WITH_WARNINGS" if warnings else "PASS"
    report = {
        "status": status,
        "course_id": overlay.get("course_id"),
        "theme_id": overlay.get("theme_id"),
        "canonical_item_count": len(canonical_items),
        "covered_item_count": len(set(refs) & set(canonical_items)),
        "block_count": len(blocks),
        "failures": failures,
        "warnings": warnings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
