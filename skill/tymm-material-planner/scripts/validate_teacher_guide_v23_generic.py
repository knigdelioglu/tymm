#!/usr/bin/env python3
"""Reusable quality gate for Teacher Guide V2.3 book-first mirrors.

Theme-specific validators may import :func:`validate` and add source-parity
contracts without duplicating the generic book-first invariants.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_page_range(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*(?:[-–—]\s*(\d+)\s*)?", value)
    if not match:
        raise ValueError(value)
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        raise ValueError(value)
    return start, end


def discover_mirror_paths(primary: Path) -> list[Path]:
    paths = [primary]
    paths.extend(path for path in primary.parent.glob("book_mirror_v23_*.json") if path != primary)
    return sorted(paths, key=lambda p: parse_page_range(read_json(p)["scope"]["printed_page_range"])[0])


def normalize_note(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"[“\"].+?[”\"]", "<anchor>", text)
    text = re.sub(r"\bsayfa\s+\d+(?:[-–—]\d+)?\b", "<page>", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def note_text(entry: dict[str, Any]) -> str:
    note = entry.get("teacher_note")
    if isinstance(note, str):
        return note
    if isinstance(note, list):
        return " ".join(str(value) for value in note)
    return ""


def validate(
    root: Path,
    mirror_path: Path,
    manifest_path: Path,
    schema_path: Path,
    markdown_path: Path,
) -> dict[str, Any]:
    schema = read_json(schema_path)
    manifest = read_json(manifest_path)
    markdown = markdown_path.read_text(encoding="utf-8")
    mirror_paths = discover_mirror_paths(mirror_path)
    mirrors = [read_json(path) for path in mirror_paths]
    failures: list[str] = []
    warnings: list[str] = []

    for path, mirror in zip(mirror_paths, mirrors):
        for error in sorted(Draft202012Validator(schema).iter_errors(mirror), key=lambda e: list(e.absolute_path)):
            failures.append(f"SCHEMA:{path.name}:{'.'.join(map(str, error.absolute_path)) or '$'}:{error.message}")
        if mirror.get("course_id") != manifest.get("course_id") or mirror.get("theme_id") != manifest.get("theme_id"):
            failures.append(f"MIRROR_MANIFEST_IDENTITY_MISMATCH:{path.name}")

    scopes: list[tuple[int, int, str]] = []
    for path, mirror in zip(mirror_paths, mirrors):
        try:
            scopes.append((*parse_page_range(mirror["scope"]["printed_page_range"]), path.name))
        except (KeyError, ValueError):
            failures.append(f"INVALID_SCOPE:{path.name}")
    for left, right in zip(scopes, scopes[1:]):
        if right[0] <= left[1]:
            failures.append(f"OVERLAPPING_MIRROR_FRAGMENTS:{left[2]}:{right[2]}")
        elif right[0] != left[1] + 1:
            failures.append(f"MIRROR_FRAGMENT_GAP:{left[2]}:{right[2]}:{left[1]}->{right[0]}")

    entries = [entry for mirror in mirrors for entry in mirror.get("entries", [])]
    checklist = [row for mirror in mirrors for row in mirror.get("page_checklist", [])]

    canonical: dict[str, dict[str, Any]] = {}
    for row in manifest.get("sections", []):
        section = read_json(root / row["content_ref"])
        for unit in section.get("guide_units", []):
            for item in unit.get("items", []):
                canonical[item["item_id"]] = {
                    "section_id": section["section_id"],
                    "unit_id": unit.get("unit_id"),
                    "item": item,
                }

    seen_mirror_ids: set[str] = set()
    projections: dict[str, list[tuple[str, set[str] | None]]] = defaultdict(list)
    questions = 0
    recognizable = 0
    component_projected_entries = 0
    teacher_notes: list[str] = []

    for entry in entries:
        mid = str(entry.get("mirror_id", ""))
        if mid in seen_mirror_ids:
            failures.append(f"DUPLICATE_MIRROR_ID:{mid}")
        seen_mirror_ids.add(mid)

        refs = entry.get("canonical_item_refs", [])
        answer_keys = entry.get("answer_keys")
        if answer_keys and len(refs) != 1:
            failures.append(f"ANSWER_KEYS_REQUIRE_SINGLE_CANONICAL_REF:{mid}")
        if answer_keys:
            component_projected_entries += 1

        for ref in refs:
            keys = set(answer_keys) if isinstance(answer_keys, list) else None
            projections[ref].append((mid, keys))
            if ref not in canonical:
                failures.append(f"UNKNOWN_CANONICAL_REF:{mid}:{ref}")
                continue
            if canonical[ref]["section_id"] != entry.get("section_id"):
                failures.append(f"SECTION_DRIFT:{mid}:{ref}")
            if entry.get("unit_id") and canonical[ref].get("unit_id") != entry.get("unit_id"):
                failures.append(f"UNIT_DRIFT:{mid}:{ref}")
            if keys:
                item = canonical[ref]["item"]
                value = item.get("expected_answer")
                if not isinstance(value, dict):
                    value = item.get("expected_response")
                if not isinstance(value, dict):
                    failures.append(f"ANSWER_KEYS_REQUIRE_OBJECT:{mid}:{ref}")
                else:
                    missing_keys = sorted(keys - set(value))
                    if missing_keys:
                        failures.append(f"UNKNOWN_ANSWER_KEYS:{mid}:{ref}:{','.join(missing_keys)}")

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
            teacher_notes.extend(value for value in note if isinstance(value, str) and value.strip())

        expected_heading = f"## Sayfa {entry['printed_page_range']} — {entry['book_heading']}"
        if expected_heading not in markdown:
            failures.append(f"MISSING_BOOK_FIRST_HEADING:{mid}:{expected_heading}")

    for ref, rows in projections.items():
        if len(rows) <= 1:
            continue
        if any(keys is None for _, keys in rows):
            failures.append(f"DUPLICATE_CANONICAL_PROJECTION_WITHOUT_COMPONENTS:{ref}")
            continue
        used: set[str] = set()
        for mid, keys in rows:
            assert keys is not None
            overlap = used & keys
            if overlap:
                failures.append(f"OVERLAPPING_CANONICAL_COMPONENTS:{ref}:{mid}:{','.join(sorted(overlap))}")
            used |= keys

    if questions == 0:
        failures.append("NO_QUESTION_ENTRIES")
    elif recognizable != questions:
        failures.append(f"QUESTION_RECOGNIZABILITY:{recognizable}/{questions}")

    normalized = Counter(normalize_note(text) for text in teacher_notes)
    repeated = sorted((text, count) for text, count in normalized.items() if count > 1)
    if repeated:
        failures.append("REPEATED_TEACHER_NOTES:" + repr(repeated))

    note_entries = sum(1 for entry in entries if entry.get("teacher_note"))
    density = note_entries / max(len(entries), 1)
    if density >= 0.95:
        warnings.append(f"TEACHER_NOTE_DENSITY_HIGH:{density:.2f}")

    if "### Pedagojik amaç" in markdown or "### Takip soruları" in markdown:
        failures.append("V22_FIXED_PEDAGOGY_HEADINGS_LEAKED_INTO_V23")
    if "## Sayfa indeksli ders kontrol listesi" not in markdown or not checklist:
        failures.append("MISSING_PAGE_CHECKLIST")

    min_scope_start = min((start for start, _, _ in scopes), default=0)
    max_scope_end = max((end for _, end, _ in scopes), default=0)
    expected_scope_text = f"basılı s.{min_scope_start}-{max_scope_end}"
    if expected_scope_text not in markdown:
        failures.append(f"COMBINED_SCOPE_NOT_RENDERED:{expected_scope_text}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "course_id": manifest.get("course_id"),
        "theme_id": manifest.get("theme_id"),
        "metrics": {
            "mirror_files": len(mirror_paths),
            "scope": f"{min_scope_start}-{max_scope_end}",
            "entries": len(entries),
            "questions": questions,
            "recognizable_questions": recognizable,
            "component_projected_entries": component_projected_entries,
            "shared_canonical_items": sum(1 for rows in projections.values() if len(rows) > 1),
            "teacher_note_density": round(density, 3),
            "review_required_fragments": sum(1 for mirror in mirrors if mirror.get("scope", {}).get("status") == "REVIEW_REQUIRED"),
        },
        "seen_mirror_ids": sorted(seen_mirror_ids),
        "headings": sorted({str(entry.get("book_heading")) for entry in entries}),
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--mirror", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--schema", default="skill/tymm-material-planner/schemas/teacher_guide_book_mirror.schema.json")
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = validate(root, root / args.mirror, root / args.manifest, root / args.schema, root / args.markdown)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
