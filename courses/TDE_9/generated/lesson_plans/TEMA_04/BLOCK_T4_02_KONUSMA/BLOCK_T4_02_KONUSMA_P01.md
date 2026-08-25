# Dilimizin Zenginlikleri: Kanıt Bankasından Karşılaştırmalı Konuşma Planına

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_9` |
| Tema | `TEMA_04` |
| Blok | `BLOCK_T4_02_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

10 saatlik 4. Tema Konuşma Atölyesi bloğunun ilk iki ders saatinde öğrenciler T4_ACT_08_KONUSMA_SIRASI kapsamında 'Dilimizin Zenginlikleri' sunumuna hazırlanır. İlk saatte sosyal medya dili ile Türkçe/edebî dil kullanım örnekleri bağlam, amaç, hedef kitle, anlaşılırlık ve sözcük tercihi bakımından kanıta dayalı biçimde incelenir; sosyal medya dili tek başına 'yanlış' ilan edilmez ve yabancı kökenli her sözcük otomatik hata sayılmaz. İkinci saatte seçilen örnekler karşılaştırma matrisine dönüştürülür; öğrenci konuşma amacı, hedef kitlesi, ana düşüncesi ve 2-3 destekleyici karşılaştırma noktası oluşturur. FORM_IN_T4_KONUSMA_CRITERIA yalnız biçimlendirici öz-kontrol için kullanılır; approved TDE9_KONUSMA_RUBRIC ile puanlama canlı sunum aşamasına bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`
- **Kullanılan etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Kullanılan formlar:** `FORM_IN_T4_KONUSMA_CRITERIA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_IN_T4_KONUSMA_CRITERIA` | `USED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE9_KONUSMA_RUBRIC` | `MAT_T4_KONUSMA_RUBRIC` | `DEFERRED` |

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

## 1. Ders — Sosyal medya ve Türkçe/edebî dil örneklerinden güvenilir konuşma kanıtı toplama

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`

### Hedef

Öğrencinin sosyal medya dili ve Türkçe/edebî dil kullanım örneklerini bağlam, amaç, hedef kitle, anlaşılırlık ve sözcük seçimi bakımından karşılaştırması; genelleyici iyi/kötü yargıları yerine gözlenebilir dil kanıtları toplaması.

### Derse giriş

'Aynı düşünceyi arkadaş grubuna yazarken, sınıfta sunarken ve edebî bir metinde aktarırken aynı dil tercihlerinin hepsi aynı işlevi görür mü?' sorusuyla bağlam ve amaç farkı görünür kılınır.

### Öğretmenin yapacakları

1. T4_ACT_08_KONUSMA_SIRASI kapsamında sunum görevinin sosyal medya dili ve Türkçe kelime kullanımı eksenini açıkla.
2. Öğrencilerin örnekleri kişisel hesap, kullanıcı adı veya özel mesaj ifşa etmeden anonimleştirilmiş/kitapta verilen dil örnekleri üzerinden incelemesini sağla.
3. Her örnek için 'bağlam → amaç/hedef kitle → dil tercihi → anlaşılırlık/etki' zincirini kurdur.
4. Sosyal medya dilini bütünüyle bozuk dil olarak etiketleme; öğrenciden hangi tercihin hangi bağlamda işlevsel veya sorunlu olduğunu kanıtla açıklamasını iste.
5. Türkçe karşılığı bulunan bir sözcük örneğinde yalnız kökene göre hüküm verme; anlam açıklığı, kullanım bağlamı ve Türkçe karşılığın işlevini karşılaştırmalı düşündür.
6. Saat sonunda öğrenciden en az üç karşılaştırma kanıtı ve her biri için kısa kaynak/bağlam notu oluşturmasını iste.

### Öğrencinin yapacakları

- En az üç dil kullanım örneği seçer veya ders materyalindeki örnekleri kullanır.
- Her örneğin bağlamını, amacını ve hedef kitlesini belirtir.
- Dil/sözcük tercihinin anlaşılırlık veya iletişim etkisini açıklar.
- Genelleyici iyi/kötü yargısı yerine kanıta dayalı karşılaştırma notu yazar.
- Kişisel/özel sosyal medya verisi kullanmadan kısa bir kanıt bankası oluşturur.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Ana ürün en az üç satırlı kanıt bankasıdır: bağlam/amaç → dil veya sözcük tercihi → iletişim etkisi → kısa kaynak/örnek notu. Kanıt kişisel veri içermemelidir.

### Kapanış

Öğrenci 'Bir dil tercihini bağlamdan bağımsız iyi/kötü saymak yerine ... kanıtına bakmalıyım; çünkü ...' ifadesini tamamlar.

### Materyaller

- T4_ACT_08_KONUSMA_SIRASI — ders kitabı s.277–279
- Tema 4 okuma notları
- Anonimleştirilmiş veya ders materyalinde verilen dil kullanım örnekleri

## 2. Ders — Kanıtları konuşma amacı, ana düşünce ve karşılaştırma planına dönüştürme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`

### Hedef

Öğrencinin ilk saatteki kanıt bankasından konuşma amacı ve hedef kitlesine uygun ana düşünce seçmesi; 2-3 karşılaştırma noktası ile kanıt desteklerini düzenleyerek ilk konuşma planını oluşturması.

### Derse giriş

Kanıt bankası açılır. 'Üç örnek yan yana durduğunda dinleyiciye hangi ana fikri kanıtlamak istiyorum?' sorusuyla içerik seçimine geçilir.

### Öğretmenin yapacakları

1. Öğrenciden konuşma amacını ve hedef kitlesini birer cümleyle belirlemesini iste.
2. Kanıt bankasından 2-3 güçlü karşılaştırma noktası seçtir; her noktanın ana düşünceye hizmet edip etmediğini sorgulat.
3. Karşılaştırma matrisini 'bağlam/örnek → sosyal medya dilindeki tercih → Türkçe/edebî kullanım karşılığı veya alternatifi → işlev/etki → konuşmada kullanılacak çıkarım' başlıklarıyla kurdur.
4. FORM_IN_T4_KONUSMA_CRITERIA'yı yalnız biçimlendirici plan kontrolü için kullandır; performans düzeyi veya rubrik puanı üretme.
5. Ana düşünceyi 'sosyal medya dili kötüdür' gibi peşin hükme dönüştürme; öğrencinin seçtiği kanıtların izin verdiği ölçüde daha sınırlı ve savunulabilir bir ifade kurmasını sağla.
6. Saat sonunda ana düşünce + 2-3 karşılaştırma noktası + her nokta için en az bir kanıt içeren konuşma iskeletini tamamlat.

### Öğrencinin yapacakları

- Konuşmasının amacını ve hedef kitlesini belirler.
- Kanıt bankasından 2-3 karşılaştırma noktası seçer.
- Her karşılaştırma noktasını en az bir örnek/kanıtla destekler.
- Kanıtlara dayalı, aşırı genelleme içermeyen bir ana düşünce kurar.
- FORM_IN_T4_KONUSMA_CRITERIA ile planını öz-kontrol eder ve gerekirse bir noktayı revize eder.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T4_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana ürün konuşma iskeletidir: amaç + hedef kitle + ana düşünce + 2-3 karşılaştırma noktası + her nokta için kanıt. Ölçüt tablosu yalnız planın biçimlendirici kontrolüdür; rubrik puanı değildir.

### Kapanış

Öğrenci 'Konuşmamın ana düşüncesi ...; bunu özellikle ... ve ... karşılaştırma kanıtlarıyla göstereceğim.' ifadesini tamamlar.

### Materyaller

- İlk saat kanıt bankası
- FORM_IN_T4_KONUSMA_CRITERIA — ders kitabı s.279
- T4_ACT_08_KONUSMA_SIRASI

## Öğretmen notu

Bu paket BLOCK_T4_02_KONUSMA bloğunun pedagojik olarak tasarlanmış ilk 2 saatidir; resmî MEB saat-saat alt sıralaması değildir. T4_ACT_08 sosyal medya dili ve Türkçe kelime kullanımı üzerine sözlü sunum performansını doğrular. FORM_IN_T4_KONUSMA_CRITERIA bir assessment_criteria_table'dır; approved TDE9_KONUSMA_RUBRIC'in yerine geçmez. Rubrik puanlaması canlı sunum aşamasına bırakılır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 8 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`
- **Kullanılan etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Sonraki adım:** P02'de konuşma iskeleti giriş-gelişme-sonuç akışına dönüştürülmeli; bağlaşıklık, Türkçe kelime/söz varlığı seçimi, ses-vurgu-tonlama, görsel destek ve süre yönetimi için kontrollü prova yapılmalıdır. Canlı sunum ve approved rubrik puanlaması sonraki pakete bırakılmalıdır.

---

<!-- TYMM_JSON_SHA256:0eab926c01df0bcb1d302c42c27492b61193c698cb32cec74bb4a80e4e2e8301 -->
