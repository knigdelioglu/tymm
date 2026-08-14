---
name: tymm-material-planner
description: >-
  Türkiye Yüzyılı Maarif Modeli (TYMM) öğretim programı ve resmî ders kitaplarına göre sınıf içi materyal,
  öğrenme yaşantısı, çalışma kâğıdı, ölçme-değerlendirme araçları ve öğretmen kaynakları planlamak ve üretmek için kullanılır.
  Plans TYMM class resources, lesson materials, and teacher supports aligned to the Türkiye Yüzyılı Maarif Modeli.
---

# TYMM Material Planner

## Use

Use this skill when the user wants classroom resources, lesson materials, or teacher supports aligned to the Türkiye Yüzyılı Maarif Modeli (TYMM), especially when the user provides an official curriculum and an official textbook.

Accept high-level requests such as:

- “9. sınıf TDE 2. tema için kaynak hazırla.”
- “10. sınıf fizik bu ünite için öğretmen kaynaklarını üret.”
- “Bu program ve ders kitabına göre eksik sınıf içi materyalleri planla.”
- “Tema 2 TDE4.4 için kitapta ne eksik?”
- “Şiir yazarken öğrenciyi nasıl değerlendireceğim?”

Do not require the user to choose worksheet, rubric, poster, experiment sheet, or another document type. Infer the required instructional resources from the curriculum, textbook, subject profile, expected evidence, and gaps.

## Core contract

1. **Single Source of Truth Invariant**: The authoritative source of truth consists strictly of persistent, verified, frozen canonical structured JSON files in `knowledge/<COURSE_GRADE>/`. The local Vector Database (`knowledge.sqlite` / `sqlite-vec`) is **NOT** the source of truth; it is solely a candidate retrieval accelerator / semantic candidate finder.
2. **Deterministic Knowledge Resolver**: All queries and generation steps must pass through the deterministic Knowledge Resolver pipeline: Exact Structured Lookup → Relationship Graph Expansion → Hybrid Candidate Search (FTS5 + sqlite-vec + RRF) → Canonical Entity Resolution.
3. **Immutable Authority Ranking**:
   - `Rank 1`: `OFFICIAL_CURRICULUM_FROZEN` (`curriculum_map.json`)
   - `Rank 2`: `OFFICIAL_TEXTBOOK_FROZEN` (`textbook_map.json`)
   - `Rank 3`: `OFFICIAL_TEXTBOOK_FORM_FROZEN` (`textbook_forms_index.json`)
   - `Rank 4`: `VALIDATED_ALIGNMENT` (`themes/tema_XX/alignment.json`)
   - `Rank 5`: `VALIDATED_GAP` (`themes/tema_XX/gap_analysis.json`)
   - `Rank 6`: `VALIDATED_RESOURCE_PLAN` (`themes/tema_XX/resource_plan.json`)
   - `Rank 7`: `VALIDATED_PRODUCTION_PLAN` (`production/production_manifest.json`)
   - `Rank 8`: `PEDAGOGICAL_RECOMMENDATION` (`production/school_based_planning_options.json`)
   *Rule: Level 8 Pedagogical Recommendations cannot override official facts (Ranks 1–7).*
4. Maintain persistent knowledge maps (`knowledge/<COURSE_GRADE>/`) as the primary working cache prior to material planning and generation.
5. Track source identity and SHA-256 fingerprint for curriculum, textbook, and knowledge files. If hashes match and index is `INDEX_FRESH`, do not re-parse raw files.
6. Preserve official curriculum statements, codes, and process components verbatim (`verbatim: true`).
7. Classify textbook assessment tools into 7 distinct structural types (`assessment_criteria`, `checklist`, `self_assessment`, `peer_assessment`, `teacher_evaluation_form`, `analytic_rubric`, `rating_scale`) based on structure and performance levels, never solely by printed title.
8. If verified map data conflicts with a new input or PDF reading, never silently overwrite; set `KNOWLEDGE_CONFLICT` -> `REVIEW_REQUIRED`.
9. Use other official MEB documents next.
10. Use MEB/TYMM web verification only when an input is missing, its identity/version/currentness is uncertain, or the program and textbook conflict.
11. Use external sources only after identifying an instructional need that the supplied program and textbook do not adequately support.
12. Never silently replace a supplied curriculum or textbook with a web result.
13. Never invent official learning outcomes, codes, process components, values, lesson hours, editions, or program versions.
14. Keep official facts, textbook extractions, external sources, and generated pedagogy separate through provenance.
15. Do not present generated material as MEB-approved.
16. Do not reproduce long copyrighted textbook or literary content merely because the user supplied the book.

## Required decision order

Follow this order:

```
USER REQUEST
   │
   ▼
[Gate 0: Knowledge Resolution & Freshness Check]
   ├── Check knowledge/<COURSE_GRADE>/index/ (knowledge.sqlite, index_manifest.json)
   ├── Exact Structured Lookup (Outcome codes, Form IDs, Material IDs, Theme IDs)
   ├── Structured Relationship Expansion
   └── Hybrid Retrieval (FTS5 + sqlite-vec + RRF) -> Canonical Record Resolution
   │
   ▼
[Gate 1: Curriculum, Textbook & Assessment Forms Resolution]
   └── Load verified curriculum_map, textbook_map, textbook_forms_index (7 structural types)
   │
   ▼
[Gate 2: Instructional Needs Analysis]
   └── Derive instructional needs and expected student evidence
   │
   ▼
[Gate 3: Instructional Resource Plan]
   └── Define resource functions and production decisions (REUSE vs GENERATE)
   │
   ▼
[Gate 4: Alignment & Two-Stage Gap Analysis]
   └── Program-textbook alignment matrix and remaining gaps
   │
   ▼
[Gate 5: External Sources & Rights]
   └── External source packs (only if justified by remaining gaps)
   │
   ▼
[Gate 6: Generation]
   └── Produce required materials strictly grounded in resolved canonical entities
   │
   ▼
[Gate 7: Validation & Quality Handoff]
   └── Coverage matrix and multi-dimensional QA report
```

The governing rule is: determine what learning requires first, check what the textbook already provides second, and produce only what remains necessary third.

## Gate 0: knowledge resolution, authority, and persistent knowledge base

Check the persistent knowledge base (`knowledge/<COURSE_GRADE>/`) before re-parsing raw files.
1. Run `KnowledgeResolver` (`scripts/knowledge_resolver.py resolve --query <user_query>`).
2. Verify index freshness via `KnowledgeIndexer` (`scripts/knowledge_index.py status`).
3. Check `source_manifest.json` and compute SHA-256 fingerprints.
4. If an exact entity is present in query (e.g. `TDE4.4`, `FORM_IN_T2_YAZMA_CRITERIA`, `MAT_T2_YAZMA_RUBRIC`), resolve canonical entity directly and expand the relationship graph without vector DB search.
5. If the query is semantic or exploratory, invoke local hybrid RAG (FTS5 + `sqlite-vec` with RRF), and resolve top semantic candidates back to canonical structured JSON records.
6. If any knowledge conflict or stale index is detected, set `resolution_status = "REVIEW_REQUIRED"` and halt generation until verified.

## Gate 1: curriculum, textbook, and assessment forms resolution

Read the supplied curriculum first (or load `curriculum_map.json`). Preserve exact official wording (`verbatim: true`), codes, process components, and source locators.

Read the supplied textbook separately (or load `textbook_map.json` and `textbook_forms_index.json`). Build structured persistent models containing:

- book identity, course, grade, edition, and program-year clues
- units/themes and page ranges
- texts, genres, authors, works, concepts, data, visuals, and media
- existing activities, questions, student products
- assessment instruments indexed into `textbook_forms_index.json` categorized into 7 structural types:
  1. `assessment_criteria` (ölçüt tablosu, no rating level descriptors)
  2. `checklist` (ikili / binary kontrol listesi)
  3. `self_assessment` (öz değerlendirme formu)
  4. `peer_assessment` (akran değerlendirme formu)
  5. `teacher_evaluation_form` (öğretmen gözlem / değerlendirme formu)
  6. `analytic_rubric` (çok boyutlu ölçütler ve açık performans düzeyi betimleyicileri içeren matris)
  7. `rating_scale` (dereceleme ölçeği, frequency or numerical score without cell descriptors)
  *Rule: Classify based on structure, never solely on printed title.*
- supports, enrichment, safety, accessibility, and explicit program links
- page, section, figure, table, or activity locators
- OCR uncertainty and human-review flags

For theme-level requests, slice only required theme records (`themes/tema_XX/`) instead of remodeling the entire PDF.

Compare program and textbook identity. If class, program year, unit/theme structure, or edition conflicts, set PROGRAM_TEXTBOOK_VERSION_MISMATCH, mark the alignment contract CONFLICTED, and stop final generation until teacher verification.

## Gate 2: instructional needs analysis

Answer:

What learning experiences, student actions, evidence, support, feedback, and assessment are needed for the targeted outcomes to occur?

Create one or more instructional_needs_analysis records with:

- need_id, targeted_learning_outcomes, targeted_process_components
- domain_or_subject_profile, conceptual_prerequisites, procedural_or_skill_prerequisites
- expected_student_actions, expected_student_evidence, likely_misconceptions
- cognitive_demand, interaction_need, representation_need, practice_need, feedback_need
- assessment_need, differentiation_need, enrichment_opportunity, accessibility_need, safety_need
- external_content_need, rationale and provenance

Ground each need in official outcomes/process components, the subject profile, textbook experiences, expected evidence, or a justified authoritative pedagogical source.

## Gate 3: instructional resource plan

Convert needs into a teacher-visible plan. A resource_type is an instructional function, not a file format. Use functions such as:

- `learning_input_or_representation`, `scaffold_or_concept_support`, `guided_practice`
- `student_production_task`, `feedback_support`, `assessment_support`
- `differentiation_support`, `enrichment`, `teacher_implementation_support`
- `accessibility_support`, `safety_support`, `external_content`

Use only these production decisions:
- `REUSE_TEXTBOOK`
- `REUSE_WITH_TEACHER_GUIDE`
- `ADAPT_TEXTBOOK_ACTIVITY`
- `GENERATE`
- `GENERATE_ASSESSMENT_SUPPORT`
- `GENERATE_DIFFERENTIATION`
- `GENERATE_ENRICHMENT`
- `NO_ACTION`

## Gate 4: alignment and two-stage gap analysis

Create program_textbook_alignment records with:
- program item and locator
- instructional need and need_id
- resource plan and resource_plan_id
- textbook section/activity and locator
- textbook student action and evidence
- primary coverage: `COVERED`, `PARTIALLY_COVERED`, or `NOT_COVERED`
- need tags: `NEEDS_ASSESSMENT_SUPPORT`, `NEEDS_DIFFERENTIATION`, `NEEDS_ENRICHMENT`
- remaining gap and production decision

Evaluate this chain:
`learning requirement → required instructional resource → textbook coverage → remaining gap → production decision`

Do not mark a target `COVERED` merely because the textbook mentions the topic. If the textbook does not provide the expected student evidence or the required process component, mark it `PARTIALLY_COVERED` or `NOT_COVERED`.

Do not recreate a sufficient textbook activity. Prefer `REUSE_TEXTBOOK`, `REUSE_WITH_TEACHER_GUIDE`, or `ADAPT_TEXTBOOK_ACTIVITY` when appropriate.

## Gate 5: external sources and rights

If a remaining gap has `external_source_needed=true`, create `external_source_pack` entries only for that gap. For each source_card record authority, date, URL, usable scope, student level, license/copyright status, transformation, gap item, and verification status.

External sources must not replace the supplied curriculum or textbook. A user upload does not by itself grant reproduction rights.

For supplied textbook content, prefer page references or new derived tasks. Limited quotation may be used only when justified. Do not automatically reproduce long copyrighted passages.

## Gate 6: generation

Generate only resources whose `production_decision` requires action. Select the output format after selecting the instructional function. Produce teacher and student views when the plan requires both.

Subject routing:
- TDE/Turkish: input text/audio, close reading, vocabulary/concept support, comparison, speaking/writing product, criteria, feedback.
- Mathematics: problem context, representation, modeling, reasoning, strategy comparison, error analysis, practice, formative evidence.
- Science/Physics/Chemistry/Biology: phenomenon, hypothesis, variables, experiment/data, safety, observation, graph/model, claim-evidence-reasoning, misconception check.
- History/Social/Geography: primary/secondary sources, provenance, chronology, map/data/graph, perspectives, claim-evidence, change/continuity, spatial relation.
- Other subjects: load the relevant subject profile and apply its decision rules.

## Gate 7: validation and handoff

Create a coverage_matrix with this chain:
`program target → instructional need → recommended resource → textbook counterpart → remaining gap → generated or reused material → student evidence → assessment instrument`

Create a quality_report with `PASS`, `FAIL`, `N/A`, or `REVIEW` for all QA dimensions.

## Reference loading

Read only the references needed for the request:

- [references/knowledge-resolver.md](./references/knowledge-resolver.md) for deterministic retrieval pipeline, intent classification, authority precedence, and knowledge context pack schemas.
- [references/hybrid-rag.md](./references/hybrid-rag.md) for local SQLite + `sqlite-vec` + FTS5 architecture, embeddings, and RRF algorithms.
- [references/knowledge-base.md](./references/knowledge-base.md) for persistent knowledge base directory structure, map schemas, fingerprinting, and theme slicing.
- [references/input-resolution.md](./references/input-resolution.md) for input authority, curriculum resolution, textbook extraction, locators, and mismatch handling.
- [references/instructional-needs.md](./references/instructional-needs.md) for needs analysis and evidence-first decisions.
- [references/resource-planning.md](./references/resource-planning.md) for resource functions, priorities, and production decisions.
- [references/alignment-gap.md](./references/alignment-gap.md) for alignment contracts, gap analysis, reuse, and coverage matrices.
- [references/subject-profiles.md](./references/subject-profiles.md) for domain-specific resource-planning rules.
- [references/source-and-rights.md](./references/source-and-rights.md) for external sources, provenance, copyright, and textbook use.
- [references/assessment-accessibility.md](./references/assessment-accessibility.md) for assessment, differentiation, accessibility, safety, and quality gates.
