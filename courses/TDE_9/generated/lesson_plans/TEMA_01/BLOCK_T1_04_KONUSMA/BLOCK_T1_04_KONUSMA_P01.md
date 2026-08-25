# Konuşmayı Tasarlamak: Altı Şapka ile Rol, Bakış Açısı ve İkna İçeriği

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

10 saatlik 1. Tema Konuşma Atölyesi bloğunun ilk iki ders saatinde öğrenciler, ders kitabındaki Altı Şapkalı Düşünme Tekniği görevine hazırlanır. İlk saatte konuşma amacı, muhatap, grup düzeni ve şapka rollerinin düşünsel işlevleri çözümlenir; ikinci saatte seçilen role uygun argüman, gerekçe, örnek ve kısa slogan/özet mesaj üretilerek konuşma planı oluşturulur. Bu pakette tam sınıf sunumu yapılmaz; ses, diksiyon, beden dili ve sunum sonrası değerlendirme sonraki paketlere bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`
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

## 1. Ders — Konuşma görevi, muhatap ve şapka rollerini çözümleme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`

### Hedef

Öğrencinin Altı Şapkalı Düşünme Tekniğiyle yürütülecek grup konuşmasının amacını ve muhatabını belirlemesi; şapka rollerinin farklı düşünme işlevlerini ayırt ederek grup içi görev ve konuşma akışını planlaması.

### Derse giriş

Daha önce incelenen deneme metinlerinden hareketle aynı konuya farklı bakış açılarından yaklaşmanın neyi değiştirdiği hatırlatılır. Ardından 'Bir konuşmada herkes aynı bakış açısından düşünürse ne kaybederiz?' sorusu üzerinden Altı Şapkalı Düşünme Tekniğine geçilir.

### Öğretmenin yapacakları

1. Ders kitabı s. 63-65'teki T1_ACT_13 basamaklarını temel alarak konuşma görevinin amacını ve grup yapısını netleştir.
2. Şapka renklerini yalnız ezberletme; kitapta verilen her rolün hangi tür düşünsel katkıyı üretmesi gerektiğini öğrencilerden açıklamalarını iste.
3. Grupların görev dağılımını yapmasını ve her öğrencinin rolünü kendi cümlesiyle tanımlamasını sağla.
4. FORM_IN_T1_KONUSMA_CRITERIA'yı sunum sonrası not çizelgesi gibi değil, hazırlıkta ulaşılması gereken kalite ölçütleri olarak tanıt.
5. Ders sonunda her grubun konuşma amacını, muhatabını, rol dağılımını ve beklenen ortak sonucu kısa plan hâline getirmesini sağla.

### Öğrencinin yapacakları

- Konuşma görevinin amacını ve hedef dinleyiciyi belirler.
- Şapka rollerinin düşünsel işlevlerini birbirinden ayırır.
- Kendi rolünün konuşmaya ne katması gerektiğini açıklar.
- Grup içinde görev ve süre paylaşımı yapar.
- Konuşma ölçütlerinden hazırlık sırasında özellikle dikkat edeceği iki noktayı seçer.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T1_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana kanıt grup konuşma planının ilk bölümüdür: amaç, muhatap, rol dağılımı ve her rolün beklenen katkısı görünür olmalıdır. Öğrencinin yalnız şapka rengini değil rolünün işlevini açıklayabilmesi beklenir.

### Kapanış

Her öğrenci 'Benim şapkamın görevi …; konuşmada bunu … yaparak göstereceğim.' cümlesini tamamlar.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 63-65
- Daha önce incelenen deneme metinleri ve öğrenci notları
- FORM_IN_T1_KONUSMA_CRITERIA — s. 65
- Grup konuşma planı için defter/çalışma alanı

## 2. Ders — Role uygun argüman ve ikna içeriği oluşturma

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`

### Hedef

Öğrencinin seçilen şapka rolünün düşünsel işlevine uygun konuşma içeriği üretmesi; iddia, gerekçe, kanıt/örnek ve kısa etkili mesajları muhatabı dikkate alarak yapılandırması.

### Derse giriş

Gruplardan aynı konu hakkında iki farklı şapka rolünün nasıl farklı cümleler kurabileceğine ilişkin kısa örnek üretmeleri istenir. Böylece rolün yalnız renk değil içerik üretme kuralı olduğu görünür hâle getirilir.

### Öğretmenin yapacakları

1. T1_ACT_13'teki rol yönergelerine göre her öğrencinin kendi bakış açısına uygun en az iki içerik birimi üretmesini sağla.
2. İçeriği 'iddia/görüş → gerekçe → örnek veya dayanak → dinleyiciye etkisi' zinciriyle kurdur.
3. Şapka rolüne aykırı veya genel kalan fikirlerde 'Bu düşünce senin rolünün hangi işlevini yerine getiriyor?' sorusuyla yeniden yapılandırma yaptır.
4. Kitapta istenen özgün slogan/özet karar niteliğindeki kısa etkili ifadeyi ancak grubun temel düşünceleri netleştikten sonra ürettir.
5. Ders sonunda grup üyelerinin içeriklerini sıraya koyarak taslak konuşma akışı oluşturmasını ve tekrarları ayıklamasını sağla.

### Öğrencinin yapacakları

- Rolüne uygun en az iki görüş/argüman üretir.
- Her önemli görüşü gerekçe ve uygun örnek/dayanakla destekler.
- İçeriğini hedef dinleyici açısından anlaşılır ve ikna edici hâle getirir.
- Rolünün işlevine uygun kısa bir slogan veya özet mesaj geliştirir.
- Grup arkadaşlarının içerikleriyle kendi içeriğini birleştirerek taslak konuşma akışı oluşturur.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T1_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana ürün role dayalı konuşma notları ve grup taslak akışıdır. Her öğrencide en az bir görüş, gerekçe/dayanak ve rolüne uygun etkili mesaj bulunması beklenir. Henüz sunum performansı değerlendirilmez.

### Kapanış

Gruplar bir sonraki paket için 'İçeriğimiz hazır; sunumda özellikle … yönünü prova etmemiz gerekiyor.' cümlesiyle prova ihtiyacını belirler.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 63-65
- Grup konuşma planı
- FORM_IN_T1_KONUSMA_CRITERIA — s. 65

## Öğretmen notu

Bu paket BLOCK_T1_04_KONUSMA bloğunun pedagojik olarak tasarlanmış ilk 2 saatidir; resmî MEB saat-saat alt sıralaması değildir. Yeni blokta Yazma continuation state'i taşınmamıştır. Yalnız T1_ACT_13 ve tema içi konuşma ölçüt tablosu kullanılmıştır. Tam sunum, TDE3.3 kapsamındaki ses/diksiyon/beden dili uygulaması ve T1_ACT_14 ile öz-akran-öğretmen değerlendirmesi sonraki paketlere bırakılmıştır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 8 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`
- **Kullanılan etkinlikler:** `T1_ACT_13_KONUSMA_SIRASI`
- **Sonraki adım:** P02'de taslak konuşma içeriğini prova üzerinden işlevsel hâle getir. TDE3.3 doğrultusunda ses tonu, vurgu-tonlama, diksiyon, göz teması, jest-mimik ve süre yönetimini FORM_IN_T1_KONUSMA_CRITERIA ölçütleriyle çalış; tam değerlendirme formlarını sunum sonrası paketlere bırak.

---

<!-- TYMM_JSON_SHA256:6d0c0c9e0374159c1c1005c78af23536751667c27cfcc3be49876910dbd6cb92 -->
