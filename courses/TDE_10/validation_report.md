# TDE_10 Canonical Knowledge Validation Report

**Status:** `P0 PASS / CANONICAL FROZEN / REUSE ONLY`

```text
Official curriculum snapshots        PASS (4/4)
Canonical learning outcomes          PASS (64/64)
Curriculum canonical map             VERIFIED / FROZEN
Official local textbook PDF          VERIFIED / FROZEN
Program-textbook alignment           PASS (64/64 COVERED)
Verified remaining resource gaps     0
New assessment artifacts             0
Production mode                      REUSE_ONLY_NO_NEW_ARTIFACTS
Teaching blocks                      16
Knowledge index                      INDEX_FRESH
Resolver stale/conflict gates        PASS
No-gap generation gate               PASS
Runtime projection                   PASS
P0                                    PASS
```

The 10th-grade course uses the local official MEB textbook snapshot `source_docs/turk-dili-ve-edebiyati-10.pdf`. All 64 scoped outcomes have verified textbook action/evidence paths. Cross-theme consolidation found no verified resource gap, so the production contract deliberately contains no new physical artifact.

The derived `knowledge.sqlite` and runtime SQLite are rebuildable projections only; canonical JSON/MD remains source of truth. A direct material-generation request is blocked with `NO_VERIFIED_RESOURCE_GAP` unless canonical evidence later establishes a real gap.

Runtime row counts: `{"courses": 1, "themes": 4, "blocks": 16, "block_activities": 75, "outcomes": 64, "block_outcomes": 64, "textbook_sections": 24, "activities": 75, "activity_outcomes": 300, "forms": 35, "activity_forms": 119, "resource_decisions": 16, "assessment_artifacts": 0, "assessment_gap_mappings": 0, "assessment_task_bindings": 0, "timeline_themes": 4, "timeline_blocks": 16, "source_references": 4, "entity_source_references": 0}`.
