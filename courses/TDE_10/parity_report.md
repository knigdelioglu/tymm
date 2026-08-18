# TDE_10 → TDE_9 Bilgi Tabanı Parity Raporu

**Durum:** `FAZ 1 TAMAMLANDI / PARITY RELEASE BLOCKED`

Bu raporun amacı 10. sınıf verisini 9. sınıfla içerik olarak aynılaştırmak değil; **aynı kaynak sadakati, aynı doğrulama derinliği, aynı outcome-level izlenebilirlik ve aynı assessment/gap karar güvenilirliği seviyesine çıkarmaktır.**

Canonical sözleşme: `courses/TDE_10/parity_contract.json`

## 1. Referans implementation

`courses/TDE_9/` doğrulama derinliği açısından referans implementation kabul edilmiştir.

Bu şu anlama gelmez:

- 9. sınıfın süreç bileşenleri 10. sınıfa kopyalanmaz.
- 9. sınıfın sayfa numaraları, etkinlikleri veya form yapıları 10. sınıf verisi sayılmaz.
- 9. sınıftaki 7 gap / 3 artifact sonucu 10. sınıf için hedef değildir.

Referans alınan şey **kanıt standardıdır**.

## 2. Alan sınıfları

### REQUIRED_PARITY

TDE_10 aşağıdaki alanlarda TDE_9 seviyesinde kanıt taşımadan parity PASS alamaz:

- curriculum tema kimliği ve locator
- tema girişinin resmî verbatim metni
- ders saati verbatim + locator
- alan becerileri
- kavramsal beceriler
- eğilimler
- sosyal-duygusal öğrenme becerileri
- değerler
- okuryazarlık becerileri
- disiplinler arası ilişkiler
- beceriler arası ilişkiler
- içerik çerçevesi
- anahtar kavramlar
- öğrenme kanıtları / ölçme-değerlendirme hükümleri
- resmî assessment araçları ve performans görevleri
- 64 öğrenme çıktısı için verbatim + locator
- textbook section/activity/form izlenebilirliği
- outcome-level need → resource plan → alignment → gap zinciri
- aynı coverage semantiği
- gerçek cross-theme assessment/support karşılaştırması

### SOURCE_NOT_APPLICABLE

Aşağıdaki farklılıklar parity hatası değildir:

- Resmî TDE_10 snapshot'larında açık `TDE*.x.y` alt süreç kodu yayımlanmamışsa bu kodların boş kalması.
- TDE_9'a özgü sayfa numaraları ve dosya isimlerinin TDE_10'da bulunmaması.
- TDE_10 artifact sayısının TDE_9 ile aynı olmaması.

### TDE10_SPECIFIC_EXTENSION

TDE_10'un kendi kaynağına özgü şu alanlar korunur:

- multi-part official curriculum snapshot bundle
- local official textbook PDF primary snapshot
- official web cross-check
- stable entity keys
- process-component representation policy
- 43 + 2 tema dış zaman modeli
- EBA DPA target URL kayıtları

## 3. Faz 1 denetim sonucu

| Alan | Durum |
|---|---|
| 64 parent outcome verbatim | PASS |
| Curriculum effective-schema parity | FAIL |
| Curriculum bağlam verbatim derinliği | FAIL |
| 24 textbook section | PASS |
| 75 textbook activity envanteri | PASS |
| Activity semantic/evidence depth | FAIL |
| Structure-not-title form kuralı | PASS |
| TDE_9 canonical taxonomy parity | FAIL |
| 8 EBA DPA target structure | REVIEW_REQUIRED |
| need/resource/alignment/gap ID zinciri | PASS |
| Outcome-level need granularity | FAIL |
| Coverage criterion parity | FAIL |
| Cross-theme assessment comparison | FAIL |
| Zero-gap parity certification | WITHHELD |
| Zero-artifact production manifest semantics | PASS |

## 4. Fail-closed kararı

Mevcut TDE_10 teknik P0 sonucu silinmemiştir; ancak bundan sonra şu şekilde yorumlanacaktır:

`TECHNICAL_P0_PASS_NOT_PARITY_CERTIFICATION`

Özellikle aşağıdaki sekiz assessment hedefinin iç yapısı doğrulanmadan `0 verified gap` parity sonucu FROZEN kabul edilmeyecektir:

1. Tema 1 konuşma DPA
2. Tema 1 yazma DPA
3. Tema 2 konuşma DPA
4. Tema 2 yazma DPA
5. Tema 3 konuşma DPA
6. Tema 3 yazma DPA
7. Tema 4 konuşma DPA
8. Tema 4 yazma DPA

Bağlantının resmî PDF içinde bulunması **resource existence** kanıtıdır. Hedefin analitik rubrik, rating scale veya başka bir değerlendirme yapısı olduğu ayrıca doğrulanmalıdır.

## 5. Coverage karar standardı

### COVERED

Yalnızca gerekli öğrenci eylemi, beklenen kanıt, programın normatif assessment/support gereksinimi ve gerekli değerlendirme aracı doğrulanmışsa verilir.

### PARTIALLY_COVERED

Öğretim yolu mevcut fakat zorunlu assessment, feedback, evidence veya support bileşeni eksik ya da yapısal olarak unresolved ise verilir.

### NOT_COVERED

Programın beklediği temel öğrenme eylemi veya zorunlu kaynak yolu kitapta yoksa verilir.

### Kritik kural

`UNRESOLVED ≠ COVERED`

## 6. Sonraki kapı — Faz 2

Faz 2'de `curriculum_map.json` yeniden parity denetimine alınacaktır. Hedef:

1. TDE_9'da verbatim + locator bulunan fakat TDE_10'da yalnız summary/codes/items biçiminde bulunan alanları resmî 10. sınıf snapshot'larından tamamlamak.
2. Resmî kaynakta olmayan hiçbir alanı uydurmamak.
3. 64 outcome'u değiştirmeden tema/program bağlamını aynı denetlenebilirlik seviyesine çıkarmak.
4. Faz 2 PASS olmadan textbook/assessment sonuçlarını yeniden FROZEN saymamak.

## 7. Parity tamamlanma tanımı

TDE_10 ancak aşağıdaki koşulların tümü sağlandığında TDE_9 seviyesi kabul edilecektir:

- REQUIRED_PARITY alanlarının tamamı doğrulandı.
- Kaynakta bulunmayan alanların tamamı SOURCE_NOT_APPLICABLE olarak kanıtlandı.
- 75 activity TDE_9 seviyesinde öğrenci eylemi ve evidence derinliği taşıyor.
- 35 form yapısal olarak doğrulandı.
- Sekiz EBA DPA hedefinin yapısı çözüldü.
- 64 outcome için coverage yeniden türetildi.
- Gerçek cross-theme assessment consolidation yapıldı.
- Production kararı bu yeni analizden yeniden üretildi.
- Final P0 ve TDE_9 regresyonu geçti.
