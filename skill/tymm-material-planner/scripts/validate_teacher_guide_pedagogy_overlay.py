#!/usr/bin/env python3
"""Validate pedagogy-first TYMM teacher-guide overlays.

V2.1 protects teacher-facing answer/task-card fidelity.
V2.2 adds semantic quality gates for phase correctness, one-time placement of
curated section guidance, repetition limits, selective board notes, contextual
scaffolds, and explicit human promotion to REFERENCE_QUALITY.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover
    raise SystemExit("jsonschema is required: pip install jsonschema==4.23.0") from exc

PAGE_RANGE_RE = re.compile(r"^\s*(\d+)\s*(?:[-–—]\s*(\d+)\s*)?$")
QUESTION_RANGE_RE = re.compile(r"(?:^|_)Q(\d+)_(\d+)(?:_|$)")
LABEL_RANGE_RE = re.compile(r"(\d+)\s*[-–—]\s*(\d+)\.?\s*soru", re.IGNORECASE)
PROFILE_FIELDS = (
    "teacher_moves",
    "follow_up_questions",
    "misconception_interventions",
    "board_notes",
    "assessment_look_fors",
    "support",
    "enrichment",
    "source_limitations",
)
MAX_COUNTS = {
    "teacher_moves": 4,
    "follow_up_questions": 4,
    "misconception_interventions": 3,
    "board_notes": 2,
    "assessment_look_fors": 4,
    "support": 2,
    "enrichment": 2,
}
REPEAT_LIMITS = {
    "teacher_moves": 3,
    "follow_up_questions": 3,
    "misconception_interventions": 3,
    "board_notes": 2,
    "assessment_look_fors": 3,
    "support": 3,
    "enrichment": 3,
}


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


def classify_phase(section_type: str, unit_title: str) -> str:
    if section_type == "THEME_OPENING":
        return "opening"
    if section_type == "THEME_ASSESSMENT":
        return "assessment"
    title = unit_title.casefold()
    if any(key in title for key in ("yönet", "hazır", "planla")):
        return "manage"
    if any(key in title for key in ("değerl", "yansıt", "öz değerlend", "kontrol")):
        return "reflect"
    if section_type in {"SPEAKING", "WRITING"}:
        return "analyze_apply"
    if any(key in title for key in ("çözüm", "kural", "uygula", "gerçekleştir")):
        return "analyze_apply"
    if any(key in title for key in ("anlam", "içerik")):
        return "meaning"
    return "meaning"


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
        return [{
            "task_id": f"{item_id}#Q{number}",
            "question_number": number,
            "expected_answer": answer,
            "expected_response": None,
            "answer_component_key": component_key,
            "split_from_group": True,
        } for number, answer, component_key in split]
    return [{
        "task_id": item_id,
        "question_number": None,
        "expected_answer": item.get("expected_answer"),
        "expected_response": item.get("expected_response"),
        "answer_component_key": None,
        "split_from_group": False,
    }]


def block_field_values(block: dict[str, Any], field: str) -> list[str]:
    if field in {"support", "enrichment"}:
        differentiation = block.get("differentiation")
        if isinstance(differentiation, dict):
            values = differentiation.get(field, [])
            return values if isinstance(values, list) else []
        return []
    values = block.get(field, [])
    return values if isinstance(values, list) else []


def pedagogical_fingerprint(block: dict[str, Any]) -> tuple[Any, ...]:
    return (
        tuple(block_field_values(block, "teacher_moves")),
        tuple(block_field_values(block, "follow_up_questions")),
        tuple(block_field_values(block, "misconception_interventions")),
        tuple(block_field_values(block, "board_notes")),
        tuple(block_field_values(block, "assessment_look_fors")),
        tuple(block_field_values(block, "support")),
        tuple(block_field_values(block, "enrichment")),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--overlay", default="courses/TDE_11/teacher_guide/TEMA_01/pedagogy_v2.json")
    parser.add_argument("--manifest", default="courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json")
    parser.add_argument("--schema", default="skill/tymm-material-planner/schemas/teacher_guide_pedagogy_overlay.schema.json")
    parser.add_argument("--profiles", default="skill/tymm-material-planner/data/teacher_guide_v2_profiles.json")
    parser.add_argument("--markdown", default=None)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    overlay_path = root / args.overlay
    manifest_path = root / args.manifest
    schema_path = root / args.schema
    profiles_path = root / args.profiles
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
    version = overlay.get("schema_version")
    is_v21_plus = version in {"2.1.0", "2.2.0"}
    is_v22 = version == "2.2.0"
    profiles = read_json(profiles_path) if is_v22 and profiles_path.is_file() else None

    markdown = ""
    if is_v21_plus:
        if not markdown_path.is_file():
            failures.append(f"MISSING_TEACHER_MARKDOWN:{markdown_path}")
        else:
            markdown = markdown_path.read_text(encoding="utf-8")
    if is_v22 and profiles is None:
        failures.append(f"MISSING_PROFILES:{profiles_path}")

    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(overlay), key=lambda e: list(e.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        failures.append(f"SCHEMA:{location}: {error.message}")

    if overlay.get("course_id") != manifest.get("course_id"):
        failures.append("COURSE_ID_MISMATCH")
    if overlay.get("theme_id") != manifest.get("theme_id"):
        failures.append("THEME_ID_MISMATCH")

    if overlay.get("status") == "REFERENCE_QUALITY":
        review = overlay.get("quality_review")
        if not isinstance(review, dict) or review.get("decision") != "APPROVED":
            failures.append("REFERENCE_QUALITY_REQUIRES_EXPLICIT_APPROVED_REVIEW")

    canonical_items: dict[str, dict[str, Any]] = {}
    canonical_sections: dict[str, dict[str, Any]] = {}

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
        canonical_sections[section_id] = section
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
    blocks_by_section: dict[str, list[dict[str, Any]]] = defaultdict(list)
    sentence_counts: dict[str, Counter[str]] = {field: Counter() for field in REPEAT_LIMITS}
    fingerprints: dict[str, dict[tuple[Any, ...], str]] = defaultdict(dict)

    theme_phase_profiles = profiles.get("phase_profiles", {}) if isinstance(profiles, dict) else {}
    raw_phase_templates = {
        field: {
            text
            for phase in theme_phase_profiles.values()
            if isinstance(phase, dict)
            for text in (phase.get(field, []) if isinstance(phase.get(field, []), list) else [])
            if isinstance(text, str)
        }
        for field in REPEAT_LIMITS
    }

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

        section = canonical_sections.get(section_id) if isinstance(section_id, str) else None
        if section is None:
            failures.append(f"UNKNOWN_SECTION_REF:{block_id}:{section_id}")
        else:
            blocks_by_section[section_id].append(block)

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

        if is_v22 and section is not None:
            phase_name = block.get("phase_name")
            expected_phase = classify_phase(str(section.get("section_type", "")), str(block.get("title", "")))
            if phase_name != expected_phase:
                failures.append(f"PHASE_MISMATCH:{block_id}:{phase_name}!={expected_phase}")
            if section.get("section_type") in {"SPEAKING", "WRITING"} and phase_name == "meaning":
                failures.append(f"PRODUCTION_SKILL_MISCLASSIFIED_AS_MEANING:{block_id}")

            for field, maximum in MAX_COUNTS.items():
                values = block_field_values(block, field)
                if len(values) > maximum:
                    failures.append(f"PEDAGOGY_FIELD_TOO_DENSE:{block_id}:{field}:{len(values)}>{maximum}")
                for value in values:
                    if isinstance(value, str):
                        sentence_counts[field][value] += 1
                        if value in raw_phase_templates.get(field, set()):
                            failures.append(f"UNCONTEXTUALIZED_PHASE_TEMPLATE:{block_id}:{field}:{value}")

            if board_notes:
                section_profile = (
                    profiles.get("section_profiles", {})
                    .get(overlay.get("theme_id"), {})
                    .get(section_id, {})
                    if isinstance(profiles, dict) else {}
                )
                curated_board = set(section_profile.get("board_notes", [])) if isinstance(section_profile, dict) else set()
                for note in board_notes:
                    if note not in curated_board:
                        failures.append(f"NON_CURATED_BOARD_NOTE:{block_id}:{note}")

            fingerprint = pedagogical_fingerprint(block)
            previous = fingerprints[section_id].get(fingerprint)
            if previous is not None:
                failures.append(f"DUPLICATE_PEDAGOGICAL_PACKAGE:{section_id}:{previous}:{block_id}")
            else:
                fingerprints[section_id][fingerprint] = str(block_id)

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

        if is_v21_plus:
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

    if is_v21_plus:
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

        unanswered_question_items: set[str] = set()
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
                unanswered_question_items.add(item_id)
            if expected_has_answer and f"<!-- answer:{task_id} -->" not in markdown:
                failures.append(f"ANSWER_NOT_RENDERED_TO_MARKDOWN:{task_id}")
            if f"<!-- task:{task_id} -->" not in markdown:
                failures.append(f"TASK_NOT_RENDERED_TO_MARKDOWN:{task_id}")

        warnings.extend(f"QUESTION_WITHOUT_CANONICAL_ANSWER:{item_id}" for item_id in sorted(unanswered_question_items))

        for item_id, canonical in canonical_items.items():
            split = split_expected_answers(canonical["item"])
            if split and item_id in task_cards_by_id:
                failures.append(f"BUNDLED_QUESTION_NOT_SPLIT:{item_id}")

    if is_v22 and isinstance(profiles, dict):
        theme_profiles = profiles.get("section_profiles", {}).get(overlay.get("theme_id"), {})
        if not isinstance(theme_profiles, dict):
            failures.append(f"MISSING_THEME_PROFILES:{overlay.get('theme_id')}")
        else:
            for section_id, section_profile in theme_profiles.items():
                if not isinstance(section_profile, dict) or section_id not in canonical_sections:
                    continue
                section_blocks = blocks_by_section.get(section_id, [])
                for field in PROFILE_FIELDS:
                    expected_entries = section_profile.get(field, [])
                    if not isinstance(expected_entries, list):
                        continue
                    if field == "board_notes":
                        expected_entries = expected_entries[: 2 * len(section_blocks)]
                    actual_entries: list[str] = []
                    for block in section_blocks:
                        actual_entries.extend(block_field_values(block, field))
                    for entry in expected_entries:
                        if not isinstance(entry, str) or not entry.strip():
                            continue
                        count = actual_entries.count(entry)
                        if count != 1:
                            failures.append(f"SECTION_GUIDANCE_NOT_EXACTLY_ONCE:{section_id}:{field}:{count}:{entry}")

        for field, limit in REPEAT_LIMITS.items():
            for text, count in sentence_counts[field].items():
                if count > limit:
                    failures.append(f"PEDAGOGY_TEXT_OVERREPEATED:{field}:{count}>{limit}:{text}")

        intents_by_section: dict[str, Counter[str]] = defaultdict(Counter)
        for block in blocks:
            if isinstance(block, dict) and isinstance(block.get("section_id"), str):
                intent = block.get("pedagogical_intent")
                if isinstance(intent, str):
                    intents_by_section[block["section_id"]][intent] += 1
        for section_id, counter in intents_by_section.items():
            for intent, count in counter.items():
                if count > 1:
                    failures.append(f"DUPLICATE_PEDAGOGICAL_INTENT:{section_id}:{count}:{intent}")

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
        "schema_version": version,
        "overlay_status": overlay.get("status"),
        "canonical_item_count": len(canonical_items),
        "covered_item_count": len(set(refs) & set(canonical_items)),
        "task_card_count": len(task_cards_by_id) if is_v21_plus else None,
        "question_task_card_count": sum(1 for card in task_cards_by_id.values() if card.get("item_type") == "QUESTION") if is_v21_plus else None,
        "block_count": len(blocks),
        "blocks_with_board_notes": sum(1 for block in blocks if isinstance(block, dict) and block.get("board_notes")),
        "semantic_quality_gates": is_v22,
        "failures": failures,
        "warnings": warnings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
