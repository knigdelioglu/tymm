#!/usr/bin/env python3
"""Source-parity gate for the complete Theme 4 Teacher Guide V2.3 (s.236-307)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_teacher_guide_v23_generic import discover_mirror_paths, read_json, validate

EXPECTED = {
    "mirror_files": 7,
    "scope": "236-307",
    "entries": 143,
    "questions": 105,
    "recognizable_questions": 105,
    "review_required_fragments": 3,
    "component_registry_entries": 65,
    "component_registry_used": 65,
}

EXPECTED_FRAGMENTS = {
    "236-239": ("PILOT", 7, 5),
    "240-262": ("REFERENCE_QUALITY", 32, 22),
    "263-279": ("REFERENCE_QUALITY", 34, 22),
    "280-283": ("REVIEW_REQUIRED", 10, 7),
    "284-297": ("REVIEW_REQUIRED", 33, 29),
    "298-302": ("REVIEW_REQUIRED", 13, 6),
    "303-307": ("REFERENCE_QUALITY", 14, 14),
}

OPENING_IDS = {
    "T4V23_P238_Q01",
    "T4V23_P238_Q02",
    "T4V23_P239_Q03",
    "T4V23_P239_Q04",
    "T4V23_P239_Q05",
}
THEATRE_Q251 = {
    "T4V23_P251_252_Q01",
    "T4V23_P251_252_Q02",
    "T4V23_P252_Q03",
}
THEATRE_Q262 = {"T4V23_P262_Q01", "T4V23_P262_Q02"}
SPEAKING_Q = {
    "T4V23_P280_Q01",
    "T4V23_P280_Q02",
    "T4V23_P281_Q03",
    "T4V23_P281_Q04",
    "T4V23_P283_Q01",
    "T4V23_P283_Q02",
    "T4V23_P283_Q03",
}
ASSESSMENT_Q = {f"T4V23_P{page}_Q{num:02d}" for page, num in [
    (303, 1), (304, 2), (304, 3), (304, 4), (305, 5), (305, 6),
    (306, 7), (306, 8), (306, 9), (307, 10), (307, 11), (307, 12),
    (307, 13), (307, 14),
]}


def page_span(entry: dict) -> tuple[int, int]:
    raw = str(entry.get("printed_page_range", "0")).replace("–", "-").replace("—", "-")
    parts = raw.split("-")
    return int(parts[0]), int(parts[-1])


def in_range(entry: dict, start: int, end: int) -> bool:
    left, right = page_span(entry)
    return left >= start and right <= end


def rows_in(entries: list[dict], start: int, end: int) -> list[dict]:
    return [entry for entry in entries if in_range(entry, start, end)]


def questions_in(entries: list[dict], start: int, end: int) -> list[dict]:
    return [
        entry for entry in entries
        if in_range(entry, start, end) and entry.get("presentation_type") == "QUESTION"
    ]


def ids(rows: list[dict]) -> set[str]:
    return {str(row.get("mirror_id")) for row in rows}


def require_exact_ids(failures: list[str], label: str, actual: set[str], expected: set[str]) -> None:
    if actual != expected:
        failures.append(
            f"TEMA04_{label}_ID_PARITY:missing={sorted(expected-actual)!r}:extra={sorted(actual-expected)!r}"
        )


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

    for key, expected in EXPECTED.items():
        if metrics.get(key) != expected:
            failures.append(f"TEMA04_METRIC_PARITY:{key}:{metrics.get(key)}!={expected}")

    mirror_paths = discover_mirror_paths(mirror_path)
    mirrors = [read_json(path) for path in mirror_paths]
    entries = [entry for mirror in mirrors for entry in mirror.get("entries", [])]
    by_id = {str(entry.get("mirror_id")): entry for entry in entries}

    # Fragment coverage and natural granularity.
    for mirror in mirrors:
        scope = str(mirror.get("scope", {}).get("printed_page_range"))
        expected = EXPECTED_FRAGMENTS.get(scope)
        if expected is None:
            failures.append(f"TEMA04_UNEXPECTED_FRAGMENT:{scope}")
            continue
        status, expected_entries, expected_questions = expected
        rows = list(mirror.get("entries", []))
        qrows = [row for row in rows if row.get("presentation_type") == "QUESTION"]
        if mirror.get("scope", {}).get("status") != status:
            failures.append(f"TEMA04_FRAGMENT_STATUS:{scope}:{mirror.get('scope', {}).get('status')}!={status}")
        if len(rows) != expected_entries or len(qrows) != expected_questions:
            failures.append(
                f"TEMA04_FRAGMENT_GRANULARITY:{scope}:{len(rows)}/{len(qrows)}"
                f"!={expected_entries}/{expected_questions}"
            )
    if {str(m.get("scope", {}).get("printed_page_range")) for m in mirrors} != set(EXPECTED_FRAGMENTS):
        failures.append("TEMA04_FRAGMENT_COVERAGE_DRIFT")

    # Opening: s.237 is a transition/reference, not a fabricated question.
    require_exact_ids(failures, "OPENING", ids(questions_in(entries, 236, 239)), OPENING_IDS)
    if by_id.get("T4V23_P237_YUNUS_REFERENCE", {}).get("presentation_type") != "REFERENCE":
        failures.append("TEMA04_P237_YUNUS_MUST_REMAIN_REFERENCE")

    # Theatre: the source has three real Metni Anlayalım questions at s.251-252 and two Sıra Sizde at s.262.
    require_exact_ids(
        failures,
        "THEATRE_P251_252",
        {str(row.get("mirror_id")) for row in questions_in(entries, 251, 252) if row.get("mirror_id") in THEATRE_Q251},
        THEATRE_Q251,
    )
    require_exact_ids(failures, "THEATRE_P262", ids(questions_in(entries, 262, 262)), THEATRE_Q262)
    if by_id.get("T4V23_P256_YAPI", {}).get("presentation_type") != "TABLE":
        failures.append("TEMA04_P256_STRUCTURE_MUST_REMAIN_TABLE")
    for mid in ("T4V23_P260_SOSYAL_BILIM", "T4V23_P261_CATISMA"):
        if by_id.get(mid, {}).get("presentation_type") != "PROCESS":
            failures.append(f"TEMA04_THEATRE_PROCESS_BOUNDARY:{mid}")

    # Küçürek hikâye: eight Metni Anlayalım questions are separate; group techniques stay processes.
    kucurek_metni = questions_in(entries, 269, 270)
    if len(kucurek_metni) != 8:
        failures.append(f"TEMA04_KUCU_REK_METNI_ANLAYALIM_1_8:{len(kucurek_metni)}/8")
    if by_id.get("T4V23_P274_KARAKTER_COZUMLEME", {}).get("presentation_type") != "PROCESS":
        failures.append("TEMA04_P274_CHARACTER_GROUP_MUST_REMAIN_PROCESS")
    if by_id.get("T4V23_P276_277_CATISMA", {}).get("presentation_type") != "PROCESS":
        failures.append("TEMA04_P276_277_CONFLICT_GROUP_MUST_REMAIN_PROCESS")

    # Speaking: four preparation questions + three reflection questions, with performance/rubric kept separate.
    require_exact_ids(failures, "SPEAKING_7", ids(questions_in(entries, 280, 283)), SPEAKING_Q)
    if by_id.get("T4V23_P281_PERFORMANS", {}).get("presentation_type") != "PROCESS":
        failures.append("TEMA04_SPEAKING_PERFORMANCE_MUST_REMAIN_PROCESS")
    if by_id.get("T4V23_P283_RUBRIK", {}).get("presentation_type") != "ASSESSMENT":
        failures.append("TEMA04_SPEAKING_QR_RUBRIC_BOUNDARY")

    # Listening/viewing: 11 Metni Anlayalım + 14 Çözümleyebilme source questions remain individually findable.
    listening = rows_in(entries, 284, 297)
    listening_questions = [row for row in listening if row.get("presentation_type") == "QUESTION"]
    if len(listening) != 33 or len(listening_questions) != 29:
        failures.append(f"TEMA04_LISTENING_GRANULARITY:{len(listening)}/{len(listening_questions)}")
    metni_11 = [row for row in listening_questions if "Metni Anlayalım" in str(row.get("book_heading", ""))]
    if len(metni_11) != 11:
        failures.append(f"TEMA04_LISTENING_METNI_ANLAYALIM:{len(metni_11)}/11")
    cozum_14 = [row for row in listening_questions if in_range(row, 294, 296)]
    if len(cozum_14) != 14:
        failures.append(f"TEMA04_LISTENING_COZUMLEME:{len(cozum_14)}/14")
    for row in listening_questions:
        if row.get("printed_page_range") in {"287", "288", "289", "290", "291", "293", "294", "295", "296", "297"}:
            note = str(row.get("teacher_note", "")) + " " + str(row.get("source_locator", ""))
            if any(token in str(row.get("source_locator", "")) for token in ("QR", "video")) and not any(
                token in note.casefold() for token in ("video", "kanıt", "izlen", "qr")
            ):
                failures.append(f"TEMA04_MEDIA_BOUNDARY_MISSING:{row.get('mirror_id')}")

    # Writing: only the real 3+3 questions are QUESTIONs; production and sharing remain processes.
    writing = rows_in(entries, 298, 302)
    writing_questions = [row for row in writing if row.get("presentation_type") == "QUESTION"]
    if len(writing) != 13 or len(writing_questions) != 6:
        failures.append(f"TEMA04_WRITING_GRANULARITY:{len(writing)}/{len(writing_questions)}")
    if by_id.get("T4V23_P302_PAYLASIM", {}).get("presentation_type") != "PROCESS":
        failures.append("TEMA04_P302_SHARE_ACTION_MUST_NOT_BECOME_QUESTION")
    if by_id.get("T4V23_P302_RUBRIK", {}).get("presentation_type") != "ASSESSMENT":
        failures.append("TEMA04_WRITING_QR_RUBRIC_BOUNDARY")

    # Theme assessment: 14 printed questions = 14 recognizable cards, in source order.
    assessment_rows = rows_in(entries, 303, 307)
    assessment_questions = [row for row in assessment_rows if row.get("presentation_type") == "QUESTION"]
    require_exact_ids(failures, "ASSESSMENT_14", ids(assessment_questions), ASSESSMENT_Q)
    if len(assessment_rows) != 14 or len(assessment_questions) != 14:
        failures.append(f"TEMA04_ASSESSMENT_GRANULARITY:{len(assessment_rows)}/{len(assessment_questions)}")
    q5 = by_id.get("T4V23_P305_Q05", {})
    if q5.get("rights_mode") != "PAGE_REFERENCE" or "görsel" not in str(q5.get("teacher_note", "")).casefold():
        failures.append("TEMA04_Q5_VISUAL_LAYER_BOUNDARY")
    for mid, key in (("T4V23_P307_Q13", "13"), ("T4V23_P307_Q14", "14")):
        row = by_id.get(mid, {})
        if tuple(row.get("answer_keys", [])) != (key,):
            failures.append(f"TEMA04_AIDIYET_COMPONENT_DRIFT:{mid}")
        note = str(row.get("teacher_note", "")).casefold()
        if "video" not in note or not any(token in note for token in ("kanıt", "sahne", "olay", "ayrıntı")):
            failures.append(f"TEMA04_AIDIYET_MEDIA_BOUNDARY:{mid}")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "metrics": {
            **metrics,
            "theme4_full_reference": not failures,
            "fragment_count": len(mirrors),
            "assessment_source_questions": len(assessment_questions),
            "listening_source_questions": len(listening_questions),
            "writing_source_questions": len(writing_questions),
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
