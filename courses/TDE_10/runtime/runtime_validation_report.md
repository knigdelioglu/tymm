# Runtime Course Package Validation Report

**Final:** PASS

| Check | Status | Detail |
|---|---|---|
| schema validation | PASS | runtime schema loaded |
| foreign key integrity | PASS | PRAGMA foreign_key_check |
| canonical ID uniqueness: themes | PASS |  |
| canonical ID uniqueness: blocks | PASS |  |
| canonical ID uniqueness: outcomes | PASS |  |
| canonical ID uniqueness: activities | PASS |  |
| canonical ID uniqueness: forms | PASS |  |
| canonical ID uniqueness: assessment_artifacts | PASS |  |
| orphan relations | PASS | 0 |
| source fingerprint status | PASS | RUNTIME_FRESH |
| timeline projection status | PASS | block hours remain ORDER_ONLY |
| assessment mapping status | PASS | runtime=0, canonical=0 |
| assessment artifact projection status | PASS | runtime=0, canonical=0 |
| resource decision projection status | PASS |  |
| application query A | PASS | rows=1 |
| application query B | PASS | rows=1 |
| application query C | PASS | rows=16 |
| application query D | PASS | rows=1 |
| application query E | PASS | rows=1 |
| copyright payload check | PASS |  |
| user state excluded | PASS |  |
| vector/model dependency excluded | PASS |  |

## Row counts

- `courses`: 1
- `themes`: 4
- `blocks`: 16
- `block_activities`: 75
- `outcomes`: 64
- `block_outcomes`: 64
- `textbook_sections`: 24
- `activities`: 75
- `activity_outcomes`: 300
- `forms`: 35
- `activity_forms`: 126
- `resource_decisions`: 64
- `assessment_artifacts`: 0
- `assessment_gap_mappings`: 0
- `assessment_task_bindings`: 0
- `timeline_themes`: 4
- `timeline_blocks`: 16
- `source_references`: 4
- `entity_source_references`: 0
