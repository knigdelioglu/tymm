#!/usr/bin/env python3
"""Render canonical TYMM lesson plans as distribution-ready teacher Markdown.

The canonical JSON and canonical Markdown remain audit artifacts. This renderer
builds a display-only projection: structured IDs are resolved to readable
labels, teacher prose is humanized, and official TYMM learning-outcome codes
remain visible because they are legitimate curriculum references.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

import render_lesson_plan_markdown as canonical_renderer
import teacher_facing_text


SCOPE_LABELS = {
    "PACKAGE": "Bu ders planı",
    "BLOCK": "Ders bölümü",
    "THEME": "Tema",
    "COURSE": "Ders geneli",
    "ANNUAL": "Yıl geneli",
    "CORE": "Temel öğretim",
    "CORE_INSTRUCTION": "Temel öğretim",
}
USAGE_LABELS = {
    "USED": "Kullanılıyor",
    "REFERENCE_ONLY": "Başvuru amacıyla",
    "REQUIRED": "Gerekli",
    "OPTIONAL": "İsteğe bağlı",
}
ENUM_LABELS = {
    **teacher_facing_text.ENUM_LABELS,
    "PARALLEL_GROUPS": "Paralel grup çalışması",
    "SMALL_GROUP_LIVE": "Küçük grupta canlı uygulama",
    "TEACHER_OBSERVED_LIVE": "Öğretmen gözleminde canlı uygulama",
    "RECORDED_ORAL_IF_ALLOWED": "Uygunsa kayıtlı sözlü uygulama",
}

VISIBLE_TECHNICAL_RE = teacher_facing_text.TECHNICAL_REFERENCE_RE
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _label(mapping: dict[str, str], value: Any) -> str:
    key = str(value or "").strip()
    if not key:
        return "—"
    return mapping.get(key, key)


def _reference_label(catalog: teacher_facing_text.TeacherReferenceCatalog, value: Any) -> str:
    key = str(value or "").strip()
    replacements = {
        **catalog.activities,
        **catalog.activity_aliases,
        **catalog.forms,
        **catalog.form_aliases,
        **catalog.artifacts,
        **catalog.resources,
        **catalog.resource_aliases,
        **catalog.sections,
        **catalog.texts,
        **catalog.blocks,
        **catalog.themes,
        **catalog.package_refs,
    }
    return replacements.get(key, key)


def _teacher_display_plan(
    plan: dict[str, Any],
    *,
    catalog: teacher_facing_text.TeacherReferenceCatalog,
    package_ranges: dict[int, teacher_facing_text.PackageRange],
) -> dict[str, Any]:
    display = teacher_facing_text.normalize_teacher_facing_text(
        plan,
        catalog=catalog,
        package_ranges=package_ranges,
    )
    display = copy.deepcopy(display)

    display["course_id"] = catalog.course_label
    display["theme_id"] = catalog.themes.get(str(plan.get("theme_id")), str(plan.get("theme_id")))
    display["block_id"] = catalog.blocks.get(str(plan.get("block_id")), str(plan.get("block_id")))
    display["used_activity_ids"] = [
        _reference_label(catalog, value) for value in plan.get("used_activity_ids", [])
    ]
    display["used_form_ids"] = [
        _reference_label(catalog, value) for value in plan.get("used_form_ids", [])
    ]
    if "instruction_scope" in display:
        display["instruction_scope"] = _label(SCOPE_LABELS, display["instruction_scope"])
    if "assessment_scope" in display:
        display["assessment_scope"] = _label(SCOPE_LABELS, display["assessment_scope"])

    for index, lesson in enumerate(display.get("lessons", [])):
        source = plan.get("lessons", [])[index]
        lesson["activity_ids"] = [
            _reference_label(catalog, value) for value in source.get("activity_ids", [])
        ]
        lesson["form_ids"] = [
            _reference_label(catalog, value) for value in source.get("form_ids", [])
        ]
        if "instruction_scope" in lesson:
            lesson["instruction_scope"] = _label(SCOPE_LABELS, lesson["instruction_scope"])
        if "assessment_scope" in lesson:
            lesson["assessment_scope"] = _label(SCOPE_LABELS, lesson["assessment_scope"])

    continuation = display.get("continuation_summary")
    source_continuation = plan.get("continuation_summary")
    if isinstance(continuation, dict) and isinstance(source_continuation, dict):
        continuation["used_activity_ids"] = [
            _reference_label(catalog, value)
            for value in source_continuation.get("used_activity_ids", [])
        ]

    grounding = display.get("grounded_references")
    source_grounding = plan.get("grounded_references")
    if isinstance(grounding, dict) and isinstance(source_grounding, dict):
        for target, source in zip(
            grounding.get("form_refs", []), source_grounding.get("form_refs", [])
        ):
            target["form_id"] = _reference_label(catalog, source.get("form_id"))
            target["usage"] = _label(USAGE_LABELS, source.get("usage"))
        for target, source in zip(
            grounding.get("assessment_artifact_refs", []),
            source_grounding.get("assessment_artifact_refs", []),
        ):
            target["artifact_id"] = _reference_label(catalog, source.get("artifact_id"))
            target["binding_key"] = "İlgili değerlendirme görevi"
            target["usage"] = _label(USAGE_LABELS, source.get("usage"))
        for target, source in zip(
            grounding.get("resource_refs", []), source_grounding.get("resource_refs", [])
        ):
            target["resource_plan_id"] = _reference_label(
                catalog, source.get("resource_plan_id")
            )
            target["usage"] = _label(USAGE_LABELS, source.get("usage"))

    large_class = display.get("large_class_route")
    if isinstance(large_class, dict):
        large_class["mode"] = _label(ENUM_LABELS, large_class.get("mode"))

    adaptations = display.get("classroom_adaptations")
    if isinstance(adaptations, dict):
        adaptations["trigger_categories"] = [
            _label(ENUM_LABELS, value) for value in adaptations.get("trigger_categories", [])
        ]
        live = adaptations.get("live_performance_access")
        if isinstance(live, dict):
            live["alternative_modes"] = [
                _label(ENUM_LABELS, value) for value in live.get("alternative_modes", [])
            ]

    return display


def _polish_markdown(markdown: str, *, source_digest: str) -> str:
    replacements = (
        ("> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.",
         "> Bu belge doğrulanmış ders planı verilerinden otomatik olarak hazırlanmıştır."),
        ("## Paket bilgisi", "## Plan bilgisi"),
        ("## Paket özeti", "## Plan özeti"),
        ("## Canonical referanslar", "## Kaynak ve değerlendirme bağlantıları"),
        ("### Form referansları", "### Değerlendirme formları"),
        ("### Değerlendirme artefakt referansları", "### Değerlendirme araçları"),
        ("| Artefakt | Binding | Kullanım |", "| Değerlendirme aracı | İlişkili görev | Kullanım |"),
        ("### Kaynak plan referansları", "### Ek öğretim materyalleri"),
        ("| Kaynak planı | Kullanım |", "| Materyal | Kullanım |"),
        ("## Kalabalık sınıf rotası", "## Kalabalık sınıflarda uygulama"),
        ("**Mod:**", "**Uygulama biçimi:**"),
        ("**Aktivasyon:**", "**Ne zaman kullanılır:**"),
        ("**Tetikleyiciler:**", "**Bu uyarlamanın gerektiği durumlar:**"),
        ("**Değerlendirme construct'ı korunur:**", "**Ölçülen beceri korunur:**"),
        ("### Medya fallback", "### Medya kullanılamadığında alternatif uygulama"),
        ("**Alternatif modlar:**", "**Alternatif uygulama biçimleri:**"),
        ("### Kaynak bağları", "### Kullanılacak kaynaklar"),
        ("**Blokta kalan:**", "**Bu ders bölümünde kalan:**"),
    )
    for old, new in replacements:
        markdown = markdown.replace(old, new)

    markdown = re.sub(r"^\| Şema \|.*\|\n", "", markdown, flags=re.MULTILINE)
    markdown = re.sub(
        r"<!-- TYMM_JSON_SHA256:[0-9a-f]+ -->",
        f"<!-- TYMM_SOURCE_SHA256:{source_digest} -->",
        markdown,
    )
    return markdown


def visible_technical_references(markdown: str) -> list[str]:
    visible = HTML_COMMENT_RE.sub("", markdown)
    # Official TYMM outcome codes (e.g. TDE2.2) contain no underscore and are
    # deliberately not matched by the implementation-ID detector.
    return sorted({match.group(0) for match in VISIBLE_TECHNICAL_RE.finditer(visible)})


def render_teacher(
    plan: dict[str, Any],
    *,
    catalog: teacher_facing_text.TeacherReferenceCatalog,
    package_ranges: dict[int, teacher_facing_text.PackageRange],
) -> str:
    display = _teacher_display_plan(
        plan,
        catalog=catalog,
        package_ranges=package_ranges,
    )
    markdown = canonical_renderer.render(display)
    markdown = _polish_markdown(
        markdown,
        source_digest=canonical_renderer.canonical_digest(plan),
    )
    unresolved = visible_technical_references(markdown)
    if unresolved:
        raise teacher_facing_text.TeacherFacingTextError(
            f"UNRESOLVED_TEACHER_MARKDOWN_REFERENCES:{unresolved}"
        )
    return markdown


def export_course(root: Path, *, output_root: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    catalog = teacher_facing_text.TeacherReferenceCatalog.from_knowledge_root(root)
    source_root = root / "generated/lesson_plans"
    destination_root = output_root or (root / "generated/teacher_lesson_plans")
    written = 0

    for json_path in sorted(source_root.glob("*/*/*.json")):
        relative = json_path.relative_to(source_root)
        destination = destination_root / relative.with_suffix(".md")
        plan = canonical_renderer.read_json(json_path)
        ranges = teacher_facing_text.package_ranges_for_block(json_path.parent)
        markdown = render_teacher(plan, catalog=catalog, package_ranges=ranges)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(markdown, encoding="utf-8")
        written += 1

    return {
        "course_id": root.name,
        "status": "PASS",
        "written": written,
        "output_root": destination_root.as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument("--output-root")
    args = parser.parse_args()

    reports = []
    for root_text in args.knowledge_root:
        root = Path(root_text)
        output_root = Path(args.output_root) / root.name if args.output_root else None
        reports.append(export_course(root, output_root=output_root))
    print(json.dumps({"status": "PASS", "courses": reports}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
