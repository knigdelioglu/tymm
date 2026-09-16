#!/usr/bin/env python3
"""Source-parity gate for the complete Theme 3 Teacher Guide V2.3 (s.160-235)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_teacher_guide_v23_generic import discover_mirror_paths, read_json, validate

EXPECTED = {
    "mirror_files": 7,
    "scope": "160-235",
    "entries": 146,
    "questions": 114,
    "recognizable_questions": 114,
    "component_projected_entries": 115,
    "shared_canonical_items": 28,
    "review_required_fragments": 4,
    "component_registry_entries": 44,
    "component_registry_used": 44,
}

EXPECTED_FRAGMENTS = {
    "160-163": "PILOT",
    "164-193": "REFERENCE_QUALITY",
    "194-209": "REFERENCE_QUALITY",
    "210-214": "REVIEW_REQUIRED",
    "215-224": "REVIEW_REQUIRED",
    "225-229": "REVIEW_REQUIRED",
    "230-235": "REVIEW_REQUIRED",
}

HUZUR_METNI_ANLAYALIM = {
    "T3V23_P175_Q01", "T3V23_P175_Q02",
    *{f"T3V23_P176_Q{n:02d}" for n in range(3, 14)},
    "T3V23_P177_Q14",
}

ASSESSMENT_IDS = {
    "T3V23_P230_Q01", "T3V23_P230_Q02",
    *{f"T3V23_P231_Q{n:02d}" for n in range(3, 7)},
    "T3V23_P232_Q07",
    *{f"T3V23_P233_Q{n:02d}" for n in range(8, 12)},
    *{f"T3V23_P234_Q{n:02d}" for n in range(12, 16)},
    "T3V23_P235_Q16",
}

ASSESSMENT_COMPONENTS = {
    "T3V23_P230_Q01": ("degerlendirme",),
    "T3V23_P230_Q02": ("sentez_ornegi",),
    "T3V23_P231_Q03": ("3",),
    "T3V23_P231_Q04": ("4",),
    "T3V23_P231_Q05": ("5",),
    "T3V23_P231_Q06": ("6",),
    "T3V23_P232_Q07": ("7",),
    "T3V23_P233_Q08": ("8",),
    "T3V23_P233_Q09": ("9",),
    "T3V23_P233_Q10": ("10",),
    "T3V23_P233_Q11": ("11",),
    "T3V23_P234_Q12": ("12",),
    "T3V23_P234_Q13": ("13",),
    "T3V23_P234_Q14": ("14",),
    "T3V23_P234_Q15": ("15",),
    "T3V23_P235_Q16": (),
}


def page_span(entry: dict) -> tuple[int, int]:
    text = str(entry.get("printed_page_range", "0"))
    parts = text.replace("–", "-").replace("—", "-").split("-")
    start = int(parts[0])
    return start, int(parts[-1])


def entries_in(entries: list[dict], start: int, end: int) -> list[dict]:
    result = []
    for entry in entries:
        left, right = page_span(entry)
        if left >= start and right <= end:
            result.append(entry)
    return result


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

    for key, value in EXPECTED.items():
        if metrics.get(key) != value:
            failures.append(f"TEMA03_METRIC_PARITY:{key}:{metrics.get(key)}!={value}")

    mirrors = [read_json(path) for path in discover_mirror_paths(mirror_path)]
    entries = [entry for mirror in mirrors for entry in mirror.get("entries", [])]

    actual_fragments = {
        str(mirror.get("scope", {}).get("printed_page_range")): mirror.get("scope", {}).get("status")
        for mirror in mirrors
    }
    if actual_fragments != EXPECTED_FRAGMENTS:
        failures.append(f"TEMA03_FRAGMENT_PARITY:{actual_fragments!r}")

    # Opening: six real questions; theme reference itself is not converted to a fake question.
    opening = entries_in(entries, 160, 163)
    opening_questions = [entry for entry in opening if entry.get("presentation_type") == "QUESTION"]
    if len(opening) != 7 or len(opening_questions) != 6:
        failures.append(f"TEMA03_OPENING_PARITY:{len(opening)}/{len(opening_questions)}")

    # Huzur: the source has 14 separate Metni Anlayalım questions (1-14).
    huzur_metni = [entry for entry in entries if entry.get("mirror_id") in HUZUR_METNI_ANLAYALIM]
    huzur_keys = {tuple(entry.get("answer_keys", [])) for entry in huzur_metni}
    if len(huzur_metni) != 14 or huzur_keys != {(str(n),) for n in range(1, 15)}:
        failures.append("TEMA03_HUZUR_MUST_KEEP_14_DISTINCT_METNI_ANLAYALIM_QUESTIONS")

    # Biography/tezkire and speaking retain the already verified natural source granularity.
    biography = entries_in(entries, 194, 209)
    biography_questions = [entry for entry in biography if entry.get("presentation_type") == "QUESTION"]
    if len(biography) != 33 or len(biography_questions) != 28:
        failures.append(f"TEMA03_BIOGRAPHY_PARITY:{len(biography)}/{len(biography_questions)}")

    speaking = entries_in(entries, 210, 214)
    speaking_questions = [entry for entry in speaking if entry.get("presentation_type") == "QUESTION"]
    if len(speaking) != 8 or len(speaking_questions) != 4:
        failures.append(f"TEMA03_SPEAKING_PARITY:{len(speaking)}/{len(speaking_questions)}")

    # Listening: 22 source questions + five natural process/reference blocks.
    listening = entries_in(entries, 215, 224)
    listening_questions = [entry for entry in listening if entry.get("presentation_type") == "QUESTION"]
    listening_nonquestions = [entry for entry in listening if entry.get("presentation_type") != "QUESTION"]
    if len(listening) != 27 or len(listening_questions) != 22 or len(listening_nonquestions) != 5:
        failures.append(
            f"TEMA03_LISTENING_NATURAL_GRANULARITY:{len(listening)}/{len(listening_questions)}/{len(listening_nonquestions)}"
        )
    if len([e for e in listening_questions if e.get("printed_page_range") == "215"]) != 3:
        failures.append("TEMA03_P215_MUST_KEEP_3_SOURCE_QUESTIONS")
    if len([e for e in listening_questions if str(e.get("mirror_id", "")).startswith("T3V23_P218_HATIR_Q")]) != 2:
        failures.append("TEMA03_P218_MUST_KEEP_2_HATIRLAYALIM_QUESTIONS")

    media_questions = [e for e in listening_questions if "QR medya gerekli" in str(e.get("source_locator", ""))]
    if len(media_questions) < 10:
        failures.append(f"TEMA03_MEDIA_BOUND_QUESTION_COVERAGE_TOO_LOW:{len(media_questions)}")
    for entry in media_questions:
        combined = " ".join(str(entry.get(k, "")) for k in ("teacher_note", "source_locator", "prompt_display")).casefold()
        if not any(token in combined for token in ("medya", "duy", "izle", "kanıt", "hazır")):
            failures.append(f"TEMA03_MEDIA_EVIDENCE_BOUNDARY_MISSING:{entry.get('mirror_id')}")

    # Writing is a process, not a question bank: seven natural blocks and zero invented QUESTION cards.
    writing = entries_in(entries, 225, 229)
    writing_questions = [entry for entry in writing if entry.get("presentation_type") == "QUESTION"]
    if len(writing) != 7 or writing_questions:
        failures.append(f"TEMA03_WRITING_NATURAL_GRANULARITY:{len(writing)}/{len(writing_questions)}")
    p228 = [entry for entry in writing if entry.get("mirror_id") == "T3V23_P228_YAZMA_DEGER"]
    writing_qr_boundary = False
    if len(p228) == 1:
        text = " ".join(str(p228[0].get(k, "")) for k in ("teacher_note", "source_locator")).casefold()
        writing_qr_boundary = "qr" in text and "görünmeyen" in text
    if not writing_qr_boundary:
        failures.append("TEMA03_WRITING_QR_BOUNDARY_MISSING")

    # Theme assessment: exactly 16 source questions, each mapped to its real book number.
    assessment = entries_in(entries, 230, 235)
    assessment_questions = [entry for entry in assessment if entry.get("presentation_type") == "QUESTION"]
    assessment_ids = {str(entry.get("mirror_id")) for entry in assessment_questions}
    if len(assessment) != 16 or len(assessment_questions) != 16 or assessment_ids != ASSESSMENT_IDS:
        failures.append(f"TEMA03_ASSESSMENT_16_QUESTION_PARITY:{len(assessment)}/{len(assessment_questions)}")

    by_id = {str(entry.get("mirror_id")): entry for entry in assessment_questions}
    for mirror_id, expected_keys in ASSESSMENT_COMPONENTS.items():
        entry = by_id.get(mirror_id)
        if not entry:
            continue
        actual_keys = tuple(entry.get("answer_keys", []))
        if actual_keys != expected_keys:
            failures.append(f"TEMA03_ASSESSMENT_COMPONENT_DRIFT:{mirror_id}:{actual_keys!r}!={expected_keys!r}")

    # Canonical source-numbering regression guard for the two groups that were previously shifted.
    assessment_section = read_json(root / "courses/TDE_11/teacher_guide/TEMA_03/sections/06_tema_olcme.json")
    canonical = {
        item["item_id"]: item
        for unit in assessment_section.get("guide_units", [])
        for item in unit.get("items", [])
    }
    q3_6 = canonical.get("T3_G21_P231_Q3_6", {}).get("expected_answer", {})
    if set(q3_6) != {"3", "4", "5", "6"} or q3_6.get("5") != "E" or q3_6.get("6") != "C" or not isinstance(q3_6.get("3"), dict):
        failures.append("TEMA03_CANONICAL_Q3_6_SOURCE_NUMBERING_REGRESSION")
    q7_11 = canonical.get("T3_G21_P232_233_Q7_11", {}).get("expected_answer", {})
    if q7_11.get("9") != "C" or q7_11.get("8") == "C":
        failures.append("TEMA03_CANONICAL_Q8_Q9_SOURCE_NUMBERING_REGRESSION")

    q15 = by_id.get("T3V23_P234_Q15", {})
    q15_text = " ".join(str(q15.get(k, "")) for k in ("teacher_note", "source_locator")).casefold()
    assessment_media_boundary = "qr" in q15_text and any(token in q15_text for token in ("gözledi", "video", "medya"))
    if not assessment_media_boundary:
        failures.append("TEMA03_ASSESSMENT_Q15_MEDIA_BOUNDARY_MISSING")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "metrics": {
            **metrics,
            "pdf_verified_opening_questions": len(opening_questions),
            "pdf_verified_huzur_metni_anlayalim_questions": len(huzur_metni),
            "pdf_verified_biography_tezkire_questions": len(biography_questions),
            "pdf_verified_speaking_questions": len(speaking_questions),
            "pdf_verified_listening_questions": len(listening_questions),
            "listening_natural_process_blocks": len(listening_nonquestions),
            "pdf_verified_writing_questions": len(writing_questions),
            "writing_natural_process_blocks": len(writing),
            "pdf_verified_theme_assessment_questions": len(assessment_questions),
            "writing_qr_boundary_preserved": writing_qr_boundary,
            "assessment_media_boundary_preserved": assessment_media_boundary,
            "full_theme_scope": metrics.get("scope") == "160-235",
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
