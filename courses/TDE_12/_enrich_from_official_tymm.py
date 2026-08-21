#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
MAP_PATH = ROOT / "curriculum_map.json"
MANIFEST_PATH = ROOT / "source_manifest.json"
REMOTE_PATH = ROOT / "curriculum_remote_sections.json"
REPORT_PATH = ROOT / "validation_report.md"
README_PATH = ROOT / "README.md"

THEMES = {
    "TEMA_01": {
        "number": 1,
        "title": "BENİM YOLCULUĞUM",
        "url": "https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/335",
    },
    "TEMA_02": {
        "number": 2,
        "title": "TOPLUMUN AHENGİ",
        "url": "https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/340",
    },
    "TEMA_03": {
        "number": 3,
        "title": "HAYATIN DENGESİ",
        "url": "https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/348",
    },
    "TEMA_04": {
        "number": 4,
        "title": "HAYALİMDEKİ YARIN",
        "url": "https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/351",
    },
}

SECTION_SPECS = {
    "field_skills": ("Alan Becerileri", "Eğilimler"),
    "tendencies": ("Eğilimler", "Programlar Arası Bileşenler"),
    "social_emotional_learning_skills": ("Sosyal-Duygusal Öğrenme Becerileri", "Değerler"),
    "values": ("Değerler", "Okuryazarlık Becerileri"),
    "literacy_skills": ("Okuryazarlık Becerileri", "Disiplinler Arası İlişkiler"),
    "interdisciplinary_relations": ("Disiplinler Arası İlişkiler", "Beceriler Arası İlişkiler"),
    "skills_relations": ("Beceriler Arası İlişkiler", "Öğrenme Çıktıları ve Süreç Bileşenleri"),
    "content_framework": ("İçerik Çerçevesi", "Anahtar Kavramlar"),
    "key_concepts": ("Anahtar Kavramlar", "Öğrenme Kanıtları (Ölçme ve Değerlendirme)"),
    "learning_evidence": ("Öğrenme Kanıtları (Ölçme ve Değerlendirme)", "Öğrenme-Öğretme Yaşantıları"),
    "learning_teaching_experiences": ("Öğrenme-Öğretme Yaşantıları", "Farklılaştırma"),
}

OUTCOME_SUBHEADINGS = {
    "Metin Tahlili (Anlama)",
    "Dinleme/İzleme",
    "Okuma",
    "Edebiyat Atölyesi (Anlatma)",
    "Konuşma",
    "Yazma",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def fetch_lines(url: str, theme_number: int, title: str) -> tuple[list[str], str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 TYMM curriculum canonical validator"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    lines = [norm(x) for x in soup.get_text("\n", strip=True).splitlines() if norm(x)]
    anchor = f"{theme_number}. TEMA: {title}"
    try:
        start = lines.index(anchor)
    except ValueError as exc:
        raise AssertionError(f"OFFICIAL_THEME_ANCHOR_NOT_FOUND:{anchor}") from exc
    scoped = lines[start:]
    raw_text = "\n".join(scoped)
    return scoped, hashlib.sha256(raw_text.encode("utf-8")).hexdigest()


def index_exact(lines: list[str], value: str, start: int = 0) -> int:
    for idx in range(start, len(lines)):
        if lines[idx] == value:
            return idx
    raise AssertionError(f"OFFICIAL_SECTION_HEADING_NOT_FOUND:{value}")


def section(lines: list[str], start_heading: str, end_heading: str) -> str:
    a = index_exact(lines, start_heading)
    b = index_exact(lines, end_heading, a + 1)
    text = "\n".join(lines[a + 1:b]).strip()
    if not text:
        raise AssertionError(f"OFFICIAL_SECTION_EMPTY:{start_heading}")
    return text


def extract_outcomes(lines: list[str]) -> dict[str, str]:
    a = index_exact(lines, "Öğrenme Çıktıları ve Süreç Bileşenleri")
    b = index_exact(lines, "İçerik Çerçevesi", a + 1)
    segment = lines[a + 1:b]
    rows: dict[str, str] = {}
    current: str | None = None
    chunks: list[str] = []

    def flush() -> None:
        nonlocal current, chunks
        if current is not None:
            text = norm(" ".join(chunks))
            if not text:
                raise AssertionError(f"REMOTE_OUTCOME_EMPTY:{current}")
            rows[current] = text
        current = None
        chunks = []

    for line in segment:
        m = re.match(r"^(TDE[1-4]\.[1-4])\.\s*(.*)$", line)
        if m:
            flush()
            current = m.group(1)
            chunks = [m.group(2)] if m.group(2) else []
            continue
        if current is not None and line not in OUTCOME_SUBHEADINGS:
            chunks.append(line)
    flush()

    expected = [f"TDE{x}.{y}" for x in range(1, 5) for y in range(1, 5)]
    if list(rows) != expected:
        raise AssertionError(f"REMOTE_OUTCOME_SET_MISMATCH:{list(rows)}")
    return rows


def extract_differentiation(lines: list[str]) -> dict[str, str]:
    a = index_exact(lines, "Farklılaştırma")
    enrich = index_exact(lines, "Zenginleştirme", a + 1)
    support = index_exact(lines, "Destekleme", enrich + 1)
    tail = len(lines)
    for idx in range(support + 1, len(lines)):
        if lines[idx] == "#####":
            tail = idx
            break
    enrichment = "\n".join(lines[enrich + 1:support]).strip()
    supporting = "\n".join(lines[support + 1:tail]).strip()
    if not enrichment or not supporting:
        raise AssertionError("DIFFERENTIATION_SUBSECTION_EMPTY")
    return {
        "verbatim": "\n".join(lines[enrich:tail]).strip(),
        "enrichment": enrichment,
        "support": supporting,
    }


def conceptual_skills_from_relations(relations: str) -> str:
    parts = [norm(p) for p in relations.replace("\n", " ").split(",")]
    kb = [p for p in parts if re.match(r"^KB\d+\.\d+\.", p)]
    if not kb:
        raise AssertionError("CONCEPTUAL_SKILLS_NOT_FOUND_IN_SKILLS_RELATIONS")
    return ", ".join(kb)


def explicit_element(url: str, heading: str, value: str) -> dict:
    return {
        "source_status": "SOURCE_EXPLICIT",
        "heading": heading,
        "verbatim": value,
        "source_locator": f"{url} :: {heading}",
        "verification_status": "VERIFIED_OFFICIAL_WEB",
        "canonical_evidence_file": "curriculum_remote_sections.json",
    }


def main() -> int:
    curriculum = load_json(MAP_PATH)
    manifest = load_json(MANIFEST_PATH)
    by_theme = {row["theme_id"]: row for row in curriculum["themes"]}
    remote_themes = []

    for theme_id, meta in THEMES.items():
        theme = by_theme[theme_id]
        assert theme["exact_theme_name"] == meta["title"]
        assert theme["source_locator"] == meta["url"]
        lines, page_text_sha256 = fetch_lines(meta["url"], meta["number"], meta["title"])

        sections: dict[str, str] = {}
        for key, (start_heading, end_heading) in SECTION_SPECS.items():
            sections[key] = section(lines, start_heading, end_heading)

        diff = extract_differentiation(lines)
        outcomes = extract_outcomes(lines)
        conceptual = conceptual_skills_from_relations(sections["skills_relations"])

        # Fail closed on the high-value section identities expected on every TDE_12 theme page.
        assert "Metin Tahlili (Anlama)" in sections["field_skills"]
        assert re.search(r"\bE\d+\.\d+\.", sections["tendencies"])
        assert "SDB" in sections["social_emotional_learning_skills"]
        assert re.search(r"\bD\d+\.", sections["values"])
        assert "OB" in sections["literacy_skills"]
        assert "KB" in sections["skills_relations"]
        assert meta["title"].split()[0].title() in sections["content_framework"] or "temas" in sections["content_framework"].lower()
        assert "performans görevi" in sections["learning_evidence"].lower()
        assert "Temel Kabuller" in sections["learning_teaching_experiences"]

        elements = theme.setdefault("program_elements", {})
        for key, (heading, _) in SECTION_SPECS.items():
            elements[key] = explicit_element(meta["url"], heading, sections[key])

        elements["conceptual_skills"] = {
            "source_status": "SOURCE_EXPLICIT_WITHIN_SKILLS_RELATIONS",
            "heading": "Beceriler Arası İlişkiler",
            "verbatim": conceptual,
            "source_locator": f"{meta['url']} :: Beceriler Arası İlişkiler",
            "verification_status": "VERIFIED_OFFICIAL_WEB",
            "canonical_evidence_file": "curriculum_remote_sections.json",
            "extraction_rule": "Only source-published KB-coded conceptual skills are projected from Beceriler Arası İlişkiler; no code is synthesized.",
        }
        elements["differentiation"] = {
            **explicit_element(meta["url"], "Farklılaştırma", diff["verbatim"]),
            "enrichment": {
                "heading": "Zenginleştirme",
                "verbatim": diff["enrichment"],
                "source_locator": f"{meta['url']} :: Zenginleştirme",
            },
            "support": {
                "heading": "Destekleme",
                "verbatim": diff["support"],
                "source_locator": f"{meta['url']} :: Destekleme",
            },
        }

        for outcome in theme["learning_outcomes"]:
            code = outcome["outcome_code"]
            outcome["outcome_verbatim"] = outcomes[code]
            outcome["source_locator"] = f"{meta['url']} :: {code}"
            outcome["verification_status"] = "VERIFIED_OFFICIAL_WEB_AND_LOCAL_PDF"
            outcome["remote_evidence_file"] = "curriculum_remote_sections.json"

        remote_themes.append({
            "theme_id": theme_id,
            "theme_title": meta["title"],
            "source_url": meta["url"],
            "normalized_page_text_sha256": page_text_sha256,
            "verification_status": "VERIFIED_OFFICIAL_WEB",
            "sections": {
                **sections,
                "conceptual_skills_projected_from_skills_relations": conceptual,
                "differentiation": diff,
            },
            "learning_outcomes": outcomes,
        })

    curriculum["last_validated"] = str(date.today())
    curriculum["canonical_freeze_status"] = "FROZEN_PENDING_SOURCE_FINGERPRINT_CHANGE"
    validation = curriculum.setdefault("source_validation", {})
    validation["program_elements_official_web_status"] = "PASS_4_OF_4_REQUIRED_SECTION_FAMILIES_CAPTURED"
    validation["program_elements_required_families_per_theme"] = 13
    validation["program_elements_required_families_total"] = 52
    validation["remote_outcome_verbatim_status"] = "PASS_64_OF_64_OFFICIAL_WEB_VERBATIM"
    validation["remote_section_evidence_file"] = "curriculum_remote_sections.json"
    validation["canonical_revalidation_status"] = "PASS_AFTER_OFFICIAL_WEB_PROGRAM_ELEMENT_ENRICHMENT"

    remote = {
        "schema_version": "1.0",
        "course_id": "TDE_12",
        "grade": 12,
        "course_title": "Türk Dili ve Edebiyatı",
        "captured_on": str(date.today()),
        "authority": "T.C. Millî Eğitim Bakanlığı - Türkiye Yüzyılı Maarif Modeli",
        "evidence_type": "OFFICIAL_REMOTE_TYMM_THEME_SECTION_TEXT",
        "canonical_role": "Clean official-web verbatim companion to the immutable local PDF evidence. Local PDFs remain the primary binary snapshots.",
        "themes": remote_themes,
    }
    REMOTE_PATH.write_text(json.dumps(remote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MAP_PATH.write_text(json.dumps(curriculum, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest["last_validated"] = str(date.today())
    manifest["remote_section_evidence"] = {
        "status": "VERIFIED_4_OF_4_OFFICIAL_THEME_PAGES",
        "evidence_file": "curriculum_remote_sections.json",
        "purpose": "Clean official-web verbatim for program elements and outcome text; local PDF SHA-256 snapshots remain primary source fingerprints.",
        "theme_count": 4,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = REPORT_PATH.read_text(encoding="utf-8")
    marker = "## Program bileşenleri kanıt derinliği"
    if marker in report:
        report = report.split(marker)[0].rstrip() + "\n"
    report += f"""

{marker}

- Program element capture: **PASS — 4/4 tema × 13 zorunlu bileşen ailesi = 52/52**
- Outcome temiz web verbatim doğrulaması: **PASS — 64/64**
- Resmî web evidence: `curriculum_remote_sections.json`
- PDF text-layer glyph bozulmaları canonical outcome metnine taşınmadı; yerel PDF ve `curriculum_normative_text.json` birincil snapshot/kanıt katmanı olarak korunmaktadır.
- Kavramsal beceriler yalnız `Beceriler Arası İlişkiler` içinde resmen yayımlanan `KB*` kayıtlarından projekte edilmiştir; sentetik kod üretilmemiştir.
- Farklılaştırma, Zenginleştirme ve Destekleme hükümleri 4/4 tema için verbatim yakalanmıştır.
"""
    REPORT_PATH.write_text(report.rstrip() + "\n", encoding="utf-8")

    readme = README_PATH.read_text(encoding="utf-8")
    if "curriculum_remote_sections.json" not in readme:
        readme += "\n- `curriculum_remote_sections.json`: Resmî TYMM tema sayfalarından temiz verbatim program bileşeni/outcome kanıtı; PDF snapshot kanıtını tamamlar.\n"
    README_PATH.write_text(readme.rstrip() + "\n", encoding="utf-8")

    # Final local assertions before the shared gate.
    for theme in curriculum["themes"]:
        elements = theme["program_elements"]
        for key in [
            "field_skills", "tendencies", "social_emotional_learning_skills", "values",
            "literacy_skills", "interdisciplinary_relations", "skills_relations",
            "conceptual_skills", "content_framework", "key_concepts", "learning_evidence",
            "learning_teaching_experiences", "differentiation",
        ]:
            assert elements[key]["source_status"].startswith("SOURCE_EXPLICIT"), (theme["theme_id"], key)
            assert elements[key]["verbatim"], (theme["theme_id"], key)
            assert "�" not in elements[key]["verbatim"], (theme["theme_id"], key)
        for outcome in theme["learning_outcomes"]:
            assert "�" not in outcome["outcome_verbatim"], (theme["theme_id"], outcome["outcome_code"])

    print("TDE12 OFFICIAL WEB PROGRAM ELEMENT ENRICHMENT: PASS")
    print("program element families: 52/52")
    print("clean official-web outcomes: 64/64")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
