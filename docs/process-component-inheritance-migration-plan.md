# Süreç Bileşeni Inheritance Düzeltme Planı

**Kapsam:** `courses/TDE_9`, `courses/TDE_10`, `courses/TDE_11`, `courses/TDE_12` + shared extraction/validation/index/runtime zinciri.

**Temel invariant:** `@docs/canonical-process-component-inheritance.md`

## Hedef

Tema sayfasında tekrar yazılmadığı için kaybolan çatı süreç bileşenlerini resmî öğretim programındaki parent-outcome hiyerarşisinden canonical veriye doğru provenance ile bağlamak; aynı hatanın yeni sınıf/ders bootstraplarında ve validatorlarda tekrar PASS almasını engellemek.

---

## P0 — Canonical doğruluğu geri kazan

### P0.1 — Her sınıf için normatif çatı katalogunu çıkar

Her `TDE_9`–`TDE_12` için yalnız o sınıfın resmî öğretim programından parent outcome → process component hiyerarşisini çıkar.

Önerilen derived/audit yapı:

```text
courses/TDE_<grade>/source_docs/curriculum_process_component_catalog.json
```

Her parent outcome için:

- parent code/verbatim
- component code/verbatim
- normatif source locator
- sınıf/course id
- verification status

TDE_10'daki mevcut `curriculum_process_component_audit.json` başlangıç kanıtı olarak kullanılabilir; ancak `PARTIAL_VERIFIED_NOT_CANONICAL_COMPLETE` durumundaki kayıtlar tamamlanmadan canonical'a promote edilmemeli.

**Acceptance:** ilgili sınıfın programında süreç bileşeni bulunan bütün parent outcome family'leri katalogda; sentetik kod yok; locator eksikliği yok.

### P0.2 — Canonical çözümleme modelini tanımla

Theme outcome için üç kavramı ayır:

1. **explicit** — tema sayfasında doğrudan yayımlanan süreç bileşenleri
2. **inherited** — genel/çatı parent outcome tanımından gelen süreç bileşenleri
3. **effective** — downstream/runtime tarafından kullanılacak çözümlenmiş sonuç

Çözümleme kuralı:

```text
THEME_EXPLICIT varsa
    effective = theme explicit
aksi halde ROOF catalog varsa
    effective = roof inherited
aksi halde
    effective = [] ancak SOURCE_VERIFIED_NONE ise
```

Hem explicit hem roof mevcut olup kod/metin çelişirse `REVIEW_REQUIRED`; sessiz merge yapılmaz.

Schema migration sırasında geriye uyumluluk gerekiyorsa mevcut `process_components_verbatim` effective projection olarak korunabilir; provenance ayrı alan/obje ile eklenmelidir.

**Acceptance:** inherited veri “tema sayfasından verbatim alınmış” gibi yanlış provenance taşımaz.

### P0.3 — TDE_9 canonical migration

Önce TDE_9 ile referans migration yap:

- 54 outcome'un tamamını parent-code bazında katalogla eşleştir.
- Mevcut dolu tema-spesifik kayıtları koru ve explicit olarak işaretle.
- Çatı bileşenlerine sahip olduğu hâlde `[]` kalan outcome'ları inherit et.
- source locatorları çatı ve tema kaynaklarını ayıracak şekilde düzelt.
- `validation_report.md` içindeki “Tema 2, 3 ve 4'te boş olması MEB program yapısından kaynaklanmaktadır” kararını kaldır/düzelt.

**Acceptance:** roof component taşıyan hiçbir TDE_9 outcome efektif olarak boş değil; validation yeni invariant ile PASS.

### P0.4 — TDE_10, TDE_11, TDE_12 migration

TDE_9 referans migrationı yeşil olduktan sonra aynı generic resolver ile diğer sınıfları migrate et.

- TDE_10 partial audit tamamlanır ve normatif kaynakla kapatılır.
- TDE_11 ve TDE_12 mevcut `PASS` raporları yeni completeness metriği ile yeniden üretilir.
- Sınıflar arası içerik kopyalanmaz; yalnız shared resolver/schema kullanılır.

**Acceptance:** 9–12 tüm sınıflarda explicit/inherited/effective sayıları raporlanır ve roof→theme orphan kalmaz.

---

## P0 — Hatanın yeniden PASS almasını engelle

### P0.5 — Shared validator/gate ekle

Generic validation kuralı:

```text
roof_catalog[parent_code].components > 0
AND effective(theme_outcome).components == 0
=> PROCESS_COMPONENT_INHERITANCE_MISSING
=> FAIL
```

Ek kontroller:

- inherited component source locator zorunlu
- component code parent prefix uyumu
- duplicate component code fail
- theme/roof conflict fail-closed
- canonical field boş ama roof doluysa freeze/publish yasak
- yalnız explicit bileşen sayısına bakarak completeness PASS verilemez

Bu kontrol hem curriculum-only hem full-course P0 gate'e bağlanmalı.

**Acceptance:** eski hatalı fixture/test verisi bilerek verildiğinde CI kırılıyor.

### P0.6 — Regression testleri

En az şu fixture'lar:

1. tema explicit yok + roof var → inherited PASS
2. tema explicit var + roof var → explicit PASS
3. roof var + effective `[]` → FAIL
4. roof yok ve resmî olarak none doğrulanmış → `[]` PASS
5. theme/roof code conflict → REVIEW_REQUIRED/FAIL
6. inherited kayıtta locator yok → FAIL
7. başka grade kataloğundan component sızması → FAIL

TDE_9'daki mevcut problem ayrıca gerçek veri regression fixture'ı olmalı.

---

## P0 — Derived katmanları yeniden üret

### P0.7 — Index ve runtime rebuild

Canonical migration tamamlandıktan sonra:

- `knowledge.sqlite` / knowledge index
- course runtime SQLite
- runtime manifests/fingerprints
- ilgili generated package/projectionlar

fresh rebuild edilir.

`build_runtime_course_package.py` mevcut canonical `process_components_verbatim` alanını doğrudan runtime'a taşıdığı için stale runtime bırakılmamalıdır.

**Acceptance:** runtime outcome kayıtlarının effective process component içeriği canonical ile birebir; fingerprint canonical son durumunu gösteriyor.

### P0.8 — Downstream tüketici doğrulaması

ÖğretmenOS veya başka tüketicilere giden paketlerde:

- süreç bileşeni alanlarının doluluk/origin kontrolü
- inherited bileşenlerin UI/API'de yanlışlıkla “tema sayfasında açıkça yazıyor” şeklinde sunulmaması
- boş diziyi gizleyen UI workaround yapılmaması

**Acceptance:** downstream yalnız düzeltilmiş runtime/package kullanıyor.

---

## P1 — Şema ve gözlemlenebilirlik iyileştirmesi

### P1.1 — Completeness metrikleri

Her course validation raporu en az şunları vermeli:

- total outcomes
- outcomes_with_roof_components
- explicit_component_outcomes
- inherited_component_outcomes
- verified_no_component_outcomes
- unresolved_component_outcomes
- inheritance_missing_count
- conflict_count

`PASS` için `inheritance_missing_count = 0` ve `conflict_count = 0` zorunlu.

### P1.2 — Source authority modeli

Normatif TYMM öğretim programı ile OGM vb. destekleyici MEB kaynaklarını şemada ayır:

- `NORMATIVE_CURRICULUM`
- `SUPPORTING_MEB_CROSSCHECK`

Destekleyici kaynak canonical wording'i tek başına değiştiremez.

### P1.3 — Bootstrap prompt hardening

Aşağıdaki promptlarda inheritance invariant zorunlu referans olmalı:

- `docs/yeni-ders-sinif-bootstrap-promptu.md`
- `docs/yalniz-ogretim-programi-bootstrap-promptu.md`
- ileride canonical curriculum çıkaran tüm prompt/workflowlar

---

## Önerilen uygulama sırası

```text
P0.1 roof catalogs
  ↓
P0.2 resolver/schema
  ↓
P0.3 TDE_9 reference migration
  ↓
P0.5 validator + P0.6 tests
  ↓
P0.4 TDE_10/11/12 migration
  ↓
P0.7 index/runtime rebuild
  ↓
P0.8 downstream verification
  ↓
P1 metrics/authority cleanup
```

## Done kriteri

Bu iş ancak aşağıdakilerin tamamı sağlandığında bitmiş sayılır:

- TDE_9–12 için normatif roof component katalogları tam ve kaynaklı.
- Parent roof component taşıyan hiçbir theme outcome efektif `[]` değil.
- Explicit ve inherited provenance ayrılmış.
- Eski yanlış TDE_9 validation hükmü kaldırılmış.
- 9–12 validation raporları yeni gate ile yeniden PASS.
- Regression testleri eski bug'ı yakalıyor.
- Derived index/runtime fresh rebuild edilmiş.
- Downstream paketler stale değil.
