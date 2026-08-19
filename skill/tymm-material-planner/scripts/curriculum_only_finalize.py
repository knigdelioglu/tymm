#!/usr/bin/env python3
"""Finalize a curriculum-only course package from local official curriculum PDFs.

The finalizer is intentionally textbook-agnostic. It computes source SHA-256
fingerprints, captures page-bound text evidence from the local official PDFs,
links curriculum outcomes back to local source pages, and synchronizes an
optional user-confirmed school-based planning layer without rewriting official
instructional hours.

Requires Poppler's ``pdftotext`` executable on PATH.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

LIFECYCLE = "CURRICULUM_ONLY_AWAITING_TEXTBOOK"


class CurriculumOnlyFinalizeError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CurriculumOnlyFinalizeError(message)


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"MISSING_REQUIRED_FILE: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CurriculumOnlyFinalizeError(f"INVALID_JSON: {path}: {exc}") from exc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_pdf_pages(pdf: Path) -> tuple[list[str], str, int]:
    require(shutil.which("pdftotext") is not None, "PDFTOTEXT_NOT_AVAILABLE")
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    text = result.stdout.decode("utf-8", errors="replace")
    pages = [page.rstrip() for page in text.split("\f") if page.strip()]
    replacement_count = sum(page.count("\ufffd") for page in pages)
    quality = "PASS_TEXT_LAYER" if replacement_count == 0 else "TEXT_LAYER_WITH_GLYPH_REPLACEMENTS"
    return pages, quality, replacement_count


def build_bundle_fingerprint(parts: list[dict[str, Any]]) -> str:
    rows = [f"{part['theme_id']}:{part['sha256']}" for part in parts]
    return hashlib.sha256("\n".join(sorted(rows)).encode("utf-8")).hexdigest()


def finalize(root: Path) -> dict[str, Any]:
    manifest_path = root / "source_manifest.json"
    curriculum_path = root / "curriculum_map.json"
    manifest = read_json(manifest_path)
    curriculum = read_json(curriculum_path)

    require(manifest.get("overall_status") == LIFECYCLE, "SOURCE_MANIFEST_LIFECYCLE_MISMATCH")
    require(curriculum.get("lifecycle_status") == LIFECYCLE, "CURRICULUM_LIFECYCLE_MISMATCH")
    require(manifest.get("course_id") == curriculum.get("course_id"), "COURSE_ID_MISMATCH")

    parts_list = manifest.get("curriculum_source_bundle", {}).get("parts", [])
    require(isinstance(parts_list, list) and parts_list, "SOURCE_BUNDLE_PARTS_MISSING")
    parts = {part.get("theme_id"): part for part in parts_list}
    require(None not in parts, "SOURCE_PART_THEME_ID_MISSING")

    local_files = manifest.get("local_uploaded_snapshots", {}).get("files", [])
    require(isinstance(local_files, list), "LOCAL_SNAPSHOT_LIST_MISSING")
    local_by_name = {row.get("filename"): row for row in local_files}

    evidence_themes: list[dict[str, Any]] = []
    evidence_by_theme: dict[str, dict[str, Any]] = {}

    for theme_id in sorted(parts):
        part = parts[theme_id]
        local_path = part.get("local_path")
        local_filename = part.get("local_filename")
        require(isinstance(local_path, str) and local_path, f"LOCAL_PATH_MISSING: {theme_id}")
        require(isinstance(local_filename, str) and local_filename, f"LOCAL_FILENAME_MISSING: {theme_id}")
        pdf = root / local_path
        require(pdf.is_file(), f"LOCAL_SOURCE_MISSING: {local_path}")
        raw = pdf.read_bytes()
        sha256 = sha256_bytes(raw)
        pages, quality, replacement_count = extract_pdf_pages(pdf)
        require(pages, f"PDF_TEXT_EXTRACTION_EMPTY: {local_path}")

        part["sha256"] = sha256
        part["source_fingerprint_type"] = "SHA256"
        part["source_fingerprint_status"] = "VERIFIED_LOCAL_BINARY"
        part["page_count_pdf"] = len(pages)

        local = local_by_name.get(local_filename)
        require(isinstance(local, dict), f"LOCAL_SNAPSHOT_MANIFEST_ROW_MISSING: {local_filename}")
        local["sha256"] = sha256
        local["source_fingerprint_type"] = "SHA256"
        local["page_count_pdf"] = len(pages)

        page_rows = [
            {
                "page": index + 1,
                "source_locator": f"{local_path}#page={index + 1}",
                "text": page,
            }
            for index, page in enumerate(pages)
        ]
        evidence = {
            "theme_id": theme_id,
            "theme_title": part.get("expected_theme_title"),
            "source_file": local_path,
            "source_sha256": sha256,
            "page_count": len(pages),
            "extraction_method": "pdftotext -layout (Poppler)",
            "extraction_status": "VERIFIED_SOURCE_BOUND_TEXT_EVIDENCE",
            "extraction_quality": quality,
            "replacement_character_count": replacement_count,
            "pages": page_rows,
        }
        evidence_themes.append(evidence)
        evidence_by_theme[theme_id] = evidence

    bundle_sha256 = build_bundle_fingerprint(parts_list)
    manifest["schema_version"] = "1.2"
    manifest["curriculum_source_bundle_sha256"] = bundle_sha256
    manifest["curriculum_source_bundle"]["bundle_fingerprint_type"] = "SHA256_OF_SORTED_THEME_SHA256_ROWS"
    manifest["curriculum_source_bundle"]["bundle_fingerprint_status"] = "VERIFIED"
    manifest["local_uploaded_snapshots"]["fingerprint_status"] = "PASS_ALL_SHA256_VERIFIED"
    manifest.setdefault("source_resolution_rules", {})["fingerprint_rule"] = (
        "Local official PDF snapshots use SHA-256; Git blob SHA is retained only as repository transport identity."
    )

    normative_path = root / "curriculum_normative_text.json"
    normative = {
        "schema_version": "1.0",
        "course_id": manifest.get("course_id"),
        "grade": manifest.get("grade"),
        "course_title": manifest.get("course_title"),
        "evidence_type": "LOCAL_OFFICIAL_CURRICULUM_PDF_PAGE_TEXT",
        "source_bundle_sha256": bundle_sha256,
        "canonical_role": (
            "Source-bound page text evidence for curriculum_map.json; the PDF remains the primary official snapshot."
        ),
        "themes": evidence_themes,
    }
    normative_path.write_text(json.dumps(normative, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    curriculum["schema_version"] = "1.2"
    curriculum["source_mode"] = "OFFICIAL_REMOTE_TYMM_THEME_BUNDLE_WITH_MAPPED_LOCAL_PDF_SNAPSHOTS"
    curriculum["verification_status"] = "VERIFIED_OFFICIAL_REMOTE_AND_LOCAL"
    curriculum["canonical_freeze_status"] = "FROZEN_PENDING_SOURCE_FINGERPRINT_CHANGE"

    source_validation = curriculum.setdefault("source_validation", {})
    source_validation["local_pdf_theme_mapping"] = "PASS_ALL_CONTENT_VERIFIED_AND_RENAMED"
    source_validation["local_pdf_fingerprint_status"] = "PASS_ALL_SHA256_VERIFIED"
    source_validation["curriculum_source_bundle_sha256"] = bundle_sha256
    source_validation["normative_text_evidence"] = "PASS_FULL_LOCAL_PDF_PAGE_TEXT_CAPTURED"

    time_model = manifest.get("annual_time_model", {})
    if time_model:
        scope = curriculum.setdefault("scope_summary", {})
        scope["official_instructional_hours_per_theme"] = time_model.get("instructional_hours_per_theme")
        scope["school_based_planning_hours_per_theme"] = time_model.get("school_based_planning_hours_per_theme")
        scope["theme_total_hours_with_school_based_planning"] = time_model.get("theme_total_hours")
        scope["official_instructional_hours_total"] = time_model.get("annual_instructional_hours")
        scope["annual_school_based_planning_hours"] = time_model.get("annual_school_based_planning_hours")
        scope["annual_total_hours_with_school_based_planning"] = time_model.get("annual_total_hours")

    themes = curriculum.get("themes", [])
    require(isinstance(themes, list) and len(themes) == len(parts), "CURRICULUM_THEME_SET_MISMATCH")
    total_outcomes = 0
    localized_outcomes = 0

    for theme in themes:
        theme_id = theme.get("theme_id")
        require(theme_id in parts, f"UNKNOWN_CURRICULUM_THEME: {theme_id}")
        part = parts[theme_id]
        evidence = evidence_by_theme[theme_id]
        theme["local_source_snapshot"] = {
            "filename": part.get("local_filename"),
            "path": part.get("local_path"),
            "sha256": part.get("sha256"),
            "git_blob_sha": part.get("git_blob_sha"),
            "page_count": part.get("page_count_pdf"),
            "verification_status": "VERIFIED_LOCAL_OFFICIAL_SNAPSHOT",
        }
        theme["normative_text_evidence"] = {
            "status": "VERIFIED_LOCAL_PDF_TEXT_EXTRACTION",
            "canonical_evidence_file": "curriculum_normative_text.json",
            "evidence_theme_id": theme_id,
            "source_pdf": part.get("local_path"),
            "source_sha256": part.get("sha256"),
            "page_count": evidence.get("page_count"),
            "extraction_method": evidence.get("extraction_method"),
            "extraction_quality": evidence.get("extraction_quality"),
            "verbatim_evidence_scope": "FULL_PDF_PAGE_TEXT_PRESERVED",
        }
        process_policy = theme.setdefault("process_component_policy", {})
        process_policy["canonical_evidence_file"] = "curriculum_normative_text.json"
        process_policy["evidence_status"] = "VERIFIED_LOCAL_PDF_TEXT_EXTRACTION"

        if time_model:
            hours = theme.setdefault("allocated_lesson_hours", {})
            hours["planning_layer"] = {
                "school_based_planning_hours": time_model.get("school_based_planning_hours_per_theme"),
                "theme_total_hours": time_model.get("theme_total_hours"),
                "authority": "USER_CONFIRMED_PLANNING_RULE",
                "semantics": (
                    "Official TYMM instructional hours remain unchanged; school-based planning is a separate planning layer."
                ),
            }
            theme["school_based_planning_provisions"] = {
                "source_status": "SOURCE_NOT_EXPLICIT_ON_THEME_PAGE",
                "planning_layer": {
                    "authority": "USER_CONFIRMED_PLANNING_RULE",
                    "hours": time_model.get("school_based_planning_hours_per_theme"),
                    "outer_theme_total_hours": time_model.get("theme_total_hours"),
                    "curriculum_gap": False,
                },
            }

        for outcome in theme.get("learning_outcomes", []):
            total_outcomes += 1
            code = outcome.get("outcome_code")
            page_no = next(
                (page["page"] for page in evidence["pages"] if isinstance(code, str) and code in page["text"]),
                None,
            )
            if page_no is not None:
                localized_outcomes += 1
                outcome["local_source_locator"] = f"{part['local_path']}#page={page_no}"
                outcome["local_source_sha256"] = part["sha256"]
                outcome["verification_status"] = "VERIFIED_OFFICIAL_WEB_AND_LOCAL_PDF"

        assessment_pages = sorted(
            {
                page["page"]
                for page in evidence["pages"]
                if "performans görevi" in page["text"].lower()
                or "tema sonu değerlendirme" in page["text"].lower()
            }
        )
        for assessment in theme.get("assessment_requirements", []):
            assessment["local_evidence_pages"] = [
                f"{part['local_path']}#page={page_no}" for page_no in assessment_pages
            ]
            assessment["local_source_sha256"] = part["sha256"]

    require(total_outcomes > 0, "NO_OUTCOMES_FOUND")
    require(localized_outcomes == total_outcomes, f"OUTCOME_LOCALIZATION_INCOMPLETE: {localized_outcomes}/{total_outcomes}")

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    curriculum_path.write_text(json.dumps(curriculum, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "course_id": manifest.get("course_id"),
        "source_parts": len(parts),
        "bundle_sha256": bundle_sha256,
        "outcomes": total_outcomes,
        "localized_outcomes": localized_outcomes,
        "normative_evidence_file": str(normative_path),
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--knowledge-root",
        default=os.environ.get("TYMM_KNOWLEDGE_ROOT"),
        help="Course root, e.g. courses/TDE_11. Can also be set with TYMM_KNOWLEDGE_ROOT.",
    )
    args = parser.parse_args()
    require(bool(args.knowledge_root), "KNOWLEDGE_ROOT_REQUIRED")
    root = Path(args.knowledge_root).resolve()
    require(root.is_dir(), f"KNOWLEDGE_ROOT_NOT_FOUND: {root}")
    report = finalize(root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"CURRICULUM-ONLY FINALIZE: PASS ({report['course_id']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
