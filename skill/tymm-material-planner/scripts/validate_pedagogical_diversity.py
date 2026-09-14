#!/usr/bin/env python3
"""Deterministic pedagogical-diversity checks for TYMM lesson plans.

Grounding/schema validation remains authoritative and separate. This validator
measures teacher-facing lesson progression and verifies the optional package-
design overlays. ADVISORY mode reports similarity signals. STRICT mode also
requires complete overlay coverage, meaningful adjacent-lesson deltas and
non-generic lesson titles.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

GENERIC_TITLE_MARKERS = (
    "kanıt üretme ve geliştirme",
    "kanıt üretme",
    "uygulama ve geliştirme",
)

PROGRESSION_ROLES = {
    "INITIAL_CONSTRUCTION",
    "DEEPENING",
    "TRANSFER",
    "REVISION",
    "SYNTHESIS",
    "PERFORMANCE",
    "REFLECTION",
}

DEFAULT_THRESHOLDS: dict[str, float] = {
    "title_similarity": 0.92,
    "opening_similarity": 0.90,
    "assessment_similarity": 0.94,
    "closure_similarity": 0.94,
    "action_overlap": 0.60,
    "structural_duplicate_dimensions": 4.0,
    "generic_title_share": 0.20,
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def normalize_text(value: Any) -> str:
    text = str(value or "").casefold()
    text = re.sub(r"[^\wçğıöşüâîû]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def similarity(left: Any, right: Any) -> float:
    a = normalize_text(left)
    b = normalize_text(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


def action_overlap(left: Any, right: Any) -> float:
    a = {normalize_text(item) for item in (left or []) if normalize_text(item)}
    b = {normalize_text(item) for item in (right or []) if normalize_text(item)}
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def validate_catalog(catalog: dict[str, Any] | None) -> list[str]:
    if catalog is None:
        return ["PEDAGOGICAL_ROUTE_CATALOG_MISSING"]
    routes = catalog.get("routes")
    if not isinstance(routes, list) or len(routes) < 8:
        return ["PEDAGOGICAL_ROUTE_CATALOG_TOO_SMALL"]

    errors: list[str] = []
    route_ids: list[str] = []
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            errors.append(f"ROUTE_NOT_OBJECT:{index}")
            continue
        route_id = route.get("route_id")
        if not isinstance(route_id, str) or not route_id.strip():
            errors.append(f"ROUTE_ID_MISSING:{index}")
            continue
        route_ids.append(route_id)
        for field in ("label", "lesson_1_pattern", "lesson_2_delta", "student_evidence_pattern"):
            if not isinstance(route.get(field), str) or not route[field].strip():
                errors.append(f"ROUTE_FIELD_MISSING:{route_id}:{field}")

    duplicates = sorted(route_id for route_id, count in Counter(route_ids).items() if count > 1)
    errors.extend(f"DUPLICATE_ROUTE_ID:{route_id}" for route_id in duplicates)
    return errors


def overlay_paths(root: Path) -> list[Path]:
    planning = root / "planning"
    return sorted(planning.glob("pedagogical_package_design*.json"))


def validate_overlay(
    overlay: dict[str, Any] | None,
    *,
    known_packages: set[str],
    valid_routes: set[str],
    strict: bool,
    source_path: str = "planning/pedagogical_package_design.json",
    expected_lesson_nos: dict[str, set[int]] | None = None,
    global_seen: set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    designed: set[str] = set()
    if overlay is None:
        return failures, warnings, designed

    target = failures if strict else warnings
    course_id = overlay.get("course_id")
    if course_id is not None and not isinstance(course_id, str):
        target.append({"path": source_path, "code": "DESIGN_COURSE_ID_INVALID"})

    packages = overlay.get("packages")
    if not isinstance(packages, list):
        target.append({"path": source_path, "code": "DESIGN_PACKAGES_INVALID"})
        return failures, warnings, designed

    local_seen: set[str] = set()
    shared_seen = global_seen if global_seen is not None else set()
    for raw in packages:
        entry = raw if isinstance(raw, dict) else {}
        package_id = entry.get("package_id")
        errors: list[str] = []
        if not isinstance(package_id, str) or not package_id:
            errors.append("PACKAGE_ID_MISSING")
            package_id = "<missing>"
        else:
            if package_id not in known_packages:
                errors.append("PACKAGE_ID_UNKNOWN")
            if package_id in local_seen:
                errors.append("PACKAGE_ID_DUPLICATE_IN_OVERLAY")
            if package_id in shared_seen:
                errors.append("PACKAGE_ID_DUPLICATE_ACROSS_OVERLAYS")
            local_seen.add(package_id)
            shared_seen.add(package_id)
            if package_id in known_packages:
                designed.add(package_id)

        if entry.get("route_id") not in valid_routes:
            errors.append("ROUTE_ID_UNKNOWN")

        progression = entry.get("lesson_progression")
        progression_lesson_nos: set[int] = set()
        if not isinstance(progression, list) or not progression:
            errors.append("LESSON_PROGRESSION_MISSING")
        else:
            for step_raw in progression:
                step = step_raw if isinstance(step_raw, dict) else {}
                lesson_no = step.get("lesson_no")
                if not isinstance(lesson_no, int) or lesson_no < 1:
                    errors.append("PROGRESSION_LESSON_NO_INVALID")
                elif lesson_no in progression_lesson_nos:
                    errors.append("PROGRESSION_LESSON_NO_DUPLICATE")
                else:
                    progression_lesson_nos.add(lesson_no)
                if step.get("role") not in PROGRESSION_ROLES:
                    errors.append("PROGRESSION_ROLE_INVALID")
                for field in ("cognitive_operation", "student_evidence", "delta_from_previous"):
                    if not isinstance(step.get(field), str) or not step[field].strip():
                        errors.append(f"PROGRESSION_FIELD_MISSING:{field}")

        expected = (expected_lesson_nos or {}).get(package_id)
        if expected is not None and progression_lesson_nos != expected:
            errors.append(
                "PROGRESSION_LESSON_SET_MISMATCH:"
                f"actual={sorted(progression_lesson_nos)}:expected={sorted(expected)}"
            )

        if errors:
            target.append(
                {
                    "path": source_path,
                    "package_id": package_id,
                    "code": "INVALID_PACKAGE_DESIGN",
                    "details": sorted(set(errors)),
                }
            )
    return failures, warnings, designed


def analyze_pair(first: dict[str, Any], second: dict[str, Any], thresholds: dict[str, float]) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "title_similarity": round(similarity(first.get("title"), second.get("title")), 4),
        "opening_similarity": round(similarity(first.get("opening"), second.get("opening")), 4),
        "teacher_action_overlap": round(action_overlap(first.get("teacher_actions"), second.get("teacher_actions")), 4),
        "student_action_overlap": round(action_overlap(first.get("student_actions"), second.get("student_actions")), 4),
        "assessment_similarity": round(similarity(first.get("assessment"), second.get("assessment")), 4),
        "closure_similarity": round(similarity(first.get("closure"), second.get("closure")), 4),
    }
    duplicate_dimensions = sum(
        (
            metrics["opening_similarity"] >= thresholds["opening_similarity"],
            metrics["teacher_action_overlap"] >= thresholds["action_overlap"],
            metrics["student_action_overlap"] >= thresholds["action_overlap"],
            metrics["assessment_similarity"] >= thresholds["assessment_similarity"],
            metrics["closure_similarity"] >= thresholds["closure_similarity"],
        )
    )
    metrics["duplicate_dimensions"] = duplicate_dimensions
    metrics["insufficient_delta"] = bool(
        metrics["title_similarity"] >= thresholds["title_similarity"]
        and duplicate_dimensions >= int(thresholds["structural_duplicate_dimensions"])
    )
    return metrics


def validate_course(
    root: Path,
    *,
    strict: bool = False,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    generated = root / "generated/lesson_plans"
    json_files = sorted(generated.glob("**/*.json"))

    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    pair_metrics: list[dict[str, Any]] = []
    lesson_titles: list[tuple[str, str]] = []
    plans: dict[str, dict[str, Any]] = {}
    expected_lesson_nos: dict[str, set[int]] = {}

    for path in json_files:
        relative = path.relative_to(root).as_posix()
        try:
            plan = read_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append({"path": relative, "code": "PLAN_JSON_INVALID", "details": [str(exc)]})
            continue
        package_id = path.stem
        plans[package_id] = plan
        lessons = plan.get("lessons")
        if isinstance(lessons, list):
            expected_lesson_nos[package_id] = {
                int(lesson["lesson_no"])
                for lesson in lessons
                if isinstance(lesson, dict) and isinstance(lesson.get("lesson_no"), int)
            }

    catalog_path = root / "planning/pedagogical_route_catalog.json"
    catalog = read_json(catalog_path) if catalog_path.exists() else None
    catalog_errors = validate_catalog(catalog)
    if catalog_errors:
        failures.append(
            {
                "path": "planning/pedagogical_route_catalog.json",
                "code": "INVALID_PEDAGOGICAL_ROUTE_CATALOG",
                "details": catalog_errors,
            }
        )

    valid_routes = {
        route.get("route_id")
        for route in (catalog or {}).get("routes", [])
        if isinstance(route, dict) and isinstance(route.get("route_id"), str)
    }
    known_packages = set(plans)
    overlays = overlay_paths(root)
    designed_packages: set[str] = set()
    global_seen: set[str] = set()

    if not overlays:
        target = failures if strict else warnings
        target.append({"path": "planning", "code": "PEDAGOGICAL_DESIGN_OVERLAYS_MISSING"})

    for path in overlays:
        relative = path.relative_to(root).as_posix()
        try:
            overlay = read_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            target = failures if strict else warnings
            target.append({"path": relative, "code": "DESIGN_JSON_INVALID", "details": [str(exc)]})
            continue
        if overlay.get("course_id") != root.name:
            target = failures if strict else warnings
            target.append(
                {
                    "path": relative,
                    "code": "DESIGN_COURSE_ID_MISMATCH",
                    "details": [f"{overlay.get('course_id')}!={root.name}"],
                }
            )
        overlay_failures, overlay_warnings, designed = validate_overlay(
            overlay,
            known_packages=known_packages,
            valid_routes=valid_routes,
            strict=strict,
            source_path=relative,
            expected_lesson_nos=expected_lesson_nos,
            global_seen=global_seen,
        )
        failures.extend(overlay_failures)
        warnings.extend(overlay_warnings)
        designed_packages.update(designed)

    missing_designs = sorted(known_packages - designed_packages)
    extra_designs = sorted(global_seen - known_packages)
    design_coverage_complete = not missing_designs and not extra_designs and len(designed_packages) == len(known_packages)
    if missing_designs or extra_designs:
        target = failures if strict else warnings
        target.append(
            {
                "path": "planning/pedagogical_package_design*.json",
                "code": "PEDAGOGICAL_DESIGN_COVERAGE_MISMATCH",
                "details": [
                    f"known_packages={len(known_packages)}",
                    f"designed_packages={len(designed_packages)}",
                    f"missing={missing_designs}",
                    f"extra={extra_designs}",
                ],
            }
        )

    for path in json_files:
        relative = path.relative_to(root).as_posix()
        plan = plans.get(path.stem)
        if plan is None:
            continue
        lessons = plan.get("lessons")
        if not isinstance(lessons, list) or not lessons:
            failures.append({"path": relative, "code": "LESSONS_MISSING"})
            continue

        for lesson in lessons:
            title = lesson.get("title") if isinstance(lesson, dict) else None
            if isinstance(title, str):
                lesson_titles.append((relative, title))

        for index in range(len(lessons) - 1):
            first = lessons[index]
            second = lessons[index + 1]
            if not isinstance(first, dict) or not isinstance(second, dict):
                failures.append({"path": relative, "code": "LESSON_OBJECT_INVALID"})
                continue
            metrics = analyze_pair(first, second, thresholds)
            pair_metrics.append(
                {
                    "path": relative,
                    "from_lesson_no": first.get("lesson_no"),
                    "to_lesson_no": second.get("lesson_no"),
                    **metrics,
                }
            )

            similarities: list[str] = []
            if metrics["title_similarity"] >= thresholds["title_similarity"]:
                similarities.append("LESSON_TITLE_NEAR_DUPLICATE")
            if metrics["opening_similarity"] >= thresholds["opening_similarity"]:
                similarities.append("OPENING_NEAR_DUPLICATE")
            if metrics["teacher_action_overlap"] >= thresholds["action_overlap"]:
                similarities.append("TEACHER_ACTIONS_HIGH_OVERLAP")
            if metrics["student_action_overlap"] >= thresholds["action_overlap"]:
                similarities.append("STUDENT_ACTIONS_HIGH_OVERLAP")
            if metrics["assessment_similarity"] >= thresholds["assessment_similarity"]:
                similarities.append("ASSESSMENT_NEAR_DUPLICATE")
            if metrics["closure_similarity"] >= thresholds["closure_similarity"]:
                similarities.append("CLOSURE_NEAR_DUPLICATE")

            record = {
                "path": relative,
                "code": "INSUFFICIENT_LESSON_DELTA" if metrics["insufficient_delta"] else "PEDAGOGICAL_SIMILARITY",
                "details": similarities,
                "metrics": metrics,
            }
            if metrics["insufficient_delta"] and strict:
                failures.append(record)
            elif similarities:
                warnings.append(record)

    generic_titles = [
        (path, title)
        for path, title in lesson_titles
        if any(marker in normalize_text(title) for marker in GENERIC_TITLE_MARKERS)
    ]
    generic_share = len(generic_titles) / len(lesson_titles) if lesson_titles else 0.0
    if generic_titles and strict:
        failures.append(
            {
                "path": "generated/lesson_plans",
                "code": "GENERIC_LESSON_TITLES_PRESENT",
                "details": [f"count={len(generic_titles)}", *[f"{path}:{title}" for path, title in generic_titles[:20]]],
            }
        )
    elif generic_share > thresholds["generic_title_share"]:
        warnings.append(
            {
                "path": "generated/lesson_plans",
                "code": "GENERIC_TITLE_OVERUSE",
                "details": [
                    f"{len(generic_titles)}/{len(lesson_titles)}={generic_share:.3f}",
                    f"threshold={thresholds['generic_title_share']:.3f}",
                ],
            }
        )

    insufficient_count = sum(1 for item in pair_metrics if item["insufficient_delta"])
    return {
        "course_id": root.name,
        "status": "PASS" if not failures else "FAIL",
        "mode": "STRICT" if strict else "ADVISORY",
        "packages": len(json_files),
        "design_overlays": len(overlays),
        "designed_packages": len(designed_packages),
        "design_coverage_complete": design_coverage_complete,
        "lesson_titles": len(lesson_titles),
        "adjacent_lesson_pairs": len(pair_metrics),
        "insufficient_delta_pairs": insufficient_count,
        "generic_title_count": len(generic_titles),
        "generic_title_share": round(generic_share, 4),
        "thresholds": thresholds,
        "failures": failures,
        "warnings": warnings,
        "pair_metrics": pair_metrics,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument("--report")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    reports = [validate_course(Path(root), strict=args.strict) for root in args.knowledge_root]
    payload = {
        "status": "PASS" if all(report["status"] == "PASS" for report in reports) else "FAIL",
        "mode": "STRICT" if args.strict else "ADVISORY",
        "courses": reports,
        "summary": {
            "courses": len(reports),
            "packages": sum(report["packages"] for report in reports),
            "design_overlays": sum(report["design_overlays"] for report in reports),
            "designed_packages": sum(report["designed_packages"] for report in reports),
            "adjacent_lesson_pairs": sum(report["adjacent_lesson_pairs"] for report in reports),
            "insufficient_delta_pairs": sum(report["insufficient_delta_pairs"] for report in reports),
            "generic_title_count": sum(report["generic_title_count"] for report in reports),
            "failure_records": sum(len(report["failures"]) for report in reports),
            "warning_records": sum(len(report["warnings"]) for report in reports),
        },
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
