# Süreç Bileşeni Inheritance Düzeltme Planı

**Kapsam:** `courses/TDE_9`, `courses/TDE_10`, `courses/TDE_11`, `courses/TDE_12` + shared extraction/validation/index/runtime zinciri.

**Temel invariant:** `@docs/canonical-process-component-inheritance.md`

## Hedef

Tema sayfasında tekrar yazılmadığı için kaybolan çatı süreç bileşenlerini resmî öğretim programındaki ortak parent-outcome hiyerarşisinden canonical veriye doğru provenance ile bağlamak; doğrulanmış tema-spesifik specialization'ları korumak; aynı hatanın yeni sınıf/ders bootstraplarında ve validatorlarda tekrar PASS almasını engellemek.

---

## P0.1 — Course-wide normatif roof catalog

2024 resmî Türk Dili ve Edebiyatı Dersi Öğretim Programı'nın ortak bölümünden tek canonical katalog oluştur:

`courses/TDE_SHARED/curriculum_process_component_catalog.json`

Katalog:

- `TDE1.1`–`TDE1.4`
- `TDE2.1`–`TDE2.4`
- `TDE3.1`–`TDE3.4`
- `TDE4.1`–`TDE4.4`

parent family'lerinin resmî subordinate süreç bileşeni kodlarını, kısa verbatim başlıklarını ve source locatorlarını taşır.

Bu katalog grade-theme verisinden kopyalanmaz. Programın bütün kademelerde süreç bileşenlerinin kullanılmasını ve çatı çıktıların tekrar karmaşasını önlemek için tanımlandığını açıklayan ortak bölüm (`s. 19`) normatif inheritance dayanağıdır.

**Acceptance:** 16 parent family, 66 subordinate component; duplicate yok; parent-prefix ihlali yok; locator eksikliği yok.

## P0.2 — Generic resolver/schema

Theme outcome için üç katmanı ayır:

1. **explicit** — tema sayfasında doğrudan yayımlanan süreç bileşenleri
2. **inherited** — shared roof catalogdan gelen süreç bileşenleri
3. **effective** — downstream/runtime tarafından kullanılacak çözüm

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

Verified tema specialization, aynı subordinate kodu roof'tan farklı ifadeyle kullanabilir; bu tek başına conflict değildir. Explicit set ile roof set merge edilmez.

**Acceptance:** inherited veri tema sayfasından alınmış gibi provenance taşımaz; explicit specialization korunur.

## P0.3 — TDE_9 referans migration

TDE_9 ilk gerçek veri migrationıdır:

- 54 outcome shared katalogla eşleştirilir.
- Tema 1'de resmî explicit tanım taşıyan mevcut kayıtlar explicit olarak korunur.
- Explicit olmayan ve roof family'ye sahip outcome'lar inherited olarak çözülür.
- `validation_report.md` içindeki boş süreç bileşenlerini MEB yapısının doğal sonucu sayan yanlış hüküm kaldırılır.
- explicit/inherited/effective sayıları raporlanır.

**Beklenen mevcut başlangıç:** 54 outcome; yalnız iki outcome (`TDE1.2`, `TDE2.2`, Tema 1) explicit süreç bileşeni taşıyor, kalan kayıtların büyük bölümü roof inheritance gerektiriyor. Bu sayı migration sırasında script ile yeniden hesaplanıp doğrulanmalıdır.

## P0.4 — Shared validator/gate

Generic kural:

```text
THEME_EXPLICIT yok
AND roof_catalog[parent_code].components > 0
AND effective(theme_outcome).components == 0
=> PROCESS_COMPONENT_INHERITANCE_MISSING
=> FAIL
```

Ek kontroller:

- inherited source locator zorunlu
- component code parent-prefix uyumu
- duplicate component code fail
- başka grade'in theme verisinden inheritance fail
- unresolved parent family fail-closed
- yalnız explicit count ile completeness PASS verilemez

Curriculum-only ve full-course P0 gate'e bağlanır.

## P0.5 — Regression tests

En az:

1. explicit yok + roof var → inherited PASS
2. verified explicit var + roof var → explicit PASS, merge yok
3. verified explicit aynı alt kodu farklı tema-semantikle kullanıyor → PASS
4. roof var + effective boş → FAIL
5. roof yok + `SOURCE_VERIFIED_NONE` → boş PASS
6. inherited locator yok → FAIL
7. duplicate component code → FAIL
8. başka grade'in theme kaydını inheritance kaynağı yapma → FAIL

TDE_9 eski bug'ı gerçek veri regression case olarak tutulur.

## P0.6 — TDE_10, TDE_11, TDE_12 migration

TDE_9 referans migration yeşil olduktan sonra aynı resolver kullanılır.

- TDE_10'daki `curriculum_process_component_audit.json` supporting/cross-check kanıt olarak korunabilir; shared roof catalogun yerine geçmez.
- TDE_10 source manifestteki “theme snapshotta subordinate kod yok, dolayısıyla synthesize edilmedi” varsayımı shared roof inheritance açısından yeniden değerlendirilir.
- TDE_11 ve TDE_12 PASS raporları yeni completeness metriği ile yeniden üretilir.

## P0.7 — Derived katmanları fresh rebuild

Canonical migration sonrası:

- knowledge index / `knowledge.sqlite`
- course runtime SQLite
- runtime manifests/fingerprints
- generated package/projectionlar

fresh build edilir.

Stale runtime publish yasaktır.

## P0.8 — Downstream doğrulama

ÖğretmenOS ve diğer tüketicilerde:

- effective süreç bileşeni doluluğu
- `THEME_EXPLICIT` / `ROOF_INHERITED` origin bilgisi
- UI'nin boş diziyi gizleyerek canonical hatayı maskelememesi

kontrol edilir.

---

## P1 — Gözlemlenebilirlik

Her course validation raporu en az:

- total outcomes
- outcomes_with_roof_components
- explicit_component_outcomes
- inherited_component_outcomes
- verified_no_component_outcomes
- unresolved_component_outcomes
- inheritance_missing_count
- structural_error_count

metriklerini verir.

PASS için `inheritance_missing_count = 0`, `unresolved_component_outcomes = 0` ve `structural_error_count = 0` zorunludur.

## P1 — Bootstrap hardening

Şu prompt/workflowlar shared roof invariantını zorunlu referans almalı:

- `docs/yeni-ders-sinif-bootstrap-promptu.md`
- `docs/yalniz-ogretim-programi-bootstrap-promptu.md`
- canonical curriculum çıkaran gelecekteki tüm workflowlar

---

## Uygulama sırası

```text
P0.1 shared roof catalog
  ↓
P0.2 resolver/schema
  ↓
P0.3 TDE_9 reference migration
  ↓
P0.4 validator + P0.5 tests
  ↓
P0.6 TDE_10/11/12 migration
  ↓
P0.7 index/runtime rebuild
  ↓
P0.8 downstream verification
```

## Done kriteri

- Shared TDE roof catalog complete ve normatif kaynaklı.
- Parent roof component taşıyan hiçbir non-explicit theme outcome efektif boş değil.
- Explicit specialization ve inherited provenance ayrılmış.
- Eski yanlış TDE_9 validation hükmü kaldırılmış.
- TDE_9–12 yeni gate ile yeniden PASS.
- Regression testleri eski bug'ı yakalıyor.
- Derived index/runtime fresh rebuild edilmiş.
- Downstream paketler stale değil.
