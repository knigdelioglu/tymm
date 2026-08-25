# Konuşmayı Prova Etmek: Ses, Beden Dili ve Süre Yönetimi

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_9` |
| Tema | `TEMA_01` |
| Blok | `BLOCK_T1_04_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

10 saatlik 1. Tema Konuşma Atölyesi bloğunun 3. ve 4. ders saatlerinde öğrenciler P01'de hazırladıkları Altı Şapkalı Düşünme konuşma akışını performansa dönüştürmeye hazırlanır. İlk saatte ses tonu, vurgu-tonlama, telaffuz ve diksiyon; ikinci saatte göz teması, jest-mimik, beden duruşu, grup geçişleri ve süre yönetimi kısa prova döngüleriyle çalışılır. FORM_IN_T1_KONUSMA_CRITERIA prova ölçütü olarak kullanılır; tam sınıf sunumu ve sunum sonrası öz/akran/öğretmen formları sonraki paketlere bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.3`
- **Kullanılan etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Kullanılan formlar:** `FORM_IN_T1_KONUSMA_CRITERIA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_IN_T1_KONUSMA_CRITERIA` | `USED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| — | — | — |

### Kaynak plan referansları

| Kaynak planı | Kullanım |
|---|---|
| — | — |

## Kalabalık sınıf rotası

- **Mod:** `PARALLEL_GROUPS`
- **Aktivasyon:** Tek sıra canlı performans rotası mevcut ders saatinde tüm öğrenciler için güvenilir biçimde tamamlanamıyorsa kullan.
- **Uygulandığı dersler:** `1`, `2`
- **Paralel grup sayısı:** 5
- **Gruplama:** Sınıfı 4-6 kişilik paralel performans gruplarına ayır; konuşmacı ve gözlemci rollerini her turda döndür, hiçbir öğrenciyi yalnız gözlemci rolünde bırakma.
- **Öğretmen rotasyonu:** Öğretmen gruplar arasında planlı olarak döner; her öğrenciden en az bir doğrudan performans kanıtı toplar ve diğer kanıtları akran kayıtlarıyla çapraz kontrol eder.
- **Akran gözlemci:** Her gruptaki akran gözlemci yalnız plandaki mevcut performans ölçütlerinden bir güçlü davranış ve bir geliştirme kanıtı kaydeder; kişilik veya genel beğeni yorumu yapmaz.
- **Performans zaman sınırı:** 120 saniye
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

## 1. Ders — Ses tonu, vurgu-tonlama ve diksiyon provası

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.3`

### Hedef

Öğrencinin hazırladığı konuşma içeriğini anlaşılır ve etkili biçimde sunmak için ses tonu, vurgu-tonlama, telaffuz ve diksiyonunu konuşma amacına ve muhataba göre düzenlemesi.

### Derse giriş

P01'de hazırlanan aynı kısa konuşma cümlesi iki farklı söyleyişle seslendirilir. Öğrencilerden içerik değişmediği hâlde dinleyici üzerindeki etkinin neden değiştiğini açıklamaları istenir.

### Öğretmenin yapacakları

1. Ders kitabı s. 63-65'teki T1_ACT_13 ve FORM_IN_T1_KONUSMA_CRITERIA ölçütlerini temel al.
2. Gruplara 30-45 saniyelik kısa prova turları yaptır; her turda yalnız bir performans odağı seç: anlaşılır ses, vurgu-tonlama, telaffuz/diksiyon veya konuşma hızı.
3. Öğrencilerin ezberlenmiş yapay bir ton yerine rolün düşünsel işlevine ve mesaja uygun söyleyiş geliştirmesini sağla.
4. Geri bildirimi 'iyi/kötü' biçiminde değil gözlenebilir davranış üzerinden kur: 'mesajın ana sözcüğü duyuldu/duyulmadı', 'tempo anlamı destekledi/desteklemedi' gibi.
5. Her öğrencinin ikinci prova turunda ilk turdan tek bir performans unsurunu bilinçli biçimde değiştirmesini sağla.

### Öğrencinin yapacakları

- Kendi konuşma bölümünü kısa prova ile seslendirir.
- Ses tonu, vurgu-tonlama, telaffuz ve konuşma hızından birini ölçütlere göre denetler.
- Aldığı gözlenebilir geri bildirime göre tek bir performans unsurunu değiştirir.
- İlk ve ikinci prova arasındaki farkın dinleyiciye etkisini açıklar.
- Tam sunumda özellikle koruyacağı bir söyleyiş tercihini belirler.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T1_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana kanıt iki kısa prova arasındaki gözlenebilir değişikliktir. Öğrencinin yalnız 'daha iyi söyledim' demesi yerine hangi ses/söyleyiş unsurunu değiştirdiğini ve bunun mesajı nasıl etkilediğini açıklaması beklenir.

### Kapanış

Öğrenciler 'Sunumda sesimi özellikle … için … biçimde kullanacağım.' cümlesini tamamlar.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 63-65
- P01 grup konuşma planı ve bireysel konuşma notları
- FORM_IN_T1_KONUSMA_CRITERIA — s. 65

## 2. Ders — Beden dili, göz teması, grup geçişi ve süre yönetimi

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.3`

### Hedef

Öğrencinin konuşma sırasında göz teması, jest-mimik, beden duruşu ve grup içi geçişleri bilinçli biçimde kullanması; kendisine ayrılan süreyi konuşma bütünlüğünü bozmadan yönetmesi.

### Derse giriş

Öğrenciler ilk dersteki bir konuşma bölümünü bu kez yalnız beden dili ve göz teması açısından izler. 'Sözcükleri değiştirmeden dinleyiciyle ilişkiyi ne değiştirdi?' sorusuyla ikinci prova odağı kurulur.

### Öğretmenin yapacakları

1. FORM_IN_T1_KONUSMA_CRITERIA'daki beden dili, jest-mimik, göz teması, organizasyon ve süre boyutlarını prova kontrol listesi olarak kullandır.
2. Gruplara kısa ayakta prova yaptır; konuşmacı değişimlerinin kesintisiz ve rol sırasına uygun olmasını kontrol ettir.
3. Beden dilini gösteriye dönüştürme; hareketin mesajı desteklemesi ve doğal görünmesi ölçütünü kullan.
4. Her öğrenciye belirlenen kısa prova süresi ver; süre aşımında içeriği hızlandırmak yerine önceliklendirme yapmasını iste.
5. Ders sonunda gruplara tam sunum öncesi tek bir ortak iyileştirme hedefi seçtir.

### Öğrencinin yapacakları

- Konuşurken dinleyiciyle göz teması kurmayı ve uygun beden duruşunu dener.
- Jest ve mimiklerinin mesajla uyumunu kontrol eder.
- Grup içi konuşmacı geçişlerini prova eder.
- Kendisine ayrılan süre içinde ana mesajını koruyarak konuşmayı tamamlar.
- Grubun tam sunum öncesi ortak geliştirme hedefini belirler.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T1_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Grup için kısa prova gözlem kaydı tutulur: göz teması/beden dili, konuşmacı geçişi ve süre yönetiminden en az bir güçlü yön ile bir geliştirme noktası belirlenir. Bu kayıt P03 tam sunumuna hazırlık kanıtıdır.

### Kapanış

Her grup 'Sunuma hazırız; son olarak … ölçütünü özellikle kontrol edeceğiz.' cümlesiyle tek ortak hedef belirler.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 63-65
- P01 grup konuşma akışı
- FORM_IN_T1_KONUSMA_CRITERIA — s. 65
- Süre takibi için sınıf saati/zamanlayıcı

## Öğretmen notu

Bu paket BLOCK_T1_04_KONUSMA bloğunun pedagojik olarak tasarlanmış 3. ve 4. saatleridir; resmî MEB saat-saat alt sıralaması değildir. Yalnız T1_ACT_13 ve tema içi konuşma ölçüt tablosu kullanılmıştır. P02 performans provasıdır; tam sınıf sunumu P03'e, T1_ACT_14 ile öz/akran/öğretmen değerlendirme formları P04'e bırakılmıştır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 6 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Sonraki adım:** P03'te grupların Altı Şapkalı Düşünme Tekniğine göre hazırladıkları konuşmaları sınıf önünde gerçekleştirmelerini sağla. İçerik-role uygunluk ile TDE3.3 performans ölçütlerini birlikte gözle; sunum sonrası öz/akran/öğretmen değerlendirme formlarını P04'e bırak.

---

<!-- TYMM_JSON_SHA256:23d4e4d5b04c65f8eebb78b55eb87d6493885f1bd942383fe664848703edeee1 -->
