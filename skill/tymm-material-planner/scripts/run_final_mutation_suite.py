#!/usr/bin/env python3
"""Run the final fail-closed mutation matrix for TYMM lesson-plan production."""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import inspect
import io
import json
import sys
import unittest
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = REPO_ROOT / "skill/tymm-material-planner/tests/final_mutation_manifest.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(path: Path, cache: dict[Path, Any]) -> Any:
    path = path.resolve()
    if path in cache:
        return cache[path]
    module_name = "tymm_final_mutation_" + "_".join(path.relative_to(REPO_ROOT).parts).replace(".", "_").replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"MUTATION_TEST_MODULE_UNLOADABLE:{path.relative_to(REPO_ROOT).as_posix()}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    cache[path] = module
    return module


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != "1.0.0":
        errors.append("MUTATION_MANIFEST_SCHEMA_VERSION_UNSUPPORTED")

    required = manifest.get("required_risk_families")
    mutations = manifest.get("mutations")
    if not isinstance(required, list) or not required or not all(isinstance(item, str) and item for item in required):
        errors.append("MUTATION_REQUIRED_RISK_FAMILIES_INVALID")
        required = []
    if not isinstance(mutations, list) or not mutations:
        errors.append("MUTATION_CASES_MISSING")
        mutations = []

    ids: list[str] = []
    covered: list[str] = []
    for index, case in enumerate(mutations, start=1):
        prefix = f"MUTATION_CASE_{index}"
        if not isinstance(case, dict):
            errors.append(f"{prefix}:NOT_OBJECT")
            continue
        mutation_id = case.get("id")
        risk_family = case.get("risk_family")
        test_file = case.get("test_file")
        test_class = case.get("test_class")
        test_method = case.get("test_method")
        detectors = case.get("expected_detectors")
        if not isinstance(mutation_id, str) or not mutation_id:
            errors.append(f"{prefix}:ID_INVALID")
        else:
            ids.append(mutation_id)
        if not isinstance(risk_family, str) or not risk_family:
            errors.append(f"{prefix}:RISK_FAMILY_INVALID")
        else:
            covered.append(risk_family)
        if not isinstance(test_file, str) or not test_file:
            errors.append(f"{prefix}:TEST_FILE_INVALID")
        if not isinstance(test_class, str) or not test_class:
            errors.append(f"{prefix}:TEST_CLASS_INVALID")
        if not isinstance(test_method, str) or not test_method.startswith("test_"):
            errors.append(f"{prefix}:TEST_METHOD_INVALID")
        if not isinstance(detectors, list) or not detectors or not all(isinstance(item, str) and item for item in detectors):
            errors.append(f"{prefix}:EXPECTED_DETECTORS_INVALID")

    duplicate_ids = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        errors.append("MUTATION_IDS_NOT_UNIQUE:" + ",".join(duplicate_ids))

    missing = sorted(set(required) - set(covered))
    unexpected = sorted(set(covered) - set(required))
    if missing:
        errors.append("MUTATION_RISK_FAMILIES_MISSING:" + ",".join(missing))
    if unexpected:
        errors.append("MUTATION_RISK_FAMILIES_UNDECLARED:" + ",".join(unexpected))
    return errors


def run_case(case: dict[str, Any], module_cache: dict[Path, Any]) -> dict[str, Any]:
    test_path = REPO_ROOT / case["test_file"]
    if not test_path.is_file():
        return {
            "id": case["id"],
            "risk_family": case["risk_family"],
            "status": "SURVIVED",
            "errors": [f"MUTATION_TEST_FILE_MISSING:{case['test_file']}"],
        }

    try:
        module = load_module(test_path, module_cache)
        test_class = getattr(module, case["test_class"])
        if not issubclass(test_class, unittest.TestCase):
            raise ValueError("TEST_CLASS_NOT_UNITTEST_CASE")
        test_method = getattr(test_class, case["test_method"])
        source = inspect.getsource(test_method)
        missing_detectors = [token for token in case["expected_detectors"] if token not in source]
        if missing_detectors:
            raise ValueError("EXPECTED_DETECTOR_NOT_ASSERTED:" + ",".join(missing_detectors))
    except (AttributeError, TypeError, ValueError, OSError) as exc:
        return {
            "id": case["id"],
            "risk_family": case["risk_family"],
            "status": "SURVIVED",
            "errors": [str(exc)],
        }

    suite = unittest.TestSuite([test_class(case["test_method"])])
    stream = io.StringIO()
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)

    failures = [text for _, text in result.failures]
    errors = [text for _, text in result.errors]
    unexpected = [str(item) for item in result.unexpectedSuccesses]
    successful = result.wasSuccessful() and result.testsRun == 1
    return {
        "id": case["id"],
        "risk_family": case["risk_family"],
        "test": f"{case['test_file']}::{case['test_class']}.{case['test_method']}",
        "expected_detectors": case["expected_detectors"],
        "status": "KILLED" if successful else "SURVIVED",
        "tests_run": result.testsRun,
        "errors": failures + errors + unexpected,
        "captured_output": captured.getvalue()[-2000:] if not successful else "",
    }


def run(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    manifest_errors = validate_manifest(manifest)
    if manifest_errors:
        return {
            "status": "FAIL",
            "manifest": manifest_path.relative_to(REPO_ROOT).as_posix(),
            "manifest_errors": manifest_errors,
            "summary": {
                "risk_families": 0,
                "mutation_cases": 0,
                "killed_mutations": 0,
                "surviving_mutations": 0,
                "mutation_score": 0.0,
            },
            "mutations": [],
        }

    module_cache: dict[Path, Any] = {}
    results = [run_case(case, module_cache) for case in manifest["mutations"]]
    killed = sum(item["status"] == "KILLED" for item in results)
    survived = len(results) - killed
    risk_counts = Counter(item["risk_family"] for item in results if item["status"] == "KILLED")
    required = manifest["required_risk_families"]
    uncovered = [risk for risk in required if risk_counts[risk] == 0]
    status = "PASS" if survived == 0 and not uncovered else "FAIL"
    return {
        "status": status,
        "manifest": manifest_path.relative_to(REPO_ROOT).as_posix(),
        "required_risk_families": required,
        "uncovered_risk_families": uncovered,
        "summary": {
            "risk_families": len(required),
            "mutation_cases": len(results),
            "killed_mutations": killed,
            "surviving_mutations": survived,
            "mutation_score": round(killed / len(results), 6) if results else 0.0,
        },
        "coverage_by_risk_family": {
            risk: {
                "mutation_cases": sum(item["risk_family"] == risk for item in results),
                "killed_mutations": sum(item["risk_family"] == risk and item["status"] == "KILLED" for item in results),
            }
            for risk in required
        },
        "mutations": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--report")
    args = parser.parse_args()

    try:
        payload = run(Path(args.manifest))
    except (OSError, json.JSONDecodeError) as exc:
        payload = {
            "status": "FAIL",
            "manifest_errors": [f"MUTATION_SUITE_FAIL_CLOSED:{exc}"],
            "summary": {
                "risk_families": 0,
                "mutation_cases": 0,
                "killed_mutations": 0,
                "surviving_mutations": 0,
                "mutation_score": 0.0,
            },
            "mutations": [],
        }

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
