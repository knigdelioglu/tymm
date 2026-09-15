#!/usr/bin/env python3
"""Build pedagogy-first Teacher Guide V2 overlays and Markdown from canonical guides.

V2.2 keeps canonical task-card fidelity while making the section-level pedagogy
context-sensitive: curated section guidance is placed once at the most relevant
unit, speaking/writing phases are classified before generic meaning phases,
boilerplate fallbacks are contextualized to the actual task, and board notes are
only emitted when a curated note is genuinely relevant.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

DEFAULT_THEMES = ("TEMA_02", "TEMA_03", "TEMA_04")
QUESTION_RANGE_RE = re.compile(r"(?:^|_)Q(\d+)_(\d+)(?:_|$)")
LABEL_RANGE_RE = re.compile(r"(\d+)\s*[-–—]\s*(\d+)\.?\s*soru", re.IGNORECASE)
PROFILE_FIELDS = (
    "teacher_moves",
    "follow_up_questions",
    "misconception_interventions",
    "board_notes",
    "assessment_look_fors",
    "support",
    "enrichment",
    "source_limitations",
)
FIELD_CAPS = {
    "teacher_moves": 4,
    "follow_up_questions": 4,
    "misconception_interventions": 3,
    "board_notes": 2,
    "assessment_look_fors": 4,
    "support": 2,
    "enrichment": 2,
    "source_limitations": 99,
}
STOPWORDS = {
    "ve", "veya", "ile", "icin", "bir", "bu", "su", "da", "de", "mi", "mu",
    "metin", "gorev", "ogrenci", "ogrencinin", "olarak", "uzerinden", "gibi",
    "daha", "yalniz", "sonra", "once", "kendi", "ayni", "ise",
}
TR_MAP = str.maketrans({"ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u"})


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def unique(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        value = value.strip()
        if value and value not in out:
            out.append(value)
    return out


def is_nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def classify_phase(section_type: str, unit_title: str) -> str:
    if section_type == "THEME_OPENING":
        return "opening"
    if section_type == "THEME_ASSESSMENT":
        return "assessment"

    title = unit_title.casefold()
    if any(key in title for key in ("yönet", "hazır", "planla")):
        return "manage"
    if any(key in title for key in ("değerl", "yansıt", "öz değerlend", "kontrol")):
        return "reflect"

    # Production skills must not fall into the reading/listening "meaning" profile
    # merely because their unit title contains "içerik".
    if section_type in {"SPEAKING", "WRITING"}:
        return "analyze_apply"

    if any(key in title for key in ("çözüm", "kural", "uygula", "gerçekleştir")):
        return "analyze_apply"
    if any(key in title for key in ("anlam", "içerik")):
        return "meaning"
    return "meaning"


def slug(value: str) -> str:
    value = value.upper()
    value = value.replace("İ", "I").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O").replace("Ç", "C")
    return re.sub(r"[^A-Z0-9]+", "_", value).strip("_")


def normalize_tokens(value: str) -> set[str]:
    text = value.casefold().translate(TR_MAP)
    tokens = set(re.findall(r"[a-z0-9]+", text))
    return {token for token in tokens if len(token) >= 3 and token not in STOPWORDS}


def question_range(item: dict[str, Any]) -> tuple[int, int] | None:
    match = QUESTION_RANGE_RE.search(str(item.get("item_id", "")))
    if not match:
        match = LABEL_RANGE_RE.search(str(item.get("label", "")))
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    return (start, end) if end >= start else None


def split_expected_answers(item: dict[str, Any]) -> list[tuple[str, Any, str | None]] | None:
    if item.get("item_type") != "QUESTION":
        return None

    answer = item.get("expected_answer")
    if not is_nonempty(answer):
        answer = item.get("expected_response")
    if not is_nonempty(answer):
        return None

    if isinstance(answer, dict) and len(answer) > 1:
        keys = list(answer)
        if all(re.fullmatch(r"\d+", str(key)) for key in keys):
            ordered = sorted(((int(str(key)), str(key), answer[key]) for key in keys), key=lambda row: row[0])
            return [(key, value, None) for _, key, value in ordered]

    qr = question_range(item)
    if qr is None:
        return None
    start, end = qr
    count = end - start + 1
    numbers = [str(number) for number in range(start, end + 1)]

    if isinstance(answer, dict) and len(answer) == count:
        return [(number, value, str(key)) for number, (key, value) in zip(numbers, answer.items())]
    if isinstance(answer, list) and len(answer) == count:
        return [(number, value, None) for number, value in zip(numbers, answer)]
    return None


def make_task_cards(item: dict[str, Any]) -> list[dict[str, Any]]:
    item_id = item["item_id"]
    label = item.get("label") or item.get("title") or item_id
    item_type = item.get("item_type", "TASK")
    page_range = item.get("printed_page_range")
    provenance = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
    source_locators = provenance.get("source_locators", []) if isinstance(provenance, dict) else []

    common = {
        "source_item_ref": item_id,
        "printed_page_range": page_range,
        "item_type": item_type,
        "acceptance_criteria": item.get("acceptance_criteria"),
        "canonical_teacher_guidance": item.get("teacher_guidance"),
        "canonical_common_misconceptions": item.get("common_misconceptions"),
        "canonical_assessment_evidence": item.get("assessment_evidence"),
        "canonical_differentiation": item.get("differentiation"),
        "source_locators": source_locators,
    }

    split = split_expected_answers(item)
    if split:
        cards: list[dict[str, Any]] = []
        for number, answer, component_key in split:
            card = {
                **common,
                "task_id": f"{item_id}#Q{number}",
                "label": f"{label} — Soru {number}",
                "question_number": number,
                "prompt_mode": "LOCATOR_ONLY",
                "book_prompt": f"Ders kitabı s.{page_range} — {number}. soru",
                "expected_answer": answer,
                "expected_response": None,
                "split_from_group": True,
            }
            if component_key:
                card["answer_component_key"] = component_key
            cards.append(card)
        return cards

    return [{
        **common,
        "task_id": item_id,
        "label": str(label),
        "question_number": None,
        "prompt_mode": "CANONICAL_LABEL",
        "book_prompt": str(label),
        "expected_answer": item.get("expected_answer"),
        "expected_response": item.get("expected_response"),
        "split_from_group": False,
    }]


def unit_descriptor(unit: dict[str, Any]) -> str:
    parts = [str(unit.get("title", "")), str(unit.get("purpose", ""))]
    for item in unit.get("items", []):
        parts.append(str(item.get("label", "")))
        parts.append(str(item.get("item_type", "")))
    return " ".join(parts)


def phase_hint(text: str) -> str | None:
    norm = text.casefold()
    if any(key in norm for key in ("tahmin", "strateji", "hazır", "amaç", "ön bilgi", "planla")):
        return "manage"
    if any(key in norm for key in ("öz değerlend", "geri bildirim", "revizyon", "yansıt", "değerlendir")):
        return "reflect"
    if any(key in norm for key in ("çözüm", "yapı", "üslup", "işlev", "uygula", "ürün", "taslak", "performans")):
        return "analyze_apply"
    if any(key in norm for key in ("konu", "tema", "ileti", "anlam", "yorum", "çıkarım", "soru")):
        return "meaning"
    return None


def assign_section_guidance(
    units: list[dict[str, Any]],
    section_type: str,
    section_profile: dict[str, Any],
) -> dict[str, dict[str, list[str]]]:
    assignments = {
        unit["unit_id"]: {field: [] for field in PROFILE_FIELDS}
        for unit in units
    }
    phases = {unit["unit_id"]: classify_phase(section_type, unit["title"]) for unit in units}
    descriptors = {unit["unit_id"]: normalize_tokens(unit_descriptor(unit)) for unit in units}

    for field in PROFILE_FIELDS:
        entries = section_profile.get(field, [])
        if not isinstance(entries, list):
            continue
        if field == "board_notes":
            # At most two curated board notes per unit across the section.
            entries = entries[: 2 * len(units)]
        cap = FIELD_CAPS[field]
        for entry in entries:
            if not isinstance(entry, str) or not entry.strip():
                continue
            entry_tokens = normalize_tokens(entry)
            hint = phase_hint(entry)
            candidates: list[tuple[int, int, str]] = []
            for index, unit in enumerate(units):
                unit_id = unit["unit_id"]
                if len(assignments[unit_id][field]) >= cap:
                    continue
                overlap = len(entry_tokens & descriptors[unit_id])
                score = overlap * 10
                if hint and phases[unit_id] == hint:
                    score += 7
                if not hint:
                    preferred = "analyze_apply" if section_type in {"SPEAKING", "WRITING"} else "meaning"
                    if phases[unit_id] == preferred:
                        score += 2
                # Stable tie-break: earlier units win, but only after semantic score.
                candidates.append((score, -index, unit_id))
            if not candidates:
                raise ValueError(f"no guidance capacity for {field}: {entry}")
            _, _, chosen = max(candidates)
            assignments[chosen][field].append(entry)
    return assignments


def lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text


def task_anchor(unit: dict[str, Any]) -> str:
    for item in unit.get("items", []):
        label = item.get("label") or item.get("title")
        if isinstance(label, str) and label.strip():
            return label.strip()
    return unit["title"]


def contextual_fallback(
    field: str,
    phase_name: str,
    phase_profile: dict[str, Any],
    unit: dict[str, Any],
    ordinal: int,
) -> str:
    values = phase_profile.get(field, [])
    if not isinstance(values, list) or not values:
        raise ValueError(f"missing phase fallback: {phase_name}:{field}")
    base = str(values[ordinal % len(values)])
    anchor = task_anchor(unit)

    if field == "teacher_moves":
        return f"“{anchor}” görevinde {lower_first(base)}"
    if field == "follow_up_questions":
        return f"“{anchor}” için: {base}"
    if field == "misconception_interventions":
        return f"“{anchor}” sırasında {lower_first(base)}"
    if field == "assessment_look_fors":
        return f"“{anchor}” için ölçmede: {lower_first(base)}"
    if field == "support":
        return f"“{anchor}” için destek: {lower_first(base)}"
    if field == "enrichment":
        return f"“{anchor}” için zenginleştirme: {lower_first(base)}"
    return base


def select_guidance(
    field: str,
    assigned: list[str],
    phase_name: str,
    phase_profile: dict[str, Any],
    unit: dict[str, Any],
    ordinal: int,
) -> list[str]:
    # Board notes are intentionally not auto-filled. "Tahtaya yaz" must be a
    # curated decision, not a schema-compliance placeholder.
    if field == "board_notes":
        return unique(assigned)[:2]
    if assigned:
        limit = {
            "teacher_moves": 4,
            "follow_up_questions": 4,
            "misconception_interventions": 3,
            "assessment_look_fors": 4,
            "support": 2,
            "enrichment": 2,
        }.get(field, 4)
        return unique(assigned)[:limit]
    return [contextual_fallback(field, phase_name, phase_profile, unit, ordinal)]


def render_scalar(value: Any) -> str:
    if value is True:
        return "Evet"
    if value is False:
        return "Hayır"
    if value is None:
        return ""
    return str(value)


def render_value_lines(value: Any, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if not is_nonempty(value):
        return []
    if isinstance(value, str):
        return [prefix + value]
    if isinstance(value, list):
        lines: list[str] = []
        for entry in value:
            if isinstance(entry, (dict, list)):
                nested = render_value_lines(entry, indent + 1)
                if nested:
                    lines.append(prefix + "-")
                    lines.extend(nested)
            else:
                lines.append(prefix + f"- {render_scalar(entry)}")
        return lines
    if isinstance(value, dict):
        lines = []
        for key, entry in value.items():
            if isinstance(entry, (dict, list)):
                lines.append(prefix + f"- **{key}:**")
                lines.extend(render_value_lines(entry, indent + 1))
            else:
                lines.append(prefix + f"- **{key}:** {render_scalar(entry)}")
        return lines
    return [prefix + render_scalar(value)]


def append_field(lines: list[str], heading: str, value: Any) -> None:
    rendered = render_value_lines(value)
    if rendered:
        lines += ["", f"**{heading}:**"]
        lines.extend(rendered)


def render_task_card(lines: list[str], card: dict[str, Any]) -> None:
    page = card.get("printed_page_range")
    question_no = card.get("question_number")
    title = f"Soru {question_no}" if question_no else card["label"]
    lines += [
        "",
        f"#### {title}",
        f"<!-- task:{card['task_id']} -->",
        f"**Kitaptaki görev:** {card['book_prompt']}",
    ]
    if card["prompt_mode"] == "LOCATOR_ONLY":
        lines.append(
            "_Not: Birebir soru metni canonical teacher-guide verisinde tutulmadığı için "
            "uydurulmamıştır; soru ders kitabındaki bu konumdan okunur._"
        )
    if page:
        lines.append(f"**Sayfa:** {page}")
    lines.append(f"**Tür:** {card['item_type']}")

    answer = card.get("expected_answer")
    response = card.get("expected_response")
    if is_nonempty(answer):
        lines += ["", f"<!-- answer:{card['task_id']} -->", "**Beklenen cevap / cevap odağı:**"]
        lines.extend(render_value_lines(answer))
    elif is_nonempty(response):
        lines += ["", f"<!-- answer:{card['task_id']} -->", "**Beklenen ürün / yanıt:**"]
        lines.extend(render_value_lines(response))

    append_field(lines, "Kabul ölçütleri", card.get("acceptance_criteria"))
    append_field(lines, "Canonical öğretmen notu", card.get("canonical_teacher_guidance"))
    append_field(lines, "Yaygın hata / kavram yanılgısı", card.get("canonical_common_misconceptions"))
    append_field(lines, "Ölçme kanıtı", card.get("canonical_assessment_evidence"))

    differentiation = card.get("canonical_differentiation")
    if isinstance(differentiation, dict):
        append_field(lines, "Destek", differentiation.get("support"))
        append_field(lines, "Zenginleştirme", differentiation.get("enrichment"))


def render_markdown(overlay: dict[str, Any], sections_by_id: dict[str, dict[str, Any]]) -> str:
    lines = [
        f"# {overlay['theme_id']} — Teacher Guide V2",
        "",
        "> Bu dosya canonical ders kitabı/teacher-guide itemlerini değiştirmez. Pedagojik uygulama katmanıdır.",
        "> Kitaptaki soru metni canonical kaynakta birebir doğrulanmamışsa burada soru uydurulmaz; görev etiketi ve sayfa konumu kullanılır.",
        "> Canonical cevap, kabul ölçütü ve item düzeyi öğretmen notları mümkün olduğunda doğrudan bu çıktıda gösterilir.",
        "> Tahta notu yalnız küratörlü ve o blokta gerçekten işlevsel olduğunda gösterilir.",
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
            f"**Pedagojik faz:** {block['phase_name']}",
            "",
            "### Kitaptaki görevler ve cevap anahtarı",
        ]
        for card in block["task_cards"]:
            render_task_card(lines, card)

        lines += ["", "### Pedagojik amaç", "", block["pedagogical_intent"], "", "### Bu blokta öğretmen hamlesi"]
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
        lines += ["", "### Bu blokta farklılaştırma", "", "**Destek**"]
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
    phase_ordinals: dict[tuple[str, str], int] = defaultdict(int)
    unit_count = item_count = task_card_count = split_question_card_count = 0
    curated_assignment_count = contextual_fallback_count = 0
    board_note_block_count = 0

    for section_index in manifest["sections"]:
        section_id = section_index["section_id"]
        section = read_json(root / section_index["content_ref"])
        sections_by_id[section_id] = section
        section_profile = theme_profiles.get(section_id)
        if not isinstance(section_profile, dict):
            raise ValueError(f"missing section profile: {theme_id}:{section_id}")

        units = [unit for unit in section.get("guide_units", []) if unit.get("items")]
        assignments = assign_section_guidance(units, section["section_type"], section_profile)

        for unit_index, unit in enumerate(units):
            items = unit.get("items", [])
            refs = [item["item_id"] for item in items if isinstance(item.get("item_id"), str)]
            if not refs:
                continue

            unit_count += 1
            item_count += len(refs)
            phase_name = classify_phase(section["section_type"], unit["title"])
            phase = profiles["phase_profiles"][phase_name]
            assigned = assignments[unit["unit_id"]]
            curated_assignment_count += sum(len(assigned[field]) for field in PROFILE_FIELDS)

            purpose = unit.get("purpose")
            purpose_text = purpose.strip() if isinstance(purpose, str) and purpose.strip() else ""
            if unit_index == 0:
                pedagogical_intent = f"{section_profile['focus']} {purpose_text}".strip()
            else:
                pedagogical_intent = purpose_text or f"{unit['title']} için önceki blokta kurulan bölüm odağını derinleştir."

            task_cards: list[dict[str, Any]] = []
            for item in items:
                cards = make_task_cards(item)
                task_cards.extend(cards)
                task_card_count += len(cards)
                split_question_card_count += sum(1 for card in cards if card["split_from_group"])

            selected: dict[str, list[str]] = {}
            for field in (
                "teacher_moves",
                "follow_up_questions",
                "misconception_interventions",
                "board_notes",
                "assessment_look_fors",
                "support",
                "enrichment",
            ):
                ordinal_key = (phase_name, field)
                before = bool(assigned[field])
                selected[field] = select_guidance(
                    field,
                    assigned[field],
                    phase_name,
                    phase,
                    unit,
                    phase_ordinals[ordinal_key],
                )
                if field != "board_notes" and not before:
                    contextual_fallback_count += 1
                    phase_ordinals[ordinal_key] += 1

            if selected["board_notes"]:
                board_note_block_count += 1

            block = {
                "block_id": f"{theme_id.replace('TEMA_', 'T')}V2_{slug(unit['unit_id'])}",
                "section_id": section_id,
                "phase_name": phase_name,
                "printed_page_range": unit.get("printed_page_range") or section["printed_page_range"],
                "title": unit["title"],
                "source_item_refs": refs,
                "book_task_summaries": [f"{card['label']} [{card['item_type']}]" for card in task_cards],
                "task_cards": task_cards,
                "pedagogical_intent": pedagogical_intent,
                "teacher_moves": selected["teacher_moves"],
                "follow_up_questions": selected["follow_up_questions"],
                "misconception_interventions": selected["misconception_interventions"],
                "board_notes": selected["board_notes"],
                "assessment_look_fors": selected["assessment_look_fors"],
                "differentiation": {
                    "support": selected["support"],
                    "enrichment": selected["enrichment"],
                },
            }
            limitations = unique(assigned["source_limitations"])
            if limitations:
                block["source_limitations"] = limitations
            blocks.append(block)

    overlay = {
        "schema_version": "2.2.0",
        "document_type": "TYMM_TEACHER_GUIDE_PEDAGOGY_OVERLAY",
        "course_id": "TDE_11",
        "theme_id": theme_id,
        "status": "REVIEW_REQUIRED",
        "quality_review": None,
        "principles": profiles["principles"],
        "blocks": blocks,
    }
    overlay_path = guide_root / "pedagogy_v2.json"
    markdown_path = guide_root / "TEACHER_GUIDE_V2.md"
    overlay_path.write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(overlay, sections_by_id), encoding="utf-8")

    return overlay_path, markdown_path, {
        "theme": theme_id,
        "units": unit_count,
        "items": item_count,
        "task_cards": task_card_count,
        "split_question_cards": split_question_card_count,
        "blocks": len(blocks),
        "curated_guidance_assignments": curated_assignment_count,
        "contextual_fallbacks": contextual_fallback_count,
        "blocks_with_board_notes": board_note_block_count,
    }


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
