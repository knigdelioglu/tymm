# TYMM Local Hybrid RAG Architecture Reference

## 1. Local Isolated Architecture Overview

The **TYMM Local Hybrid RAG Index** provides deterministic, high-speed, 100% offline semantic candidate discovery over frozen structured curriculum knowledge bases.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          LOCAL HYBRID RAG INDEX                        │
│                                                                        │
│   knowledge/<course_id>/index/                                         │
│   ├── knowledge.sqlite                                                 │
│   │   ├── metadata            (Canonical schema, locators, hashes)     │
│   │   ├── fts_entities        (FTS5 unicode61 full-text search)        │
│   │   └── vec_entities        (sqlite-vec 384-dim vector table)        │
│   ├── index_manifest.json     (Fingerprints, source SHA256, model ver) │
│   └── index_validation_report.md (Build validation metrics)           │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **CRITICAL INVARIANT:**
> The Vector Database is **NOT** the source of truth. Authoritative source of truth consists strictly of persistent, verified, frozen canonical JSON files in `knowledge/<course_id>/`. The Vector DB is solely a candidate retrieval accelerator.

---

## 2. Vector Backend Architecture & Explicit Accepted Deviation

- **Requested Backend**: `sqlite-vector/sqliteai-vector`
- **Selected Backend**: `sqlite-vec` (v0.1.9)
- **Selection Status**: `EXPLICIT_ACCEPTED_DEVIATION`
- **Selection Reason**: `sqlite-vec` is the modern official lightweight native C SQLite extension by Alex Garcia supporting fast vector search without heavy external AI dependencies. It compiles and runs reliably on macOS ARM64 / x86_64, whereas legacy `sqlite-vector`/`sqliteai-vector` has packaging/build complexities and deprecations.
- **SQLite Version**: `3.53.1`
- **sqlite-vec Version**: `v0.1.9`
- **Platform / Arch**: `macOS-27.0-arm64-arm-64bit-Mach-O` / `arm64`

> [!CAUTION]
> Silent fallback to any other backend is forbidden. If the vector extension changes, `KnowledgeIndexer.check_status()` returns `VECTOR_BACKEND_MISMATCH` and requires an explicit rebuild.

---

## 3. Embedding Model Runtime Provenance

- **Base Embedding Model**: `intfloat/multilingual-e5-small`
- **Runtime Model Repository**: `Xenova/multilingual-e5-small`
- **Runtime Model File**: `model_quantized.onnx`
- **Runtime Format**: `ONNX`
- **Quantization**: `quantized`
- **Embedding Dimension**: `384`
- **Pooling Strategy**: `attention_masked_mean_pooling` (attention-mask weighted mean pooling over token embeddings)
- **Normalization**: `L2` (exact Euclidean norm normalization)
- **Query Prefix**: `"query: "`
- **Passage Prefix**: `"passage: "`
- **Model File SHA256**: `f80102d3f2a1229f387d3c81909990d8945513e347b0eab049f7de3c6f98c193`

If the runtime ONNX artifact hash changes, `KnowledgeIndexer.check_status()` returns `EMBEDDING_ARTIFACT_MISMATCH` requiring a full vector rebuild.

---

## 4. Reciprocal Rank Fusion (RRF) Algorithm

Hybrid search combines lexical candidate ranks (FTS5 unicode61) and vector candidate ranks (`sqlite-vec`) into a unified reciprocal rank score:

$$RRF(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where:
- $M = \{\text{Vector Search}, \text{FTS5 Search}\}$
- $k = 60$ (standard rank constant)
- $r_m(d)$ is the 1-based rank of document $d$ in retrieval modality $m$.

### Filtration Pipeline
Candidates passing through RRF are filtered deterministically against:
1. `theme_id` (if specified or inferred from query context).
2. `entity_type` (e.g. restricting to `textbook_form` and `production_material` for assessment queries).
3. `authority_level` (ensuring lower authority recommendations cannot shadow official records).

---

## 5. Stable Entity Key Schema & Duplicate Protection

Every indexed entity receives a collision-free, deterministic stable key:

| Entity Type | Canonical Source File | Authority | Stable Key Format |
|:---|:---|:---:|:---|
| `curriculum_theme` | `curriculum_map.json` | 1 | `{course_id}::curriculum_theme::{theme_id}` |
| `curriculum_outcome` | `curriculum_map.json` | 1 | `{course_id}::curriculum_outcome::{theme_id}::{outcome_code}` |
| `process_component` | `curriculum_map.json` | 1 | `{course_id}::process_component::{theme_id}::{outcome_code}::{component_code}` |
| `textbook_section` | `textbook_map.json` | 2 | `{course_id}::textbook_section::{theme_id}::{section_id}` |
| `textbook_activity` | `textbook_map.json` | 2 | `{course_id}::textbook_activity::{theme_id}::{activity_id}` |
| `textbook_form` | `textbook_forms_index.json` | 3 | `{course_id}::textbook_form::{form_id}` |
| `alignment_record` | `themes/tema_XX/alignment.json` | 4 | `{course_id}::alignment_record::{theme_id}::{outcome_code}` |
| `remaining_gap` | `themes/tema_XX/gap_analysis.json` | 5 | `{course_id}::remaining_gap::{theme_id}::{gap_id}` |
| `instructional_need` | `themes/tema_XX/needs.json` | 6 | `{course_id}::instructional_need::{theme_id}::{need_id}` |
| `resource_plan` | `themes/tema_XX/resource_plan.json` | 6 | `{course_id}::resource_plan::{theme_id}::{resource_id}` |
| `production_material` | `production/production_manifest.json` | 7 | `{course_id}::production_material::{material_id}` |
| `teaching_block` | `production/teaching_blocks.json` | 7 | `{course_id}::teaching_block::{theme_id}::{block_id}` |
| `school_based_option` | `production/school_based_planning_options.json` | 8 | `{course_id}::school_based_option::{theme_id}::{option_id}` |

> [!CAUTION]
> If any duplicate stable key is detected during extraction, the indexer raises `DuplicateCanonicalKeyError("DUPLICATE_CANONICAL_KEY")` and aborts immediately. Suffix fallback or silent overwrite is forbidden.

---

## 6. Maintenance & CLI Operations

```bash
# Check index freshness and provenance
~/.gemini/config/skills/tymm-material-planner/.venv/bin/python3 \
  ~/.gemini/config/skills/tymm-material-planner/scripts/knowledge_index.py status \
  --knowledge-root knowledge/TDE_9

# Force rebuild index
~/.gemini/config/skills/tymm-material-planner/.venv/bin/python3 \
  ~/.gemini/config/skills/tymm-material-planner/scripts/knowledge_index.py rebuild \
  --knowledge-root knowledge/TDE_9

# Hybrid query CLI
~/.gemini/config/skills/tymm-material-planner/.venv/bin/python3 \
  ~/.gemini/config/skills/tymm-material-planner/scripts/knowledge_index.py query \
  --knowledge-root knowledge/TDE_9 \
  --query "şiir yazma değerlendirme" \
  --top-k 5
```
