# Altı Şapkalı Sunum: Rolü Korumak, İkna Etmek ve Akıcı Konuşmak

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

10 saatlik 1. Tema Konuşma Atölyesi bloğunun 5. ve 6. ders saatlerinde öğrenciler, P01-P02'de hazırlayıp prova ettikleri Altı Şapkalı Düşünme konuşmalarını sınıf önünde gerçekleştirir. Sunumda role uygun içerik, argüman-gerekçe-dayanak ilişkisi, ses tonu, vurgu-tonlama, diksiyon, göz teması, jest-mimik, grup geçişi ve süre yönetimi birlikte gözlenir. FORM_IN_T1_KONUSMA_CRITERIA performans odağı olarak kullanılır; ayrıntılı öz/akran/öğretmen değerlendirme formları P04'e bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Kullanılan formlar:** `FORM_IN_T1_KONUSMA_CRITERIA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_BOB_02_T1_KONUSMA_OZ` | `DEFERRED` |
| `FORM_BOB_09_T1_T2_AKRAN` | `DEFERRED` |
| `FORM_BOB_11_GENEL_GOZLEM` | `DEFERRED` |
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

## 1. Ders — Grup sunumlarını gerçekleştirme: içerik ve rol tutarlılığı

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`

### Hedef

Öğrencinin kendi şapka rolünün düşünsel işlevini koruyarak görüş, gerekçe ve dayanaklarını muhataba uygun biçimde sunması; grup akışı içinde kendi bölümünü zamanında ve anlaşılır şekilde gerçekleştirmesi.

### Derse giriş

Gruplar P02 sonunda seçtikleri ortak geliştirme hedefini son kez kontrol eder. Sunum sırasında yeni içerik eklemek yerine hazırlanan düşünce akışını etkili biçimde gerçekleştirmeye odaklanılacağı hatırlatılır.

### Öğretmenin yapacakları

1. T1_ACT_13 kapsamında grup sunumlarını başlat ve mümkün olduğunca gerçek dinleyici koşullarını koru.
2. FORM_IN_T1_KONUSMA_CRITERIA'dan özellikle role uygun içerik, düşüncelerin düzeni, anlaşılır söyleyiş ve süre yönetimini gözlem odağı yap.
3. Sunum sırasında öğrenciyi sık sık keserek düzeltme yapma; performansın bütünlüğünü koru ve gözlemleri not al.
4. Dinleyici öğrencilerden her sunum için yalnız bir güçlü içerik/ikna unsuru ile bir açık soru not etmelerini iste; henüz resmî akran formunu kullandırma.
5. Sunum sonunda gruba yalnız kısa ve betimleyici bir anlık geri bildirim ver; ayrıntılı değerlendirmeyi P04'e sakla.

### Öğrencinin yapacakları

- Kendi şapka rolüne uygun görüş ve gerekçeleri sunar.
- Argümanını uygun örnek veya dayanakla destekler.
- Grup konuşma sırasını ve geçişlerini korur.
- Ses tonu, diksiyon, göz teması ve beden dilini konuşma amacına uygun kullanır.
- Dinleyici olarak başka grubun sunumundan bir güçlü nokta ve bir açık soru kaydeder.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T1_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana kanıt gerçek grup sunum performansıdır. Öğretmen role uygun içerik, argüman-gerekçe/dayanak, akıcılık ve temel sunum kurallarını kısa gözlem notlarıyla kaydeder; bu kayıt P04'teki ayrıntılı değerlendirmeye veri sağlar.

### Kapanış

Sunum yapan öğrenciler yalnız tek cümlelik hızlı öz izlenim yazar: 'Sunum sırasında en iyi çalışan yönüm … oldu.' Ayrıntılı öz değerlendirme P04'e bırakılır.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 63-65
- P01-P02 grup konuşma planları
- FORM_IN_T1_KONUSMA_CRITERIA — s. 65
- Sunum sırası ve süre takibi için sınıf planı

## 2. Ders — Grup sunumlarını tamamlama: performans bütünlüğü ve dinleyici etkisi

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`

### Hedef

Öğrencinin grup sunumunu içerik, söyleyiş ve sözsüz iletişim boyutlarını birlikte yöneterek tamamlaması; dinleyici olarak da ikna edici ve etkili konuşmanın gözlenebilir özelliklerini ayırt etmesi.

### Derse giriş

İlk derste gözlenen genel bir güçlü davranış ve genel bir geliştirme alanı isim vermeden sınıfla paylaşılır. İkinci tur grupları kendi hedeflerini buna göre son kez kontrol eder.

### Öğretmenin yapacakları

1. Kalan grup sunumlarını aynı ölçüt ve koşullarla gerçekleştir.
2. Gruplar arasında ölçüt değiştirme; tüm öğrenciler için aynı temel performans odağını koru.
3. Dinleyici notlarında kişisel beğeni yerine gözlenebilir konuşma davranışı veya içerik özelliği kullanılmasını sağla.
4. Sunumlar tamamlandıktan sonra sınıftan etkili konuşmanın hangi davranışlarla görünür hâle geldiğine ilişkin örnekler topla.
5. P04 için her öğrencinin kendi sunumuna ilişkin hatırladığı bir güçlü yön ve bir geliştirme alanını not etmesini sağla; henüz puanlama veya ayrıntılı form doldurma yapma.

### Öğrencinin yapacakları

- Hazırladığı grup sunumunu tamamlar.
- Konuşma sırasında süre, geçiş, ses ve beden dili unsurlarını birlikte yönetir.
- Dinleyici olarak gözlenebilir güçlü konuşma davranışlarını kaydeder.
- Sunum sonrasında kendi performansına ilişkin bir güçlü yön ve bir geliştirme alanı belirler.
- P04'te kullanmak üzere kısa performans notunu saklar.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T1_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

İkinci dersin ana kanıtı kalan grup sunumları ve öğrencilerin performans sonrası kısa öz izlenim kayıtlarıdır. Bu pakette sonuç notundan çok gerçek performansın tamamlanması ve ortak ölçütlerin gözlenmesi esas alınır.

### Kapanış

Öğrenciler 'Sunumumu yeniden yapsam ilk değiştireceğim şey … olurdu; çünkü …' cümlesini yazar. Bu cümle P04 öz değerlendirmesinin başlangıç verisidir.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 63-65
- Grup sunum notları
- FORM_IN_T1_KONUSMA_CRITERIA — s. 65
- Öğretmenin kısa performans gözlem notları

## Öğretmen notu

Bu paket BLOCK_T1_04_KONUSMA bloğunun pedagojik olarak tasarlanmış 5. ve 6. saatleridir; resmî MEB saat-saat alt sıralaması değildir. Ana canonical etkinlik T1_ACT_13'tür. Gerçek sunumlar bu pakette tamamlanır; T1_ACT_14 ve FORM_BOB_02/09/11 ile ayrıntılı öz-akran-öğretmen değerlendirmesi P04'e bırakılır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 4 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Sonraki adım:** P04'te T1_ACT_14_KONUSMA_SONRASI ile FORM_BOB_02_T1_KONUSMA_OZ, FORM_BOB_09_T1_T2_AKRAN ve FORM_BOB_11_GENEL_GOZLEM'i kullan. Öğrencilerin performans kanıtlarına dayanarak güçlü yön, geliştirme alanı ve gerekçeli iyileştirme hedefi oluşturmalarını sağla. Tema sonu test ve öğrenme günlüğünü P05'e bırak.

---

<!-- TYMM_JSON_SHA256:fff3201e168e84e12a15d6f038bd1c309a3177d9faf2dfed3e937d79128f3e41 -->
