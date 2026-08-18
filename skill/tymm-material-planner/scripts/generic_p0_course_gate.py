#!/usr/bin/env python3
"""Generic P0 gate for TYMM course knowledge packages.

Unlike the TDE_9 historical regression gate, this gate derives expected artifact
and gap counts from the course production manifest. It therefore supports both:
- generated-artifact courses, and
- verified reuse-only courses with zero resource gaps / zero new artifacts.

The gate remains fail-closed for stale indexes, ambiguous outcome codes,
knowledge conflicts, and generation requests with no verified resource gap.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from build_runtime_course_package import build as build_runtime
from knowledge_index import KnowledgeIndexer
from knowledge_resolver import KnowledgeResolver
from production_schema import REUSE_ONLY_MODE, build_artifact_maps


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_gate(root: Path) -> dict:
    curriculum = read_json(root / "curriculum_map.json")
    textbook = read_json(root / "textbook_map.json")
    require(curriculum.get("verification_status") == "VERIFIED", "curriculum verification_status != VERIFIED")
    require(curriculum.get("canonical_freeze_status") == "FROZEN", "curriculum canonical_freeze_status != FROZEN")
    require(str(textbook.get("freeze_status", "")).startswith("FROZEN"), "textbook is not FROZEN")
    themes = curriculum.get("themes", [])
    require(len(themes) == 4, f"expected 4 themes, got {len(themes)}")
    outcome_count = sum(len(t.get("learning_outcomes", [])) for t in themes)
    require(outcome_count > 0, "no canonical learning outcomes")
    return {"themes": len(themes), "outcomes": outcome_count, "status": "PASS"}


def production_gate(root: Path) -> dict:
    manifest = read_json(root / "production" / "production_manifest.json")
    artifacts, artifact_by_id, alias_map, provenance = build_artifact_maps(manifest)
    expected_artifacts = manifest.get("expected_new_artifact_count", len(artifacts))
    expected_gaps = manifest.get("verified_resource_gap_count")
    require(expected_gaps is not None, "verified_resource_gap_count missing")
    require(len(artifacts) == expected_artifacts, f"artifact count mismatch: {len(artifacts)} != {expected_artifacts}")
    require(len(alias_map) == expected_gaps, f"gap alias count mismatch: {len(alias_map)} != {expected_gaps}")
    require(len(provenance) == expected_gaps, f"gap provenance count mismatch: {len(provenance)} != {expected_gaps}")
    require(not any(a.startswith("MAT_") for a in artifact_by_id), "legacy MAT_* used as canonical artifact identity")
    reuse_only = manifest.get("production_mode") == REUSE_ONLY_MODE
    if reuse_only:
        require(expected_gaps == 0 and expected_artifacts == 0, "reuse-only mode requires zero gaps and zero new artifacts")
        require(manifest.get("generation_authorization", {}).get("allowed") is False, "reuse-only manifest opened generation")
    return {
        "schema_version": manifest.get("schema_version"),
        "production_mode": manifest.get("production_mode"),
        "verified_resource_gap_count": expected_gaps,
        "expected_new_artifact_count": expected_artifacts,
        "artifact_ids": sorted(artifact_by_id),
        "gap_aliases": sorted(alias_map),
        "status": "PASS",
    }


def rebuild_index_gate(root: Path, production: dict) -> dict:
    indexer = KnowledgeIndexer(str(root))
    Path(indexer.db_path).unlink(missing_ok=True)
    manifest = indexer.build_index(force=True)
    status = indexer.check_status()
    require(status.get("status") == "INDEX_FRESH", f"index not fresh after rebuild: {status}")
    require(manifest.get("production_schema_version") == "1.1", "index production schema != 1.1")
    require(manifest.get("artifact_identity_field") == "artifact_id", "index artifact identity is not artifact_id")
    require(manifest.get("production_artifact_count") == production["expected_new_artifact_count"], "index artifact count mismatch")
    require(manifest.get("production_gap_alias_count") == production["verified_resource_gap_count"], "index gap alias count mismatch")

    db = sqlite3.connect(indexer.db_path)
    artifact_rows = db.execute("SELECT entity_id,entity_key FROM metadata WHERE entity_type='assessment_artifact' ORDER BY entity_id").fetchall()
    duplicate_count = db.execute("SELECT COUNT(*) FROM (SELECT entity_key FROM metadata GROUP BY entity_key HAVING COUNT(*)>1)").fetchone()[0]
    db.close()
    require(len(artifact_rows) == production["expected_new_artifact_count"], "assessment_artifact row count mismatch")
    require(duplicate_count == 0, "duplicate entity_key in rebuilt index")
    return {
        "freshness": status.get("status"),
        "indexed_record_count": manifest.get("indexed_record_count"),
        "artifact_rows": [{"entity_id": r[0], "entity_key": r[1]} for r in artifact_rows],
        "duplicate_entity_keys": duplicate_count,
        "status": "PASS",
    }


def resolver_gate(root: Path, production: dict) -> dict:
    resolver = KnowledgeResolver(str(root))
    curriculum = read_json(root / "curriculum_map.json")
    probes = []
    for theme in curriculum.get("themes", []):
        theme_no = theme.get("theme_no")
        outcomes = theme.get("learning_outcomes", [])
        require(outcomes, f"theme {theme_no} has no outcomes")
        code = outcomes[-1].get("outcome_code")
        query = f"Tema {theme_no} {code} için kitapta ne eksik?"
        pack = resolver.resolve(query)
        require(pack.get("resolution_status") == "RESOLVED", f"resolver probe not RESOLVED: {query}: {pack.get('resolution_status')}")
        require(pack.get("index_freshness") == "INDEX_FRESH", f"resolver probe index not fresh: {query}")
        require(not pack.get("conflicts"), f"resolver probe conflict: {query}")
        matching = [a for a in pack.get("alignment_context", []) if a.get("outcome_code") == code]
        require(matching, f"resolver probe returned no alignment for {query}")
        probes.append({"query": query, "coverage": matching[0].get("primary_coverage")})

    # Repeated outcome codes across themes must be ambiguous without a theme scope.
    ambiguous_code = curriculum["themes"][0]["learning_outcomes"][-1]["outcome_code"]
    ambiguous = resolver.resolve(ambiguous_code)
    require(ambiguous.get("ambiguity_status") == "AMBIGUOUS_ENTITY", "theme-less repeated outcome did not become ambiguous")
    require(not ambiguous.get("material_generation_allowed"), "ambiguous outcome opened generation")

    generation_probe = None
    if production.get("production_mode") == REUSE_ONLY_MODE:
        query = f"Tema 1 {ambiguous_code} için rubrik hazırla"
        generation_probe = resolver.resolve(query)
        require(generation_probe.get("resolution_status") == "RESOLVED", "reuse-only generation probe should resolve canonically")
        require(not generation_probe.get("material_generation_allowed"), "reuse-only/no-gap course opened material generation")
        require(generation_probe.get("material_generation_block_reason") == "NO_VERIFIED_RESOURCE_GAP", f"wrong reuse-only block reason: {generation_probe.get('material_generation_block_reason')}")
        require(not generation_probe.get("production_context"), "reuse-only generation probe unexpectedly resolved a production artifact")

    return {
        "structured_probes": probes,
        "ambiguity_probe": {
            "query": ambiguous_code,
            "status": ambiguous.get("resolution_status"),
            "ambiguity_status": ambiguous.get("ambiguity_status"),
            "block_reason": ambiguous.get("material_generation_block_reason"),
        },
        "generation_probe": None if generation_probe is None else {
            "allowed": generation_probe.get("material_generation_allowed"),
            "block_reason": generation_probe.get("material_generation_block_reason"),
        },
        "status": "PASS",
    }


def stale_gate(root: Path) -> dict:
    with tempfile.TemporaryDirectory() as td:
        temp_root = Path(td) / root.name
        shutil.copytree(root, temp_root)
        path = sorted(temp_root.glob("themes/tema_*/alignment.json"))[0]
        data = read_json(path)
        data["p0_stale_probe"] = True
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        pack = KnowledgeResolver(str(temp_root)).resolve("Tema 1 TDE4.4 için kitapta ne eksik?")
        require(pack.get("index_freshness") == "INDEX_STALE", f"stale index not detected: {pack.get('index_freshness')}")
        require(pack.get("resolution_status") == "REVIEW_REQUIRED", "stale index must require review")
        require(not pack.get("material_generation_allowed"), "stale index opened generation")
        require(pack.get("material_generation_block_reason") == "INDEX_STALE", f"wrong stale block reason: {pack.get('material_generation_block_reason')}")
        return {"status": "PASS", "block_reason": pack.get("material_generation_block_reason")}


def conflict_gate(root: Path) -> dict:
    with tempfile.TemporaryDirectory() as td:
        temp_root = Path(td) / root.name
        shutil.copytree(root, temp_root)
        path = sorted(temp_root.glob("themes/tema_*/gap_analysis.json"))[0]
        data = read_json(path)
        rows = data.get("gap_records", []) or data.get("gaps", [])
        require(rows, "conflict fixture has no gap-analysis rows")
        rows[0]["primary_coverage"] = "NOT_COVERED"
        rows[0]["remaining_gap"] = "P0 synthetic conflict fixture"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        code = rows[0].get("outcome_code")
        pack = KnowledgeResolver(str(temp_root)).resolve(f"Tema 1 {code} için kitapta ne eksik?")
        require(pack.get("resolution_status") == "REVIEW_REQUIRED", "knowledge conflict must require review")
        require(pack.get("conflicts"), "conflict fixture produced no conflict")
        require(not pack.get("material_generation_allowed"), "knowledge conflict opened generation")
        require(pack.get("material_generation_block_reason") == "KNOWLEDGE_CONFLICT", f"wrong conflict block reason: {pack.get('material_generation_block_reason')}")
        return {"status": "PASS", "conflicts": len(pack.get("conflicts", []))}


def runtime_gate(root: Path, canonical: dict, production: dict) -> dict:
    result = build_runtime(root)
    require(result.get("status") == "PASS", f"runtime build/validation failed: {result.get('status')}")
    counts = result.get("row_counts", {})
    require(counts.get("themes") == canonical["themes"], f"runtime theme count mismatch: {counts.get('themes')}")
    require(counts.get("outcomes") == canonical["outcomes"], f"runtime outcome count mismatch: {counts.get('outcomes')}")
    teaching = read_json(root / "production" / "teaching_blocks.json")
    expected_blocks = teaching.get("summary", {}).get("total_teaching_blocks", len(teaching.get("blocks", [])))
    require(counts.get("blocks") == expected_blocks, f"runtime block count mismatch: {counts.get('blocks')} != {expected_blocks}")
    require(counts.get("assessment_artifacts") == production["expected_new_artifact_count"], "runtime artifact count mismatch")
    require(counts.get("assessment_gap_mappings") == production["verified_resource_gap_count"], "runtime gap mapping count mismatch")
    return {"status": "PASS", "row_counts": counts}


def main() -> int:
    root = Path(os.environ.get("TYMM_KNOWLEDGE_ROOT", str(REPO_ROOT / "courses" / "TDE_10"))).resolve()
    require(root.exists(), f"knowledge root does not exist: {root}")
    canonical = canonical_gate(root)
    production = production_gate(root)
    report = {
        "course_id": root.name,
        "canonical": canonical,
        "production_schema": production,
        "index_rebuild": rebuild_index_gate(root, production),
        "resolver": resolver_gate(root, production),
        "stale_gate": stale_gate(root),
        "conflict_gate": conflict_gate(root),
        "runtime": runtime_gate(root, canonical, production),
        "final": "PASS",
    }
    report_path = root / "index" / "p0_gate_report.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"GENERIC P0 COURSE GATE: PASS ({root.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
