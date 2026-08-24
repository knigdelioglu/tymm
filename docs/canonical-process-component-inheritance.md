# Canonical Süreç Bileşeni Inheritance Kuralı

> **Kritik canonical invariant — tüm ders/sınıf bootstrap, extraction, validation, index ve runtime akışlarında zorunludur.**

## Problem

TYMM Türk Dili ve Edebiyatı programında alan becerilerinin süreç bileşenleri her tema altında tekrar yazılmaz. Programın genel/çatı bölümünde tanımlanan bir `TDE*.x` çıktısının süreç bileşenlerinin tema sayfasında tekrar edilmemesi, o tema için süreç bileşeni bulunmadığı anlamına gelmez.

Aşağıdaki varsayım **yasaktır**:

> Tema/ünite sayfasında alt süreç maddeleri görünmüyorsa `process_components_verbatim: []` yaz.

Bu varsayım canonical knowledge kaybına yol açar.

## Normatif dayanak

2024 Türk Dili ve Edebiyatı Dersi Öğretim Programı, hazırlık sınıfından itibaren tüm kademelerde ilgili alan/bütünleşik becerilerin süreç bileşenlerinin kullanılmasını zorunlu kılar ve çatı öğrenme çıktılarının aynı süreç bileşenlerinin her temada tekrarından doğacak karmaşayı önlemek amacıyla kullanıldığını açıklar (`s. 19`).

Bu nedenle çatı hiyerarşisi grade-theme verisinden türetilen bir tahmin değil, programın course-wide normatif katmanıdır.

## Zorunlu çözümleme sırası

Bir tema/ünite içindeki parent outcome (`TDE1.1`, `TDE2.1`, `TDE3.1`, `TDE4.1` vb.) için süreç bileşenleri şu sırayla çözülür:

1. Aynı outcome için tema/üniteye özgü ve resmî kaynakta açıkça yayımlanmış süreç bileşenleri varsa **tema-spesifik explicit tanım kullanılır**.
2. Tema/üniteye özgü explicit süreç bileşeni yoksa, resmî programın ortak/çatı bölümündeki aynı parent outcome süreç bileşenleri **inherit edilir**.
3. Çatı tanımı varken ve tema-spesifik override yokken efektif süreç bileşeni boş bırakılamaz.
4. `[]` yalnız normatif kaynak parent outcome için gerçekten süreç bileşeni olmadığını açıkça doğruluyorsa kullanılabilir.

## Tema-spesifik specialization bir conflict değildir

Tema-spesifik süreç bileşenleri aynı subordinate kodu (`TDE*.x.y`) çatıdaki genel semantikten daha özel, tema bağlamına uyarlanmış bir ifadeyle kullanabilir. Bu, resmî kaynakla doğrulanmışsa normal bir specialization/override davranışıdır.

Dolayısıyla:

```text
verified THEME_EXPLICIT varsa
    effective = THEME_EXPLICIT
aksi halde ROOF varsa
    effective = ROOF_INHERITED
aksi halde verified-none varsa
    effective = []
aksi halde
    unresolved/fail
```

Tema-spesifik set ile roof set sessizce birleştirilmez. Roof'taki eksik görünen maddeler explicit tema setine otomatik eklenmez.

Gerçek conflict; aynı scope içinde iki ayrı resmî kayıt, aynı canonical anahtar için uzlaştırılamayan iki farklı gerçek iddia oluşturduğunda söz konusudur. Yalnız roof ile verified theme specialization arasındaki metin farkı conflict değildir.

## Shared roof catalog

TDE çatı süreç bileşenleri 9, 10, 11 ve 12 için dört kez kopyalanmamalıdır. Tek course-wide canonical katalog kullanılmalıdır:

`courses/TDE_SHARED/curriculum_process_component_catalog.json`

Grade/theme curriculum map'leri kendi explicit tanımlarını taşır; inheritance yalnız bu shared normatif katalogdan yapılır.

Başka bir sınıfın tema verisi inheritance kaynağı olamaz.

## Provenance zorunluluğu

Her efektif süreç bileşeni en az şunları çözebilmelidir:

- `component_code`
- `component_title_verbatim`
- `source_locator`
- `resolution_origin`: `THEME_EXPLICIT` | `ROOF_INHERITED`
- `verification_status`

Tema-spesifik explicit kayıtta source locator tema sayfasına; inherited kayıtta source locator shared roof kataloğundaki genel program sayfasına işaret eder.

Mevcut şema yalnız `process_components_verbatim` alanını kullanıyorsa migration sırasında explicit/inherited/effective katmanları ayrıştırılmalı; provenance kaybedilmemelidir.

## Fail-closed validation kuralı

Aşağıdaki durum **PASS olamaz**:

```text
THEME_EXPLICIT yok
AND shared roof catalog[parent_code].components > 0
AND effective(theme_outcome).components == 0
```

Validator bu durumda en az `PROCESS_COMPONENT_INHERITANCE_MISSING` üretmeli ve canonical freeze/runtime publish engellenmelidir.

Ayrıca yalnız tema sayfasında explicit yayımlanan bileşenleri saymak completeness ölçümü değildir. Doğrulama **explicit**, **inherited** ve **effective** kapsamı ayrı raporlamalıdır.

## 24 Ağustos 2026 yeniden doğrulama ve kapanış notu

Süreç bileşeni hatası canonical, index, runtime ve downstream katmanlarında yeniden kontrol edilmiştir. Kontrol sırasında mevcut canonical source setinin cross-grade audit sonrasından beri değişmediği doğrulanmış; 9–12. sınıf sonuçları yeniden karşılaştırılmıştır.

Doğrulanan sonuçlar:

- `TDE_9`: 54 outcome; 2 `THEME_EXPLICIT`, 52 `ROOF_INHERITED`, 0 unresolved, 0 inheritance missing, 0 structural error.
- `TDE_10`: 64 outcome; 0 explicit, 64 `ROOF_INHERITED`, 0 unresolved, 0 inheritance missing, 0 structural error.
- `TDE_11`: 64 outcome; 0 explicit, 64 `ROOF_INHERITED`, 0 unresolved, 0 inheritance missing, 0 structural error.
- `TDE_12`: 64 outcome; 0 explicit, 64 `ROOF_INHERITED`, 0 unresolved, 0 inheritance missing, 0 structural error.
- TDE_9 ve TDE_10 P0 gate sonuçları `PASS`; knowledge indexleri fresh ve shared roof catalog + grade resolution contract fingerprintlerini taşıyor.
- TDE_9/TDE_10 runtime paketleri `1.2.0`; effective süreç bileşenleri ve inheritance sayımları runtime manifestine projekte edilmiş durumda.
- TDE_11/TDE_12 curriculum validation raporları inheritance completeness metriklerini açıkça taşıyor.
- ÖğretmenOS TDE_11/TDE_12 curriculum-only runtime paketleri `1.2.0`, `64/64 ROOF_INHERITED`, `RUNTIME_FRESH`, `PASS`; `process_component_origin` downstream runtime'da korunuyor.

Yeniden kontrolde ayrıca bir **tekrar riski** tespit edilmiştir: tarihsel `knowledge_index.py` motoru raw `process_components_verbatim` alanını okuyordu. Onaylı CI/build yolu zaten `effective_knowledge_index.py` kullanıyordu; ancak manuel legacy rebuild eski hatayı yeniden üretebilirdi. Bu yol da kapatılmıştır:

- tarihsel motor `_knowledge_index_legacy.py` altında internal implementation olarak tutulur,
- public `knowledge_index.py` compatibility facade'dır,
- `curriculum_process_component_resolution.json` bulunan bir kursta raw extractor veya raw build/rebuild çağrısı `PROCESS_COMPONENT_EFFECTIVE_INDEX_REQUIRED` ile fail-closed olur,
- effective build yolu internal motoru yalnız `effective_knowledge_index.py` üzerinden, shared roof projection uygulanmış halde kullanır,
- regression testi raw legacy rebuild/extraction'ın contract bulunan kursta başarısız olmasını zorunlu kılar.

Bu nedenle mevcut onaylı veri ve build zincirinde başlangıçtaki "tema sayfasında tekrar yoksa süreç bileşeni yoktur" hatası için açık bir yol bırakılmamalıdır.

## Bundan sonra dikkat edilmesi gerekenler

1. **`process_components_verbatim` effective veri değildir.** Resolution contract bulunan kursta bu alan yalnız tema-spesifik explicit katman olarak yorumlanmalıdır.
2. **Index build/rebuild için `effective_knowledge_index.py` kullan.** `knowledge_index.py` contract bulunan kursta rebuild amacıyla kullanılmamalı ve fail-closed kalmalıdır.
3. **Shared roof catalog tek normatif kaynaktır.** Başka grade/theme kaydından süreç bileşeni kopyalanmamalı veya inference yapılmamalıdır.
4. **Explicit override roof ile merge edilmez.** Verified `THEME_EXPLICIT` varsa o outcome için effective set explicit settir.
5. **Boş effective set varsayılan değildir.** Yalnız `SOURCE_VERIFIED_NONE` resmî kaynakla açıkça kanıtlanırsa `[]` kabul edilebilir.
6. **Her canonical değişiklikte inheritance gate tekrar çalışmalıdır.** Shared catalog, curriculum map veya resolution contract değişirse index/runtime stale sayılmalı ve fresh rebuild yapılmalıdır.
7. **Fingerprint zinciri korunmalıdır.** Index ve runtime manifestleri hem grade resolution contract'ı hem `../TDE_SHARED/curriculum_process_component_catalog.json` hashini taşımalıdır.
8. **Downstream origin kaybolmamalıdır.** SQLite/API/UI katmanları `THEME_EXPLICIT` ve `ROOF_INHERITED` provenance bilgisini korumalıdır.
9. **Yeni ders/sınıf bootstraplarında bu invariant ilk günden uygulanmalıdır.** Sonradan boş dizileri düzeltmeye dayalı migration normal çalışma biçimi olmamalıdır.
10. **PASS yalnız sayısal completeness ile verilmelidir.** `inheritance_missing_count = 0`, `unresolved_component_outcomes = 0`, `structural_error_count = 0` zorunlu kalmalıdır.

## Bilinen mevcut durum

TDE_9, TDE_10, TDE_11 ve TDE_12 süreç bileşeni completeness açısından yeni invariant ile yeniden doğrulanmıştır. Eski invariant öncesi `PASS`/`FROZEN` kararları tarihsel kanıt olarak kullanılmamalı; güncel cross-grade audit, grade validation/P0 raporları ve fresh runtime/index manifestleri esas alınmalıdır.

## Uygulama sırası

Düzeltme ve kapanış ayrıntıları:

`@docs/process-component-inheritance-migration-plan.md`
