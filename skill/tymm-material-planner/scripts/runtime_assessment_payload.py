#!/usr/bin/env python3
"""Project canonical assessment rubric payloads and multi-part source provenance into runtime SQLite."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

PROJECTION_VERSION = "1.0.0"
RUNTIME_SCHEMA_VERSION = "1.1.0"
RUNTIME_PACKAGE_VERSION = "1.1.0"

ARTIFACT_COLUMNS = {
    "level_model_json": "TEXT NOT NULL DEFAULT '[]'",
    "criteria_json": "TEXT NOT NULL DEFAULT '[]'",
    "provenance_json": "TEXT NOT NULL DEFAULT '{}'",
}
BINDING_COLUMNS = {
    "task_specific_criteria_json": "TEXT NOT NULL DEFAULT '[]'",
    "source_equivalence_status": "TEXT",
    "binding_key_semantics": "TEXT",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(value: Any, default: Any) -> str:
    if value is None:
        value = default
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _table_columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in db.execute(f"PRAGMA table_info({table})")}


def _ensure_columns(
    db: sqlite3.Connection,
    table: str,
    required: dict[str, str],
) -> list[str]:
    existing = _table_columns(db, table)
    added: list[str] = []
    for name, definition in required.items():
        if name in existing:
            continue
        db.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
        added.append(name)
    return added


def _resolve_level_model(
    registry: dict[str, Any],
    artifact: dict[str, Any],
) -> dict[str, Any]:
    ref = artifact.get("level_model_ref")
    if not ref:
        return {}
    direct = registry.get("level_model")
    if isinstance(direct, dict) and direct.get("model_id") == ref:
        return direct
    models = registry.get("level_models")
    if isinstance(models, list):
        for model in models:
            if isinstance(model, dict) and model.get("model_id") == ref:
                return model
    return {}


def _append_schema_extension(schema_path: Path) -> None:
    marker = "-- assessment-rubric-payload-extension-v1"
    text = schema_path.read_text(encoding="utf-8") if schema_path.exists() else ""
    if marker in text:
        return
    extension = f"""
{marker}
ALTER TABLE assessment_artifacts ADD COLUMN level_model_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE assessment_artifacts ADD COLUMN criteria_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE assessment_artifacts ADD COLUMN provenance_json TEXT NOT NULL DEFAULT '{{}}';
ALTER TABLE assessment_task_bindings ADD COLUMN task_specific_criteria_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE assessment_task_bindings ADD COLUMN source_equivalence_status TEXT;
ALTER TABLE assessment_task_bindings ADD COLUMN binding_key_semantics TEXT;
"""
    schema_path.write_text(text.rstrip() + "\n\n" + extension.lstrip(), encoding="utf-8")


def _append_validation_section(report_path: Path, checks: list[tuple[str, bool, str]]) -> None:
    if not report_path.exists():
        return
    marker = "## Assessment rubric payload projection"
    text = report_path.read_text(encoding="utf-8")
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n"
    lines = [
        "",
        marker,
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    lines.extend(
        f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |"
        for name, ok, detail in checks
    )
    report_path.write_text(text.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def project_runtime_assessment_payload(root: Path | str) -> dict[str, Any]:
    root = Path(root).resolve()
    runtime = root / "runtime"
    db_path = runtime / "course_runtime.sqlite"
    manifest_path = runtime / "runtime_manifest.json"
    schema_path = runtime / "runtime_schema.sql"
    validation_report_path = runtime / "runtime_validation_report.md"
    registry_path = root / "production" / "assessment_artifact_registry.json"
    curriculum_path = root / "curriculum_map.json"

    for required in (db_path, manifest_path, registry_path, curriculum_path):
        if not required.exists():
            raise ValueError(f"RUNTIME_ASSESSMENT_PAYLOAD_MISSING_INPUT: {required}")

    registry = _read_json(registry_path)
    curriculum = _read_json(curriculum_path)
    runtime_manifest = _read_json(manifest_path)

    db = sqlite3.connect(db_path)
    db.execute("PRAGMA foreign_keys=ON")
    try:
        added_artifact_columns = _ensure_columns(
            db,
            "assessment_artifacts",
            ARTIFACT_COLUMNS,
        )
        added_binding_columns = _ensure_columns(
            db,
            "assessment_task_bindings",
            BINDING_COLUMNS,
        )

        artifacts = registry.get("annual_artifacts", [])
        if not isinstance(artifacts, list):
            raise ValueError("RUNTIME_ASSESSMENT_PAYLOAD_INVALID_REGISTRY: annual_artifacts")

        canonical_artifact_ids: set[str] = set()
        expected_criteria_artifacts = 0
        expected_level_model_artifacts = 0
        expected_task_criteria_bindings = 0
        expected_binding_count = 0

        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            artifact_id = artifact.get("artifact_id")
            if not artifact_id:
                continue
            canonical_artifact_ids.add(artifact_id)

            criteria = artifact.get("core_criteria", [])
            if criteria:
                expected_criteria_artifacts += 1
            level_model = _resolve_level_model(registry, artifact)
            if level_model:
                expected_level_model_artifacts += 1
            provenance = {
                "provenance_policy": artifact.get("provenance_policy"),
                "source_equivalence_status": artifact.get("source_equivalence_status"),
                "projection_version": PROJECTION_VERSION,
            }

            row = db.execute(
                "SELECT 1 FROM assessment_artifacts WHERE artifact_id=?",
                (artifact_id,),
            ).fetchone()
            if row is None:
                raise ValueError(
                    f"RUNTIME_ASSESSMENT_PAYLOAD_ARTIFACT_NOT_PROJECTED: {artifact_id}"
                )

            db.execute(
                """
                UPDATE assessment_artifacts
                SET level_model_json=?, criteria_json=?, provenance_json=?
                WHERE artifact_id=?
                """,
                (
                    _dump(level_model, {}),
                    _dump(criteria, []),
                    _dump(provenance, {}),
                    artifact_id,
                ),
            )

            for binding in artifact.get("task_bindings", []):
                if not isinstance(binding, dict):
                    continue
                binding_id = binding.get("gap_instance_id")
                if not binding_id:
                    continue
                expected_binding_count += 1
                task_criteria = binding.get("task_specific_criteria", [])
                if task_criteria:
                    expected_task_criteria_bindings += 1

                row = db.execute(
                    """
                    SELECT 1
                    FROM assessment_task_bindings
                    WHERE artifact_id=? AND gap_instance_id=?
                    """,
                    (artifact_id, binding_id),
                ).fetchone()
                if row is None:
                    raise ValueError(
                        "RUNTIME_ASSESSMENT_PAYLOAD_BINDING_NOT_PROJECTED: "
                        f"{artifact_id}:{binding_id}"
                    )

                db.execute(
                    """
                    UPDATE assessment_task_bindings
                    SET task_specific_criteria_json=?,
                        source_equivalence_status=?,
                        binding_key_semantics=?
                    WHERE artifact_id=? AND gap_instance_id=?
                    """,
                    (
                        _dump(task_criteria, []),
                        binding.get("source_equivalence_status"),
                        binding.get("binding_key_semantics"),
                        artifact_id,
                        binding_id,
                    ),
                )

        source_ref_ids = {
            row[0] for row in db.execute("SELECT source_id FROM source_references")
        }
        for theme in curriculum.get("themes", []):
            if not isinstance(theme, dict):
                continue
            source_id = theme.get("source_id") or curriculum.get("source_id")
            locator = theme.get("source_locator")
            theme_id = theme.get("theme_id")
            if (
                source_id
                and locator
                and theme_id
                and source_id in source_ref_ids
            ):
                db.execute(
                    """
                    INSERT OR IGNORE INTO entity_source_references
                    (entity_type,entity_id,source_id,locator)
                    VALUES (?,?,?,?)
                    """,
                    ("theme", theme_id, source_id, locator),
                )

        db.commit()

        runtime_artifact_ids = {
            row[0] for row in db.execute(
                "SELECT artifact_id FROM assessment_artifacts"
            )
        }
        criteria_count = db.execute(
            """
            SELECT COUNT(*)
            FROM assessment_artifacts
            WHERE criteria_json NOT IN ('[]','{}','null','')
            """
        ).fetchone()[0]
        level_model_count = db.execute(
            """
            SELECT COUNT(*)
            FROM assessment_artifacts
            WHERE level_model_json NOT IN ('[]','{}','null','')
            """
        ).fetchone()[0]
        task_criteria_count = db.execute(
            """
            SELECT COUNT(*)
            FROM assessment_task_bindings
            WHERE task_specific_criteria_json NOT IN ('[]','{}','null','')
            """
        ).fetchone()[0]
        binding_count = db.execute(
            "SELECT COUNT(*) FROM assessment_task_bindings"
        ).fetchone()[0]
        entity_source_count = db.execute(
            "SELECT COUNT(*) FROM entity_source_references"
        ).fetchone()[0]

        payload_json_valid = True
        try:
            for row in db.execute(
                """
                SELECT level_model_json,criteria_json,provenance_json
                FROM assessment_artifacts
                """
            ):
                for value in row:
                    json.loads(value)
            for row in db.execute(
                """
                SELECT targeted_outcomes_json,task_specific_criteria_json
                FROM assessment_task_bindings
                """
            ):
                for value in row:
                    json.loads(value)
        except (TypeError, json.JSONDecodeError):
            payload_json_valid = False

        checks = [
            (
                "artifact identity projection",
                runtime_artifact_ids == canonical_artifact_ids,
                f"runtime={len(runtime_artifact_ids)}, canonical={len(canonical_artifact_ids)}",
            ),
            (
                "rubric criteria payload",
                criteria_count == expected_criteria_artifacts,
                f"runtime={criteria_count}, canonical={expected_criteria_artifacts}",
            ),
            (
                "rubric level model payload",
                level_model_count == expected_level_model_artifacts,
                f"runtime={level_model_count}, canonical={expected_level_model_artifacts}",
            ),
            (
                "task binding count",
                binding_count == expected_binding_count,
                f"runtime={binding_count}, canonical={expected_binding_count}",
            ),
            (
                "task-specific criteria payload",
                task_criteria_count == expected_task_criteria_bindings,
                f"runtime={task_criteria_count}, canonical={expected_task_criteria_bindings}",
            ),
            (
                "payload JSON validity",
                payload_json_valid,
                "all projected JSON columns parse",
            ),
        ]

        if not all(ok for _, ok, _ in checks):
            failed = [name for name, ok, _ in checks if not ok]
            raise ValueError(
                "RUNTIME_ASSESSMENT_PAYLOAD_VALIDATION_FAILED: "
                + ", ".join(failed)
            )

        row_counts = runtime_manifest.setdefault("row_counts", {})
        row_counts["assessment_artifacts"] = len(runtime_artifact_ids)
        row_counts["assessment_task_bindings"] = binding_count
        row_counts["entity_source_references"] = entity_source_count
        runtime_manifest["schema_version"] = RUNTIME_SCHEMA_VERSION
        runtime_manifest["runtime_package_version"] = RUNTIME_PACKAGE_VERSION
        runtime_manifest["assessment_payload_projection_version"] = PROJECTION_VERSION
        runtime_manifest["assessment_payload_capabilities"] = {
            "rubric_level_model": True,
            "rubric_criteria": True,
            "task_specific_criteria": True,
            "source_equivalence_status": True,
            "binding_key_semantics": True,
        }
        runtime_manifest["validation_status"] = "PASS"
        manifest_path.write_text(
            json.dumps(runtime_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        _append_schema_extension(schema_path)
        _append_validation_section(validation_report_path, checks)

        return {
            "status": "PASS",
            "projection_version": PROJECTION_VERSION,
            "artifact_count": len(runtime_artifact_ids),
            "binding_count": binding_count,
            "criteria_artifact_count": criteria_count,
            "level_model_artifact_count": level_model_count,
            "task_criteria_binding_count": task_criteria_count,
            "entity_source_reference_count": entity_source_count,
            "added_artifact_columns": added_artifact_columns,
            "added_binding_columns": added_binding_columns,
        }
    finally:
        db.close()


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", required=True)
    args = parser.parse_args()
    try:
        result = project_runtime_assessment_payload(args.knowledge_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
