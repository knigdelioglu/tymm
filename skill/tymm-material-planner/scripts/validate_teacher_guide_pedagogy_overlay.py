#!/usr/bin/env python3
"""Validate a pedagogy-first TYMM teacher-guide overlay.

V2.0 checks structural pedagogy coverage. V2.1 additionally protects the three
teacher-facing P0 contracts:
1) canonical answers are present in the teacher-facing task cards/Markdown,
2) bundled numbered questions are expanded into first-class question cards,
3) canonical item-level pedagogy fields are preserved instead of discarded.
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
QUESTION_RANGE_RE = re.compile(r"(?:^|_)Q(\d+)_(\d+)(?:_|$)")
LABEL_RANGE_RE = re.compile(r"(\d+)\s*[-–—]\s*(\d+)\.?\s*soru", re.IGNORECASE)


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


def is_nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def question_range(item: dict[str, Any]) -> tuple[int, int] | None:
    match = QUESTION_RANGE_RE.search(str(item.get("item_id", "")))
    if not match:
        match = LABEL_RANGE_RE.search(str(item.get("label", "")))
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    return (start, end) if end >= start else None


def split_expected_answers(item: dict[str, Any]) -> list[tuple[str, Any, str | None]] | None:
    if item.get("item_type") != "QUESTION":
        return None

    answer = item.get("expected_answer")
    if not is_nonempty(answer):
        answer = item.get("expected_response")
    if not is_nonempty(answer):
        return None

    if isinstance(answer, dict) and len(answer) > 1:
        keys = list(answer)
        if all(re.fullmatch(r"\d+", str(key)) for key in keys):
            ordered = sorted(((int(str(key)), str(key), answer[key]) for key in keys), key=lambda row: row[0])
            return [(key, value, None) for _, key, value in ordered]

    qr = question_range(item)
    if qr is None:
        return None
    start, end = qr
    count = end - start + 1
    numbers = [str(number) for number in range(start, end + 1)]

    if isinstance(answer, dict) and len(answer) == count:
        return [(number, value, str(key)) for number, (key, value) in zip(numbers, answer.items())]
    if isinstance(answer, list) and len(answer) == count:
        return [(number, value, None) for number, value in zip(numbers, answer)]
    return None


def expected_task_specs(item: dict[str, Any]) -> list[dict[str, Any]]:
    item_id = item["item_id"]
    split = split_expected_answers(item)
    if split:
        return [
            {
                "task_id": f"{item_id}#Q{number}",
                "question_number": number,
                "expected_answer": answer,
                "expected_response": None,
                "answer_component_key": component_key,
                "split_from_group": True,
            }
            for number, answer, component_key in split
        ]
    return [{
        "task_id": item_id,
        "question_number": None,
        "expected_answer": item.get("expected_answer"),
        "expected_response": item.get("expected_response"),
        "answer_component_key": None,
        "split_from_group": False,
    }]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--overlay", default="courses/TDE_11/teacher_guide/TEMA_01/pedagogy_v2.json")
    parser.add_argument("--manifest", default="courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json")
    parser.add_argument("--schema", default="skill/tymm-material-planner/schemas/teacher_guide_pedagogy_overlay.schema.json")
    parser.add_argument("--markdown", default=None, help="Teacher-facing Markdown. Defaults to TEACHER_GUIDE_V2.md next to overlay.")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    overlay_path = root / args.overlay
    manifest_path = root / args.manifest
    schema_path = root / args.schema
    markdown_path = root / args.markdown if args.markdown else overlay_path.with_name("TEACHER_GUIDE_V2.md")

    failures: list[str] = []
    warnings: list[str] = []

    for path, label in ((overlay_path, "overlay"), (manifest_path, "manifest"), (schema_path, "schema")):
        if not path.is_file():
            failures.append(f"MISSING_{label.upper()}: {path}")

    if failures:
        print(json.dumps({"status": "FAIL", "failures": failures}, ensure_ascii=False, indent=2))
        return 1

    overlay = read_json(overlay_path)
    manifest = read_json(manifest_path)
    schema = read_json(schema_path)
    is_v21 = overlay.get("schema_version") == "2.1.0"
    markdown = ""
    if is_v21:
        if not markdown_path.is_file():
            failures.append(f"MISSING_TEACHER_MARKDOWN:{markdown_path}")
        else:
            markdown = markdown_path.read_text(encoding="utf-8")

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
                    "item": item,
                }

    refs: list[str] = []
    task_cards_by_id: dict[str, dict[str, Any]] = {}
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
                failures.append(f"SOURCE_ITEM_SECTION_MISMATCH:{block_id}:{item_id}:{canonical['section_id']}!={section_id}")
            item_pages = canonical.get("printed_page_range")
            if isinstance(page_range, str) and isinstance(item_pages, str):
                try:
                    if not intersects(page_range, item_pages):
                        failures.append(f"SOURCE_ITEM_PAGE_MISMATCH:{block_id}:{item_id}:block={page_range}:item={item_pages}")
                except ValueError:
                    failures.append(f"INVALID_PAGE_RANGE:{block_id}:{page_range}:{item_pages}")

        if is_v21:
            cards = block.get("task_cards")
            if not isinstance(cards, list) or not cards:
                failures.append(f"TASK_CARDS_REQUIRED:{block_id}")
            else:
                card_refs = Counter()
                for card in cards:
                    if not isinstance(card, dict):
                        failures.append(f"INVALID_TASK_CARD:{block_id}")
                        continue
                    task_id = card.get("task_id")
                    source_ref = card.get("source_item_ref")
                    if not isinstance(task_id, str) or not task_id:
                        failures.append(f"TASK_ID_REQUIRED:{block_id}")
                        continue
                    if task_id in task_cards_by_id:
                        failures.append(f"DUPLICATE_TASK_ID:{task_id}")
                    task_cards_by_id[task_id] = card
                    if isinstance(source_ref, str):
                        card_refs[source_ref] += 1
                    if source_ref not in source_refs:
                        failures.append(f"TASK_CARD_SOURCE_NOT_IN_BLOCK:{block_id}:{task_id}:{source_ref}")
                    canonical = canonical_items.get(source_ref) if isinstance(source_ref, str) else None
                    if canonical is None:
                        failures.append(f"TASK_CARD_UNKNOWN_SOURCE:{block_id}:{task_id}:{source_ref}")
                        continue
                    item = canonical["item"]
                    if card.get("acceptance_criteria") != item.get("acceptance_criteria"):
                        failures.append(f"TASK_CARD_ACCEPTANCE_DRIFT:{task_id}")
                    if card.get("canonical_teacher_guidance") != item.get("teacher_guidance"):
                        failures.append(f"TASK_CARD_TEACHER_GUIDANCE_DRIFT:{task_id}")
                    if card.get("canonical_common_misconceptions") != item.get("common_misconceptions"):
                        failures.append(f"TASK_CARD_MISCONCEPTION_DRIFT:{task_id}")
                    if card.get("canonical_assessment_evidence") != item.get("assessment_evidence"):
                        failures.append(f"TASK_CARD_ASSESSMENT_DRIFT:{task_id}")
                    if card.get("canonical_differentiation") != item.get("differentiation"):
                        failures.append(f"TASK_CARD_DIFFERENTIATION_DRIFT:{task_id}")

                for source_ref in source_refs:
                    if card_refs[source_ref] == 0:
                        failures.append(f"SOURCE_ITEM_WITHOUT_TASK_CARD:{block_id}:{source_ref}")

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

    if is_v21:
        expected_specs: dict[str, tuple[str, dict[str, Any], dict[str, Any]]] = {}
        for item_id, canonical in canonical_items.items():
            item = canonical["item"]
            for spec in expected_task_specs(item):
                expected_specs[spec["task_id"]] = (item_id, item, spec)

        missing_tasks = sorted(set(expected_specs) - set(task_cards_by_id))
        unexpected_tasks = sorted(set(task_cards_by_id) - set(expected_specs))
        if missing_tasks:
            failures.append("MISSING_FIRST_CLASS_TASKS: " + ", ".join(missing_tasks))
        if unexpected_tasks:
            failures.append("UNEXPECTED_TASK_CARDS: " + ", ".join(unexpected_tasks))

        for task_id, (item_id, item, spec) in expected_specs.items():
            card = task_cards_by_id.get(task_id)
            if card is None:
                continue
            if card.get("question_number") != spec["question_number"]:
                failures.append(f"QUESTION_NUMBER_DRIFT:{task_id}")
            if card.get("split_from_group") != spec["split_from_group"]:
                failures.append(f"SPLIT_FLAG_DRIFT:{task_id}")
            if card.get("expected_answer") != spec["expected_answer"]:
                failures.append(f"EXPECTED_ANSWER_DRIFT:{task_id}")
            if card.get("expected_response") != spec["expected_response"]:
                failures.append(f"EXPECTED_RESPONSE_DRIFT:{task_id}")
            component_key = spec.get("answer_component_key")
            if component_key is not None and card.get("answer_component_key") != component_key:
                failures.append(f"ANSWER_COMPONENT_KEY_DRIFT:{task_id}")

            expected_has_answer = is_nonempty(spec["expected_answer"]) or is_nonempty(spec["expected_response"])
            if item.get("item_type") == "QUESTION" and not expected_has_answer:
                warnings.append(f"QUESTION_WITHOUT_CANONICAL_ANSWER:{item_id}")
            if expected_has_answer and f"<!-- answer:{task_id} -->" not in markdown:
                failures.append(f"ANSWER_NOT_RENDERED_TO_MARKDOWN:{task_id}")
            if f"<!-- task:{task_id} -->" not in markdown:
                failures.append(f"TASK_NOT_RENDERED_TO_MARKDOWN:{task_id}")

        for item_id, canonical in canonical_items.items():
            split = split_expected_answers(canonical["item"])
            if split and item_id in task_cards_by_id:
                failures.append(f"BUNDLED_QUESTION_NOT_SPLIT:{item_id}")

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
        "schema_version": overlay.get("schema_version"),
        "canonical_item_count": len(canonical_items),
        "covered_item_count": len(set(refs) & set(canonical_items)),
        "task_card_count": len(task_cards_by_id) if is_v21 else None,
        "question_task_card_count": sum(1 for card in task_cards_by_id.values() if card.get("item_type") == "QUESTION") if is_v21 else None,
        "block_count": len(blocks),
        "failures": failures,
        "warnings": warnings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
