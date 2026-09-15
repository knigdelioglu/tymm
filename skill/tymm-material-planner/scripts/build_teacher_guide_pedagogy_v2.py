#!/usr/bin/env python3
"""Build pedagogy-first Teacher Guide V2 overlays and Markdown from canonical guides.

Canonical section JSON remains the source of book/page/item truth. This builder
adds the teacher-facing layer from curated phase + section profiles. Item refs
are discovered from the canonical sections, so a newly-added item cannot be
silently omitted from a generated V2 guide.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_THEMES = ("TEMA_02", "TEMA_03", "TEMA_04")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def unique(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        value = value.strip()
        if value and value not in out:
            out.append(value)
    return out


def classify_phase(section_type: str, unit_title: str) -> str:
    if section_type == "THEME_OPENING":
        return "opening"
    if section_type == "THEME_ASSESSMENT":
        return "assessment"
    title = unit_title.casefold()
    if "yönet" in title or "hazırl" in title:
        return "manage"
    if "değerl" in title or "yansıt" in title or "öz değerlend" in title:
        return "reflect"
    if "çözüm" in title or "kural" in title or "uygula" in title or "gerçekleştir" in title:
        return "analyze_apply"
    if "anlam" in title or "içerik" in title:
        return "meaning"
    if section_type in {"SPEAKING", "WRITING"}:
        return "analyze_apply"
    return "meaning"


def slug(value: str) -> str:
    value = value.upper()
    value = value.replace("İ", "I").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O").replace("Ç", "C")
    return re.sub(r"[^A-Z0-9]+", "_", value).strip("_")


def render_markdown(overlay: dict[str, Any], sections_by_id: dict[str, dict[str, Any]]) -> str:
    lines = [
        f"# {overlay['theme_id']} — Teacher Guide V2",
        "",
        "> Bu dosya canonical ders kitabı/teacher-guide itemlerini değiştirmez. Pedagojik uygulama katmanıdır.",
        "> Kitaptaki soru metni canonical kaynakta birebir doğrulanmamışsa burada soru uydurulmaz; görev etiketi ve sayfa konumu kullanılır.",
        "",
        "## Kullanım ilkeleri",
    ]
    for principle in overlay["principles"]:
        lines.append(f"- {principle}")
    for block in overlay["blocks"]:
        section = sections_by_id[block["section_id"]]
        lines += [
            "",
            f"## s.{block['printed_page_range']} — {block['title']}",
            "",
            f"**Bölüm:** {section['title']}",
            "",
            "### Kitaptaki görevler",
        ]
        lines += [f"- {x}" for x in block["book_task_summaries"]]
        lines += ["", "### Pedagojik amaç", "", block["pedagogical_intent"], "", "### Öğretmen hamlesi"]
        lines += [f"- {x}" for x in block["teacher_moves"]]
        lines += ["", "### Takip soruları"]
        lines += [f"- {x}" for x in block["follow_up_questions"]]
        lines += ["", "### Yanlış/kısmi cevapta müdahale"]
        lines += [f"- {x}" for x in block["misconception_interventions"]]
        if block["board_notes"]:
            lines += ["", "### Tahta notu"]
            lines += [f"- **{x}**" for x in block["board_notes"]]
        lines += ["", "### Ölçmede bak"]
        lines += [f"- {x}" for x in block["assessment_look_fors"]]
        lines += ["", "### Farklılaştırma", "", "**Destek**"]
        lines += [f"- {x}" for x in block["differentiation"]["support"]]
        lines += ["", "**Zenginleştirme**"]
        lines += [f"- {x}" for x in block["differentiation"]["enrichment"]]
        if block.get("source_limitations"):
            lines += ["", "### Kaynak sınırı"]
            lines += [f"- {x}" for x in block["source_limitations"]]
    return "\n".join(lines).rstrip() + "\n"


def build_theme(root: Path, theme_id: str, profiles: dict[str, Any]) -> tuple[Path, Path, dict[str, Any]]:
    guide_root = root / "courses" / "TDE_11" / "teacher_guide" / theme_id
    manifest_path = guide_root / "teacher_guide.json"
    manifest = read_json(manifest_path)
    if manifest.get("theme_id") != theme_id:
        raise ValueError(f"theme mismatch: {manifest_path}")

    theme_profiles = profiles["section_profiles"].get(theme_id)
    if not isinstance(theme_profiles, dict):
        raise ValueError(f"missing curated profiles for {theme_id}")

    sections_by_id: dict[str, dict[str, Any]] = {}
    blocks: list[dict[str, Any]] = []
    unit_count = 0
    item_count = 0

    for section_index in manifest["sections"]:
        section_id = section_index["section_id"]
        section = read_json(root / section_index["content_ref"])
        sections_by_id[section_id] = section
        section_profile = theme_profiles.get(section_id)
        if not isinstance(section_profile, dict):
            raise ValueError(f"missing section profile: {theme_id}:{section_id}")

        for unit in section.get("guide_units", []):
            items = unit.get("items", [])
            refs = [item["item_id"] for item in items if isinstance(item.get("item_id"), str)]
            if not refs:
                continue
            unit_count += 1
            item_count += len(refs)
            phase_name = classify_phase(section["section_type"], unit["title"])
            phase = profiles["phase_profiles"][phase_name]
            purpose = unit.get("purpose")
            if isinstance(purpose, str) and purpose.strip():
                pedagogical_intent = f"{section_profile['focus']} {purpose.strip()}"
            else:
                pedagogical_intent = section_profile["focus"]

            book_tasks = []
            for item in items:
                label = item.get("label") or item.get("title") or item.get("item_id")
                item_type = item.get("item_type", "TASK")
                book_tasks.append(f"{label} [{item_type}]")

            block = {
                "block_id": f"{theme_id.replace('TEMA_', 'T')}V2_{slug(unit['unit_id'])}",
                "section_id": section_id,
                "printed_page_range": unit.get("printed_page_range") or section["printed_page_range"],
                "title": unit["title"],
                "source_item_refs": refs,
                "book_task_summaries": book_tasks,
                "pedagogical_intent": pedagogical_intent,
                "teacher_moves": unique(phase["teacher_moves"] + section_profile["teacher_moves"]),
                "follow_up_questions": unique(phase["follow_up_questions"] + section_profile["follow_up_questions"]),
                "misconception_interventions": unique(phase["misconception_interventions"] + section_profile["misconception_interventions"]),
                "board_notes": unique(phase["board_notes"] + section_profile["board_notes"]),
                "assessment_look_fors": unique(phase["assessment_look_fors"] + section_profile["assessment_look_fors"]),
                "differentiation": {
                    "support": unique(phase["support"] + section_profile["support"]),
                    "enrichment": unique(phase["enrichment"] + section_profile["enrichment"]),
                },
            }
            limitations = unique(section_profile.get("source_limitations", []))
            if limitations:
                block["source_limitations"] = limitations
            blocks.append(block)

    overlay = {
        "schema_version": "2.0.0",
        "document_type": "TYMM_TEACHER_GUIDE_PEDAGOGY_OVERLAY",
        "course_id": "TDE_11",
        "theme_id": theme_id,
        "status": "REFERENCE_QUALITY",
        "principles": profiles["principles"],
        "blocks": blocks,
    }
    overlay_path = guide_root / "pedagogy_v2.json"
    markdown_path = guide_root / "TEACHER_GUIDE_V2.md"
    overlay_path.write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(overlay, sections_by_id), encoding="utf-8")
    return overlay_path, markdown_path, {"theme": theme_id, "units": unit_count, "items": item_count, "blocks": len(blocks)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--profiles", default="skill/tymm-material-planner/data/teacher_guide_v2_profiles.json")
    parser.add_argument("--theme", action="append", dest="themes", help="Repeatable, e.g. --theme TEMA_02")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    profiles = read_json(root / args.profiles)
    themes = tuple(args.themes or DEFAULT_THEMES)
    reports = []
    for theme_id in themes:
        _, _, report = build_theme(root, theme_id, profiles)
        reports.append(report)
    print(json.dumps({"status": "PASS", "generated": reports}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
