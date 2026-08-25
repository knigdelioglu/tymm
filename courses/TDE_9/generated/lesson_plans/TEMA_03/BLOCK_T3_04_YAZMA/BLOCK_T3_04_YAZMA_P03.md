# İnfografik Revizyonu: Doğruluk, Anlam Bütünlüğü, Görsel-Metin Dengesi ve Dil İşçiliği

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_9` |
| Tema | `TEMA_03` |
| Blok | `BLOCK_T3_04_YAZMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

10 saatlik 3. Tema Yazma Atölyesi bloğunun 5. ve 6. ders saatlerinde öğrenciler P02'de oluşturdukları ilk tam infografik taslağı T3_ACT_12_YAZMA_SIRASI kapsamında hedefli biçimde revize eder. İlk saatte bilgi doğruluğu, anlam bütünlüğü, bilgi hiyerarşisi, görsel-metin dengesi ve kaynak güvenilirliği yeniden kontrol edilir; tasarımın bilgiyi gölgelemesine veya özgünlük adına kaynaksız içerik eklenmesine izin verilmez. İkinci saatte dil ve söz varlığı, açıklık, bağdaşıklık, yazım-noktalama ve görsel üzerindeki metinlerin okunabilirliği gözden geçirilir. FORM_IN_T3_YAZMA_CRITERIA yalnız biçimlendirici kontrol sağlar; T3_ACT_13, öz/akran/öğretmen değerlendirmesi ve approved TDE9_YAZMA_RUBRIC puanlaması P04'e bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE4.2`, `TDE4.3`
- **Kullanılan etkinlikler:** `T3_ACT_12_YAZMA_SIRASI`
- **Kullanılan formlar:** `FORM_IN_T3_YAZMA_CRITERIA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_BOB_05_T3_YAZMA_OZ` | `USED` |
| `FORM_BOB_10_T3_T4_AKRAN` | `USED` |
| `FORM_BOB_11_GENEL_GOZLEM` | `USED` |
| `FORM_IN_T3_YAZMA_CRITERIA` | `USED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE9_YAZMA_RUBRIC` | `MAT_T3_YAZMA_RUBRIC` | `DEFERRED` |

### Kaynak plan referansları

| Kaynak planı | Kullanım |
|---|---|
| `RES_T3_06_YAZMA_RUBRIC` | `USED` |

## Sınıf uyarlamaları

- **Tetikleyiciler:** `MEDIA_DEPENDENT`
- **Gerekçe:** Bu paket MEDIA_DEPENDENT sinyali taşıdığı için farklılaştırma ve erişilebilirlik rotası first-class olarak tutulur; destek, öğrenme çıktısını veya beklenen kanıtı azaltmaz.
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
- **Çevrimdışı rota:** Birincil medya türü (VIDEO, DIGITAL_TOOL) çevrimiçi açılamazsa aynı kaynak dosyanın önceden hazırlanmış yerel/çevrimdışı kopyasını veya aynı kanıtı taşıyan öğretmen-onaylı eşdeğeri kullan; internet erişimini çekirdek dersin ön koşulu yapma.
- **Erişim desteği:** Altyazı/transkript, yeniden oynatma ve sözel/görsel açıklama erişim desteği olarak kullanılabilir. Dinleme/izleme becerisinin kendisi hedef veya ölçme nesnesiyse transkript varsayılan olarak işitsel/görsel kanıtın yerine geçmez; gerekli bireysel uyarlama öğretmen tarafından aynı construct korunarak belirlenir.

# Ders akışı

## 1. Ders — İçerik doğruluğu ve görsel-metin dengesini kanıtla revize etme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE4.2`, `TDE4.3`

### Hedef

Öğrencinin ilk tam infografik taslağındaki her temel bilgi ve görseli kaynaklı kanıtla yeniden kontrol etmesi; anlam bütünlüğünü, bilgi hiyerarşisini ve görsel-metin dengesini güçlendirecek gerekçeli revizyonlar yapması.

### Derse giriş

P02 ilk tam taslağı ile Dinleme/İzleme P04 kaynaklı kanıt dosyası yan yana açılır. 'Taslak güzel görünüyor olabilir; peki her önemli bilgi hâlâ doğru, kaynaklı ve ana mesaja hizmet ediyor mu?' sorusuyla içerik revizyonu başlatılır.

### Öğretmenin yapacakları

1. Öğrenciden taslaktaki her ana bilgi birimini kaynaklı kanıt dosyasındaki karşılığıyla eşleştirmesini iste.
2. Kaynağı belirsiz, anlamı aşırı genelleştirilmiş veya belgesel kanıtını aşan bir ifade varsa düzeltmesini ya da çıkarmasını sağla.
3. Bilgi hiyerarşisini kontrol ettir: ana mesajı desteklemeyen ayrıntı, ana bilgiden daha baskın görünüyorsa yerleşim veya metin ağırlığını değiştir.
4. Her görsel için 'hangi bilgiyi taşıyor/açıklıyor?' sorusunu yeniden sor; dekoratif veya yanlış ilişkilendirilmiş görseli değiştir, küçült veya kaldır.
5. Özgünlüğü kaynaktan kopmak olarak değil, kaynaklı bilgiyi öğrencinin kendi açık ve işlevsel düzeninde yeniden kurması olarak ele al.
6. FORM_IN_T3_YAZMA_CRITERIA ile içerik doğruluğu, organizasyon ve görsel-metin uyumuna ilişkin en az iki revizyon kararı kaydettir.

### Öğrencinin yapacakları

- Her ana bilgi birimini kaynaklı kanıt dosyasıyla karşılaştırır.
- Kaynağı belirsiz veya aşırı genelleştirilmiş ifadeleri düzeltir ya da çıkarır.
- Ana mesaj ile bilgi hiyerarşisinin uyumunu kontrol eder.
- Görsellerin ilgili bilgiyi gerçekten destekleyip desteklemediğini değerlendirir.
- İçerik/organizasyon ve görsel-metin düzeyinde en az iki gerekçeli revizyon yapar.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_12_YAZMA_SIRASI`
- **Formlar:** `FORM_IN_T3_YAZMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana kanıt 'ilk taslak öğesi → kaynak/ölçüt kontrolü → sorun → yapılan revizyon → gerekçe' tablosudur. En az iki revizyonun doğrudan doğruluk, anlam bütünlüğü veya görsel-metin işlevine bağlanması beklenir.

### Kapanış

Öğrenci 'Taslakta ... öğesini ... kanıtı/ölçütü nedeniyle ... biçiminde değiştirdim; bu değişiklik ana mesajı ... yönden güçlendirdi.' ifadesini tamamlar.

### Materyaller

- P02 ilk tam infografik taslağı
- Dinleme/İzleme P04 kaynaklı kanıt dosyası
- FORM_IN_T3_YAZMA_CRITERIA — ders kitabı s.205
- Nevruz Belgeseli gerektiğinde kanıta dönüş için

## 2. Ders — Dil, söz varlığı, bağdaşıklık ve yazım-noktalama revizyonu

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE4.2`, `TDE4.3`

### Hedef

Öğrencinin infografik metnindeki sözcük ve cümleleri bağlama ve iletişim amacına uygunlaştırması; metin birimleri arasındaki bağlantıyı, açıklığı, yazım-noktalamayı ve okunabilirliği gözden geçirerek paylaşım öncesi revize edilmiş sürüm oluşturması.

### Derse giriş

İlk saat içerik revizyonu tamamlandıktan sonra bir metin bloğu seçilir. 'Bilgi doğru olsa bile ifade belirsiz, gereksiz uzun veya kopuksa okur ne kaybeder?' sorusuyla dil işçiliğine geçilir.

### Öğretmenin yapacakları

1. Metin bloklarını tek tek okut; belirsiz, gereksiz uzun, tekrarlı veya bağlama uymayan ifadeleri öğrencinin kendisinin işaretlemesini sağla.
2. Sözcük seçimini infografik bağlamına uygunluk ve açıklık üzerinden kontrol ettir; deyim/atasözü kullanımını yalnız anlamı gerçekten destekliyorsa kabul et, zorunlu süs unsuruna dönüştürme.
3. Kısa metin birimleri arasında başlık, alt başlık ve bağlantı ifadeleriyle bağdaşıklığın kurulup kurulmadığını sorgulat.
4. Yazım ve noktalama hatalarını yalnız işaretlemek yerine öğrenciden hatayı düzeltip okuma/anlam etkisini açıklamasını iste.
5. Görsel üzerindeki metinlerin okunabilirliğini kontrol ettir; bilgi yoğunluğu okunabilirliği bozuyorsa metni kısalt veya yeniden dağıt.
6. FORM_IN_T3_YAZMA_CRITERIA ile son biçimlendirici öz-kontrolü yaptır; approved TDE9_YAZMA_RUBRIC ile puanlama ve T3_ACT_13 formları P04'e bırak.

### Öğrencinin yapacakları

- Belirsiz, uzun veya tekrarlı ifadeleri işaretler ve sadeleştirir.
- Söz varlığını bağlam ve iletişim amacı açısından gözden geçirir.
- Başlık, alt başlık ve metin birimleri arasındaki bağlantıları güçlendirir.
- Yazım ve noktalama hatalarını düzeltir.
- Görsel üzerindeki metin yoğunluğunu ve okunabilirliği kontrol eder.
- FORM_IN_T3_YAZMA_CRITERIA ile revize edilmiş taslağın paylaşım öncesi eksiklerini belirler.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_12_YAZMA_SIRASI`
- **Formlar:** `FORM_IN_T3_YAZMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana ürün paylaşım öncesi revize edilmiş infografik taslaktır. Öğrenci en az bir dil/anlatım, bir bağdaşıklık/okunabilirlik ve bir yazım-noktalama düzeltmesini önce-sonra kanıtıyla gösterebilmelidir.

### Kapanış

Öğrenci 'Paylaşımdan önce en önemli dil düzeltmem ... oldu; çünkü önce ... iken şimdi ... ve okur bilgiyi ... biçimde daha açık izleyebiliyor.' cümlesini tamamlar.

### Materyaller

- P03 ilk saat içerik ve görsel revizyonu yapılmış taslak
- FORM_IN_T3_YAZMA_CRITERIA — s.205
- P02 metin taslağı ile karşılaştırma kaydı
- Kâğıt veya mevcut dijital tasarım aracı

## Öğretmen notu

Bu paket BLOCK_T3_04_YAZMA bloğunun pedagojik olarak tasarlanmış 5. ve 6. saatleridir; resmî MEB saat-saat alt sıralaması değildir. Tema 3 görev bağında anlam bütünlüğü, grafik/görsel düzen, dil ve imla tutarlılığı; program/ölçüt bağında doğruluk, tutarlılık ve özgünlük kanıtları önemlidir. Özgünlük kaynaksız ekleme olarak değil, kaynaklı bilgiyi öğrencinin kendi işlevsel infografik düzeninde kurması olarak ele alınır. T3_ACT_13 ve approved TDE9_YAZMA_RUBRIC ile öğretmen puanlaması P04'e bırakılmıştır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 4 saat
- **Kapsanan çıktılar:** `TDE4.1`, `TDE4.2`, `TDE4.3`
- **Kullanılan etkinlikler:** `T3_ACT_12_YAZMA_SIRASI`
- **Sonraki adım:** P04'te revize edilmiş infografik paylaşılmalı; T3_ACT_13 kapsamında FORM_BOB_10_T3_T4_AKRAN, FORM_BOB_05_T3_YAZMA_OZ ve FORM_BOB_11_GENEL_GOZLEM kullanılmalı, approved TDE9_YAZMA_RUBRIC / RES_T3_06_YAZMA_RUBRIC ile öğretmen değerlendirme kanıtı eklenmeli ve P05 için tek nihai revizyon önceliği seçilmelidir.

---

<!-- TYMM_JSON_SHA256:231a2e925d6b3dc0ed98afa3acd467558c410d4157b0b3f2b272e62924fa64cb -->
