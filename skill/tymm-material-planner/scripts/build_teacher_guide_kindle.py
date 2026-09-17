#!/usr/bin/env python3
"""Build Kindle-friendly EPUB 3 books from TDE 11 Teacher Guide V3 JSON.

The V3 JSON remains the canonical source. This renderer only projects that data
into a reading-first layout optimized for Kindle/e-ink use. Internal task IDs,
provenance IDs and machine-oriented labels remain in the canonical data but are
not exposed in the teacher-facing reading surface.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import uuid
import zipfile
from pathlib import Path
from typing import Any, Iterable

COURSE_ID = "TDE_11"
THEMES = [f"TEMA_{index:02d}" for index in range(1, 5)]
DEFAULT_PROFILE = "courses/TDE_11/teacher_guide_kindle/kindle_profile.json"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
XHTML_NS = "http://www.w3.org/1999/xhtml"
EPUB_NS = "http://www.idpf.org/2007/ops"

TASK_TYPE_LABELS = {
    "QUESTION": "",
    "PROCESS": "Süreç görevi",
    "REFERENCE": "Başvuru",
    "ACTIVITY": "Etkinlik",
    "PERFORMANCE": "Performans görevi",
    "PERFORMANCE_TASK": "Performans görevi",
    "TEACHER_NOTE": "Öğretmen notu",
}

KEY_LABELS = {
    "organization": "Organizasyon",
    "organisation": "Organizasyon",
    "kart_ornekleri": "Kart örnekleri",
    "card_examples": "Kart örnekleri",
    "paylasim": "Paylaşım",
    "sharing": "Paylaşım",
    "adimlar": "Adımlar",
    "steps": "Adımlar",
    "amac": "Amaç",
    "purpose": "Amaç",
    "hedef_kitle": "Hedef kitle",
    "audience": "Hedef kitle",
    "icerik": "İçerik",
    "content": "İçerik",
    "kanit": "Kanıt",
    "evidence": "Kanıt",
    "gerekce": "Gerekçe",
    "reasoning": "Gerekçe",
    "degerlendirme": "Değerlendirme",
    "assessment": "Değerlendirme",
    "timing": "Zamanlama",
    "mental_reply": "Zihinde cevaplayıp göndermeme",
    "reply": "Yanıt",
    "example": "Örnek",
    "examples": "Örnekler",
    "result": "Sonuç",
    "results": "Sonuçlar",
}

INTERNAL_LOCATOR_PATTERNS = [
    re.compile(r"^(?:TEMA_\d+::)?T\d+(?:V\d+)?_[A-Z0-9_.:/-]+$", re.IGNORECASE),
    re.compile(r"^(?:BLOCK|FORM)_[A-Z0-9_.:/-]+$", re.IGNORECASE),
    re.compile(r"^[A-Z][A-Z0-9-]*(?:_[A-Z0-9.-]+){2,}$"),
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def escape(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def compact_ws(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def clean_visible_text(value: Any) -> str:
    """Remove machine-facing notation without changing the substantive content."""
    text = compact_ws(value)
    if not text:
        return ""

    # Curriculum/internal codes are useful in JSON provenance, not in a Kindle book.
    text = re.sub(r"\bTDE\d+(?:\.\d+)+\b", "ilgili öğrenme çıktısı", text)
    text = re.sub(r"\b(?:TEMA_\d+::)?T\d+(?:V\d+)?_[A-Z0-9_.:/-]+\b", "", text)
    text = re.sub(r"\b(?:BLOCK|FORM)_[A-Z0-9_.:/-]+\b", "", text)

    # Machine-generated answer-component labels such as “q1 timing:” are not
    # useful to a teacher. Keep the sub-question identity, discard the debug key.
    text = re.sub(
        r"\bq(\d+)\s+[a-z][a-z0-9 _-]{1,40}\s*:",
        lambda match: f"Alt soru {match.group(1)}:",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bq(\d+)\b", lambda match: f"{match.group(1)}. alt soru", text, flags=re.IGNORECASE)
    text = re.sub(r"\badimlar\s*:", "Adımlar:", text, flags=re.IGNORECASE)

    # Tidy punctuation left behind after removing internal tokens.
    text = re.sub(r"\(\s*[,;:·\-–—]*\s*\)", "", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,;:])\s*([,;:])", r"\1 ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def slug(value: str) -> str:
    result = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
    return result or "item"


def task_anchor(task_id: str) -> str:
    digest = hashlib.sha1(task_id.encode("utf-8")).hexdigest()[:10]
    return f"task-{slug(task_id)[:54]}-{digest}"


def humanize_key(key: str) -> str:
    normalized = key.strip().lower()
    if normalized in KEY_LABELS:
        return KEY_LABELS[normalized]

    match = re.fullmatch(r"q(\d+)_(.+)", normalized)
    if match:
        number, remainder = match.groups()
        remainder_label = KEY_LABELS.get(remainder, remainder.replace("_", " "))
        return f"Alt soru {number} — {remainder_label}"

    replacements = {
        "ornek": "örnek",
        "ornekleri": "örnekleri",
        "paylasim": "paylaşım",
        "adim": "adım",
        "adimlar": "adımlar",
        "icerik": "içerik",
        "degerlendirme": "değerlendirme",
        "gerekce": "gerekçe",
        "kanit": "kanıt",
        "cikti": "çıktı",
        "amac": "amaç",
        "olcut": "ölçüt",
        "olcutler": "ölçütler",
    }
    words = [replacements.get(word, word) for word in normalized.replace("-", "_").split("_") if word]
    label = " ".join(words).strip()
    return label[:1].upper() + label[1:] if label else key


def render_value(value: Any) -> str:
    if value is None or value == "" or value == [] or value == {}:
        return ""
    if isinstance(value, bool):
        return "Evet" if value else "Hayır"
    if isinstance(value, str):
        paragraphs = [clean_visible_text(part) for part in re.split(r"\n\s*\n", value)]
        paragraphs = [part for part in paragraphs if part]
        return "".join(f"<p>{escape(part)}</p>" for part in paragraphs)
    if isinstance(value, (int, float)):
        return f"<p>{escape(value)}</p>"
    if isinstance(value, list):
        parts = []
        for entry in value:
            if isinstance(entry, str):
                cleaned = clean_visible_text(entry)
                if cleaned:
                    parts.append(f"<li>{escape(cleaned)}</li>")
                continue
            rendered = render_value(entry)
            if rendered:
                parts.append(f"<li>{rendered}</li>")
        return f"<ul>{''.join(parts)}</ul>" if parts else ""
    if isinstance(value, dict):
        rows = []
        for key, entry in value.items():
            rendered = render_value(entry)
            if rendered:
                rows.append(f"<dt>{escape(humanize_key(str(key)))}</dt><dd>{rendered}</dd>")
        return f"<dl>{''.join(rows)}</dl>" if rows else ""
    cleaned = clean_visible_text(value)
    return f"<p>{escape(cleaned)}</p>" if cleaned else ""


def section_block(title: str, value: Any, css_class: str = "detail") -> str:
    body = render_value(value)
    if not body:
        return ""
    return f'<section class="{css_class}"><h4>{escape(title)}</h4>{body}</section>'


def list_block(title: str, values: Iterable[Any] | None, css_class: str = "detail") -> str:
    items = list(values or [])
    return section_block(title, items, css_class) if items else ""


def paired_misconceptions(task: dict[str, Any]) -> str:
    misconceptions = list(task.get("common_misconceptions") or [])
    interventions = list(task.get("misconception_interventions") or [])
    if not misconceptions and not interventions:
        return ""
    rows: list[str] = []
    count = max(len(misconceptions), len(interventions))
    for index in range(count):
        misconception = clean_visible_text(misconceptions[index]) if index < len(misconceptions) else ""
        intervention = clean_visible_text(interventions[index]) if index < len(interventions) else ""
        row = '<div class="misconception-pair">'
        if misconception:
            row += f'<p><strong>Yanılgı:</strong> {escape(misconception)}</p>'
        if intervention:
            row += f'<p><strong>Müdahale:</strong> {escape(intervention)}</p>'
        row += "</div>"
        rows.append(row)
    return '<section class="detail warning"><h4>Sık yanılgılar ve müdahale</h4>' + "".join(rows) + "</section>"


def task_type_label(task_type: Any) -> str:
    raw = compact_ws(task_type)
    if not raw:
        return ""
    return TASK_TYPE_LABELS.get(raw.upper(), raw.replace("_", " ").strip().capitalize())


def task_label(task: dict[str, Any]) -> str:
    bits: list[str] = []
    page_range = compact_ws(task.get("printed_page_range"))
    if page_range:
        bits.append(f"s. {page_range}")
    heading = clean_visible_text(task.get("book_heading"))
    if heading:
        bits.append(heading)
    question = compact_ws(task.get("question_number"))
    if question:
        bits.append(f"Soru {question}")
    else:
        type_label = task_type_label(task.get("task_type"))
        if type_label:
            bits.append(type_label)
    return " · ".join(bits) or "Görev"


def is_internal_locator(value: Any) -> bool:
    raw = compact_ws(value)
    if not raw:
        return True
    if raw.startswith(("courses/", "skill/")) or raw.endswith((".json", ".md")):
        return True
    return any(pattern.fullmatch(raw) for pattern in INTERNAL_LOCATOR_PATTERNS)


def public_source_lines(task: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for locator in task.get("source_locators") or []:
        if is_internal_locator(locator):
            continue
        cleaned = clean_visible_text(locator)
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key not in seen:
            seen.add(key)
            lines.append(cleaned)
    if task.get("content_status") == "REVIEW_REQUIRED":
        note = "Bu kart dış medya, QR veya kaynak sınırı nedeniyle öğretmen kontrolü gerektiriyor."
        if note.casefold() not in seen:
            lines.append(note)
    return lines


def render_task(task: dict[str, Any], profile: dict[str, Any]) -> str:
    anchor = task_anchor(task["task_id"])
    compact_fields = profile.get("compact_fields", {})
    detailed_fields = profile.get("detailed_fields", {})

    prompt_title = compact_fields.get("prompt_title", "Soru / görev")
    answer_title = compact_fields.get("answer_title", "Kısa cevap")
    student_title = compact_fields.get("student_title", "Sınıfta nasıl açıklarım?")
    move_title = compact_fields.get("move_title", "Öğretmen hamlesi")

    quick = []
    if task.get("book_prompt"):
        quick.append(section_block(prompt_title, task["book_prompt"], "quick prompt"))
    if task.get("expected_answer") not in (None, "", [], {}):
        quick.append(section_block(answer_title, task["expected_answer"], "quick answer"))
    elif task.get("expected_response") not in (None, "", [], {}):
        quick.append(section_block(answer_title, task["expected_response"], "quick answer"))
    if task.get("student_explanation"):
        quick.append(section_block(student_title, task["student_explanation"], "quick student"))
    if task.get("teacher_moves"):
        quick.append(list_block(move_title, task["teacher_moves"], "quick move"))

    details = [
        section_block(detailed_fields.get("answer_explanation", "Açıklama ve gerekçe"), task.get("answer_explanation")),
        section_block(detailed_fields.get("teacher_background", "Öğretmenin bilmesi gerekenler"), task.get("teacher_background")),
        section_block(detailed_fields.get("why_it_matters", "Bu görev neden burada?"), task.get("why_it_matters")),
        list_block(detailed_fields.get("follow_up_questions", "Takip soruları"), task.get("follow_up_questions")),
        paired_misconceptions(task),
        list_block(detailed_fields.get("assessment_look_fors", "Cevapta ne arayacağım?"), task.get("assessment_look_fors")),
        section_block(detailed_fields.get("support", "Destek"), task.get("support")),
        section_block(detailed_fields.get("enrichment", "Zenginleştirme"), task.get("enrichment")),
        list_block(detailed_fields.get("board_notes", "Tahta notu"), task.get("board_notes")),
    ]

    source_lines = public_source_lines(task)
    source_block = list_block("Kaynak", source_lines, "source") if source_lines else ""

    return (
        f'<article class="task" id="{anchor}" data-task-id="{escape(task["task_id"])}">'
        f'<h3>{escape(task_label(task))}</h3>'
        f'{"".join(quick)}'
        '<div class="details">'
        f'{"".join(part for part in details if part)}'
        f'{source_block}'
        '</div>'
        '</article>'
    )


def xhtml_document(title: str, body: str, css_href: str = "../css/kindle.css") -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="{XHTML_NS}" xmlns:epub="{EPUB_NS}" lang="tr" xml:lang="tr">
<head>
  <meta charset="utf-8" />
  <title>{escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="{css_href}" />
</head>
<body>
{body}
</body>
</html>
'''


def theme_label(theme_id: str) -> str:
    try:
        return f"{int(theme_id.split('_')[-1])}. Tema"
    except (TypeError, ValueError):
        return theme_id.replace("_", " ")


def render_title_page(book_title: str, subtitle: str, scope: str) -> str:
    body = f'''
<section class="title-page" epub:type="titlepage">
  <p class="eyebrow">TYMM · 11. Sınıf Türk Dili ve Edebiyatı</p>
  <h1>{escape(book_title)}</h1>
  <h2>{escape(subtitle)}</h2>
  <p>{escape(scope)}</p>
  <p class="small">Kaynak: 11. sınıf Öğretmen Rehberi V3. Bu EPUB öğretmenin hızlı başvuru ve ders içi kullanımına göre düzenlenmiştir.</p>
</section>
'''
    return xhtml_document(book_title, body, "css/kindle.css")


def render_section_page(theme: dict[str, Any], section: dict[str, Any], tasks: list[dict[str, Any]], profile: dict[str, Any]) -> str:
    task_html = "".join(render_task(task, profile) for task in tasks)
    body = f'''
<header class="section-header">
  <p class="theme-label">{escape(theme_label(theme['theme_id']))}</p>
  <h1>{escape(clean_visible_text(section['title']))}</h1>
  <p class="section-meta">Ders kitabı s. {escape(section['printed_page_range'])} · {len(tasks)} görev kartı</p>
</header>
{task_html}
'''
    return xhtml_document(clean_visible_text(section["title"]), body)


def render_nav(book_title: str, themes: list[dict[str, Any]], section_files: dict[str, str]) -> str:
    theme_items = []
    for theme in themes:
        sections = []
        for section in theme["sections"]:
            href = section_files[f"{theme['theme_id']}::{section['section_id']}"]
            sections.append(
                f'<li><a href="{escape(href)}">{escape(clean_visible_text(section["title"]))} '
                f'<span class="toc-page">s. {escape(section["printed_page_range"])}</span></a></li>'
            )
        title = clean_visible_text(theme.get("title", ""))
        theme_heading = f"{theme_label(theme['theme_id'])} — {title}" if title else theme_label(theme["theme_id"])
        theme_items.append(f'<li><span>{escape(theme_heading)}</span><ol>{"".join(sections)}</ol></li>')
    body = f'''
<nav epub:type="toc" id="toc">
  <h1>{escape(book_title)}</h1>
  <ol>
    <li><a href="title.xhtml">Başlangıç</a></li>
    {''.join(theme_items)}
  </ol>
</nav>
<nav epub:type="landmarks" hidden="hidden">
  <ol><li><a epub:type="bodymatter" href="title.xhtml">Başlangıç</a></li></ol>
</nav>
'''
    return xhtml_document("İçindekiler", body, "css/kindle.css")


def stylesheet() -> str:
    return """@charset \"UTF-8\";
body { font-family: serif; line-height: 1.45; margin: 5%; }
h1, h2, h3, h4 { font-family: sans-serif; line-height: 1.22; page-break-after: avoid; break-after: avoid; }
h1 { font-size: 1.55em; }
h2 { font-size: 1.18em; font-weight: normal; }
h3 { font-size: 1.12em; margin-top: 1.9em; border-top: 0.08em solid currentColor; padding-top: 0.72em; }
h4 { font-size: 0.98em; margin: 0 0 0.35em; }
p { margin: 0.48em 0; orphans: 2; widows: 2; }
ul, ol { margin: 0.35em 0 0.65em; padding-left: 1.35em; }
li { margin: 0.3em 0; }
dl { margin: 0.4em 0; }
dt { font-weight: bold; margin-top: 0.55em; }
dd { margin-left: 0.8em; }
.title-page { margin-top: 20%; text-align: center; }
.eyebrow, .theme-label { font-family: sans-serif; font-weight: bold; letter-spacing: 0.04em; }
.small, .section-meta, .source { font-size: 0.84em; }
.section-header { page-break-before: always; break-before: page; margin-bottom: 1.5em; }
.task { margin-bottom: 2.4em; }
.quick { border-left: 0.18em solid currentColor; padding: 0.15em 0 0.15em 0.75em; margin: 0.9em 0; page-break-inside: avoid; break-inside: avoid; }
.quick h4 { text-transform: uppercase; letter-spacing: 0.025em; }
.student { font-style: italic; }
.details { margin-top: 1.25em; }
.detail { margin-top: 1.05em; }
.warning { border: 0.06em solid currentColor; padding: 0.7em; }
.misconception-pair + .misconception-pair { border-top: 0.05em dotted currentColor; margin-top: 0.6em; padding-top: 0.6em; }
.source { border-top: 0.05em solid currentColor; margin-top: 1.25em; padding-top: 0.55em; }
.toc-page { font-size: 0.85em; }
a { color: inherit; text-decoration: none; }
"""


def container_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
'''


def render_opf(book_title: str, identifier: str, modified: str, section_files: list[str]) -> str:
    manifest = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="css" href="css/kindle.css" media-type="text/css"/>',
        '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
    ]
    spine = ['<itemref idref="title"/>']
    for index, href in enumerate(section_files, start=1):
        item_id = f"sec{index:03d}"
        manifest.append(f'<item id="{item_id}" href="{escape(href)}" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{item_id}"/>')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="tr">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="pub-id">{escape(identifier)}</dc:identifier>
    <dc:title>{escape(book_title)}</dc:title>
    <dc:language>tr</dc:language>
    <dc:creator>TYMM Öğretmen Rehberi V3</dc:creator>
    <meta property="dcterms:modified">{escape(modified)}</meta>
  </metadata>
  <manifest>{''.join(manifest)}</manifest>
  <spine>{''.join(spine)}</spine>
</package>
'''


def zip_write_text(zf: zipfile.ZipFile, name: str, text: str, compress: bool = True) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
    info.external_attr = 0o644 << 16
    zf.writestr(info, text.encode("utf-8"))


def source_digest(themes: list[dict[str, Any]]) -> str:
    payload = json.dumps(themes, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_epub(output: Path, book_title: str, subtitle: str, themes: list[dict[str, Any]], profile: dict[str, Any]) -> dict[str, Any]:
    section_files: dict[str, str] = {}
    section_docs: list[tuple[str, str]] = []
    ordered_hrefs: list[str] = []

    for theme in themes:
        task_map = {task["task_id"]: task for task in theme["tasks"]}
        for section_index, section in enumerate(theme["sections"], start=1):
            tasks = [task_map[task_id] for task_id in section["task_ids"] if task_id in task_map]
            filename = f'text/{theme["theme_id"].lower()}_{section_index:03d}_{slug(section["section_id"])}.xhtml'
            section_files[f'{theme["theme_id"]}::{section["section_id"]}'] = filename
            ordered_hrefs.append(filename)
            section_docs.append((filename, render_section_page(theme, section, tasks, profile)))

    digest = source_digest(themes)
    identifier = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"tymm:{COURSE_ID}:{digest}:{book_title}"))
    modified = profile.get("metadata", {}).get("modified", "2026-09-17T00:00:00Z")
    task_count = sum(len(theme["tasks"]) for theme in themes)
    scope = f'{len(themes)} tema · {task_count} görev kartı · Kindle/e-ink okuma düzeni'

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as zf:
        zip_write_text(zf, "mimetype", "application/epub+zip", compress=False)
        zip_write_text(zf, "META-INF/container.xml", container_xml())
        zip_write_text(zf, "OEBPS/css/kindle.css", stylesheet())
        zip_write_text(zf, "OEBPS/title.xhtml", render_title_page(book_title, subtitle, scope))
        zip_write_text(zf, "OEBPS/nav.xhtml", render_nav(book_title, themes, section_files))
        for href, document in section_docs:
            zip_write_text(zf, f"OEBPS/{href}", document)
        zip_write_text(zf, "OEBPS/content.opf", render_opf(book_title, identifier, modified, ordered_hrefs))

    return {
        "path": str(output),
        "themes": [theme["theme_id"] for theme in themes],
        "tasks": task_count,
        "sections": sum(len(theme["sections"]) for theme in themes),
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "source_sha256": digest,
    }


def load_theme(root: Path, theme_id: str) -> dict[str, Any]:
    path = root / "courses" / COURSE_ID / "teacher_guide" / theme_id / "teacher_guide_v3.json"
    if not path.exists():
        raise FileNotFoundError(path)
    guide = read_json(path)
    if guide.get("schema_version") != "3.0.0" or guide.get("document_type") != "TYMM_TEACHER_GUIDE_V3":
        raise ValueError(f"not a Teacher Guide V3 document: {path}")
    if guide.get("course_id") != COURSE_ID or guide.get("theme_id") != theme_id:
        raise ValueError(f"guide identity mismatch: {path}")
    return guide


def build_all(root: Path, profile_path: Path, output_dir: Path | None = None) -> list[dict[str, Any]]:
    profile = read_json(profile_path)
    configured_themes = profile.get("themes") or THEMES
    themes = [load_theme(root, theme_id) for theme_id in configured_themes]
    outputs = output_dir or (root / profile.get("output_dir", "courses/TDE_11/teacher_guide_kindle/output"))
    metadata = profile.get("metadata", {})

    reports = []
    combined_name = profile.get("combined_filename", "TDE_11_OGRETMEN_REHBERI_V3.epub")
    reports.append(
        build_epub(
            outputs / combined_name,
            metadata.get("title", "11. Sınıf Türk Dili ve Edebiyatı — Öğretmen Rehberi"),
            metadata.get("subtitle", "Öğretmen Rehberi V3 · Kindle Sürümü"),
            themes,
            profile,
        )
    )

    if profile.get("build_theme_books", True):
        for theme in themes:
            number = theme["theme_id"].split("_")[-1]
            reports.append(
                build_epub(
                    outputs / f"TDE_11_TEMA_{number}_OGRETMEN_REHBERI_V3.epub",
                    f'{metadata.get("title", "11. Sınıf Türk Dili ve Edebiyatı — Öğretmen Rehberi")} · Tema {int(number)}',
                    clean_visible_text(theme.get("title")) or metadata.get("subtitle", "Öğretmen Rehberi V3 · Kindle Sürümü"),
                    [theme],
                    profile,
                )
            )
    return reports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--profile", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    profile_path = (args.profile or (root / DEFAULT_PROFILE)).resolve()
    output_dir = args.output_dir.resolve() if args.output_dir else None
    reports = build_all(root, profile_path, output_dir)
    print(json.dumps({"status": "PASS", "outputs": reports}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
