#!/usr/bin/env python3
"""Validate the neutral TDE 11 teacher-book source layer."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

THEMES = [f"TEMA_{n:02d}" for n in range(1, 5)]
FORBIDDEN_PATHS = [
    "courses/TDE_11/teacher_guide",
    "courses/TDE_11/teacher_guide_v3",
    "courses/TDE_11/teacher_guide_kindle",
]
FORBIDDEN_TEXT = [
    "book_mirror_v23",
    "teacher_guide_v3",
    "pedagogy_v2",
    "legacy_teacher_guide",
]
FORBIDDEN_KEYS = {
    "mirror_id",
    "canonical_item_refs",
    "teacher_note",
    "teacher_guidance",
    "common_misconceptions",
    "misconception_interventions",
    "differentiation",
    "why_it_matters",
    "teacher_moves",
    "follow_up_questions",
    "board_notes",
    "acceptance_criteria",
}
SOURCE_ID_RE = re.compile(r"^T0[1-4]-S\d{4}$")
ANSWER_ID_RE = re.compile(r"^T0[1-4]-A\d{4}$")
LEGACY_ID_RE = re.compile(r"T\d+V23_", re.I)

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def compact(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()

def walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()
    root = args.repo_root.resolve()
    failures: list[str] = []

    for rel in FORBIDDEN_PATHS:
        if (root / rel).exists():
            failures.append(f"LEGACY_PATH_PRESENT:{rel}")

    base = root / "courses/TDE_11/teacher_book/source"
    manifest_path = base / "manifest.json"
    policy_path = root / "courses/TDE_11/teacher_book/SOURCE_POLICY.md"
    if not manifest_path.is_file():
        failures.append("SOURCE_MANIFEST_MISSING")
        manifest = {}
    else:
        manifest = read_json(manifest_path)
    if not policy_path.is_file():
        failures.append("SOURCE_POLICY_MISSING")

    if manifest.get("document_type") != "TYMM_TEACHER_BOOK_SOURCE_MANIFEST":
        failures.append("SOURCE_MANIFEST_TYPE_INVALID")
    if manifest.get("course_id") != "TDE_11":
        failures.append("SOURCE_MANIFEST_COURSE_INVALID")

    total_records = 0
    total_answers = 0
    all_source_ids: set[str] = set()
    inventory = read_json(root / "courses/TDE_11/textbook_question_inventory.json")
    inventory_questions = inventory.get("questions", [])
    source_question_keys: set[tuple[str, str, str]] = set()

    for theme in THEMES:
        theme_dir = base / theme
        source_path = theme_dir / "source_index.json"
        answer_path = theme_dir / "answer_bank.json"
        if not source_path.is_file() or not answer_path.is_file():
            failures.append(f"THEME_SOURCE_FILES_MISSING:{theme}")
            continue
        source = read_json(source_path)
        bank = read_json(answer_path)

        if source.get("document_type") != "TYMM_TEACHER_BOOK_SOURCE_INDEX":
            failures.append(f"SOURCE_TYPE_INVALID:{theme}")
        if bank.get("document_type") != "TYMM_TEACHER_BOOK_ANSWER_BANK":
            failures.append(f"ANSWER_TYPE_INVALID:{theme}")
        if source.get("theme_id") != theme or bank.get("theme_id") != theme:
            failures.append(f"THEME_ID_MISMATCH:{theme}")

        raw = source_path.read_text(encoding="utf-8") + "\n" + answer_path.read_text(encoding="utf-8")
        raw_lower = raw.lower()
        for token in FORBIDDEN_TEXT:
            if token.lower() in raw_lower:
                failures.append(f"LEGACY_TEXT_LEAK:{theme}:{token}")
        if LEGACY_ID_RE.search(raw):
            failures.append(f"LEGACY_ID_LEAK:{theme}")
        actually_leaked = sorted((set(walk_keys(source)) | set(walk_keys(bank))) & FORBIDDEN_KEYS)
        for key in actually_leaked:
            failures.append(f"LEGACY_FIELD_LEAK:{theme}:{key}")

        answers = bank.get("answers", [])
        answer_ids: set[str] = set()
        for answer in answers:
            aid = answer.get("answer_id", "")
            if not ANSWER_ID_RE.fullmatch(aid):
                failures.append(f"ANSWER_ID_INVALID:{theme}:{aid}")
            if aid in answer_ids:
                failures.append(f"ANSWER_ID_DUPLICATE:{theme}:{aid}")
            answer_ids.add(aid)
            if "legacy_teacher_guide" in answer.get("source_ids", []):
                failures.append(f"LEGACY_ANSWER_SOURCE:{theme}:{aid}")
        if bank.get("counts", {}).get("answers") != len(answers):
            failures.append(f"ANSWER_COUNT_STALE:{theme}")
        total_answers += len(answers)

        records = source.get("records", [])
        local_source_ids: set[str] = set()
        linked = 0
        for record in records:
            sid = record.get("source_record_id", "")
            if not SOURCE_ID_RE.fullmatch(sid):
                failures.append(f"SOURCE_ID_INVALID:{theme}:{sid}")
            if sid in local_source_ids or sid in all_source_ids:
                failures.append(f"SOURCE_ID_DUPLICATE:{theme}:{sid}")
            local_source_ids.add(sid)
            all_source_ids.add(sid)
            refs = record.get("answer_refs", [])
            linked += 1 if refs else 0
            for ref in refs:
                if ref not in answer_ids:
                    failures.append(f"ANSWER_REF_UNRESOLVED:{theme}:{sid}:{ref}")
            if record.get("source_status") not in {"VERIFIED", "REVIEW_REQUIRED"}:
                failures.append(f"SOURCE_STATUS_INVALID:{theme}:{sid}")
            if record.get("task_type") == "QUESTION" and record.get("prompt"):
                source_question_keys.add((theme, compact(record.get("printed_page_range")), compact(record["prompt"])))
        if source.get("counts", {}).get("records") != len(records):
            failures.append(f"SOURCE_COUNT_STALE:{theme}")
        if source.get("counts", {}).get("linked_answers") != linked:
            failures.append(f"LINKED_ANSWER_COUNT_STALE:{theme}")
        total_records += len(records)

    for q in inventory_questions:
        key = (q.get("theme_id"), compact(q.get("printed_page_range")), compact(q.get("prompt")))
        if key not in source_question_keys:
            failures.append(f"QUESTION_INVENTORY_NOT_IN_SOURCE:{q.get('question_id')}")

    totals = manifest.get("totals", {})
    if totals.get("source_records") != total_records:
        failures.append(f"MANIFEST_SOURCE_TOTAL_STALE:{total_records}")
    if totals.get("clean_answers") != total_answers:
        failures.append(f"MANIFEST_ANSWER_TOTAL_STALE:{total_answers}")

    status = "PASS" if not failures else "FAIL"
    print(json.dumps({
        "status": status,
        "counts": {
            "themes": len(THEMES),
            "source_records": total_records,
            "clean_answers": total_answers,
            "inventory_questions": len(inventory_questions),
        },
        "failures": failures,
    }, ensure_ascii=False, indent=2))
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
