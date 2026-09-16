#!/usr/bin/env python3
"""Source-parity gate for the Theme 2 Teacher Guide V2.3 checkpoint (s.84-128)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_teacher_guide_v23_generic import discover_mirror_paths, note_text, read_json, validate

REQUIRED_QUESTION_IDS = {
    "T2V23_P86_Q01", "T2V23_P86_Q02", "T2V23_P86_Q03",
    "T2V23_P87_Q01", "T2V23_P87_Q02", "T2V23_P87_Q03",
    "T2V23_P88_Q01", "T2V23_P88_Q02", "T2V23_P88_Q03", "T2V23_P88_Q04", "T2V23_P88_Q05", "T2V23_P88_Q06",
    "T2V23_P90_Q01", "T2V23_P90_Q02",
    "T2V23_P96_Q03",
    "T2V23_P98_NARRATIVE", "T2V23_P99_Q02", "T2V23_P99_Q03",
    "T2V23_P100_Q01", "T2V23_P100_Q02", "T2V23_P100_Q03", "T2V23_P100_Q04",
    "T2V23_P100_Q05", "T2V23_P100_Q06", "T2V23_P100_Q07", "T2V23_P100_Q08",
    "T2V23_P101_Q09", "T2V23_P101_Q10", "T2V23_P102_Q11",
    "T2V23_P106_Q1A", "T2V23_P107_Q1B", "T2V23_P107_AYTMATOV",
    "T2V23_P108_Q01", "T2V23_P108_Q02", "T2V23_P108_Q03",
    "T2V23_P112_Q01", "T2V23_P112_Q02", "T2V23_P112_Q03", "T2V23_P112_Q04", "T2V23_P112_Q05",
    "T2V23_P113_Q01", "T2V23_P113_Q02", "T2V23_P113_Q03", "T2V23_P113_Q04", "T2V23_P113_Q05",
    "T2V23_P117_Q01", "T2V23_P117_Q02", "T2V23_P117_Q03", "T2V23_P117_BILGE_KAGAN",
    "T2V23_P119_Q01", "T2V23_P120_Q02", "T2V23_P120_DIL_KULTUR_TARIH",
    "T2V23_P121_Q01", "T2V23_P121_Q02", "T2V23_P121_NARRATOR",
    "T2V23_P122_Q02", "T2V23_P122_Q03", "T2V23_P122_Q04",
    "T2V23_P123_Q05", "T2V23_P123_Y01", "T2V23_P123_Y02", "T2V23_P123_Y03",
    "T2V23_P124_Y04", "T2V23_P124_Y05", "T2V23_P125_ORHUN_VALUE",
    "T2V23_P127_DLT_Q01", "T2V23_P127_DLT_Q02", "T2V23_P127_DLT_Q03", "T2V23_P127_DLT_Q04",
    "T2V23_P127_DLT_Q05", "T2V23_P127_DLT_Q06", "T2V23_P127_DLT_Q07",
    "T2V23_P127_KAPLAN_Q01", "T2V23_P127_KAPLAN_Q02",
    "T2V23_P128_SPREAD_Q03", "T2V23_P128_REFLECT_Q01", "T2V23_P128_REFLECT_Q02", "T2V23_P128_REFLECT_Q03",
}

REQUIRED_P100_IDS = {f"T2V23_P100_Q{n:02d}" for n in range(1, 9)}
REQUIRED_P112_IDS = {f"T2V23_P112_Q{n:02d}" for n in range(1, 6)}
REQUIRED_P113_IDS = {f"T2V23_P113_Q{n:02d}" for n in range(1, 6)}
REQUIRED_P117_IDS = {"T2V23_P117_Q01", "T2V23_P117_Q02", "T2V23_P117_Q03", "T2V23_P117_BILGE_KAGAN"}
REQUIRED_ORHUN_ANALYSIS_IDS = {
    "T2V23_P121_NARRATOR",
    "T2V23_P122_Q02", "T2V23_P122_Q03", "T2V23_P122_Q04",
    "T2V23_P123_Q05", "T2V23_P123_Y01", "T2V23_P123_Y02", "T2V23_P123_Y03",
    "T2V23_P124_Y04", "T2V23_P124_Y05",
}
REQUIRED_DLT_IDS = {
    *(f"T2V23_P127_DLT_Q{n:02d}" for n in range(1, 8)),
    "T2V23_P127_KAPLAN_Q01", "T2V23_P127_KAPLAN_Q02",
}
REQUIRED_P128_IDS = {
    "T2V23_P128_SPREAD_Q03",
    "T2V23_P128_REFLECT_Q01", "T2V23_P128_REFLECT_Q02", "T2V23_P128_REFLECT_Q03",
}
REQUIRED_GRAMMAR_IDS = {
    "T2V23_P102_GRAMMAR_01",
    "T2V23_P103_GRAMMAR_02",
    "T2V23_P104_GRAMMAR_03",
    "T2V23_P104_GRAMMAR_04",
}
REQUIRED_P108_IDS = {
    "T2V23_P108_Q01",
    "T2V23_P108_Q02",
    "T2V23_P108_Q03",
    "T2V23_P108_110_MEMOIR",
}
REQUIRED_HEADINGS = {
    "Temaya Başlarken — Vatan yahut Silistre",
    "Düşünelim Paylaşalım — Ortak Türk Alfabesi",
    "Konuya Başlarken — Türklerde Toylar, Merasimler, Festivaller ve Şenlikler",
    "Okumayı Yönetebilme — Oğulla Buluşma",
    "Anlam Oluşturabilme — Söz Varlığımız",
    "Metni Anlayalım — Oğulla Buluşma",
    "Çözümleyebilme — Fark Edelim / hikâye haritası",
    "Eski İstanbul’dan Çizgiler — Anı metni",
    "Süreci Değerlendirebilme — Oğulla Buluşma",
    "Çıkış Kartı — Üç Yaz / İki Sor / Bir Paylaş",
    "Konuya Başlarken — Orhun Vadisi",
    "Okumayı Yönetebilme — Kül Tigin Âbidesi",
    "Metni Anlayalım — Kül Tigin Âbidesi",
    "Karşılaştıralım — Oğulla Buluşma / Kül Tigin Âbidesi",
    "Çözümleyebilme — anlatıcı ve amaç",
    "Yorumlayalım — Orhun Abideleri",
    "Ders Dışı Etkinlik — Orhun ve sosyal bilimler",
    "Ara Metin — Dîvânu Lugâti’t-Türk",
    "Fark Edelim — Türk Edebiyatı ve Türk Milletinin Kültürel Değerleri",
    "Fark Edelim — Türkçenin tarihî yayılımı",
    "Süreci Değerlendirebilme — Kül Tigin Âbidesi",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.repo_root.resolve()
    mirror_path = root / "courses/TDE_11/teacher_guide/TEMA_02/book_mirror_v23.json"
    manifest_path = root / "courses/TDE_11/teacher_guide/TEMA_02/teacher_guide.json"
    schema_path = root / "skill/tymm-material-planner/schemas/teacher_guide_book_mirror.schema.json"
    markdown_path = root / "courses/TDE_11/teacher_guide/TEMA_02/TEACHER_GUIDE_V23_PILOT.md"

    report = validate(root, mirror_path, manifest_path, schema_path, markdown_path)
    failures = list(report["failures"])
    warnings = list(report["warnings"])
    seen = set(report.get("seen_mirror_ids", []))
    headings = set(report.get("headings", []))

    metrics = report["metrics"]
    if metrics.get("scope") != "84-128":
        failures.append(f"TEMA02_CHECKPOINT_SCOPE_MUST_BE_84_128:{metrics.get('scope')}")
    if metrics.get("entries") != 102:
        failures.append(f"TEMA02_ENTRY_PARITY_MUST_BE_102:{metrics.get('entries')}")
    if metrics.get("questions") != 78 or metrics.get("recognizable_questions") != 78:
        failures.append(
            f"TEMA02_QUESTION_PARITY_MUST_BE_78_78:{metrics.get('recognizable_questions')}/{metrics.get('questions')}"
        )
    if metrics.get("component_registry_entries") != 31 or metrics.get("component_registry_used") != 31:
        failures.append(
            f"TEMA02_COMPONENT_REGISTRY_MUST_BE_31_31:{metrics.get('component_registry_used')}/{metrics.get('component_registry_entries')}"
        )
    if metrics.get("component_projected_entries") != 94:
        failures.append(f"TEMA02_COMPONENT_PROJECTION_PARITY_MUST_BE_94:{metrics.get('component_projected_entries')}")
    if metrics.get("shared_canonical_items") != 21:
        failures.append(f"TEMA02_SHARED_CANONICAL_PARITY_MUST_BE_21:{metrics.get('shared_canonical_items')}")

    missing_questions = sorted(REQUIRED_QUESTION_IDS - seen)
    if missing_questions:
        failures.append("TEMA02_REQUIRED_QUESTIONS_MISSING:" + ",".join(missing_questions))
    for label, required in (
        ("P100", REQUIRED_P100_IDS),
        ("P112", REQUIRED_P112_IDS),
        ("P113", REQUIRED_P113_IDS),
        ("P117", REQUIRED_P117_IDS),
        ("ORHUN_ANALYSIS", REQUIRED_ORHUN_ANALYSIS_IDS),
        ("DLT", REQUIRED_DLT_IDS),
        ("P128", REQUIRED_P128_IDS),
        ("GRAMMAR", REQUIRED_GRAMMAR_IDS),
        ("MEMOIR", REQUIRED_P108_IDS),
    ):
        missing = sorted(required - seen)
        if missing:
            failures.append(f"TEMA02_{label}_TASKS_MISSING:" + ",".join(missing))

    missing_headings = sorted(REQUIRED_HEADINGS - headings)
    if missing_headings:
        failures.append("TEMA02_BOOK_HEADINGS_MISSING:" + " | ".join(missing_headings))

    mirrors = [read_json(path) for path in discover_mirror_paths(mirror_path)]
    entries = [entry for mirror in mirrors for entry in mirror.get("entries", [])]

    p88 = [entry for entry in entries if str(entry.get("mirror_id", "")).startswith("T2V23_P88_Q")]
    if len(p88) != 6 or any(entry.get("presentation_type") != "QUESTION" for entry in p88):
        failures.append(f"TEMA02_P88_MUST_HAVE_6_QUESTION_CARDS:{len(p88)}")

    p88_q1 = [entry for entry in entries if entry.get("mirror_id") == "T2V23_P88_Q01"]
    if len(p88_q1) != 1:
        failures.append("TEMA02_P88_MEDIA_BOUNDARY_ENTRY_MISSING")
    else:
        note = note_text(p88_q1[0]).casefold()
        locator = str(p88_q1[0].get("source_locator", "")).casefold()
        if "video" not in note or "izledi" not in note or "video" not in locator:
            failures.append("TEMA02_P88_MEDIA_BOUNDARY_NOT_EXPLICIT")

    p113 = [entry for entry in entries if entry.get("mirror_id") in REQUIRED_P113_IDS]
    if len(p113) != 5 or any(entry.get("presentation_type") != "QUESTION" for entry in p113):
        failures.append(f"TEMA02_P113_MUST_HAVE_5_QUESTION_CARDS:{len(p113)}")
    p113_q1 = [entry for entry in entries if entry.get("mirror_id") == "T2V23_P113_Q01"]
    if len(p113_q1) != 1:
        failures.append("TEMA02_P113_MEDIA_BOUNDARY_ENTRY_MISSING")
    else:
        note = note_text(p113_q1[0]).casefold()
        locator = str(p113_q1[0].get("source_locator", "")).casefold()
        if "qr" not in note or "görül" not in note or "video" not in locator:
            failures.append("TEMA02_P113_MEDIA_BOUNDARY_NOT_EXPLICIT")

    dlt_questions = [entry for entry in entries if entry.get("mirror_id") in REQUIRED_DLT_IDS]
    if len(dlt_questions) != 9 or any(entry.get("presentation_type") != "QUESTION" for entry in dlt_questions):
        failures.append(f"TEMA02_DLT_MUST_HAVE_7_PLUS_2_QUESTION_CARDS:{len(dlt_questions)}")

    p128 = [entry for entry in entries if entry.get("mirror_id") in REQUIRED_P128_IDS]
    if len(p128) != 4 or any(entry.get("presentation_type") != "QUESTION" for entry in p128):
        failures.append(f"TEMA02_P128_MUST_HAVE_1_PLUS_3_QUESTION_CARDS:{len(p128)}")

    fragment_88_112 = [mirror for mirror in mirrors if mirror.get("scope", {}).get("printed_page_range") == "88-112"]
    if len(fragment_88_112) != 1 or fragment_88_112[0].get("scope", {}).get("status") != "REVIEW_REQUIRED":
        failures.append("TEMA02_88_112_MUST_REMAIN_REVIEW_REQUIRED")
    fragment_113_128 = [mirror for mirror in mirrors if mirror.get("scope", {}).get("printed_page_range") == "113-128"]
    if len(fragment_113_128) != 1 or fragment_113_128[0].get("scope", {}).get("status") != "REVIEW_REQUIRED":
        failures.append("TEMA02_113_128_MUST_REMAIN_REVIEW_REQUIRED")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "metrics": {
            **metrics,
            "pdf_verified_p88_questions": 6,
            "pdf_verified_p100_questions": 8,
            "pdf_verified_p112_questions": 5,
            "pdf_verified_p113_questions": 5,
            "pdf_verified_p117_questions": 4,
            "pdf_verified_orhun_analysis_questions": 10,
            "pdf_verified_dlt_questions": 9,
            "pdf_verified_p128_questions": 4,
            "pdf_verified_grammar_tasks": 4,
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
