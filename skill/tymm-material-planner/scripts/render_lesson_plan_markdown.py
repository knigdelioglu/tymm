#!/usr/bin/env python3
"""Deterministically render TYMM lesson-plan JSON as teacher-readable Markdown.

The renderer is intentionally fail-closed: if a plan contains a field that is not
explicitly represented here, rendering fails instead of silently dropping it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

TOP_LEVEL_KEYS = {
    "schema_version",
    "course_id",
    "theme_id",
    "block_id",
    "lesson_hours",
    "plan_title",
    "plan_summary",
    "instruction_scope",
    "assessment_scope",
    "assessed_outcome_codes",
    "grounded_references",
    "large_class_route",
    "classroom_adaptations",
    "outcome_codes",
    "used_activity_ids",
    "used_form_ids",
    "lessons",
    "teacher_notes",
    "continuation_summary",
}
LESSON_KEYS = {
    "lesson_no",
    "duration_lesson_hours",
    "title",
    "objective",
    "instruction_scope",
    "assessment_scope",
    "assessed_outcome_codes",
    "outcome_codes",
    "opening",
    "teacher_actions",
    "student_actions",
    "activity_ids",
    "form_ids",
    "assessment",
    "closure",
    "materials",
}
CONTINUATION_KEYS = {
    "planned_now_hours",
    "remaining_block_hours",
    "covered_outcome_codes",
    "used_activity_ids",
    "next_step_hint",
}
GROUNDING_KEYS = {"form_refs", "assessment_artifact_refs", "resource_refs"}
LARGE_CLASS_KEYS = {
    "mode",
    "activation_condition",
    "applies_to_lesson_numbers",
    "parallel_group_count",
    "grouping_strategy",
    "teacher_rotation_strategy",
    "peer_observer_strategy",
    "performance_time_limit_seconds",
    "evidence_equivalence",
    "core_hours_independent_of_school_based_extension",
    "optional_school_based_extension",
}
ADAPTATION_KEYS = {
    "trigger_categories",
    "justification",
    "differentiation",
    "accessibility",
    "media_fallback",
    "live_performance_access",
    "evidence_equivalence",
}
DIFFERENTIATION_KEYS = {"scaffold_route", "enrichment_route", "outcomes_unchanged"}
ACCESSIBILITY_KEYS = {
    "representation_supports",
    "participation_supports",
    "environment_supports",
    "assessment_construct_preserved",
}
MEDIA_FALLBACK_KEYS = {
    "required",
    "network_independent_core_route",
    "same_source_or_equivalent_required",
    "transcript_is_support_not_default_substitute",
    "offline_route",
    "access_support_route",
}
LIVE_ACCESS_KEYS = {
    "required",
    "alternative_modes",
    "same_performance_evidence_required",
    "written_only_substitution_allowed",
    "recording_requires_consent",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_known(value: dict[str, Any], allowed: set[str], where: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"UNRENDERED_FIELDS:{where}:{','.join(unknown)}")


def _md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _bool(value: bool) -> str:
    return "Evet" if value else "Hayır"


def _code_list(values: list[Any]) -> str:
    if not values:
        return "Yok"
    return ", ".join(f"`{value}`" for value in values)


def _bullet_strings(lines: list[str], values: list[Any]) -> None:
    if not values:
        lines.append("- Yok")
        return
    lines.extend(f"- {value}" for value in values)


def _numbered_strings(lines: list[str], values: list[Any]) -> None:
    if not values:
        lines.append("1. Yok")
        return
    lines.extend(f"{index}. {value}" for index, value in enumerate(values, start=1))


def canonical_digest(plan: dict[str, Any]) -> str:
    payload = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _render_grounding(lines: list[str], grounding: dict[str, Any]) -> None:
    _ensure_known(grounding, GROUNDING_KEYS, "grounded_references")
    lines.extend(["## Canonical referanslar", ""])

    lines.extend(["### Form referansları", "", "| Form | Kullanım |", "|---|---|"])
    for item in grounding.get("form_refs", []):
        _ensure_known(item, {"form_id", "usage"}, "grounded_references.form_refs[]")
        lines.append(f"| `{_md_cell(item['form_id'])}` | `{_md_cell(item['usage'])}` |")
    if not grounding.get("form_refs"):
        lines.append("| — | — |")
    lines.append("")

    lines.extend(["### Değerlendirme artefakt referansları", "", "| Artefakt | Binding | Kullanım |", "|---|---|---|"])
    for item in grounding.get("assessment_artifact_refs", []):
        _ensure_known(item, {"artifact_id", "binding_key", "usage"}, "grounded_references.assessment_artifact_refs[]")
        lines.append(
            f"| `{_md_cell(item['artifact_id'])}` | `{_md_cell(item['binding_key'])}` | `{_md_cell(item['usage'])}` |"
        )
    if not grounding.get("assessment_artifact_refs"):
        lines.append("| — | — | — |")
    lines.append("")

    lines.extend(["### Kaynak plan referansları", "", "| Kaynak planı | Kullanım |", "|---|---|"])
    for item in grounding.get("resource_refs", []):
        _ensure_known(item, {"resource_plan_id", "usage"}, "grounded_references.resource_refs[]")
        lines.append(f"| `{_md_cell(item['resource_plan_id'])}` | `{_md_cell(item['usage'])}` |")
    if not grounding.get("resource_refs"):
        lines.append("| — | — |")
    lines.append("")


def _render_large_class(lines: list[str], route: dict[str, Any]) -> None:
    _ensure_known(route, LARGE_CLASS_KEYS, "large_class_route")
    lines.extend(
        [
            "## Kalabalık sınıf rotası",
            "",
            f"- **Mod:** `{route['mode']}`",
            f"- **Aktivasyon:** {route['activation_condition']}",
            f"- **Uygulandığı dersler:** {_code_list(route['applies_to_lesson_numbers'])}",
            f"- **Paralel grup sayısı:** {route['parallel_group_count']}",
            f"- **Gruplama:** {route['grouping_strategy']}",
            f"- **Öğretmen rotasyonu:** {route['teacher_rotation_strategy']}",
            f"- **Akran gözlemci:** {route['peer_observer_strategy']}",
            f"- **Performans zaman sınırı:** {route['performance_time_limit_seconds']} saniye",
            f"- **Kanıt eşdeğerliği:** {route['evidence_equivalence']}",
            f"- **Çekirdek saat okul-temelli uzatmadan bağımsız:** {_bool(route['core_hours_independent_of_school_based_extension'])}",
        ]
    )
    extension = route.get("optional_school_based_extension")
    if extension is not None:
        _ensure_known(extension, {"allowed", "purpose"}, "large_class_route.optional_school_based_extension")
        lines.extend(
            [
                f"- **Opsiyonel okul-temelli uzatma:** {_bool(extension['allowed'])}",
                f"- **Opsiyonel uzatma amacı:** {extension['purpose']}",
            ]
        )
    lines.append("")


def _render_adaptations(lines: list[str], adaptations: dict[str, Any]) -> None:
    _ensure_known(adaptations, ADAPTATION_KEYS, "classroom_adaptations")
    lines.extend(
        [
            "## Sınıf uyarlamaları",
            "",
            f"- **Tetikleyiciler:** {_code_list(adaptations['trigger_categories'])}",
            f"- **Gerekçe:** {adaptations['justification']}",
            f"- **Kanıt eşdeğerliği:** {adaptations['evidence_equivalence']}",
            "",
        ]
    )

    differentiation = adaptations["differentiation"]
    _ensure_known(differentiation, DIFFERENTIATION_KEYS, "classroom_adaptations.differentiation")
    lines.extend(["### Farklılaştırma", "", "**Destek rotası**", ""])
    _bullet_strings(lines, differentiation["scaffold_route"])
    lines.extend(["", "**Zenginleştirme rotası**", ""])
    _bullet_strings(lines, differentiation["enrichment_route"])
    lines.extend(["", f"**Öğrenme çıktıları değişmez:** {_bool(differentiation['outcomes_unchanged'])}", ""])

    accessibility = adaptations["accessibility"]
    _ensure_known(accessibility, ACCESSIBILITY_KEYS, "classroom_adaptations.accessibility")
    lines.extend(["### Erişilebilirlik", "", "**Temsil destekleri**", ""])
    _bullet_strings(lines, accessibility["representation_supports"])
    lines.extend(["", "**Katılım destekleri**", ""])
    _bullet_strings(lines, accessibility["participation_supports"])
    lines.extend(["", "**Ortam destekleri**", ""])
    _bullet_strings(lines, accessibility["environment_supports"])
    lines.extend(
        [
            "",
            f"**Değerlendirme construct'ı korunur:** {_bool(accessibility['assessment_construct_preserved'])}",
            "",
        ]
    )

    media = adaptations.get("media_fallback")
    if media is not None:
        _ensure_known(media, MEDIA_FALLBACK_KEYS, "classroom_adaptations.media_fallback")
        lines.extend(
            [
                "### Medya fallback",
                "",
                f"- **Zorunlu:** {_bool(media['required'])}",
                f"- **Çevrimdışı çekirdek rota:** {_bool(media['network_independent_core_route'])}",
                f"- **Aynı/eşdeğer kaynak zorunlu:** {_bool(media['same_source_or_equivalent_required'])}",
                f"- **Transkript varsayılan ikame değildir:** {_bool(media['transcript_is_support_not_default_substitute'])}",
                f"- **Çevrimdışı rota:** {media['offline_route']}",
                f"- **Erişim desteği:** {media['access_support_route']}",
                "",
            ]
        )

    live = adaptations.get("live_performance_access")
    if live is not None:
        _ensure_known(live, LIVE_ACCESS_KEYS, "classroom_adaptations.live_performance_access")
        lines.extend(
            [
                "### Canlı performans erişimi",
                "",
                f"- **Zorunlu:** {_bool(live['required'])}",
                f"- **Alternatif modlar:** {_code_list(live['alternative_modes'])}",
                f"- **Aynı performans kanıtı zorunlu:** {_bool(live['same_performance_evidence_required'])}",
                f"- **Yalnız yazılı ikameye izin:** {_bool(live['written_only_substitution_allowed'])}",
                f"- **Kayıt rıza gerektirir:** {_bool(live['recording_requires_consent'])}",
                "",
            ]
        )


def _render_lesson(lines: list[str], lesson: dict[str, Any]) -> None:
    _ensure_known(lesson, LESSON_KEYS, f"lessons[{lesson.get('lesson_no', '?')}]")
    lines.extend(
        [
            f"## {lesson['lesson_no']}. Ders — {lesson['title']}",
            "",
            f"**Süre:** {lesson['duration_lesson_hours']} ders saati  ",
            f"**Öğrenme çıktıları:** {_code_list(lesson['outcome_codes'])}",
        ]
    )
    if "instruction_scope" in lesson:
        lines.append(f"**Öğretim kapsamı:** `{lesson['instruction_scope']}`  ")
    if "assessment_scope" in lesson:
        lines.append(f"**Değerlendirme kapsamı:** `{lesson['assessment_scope']}`  ")
        lines.append(f"**Değerlendirilen çıktılar:** {_code_list(lesson['assessed_outcome_codes'])}")
    lines.extend(["", "### Hedef", "", lesson["objective"], "", "### Derse giriş", "", lesson["opening"], ""])

    lines.extend(["### Öğretmenin yapacakları", ""])
    _numbered_strings(lines, lesson["teacher_actions"])
    lines.extend(["", "### Öğrencinin yapacakları", ""])
    _bullet_strings(lines, lesson["student_actions"])
    lines.extend(
        [
            "",
            "### Kaynak bağları",
            "",
            f"- **Etkinlikler:** {_code_list(lesson['activity_ids'])}",
            f"- **Formlar:** {_code_list(lesson['form_ids'])}",
            "",
            "### Ölçme / öğrenme kanıtı",
            "",
            lesson["assessment"],
            "",
            "### Kapanış",
            "",
            lesson["closure"],
            "",
            "### Materyaller",
            "",
        ]
    )
    _bullet_strings(lines, lesson["materials"])
    lines.append("")


def _render_continuation(lines: list[str], continuation: dict[str, Any]) -> None:
    _ensure_known(continuation, CONTINUATION_KEYS, "continuation_summary")
    lines.extend(
        [
            "## İlerleme ve devam",
            "",
            f"- **Bu pakette planlanan:** {continuation['planned_now_hours']} saat",
            f"- **Blokta kalan:** {continuation['remaining_block_hours']} saat",
            f"- **Kapsanan çıktılar:** {_code_list(continuation['covered_outcome_codes'])}",
            f"- **Kullanılan etkinlikler:** {_code_list(continuation['used_activity_ids'])}",
            f"- **Sonraki adım:** {continuation['next_step_hint']}",
            "",
        ]
    )


def render(plan: dict[str, Any]) -> str:
    _ensure_known(plan, TOP_LEVEL_KEYS, "$")
    lines: list[str] = [
        f"# {plan['plan_title']}",
        "",
        "> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.",
        "",
        "## Paket bilgisi",
        "",
        "| Alan | Değer |",
        "|---|---|",
        f"| Ders | `{_md_cell(plan['course_id'])}` |",
        f"| Tema | `{_md_cell(plan['theme_id'])}` |",
        f"| Blok | `{_md_cell(plan['block_id'])}` |",
        f"| Süre | {plan['lesson_hours']} ders saati |",
        f"| Şema | `{_md_cell(plan['schema_version'])}` |",
        "",
        "## Paket özeti",
        "",
        plan["plan_summary"],
        "",
        "## Öğrenme ve değerlendirme kapsamı",
        "",
        f"- **Öğrenme çıktıları:** {_code_list(plan['outcome_codes'])}",
        f"- **Kullanılan etkinlikler:** {_code_list(plan['used_activity_ids'])}",
        f"- **Kullanılan formlar:** {_code_list(plan['used_form_ids'])}",
    ]
    if "instruction_scope" in plan:
        lines.append(f"- **Öğretim kapsamı:** `{plan['instruction_scope']}`")
    if "assessment_scope" in plan:
        lines.append(f"- **Değerlendirme kapsamı:** `{plan['assessment_scope']}`")
        lines.append(f"- **Değerlendirilen çıktılar:** {_code_list(plan['assessed_outcome_codes'])}")
    lines.append("")

    if "grounded_references" in plan:
        _render_grounding(lines, plan["grounded_references"])
    if "large_class_route" in plan:
        _render_large_class(lines, plan["large_class_route"])
    if "classroom_adaptations" in plan:
        _render_adaptations(lines, plan["classroom_adaptations"])

    lines.extend(["# Ders akışı", ""])
    for lesson in plan["lessons"]:
        _render_lesson(lines, lesson)

    lines.extend(["## Öğretmen notu", "", plan["teacher_notes"] or "—", ""])
    _render_continuation(lines, plan["continuation_summary"])
    lines.extend(
        [
            "---",
            "",
            f"<!-- TYMM_JSON_SHA256:{canonical_digest(plan)} -->",
            "",
        ]
    )
    return "\n".join(lines)


def render_file(json_path: Path, *, write: bool) -> Path:
    plan = read_json(json_path)
    markdown = render(plan)
    md_path = json_path.with_suffix(".md")
    if write:
        md_path.write_text(markdown, encoding="utf-8")
    return md_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    count = 0
    for root_text in args.knowledge_root:
        root = Path(root_text)
        for json_path in sorted((root / "generated/lesson_plans").glob("**/*.json")):
            render_file(json_path, write=args.write)
            count += 1
    print(json.dumps({"status": "PASS", "packages": count, "written": bool(args.write)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
