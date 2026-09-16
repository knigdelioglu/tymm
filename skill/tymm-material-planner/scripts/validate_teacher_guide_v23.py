#!/usr/bin/env python3
"""Quality gate for the Teacher Guide V2.3 book-first pilot."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

GOLDEN_HEADINGS_36_52 = {
    "Konuya Başlarken",
    "Okumayı Yönetebilme — Âli’ye Mektuplar",
    "Söz Varlığımız",
    "Metni Anlayalım",
    "Fark Edelim",
    "Sıra Sizde — Öznel ve nesnel ifadeler",
    "Mektup türleri",
    "Fark Edelim / Karşılaştıralım",
    "Çözümleyebilme — Mektubun yapı unsurları",
    "Mektup ve sosyal bilimler",
    "Süreci Değerlendirebilme",
    "Metin ve Gerçeklik",
    "İletişim, zaman ve teknoloji",
    "Farklı dönemlerden iletişim örnekleri",
    "Ara metin: Dilekçe",
    "Dilekçe yazma / ileri okuma",
}

EXACT_STAGE_HEADINGS_53_58 = {
    "Konuşmayı Yönetebilme",
    "İçerik Oluşturabilme",
    "Kural Uygulayabilme",
    "Süreci Değerlendirebilme",
}

EXACT_HEADINGS_59_73 = {
    "Konuya Başlarken — Hatırlayalım",
    "Dinleme / İzlemeyi Yönetebilme — Sıra Sizde",
    "Düşünelim Paylaşalım",
    "Ders Dışı Etkinlik — İletişim ve E-posta",
    "Metni Dinleyelim / İzleyelim",
    "Gözlem Formu",
    "Anlam Oluşturabilme — Söz Varlığımız",
    "Metni Anlayalım",
    "Birlikte Çalışalım",
    "Sıra Sizde — Paydos / iletişim aksaklıkları",
    "Sıra Sizde — iletişim engelleri kavram haritası",
    "Sıra Sizde — iletişim engellerine çözüm",
    "Sıra Sizde — çözüm yollarını karşılaştırma",
    "Sıra Sizde — iletişim kanalları",
    "Çözümleyebilme",
    "Süreci Değerlendirebilme",
    "Çıkış Kartı",
}

REQUIRED_LISTENING_IDS = {
    "T1V23_P66_Q01", "T1V23_P66_Q02", "T1V23_P66_Q03", "T1V23_P66_Q04", "T1V23_P66_Q05",
    "T1V23_P67_Q06", "T1V23_P67_Q07", "T1V23_P67_Q08", "T1V23_P67_Q09",
    "T1V23_P72_Q01", "T1V23_P72_Q02", "T1V23_P73_Q01", "T1V23_P73_Q02", "T1V23_P73_EXIT",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--mirror", default="courses/TDE_11/teacher_guide/TEMA_01/book_mirror_v23.json")
    parser.add_argument("--manifest", default="courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json")
    parser.add_argument("--schema", default="skill/tymm-material-planner/schemas/teacher_guide_book_mirror.schema.json")
    parser.add_argument("--markdown", default="courses/TDE_11/teacher_guide/TEMA_01/TEACHER_GUIDE_V23_PILOT.md")
    args = parser.parse_args()
    root = args.repo_root.resolve()

    schema = read_json(root / args.schema)
    manifest = read_json(root / args.manifest)
    markdown = (root / args.markdown).read_text(encoding="utf-8")
    mirror_paths = discover_mirror_paths(root / args.mirror)
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
                canonical[item["item_id"]] = {"section_id": section["section_id"], "item": item}

    seen_mirror_ids: set[str] = set()
    projections: dict[str, list[tuple[str, set[str] | None]]] = defaultdict(list)
    questions = 0
    recognizable = 0
    component_projected_entries = 0
    teacher_notes: list[str] = []

    for entry in entries:
        mid = entry.get("mirror_id")
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
            projections[ref].append((str(mid), keys))
            if ref not in canonical:
                failures.append(f"UNKNOWN_CANONICAL_REF:{mid}:{ref}")
                continue
            if canonical[ref]["section_id"] != entry.get("section_id"):
                failures.append(f"SECTION_DRIFT:{mid}:{ref}")
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
    headings = {str(entry.get("book_heading")) for entry in entries}

    if max_scope_end >= 52:
        missing_headings = sorted(GOLDEN_HEADINGS_36_52 - headings)
        if missing_headings:
            failures.append("GOLDEN_BOOK_HEADINGS_MISSING:" + " | ".join(missing_headings))

    expected_scope_text = f"basılı s.{min_scope_start}-{max_scope_end}"
    if expected_scope_text not in markdown:
        failures.append(f"COMBINED_SCOPE_NOT_RENDERED:{expected_scope_text}")

    if max_scope_end >= 58:
        missing_stages = sorted(EXACT_STAGE_HEADINGS_53_58 - headings)
        if missing_stages:
            failures.append("EXACT_SPEAKING_STAGE_HEADINGS_MISSING:" + " | ".join(missing_stages))

        speaking_fragments = [
            mirror for mirror in mirrors
            if parse_page_range(mirror["scope"]["printed_page_range"]) == (53, 58)
        ]
        if len(speaking_fragments) != 1 or speaking_fragments[0].get("scope", {}).get("status") != "REVIEW_REQUIRED":
            failures.append("SPEAKING_QR_LIMIT_MUST_REMAIN_REVIEW_REQUIRED")

        qr_entries = [entry for entry in entries if entry.get("mirror_id") == "T1V23_P58_QR_LIMIT"]
        if len(qr_entries) != 1:
            failures.append("MISSING_P58_QR_SOURCE_LIMIT_ENTRY")
        else:
            qr_note = note_text(qr_entries[0]).casefold()
            if "qr" not in qr_note or "uydur" not in qr_note:
                failures.append("P58_QR_LIMIT_NOT_EXPLICIT")

        live_entries = [entry for entry in entries if entry.get("mirror_id") == "T1V23_P57_APPLY"]
        if len(live_entries) != 1 or not live_entries[0].get("show_acceptance"):
            failures.append("P57_LIVE_PERFORMANCE_EVIDENCE_NOT_VISIBLE")

    if max_scope_end >= 73:
        missing_listening_headings = sorted(EXACT_HEADINGS_59_73 - headings)
        if missing_listening_headings:
            failures.append("EXACT_LISTENING_HEADINGS_MISSING:" + " | ".join(missing_listening_headings))

        missing_listening_ids = sorted(REQUIRED_LISTENING_IDS - seen_mirror_ids)
        if missing_listening_ids:
            failures.append("LISTENING_FIRST_CLASS_TASKS_MISSING:" + ",".join(missing_listening_ids))

        metni_anlayalim = [
            entry for entry in entries
            if entry.get("mirror_id", "").startswith("T1V23_P66_Q") or entry.get("mirror_id", "").startswith("T1V23_P67_Q")
        ]
        if len(metni_anlayalim) != 9:
            failures.append(f"LISTENING_METNI_ANLAYALIM_MUST_HAVE_9_QUESTIONS:{len(metni_anlayalim)}")
        if any(entry.get("presentation_type") != "QUESTION" for entry in metni_anlayalim):
            failures.append("LISTENING_METNI_ANLAYALIM_NOT_ALL_QUESTION_CARDS")

        source_sensitive_ids = {"T1V23_P67_Q08", "T1V23_P72_Q01", "T1V23_P73_Q01"}
        for mid in source_sensitive_ids:
            matched = [entry for entry in entries if entry.get("mirror_id") == mid]
            if len(matched) != 1:
                failures.append(f"SOURCE_SENSITIVE_LISTENING_ENTRY_MISSING:{mid}")
                continue
            note = note_text(matched[0]).casefold()
            if not any(token in note for token in ("medya", "qr", "kanıt")):
                failures.append(f"SOURCE_SENSITIVE_LISTENING_NOTE_WEAK:{mid}")

        canonical_listening = canonical.get("T1_G16_P65_71_COMPREHENSION", {}).get("item", {})
        provenance = canonical_listening.get("provenance", {}) if isinstance(canonical_listening, dict) else {}
        provenance_note = str(provenance.get("note", "")).casefold() if isinstance(provenance, dict) else ""
        if "yeniden doğrulan" not in provenance_note or "medya" not in provenance_note:
            failures.append("LISTENING_CANONICAL_PDF_REFRESH_NOT_RECORDED")

    result = {
        "status": "PASS" if not failures else "FAIL",
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
            "pdf_verified_listening_questions": 9 if max_scope_end >= 73 else 0,
        },
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
