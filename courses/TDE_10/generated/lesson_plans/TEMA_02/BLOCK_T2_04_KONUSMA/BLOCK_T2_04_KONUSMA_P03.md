# Podcast Revizyonu ve Nihai Kayıt: İki Mikro Hedeften Tutarlı Performansa

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_10` |
| Tema | `TEMA_02` |
| Blok | `BLOCK_T2_04_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

Tema 2 Konuşma bloğunun 5-6. saatlerinde T2_ACT_16_PODCAST_URETIM sürdürülür. P02 ilk kayıt kanıtlarından seçilen en fazla iki mikro-gelişim hedefi üzerinde çalışılır. İlk saatte içerik/provenance, akış ve sözlü icra alanlarından yalnız hedeflenen davranışlar için kontrollü prova yapılır. İkinci saatte nihai podcast kaydı veya eşdeğer canlı performans gerçekleştirilir. Kaynaklı içerik, ritim-vurgu-tonlama, duraklama ve işitsel ögelerin işlevi gözlenir; henüz resmî DPA veya yansıtma formu kullanılmaz.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T2_ACT_16_PODCAST_URETIM`
- **Kullanılan formlar:** Yok

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_T2_PODCAST_YANSITMA` | `DEFERRED` |
| `LINK_T2_PODCAST_DPA` | `DEFERRED` |

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

- **Tetikleyiciler:** `MEDIA_DEPENDENT`, `LIVE_PERFORMANCE`
- **Gerekçe:** Bu paket MEDIA_DEPENDENT, LIVE_PERFORMANCE sinyali taşıdığı için farklılaştırma ve erişilebilirlik rotası first-class olarak tutulur; destek, öğrenme çıktısını veya beklenen kanıtı azaltmaz.
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

### Medya fallback

- **Zorunlu:** Evet
- **Çevrimdışı çekirdek rota:** Evet
- **Aynı/eşdeğer kaynak zorunlu:** Evet
- **Transkript varsayılan ikame değildir:** Evet
- **Çevrimdışı rota:** Birincil medya türü (AUDIO) çevrimiçi açılamazsa aynı kaynak dosyanın önceden hazırlanmış yerel/çevrimdışı kopyasını veya aynı kanıtı taşıyan öğretmen-onaylı eşdeğeri kullan; internet erişimini çekirdek dersin ön koşulu yapma.
- **Erişim desteği:** Altyazı/transkript, yeniden oynatma ve sözel/görsel açıklama erişim desteği olarak kullanılabilir. Dinleme/izleme becerisinin kendisi hedef veya ölçme nesnesiyse transkript varsayılan olarak işitsel/görsel kanıtın yerine geçmez; gerekli bireysel uyarlama öğretmen tarafından aynı construct korunarak belirlenir.

### Canlı performans erişimi

- **Zorunlu:** Evet
- **Alternatif modlar:** `SMALL_GROUP_LIVE`, `TEACHER_OBSERVED_LIVE`, `RECORDED_ORAL_IF_ALLOWED`
- **Aynı performans kanıtı zorunlu:** Evet
- **Yalnız yazılı ikameye izin:** Hayır
- **Kayıt rıza gerektirir:** Evet

# Ders akışı

## 1. Ders — İki mikro hedef için kontrollü podcast provası

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`

### Hedef

P02 ilk kayıt kanıtlarından seçilen en fazla iki davranışı düzeltmek ve nihai kayda hazırlanmak.

### Derse giriş

P02 ilk kayıt kanıtı ve iki mikro hedef açılır; yeni konu veya yeni araştırma ekseni eklenmez.

### Öğretmenin yapacakları

1. Her hedefi gözlenebilir davranışa çevir.
2. İçerik hedefinde kaynağa geri doğrulama yaptır; icra hedefinde ritim-vurgu-tonlama-duraklama veya işitsel öge işlevini çalıştır.
3. Tüm senaryoyu yeniden yazdırma; yalnız hedefle ilgili bölümü düzelt.
4. İşitsel öge anlatımı bastırıyorsa azalt veya kaldır.

### Öğrencinin yapacakları

- İki mikro hedefi prova eder.
- Kaynak izini korur.
- Önce/sonra kısa prova kanıtı çıkarır.
- Nihai kayıt için son akışı dondurur.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_16_PODCAST_URETIM`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

P02 kanıtı → mikro hedef → prova değişikliği → yeni prova kanıtı zinciri.

### Kapanış

Öğrenci nihai kayıtta özellikle izleyeceği iki davranışı belirtir.

### Materyaller

- P02 ilk kayıt
- Podcast senaryosu
- Kaynak/provenance kaydı
- Kayıt aracı

## 2. Ders — Nihai podcast performansı ve kanıt kaydı

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`

### Hedef

Kaynaklı içerik ile sözlü icrayı tutarlı bir nihai podcast performansında birleştirmek.

### Derse giriş

Nihai performans için kaynak doğruluğu, akış ve sözlü icra odakları hatırlatılır.

### Öğretmenin yapacakları

1. Nihai kayıt veya canlı performansı gerçekleştir.
2. Biyografik/edebî iddiaların P01 kaynak kayıtlarıyla uyumunu örneklemle kontrol et.
3. Ritim-vurgu-tonlama ve işitsel ögelerin anlamı destekleyip desteklemediğine kanıt notu al.
4. Henüz LINK_T2_PODCAST_DPA veya FORM_T2_PODCAST_YANSITMA kullanma; P04'e bırak.

### Öğrencinin yapacakları

- Nihai podcast performansını gerçekleştirir.
- Kaynaklı içerik ve sözlü icrayı bütünleştirir.
- P02'ye göre değişen iki davranışı işaretler.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_16_PODCAST_URETIM`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Nihai podcast + P02/P03 önce-sonra performans kanıtı.

### Kapanış

Öğrenci nihai kayıtta en belirgin gelişimi bir kanıtla açıklar.

### Materyaller

- Nihai senaryo
- Kaynak kaydı
- Kayıt/sunum aracı

## Öğretmen notu

Bu paket pedagojik olarak 5-6. saatlerdir; resmî MEB saat-saat sıralaması değildir. Resmî DPA değerlendirmesi P04'e bırakılır ve kriterleri kaynak görünürlüğü dışında asla türetilmez.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 4 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T2_ACT_16_PODCAST_URETIM`
- **Sonraki adım:** P04'te nihai performansı LINK_T2_PODCAST_DPA ile yalnız erişilebiliyorsa değerlendir; FORM_T2_PODCAST_YANSITMA ile kanıtlı süreç yansıtması yap.

---

<!-- TYMM_JSON_SHA256:5541ad53e418f7c06e22f77ec8ad966bfae8de1c085454992723728744e91592 -->
