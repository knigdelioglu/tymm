# Canonical Süreç Bileşeni Inheritance Kuralı

> **Kritik canonical invariant — tüm ders/sınıf bootstrap, extraction, validation, index ve runtime akışlarında zorunludur.**

## Problem

TYMM programlarında bazı alan becerileri için süreç bileşenleri her tema altında tekrar yazılmayabilir. Programın genel/çatı bölümünde tanımlanan bir `TDE*.x` öğrenme çıktısının süreç bileşenlerinin tema sayfasında tekrar edilmemesi, o tema için süreç bileşeni bulunmadığı anlamına gelmez.

Aşağıdaki varsayım **yasaktır**:

> Tema/ünite sayfasında alt süreç maddeleri görünmüyorsa `process_components_verbatim: []` yaz.

Bu varsayım canonical knowledge kaybına yol açar.

## Zorunlu yorum

Bir tema/ünite içindeki parent outcome (`TDE1.1`, `TDE2.1`, `TDE3.1`, `TDE4.1` vb.) için süreç bileşenleri çözülürken:

1. Önce aynı outcome için tema/üniteye özgü, açıkça yayımlanmış süreç bileşenleri aranır.
2. Tema/üniteye özgü süreç bileşenleri yoksa, resmî programın genel/çatı bölümünde aynı parent outcome altında tanımlanan süreç bileşenleri **inherit edilir**.
3. Çatı tanımı varken tema kaydının efektif süreç bileşeni boş bırakılamaz.
4. `[]` yalnız resmî kaynakta parent outcome için gerçekten süreç bileşeni bulunmadığı doğrulanmışsa kullanılabilir.
5. Tema-spesifik tanım ile çatı tanımı arasında kod/metin çatışması varsa sessiz merge/override yapılmaz; kayıt `REVIEW_REQUIRED` olur.
6. Başka sınıftan, destekleyici materyalden veya model bilgisinden süreç bileşeni uydurulmaz. Normatif kaynak her zaman ilgili sınıfın resmî öğretim programıdır; destekleyici MEB kaynakları yalnız çapraz doğrulama için kullanılabilir.

## Provenance zorunluluğu

Inheritance, kaynak bilgisini kaybetmemelidir. Her efektif süreç bileşeni en az şunları taşımalıdır:

- `component_code`
- `component_verbatim`
- `source_locator`
- `resolution_origin`: `THEME_EXPLICIT` | `ROOF_INHERITED`
- `verification_status`

Mevcut şema tek bir `process_components_verbatim` alanı kullanıyorsa migration tamamlanana kadar bu alanın yanında inheritance/provenance bilgisi tutulmalı; runtime'a boş dizi taşınmamalıdır.

## Fail-closed validation kuralı

Aşağıdaki durum **PASS olamaz**:

```text
parent outcome resmî çatı süreç bileşenlerine sahip
AND
canonical theme outcome effective process component listesi boş
```

Validator bu durumda en az `PROCESS_COMPONENT_INHERITANCE_MISSING` hatası üretmeli ve canonical freeze/runtime publish engellenmelidir.

Ayrıca yalnız tema sayfalarında açıkça tekrar edilen bileşenleri saymak, “explicit process component completeness” ölçümü değildir. Doğrulama hem **explicit** hem **inherited/effective** kapsamı ayrı ayrı raporlamalıdır.

## Bilinen mevcut etki

Bu invariant eklenmeden üretilmiş TDE_9, TDE_10, TDE_11 ve TDE_12 canonical verileri süreç bileşeni completeness açısından yeniden denetlenmelidir. Önceki `PASS`/`FROZEN` kararları, bu invariantı kontrol etmedikleri sürece süreç bileşeni doğruluğunun kanıtı sayılmaz.

## Uygulama sırası

Düzeltme planı için:

`@docs/process-component-inheritance-migration-plan.md`

kullanılmalıdır.
