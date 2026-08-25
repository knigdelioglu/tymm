#!/usr/bin/env python3
"""Validate P7 structured grounding for form/resource/artifact references."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from apply_grounded_references import build_grounding, load_catalogs, prose_strings, read_json


def _duplicate_key(items: Any, key: str) -> bool:
    if not isinstance(items, list):
        return False
    values = [item.get(key) for item in items if isinstance(item, dict)]
    return len(values) != len(set(values))


def _unverified_equivalence_artifacts(catalogs: dict[str, Any], plan: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for artifact_id, artifact in catalogs["artifacts"].items():
        for binding in artifact.get("task_bindings", []):
            if not isinstance(binding, dict) or binding.get("block_id") != plan.get("block_id"):
                continue
            status = str(binding.get("source_equivalence_status") or "").upper()
            if "UNVERIFIED" in status or "UNRESOLVED" in status:
                result.add(artifact_id)
    return result


def _has_forbidden_equivalence_claim(plan: dict[str, Any], artifact_ids: set[str]) -> bool:
    if not artifact_ids:
        return False
    markers = (
        "eba ile aynı", "eba'nın aynısı", "eba’nın aynısı", "birebir eba",
        "resmî eba rubriğinin aynısı", "resmi eba rubriğinin aynısı",
        "verbatim eba", "eba rubriğini birebir",
    )
    for text in prose_strings(plan):
        lowered = text.lower()
        if any(artifact_id in text for artifact_id in artifact_ids) and any(marker in lowered for marker in markers):
            return True
    return False


def validate_plan(root: Path, plan: dict[str, Any], catalogs: dict[str, Any] | None = None) -> list[str]:
    catalogs = catalogs or load_catalogs(root)
    errors: list[str] = []
    try:
        expected = build_grounding(plan, catalogs)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    actual = plan.get("grounded_references")
    if expected is None:
        if actual is not None:
            errors.append("GROUNDING_PRESENT_WITHOUT_CANONICAL_REFERENCE")
        return errors
    if not isinstance(actual, dict):
        errors.append("GROUNDED_REFERENCES_REQUIRED")
        return errors

    for key in ("form_refs", "assessment_artifact_refs", "resource_refs"):
        if not isinstance(actual.get(key), list):
            errors.append(f"GROUNDING_{key.upper()}_NOT_LIST")
    if errors:
        return errors

    if _duplicate_key(actual["form_refs"], "form_id"):
        errors.append("GROUNDING_FORM_REF_DUPLICATE")
    if _duplicate_key(actual["assessment_artifact_refs"], "artifact_id"):
        errors.append("GROUNDING_ARTIFACT_REF_DUPLICATE")
    if _duplicate_key(actual["resource_refs"], "resource_plan_id"):
        errors.append("GROUNDING_RESOURCE_REF_DUPLICATE")

    if actual != expected:
        expected_forms = {item["form_id"]: item for item in expected["form_refs"]}
        actual_forms = {
            item.get("form_id"): item for item in actual["form_refs"] if isinstance(item, dict)
        }
        for form_id, expected_ref in expected_forms.items():
            actual_ref = actual_forms.get(form_id)
            if actual_ref is None:
                errors.append(f"FORM_REFERENCE_NOT_GROUNDED:{form_id}")
            elif actual_ref != expected_ref:
                errors.append(f"FORM_REFERENCE_USAGE_MISMATCH:{form_id}:{actual_ref.get('usage')}!={expected_ref['usage']}")

        expected_artifacts = {item["artifact_id"]: item for item in expected["assessment_artifact_refs"]}
        actual_artifacts = {
            item.get("artifact_id"): item for item in actual["assessment_artifact_refs"] if isinstance(item, dict)
        }
        for artifact_id, expected_ref in expected_artifacts.items():
            actual_ref = actual_artifacts.get(artifact_id)
            if actual_ref is None:
                errors.append(f"ARTIFACT_REFERENCE_NOT_GROUNDED:{artifact_id}")
            elif actual_ref.get("binding_key") != expected_ref["binding_key"]:
                errors.append(
                    f"ARTIFACT_BINDING_KEY_MISMATCH:{artifact_id}:{actual_ref.get('binding_key')}!={expected_ref['binding_key']}"
                )
            elif actual_ref.get("usage") != expected_ref["usage"]:
                errors.append(
                    f"ARTIFACT_REFERENCE_USAGE_MISMATCH:{artifact_id}:{actual_ref.get('usage')}!={expected_ref['usage']}"
                )

        expected_resources = {item["resource_plan_id"]: item for item in expected["resource_refs"]}
        actual_resources = {
            item.get("resource_plan_id"): item for item in actual["resource_refs"] if isinstance(item, dict)
        }
        for resource_id, expected_ref in expected_resources.items():
            actual_ref = actual_resources.get(resource_id)
            if actual_ref is None:
                errors.append(f"RESOURCE_REFERENCE_NOT_GROUNDED:{resource_id}")
            elif actual_ref != expected_ref:
                errors.append(
                    f"RESOURCE_REFERENCE_USAGE_MISMATCH:{resource_id}:{actual_ref.get('usage')}!={expected_ref['usage']}"
                )

        extra_forms = sorted(set(actual_forms) - set(expected_forms))
        extra_artifacts = sorted(set(actual_artifacts) - set(expected_artifacts))
        extra_resources = sorted(set(actual_resources) - set(expected_resources))
        if extra_forms:
            errors.append(f"UNJUSTIFIED_FORM_REFERENCES:{extra_forms}")
        if extra_artifacts:
            errors.append(f"UNJUSTIFIED_ARTIFACT_REFERENCES:{extra_artifacts}")
        if extra_resources:
            errors.append(f"UNJUSTIFIED_RESOURCE_REFERENCES:{extra_resources}")

    unverified = _unverified_equivalence_artifacts(catalogs, plan)
    if _has_forbidden_equivalence_claim(plan, unverified):
        errors.append("UNVERIFIED_EXTERNAL_ASSESSMENT_EQUIVALENCE_CLAIM")
    return errors


def validate_course(root: Path) -> dict[str, Any]:
    catalogs = load_catalogs(root)
    manifest_path = root / "production" / "grounded_reference_manifest.json"
    if not manifest_path.exists():
        return {"status": "FAIL", "course_id": root.name, "errors": ["GROUNDING_MANIFEST_MISSING"]}
    manifest = read_json(manifest_path)
    errors: list[str] = []
    generated = root / "generated" / "lesson_plans"
    packages: list[dict[str, Any]] = []
    totals = {"form_refs": 0, "assessment_artifact_refs": 0, "resource_refs": 0}
    usage_counts = {"DEFERRED": 0, "REFERENCE_ONLY": 0, "USED": 0}

    for path in sorted(generated.rglob("*.json")):
        plan = read_json(path)
        plan_errors = validate_plan(root, plan, catalogs)
        relative = path.relative_to(root).as_posix()
        errors.extend(f"{path.stem}:{error}" for error in plan_errors)
        grounding = plan.get("grounded_references")
        if not isinstance(grounding, dict):
            continue
        row = {
            "package_id": path.stem,
            "path": relative,
            "theme_id": plan.get("theme_id"),
            "block_id": plan.get("block_id"),
            "form_refs": len(grounding.get("form_refs", [])),
            "assessment_artifact_refs": len(grounding.get("assessment_artifact_refs", [])),
            "resource_refs": len(grounding.get("resource_refs", [])),
        }
        packages.append(row)
        for key in totals:
            refs = grounding.get(key, [])
            totals[key] += len(refs) if isinstance(refs, list) else 0
            if isinstance(refs, list):
                for ref in refs:
                    if isinstance(ref, dict) and ref.get("usage") in usage_counts:
                        usage_counts[ref["usage"]] += 1

    expected_summary = {
        "target_packages": len(packages),
        **totals,
        "usage_counts": usage_counts,
    }
    if manifest.get("schema_version") != "1.0.0":
        errors.append(f"GROUNDING_MANIFEST_SCHEMA_INVALID:{manifest.get('schema_version')}")
    if manifest.get("course_id") != root.name:
        errors.append(f"GROUNDING_MANIFEST_COURSE_MISMATCH:{manifest.get('course_id')}")
    if manifest.get("summary") != expected_summary:
        errors.append(f"GROUNDING_MANIFEST_SUMMARY_MISMATCH:{manifest.get('summary')}!={expected_summary}")
    if manifest.get("packages") != packages:
        errors.append("GROUNDING_MANIFEST_PACKAGE_SET_MISMATCH")
    policy = manifest.get("policy", {})
    required_policy = {
        "canonical_reference_ids_must_not_remain_prose_only": True,
        "used_forms_require_structured_used_reference": True,
        "artifact_binding_key_required": True,
        "resource_theme_binding_required": True,
        "mutable_lifecycle_metadata_not_duplicated_into_plan_refs": True,
    }
    if policy != required_policy:
        errors.append("GROUNDING_MANIFEST_POLICY_MISMATCH")

    return {
        "status": "PASS" if not errors else "FAIL",
        "course_id": root.name,
        "errors": errors,
        "summary": expected_summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    args = parser.parse_args()
    try:
        results = [validate_course(Path(root)) for root in args.knowledge_root]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    status = "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL"
    print(json.dumps({"status": status, "courses": results}, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
