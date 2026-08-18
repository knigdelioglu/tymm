# TDE_10 Canonical Knowledge Validation Report

**Course:** TDE_10 — 10. Sınıf Türk Dili ve Edebiyatı  
**Status:** `CURRICULUM_DRAFT_VALIDATED / NOT_FROZEN`  
**Architecture reference:** `docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md`

## 1. Current validation result

TDE_10 curriculum canonicalization has started using TDE_9 as the schema/architecture reference, without copying TDE_9 course facts.

Current state:

```text
Source registration                  PASS
4-part curriculum bundle presence    PASS
Official web theme identity          PASS
Theme order                          PASS
Official 43-hour theme instruction   PASS
User-confirmed +2 school planning    PASS AS PLANNING RULE
64 scoped learning outcomes          PASS
Stable entity key uniqueness         PASS
Assessment instrument extraction     PASS (theme-level)
Process component extraction         PENDING
Local PDF page-level locator audit   PENDING
Textbook canonical map               PENDING
Textbook forms index                 PENDING
Program-textbook alignment           BLOCKED BY TEXTBOOK MAP
Gap analysis                         BLOCKED BY ALIGNMENT
Canonical freeze                     BLOCKED
Production/P0 gate                   BLOCKED
```

## 2. Source identity

The curriculum is registered as one multi-part source bundle with four theme snapshots:

1. `TEMA_01` — `SÖZÜN EZGİSİ`
2. `TEMA_02` — `KELİMELERİN RİTMİ`
3. `TEMA_03` — `DÜNDEN BUGÜNE`
4. `TEMA_04` — `NESİLLERİN MİRASI`

Official TYMM cross-check locators:

- https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/242?kod=D15
- https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/247
- https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/256
- https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/261

All four official pages identify the course as 10th-grade Turkish Language and Literature and state 43 instructional hours for the theme.

## 3. Time model

The repository uses the user-confirmed planning rule:

```text
1 theme = 45 hours outer block
        = 43 hours official theme instruction
        + 2 hours school-based planning

4 themes = 180 hours
         = 172 hours theme instruction
         + 8 hours school-based planning
```

The distinction is explicit in `curriculum_map.json` and `planning/course_timeline.json`.

The 2-hour school-based allocation is not represented as a curriculum gap and is not treated as part of the official 43-hour theme instruction.

## 4. Outcome identity validation

Each theme currently contains 16 scoped learning outcomes:

```text
TDE1.1–TDE1.4  Dinleme/İzleme
TDE2.1–TDE2.4  Okuma
TDE3.1–TDE3.4  Konuşma
TDE4.1–TDE4.4  Yazma
```

Total canonical outcome records: **64**.

Outcome codes repeat across themes, so course-wide identity never relies on the bare outcome code. Stable identity follows the architecture report:

```text
TDE_10::curriculum_outcome::TEMA_01::TDE2.1
TDE_10::curriculum_outcome::TEMA_02::TDE2.1
...
```

All 64 generated stable keys are unique.

## 5. Theme-level assessment requirements captured

The curriculum map now captures, at theme level:

- official assessment instrument names,
- speaking performance tasks,
- writing performance tasks,
- rubric criterion hints explicitly named by the curriculum,
- theme-end assessment method.

Important architectural rule remains active:

> A curriculum requirement for a `dereceli puanlama anahtarı` is not silently rewritten as an official requirement for an `analytic rubric`.

Physical assessment artifacts will only be decided after textbook coverage and cross-theme assessment consolidation.

## 6. Why the curriculum map is not FROZEN yet

The current official TYMM web pages expose the outcome statements and broad teaching/assessment structure, but the TDE_9 canonical schema also preserves process-component detail and page-level provenance from the source snapshots.

For that reason:

```text
process_components_verbatim = []
process_components_status   = PENDING_PDF_EXTRACTION
canonical_freeze_status     = NOT_FROZEN
```

This is intentional fail-closed behavior, not missing-data acceptance.

Before `curriculum_map.json` may become `VERIFIED / FROZEN`, the four local source snapshots must be audited for:

- process-component wording,
- source/page locators,
- any wording/version differences against the official web pages,
- differentiation/support/enrichment provisions required by the canonical schema.

## 7. Textbook gate

The primary textbook locator remains the exact registered official TYMM/MEB URL:

https://tymm.meb.gov.tr/kitap/78/turk-dili-ve-edebiyati-10.sinif-ders-kitabi

No third-party book copy is accepted as a silent primary-source replacement.

Until the official textbook source is resolved and mapped, these files must not be treated as complete:

```text
textbook_map.json
textbook_forms_index.json
themes/*/alignment.json
themes/*/gap_analysis.json
themes/*/resource_plan.json
production/*
index/knowledge.sqlite
runtime/course_runtime.sqlite
```

## 8. Next production sequence

The next steps follow the reusable architecture playbook:

```text
1. Complete curriculum process-component extraction
2. Resolve/map official textbook
3. Build textbook_forms_index
4. Freeze curriculum + textbook canonical maps
5. Build per-theme needs/alignment/gap/resource plans
6. Cross-theme consolidation
7. Build assessment artifact registry + production manifest
8. Build/rebuild knowledge.sqlite
9. Resolver safety regression
10. Runtime projection
11. P0 Production Gate
12. Artifact generation + teacher review lifecycle
```

## 9. Current conclusion

The TDE_10 course is no longer an empty source-registration shell. The first canonical curriculum layer and 45-hour theme timeline now exist and are structurally aligned with the TDE_9 reference implementation.

However, in accordance with the architecture report, **generation is not opened yet**. The current course state is deliberately `NOT_FROZEN` until process-component and official-textbook validation are completed.
