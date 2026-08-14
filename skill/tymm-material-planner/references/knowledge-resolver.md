# TYMM Knowledge Resolver Reference

## 1. Overview and Core Invariant

The **Knowledge Resolver** is the deterministic retrieval, disambiguation, and orchestration layer for the Türkiye Yüzyılı Maarif Modeli (TYMM) knowledge bases.

> [!IMPORTANT]
> **CRITICAL ARCHITECTURAL RULE: SINGLE SOURCE OF TRUTH INVARIANT**
> - The Vector Database (`knowledge.sqlite` / `sqlite-vec`) is **NOT** the source of truth.
> - The authoritative source of truth consists strictly of persistent, verified, frozen canonical JSON files in `knowledge/<course_id>/`.
> - Vector retrieval is purely a candidate accelerator (`RETRIEVAL ACCELERATOR / SEMANTIC CANDIDATE FINDER`).
> - Vector similarity must **NEVER** be used to guess or resolve entity ambiguity.

---

## 2. Mandatory Deterministic Retrieval Pipeline

When a user request arrives, the Knowledge Resolver executes the following mandatory pipeline:

```
USER REQUEST
   │
   ▼
[Stage 1: Course Resolution]
   │ Determine course_id (e.g. TDE_9)
   ▼
[Stage 2: Cache & Freshness Check]
   │ Validate index_manifest.json against source JSON SHA-256 hashes & model artifact hash
   │ (If hash mismatch -> INDEX_STALE / EMBEDDING_ARTIFACT_MISMATCH -> Generation Blocked)
   ▼
[Stage 3: Exact Structured Lookup & Disambiguation]
   │ Extract outcome codes, form IDs, material IDs, theme locators
   │ If outcome exists across multiple themes and no theme context is provided:
   │    └── Set AMBIGUOUS_ENTITY, list candidates, set PARTIALLY_RESOLVED, block generation.
   │ If exact theme context exists:
   │    └── Resolve exact theme-scoped canonical entity (e.g. TEMA_02::TDE4.4). Skip vector DB.
   ▼
[Stage 4: Structured Relationship Expansion]
   │ Traverse canonical graphs (Curriculum -> Alignment -> Gap -> Need -> Plan -> Form)
   ▼
[Stage 5: Hybrid Retrieval (FTS5 + sqlite-vec + RRF)]
   │ Only invoked for semantic discovery / broad queries without exact IDs
   │ Combines SQLite unicode61 FTS5 and 384-dim E5 embeddings via RRF
   ▼
[Stage 6: Canonical Record Resolution & Authority Ordering]
   │ Map candidates back to authoritative JSON records
   │ Enforce strict authority precedence (Levels 1-8)
   ▼
[Stage 7: Conflict Detection & Material Generation Gate]
   │ Check for coverage contradictions (KNOWLEDGE_CONFLICT -> REVIEW_REQUIRED)
   │ Evaluate Material Generation Safety Gate (All 5 criteria required for true)
   │ Emit structured Knowledge Context Pack
```

---

## 3. Outcome Ambiguity & Theme Scoping Rules

In TYMM curricula, learning outcome codes (e.g. `TDE4.4`) repeat across themes with distinct verbatim descriptions and pedagogical requirements.

### Ambiguous Query Handling
- **Query**: `"TDE4.4"` (No theme specified)
  - `resolution_status`: `"PARTIALLY_RESOLVED"`
  - `ambiguity_status`: `"AMBIGUOUS_ENTITY"`
  - `material_generation_allowed`: `false`
  - `resolved_candidates`:
    - `TEMA_01::TDE4.4` (Edebî söyleyişin inceliğini yansıttığı yazısına yönelik...)
    - `TEMA_02::TDE4.4` (Yazısına yönelik değerlendirmelerini konu ve diğer yazma unsurları bağlamında...)
    - `TEMA_03::TDE4.4` (Yapısını incelikle ördüğü yazısına yönelik değerlendirmelerini...)
    - `TEMA_04::TDE4.4` (Yazısına yönelik değerlendirmelerini üslup ve diğer yazma unsurları bağlamında...)

### Disambiguated Query Handling
- **Query**: `"Tema 2 TDE4.4"`
  - `resolution_status`: `"RESOLVED"`
  - `ambiguity_status`: `"UNAMBIGUOUS"`
  - `resolved_entities[0].entity_key`: `"TDE_9::curriculum_outcome::TEMA_02::TDE4.4"`
  - `material_generation_allowed`: `true` (subject to freshness and conflict checks)

---

## 4. Assessment Terminology Separation

Strict terminology separation is enforced across all resolver outputs, semantic texts, and reports:

1. **`OFFICIAL_REQUIREMENT`**: Verbatim curriculum text (`"dereceli puanlama anahtarı"`).
2. **`TEXTBOOK_PROVIDES`**: Actual canonical structural instrument in the textbook (e.g. `assessment_criteria_table`, `self_assessment_form`, `checklist`).
3. **`REMAINING_GAP`**: Absence of the rated scoring structure in the textbook (`"Programın istediği dereceli puanlama anahtarı yapısının ders kitabında bulunmaması"`).
4. **`SELECTED_IMPLEMENTATION`**: The instructional output format chosen to fulfill the gap (`analytic_rubric`).

> [!WARNING]
> Phrases like *"program analitik rubrik istiyor"* or *"kitapta analitik rubrik gap'i var"* are strictly forbidden. The program demands a `"dereceli puanlama anahtarı"`; `analytic_rubric` is strictly the `selected_implementation`.

---

## 5. Material Generation Safety Gate

Downstream material generation is strictly governed by the **Material Generation Safety Gate**:

$$\text{material\_generation\_allowed} = \text{true} \iff \begin{cases}
\text{index\_freshness} = \text{"INDEX\_FRESH"} \\
\text{resolution\_status} = \text{"RESOLVED"} \\
\text{conflicts} = [] \\
\text{ambiguity\_status} \neq \text{"AMBIGUOUS\_ENTITY"} \\
\text{canonical\_resolution\_verified} = \text{true}
\end{cases}$$

If any condition is violated, `material_generation_allowed` evaluates to `false` and the exact `material_generation_block_reason` is returned.

---

## 6. Immutable Authority Precedence

| Rank | Authority Level | Canonical Origin | Precedence Guarantee |
|:---:|:---|:---|:---|
| **1** | `OFFICIAL_CURRICULUM_FROZEN` | `curriculum_map.json` | Verbatim official curriculum text and process components. Highest authority. |
| **2** | `OFFICIAL_TEXTBOOK_FROZEN` | `textbook_map.json` | Official MEB textbook sections, activities, and texts. |
| **3** | `OFFICIAL_TEXTBOOK_FORM_FROZEN` | `textbook_forms_index.json` | 28 official assessment instruments and classified structural types. |
| **4** | `VALIDATED_ALIGNMENT` | `themes/tema_XX/alignment.json` | Verified curriculum-textbook coverage mappings. |
| **5** | `VALIDATED_GAP` | `themes/tema_XX/gap_analysis.json` | Validated structural and pedagogical gaps (`PARTIALLY_COVERED`, etc.). |
| **6** | `VALIDATED_RESOURCE_PLAN` | `themes/tema_XX/resource_plan.json` | Verified theme-level instructional and assessment resource plans. |
| **7** | `VALIDATED_PRODUCTION_PLAN` | `production/production_manifest.json` | Required and approved production queue materials. |
| **8** | `PEDAGOGICAL_RECOMMENDATION` | `production/school_based_planning_options.json` | School-based planning options. Must **never** override official facts (Ranks 1–7). |
