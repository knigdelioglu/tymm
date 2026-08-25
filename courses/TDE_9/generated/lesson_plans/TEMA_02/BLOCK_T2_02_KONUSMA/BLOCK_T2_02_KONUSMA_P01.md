# Karakterden Konuşma Amacına: Seçim, Yorum ve Sunum Planı

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

10 saatlik 2. Tema Konuşma Atölyesi bloğunun ilk iki ders saatinde öğrenciler T2_ACT_08_KONUSMA_SIRASI kapsamında ‘Bir Kavak ve İnsanlar’ hikâyesinden bir karakter seçer, karaktere ilişkin metin kanıtlarını kendi yorumlarından ayırır ve hazırlıklı konuşmanın amacını, hedef dinleyicisini, stratejisini ve ana düşüncesini planlar. İkinci saatte karakterin özellikleri, eylemleri ve değişimi konuşma içeriğinin omurgasına dönüştürülür. Canlı performans, ses-diksiyon, beden dili ve değerlendirme formları sonraki paketlere bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`
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

## 1. Ders — Karakter seçimi, konuşma amacı ve strateji belirleme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`

### Hedef

Öğrencinin hikâyeden seçtiği karakteri metin kanıtlarıyla gerekçelendirmesi; bu karakter hakkında yapacağı hazırlıklı konuşmanın amacını, hedef dinleyicisini ve konuşma stratejisini belirlemesi.

### Derse giriş

Okuma bloğunda oluşturulan kişi çözümleme kayıtlarına dönülür. ‘Bir karakteri yalnız tanıtmak ile onun yolculuğuna kendi yorumunu katmak arasında ne fark vardır?’ sorusuyla konuşma görevinin amacı açılır.

### Öğretmenin yapacakları

1. Ders kitabı s. 125-128'deki T2_ACT_08_KONUSMA_SIRASI basamaklarını temel al.
2. Öğrenciden ‘Bir Kavak ve İnsanlar’ hikâyesinden bir karakter seçmesini ve seçimini en az iki metin göstergesiyle gerekçelendirmesini iste.
3. Karakter hakkında metinde açıkça verilen bilgi ile öğrencinin yorumunu ayrı sütunlarda tuttur; yorumun metinle çelişmemesini sağla.
4. Konuşma amacını ‘karakteri anlatacağım’ düzeyinde bırakma; karakterin hangi yönünü, değişimini veya çatışmasını görünür kılmak istediğini netleştir.
5. Hedef dinleyici ve sunum koşuluna göre bir konuşma stratejisi seçtir; seçimin neden uygun olduğunu kısa gerekçeyle yazdır.
6. FORM_IN_T2_KONUSMA_CRITERIA'yı puan vermek için değil, hazırlıkta ulaşılacak performans ölçütlerini önceden görmek için kullandır.

### Öğrencinin yapacakları

- Hikâyeden bir karakter seçer.
- Seçimini iki metin göstergesiyle gerekçelendirir.
- Metinde açıkça verilen karakter bilgileriyle kendi yorumunu ayırır.
- Konuşma amacını ve hedef dinleyiciyi belirler.
- Kullanacağı konuşma stratejisini seçer ve gerekçelendirir.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T2_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana kanıt ‘karakter → iki metin göstergesi → benim yorumum → konuşma amacı → strateji’ planıdır. Karakter tercihi estetik beğeniye göre değişebilir; değerlendirme seçimin metin kanıtı ve konuşma amacıyla ilişkilendirilmesine dayanır.

### Kapanış

Öğrenci ‘Bu karakter üzerinden dinleyiciye özellikle … göstermek istiyorum; çünkü metindeki … ve … göstergeleri bunu destekliyor.’ cümlesini tamamlar.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 125-129
- ‘Bir Kavak ve İnsanlar’ — Tarık Buğra
- Tema 2 Okuma kişi/olay çözümleme kayıtları
- FORM_IN_T2_KONUSMA_CRITERIA — s. 129

## 2. Ders — Karakter yorumunu ana düşünce etrafında konuşma planına dönüştürme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`

### Hedef

Öğrencinin karaktere ilişkin metin kanıtlarını ve kendi yorumunu ana düşünce etrafında düzenlemesi; konuşmanın giriş-gelişme-sonuç akışını ve destekleyici içerik birimlerini planlaması.

### Derse giriş

Birinci dersteki karakter seçimleri açılır. ‘Karakter hakkında bildiğimiz her şeyi söylemek mi, yoksa tek bir ana düşünceyi destekleyen ayrıntıları seçmek mi daha etkili bir sunum üretir?’ sorusuyla içerik seçimine geçilir.

### Öğretmenin yapacakları

1. T2_ACT_08'in karakteri yeniden kurgulama ve sunum hazırlama yönergelerini temel al.
2. Her öğrenciden konuşmasının karaktere ilişkin tek bir ana düşüncesini yazmasını iste; destekleyici ayrıntıları bu düşünceye hizmet edip etmediğine göre seçtir.
3. İçeriği ‘metin kanıtı → öğrenci yorumu → ana düşünceye katkı’ zinciriyle kurdur.
4. Konuşmayı giriş-gelişme-sonuç akışına yerleştir; girişte karakter ve amaç, gelişmede seçilmiş kanıt/yorumlar, sonuçta karaktere ilişkin bütüncül yorum yer alsın.
5. Ders kitabındaki görsel/estetik kurgu hazırlığına zemin oluşturmak için sunumda hangi düşüncenin görselle desteklenebileceğini belirlet; görsel üretimini P02'ye bırak.

### Öğrencinin yapacakları

- Karaktere ilişkin ana düşünce oluşturur.
- Ana düşünceyi destekleyen metin kanıtlarını seçer.
- Kendi yorumunu metin kanıtından ayırarak konuşmaya yerleştirir.
- Giriş-gelişme-sonuç akışını planlar.
- Görselle desteklenebilecek bir içerik noktasını belirler.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T2_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana ürün karakter sunum planıdır: ana düşünce, en az iki kanıt/yorum bağlantısı ve giriş-gelişme-sonuç akışı görünür olmalıdır. Ayrıntı sayısından çok içerik seçiminin ana düşünceye hizmet etmesi değerlendirilir.

### Kapanış

Öğrenci ‘Konuşmamın ana düşüncesi …; bunu … ve … üzerinden geliştireceğim.’ cümlesini tamamlar.

### Materyaller

- 9. sınıf Türk Dili ve Edebiyatı ders kitabı s. 125-128
- P01 karakter seçimi ve amaç notları
- FORM_IN_T2_KONUSMA_CRITERIA — s. 129

## Öğretmen notu

Bu paket BLOCK_T2_02_KONUSMA bloğunun pedagojik olarak tasarlanmış ilk 2 saatidir; resmî MEB saat-saat alt sıralaması değildir. Yeni blokta Okuma continuation state'i taşınmamıştır. T2_ACT_08 ve FORM_IN_T2_KONUSMA_CRITERIA hazırlık amacıyla kullanılmıştır. Canlı sunum, TDE3.3 performans ölçütleri ve T2_ACT_09 değerlendirme süreci sonraki paketlere bırakılmıştır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 8 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`
- **Kullanılan etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`
- **Sonraki adım:** P02'de karakter yorumunu zenginleştir: ders kitabındaki özdeşleştirme/sınıflandırma ve görsel tasarım yönergelerini kullanarak içerik seçimini tamamla; ardından FORM_IN_T2_KONUSMA_CRITERIA ölçütleriyle kısa prova döngülerine geç. Tam sınıf performansını P03'e bırak.

---

<!-- TYMM_JSON_SHA256:e491feaebfbbaa82110309b90ef0545546d20ccee299eeea734c3aa271726a34 -->
