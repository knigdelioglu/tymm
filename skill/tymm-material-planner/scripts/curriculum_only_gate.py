#!/usr/bin/env python3
"""Fail-closed validation for curriculum-only TYMM course packages.

This gate is intentionally separate from ``generic_p0_course_gate.py``.  It validates
only information that can be established before an official textbook is available
and rejects placeholder textbook/gap/production state created merely to satisfy P0.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

LIFECYCLE = "CURRICULUM_ONLY_AWAITING_TEXTBOOK"
DEFERRED_STATUS = "DEFERRED_UNTIL_OFFICIAL_TEXTBOOK_AVAILABLE"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class CurriculumOnlyGateError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CurriculumOnlyGateError(message)


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"MISSING_REQUIRED_CANONICAL_FILE: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CurriculumOnlyGateError(f"INVALID_JSON: {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verified(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("VERIFIED")


def validate_source_manifest(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    require(manifest.get("overall_status") == LIFECYCLE, "SOURCE_LIFECYCLE_MISMATCH")
    scope = manifest.get("scope", {})
    require(scope.get("curriculum_source_complete") is True, "CURRICULUM_SOURCE_NOT_COMPLETE")
    require(scope.get("curriculum_mapped") is True, "CURRICULUM_NOT_MAPPED")
    require(scope.get("textbook_source_registered") is False, "TEXTBOOK_REGISTERED_IN_CURRICULUM_ONLY_STATE")
    require(scope.get("alignment_performed") is False, "ALIGNMENT_PERFORMED_TOO_EARLY")
    require(scope.get("gap_analysis_performed") is False, "GAP_ANALYSIS_PERFORMED_TOO_EARLY")
    require(scope.get("materials_generated") is False, "MATERIALS_GENERATED_TOO_EARLY")
    require(scope.get("coverage_status") == "NOT_EVALUATED", "COVERAGE_STATUS_MUST_BE_NOT_EVALUATED")
    require(scope.get("gap_status") == "NOT_EVALUATED", "GAP_STATUS_MUST_BE_NOT_EVALUATED")
    require(scope.get("production_status") == "NOT_EVALUATED", "PRODUCTION_STATUS_MUST_BE_NOT_EVALUATED")

    bundle = manifest.get("curriculum_source_bundle", {})
    expected = bundle.get("expected_part_count")
    verified_count = bundle.get("verified_part_count")
    parts = bundle.get("parts", [])
    require(isinstance(expected, int) and expected > 0, "INVALID_EXPECTED_SOURCE_PART_COUNT")
    require(verified_count == expected, "SOURCE_BUNDLE_NOT_FULLY_VERIFIED")
    require(isinstance(parts, list) and len(parts) == expected, "SOURCE_BUNDLE_PART_COUNT_MISMATCH")

    theme_ids: set[str] = set()
    source_ids: set[str] = set()
    fingerprint_rows: list[str] = []
    for part in parts:
        require(isinstance(part, dict), "SOURCE_PART_NOT_OBJECT")
        theme_id = part.get("theme_id")
        source_id = part.get("source_id")
        require(isinstance(theme_id, str) and theme_id, "SOURCE_PART_THEME_ID_MISSING")
        require(isinstance(source_id, str) and source_id, "SOURCE_PART_SOURCE_ID_MISSING")
        require(theme_id not in theme_ids, f"DUPLICATE_SOURCE_THEME_ID: {theme_id}")
        require(source_id not in source_ids, f"DUPLICATE_SOURCE_ID: {source_id}")
        theme_ids.add(theme_id)
        source_ids.add(source_id)
        require(verified(part.get("verification_status")), f"SOURCE_PART_NOT_VERIFIED: {source_id}")
        local_path = part.get("local_path")
        local_sha256 = part.get("sha256")
        require(isinstance(local_path, str) and local_path, f"LOCAL_PATH_MISSING: {source_id}")
        require(isinstance(local_sha256, str) and SHA256_RE.fullmatch(local_sha256), f"SHA256_MISSING_OR_INVALID: {source_id}")
        path = root / local_path
        require(path.is_file(), f"LOCAL_SOURCE_MISSING: {local_path}")
        actual = sha256_file(path)
        require(actual == local_sha256, f"LOCAL_SOURCE_FINGERPRINT_MISMATCH: {local_path}")
        fingerprint_rows.append(f"{theme_id}:{local_sha256}")

    expected_bundle_fp = hashlib.sha256("\n".join(sorted(fingerprint_rows)).encode("utf-8")).hexdigest()
    require(manifest.get("curriculum_source_bundle_sha256") == expected_bundle_fp, "SOURCE_BUNDLE_FINGERPRINT_MISMATCH")

    time_model = manifest.get("annual_time_model", {})
    if time_model:
        tc = time_model.get("theme_count")
        theme_total = time_model.get("theme_total_hours")
        instruction = time_model.get("instructional_hours_per_theme")
        planning = time_model.get("school_based_planning_hours_per_theme")
        require(tc == expected, "TIME_MODEL_THEME_COUNT_MISMATCH")
        require(theme_total == instruction + planning, "TIME_MODEL_THEME_TOTAL_MISMATCH")
        require(time_model.get("annual_instructional_hours") == tc * instruction, "ANNUAL_INSTRUCTIONAL_HOURS_MISMATCH")
        require(time_model.get("annual_school_based_planning_hours") == tc * planning, "ANNUAL_PLANNING_HOURS_MISMATCH")
        require(time_model.get("annual_total_hours") == tc * theme_total, "ANNUAL_TOTAL_HOURS_MISMATCH")

    deferred = set(manifest.get("deferred_stages", []))
    required_deferred = {
        "TEXTBOOK_MAP", "TEXTBOOK_FORMS_INDEX", "TEXTBOOK_COVERAGE", "ALIGNMENT",
        "GAP_ANALYSIS", "RESOURCE_PLAN", "PRODUCTION_ARTIFACT_REGISTRY",
        "FULL_P0_TEXTBOOK_RUNTIME", "PRODUCTION_GATE",
    }
    require(required_deferred.issubset(deferred), "DEFERRED_STAGE_SET_INCOMPLETE")
    return {
        "source_parts": expected,
        "source_theme_ids": sorted(theme_ids),
        "bundle_sha256": expected_bundle_fp,
        "status": "PASS",
    }


def validate_curriculum(root: Path, manifest: dict[str, Any], curriculum: dict[str, Any]) -> dict[str, Any]:
    require(curriculum.get("course_id") == manifest.get("course_id"), "COURSE_ID_MISMATCH")
    require(curriculum.get("lifecycle_status") == LIFECYCLE, "CURRICULUM_LIFECYCLE_MISMATCH")
    require(verified(curriculum.get("verification_status")), "CURRICULUM_NOT_VERIFIED")
    require(str(curriculum.get("canonical_freeze_status", "")).startswith("FROZEN"), "CURRICULUM_NOT_FROZEN")

    manifest_parts = {p["theme_id"]: p for p in manifest["curriculum_source_bundle"]["parts"]}
    themes = curriculum.get("themes", [])
    require(isinstance(themes, list), "THEMES_NOT_LIST")
    require(len(themes) == len(manifest_parts), "CURRICULUM_THEME_COUNT_MISMATCH")

    stable_keys: set[str] = set()
    assessment_ids: set[str] = set()
    outcomes = 0
    assessments = 0
    source_refs = 0
    synthetic_subcodes: list[str] = []

    explicit_subcomponent_state = curriculum.get("source_validation", {}).get("explicit_subcomponent_id_scan", "")
    no_explicit_subcomponents = "NONE_EXPLICIT" in str(explicit_subcomponent_state)

    for theme in themes:
        theme_id = theme.get("theme_id")
        require(theme_id in manifest_parts, f"UNKNOWN_THEME_ID: {theme_id}")
        part = manifest_parts[theme_id]
        require(theme.get("source_id") == part.get("source_id"), f"THEME_SOURCE_ID_MISMATCH: {theme_id}")
        require(isinstance(theme.get("exact_theme_name"), str) and theme.get("exact_theme_name"), f"THEME_NAME_MISSING: {theme_id}")
        require(isinstance(theme.get("source_locator"), str) and theme.get("source_locator"), f"THEME_SOURCE_LOCATOR_MISSING: {theme_id}")
        source_refs += 1

        local = theme.get("local_source_snapshot", {})
        require(local.get("filename") == part.get("local_filename"), f"LOCAL_SNAPSHOT_FILENAME_MISMATCH: {theme_id}")
        require(local.get("sha256") == part.get("sha256"), f"LOCAL_SNAPSHOT_SHA256_MISMATCH: {theme_id}")

        hours = theme.get("allocated_lesson_hours", {})
        require(isinstance(hours.get("instructional_total"), int), f"INSTRUCTIONAL_HOURS_MISSING: {theme_id}")
        require(str(hours.get("verbatim", "")), f"INSTRUCTIONAL_HOURS_VERBATIM_MISSING: {theme_id}")
        require(isinstance(hours.get("source_locator"), str) and hours.get("source_locator"), f"HOURS_SOURCE_LOCATOR_MISSING: {theme_id}")
        planning = hours.get("planning_layer", {})
        manifest_time = manifest.get("annual_time_model", {})
        if manifest_time:
            require(planning.get("school_based_planning_hours") == manifest_time.get("school_based_planning_hours_per_theme"), f"PLANNING_HOURS_MISMATCH: {theme_id}")
            require(planning.get("theme_total_hours") == manifest_time.get("theme_total_hours"), f"THEME_TOTAL_HOURS_MISMATCH: {theme_id}")
            require(planning.get("authority") == "USER_CONFIRMED_PLANNING_RULE", f"PLANNING_AUTHORITY_MISMATCH: {theme_id}")

        process_policy = theme.get("process_component_policy", {})
        require(process_policy.get("canonical_policy") == "DO_NOT_SYNTHESIZE_OR_COPY_FROM_OTHER_GRADES", f"PROCESS_POLICY_MISSING: {theme_id}")
        normative_ref = theme.get("normative_text_evidence", {})
        require(normative_ref.get("status") == "VERIFIED_LOCAL_PDF_TEXT_EXTRACTION", f"NORMATIVE_TEXT_EVIDENCE_NOT_VERIFIED: {theme_id}")
        evidence_file = normative_ref.get("canonical_evidence_file")
        require(isinstance(evidence_file, str) and (root / evidence_file).is_file(), f"NORMATIVE_EVIDENCE_FILE_MISSING: {theme_id}")

        rows = theme.get("learning_outcomes", [])
        require(isinstance(rows, list) and rows, f"NO_OUTCOMES: {theme_id}")
        for row in rows:
            outcomes += 1
            code = row.get("outcome_code")
            text = row.get("outcome_verbatim")
            stable = row.get("stable_entity_key")
            locator = row.get("source_locator")
            require(isinstance(code, str) and code, f"OUTCOME_CODE_MISSING: {theme_id}")
            require(isinstance(text, str) and text.strip(), f"OUTCOME_VERBATIM_MISSING: {theme_id}/{code}")
            require(row.get("theme_scope") == theme_id, f"OUTCOME_SCOPE_MISMATCH: {theme_id}/{code}")
            require(isinstance(locator, str) and locator, f"OUTCOME_LOCATOR_MISSING: {theme_id}/{code}")
            require(verified(row.get("verification_status")), f"OUTCOME_NOT_VERIFIED: {theme_id}/{code}")
            require(isinstance(stable, str) and stable, f"OUTCOME_STABLE_KEY_MISSING: {theme_id}/{code}")
            require(stable not in stable_keys, f"DUPLICATE_CANONICAL_KEY: {stable}")
            stable_keys.add(stable)
            require(theme_id in stable and code in stable, f"OUTCOME_STABLE_KEY_SCOPE_UNSAFE: {stable}")
            source_refs += 1
            if no_explicit_subcomponents and code.count(".") > 1:
                synthetic_subcodes.append(code)

        ars = theme.get("assessment_requirements", [])
        require(isinstance(ars, list), f"ASSESSMENT_REQUIREMENTS_NOT_LIST: {theme_id}")
        for row in ars:
            assessments += 1
            aid = row.get("assessment_id")
            require(isinstance(aid, str) and aid, f"ASSESSMENT_ID_MISSING: {theme_id}")
            require(aid not in assessment_ids, f"DUPLICATE_ASSESSMENT_ID: {aid}")
            assessment_ids.add(aid)
            require(isinstance(row.get("requirement"), str) and row.get("requirement"), f"ASSESSMENT_REQUIREMENT_MISSING: {aid}")
            require(isinstance(row.get("source_locator"), str) and row.get("source_locator"), f"ASSESSMENT_LOCATOR_MISSING: {aid}")
            source_refs += 1

    require(not synthetic_subcodes, f"SYNTHETIC_SUBCODES_DETECTED: {synthetic_subcodes}")

    scope = curriculum.get("scope_summary", {})
    require(scope.get("total_learning_outcomes") == outcomes, "OUTCOME_COUNT_SUMMARY_MISMATCH")
    mt = manifest.get("annual_time_model", {})
    if mt:
        require(scope.get("theme_total_hours_with_school_based_planning") == mt.get("theme_total_hours"), "MAP_TIME_MODEL_NOT_SYNCED")
        require(scope.get("school_based_planning_hours_per_theme") == mt.get("school_based_planning_hours_per_theme"), "MAP_PLANNING_MODEL_NOT_SYNCED")
        require(scope.get("annual_total_hours_with_school_based_planning") == mt.get("annual_total_hours"), "MAP_ANNUAL_TIME_MODEL_NOT_SYNCED")

    evidence = read_json(root / "curriculum_normative_text.json")
    require(evidence.get("course_id") == curriculum.get("course_id"), "NORMATIVE_EVIDENCE_COURSE_MISMATCH")
    evidence_themes = {t.get("theme_id"): t for t in evidence.get("themes", [])}
    require(set(evidence_themes) == set(manifest_parts), "NORMATIVE_EVIDENCE_THEME_SET_MISMATCH")
    for theme_id, part in manifest_parts.items():
        row = evidence_themes[theme_id]
        require(row.get("source_sha256") == part.get("sha256"), f"NORMATIVE_EVIDENCE_FINGERPRINT_MISMATCH: {theme_id}")
        require(isinstance(row.get("pages"), list) and row.get("pages"), f"NORMATIVE_EVIDENCE_PAGES_MISSING: {theme_id}")

    return {
        "themes": len(themes),
        "outcomes": outcomes,
        "assessment_requirements": assessments,
        "unique_canonical_keys": len(stable_keys),
        "source_locators_checked": source_refs,
        "synthetic_subcodes": 0,
        "status": "PASS",
    }


def validate_fail_closed_lifecycle(root: Path) -> dict[str, Any]:
    forbidden_files = [
        root / "textbook_map.json",
        root / "textbook_forms_index.json",
        root / "production" / "production_manifest.json",
        root / "production" / "assessment_artifact_registry.json",
        root / "production" / "assessment_design_contract.json",
    ]
    present_forbidden = [str(p.relative_to(root)) for p in forbidden_files if p.exists()]
    require(not present_forbidden, f"PREMATURE_TEXTBOOK_OR_PRODUCTION_FILES: {present_forbidden}")

    premature_patterns = [
        "themes/tema_*/alignment.json",
        "themes/tema_*/gap_analysis.json",
        "themes/tema_*/resource_plan.json",
        "generated/*/artifact.json",
    ]
    present: list[str] = []
    for pattern in premature_patterns:
        present.extend(str(p.relative_to(root)) for p in root.glob(pattern))
    require(not present, f"PREMATURE_DERIVED_OR_GENERATED_STATE: {present}")
    return {"premature_files": 0, "status": "PASS"}


def run(root: Path) -> dict[str, Any]:
    manifest = read_json(root / "source_manifest.json")
    curriculum = read_json(root / "curriculum_map.json")
    source = validate_source_manifest(root, manifest)
    canonical = validate_curriculum(root, manifest, curriculum)
    lifecycle = validate_fail_closed_lifecycle(root)
    return {
        "course_id": manifest.get("course_id"),
        "lifecycle_status": LIFECYCLE,
        "source": source,
        "canonical": canonical,
        "lifecycle_safety": lifecycle,
        "textbook_status": "AWAITING_OFFICIAL_TEXTBOOK",
        "coverage_status": "NOT_EVALUATED",
        "gap_status": "NOT_EVALUATED",
        "production_status": "NOT_EVALUATED",
        "full_p0_status": DEFERRED_STATUS,
        "final": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--knowledge-root",
        default=os.environ.get("TYMM_KNOWLEDGE_ROOT"),
        help="Course root, e.g. courses/TDE_11. Can also be set with TYMM_KNOWLEDGE_ROOT.",
    )
    parser.add_argument("--report", help="Optional JSON report output path")
    args = parser.parse_args()
    require(bool(args.knowledge_root), "KNOWLEDGE_ROOT_REQUIRED")
    root = Path(args.knowledge_root).resolve()
    require(root.is_dir(), f"KNOWLEDGE_ROOT_NOT_FOUND: {root}")
    report = run(root)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    print(text, end="")
    print(f"CURRICULUM-ONLY GATE: PASS ({report['course_id']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
