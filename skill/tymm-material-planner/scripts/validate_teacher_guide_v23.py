#!/usr/bin/env python3
"""Quality gate for the Teacher Guide V2.3 book-first pilot."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_note(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"[“\"].+?[”\"]", "<anchor>", text)
    text = re.sub(r"\bsayfa\s+\d+(?:[-–—]\d+)?\b", "<page>", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--mirror", default="courses/TDE_11/teacher_guide/TEMA_01/book_mirror_v23.json")
    parser.add_argument("--manifest", default="courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json")
    parser.add_argument("--schema", default="skill/tymm-material-planner/schemas/teacher_guide_book_mirror.schema.json")
    parser.add_argument("--markdown", default="courses/TDE_11/teacher_guide/TEMA_01/TEACHER_GUIDE_V23_PILOT.md")
    args = parser.parse_args()
    root = args.repo_root.resolve()

    mirror = read_json(root / args.mirror)
    schema = read_json(root / args.schema)
    manifest = read_json(root / args.manifest)
    markdown = (root / args.markdown).read_text(encoding="utf-8")
    failures: list[str] = []
    warnings: list[str] = []

    for error in sorted(Draft202012Validator(schema).iter_errors(mirror), key=lambda e: list(e.absolute_path)):
        failures.append(f"SCHEMA:{'.'.join(map(str, error.absolute_path)) or '$'}:{error.message}")

    if mirror.get("course_id") != manifest.get("course_id") or mirror.get("theme_id") != manifest.get("theme_id"):
        failures.append("MIRROR_MANIFEST_IDENTITY_MISMATCH")

    canonical: dict[str, dict[str, Any]] = {}
    for row in manifest.get("sections", []):
        section = read_json(root / row["content_ref"])
        for unit in section.get("guide_units", []):
            for item in unit.get("items", []):
                canonical[item["item_id"]] = {"section_id": section["section_id"], "item": item}

    seen_mirror_ids: set[str] = set()
    seen_refs: Counter[str] = Counter()
    questions = 0
    recognizable = 0
    teacher_notes: list[str] = []

    for entry in mirror.get("entries", []):
        mid = entry.get("mirror_id")
        if mid in seen_mirror_ids:
            failures.append(f"DUPLICATE_MIRROR_ID:{mid}")
        seen_mirror_ids.add(mid)

        refs = entry.get("canonical_item_refs", [])
        for ref in refs:
            seen_refs[ref] += 1
            if ref not in canonical:
                failures.append(f"UNKNOWN_CANONICAL_REF:{mid}:{ref}")
            elif canonical[ref]["section_id"] != entry.get("section_id"):
                failures.append(f"SECTION_DRIFT:{mid}:{ref}")

        if entry.get("presentation_type") == "QUESTION":
            questions += 1
            prompt = entry.get("prompt_display")
            mode = entry.get("prompt_mode")
            if isinstance(prompt, str) and prompt.strip() and mode in {"VERBATIM_SHORT", "VERIFIED_SUMMARY"}:
                recognizable += 1
            if mode == "LOCATOR_ONLY":
                failures.append(f"LOCATOR_ONLY_QUESTION:{mid}")

        note = entry.get("teacher_note")
        if isinstance(note, str) and note.strip():
            teacher_notes.append(note)
        elif isinstance(note, list):
            teacher_notes.extend(x for x in note if isinstance(x, str) and x.strip())

        expected_heading = f"## Sayfa {entry['printed_page_range']} — {entry['book_heading']}"
        if expected_heading not in markdown:
            failures.append(f"MISSING_BOOK_FIRST_HEADING:{mid}:{expected_heading}")

    if questions == 0:
        failures.append("NO_QUESTION_ENTRIES")
    elif recognizable != questions:
        failures.append(f"QUESTION_RECOGNIZABILITY:{recognizable}/{questions}")

    duplicates = sorted(ref for ref, count in seen_refs.items() if count > 1)
    if duplicates:
        failures.append("DUPLICATE_CANONICAL_PROJECTION:" + ",".join(duplicates))

    normalized = Counter(normalize_note(x) for x in teacher_notes)
    repeated = sorted((text, count) for text, count in normalized.items() if count > 1)
    if repeated:
        failures.append("REPEATED_TEACHER_NOTES:" + repr(repeated))

    note_entries = sum(1 for entry in mirror.get("entries", []) if entry.get("teacher_note"))
    density = note_entries / max(len(mirror.get("entries", [])), 1)
    if density >= 0.95:
        warnings.append(f"TEACHER_NOTE_DENSITY_HIGH:{density:.2f}")

    if "### Pedagojik amaç" in markdown or "### Takip soruları" in markdown:
        failures.append("V22_FIXED_PEDAGOGY_HEADINGS_LEAKED_INTO_V23")

    if "## Sayfa indeksli ders kontrol listesi" not in markdown:
        failures.append("MISSING_PAGE_CHECKLIST")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "metrics": {
            "entries": len(mirror.get("entries", [])),
            "questions": questions,
            "recognizable_questions": recognizable,
            "teacher_note_density": round(density, 3),
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
