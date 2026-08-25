# Canlandırmayı Değerlendirmek: Öz, Akran ve Resmî Öğretmen Geri Bildirimi

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_10` |
| Tema | `TEMA_04` |
| Blok | `BLOCK_T4_02_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

Tema 4 Konuşma bloğunun 7-8. saatlerinde önce P03'te tamamlanamayan performanslar varsa aynı görev koşullarıyla tamamlanır; ardından T4_ACT_11_CANLANDIRMA_DEGERLENDIRME kapsamında FORM_T4_KONUSMA_OZ ve FORM_T4_KONUSMA_AKRAN kullanılır. LINK_T4_KONUSMA_DPA erişilebiliyorsa resmî öğretmen değerlendirmesi de eklenir. Öz, akran ve öğretmen kanıtları tek bir yapay puanda birleştirilmez; öğrenci P05 için tek gözlenebilir gelişim hedefi seçer.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`, `T4_ACT_11_CANLANDIRMA_DEGERLENDIRME`
- **Kullanılan formlar:** `FORM_T4_KONUSMA_OZ`, `FORM_T4_KONUSMA_AKRAN`, `LINK_T4_KONUSMA_DPA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_T4_KONUSMA_AKRAN` | `USED` |
| `FORM_T4_KONUSMA_OZ` | `USED` |
| `LINK_T4_KONUSMA_DPA` | `USED` |

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
- **Paralel grup sayısı:** 4
- **Gruplama:** Sınıfı 4-6 kişilik paralel performans gruplarına ayır; konuşmacı ve gözlemci rollerini her turda döndür, hiçbir öğrenciyi yalnız gözlemci rolünde bırakma.
- **Öğretmen rotasyonu:** Öğretmen gruplar arasında planlı olarak döner; her öğrenciden en az bir doğrudan performans kanıtı toplar ve diğer kanıtları akran kayıtlarıyla çapraz kontrol eder.
- **Akran gözlemci:** Her gruptaki akran gözlemci yalnız plandaki mevcut performans ölçütlerinden bir güçlü davranış ve bir geliştirme kanıtı kaydeder; kişilik veya genel beğeni yorumu yapmaz.
- **Performans zaman sınırı:** 180 saniye
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

## 1. Ders — Kalan performansları tamamlama ve öz/akran değerlendirmesi

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.4`

### Hedef

Canlandırma performansını gözlenebilir kanıta dayanarak öz ve akran bakışından değerlendirmek.

### Derse giriş

P03 sonunda kalan performans varsa önce tamamlanır.

### Öğretmenin yapacakları

1. Kalan performansları görev koşullarını değiştirmeden tamamlat.
2. FORM_T4_KONUSMA_AKRAN geri bildirimini kişilik veya görüş beğenisine değil sahne davranışına dayandır.
3. FORM_T4_KONUSMA_OZ ile öğrencinin kendi rolünü, kaynak bağlılığını, ses/beden/mekân kullanımını kanıtla değerlendirmesini sağla.
4. Öz ve akran görüşü farklıysa farkın hangi kanıttan doğduğunu sorgulat.

### Öğrencinin yapacakları

- Varsa kalan performansı tamamlar.
- Akran değerlendirmesi yapar.
- Öz değerlendirme yapar.
- Bir güçlü yön ve bir gelişim alanını kanıtla yazar.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`, `T4_ACT_11_CANLANDIRMA_DEGERLENDIRME`
- **Formlar:** `FORM_T4_KONUSMA_OZ`, `FORM_T4_KONUSMA_AKRAN`

### Ölçme / öğrenme kanıtı

öz/akran formu + somut performans kanıtı.

### Kapanış

Bir güçlü davranış ve bir gelişim alanı seçilir.

### Materyaller

- FORM_T4_KONUSMA_OZ
- FORM_T4_KONUSMA_AKRAN
- P03 performans notları

## 2. Ders — Geri bildirim kaynaklarını sentezleyip tek gelişim hedefi seçme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.4`

### Hedef

Öz, akran ve erişilebiliyorsa resmî DPA kanıtlarını karşılaştırıp tek gözlenebilir yeniden performans hedefi belirlemek.

### Derse giriş

Öz/akran kayıtlarının yanına P03 öğretmen gözlemi ve varsa DPA sonucu eklenir.

### Öğretmenin yapacakları

1. Geri bildirim araçlarını tek puanda eritme.
2. Tekrarlanan bulguları ve yalnız bir kaynakta görünen bulguları ayırt ettir.
3. Hedefi 'daha iyi canlandıracağım' gibi genel değil; kaynak bağlılığı, rol geçişi, ses, beden dili, mekân veya sahne akışı gibi gözlenebilir tek davranışa indir.
4. DPA erişilemiyorsa resmî kriter/puan üretmeden hedefi diğer doğrulanmış kanıtlardan çıkar.

### Öğrencinin yapacakları

- Geri bildirimleri karşılaştırır.
- Tekrarlanan bulguları belirler.
- Tek gözlenebilir P05 hedefi seçer.
- Hedefini önceki performans kanıtıyla gerekçelendirir.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_11_CANLANDIRMA_DEGERLENDIRME`
- **Formlar:** `FORM_T4_KONUSMA_OZ`, `FORM_T4_KONUSMA_AKRAN`, `LINK_T4_KONUSMA_DPA`

### Ölçme / öğrenme kanıtı

geri bildirim kaynağı → kanıt → tek P05 hedefi.

### Kapanış

P05'te yeniden oynanacak kısa sahne bölümü ve gözlenecek davranış belirlenir.

### Materyaller

- Öz/akran formları
- P03 öğretmen gözlemi
- Varsa resmî DPA

## Öğretmen notu

Auth-gated DPA kriterleri türetilmez; araçların kanıt işlevleri ayrı tutulur.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 2 saat
- **Kapsanan çıktılar:** `TDE3.4`
- **Kullanılan etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`, `T4_ACT_11_CANLANDIRMA_DEGERLENDIRME`
- **Sonraki adım:** P05'te tek hedef için kısa prova + aynı sahnenin hedefle ilişkili kısa bölümünün yeniden performansı ile bloğu kapat.

---

<!-- TYMM_JSON_SHA256:05fda282dfd19db190d55ff66cc530410550337cc7f76a6ee72ad38ebc4f078f -->
