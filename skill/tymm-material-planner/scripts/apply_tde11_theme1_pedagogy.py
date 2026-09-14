#!/usr/bin/env python3
"""Apply the TDE11 Theme 1 pedagogy revision with teacher-facing ID hygiene.

Canonical structural references such as used_form_ids remain untouched. Only
human-facing lesson prose is normalized so internal FORM_* identifiers never
leak into the teacher projection.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SCRIPT_DIR))

import revise_tde11_theme1_pedagogy as base  # noqa: E402
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

FORM_LABELS = {
    "FORM_T1_P035_OZ_DEGERLENDIRME_01": "doğrulanmış öz değerlendirme formu",
    "FORM_T1_P054_KONTROL_LISTESI_03": "doğrulanmış konuşma kontrol listesi",
    "FORM_T1_P058_OZ_DEGERLENDIRME_05": "doğrulanmış konuşma öz değerlendirme formu",
    "FORM_T1_P064_GOZLEM_FORMU_07": "doğrulanmış dinleme/izleme gözlem formu",
    "FORM_T1_P073_CIKIS_KARTI_08": "doğrulanmış dinleme/izleme çıkış kartı",
}


def replace_ids(value: Any) -> Any:
    if isinstance(value, str):
        result = value
        for form_id, label in FORM_LABELS.items():
            result = result.replace(form_id, label)
        return result
    if isinstance(value, list):
        return [replace_ids(item) for item in value]
    return value


def sanitize_teacher_prose(plan: dict[str, Any]) -> dict[str, Any]:
    for lesson in plan.get("lessons", []):
        if not isinstance(lesson, dict):
            continue
        for field in TEACHER_FIELDS:
            if field in lesson:
                lesson[field] = replace_ids(lesson[field])
    return plan


def canonical_json(plan: dict[str, Any]) -> str:
    return json.dumps(plan, ensure_ascii=False, separators=(",", ":")) + "\n"


def run(*, write: bool, check: bool) -> dict[str, Any]:
    overlay = base.load_json(base.OVERLAY_PATH)
    designs = [item for item in overlay.get("packages", []) if item["package_id"].startswith("BLOCK_T1_")]
    if len(designs) != 22:
        raise ValueError(f"THEME1_DESIGN_COUNT:{len(designs)}!=22")

    changed: list[str] = []
    drift: list[str] = []
    for design in designs:
        json_path = base.locate_package(design["package_id"])
        current = base.load_json(json_path)
        expected = sanitize_teacher_prose(base.transform(current, design))
        json_text = canonical_json(expected)
        md_text = render(expected)
        md_path = json_path.with_suffix(".md")

        if json_path.read_text(encoding="utf-8") != json_text:
            changed.append(json_path.relative_to(REPO_ROOT).as_posix())
            if check:
                drift.append(json_path.relative_to(REPO_ROOT).as_posix())
            if write:
                json_path.write_text(json_text, encoding="utf-8")
        if not md_path.exists() or md_path.read_text(encoding="utf-8") != md_text:
            changed.append(md_path.relative_to(REPO_ROOT).as_posix())
            if check:
                drift.append(md_path.relative_to(REPO_ROOT).as_posix())
            if write:
                md_path.write_text(md_text, encoding="utf-8")

    payload = {
        "status": "FAIL" if drift else "PASS",
        "theme": "TEMA_01",
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
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run(write=args.write, check=args.check)
    return 1 if payload["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
