#!/usr/bin/env python3
"""Build the Teacher Guide V2.3 book-first pilot.

Projection order:
  textbook page/heading -> recognisable book task -> canonical answer/component -> selective teacher note.

The mirror is a thin, reviewable UX contract. It never replaces canonical
teacher-guide data and never auto-fills pedagogy from generic profiles.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


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


def render_scalar(value: Any) -> str:
    if value is True:
        return "Evet"
    if value is False:
        return "Hayır"
    if value is None:
        return ""
    return str(value)


def humanize_key(key: str) -> str:
    return key.replace("_", " ").strip().capitalize()


def render_value(value: Any, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if not nonempty(value):
        return []
    if isinstance(value, str):
        return [prefix + value]
    if isinstance(value, list):
        lines: list[str] = []
        for entry in value:
            if isinstance(entry, (dict, list)):
                lines.append(prefix + "-")
                lines.extend(render_value(entry, indent + 1))
            else:
                lines.append(prefix + f"- {render_scalar(entry)}")
        return lines
    if isinstance(value, dict):
        lines = []
        for key, entry in value.items():
            label = humanize_key(str(key))
            if isinstance(entry, (dict, list)):
                lines.append(prefix + f"- **{label}:**")
                lines.extend(render_value(entry, indent + 1))
            else:
                lines.append(prefix + f"- **{label}:** {render_scalar(entry)}")
        return lines
    return [prefix + render_scalar(value)]


def parse_page_range(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*(?:[-–—]\s*(\d+)\s*)?", value)
    if not match:
        raise ValueError(f"invalid printed page range: {value}")
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        raise ValueError(f"invalid printed page range: {value}")
    return start, end


def discover_mirror_paths(primary: Path) -> list[Path]:
    candidates = [primary]
    for path in primary.parent.glob("book_mirror_v23_*.json"):
        if path != primary:
            candidates.append(path)
    return sorted(candidates, key=lambda p: parse_page_range(read_json(p)["scope"]["printed_page_range"])[0])


def merge_mirrors(paths: list[Path]) -> dict[str, Any]:
    docs = [read_json(path) for path in paths]
    base = docs[0]
    course_id = base["course_id"]
    theme_id = base["theme_id"]
    principles: list[str] = []
    entries: list[dict[str, Any]] = []
    checklist: list[dict[str, Any]] = []
    starts: list[int] = []
    ends: list[int] = []

    for doc in docs:
        if doc["course_id"] != course_id or doc["theme_id"] != theme_id:
            raise ValueError("mirror fragment identity mismatch")
        start, end = parse_page_range(doc["scope"]["printed_page_range"])
        starts.append(start)
        ends.append(end)
        for principle in doc.get("guide_principles", []):
            if principle not in principles:
                principles.append(principle)
        entries.extend(doc["entries"])
        checklist.extend(doc["page_checklist"])

    return {
        "schema_version": "2.3.0",
        "document_type": "TYMM_TEACHER_GUIDE_BOOK_MIRROR",
        "course_id": course_id,
        "theme_id": theme_id,
        "scope": {"printed_page_range": f"{min(starts)}-{max(ends)}", "status": "PILOT"},
        "source_policy": base["source_policy"],
        "guide_principles": principles,
        "entries": entries,
        "page_checklist": checklist,
        "mirror_files": [str(path) for path in paths],
    }


def index_canonical(root: Path, manifest: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    sections: dict[str, dict[str, Any]] = {}
    items: dict[str, dict[str, Any]] = {}
    for row in manifest.get("sections", []):
        section_id = row["section_id"]
        section = read_json(root / row["content_ref"])
        sections[section_id] = section
        for unit in section.get("guide_units", []):
            for item in unit.get("items", []):
                item_id = item["item_id"]
                if item_id in items:
                    raise ValueError(f"duplicate canonical item: {item_id}")
                items[item_id] = {"section_id": section_id, "unit_id": unit.get("unit_id"), "item": item}
    return sections, items


def project_value(entry: dict[str, Any], value: Any) -> Any:
    keys = entry.get("answer_keys")
    if not keys:
        return value
    if not isinstance(value, dict):
        raise ValueError(f"answer_keys requires object answer: {entry['mirror_id']}")
    missing = [key for key in keys if key not in value]
    if missing:
        raise ValueError(f"unknown answer_keys for {entry['mirror_id']}: {missing}")
    if len(keys) == 1:
        return value[keys[0]]
    return {key: value[key] for key in keys}


def add_teacher_note(lines: list[str], note: Any) -> None:
    if not nonempty(note):
        return
    lines += ["", "**Öğretmen notu:**"]
    if isinstance(note, list):
        lines.extend(f"- {x}" for x in note if isinstance(x, str) and x.strip())
    else:
        lines.append(str(note))


def add_optional_canonical_fields(lines: list[str], entry: dict[str, Any], item: dict[str, Any]) -> None:
    if entry.get("show_acceptance") and nonempty(item.get("acceptance_criteria")):
        lines += ["", "**Kabul ölçütü:**"]
        lines.extend(render_value(item["acceptance_criteria"]))
    if entry.get("show_common_misconceptions") and nonempty(item.get("common_misconceptions")):
        lines += ["", "**Dikkat:**"]
        lines.extend(render_value(item["common_misconceptions"]))
    if entry.get("show_differentiation") and nonempty(item.get("differentiation")):
        diff = item["differentiation"]
        if isinstance(diff, dict):
            if nonempty(diff.get("support")):
                lines += ["", "**Destek:**"]
                lines.extend(render_value(diff["support"]))
            if nonempty(diff.get("enrichment")):
                lines += ["", "**Zenginleştirme:**"]
                lines.extend(render_value(diff["enrichment"]))


def render_entry(lines: list[str], entry: dict[str, Any], canonical: dict[str, dict[str, Any]]) -> None:
    presentation = entry["presentation_type"]
    prompt = entry.get("prompt_display")
    if prompt:
        lines += ["", f"### {prompt}"]
    elif presentation in {"PROCESS", "REFERENCE", "VOCABULARY", "TABLE", "COMPARISON", "ASSESSMENT"}:
        lines += ["", f"### {entry['book_heading']}"]

    refs = entry["canonical_item_refs"]
    for ref in refs:
        item = canonical[ref]["item"]
        if len(refs) > 1:
            lines += ["", f"**{item.get('label', ref)}**"]

        answer = project_value(entry, item.get("expected_answer"))
        response = project_value(entry, item.get("expected_response")) if nonempty(item.get("expected_response")) else item.get("expected_response")
        if nonempty(answer):
            heading = {
                "PROCESS": "Uygulama / beklenen süreç",
                "REFERENCE": "Hızlı başvuru",
                "VOCABULARY": "Beklenen karşılıklar",
                "TABLE": "Beklenen çözüm",
                "COMPARISON": "Karşılaştırma odağı",
                "ASSESSMENT": "Beklenen değerlendirme odağı",
            }.get(presentation, "Beklenen cevap")
            lines += ["", f"**{heading}:**"]
            lines.extend(render_value(answer))
        elif nonempty(response):
            lines += ["", "**Beklenen ürün / yanıt:**"]
            lines.extend(render_value(response))

        add_optional_canonical_fields(lines, entry, item)

    add_teacher_note(lines, entry.get("teacher_note"))


def render_markdown(mirror: dict[str, Any], canonical: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# 11. Sınıf Türk Dili ve Edebiyatı — Öğretmen Rehberi V2.3 Pilot",
        "",
        f"> Kapsam: {mirror['theme_id']} / basılı s.{mirror['scope']['printed_page_range']}.",
        "> Bu çıktı ders kitabının yerine geçmez. Önce kitabın sayfa ve etkinlik akışını görünür kılar; ardından canonical cevap ve yalnız gerekli öğretmen notunu gösterir.",
        "> `LOCATOR_ONLY` soru kartı normal kabul edilmez; soru öğretmenin tanıyacağı kısa ve doğrulanmış bir ifadeyle görünmelidir.",
        "",
        "## Hızlı kullanım ilkeleri",
    ]
    lines.extend(f"- {p}" for p in mirror.get("guide_principles", []))

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    order: list[tuple[str, str]] = []
    for entry in mirror["entries"]:
        key = (entry["printed_page_range"], entry["book_heading"])
        if key not in grouped:
            order.append(key)
        grouped[key].append(entry)

    for page_range, heading in order:
        lines += ["", f"## Sayfa {page_range} — {heading}"]
        for entry in grouped[(page_range, heading)]:
            render_entry(lines, entry, canonical)

    lines += ["", "## Sayfa indeksli ders kontrol listesi", "", "| Sayfa | Dersten çıkmadan kontrol et |", "|---|---|"]
    for row in mirror["page_checklist"]:
        lines.append(f"| {row['printed_page_range']} | {row['check']} |")

    return "\n".join(lines).rstrip() + "\n"


def build(root: Path, mirror_path: Path, manifest_path: Path, output_path: Path) -> dict[str, Any]:
    mirror_paths = discover_mirror_paths(mirror_path)
    mirror = merge_mirrors(mirror_paths)
    manifest = read_json(manifest_path)
    if mirror["course_id"] != manifest["course_id"] or mirror["theme_id"] != manifest["theme_id"]:
        raise ValueError("mirror/manifest identity mismatch")

    _, canonical = index_canonical(root, manifest)
    missing = sorted({ref for entry in mirror["entries"] for ref in entry["canonical_item_refs"] if ref not in canonical})
    if missing:
        raise ValueError("unknown canonical refs: " + ", ".join(missing))

    output_path.write_text(render_markdown(mirror, canonical), encoding="utf-8")
    question_entries = [entry for entry in mirror["entries"] if entry["presentation_type"] == "QUESTION"]
    locator_only = [entry["mirror_id"] for entry in question_entries if entry.get("prompt_mode") == "LOCATOR_ONLY"]
    return {
        "status": "PASS",
        "mirror_files": len(mirror_paths),
        "scope": mirror["scope"]["printed_page_range"],
        "entries": len(mirror["entries"]),
        "questions": len(question_entries),
        "locator_only_questions": locator_only,
        "output": str(output_path.relative_to(root)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--mirror", default="courses/TDE_11/teacher_guide/TEMA_01/book_mirror_v23.json")
    parser.add_argument("--manifest", default="courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json")
    parser.add_argument("--output", default="courses/TDE_11/teacher_guide/TEMA_01/TEACHER_GUIDE_V23_PILOT.md")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = build(root, root / args.mirror, root / args.manifest, root / args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
