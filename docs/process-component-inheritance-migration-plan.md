# Süreç Bileşeni Inheritance Düzeltme Planı

**Kapsam:** `courses/TDE_9`, `courses/TDE_10`, `courses/TDE_11`, `courses/TDE_12` + shared extraction/validation/index/runtime zinciri.  
**Temel invariant:** `@docs/canonical-process-component-inheritance.md`  
**Migration durumu:** `P0 COMPLETE` — 24 Ağustos 2026

## Hedef

Tema sayfasında tekrar yazılmadığı için kaybolan çatı süreç bileşenlerini resmî öğretim programındaki ortak parent-outcome hiyerarşisinden canonical veriye doğru provenance ile bağlamak; doğrulanmış tema-spesifik specialization'ları korumak; aynı hatanın yeni sınıf/ders bootstraplarında ve validatorlarda tekrar PASS almasını engellemek.

Bu hedef tamamlanmıştır. Aşağıdaki maddeler migration kapanış kaydı olarak korunur.

---

## P0.1 — Course-wide normatif roof catalog — COMPLETE

Canonical katalog:

`courses/TDE_SHARED/curriculum_process_component_catalog.json`

Sonuç:

- 16 parent family (`TDE1.1`–`TDE4.4`)
- 66 subordinate process component
- normatif inheritance dayanağı: resmî ortak program bölümü
- duplicate: 0
- parent-prefix ihlali: 0
- locator eksikliği: 0

Katalog grade-theme verisinden kopyalanmaz; programın ortak/çatı bölümüne dayanır.

## P0.2 — Generic resolver/schema — COMPLETE

Üç katman ayrılmıştır:

1. **explicit** — tema sayfasında doğrudan yayımlanan süreç bileşenleri
2. **inherited** — shared roof catalogdan gelen süreç bileşenleri
3. **effective** — downstream/runtime tarafından kullanılan çözüm

Çözümleme:

```text
verified THEME_EXPLICIT varsa
    effective = theme explicit
aksi halde ROOF catalog varsa
    effective = roof inherited
aksi halde SOURCE_VERIFIED_NONE varsa
    effective = []
aksi halde
    unresolved/fail
```

Verified tema specialization roof ile merge edilmez. Effective projection provenance originini korur.

## P0.3 — TDE_9 referans migration — COMPLETE

Sonuç:

- total outcomes: `54`
- roof-covered: `54`
- explicit: `2`
- inherited: `52`
- verified-none: `0`
- unresolved: `0`
- inheritance missing: `0`
- structural error: `0`

Eski “tema sayfasında tekrar edilmemişse süreç bileşeni yoktur” yorumu `courses/TDE_9/validation_report.md` içinde açıkça geri çekilmiştir.

## P0.4 — Shared validator/gate — COMPLETE

Generic fail-closed kural uygulanmaktadır:

```text
THEME_EXPLICIT yok
AND roof_catalog[parent_code].components > 0
AND effective(theme_outcome).components == 0
=> PROCESS_COMPONENT_INHERITANCE_MISSING
=> FAIL
```

Gate ayrıca şunları denetler:

- inherited source locator zorunluluğu
- component parent-prefix uyumu
- duplicate component code
- cross-grade theme-data leakage
- unresolved parent family
- resolution-contract / curriculum scope eşitliği
- expected explicit/inherited count drift
- canonical fingerprint freshness
- duplicate canonical identity

## P0.5 — Regression tests — COMPLETE

Regression kapsamı:

1. explicit yok + roof var → inherited PASS
2. verified explicit var + roof var → explicit PASS, merge yok
3. verified explicit specialization → PASS
4. roof var + effective boş → FAIL
5. roof yok + `SOURCE_VERIFIED_NONE` → boş PASS
6. inherited locator yok → FAIL
7. duplicate component code → FAIL
8. başka grade'in theme kaydını inheritance kaynağı yapma → FAIL
9. duplicate canonical outcome identity → `DuplicateCanonicalKeyError`
10. stale derived index/runtime → fail-closed
11. knowledge conflict → fail-closed

TDE_9 eski gerçek bug'ı regression case olarak korunur.

## P0.6 — TDE_10, TDE_11, TDE_12 migration — COMPLETE

Aynı shared resolver ile sonuçlar:

| Course | Total | Explicit | Inherited | Unresolved | Missing | Status |
|---|---:|---:|---:|---:|---:|---|
| TDE_9 | 54 | 2 | 52 | 0 | 0 | PASS |
| TDE_10 | 64 | 0 | 64 | 0 | 0 | PASS |
| TDE_11 | 64 | 0 | 64 | 0 | 0 | PASS |
| TDE_12 | 64 | 0 | 64 | 0 | 0 | PASS |

Durable kanıt:

`docs/process-component-inheritance-audit.json`

TDE_11/TDE_12 curriculum validation raporları completeness metrikleriyle güncellenmiştir.

## P0.7 — Derived katmanları fresh rebuild — COMPLETE

TDE_9 fresh derived sonuçları:

- knowledge index: `INDEX_FRESH`
- index schema: `2.1`
- indexed records: `595`
- runtime package: `1.2.0`
- runtime compiler: `1.2.0`
- runtime validation: `PASS`
- process-component resolution: `PASS`
- shared roof catalog + resolution contract fingerprint'e dahil

TDE_10 da aynı dependency-aware shared çözümle yeniden publish edilmiştir.

Stale publish koruması CI'da aktiftir. Ders planı cursor/generated paket değişiklikleri, index/runtime dependency olmadığı için artık gereksiz P0 rebuild veya stale-publish veto oluşturmaz.

## P0.8 — Downstream doğrulama — COMPLETE

ÖğretmenOS curriculum-only TDE_11/TDE_12 builder'ında bulunan veri kaybı giderilmiştir.

Downstream runtime artık:

- shared roof catalogu dependency olarak taşır,
- grade-specific resolution contract'ı dependency olarak taşır,
- effective process component listesini SQLite'a yazar,
- `process_component_origin` kolonunu korur,
- shared catalog + resolution contract'ı canonical fingerprint'e dahil eder,
- unresolved/missing durumda fail-closed çalışır.

Published downstream sonuçlar:

- TDE_11 runtime `1.2.0`: 64/64 `ROOF_INHERITED`, `RUNTIME_FRESH`, PASS
- TDE_12 runtime `1.2.0`: 64/64 `ROOF_INHERITED`, `RUNTIME_FRESH`, PASS

---

## P1 — Gözlemlenebilirlik — COMPLETE

Course validation/audit katmanı şu metrikleri raporlar:

- total outcomes
- outcomes_with_roof_components
- explicit_component_outcomes
- inherited_component_outcomes
- verified_no_component_outcomes
- unresolved_component_outcomes
- inheritance_missing_count
- structural_error_count

PASS için `inheritance_missing_count = 0`, `unresolved_component_outcomes = 0` ve `structural_error_count = 0` zorunludur.

## P1 — Bootstrap hardening — COMPLETE

Aşağıdaki prompt/workflowlar shared roof invariantını zorunlu referans almaktadır:

- `docs/yeni-ders-sinif-bootstrap-promptu.md`
- `docs/yalniz-ogretim-programi-bootstrap-promptu.md`
- `AGENTS.md`
- canonical curriculum validation workflowları

## P1 — Downstream presentation provenance — IMPLEMENTED / CI CONFIRMATION PENDING

ÖğretmenOS tarafında uygulandı:

- `Outcome.processComponentOrigin` domain modeline eklendi,
- data source `process_component_origin` kolonunu schema-aware biçimde okuyor,
- eski runtime schema'larında kolon yoksa `NULL AS process_component_origin` ile backward compatibility korunuyor,
- outcome detayında `ROOF_INHERITED` → “Resmî programın ortak çatı tanımından devralındı” olarak gösteriliyor,
- `THEME_EXPLICIT` → “Bu tema için resmî programda açıkça tanımlandı” olarak gösteriliyor,
- raw süreç bileşeni JSON'u öğretmen-okunabilir kod + ifade listesine dönüştürülüyor,
- TDE_11/TDE_12 paket regression testi provenance'ın DB → data source → domain model → block detail zincirinde korunduğunu assert ediyor.

Bu P1 değişiklikleri canonical migration kapanışını etkilemez. Son push için CI publish kanıtı oluşana kadar bu bölüm bilinçli olarak `CI CONFIRMATION PENDING` tutulur.

---

## Uygulama sırası — TAMAMLANDI

```text
P0.1 shared roof catalog            COMPLETE
  ↓
P0.2 resolver/schema                COMPLETE
  ↓
P0.3 TDE_9 reference migration      COMPLETE
  ↓
P0.4 validator + P0.5 tests         COMPLETE
  ↓
P0.6 TDE_10/11/12 migration         COMPLETE
  ↓
P0.7 index/runtime rebuild          COMPLETE
  ↓
P0.8 downstream verification        COMPLETE
```

## Done kriteri — KARŞILANDI

- Shared TDE roof catalog complete ve normatif kaynaklı. ✅
- Parent roof component taşıyan hiçbir non-explicit theme outcome efektif boş değil. ✅
- Explicit specialization ve inherited provenance ayrılmış. ✅
- Eski yanlış TDE_9 validation hükmü kaldırılmış. ✅
- TDE_9–12 yeni gate ile yeniden PASS. ✅
- Regression testleri eski bug'ı yakalıyor. ✅
- Derived index/runtime fresh rebuild edilmiş. ✅
- Downstream paketler stale değil ve effective component verisini koruyor. ✅

**P0 migration kapanış sonucu:** `COMPLETE / PASS`
