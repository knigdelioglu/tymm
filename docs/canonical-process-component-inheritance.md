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

## Bilinen mevcut etki

Bu invariant eklenmeden üretilmiş TDE_9, TDE_10, TDE_11 ve TDE_12 canonical verileri süreç bileşeni completeness açısından yeniden denetlenmelidir. Önceki `PASS`/`FROZEN` kararları bu invariantı kontrol etmedikleri sürece süreç bileşeni doğruluğunun kanıtı değildir.

## Uygulama sırası

Düzeltme planı:

`@docs/process-component-inheritance-migration-plan.md`
