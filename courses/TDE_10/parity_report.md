# TDE_10 → TDE_9 Bilgi Tabanı Parity Raporu

**Durum:** `FAZ 1-3 PASS / FAZ 4 AUTH-GATED / FAZ 5-13 YENİDEN TÜRETİLDİ / PARITY RELEASE BLOCKED`

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


## 8. Faz 2 uygulama sonucu

Faz 2 tamamlandı. `curriculum_map.json` dört kayıtlı resmî TDE_10 tema PDF snapshot'ından yeniden zenginleştirildi.

- 4/4 tema girişi verbatim + yerel PDF locator kazandı.
- Ders saati, alan becerileri, eğilimler, sosyal-duygusal öğrenme, değerler, okuryazarlık, disiplinler arası ilişkiler ve beceriler arası ilişkiler verbatim + locator kazandı.
- İçerik çerçevesi, anahtar kavramlar ve öğrenme kanıtları/ölçme-değerlendirme hükümleri verbatim + locator kazandı.
- 64 parent outcome korunarak tekrar sayıldı.
- Resmî tema snapshot'ında ayrı bir Kavramsal Beceriler alanı yayımlanmadığı durum SOURCE_NOT_APPLICABLE olarak açıkça kaydedildi; veri uydurulmadı.
- TDE_9 süreç alt kodları TDE_10'a kopyalanmadı.

**Faz 2 gate:** `PASS_WITH_SOURCE_NOT_APPLICABLE_EXCEPTIONS`

Sonraki kapı: **Faz 3 — textbook activity semantic/evidence depth parity**.


## 9. Faz 3 uygulama sonucu

Faz 3 tamamlandı. 75 textbook activity kaydı doğrudan yerel resmî ders kitabı PDF sayfa aralıklarıyla yeniden doğrulandı. Her kayda PDF sayfası, ayrıntılı öğrenci eylemi, beklenen ürün/kanıt, sayfa-overlap ile ilişkili form kimlikleri ve source-text hash eklendi. Kaynakta ayrı bir activity başlığı gözlenmeyen kayıtlarda başlık uydurulmadı; `NOT_SEPARATELY_TITLED_IN_SOURCE` kullanıldı.

**Faz 3 gate:** `PASS_75_OF_75_LOCAL_PDF_SOURCE_BACKED`

Sonraki kapı: **Faz 4 — form taxonomy normalization ve 8 EBA DPA hedefinin yapısal çözümü**.


## 10. Faz 4-13 uygulama sonucu

Faz 4 EBA hedef probe sonucunda sekiz resmî DPA bağlantısının tamamı EBA giriş ekranına yönlenmiştir. Bu nedenle hedeflerin gerçek yapısı doğrulanamamış ve `UNRESOLVED` korunmuştur.

Buna rağmen sonraki türetim aşamaları fail-closed olarak tamamlanmıştır:

- 35 form structure-first kuralıyla yeniden normalize edildi; TDE_9 referans taxonomy ilişkisi açıkça kaydedildi.
- 4 tema x 16 outcome = 64 outcome-level `needs.json` kaydı üretildi.
- 64 resource plan need-first olarak yeniden türetildi; coverage önceden varsayılmadı.
- 64 alignment row yeniden oluşturuldu: 56 `COVERED`, 8 `PARTIALLY_COVERED`, 0 `NOT_COVERED`.
- Sekiz partial row yalnız konuşma/yazma `.4` outcome'larıdır ve nedeni EBA DPA hedeflerinin authentication-gated olmasıdır.
- Gap analizi: 0 confirmed required gap, 8 unresolved assessment target. Bu sekiz kayıt artifact üretimine yetki vermez.
- Cross-theme audit dört konuşma ve dört yazma assessment ihtiyacını ayrı iki provisional cluster altında gerçekten karşılaştırır.
- Production manifest artık `REUSE_ONLY` olarak parity-certified değildir; `PARITY_REVIEW_BLOCKED` durumundadır.

**Önemli:** Bu aşamada `0 confirmed gap` vardır fakat `0 required artifact` henüz parity-certified değildir. Sekiz EBA hedefi görülmeden Faz 4 ve Faz 9 kapanamaz.

Sonraki uygulanabilir faz: **Faz 14 — TDE_9 eşdeğer bütünlük/validation raporu**. Faz 15 P0/regresyon testleri, Faz 14 sonrasında çalıştırılacaktır.
