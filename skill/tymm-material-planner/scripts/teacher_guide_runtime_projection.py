#!/usr/bin/env python3
"""Project validated, generic teacher-guide sources into runtime SQLite.

Teacher guides are canonical content.  This module deliberately knows only
the generic guide contract and the canonical entity tables exposed by the
course runtime; it does not know a subject, grade, theme name, or skill set.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import re
from pathlib import Path
from typing import Any, Iterable


PROJECTION_VERSION = "1.0.0"
TEACHER_GUIDE_SCHEMA_VERSION = "1.0.0"
TEACHER_GUIDE_MANIFEST_TYPE = "TYMM_TEACHER_GUIDE_MANIFEST"
TEACHER_GUIDE_SEAL_FILENAME = "teacher_guide_validation_seal.json"


TEACHER_GUIDE_SCHEMA = r'''
CREATE TABLE canonical_entities (
    entity_type TEXT NOT NULL CHECK (length(trim(entity_type)) > 0),
    entity_id TEXT NOT NULL CHECK (length(trim(entity_id)) > 0),
    PRIMARY KEY (entity_type, entity_id)
);
CREATE TABLE teacher_guides (
    guide_id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL REFERENCES courses(course_id),
    scope_type TEXT NOT NULL CHECK (length(trim(scope_type)) > 0),
    scope_id TEXT NOT NULL CHECK (length(trim(scope_id)) > 0),
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    content_status TEXT NOT NULL CHECK (length(trim(content_status)) > 0),
    schema_version TEXT NOT NULL CHECK (length(trim(schema_version)) > 0),
    provenance_json TEXT NOT NULL,
    FOREIGN KEY (scope_type, scope_id)
        REFERENCES canonical_entities(entity_type, entity_id),
    UNIQUE (course_id, scope_type, scope_id)
);
CREATE TABLE teacher_guide_sections (
    section_id TEXT PRIMARY KEY,
    guide_id TEXT NOT NULL REFERENCES teacher_guides(guide_id),
    section_order INTEGER NOT NULL CHECK (section_order > 0),
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    section_type TEXT NOT NULL CHECK (length(trim(section_type)) > 0),
    page_locator TEXT,
    source_locator TEXT,
    content_status TEXT NOT NULL CHECK (length(trim(content_status)) > 0),
    provenance_json TEXT NOT NULL,
    UNIQUE (guide_id, section_order)
);
CREATE TABLE teacher_guide_units (
    unit_id TEXT PRIMARY KEY,
    section_id TEXT NOT NULL REFERENCES teacher_guide_sections(section_id),
    unit_order INTEGER NOT NULL CHECK (unit_order > 0),
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    page_locator TEXT,
    source_locator TEXT,
    content_status TEXT NOT NULL CHECK (length(trim(content_status)) > 0),
    purpose_json TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    UNIQUE (section_id, unit_order)
);
CREATE TABLE teacher_guide_items (
    item_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL REFERENCES teacher_guide_units(unit_id),
    item_order INTEGER NOT NULL CHECK (item_order > 0),
    title TEXT,
    label TEXT NOT NULL CHECK (length(trim(label)) > 0),
    item_type TEXT NOT NULL CHECK (length(trim(item_type)) > 0),
    page_locator TEXT,
    source_locator TEXT,
    content_status TEXT NOT NULL CHECK (length(trim(content_status)) > 0),
    expected_response_json TEXT NOT NULL,
    acceptance_criteria_json TEXT NOT NULL,
    teacher_guidance_json TEXT NOT NULL,
    common_misconceptions_json TEXT NOT NULL,
    assessment_evidence_json TEXT NOT NULL,
    differentiation_json TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    canonical_payload_sha256 TEXT NOT NULL
        CHECK (length(trim(canonical_payload_sha256)) = 64),
    UNIQUE (unit_id, item_order)
);
CREATE TABLE teacher_guide_item_relations (
    item_id TEXT NOT NULL REFERENCES teacher_guide_items(item_id),
    target_type TEXT NOT NULL CHECK (length(trim(target_type)) > 0),
    target_id TEXT NOT NULL CHECK (length(trim(target_id)) > 0),
    relation_type TEXT NOT NULL CHECK (length(trim(relation_type)) > 0),
    relation_order INTEGER NOT NULL DEFAULT 1 CHECK (relation_order > 0),
    PRIMARY KEY (item_id, target_type, target_id, relation_type),
    FOREIGN KEY (target_type, target_id)
        REFERENCES canonical_entities(entity_type, entity_id)
);
CREATE INDEX idx_teacher_guide_scope
    ON teacher_guides(scope_type, scope_id, guide_id);
CREATE INDEX idx_teacher_guide_section_order
    ON teacher_guide_sections(guide_id, section_order, section_id);
CREATE INDEX idx_teacher_guide_unit_order
    ON teacher_guide_units(section_id, unit_order, unit_id);
CREATE INDEX idx_teacher_guide_item_order
    ON teacher_guide_items(unit_id, item_order, item_id);
CREATE INDEX idx_teacher_guide_relation_target
    ON teacher_guide_item_relations(target_type, target_id, relation_order, item_id);
'''


class TeacherGuideProjectionError(ValueError):
    """Raised when a canonical guide cannot be projected fail-closed."""


def compact_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TeacherGuideProjectionError(f"TEACHER_GUIDE_{field.upper()}_REQUIRED")
    return value.strip()


def _string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise TeacherGuideProjectionError(f"TEACHER_GUIDE_{field.upper()}_INVALID")
    return [item.strip() for item in value]


def _json_value(value: Any, field: str) -> Any:
    # All JSON values, including null, are valid and are serialized without
    # flattening them into display text.
    if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
        return value
    raise TeacherGuideProjectionError(f"TEACHER_GUIDE_{field.upper()}_INVALID_JSON")


def _provenance(node: dict[str, Any], field: str) -> dict[str, Any]:
    value = node.get("provenance")
    if not isinstance(value, dict):
        raise TeacherGuideProjectionError(f"{field}.provenance_REQUIRED")
    source_ids = _string_list(value.get("source_ids"), f"{field}.provenance.source_ids")
    source_locators = _string_list(
        value.get("source_locators"), f"{field}.provenance.source_locators"
    )
    if not source_ids or not source_locators:
        raise TeacherGuideProjectionError(f"{field}.provenance_INCOMPLETE")
    return value


def _normal_type(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _target_type_from_ref(key: str) -> str:
    name = _normal_type(key[:-5] if key.endswith("_refs") else key)
    aliases = {
        "theme": "theme",
        "themes": "theme",
        "scope": "scope",
        "block": "block",
        "blocks": "block",
        "outcome": "outcome",
        "outcomes": "outcome",
        "activity": "activity",
        "activities": "activity",
        "textbook": "textbook_section",
        "textbook_section": "textbook_section",
        "textbook_sections": "textbook_section",
        "form": "form",
        "forms": "form",
        "assessment": "assessment",
        "assessments": "assessment",
        "assessment_artifact": "assessment",
        "assessment_artifacts": "assessment",
        "lesson_plan": "lesson_plan_package",
        "lesson_plans": "lesson_plan_package",
        "lesson_plan_package": "lesson_plan_package",
        "lesson_plan_packages": "lesson_plan_package",
    }
    return aliases.get(name, name)


def _repo_root_for_course(course_root: Path) -> Path:
    # A course source is normally <repo>/courses/<course_id>.  The fallback
    # keeps fixtures that use a standalone course directory generic.
    if course_root.parent.name == "courses":
        return course_root.parent.parent
    return course_root


def resolve_reference(course_root: Path, reference: str) -> Path:
    path = Path(reference)
    candidates = [path] if path.is_absolute() else [course_root / path]
    repo_root = _repo_root_for_course(course_root)
    if not path.is_absolute():
        candidates.append(repo_root / path)
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_file():
            return resolved
    raise TeacherGuideProjectionError(f"TEACHER_GUIDE_SOURCE_MISSING:{reference}")


def _relative_source_key(course_root: Path, path: Path, declared: str) -> str:
    try:
        return path.resolve().relative_to(course_root.resolve()).as_posix()
    except ValueError:
        return declared.replace("\\", "/")


def discover_teacher_guide_sources(
    course_root: Path,
) -> list[tuple[str, Path, dict[str, Any]]]:
    """Discover manifests by document type, never by course/theme path."""
    result: list[tuple[str, Path, dict[str, Any]]] = []
    for path in sorted(course_root.rglob("*.json")):
        if "runtime" in path.parts:
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and value.get("document_type") == TEACHER_GUIDE_MANIFEST_TYPE:
            result.append((path.relative_to(course_root).as_posix(), path, value))
    return result


def teacher_guide_source_files(course_root: Path) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for manifest_key, manifest_path, manifest in discover_teacher_guide_sources(course_root):
        if manifest_path.resolve() not in seen:
            files.append((manifest_key, manifest_path))
            seen.add(manifest_path.resolve())
        sections = manifest.get("sections")
        if not isinstance(sections, list):
            raise TeacherGuideProjectionError(f"{manifest_key}:sections_INVALID")
        for section_index in sections:
            if not isinstance(section_index, dict):
                raise TeacherGuideProjectionError(f"{manifest_key}:section_INDEX_INVALID")
            declared = _nonempty(section_index.get("content_ref"), "section_content_ref")
            section_path = resolve_reference(course_root, declared)
            if section_path.resolve() not in seen:
                files.append((_relative_source_key(course_root, section_path, declared), section_path))
                seen.add(section_path.resolve())
    return sorted(files, key=lambda item: item[0])


def _canonical_rows(db: sqlite3.Connection, table: str, column: str, kind: str) -> set[tuple[str, str]]:
    if db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone() is None:
        return set()
    return {(kind, str(row[0])) for row in db.execute(f"SELECT {column} FROM {table}")}


def _canonical_entity_set(db: sqlite3.Connection, course_id: str) -> set[tuple[str, str]]:
    mapping = (
        ("themes", "theme_id", "theme"),
        ("blocks", "block_id", "block"),
        ("outcomes", "outcome_id", "outcome"),
        ("activities", "activity_id", "activity"),
        ("textbook_sections", "section_id", "textbook_section"),
        ("forms", "form_id", "form"),
        ("assessment_artifacts", "artifact_id", "assessment"),
        ("lesson_plan_packages", "package_id", "lesson_plan_package"),
    )
    entities = {("course", course_id)}
    for table, column, kind in mapping:
        entities.update(_canonical_rows(db, table, column, kind))
    if db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='canonical_entities'"
    ).fetchone():
        entities.update(
            (str(row[0]), str(row[1]))
            for row in db.execute(
                "SELECT entity_type, entity_id FROM canonical_entities"
            )
        )
    return entities


def _insert_entities(db: sqlite3.Connection, entities: Iterable[tuple[str, str]]) -> None:
    db.executemany(
        "INSERT OR IGNORE INTO canonical_entities(entity_type, entity_id) VALUES (?, ?)",
        sorted(entities),
    )


def _scope(manifest: dict[str, Any]) -> tuple[str, str]:
    scope_type = manifest.get("scope_type")
    scope_id = manifest.get("scope_id")
    if scope_type is None and manifest.get("theme_id") is not None:
        scope_type, scope_id = "theme", manifest.get("theme_id")
    if isinstance(manifest.get("scope"), dict):
        scope_type = manifest["scope"].get("type", scope_type)
        scope_id = manifest["scope"].get("id", scope_id)
    return _nonempty(scope_type, "scope_type"), _nonempty(scope_id, "scope_id")


def _guide_id(manifest: dict[str, Any], scope_type: str, scope_id: str) -> str:
    value = manifest.get("guide_id")
    return _nonempty(value, "guide_id") if value is not None else f"{manifest['course_id']}:{scope_type}:{scope_id}"


def _refs(node: dict[str, Any], field: str) -> list[tuple[str, str, str]]:
    result: list[tuple[str, str, str]] = []
    for key, value in node.items():
        if key == "relations":
            if value is None:
                continue
            if not isinstance(value, list):
                raise TeacherGuideProjectionError(f"{field}.relations_INVALID")
            for relation in value:
                if not isinstance(relation, dict):
                    raise TeacherGuideProjectionError(f"{field}.relation_INVALID")
                target_type = _nonempty(
                    relation.get("target_type", relation.get("targetType")),
                    f"{field}.relation.target_type",
                )
                target_id = _nonempty(
                    relation.get("target_id", relation.get("targetId")),
                    f"{field}.relation.target_id",
                )
                relation_type = _nonempty(
                    relation.get("relation_type", relation.get("relationType", "references")),
                    f"{field}.relation.relation_type",
                )
                result.append((_normal_type(target_type), target_id, relation_type))
            continue
        if not key.endswith("_refs"):
            continue
        for target_id in _string_list(value, f"{field}.{key}"):
            result.append((_target_type_from_ref(key), target_id, "references"))
    block_id = node.get("block_id")
    if isinstance(block_id, str) and block_id.strip():
        result.append(("block", block_id.strip(), "context"))
    return result


def _normal_path(value: str, course_id: str) -> str:
    result = value.replace("\\", "/").lstrip("./")
    prefix = f"courses/{course_id}/"
    if result.startswith(prefix):
        return result[len(prefix) :]
    return result


def _resolve_relation(
    db: sqlite3.Connection,
    entities: set[tuple[str, str]],
    target_type: str,
    target_id: str,
    course_id: str,
    scope_type: str | None = None,
    scope_id: str | None = None,
) -> str:
    key = (target_type, target_id)
    if key in entities:
        return target_id
    if target_type == "scope":
        key = ("scope", target_id)
        if key in entities:
            return target_id
    if target_type == "outcome":
        if scope_type == "theme" and scope_id:
            rows = db.execute(
                "SELECT outcome_id FROM outcomes WHERE theme_id=? AND (outcome_id=? OR outcome_code=?) ORDER BY outcome_id",
                (scope_id, target_id, target_id),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT outcome_id FROM outcomes WHERE outcome_id=? OR outcome_code=? ORDER BY outcome_id",
                (target_id, target_id),
            ).fetchall()
        if len(rows) == 1 and ("outcome", str(rows[0][0])) in entities:
            return str(rows[0][0])
    if target_type == "lesson_plan_package":
        normalized = _normal_path(target_id, course_id)
        rows = [
            str(row[0])
            for row in db.execute(
                "SELECT package_id FROM lesson_plan_packages WHERE source_path=? ORDER BY package_id",
                (normalized,),
            ).fetchall()
        ]
        if len(rows) == 1 and (target_type, rows[0]) in entities:
            return rows[0]
    raise TeacherGuideProjectionError(
        f"TEACHER_GUIDE_DANGLING_RELATION:{target_type}:{target_id}"
    )


def _node_value(node: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in node:
            return node[key]
    return default


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _nonempty(value, field)


def _locator(value: Any, field: str) -> str | None:
    """Store scalar locators as text and structured locators as canonical JSON."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return compact_json(_json_value(value, field))


def _content_class(provenance: dict[str, Any]) -> str | None:
    value = provenance.get("content_class")
    return value if isinstance(value, str) else None


def _guide_provenance(manifest: dict[str, Any]) -> dict[str, Any]:
    if isinstance(manifest.get("provenance"), dict):
        return _provenance(manifest, "guide")
    source_ids = [
        source.get("source_id")
        for source in manifest.get("source_manifest", [])
        if isinstance(source, dict) and isinstance(source.get("source_id"), str)
    ]
    source_locators = [
        source.get("path")
        for source in manifest.get("source_manifest", [])
        if isinstance(source, dict) and isinstance(source.get("path"), str)
    ]
    if not source_ids or not source_locators:
        raise TeacherGuideProjectionError("TEACHER_GUIDE_GUIDE_PROVENANCE_INCOMPLETE")
    return {
        "source_ids": source_ids,
        "source_locators": source_locators,
        "content_class": manifest.get("content_class", "MIXED"),
    }


def project_teacher_guides(
    course_root: Path,
    db: sqlite3.Connection,
    runtime_manifest: dict[str, Any],
) -> dict[str, Any]:
    """Project all discovered manifests and return manifest capability data."""
    manifests = discover_teacher_guide_sources(course_root)
    empty = {
        "available": False,
        "schema_version": TEACHER_GUIDE_SCHEMA_VERSION,
        "validation_status": "NOT_PRESENT",
        "source_bound": False,
        "source_validation_status": "NOT_PRESENT",
        "row_counts": {
            "canonical_entities": 0,
            "teacher_guides": 0,
            "teacher_guide_sections": 0,
            "teacher_guide_units": 0,
            "teacher_guide_items": 0,
            "teacher_guide_item_relations": 0,
        },
    }
    if not manifests:
        return {"capability": empty, "validation": {"status": "NOT_PRESENT", "scope": "COURSE", "source_bound": False}}

    curriculum_path = course_root / "curriculum_map.json"
    if not curriculum_path.is_file():
        raise TeacherGuideProjectionError("TEACHER_GUIDE_CURRICULUM_MAP_MISSING")
    course_id = _nonempty(json.loads(curriculum_path.read_text(encoding="utf-8")).get("course_id"), "course_id")
    entities = _canonical_entity_set(db, course_id)

    # Guide scopes are canonical scope entities; they are not guessed from
    # labels, and a source must explicitly declare the scope identifier.
    for _, _, manifest in manifests:
        manifest_course = _nonempty(manifest.get("course_id"), "course_id")
        if manifest_course != course_id:
            raise TeacherGuideProjectionError("TEACHER_GUIDE_COURSE_ID_MISMATCH")
        scope_type, scope_id = _scope(manifest)
        entities.add((scope_type, scope_id))
        entities.add(("scope", scope_id))
    _insert_entities(db, entities)

    pending_relations: list[tuple[str, str, str, str]] = []
    guide_rows: list[dict[str, Any]] = []
    section_rows: list[dict[str, Any]] = []
    unit_rows: list[dict[str, Any]] = []
    item_rows: list[dict[str, Any]] = []
    seen_ids: set[tuple[str, str]] = set()
    source_validation_statuses: set[str] = set()

    for manifest_key, _, manifest in manifests:
        scope_type, scope_id = _scope(manifest)
        guide_id = _guide_id(manifest, scope_type, scope_id)
        guide_provenance = _guide_provenance(manifest)
        source_validation_status = str(
            manifest.get("validation_contract", {}).get(
                "current_status", manifest.get("status", "UNKNOWN")
            )
        )
        if source_validation_status not in {"PASS", "PASS_WITH_WARNINGS"}:
            raise TeacherGuideProjectionError(
                f"{manifest_key}:SOURCE_VALIDATION_NOT_PASSED:{source_validation_status}"
            )
        source_validation_statuses.add(source_validation_status)
        if ("guide", guide_id) in seen_ids:
            raise TeacherGuideProjectionError(f"TEACHER_GUIDE_DUPLICATE_GUIDE:{guide_id}")
        seen_ids.add(("guide", guide_id))
        guide_rows.append({
            "guide_id": guide_id,
            "course_id": course_id,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "title": _nonempty(manifest.get("title", guide_id), "title"),
            "content_status": _nonempty(manifest.get("content_status", manifest.get("status", "UNKNOWN")), "content_status"),
            "schema_version": _nonempty(manifest.get("schema_version"), "schema_version"),
            "provenance": guide_provenance,
        })
        sections = manifest.get("sections")
        if not isinstance(sections, list) or not sections:
            raise TeacherGuideProjectionError(f"{manifest_key}:sections_REQUIRED")
        for section_order, section_index in enumerate(sections, start=1):
            if not isinstance(section_index, dict):
                raise TeacherGuideProjectionError(f"{manifest_key}:section_INDEX_INVALID")
            declared = _nonempty(section_index.get("content_ref"), "section_content_ref")
            section_path = resolve_reference(course_root, declared)
            section = json.loads(section_path.read_text(encoding="utf-8"))
            if not isinstance(section, dict):
                raise TeacherGuideProjectionError(f"{declared}:section_OBJECT_REQUIRED")
            section_id = _nonempty(_node_value(section, "section_id", default=section_index.get("section_id")), "section_id")
            if section_id != section_index.get("section_id", section_id):
                raise TeacherGuideProjectionError(f"{declared}:SECTION_MANIFEST_MISMATCH")
            if ("section", section_id) in seen_ids:
                raise TeacherGuideProjectionError(f"TEACHER_GUIDE_DUPLICATE_SECTION:{section_id}")
            seen_ids.add(("section", section_id))
            section_provenance = _provenance(section, f"section:{section_id}")
            section_rows.append({
                "section_id": section_id,
                "guide_id": guide_id,
                "section_order": section_order,
                "title": _nonempty(_node_value(section, "title", default=section_index.get("title")), "section_title"),
                "section_type": _nonempty(_node_value(section, "section_type", default=section_index.get("section_type")), "section_type"),
                "page_locator": _locator(_node_value(section, "page_locator", "printed_page_range", default=section_index.get("printed_page_range")), f"section:{section_id}.page_locator"),
                "source_locator": _locator(_node_value(section, "source_locator", default=declared), f"section:{section_id}.source_locator"),
                "content_status": _nonempty(_node_value(section, "content_status", default=section_index.get("content_status", "UNKNOWN")), "section_content_status"),
                "provenance": section_provenance,
            })
            section_relations = _refs(section_index, f"section_index:{section_id}") + _refs(section, f"section:{section_id}")
            units = section.get("guide_units", section.get("units"))
            if not isinstance(units, list):
                raise TeacherGuideProjectionError(f"{declared}:guide_units_REQUIRED")
            for unit_order, unit in enumerate(units, start=1):
                if not isinstance(unit, dict):
                    raise TeacherGuideProjectionError(f"{declared}:unit_INVALID")
                unit_id = _nonempty(unit.get("unit_id"), "unit_id")
                if ("unit", unit_id) in seen_ids:
                    raise TeacherGuideProjectionError(f"TEACHER_GUIDE_DUPLICATE_UNIT:{unit_id}")
                seen_ids.add(("unit", unit_id))
                unit_provenance = _provenance(unit, f"unit:{unit_id}")
                unit_rows.append({
                    "unit_id": unit_id,
                    "section_id": section_id,
                    "unit_order": unit_order,
                    "title": _nonempty(unit.get("title"), "unit_title"),
                    "page_locator": _locator(_node_value(unit, "page_locator", "printed_page_range"), f"unit:{unit_id}.page_locator"),
                    "source_locator": _locator(_node_value(unit, "source_locator", default=declared), f"unit:{unit_id}.source_locator"),
                    "content_status": _nonempty(unit.get("content_status", "UNKNOWN"), "unit_content_status"),
                    "purpose": _json_value(unit.get("purpose"), f"unit:{unit_id}.purpose"),
                    "provenance": unit_provenance,
                })
                unit_relations = _refs(unit, f"unit:{unit_id}")
                items = unit.get("items", [])
                if not isinstance(items, list):
                    raise TeacherGuideProjectionError(f"{declared}:{unit_id}.items_INVALID")
                for item_order, item in enumerate(items, start=1):
                    if not isinstance(item, dict):
                        raise TeacherGuideProjectionError(f"{declared}:item_INVALID")
                    item_id = _nonempty(item.get("item_id"), "item_id")
                    if ("item", item_id) in seen_ids:
                        raise TeacherGuideProjectionError(f"TEACHER_GUIDE_DUPLICATE_ITEM:{item_id}")
                    seen_ids.add(("item", item_id))
                    expected_key = "expected_response" if "expected_response" in item else "expected_answer" if "expected_answer" in item else None
                    if "expected_response" in item and "expected_answer" in item and item["expected_response"] != item["expected_answer"]:
                        raise TeacherGuideProjectionError(f"{item_id}:EXPECTED_RESPONSE_CONFLICT")
                    expected = _json_value(item.get(expected_key) if expected_key else None, f"item:{item_id}.expected_response")
                    differentiation = item.get("differentiation", {})
                    if not isinstance(differentiation, dict):
                        raise TeacherGuideProjectionError(f"{item_id}:DIFFERENTIATION_INVALID")
                    differentiation = {"support": _json_value(differentiation.get("support"), f"{item_id}.support"), "enrichment": _json_value(differentiation.get("enrichment"), f"{item_id}.enrichment")}
                    provenance = _provenance(item, f"item:{item_id}")
                    row = {
                        "item_id": item_id,
                        "unit_id": unit_id,
                        "item_order": item_order,
                        "title": _optional_text(_node_value(item, "title", "item_title"), f"item:{item_id}.title"),
                        "label": _nonempty(_node_value(item, "label", "title", default=item_id), "label"),
                        "item_type": _nonempty(item.get("item_type", "content"), "item_type"),
                        "page_locator": _locator(_node_value(item, "page_locator", "printed_page_range"), f"item:{item_id}.page_locator"),
                        "source_locator": _locator(_node_value(item, "source_locator", default=declared), f"item:{item_id}.source_locator"),
                        "content_status": _nonempty(item.get("content_status", unit.get("content_status", "UNKNOWN")), "item_content_status"),
                        "expected_response": expected,
                        "acceptance_criteria": _json_value(item.get("acceptance_criteria"), f"item:{item_id}.acceptance_criteria"),
                        "teacher_guidance": _json_value(item.get("teacher_guidance"), f"item:{item_id}.teacher_guidance"),
                        "common_misconceptions": _json_value(item.get("common_misconceptions"), f"item:{item_id}.common_misconceptions"),
                        "assessment_evidence": _json_value(item.get("assessment_evidence"), f"item:{item_id}.assessment_evidence"),
                        "differentiation": differentiation,
                        "provenance": provenance,
                    }
                    item_rows.append(row)
                    raw_relations = section_relations + unit_relations + _refs(item, f"item:{item_id}")
                    unique_relations: list[tuple[str, str, str]] = []
                    for relation in raw_relations:
                        if relation not in unique_relations:
                            unique_relations.append(relation)
                    for relation_order, (target_type, target_id, relation_type) in enumerate(unique_relations, start=1):
                        resolved_id = _resolve_relation(
                            db,
                            entities,
                            target_type,
                            target_id,
                            course_id,
                            scope_type,
                            scope_id,
                        )
                        pending_relations.append((item_id, target_type, resolved_id, relation_type, relation_order))

    # First build item hashes from the canonical projected content, then write
    # all rows in stable source-array order.
    for row in item_rows:
        payload = {key: row[key] for key in row if key not in {"canonical_payload_sha256"}}
        relations = [
            {"target_type": target_type, "target_id": target_id, "relation_type": relation_type, "order": order}
            for item_id, target_type, target_id, relation_type, order in pending_relations
            if item_id == row["item_id"]
        ]
        payload["relations"] = relations
        row["canonical_payload_sha256"] = sha256_bytes(compact_json(payload).encode("utf-8"))

    db.executemany(
        "INSERT INTO teacher_guides VALUES (?,?,?,?,?,?,?,?)",
        [(r["guide_id"], r["course_id"], r["scope_type"], r["scope_id"], r["title"], r["content_status"], r["schema_version"], compact_json(r["provenance"])) for r in guide_rows],
    )
    db.executemany(
        "INSERT INTO teacher_guide_sections VALUES (?,?,?,?,?,?,?,?,?)",
        [(r["section_id"], r["guide_id"], r["section_order"], r["title"], r["section_type"], r["page_locator"], r["source_locator"], r["content_status"], compact_json(r["provenance"])) for r in section_rows],
    )
    db.executemany(
        "INSERT INTO teacher_guide_units VALUES (?,?,?,?,?,?,?,?,?)",
        [(r["unit_id"], r["section_id"], r["unit_order"], r["title"], r["page_locator"], r["source_locator"], r["content_status"], compact_json(r["purpose"]), compact_json(r["provenance"])) for r in unit_rows],
    )
    db.executemany(
        "INSERT INTO teacher_guide_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(r["item_id"], r["unit_id"], r["item_order"], r["title"], r["label"], r["item_type"], r["page_locator"], r["source_locator"], r["content_status"], compact_json(r["expected_response"]), compact_json(r["acceptance_criteria"]), compact_json(r["teacher_guidance"]), compact_json(r["common_misconceptions"]), compact_json(r["assessment_evidence"]), compact_json(r["differentiation"]), compact_json(r["provenance"]), r["canonical_payload_sha256"]) for r in item_rows],
    )
    db.executemany(
        "INSERT INTO teacher_guide_item_relations VALUES (?,?,?,?,?)",
        pending_relations,
    )
    db.commit()

    counts = {
        "canonical_entities": db.execute("SELECT COUNT(*) FROM canonical_entities").fetchone()[0],
        "teacher_guides": len(guide_rows),
        "teacher_guide_sections": len(section_rows),
        "teacher_guide_units": len(unit_rows),
        "teacher_guide_items": len(item_rows),
        "teacher_guide_item_relations": len(pending_relations),
    }
    source_files = teacher_guide_source_files(course_root)
    source_hashes = {key: sha256_file(path) for key, path in source_files}
    teacher_payload = {
        "projection_version": PROJECTION_VERSION,
        "source_hashes": source_hashes,
        "row_counts": counts,
        "items": [
            {"item_id": row["item_id"], "canonical_payload_sha256": row["canonical_payload_sha256"]}
            for row in item_rows
        ],
    }
    teacher_fingerprint = sha256_bytes(compact_json(teacher_payload).encode("utf-8"))
    status = "PASS" if counts["teacher_guide_items"] > 0 else "FAIL"
    source_status = (
        "PASS_WITH_WARNINGS"
        if "PASS_WITH_WARNINGS" in source_validation_statuses
        else "PASS"
    )
    seal = {
        "seal_type": "TEACHER_GUIDE_COURSE_VALIDATION_SEAL",
        "projection_version": PROJECTION_VERSION,
        "status": status,
        "scope": "COURSE",
        "course_id": course_id,
        "canonical_content_fingerprint": runtime_manifest.get("canonical_content_fingerprint"),
        "teacher_guide_content_fingerprint": teacher_fingerprint,
        "source_validation_status": source_status,
        "source_files": source_hashes,
        "row_counts": counts,
    }
    seal_path = course_root / "runtime" / TEACHER_GUIDE_SEAL_FILENAME
    seal_path.parent.mkdir(parents=True, exist_ok=True)
    seal_path.write_text(compact_json(seal) + "\n", encoding="utf-8")
    seal_sha256 = sha256_file(seal_path)
    validation = {
        "status": status,
        "scope": "COURSE",
        "source_bound": True,
        "content_fingerprint": f"sha256:{teacher_fingerprint}",
        "canonical_content_fingerprint": runtime_manifest.get("canonical_content_fingerprint"),
        "source_validation_status": source_status,
        "seal_path": f"runtime/{TEACHER_GUIDE_SEAL_FILENAME}",
        "seal_sha256": seal_sha256,
        "projection_version": PROJECTION_VERSION,
    }
    capability = {
        "available": status == "PASS",
        "schema_version": TEACHER_GUIDE_SCHEMA_VERSION,
        "validation_status": status,
        "source_bound": True,
        "source_validation_status": source_status,
        "row_counts": counts,
    }
    return {"capability": capability, "validation": validation}


def validate_teacher_guide_runtime(
    db: sqlite3.Connection,
    runtime_manifest: dict[str, Any],
    course_root: Path | None = None,
) -> list[str]:
    """Return deterministic validation errors for compiler finalization."""
    errors: list[str] = []
    advertised = runtime_manifest.get("capabilities", {}).get("teacher_guide") is True
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    present = {
        "canonical_entities",
        "teacher_guides",
        "teacher_guide_sections",
        "teacher_guide_units",
        "teacher_guide_items",
        "teacher_guide_item_relations",
    }
    if not advertised:
        metadata = runtime_manifest.get("teacher_guide_capabilities")
        if isinstance(metadata, dict):
            if metadata.get("available") is not False or metadata.get("source_bound") is not False or metadata.get("validation_status") != "NOT_PRESENT":
                errors.append("teacher_guide_disabled_metadata_inconsistent")
        validation = runtime_manifest.get("teacher_guide_validation")
        if isinstance(validation, dict):
            if validation.get("status") != "NOT_PRESENT" or validation.get("source_bound") is not False:
                errors.append("teacher_guide_disabled_validation_inconsistent")
        for table in (present - {"canonical_entities"}) & tables:
            if db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] != 0:
                errors.append(f"teacher_guide_disabled_but_{table}_not_empty")
        return errors
    if not present.issubset(tables):
        errors.append("teacher_guide_tables_missing")
        return errors
    if db.execute("PRAGMA foreign_key_check").fetchall():
        errors.append("teacher_guide_foreign_key_check_failed")
    validation = runtime_manifest.get("teacher_guide_validation", {})
    if validation.get("status") != "PASS" or validation.get("scope") != "COURSE" or validation.get("source_bound") is not True:
        errors.append("teacher_guide_validation_evidence_invalid")
    if validation.get("canonical_content_fingerprint") != runtime_manifest.get("canonical_content_fingerprint"):
        errors.append("teacher_guide_validation_canonical_fingerprint_mismatch")
    metadata = runtime_manifest.get("teacher_guide_capabilities", {})
    if metadata.get("available") is not True or metadata.get("validation_status") != "PASS" or metadata.get("source_bound") is not True:
        errors.append("teacher_guide_capability_metadata_inconsistent")
    expected_counts = runtime_manifest.get("row_counts", {})
    declared_counts = metadata.get("row_counts", {})
    for table in present:
        actual = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if expected_counts.get(table) != actual:
            errors.append(f"teacher_guide_manifest_row_count_mismatch:{table}")
        if declared_counts.get(table) != actual:
            errors.append(f"teacher_guide_capability_row_count_mismatch:{table}")
    seal_path = validation.get("seal_path")
    seal_sha = validation.get("seal_sha256")
    if not isinstance(seal_path, str) or not seal_path or not isinstance(seal_sha, str) or not seal_sha:
        errors.append("teacher_guide_seal_evidence_missing")
    elif course_root is not None:
        seal_file = (course_root / seal_path).resolve()
        try:
            seal_file.relative_to(course_root.resolve())
        except ValueError:
            errors.append("teacher_guide_seal_path_outside_course")
        else:
            if not seal_file.is_file():
                errors.append("teacher_guide_seal_file_missing")
            elif sha256_file(seal_file) != seal_sha:
                errors.append("teacher_guide_seal_sha256_mismatch")
            else:
                try:
                    seal = json.loads(seal_file.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    errors.append("teacher_guide_seal_json_invalid")
                else:
                    if seal.get("canonical_content_fingerprint") != runtime_manifest.get("canonical_content_fingerprint"):
                        errors.append("teacher_guide_seal_canonical_fingerprint_mismatch")
                    expected_teacher_fingerprint = validation.get("content_fingerprint", "")
                    if isinstance(expected_teacher_fingerprint, str) and expected_teacher_fingerprint.startswith("sha256:"):
                        expected_teacher_fingerprint = expected_teacher_fingerprint[len("sha256:"):]
                    if seal.get("teacher_guide_content_fingerprint") != expected_teacher_fingerprint:
                        errors.append("teacher_guide_seal_content_fingerprint_mismatch")
    if not db.execute("SELECT 1 FROM teacher_guide_items LIMIT 1").fetchone():
        errors.append("teacher_guide_items_empty")
    for table, order_column, parent_column in (
        ("teacher_guide_sections", "section_order", "guide_id"),
        ("teacher_guide_units", "unit_order", "section_id"),
        ("teacher_guide_items", "item_order", "unit_id"),
    ):
        groups = db.execute(
            f"SELECT {parent_column}, GROUP_CONCAT({order_column}, ',') FROM {table} GROUP BY {parent_column}"
        ).fetchall()
        for parent, raw in groups:
            orders = [int(value) for value in str(raw).split(",")]
            if orders != list(range(1, len(orders) + 1)):
                errors.append(f"{table}_order_not_contiguous:{parent}")
    return errors
