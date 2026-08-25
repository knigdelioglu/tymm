# Benim Mekânım Sonrası: Akran, Öz ve Öğretmen Geri Bildirimini Kanıta Dönüştürmek

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_9` |
| Tema | `TEMA_03` |
| Blok | `BLOCK_T3_02_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

10 saatlik 3. Tema Konuşma Atölyesi bloğunun 7. ve 8. ders saatlerinde, P03'te sınıf mevcudu nedeniyle tamamlanmamış canlı sunumlar varsa önce bunlar bitirilir. Ardından T3_ACT_09_KONUSMA_SONRASI kapsamında öğrenciler konuşma ürününü kişisel beğeniyle değil gözlenebilir sunum kanıtlarıyla değerlendirir: önce akran değerlendirmesi yapılır, sonra öğrenci akran görüşünü dikkate alarak öz değerlendirme formunu doldurur; öğretmen genel gözlem formu ile approved TDE9_KONUSMA_RUBRIC kanıtlarını geri bildirim olarak sürece ekler. Saat sonunda her öğrenci P05 için tek, somut ve yeniden performansta gözlenebilir bir iyileştirme hedefi seçer.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.4`
- **Kullanılan etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`, `T3_ACT_09_KONUSMA_SONRASI`
- **Kullanılan formlar:** `FORM_BOB_06_T3_KONUSMA_OZ`, `FORM_BOB_10_T3_T4_AKRAN`, `FORM_BOB_11_GENEL_GOZLEM`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_BOB_06_T3_KONUSMA_OZ` | `USED` |
| `FORM_BOB_10_T3_T4_AKRAN` | `USED` |
| `FORM_BOB_11_GENEL_GOZLEM` | `USED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE9_KONUSMA_RUBRIC` | `MAT_T3_KONUSMA_RUBRIC` | `USED` |

### Kaynak plan referansları

| Kaynak planı | Kullanım |
|---|---|
| `RES_T3_05_KONUSMA_RUBRIC` | `USED` |

## Kalabalık sınıf rotası

- **Mod:** `PARALLEL_GROUPS`
- **Aktivasyon:** Tek sıra canlı performans rotası mevcut ders saatinde tüm öğrenciler için güvenilir biçimde tamamlanamıyorsa kullan.
- **Uygulandığı dersler:** `1`
- **Paralel grup sayısı:** 5
- **Gruplama:** Sınıfı 4-6 kişilik paralel performans gruplarına ayır; konuşmacı ve gözlemci rollerini her turda döndür, hiçbir öğrenciyi yalnız gözlemci rolünde bırakma.
- **Öğretmen rotasyonu:** Öğretmen gruplar arasında planlı olarak döner; her öğrenciden en az bir doğrudan performans kanıtı toplar ve diğer kanıtları akran kayıtlarıyla çapraz kontrol eder.
- **Akran gözlemci:** Her gruptaki akran gözlemci yalnız plandaki mevcut performans ölçütlerinden bir güçlü davranış ve bir geliştirme kanıtı kaydeder; kişilik veya genel beğeni yorumu yapmaz.
- **Performans zaman sınırı:** 90 saniye
- **Kanıt eşdeğerliği:** Standart sınıf rotasındaki aynı etkinlik, öğrenme çıktıları, performans ölçütleri ve öğrenci kanıtları korunur; yalnız yürütme paralelleştirilir ve öğretmen gözlemi rotasyonla örneklenir.
- **Çekirdek saat okul-temelli uzatmadan bağımsız:** Evet
- **Opsiyonel okul-temelli uzatma:** Evet
- **Opsiyonel uzatma amacı:** Yalnız hedefli ek prova veya kısa yeniden performans için kullanılabilir; çekirdek paketin tamamlanması okul-temelli saate bağlı değildir.

## Sınıf uyarlamaları

- **Tetikleyiciler:** `LIVE_PERFORMANCE`
- **Gerekçe:** Bu paket LIVE_PERFORMANCE sinyali taşıdığı için farklılaştırma ve erişilebilirlik rotası first-class olarak tutulur; destek, öğrenme çıktısını veya beklenen kanıtı azaltmaz.
- **Kanıt eşdeğerliği:** Uyarlama yalnız temsil, süreç, ortam veya katılım yolunu değiştirir; canonical öğrenme çıktısı, görevin temel yapısı ve değerlendirmede aranan kanıt aynı kalır.

### Farklılaştırma

**Destek rotası**

- Yönergeyi görünür küçük adımlara böl; model/örnek yalnız süreci görünür kılsın, hedef metin veya performans kanıtını azaltmasın.
- Hazırlıkta anahtar yönerge ve kısa kontrol sırası kullan; öğrencinin yapacağı işlemleri tek ekranda/sayfada izlenebilir tut.

**Zenginleştirme rotası**

- Çekirdek görevi erken ve yeterli kanıtla tamamlayan öğrenci aynı çıktı üzerinde karşılaştırmalı ikinci kanıt, alternatif bağlam veya daha bağımsız gerekçelendirme üretsin; yeni zorunlu çıktı icat edilmesin.

**Öğrenme çıktıları değişmez:** Evet

### Erişilebilirlik

**Temsil destekleri**

- Yönergeleri sözlü ve yazılı olarak birlikte sun; metni seçilebilir/büyütülebilir tut ve renk tek başına anlam taşımasın.
- Görsel unsur zorunluysa temel bilgiyi kısa sözel açıklama/alt metin eşdeğeriyle de erişilebilir kıl.

**Katılım destekleri**

- Hazırlık ve geri bildirim aşamalarında ikili/küçük grup veya öğretmen destekli rota kullanılabilir; bireysel kanıt gereken yerde aynı bireysel kanıt korunur.

**Ortam destekleri**

- Gerektiğinde dikkat dağıtıcıları azaltılmış oturma/çalışma konumu, okunabilir çıktı ve erişilebilir cihaz kullanımına izin ver; görev ölçütlerini değiştirme.

**Değerlendirme construct'ı korunur:** Evet

### Canlı performans erişimi

- **Zorunlu:** Evet
- **Alternatif modlar:** `SMALL_GROUP_LIVE`, `TEACHER_OBSERVED_LIVE`, `RECORDED_ORAL_IF_ALLOWED`
- **Aynı performans kanıtı zorunlu:** Evet
- **Yalnız yazılı ikameye izin:** Hayır
- **Kayıt rıza gerektirir:** Evet

# Ders akışı

## 1. Ders — Kalan canlı sunumları tamamlama ve akran geri bildirimini gözlenebilir kanıta bağlama

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.3`, `TDE3.4`

### Hedef

Sınıf koşulları nedeniyle P03'te sunumunu tamamlayamayan öğrencilerin performanslarını eşit değerlendirme koşullarında gerçekleştirmesi; ardından öğrencilerin akran sunumlarına kişilik veya zevk yargısı yerine içerik, organizasyon, görsel kullanım ve sözlü performans kanıtlarına dayalı geri bildirim vermesi.

### Derse giriş

P03'ten kalan sunumlar varsa önce bunlar tamamlanır. Ardından 'İyi bir akran geri bildirimi konuşmacı hakkında mı, sunumda gerçekten gördüğümüz davranış hakkında mı konuşur?' sorusuyla değerlendirme dili netleştirilir.

### Öğretmenin yapacakları

1. P03'te sunumu gerçekleşmeyen öğrenci varsa T3_ACT_08 kapsamında önce canlı performansı tamamlat; eksik performans için puan uydurma.
2. Sunan her öğrenci için approved TDE9_KONUSMA_RUBRIC kanıtlarını aynı çekirdek ölçütlerde tamamla.
3. T3_ACT_09'a geçildiğinde FORM_BOB_10_T3_T4_AKRAN'ı kullandır; akran geri bildirimini kişiye değil sunum ürününe ve gözlenebilir davranışlara yönelt.
4. Geri bildirimlerde en az bir güçlü davranış ve bir geliştirme önerisinin somut kanıta dayanmasını iste: karşılaştırma kanıtı, organizasyon, görsel işlevi, ses-vurgu-tonlama, beden dili veya Türkçe kullanımı gibi.
5. 'Güzeldi', 'heyecanlıydı', 'zayıftı' gibi genel yargıları 'hangi davranışı nerede gördün?' sorusuyla kanıt diline dönüştür.
6. Akran değerlendirmesi tamamlanmadan ayrıntılı öğretmen rubrik sonucunu açıklama; öğrencinin önce bağımsız gözlem üretmesini sağla.

### Öğrencinin yapacakları

- Sunumu kaldıysa Benim Mekânım performansını tamamlar.
- Bir akran sunumunu içerik ve performans davranışları açısından dikkatle izler.
- FORM_BOB_10_T3_T4_AKRAN üzerinden en az bir güçlü yönü gözlenebilir kanıtla açıklar.
- En az bir geliştirme önerisini uygulanabilir ve saygılı biçimde yazar.
- Kişilik/zevk yargısı ile performans kanıtını birbirinden ayırır.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`, `T3_ACT_09_KONUSMA_SONRASI`
- **Formlar:** `FORM_BOB_10_T3_T4_AKRAN`

### Ölçme / öğrenme kanıtı

Ana kanıt, varsa tamamlanan canlı sunumun rubrik gözlem kaydı ile kanıta dayalı akran değerlendirme formudur. Akran görüşünde en az bir güçlü davranış ve bir geliştirme önerisinin somut sunum göstergesine bağlanması beklenir.

### Kapanış

Öğrenci 'Akranımın sunumunda ... davranışını ... kanıtı gösteriyor; geliştirme önerim ... çünkü ...' cümlesini tamamlar.

### Materyaller

- Benim Mekânım sunumları ve görselleri
- FORM_BOB_10_T3_T4_AKRAN — s.311
- Approved TDE9_KONUSMA_RUBRIC / RES_T3_05_KONUSMA_RUBRIC
- P03 öğretmen performans kanıtları

## 2. Ders — Akran görüşünden öz değerlendirmeye, öğretmen geri bildirimine ve tek iyileştirme hedefine

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.4`

### Hedef

Öğrencinin akran geri bildirimini dikkate alarak kendi performansını FORM_BOB_06_T3_KONUSMA_OZ ile değerlendirmesi; öğretmen gözlemi ve approved rubrik geri bildirimiyle karşılaştırarak güçlü yönünü ve P05'te yeniden performansla geliştireceği tek somut hedefi belirlemesi.

### Derse giriş

Öğrenci kendi P02 performans hedefini, P03 ilk izlenimini ve aldığı akran formunu yan yana getirir. 'Akran görüşüyle kendi izlenimim uyuşmuyorsa hangi sunum kanıtına dönmeliyim?' sorusuyla öz değerlendirme başlatılır.

### Öğretmenin yapacakları

1. Öğrenciden akran geri bildirimini gördükten sonra FORM_BOB_06_T3_KONUSMA_OZ ile öz değerlendirme yapmasını iste.
2. FORM_BOB_11_GENEL_GOZLEM'i öğretmen süreç kanıtı olarak kullan ve approved TDE9_KONUSMA_RUBRIC'teki düzey/kanıt geri bildirimini öğrencinin değerlendirme sentezine ekle.
3. Öz, akran, genel gözlem ve rubrik kanıtları arasında ortaklaşan güçlü yön ile geliştirme alanını belirlet; uyuşmazlık varsa canlı performans kanıtına dön.
4. Rubrik puanını tek başına sonuç olarak sunma; öğrencinin hangi ölçütte hangi gözlenebilir davranışın düzeyi taşıdığını görmesini sağla.
5. P05 için yalnız bir hedef seçtir: örneğin karşılaştırmayı daha açık kanıtlama, sonuç bölümünü ana düşünceye bağlama, görsel geçişini akıcılaştırma, ses-vurgu-tonlama, beden dili veya süre yönetimi.
6. Hedefin 'daha iyi konuşacağım' gibi soyut değil, kısa yeniden performansta gözlenebilir/değerlendirilebilir olmasını sağla.

### Öğrencinin yapacakları

- Akran geri bildirimini okuyup kendi sunum kanıtlarıyla karşılaştırır.
- FORM_BOB_06_T3_KONUSMA_OZ'yu doldurur ve açık uçlu yansıtma sorularını yanıtlar.
- FORM_BOB_11_GENEL_GOZLEM ve öğretmen rubrik geri bildirimini inceler.
- Bir güçlü yönünü en az bir performans kanıtıyla açıklar.
- P05 için tek, somut ve gözlenebilir iyileştirme hedefi belirler.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_09_KONUSMA_SONRASI`
- **Formlar:** `FORM_BOB_06_T3_KONUSMA_OZ`, `FORM_BOB_11_GENEL_GOZLEM`

### Ölçme / öğrenme kanıtı

Ana ürün dört kaynaklı kısa değerlendirme sentezidir: 'akran görüşü → öz değerlendirme → öğretmen gözlemi/rubrik kanıtı → güçlü yön + tek iyileştirme hedefi'. Hedef, P05'te kısa yeniden performansla karşılaştırılabilecek kadar somut olmalıdır.

### Kapanış

Öğrenci 'Sunumumda güçlü olan ...; bunu ... kanıtı gösteriyor. Yeniden performansta özellikle ... davranışını ... biçimde değiştireceğim.' ifadesini tamamlar.

### Materyaller

- FORM_BOB_06_T3_KONUSMA_OZ — s.307
- FORM_BOB_10_T3_T4_AKRAN — s.311
- FORM_BOB_11_GENEL_GOZLEM — s.312
- Approved TDE9_KONUSMA_RUBRIC / RES_T3_05_KONUSMA_RUBRIC
- P02-P03 performans ve prova kayıtları

## Öğretmen notu

Bu paket BLOCK_T3_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 7. ve 8. saatleridir; resmî MEB saat-saat alt sıralaması değildir. T3_ACT_09 kaynakta öz değerlendirme, akran değerlendirme ve genel gözlem formlarını açıkça bağlar; program TDE3.4 ayrıca öğretmen dereceli puanlama anahtarı değerlendirmesini zorunlu kılar. Approved yıllık TDE9_KONUSMA_RUBRIC bu gap'i karşılamak için kullanılır. P05 yeni değerlendirme turu açmayacak; seçilen tek hedefi kısa prova ve yeniden performansla sınayacaktır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 2 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`, `T3_ACT_09_KONUSMA_SONRASI`
- **Sonraki adım:** P05'te P04 değerlendirme sentezinden seçilen tek iyileştirme hedefi için kısa prova yapılmalı; ardından Benim Mekânım sunumunun hedefle ilgili 45-90 saniyelik bölümü yeniden gerçekleştirilerek 'önce kanıtı → değişiklik → sonra kanıtı' karşılaştırması yapılmalı ve konuşma bloğu kapatılmalıdır.

---

<!-- TYMM_JSON_SHA256:db8c8d10c9f72c198431d0e095cc0c67968414da3e584f20a9d6d7397e975557 -->
