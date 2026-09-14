#!/usr/bin/env python3
"""Apply one TDE11 pedagogical theme overlay deterministically.

Canonical outcomes, activities, form IDs, materials, grounding, adaptations and
lesson-hour topology remain authoritative. Only teacher-facing pedagogical prose
and titles are revised. Technical form IDs are resolved from the verified form
catalog before Markdown is regenerated.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
COURSE_ROOT = REPO_ROOT / "courses/TDE_11"
sys.path.insert(0, str(SCRIPT_DIR))

import revise_tde11_theme1_pedagogy as base  # noqa: E402
import teacher_facing_text  # noqa: E402
from render_lesson_plan_markdown import render  # noqa: E402

TEACHER_FIELDS = {
    "title",
    "objective",
    "opening",
    "teacher_actions",
    "student_actions",
    "assessment",
    "closure",
}
FORM_ID_RE = re.compile(r"\bFORM_[A-Z0-9_]+\b", re.IGNORECASE)
THEME_RE = re.compile(r"^TEMA_(0[1-4])$")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"


def overlay_path(theme_id: str) -> Path:
    if theme_id == "TEMA_01":
        return COURSE_ROOT / "planning/pedagogical_package_design.json"
    return COURSE_ROOT / f"planning/pedagogical_package_design_{theme_id.lower()}.json"


def theme_config(theme_id: str) -> tuple[dict[str, list[str]], set[tuple[str, int]]]:
    if theme_id == "TEMA_01":
        return base.TITLE_MAP, set(base.PRESERVE_BODY)
    path = COURSE_ROOT / f"planning/pedagogical_title_map_{theme_id.lower()}.json"
    config = read_json(path)
    if config.get("course_id") != "TDE_11" or config.get("theme_id") != theme_id:
        raise ValueError(f"TITLE_CONFIG_SCOPE_MISMATCH:{path}")
    titles = config.get("titles")
    if not isinstance(titles, dict):
        raise ValueError(f"TITLE_MAP_INVALID:{path}")
    normalized_titles: dict[str, list[str]] = {}
    for package_id, values in titles.items():
        if not isinstance(package_id, str) or not isinstance(values, list) or not all(isinstance(v, str) and v.strip() for v in values):
            raise ValueError(f"TITLE_MAP_ENTRY_INVALID:{package_id}")
        normalized_titles[package_id] = values
    preserve: set[tuple[str, int]] = set()
    for item in config.get("preserve_body_lessons", []):
        if not isinstance(item, dict) or not isinstance(item.get("package_id"), str) or not isinstance(item.get("lesson_no"), int):
            raise ValueError("PRESERVE_BODY_ENTRY_INVALID")
        preserve.add((item["package_id"], item["lesson_no"]))
    return normalized_titles, preserve


def verified_form_labels() -> dict[str, str]:
    catalog = teacher_facing_text.TeacherReferenceCatalog.from_knowledge_root(COURSE_ROOT)
    return {form_id.casefold(): label for form_id, label in catalog.forms.items()}


def replace_form_ids(value: Any, labels: dict[str, str]) -> Any:
    if isinstance(value, str):
        def repl(match: re.Match[str]) -> str:
            technical = match.group(0)
            label = labels.get(technical.casefold())
            if label is None:
                raise ValueError(f"UNRESOLVED_TEACHER_FORM_ID:{technical}")
            return f"doğrulanmış {label}"
        return FORM_ID_RE.sub(repl, value)
    if isinstance(value, list):
        return [replace_form_ids(item, labels) for item in value]
    return value


def sanitize_teacher_prose(plan: dict[str, Any], labels: dict[str, str]) -> dict[str, Any]:
    for lesson in plan.get("lessons", []):
        if not isinstance(lesson, dict):
            continue
        for field in TEACHER_FIELDS:
            if field not in lesson:
                continue
            lesson[field] = replace_form_ids(lesson[field], labels)
            values = lesson[field] if isinstance(lesson[field], list) else [lesson[field]]
            for value in values:
                if isinstance(value, str) and FORM_ID_RE.search(value):
                    raise ValueError(f"TEACHER_FORM_ID_LEAK:{field}:{FORM_ID_RE.search(value).group(0)}")
    return plan


def locate_package(theme_id: str, package_id: str) -> Path:
    root = COURSE_ROOT / f"generated/lesson_plans/{theme_id}"
    matches = list(root.glob(f"**/{package_id}.json"))
    if len(matches) != 1:
        raise ValueError(f"PACKAGE_LOOKUP:{theme_id}:{package_id}:found={len(matches)}")
    return matches[0]


def transform(
    plan: dict[str, Any],
    design: dict[str, Any],
    titles: list[str],
    preserve_body: set[tuple[str, int]],
    form_labels: dict[str, str],
) -> dict[str, Any]:
    package_id = str(design["package_id"])
    route_id = str(design["route_id"])
    lessons = plan.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        raise ValueError(f"LESSONS_MISSING:{package_id}")
    if len(titles) != len(lessons):
        raise ValueError(f"TITLE_COUNT_MISMATCH:{package_id}:{len(titles)}!={len(lessons)}")
    progression = {int(item["lesson_no"]): item for item in design.get("lesson_progression", [])}
    lesson_nos = {int(item["lesson_no"]) for item in lessons}
    if set(progression) != lesson_nos:
        raise ValueError(f"PROGRESSION_LESSON_SET_MISMATCH:{package_id}")

    result = copy.deepcopy(plan)
    revised: list[dict[str, Any]] = []
    for index, lesson in enumerate(lessons):
        lesson_no = int(lesson["lesson_no"])
        title = titles[index]
        if (package_id, lesson_no) in preserve_body:
            next_lesson = copy.deepcopy(lesson)
            next_lesson["title"] = title
        else:
            next_lesson = base.revised_lesson(
                package_id,
                route_id,
                lesson,
                progression[lesson_no],
                title,
            )
        revised.append(next_lesson)
    result["lessons"] = revised
    return sanitize_teacher_prose(result, form_labels)


def run(theme_id: str, *, write: bool, check: bool) -> dict[str, Any]:
    if THEME_RE.fullmatch(theme_id) is None:
        raise ValueError(f"THEME_ID_INVALID:{theme_id}")
    overlay = read_json(overlay_path(theme_id))
    designs = overlay.get("packages")
    if not isinstance(designs, list) or len(designs) != 22:
        raise ValueError(f"THEME_DESIGN_COUNT:{theme_id}:{len(designs) if isinstance(designs, list) else 'invalid'}!=22")
    prefix = f"BLOCK_T{int(theme_id[-2:])}_"
    if any(not isinstance(item, dict) or not str(item.get("package_id", "")).startswith(prefix) for item in designs):
        raise ValueError(f"THEME_DESIGN_SCOPE_INVALID:{theme_id}")

    title_map, preserve_body = theme_config(theme_id)
    design_ids = {str(item["package_id"]) for item in designs}
    if set(title_map) != design_ids:
        raise ValueError(
            f"TITLE_MAP_COVERAGE:{theme_id}:missing={sorted(design_ids-set(title_map))}:extra={sorted(set(title_map)-design_ids)}"
        )
    form_labels = verified_form_labels()

    changed: list[str] = []
    drift: list[str] = []
    for design in designs:
        package_id = str(design["package_id"])
        json_path = locate_package(theme_id, package_id)
        current = read_json(json_path)
        expected = transform(current, design, title_map[package_id], preserve_body, form_labels)
        json_text = canonical_json(expected)
        md_text = render(expected)
        md_path = json_path.with_suffix(".md")

        for path, expected_text in ((json_path, json_text), (md_path, md_text)):
            actual_text = path.read_text(encoding="utf-8") if path.exists() else ""
            if actual_text == expected_text:
                continue
            relative = path.relative_to(REPO_ROOT).as_posix()
            changed.append(relative)
            if check:
                drift.append(relative)
            if write:
                path.write_text(expected_text, encoding="utf-8")

    payload = {
        "status": "FAIL" if drift else "PASS",
        "theme": theme_id,
        "packages": len(designs),
        "teacher_form_id_hygiene": "PASS",
        "write": write,
        "check": check,
        "changed_or_would_change": sorted(set(changed)),
        "drift": sorted(set(drift)),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", required=True, choices=["TEMA_01", "TEMA_02", "TEMA_03", "TEMA_04"])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run(args.theme, write=args.write, check=args.check)
    return 1 if payload["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
