#!/usr/bin/env python3
"""Materialize P7 structured form/resource/artifact references in lesson plans."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

USAGES = {"USED", "DEFERRED", "REFERENCE_ONLY"}
ID_TOKEN_RE = re.compile(r"\b(?:FORM|LINK|RES)_[A-Z0-9_]+\b|\bTDE(?:9|10)_[A-Z0-9_]*(?:RUBRIC|KONTROL_LISTESI)\b")
DEFER_MARKERS = (
    "bırak", "sonraki", "henüz", "kullanılmam", "kullanma", "kullanılmay",
    "tamamlandıysa", "aksi durumda", "geçmeden", "deferred", "erte",
)
POSITIVE_MARKERS = ("kullan", "puanla", "değerlendir", "uygula", "rubri")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED:{path}")
    return data


def write_json(path: Path, payload: dict[str, Any], *, pretty: bool = False) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None, separators=None if pretty else (",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")


def load_catalogs(root: Path) -> dict[str, Any]:
    forms_index = read_json(root / "textbook_forms_index.json")
    form_ids = {
        item.get("form_id") for item in forms_index.get("forms", [])
        if isinstance(item, dict) and isinstance(item.get("form_id"), str)
    }

    registry = read_json(root / "production" / "assessment_artifact_registry.json")
    artifacts: dict[str, dict[str, Any]] = {}
    for artifact in registry.get("annual_artifacts", []):
        if not isinstance(artifact, dict) or not isinstance(artifact.get("artifact_id"), str):
            continue
        artifacts[artifact["artifact_id"]] = artifact

    resource_plan = read_json(root / "production" / "consolidated_resource_plan.json")
    resources: dict[str, dict[str, Any]] = {}
    for resource in resource_plan.get("resources", []):
        if not isinstance(resource, dict):
            continue
        ids: set[str] = set()
        if isinstance(resource.get("resource_id"), str):
            ids.add(resource["resource_id"])
        for item in resource.get("resource_plan_ids", []):
            if isinstance(item, str):
                ids.add(item)
        for resource_id in ids:
            resources[resource_id] = resource

    return {"form_ids": form_ids, "artifacts": artifacts, "resources": resources}


def _text_values(value: Any, *, skip_grounding: bool = True) -> list[str]:
    result: list[str] = []
    if isinstance(value, str):
        result.append(value)
    elif isinstance(value, list):
        for item in value:
            result.extend(_text_values(item, skip_grounding=skip_grounding))
    elif isinstance(value, dict):
        for key, item in value.items():
            if skip_grounding and key == "grounded_references":
                continue
            if key in {
                "used_form_ids", "form_ids", "used_activity_ids", "activity_ids",
                "outcome_codes", "assessed_outcome_codes", "covered_outcome_codes",
            }:
                continue
            result.extend(_text_values(item, skip_grounding=skip_grounding))
    return result


def prose_strings(plan: dict[str, Any]) -> list[str]:
    return _text_values(plan)


def canonical_ids_in_prose(plan: dict[str, Any], ids: set[str]) -> set[str]:
    strings = prose_strings(plan)
    return {identifier for identifier in ids if any(identifier in text for text in strings)}


def unresolved_id_tokens(plan: dict[str, Any], catalogs: dict[str, Any]) -> set[str]:
    known = set(catalogs["form_ids"]) | set(catalogs["artifacts"]) | set(catalogs["resources"])
    found: set[str] = set()
    for text in prose_strings(plan):
        found.update(ID_TOKEN_RE.findall(text))
    return found - known


def usage_for(plan: dict[str, Any], identifier: str, *, used: bool = False) -> str:
    if used:
        return "USED"
    matches = [text.lower() for text in prose_strings(plan) if identifier in text]
    if any(any(marker in text for marker in DEFER_MARKERS) for text in matches):
        return "DEFERRED"
    if any(any(marker in text for marker in POSITIVE_MARKERS) for text in matches):
        return "USED"
    return "REFERENCE_ONLY"


def artifact_binding(artifact: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any] | None:
    bindings = [item for item in artifact.get("task_bindings", []) if isinstance(item, dict)]
    block_id = plan.get("block_id")
    theme_id = plan.get("theme_id")
    exact = [item for item in bindings if item.get("block_id") == block_id]
    if len(exact) == 1:
        return exact[0]
    theme = [item for item in bindings if item.get("theme_id") == theme_id]
    if len(theme) == 1:
        return theme[0]
    return None


def resource_applies(resource: dict[str, Any], plan: dict[str, Any]) -> bool:
    themes = resource.get("themes", [])
    return isinstance(themes, list) and plan.get("theme_id") in themes


def build_grounding(plan: dict[str, Any], catalogs: dict[str, Any]) -> dict[str, Any] | None:
    unresolved = unresolved_id_tokens(plan, catalogs)
    if unresolved:
        raise ValueError(f"UNRESOLVED_CANONICAL_REFERENCE_TOKENS:{sorted(unresolved)}")

    used_forms = {
        item for item in plan.get("used_form_ids", [])
        if isinstance(item, str)
    }
    form_mentions = canonical_ids_in_prose(plan, set(catalogs["form_ids"]))
    all_forms = sorted(used_forms | form_mentions)
    form_refs = [
        {"form_id": form_id, "usage": usage_for(plan, form_id, used=form_id in used_forms)}
        for form_id in all_forms
    ]

    artifact_mentions = canonical_ids_in_prose(plan, set(catalogs["artifacts"]))
    artifact_refs: list[dict[str, str]] = []
    for artifact_id in sorted(artifact_mentions):
        artifact = catalogs["artifacts"][artifact_id]
        binding = artifact_binding(artifact, plan)
        if binding is None or not isinstance(binding.get("gap_instance_id"), str):
            raise ValueError(f"ARTIFACT_NOT_BOUND_TO_PLAN_BLOCK:{artifact_id}:{plan.get('block_id')}")
        artifact_refs.append({
            "artifact_id": artifact_id,
            "binding_key": binding["gap_instance_id"],
            "usage": usage_for(plan, artifact_id),
        })

    resource_mentions = canonical_ids_in_prose(plan, set(catalogs["resources"]))
    resource_refs: list[dict[str, str]] = []
    for resource_id in sorted(resource_mentions):
        resource = catalogs["resources"][resource_id]
        if not resource_applies(resource, plan):
            raise ValueError(f"RESOURCE_NOT_BOUND_TO_PLAN_THEME:{resource_id}:{plan.get('theme_id')}")
        resource_refs.append({
            "resource_plan_id": resource_id,
            "usage": usage_for(plan, resource_id),
        })

    if not form_refs and not artifact_refs and not resource_refs:
        return None
    return {
        "form_refs": form_refs,
        "assessment_artifact_refs": artifact_refs,
        "resource_refs": resource_refs,
    }


def apply(root: Path, *, write: bool) -> dict[str, Any]:
    catalogs = load_catalogs(root)
    generated = root / "generated" / "lesson_plans"
    if not generated.is_dir():
        raise ValueError(f"LESSON_PLAN_DIRECTORY_MISSING:{generated}")

    changed: list[str] = []
    packages: list[dict[str, Any]] = []
    counts = {"form_refs": 0, "assessment_artifact_refs": 0, "resource_refs": 0}
    usage_counts = {usage: 0 for usage in sorted(USAGES)}

    for path in sorted(generated.rglob("*.json")):
        plan = read_json(path)
        expected = build_grounding(plan, catalogs)
        current = plan.get("grounded_references")
        if expected is None:
            if current is not None and write:
                plan.pop("grounded_references", None)
                write_json(path, plan)
                changed.append(path.relative_to(root).as_posix())
            continue

        if current != expected and write:
            plan["grounded_references"] = expected
            write_json(path, plan)
            changed.append(path.relative_to(root).as_posix())

        for key in counts:
            counts[key] += len(expected[key])
            for ref in expected[key]:
                usage = ref.get("usage")
                if usage in usage_counts:
                    usage_counts[usage] += 1
        packages.append({
            "package_id": path.stem,
            "path": path.relative_to(root).as_posix(),
            "theme_id": plan.get("theme_id"),
            "block_id": plan.get("block_id"),
            "form_refs": len(expected["form_refs"]),
            "assessment_artifact_refs": len(expected["assessment_artifact_refs"]),
            "resource_refs": len(expected["resource_refs"]),
        })

    manifest = {
        "schema_version": "1.0.0",
        "course_id": root.name,
        "policy": {
            "canonical_reference_ids_must_not_remain_prose_only": True,
            "used_forms_require_structured_used_reference": True,
            "artifact_binding_key_required": True,
            "resource_theme_binding_required": True,
            "mutable_lifecycle_metadata_not_duplicated_into_plan_refs": True,
        },
        "summary": {
            "target_packages": len(packages),
            **counts,
            "usage_counts": usage_counts,
        },
        "packages": packages,
    }
    manifest_path = root / "production" / "grounded_reference_manifest.json"
    existing = read_json(manifest_path) if manifest_path.exists() else None
    if existing != manifest and write:
        write_json(manifest_path, manifest, pretty=True)
        changed.append(manifest_path.relative_to(root).as_posix())

    return {
        "status": "PASS",
        "course_id": root.name,
        "target_packages": len(packages),
        **counts,
        "usage_counts": usage_counts,
        "changed_paths": changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        results = [apply(Path(root), write=args.write) for root in args.knowledge_root]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    print(json.dumps({"status": "PASS", "courses": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
