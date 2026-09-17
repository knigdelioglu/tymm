#!/usr/bin/env python3
"""Validate Kindle EPUB outputs against canonical Teacher Guide V3 JSON."""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

COURSE_ID = "TDE_11"
THEMES = [f"TEMA_{index:02d}" for index in range(1, 5)]
DEFAULT_PROFILE = "courses/TDE_11/teacher_guide_kindle/kindle_profile.json"
XHTML_NS = "http://www.w3.org/1999/xhtml"
CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
OPF_NS = "http://www.idpf.org/2007/opf"

VISIBLE_DEBUG_PATTERNS = [
    ("INTERNAL_ID_VISIBLE", re.compile(r"\b(?:TEMA_\d+::)?T\d+(?:V\d+)?_[A-Z0-9_.:/-]+\b")),
    ("BLOCK_FORM_ID_VISIBLE", re.compile(r"\b(?:BLOCK|FORM)_[A-Z0-9_.:/-]+\b")),
    ("CURRICULUM_CODE_VISIBLE", re.compile(r"\bTDE\d+(?:\.\d+)+\b")),
    ("MACHINE_SUBQUESTION_LABEL_VISIBLE", re.compile(r"\bq\d+\s+[a-z][a-z0-9 _-]{1,40}\s*:", re.IGNORECASE)),
    ("ENGLISH_TASK_TYPE_VISIBLE", re.compile(r"\b(?:Process|Reference)\b")),
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_task_ids(root: Path, themes: list[str]) -> dict[str, list[str]]:
    result = {}
    for theme in themes:
        path = root / "courses" / COURSE_ID / "teacher_guide" / theme / "teacher_guide_v3.json"
        guide = read_json(path)
        result[theme] = [task["task_id"] for task in guide["tasks"]]
    return result


def visible_text(doc: ET.Element) -> str:
    return re.sub(r"\s+", " ", " ".join(part for part in doc.itertext() if part)).strip()


def validate_epub(path: Path, expected_task_ids: list[str]) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"MISSING_EPUB: {path}"]

    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        if not names or names[0] != "mimetype":
            errors.append("EPUB_MIMETYPE_NOT_FIRST")
        if "mimetype" not in names or zf.read("mimetype") != b"application/epub+zip":
            errors.append("EPUB_MIMETYPE_INVALID")
        elif zf.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            errors.append("EPUB_MIMETYPE_COMPRESSED")
        for required in ["META-INF/container.xml", "OEBPS/content.opf", "OEBPS/nav.xhtml", "OEBPS/title.xhtml"]:
            if required not in names:
                errors.append(f"EPUB_REQUIRED_FILE_MISSING: {required}")

        if "META-INF/container.xml" in names:
            try:
                container = ET.fromstring(zf.read("META-INF/container.xml"))
                rootfile = container.find(f".//{{{CONTAINER_NS}}}rootfile")
                if rootfile is None or rootfile.attrib.get("full-path") != "OEBPS/content.opf":
                    errors.append("EPUB_CONTAINER_ROOTFILE_INVALID")
            except ET.ParseError as exc:
                errors.append(f"EPUB_CONTAINER_XML_INVALID: {exc}")

        manifest_hrefs: set[str] = set()
        spine_ids: list[str] = []
        id_to_href: dict[str, str] = {}
        if "OEBPS/content.opf" in names:
            try:
                opf = ET.fromstring(zf.read("OEBPS/content.opf"))
                for item in opf.findall(f".//{{{OPF_NS}}}manifest/{{{OPF_NS}}}item"):
                    item_id, href = item.attrib.get("id"), item.attrib.get("href")
                    if item_id and href:
                        id_to_href[item_id] = href
                        manifest_hrefs.add(href)
                for itemref in opf.findall(f".//{{{OPF_NS}}}spine/{{{OPF_NS}}}itemref"):
                    if itemref.attrib.get("idref"):
                        spine_ids.append(itemref.attrib["idref"])
                for idref in spine_ids:
                    if idref not in id_to_href:
                        errors.append(f"EPUB_SPINE_ID_MISSING_FROM_MANIFEST: {idref}")
            except ET.ParseError as exc:
                errors.append(f"EPUB_OPF_XML_INVALID: {exc}")

        seen_tasks: list[str] = []
        debug_hits: Counter[tuple[str, str]] = Counter()
        for name in names:
            if not name.endswith(".xhtml"):
                continue
            try:
                doc = ET.fromstring(zf.read(name))
            except ET.ParseError as exc:
                errors.append(f"EPUB_XHTML_INVALID: {name}: {exc}")
                continue

            text = visible_text(doc)
            for code, pattern in VISIBLE_DEBUG_PATTERNS:
                for match in pattern.finditer(text):
                    debug_hits[(code, match.group(0))] += 1

            # Machine IDs are allowed as invisible data attributes for parity,
            # but the old visible task-meta paragraph must never return.
            for node in doc.findall(f".//{{{XHTML_NS}}}p"):
                classes = set(node.attrib.get("class", "").split())
                if "task-meta" in classes:
                    errors.append(f"VISIBLE_TASK_META_PRESENT: {name}")
                    break

            if not name.startswith("OEBPS/text/"):
                continue
            for article in doc.findall(f".//{{{XHTML_NS}}}article"):
                task_id = article.attrib.get("data-task-id")
                if task_id:
                    seen_tasks.append(task_id)

        for (code, token), count in sorted(debug_hits.items()):
            errors.append(f"{code}: {token!r} x{count}")

        seen_counter = Counter(seen_tasks)
        expected_counter = Counter(expected_task_ids)
        missing = sorted((expected_counter - seen_counter).elements())
        extras = sorted((seen_counter - expected_counter).elements())
        duplicates = sorted(task_id for task_id, count in seen_counter.items() if count > 1)
        if missing:
            errors.append(f"TASKS_MISSING: {len(missing)}: {missing[:12]}")
        if extras:
            errors.append(f"TASKS_EXTRA: {len(extras)}: {extras[:12]}")
        if duplicates:
            errors.append(f"TASKS_DUPLICATE: {len(duplicates)}: {duplicates[:12]}")

        for href in manifest_hrefs:
            if href.startswith("http:") or href.startswith("https:"):
                continue
            if f"OEBPS/{href}" not in names:
                errors.append(f"EPUB_MANIFEST_TARGET_MISSING: {href}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--profile", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    profile_path = (args.profile or (root / DEFAULT_PROFILE)).resolve()
    profile = read_json(profile_path)
    themes = profile.get("themes") or THEMES
    output_dir = args.output_dir.resolve() if args.output_dir else (root / profile.get("output_dir", "courses/TDE_11/teacher_guide_kindle/output"))
    canonical = canonical_task_ids(root, themes)

    checks = []
    combined = output_dir / profile.get("combined_filename", "TDE_11_OGRETMEN_REHBERI_V3.epub")
    combined_errors = validate_epub(combined, [task_id for theme in themes for task_id in canonical[theme]])
    checks.append({"file": str(combined), "errors": combined_errors})

    if profile.get("build_theme_books", True):
        for theme in themes:
            number = theme.split("_")[-1]
            path = output_dir / f"TDE_11_TEMA_{number}_OGRETMEN_REHBERI_V3.epub"
            checks.append({"file": str(path), "errors": validate_epub(path, canonical[theme])})

    errors = [error for check in checks for error in check["errors"]]
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "checks": checks, "error_count": len(errors)}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
