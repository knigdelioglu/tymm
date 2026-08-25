# Türk Destanları Sunumunu Değerlendirmek: Öz, Akran ve Resmî DPA Kanıtlarını Birleştirmek

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_10` |
| Tema | `TEMA_03` |
| Blok | `BLOCK_T3_02_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

Tema 3 Konuşma bloğunun 7-8. saatlerinde T3_ACT_10_KONUSMA_OZ_AKRAN kullanılır. P03'te kalan sunumlar varsa önce tamamlanır. Ardından FORM_T3_KONUSMA_OZ ve FORM_T3_KONUSMA_AKRAN ile kanıta dayalı değerlendirme yapılır. LINK_T3_KONUSMA_DPA öğretmen tarafından erişilebiliyorsa resmî EBA aracı aynen kullanılır; hedef yapısı auth-gated olduğu için kriter/seviye/puan uydurulmaz. Öğrenci P05 için tek gözlenebilir gelişim hedefi seçer.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T3_ACT_09_DESTAN_SUNUM`, `T3_ACT_10_KONUSMA_OZ_AKRAN`
- **Kullanılan formlar:** `FORM_T3_KONUSMA_OZ`, `FORM_T3_KONUSMA_AKRAN`, `LINK_T3_KONUSMA_DPA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_T3_KONUSMA_AKRAN` | `USED` |
| `FORM_T3_KONUSMA_OZ` | `USED` |
| `LINK_T3_KONUSMA_DPA` | `USED` |

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
- **Uygulandığı dersler:** `1`
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

## 1. Ders — Kalan sunumlar, öz ve akran değerlendirme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Canlı performansı somut kanıtlarla öz ve akran bakışından değerlendirmek.

### Derse giriş

Varsa P03'ten kalan sunumlar aynı görev koşullarıyla tamamlanır.

### Öğretmenin yapacakları

1. FORM_T3_KONUSMA_AKRAN'da genel beğeni yerine gözlenebilir performans kanıtı iste.
2. FORM_T3_KONUSMA_OZ ile öğrencinin kendi içerik, akış ve icra kanıtını incelemesini sağla.
3. Öz ve akran görüşü ayrışıyorsa farkı kanıtla açıklat.

### Öğrencinin yapacakları

- Varsa sunumunu tamamlar.
- Akran değerlendirmesi yapar.
- Öz değerlendirme yapar.
- Bir güçlü yön ve bir gelişim alanını kanıtla belirler.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_09_DESTAN_SUNUM`, `T3_ACT_10_KONUSMA_OZ_AKRAN`
- **Formlar:** `FORM_T3_KONUSMA_OZ`, `FORM_T3_KONUSMA_AKRAN`

### Ölçme / öğrenme kanıtı

Öz/akran formu + somut performans dayanağı.

### Kapanış

Bir güçlü yön ve bir gelişim alanı yazılır.

### Materyaller

- FORM_T3_KONUSMA_OZ
- FORM_T3_KONUSMA_AKRAN

## 2. Ders — Resmî DPA ve tek gelişim hedefi

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.4`

### Hedef

Resmî öğretmen değerlendirmesi ile öz/akran kanıtlarını karşılaştırarak P05 için tek gözlenebilir hedef seçmek.

### Derse giriş

Öz/akran kayıtlarının yanına öğretmen performans kanıtı eklenir.

### Öğretmenin yapacakları

1. LINK_T3_KONUSMA_DPA erişilebiliyorsa resmî aracı aynen kullan.
2. Erişilemiyorsa kriter, seviye veya puan uydurma; resmî puanı beklemede bırak.
3. Farklı değerlendirme araçlarını tek yapay puana dönüştürme.
4. P05 hedefini tek gözlenebilir davranışa indir.

### Öğrencinin yapacakları

- Geri bildirim kaynaklarını karşılaştırır.
- Tekrarlanan bulguları belirler.
- P05 için tek gözlenebilir gelişim hedefi seçer ve mevcut kanıtla gerekçelendirir.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_10_KONUSMA_OZ_AKRAN`
- **Formlar:** `FORM_T3_KONUSMA_OZ`, `FORM_T3_KONUSMA_AKRAN`, `LINK_T3_KONUSMA_DPA`

### Ölçme / öğrenme kanıtı

geri bildirim kaynağı → kanıt → tek gelişim hedefi.

### Kapanış

Hedef, P05'te gözlenecek değişiklikle yazılır.

### Materyaller

- Öz/akran formları
- LINK_T3_KONUSMA_DPA

## Öğretmen notu

Auth-gated resmî DPA yapısı çıkarılamadığı için hiçbir kriter tahmin edilmez.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 2 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T3_ACT_09_DESTAN_SUNUM`, `T3_ACT_10_KONUSMA_OZ_AKRAN`
- **Sonraki adım:** P05'te yalnız seçilen tek hedef için kısa prova ve yeniden performans yaparak bloğu 10/10 kapat.

---

<!-- TYMM_JSON_SHA256:fc6ab5c89958f3242e36e314089c7930faf4f6d6662bd878ba81e6915e37691b -->
