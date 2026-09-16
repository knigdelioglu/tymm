#!/usr/bin/env python3
"""Source-parity gate for the Theme 3 Teacher Guide V2.3 opening pilot (s.160-163)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_teacher_guide_v23_generic import discover_mirror_paths, read_json, validate

REQUIRED_QUESTIONS = {
    "T3V23_P162_Q01", "T3V23_P162_Q02", "T3V23_P162_Q03", "T3V23_P162_Q04",
    "T3V23_P163_Q05", "T3V23_P163_Q06",
}
REQUIRED_ENTRIES = {"T3V23_P160_161_THEME_OPEN", *REQUIRED_QUESTIONS}
REQUIRED_HEADINGS = {
    "3. Tema — Yaşamın İzinde / tema çerçevesi",
    "Temaya Başlarken — edebiyat ve yaşam",
    "Temaya Başlarken — görsellerin çağrışımı",
    "Temaya Başlarken — biyografi ve tezkire ön karşılaştırması",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.repo_root.resolve()
    mirror_path = root / "courses/TDE_11/teacher_guide/TEMA_03/book_mirror_v23.json"
    manifest_path = root / "courses/TDE_11/teacher_guide/TEMA_03/teacher_guide.json"
    schema_path = root / "skill/tymm-material-planner/schemas/teacher_guide_book_mirror.schema.json"
    markdown_path = root / "courses/TDE_11/teacher_guide/TEMA_03/TEACHER_GUIDE_V23_PILOT.md"

    report = validate(root, mirror_path, manifest_path, schema_path, markdown_path)
    failures = list(report["failures"])
    warnings = list(report["warnings"])
    metrics = report["metrics"]
    seen = set(report.get("seen_mirror_ids", []))
    headings = set(report.get("headings", []))

    expected = {
        "scope": "160-163",
        "entries": 7,
        "questions": 6,
        "recognizable_questions": 6,
        "component_projected_entries": 4,
        "shared_canonical_items": 1,
        "component_registry_entries": 0,
        "component_registry_used": 0,
    }
    for key, value in expected.items():
        if metrics.get(key) != value:
            failures.append(f"TEMA03_METRIC_PARITY:{key}:{metrics.get(key)}!={value}")

    missing_entries = sorted(REQUIRED_ENTRIES - seen)
    if missing_entries:
        failures.append("TEMA03_OPENING_ENTRIES_MISSING:" + ",".join(missing_entries))
    missing_headings = sorted(REQUIRED_HEADINGS - headings)
    if missing_headings:
        failures.append("TEMA03_BOOK_HEADINGS_MISSING:" + " | ".join(missing_headings))

    mirrors = [read_json(path) for path in discover_mirror_paths(mirror_path)]
    entries = [entry for mirror in mirrors for entry in mirror.get("entries", [])]
    questions = [entry for entry in entries if entry.get("mirror_id") in REQUIRED_QUESTIONS]
    if len(questions) != 6 or any(entry.get("presentation_type") != "QUESTION" for entry in questions):
        failures.append(f"TEMA03_OPENING_MUST_HAVE_6_QUESTION_CARDS:{len(questions)}")

    p162 = [entry for entry in entries if str(entry.get("mirror_id", "")).startswith("T3V23_P162_Q")]
    projected_keys = {tuple(entry.get("answer_keys", [])) for entry in p162}
    if len(p162) != 4 or projected_keys != {("1",), ("2",), ("3",), ("4",)}:
        failures.append("TEMA03_P162_MUST_KEEP_4_DISTINCT_SOURCE_QUESTIONS")

    if len(mirrors) != 1 or mirrors[0].get("scope", {}).get("status") != "PILOT":
        failures.append("TEMA03_160_163_MUST_REMAIN_PILOT")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "metrics": {
            **metrics,
            "pdf_verified_opening_questions": 6,
            "pilot_scope": True,
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
