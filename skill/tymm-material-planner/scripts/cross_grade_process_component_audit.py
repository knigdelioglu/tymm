#!/usr/bin/env python3
"""Run the canonical process-component gate across all TYMM TDE grades.

This audit is intentionally dependency-free. It persists a small machine-readable
summary so the repository has durable evidence of the latest 9-12 inheritance
validation instead of relying only on ephemeral GitHub Actions state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
sys.path.insert(0, str(SCRIPT_DIR))

from p0_process_component_gate import gate

COURSES = ("TDE_9", "TDE_10", "TDE_11", "TDE_12")
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "process-component-inheritance-audit.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    catalog = repo_root / "courses" / "TDE_SHARED" / "curriculum_process_component_catalog.json"
    if not catalog.exists():
        raise FileNotFoundError(f"shared process-component catalog missing: {catalog}")

    results: list[dict[str, Any]] = []
    final = "PASS"
    for course_id in COURSES:
        root = repo_root / "courses" / course_id
        try:
            result = gate(root, catalog)
            results.append(
                {
                    "course_id": course_id,
                    "status": "PASS",
                    "contract_mode": result.get("contract_mode"),
                    "counts": result.get("counts", {}),
                    "curriculum_sha256": sha256(root / "curriculum_map.json"),
                    "resolution_contract_sha256": sha256(root / "curriculum_process_component_resolution.json"),
                }
            )
        except Exception as exc:  # fail-closed audit boundary
            final = "FAIL"
            results.append(
                {
                    "course_id": course_id,
                    "status": "FAIL",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    return {
        "schema_version": "1.0",
        "audit_type": "TYMM_TDE_PROCESS_COMPONENT_INHERITANCE",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "catalog_id": "TDE_2024_ROOF_PROCESS_COMPONENTS",
        "catalog_sha256": sha256(catalog),
        "courses": results,
        "summary": {
            "course_count": len(COURSES),
            "passed": sum(1 for item in results if item.get("status") == "PASS"),
            "failed": sum(1 for item in results if item.get("status") == "FAIL"),
        },
        "final": final,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TYMM TDE 9-12 process-component inheritance audit.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report = run(args.repo_root)
    output = args.output
    if not output.is_absolute():
        output = args.repo_root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["final"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
