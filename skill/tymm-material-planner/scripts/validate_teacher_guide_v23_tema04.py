#!/usr/bin/env python3
"""Source-parity gate for the Theme 4 Teacher Guide V2.3 opening (s.236-239)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_teacher_guide_v23_generic import discover_mirror_paths, read_json, validate

QUESTIONS = {
    "T4V23_P238_Q01": ("1",),
    "T4V23_P238_Q02": ("2",),
    "T4V23_P239_Q03": ("3",),
    "T4V23_P239_Q04": ("4",),
    "T4V23_P239_Q05": ("5",),
}

EXPECTED = {
    "mirror_files": 1,
    "scope": "236-239",
    "entries": 7,
    "questions": 5,
    "recognizable_questions": 5,
    "component_projected_entries": 5,
    "shared_canonical_items": 2,
    "review_required_fragments": 0,
    "component_registry_entries": 0,
    "component_registry_used": 0,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.repo_root.resolve()

    mirror_path = root / "courses/TDE_11/teacher_guide/TEMA_04/book_mirror_v23.json"
    manifest_path = root / "courses/TDE_11/teacher_guide/TEMA_04/teacher_guide.json"
    schema_path = root / "skill/tymm-material-planner/schemas/teacher_guide_book_mirror.schema.json"
    markdown_path = root / "courses/TDE_11/teacher_guide/TEMA_04/TEACHER_GUIDE_V23_PILOT.md"

    report = validate(root, mirror_path, manifest_path, schema_path, markdown_path)
    failures = list(report["failures"])
    warnings = list(report["warnings"])
    metrics = report["metrics"]

    for key, value in EXPECTED.items():
        if metrics.get(key) != value:
            failures.append(f"TEMA04_METRIC_PARITY:{key}:{metrics.get(key)}!={value}")

    mirrors = [read_json(path) for path in discover_mirror_paths(mirror_path)]
    entries = [entry for mirror in mirrors for entry in mirror.get("entries", [])]
    by_id = {str(entry.get("mirror_id")): entry for entry in entries}

    if len(mirrors) != 1 or mirrors[0].get("scope") != {"printed_page_range": "236-239", "status": "PILOT"}:
        failures.append("TEMA04_OPENING_MUST_REMAIN_236_239_PILOT")

    theme = by_id.get("T4V23_P236_THEME_OPEN", {})
    if theme.get("presentation_type") != "REFERENCE" or len(theme.get("canonical_item_refs", [])) != 2:
        failures.append("TEMA04_P236_THEME_FRAME_PARITY")

    yunus = by_id.get("T4V23_P237_YUNUS_REFERENCE", {})
    if yunus.get("presentation_type") != "REFERENCE":
        failures.append("TEMA04_P237_YUNUS_MUST_NOT_BECOME_QUESTION")
    if any(entry.get("presentation_type") == "QUESTION" and entry.get("printed_page_range") == "237" for entry in entries):
        failures.append("TEMA04_P237_SOURCE_HAS_NO_QUESTION")

    question_rows = [entry for entry in entries if entry.get("presentation_type") == "QUESTION"]
    if len(question_rows) != 5 or {str(entry.get("mirror_id")) for entry in question_rows} != set(QUESTIONS):
        failures.append(f"TEMA04_OPENING_MUST_HAVE_5_SOURCE_QUESTIONS:{len(question_rows)}")

    for mirror_id, expected_keys in QUESTIONS.items():
        entry = by_id.get(mirror_id)
        if not entry:
            failures.append(f"TEMA04_QUESTION_MISSING:{mirror_id}")
            continue
        actual_keys = tuple(entry.get("answer_keys", []))
        if actual_keys != expected_keys:
            failures.append(f"TEMA04_ANSWER_KEY_DRIFT:{mirror_id}:{actual_keys!r}!={expected_keys!r}")

    p238 = [entry for entry in question_rows if entry.get("printed_page_range") == "238"]
    p239 = [entry for entry in question_rows if entry.get("printed_page_range") == "239"]
    if len(p238) != 2 or len(p239) != 3:
        failures.append(f"TEMA04_PAGE_QUESTION_PARITY:{len(p238)}/2:{len(p239)}/3")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "metrics": {
            **metrics,
            "pdf_verified_opening_questions": len(question_rows),
            "p237_nonquestion_boundary_preserved": yunus.get("presentation_type") == "REFERENCE",
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
