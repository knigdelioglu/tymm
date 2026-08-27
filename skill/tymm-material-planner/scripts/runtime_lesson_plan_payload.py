#!/usr/bin/env python3
"""Project validated TYMM lesson-plan packages into runtime SQLite.

Canonical lesson-plan JSON remains the validated source of truth. Runtime
payload_json is a deterministic teacher-facing projection of that source:
structured IDs stay canonical while prose is resolved to readable Turkish
labels from verified course metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

import teacher_facing_text
import validation_binding

PROJECTION_VERSION = "1.2.0"
RUNTIME_SCHEMA_VERSION = "1.2.0"
RUNTIME_PACKAGE_VERSION = "1.3.0"

PACKAGE_ID_RE = re.compile(r"^(?P<block_id>.+)_P(?P<package_no>\d{2})$")
VALIDATION_SEAL_FILENAME = "lesson_plan_validation_seal.json"
LESSON_PLAN_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "schemas" / "lesson_plan.schema.json"
)
REQUIRED_ENGINEERING_CHECKS = {
    "JSON_SCHEMA_DRAFT_2020_12",
    "SOURCE_BOUND_GROUNDING",
    "NESTED_REFERENCE_GROUNDING",
    "CALENDAR_SCOPE",
    "DETERMINISTIC_JSON_MARKDOWN_PARITY",
    "PACKAGE_TOPOLOGY",
    "PACKAGE_COUNT",
    "LESSON_HOUR_TOTAL",
    "FRESH_RUNTIME_CONTEXT",
    "VALIDATION_REPORT_PASS",
    "VALIDATED_COMMIT_SHA",
    "VALIDATED_CONTENT_FINGERPRINT",
}

TABLE_SQL = """
CREATE TABLE IF NOT EXISTS lesson_plan_packages (
    package_id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL REFERENCES courses(course_id),
    theme_id TEXT NOT NULL REFERENCES themes(theme_id),
    block_id TEXT NOT NULL REFERENCES blocks(block_id),
    package_no INTEGER NOT NULL CHECK(package_no > 0),
    lesson_hours INTEGER NOT NULL CHECK(lesson_hours > 0),
    plan_title TEXT NOT NULL,
    plan_summary TEXT NOT NULL,
    remaining_block_hours INTEGER NOT NULL CHECK(remaining_block_hours >= 0),
    schema_version TEXT NOT NULL,
    validation_status TEXT NOT NULL,
    source_path TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    UNIQUE(block_id, package_no)
);
CREATE INDEX IF NOT EXISTS idx_lesson_plan_theme_block
    ON lesson_plan_packages(theme_id, block_id, package_no);
CREATE INDEX IF NOT EXISTS idx_lesson_plan_block_package
    ON lesson_plan_packages(block_id, package_no);
"""


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"LESSON_PLAN_JSON_OBJECT_REQUIRED: {path}")
    return value


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _compact_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _append_schema_extension(schema_path: Path) -> None:
    marker = "-- lesson-plan-payload-extension-v1"
    text = schema_path.read_text(encoding="utf-8") if schema_path.exists() else ""
    if marker in text:
        return
    extension = f"\n{marker}\n{TABLE_SQL.strip()}\n"
    schema_path.write_text(text.rstrip() + "\n" + extension, encoding="utf-8")


def _append_validation_section(
    report_path: Path,
    checks: list[tuple[str, bool, str]],
) -> None:
    if not report_path.exists():
        return
    marker = "## Lesson plan payload projection"
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
    report_path.write_text(
        text.rstrip() + "\n" + "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def _production_topology(production_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    topology: dict[str, dict[str, Any]] = {}
    for theme in production_plan.get("themes", []):
        if not isinstance(theme, dict):
            continue
        theme_id = theme.get("theme_id")
        for block in theme.get("blocks", []):
            if not isinstance(block, dict) or not block.get("block_id"):
                continue
            block_id = str(block["block_id"])
            topology[block_id] = {
                "theme_id": theme_id,
                "package_count": block.get("package_count"),
                "planned_hours": block.get("planned_hours"),
            }
    return topology


def _recompute_runtime_fingerprint(
    runtime_manifest: dict[str, Any],
    additional_hashes: dict[str, str],
) -> str:
    hashes = dict(runtime_manifest.get("canonical_source_hashes") or {})
    # Validation seals are derived proof metadata, not canonical lesson-plan
    # content. Keep them outside the runtime content fingerprint so freshness
    # remains equal to compiler_state while the seal is verified separately.
    hashes.pop(f"planning/{VALIDATION_SEAL_FILENAME}", None)
    hashes.update(additional_hashes)
    canonical = "\n".join(f"{key}:{hashes[key]}" for key in sorted(hashes))
    fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    runtime_manifest["canonical_source_hashes"] = {
        key: hashes[key] for key in sorted(hashes)
    }
    runtime_manifest["canonical_source_files"] = sorted(hashes)
    runtime_manifest["canonical_content_fingerprint"] = fingerprint
    return fingerprint


def _verify_validation_seal(
    root: Path,
    course_id: str,
    production_plan: dict[str, Any],
    expected_package_count: int,
    expected_hours: int,
) -> tuple[Path, dict[str, Any]]:
    progress = production_plan.get("progress") or {}
    if progress.get("completed_packages") != expected_package_count:
        raise ValueError("RUNTIME_LESSON_PLAN_COMPLETED_PACKAGE_COUNT_MISMATCH")
    if progress.get("completed_instruction_hours") != expected_hours:
        raise ValueError("RUNTIME_LESSON_PLAN_COMPLETED_HOURS_MISMATCH")
    if progress.get("next") is not None:
        raise ValueError("RUNTIME_LESSON_PLAN_NEXT_PACKAGE_MUST_BE_NULL")

    engineering = production_plan.get("engineering_validation") or {}
    if engineering.get("status") != "PASS":
        raise ValueError(
            "RUNTIME_LESSON_PLAN_ENGINEERING_VALIDATION_NOT_PASS: "
            f"{engineering.get('status')}"
        )
    if engineering.get("scope") != "FULL_GENERATED_LESSON_PLAN_SET":
        raise ValueError("RUNTIME_LESSON_PLAN_ENGINEERING_SCOPE_INVALID")
    if engineering.get("validated_packages") != expected_package_count:
        raise ValueError("RUNTIME_LESSON_PLAN_ENGINEERING_PACKAGE_COUNT_MISMATCH")
    if engineering.get("validated_instruction_hours") != expected_hours:
        raise ValueError("RUNTIME_LESSON_PLAN_ENGINEERING_HOURS_MISMATCH")
    if engineering.get("failure_records") != 0 or engineering.get("warning_records") != 0:
        raise ValueError("RUNTIME_LESSON_PLAN_ENGINEERING_NOT_CLEAN")
    checks = engineering.get("checks")
    if not isinstance(checks, list) or not REQUIRED_ENGINEERING_CHECKS.issubset(set(checks)):
        missing = sorted(REQUIRED_ENGINEERING_CHECKS - set(checks or []))
        raise ValueError(
            "RUNTIME_LESSON_PLAN_ENGINEERING_CHECKS_MISSING:" + ",".join(missing)
        )

    seal_path = root / "planning" / VALIDATION_SEAL_FILENAME
    if not seal_path.exists():
        raise ValueError("RUNTIME_LESSON_PLAN_VALIDATION_SEAL_MISSING")
    seal = _read_json(seal_path)
    if seal.get("seal_type") != "LESSON_PLAN_COURSE_VALIDATION_SEAL":
        raise ValueError("RUNTIME_LESSON_PLAN_VALIDATION_SEAL_TYPE_INVALID")
    if seal.get("course_id") != course_id:
        raise ValueError("RUNTIME_LESSON_PLAN_VALIDATION_SEAL_COURSE_MISMATCH")
    if seal.get("status") != "PASS":
        raise ValueError("RUNTIME_LESSON_PLAN_VALIDATION_SEAL_NOT_PASS")
    if seal.get("scope") != "FULL_GENERATED_LESSON_PLAN_SET":
        raise ValueError("RUNTIME_LESSON_PLAN_VALIDATION_SEAL_SCOPE_INVALID")
    if seal.get("validated_packages") != expected_package_count:
        raise ValueError("RUNTIME_LESSON_PLAN_VALIDATION_SEAL_PACKAGE_COUNT_MISMATCH")
    if seal.get("validated_instruction_hours") != expected_hours:
        raise ValueError("RUNTIME_LESSON_PLAN_VALIDATION_SEAL_HOURS_MISMATCH")
    if seal.get("failure_records") != 0 or seal.get("warning_records") != 0:
        raise ValueError("RUNTIME_LESSON_PLAN_VALIDATION_SEAL_NOT_CLEAN")

    stored_binding = seal.get("validation_binding")
    if not isinstance(stored_binding, dict):
        raise ValueError("RUNTIME_LESSON_PLAN_VALIDATION_BINDING_MISSING")
    current_binding = validation_binding.compute_content_binding(
        [root],
        LESSON_PLAN_SCHEMA_PATH,
    )
    for key in (
        "schema_version",
        "algorithm",
        "content_fingerprint",
        "fingerprinted_files",
    ):
        if stored_binding.get(key) != current_binding.get(key):
            raise ValueError(
                "RUNTIME_LESSON_PLAN_COURSE_VALIDATION_BINDING_MISMATCH:"
                f"{key}:{stored_binding.get(key)}!={current_binding.get(key)}"
            )
    validation_binding.resolve_commit_sha(stored_binding.get("commit_sha"))

    embedded_binding = engineering.get("course_validation_binding")
    if embedded_binding is not None:
        if not isinstance(embedded_binding, dict):
            raise ValueError("RUNTIME_LESSON_PLAN_EMBEDDED_BINDING_INVALID")
        for key in (
            "schema_version",
            "algorithm",
            "content_fingerprint",
            "fingerprinted_files",
        ):
            if embedded_binding.get(key) != stored_binding.get(key):
                raise ValueError(
                    "RUNTIME_LESSON_PLAN_EMBEDDED_BINDING_MISMATCH:"
                    f"{key}"
                )

    return seal_path, {
        **current_binding,
        "validated_commit_sha": stored_binding.get("commit_sha"),
    }


def project_runtime_lesson_plan_payload(root: Path | str) -> dict[str, Any]:
    root = Path(root).resolve()
    runtime = root / "runtime"
    db_path = runtime / "course_runtime.sqlite"
    manifest_path = runtime / "runtime_manifest.json"
    schema_path = runtime / "runtime_schema.sql"
    validation_report_path = runtime / "runtime_validation_report.md"
    production_plan_path = root / "planning" / "lesson_plan_production_plan.json"
    lesson_plan_root = root / "generated" / "lesson_plans"

    for required in (db_path, manifest_path):
        if not required.exists():
            raise ValueError(f"RUNTIME_LESSON_PLAN_MISSING_INPUT: {required}")

    runtime_manifest = _read_json(manifest_path)
    course_id = str(runtime_manifest.get("course_id") or "")
    if not course_id:
        raise ValueError("RUNTIME_LESSON_PLAN_COURSE_ID_MISSING")

    plan_files = sorted(lesson_plan_root.glob("*/*/*.json")) if lesson_plan_root.exists() else []
    if not production_plan_path.exists() and not plan_files:
        # Courses without a generated lesson-plan database remain valid runtimes.
        runtime_manifest["lesson_plan_payload_projection_version"] = PROJECTION_VERSION
        runtime_manifest["lesson_plan_capabilities"] = {
            "available": False,
            "package_payload_json": False,
            "block_package_navigation": False,
            "teacher_facing_projection": False,
            "validation_bound": False,
        }
        runtime_manifest.setdefault("row_counts", {})["lesson_plan_packages"] = 0
        manifest_path.write_text(
            json.dumps(runtime_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return {
            "status": "PASS",
            "projection_version": PROJECTION_VERSION,
            "package_count": 0,
            "instruction_hours": 0,
            "available": False,
        }

    if not production_plan_path.exists():
        raise ValueError("RUNTIME_LESSON_PLAN_PRODUCTION_PLAN_MISSING")
    if not plan_files:
        raise ValueError("RUNTIME_LESSON_PLAN_FILES_MISSING")

    production_plan = _read_json(production_plan_path)
    if production_plan.get("course_id") != course_id:
        raise ValueError(
            "RUNTIME_LESSON_PLAN_PRODUCTION_COURSE_MISMATCH: "
            f"{production_plan.get('course_id')} != {course_id}"
        )
    if production_plan.get("status") != "COMPLETED":
        raise ValueError(
            "RUNTIME_LESSON_PLAN_PRODUCTION_NOT_COMPLETED: "
            f"{production_plan.get('status')}"
        )

    progress = production_plan.get("progress") or {}
    expected_package_count = progress.get("total_packages")
    expected_hours = progress.get("queued_instruction_hours")
    if not isinstance(expected_package_count, int) or expected_package_count <= 0:
        raise ValueError("RUNTIME_LESSON_PLAN_EXPECTED_PACKAGE_COUNT_INVALID")
    if not isinstance(expected_hours, int) or expected_hours <= 0:
        raise ValueError("RUNTIME_LESSON_PLAN_EXPECTED_HOURS_INVALID")

    validation_seal_path, verified_binding = _verify_validation_seal(
        root,
        course_id,
        production_plan,
        expected_package_count,
        expected_hours,
    )

    topology = _production_topology(production_plan)
    teacher_catalog = teacher_facing_text.TeacherReferenceCatalog.from_knowledge_root(root)
    package_range_cache: dict[str, dict[int, teacher_facing_text.PackageRange]] = {}
    additional_hashes = {
        production_plan_path.relative_to(root).as_posix(): _sha256(production_plan_path),
    }

    def teacher_projection(source_payload: dict[str, Any], path: Path) -> dict[str, Any]:
        block_id = str(source_payload.get("block_id") or path.parent.name)
        ranges = package_range_cache.get(block_id)
        if ranges is None:
            ranges = teacher_facing_text.package_ranges_for_block(path.parent)
            package_range_cache[block_id] = ranges
        return teacher_facing_text.normalize_teacher_facing_text(
            source_payload,
            catalog=teacher_catalog,
            package_ranges=ranges,
        )

    db = sqlite3.connect(db_path)
    db.execute("PRAGMA foreign_keys=ON")
    try:
        db.executescript(TABLE_SQL)
        db.execute("DELETE FROM lesson_plan_packages")

        runtime_course = db.execute(
            "SELECT course_id FROM courses LIMIT 1"
        ).fetchone()
        if runtime_course is None or runtime_course[0] != course_id:
            raise ValueError("RUNTIME_LESSON_PLAN_RUNTIME_COURSE_MISMATCH")
        theme_ids = {row[0] for row in db.execute("SELECT theme_id FROM themes")}
        block_theme = {
            row[0]: row[1]
            for row in db.execute("SELECT block_id,theme_id FROM blocks")
        }

        package_numbers: dict[str, set[int]] = {}
        block_hours: dict[str, int] = {}
        projected_hours = 0

        for path in plan_files:
            payload = _read_json(path)
            source_path = path.relative_to(root).as_posix()
            additional_hashes[source_path] = _sha256(path)

            package_id = path.stem
            match = PACKAGE_ID_RE.fullmatch(package_id)
            if match is None:
                raise ValueError(f"RUNTIME_LESSON_PLAN_PACKAGE_ID_INVALID: {package_id}")
            block_id = match.group("block_id")
            package_no = int(match.group("package_no"))
            theme_id = str(payload.get("theme_id") or "")

            if payload.get("course_id") != course_id:
                raise ValueError(f"RUNTIME_LESSON_PLAN_COURSE_MISMATCH: {source_path}")
            if payload.get("block_id") != block_id:
                raise ValueError(f"RUNTIME_LESSON_PLAN_BLOCK_ID_MISMATCH: {source_path}")
            if path.parent.name != block_id or path.parent.parent.name != theme_id:
                raise ValueError(f"RUNTIME_LESSON_PLAN_PATH_ID_MISMATCH: {source_path}")
            if theme_id not in theme_ids:
                raise ValueError(f"RUNTIME_LESSON_PLAN_UNKNOWN_THEME: {theme_id}")
            if block_id not in block_theme:
                raise ValueError(f"RUNTIME_LESSON_PLAN_UNKNOWN_BLOCK: {block_id}")
            if block_theme[block_id] != theme_id:
                raise ValueError(
                    f"RUNTIME_LESSON_PLAN_BLOCK_THEME_MISMATCH: {block_id}/{theme_id}"
                )

            topology_entry = topology.get(block_id)
            if topology_entry is None:
                raise ValueError(f"RUNTIME_LESSON_PLAN_BLOCK_NOT_IN_PRODUCTION_PLAN: {block_id}")
            if topology_entry.get("theme_id") != theme_id:
                raise ValueError(
                    f"RUNTIME_LESSON_PLAN_PRODUCTION_THEME_MISMATCH: {block_id}"
                )

            lesson_hours = payload.get("lesson_hours")
            if not isinstance(lesson_hours, int) or lesson_hours <= 0:
                raise ValueError(f"RUNTIME_LESSON_PLAN_HOURS_INVALID: {source_path}")
            continuation = payload.get("continuation_summary") or {}
            remaining = continuation.get("remaining_block_hours")
            if not isinstance(remaining, int) or remaining < 0:
                raise ValueError(
                    f"RUNTIME_LESSON_PLAN_REMAINING_HOURS_INVALID: {source_path}"
                )

            runtime_payload = teacher_projection(payload, path)
            plan_title = runtime_payload.get("plan_title")
            plan_summary = runtime_payload.get("plan_summary")
            schema_version = payload.get("schema_version")
            if not isinstance(plan_title, str) or not plan_title.strip():
                raise ValueError(f"RUNTIME_LESSON_PLAN_TITLE_MISSING: {source_path}")
            if not isinstance(plan_summary, str) or not plan_summary.strip():
                raise ValueError(f"RUNTIME_LESSON_PLAN_SUMMARY_MISSING: {source_path}")
            if not isinstance(schema_version, str) or not schema_version.strip():
                raise ValueError(f"RUNTIME_LESSON_PLAN_SCHEMA_MISSING: {source_path}")

            package_numbers.setdefault(block_id, set()).add(package_no)
            block_hours[block_id] = block_hours.get(block_id, 0) + lesson_hours
            projected_hours += lesson_hours

            db.execute(
                """
                INSERT INTO lesson_plan_packages (
                    package_id,course_id,theme_id,block_id,package_no,
                    lesson_hours,plan_title,plan_summary,remaining_block_hours,
                    schema_version,validation_status,source_path,payload_sha256,
                    payload_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    package_id,
                    course_id,
                    theme_id,
                    block_id,
                    package_no,
                    lesson_hours,
                    plan_title,
                    plan_summary,
                    remaining,
                    schema_version,
                    "PASS",
                    source_path,
                    additional_hashes[source_path],
                    _compact_json(runtime_payload),
                ),
            )

        projected_count = db.execute(
            "SELECT COUNT(*) FROM lesson_plan_packages"
        ).fetchone()[0]

        topology_ok = True
        topology_details: list[str] = []
        for block_id, entry in topology.items():
            package_count = entry.get("package_count")
            planned_hours = entry.get("planned_hours")
            expected_numbers = (
                set(range(1, package_count + 1))
                if isinstance(package_count, int) and package_count > 0
                else set()
            )
            actual_numbers = package_numbers.get(block_id, set())
            actual_hours = block_hours.get(block_id, 0)
            block_ok = (
                expected_numbers == actual_numbers
                and isinstance(planned_hours, int)
                and actual_hours == planned_hours
            )
            topology_ok = topology_ok and block_ok
            if not block_ok:
                topology_details.append(
                    f"{block_id}: packages={sorted(actual_numbers)} "
                    f"expected={sorted(expected_numbers)} hours={actual_hours}/{planned_hours}"
                )

        payload_json_valid = True
        teacher_projection_parity = True
        teacher_projection_parity_detail = (
            "all SQLite payloads match deterministic teacher-facing projection and source SHA256"
        )
        try:
            for source_path, payload_sha256, payload_json in db.execute(
                "SELECT source_path,payload_sha256,payload_json FROM lesson_plan_packages"
            ):
                source = root / source_path
                if not source.exists():
                    teacher_projection_parity = False
                    teacher_projection_parity_detail = f"missing source: {source_path}"
                    break
                source_payload = _read_json(source)
                if payload_sha256 != _sha256(source):
                    teacher_projection_parity = False
                    teacher_projection_parity_detail = f"SHA mismatch: {source_path}"
                    break
                parsed_payload = json.loads(payload_json)
                expected_payload = teacher_projection(source_payload, source)
                if parsed_payload != expected_payload:
                    teacher_projection_parity = False
                    teacher_projection_parity_detail = f"projection mismatch: {source_path}"
                    break
        except (TypeError, json.JSONDecodeError, teacher_facing_text.TeacherFacingTextError):
            payload_json_valid = False
            teacher_projection_parity = False
            teacher_projection_parity_detail = "payload_json/projection failure"

        checks = [
            (
                "lesson plan validation seal",
                True,
                f"verified={verified_binding['content_fingerprint']}",
            ),
            (
                "lesson plan package count",
                projected_count == expected_package_count,
                f"runtime={projected_count}, expected={expected_package_count}",
            ),
            (
                "lesson plan instruction hours",
                projected_hours == expected_hours,
                f"runtime={projected_hours}, expected={expected_hours}",
            ),
            (
                "lesson plan block topology",
                topology_ok,
                "all blocks match package count and planned hours"
                if topology_ok
                else "; ".join(topology_details[:4]),
            ),
            (
                "lesson plan payload JSON validity",
                payload_json_valid,
                "all payload_json rows parse",
            ),
            (
                "lesson plan teacher-facing projection parity",
                teacher_projection_parity,
                teacher_projection_parity_detail,
            ),
            (
                "lesson plan foreign key integrity",
                db.execute("PRAGMA foreign_key_check").fetchall() == [],
                "PRAGMA foreign_key_check",
            ),
        ]
        if not all(ok for _, ok, _ in checks):
            failed = [name for name, ok, _ in checks if not ok]
            raise ValueError(
                "RUNTIME_LESSON_PLAN_VALIDATION_FAILED: " + ", ".join(failed)
            )

        fingerprint = _recompute_runtime_fingerprint(
            runtime_manifest,
            additional_hashes,
        )
        db.execute(
            "UPDATE courses SET schema_version=?, source_manifest_fingerprint=?",
            (RUNTIME_SCHEMA_VERSION, fingerprint),
        )
        db.commit()

        row_counts = runtime_manifest.setdefault("row_counts", {})
        row_counts["lesson_plan_packages"] = projected_count
        runtime_manifest["schema_version"] = RUNTIME_SCHEMA_VERSION
        runtime_manifest["runtime_package_version"] = RUNTIME_PACKAGE_VERSION
        runtime_manifest["lesson_plan_payload_projection_version"] = PROJECTION_VERSION
        runtime_manifest["lesson_plan_schema_version"] = production_plan.get(
            "source_contract", {}
        ).get("output_schema") or "lesson_plan.schema.json"
        runtime_manifest["lesson_plan_package_count"] = projected_count
        runtime_manifest["lesson_plan_instruction_hours"] = projected_hours
        runtime_manifest["lesson_plan_validation"] = {
            "status": "VERIFIED",
            "scope": "COURSE",
            "binding_schema_version": verified_binding["schema_version"],
            "binding_algorithm": verified_binding["algorithm"],
            "content_fingerprint": verified_binding["content_fingerprint"],
            "fingerprinted_files": verified_binding["fingerprinted_files"],
            "validated_commit_sha": verified_binding["validated_commit_sha"],
            "seal_path": validation_seal_path.relative_to(root).as_posix(),
        }
        runtime_manifest["lesson_plan_capabilities"] = {
            "available": True,
            "package_payload_json": True,
            "block_package_navigation": True,
            "source_hash_per_package": True,
            "source_payload_parity": False,
            "teacher_facing_projection": True,
            "teacher_projection_source_bound": True,
            "validation_bound": True,
            "calendar_neutral": bool(
                (production_plan.get("calendar_policy") or {}).get("calendar_neutral")
            ),
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
            "package_count": projected_count,
            "instruction_hours": projected_hours,
            "canonical_content_fingerprint": fingerprint,
            "lesson_plan_validation_fingerprint": verified_binding["content_fingerprint"],
            "teacher_facing_projection": True,
            "available": True,
        }
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", required=True)
    args = parser.parse_args()
    try:
        result = project_runtime_lesson_plan_payload(args.knowledge_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (
        ValueError,
        sqlite3.Error,
        json.JSONDecodeError,
        teacher_facing_text.TeacherFacingTextError,
    ) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())