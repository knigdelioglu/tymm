#!/usr/bin/env python3
"""Temporary branch codemod for specific-evidence integration validation."""
from pathlib import Path


def patch(path_text: str, replacements: list[tuple[str, str]]) -> None:
    path = Path(path_text)
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"PATCH_ANCHOR_COUNT:{path}:{count}:{old[:80]!r}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


patch("skill/tymm-material-planner/scripts/lesson_plan_generator.py", [
    (
        "import lesson_plan_context\nimport validate_lesson_plan\n",
        "import lesson_plan_context\nimport lesson_plan_evidence_quality\nimport validate_lesson_plan\n",
    ),
    (
        "        \"Öğretim akışını pedagojik öneri olarak tasarla; bunu resmî MEB alt-ders sıralaması gibi sunma. \"\n"
        "        \"Yanıt yalnız RESPONSE_SCHEMA ile uyumlu tek bir JSON nesnesi olmalıdır.\"\n",
        "        \"Öğretim akışını pedagojik öneri olarak tasarla; bunu resmî MEB alt-ders sıralaması gibi sunma. \"\n"
        "        \"Önceki öğrenme veya ölçme kanıtına atıf gerekiyorsa çalışma ürünleri gibi toplu ifadeler kullanma; \"\n"
        "        \"metni ve somut kanıt türünü adıyla belirt. \"\n"
        "        \"Yanıt yalnız RESPONSE_SCHEMA ile uyumlu tek bir JSON nesnesi olmalıdır.\"\n",
    ),
    (
        "            \"continuation_summary.remaining_block_hours, blok toplamından önceki tamamlanan saatler ve bu plan düşülerek hesaplanmalı.\",\n"
        "            \"Takvim alanları üretme.\",\n",
        "            \"continuation_summary.remaining_block_hours, blok toplamından önceki tamamlanan saatler ve bu plan düşülerek hesaplanmalı.\",\n"
        "            \"Önceki öğrenme/ölçme kanıtlarına atıfta P01-P06 öğrenci çalışma ürünleri, önceki ürünler veya çalışma ürünleri gibi belirsiz toplu ifadeler kullanma; ilgili metni ve kanıtı somut adıyla yaz (ör. anlama/çözümleme cevapları ve zihin haritası, Kontrol Noktası ve düzeltme kaydı, karşılaştırma tablosu).\",\n"
        "            \"Takvim alanları üretme.\",\n",
    ),
    (
        "    errors = list(shape_errors) + list(grounding.get(\"errors\", []))\n"
        "    warnings = list(grounding.get(\"warnings\", []))\n",
        "    errors = list(shape_errors) + list(grounding.get(\"errors\", []))\n"
        "    errors += lesson_plan_evidence_quality.vague_evidence_errors(plan)\n"
        "    warnings = list(grounding.get(\"warnings\", []))\n",
    ),
])

patch("skill/tymm-material-planner/scripts/runtime_lesson_plan_payload.py", [
    (
        "import teacher_facing_text\nimport validation_binding\n",
        "import lesson_plan_evidence_quality\nimport teacher_facing_text\nimport validation_binding\n",
    ),
    (
        "        return teacher_facing_text.normalize_teacher_facing_text(\n"
        "            source_payload,\n"
        "            catalog=teacher_catalog,\n"
        "            package_ranges=ranges,\n"
        "        )\n",
        "        evidence_payload = lesson_plan_evidence_quality.project_specific_assessment_evidence(\n"
        "            source_payload,\n"
        "            plan_path=path,\n"
        "        )\n"
        "        return teacher_facing_text.normalize_teacher_facing_text(\n"
        "            evidence_payload,\n"
        "            catalog=teacher_catalog,\n"
        "            package_ranges=ranges,\n"
        "        )\n",
    ),
])

patch("skill/tymm-material-planner/scripts/validate_all_lesson_plans.py", [
    (
        "import lesson_plan_context  # noqa: E402\nimport teacher_facing_text  # noqa: E402\n",
        "import lesson_plan_context  # noqa: E402\nimport lesson_plan_evidence_quality  # noqa: E402\nimport teacher_facing_text  # noqa: E402\n",
    ),
    (
        "            teacher_projection = teacher_facing_text.normalize_teacher_facing_text(\n"
        "                plan,\n"
        "                catalog=teacher_catalog,\n"
        "                package_ranges=ranges,\n"
        "            )\n"
        "            projection_errors = teacher_facing_text.teacher_facing_validation_errors(\n"
        "                teacher_projection\n"
        "            )\n",
        "            evidence_projection = lesson_plan_evidence_quality.project_specific_assessment_evidence(\n"
        "                plan,\n"
        "                plan_path=plan_path,\n"
        "            )\n"
        "            teacher_projection = teacher_facing_text.normalize_teacher_facing_text(\n"
        "                evidence_projection,\n"
        "                catalog=teacher_catalog,\n"
        "                package_ranges=ranges,\n"
        "            )\n"
        "            projection_errors = teacher_facing_text.teacher_facing_validation_errors(\n"
        "                teacher_projection\n"
        "            )\n"
        "            projection_errors += lesson_plan_evidence_quality.vague_evidence_errors(\n"
        "                teacher_projection\n"
        "            )\n",
    ),
])

patch("skill/tymm-material-planner/scripts/render_teacher_lesson_plan_markdown.py", [
    (
        "import render_lesson_plan_markdown as canonical_renderer\nimport teacher_facing_text\n",
        "import lesson_plan_evidence_quality\nimport render_lesson_plan_markdown as canonical_renderer\nimport teacher_facing_text\n",
    ),
    (
        "def render_teacher(\n"
        "    plan: dict[str, Any],\n"
        "    *,\n"
        "    catalog: teacher_facing_text.TeacherReferenceCatalog,\n"
        "    package_ranges: dict[int, teacher_facing_text.PackageRange],\n"
        ") -> str:\n",
        "def render_teacher(\n"
        "    plan: dict[str, Any],\n"
        "    *,\n"
        "    catalog: teacher_facing_text.TeacherReferenceCatalog,\n"
        "    package_ranges: dict[int, teacher_facing_text.PackageRange],\n"
        "    source_digest: str | None = None,\n"
        ") -> str:\n",
    ),
    (
        "        source_digest=canonical_renderer.canonical_digest(plan),\n",
        "        source_digest=source_digest or canonical_renderer.canonical_digest(plan),\n",
    ),
    (
        "        plan = canonical_renderer.read_json(json_path)\n"
        "        ranges = teacher_facing_text.package_ranges_for_block(json_path.parent)\n"
        "        markdown = render_teacher(plan, catalog=catalog, package_ranges=ranges)\n",
        "        plan = canonical_renderer.read_json(json_path)\n"
        "        evidence_plan = lesson_plan_evidence_quality.project_specific_assessment_evidence(\n"
        "            plan,\n"
        "            plan_path=json_path,\n"
        "        )\n"
        "        ranges = teacher_facing_text.package_ranges_for_block(json_path.parent)\n"
        "        markdown = render_teacher(\n"
        "            evidence_plan,\n"
        "            catalog=catalog,\n"
        "            package_ranges=ranges,\n"
        "            source_digest=canonical_renderer.canonical_digest(plan),\n"
        "        )\n",
    ),
])

print("SPECIFIC_EVIDENCE_INTEGRATION_PATCHED")
