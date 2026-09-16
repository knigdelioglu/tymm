#!/usr/bin/env python3
"""Source-parity gate for the Theme 3 Teacher Guide V2.3 checkpoint (s.160-209)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_teacher_guide_v23_generic import discover_mirror_paths, read_json, validate

OPENING_QUESTIONS = {
    "T3V23_P162_Q01", "T3V23_P162_Q02", "T3V23_P162_Q03", "T3V23_P162_Q04",
    "T3V23_P163_Q05", "T3V23_P163_Q06",
}
HUZUR_METNI_ANLAYALIM = {
    "T3V23_P175_Q01", "T3V23_P175_Q02",
    *{f"T3V23_P176_Q{n:02d}" for n in range(3, 14)},
    "T3V23_P177_Q14",
}
HUZUR_OTHER_QUESTIONS = {
    "T3V23_P164_Q01", "T3V23_P164_Q02", "T3V23_P164_Q03",
    "T3V23_P182_Q01_GERCEK_KURGU", "T3V23_P182_YAZAR_ESER",
    "T3V23_P183_Q02_GERCEK_KURGU", "T3V23_P183_SIRA_Q01_OZNEL_NESNEL",
    "T3V23_P184_185_SIRA_Q02_DUYARLILIK", "T3V23_P186_SIRA_Q03_DIL",
    "T3V23_P186_COZUM_Q01_YAPI", "T3V23_P187_COZUM_Q02_USLUP_YAPI",
    "T3V23_P187_COZUM_Q03A", "T3V23_P188_COZUM_Q03B",
    "T3V23_P188_COZUM_Q03C", "T3V23_P188_COZUM_Q03CC", "T3V23_P188_COZUM_Q04",
    "T3V23_P189_CATISMA", "T3V23_P190_DONEM_DILI",
    "T3V23_P190_191_GRAMMAR_Q01", "T3V23_P191_GRAMMAR_Q02", "T3V23_P191_GRAMMAR_Q03",
    "T3V23_P192_DEGER_Q01", "T3V23_P193_DEGER_Q02", "T3V23_P193_DEGER_Q03",
}
HUZUR_QUESTIONS = HUZUR_METNI_ANLAYALIM | HUZUR_OTHER_QUESTIONS

BIOGRAPHY_QUESTIONS = {
    "T3V23_P194_Q01", "T3V23_P194_Q02",
    "T3V23_P199_Q01", "T3V23_P199_Q02", "T3V23_P199_Q03",
    "T3V23_P200_FARK_EDELIM",
    "T3V23_P202_Q01_OZNEL_NESNEL", "T3V23_P202_Q02_BASKIN_ANLATIM",
    "T3V23_P203_Q01_BIYOGRAFI_ORNEK", "T3V23_P203_Q02_BIYOGRAFI_TUR",
    "T3V23_P204_Q01_HUZUR_AKIF_COMPARE", "T3V23_P204_Q02_SIBER_GERCEKLIK",
    "T3V23_P205_COZUM_Q01", "T3V23_P205_COZUM_Q02", "T3V23_P205_COZUM_Q03", "T3V23_P205_COZUM_Q04",
    "T3V23_P205_SIRA_Q01_ASIM", "T3V23_P205_SIRA_Q02_ASIM",
    *{f"T3V23_P208_Q{n:02d}" for n in range(1, 7)},
    *{f"T3V23_P209_Q{n:02d}" for n in range(1, 5)},
}
BIOGRAPHY_REQUIRED_NONQUESTIONS = {
    "T3V23_P195_OKUMA_YONETIM",
    "T3V23_P195_197_AKIF_METNI",
    "T3V23_P198_SOZ_VARLIGI",
    "T3V23_P201_CALISMA_KAGIDI",
    "T3V23_P206_207_USULI",
}

REQUIRED_ENTRIES = {
    "T3V23_P160_161_THEME_OPEN",
    *OPENING_QUESTIONS,
    *HUZUR_QUESTIONS,
    "T3V23_P165_OKUMA_PLANI",
    "T3V23_P165_166_KELIME_TAHMIN_STRATEJI",
    "T3V23_P167_171_HUZUR_METNI",
    "T3V23_P172_SOZ_VARLIGI",
    "T3V23_P174_USLUP_HARITASI",
    "T3V23_P177_178_HUZUR_MESCID_COMPARE",
    "T3V23_P178_179_OKUMA_CEMBERI",
    "T3V23_P180_181_KISI_TABLOLARI",
    "T3V23_P191_SOSYAL_BILIM",
    "T3V23_P193_CIKIS_321",
    *BIOGRAPHY_QUESTIONS,
    *BIOGRAPHY_REQUIRED_NONQUESTIONS,
}
REQUIRED_HEADINGS = {
    "3. Tema — Yaşamın İzinde / tema çerçevesi",
    "Temaya Başlarken — edebiyat ve yaşam",
    "Konuya Başlarken — yazar, hayat ve roman",
    "Okumayı Yönetebilme — Huzur için tahmin, araştırma ve çalışma kâğıdı",
    "Metni Okuyalım — Huzur",
    "Anlam Oluşturabilme — Söz Varlığımız",
    "Metni Anlayalım — Huzur",
    "Karşılaştıralım — Huzur / Mescid-i Aksa",
    "Karşılaştıralım — Okuma Çemberi 1-2. adımlar",
    "Fark Edelim — gerçek hayat / kurmaca balık kılçığı",
    "Sıra Sizde — öznel ve nesnel anlatım",
    "Çözümleyebilme — Huzur'un yapı unsurları",
    "Çözümleyebilme — yazarın üslup seçimi",
    "Sıra Sizde — cümle ögeleri",
    "Süreci Değerlendirebilme — Huzur çözümleme çalışma kâğıdı",
    "Çıkış Kartı — Üç Yaz / İki Sor / Bir Paylaş",
    "Konuya Başlarken — biyografide yaşam ayrıntıları",
    "Okumayı Yönetebilme — Mehmet Akif Ersoy",
    "Metni Okuyalım — Mehmet Akif Ersoy",
    "Çalışma Kâğıdı — Mehmet Akif Ersoy biyografisi",
    "Fark Edelim — biyografi örnekleri",
    "Karşılaştıralım — Huzur / Mehmet Akif Ersoy",
    "Çözümleyebilme — biyografinin yapı unsurları",
    "Bilgi Köşesi / Ara Metin — Tezkire ve Usûlî",
    "Sıra Sizde — Usûlî tezkiresi",
    "Süreci Değerlendirebilme — beğeni ölçütü belirleme",
}

EXPECTED = {
    "scope": "160-209",
    "entries": 88,
    "questions": 72,
    "recognizable_questions": 72,
    "component_projected_entries": 72,
    "shared_canonical_items": 16,
    "component_registry_entries": 25,
    "component_registry_used": 25,
}


def require_question_cards(failures: list[str], entries: list[dict], label: str, required: set[str]) -> None:
    rows = [entry for entry in entries if entry.get("mirror_id") in required]
    if len(rows) != len(required) or any(entry.get("presentation_type") != "QUESTION" for entry in rows):
        failures.append(f"TEMA03_{label}_QUESTION_CARD_PARITY:{len(rows)}/{len(required)}")


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

    for key, value in EXPECTED.items():
        if metrics.get(key) != value:
            failures.append(f"TEMA03_METRIC_PARITY:{key}:{metrics.get(key)}!={value}")

    missing_entries = sorted(REQUIRED_ENTRIES - seen)
    if missing_entries:
        failures.append("TEMA03_REQUIRED_ENTRIES_MISSING:" + ",".join(missing_entries))
    missing_headings = sorted(REQUIRED_HEADINGS - headings)
    if missing_headings:
        failures.append("TEMA03_BOOK_HEADINGS_MISSING:" + " | ".join(missing_headings))

    mirrors = [read_json(path) for path in discover_mirror_paths(mirror_path)]
    entries = [entry for mirror in mirrors for entry in mirror.get("entries", [])]
    require_question_cards(failures, entries, "OPENING", OPENING_QUESTIONS)
    require_question_cards(failures, entries, "HUZUR", HUZUR_QUESTIONS)
    require_question_cards(failures, entries, "HUZUR_METNI_ANLAYALIM", HUZUR_METNI_ANLAYALIM)
    require_question_cards(failures, entries, "BIOGRAPHY_TEZKIRE", BIOGRAPHY_QUESTIONS)

    metni = [entry for entry in entries if entry.get("mirror_id") in HUZUR_METNI_ANLAYALIM]
    metni_keys = {tuple(entry.get("answer_keys", [])) for entry in metni}
    if len(metni) != 14 or metni_keys != {(str(n),) for n in range(1, 15)}:
        failures.append("TEMA03_HUZUR_MUST_KEEP_14_DISTINCT_METNI_ANLAYALIM_QUESTIONS")

    grammar = {"T3V23_P190_191_GRAMMAR_Q01", "T3V23_P191_GRAMMAR_Q02", "T3V23_P191_GRAMMAR_Q03"}
    require_question_cards(failures, entries, "HUZUR_GRAMMAR", grammar)

    p199 = {"T3V23_P199_Q01", "T3V23_P199_Q02", "T3V23_P199_Q03"}
    p205 = {
        "T3V23_P205_COZUM_Q01", "T3V23_P205_COZUM_Q02", "T3V23_P205_COZUM_Q03", "T3V23_P205_COZUM_Q04",
        "T3V23_P205_SIRA_Q01_ASIM", "T3V23_P205_SIRA_Q02_ASIM",
    }
    p208 = {f"T3V23_P208_Q{n:02d}" for n in range(1, 7)}
    p209 = {f"T3V23_P209_Q{n:02d}" for n in range(1, 5)}
    require_question_cards(failures, entries, "P199", p199)
    require_question_cards(failures, entries, "P205", p205)
    require_question_cards(failures, entries, "P208", p208)
    require_question_cards(failures, entries, "P209", p209)

    expected_fragments = {
        "160-163": "PILOT",
        "164-193": "REFERENCE_QUALITY",
        "194-209": "REFERENCE_QUALITY",
    }
    for page_range, status in expected_fragments.items():
        rows = [mirror for mirror in mirrors if mirror.get("scope", {}).get("printed_page_range") == page_range]
        if len(rows) != 1 or rows[0].get("scope", {}).get("status") != status:
            failures.append(f"TEMA03_FRAGMENT_STATUS:{page_range}:{status}")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "metrics": {
            **metrics,
            "pdf_verified_opening_questions": 6,
            "pdf_verified_huzur_questions": len(HUZUR_QUESTIONS),
            "pdf_verified_huzur_metni_anlayalim_questions": 14,
            "pdf_verified_biography_tezkire_questions": len(BIOGRAPHY_QUESTIONS),
            "biography_tezkire_reference_scope": True,
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
