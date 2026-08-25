#!/usr/bin/env python3
"""Validate P6 classroom adaptation coverage and evidence-preserving fallback contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from apply_classroom_adaptations import detect_triggers, media_types


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def error(errors: list[str], code: str, detail: Any | None = None) -> None:
    errors.append(code if detail is None else f"{code}:{detail}")


def _nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _validate_adaptation(
    package_id: str,
    plan: dict[str, Any],
    triggers: list[str],
    errors: list[str],
) -> None:
    prefix = f"{package_id}:"
    adaptation = plan.get("classroom_adaptations")
    if not isinstance(adaptation, dict):
        error(errors, prefix + "CLASSROOM_ADAPTATIONS_REQUIRED")
        return

    declared = adaptation.get("trigger_categories")
    if not isinstance(declared, list) or declared != triggers:
        error(errors, prefix + "TRIGGER_CATEGORIES_MISMATCH", declared)

    justification = adaptation.get("justification")
    if not isinstance(justification, str) or not justification.strip():
        error(errors, prefix + "JUSTIFICATION_REQUIRED")

    differentiation = adaptation.get("differentiation")
    if not isinstance(differentiation, dict):
        error(errors, prefix + "DIFFERENTIATION_REQUIRED")
    else:
        if not _nonempty_string_list(differentiation.get("scaffold_route")):
            error(errors, prefix + "SCAFFOLD_ROUTE_REQUIRED")
        if not _nonempty_string_list(differentiation.get("enrichment_route")):
            error(errors, prefix + "ENRICHMENT_ROUTE_REQUIRED")
        if differentiation.get("outcomes_unchanged") is not True:
            error(errors, prefix + "DIFFERENTIATION_MUST_PRESERVE_OUTCOMES")

    accessibility = adaptation.get("accessibility")
    if not isinstance(accessibility, dict):
        error(errors, prefix + "ACCESSIBILITY_REQUIRED")
    else:
        for key in ("representation_supports", "participation_supports", "environment_supports"):
            if not _nonempty_string_list(accessibility.get(key)):
                error(errors, prefix + f"{key.upper()}_REQUIRED")
        if accessibility.get("assessment_construct_preserved") is not True:
            error(errors, prefix + "ASSESSMENT_CONSTRUCT_MUST_BE_PRESERVED")

    evidence = adaptation.get("evidence_equivalence")
    if not isinstance(evidence, str) or not evidence.strip():
        error(errors, prefix + "EVIDENCE_EQUIVALENCE_REQUIRED")

    media = adaptation.get("media_fallback")
    if "MEDIA_DEPENDENT" in triggers:
        if not isinstance(media, dict):
            error(errors, prefix + "MEDIA_FALLBACK_REQUIRED")
        else:
            for key in (
                "required",
                "network_independent_core_route",
                "same_source_or_equivalent_required",
                "transcript_is_support_not_default_substitute",
            ):
                if media.get(key) is not True:
                    error(errors, prefix + f"MEDIA_{key.upper()}_MUST_BE_TRUE")
            for key in ("offline_route", "access_support_route"):
                value = media.get(key)
                if not isinstance(value, str) or not value.strip():
                    error(errors, prefix + f"MEDIA_{key.upper()}_REQUIRED")
    elif media is not None:
        error(errors, prefix + "MEDIA_FALLBACK_WITHOUT_MEDIA_TRIGGER")

    live = adaptation.get("live_performance_access")
    if "LIVE_PERFORMANCE" in triggers:
        if not isinstance(live, dict):
            error(errors, prefix + "LIVE_PERFORMANCE_ACCESS_REQUIRED")
        else:
            if live.get("required") is not True:
                error(errors, prefix + "LIVE_PERFORMANCE_ACCESS_REQUIRED_FLAG")
            expected_modes = {
                "SMALL_GROUP_LIVE",
                "TEACHER_OBSERVED_LIVE",
                "RECORDED_ORAL_IF_ALLOWED",
            }
            modes = live.get("alternative_modes")
            if not isinstance(modes, list) or not expected_modes.issubset(set(modes)):
                error(errors, prefix + "LIVE_ALTERNATIVE_MODES_INCOMPLETE", modes)
            if live.get("same_performance_evidence_required") is not True:
                error(errors, prefix + "LIVE_PERFORMANCE_EVIDENCE_MUST_BE_PRESERVED")
            if live.get("written_only_substitution_allowed") is not False:
                error(errors, prefix + "WRITTEN_ONLY_SPEAKING_SUBSTITUTION_FORBIDDEN")
            if live.get("recording_requires_consent") is not True:
                error(errors, prefix + "RECORDING_CONSENT_REQUIRED")
    elif live is not None:
        error(errors, prefix + "LIVE_ACCESS_WITHOUT_PERFORMANCE_TRIGGER")


def validate_course(knowledge_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    generated = knowledge_root / "generated" / "lesson_plans"
    manifest_path = knowledge_root / "production" / "classroom_adaptation_manifest.json"
    if not manifest_path.exists():
        return {
            "status": "FAIL",
            "course_id": knowledge_root.name,
            "errors": ["CLASSROOM_ADAPTATION_MANIFEST_MISSING"],
            "target_packages": 0,
        }

    discovered: dict[str, dict[str, Any]] = {}
    media_count = 0
    performance_count = 0
    overlap_count = 0
    total_plans = 0

    for path in sorted(generated.rglob("*.json")):
        total_plans += 1
        plan = read_json(path)
        triggers = detect_triggers(plan)
        adaptation = plan.get("classroom_adaptations")
        relative = path.relative_to(knowledge_root).as_posix()
        package_id = path.stem

        if not triggers:
            if adaptation is not None:
                error(errors, f"{package_id}:ADAPTATION_WITHOUT_CRITICAL_TRIGGER")
            continue

        if "MEDIA_DEPENDENT" in triggers:
            media_count += 1
        if "LIVE_PERFORMANCE" in triggers:
            performance_count += 1
        if len(triggers) == 2:
            overlap_count += 1

        _validate_adaptation(package_id, plan, triggers, errors)
        discovered[package_id] = {
            "path": relative,
            "theme_id": plan.get("theme_id"),
            "block_id": plan.get("block_id"),
            "trigger_categories": triggers,
            "media_types": media_types(plan) if "MEDIA_DEPENDENT" in triggers else [],
        }

    manifest = read_json(manifest_path)
    if manifest.get("schema_version") != "1.0.0":
        error(errors, "ADAPTATION_MANIFEST_SCHEMA_VERSION_INVALID", manifest.get("schema_version"))
    if manifest.get("course_id") != knowledge_root.name:
        error(errors, "ADAPTATION_MANIFEST_COURSE_ID_MISMATCH", manifest.get("course_id"))

    policy = manifest.get("policy")
    expected_policy = {
        "critical_trigger_categories": ["MEDIA_DEPENDENT", "LIVE_PERFORMANCE"],
        "non_target_packages_not_forced": True,
        "outcome_and_assessment_construct_preservation_required": True,
        "media_core_route_must_not_require_network": True,
        "transcript_is_support_not_default_listening_substitute": True,
        "written_only_speaking_substitution_forbidden": True,
        "recording_requires_consent": True,
    }
    if policy != expected_policy:
        error(errors, "ADAPTATION_POLICY_MISMATCH", policy)

    packages = manifest.get("packages")
    if not isinstance(packages, list):
        error(errors, "ADAPTATION_MANIFEST_PACKAGES_NOT_LIST")
        packages = []
    indexed: dict[str, dict[str, Any]] = {}
    for package in packages:
        if not isinstance(package, dict):
            error(errors, "ADAPTATION_MANIFEST_PACKAGE_NOT_OBJECT")
            continue
        package_id = package.get("package_id")
        if not isinstance(package_id, str) or not package_id:
            error(errors, "ADAPTATION_MANIFEST_PACKAGE_ID_INVALID")
            continue
        if package_id in indexed:
            error(errors, "ADAPTATION_MANIFEST_PACKAGE_ID_DUPLICATE", package_id)
            continue
        indexed[package_id] = package

    if set(indexed) != set(discovered):
        error(
            errors,
            "ADAPTATION_PACKAGE_SET_MISMATCH",
            {
                "missing": sorted(set(discovered) - set(indexed)),
                "extra": sorted(set(indexed) - set(discovered)),
            },
        )

    for package_id, actual in discovered.items():
        declared = indexed.get(package_id)
        if not declared:
            continue
        for key in ("path", "theme_id", "block_id", "trigger_categories", "media_types"):
            if declared.get(key) != actual[key]:
                error(errors, f"{package_id}:MANIFEST_{key.upper()}_MISMATCH", declared.get(key))

    expected_summary = {
        "target_packages": len(discovered),
        "media_dependent_packages": media_count,
        "live_performance_packages": performance_count,
        "overlap_packages": overlap_count,
    }
    if manifest.get("summary") != expected_summary:
        error(errors, "ADAPTATION_SUMMARY_MISMATCH", manifest.get("summary"))

    if not discovered:
        error(errors, "NO_CRITICAL_ADAPTATION_PACKAGES_DISCOVERED")

    return {
        "status": "PASS" if not errors else "FAIL",
        "course_id": knowledge_root.name,
        "errors": errors,
        "total_plans": total_plans,
        **expected_summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    args = parser.parse_args()
    try:
        courses = [validate_course(Path(root)) for root in args.knowledge_root]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2

    status = "PASS" if all(item["status"] == "PASS" for item in courses) else "FAIL"
    payload = {
        "status": status,
        "courses": courses,
        "summary": {
            "courses": len(courses),
            "total_plans": sum(item.get("total_plans", 0) for item in courses),
            "target_packages": sum(item.get("target_packages", 0) for item in courses),
            "media_dependent_packages": sum(item.get("media_dependent_packages", 0) for item in courses),
            "live_performance_packages": sum(item.get("live_performance_packages", 0) for item in courses),
            "overlap_packages": sum(item.get("overlap_packages", 0) for item in courses),
            "errors": sum(len(item.get("errors", [])) for item in courses),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
