#!/usr/bin/env python3
"""Source-parity gate for Theme 4 Teacher Guide V2.3 checkpoint (s.236-279)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_teacher_guide_v23_generic import discover_mirror_paths, read_json, validate

OPENING_QUESTIONS = {
    "T4V23_P238_Q01": ("1",),
    "T4V23_P238_Q02": ("2",),
    "T4V23_P239_Q03": ("3",),
    "T4V23_P239_Q04": ("4",),
    "T4V23_P239_Q05": ("5",),
}

THEATRE_Q251 = {
    "T4V23_P251_252_Q01",
    "T4V23_P251_252_Q02",
    "T4V23_P252_Q03",
}
THEATRE_Q257_258 = {
    "T4V23_P257_Q01", "T4V23_P257_258_Q02",
    "T4V23_P258_Q01", "T4V23_P258_Q02",
}
THEATRE_Q259_260 = {
    "T4V23_P259_Q01", "T4V23_P259_Q02",
    "T4V23_P260_Q01", "T4V23_P260_Q02", "T4V23_P260_Q03", "T4V23_P260_Q04",
}
THEATRE_Q262 = {"T4V23_P262_Q01", "T4V23_P262_Q02"}

MERDIVEN_P268 = {
    "T4V23_P268_Q01", "T4V23_P268_Q02", "T4V23_P268_Q03",
}
MERDIVEN_METNI_ANLAYALIM = {
    *{f"T4V23_P269_Q{n:02d}" for n in range(1, 8)},
    "T4V23_P270_Q08",
}
MERDIVEN_P272 = {"T4V23_P272_Q01", "T4V23_P272_Q02"}
MERDIVEN_P273 = {"T4V23_P273_Q01", "T4V23_P273_Q02"}
MERDIVEN_P275_277 = {
    "T4V23_P275_Q01", "T4V23_P275_Q02A", "T4V23_P275_Q02B",
    "T4V23_P276_Q03", "T4V23_P277_Q01", "T4V23_P277_Q02",
}

EXPECTED = {
    "mirror_files": 3,
    "scope": "236-279",
    "entries": 73,
    "questions": 49,
    "recognizable_questions": 49,
    "component_projected_entries": 55,
    "shared_canonical_items": 16,
    "review_required_fragments": 0,
    "component_registry_entries": 32,
    "component_registry_used": 32,
}

EXPECTED_FRAGMENTS = {
    "236-239": "PILOT",
    "240-262": "REFERENCE_QUALITY",
    "263-279": "REFERENCE_QUALITY",
}


def page_span(entry: dict) -> tuple[int, int]:
    raw = str(entry.get("printed_page_range", "0")).replace("–", "-").replace("—", "-")
    parts = raw.split("-")
    return int(parts[0]), int(parts[-1])


def entries_in(entries: list[dict], start: int, end: int) -> list[dict]:
    result = []
    for entry in entries:
        left, right = page_span(entry)
        if left >= start and right <= end:
            result.append(entry)
    return result


def require_questions(failures: list[str], entries: list[dict], label: str, ids: set[str]) -> None:
    rows = [entry for entry in entries if entry.get("mirror_id") in ids]
    if len(rows) != len(ids) or any(entry.get("presentation_type") != "QUESTION" for entry in rows):
        failures.append(f"TEMA04_{label}_QUESTION_PARITY:{len(rows)}/{len(ids)}")


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

    actual_fragments = {
        str(mirror.get("scope", {}).get("printed_page_range")): mirror.get("scope", {}).get("status")
        for mirror in mirrors
    }
    if actual_fragments != EXPECTED_FRAGMENTS:
        failures.append(f"TEMA04_FRAGMENT_PARITY:{actual_fragments!r}")

    opening = entries_in(entries, 236, 239)
    opening_questions = [entry for entry in opening if entry.get("presentation_type") == "QUESTION"]
    if len(opening) != 7 or len(opening_questions) != 5:
        failures.append(f"TEMA04_OPENING_PARITY:{len(opening)}/{len(opening_questions)}")

    yunus = by_id.get("T4V23_P237_YUNUS_REFERENCE", {})
    if yunus.get("presentation_type") != "REFERENCE":
        failures.append("TEMA04_P237_YUNUS_MUST_NOT_BECOME_QUESTION")
    if any(entry.get("presentation_type") == "QUESTION" and entry.get("printed_page_range") == "237" for entry in entries):
        failures.append("TEMA04_P237_SOURCE_HAS_NO_QUESTION")

    for mirror_id, expected_keys in OPENING_QUESTIONS.items():
        entry = by_id.get(mirror_id)
        if not entry or entry.get("presentation_type") != "QUESTION":
            failures.append(f"TEMA04_OPENING_QUESTION_MISSING:{mirror_id}")
            continue
        if tuple(entry.get("answer_keys", [])) != expected_keys:
            failures.append(f"TEMA04_OPENING_ANSWER_KEY_DRIFT:{mirror_id}")

    theatre = entries_in(entries, 240, 262)
    theatre_questions = [entry for entry in theatre if entry.get("presentation_type") == "QUESTION"]
    theatre_nonquestions = [entry for entry in theatre if entry.get("presentation_type") != "QUESTION"]
    if len(theatre) != 32 or len(theatre_questions) != 22 or len(theatre_nonquestions) != 10:
        failures.append(f"TEMA04_THEATRE_NATURAL_GRANULARITY:{len(theatre)}/{len(theatre_questions)}/{len(theatre_nonquestions)}")

    require_questions(failures, theatre, "P251_252", THEATRE_Q251)
    require_questions(failures, theatre, "P257_258", THEATRE_Q257_258)
    require_questions(failures, theatre, "P259_260", THEATRE_Q259_260)
    require_questions(failures, theatre, "P262", THEATRE_Q262)

    # Source has three real Metni Anlayalım questions here; do not recreate V2's artificial four-card split.
    source_q251 = [entry for entry in theatre_questions if entry.get("mirror_id") in THEATRE_Q251]
    if len(source_q251) != 3:
        failures.append("TEMA04_P251_252_MUST_KEEP_3_SOURCE_QUESTIONS")
    q1 = by_id.get("T4V23_P251_252_Q01", {})
    if tuple(q1.get("answer_keys", [])) != ("source_q1_topic_purpose_author",):
        failures.append("TEMA04_P251_Q1_MUST_KEEP_TOPIC_PURPOSE_AUTHOR_TOGETHER")
    q2 = by_id.get("T4V23_P251_252_Q02", {})
    if tuple(q2.get("answer_keys", [])) != ("source_q2_character",):
        failures.append("TEMA04_P251_Q2_CHARACTER_SUBPARTS_MUST_STAY_TOGETHER")

    theatre_process_ids = {
        "T4V23_P240_TIYATRO_ONBILGI",
        "T4V23_P241_242_OKUMA_YONETIM",
        "T4V23_P248_249_TIYATRO_ISLEVI",
        "T4V23_P260_SOSYAL_BILIM",
        "T4V23_P261_CATISMA",
    }
    for mid in theatre_process_ids:
        if by_id.get(mid, {}).get("presentation_type") != "PROCESS":
            failures.append(f"TEMA04_PROCESS_BOUNDARY_DRIFT:{mid}")
    if by_id.get("T4V23_P256_YAPI", {}).get("presentation_type") != "TABLE":
        failures.append("TEMA04_P256_STRUCTURE_MUST_REMAIN_TABLE_PROCESS")
    if {str(e.get("mirror_id")) for e in theatre_questions if e.get("printed_page_range") == "262"} != THEATRE_Q262:
        failures.append("TEMA04_P262_MUST_KEEP_2_SOURCE_QUESTIONS")

    merdiven = entries_in(entries, 263, 279)
    merdiven_questions = [entry for entry in merdiven if entry.get("presentation_type") == "QUESTION"]
    merdiven_nonquestions = [entry for entry in merdiven if entry.get("presentation_type") != "QUESTION"]
    if len(merdiven) != 34 or len(merdiven_questions) != 22 or len(merdiven_nonquestions) != 12:
        failures.append(f"TEMA04_MERDIVEN_NATURAL_GRANULARITY:{len(merdiven)}/{len(merdiven_questions)}/{len(merdiven_nonquestions)}")

    require_questions(failures, merdiven, "MERDIVEN_P268", MERDIVEN_P268)
    require_questions(failures, merdiven, "MERDIVEN_METNI_ANLAYALIM", MERDIVEN_METNI_ANLAYALIM)
    require_questions(failures, merdiven, "MERDIVEN_P272", MERDIVEN_P272)
    require_questions(failures, merdiven, "MERDIVEN_P273", MERDIVEN_P273)
    require_questions(failures, merdiven, "MERDIVEN_P275_277", MERDIVEN_P275_277)

    # Source Q1 asks about the elderly and young man together. Keep the pair in one card.
    merdiven_q1 = by_id.get("T4V23_P269_Q01", {})
    if tuple(merdiven_q1.get("answer_keys", [])) != ("ihtiyar", "delikanli"):
        failures.append("TEMA04_MERDIVEN_Q1_MUST_KEEP_TWO_CHARACTERS_TOGETHER")

    # The source has eight numbered Metni Anlayalım questions, all of which must remain independently findable.
    metni_rows = [entry for entry in merdiven_questions if entry.get("mirror_id") in MERDIVEN_METNI_ANLAYALIM]
    if len(metni_rows) != 8:
        failures.append(f"TEMA04_MERDIVEN_MUST_KEEP_8_METNI_ANLAYALIM:{len(metni_rows)}")

    # p271 has two source question foci, but they form one natural two-text comparison activity.
    p271 = by_id.get("T4V23_P271_FARK_EDELIM", {})
    if p271.get("presentation_type") != "COMPARISON":
        failures.append("TEMA04_P271_MUST_REMAIN_COMPARISON_BLOCK")
    p271_heading = str(p271.get("book_heading", ""))
    if "Soru 1" not in p271_heading or "Soru 2" not in p271_heading:
        failures.append("TEMA04_P271_MUST_EXPOSE_BOTH_SOURCE_QUESTION_FOCI")

    # Natural process boundaries: source subquestions organize collaborative analysis, not a question bank.
    merdiven_type_contract = {
        "T4V23_P263_KONUYA_BASLARKEN": "PROCESS",
        "T4V23_P264_265_OKUMA_YONETIM": "PROCESS",
        "T4V23_P270_CALISMA_KAGIDI": "TABLE",
        "T4V23_P274_KARAKTER_COZUMLEME": "PROCESS",
        "T4V23_P275_YAPI": "TABLE",
        "T4V23_P276_277_CATISMA": "PROCESS",
        "T4V23_P278_DISIPLIN": "TABLE",
        "T4V23_P279_BEGeni": "ASSESSMENT",
        "T4V23_P279_BEYIN_FIRTINASI": "PROCESS",
    }
    for mid, expected_type in merdiven_type_contract.items():
        actual = by_id.get(mid, {}).get("presentation_type")
        if actual != expected_type:
            failures.append(f"TEMA04_MERDIVEN_PROCESS_BOUNDARY_DRIFT:{mid}:{actual}!={expected_type}")

    edgu = by_id.get("T4V23_P278_279_EDGU_POETIKA", {})
    if edgu.get("presentation_type") != "QUESTION" or edgu.get("prompt_mode") not in {"VERBATIM_SHORT", "VERIFIED_SUMMARY"}:
        failures.append("TEMA04_EDGU_POETIKA_QUESTION_MUST_REMAIN_RECOGNIZABLE")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "metrics": {
            **metrics,
            "pdf_verified_opening_questions": len(opening_questions),
            "pdf_verified_theatre_questions": len(theatre_questions),
            "theatre_natural_process_blocks": len(theatre_nonquestions),
            "pdf_verified_merdiven_question_cards": len(merdiven_questions),
            "merdiven_metni_anlayalim_questions": len(metni_rows),
            "merdiven_natural_nonquestion_blocks": len(merdiven_nonquestions),
            "p271_source_question_foci": 2,
            "p237_nonquestion_boundary_preserved": yunus.get("presentation_type") == "REFERENCE",
            "p251_source_granularity_preserved": len(source_q251) == 3,
            "p271_comparison_boundary_preserved": p271.get("presentation_type") == "COMPARISON",
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
