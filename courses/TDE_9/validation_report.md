# TDE_9 Canonical Validation Report

**Ders / sınıf:** Türk Dili ve Edebiyatı 9. Sınıf (`TDE_9`)  
**Son düzeltme:** 24 Ağustos 2026  
**Durum:** `CANONICAL_PROCESS_COMPONENT_RESOLUTION_PASS__DOWNSTREAM_REBUILD_PENDING`

## Kritik düzeltme

14 Ağustos 2026 tarihli önceki doğrulama raporundaki aşağıdaki hüküm **geri çekilmiştir**:

> Tema 2, 3 ve 4'te `process_components_verbatim: []` olması MEB program yapısından kaynaklanmaktadır ve bu nedenle eksiksizdir.

Bu yorum yanlıştı. Resmî 2024 Türk Dili ve Edebiyatı Dersi Öğretim Programının ortak bölümünde alan/bütünleşik becerilerin süreç bileşenlerinin bütün kademelerde kullanılması gerektiği ve çatı öğrenme çıktılarının aynı süreç bileşenlerinin her tema altında tekrar edilmesinden doğacak karmaşayı önlemek amacıyla tanımlandığı açıklanır.

Dolayısıyla tema kaydında subordinate süreç bileşenlerinin tekrar edilmemesi **effective süreç bileşeni yokluğu değildir**.

## Yeni canonical model

Süreç bileşeni bilgisi normalize edilmiş iki katmanlı canonical model olarak çözülür:

1. `courses/TDE_SHARED/curriculum_process_component_catalog.json`
   - course-wide normatif roof hierarchy
   - 16 parent outcome family
   - 66 subordinate process component
   - 9, 10, 11 ve 12. sınıflarda uygulanabilir

2. `courses/TDE_9/curriculum_process_component_resolution.json`
   - TDE_9 outcome → explicit/inherited resolution contract
   - tema-spesifik explicit override'ları korur
   - geri kalan outcome'ları shared roof hierarchy'ye bağlar

`curriculum_map.json` içindeki legacy `process_components_verbatim` alanı migration boyunca **tema-spesifik explicit veri alanı** olarak yorumlanır. Bu alanın `[]` olması artık hiçbir tüketici tarafından effective empty olarak yorumlanamaz.

## Resolution precedence

```text
verified THEME_EXPLICIT varsa
    effective = THEME_EXPLICIT
aksi halde shared ROOF varsa
    effective = ROOF_INHERITED
aksi halde SOURCE_VERIFIED_NONE varsa
    effective = []
aksi halde
    FAIL / PROCESS_COMPONENT_INHERITANCE_MISSING
```

Tema-spesifik explicit set ile roof set merge edilmez. Resmî tema specialization'ı aynı subordinate kodu roof'tan farklı bağlamsal ifadeyle kullanabilir; bu tek başına conflict değildir.

## TDE_9 süreç bileşeni sonucu

| Metrik | Sonuç |
|---|---:|
| Toplam öğrenme çıktısı | 54 |
| Shared roof component family ile eşleşen | 54 |
| Tema-spesifik explicit süreç bileşeni taşıyan outcome | 2 |
| Roof inheritance ile çözülen outcome | 52 |
| `SOURCE_VERIFIED_NONE` | 0 |
| Unresolved | 0 |
| Inheritance missing | 0 |

Tema 1'de explicit override taşıyan iki kayıt:

- `TDE9_T1_D2` / `TDE1.2`: 4 tema-spesifik süreç bileşeni
- `TDE9_T1_O2` / `TDE2.2`: 5 tema-spesifik süreç bileşeni

Diğer 52 outcome effective süreç bileşenlerini `TDE_2024_ROOF_PROCESS_COMPONENTS` kataloğundan inherit eder.

## Fail-closed doğrulama

Aşağıdaki dosyalar bu invariantı uygular:

- `skill/tymm-material-planner/scripts/process_component_resolver.py`
- `skill/tymm-material-planner/scripts/p0_process_component_gate.py`
- `skill/tymm-material-planner/tests/test_process_component_inheritance.py`
- `.github/workflows/tymm-p0-production-gate.yml`

P0 gate şu durumlarda FAIL verir:

- roof family bulunduğu hâlde outcome çözümlenemiyorsa,
- inherited component locator'ı yoksa,
- component parent-prefix ihlali varsa,
- duplicate component code varsa,
- resolution contract ile curriculum outcome seti farklıysa,
- beklenen explicit/inherited origin veya component sayısı değişmişse,
- başka grade/theme verisi inheritance kaynağı olarak kullanılmaya çalışılırsa.

## Önceki rapordan korunan bulgular

Bu düzeltme yalnız süreç bileşenlerinin canonical modellenmesiyle ilgilidir. Önceki rapordaki tema sayısı, outcome sayısı, ders saati, textbook section/activity/form locator ve assessment form sınıflandırması bulguları bu değişiklik nedeniyle kendiliğinden geçersiz sayılmaz. Ancak eski rapor artık **tam canonical validation kanıtı olarak kullanılmamalıdır**; bu dosya onun yerine geçer.

## Kalan P0 iş

Canonical resolution sözleşmesi tamamlanmıştır; ancak migration aşağıdaki derived/downstream katmanlar fresh rebuild edilmeden bitmiş sayılmaz:

1. knowledge index süreç bileşenlerini raw legacy array yerine effective resolver üzerinden almalı,
2. runtime SQLite `outcomes.process_components` effective seti taşımalı,
3. runtime/index fingerprint shared roof catalog + resolution contract değişikliklerini kapsamalı,
4. ÖğretmenOS ve diğer tüketiciler inherited origin bilgisini korumalı,
5. TDE_10, TDE_11 ve TDE_12 aynı shared resolver ile yeniden doğrulanmalı.

Bu nedenle bu raporun genel durumu bilinçli olarak `FULL_PASS` değildir.

## Nihai invariant

> Tema sayfasında subordinate maddelerin tekrar edilmemesi süreç bileşeninin yokluğu değildir. Tema-spesifik explicit tanım yoksa effective süreç bileşenleri resmî shared roof hierarchy'den inherit edilir.
