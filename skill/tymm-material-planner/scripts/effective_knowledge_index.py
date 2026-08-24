#!/usr/bin/env python3
"""Compatibility projection that makes the existing knowledge index consume effective TYMM process components.

The historical indexer reads ``curriculum_map.json.process_components_verbatim`` directly.
During the process-component schema migration that field is intentionally retained as the
THEME_EXPLICIT-only legacy field. This module keeps the stable indexer implementation but
projects the shared roof inheritance in memory before extraction.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import knowledge_index as legacy
from process_component_resolver import audit_curriculum, project_effective_components


class EffectiveKnowledgeCorpusExtractor(legacy.KnowledgeCorpusExtractor):
    def __init__(self, knowledge_root: str):
        super().__init__(knowledge_root)
        self._process_origin_by_scope: dict[tuple[str, str], str] = {}
        self._roof_catalog_id: str | None = None

    @staticmethod
    def _assert_no_duplicate_curriculum_outcome_keys(data: dict[str, Any]) -> None:
        """Preserve the legacy canonical-key error before inheritance count validation.

        Effective projection adds a stricter process-component count contract. A duplicated
        theme/outcome would otherwise fail that count contract first and mask the more precise
        duplicate canonical identity error that downstream gates already rely on.
        """
        seen: set[tuple[str, str]] = set()
        for theme in data.get("themes", []):
            theme_id = str(theme.get("theme_id") or f"TEMA_{theme.get('theme_no', 0):02d}")
            for outcome in theme.get("learning_outcomes", []):
                outcome_code = str(outcome.get("outcome_code") or "")
                key = (theme_id, outcome_code)
                if key in seen:
                    raise legacy.DuplicateCanonicalKeyError(
                        f"Duplicate curriculum outcome canonical key: "
                        f"{self_course_id(data)}::curriculum_outcome::{theme_id}::{outcome_code}"
                    )
                seen.add(key)

    def _read_json(self, rel_path: str):
        data = super()._read_json(rel_path)
        if rel_path != "curriculum_map.json" or not data:
            return data

        self._assert_no_duplicate_curriculum_outcome_keys(data)

        contract_path = Path(self.knowledge_root) / "curriculum_process_component_resolution.json"
        if not contract_path.exists():
            return data

        contract = super()._read_json("curriculum_process_component_resolution.json") or {}
        shared_rel = "../TDE_SHARED/curriculum_process_component_catalog.json"
        catalog = super()._read_json(shared_rel)
        if not catalog:
            raise ValueError("PROCESS_COMPONENT_ROOF_CATALOG_MISSING_FOR_INDEX")
        if contract.get("course_id") != data.get("course_id"):
            raise ValueError("PROCESS_COMPONENT_COURSE_CONTRACT_MISMATCH_FOR_INDEX")
        if contract.get("catalog_id") != catalog.get("catalog_id"):
            raise ValueError("PROCESS_COMPONENT_CATALOG_CONTRACT_MISMATCH_FOR_INDEX")

        audit = audit_curriculum(data, catalog)
        if audit.get("final") != "PASS":
            raise ValueError(f"PROCESS_COMPONENT_INHERITANCE_INVALID_FOR_INDEX: {audit.get('counts')}")
        expected_counts = contract.get("expected_counts", {})
        for key, expected in expected_counts.items():
            actual = audit.get("counts", {}).get(key)
            if actual != expected:
                raise ValueError(
                    f"PROCESS_COMPONENT_COUNT_MISMATCH_FOR_INDEX: {key} actual={actual} expected={expected}"
                )

        projected = project_effective_components(data, catalog)
        self._roof_catalog_id = catalog.get("catalog_id")
        for theme in projected.get("themes", []):
            theme_id = theme.get("theme_id", "")
            for outcome in theme.get("learning_outcomes", []):
                code = outcome.get("outcome_code", "")
                resolution = outcome.get("process_component_resolution", {})
                origin = resolution.get("origin", "UNRESOLVED")
                self._process_origin_by_scope[(theme_id, code)] = origin
                # Compatibility projection: the legacy extractor iterates this field.
                outcome["process_components_verbatim"] = copy.deepcopy(
                    outcome.get("process_components_effective", [])
                )
        return projected

    def extract_all(self):
        records = super().extract_all()
        shared_rel = "../TDE_SHARED/curriculum_process_component_catalog.json"
        shared_hash = self.source_file_hashes.get(shared_rel, {}).get("sha256", "")
        curriculum_hash = self.source_file_hashes.get("curriculum_map.json", {}).get("sha256", "")

        for record in records:
            if record.get("entity_type") != "process_component":
                continue
            entity_id = str(record.get("entity_id", ""))
            parts = entity_id.split("::")
            if len(parts) < 3:
                raise ValueError(f"PROCESS_COMPONENT_INDEX_ID_INVALID: {entity_id}")
            theme_id, parent_code = parts[0], parts[1]
            origin = self._process_origin_by_scope.get((theme_id, parent_code))
            if origin == "ROOF_INHERITED":
                record["canonical_source_file"] = shared_rel
                record["canonical_json_path_or_record_key"] = (
                    f"parents[{parent_code}].components[{parts[-1]}]"
                )
                record["authority_name"] = "OFFICIAL_CURRICULUM_ROOF_INHERITED"
                record["origin"] = "roof_inherited"
                record["source_file_hash"] = shared_hash
            elif origin == "THEME_EXPLICIT":
                record["canonical_source_file"] = "curriculum_map.json"
                record["authority_name"] = "OFFICIAL_CURRICULUM_THEME_EXPLICIT"
                record["origin"] = "theme_explicit"
                record["source_file_hash"] = curriculum_hash
            elif origin == "SOURCE_VERIFIED_NONE":
                raise ValueError(
                    f"SOURCE_VERIFIED_NONE outcome unexpectedly produced process component record: {entity_id}"
                )
            else:
                raise ValueError(
                    f"PROCESS_COMPONENT_INDEX_ORIGIN_UNRESOLVED: {theme_id} {parent_code} -> {origin}"
                )
        return records


def self_course_id(data: dict[str, Any]) -> str:
    return str(data.get("course_id") or "UNKNOWN_COURSE")


# KnowledgeIndexer.build_index resolves KnowledgeCorpusExtractor from the legacy module's
# globals at runtime. Replacing that one symbol preserves the mature indexer/search logic.
legacy.KnowledgeCorpusExtractor = EffectiveKnowledgeCorpusExtractor
KnowledgeIndexer = legacy.KnowledgeIndexer


def main():
    legacy.main()


if __name__ == "__main__":
    main()
