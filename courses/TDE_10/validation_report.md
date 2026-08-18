# TDE_10 Canonical Knowledge Validation Report

**Course:** TDE_10 — 10. Sınıf Türk Dili ve Edebiyatı  
**Status:** `CURRICULUM_DRAFT + NEEDS_COMPLETE / TEXTBOOK_CONTENT_MAPPING_PENDING / NOT_FROZEN`  
**Architecture reference:** `docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md`

## 1. Current validation result

TDE_10 canonicalization is being built with TDE_9 as the schema/architecture reference, without copying TDE_9 course facts.

Current state:

```text
Source registration                         PASS
4-part curriculum bundle presence           PASS
Official TYMM theme identity                PASS
Theme order                                 PASS
Official 43-hour theme instruction          PASS
User-confirmed +2 school planning           PASS AS PLANNING RULE
64 scoped learning outcomes                 PASS
Stable entity key uniqueness                PASS
Theme-level assessment requirements         PASS
Process-component supporting audit          PARTIAL / FAIL-CLOSED
Instructional needs — TEMA_01               CREATED
Instructional needs — TEMA_02               CREATED
Instructional needs — TEMA_03               CREATED
Instructional needs — TEMA_04               CREATED
Official OGM textbook theme assets          RESOLVED AS SUPPORTING ASSETS
Textbook source-structure map               CREATED / NOT FROZEN
Textbook page-level content mapping          PENDING
Textbook forms index                        PENDING
Program-textbook alignment                  BLOCKED BY TEXTBOOK CONTENT MAP
Gap analysis                                BLOCKED BY ALIGNMENT
Canonical freeze                            BLOCKED
Production/index/runtime/P0                  BLOCKED
```

## 2. Source identity

The curriculum is registered as one multi-part source bundle with four theme snapshots:

1. `TEMA_01` — `SÖZÜN EZGİSİ`
2. `TEMA_02` — `KELİMELERİN RİTMİ`
3. `TEMA_03` — `DÜNDEN BUGÜNE`
4. `TEMA_04` — `NESİLLERİN MİRASI`

Normative TYMM cross-check locators:

- `https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/242?kod=D15`
- `https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/247`
- `https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/256`
- `https://tymm.meb.gov.tr/turk-dili-ve-edebiyati-dersi/unite/261`

The official pages identify the course as 10th-grade Turkish Language and Literature and state 43 instructional hours per theme.

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

The distinction is explicit in `source_manifest.json`, `curriculum_map.json` and `planning/course_timeline.json`.

The 2-hour school-based allocation is not represented as a curriculum gap and is not treated as part of the official 43-hour theme instruction.

## 4. Outcome identity validation

Each theme contains 16 scoped learning outcomes:

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

## 5. Process-component audit and authority resolution

`source_docs/curriculum_process_component_audit.json` records the process-component hierarchy currently verified from official MEB/OGM supporting material.

Examples already cross-checked include:

```text
TDE2.1.1  İnceler ve görüş oluşturur.
TDE2.1.2  Seçim yapar.
TDE2.2.1  Ön bilgilerle bağlantı kurar.
TDE2.2.2  Tahmin eder.
TDE2.3.1  Parçaları belirler.
TDE2.3.2  Parçalar arasındaki ilişkileri belirler.
TDE2.3.3  Parçalar arasındaki etkileşimleri belirler.
TDE3.1.1  Seçim yapar.
TDE3.1.2  İlişkiyi sürdürür.
TDE4.1.1  Seçim yapar.
TDE4.1.2  İlişkiyi sürdürür.
```

A wording difference was found between the normative TYMM curriculum and OGM supporting material for some `TDE*.4` labels:

```text
Normative TYMM:  ... sürecini değerlendirebilme
OGM support:     ... değerlendirmelerini yansıtabilme / Yansıtabilme
```

Resolution is fail-closed and authority-based: **normative TYMM curriculum wording wins**. OGM may support process-component semantics but cannot silently rewrite canonical outcome wording.

The component audit is still partial, therefore `curriculum_map.json` remains `NOT_FROZEN`.

## 6. Instructional needs layer

The four theme-level `needs.json` files now exist:

```text
themes/tema_01/needs.json
themes/tema_02/needs.json
themes/tema_03/needs.json
themes/tema_04/needs.json
```

Each separates the four skill areas and records:

- targeted learning outcomes,
- available process-component evidence,
- prerequisites,
- expected student actions,
- expected student evidence,
- likely misconceptions,
- cognitive demand,
- interaction/representation/practice needs,
- feedback and assessment needs,
- differentiation/enrichment/accessibility needs,
- provenance.

Crucial invariant:

> `needs.json` describes what learning evidence is required; it does **not** claim that the textbook fails to provide it.

For that reason the records use `TEXTBOOK_COVERAGE_PENDING` rather than creating premature gaps or generation decisions.

## 7. Theme-level assessment requirements captured

The curriculum map and needs layer capture:

- official assessment instrument names,
- speaking performance tasks,
- writing performance tasks,
- rubric criterion hints explicitly named by the curriculum,
- theme-end assessment method.

Architectural rule remains active:

> A curriculum requirement for a `dereceli puanlama anahtarı` is not silently rewritten as an official requirement for an `analytic rubric`.

Physical assessment artifacts will only be decided after textbook coverage and cross-theme assessment consolidation.

## 8. Textbook source resolution

The primary textbook locator remains the exact registered official TYMM/MEB URL:

`https://tymm.meb.gov.tr/kitap/78/turk-dili-ve-edebiyati-10.sinif-ders-kitabi`

Four official MEB/OGM e-book theme previews have also been resolved as **supporting assets**:

```text
TEMA_01  Sözün Ezgisi       OGM asset 6403  pages 10–83
TEMA_02  Kelimelerin Ritmi  OGM asset 6407  pages 84–153
TEMA_03  Dünden Bugüne      OGM asset 6834  pages 154–233
TEMA_04  Nesillerin Mirası  OGM asset 6409  pages 234–310
```

These assets are registered in `source_manifest.json` with lower authority than the exact user-supplied TYMM textbook locator. They may support mapping, but they do not silently replace the primary source.

`textbook_map.json` now exists as a **source-structure draft**. It records the verified theme identities and preview page ranges but intentionally keeps:

```text
sections = []
activities = []
assessment_form_ids = []
```

until actual page-level textbook content is extracted. Empty arrays mean `UNRESOLVED`, not `ABSENT`.

## 9. Freeze blockers

Before curriculum/textbook canonical maps may become `FROZEN`:

1. Complete grade-10 process-component hierarchy audit.
2. Complete local curriculum snapshot/page locator audit.
3. Verify exact TYMM primary textbook ↔ official OGM preview identity/linkage where possible.
4. Extract textbook page-level sections, activities, expected student evidence and assessment forms.
5. Classify textbook forms without assuming every criteria table is an analytic rubric.

Until these are complete, alignment/gap/resource-plan generation remains closed.

## 10. Next production sequence

```text
1. Complete process-component extraction/audit
2. Complete official textbook page-level map
3. Build textbook_forms_index
4. Freeze curriculum + textbook canonical maps
5. Build per-theme alignment
6. Build gap analysis
7. Build resource plans
8. Cross-theme consolidation
9. Build assessment artifact registry + production manifest
10. Build/rebuild knowledge.sqlite
11. Resolver safety regression
12. Runtime projection
13. P0 Production Gate
14. Artifact generation + teacher review lifecycle
```

## 11. Current conclusion

TDE_10 is now beyond source registration. It has:

- a 64-outcome curriculum draft map,
- scoped stable entity identities,
- a 45-hour-per-theme / 180-hour annual timeline,
- a partial official process-component audit,
- all four curriculum-based instructional-needs files,
- resolved official MEB/OGM textbook theme assets,
- a textbook source-structure draft.

In accordance with the architecture report, **no gap, resource-generation decision, index or P0 PASS is fabricated before the textbook content layer is actually mapped and canonical sources are frozen.**
