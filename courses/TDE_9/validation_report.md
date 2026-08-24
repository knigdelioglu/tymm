# TDE_9 Canonical Validation Report

**Ders / sınıf:** Türk Dili ve Edebiyatı 9. Sınıf (`TDE_9`)  
**Son düzeltme:** 24 Ağustos 2026  
**Durum:** `FULL_PASS__PROCESS_COMPONENT_INHERITANCE_MIGRATION_COMPLETE`

## Kritik düzeltme

14 Ağustos 2026 tarihli önceki doğrulama raporundaki aşağıdaki hüküm **geri çekilmiştir**:

> Tema 2, 3 ve 4'te `process_components_verbatim: []` olması MEB program yapısından kaynaklanmaktadır ve bu nedenle eksiksizdir.

Bu yorum yanlıştı. Resmî 2024 Türk Dili ve Edebiyatı Dersi Öğretim Programının ortak bölümünde alan/bütünleşik becerilerin süreç bileşenlerinin bütün kademelerde kullanılması gerektiği ve çatı öğrenme çıktılarının aynı süreç bileşenlerinin her tema altında tekrar edilmesinden doğacak karmaşayı önlemek amacıyla tanımlandığı açıklanır.

Dolayısıyla tema kaydında subordinate süreç bileşenlerinin tekrar edilmemesi **effective süreç bileşeni yokluğu değildir**.

## Canonical model

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

`curriculum_map.json` içindeki legacy `process_components_verbatim` alanı migration boyunca **tema-spesifik explicit veri alanı** olarak yorumlanır. Bu alanın `[]` olması hiçbir tüketici tarafından effective empty olarak yorumlanamaz.

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
| Structural error | 0 |

Tema 1'de explicit override taşıyan iki kayıt:

- `TDE9_T1_D2` / `TDE1.2`: 4 tema-spesifik süreç bileşeni
- `TDE9_T1_O2` / `TDE2.2`: 5 tema-spesifik süreç bileşeni

Diğer 52 outcome effective süreç bileşenlerini `TDE_2024_ROOF_PROCESS_COMPONENTS` kataloğundan inherit eder.

## Derived index sonucu

Fresh knowledge index yeniden üretilmiştir.

- `courses/TDE_9/index/index_manifest.json`
- index schema: `2.1`
- build status: `SUCCESS`
- indexed record count: `595`
- `process_component` entity type indexe dahildir
- `curriculum_process_component_resolution.json` index fingerprint'ine dahildir
- `../TDE_SHARED/curriculum_process_component_catalog.json` index fingerprint'ine dahildir
- process-component canonical originleri index kayıtlarında `roof_inherited` / `theme_explicit` olarak korunur

P0 report içindeki effective process-component kayıt dağılımı:

- roof-inherited subordinate process-component record: `228`
- theme-explicit subordinate process-component record: `9`

Bu sayılar outcome sayısı değil, indexe yazılmış subordinate process-component entity sayılarıdır.

## Runtime sonucu

Fresh runtime package yeniden üretilmiş ve yayımlanmıştır.

- `runtime_package_version`: `1.2.0`
- `compiler_version`: `1.2.0`
- `validation_status`: `PASS`
- `process_component_resolution_status`: `PASS`
- total outcomes: `54`
- explicit outcome: `2`
- inherited outcome: `52`
- unresolved outcome: `0`
- inheritance missing: `0`
- structural error: `0`

Runtime canonical fingerprint'i hem shared roof catalogu hem de TDE_9 resolution contract'ını kapsar. Bu kaynaklardan biri değişirse mevcut runtime fresh kabul edilmez.

## P0 production gate sonucu

`courses/TDE_9/index/p0_gate_report.json` sonucu:

- index rebuild: `INDEX_FRESH`
- production schema: `1.1`
- canonical assessment artifact: `3`
- historical gap alias: `7`
- alias → artifact resolution: `PASS`
- semantic retrieval probes: `PASS`
- stale-index fail-closed gate: `PASS`
- knowledge-conflict fail-closed gate: `PASS`
- final: `PASS`

Duplicate canonical identity regressionında effective inheritance doğrulamasının daha spesifik `DuplicateCanonicalKeyError`ı maskelemesi de düzeltilmiştir. Duplicate identity artık inheritance count validation'dan önce fail eder.

## Cross-grade doğrulama

Aynı shared resolver ve normatif roof catalog ile dört sınıf birlikte yeniden doğrulanmıştır:

| Sınıf | Toplam outcome | Explicit | Inherited | Unresolved | Inheritance missing | Sonuç |
|---|---:|---:|---:|---:|---:|---|
| TDE_9 | 54 | 2 | 52 | 0 | 0 | PASS |
| TDE_10 | 64 | 0 | 64 | 0 | 0 | PASS |
| TDE_11 | 64 | 0 | 64 | 0 | 0 | PASS |
| TDE_12 | 64 | 0 | 64 | 0 | 0 | PASS |

Durable cross-grade kanıtı: `docs/process-component-inheritance-audit.json`.

## Downstream sonucu

ÖğretmenOS curriculum-only TDE_11 ve TDE_12 runtime builder'ında bulunan downstream veri kaybı da düzeltilmiştir.

Önceki builder yalnız tema-level process alanını okuyordu; shared roof + resolution contract paket içinde olmadığı için inherited bileşenler uygulama runtime'ına taşınmıyordu.

Yeni downstream runtime contract:

- shared roof catalog paket dependency'sidir,
- grade-specific resolution contract paket dependency'sidir,
- effective process components runtime SQLite'a yazılır,
- `process_component_origin` runtime SQLite'da korunur,
- shared catalog + resolution contract canonical fingerprint'e katılır,
- TDE_11: 64/64 `ROOF_INHERITED`, `RUNTIME_FRESH`, PASS,
- TDE_12: 64/64 `ROOF_INHERITED`, `RUNTIME_FRESH`, PASS.

Uygulama sunum katmanının provenance originini kullanıcıya ayrıca göstermesi zorunlu canonical blocker değildir; runtime veri katmanı origin bilgisini kaybetmeden taşımaktadır.

## Fail-closed doğrulama

Aşağıdaki dosyalar bu invariantı uygular:

- `skill/tymm-material-planner/scripts/process_component_resolver.py`
- `skill/tymm-material-planner/scripts/p0_process_component_gate.py`
- `skill/tymm-material-planner/scripts/effective_knowledge_index.py`
- `skill/tymm-material-planner/scripts/build_runtime_course_package.py`
- `skill/tymm-material-planner/tests/test_process_component_inheritance.py`
- `skill/tymm-material-planner/tests/test_resolver_runner.py`
- `skill/tymm-material-planner/tests/test_runtime_course_package.py`
- `.github/workflows/tymm-p0-production-gate.yml`
- `.github/workflows/tymm-process-component-inheritance.yml`

Gate şu durumlarda FAIL verir:

- roof family bulunduğu hâlde outcome çözümlenemiyorsa,
- inherited component locator'ı yoksa,
- component parent-prefix ihlali varsa,
- duplicate component code varsa,
- resolution contract ile curriculum outcome seti farklıysa,
- beklenen explicit/inherited origin veya component sayısı değişmişse,
- başka grade/theme verisi inheritance kaynağı olarak kullanılmaya çalışılırsa,
- canonical source fingerprint değişip index/runtime yeniden üretilmemişse,
- duplicate canonical identity varsa.

## Migration kapanış durumu

P0 migration tamamlanmıştır:

1. shared normatif roof catalog: **COMPLETE**
2. explicit/inherited effective resolver: **COMPLETE**
3. TDE_9 canonical migration: **COMPLETE**
4. TDE_10/TDE_11/TDE_12 cross-grade revalidation: **COMPLETE**
5. fail-closed validator: **COMPLETE**
6. regression fixtures: **COMPLETE**
7. knowledge index + runtime fresh rebuild: **COMPLETE**
8. downstream runtime preservation: **COMPLETE**

Bu nedenle önceki `DOWNSTREAM_REBUILD_PENDING` durumu kaldırılmıştır.

## Nihai invariant

> Tema sayfasında subordinate maddelerin tekrar edilmemesi süreç bileşeninin yokluğu değildir. Tema-spesifik explicit tanım yoksa effective süreç bileşenleri resmî shared roof hierarchy'den inherit edilir.
