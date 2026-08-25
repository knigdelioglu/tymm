# Karakterimin Yolculuğu: Canlı Sunum ve Performans Kanıtı

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

10 saatlik 2. Tema Konuşma Atölyesi bloğunun 5. ve 6. ders saatlerinde öğrenciler P01-P02'de hazırladıkları ‘Karakterimin Yolculuğu’ konuşmalarını sınıf önünde gerçekleştirir. İlk saatte sunum düzeni ve performansın ilk bölümü; ikinci saatte kalan sunumlar ve kısa performans sonrası kanıt kaydı yürütülür. Değerlendirme odağı T2_ACT_08 ve FORM_IN_T2_KONUSMA_CRITERIA'daki içerik kurgusu, ses-diksiyon, akıcılık, beden dili, Türkçenin doğru kullanımı, görsel kullanım ve zaman yönetimidir. Repodaki TDE9_KONUSMA_RUBRIC yalnız öğretmen incelemesi/onayı tamamlanmışsa analitik puanlama desteği olarak kullanılabilir; mevcut REVIEW_REQUIRED durumu resmî/onaylı puanlama aracı gibi sunulmaz. Öz/akran değerlendirme T2_ACT_09 ile P04'e bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Kullanılan formlar:** `FORM_IN_T2_KONUSMA_CRITERIA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_BOB_04_T2_KONUSMA_OZ` | `DEFERRED` |
| `FORM_BOB_09_T1_T2_AKRAN` | `DEFERRED` |
| `FORM_BOB_11_GENEL_GOZLEM` | `DEFERRED` |
| `FORM_IN_T2_KONUSMA_CRITERIA` | `USED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE9_KONUSMA_RUBRIC` | `MAT_T2_KONUSMA_RUBRIC` | `DEFERRED` |

### Kaynak plan referansları

| Kaynak planı | Kullanım |
|---|---|
| `RES_T2_08` | `USED` |

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

## 1. Ders — Canlı karakter sunumlarını başlatma ve performans kanıtı toplama

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`

### Hedef

Öğrencinin seçtiği karakteri ana düşünce etrafında kurguladığı hazırlıklı konuşmayla sınıfa sunması; içerik, ses-diksiyon, akıcılık, beden dili, Türkçenin doğru kullanımı ve süre yönetimi ölçütlerini gerçek performansta uygulaması.

### Derse giriş

P02 sonunda belirlenen kişisel performans hedefleri kısa biçimde hatırlatılır. Öğrencilere sunum sırasında hedefin ‘kusursuz olmak’ değil, hazırlanan içeriği dinleyiciye anlaşılır ve etkili biçimde aktarmak olduğu belirtilir.

### Öğretmenin yapacakları

1. T2_ACT_08'in s. 128-129'daki canlı sunum basamaklarını ve FORM_IN_T2_KONUSMA_CRITERIA ölçütlerini temel al.
2. Sunum öncesi her öğrencinin ana düşüncesini, görselini ve kişisel performans hedefini hazır bulundurmasını sağla.
3. Sunum sırasında öğrenciyi gereksiz yere kesme; içerik kurgusu, ses-diksiyon, akıcılık, beden dili/göz teması, Türkçenin doğru kullanımı, görselin işlevi ve süre kullanımına ilişkin kısa gözlem kanıtları kaydet.
4. Dinleyici öğrencilerin sunum sırasında ayrıntılı form doldurmak yerine bir güçlü performans davranışı ve bir soru not etmelerini sağla; T2_ACT_09 değerlendirmesi P04'te yapılacaktır.
5. TDE9_KONUSMA_RUBRIC yalnız öğretmen incelemesi/onayı tamamlanmışsa kullan; mevcut REVIEW_REQUIRED sürüm kullanılıyorsa bunun pilot/inceleme amaçlı olduğunu ve resmî MEB puanlama kuralı olmadığını açıkça koru.

### Öğrencinin yapacakları

- Karakter sunumunu hazırladığı ana düşünce ve akışa göre gerçekleştirir.
- Metin kanıtı ile kendi karakter yorumunu anlaşılır biçimde ayırarak sunar.
- Ses, diksiyon, akıcılık ve beden dilini dinleyiciye göre kullanır.
- Görsel desteğini konuşmanın ilgili noktasında işlevsel biçimde kullanır.
- Belirlenen süre içinde ana düşüncesini koruyarak sunumunu tamamlar.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T2_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana kanıt canlı sözlü performanstır. Öğretmen her sunum için en az iki somut gözlem kaydı tutar: biri içerik/organizasyon, biri performans/dil boyutundan. REVIEW_REQUIRED rubrik kullanılıyorsa sonuç pilot gözlem olarak tutulur; onaylı resmî puan gibi sunulmaz.

### Kapanış

Sunum yapan öğrenciler yalnız kısa bir öz izlenim yazar: ‘Bugünkü sunumda P02 hedefimi … ölçüde uygulayabildim; bunu … davranışından görüyorum.’ Ayrıntılı öz değerlendirme P04'e bırakılır.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 128-129
- P01-P02 karakter sunum planı ve görseli
- FORM_IN_T2_KONUSMA_CRITERIA — s. 129
- TDE9_KONUSMA_RUBRIC / RES_T2_08 — yalnız REVIEW_REQUIRED durumu ve öğretmen inceleme koşulu korunarak

## 2. Ders — Canlı sunumları tamamlama ve gözlem kanıtlarını düzenleme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`

### Hedef

Öğrencilerin kalan karakter sunumlarını aynı ölçütlerle tamamlaması; öğretmenin ve dinleyicilerin performans sonrası değerlendirmeye temel oluşturacak gözlenebilir kanıtları düzenlemesi.

### Derse giriş

İlk dersin gözlem deneyiminden hareketle ‘Bir konuşmayı değerlendirirken genel beğeni mi, gözlenebilir davranış mı daha güvenilir kanıt sağlar?’ sorusu yöneltilir; ikinci tur sunumlarında kanıt dilinin korunacağı belirtilir.

### Öğretmenin yapacakları

1. Kalan sunumları T2_ACT_08 ve aynı ölçüt çerçevesiyle gerçekleştir.
2. Her öğrenci için güçlü yön ve geliştirme alanı yazarken ‘etkileyiciydi/zayıftı’ gibi genel ifadeleri gözlenebilir davranışa dönüştür.
3. Sunum yapan öğrenciyle dinleyici notlarının kişilik değerlendirmesine dönüşmesini engelle; yalnız performans davranışları ve içerik kanıtları üzerinden ilerle.
4. Sunum sonunda öğretmen gözlem notlarını P04'te kullanılacak başlıklara göre düzenle: içerik/kurgu, organizasyon-süre, ses-diksiyon-akıcılık, beden dili, Türkçe/söz varlığı.
5. P04 öncesinde öğrenciye ayrıntılı sonuç veya düzey açıklaması verme; önce öz ve akran değerlendirmesinin bağımsız yapılmasını koru.

### Öğrencinin yapacakları

- Sunumunu sınıf önünde tamamlar.
- Dinleyici olduğunda bir akranının gözlenebilir güçlü davranışını ve bir geliştirme sorusunu not eder.
- Sunum sonrası ilk izlenimini kısa kanıt cümlesiyle kaydeder.
- Ayrıntılı öz/akran değerlendirmesini P04'e bırakır.
- Geri bildirim alırken kişiye değil performans davranışına odaklanır.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T2_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

P03 sonunda her öğrenci için canlı performans kanıtı ile en az iki öğretmen gözlemi ve bir dinleyici gözlem notu bulunur. Bu kayıtlar P04'te T2_ACT_09 kapsamındaki öz/akran/öğretmen değerlendirmesine girdi olacaktır.

### Kapanış

Öğrenciler ‘Sunumumu yeniden izleyebilseydim özellikle … davranışım için kanıt arardım; çünkü …’ cümlesini tamamlar. Sonraki paket değerlendirme ve yansıtma aşamasıdır.

### Materyaller

- Canlı karakter sunumları
- FORM_IN_T2_KONUSMA_CRITERIA — s. 129
- Öğretmen gözlem notları
- TDE9_KONUSMA_RUBRIC / RES_T2_08 — onay koşuluna bağlı pilot destek

## Öğretmen notu

Bu paket BLOCK_T2_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 5. ve 6. saatleridir; resmî MEB saat-saat alt sıralaması değildir. T2_ACT_08 kapsamında canlı performans gerçekleştirilmiştir. T2_ACT_09, FORM_BOB_04_T2_KONUSMA_OZ, FORM_BOB_09_T1_T2_AKRAN ve FORM_BOB_11_GENEL_GOZLEM P04'e bırakılmıştır. Programın zorunlu analitik öğretmen değerlendirmesi için canonical yıllık artifact TDE9_KONUSMA_RUBRIC mevcuttur; ancak repodaki güncel artifact lifecycle'ı REVIEW_REQUIRED olduğundan öğretmen onayı tamamlanmadan resmî/onaylı puanlama anahtarı olarak sunulmamalıdır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 4 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Sonraki adım:** P04'te T2_ACT_09_KONUSMA_SONRASI'na geç. Önce akran değerlendirmesi, ardından akran görüşünü dikkate alan FORM_BOB_04_T2_KONUSMA_OZ öz değerlendirmesi ve öğretmen gözlemini birleştir. TDE9_KONUSMA_RUBRIC yalnız öğretmen onayı varsa analitik sonuç üretmek için kullanılsın; REVIEW_REQUIRED ise pilot gözlem statüsü açıkça korunsun. P05'i geri bildirim sentezi, telafi hedefi ve kısa yeniden performans için ayır.

---

<!-- TYMM_JSON_SHA256:087f9cce20a6ee702a0b52c97963e77a2827a2e04db46d24ad9e05a359b7214e -->
