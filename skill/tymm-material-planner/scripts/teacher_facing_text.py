#!/usr/bin/env python3
"""Resolve TYMM implementation IDs in prose shown to teachers.

Canonical IDs remain authoritative in structured JSON fields. Only prose is
humanized, and labels come from verified course metadata rather than a manual
per-plan translation table.
"""
from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TECHNICAL_REFERENCE_RE = re.compile(
    r"\b(?:P\d{1,2}|[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+)\b",
    re.IGNORECASE,
)
PACKAGE_RANGE_CORE = r"P(\d{1,2})\s*[-–—/]\s*P(\d{1,2})"
PACKAGE_RANGE_ATTR_RE = re.compile(
    rf"\b{PACKAGE_RANGE_CORE}['’]?(?:deki|daki|teki|taki)\b",
    re.IGNORECASE,
)
PACKAGE_RANGE_LOCATIVE_RE = re.compile(
    rf"\b{PACKAGE_RANGE_CORE}['’]?(?:de|da|te|ta)\b",
    re.IGNORECASE,
)
PACKAGE_RANGE_ABLATIVE_RE = re.compile(
    rf"\b{PACKAGE_RANGE_CORE}['’]?(?:den|dan|ten|tan)\b",
    re.IGNORECASE,
)
PACKAGE_RANGE_DATIVE_RE = re.compile(
    rf"\b{PACKAGE_RANGE_CORE}['’]?(?:ye|ya|e|a)\b",
    re.IGNORECASE,
)
PACKAGE_RANGE_GENITIVE_RE = re.compile(
    rf"\b{PACKAGE_RANGE_CORE}['’]?(?:nin|nın|nun|nün|in|ın|un|ün)\b",
    re.IGNORECASE,
)
PACKAGE_RANGE_ACCUSATIVE_RE = re.compile(
    rf"\b{PACKAGE_RANGE_CORE}['’]?(?:yi|yı|yu|yü|i|ı|u|ü)\b",
    re.IGNORECASE,
)
PACKAGE_RANGE_RE = re.compile(rf"\b{PACKAGE_RANGE_CORE}\b", re.IGNORECASE)

PACKAGE_ATTR_RE = re.compile(
    r"\bP(\d{1,2})['’]?(?:deki|daki|teki|taki)\b",
    re.IGNORECASE,
)
PACKAGE_LOCATIVE_RE = re.compile(
    r"\bP(\d{1,2})['’]?(?:de|da|te|ta)\b",
    re.IGNORECASE,
)
PACKAGE_ABLATIVE_RE = re.compile(
    r"\bP(\d{1,2})['’]?(?:den|dan|ten|tan)\b",
    re.IGNORECASE,
)
PACKAGE_DATIVE_RE = re.compile(
    r"\bP(\d{1,2})['’]?(?:ye|ya|e|a)\b",
    re.IGNORECASE,
)
PACKAGE_GENITIVE_RE = re.compile(
    r"\bP(\d{1,2})['’]?(?:nin|nın|nun|nün|in|ın|un|ün)\b",
    re.IGNORECASE,
)
PACKAGE_ACCUSATIVE_RE = re.compile(
    r"\bP(\d{1,2})['’]?(?:yi|yı|yu|yü|i|ı|u|ü)\b",
    re.IGNORECASE,
)
PACKAGE_RE = re.compile(r"\bP(\d{1,2})\b", re.IGNORECASE)

ACTIVITY_SHORT_RE = re.compile(r"^(T\d+_ACT_\d+)(?:_|$)", re.IGNORECASE)
FORM_SHORT_RE = re.compile(r"^(FORM_[A-Z]+_\d+)(?:_|$)", re.IGNORECASE)
RESOURCE_SHORT_RE = re.compile(r"^(RES_T\d+_\d+)(?:_|$)", re.IGNORECASE)
PACKAGE_FILE_RE = re.compile(r"_P(\d{2})\.json$", re.IGNORECASE)
COURSE_ID_RE = re.compile(r"\bTDE_(\d+)\b", re.IGNORECASE)
THEME_PREFIX_RE = re.compile(r"^\s*\d+\.\s*TEMA\s*:\s*", re.IGNORECASE)
REGISTRY_PAGE_RE = re.compile(r"Ders kitabı\s+s\.\s*([^;]+)", re.IGNORECASE)
DUPLICATE_PAGE_RE = re.compile(
    r"(\(ders kitabı s\.\s*[^)]+\))\s*[—-]\s*ders kitabı s\.\s*"
    r"\d+(?:\s*[-–—]\s*\d+)?",
    re.IGNORECASE,
)

ENUM_LABELS = {
    "MEDIA_DEPENDENT": "medya gerektiren",
    "LIVE_PERFORMANCE": "canlı performans",
    "REVIEW_REQUIRED": "öğretmen incelemesi gereken",
    "REFERENCE_ONLY": "yalnızca başvuru amacıyla",
    "DIGITAL_TOOL": "dijital araç",
    "VIDEO": "video",
}

TEACHER_TERM_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bfresh-read edilmeden\b", re.IGNORECASE), "yeniden okunmadan"),
    (re.compile(r"\blesson plan\b", re.IGNORECASE), "ders planı"),
    (re.compile(r"\bteaching block\b", re.IGNORECASE), "öğretim bloğu"),
    (re.compile(r"\bmaster sıra\b", re.IGNORECASE), "ana üretim sırası"),
    (re.compile(r"\bcursor\b", re.IGNORECASE), "üretim konumu"),
    (re.compile(r"\bsummative\b", re.IGNORECASE), "sonuç değerlendirme"),
    (re.compile(r"\bapproved\b", re.IGNORECASE), "onaylanmış"),
    (re.compile(r"\balignment\b", re.IGNORECASE), "program eşleştirmesi"),
    (re.compile(r"\bcanonical\b", re.IGNORECASE), "tanımlı"),
    (re.compile(r"\bfirst-class\b", re.IGNORECASE), "temel"),
    (re.compile(r"\bassessment_criteria_table\b", re.IGNORECASE), "değerlendirme ölçütleri tablosu"),
    (re.compile(r"\banalytic_rubric\b", re.IGNORECASE), "analitik dereceli puanlama anahtarı"),
    (re.compile(r"\bassessment_gate_audit\b", re.IGNORECASE), "değerlendirme uygunluk denetimi"),
    (re.compile(r"\bvalidate_lesson_plan\b", re.IGNORECASE), "ders planı doğrulaması"),
    (re.compile(r"\bclosure_time_budgets\.json\b", re.IGNORECASE), "tema kapanışı süre planı"),
    (re.compile(r"\brequired_segments\b", re.IGNORECASE), "zorunlu bölümler"),
    (re.compile(r"\boptional_extensions\b", re.IGNORECASE), "isteğe bağlı genişletmeler"),
)


class TeacherFacingTextError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TeacherFacingTextError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


def _string(value: Any) -> str:
    return str(value or "").strip()


def _page_label(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower().startswith("s."):
        text = text[2:].strip()
    return f"ders kitabı s. {text}"


def _with_page(title: str, page: Any) -> str:
    label = _page_label(page)
    return title if label is None else f"{title} ({label})"


def _theme_label(theme_no: Any, title: str) -> str:
    cleaned = THEME_PREFIX_RE.sub("", title).strip()
    if theme_no and cleaned:
        return f"{theme_no}. Tema: {cleaned}"
    return cleaned or title


def _unique_aliases(
    values: dict[str, str],
    pattern: re.Pattern[str],
) -> dict[str, str]:
    candidates: dict[str, set[str]] = {}
    for key, label in values.items():
        match = pattern.match(key)
        if match:
            candidates.setdefault(match.group(1), set()).add(label)
    return {
        alias: next(iter(labels))
        for alias, labels in candidates.items()
        if len(labels) == 1
    }


def _registry_page(locator: Any) -> str | None:
    match = REGISTRY_PAGE_RE.search(_string(locator))
    return match.group(1).strip() if match else None


def _generic_resource_label(resource: dict[str, Any]) -> str:
    resource_type = _string(resource.get("resource_type")).lower()
    if "assessment" in resource_type:
        return "ilgili değerlendirme desteği"
    if "differ" in resource_type:
        return "ilgili farklılaştırma desteği"
    if "enrich" in resource_type:
        return "ilgili zenginleştirme materyali"
    if "guide" in resource_type:
        return "ilgili öğretmen rehberi"
    return "ilgili öğretim materyali"


PackageRange = tuple[int, int]


def package_ranges_for_block(block_dir: Path) -> dict[int, PackageRange]:
    ranges: dict[int, PackageRange] = {}
    cursor = 1
    package_files: list[tuple[int, Path]] = []
    for path in block_dir.glob("*_P*.json"):
        match = PACKAGE_FILE_RE.search(path.name)
        if match:
            package_files.append((int(match.group(1)), path))
    for package_no, path in sorted(package_files):
        plan = read_json(path)
        hours = plan.get("lesson_hours")
        if not isinstance(hours, int) or isinstance(hours, bool) or hours <= 0:
            raise TeacherFacingTextError(f"LESSON_HOURS_INVALID:{path}")
        end = cursor + hours - 1
        ranges[package_no] = (cursor, end)
        cursor = end + 1
    return ranges


def teacher_lesson_hour_range(
    start: int,
    end: int,
    *,
    grammatical_case: str = "plain",
) -> str:
    singular = start == end
    prefix = f"{start}." if singular else f"{start}–{end}."
    forms = {
        "plain": "ders saati" if singular else "ders saatleri",
        "locative": "ders saatinde" if singular else "ders saatlerinde",
        "attributive": "ders saatindeki" if singular else "ders saatlerindeki",
        "ablative": "ders saatinden" if singular else "ders saatlerinden",
        "dative": "ders saatine" if singular else "ders saatlerine",
        "genitive": "ders saatinin" if singular else "ders saatlerinin",
        "accusative": "ders saatini" if singular else "ders saatlerini",
    }
    return f"{prefix} {forms[grammatical_case]}"


@dataclass(frozen=True)
class TeacherReferenceCatalog:
    course_label: str
    themes: dict[str, str]
    blocks: dict[str, str]
    package_refs: dict[str, str]
    activities: dict[str, str]
    activity_aliases: dict[str, str]
    forms: dict[str, str]
    form_aliases: dict[str, str]
    artifacts: dict[str, str]
    resources: dict[str, str]
    resource_aliases: dict[str, str]
    sections: dict[str, str]
    texts: dict[str, str]

    @classmethod
    def from_knowledge_root(cls, root: Path) -> "TeacherReferenceCatalog":
        root = root.resolve()
        textbook = read_json(root / "textbook_map.json")
        forms_index = read_json(root / "textbook_forms_index.json")
        teaching_blocks = read_json(root / "production/teaching_blocks.json")
        form_registry = _read_optional_json(
            root / "production/assessment_form_registry.json"
        )
        artifact_registry = _read_optional_json(
            root / "production/assessment_artifact_registry.json"
        )
        production_manifest = _read_optional_json(
            root / "production/production_manifest.json"
        )
        resource_plan = _read_optional_json(
            root / "production/consolidated_resource_plan.json"
        )

        grade = teaching_blocks.get("grade") or textbook.get("grade")
        course_title = (
            _string(teaching_blocks.get("course_title"))
            or _string(textbook.get("course_title"))
            or "Türk Dili ve Edebiyatı"
        )
        course_label = f"{grade}. sınıf {course_title}" if grade else course_title

        themes: dict[str, str] = {}
        activities: dict[str, str] = {}
        sections: dict[str, str] = {}
        texts: dict[str, str] = {}

        for theme in textbook.get("themes", []):
            if not isinstance(theme, dict):
                continue
            theme_id = _string(theme.get("theme_id"))
            theme_no = theme.get("theme_no")
            theme_title = _string(theme.get("theme_title"))
            if theme_id and theme_title:
                themes[theme_id] = _theme_label(theme_no, theme_title)

            for section in theme.get("sections", []):
                if not isinstance(section, dict):
                    continue
                section_id = _string(section.get("section_id"))
                section_title = _string(section.get("section_title"))
                if section_id and section_title:
                    sections[section_id] = _with_page(
                        section_title,
                        section.get("printed_page_range"),
                    )

                for text in section.get("main_texts", []):
                    if not isinstance(text, dict):
                        continue
                    text_id = _string(text.get("text_id"))
                    title = _string(text.get("title"))
                    author = _string(text.get("author"))
                    if text_id and title:
                        readable = f"{title} — {author}" if author else title
                        texts[text_id] = _with_page(
                            readable,
                            text.get("printed_page"),
                        )

                for activity in section.get("activities", []):
                    if not isinstance(activity, dict):
                        continue
                    activity_id = _string(activity.get("activity_id"))
                    title = (
                        _string(activity.get("exact_title"))
                        or _string(activity.get("activity_title"))
                        or _string(activity.get("title"))
                        or _string(activity.get("student_action"))
                    )
                    if activity_id and title:
                        activities[activity_id] = _with_page(
                            title,
                            activity.get("printed_page"),
                        )

        forms: dict[str, str] = {}
        for form in forms_index.get("forms", []):
            if not isinstance(form, dict):
                continue
            form_id = _string(form.get("form_id"))
            title = _string(form.get("title")) or _string(
                form.get("printed_title")
            )
            if form_id and title:
                forms[form_id] = _with_page(
                    title,
                    form.get("printed_page"),
                )

        for form in form_registry.get("forms", []):
            if not isinstance(form, dict):
                continue
            form_id = _string(form.get("form_id"))
            task_title = _string(form.get("task_title"))
            if not form_id or not task_title:
                continue
            forms.setdefault(
                form_id,
                _with_page(
                    f"{task_title} değerlendirme formu",
                    _registry_page(form.get("textbook_locator")),
                ),
            )

        blocks: dict[str, str] = {}
        for block in teaching_blocks.get("blocks", []):
            if not isinstance(block, dict):
                continue
            block_id = _string(block.get("block_id"))
            title = _string(block.get("title"))
            if block_id and title:
                blocks[block_id] = title

        artifacts: dict[str, str] = {}
        resources: dict[str, str] = {}
        for item in production_manifest.get("production_queue", []):
            if not isinstance(item, dict):
                continue
            artifact_id = _string(item.get("artifact_id"))
            title = _string(item.get("title"))
            if artifact_id and title:
                artifacts[artifact_id] = title
                for resource_id in item.get("resource_plan_ids", []):
                    if isinstance(resource_id, str):
                        resources[resource_id] = title

        for item in artifact_registry.get("annual_artifacts", []):
            if not isinstance(item, dict):
                continue
            artifact_id = _string(item.get("artifact_id"))
            title = _string(item.get("title"))
            if artifact_id and title:
                artifacts.setdefault(artifact_id, title)

        for item in resource_plan.get("resources", []):
            if not isinstance(item, dict):
                continue
            resource_id = _string(item.get("resource_id"))
            if resource_id:
                resources.setdefault(resource_id, _generic_resource_label(item))
            for alias in item.get("resource_plan_ids", []):
                if isinstance(alias, str) and alias:
                    resources.setdefault(alias, resources.get(resource_id, "ilgili öğretim materyali"))

        package_refs: dict[str, str] = {}
        generated = root / "generated/lesson_plans"
        if generated.exists():
            for block_dir in sorted(
                path for path in generated.glob("*/*") if path.is_dir()
            ):
                ranges = package_ranges_for_block(block_dir)
                block_id = block_dir.name
                block_label = blocks.get(block_id, "Ders planı bölümü")
                for package_no, (start, end) in ranges.items():
                    package_refs[f"{block_id}_P{package_no:02d}"] = (
                        f"{block_label} · "
                        f"{teacher_lesson_hour_range(start, end)}"
                    )

        return cls(
            course_label=course_label,
            themes=themes,
            blocks=blocks,
            package_refs=package_refs,
            activities=activities,
            activity_aliases=_unique_aliases(activities, ACTIVITY_SHORT_RE),
            forms=forms,
            form_aliases=_unique_aliases(forms, FORM_SHORT_RE),
            artifacts=artifacts,
            resources=resources,
            resource_aliases=_unique_aliases(resources, RESOURCE_SHORT_RE),
            sections=sections,
            texts=texts,
        )

    def replacements(self, plan: dict[str, Any]) -> dict[str, str]:
        result: dict[str, str] = {}
        course_id = _string(plan.get("course_id"))
        if course_id:
            result[course_id] = self.course_label
        result.update(self.package_refs)
        result.update(self.activities)
        result.update(self.activity_aliases)
        result.update(self.forms)
        result.update(self.form_aliases)
        result.update(self.artifacts)
        result.update(self.resources)
        result.update(self.resource_aliases)
        result.update(self.sections)
        result.update(self.texts)
        result.update(self.blocks)
        result.update(self.themes)
        return result


def _package_case_label(
    package_no: int,
    ranges: dict[int, PackageRange],
    grammatical_case: str,
) -> str | None:
    value = ranges.get(package_no)
    if value is None:
        return None
    return teacher_lesson_hour_range(
        value[0],
        value[1],
        grammatical_case=grammatical_case,
    )


def _range_case_label(
    match: re.Match[str],
    ranges: dict[int, PackageRange],
    grammatical_case: str,
) -> str | None:
    first = ranges.get(int(match.group(1)))
    last = ranges.get(int(match.group(2)))
    if first is None or last is None or first[0] > last[1]:
        return None
    return teacher_lesson_hour_range(
        first[0],
        last[1],
        grammatical_case=grammatical_case,
    )


def _apply_teacher_terms(value: str) -> str:
    for token, label in ENUM_LABELS.items():
        value = re.sub(rf"\b{re.escape(token)}\b", label, value)
    for pattern, replacement in TEACHER_TERM_REPLACEMENTS:
        value = pattern.sub(replacement, value)
    return DUPLICATE_PAGE_RE.sub(r"\1", value)


def humanize_teacher_text(
    text: str,
    *,
    plan: dict[str, Any],
    catalog: TeacherReferenceCatalog,
    package_ranges: dict[int, PackageRange],
) -> str:
    value = text
    replacements = catalog.replacements(plan)
    for key in sorted(replacements, key=len, reverse=True):
        value = value.replace(key, replacements[key])

    value = COURSE_ID_RE.sub(
        lambda match: f"{match.group(1)}. sınıf Türk Dili ve Edebiyatı",
        value,
    )

    range_cases: tuple[tuple[re.Pattern[str], str, str], ...] = (
        (PACKAGE_RANGE_ATTR_RE, "attributive", "ilgili ders planlarındaki"),
        (PACKAGE_RANGE_LOCATIVE_RE, "locative", "ilgili ders planlarında"),
        (PACKAGE_RANGE_ABLATIVE_RE, "ablative", "ilgili ders planlarından"),
        (PACKAGE_RANGE_DATIVE_RE, "dative", "ilgili ders planlarına"),
        (PACKAGE_RANGE_GENITIVE_RE, "genitive", "ilgili ders planlarının"),
        (PACKAGE_RANGE_ACCUSATIVE_RE, "accusative", "ilgili ders planlarını"),
        (PACKAGE_RANGE_RE, "genitive", "ilgili ders planlarının"),
    )
    for pattern, grammatical_case, fallback in range_cases:
        value = pattern.sub(
            lambda match, case=grammatical_case, default=fallback: (
                _range_case_label(match, package_ranges, case) or default
            ),
            value,
        )

    package_cases: tuple[tuple[re.Pattern[str], str, str], ...] = (
        (PACKAGE_ATTR_RE, "attributive", "ilgili ders planındaki"),
        (PACKAGE_LOCATIVE_RE, "locative", "ilgili ders planında"),
        (PACKAGE_ABLATIVE_RE, "ablative", "ilgili ders planından"),
        (PACKAGE_DATIVE_RE, "dative", "ilgili ders planına"),
        (PACKAGE_GENITIVE_RE, "genitive", "ilgili ders planının"),
        (PACKAGE_ACCUSATIVE_RE, "accusative", "ilgili ders planını"),
        (PACKAGE_RE, "plain", "ilgili ders planı"),
    )
    for pattern, grammatical_case, fallback in package_cases:
        value = pattern.sub(
            lambda match, case=grammatical_case, default=fallback: (
                _package_case_label(
                    int(match.group(1)),
                    package_ranges,
                    case,
                )
                or default
            ),
            value,
        )

    value = _apply_teacher_terms(value)
    unresolved = sorted(
        {match.group(0) for match in TECHNICAL_REFERENCE_RE.finditer(value)}
    )
    if unresolved:
        raise TeacherFacingTextError(
            f"UNRESOLVED_TEACHER_REFERENCES:{unresolved}"
        )
    return value


def _list_strings(value: Any) -> Iterable[tuple[int, str]]:
    if not isinstance(value, list):
        return []
    return [
        (index, item)
        for index, item in enumerate(value)
        if isinstance(item, str)
    ]


def iter_teacher_facing_strings(plan: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for key in ("plan_title", "plan_summary", "teacher_notes"):
        value = plan.get(key)
        if isinstance(value, str):
            yield key, value

    lessons = plan.get("lessons")
    if isinstance(lessons, list):
        for index, lesson in enumerate(lessons):
            if not isinstance(lesson, dict):
                continue
            for key in (
                "title",
                "objective",
                "opening",
                "assessment",
                "closure",
            ):
                value = lesson.get(key)
                if isinstance(value, str):
                    yield f"lessons[{index}].{key}", value
            for key in ("teacher_actions", "student_actions", "materials"):
                for item_index, value in _list_strings(lesson.get(key)):
                    yield f"lessons[{index}].{key}[{item_index}]", value

    continuation = plan.get("continuation_summary")
    if isinstance(continuation, dict) and isinstance(
        continuation.get("next_step_hint"), str
    ):
        yield (
            "continuation_summary.next_step_hint",
            continuation["next_step_hint"],
        )

    large_class = plan.get("large_class_route")
    if isinstance(large_class, dict):
        for key in (
            "activation_condition",
            "grouping_strategy",
            "teacher_rotation_strategy",
            "peer_observer_strategy",
            "evidence_equivalence",
        ):
            value = large_class.get(key)
            if isinstance(value, str):
                yield f"large_class_route.{key}", value
        extension = large_class.get("optional_school_based_extension")
        if isinstance(extension, dict) and isinstance(
            extension.get("purpose"), str
        ):
            yield (
                "large_class_route.optional_school_based_extension.purpose",
                extension["purpose"],
            )

    adaptations = plan.get("classroom_adaptations")
    if isinstance(adaptations, dict):
        stack: list[tuple[str, Any]] = [("classroom_adaptations", adaptations)]
        while stack:
            path, value = stack.pop()
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {"trigger_categories", "alternative_modes"}:
                        continue
                    stack.append((f"{path}.{key}", child))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    stack.append((f"{path}[{index}]", child))
            elif isinstance(value, str):
                yield path, value

    grounding = plan.get("grounded_references")
    if isinstance(grounding, dict):
        for group_name in (
            "form_refs",
            "assessment_artifact_refs",
            "resource_refs",
        ):
            group = grounding.get(group_name)
            if not isinstance(group, list):
                continue
            for index, item in enumerate(group):
                if isinstance(item, dict) and isinstance(item.get("usage"), str):
                    yield (
                        f"grounded_references.{group_name}[{index}].usage",
                        item["usage"],
                    )


def teacher_facing_validation_errors(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for path, text in iter_teacher_facing_strings(plan):
        for match in TECHNICAL_REFERENCE_RE.finditer(text):
            errors.append(
                f"TEACHER_PROSE_TECHNICAL_ID:{path}:{match.group(0)}"
            )
    return errors


def normalize_teacher_facing_text(
    plan: dict[str, Any],
    *,
    catalog: TeacherReferenceCatalog,
    package_ranges: dict[int, PackageRange],
) -> dict[str, Any]:
    result = copy.deepcopy(plan)

    def humanize(value: str) -> str:
        return humanize_teacher_text(
            value,
            plan=result,
            catalog=catalog,
            package_ranges=package_ranges,
        )

    for key in ("plan_title", "plan_summary", "teacher_notes"):
        if isinstance(result.get(key), str):
            result[key] = humanize(result[key])

    lessons = result.get("lessons")
    if isinstance(lessons, list):
        for lesson in lessons:
            if not isinstance(lesson, dict):
                continue
            for key in (
                "title",
                "objective",
                "opening",
                "assessment",
                "closure",
            ):
                if isinstance(lesson.get(key), str):
                    lesson[key] = humanize(lesson[key])
            for key in ("teacher_actions", "student_actions", "materials"):
                if isinstance(lesson.get(key), list):
                    lesson[key] = [
                        humanize(item) if isinstance(item, str) else item
                        for item in lesson[key]
                    ]

    continuation = result.get("continuation_summary")
    if isinstance(continuation, dict) and isinstance(
        continuation.get("next_step_hint"), str
    ):
        continuation["next_step_hint"] = humanize(
            continuation["next_step_hint"]
        )

    large_class = result.get("large_class_route")
    if isinstance(large_class, dict):
        for key in (
            "activation_condition",
            "grouping_strategy",
            "teacher_rotation_strategy",
            "peer_observer_strategy",
            "evidence_equivalence",
        ):
            if isinstance(large_class.get(key), str):
                large_class[key] = humanize(large_class[key])
        extension = large_class.get("optional_school_based_extension")
        if isinstance(extension, dict) and isinstance(
            extension.get("purpose"), str
        ):
            extension["purpose"] = humanize(extension["purpose"])

    adaptations = result.get("classroom_adaptations")
    if isinstance(adaptations, dict):
        def normalize_nested(value: Any, key: str | None = None) -> Any:
            if key in {"trigger_categories", "alternative_modes"}:
                return value
            if isinstance(value, dict):
                return {
                    child_key: normalize_nested(child, child_key)
                    for child_key, child in value.items()
                }
            if isinstance(value, list):
                return [normalize_nested(child) for child in value]
            if isinstance(value, str):
                return humanize(value)
            return value

        result["classroom_adaptations"] = normalize_nested(adaptations)

    grounding = result.get("grounded_references")
    if isinstance(grounding, dict):
        for group_name in (
            "form_refs",
            "assessment_artifact_refs",
            "resource_refs",
        ):
            group = grounding.get(group_name)
            if not isinstance(group, list):
                continue
            for item in group:
                if isinstance(item, dict) and isinstance(item.get("usage"), str):
                    item["usage"] = humanize(item["usage"])

    errors = teacher_facing_validation_errors(result)
    if errors:
        raise TeacherFacingTextError(";".join(errors))
    return result
