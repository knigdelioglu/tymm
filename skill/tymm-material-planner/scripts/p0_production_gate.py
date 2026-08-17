#!/usr/bin/env python3
"""P0 production gate for TYMM production schema 1.1.

This gate deliberately rebuilds knowledge.sqlite from scratch and fails closed unless:
- production manifest is schema 1.1
- exactly 3 canonical assessment artifacts cover exactly 7 historical gap aliases
- artifact identity is artifact_id (never MAT_*)
- the rebuilt index is fresh and collision-free
- canonical + alias retrieval works
- stale and conflict scenarios block generation
"""

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
DEFAULT_ROOT = REPO_ROOT / "courses" / "TDE_9"

sys.path.insert(0, str(SCRIPT_DIR))

from knowledge_index import KnowledgeIndexer
from knowledge_resolver import KnowledgeResolver
from production_schema import build_artifact_maps

EXPECTED_ALIAS_MAP = {
    "MAT_T2_KONUSMA_RUBRIC": "TDE9_KONUSMA_RUBRIC",
    "MAT_T2_YAZMA_RUBRIC": "TDE9_YAZMA_RUBRIC",
    "MAT_T3_KONUSMA_RUBRIC": "TDE9_KONUSMA_RUBRIC",
    "MAT_T3_YAZMA_RUBRIC": "TDE9_YAZMA_RUBRIC",
    "MAT_T4_KONUSMA_RUBRIC": "TDE9_KONUSMA_RUBRIC",
    "MAT_T4_YAZMA_KONTROL_LISTESI": "TDE9_YAZMA_SUREC_KONTROL_LISTESI",
    "MAT_T4_YAZMA_RUBRIC": "TDE9_YAZMA_RUBRIC",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def production_schema_gate(root: Path) -> dict:
    manifest_path = root / "production" / "production_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts, artifact_by_id, alias_map, provenance = build_artifact_maps(manifest)
    require(len(artifacts) == 3, f"expected 3 artifacts, got {len(artifacts)}")
    require(len(alias_map) == 7, f"expected 7 gap aliases, got {len(alias_map)}")
    require(alias_map == EXPECTED_ALIAS_MAP, f"7→3 mapping mismatch: {alias_map}")
    require(set(provenance) == set(EXPECTED_ALIAS_MAP), "gap provenance registry mismatch")
    require(not any(a.startswith("MAT_") for a in artifact_by_id), "MAT_* used as artifact identity")
    return {
        "schema_version": manifest["schema_version"],
        "artifact_ids": sorted(artifact_by_id),
        "gap_aliases": sorted(alias_map),
        "gap_alias_to_artifact": alias_map,
    }


def rebuild_gate(root: Path) -> dict:
    indexer = KnowledgeIndexer(str(root))
    if os.path.exists(indexer.db_path):
        os.remove(indexer.db_path)
    manifest = indexer.build_index(force=True)
    status = indexer.check_status()
    require(status.get("status") == "INDEX_FRESH", f"index not fresh after rebuild: {status}")
    require(manifest.get("production_schema_version") == "1.1", "manifest production schema is not 1.1")
    require(manifest.get("artifact_identity_field") == "artifact_id", "legacy artifact identity remained")
    require(manifest.get("production_artifact_count") == 3, "manifest artifact count != 3")
    require(manifest.get("production_gap_alias_count") == 7, "manifest gap alias count != 7")

    db = sqlite3.connect(indexer.db_path)
    rows = db.execute(
        "SELECT entity_id, entity_key FROM metadata WHERE entity_type='assessment_artifact' ORDER BY entity_id"
    ).fetchall()
    duplicate_count = db.execute(
        "SELECT COUNT(*) FROM (SELECT entity_key FROM metadata GROUP BY entity_key HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    db.close()
    require(len(rows) == 3, f"expected 3 assessment_artifact rows, got {len(rows)}")
    require(duplicate_count == 0, "duplicate entity_key found")
    require(not any(row[0].startswith("MAT_") for row in rows), "MAT_* persisted as artifact identity")
    return {
        "status": status,
        "artifact_rows": [{"entity_id": r[0], "entity_key": r[1]} for r in rows],
    }


def retrieval_gate(root: Path) -> dict:
    resolver = KnowledgeResolver(str(root))
    alias_results = {}
    for alias, expected in EXPECTED_ALIAS_MAP.items():
        pack = resolver.resolve(alias)
        require(pack["resolution_status"] == "RESOLVED", f"alias {alias} not resolved: {pack['resolution_status']}")
        require(pack["material_generation_allowed"], f"alias {alias} blocked after fresh rebuild")
        ids = {a["artifact_id"] for a in pack["production_context"]}
        require(ids == {expected}, f"alias {alias} resolved to {ids}, expected {expected}")
        require(
            any(e.get("entity_id") == expected and e.get("matched_gap_alias") == alias for e in pack["resolved_entities"]),
            f"alias provenance not preserved for {alias}",
        )
        alias_results[alias] = expected

    probes = {
        "Tema 2 TDE4.4 için kitapta ne eksik?": "TDE9_YAZMA_RUBRIC",
        "Tema 3 konuşmayı nasıl değerlendireceğim?": "TDE9_KONUSMA_RUBRIC",
        "şiir yazarken öğrenciyi nasıl değerlendireceğim?": "TDE9_YAZMA_RUBRIC",
    }
    semantic_results = {}
    for query, expected in probes.items():
        pack = resolver.resolve(query)
        artifact_ids = {a["artifact_id"] for a in pack["production_context"]}
        form_ids = {f.get("form_id") for f in pack["assessment_context"] if f.get("form_id")}
        require(
            expected in artifact_ids or bool(form_ids),
            f"retrieval probe failed: {query}; artifacts={artifact_ids}, forms={form_ids}",
        )
        semantic_results[query] = {"artifacts": sorted(artifact_ids), "forms": sorted(form_ids)}
    return {"aliases": alias_results, "semantic_probes": semantic_results}


def stale_gate(root: Path) -> dict:
    with tempfile.TemporaryDirectory() as td:
        temp_root = Path(td) / "TDE_9"
        shutil.copytree(root, temp_root)
        path = temp_root / "themes" / "tema_01" / "alignment.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["p0_gate_stale_probe"] = True
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        pack = KnowledgeResolver(str(temp_root)).resolve("Tema 2 TDE4.4")
        require(pack["index_freshness"] == "INDEX_STALE", f"stale status not detected: {pack['index_freshness']}")
        require(pack["resolution_status"] == "REVIEW_REQUIRED", "stale index must require review")
        require(not pack["material_generation_allowed"], "stale index opened generation gate")
        require(pack["material_generation_block_reason"] == "INDEX_STALE", "wrong stale block reason")
        return {"status": "PASS", "block_reason": pack["material_generation_block_reason"]}


def conflict_gate(root: Path) -> dict:
    with tempfile.TemporaryDirectory() as td:
        temp_root = Path(td) / "TDE_9"
        shutil.copytree(root, temp_root)
        path = temp_root / "themes" / "tema_02" / "alignment.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for al in data.get("alignments", []):
            if al.get("outcome_code") == "TDE4.4":
                al["primary_coverage"] = "COVERED"
                al["remaining_gap"] = "Yok (Tamamen karşılandı)"
                al["production_decision"] = "REUSE_TEXTBOOK"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        pack = KnowledgeResolver(str(temp_root)).resolve("Tema 2 TDE4.4 için kitapta ne eksik?")
        require(pack["resolution_status"] == "REVIEW_REQUIRED", "conflict must require review")
        require(pack["conflicts"], "conflict fixture produced no conflict")
        require(not pack["material_generation_allowed"], "conflict opened generation gate")
        require(pack["material_generation_block_reason"] == "KNOWLEDGE_CONFLICT", "wrong conflict block reason")
        return {"status": "PASS", "conflicts": len(pack["conflicts"])}


def main() -> int:
    root = Path(os.environ.get("TYMM_KNOWLEDGE_ROOT", str(DEFAULT_ROOT))).resolve()
    require(root.exists(), f"knowledge root does not exist: {root}")
    report = {
        "course_id": root.name,
        "production_schema": production_schema_gate(root),
        "index_rebuild": rebuild_gate(root),
        "retrieval": retrieval_gate(root),
        "stale_gate": stale_gate(root),
        "conflict_gate": conflict_gate(root),
        "final": "PASS",
    }
    report_path = root / "index" / "p0_gate_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("P0 PRODUCTION GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
