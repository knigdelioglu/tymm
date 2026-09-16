#!/usr/bin/env python3
"""Export a runtime-neutral, book-first Teacher Guide V2.3 projection for ÖğretmenOS.

The export is intentionally derived from the already validated V2.3 mirror +
canonical teacher-guide sources. It does not expose the private repo at runtime;
ÖğretmenOS can vendor the generated JSON and project it into its SQLite package.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_teacher_guide_v23 import (
    apply_component_registry,
    discover_mirror_paths,
    index_canonical,
    load_component_registry,
    merge_mirrors,
    nonempty,
    project_value,
    read_json,
)

SOURCE_COMMIT = "20860e3165d5e9de18913364286e6f89f28f6046"
EXPECTED_TOTALS = {"themes": 4, "entries": 573, "questions": 404, "locator_only_questions": 0}


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def project_field(entry: dict[str, Any], item: dict[str, Any], field: str) -> Any:
    value = item.get(field)
    if field in {"expected_answer", "expected_response"} and nonempty(value):
        return project_value(entry, value)
    return value


def combine_by_ref(
    entry: dict[str, Any],
    canonical: dict[str, dict[str, Any]],
    field: str,
    *,
    gated: bool = False,
) -> Any:
    if gated:
        gate = {
            "acceptance_criteria": "show_acceptance",
            "common_misconceptions": "show_common_misconceptions",
            "differentiation": "show_differentiation",
        }.get(field)
        if gate and not entry.get(gate):
            return [] if field != "differentiation" else {"support": [], "enrichment": []}

    values: list[tuple[str, str, Any]] = []
    for ref in entry["canonical_item_refs"]:
        item = canonical[ref]["item"]
        value = project_field(entry, item, field)
        if nonempty(value):
            values.append((ref, str(item.get("label") or item.get("title") or ref), value))
    if not values:
        return [] if field != "differentiation" else {"support": [], "enrichment": []}
    if len(values) == 1:
        return values[0][2]
    return [
        {"canonical_ref": ref, "label": label, "value": value}
        for ref, label, value in values
    ]


def expected_value(entry: dict[str, Any], canonical: dict[str, dict[str, Any]]) -> Any:
    answers = combine_by_ref(entry, canonical, "expected_answer")
    if nonempty(answers):
        return answers
    return combine_by_ref(entry, canonical, "expected_response")


def fragment_statuses(paths: list[Path]) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in paths:
        doc = read_json(path)
        status = str(doc.get("scope", {}).get("status") or "REVIEW_REQUIRED")
        for entry in doc.get("entries", []):
            mirror_id = str(entry["mirror_id"])
            if mirror_id in result:
                raise ValueError(f"duplicate mirror_id across fragments: {mirror_id}")
            result[mirror_id] = status
    return result


def section_metadata(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for order, section in enumerate(manifest.get("sections", []), start=1):
        rows.append(
            {
                "section_id": section["section_id"],
                "section_order": order,
                "title": section.get("title") or section["section_id"],
                "section_type": section.get("section_type") or "CONTENT",
                "printed_page_range": section.get("printed_page_range"),
                "content_status": section.get("content_status") or "REVIEW_REQUIRED",
                "block_id": section.get("block_id"),
                "activity_refs": section.get("activity_refs", []),
                "outcome_refs": section.get("outcome_refs", []),
            }
        )
    return rows


def export_theme(root: Path, theme_no: int) -> dict[str, Any]:
    theme_id = f"TEMA_{theme_no:02d}"
    base = root / "courses" / "TDE_11" / "teacher_guide" / theme_id
    mirror_path = base / "book_mirror_v23.json"
    manifest_path = base / "teacher_guide.json"
    mirror_paths = discover_mirror_paths(mirror_path)
    mirror = merge_mirrors(mirror_paths)
    manifest = read_json(manifest_path)
    if mirror["course_id"] != manifest["course_id"] or mirror["theme_id"] != manifest["theme_id"]:
        raise ValueError(f"mirror/manifest identity mismatch: {theme_id}")

    _, canonical = index_canonical(root, manifest)
    _, registry = load_component_registry(mirror_path, mirror)
    component_count = apply_component_registry(canonical, registry)
    statuses = fragment_statuses(mirror_paths)

    entries: list[dict[str, Any]] = []
    for order, entry in enumerate(mirror["entries"], start=1):
        missing = [ref for ref in entry["canonical_item_refs"] if ref not in canonical]
        if missing:
            raise ValueError(f"unknown canonical refs for {entry['mirror_id']}: {missing}")
        presentation = str(entry["presentation_type"])
        prompt_display = entry.get("prompt_display")
        title = str(prompt_display or entry["book_heading"])
        content_status = "REVIEW_REQUIRED" if statuses[entry["mirror_id"]] == "REVIEW_REQUIRED" else "VERIFIED"
        differentiation = combine_by_ref(entry, canonical, "differentiation", gated=True)
        row = {
            "entry_order": order,
            "mirror_id": entry["mirror_id"],
            "section_id": entry["section_id"],
            "source_unit_id": entry.get("unit_id"),
            "printed_page_range": entry["printed_page_range"],
            "book_heading": entry["book_heading"],
            "presentation_type": presentation,
            "title": title,
            "prompt_display": prompt_display,
            "prompt_mode": entry.get("prompt_mode"),
            "content_status": content_status,
            "fragment_status": statuses[entry["mirror_id"]],
            "source_locator": entry.get("source_locator"),
            "rights_mode": entry.get("rights_mode"),
            "canonical_item_refs": entry["canonical_item_refs"],
            "expected_response": expected_value(entry, canonical),
            "acceptance_criteria": combine_by_ref(entry, canonical, "acceptance_criteria", gated=True),
            "teacher_guidance": entry.get("teacher_note") if nonempty(entry.get("teacher_note")) else [],
            "common_misconceptions": combine_by_ref(entry, canonical, "common_misconceptions", gated=True),
            "assessment_evidence": [],
            "differentiation": differentiation,
            "provenance": {
                "content_class": "OFFICIAL_TEXTBOOK" if not nonempty(entry.get("teacher_note")) else "MIXED",
                "source_locators": [entry.get("source_locator")] if entry.get("source_locator") else [],
                "note": "Teacher Guide V2.3 book-first projection; canonical answer is paired with selective teacher guidance.",
                "source_commit": SOURCE_COMMIT,
                "mirror_id": entry["mirror_id"],
                "canonical_item_refs": entry["canonical_item_refs"],
                "prompt_mode": entry.get("prompt_mode"),
                "rights_mode": entry.get("rights_mode"),
                "fragment_status": statuses[entry["mirror_id"]],
            },
        }
        row["projection_sha256"] = sha256(row)
        entries.append(row)

    questions = [row for row in entries if row["presentation_type"] == "QUESTION"]
    locator_only = [row["mirror_id"] for row in questions if row.get("prompt_mode") == "LOCATOR_ONLY"]
    return {
        "theme_id": theme_id,
        "title": manifest.get("title") or theme_id,
        "scope": mirror["scope"],
        "sections": section_metadata(manifest),
        "guide_principles": mirror.get("guide_principles", []),
        "page_checklist": mirror.get("page_checklist", []),
        "metrics": {
            "mirror_files": len(mirror_paths),
            "entries": len(entries),
            "questions": len(questions),
            "locator_only_questions": len(locator_only),
            "component_registry_entries": component_count,
        },
        "locator_only_question_ids": locator_only,
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        default="courses/TDE_11/teacher_guide/teacher_guide_v23_runtime_export.json",
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    themes = [export_theme(root, n) for n in range(1, 5)]
    totals = {
        "themes": len(themes),
        "entries": sum(theme["metrics"]["entries"] for theme in themes),
        "questions": sum(theme["metrics"]["questions"] for theme in themes),
        "locator_only_questions": sum(theme["metrics"]["locator_only_questions"] for theme in themes),
    }
    if totals != EXPECTED_TOTALS:
        raise SystemExit(f"V2.3 runtime export parity failed: {totals!r} != {EXPECTED_TOTALS!r}")

    payload = {
        "schema_version": "1.0.0",
        "document_type": "TYMM_TEACHER_GUIDE_V23_RUNTIME_EXPORT",
        "course_id": "TDE_11",
        "grade": 11,
        "architecture_version": "2.3.0",
        "source_repository": "knigdelioglu/tymm",
        "source_ref": "teacher-guide-v2.3-book-first",
        "source_commit": SOURCE_COMMIT,
        "projection_policy": "book-first mirror -> canonical/component answer -> selective teacher guidance",
        "totals": totals,
        "themes": themes,
    }
    payload["export_sha256"] = sha256(payload)
    output = root / args.output
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(output.relative_to(root)), "totals": totals, "sha256": payload["export_sha256"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
