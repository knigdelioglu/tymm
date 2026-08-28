#!/usr/bin/env python3
"""Turn vague prior-work references into concrete assessment evidence.

Canonical lesson-plan JSON remains unchanged. This module is used by teacher-facing
runtime/export projections and by the AI generator quality gate. Evidence labels
are derived from source-bound lesson plans rather than invented by the projection.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Iterable

PACKAGE_FILE_RE = re.compile(r"_P(?P<package_no>\d{2})\.json$", re.IGNORECASE)

# Turkish inflections seen around "ürün" in teacher prose. The stem is kept
# outside the group so evidence-phrase helpers can preserve grammatical case.
EVIDENCE_ENDING = (
    r"(?P<ending>"
    r"lerinden|lerine|lerini|leriyle|lerin|lerde|lerden|lere|leri|lerle|ler|"
    r"ünden|üne|ünü|üyle|ün|ünde|ü|den|de|e|le"
    r")?"
)

# Package ranges sometimes contain a short human descriptor before "ürünleri",
# e.g. "P05-P07 anı tahlil ürünleri". Consume that descriptor together with the
# implementation range so it never leaks into teacher-facing prose.
PACKAGE_EVIDENCE_RE = re.compile(
    r"\bP(?P<start>\d{1,2})\s*[-–—/]\s*P(?P<end>\d{1,2})\s+"
    r"(?:(?:[\wÇĞİÖŞÜçğıöşü'’.-]+)\s+){0,4}"
    r"ürün" + EVIDENCE_ENDING + r"\b",
    re.IGNORECASE,
)
GENERIC_PRIOR_EVIDENCE_RE = re.compile(
    r"\b(?:önceki|daha\s+önceki|kendi)\s+"
    r"(?:(?:ders(?:ler)?(?:deki|in)?|öğrenci|metin|metinler|hikâye|anı|şiir|deneme)\s+)*"
    r"(?:(?:ve|ile)\s+)?"
    r"(?:(?:çalışma)\s+)?"
    r"ürün" + EVIDENCE_ENDING + r"\b",
    re.IGNORECASE,
)
# A bare "çalışma ürünü" is still too vague for a serious teacher plan. In a
# lesson context it resolves to that lesson's named assessment evidence; outside
# a lesson context it resolves to prior source-bound evidence or fails closed.
BARE_EVIDENCE_RE = re.compile(
    r"\b(?:öğrenci\s+)?çalışma\s+ürün" + EVIDENCE_ENDING + r"\b",
    re.IGNORECASE,
)

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


class EvidenceResolutionError(ValueError):
    """Raised when vague teacher prose cannot be resolved from source evidence."""


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvidenceResolutionError(f"LESSON_PLAN_JSON_OBJECT_REQUIRED:{path}")
    return value


def _package_no(path: Path) -> int:
    match = PACKAGE_FILE_RE.search(path.name)
    if match is None:
        raise EvidenceResolutionError(f"LESSON_PLAN_PACKAGE_FILENAME_INVALID:{path}")
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


def _contains_vague_evidence(text: str) -> bool:
    return bool(
        PACKAGE_EVIDENCE_RE.search(text)
        or GENERIC_PRIOR_EVIDENCE_RE.search(text)
        or BARE_EVIDENCE_RE.search(text)
    )


def _lesson_evidence_candidate(lesson: dict[str, Any]) -> tuple[int, str] | None:
    candidates: list[tuple[int, str, str]] = []
    assessment = lesson.get("assessment")
    if isinstance(assessment, str) and assessment.strip():
        # A later explanatory sentence may mention "previous products" even
        # when the first sentence already names the real assessment artifact.
        # Score the first concrete sentence instead of discarding the whole field.
        assessment_sentence = _first_sentence(assessment)
        if assessment_sentence and not _contains_vague_evidence(assessment_sentence):
            candidates.append(
                (
                    _candidate_score(assessment_sentence, source="assessment"),
                    assessment_sentence,
                    "assessment",
                )
            )
    for action in lesson.get("student_actions", []):
        if not isinstance(action, str) or not action.strip():
            continue
        if _contains_vague_evidence(action):
            continue
        if any(term in action.casefold() for term in CONCRETE_EVIDENCE_TERMS):
            candidates.append(
                (_candidate_score(action, source="student_action"), action, "student_action")
            )
    if not candidates:
        title = lesson.get("title")
        if isinstance(title, str) and title.strip():
            return 0, f"{title.strip()} kaydı"
        return None

    score, chosen, source = max(candidates, key=lambda item: (item[0], len(item[1])))
    label = _clean_evidence_sentence(chosen)
    if not label:
        return None
    if source == "student_action":
        title = str(lesson.get("title") or "").strip()
        if title:
            label = f"{title}: {label}"
    return score, label


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
        candidate = _lesson_evidence_candidate(lesson)
        if candidate is not None:
            candidates.append(candidate)
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[0], len(item[1])))[1]


def _block_plans(block_dir: Path) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for path in sorted(block_dir.glob("*_P*.json")):
        try:
            number = _package_no(path)
        except EvidenceResolutionError:
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
    """Evidence that is already available before the current lesson."""
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
            lesson_limit = max((current_lesson_no or 1) - 1, 0)
            if lesson_limit == 0:
                continue
        label = _best_package_evidence(plan, lesson_limit=lesson_limit)
        if label and label not in labels:
            labels.append(label)
    return labels[-max_items:]


def _referenced_range_labels(
    *,
    block_plans: dict[int, dict[str, Any]],
    start: int,
    end: int,
    current_package: int,
    current_lesson_no: int | None,
    max_items: int = 7,
) -> list[str]:
    """Resolve an explicit package range, including source-bound future plans."""
    if end < start:
        return []
    labels: list[str] = []
    for package_no in range(start, end + 1):
        plan = block_plans.get(package_no)
        if plan is None:
            continue
        lesson_limit: int | None = None
        if package_no == current_package and current_lesson_no is not None:
            # For the current package, do not expose a not-yet-produced lesson
            # as completed evidence. Future packages, however, are canonical
            # planned evidence and may be described as such.
            lesson_limit = max(current_lesson_no - 1, 0)
            if lesson_limit == 0:
                continue
        label = _best_package_evidence(plan, lesson_limit=lesson_limit)
        if label and label not in labels:
            labels.append(label)
    return labels[-max_items:]


def _scope_for_range(start: int, end: int, current_package: int) -> str:
    if end < current_package:
        return "prior"
    if start > current_package:
        return "future"
    return "referenced"


def _evidence_phrase(
    labels: list[str],
    ending: str | None,
    *,
    source_ref: str,
    scope: str = "prior",
) -> str:
    if not labels:
        raise EvidenceResolutionError(
            f"SPECIFIC_ASSESSMENT_EVIDENCE_NOT_FOUND:{source_ref}"
        )
    joined = "; ".join(labels)
    suffix = (ending or "").casefold()

    if scope == "future":
        forms = {
            "ablative": "sonraki dersler için planlanan somut ölçme kanıtlarından",
            "dative": "sonraki dersler için planlanan somut ölçme kanıtlarına",
            "accusative": "sonraki dersler için planlanan somut ölçme kanıtlarını",
            "instrumental": "sonraki dersler için planlanan somut ölçme kanıtlarıyla",
            "genitive": "sonraki dersler için planlanan somut ölçme kanıtlarının",
            "locative": "sonraki dersler için planlanan somut ölçme kanıtlarında",
            "nominative": "sonraki dersler için planlanan somut ölçme kanıtları",
        }
    elif scope == "referenced":
        forms = {
            "ablative": "ilgili derslerdeki somut ölçme kanıtlarından",
            "dative": "ilgili derslerdeki somut ölçme kanıtlarına",
            "accusative": "ilgili derslerdeki somut ölçme kanıtlarını",
            "instrumental": "ilgili derslerdeki somut ölçme kanıtlarıyla",
            "genitive": "ilgili derslerdeki somut ölçme kanıtlarının",
            "locative": "ilgili derslerdeki somut ölçme kanıtlarında",
            "nominative": "ilgili derslerdeki somut ölçme kanıtları",
        }
    else:
        forms = {
            "ablative": "önceki derslerdeki somut ölçme kanıtlarından",
            "dative": "önceki derslerdeki somut ölçme kanıtlarına",
            "accusative": "önceki derslerdeki somut ölçme kanıtlarını",
            "instrumental": "önceki derslerdeki somut ölçme kanıtlarıyla",
            "genitive": "önceki derslerdeki somut ölçme kanıtlarının",
            "locative": "önceki derslerdeki somut ölçme kanıtlarında",
            "nominative": "önceki derslerdeki somut ölçme kanıtları",
        }

    if suffix in {"lerinden", "lerden", "ünden", "den"}:
        base = forms["ablative"]
    elif suffix in {"lerine", "lere", "üne", "e"}:
        base = forms["dative"]
    elif suffix in {"lerini", "ünü", "ü"}:
        base = forms["accusative"]
    elif suffix in {"leriyle", "lerle", "üyle", "le"}:
        base = forms["instrumental"]
    elif suffix in {"lerin", "ün"}:
        base = forms["genitive"]
    elif suffix in {"lerde", "ünde", "de"}:
        base = forms["locative"]
    else:
        base = forms["nominative"]
    return f"{base} ({joined})"


def _current_evidence_phrase(label: str | None, ending: str | None, *, source_ref: str) -> str:
    if not label:
        raise EvidenceResolutionError(
            f"SPECIFIC_CURRENT_ASSESSMENT_EVIDENCE_NOT_FOUND:{source_ref}"
        )
    suffix = (ending or "").casefold()
    if suffix in {"lerinden", "lerden", "ünden", "den"}:
        base = "bu dersteki somut ölçme kanıtından"
    elif suffix in {"lerine", "lere", "üne", "e"}:
        base = "bu dersteki somut ölçme kanıtına"
    elif suffix in {"lerini", "ünü", "ü"}:
        base = "bu dersteki somut ölçme kanıtını"
    elif suffix in {"leriyle", "lerle", "üyle", "le"}:
        base = "bu dersteki somut ölçme kanıtıyla"
    elif suffix in {"lerin", "ün"}:
        base = "bu dersteki somut ölçme kanıtının"
    elif suffix in {"lerde", "ünde", "de"}:
        base = "bu dersteki somut ölçme kanıtında"
    else:
        base = "bu dersteki somut ölçme kanıtı"
    return f"{base} ({label})"


def _expand_inline(
    text: str,
    *,
    block_plans: dict[int, dict[str, Any]],
    current_package: int,
    current_lesson_no: int | None,
    current_lesson: dict[str, Any] | None = None,
) -> str:
    def range_replacement(match: re.Match[str]) -> str:
        start = int(match.group("start"))
        end = int(match.group("end"))
        labels = _referenced_range_labels(
            block_plans=block_plans,
            start=start,
            end=end,
            current_package=current_package,
            current_lesson_no=current_lesson_no,
        )
        return _evidence_phrase(
            labels,
            match.group("ending"),
            source_ref=f"P{start:02d}-P{end:02d}@P{current_package:02d}",
            scope=_scope_for_range(start, end, current_package),
        )

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
        return _evidence_phrase(
            labels,
            match.group("ending"),
            source_ref=f"PRIOR@P{current_package:02d}",
        )

    value = GENERIC_PRIOR_EVIDENCE_RE.sub(generic_replacement, value)

    def bare_replacement(match: re.Match[str]) -> str:
        if current_lesson is not None:
            candidate = _lesson_evidence_candidate(current_lesson)
            label = candidate[1] if candidate is not None else None
            return _current_evidence_phrase(
                label,
                match.group("ending"),
                source_ref=f"CURRENT@P{current_package:02d}:L{current_lesson_no or 0}",
            )
        labels = _evidence_labels(
            block_plans=block_plans,
            start=1,
            end=current_package,
            current_package=current_package,
            current_lesson_no=current_lesson_no,
            max_items=5,
        )
        return _evidence_phrase(
            labels,
            match.group("ending"),
            source_ref=f"BARE@P{current_package:02d}",
        )

    return BARE_EVIDENCE_RE.sub(bare_replacement, value)


def _expand_materials(
    materials: list[Any],
    *,
    block_plans: dict[int, dict[str, Any]],
    current_package: int,
    current_lesson_no: int,
    current_lesson: dict[str, Any],
) -> list[Any]:
    result: list[Any] = []
    for item in materials:
        if not isinstance(item, str):
            result.append(item)
            continue
        match = PACKAGE_EVIDENCE_RE.search(item)
        if match and (match.group("ending") or "").casefold() in {"", "ler", "leri"}:
            start = int(match.group("start"))
            end = int(match.group("end"))
            labels = _referenced_range_labels(
                block_plans=block_plans,
                start=start,
                end=end,
                current_package=current_package,
                current_lesson_no=current_lesson_no,
            )
            if not labels:
                raise EvidenceResolutionError(
                    f"SPECIFIC_ASSESSMENT_EVIDENCE_NOT_FOUND:P{start:02d}-P{end:02d}@P{current_package:02d}"
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
            current_lesson=current_lesson,
        )
        if value not in result:
            result.append(value)
    return result


def project_specific_assessment_evidence(
    plan: dict[str, Any],
    *,
    plan_path: Path,
) -> dict[str, Any]:
    """Return a source-bound projection with vague product prose made specific."""
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
                        current_lesson=lesson,
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
                            current_lesson=lesson,
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
                    current_lesson=lesson,
                )

    continuation = result.get("continuation_summary")
    if isinstance(continuation, dict) and isinstance(continuation.get("next_step_hint"), str):
        continuation["next_step_hint"] = _expand_inline(
            continuation["next_step_hint"],
            block_plans=plans,
            current_package=current_package,
            current_lesson_no=None,
        )

    unresolved = vague_evidence_errors(result)
    if unresolved:
        raise EvidenceResolutionError(
            "UNRESOLVED_VAGUE_PRIOR_EVIDENCE:" + ";".join(unresolved[:10])
        )
    return result


def iter_teacher_strings(plan: dict[str, Any]) -> Iterable[tuple[str, str]]:
    # The detector is deliberately broader than the projection mutator. If a
    # newly added teacher-facing field contains vague evidence prose, validation
    # must fail rather than silently letting it through.
    def walk(value: Any, path: str = "") -> Iterable[tuple[str, str]]:
        if isinstance(value, dict):
            for child_key, child in value.items():
                child_path = f"{path}.{child_key}" if path else child_key
                yield from walk(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from walk(child, f"{path}[{index}]")
        elif isinstance(value, str):
            yield path, value

    yield from walk(plan)


def vague_evidence_errors(plan: dict[str, Any]) -> list[str]:
    """Reject generic product prose when an actual evidence name is required."""
    errors: list[str] = []
    for path, text in iter_teacher_strings(plan):
        match = (
            PACKAGE_EVIDENCE_RE.search(text)
            or GENERIC_PRIOR_EVIDENCE_RE.search(text)
            or BARE_EVIDENCE_RE.search(text)
        )
        if match:
            errors.append(f"VAGUE_PRIOR_EVIDENCE:{path}:{match.group(0)}")
    return errors
