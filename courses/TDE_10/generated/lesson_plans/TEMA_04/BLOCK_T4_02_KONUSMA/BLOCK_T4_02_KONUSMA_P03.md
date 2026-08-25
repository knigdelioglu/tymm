# Dede Korkut Canlandırması: Canlı Performans ve Kaynaklı Gözlem

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

Tema 4 Konuşma bloğunun 5-6. saatlerinde T4_ACT_10_CANLANDIRMA_SUNUM kapsamında canlı canlandırmalar yürütülür. Her performansta sahne akışı, kaynak olay/karakter bağlılığı, içerik uygunluğu, Türkçe kullanımı, ses-vurgu-tonlama, beden dili, mekân ve görsel/işitsel ögelerin işlevi gözlenir. LINK_T4_KONUSMA_DPA erişilebiliyorsa resmî araç aynen kullanılır; auth-gated yapı görülmüyorsa kriter veya puanlama modeli uydurulmaz. Sınıf mevcudu varsayılmaz; tamamlanamayan performanslar P04 başına taşınabilir.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`
- **Kullanılan formlar:** `LINK_T4_KONUSMA_DPA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_T4_KONUSMA_AKRAN` | `REFERENCE_ONLY` |
| `FORM_T4_KONUSMA_OZ` | `REFERENCE_ONLY` |
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

## 1. Ders — Canlı canlandırma rotasyonunu başlatma

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`

### Hedef

Planlanan Dede Korkut sahnesini kaynak bağlılığı ve sözlü/bedensel icra kurallarıyla canlı olarak sunmak.

### Derse giriş

P02'deki tek canlı performans hedefi görünür hâle getirilir.

### Öğretmenin yapacakları

1. Canlı performans rotasyonunu başlat.
2. Kaynak olay/karakter bilgisinin korunmasını ve yaratıcı uyarlamanın özgün metin bilgisi gibi sunulmamasını gözle.
3. Ses, akıcılık, Türkçe kullanımı, beden dili, mekân ve destek ögeleri için somut kanıt notu tut.
4. Resmî DPA erişilebiliyorsa aynen uygula; erişilemiyorsa kriter/puan uydurma.

### Öğrencinin yapacakları

- Canlandırmayı sunar.
- Kaynak bağlılığını korur.
- Ses, beden dili ve mekânı yönetir.
- Görsel/işitsel ögeleri işlevsel kullanır.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`
- **Formlar:** `LINK_T4_KONUSMA_DPA`

### Ölçme / öğrenme kanıtı

canlı performans kanıtı + erişilebiliyorsa resmî DPA kaydı.

### Kapanış

Sunum yapan grup hedef davranışına ilişkin tek cümlelik sıcak kayıt bırakır.

### Materyaller

- Canlandırma planı
- Varsa resmî DPA
- Sahne materyalleri

## 2. Ders — Canlandırma rotasyonunu sürdürme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`

### Hedef

Aynı görev ve gözlem standardıyla canlı performansları sürdürmek ve eksik performansları varsayımla tamamlamamak.

### Derse giriş

İlk saatteki aynı görev ve gözlem standardı korunur.

### Öğretmenin yapacakları

1. Performans rotasyonunu sürdür.
2. Gruplar arasında görev/ölçüt standardını değiştirme.
3. Tamamlanamayan performansları değerlendirilmiş sayma; P04 başına aktar.
4. DPA auth-gated ise resmî puanı beklemede tut.

### Öğrencinin yapacakları

- Canlı performansını gerçekleştirir.
- Planlanan hedef davranışı uygular.
- Performans sonrası ayrıntılı öz/akran değerlendirmeyi P04'e bırakır.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`
- **Formlar:** `LINK_T4_KONUSMA_DPA`

### Ölçme / öğrenme kanıtı

canlı performans ve somut öğretmen gözlem notları.

### Kapanış

Tamamlanan/kalan performanslar belirlenir.

### Materyaller

- Sahne planları
- Varsa resmî DPA

## Öğretmen notu

Auth-gated DPA'nın görünmeyen kriterleri veya puan düzeyleri hiçbir şekilde türetilmez.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 4 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`
- **Sonraki adım:** P04'te varsa kalan performansları tamamla; sonra FORM_T4_KONUSMA_OZ, FORM_T4_KONUSMA_AKRAN ve erişilebiliyorsa DPA ile tek gelişim hedefi çıkar.

---

<!-- TYMM_JSON_SHA256:f1f75d56f59424ee0c7ff75b78ccf45ac2470f267dc24e96fc28629a9240deba -->
