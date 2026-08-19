#!/usr/bin/env python3
"""TDE_10 Phase 15 technical P0 + TDE_9 regression gate.

This gate preserves the TDE_10 fail-closed parity state while verifying that shared
schema/resolver/runtime changes do not regress the TDE_9 7-gap -> 3-artifact profile.
It never grants TDE_10 parity certification while authenticated EBA assessment
target structures remain unresolved.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
TDE10 = REPO_ROOT / "courses" / "TDE_10"
TDE9 = REPO_ROOT / "courses" / "TDE_9"
REPORT = TDE10 / "source_docs" / "phase15_execution_report.json"
PYTHON = sys.executable


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run(results: List[dict], name: str, args: List[str], env: Dict[str, str] | None = None) -> bool:
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    proc = subprocess.run(
        args,
        cwd=REPO_ROOT,
        env=process_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    results.append(
        {
            "name": name,
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "returncode": proc.returncode,
            "output_tail": proc.stdout[-6000:],
        }
    )
    return proc.returncode == 0


def check_preconditions(results: List[dict]) -> bool:
    validation = read_json(TDE10 / "parity_validation_report.json")
    production = read_json(TDE10 / "production" / "production_manifest.json")
    conditions = {
        "validation_status": validation.get("status") == "VALIDATED_WITH_EXTERNAL_AUTH_BLOCKER",
        "parity_not_certified": validation.get("parity_certified") is False,
        "no_internal_hard_failures": validation.get("hard_failures") == [],
        "coverage_56_8_0": (
            validation.get("counts", {}).get("covered") == 56
            and validation.get("counts", {}).get("partially_covered") == 8
            and validation.get("counts", {}).get("not_covered") == 0
        ),
        "production_schema_1_1": production.get("schema_version") == "1.1",
        "parity_review_blocked": production.get("production_mode") == "PARITY_REVIEW_BLOCKED",
        "zero_confirmed_gaps": production.get("verified_resource_gap_count") == 0,
        "eight_unresolved_targets": production.get("unresolved_assessment_target_count") == 8,
        "empty_production_queue": production.get("production_queue") == [],
        "generation_closed": production.get("generation_authorization", {}).get("allowed") is False,
        "generation_block_reason": (
            production.get("generation_authorization", {}).get("reason")
            == "UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS"
        ),
    }
    ok = all(conditions.values())
    results.append({"name": "tde10_parity_preconditions", "status": "PASS" if ok else "FAIL", "checks": conditions})
    return ok


def check_tde9_contract(results: List[dict]) -> bool:
    sys.path.insert(0, str(SCRIPT_DIR))
    from production_schema import build_artifact_maps

    manifest = read_json(TDE9 / "production" / "production_manifest.json")
    artifacts, _, aliases, provenance = build_artifact_maps(manifest)
    counts = {"artifacts": len(artifacts), "gap_aliases": len(aliases), "provenance_rows": len(provenance)}
    ok = counts == {"artifacts": 3, "gap_aliases": 7, "provenance_rows": 7}
    results.append({"name": "tde9_legacy_7_to_3", "status": "PASS" if ok else "FAIL", "counts": counts})
    return ok


def update_phase15_metadata() -> Dict[Path, str]:
    paths = [TDE10 / "parity_contract.json", TDE10 / "source_manifest.json", TDE10 / "parity_report.md"]
    backups = {path: path.read_text(encoding="utf-8") for path in paths}

    contract_path = TDE10 / "parity_contract.json"
    contract = read_json(contract_path)
    contract["phase_gates"]["PHASE_15_P0_AND_TDE9_REGRESSION"] = "PASS_TECHNICAL_WITH_8_EXTERNAL_AUTH_BLOCKERS"
    contract["technical_p0_status"] = "PASS"
    contract["parity_certification"] = "WITHHELD_PENDING_8_AUTH_GATED_EBA_DPA_TARGETS"
    contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest_path = TDE10 / "source_manifest.json"
    manifest = read_json(manifest_path)
    manifest["overall_status"] = "TECHNICAL_P0_PASS_PARITY_REVIEW_BLOCKED"
    manifest["parity_remediation_status"] = "BLOCKED_PENDING_8_AUTH_GATED_EBA_DPA_TARGETS"
    manifest["parity_certification"] = "WITHHELD"
    manifest.setdefault("scope", {}).update(
        {
            "knowledge_index_built": True,
            "runtime_projection_built": True,
            "p0_gate_passed": True,
            "materials_generated": False,
        }
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    parity_report_path = TDE10 / "parity_report.md"
    text = parity_report_path.read_text(encoding="utf-8")
    marker = "## 11. Faz 15 teknik P0 ve TDE_9 regresyon sonucu"
    if marker not in text:
        text += (
            "\n\n" + marker + "\n\n"
            "TDE_10 teknik P0 kapıları ve TDE_9 regresyonları geçmiştir. TDE_10 materyal üretimi, "
            "sekiz authenticated EBA DPA hedefi çözülmediği için `UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS` "
            "ile fail-closed kalır. TDE_9 tarihsel **7 gap instance → 3 canonical artifact** sözleşmesi, "
            "resolver ve runtime regresyonları korunmuştur.\n\n"
            "**Faz 15:** `PASS_TECHNICAL_WITH_8_EXTERNAL_AUTH_BLOCKERS`. Bu sonuç parity sertifikası değildir.\n"
        )
        parity_report_path.write_text(text, encoding="utf-8")
    return backups


def restore(backups: Dict[Path, str]) -> None:
    for path, content in backups.items():
        path.write_text(content, encoding="utf-8")


def main() -> int:
    results: List[dict] = []
    initial_ok = check_preconditions(results)

    initial_ok &= run(results, "reuse_only_contract", [PYTHON, "skill/tymm-material-planner/tests/test_reuse_only_contract.py"])
    initial_ok &= run(results, "parity_blocked_contract", [PYTHON, "skill/tymm-material-planner/tests/test_parity_blocked_contract.py"])
    initial_ok &= check_tde9_contract(results)

    initial_ok &= run(
        results,
        "tde9_strict_p0",
        [PYTHON, "skill/tymm-material-planner/scripts/p0_production_gate.py"],
        {"TYMM_KNOWLEDGE_ROOT": str(TDE9)},
    )
    initial_ok &= run(results, "tde9_resolver_regression", [PYTHON, "skill/tymm-material-planner/tests/test_resolver_runner.py"])
    initial_ok &= run(results, "tde9_runtime_regression", [PYTHON, "skill/tymm-material-planner/tests/test_runtime_course_package.py"])

    initial_ok &= run(
        results,
        "tde10_generic_p0_initial",
        [PYTHON, "skill/tymm-material-planner/scripts/generic_p0_course_gate.py"],
        {"TYMM_KNOWLEDGE_ROOT": str(TDE10)},
    )
    initial_ok &= run(
        results,
        "tde10_index_status_initial",
        [PYTHON, "skill/tymm-material-planner/scripts/knowledge_index.py", "status", "--knowledge-root", str(TDE10)],
    )
    initial_ok &= run(
        results,
        "tde10_runtime_status_initial",
        [PYTHON, "skill/tymm-material-planner/scripts/build_runtime_course_package.py", "status", "--knowledge-root", str(TDE10)],
    )

    backups: Dict[Path, str] = {}
    if initial_ok:
        backups = update_phase15_metadata()
        final_ok = run(
            results,
            "tde10_generic_p0_final",
            [PYTHON, "skill/tymm-material-planner/scripts/generic_p0_course_gate.py"],
            {"TYMM_KNOWLEDGE_ROOT": str(TDE10)},
        )
        final_ok &= run(
            results,
            "tde10_index_status_final",
            [PYTHON, "skill/tymm-material-planner/scripts/knowledge_index.py", "status", "--knowledge-root", str(TDE10)],
        )
        final_ok &= run(
            results,
            "tde10_runtime_status_final",
            [PYTHON, "skill/tymm-material-planner/scripts/build_runtime_course_package.py", "status", "--knowledge-root", str(TDE10)],
        )
    else:
        final_ok = False

    if not final_ok and backups:
        restore(backups)

    final = "PASS_TECHNICAL_WITH_8_EXTERNAL_AUTH_BLOCKERS" if initial_ok and final_ok else "FAIL"
    report = {
        "schema_version": "1.0",
        "course_id": "TDE_10",
        "phase": 15,
        "final": final,
        "parity_certified": False,
        "external_blockers": ["8 authenticated EBA DPA target structures unresolved"],
        "tests": results,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if final.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
