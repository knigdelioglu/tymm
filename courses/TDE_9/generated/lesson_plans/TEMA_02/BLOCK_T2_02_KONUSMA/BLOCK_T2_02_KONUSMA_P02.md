# Karakteri Sahneye Hazırlamak: Kurgu, Görsel Destek ve Kontrollü Prova

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_9` |
| Tema | `TEMA_02` |
| Blok | `BLOCK_T2_02_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

10 saatlik 2. Tema Konuşma Atölyesi bloğunun 3. ve 4. ders saatlerinde öğrenciler P01'de oluşturdukları karakter sunum planını T2_ACT_08_KONUSMA_SIRASI kapsamında geliştirir. İlk saatte karakterin metne dayalı özellikleri öğrencinin estetik yorumuyla yeniden kurgulanır; uygun görsel destek hazırlanır ve görselin ana düşünceye hizmet etmesi denetlenir. İkinci saatte FORM_IN_T2_KONUSMA_CRITERIA kullanılarak kısa prova döngüleri yapılır; ses-diksiyon, akıcılık, beden dili, Türkçenin doğru kullanımı ve süre yönetiminden seçilmiş odaklarda gözlenebilir iyileştirme sağlanır. Tam sınıf sunumu P03'e bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Kullanılan formlar:** `FORM_IN_T2_KONUSMA_CRITERIA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_IN_T2_KONUSMA_CRITERIA` | `USED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE9_KONUSMA_RUBRIC` | `MAT_T2_KONUSMA_RUBRIC` | `DEFERRED` |

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

## 1. Ders — Metin kanıtından estetik karakter kurgusuna ve görsel desteğe

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`

### Hedef

Öğrencinin seçtiği karaktere ilişkin metin kanıtlarını koruyarak kendi yorumunu geliştirmesi; karakteri gerçek veya kurgusal benzerliklerle düşünmesi ve sunumun ana düşüncesini destekleyen işlevsel bir görsel tasarlaması.

### Derse giriş

P01'deki ‘metnin söylediği / benim yorumum’ ayrımı yeniden açılır. ‘Bir karaktere kendi yorumumuzu katarken metinden ne kadar uzaklaşabiliriz?’ sorusuyla yaratıcı yorum ile metne sadakat arasındaki sınır tartışılır.

### Öğretmenin yapacakları

1. Ders kitabı s. 126-128'deki T2_ACT_08 özdeşleştirme, sınıflandırma, estetik kurgu ve görsel hazırlama yönergelerini temel al.
2. Öğrencinin karakteri gerçek veya kurgusal başka bir kişiyle ilişkilendirmesi durumunda benzerliği yüzeysel isim eşleştirmesine değil davranış, değer, çatışma veya değişim gibi gözlenebilir bir ölçüte bağlat.
3. Özgün yorumların metindeki karakter kanıtlarıyla çelişip çelişmediğini kontrol ettir; çelişiyorsa öğrenciden yorumunu daraltmasını veya yeni kanıt bulmasını iste.
4. Görsel desteği süsleme amacıyla değil ana düşünceyi görünür kılma amacıyla tasarlat; her görsel için ‘Bu görsel konuşmadaki hangi düşünceyi destekliyor?’ sorusunu kullandır.
5. Ders sonunda konuşma planındaki içerik sırasını görselin kullanılacağı noktayla birlikte güncellet.

### Öğrencinin yapacakları

- Karakterin metne dayalı özelliklerini kendi yorumuyla geliştirir.
- Karakteri uygun bir gerçek/kurgusal kişi veya karakter tipiyle gerekçeli olarak ilişkilendirir.
- Yaratıcı yorumunun metin kanıtıyla uyumunu denetler.
- Ana düşünceyi destekleyen işlevsel bir görsel hazırlar veya tasarlar.
- Görselin konuşmanın hangi bölümünde ve neden kullanılacağını planlar.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T2_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana ürün güncellenmiş karakter kurgusu ve görsel kullanım planıdır. Öğrencinin estetik yorumunun metin kanıtından tamamen kopmaması ve görselin belirli bir konuşma düşüncesine hizmet etmesi beklenir.

### Kapanış

Öğrenci ‘Karaktere kattığım özgün yorum …; bunu metindeki … göstergesi sınırlandırıyor/destekliyor. Görselim ise … düşüncesini güçlendirecek.’ cümlelerini tamamlar.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 125-129
- P01 karakter sunum planı
- ‘Bir Kavak ve İnsanlar’ metni
- Sunum görseli için sınıf içi mevcut araçlar
- FORM_IN_T2_KONUSMA_CRITERIA — s. 129

## 2. Ders — Ses, akıcılık, beden dili ve süre için kontrollü prova

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.3`

### Hedef

Öğrencinin hazırladığı karakter sunumunu kısa prova turlarında ses-diksiyon, akıcılık, beden dili, Türkçenin doğru kullanımı ve zaman yönetimi açısından gözlemleyip tek tek iyileştirmesi.

### Derse giriş

Aynı kısa konuşma bölümü önce yalnız metne bakılarak, sonra dinleyiciye yönelerek söylenir. Öğrencilerden içerik değişmeden performansın hangi yönlerinin değiştiğini adlandırmaları istenir.

### Öğretmenin yapacakları

1. FORM_IN_T2_KONUSMA_CRITERIA'daki ölçütleri prova kontrol listesi olarak kullan; bütün ölçütleri aynı turda düzeltmeye çalışma.
2. 30-60 saniyelik kısa prova turları yaptır ve her turda en fazla iki odak seç: ses/diksiyon ve akıcılık; beden dili/göz teması; Türkçenin doğru kullanımı; süre/organizasyon gibi.
3. Geri bildirimi ‘iyi/kötü’ biçiminde değil gözlenebilir davranışla ver: ana sözcükte vurgu duyuldu/duyulmadı, göz teması sürdü/sık koptu, süre ana fikri sıkıştırdı/sıkıştırmadı gibi.
4. Öğrencinin görseli konuşmayı kesintiye uğratmadan doğru anda kullanmasını prova ettir.
5. İkinci prova turunda öğrenciden ilk turdan yalnız bir veya iki davranışı bilinçli biçimde değiştirmesini ve değişimin etkisini açıklamasını iste.

### Öğrencinin yapacakları

- Karakter sunumunun kısa bir bölümünü prova eder.
- Belirlenen performans ölçütlerinde kendini ve bir akranını gözlemler.
- Gözlenebilir geri bildirime göre bir veya iki davranışı değiştirir.
- Görselini konuşma akışını kesmeden kullanmayı dener.
- İlk ve ikinci prova arasındaki farkı açıklayarak P03 için kişisel performans hedefi belirler.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T2_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana kanıt iki kısa prova arasındaki gözlenebilir değişiklik ve öğrencinin P03 için belirlediği tek performans hedefidir. Prova notu nihai puan değildir.

### Kapanış

Öğrenci ‘Tam sunumda özellikle … davranışını koruyacağım/değiştireceğim; çünkü provada … farkını gördüm.’ cümlesini tamamlar.

### Materyaller

- P01-P02 konuşma planı ve görsel
- FORM_IN_T2_KONUSMA_CRITERIA — s. 129
- Süre takibi için sınıf saati/zamanlayıcı

## Öğretmen notu

Bu paket BLOCK_T2_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 3. ve 4. saatleridir; resmî MEB saat-saat alt sıralaması değildir. T2_ACT_08 kapsamında içerik kurgusu ve görsel destek tamamlanmış, ardından performans ölçütleri kısa prova döngülerinde çalışılmıştır. Repodaki TDE9_KONUSMA_RUBRIC artifact'ı REVIEW_REQUIRED durumunda olduğundan bu pakette öğretmen puanlaması için kullanılmamıştır. Tam canlı sunum P03'e bırakılmıştır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 6 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Sonraki adım:** P03'te öğrencilerin karakter sunumlarını sınıf önünde gerçekleştirmelerini sağla. İçerik kurgusu ile ses-diksiyon, akıcılık, beden dili, Türkçenin doğru kullanımı ve süre yönetimini gözle. TDE9_KONUSMA_RUBRIC yalnız öğretmen incelemesi/onayı tamamlandıysa analitik puanlama desteği olarak kullanılsın; aksi durumda REVIEW_REQUIRED pilot artifact olduğu açıkça belirtilsin. T2_ACT_09 öz/akran değerlendirmesini P04'e bırak.

---

<!-- TYMM_JSON_SHA256:c97b86b144c9d86ea53c72cba3483120f762793c77a02b5b181ff30f478b078b -->
