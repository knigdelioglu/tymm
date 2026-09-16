#!/usr/bin/env python3
"""Source-parity gate for the Theme 2 Teacher Guide V2.3 checkpoint (s.84-147).

The generic V2.3 validator owns schema, recognizability, component projection,
semantic-repeat and book-first Markdown invariants. This module locks only the
Theme 2 source-parity facts that must not regress as coverage grows.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_teacher_guide_v23_generic import discover_mirror_paths, note_text, read_json, validate


def ids(prefix: str, start: int, end: int, width: int = 2) -> set[str]:
    return {f"{prefix}{n:0{width}d}" for n in range(start, end + 1)}


REQUIRED_GROUPS: dict[str, set[str]] = {
    "P88": ids("T2V23_P88_Q", 1, 6),
    "P100": ids("T2V23_P100_Q", 1, 8),
    "P112": ids("T2V23_P112_Q", 1, 5),
    "P113": ids("T2V23_P113_Q", 1, 5),
    "P117": {"T2V23_P117_Q01", "T2V23_P117_Q02", "T2V23_P117_Q03", "T2V23_P117_BILGE_KAGAN"},
    "ORHUN_ANALYSIS": {
        "T2V23_P121_NARRATOR",
        "T2V23_P122_Q02", "T2V23_P122_Q03", "T2V23_P122_Q04",
        "T2V23_P123_Q05", "T2V23_P123_Y01", "T2V23_P123_Y02", "T2V23_P123_Y03",
        "T2V23_P124_Y04", "T2V23_P124_Y05",
    },
    "DLT": {
        *ids("T2V23_P127_DLT_Q", 1, 7),
        "T2V23_P127_KAPLAN_Q01", "T2V23_P127_KAPLAN_Q02",
    },
    "P128": {
        "T2V23_P128_SPREAD_Q03",
        "T2V23_P128_REFLECT_Q01", "T2V23_P128_REFLECT_Q02", "T2V23_P128_REFLECT_Q03",
    },
    "SPEAKING": {
        "T2V23_P129_Q01", "T2V23_P129_Q02", "T2V23_P129_Q03",
        "T2V23_P130_PERFORMANCE", "T2V23_P131_DESIGN",
        "T2V23_P132_Q01", "T2V23_P132_Q02", "T2V23_P132_Q03",
        "T2V23_P132_133_COMPARE", "T2V23_P133_BUILD_REVISE",
        "T2V23_P134_RULES", "T2V23_P135_SELF", "T2V23_P135_QR_LIMIT",
    },
    "LISTENING": {
        "T2V23_P136_Q01", "T2V23_P136_Q02", "T2V23_P137_PLAN",
        "T2V23_P138_Q01", "T2V23_P138_Q02", "T2V23_P138_139_LISTENING_FORMS",
        "T2V23_P140_VOCAB", "T2V23_P141_Q01", "T2V23_P141_Q02",
        "T2V23_P142_Q01", "T2V23_P142_Q02", "T2V23_P142_HUMOR_COMPARE",
        "T2V23_P143_LANGUAGE_COMPARE", "T2V23_P143_TASTE",
        "T2V23_P144_Q01", "T2V23_P144_Q02", "T2V23_P144_Q03", "T2V23_P144_MEDIA_MAP",
        "T2V23_P145_SIX_HATS", "T2V23_P146_OPINION",
        "T2V23_P147_VALUE", "T2V23_P147_REFLECTION",
    },
    "GRAMMAR": {
        "T2V23_P102_GRAMMAR_01", "T2V23_P103_GRAMMAR_02",
        "T2V23_P104_GRAMMAR_03", "T2V23_P104_GRAMMAR_04",
    },
    "MEMOIR": {
        "T2V23_P108_Q01", "T2V23_P108_Q02", "T2V23_P108_Q03", "T2V23_P108_110_MEMOIR",
    },
}

SPEAKING_QUESTIONS = {
    "T2V23_P129_Q01", "T2V23_P129_Q02", "T2V23_P129_Q03",
    "T2V23_P132_Q01", "T2V23_P132_Q02", "T2V23_P132_Q03",
}
LISTENING_QUESTIONS = {
    "T2V23_P136_Q01", "T2V23_P136_Q02",
    "T2V23_P138_Q01", "T2V23_P138_Q02",
    "T2V23_P141_Q01", "T2V23_P141_Q02",
    "T2V23_P142_Q01", "T2V23_P142_Q02",
    "T2V23_P144_Q01", "T2V23_P144_Q02", "T2V23_P144_Q03",
}

REQUIRED_HEADINGS = {
    "Temaya Başlarken — Vatan yahut Silistre",
    "Düşünelim Paylaşalım — Ortak Türk Alfabesi",
    "Konuya Başlarken — Türklerde Toylar, Merasimler, Festivaller ve Şenlikler",
    "Okumayı Yönetebilme — Oğulla Buluşma",
    "Metni Anlayalım — Oğulla Buluşma",
    "Eski İstanbul’dan Çizgiler — Anı metni",
    "Konuya Başlarken — Orhun Vadisi",
    "Okumayı Yönetebilme — Kül Tigin Âbidesi",
    "Metni Anlayalım — Kül Tigin Âbidesi",
    "Karşılaştıralım — Oğulla Buluşma / Kül Tigin Âbidesi",
    "Yorumlayalım — Orhun Abideleri",
    "Ara Metin — Dîvânu Lugâti’t-Türk",
    "Fark Edelim — Türk Edebiyatı ve Türk Milletinin Kültürel Değerleri",
    "Süreci Değerlendirebilme — Kül Tigin Âbidesi",
    "Konuşmayı Yönetebilme — Dünyadaki Türkiye-Türk Dünyası",
    "Performans Görevi — Türk Dünyası Ortak Kültürü",
    "İçerik Oluşturabilme — konuşma metni tasarımı",
    "Düşünelim Paylaşalım — Türk dünyası kültür unsurlarını karşılaştırma",
    "Kural Uygulayabilme — konuşma uygulama ölçütleri",
    "Süreci Değerlendirebilme — Dereceli Puanlama Anahtarı / Akran Değerlendirme",
    "Konuya Başlarken — Âşıklık geleneğinde saz",
    "Konuya Başlarken — Sazım’a / sanat-sanatçı ilişkisi",
    "Dinleme / İzlemeyi Yönetebilme — Âşık Atışması",
    "Hatırlayalım — Halk Şiiri ve Halk Şairleri",
    "Fark Edelim — etkin dinleme / Kontrol Listesi / Gözlem Formu",
    "Anlam Oluşturabilme — Söz Varlığımız",
    "Sıra Sizde — Âşıklık geleneğinin geleceğe taşınması",
    "Metni Anlayalım — Âşık Atışması",
    "Karşılaştıralım — atışma mizahı ve günlük mizah",
    "Karşılaştıralım — atışma dili / günlük dil / Münacaat",
    "Fark Edelim — Usta-Çırak Geleneği / Meşk Usûlü",
    "Çözümleyebilme — âşık atışmasının çok modlu unsurları",
    "Sıra Sizde — Altı Şapka",
    "Sıra Sizde — görüş geliştirme çalışma kâğıdı",
    "Süreci Değerlendirebilme — yansıtıcı yazı",
}

EXPECTED_METRICS = {
    "scope": "84-147",
    "entries": 137,
    "questions": 95,
    "recognizable_questions": 95,
    "component_registry_entries": 33,
    "component_registry_used": 33,
    "component_projected_entries": 125,
    "shared_canonical_items": 28,
}


def require_ids(failures: list[str], seen: set[str], label: str, required: set[str]) -> None:
    missing = sorted(required - seen)
    if missing:
        failures.append(f"TEMA02_{label}_TASKS_MISSING:" + ",".join(missing))


def require_question_cards(
    failures: list[str], entries: list[dict[str, Any]], label: str, required: set[str], count: int
) -> None:
    rows = [entry for entry in entries if entry.get("mirror_id") in required]
    if len(rows) != count or any(entry.get("presentation_type") != "QUESTION" for entry in rows):
        failures.append(f"TEMA02_{label}_QUESTION_CARD_PARITY:{len(rows)}/{count}")


def require_fragment(failures: list[str], mirrors: list[dict[str, Any]], page_range: str) -> None:
    rows = [mirror for mirror in mirrors if mirror.get("scope", {}).get("printed_page_range") == page_range]
    if len(rows) != 1 or rows[0].get("scope", {}).get("status") != "REVIEW_REQUIRED":
        failures.append(f"TEMA02_{page_range.replace('-', '_')}_MUST_REMAIN_REVIEW_REQUIRED")


def require_media_boundary(
    failures: list[str], entries: list[dict[str, Any]], mirror_id: str, note_terms: tuple[str, ...], locator_term: str = "qr"
) -> None:
    rows = [entry for entry in entries if entry.get("mirror_id") == mirror_id]
    if len(rows) != 1:
        failures.append(f"TEMA02_MEDIA_BOUNDARY_ENTRY_MISSING:{mirror_id}")
        return
    note = note_text(rows[0]).casefold()
    locator = str(rows[0].get("source_locator", "")).casefold()
    if any(term.casefold() not in note for term in note_terms) or locator_term.casefold() not in locator:
        failures.append(f"TEMA02_MEDIA_BOUNDARY_NOT_EXPLICIT:{mirror_id}")


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
    metrics = report["metrics"]
    seen = set(report.get("seen_mirror_ids", []))
    headings = set(report.get("headings", []))

    for key, expected in EXPECTED_METRICS.items():
        actual = metrics.get(key)
        if actual != expected:
            failures.append(f"TEMA02_METRIC_PARITY:{key}:{actual}!={expected}")

    for label, required in REQUIRED_GROUPS.items():
        require_ids(failures, seen, label, required)

    missing_headings = sorted(REQUIRED_HEADINGS - headings)
    if missing_headings:
        failures.append("TEMA02_BOOK_HEADINGS_MISSING:" + " | ".join(missing_headings))

    mirrors = [read_json(path) for path in discover_mirror_paths(mirror_path)]
    entries = [entry for mirror in mirrors for entry in mirror.get("entries", [])]

    require_question_cards(failures, entries, "P88", REQUIRED_GROUPS["P88"], 6)
    require_question_cards(failures, entries, "P113", REQUIRED_GROUPS["P113"], 5)
    require_question_cards(failures, entries, "DLT", REQUIRED_GROUPS["DLT"], 9)
    require_question_cards(failures, entries, "P128", REQUIRED_GROUPS["P128"], 4)
    require_question_cards(failures, entries, "SPEAKING", SPEAKING_QUESTIONS, 6)
    require_question_cards(failures, entries, "LISTENING", LISTENING_QUESTIONS, 11)

    require_media_boundary(failures, entries, "T2V23_P88_Q01", ("video", "izledi"), "video")
    require_media_boundary(failures, entries, "T2V23_P113_Q01", ("qr", "görül"), "video")
    require_media_boundary(failures, entries, "T2V23_P129_Q01", ("video", "izledi"), "video")
    require_media_boundary(failures, entries, "T2V23_P135_QR_LIMIT", ("görünmeyen", "üretmeyin"), "qr")
    require_media_boundary(failures, entries, "T2V23_P140_VOCAB", ("qr", "gerçek dinleme"), "qr")
    require_media_boundary(failures, entries, "T2V23_P144_MEDIA_MAP", ("qr medyada gerçekten", "uydur"), "qr")

    for page_range in ("88-112", "113-128", "129-135", "136-147"):
        require_fragment(failures, mirrors, page_range)

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
            "pdf_verified_speaking_questions": 6,
            "pdf_verified_listening_questions": 11,
            "pdf_verified_grammar_tasks": 4,
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
