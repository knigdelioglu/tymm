#!/usr/bin/env python3
"""Validate the V3 textbook-to-teacher-guide chain for TDE 11.

The gate is intentionally deterministic.  It validates source identity,
mirror-to-task parity, prompt and answer projection, page/locator integrity,
field provenance, explanation quality, misconception interventions, duplicate
prevention, repetition guards, and rendered Markdown determinism.  A bounded
source review (for example a QR-only rubric or an external video) is reported
as PASS_WITH_REVIEW in ``release`` mode; ``strict-review`` turns that state into
a failure without silently filling the missing content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_teacher_guide_v3 as builder


TEXTBOOK_SOURCE_ID = builder.TEXTBOOK_SOURCE_ID
TEXTBOOK_MAP_SOURCE_ID = builder.TEXTBOOK_MAP_SOURCE_ID
CANONICAL_SOURCE_ID = builder.CANONICAL_SOURCE_ID
QUESTION_TYPES = {"QUESTION"}
EXPLANATION_TYPES = {"QUESTION", "ASSESSMENT", "PERFORMANCE_TASK"}
BACKGROUND_TYPES = {"QUESTION", "ASSESSMENT", "PERFORMANCE_TASK", "VOCABULARY", "TABLE", "COMPARISON", "REFERENCE"}
MOVE_TYPES = {"QUESTION", "ASSESSMENT", "PERFORMANCE_TASK", "PROCESS", "ACTIVITY", "TABLE", "COMPARISON", "VOCABULARY"}
LOOK_FOR_TYPES = {"QUESTION", "ASSESSMENT", "PERFORMANCE_TASK", "PROCESS", "ACTIVITY"}
PEDAGOGICAL_FIELDS = {
    "answer_explanation",
    "why_it_matters",
    "teacher_background",
    "student_explanation",
    "teacher_moves",
    "follow_up_questions",
    "common_misconceptions",
    "misconception_interventions",
    "assessment_look_fors",
    "support",
    "enrichment",
    "board_notes",
}
REASONING_CUES = [
    "çünkü",
    "bu nedenle",
    "ancak",
    "ölçüt",
    "kanıt",
    "bağlam",
    "öğrenci",
    "işlev",
    "dayanak",
    "kaynak",
    "gerekçe",
]
INTERVENTION_ACTIONS = [
    # Turkish inflectional stems are intentional: generated guidance may say
    # "işaretletin", "açıklattırın" or "sordurun".
    "iste",
    "sordur",
    "yaz",
    "işaret",
    "karşılaştır",
    "ayır",
    "göster",
    "sorgulat",
    "oynat",
    "kurdur",
    "etiket",
    "seç",
    "dönüştür",
    "açıklat",
    "uygulat",
    "taşı",
    "oluştur",
    "doldur",
    "sınıflandır",
    "sınırla",
    "tartış",
    "belirle",
    "eklet",
    "üret",
    "taslak",
    "çiz",
    "böldür",
    "tamamla",
    "sorgula",
    "isteyin",
    "istetin",
    "yazdır",
    "işaretlet",
    "karşılaştır",
    "ayır",
    "göster",
    "sorgulat",
    "oynat",
    "kurdur",
    "etiketlet",
    "seçtir",
    "dönüştür",
    "yeniden yaz",
]
INTERVENTION_CONCEPTS = [
    # Concept stems keep this deterministic while accepting normal Turkish
    # suffixes and domain vocabulary.
    "kanıt",
    "bağlam",
    "davranış",
    "anlam",
    "işlev",
    "amaç",
    "karakter",
    "ileti",
    "kaynak",
    "dil",
    "tür",
    "gerekçe",
    "özne",
    "eyleyen",
    "metin",
    "söz",
    "sahne",
    "bölüm",
    "kişi",
    "gelenek",
    "yazıt",
    "tarih",
    "hitap",
    "alıcı",
    "gönderici",
    "iletişim",
    "mesaj",
    "tema",
    "konu",
    "kurmaca",
    "olgu",
    "değerlendirme",
    "üslup",
    "sözlük",
    "saz",
    "dize",
    "karşılık",
    "anlatıcı",
    "zaman",
    "olay",
    "gözlem",
    "yorum",
    "varsayım",
    "soru",
]
LOCATOR_ONLY_RE = re.compile(r"^(?:basılı|pdf|ders kitabı|kitap)\s+s?\.?\s*\d", re.IGNORECASE)
PRINTED_LOCATOR_RE = re.compile(r"basılı\s+s\.?\s*(\d+)(?:\s*[-–—]\s*(\d+))?", re.IGNORECASE)
PDF_LOCATOR_RE = re.compile(r"pdf\s+s\.?\s*(\d+)(?:\s*[-–—]\s*(\d+))?", re.IGNORECASE)
SCHEMA_VALIDATOR_AVAILABLE: bool | None = None


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_tokens(value: Any) -> list[str]:
    text = builder.normalize_text(value)
    return re.findall(r"[a-zçğıöşü0-9]+", text)


def answer_paraphrase_guard(answer: Any, explanation: str) -> bool:
    """Return True when explanation is effectively only the answer repeated."""
    answer_tokens = normalize_tokens(builder.expected_answer_text(answer))
    explanation_tokens = normalize_tokens(explanation)
    if len(answer_tokens) <= 2 or len(explanation_tokens) <= 2:
        return False
    answer_set = set(answer_tokens)
    explanation_set = set(explanation_tokens)
    jaccard = len(answer_set & explanation_set) / max(1, len(answer_set | explanation_set))
    exact = " ".join(answer_tokens) == " ".join(explanation_tokens)
    return exact or (jaccard >= 0.82 and len(explanation_tokens) <= int(len(answer_tokens) * 1.6))


def token_similarity(left: Any, right: Any) -> float:
    left_set = set(normalize_tokens(left))
    right_set = set(normalize_tokens(right))
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def parse_page_range(value: str) -> tuple[int, int]:
    return builder.parse_page_range(value)


def locator_range(value: str, pattern: re.Pattern[str]) -> tuple[int, int] | None:
    match = pattern.search(value)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2) or match.group(1))


def ranges_overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return max(left[0], right[0]) <= min(left[1], right[1])


def nonempty(value: Any) -> bool:
    return builder.nonempty(value)


def unique_list(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def schema_errors(document: Any, schema_path: Path) -> list[str]:
    global SCHEMA_VALIDATOR_AVAILABLE
    try:
        import jsonschema
    except ImportError:
        # CI installs the pinned dependency. Local validation remains useful
        # without it; the report records a warning instead of misclassifying
        # every valid document as a content failure.
        SCHEMA_VALIDATOR_AVAILABLE = False
        return []
    SCHEMA_VALIDATOR_AVAILABLE = True
    schema = read_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        path = ".".join(str(part) for part in error.path) or "$"
        errors.append(f"{path}: {error.message}")
    return errors


def mirror_question_records(root: Path, theme_id: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    theme_dir = root / "courses" / builder.COURSE_ID / "teacher_guide" / theme_id
    primary = theme_dir / "book_mirror_v23.json"
    mirror = builder.merge_mirrors(builder.discover_mirror_paths(primary))
    records: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for entry in mirror["entries"]:
        for expanded in builder.expand_mirror_entry(entry):
            if expanded.get("presentation_type") != "QUESTION":
                continue
            task_id = f"{theme_id}::{expanded['mirror_id']}"
            if task_id in records:
                duplicates.append(task_id)
            records[task_id] = expanded
    return records, duplicates


def expected_activity_refs(
    entry: dict[str, Any],
    canonical: dict[str, dict[str, Any]],
    canonical_sections: dict[str, dict[str, Any]],
    manifest_row: dict[str, Any],
) -> list[str]:
    records = [canonical[ref] for ref in entry.get("canonical_item_refs", []) if ref in canonical]
    unit = records[0].get("unit") if records else None
    refs = list(unit.get("activity_refs", [])) if unit else []
    if not refs:
        refs = list(canonical_sections[entry["section_id"]]["content"].get("activity_refs", []))
    if not refs:
        refs = list(manifest_row.get("activity_refs", []))
    return unique_list(str(ref) for ref in refs)


def expected_outcome_refs(
    entry: dict[str, Any],
    canonical: dict[str, dict[str, Any]],
    canonical_sections: dict[str, dict[str, Any]],
    manifest_row: dict[str, Any],
) -> list[str]:
    records = [canonical[ref] for ref in entry.get("canonical_item_refs", []) if ref in canonical]
    unit = records[0].get("unit") if records else None
    refs = list(unit.get("outcome_refs", [])) if unit else []
    if not refs:
        refs = list(canonical_sections[entry["section_id"]]["content"].get("outcome_refs", []))
    if not refs:
        refs = list(manifest_row.get("outcome_refs", []))
    return unique_list(str(ref) for ref in refs)


def needs_background(task: dict[str, Any]) -> bool:
    return task.get("task_type") in BACKGROUND_TYPES or nonempty(task.get("expected_answer"))


def needs_explanation(task: dict[str, Any]) -> bool:
    return task.get("task_type") in EXPLANATION_TYPES or nonempty(task.get("expected_answer"))


def validate_task_fields(
    task: dict[str, Any],
    theme_id: str,
    failures: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> None:
    task_id = task.get("task_id", "<unknown>")

    def fail(code: str, message: str) -> None:
        failures.append({"code": code, "theme_id": theme_id, "task_id": task_id, "message": message})

    def warn(code: str, message: str) -> None:
        warnings.append({"code": code, "theme_id": theme_id, "task_id": task_id, "message": message})

    explanation = task.get("answer_explanation", "")
    if needs_explanation(task):
        if not isinstance(explanation, str) or len(explanation.strip()) < 40:
            fail("EXPLANATION_MISSING", "cevap veya görev için 40 karakterden uzun answer_explanation gerekli")
        else:
            if nonempty(task.get("expected_answer")) and answer_paraphrase_guard(task.get("expected_answer"), explanation):
                fail("EXPLANATION_PARAPHRASES_ANSWER", "answer_explanation yalnız expected_answer'ın tekrarı/parafrazı")
            if not any(cue in builder.normalize_text(explanation) for cue in REASONING_CUES):
                fail("EXPLANATION_NO_REASONING", "answer_explanation kaynak, gerekçe veya ölçüt açıklamıyor")

    if needs_background(task):
        background = task.get("teacher_background")
        if not isinstance(background, str) or len(background.strip()) < 60:
            fail("TEACHER_BACKGROUND_MISSING", "kavramsal görev için anlamlı teacher_background gerekli")
        elif nonempty(task.get("expected_answer")):
            if builder.normalize_text(background) == builder.normalize_text(builder.expected_answer_text(task["expected_answer"])):
                fail("TEACHER_BACKGROUND_IS_ANSWER", "teacher_background expected_answer'ı tekrar ediyor")
            if not any(term in builder.normalize_text(background) for term in ["metin", "dil", "iletişim", "tiyatro", "kültür", "anlatıcı", "belgesel", "mektup", "yaz", "kurmaca", "tür", "görev", "ses"]):
                fail("TEACHER_BACKGROUND_NOT_DOMAIN_SPECIFIC", "teacher_background alan bilgisi göstergesi içermiyor")

    if task.get("task_type") in EXPLANATION_TYPES or nonempty(task.get("expected_answer")):
        student_explanation = task.get("student_explanation")
        if not isinstance(student_explanation, str) or len(student_explanation.strip()) < 20:
            fail("STUDENT_EXPLANATION_MISSING", "öğrenciye verilecek mini açıklama eksik")

    if task.get("task_type") in MOVE_TYPES or nonempty(task.get("expected_answer")):
        if not isinstance(task.get("teacher_moves"), list) or not task["teacher_moves"]:
            fail("TEACHER_MOVES_MISSING", "göreve özgü teacher_moves eksik")

    if task.get("task_type") in EXPLANATION_TYPES:
        if not isinstance(task.get("follow_up_questions"), list) or not task["follow_up_questions"]:
            fail("FOLLOW_UP_MISSING", "soru/performans görevinde göreve özgü takip sorusu eksik")

    if task.get("task_type") in EXPLANATION_TYPES or task.get("task_type") in {"VOCABULARY", "TABLE", "COMPARISON"} or nonempty(task.get("expected_answer")):
        misconceptions = task.get("common_misconceptions", [])
        interventions = task.get("misconception_interventions", [])
        if misconceptions and (not isinstance(interventions, list) or not interventions):
            fail("MISCONCEPTION_INTERVENTION_MISSING", "common_misconceptions için misconception_interventions gerekli")
        for intervention in interventions or []:
            normalized = builder.normalize_text(intervention)
            if re.fullmatch(r"(?:öğrenciye\s+)?(?:tekrar|yeniden)\s+sor(?:un|un)?[.!]?", normalized) or "cevabı söyle" in normalized:
                fail("GENERIC_MISCONCEPTION_INTERVENTION", "müdahale yalnız tekrar sorma/cevabı söyleme biçiminde")
            if not any(action in normalized for action in INTERVENTION_ACTIONS):
                fail("MISCONCEPTION_INTERVENTION_NO_ACTION", "müdahale uygulanabilir bir öğretmen eylemi içermiyor")
            if not any(concept in normalized for concept in INTERVENTION_CONCEPTS):
                fail("MISCONCEPTION_INTERVENTION_NO_CONCEPT", "müdahale yanılgının kavramsal nedenini açıklamıyor")

    if task.get("task_type") in LOOK_FOR_TYPES or nonempty(task.get("expected_answer")):
        if not isinstance(task.get("assessment_look_fors"), list) or not task["assessment_look_fors"]:
            fail("ASSESSMENT_LOOK_FORS_MISSING", "öğretmenin gözleyeceği unsur listesi eksik")

    if task.get("content_status") == "REVIEW_REQUIRED":
        reasons = task.get("review_reasons", [])
        if not isinstance(reasons, list) or not reasons:
            fail("REVIEW_REASON_MISSING", "REVIEW_REQUIRED item review_reasons içermiyor")
    elif task.get("review_reasons"):
        fail("REVIEW_STATUS_MISMATCH", "review_reasons bulunan görev content_status=REVIEW_REQUIRED olmalı")

    if task.get("prompt_status") == "REVIEW_REQUIRED" or task.get("prompt_mode") in {"LOCATOR_ONLY", "REVIEW_REQUIRED"}:
        if task.get("task_type") == "QUESTION":
            fail("UNRESOLVED_PROMPT_TEXT", "soru prompt'u çözülmemiş veya yalnız locator olarak kalmış")

    provenance = task.get("provenance", {})
    if TEXTBOOK_SOURCE_ID not in provenance.get("source_ids", []):
        fail("PROVENANCE_TEXTBOOK_MISSING", "task provenance official_textbook_pdf içermiyor")
    if not provenance.get("source_locators") or not provenance.get("derived_from"):
        fail("PROVENANCE_CHAIN_INCOMPLETE", "task provenance source_locator/derived_from zinciri eksik")
    field_provenance = task.get("field_provenance", {})
    required_field_provenance = {"book_prompt", "source_context", "expected_answer"} | (set(task) & PEDAGOGICAL_FIELDS)
    for field in required_field_provenance:
        metadata = field_provenance.get(field)
        if not isinstance(metadata, dict):
            fail("FIELD_PROVENANCE_MISSING", f"{field} için field_provenance eksik")
            continue
        if field == "book_prompt":
            if metadata.get("origin") != "official_textbook" or TEXTBOOK_SOURCE_ID not in metadata.get("source_ids", []):
                fail("PROMPT_PROVENANCE_INVALID", "book_prompt official textbook provenance taşımıyor")
        elif field in PEDAGOGICAL_FIELDS or field == "expected_answer":
            if metadata.get("origin") != "pedagogical_recommendation" or not metadata.get("derived_from"):
                fail("PEDAGOGY_PROVENANCE_INVALID", f"{field} canonical/pedagojik derived_from zinciri taşımıyor")

    if task.get("generation_profile") == "text_analysis":
        warn("GENERIC_FALLBACK_USED", "task-specific router text_analysis fallback kullandı")


def validate_page_and_locators(
    task: dict[str, Any],
    theme_range: tuple[int, int],
    map_offset: int,
    theme_id: str,
    failures: list[dict[str, Any]],
) -> None:
    task_id = task["task_id"]

    def fail(code: str, message: str) -> None:
        failures.append({"code": code, "theme_id": theme_id, "task_id": task_id, "message": message})

    try:
        page_range = parse_page_range(task["printed_page_range"])
    except (KeyError, ValueError) as exc:
        fail("PAGE_RANGE_INVALID", str(exc))
        return
    if page_range[0] < theme_range[0] or page_range[1] > theme_range[1]:
        fail("PAGE_RANGE_OUTSIDE_THEME", f"{task['printed_page_range']} tema aralığı {theme_range} dışında")
    locators = task.get("source_locators", [])
    if not isinstance(locators, list) or not locators:
        fail("SOURCE_LOCATOR_MISSING", "source_locators boş")
        return
    if not isinstance(task.get("source_locator"), str) or not task["source_locator"].strip():
        fail("SOURCE_LOCATOR_PRIMARY_MISSING", "source_locator boş")
    printed_ranges = [locator_range(str(locator), PRINTED_LOCATOR_RE) for locator in locators]
    printed_ranges = [value for value in printed_ranges if value]
    if not printed_ranges:
        fail("SOURCE_LOCATOR_PAGE_UNRESOLVED", "source locator içinde basılı sayfa bulunamadı")
    locator_printed_ranges = [locator_range(str(locator), PRINTED_LOCATOR_RE) for locator in locators]
    if printed_ranges and not any(ranges_overlap(page_range, printed) for printed in locator_printed_ranges if printed):
        fail("SOURCE_PAGE_MISMATCH", f"hiçbir basılı kaynak locator'ı görev sayfası {task['printed_page_range']} ile kesişmiyor")
    for locator, printed in zip(locators, locator_printed_ranges):
        pdf = locator_range(str(locator), PDF_LOCATOR_RE)
        if printed and pdf and pdf[0] - printed[0] != map_offset:
            fail("PDF_PAGE_OFFSET_MISMATCH", f"{locator} printed→PDF ofseti {map_offset} ile uyuşmuyor")


def validate_repetition(
    tasks: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> None:
    field_limits = {
        "follow_up_questions": 3,
        "misconception_interventions": 3,
        "board_notes": 3,
        "teacher_background": 4,
        "answer_explanation": 4,
    }
    for field, limit in field_limits.items():
        counter: Counter[str] = Counter()
        owners: defaultdict[str, list[str]] = defaultdict(list)
        for task in tasks:
            values = task.get(field)
            if isinstance(values, list):
                values = [value for value in values if isinstance(value, str)]
                for value in values:
                    key = builder.normalize_text(value)
                    if key:
                        counter[key] += 1
                        owners[key].append(task["task_id"])
            elif isinstance(values, str) and values.strip():
                key = builder.normalize_text(values)
                counter[key] += 1
                owners[key].append(task["task_id"])
        for key, count in counter.items():
            if count > limit:
                failures.append(
                    {
                        "code": "BOILERPLATE_REPETITION",
                        "message": f"{field} aynı içerikle {count} kez tekrarlandı (limit {limit})",
                        "owners": owners[key][:8],
                    }
                )

    similarity_fields = ["follow_up_questions", "misconception_interventions"]
    for field in similarity_fields:
        entries: list[tuple[str, str, str]] = []
        for task in tasks:
            for value in task.get(field, []) if isinstance(task.get(field), list) else []:
                if isinstance(value, str) and value.strip():
                    entries.append((task["task_id"], task.get("focus", ""), value))
        high_similarity: list[dict[str, Any]] = []
        for index, (left_id, left_focus, left_value) in enumerate(entries):
            for right_id, right_focus, right_value in entries[index + 1 :]:
                if left_id == right_id or left_focus == right_focus:
                    continue
                similarity = token_similarity(left_value, right_value)
                if similarity >= 0.94:
                    high_similarity.append({"left": left_id, "right": right_id, "similarity": round(similarity, 3)})
                    if len(high_similarity) >= 4:
                        break
            if len(high_similarity) >= 4:
                break
        if high_similarity:
            failures.append(
                {
                    "code": "SEMANTIC_BOILERPLATE_REPETITION",
                    "message": f"{field} farklı odaklarda neredeyse aynı pedagojik cümleyi kullanıyor",
                    "examples": high_similarity,
                }
            )

    board_count = sum(1 for task in tasks if task.get("board_notes"))
    if tasks and board_count / len(tasks) > 0.65:
        failures.append({"code": "BOARD_NOTE_OVERUSE", "message": f"board_notes görevlerin %{round(100 * board_count / len(tasks))}'ında kullanılmış"})


def validate_index_alignment(
    index: dict[str, Any],
    guides: dict[str, dict[str, Any]],
    mirror_records: dict[str, dict[str, dict[str, Any]]],
    activity_index: dict[str, dict[str, Any]],
    failures: list[dict[str, Any]],
) -> tuple[int, int, int, int, list[str], list[str]]:
    index_questions: dict[str, dict[str, Any]] = {}
    index_activities: dict[str, dict[str, Any]] = {}
    for theme in index.get("themes", []):
        for question in theme.get("questions", []):
            task_id = question["task_id"]
            if task_id in index_questions:
                failures.append({"code": "DUPLICATE_INDEX_QUESTION", "task_id": task_id, "message": "index question task id tekrarlanıyor"})
            index_questions[task_id] = question
        for activity in theme.get("activities", []):
            activity_id = activity["activity_id"]
            if activity_id in index_activities:
                failures.append({"code": "DUPLICATE_INDEX_ACTIVITY", "task_id": activity_id, "message": "index activity id tekrarlanıyor"})
            index_activities[activity_id] = activity

    guide_questions = {task["task_id"]: task for guide in guides.values() for task in guide.get("tasks", []) if task.get("task_type") == "QUESTION"}
    expected_questions = {task_id for records in mirror_records.values() for task_id in records}
    uncovered_questions = sorted(expected_questions - set(guide_questions))
    extra_questions = sorted(set(guide_questions) - expected_questions)
    for task_id in uncovered_questions:
        failures.append({"code": "UNCOVERED_TEXTBOOK_QUESTION", "task_id": task_id, "message": "mirror'daki soru canonical teacher guide V3'te yok"})
    for task_id in extra_questions:
        failures.append({"code": "UNEXPECTED_GUIDE_QUESTION", "task_id": task_id, "message": "teacher guide sorusu textbook task index/mirror kaynağında yok"})
    if set(index_questions) != expected_questions:
        failures.append({"code": "INDEX_QUESTION_PARITY", "message": "textbook_task_index questions mirror soru kümesiyle eşleşmiyor"})
    if set(index_questions) != set(guide_questions):
        failures.append({"code": "INDEX_GUIDE_QUESTION_PARITY", "message": "textbook_task_index questions guide soru kümesiyle eşleşmiyor"})
    for task_id, question in index_questions.items():
        task = guide_questions.get(task_id)
        if task is None:
            continue
        for field in ["section_id", "printed_page_range", "book_heading", "book_prompt", "prompt_mode", "prompt_status", "canonical_item_refs", "activity_refs", "source_locator", "question_number", "split_from_group"]:
            if question.get(field) != task.get(field):
                failures.append({"code": "INDEX_TASK_FIELD_MISMATCH", "task_id": task_id, "message": f"index/guide {field} uyuşmazlığı"})
        if not nonempty(question.get("source_ids")):
            failures.append({"code": "INDEX_PROMPT_PROVENANCE_MISSING", "task_id": task_id, "message": "index question source_ids boş"})

    map_activity_ids = set(activity_index)
    index_activity_ids = set(index_activities)
    uncovered_activities = sorted(map_activity_ids - index_activity_ids)
    extra_activities = sorted(index_activity_ids - map_activity_ids)
    for activity_id in uncovered_activities:
        failures.append({"code": "UNINDEXED_TEXTBOOK_ACTIVITY", "task_id": activity_id, "message": "textbook_map activity task index'te yok"})
    for activity_id in extra_activities:
        failures.append({"code": "UNEXPECTED_INDEX_ACTIVITY", "task_id": activity_id, "message": "task index activity textbook_map'te yok"})
    guide_activity_refs = {ref for guide in guides.values() for task in guide.get("tasks", []) for ref in task.get("activity_refs", [])}
    uncovered_guide_activities = sorted(map_activity_ids - guide_activity_refs)
    for activity_id in uncovered_guide_activities:
        failures.append({"code": "UNCOVERED_REQUIRED_ACTIVITY", "task_id": activity_id, "message": "textbook_map activity canonical teacher guide V3 görevlerinden hiçbirinde yok"})
    for activity_id, activity in index_activities.items():
        source = activity_index.get(activity_id)
        if source is None:
            continue
        for field, source_field in [("section_id", "section_id"), ("printed_page_range", "printed_page_range"), ("source_locator", "source_locator")]:
            if activity.get(field) != source.get(source_field):
                failures.append({"code": "INDEX_ACTIVITY_FIELD_MISMATCH", "task_id": activity_id, "message": f"activity {field} textbook_map ile uyuşmuyor"})
    return len(expected_questions), len(guide_questions), len(map_activity_ids), len(guide_activity_refs & map_activity_ids), uncovered_questions, uncovered_guide_activities


def validate_course(root: Path, course_id: str = builder.COURSE_ID, quality_level: str = "release") -> dict[str, Any]:
    course_dir = root / "courses" / course_id
    schema_dir = root / "skill" / "tymm-material-planner" / "schemas"
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    guides: dict[str, dict[str, Any]] = {}
    mirror_records: dict[str, dict[str, dict[str, Any]]] = {}
    canonical_by_theme: dict[str, tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]] = {}
    all_tasks: list[dict[str, Any]] = []

    map_path = course_dir / "textbook_map.json"
    index_path = course_dir / "teacher_guide_v3" / "textbook_task_index.json"
    pdf_path = course_dir / "source_docs" / "turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf"
    if not map_path.exists():
        failures.append({"code": "TEXTBOOK_MAP_MISSING", "message": str(map_path)})
        return {"status": "FAIL", "quality_level": quality_level, "failures": failures, "warnings": warnings, "counts": {}}
    textbook_map = read_json(map_path)
    activity_index, _ = builder.activity_index_from_map(textbook_map)
    map_offset = int(textbook_map.get("primary_source", {}).get("printed_to_pdf_offset", 1))
    expected_pdf_sha = textbook_map.get("primary_source", {}).get("sha256")
    if not pdf_path.exists():
        failures.append({"code": "TEXTBOOK_PDF_MISSING", "message": str(pdf_path)})
    elif expected_pdf_sha and builder.sha256_file(pdf_path) != expected_pdf_sha:
        failures.append({"code": "TEXTBOOK_PDF_HASH_MISMATCH", "message": "textbook PDF SHA-256 textbook_map ile uyuşmuyor"})

    if not index_path.exists():
        failures.append({"code": "TEXTBOOK_TASK_INDEX_MISSING", "message": str(index_path)})
        index: dict[str, Any] = {}
    else:
        index = read_json(index_path)
        for error in schema_errors(index, schema_dir / "textbook_task_index.schema.json"):
            failures.append({"code": "INDEX_SCHEMA_INVALID", "message": error})
        source = index.get("source", {})
        if source.get("path") != builder.relative_path(root, pdf_path):
            failures.append({"code": "INDEX_SOURCE_PATH_MISMATCH", "message": "index source.path textbook PDF yolu ile uyuşmuyor"})
        if expected_pdf_sha and source.get("sha256") != expected_pdf_sha:
            failures.append({"code": "INDEX_SOURCE_HASH_MISMATCH", "message": "index source.sha256 textbook_map ile uyuşmuyor"})
        if index.get("map_ref") != builder.relative_path(root, map_path):
            failures.append({"code": "INDEX_MAP_REF_MISMATCH", "message": "index map_ref textbook_map yolu ile uyuşmuyor"})

    theme_map_by_id = {theme["theme_id"]: theme for theme in textbook_map.get("themes", [])}
    for theme_id, theme in sorted(theme_map_by_id.items()):
        guide_path = course_dir / "teacher_guide" / theme_id / "teacher_guide_v3.json"
        if not guide_path.exists():
            failures.append({"code": "GUIDE_MISSING", "theme_id": theme_id, "message": str(guide_path)})
            continue
        guide = read_json(guide_path)
        guides[theme_id] = guide
        for error in schema_errors(guide, schema_dir / "teacher_guide_v3.schema.json"):
            failures.append({"code": "GUIDE_SCHEMA_INVALID", "theme_id": theme_id, "message": error})
        if guide.get("theme_id") != theme_id or guide.get("generator") != "TEXTBOOK_FIRST_TEACHER_GUIDE_V3":
            failures.append({"code": "GUIDE_IDENTITY_INVALID", "theme_id": theme_id, "message": "guide theme_id/generator V3 contractını karşılamıyor"})
        if guide.get("status") == "REFERENCE_QUALITY" and any(task.get("content_status") == "REVIEW_REQUIRED" for task in guide.get("tasks", [])):
            failures.append({"code": "GUIDE_STATUS_MISMATCH", "theme_id": theme_id, "message": "REVIEW_REQUIRED task varken guide status REFERENCE_QUALITY"})
        mirror_records[theme_id], mirror_duplicates = mirror_question_records(root, theme_id)
        for duplicate in mirror_duplicates:
            failures.append({"code": "DUPLICATE_MIRROR_QUESTION", "theme_id": theme_id, "task_id": duplicate, "message": "mirror question id tekrarlanıyor"})
        manifest_path = course_dir / "teacher_guide" / theme_id / "teacher_guide.json"
        manifest = read_json(manifest_path)
        canonical_sections, canonical = builder.index_canonical(root, manifest)
        try:
            builder.apply_component_registries(root, theme_id, canonical)
        except ValueError as exc:
            failures.append({"code": "COMPONENT_REGISTRY_INVALID", "theme_id": theme_id, "message": str(exc)})
        canonical_by_theme[theme_id] = (canonical_sections, canonical, {row["section_id"]: row for row in manifest["sections"]})
        theme_range = parse_page_range(theme["printed_page_range"])
        for task in guide.get("tasks", []):
            all_tasks.append(task)
            validate_task_fields(task, theme_id, failures, warnings)
            validate_page_and_locators(task, theme_range, map_offset, theme_id, failures)
            if task.get("task_type") == "QUESTION":
                source_entry = mirror_records[theme_id].get(task.get("task_id"))
                if source_entry is None:
                    failures.append({"code": "QUESTION_NOT_IN_MIRROR", "theme_id": theme_id, "task_id": task.get("task_id"), "message": "soru mirror kaydına bağlanamıyor"})
                    continue
                source_prompt = source_entry.get("prompt_display")
                if not isinstance(source_prompt, str) or not source_prompt.strip():
                    failures.append({"code": "UNRESOLVED_PROMPT_TEXT", "theme_id": theme_id, "task_id": task["task_id"], "message": "mirror soru prompt'u yok"})
                elif task.get("book_prompt") != re.sub(r"\s+", " ", source_prompt.strip()):
                    failures.append({"code": "PROMPT_FIDELITY_MISMATCH", "theme_id": theme_id, "task_id": task["task_id"], "message": "book_prompt mirror prompt_display ile aynı değil"})
                if task.get("book_prompt") and LOCATOR_ONLY_RE.match(task["book_prompt"]):
                    failures.append({"code": "LOCATOR_ONLY_QUESTION", "theme_id": theme_id, "task_id": task["task_id"], "message": "question book_prompt yalnız locator"})
                expected_mode = source_entry.get("prompt_mode") or "VERIFIED_SUMMARY"
                if task.get("prompt_mode") != expected_mode:
                    failures.append({"code": "PROMPT_MODE_MISMATCH", "theme_id": theme_id, "task_id": task["task_id"], "message": "prompt_mode source mirror ile uyuşmuyor"})
                expected_split = bool(source_entry.get("split_from_group", False))
                if bool(task.get("split_from_group")) != expected_split:
                    failures.append({"code": "GROUP_SPLIT_FLAG_MISMATCH", "theme_id": theme_id, "task_id": task["task_id"], "message": "group split işareti source task ile uyuşmuyor"})
                expected_keys = unique_list(str(key) for key in source_entry.get("answer_keys", []))
                if task.get("answer_component_keys") != expected_keys:
                    failures.append({"code": "ANSWER_COMPONENT_KEY_MISMATCH", "theme_id": theme_id, "task_id": task["task_id"], "message": "answer_component_keys mirror ile uyuşmuyor"})
                expected_number = builder.find_question_number(source_entry, source_entry.get("prompt_display"))
                if task.get("question_number") != expected_number:
                    failures.append({"code": "QUESTION_NUMBER_MISMATCH", "theme_id": theme_id, "task_id": task["task_id"], "message": "question_number source mirror ile uyuşmuyor"})
                expected_activities = expected_activity_refs(source_entry, canonical, canonical_sections, canonical_by_theme[theme_id][2][source_entry["section_id"]])
                expected_outcomes = expected_outcome_refs(source_entry, canonical, canonical_sections, canonical_by_theme[theme_id][2][source_entry["section_id"]])
                if task.get("activity_refs") != expected_activities:
                    failures.append({"code": "TASK_ACTIVITY_LINK_MISMATCH", "theme_id": theme_id, "task_id": task["task_id"], "message": "task activity_refs canonical section/unit ile uyuşmuyor"})
                if task.get("outcome_refs") != expected_outcomes:
                    failures.append({"code": "TASK_OUTCOME_LINK_MISMATCH", "theme_id": theme_id, "task_id": task["task_id"], "message": "task outcome_refs canonical section/unit ile uyuşmuyor"})
                try:
                    expected_answer, answer_errors = builder.project_answer(canonical, task.get("canonical_item_refs", []), task.get("answer_component_keys", []))
                except (KeyError, TypeError, ValueError) as exc:
                    expected_answer, answer_errors = None, [str(exc)]
                if answer_errors:
                    failures.append({"code": "CANONICAL_ANSWER_PROJECTION_ERROR", "theme_id": theme_id, "task_id": task["task_id"], "message": "; ".join(answer_errors)})
                elif expected_answer != task.get("expected_answer"):
                    failures.append({"code": "EXPECTED_ANSWER_FIDELITY_MISMATCH", "theme_id": theme_id, "task_id": task["task_id"], "message": "guide expected_answer canonical projection ile uyuşmuyor"})

        # The canonical answer projection check also applies to non-question
        # task cards, because process/form records may carry an expected product.
        for task in guide.get("tasks", []):
            try:
                expected_answer, answer_errors = builder.project_answer(canonical, task.get("canonical_item_refs", []), task.get("answer_component_keys", []))
            except (KeyError, TypeError, ValueError) as exc:
                expected_answer, answer_errors = None, [str(exc)]
            if answer_errors:
                failures.append({"code": "CANONICAL_ANSWER_PROJECTION_ERROR", "theme_id": theme_id, "task_id": task.get("task_id"), "message": "; ".join(answer_errors)})
            elif expected_answer != task.get("expected_answer"):
                failures.append({"code": "EXPECTED_ANSWER_FIDELITY_MISMATCH", "theme_id": theme_id, "task_id": task.get("task_id"), "message": "guide expected_answer canonical projection ile uyuşmuyor"})

        # True numbered groups must be split; other multi-component cards stay
        # as one task with answer_component_keys.
        for group_id, parts in builder.GROUPED_PROMPT_OVERRIDES.items():
            if not any(entry.get("mirror_id") == group_id for entry in builder.merge_mirrors(builder.discover_mirror_paths(course_dir / "teacher_guide" / theme_id / "book_mirror_v23.json"))["entries"]):
                continue
            task_ids = {f"{theme_id}::{group_id}#Q{part['question_number']}" for part in parts}
            actual = {task["task_id"] for task in guide.get("tasks", []) if task["task_id"] in task_ids}
            if actual != task_ids:
                failures.append({"code": "GROUPED_QUESTION_SPLIT_MISSING", "theme_id": theme_id, "task_id": group_id, "message": f"beklenen alt soru kümesi {sorted(task_ids)}"})

        # Detect overlapping answer component projections for the same source
        # item; non-overlapping component keys are intentionally allowed.
        seen_components: defaultdict[tuple[str, str], list[tuple[str, set[str]]] ] = defaultdict(list)
        for task in guide.get("tasks", []):
            for ref in task.get("canonical_item_refs", []):
                key = (theme_id, ref)
                components = set(task.get("answer_component_keys", []))
                seen_components[key].append((task["task_id"], components))
        for key, entries in seen_components.items():
            for component_index, (left_id, left_components) in enumerate(entries):
                for right_id, right_components in entries[component_index + 1 :]:
                    if not left_components or not right_components:
                        continue
                    overlap = left_components & right_components
                    if overlap:
                        failures.append({"code": "DUPLICATE_ANSWER_COMPONENT", "theme_id": theme_id, "task_id": left_id, "message": f"{right_id} ile ortak answer key: {sorted(overlap)}"})

        # Per-theme coverage metrics must be generated from the actual V3 task
        # list, rather than trusted blindly from a stale manifest.
        theme_questions = [task for task in guide.get("tasks", []) if task.get("task_type") == "QUESTION"]
        theme_activities = {activity["activity_id"] for section in theme.get("sections", []) for activity in section.get("activities", [])}
        covered = {ref for task in guide.get("tasks", []) for ref in task.get("activity_refs", []) if ref in theme_activities}
        expected_review = {task["task_id"] for task in guide.get("tasks", []) if task.get("content_status") == "REVIEW_REQUIRED"}
        coverage = guide.get("coverage", {})
        checks = {
            "textbook_question_count": len(theme_questions),
            "guide_question_count": len(theme_questions),
            "textbook_activity_count": len(theme_activities),
            "covered_activity_count": len(covered),
            "uncovered_required_activities": sorted(theme_activities - covered),
            "locator_only_questions": sorted(task["task_id"] for task in theme_questions if task.get("prompt_mode") == "LOCATOR_ONLY"),
            "unresolved_prompt_text": sorted(task["task_id"] for task in theme_questions if not nonempty(task.get("book_prompt")) or task.get("prompt_status") == "REVIEW_REQUIRED"),
            "review_required_items": sorted(expected_review),
        }
        for field, expected_value in checks.items():
            if coverage.get(field) != expected_value:
                failures.append({"code": "COVERAGE_STALE", "theme_id": theme_id, "message": f"coverage.{field} generated task listesiyle uyuşmuyor"})

        actual_md = course_dir / "teacher_guide" / theme_id / "TEACHER_GUIDE_V3.md"
        if not actual_md.exists():
            failures.append({"code": "RENDERED_GUIDE_MISSING", "theme_id": theme_id, "message": str(actual_md)})
        else:
            rendered_once = builder.render_markdown(guide)
            rendered_twice = builder.render_markdown(guide)
            if rendered_once != rendered_twice:
                failures.append({"code": "RENDERER_NONDETERMINISTIC", "theme_id": theme_id, "message": "aynı guide iki render'da farklı çıktı üretiyor"})
            actual_text = actual_md.read_text(encoding="utf-8")
            if actual_text != rendered_once:
                failures.append({"code": "RENDERED_GUIDE_STALE", "theme_id": theme_id, "message": "TEACHER_GUIDE_V3.md JSON renderer çıktısından farklı"})
            expected_hash = hashlib.sha256(rendered_once.encode("utf-8")).hexdigest()
            if guide.get("rendered_markdown_sha256") != expected_hash:
                failures.append({"code": "RENDERED_HASH_MISMATCH", "theme_id": theme_id, "message": "rendered_markdown_sha256 renderer ile uyuşmuyor"})

    # Global duplicate prevention: identical task/source packages are not
    # allowed, while distinct split components can share a canonical item.
    task_ids = [task.get("task_id") for task in all_tasks]
    for task_id, count in Counter(task_ids).items():
        if count > 1:
            failures.append({"code": "DUPLICATE_TASK_ID", "task_id": task_id, "message": f"task_id {count} kez bulunuyor"})
    exact_source_keys: defaultdict[tuple[Any, ...], list[str]] = defaultdict(list)
    for task in all_tasks:
        key = (
            task.get("section_id"),
            task.get("printed_page_range"),
            builder.normalize_text(task.get("book_prompt")),
            tuple(task.get("canonical_item_refs", [])),
            tuple(task.get("answer_component_keys", [])),
        )
        exact_source_keys[key].append(task["task_id"])
    for key, owners in exact_source_keys.items():
        if len(owners) > 1:
            failures.append({"code": "DUPLICATE_SOURCE_TASK", "message": "aynı sayfa/prompt/canonical key birden çok task olarak temsil edilmiş", "owners": owners})
    validate_repetition(all_tasks, failures, warnings)

    if index:
        textbook_questions, guide_questions, textbook_activities, covered_activities, uncovered_questions, uncovered_guide_activities = validate_index_alignment(index, guides, mirror_records, activity_index, failures)
    else:
        textbook_questions = guide_questions = textbook_activities = covered_activities = 0
        uncovered_questions = []
        uncovered_guide_activities = []

    review_items = sorted(task["task_id"] for task in all_tasks if task.get("content_status") == "REVIEW_REQUIRED")
    locator_only = sorted(task["task_id"] for task in all_tasks if task.get("task_type") == "QUESTION" and task.get("prompt_mode") == "LOCATOR_ONLY")
    unresolved_prompts = sorted(task["task_id"] for task in all_tasks if task.get("task_type") == "QUESTION" and (not nonempty(task.get("book_prompt")) or task.get("prompt_status") == "REVIEW_REQUIRED"))
    fallback_count = sum(1 for task in all_tasks if task.get("generation_profile") == "text_analysis")
    if all_tasks and fallback_count / len(all_tasks) > 0.10:
        failures.append({"code": "GENERIC_FALLBACK_OVERUSE", "message": f"text_analysis fallback {fallback_count}/{len(all_tasks)} taskta kullanılmış"})
    for theme_id, guide in guides.items():
        reported_fallback = guide.get("coverage", {}).get("generic_fallback_task_count")
        actual_fallback = sum(1 for task in guide.get("tasks", []) if task.get("generation_profile") == "text_analysis")
        if reported_fallback != actual_fallback:
            failures.append({"code": "FALLBACK_COUNT_STALE", "theme_id": theme_id, "message": "generic_fallback_task_count stale"})

    if quality_level == "strict-review" and review_items:
        failures.append({"code": "STRICT_REVIEW_REQUIRED", "message": f"strict-review modunda {len(review_items)} REVIEW_REQUIRED task var"})

    if SCHEMA_VALIDATOR_AVAILABLE is False:
        warnings.append(
            {
                "code": "SCHEMA_VALIDATION_UNAVAILABLE",
                "message": "Yerel ortamda jsonschema yok; CI'da pinned jsonschema ile tam Draft 2020-12 doğrulaması çalıştırılmalı.",
            }
        )

    counts = {
        "themes": len(guides),
        "textbook_questions": textbook_questions,
        "guide_questions": guide_questions,
        "textbook_activities": textbook_activities,
        "covered_activities": covered_activities,
        "uncovered_textbook_questions": len(uncovered_questions),
        "uncovered_required_activities": len(uncovered_guide_activities),
        "locator_only_questions": len(locator_only),
        "unresolved_prompt_text": len(unresolved_prompts),
        "review_required_items": len(review_items),
        "generic_fallback_tasks": fallback_count,
        "total_tasks": len(all_tasks),
    }
    status = "FAIL" if failures else ("PASS_WITH_REVIEW" if review_items else "PASS")
    return {
        "status": status,
        "quality_level": quality_level,
        "counts": counts,
        "theme_reports": {
            theme_id: {
                "tasks": len(guide.get("tasks", [])),
                "questions": sum(1 for task in guide.get("tasks", []) if task.get("task_type") == "QUESTION"),
                "review_required": sum(1 for task in guide.get("tasks", []) if task.get("content_status") == "REVIEW_REQUIRED"),
                "generic_fallback": sum(1 for task in guide.get("tasks", []) if task.get("generation_profile") == "text_analysis"),
            }
            for theme_id, guide in sorted(guides.items())
        },
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--course", default=builder.COURSE_ID)
    parser.add_argument("--quality-level", choices=["release", "strict-review"], default="release")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = validate_course(args.repo_root.resolve(), args.course, args.quality_level)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
