# Dilimizin Zenginlikleri Sunumunu Kurmak: Akış, Dil Seçimi ve Kontrollü Prova

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

10 saatlik 4. Tema Konuşma Atölyesi bloğunun 3. ve 4. ders saatlerinde öğrenciler P01'de oluşturdukları kanıtlı karşılaştırma iskeletini T4_ACT_08_KONUSMA_SIRASI kapsamında konuşma akışına dönüştürür. İlk saatte giriş-gelişme-sonuç düzeni, karşılaştırmalar arası bağlaşıklık, bağlama uygun Türkçe kelime/söz varlığı seçimi ve gerekiyorsa işlevsel görsel destek planlanır. İkinci saatte iki turlu kontrollü prova yapılır: ilk turda içerik-akış-süre, ikinci turda ses, diksiyon, vurgu-tonlama, beden dili, görsel yönetimi ve dil kullanımı odaklanır. FORM_IN_T4_KONUSMA_CRITERIA biçimlendirici prova kontrolü olarak kullanılır; approved TDE9_KONUSMA_RUBRIC ile puanlama henüz yapılmaz.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`
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
| `RES_T4_SHARED_KONUSMA_RUBRIC` | `DEFERRED` |

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

## 1. Ders — Karşılaştırma iskeletini anlaşılır konuşma akışına dönüştürme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`

### Hedef

Öğrencinin P01 ana düşünce ve karşılaştırma kanıtlarını giriş-gelişme-sonuç düzeninde sıralaması; karşılaştırmalar arasında bağlaşıklık kurması, bağlama uygun söz varlığı ve Türkçe kelime tercihlerini gerekçelendirmesi ve varsa görsel desteği konuşma işlevine bağlaması.

### Derse giriş

P01 konuşma iskeleti açılır. 'Dinleyici örnekleri tek tek duymak yerine bunların neden aynı ana düşünceyi desteklediğini nasıl takip edecek?' sorusuyla organizasyona geçilir.

### Öğretmenin yapacakları

1. P01 ana düşünce ve kanıtlarını giriş-gelişme-sonuç akışında düzenlet; girişte amaç/odak, gelişmede 2-3 karşılaştırma kanıtı, sonuçta kanıta dayalı çıkarım görünür olsun.
2. Karşılaştırmalar arasında uygun geçiş ve bağlaşıklık ifadeleri seçtir; yalnız bağlaç listesi ezberletme, geçişin anlam ilişkisini sorgulat.
3. Söz varlığı seçiminde Türkçe karşılıkların anlamı ve hedef kitle açısından işlevini kontrol ettir; yalnız sözcüğün kökenine bakarak doğru/yanlış hükmü kurdurma.
4. Sunumda görsel kullanılacaksa görseli dekor olarak değil karşılaştırma kanıtını anlaşılır kılan destek olarak planlat; kaynak bilgisini kaydettir.
5. FORM_IN_T4_KONUSMA_CRITERIA ile içerik, organizasyon ve dil kullanımını biçimlendirici olarak kontrol ettir; puan veya performans düzeyi üretme.
6. Saat sonunda konuşmanın kısa akış planını ve her bölümün yaklaşık işlevini tamamlat.

### Öğrencinin yapacakları

- Konuşmasını giriş-gelişme-sonuç düzenine yerleştirir.
- 2-3 karşılaştırma noktasını mantıklı sıraya dizer.
- Karşılaştırmalar arasında anlam ilişkisini gösteren geçişler kurar.
- Türkçe kelime/söz varlığı tercihlerini bağlam ve hedef kitle açısından kontrol eder.
- Varsa görsel desteğin hangi kanıtı güçlendireceğini ve kaynağını belirtir.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T4_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana ürün giriş-gelişme-sonuç akış planıdır. Her karşılaştırma kanıtı ana düşünceye bağlanmalı; geçişlerin anlam işlevi ve seçilen söz varlığının bağlama uygunluğu açıklanabilmelidir.

### Kapanış

Öğrenci 'Konuşmamda önce ..., sonra ... karşılaştırmasını, ardından ... kanıtını kullanacağım; bu sıra ana düşüncemi ... biçimde güçlendiriyor.' ifadesini tamamlar.

### Materyaller

- P01 konuşma iskeleti ve kanıt bankası
- FORM_IN_T4_KONUSMA_CRITERIA — s.279
- Varsa kaynak bilgisi kaydedilmiş işlevsel görsel destek

## 2. Ders — İki turlu prova: içerik-süreden ses, beden dili ve dil kullanımına

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`

### Hedef

Öğrencinin konuşma akışını önce içerik ve süre bakımından, ardından ses-diksiyon, vurgu-tonlama, beden dili, görsel yönetimi ve Türkçe/söz varlığı kullanımı bakımından prova ederek canlı sunum öncesi tek geliştirme hedefi belirlemesi.

### Derse giriş

'Bir sunumu aynı anda on farklı ölçütte düzeltmeye çalışmak mı, iki turda farklı odaklarla prova etmek mi daha işlevli?' sorusuyla prova yöntemi açıklanır.

### Öğretmenin yapacakları

1. İlk prova turunu içerik odağı, karşılaştırma kanıtlarının sırası, geçişlerin açıklığı ve süre yönetimi üzerine yürüt.
2. İlk tur sonunda yalnız bir içerik/organizasyon düzeltmesi yaptır; konuşmayı baştan yazdırma.
3. İkinci prova turunda sesin işitilebilirliği, telaffuz, vurgu-tonlama, konuşma hızı, beden dili/göz teması ve varsa görsel geçişlerini gözlet.
4. Dil kullanımında bağdaşıklık, cümle kuruluşu ve seçilen Türkçe/söz varlığı örneklerinin bağlama uygunluğunu kontrol ettir.
5. FORM_IN_T4_KONUSMA_CRITERIA'yı prova sonrası biçimlendirici öz-kontrol için kullandır; approved TDE9_KONUSMA_RUBRIC ile puanlama yapma.
6. Canlı sunum için öğrenciden tek gözlenebilir geliştirme hedefi seçmesini iste: örneğin süre, geçiş, vurgu, telaffuz, göz teması veya kelime tercihi.

### Öğrencinin yapacakları

- İlk turda konuşmasını içerik, akış ve süre odağıyla prova eder.
- Tek bir içerik/organizasyon düzeltmesi yapar.
- İkinci turda ses, diksiyon, vurgu-tonlama, beden dili, görsel ve dil kullanımına odaklanır.
- FORM_IN_T4_KONUSMA_CRITERIA ile prova kaydını öz-kontrol eder.
- Canlı sunumda izleyeceği tek gözlenebilir geliştirme hedefini yazar.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T4_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana kanıt iki prova kaydıdır: tur 1 içerik-akış-süre düzeltmesi; tur 2 ses/beden dili/dil kullanımı gözlemi. Paket sonunda bir tek canlı sunum geliştirme hedefi bulunmalıdır.

### Kapanış

Öğrenci 'Canlı sunumda özellikle ... davranışımı izleyeceğim; provada bunu ... kanıtından dolayı geliştirmem gerektiğini gördüm.' ifadesini tamamlar.

### Materyaller

- P02 ilk saat konuşma akış planı
- FORM_IN_T4_KONUSMA_CRITERIA
- Varsa görsel sunum materyali
- Basit süre takip aracı

## Öğretmen notu

Bu paket BLOCK_T4_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 3. ve 4. saatleridir; resmî MEB saat-saat alt sıralaması değildir. T4_ACT_08 kapsamındaki konuşma içeriği ve kural uygulama hazırlığı sürdürülür. FORM_IN_T4_KONUSMA_CRITERIA ölçüt tablosudur; approved TDE9_KONUSMA_RUBRIC ile canlı performans puanlaması P03'e bırakılır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 6 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Sonraki adım:** P03'te Dilimizin Zenginlikleri canlı sunum rotasyonu başlatılmalı; approved TDE9_KONUSMA_RUBRIC / RES_T4_SHARED_KONUSMA_RUBRIC ile gerçek performans kanıtı kaydedilmeli. T4_ACT_09 öz-akran değerlendirmesi P04'e bırakılmalıdır.

---

<!-- TYMM_JSON_SHA256:9ae9b9295b8bfbd682eeef8afd31cd6430fdc17ef57043b0726e0e50c5aa9178 -->
