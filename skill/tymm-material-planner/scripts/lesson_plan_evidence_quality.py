#!/usr/bin/env python3
"""Turn vague prior-work references into concrete assessment evidence.

Canonical lesson-plan JSON remains unchanged. This module is used by teacher-facing
runtime/export projections and by the AI generator quality gate. Evidence labels
are derived only from earlier generated lesson plans in the same block.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Iterable

PACKAGE_FILE_RE = re.compile(r"_P(?P<package_no>\d{2})\.json$", re.IGNORECASE)
PACKAGE_EVIDENCE_RE = re.compile(
    r"\bP(?P<start>\d{1,2})\s*[-–—/]\s*P(?P<end>\d{1,2})\s+"
    r"(?:(?:öğrenci)\s+)?(?:(?:çalışma)\s+)?"
    r"ürün(?P<ending>leri(?:nden|ne|ni|yle)?)\b",
    re.IGNORECASE,
)
GENERIC_EVIDENCE_RE = re.compile(
    r"\b(?:"
    r"(?:önceki|daha\s+önceki|kendi)\s+(?:(?:öğrenci)\s+)?(?:(?:çalışma)\s+)?"
    r"|(?:öğrenci\s+)?çalışma\s+"
    r")ürün(?P<ending>leri(?:nden|ne|ni|yle)?)\b",
    re.IGNORECASE,
)

# Only prose that can reach a teacher is inspected by the generator gate.
TEACHER_TEXT_KEYS = {
    "plan_summary",
    "teacher_notes",
    "title",
    "objective",
    "opening",
    "teacher_actions",
    "student_actions",
    "assessment",
    "closure",
    "materials",
    "next_step_hint",
}

CONCRETE_EVIDENCE_TERMS = (
    "tablo",
    "şema",
    "harita",
    "kayıt",
    "cevap",
    "kontrol noktası",
    "kart",
    "tahmin",
    "dayanak",
    "işaret",
    "çözümleme",
    "karşılaştırma",
)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"LESSON_PLAN_JSON_OBJECT_REQUIRED:{path}")
    return value


def _package_no(path: Path) -> int:
    match = PACKAGE_FILE_RE.search(path.name)
    if match is None:
        raise ValueError(f"LESSON_PLAN_PACKAGE_FILENAME_INVALID:{path}")
    return int(match.group("package_no"))


def _first_sentence(text: str) -> str:
    # Do not treat page abbreviation "s." as sentence end.
    masked = re.sub(
        r"\bs\.\s*",
        lambda match: match.group(0).replace(".", "§"),
        text.strip(),
        flags=re.IGNORECASE,
    )
    sentence = re.split(r"(?<=[.!?])\s+", masked, maxsplit=1)[0]
    return sentence.replace("§", ".").strip()


def _clean_evidence_sentence(text: str) -> str:
    value = _first_sentence(text).rstrip(". ")
    value = re.sub(
        r"^(?:Ana ürün|Ana kanıt|Ana değerlendirme|Çıkış görevi)\s*:?\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )
    match = re.match(
        r"^Öğrencinin ürettiği\s+(.+?)\s+değerlendirilir$",
        value,
        flags=re.IGNORECASE,
    )
    if match:
        value = match.group(1)
    value = re.sub(
        r"(?:dır|dir|dur|dür|tır|tir|tur|tür)$",
        "",
        value,
        flags=re.IGNORECASE,
    )
    return value.strip(" ;,.-")


def _candidate_score(text: str, *, source: str) -> int:
    lowered = text.casefold()
    score = 0
    if lowered.startswith("ana ürün") or lowered.startswith("ana kanıt"):
        score += 100
    elif lowered.startswith("çıkış görevi"):
        score += 60
    if source == "assessment":
        score += 20
    score += 8 * sum(term in lowered for term in CONCRETE_EVIDENCE_TERMS)
    if "s." in lowered or "sayfa" in lowered:
        score += 5
    return score


def _lesson_evidence_label(lesson: dict[str, Any]) -> str | None:
    candidates: list[tuple[int, str]] = []
    assessment = lesson.get("assessment")
    if isinstance(assessment, str) and assessment.strip():
        candidates.append((_candidate_score(assessment, source="assessment"), assessment))
    for action in lesson.get("student_actions", []):
        if not isinstance(action, str) or not action.strip():
            continue
        if any(term in action.casefold() for term in CONCRETE_EVIDENCE_TERMS):
            candidates.append((_candidate_score(action, source="student_action"), action))
    if not candidates:
        title = lesson.get("title")
        if isinstance(title, str) and title.strip():
            return f"{title.strip()} kaydı"
        return None
    _score, chosen = max(candidates, key=lambda item: (item[0], len(item[1])))
    label = _clean_evidence_sentence(chosen)
    if not label:
        return None
    # If the chosen sentence is an action rather than a named artifact, retain
    # the lesson title so the evidence remains pedagogically identifiable.
    if chosen in lesson.get("student_actions", []):
        title = str(lesson.get("title") or "").strip()
        if title:
            return f"{title}: {label}"
    return label


def _best_package_evidence(
    plan: dict[str, Any],
    *,
    lesson_limit: int | None = None,
) -> str | None:
    lessons = plan.get("lessons")
    if not isinstance(lessons, list):
        return None
    allowed = lessons if lesson_limit is None else lessons[:lesson_limit]
    candidates: list[tuple[int, str]] = []
    for lesson in allowed:
        if not isinstance(lesson, dict):
            continue
        label = _lesson_evidence_label(lesson)
        if not label:
            continue
        assessment = str(lesson.get("assessment") or "")
        candidates.append((_candidate_score(assessment, source="assessment"), label))
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[0], len(item[1])))[1]


def _block_plans(block_dir: Path) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for path in sorted(block_dir.glob("*_P*.json")):
        try:
            number = _package_no(path)
        except ValueError:
            continue
        result[number] = _read_json(path)
    return result


def _evidence_labels(
    *,
    block_plans: dict[int, dict[str, Any]],
    start: int,
    end: int,
    current_package: int,
    current_lesson_no: int | None,
    max_items: int = 7,
) -> list[str]:
    if end < start:
        return []
    labels: list[str] = []
    for package_no in range(start, end + 1):
        if package_no > current_package:
            break
        plan = block_plans.get(package_no)
        if plan is None:
            continue
        lesson_limit: int | None = None
        if package_no == current_package:
            # Plan-level prose is evaluated before the current package; lesson
            # prose may use evidence from earlier lessons in the same package.
            lesson_limit = max((current_lesson_no or 1) - 1, 0)
            if lesson_limit == 0:
                continue
        label = _best_package_evidence(plan, lesson_limit=lesson_limit)
        if label and label not in labels:
            labels.append(label)
    return labels[-max_items:]


def _case_phrase(labels: list[str], ending: str) -> str:
    joined = "; ".join(labels)
    suffix = ending.casefold()
    if suffix == "lerinden":
        base = "önceki derslerdeki somut ölçme kanıtlarından"
    elif suffix == "lerine":
        base = "önceki derslerdeki somut ölçme kanıtlarına"
    elif suffix == "lerini":
        base = "önceki derslerdeki somut ölçme kanıtlarını"
    elif suffix == "leriyle":
        base = "önceki derslerdeki somut ölçme kanıtlarıyla"
    else:
        base = "önceki derslerdeki somut ölçme kanıtları"
    return f"{base} ({joined})" if joined else base


def _expand_inline(
    text: str,
    *,
    block_plans: dict[int, dict[str, Any]],
    current_package: int,
    current_lesson_no: int | None,
) -> str:
    def range_replacement(match: re.Match[str]) -> str:
        labels = _evidence_labels(
            block_plans=block_plans,
            start=int(match.group("start")),
            end=int(match.group("end")),
            current_package=current_package,
            current_lesson_no=current_lesson_no,
        )
        return _case_phrase(labels, match.group("ending"))

    value = PACKAGE_EVIDENCE_RE.sub(range_replacement, text)

    def generic_replacement(match: re.Match[str]) -> str:
        labels = _evidence_labels(
            block_plans=block_plans,
            start=1,
            end=current_package,
            current_package=current_package,
            current_lesson_no=current_lesson_no,
            max_items=5,
        )
        return _case_phrase(labels, match.group("ending"))

    return GENERIC_EVIDENCE_RE.sub(generic_replacement, value)


def _expand_materials(
    materials: list[Any],
    *,
    block_plans: dict[int, dict[str, Any]],
    current_package: int,
    current_lesson_no: int,
) -> list[Any]:
    result: list[Any] = []
    for item in materials:
        if not isinstance(item, str):
            result.append(item)
            continue
        match = PACKAGE_EVIDENCE_RE.search(item)
        if match and match.group("ending").casefold() == "leri":
            labels = _evidence_labels(
                block_plans=block_plans,
                start=int(match.group("start")),
                end=int(match.group("end")),
                current_package=current_package,
                current_lesson_no=current_lesson_no,
            )
            prefix = item[: match.start()].strip(" ,;:-")
            prefix = re.sub(r"\s+(?:ve|ile)$", "", prefix, flags=re.IGNORECASE).strip()
            suffix = item[match.end() :].strip(" ,;:-")
            for value in ([prefix] if prefix else []) + labels + ([suffix] if suffix else []):
                if value and value not in result:
                    result.append(value)
            continue
        value = _expand_inline(
            item,
            block_plans=block_plans,
            current_package=current_package,
            current_lesson_no=current_lesson_no,
        )
        if value not in result:
            result.append(value)
    return result


def project_specific_assessment_evidence(
    plan: dict[str, Any],
    *,
    plan_path: Path,
) -> dict[str, Any]:
    """Return a source-bound projection with vague prior products made specific."""
    result = copy.deepcopy(plan)
    current_package = _package_no(plan_path)
    plans = _block_plans(plan_path.parent)

    for key in ("plan_summary", "teacher_notes"):
        value = result.get(key)
        if isinstance(value, str):
            result[key] = _expand_inline(
                value,
                block_plans=plans,
                current_package=current_package,
                current_lesson_no=None,
            )

    lessons = result.get("lessons")
    if isinstance(lessons, list):
        for index, lesson in enumerate(lessons, 1):
            if not isinstance(lesson, dict):
                continue
            for key in ("title", "objective", "opening", "assessment", "closure"):
                value = lesson.get(key)
                if isinstance(value, str):
                    lesson[key] = _expand_inline(
                        value,
                        block_plans=plans,
                        current_package=current_package,
                        current_lesson_no=index,
                    )
            for key in ("teacher_actions", "student_actions"):
                values = lesson.get(key)
                if isinstance(values, list):
                    lesson[key] = [
                        _expand_inline(
                            value,
                            block_plans=plans,
                            current_package=current_package,
                            current_lesson_no=index,
                        )
                        if isinstance(value, str)
                        else value
                        for value in values
                    ]
            materials = lesson.get("materials")
            if isinstance(materials, list):
                lesson["materials"] = _expand_materials(
                    materials,
                    block_plans=plans,
                    current_package=current_package,
                    current_lesson_no=index,
                )

    continuation = result.get("continuation_summary")
    if isinstance(continuation, dict) and isinstance(continuation.get("next_step_hint"), str):
        continuation["next_step_hint"] = _expand_inline(
            continuation["next_step_hint"],
            block_plans=plans,
            current_package=current_package,
            current_lesson_no=None,
        )
    return result


def iter_teacher_strings(plan: dict[str, Any]) -> Iterable[tuple[str, str]]:
    def walk(value: Any, path: str = "", key: str | None = None) -> Iterable[tuple[str, str]]:
        if isinstance(value, dict):
            for child_key, child in value.items():
                child_path = f"{path}.{child_key}" if path else child_key
                yield from walk(child, child_path, child_key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from walk(child, f"{path}[{index}]", key)
        elif isinstance(value, str) and key in TEACHER_TEXT_KEYS:
            yield path, value

    yield from walk(plan)


def vague_evidence_errors(plan: dict[str, Any]) -> list[str]:
    """Reject generic prior-product prose in newly generated teacher plans."""
    errors: list[str] = []
    for path, text in iter_teacher_strings(plan):
        match = PACKAGE_EVIDENCE_RE.search(text) or GENERIC_EVIDENCE_RE.search(text)
        if match:
            errors.append(f"VAGUE_PRIOR_EVIDENCE:{path}:{match.group(0)}")
    return errors
