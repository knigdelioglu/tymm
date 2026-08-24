#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from process_component_resolver import ProcessComponentError, audit_curriculum, build_catalog_index, read_json


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def outcome_key(row: dict[str, Any]) -> str:
    return str(row.get("outcome_id") or "")


def validate_expanded_contract(
    contract: dict[str, Any],
    audit_by_id: dict[str, dict[str, Any]],
    catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    contract_rows = contract.get("outcomes", [])
    contract_by_id = {outcome_key(row): row for row in contract_rows}
    require(len(contract_by_id) == len(contract_rows), "duplicate outcome_id in process component resolution contract")
    require(set(contract_by_id) == set(audit_by_id), "resolution contract outcome set differs from curriculum outcome set")

    mismatches: list[dict[str, Any]] = []
    for oid in sorted(contract_by_id):
        expected = contract_by_id[oid]
        actual = audit_by_id[oid]
        if expected.get("theme_id") != actual.get("theme_id"):
            mismatches.append({"outcome_id": oid, "field": "theme_id", "expected": expected.get("theme_id"), "actual": actual.get("theme_id")})
        if expected.get("parent_code") != actual.get("outcome_code"):
            mismatches.append({"outcome_id": oid, "field": "parent_code", "expected": expected.get("parent_code"), "actual": actual.get("outcome_code")})
        if expected.get("expected_origin") != actual.get("origin"):
            mismatches.append({"outcome_id": oid, "field": "origin", "expected": expected.get("expected_origin"), "actual": actual.get("origin")})
        if expected.get("effective_count") != actual.get("effective_count"):
            mismatches.append({"outcome_id": oid, "field": "effective_count", "expected": expected.get("effective_count"), "actual": actual.get("effective_count")})
        if expected.get("expected_origin") == "ROOF_INHERITED":
            expected_ref = f"{catalog.get('catalog_id')}#{expected.get('parent_code')}"
            if expected.get("effective_component_ref") != expected_ref:
                mismatches.append({"outcome_id": oid, "field": "effective_component_ref", "expected": expected_ref, "actual": expected.get("effective_component_ref")})
    return mismatches


def validate_compact_contract(
    contract: dict[str, Any],
    audit_by_id: dict[str, dict[str, Any]],
    catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    require(contract.get("outcome_scope") == "ALL_CURRICULUM_OUTCOMES", "compact contract must pin outcome_scope=ALL_CURRICULUM_OUTCOMES")
    catalog_index = build_catalog_index(catalog)
    explicit_ids = set(contract.get("expected_explicit_outcome_ids", []))
    verified_none_ids = set(contract.get("expected_verified_none_outcome_ids", []))
    require(not (explicit_ids & verified_none_ids), "outcome cannot be both explicit and verified-none")
    require(explicit_ids <= set(audit_by_id), "compact contract explicit outcome id is not in curriculum")
    require(verified_none_ids <= set(audit_by_id), "compact contract verified-none outcome id is not in curriculum")

    expected_outcome_ids = contract.get("expected_outcome_ids")
    if expected_outcome_ids is not None:
        require(len(expected_outcome_ids) == len(set(expected_outcome_ids)), "duplicate expected_outcome_ids in compact contract")
        require(set(expected_outcome_ids) == set(audit_by_id), "compact contract expected_outcome_ids differ from curriculum")

    mismatches: list[dict[str, Any]] = []
    for oid, actual in sorted(audit_by_id.items()):
        parent = actual.get("outcome_code")
        if oid in explicit_ids:
            expected_origin = "THEME_EXPLICIT"
            expected_count = actual.get("explicit_count")
        elif oid in verified_none_ids:
            expected_origin = "SOURCE_VERIFIED_NONE"
            expected_count = 0
        else:
            expected_origin = "ROOF_INHERITED"
            roof = catalog_index.get(parent)
            if roof is None:
                mismatches.append({"outcome_id": oid, "field": "roof_parent", "expected": "present", "actual": parent})
                continue
            expected_count = len(roof.get("components", []))

        if actual.get("origin") != expected_origin:
            mismatches.append({"outcome_id": oid, "field": "origin", "expected": expected_origin, "actual": actual.get("origin")})
        if actual.get("effective_count") != expected_count:
            mismatches.append({"outcome_id": oid, "field": "effective_count", "expected": expected_count, "actual": actual.get("effective_count")})
    return mismatches


def gate(root: Path, catalog_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    repo_root = root.parents[1]
    catalog_path = (catalog_path or (repo_root / "courses/TDE_SHARED/curriculum_process_component_catalog.json")).resolve()
    curriculum_path = root / "curriculum_map.json"
    contract_path = root / "curriculum_process_component_resolution.json"

    require(curriculum_path.exists(), f"missing curriculum map: {curriculum_path}")
    require(catalog_path.exists(), f"missing shared roof catalog: {catalog_path}")
    require(contract_path.exists(), f"missing resolution contract: {contract_path}")

    curriculum = read_json(curriculum_path)
    catalog = read_json(catalog_path)
    contract = read_json(contract_path)

    require(contract.get("course_id") == curriculum.get("course_id"), "resolution contract course mismatch")
    require(contract.get("catalog_id") == catalog.get("catalog_id"), "resolution contract catalog mismatch")
    require(contract.get("merge_explicit_with_roof") is False, "explicit and roof components must not be merged")
    require(
        contract.get("legacy_field_semantics", {}).get("meaning") == "THEME_EXPLICIT_ONLY_UNTIL_SCHEMA_RENAME",
        "legacy process_components_verbatim semantics are not pinned",
    )

    audit = audit_curriculum(curriculum, catalog)
    require(audit.get("final") == "PASS", f"process component audit failed: {audit.get('counts')}")

    expected_counts = contract.get("expected_counts", {})
    actual_counts = audit.get("counts", {})
    for key, expected in expected_counts.items():
        require(actual_counts.get(key) == expected, f"process component count mismatch for {key}: actual={actual_counts.get(key)} expected={expected}")

    audit_rows = audit.get("outcomes", [])
    audit_by_id = {outcome_key(row): row for row in audit_rows}
    require(len(audit_by_id) == len(audit_rows), "duplicate outcome_id in process component audit")
    require("" not in audit_by_id, "all curriculum outcomes must have stable outcome_id for process-component gating")

    contract_mode = contract.get("contract_mode") or ("EXPANDED_PER_OUTCOME" if contract.get("outcomes") else "COMPACT_ALL_OUTCOMES")
    if contract_mode == "EXPANDED_PER_OUTCOME":
        mismatches = validate_expanded_contract(contract, audit_by_id, catalog)
    elif contract_mode == "COMPACT_ALL_OUTCOMES":
        mismatches = validate_compact_contract(contract, audit_by_id, catalog)
    else:
        raise AssertionError(f"unknown process-component contract mode: {contract_mode}")

    require(not mismatches, f"process component resolution contract mismatches: {mismatches[:10]}")

    result = {
        "schema_version": "1.1",
        "course_id": curriculum.get("course_id"),
        "catalog_id": catalog.get("catalog_id"),
        "contract_mode": contract_mode,
        "contract_status": "MATCHED",
        "legacy_field_semantics": "THEME_EXPLICIT_ONLY_UNTIL_SCHEMA_RENAME",
        "counts": actual_counts,
        "mismatch_count": 0,
        "final": "PASS",
    }
    out = root / "index/process_component_inheritance_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed TYMM process-component inheritance gate.")
    parser.add_argument("--root", type=Path, default=Path("courses/TDE_9"))
    parser.add_argument("--catalog", type=Path)
    args = parser.parse_args()
    try:
        result = gate(args.root, args.catalog)
    except (AssertionError, ProcessComponentError, OSError, ValueError) as exc:
        print(f"P0 PROCESS COMPONENT GATE: FAIL: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("P0 PROCESS COMPONENT GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
