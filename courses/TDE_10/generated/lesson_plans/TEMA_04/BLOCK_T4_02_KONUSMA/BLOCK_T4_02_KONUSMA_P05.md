# Canlandırmada Hedefli Yeniden Performans ve Konuşma Kapanışı

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

Tema 4 Konuşma bloğunun 9-10. saatlerinde öğrenciler P04'te seçtikleri tek gözlenebilir gelişim hedefi için kısa prova yapar ve aynı canlandırmanın hedefle doğrudan ilişkili kısa bölümünü yeniden oynar. P03 canlı performans kanıtı ile P05 yeniden performans kanıtı yalnız seçilen davranış bakımından karşılaştırılır. Yeni tam DPA puanlaması yapılmaz. Paket sonunda BLOCK_T4_02_KONUSMA 10/10 tamamlanır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`, `T4_ACT_11_CANLANDIRMA_DEGERLENDIRME`
- **Kullanılan formlar:** Yok

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

## 1. Ders — Tek gelişim hedefi için mikro-prova

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`

### Hedef

P04 hedefini aynı sahnenin kısa bölümünde çalışmak ve hedef dışındaki kapsamı değiştirmeden uygulanabilir mikro-düzeltme geliştirmek.

### Derse giriş

P04 hedefi ve P03'teki ilgili performans kanıtı açılır.

### Öğretmenin yapacakları

1. Her grubun yalnız seçtiği tek hedef üzerinde çalışmasını sağla.
2. Kaynak bağlılığı hedefiyse olay/karakter kanıtını; rol geçişiyse sahne sırasını; ses/beden hedefiyse yalnız ilgili icra davranışını çalıştır.
3. Yeni sahne veya yeni olay ekleyerek kapsamı büyütme.
4. İki kısa prova turunda aynı davranışı sınat.

### Öğrencinin yapacakları

- Tek hedefini açar.
- Kısa sahne bölümünü seçer.
- Mikro-düzeltme yapar.
- İki prova turunda aynı davranışı sınar.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`, `T4_ACT_11_CANLANDIRMA_DEGERLENDIRME`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

P03 davranışı → P04 hedefi → mikro-düzeltme → prova gözlemi.

### Kapanış

Yeniden performansta aranacak değişim ölçütü tek cümleyle yazılır.

### Materyaller

- P03 performans kanıtı
- P04 hedef kaydı

## 2. Ders — Kısa yeniden canlandırma ve önce/sonra karşılaştırması

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Aynı sahne bölümünü yeniden oynayıp seçilen hedef davranışta P03'e göre gözlenebilir değişim olup olmadığını kanıtla değerlendirmek.

### Derse giriş

'Bütün performansı yeniden puanlamıyoruz; yalnız seçilen davranışta değişim var mı?' ölçütü netleştirilir.

### Öğretmenin yapacakları

1. Kısa yeniden canlandırmaları yürüt.
2. P03 ve P05 kanıtını yalnız hedef davranışta karşılaştır.
3. Değişim varsa önce/sonra kanıtıyla kaydet; yoksa kullanılan stratejinin neden yetmediğini belirlet.
4. Yeni tam DPA puanlaması yapma.

### Öğrencinin yapacakları

- Seçilen sahne bölümünü yeniden oynar.
- P03 ve P05 performansını hedef davranış açısından karşılaştırır.
- Önce/sonra kanıtını yazar.
- Bir sonraki benzer performansa aktaracağı stratejiyi belirler.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`, `T4_ACT_11_CANLANDIRMA_DEGERLENDIRME`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

P03 önce → P04 hedef → P05 mikro-düzeltme → P05 sonra → değişim kanıtı.

### Kapanış

BLOCK_T4_02_KONUSMA 10/10 tamamlanır.

### Materyaller

- P03/P04/P05 kanıtları

## Öğretmen notu

P05 ikinci summative değerlendirme değildir; geri bildirimden performans değişimine uzanan pedagojik kapanıştır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 0 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T4_ACT_10_CANLANDIRMA_SUNUM`, `T4_ACT_11_CANLANDIRMA_DEGERLENDIRME`
- **Sonraki adım:** BLOCK_T4_02_KONUSMA tamamlandı. Sonraki blok BLOCK_T4_03_DINLEME_P01 olmalıdır.

---

<!-- TYMM_JSON_SHA256:e8b35b787392190d2fcd5f184ef35e133d5fb35a649b5837182b6350e9984c17 -->
