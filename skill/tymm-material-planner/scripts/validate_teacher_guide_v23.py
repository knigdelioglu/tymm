#!/usr/bin/env python3
"""Theme 1 golden-reference checks on top of the reusable V2.3 validator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_teacher_guide_v23_generic import validate

GOLDEN_METRICS = {
    "mirror_files": 6,
    "scope": "12-83",
    "entries": 126,
    "questions": 78,
    "recognizable_questions": 78,
    "component_projected_entries": 83,
    "shared_canonical_items": 17,
}

REQUIRED_WRITING_IDS = {
    "T1V23_P74_Q01", "T1V23_P74_Q02", "T1V23_P74_Q03", "T1V23_P74_Q04",
    "T1V23_P74_Q05A", "T1V23_P74_Q05B", "T1V23_P75_PLAN",
    "T1V23_P76_CONTENT_01_04", "T1V23_P76_CONTENT_05_09", "T1V23_P77_CONTENT_10_13",
    "T1V23_P77_RULES", "T1V23_P78_REVISION", "T1V23_P78_SELF", "T1V23_P78_EXIT",
    "T1V23_P78_QR_LIMIT",
}

REQUIRED_LISTENING_IDS = {
    "T1V23_P66_Q01", "T1V23_P66_Q02", "T1V23_P66_Q03", "T1V23_P66_Q04", "T1V23_P66_Q05",
    "T1V23_P67_Q06", "T1V23_P67_Q07", "T1V23_P67_Q08", "T1V23_P67_Q09",
}

REQUIRED_THEME_ASSESSMENT_IDS = {
    "T1V23_P79_Q01", "T1V23_P80_Q02", "T1V23_P80_Q03", "T1V23_P81_Q04", "T1V23_P81_Q05",
    "T1V23_P81_Q06", "T1V23_P81_Q07", "T1V23_P82_Q08", "T1V23_P82_Q09", "T1V23_P82_Q10",
    "T1V23_P83_Q11", "T1V23_P83_Q12", "T1V23_P83_Q13",
}

REQUIRED_HEADINGS = {
    "Konuya Başlarken",
    "Okumayı Yönetebilme — Âli’ye Mektuplar",
    "Konuşmayı Yönetebilme",
    "Metni Anlayalım",
    "İçerik Oluşturabilme — 1-4. basamaklar",
    "İçerik Oluşturabilme — 5-9. basamaklar",
    "İçerik Oluşturabilme — 10-13. basamaklar",
    "Kural Uygulayabilme",
    "Tema Sonu Değerlendirme — Çıkış Kartı",
    "1. Tema Ölçme ve Değerlendirme Soruları",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def all_entries(primary: Path) -> list[dict]:
    docs = [read_json(primary)]
    docs += [read_json(path) for path in primary.parent.glob("book_mirror_v23_*.json") if path != primary]
    return [entry for doc in docs for entry in doc.get("entries", [])]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--mirror", default="courses/TDE_11/teacher_guide/TEMA_01/book_mirror_v23.json")
    parser.add_argument("--manifest", default="courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json")
    parser.add_argument("--schema", default="skill/tymm-material-planner/schemas/teacher_guide_book_mirror.schema.json")
    parser.add_argument("--markdown", default="courses/TDE_11/teacher_guide/TEMA_01/TEACHER_GUIDE_V23_PILOT.md")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    mirror_path = root / args.mirror

    report = validate(
        root,
        mirror_path,
        root / args.manifest,
        root / args.schema,
        root / args.markdown,
    )
    failures = report["failures"]
    metrics = report["metrics"]

    for key, expected in GOLDEN_METRICS.items():
        if metrics.get(key) != expected:
            failures.append(f"THEME1_GOLDEN_METRIC_DRIFT:{key}:{metrics.get(key)}!={expected}")

    if metrics.get("teacher_note_density") != 0.508:
        failures.append(f"THEME1_TEACHER_NOTE_DENSITY_DRIFT:{metrics.get('teacher_note_density')}!=0.508")

    seen = set(report.get("seen_mirror_ids", []))
    for label, required in (
        ("WRITING", REQUIRED_WRITING_IDS),
        ("LISTENING", REQUIRED_LISTENING_IDS),
        ("THEME_ASSESSMENT", REQUIRED_THEME_ASSESSMENT_IDS),
    ):
        missing = sorted(required - seen)
        if missing:
            failures.append(f"THEME1_{label}_GOLDEN_IDS_MISSING:" + ",".join(missing))

    headings = set(report.get("headings", []))
    missing_headings = sorted(REQUIRED_HEADINGS - headings)
    if missing_headings:
        failures.append("THEME1_GOLDEN_HEADINGS_MISSING:" + " | ".join(missing_headings))

    entries = {entry.get("mirror_id"): entry for entry in all_entries(mirror_path)}

    q5a = entries.get("T1V23_P74_Q05A")
    q5b = entries.get("T1V23_P74_Q05B")
    if not q5a or not q5b or q5a.get("presentation_type") != "QUESTION" or q5b.get("presentation_type") != "QUESTION":
        failures.append("THEME1_WRITING_Q5_SUBPARTS_NOT_RECOGNIZABLE")

    content_blocks = [
        entries.get("T1V23_P76_CONTENT_01_04"),
        entries.get("T1V23_P76_CONTENT_05_09"),
        entries.get("T1V23_P77_CONTENT_10_13"),
    ]
    if any(not entry or entry.get("presentation_type") != "PROCESS" for entry in content_blocks):
        failures.append("THEME1_WRITING_13_STEPS_LOST_NATURAL_GROUPING")
    if content_blocks[-1] and not str(content_blocks[-1].get("book_heading", "")).startswith("İçerik Oluşturabilme"):
        failures.append("THEME1_WRITING_STEPS_10_13_STAGE_DRIFT")

    qr = entries.get("T1V23_P78_QR_LIMIT")
    qr_note = str(qr.get("teacher_note", "")).casefold() if qr else ""
    if not qr or "qr" not in qr_note or "uydur" not in qr_note:
        failures.append("THEME1_WRITING_QR_SOURCE_LIMIT_LOST")

    q13 = entries.get("T1V23_P83_Q13")
    q13_note = str(q13.get("teacher_note", "")).casefold() if q13 else ""
    if not q13 or "eba" not in q13_note or "uydur" not in q13_note:
        failures.append("THEME1_Q13_EXTERNAL_MEDIA_LIMIT_LOST")

    listening_questions = [mid for mid in REQUIRED_LISTENING_IDS if mid in seen]
    if len(listening_questions) != 9:
        failures.append(f"THEME1_LISTENING_9_QUESTION_PARITY:{len(listening_questions)}/9")

    theme_questions = [mid for mid in REQUIRED_THEME_ASSESSMENT_IDS if mid in seen]
    if len(theme_questions) != 13:
        failures.append(f"THEME1_ASSESSMENT_13_QUESTION_PARITY:{len(theme_questions)}/13")

    report["status"] = "PASS" if not failures else "FAIL"
    report["theme1_golden"] = {
        "expected_scope": "12-83",
        "expected_entries": 126,
        "expected_questions": 78,
        "expected_recognizable_questions": 78,
        "locator_only_allowed": 0,
        "writing_question_cards": 6,
        "writing_content_steps": 13,
        "listening_questions": 9,
        "theme_assessment_questions": 13,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
