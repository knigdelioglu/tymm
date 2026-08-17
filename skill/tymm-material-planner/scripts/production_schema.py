#!/usr/bin/env python3
"""Shared production-schema 1.1 normalization and validation helpers.

The canonical production identity is ``artifact_id``. Historical MAT_* gap IDs are
accepted only as provenance/lookup aliases through ``covered_gap_instances`` and
must never become assessment-artifact identities.
"""

from typing import Any, Dict, List, Tuple

PRODUCTION_SCHEMA_VERSION = "1.1"


class ProductionSchemaError(ValueError):
    """Raised when the canonical production manifest violates schema 1.1 invariants."""


def _string_list(record: Dict[str, Any], field: str, artifact_id: str) -> List[str]:
    value = record.get(field, [])
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ProductionSchemaError(
            f"PRODUCTION_SCHEMA_INVALID: artifact '{artifact_id}' field '{field}' must be a list of non-empty strings."
        )
    if len(value) != len(set(value)):
        raise ProductionSchemaError(
            f"PRODUCTION_SCHEMA_INVALID: artifact '{artifact_id}' field '{field}' contains duplicates."
        )
    return value


def build_artifact_maps(
    manifest: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]], Dict[str, str], Dict[str, Dict[str, Any]]]:
    """Validate schema 1.1 and return artifact and alias lookup maps.

    Returns ``(artifacts, artifact_by_id, gap_alias_to_artifact_id, provenance_by_gap)``.
    """
    schema_version = str(manifest.get("schema_version", ""))
    if schema_version != PRODUCTION_SCHEMA_VERSION:
        raise ProductionSchemaError(
            f"PRODUCTION_SCHEMA_MISMATCH: expected {PRODUCTION_SCHEMA_VERSION}, found {schema_version or 'MISSING'}."
        )

    artifacts = manifest.get("production_queue", [])
    if not isinstance(artifacts, list) or not artifacts:
        raise ProductionSchemaError("PRODUCTION_SCHEMA_INVALID: production_queue must be a non-empty list.")

    artifact_by_id: Dict[str, Dict[str, Any]] = {}
    gap_alias_to_artifact_id: Dict[str, str] = {}

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise ProductionSchemaError("PRODUCTION_SCHEMA_INVALID: production_queue entries must be objects.")
        artifact_id = artifact.get("artifact_id")
        if not isinstance(artifact_id, str) or not artifact_id:
            raise ProductionSchemaError("PRODUCTION_SCHEMA_INVALID: every production artifact requires artifact_id.")
        if artifact_id in artifact_by_id:
            raise ProductionSchemaError(f"DUPLICATE_ARTIFACT_ID: {artifact_id}")
        if artifact_id.startswith("MAT_"):
            raise ProductionSchemaError(
                f"PRODUCTION_SCHEMA_INVALID: historical gap ID '{artifact_id}' cannot be used as artifact identity."
            )

        _string_list(artifact, "covered_themes", artifact_id)
        _string_list(artifact, "covered_outcomes", artifact_id)
        aliases = _string_list(artifact, "covered_gap_instances", artifact_id)

        artifact_by_id[artifact_id] = artifact
        for alias in aliases:
            if alias == artifact_id:
                raise ProductionSchemaError(
                    f"PRODUCTION_SCHEMA_INVALID: alias '{alias}' cannot equal canonical artifact identity."
                )
            previous = gap_alias_to_artifact_id.get(alias)
            if previous and previous != artifact_id:
                raise ProductionSchemaError(
                    f"DUPLICATE_GAP_ALIAS: '{alias}' maps to both '{previous}' and '{artifact_id}'."
                )
            gap_alias_to_artifact_id[alias] = artifact_id

    provenance_rows = manifest.get("gap_instance_provenance_registry", [])
    if not isinstance(provenance_rows, list):
        raise ProductionSchemaError("PRODUCTION_SCHEMA_INVALID: gap_instance_provenance_registry must be a list.")

    provenance_by_gap: Dict[str, Dict[str, Any]] = {}
    for row in provenance_rows:
        if not isinstance(row, dict):
            continue
        gap_id = row.get("gap_instance_id")
        resolved_artifact_id = row.get("resolved_artifact_id")
        if not gap_id:
            continue
        if gap_id in provenance_by_gap:
            raise ProductionSchemaError(f"DUPLICATE_GAP_PROVENANCE: {gap_id}")
        if gap_alias_to_artifact_id.get(gap_id) != resolved_artifact_id:
            raise ProductionSchemaError(
                f"GAP_MAPPING_MISMATCH: provenance '{gap_id}' resolves to '{resolved_artifact_id}' but artifact coverage resolves to '{gap_alias_to_artifact_id.get(gap_id)}'."
            )
        provenance_by_gap[gap_id] = row

    if set(provenance_by_gap) != set(gap_alias_to_artifact_id):
        missing = sorted(set(gap_alias_to_artifact_id) - set(provenance_by_gap))
        extra = sorted(set(provenance_by_gap) - set(gap_alias_to_artifact_id))
        raise ProductionSchemaError(
            f"GAP_PROVENANCE_INCOMPLETE: missing={missing}, extra={extra}."
        )

    return artifacts, artifact_by_id, gap_alias_to_artifact_id, provenance_by_gap
