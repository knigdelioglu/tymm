# Benim Mekânım Kapanışı: Tek Hedefli Prova, Yeniden Performans ve Kanıtlı Yansıtma

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_9` |
| Tema | `TEMA_03` |
| Blok | `BLOCK_T3_02_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

10 saatlik 3. Tema Konuşma Atölyesi bloğunun 9. ve 10. ders saatlerinde öğrenciler P04'te akran, öz, öğretmen gözlemi ve approved rubrik geri bildiriminden seçtikleri tek somut iyileştirme hedefini uygular. İlk saatte yalnız hedeflenen davranış için kısa, kontrollü prova yapılır; ikinci saatte Benim Mekânım sunumunun hedefle ilgili 45-90 saniyelik bölümü yeniden gerçekleştirilir. İlk canlı sunumdaki kanıt ile yeniden performanstaki kanıt karşılaştırılır ve öğrenci değişikliğin etkisini kısa yansıtmayla açıklar. Yeni puanlama sistemi, yeni form veya yeni resmî ölçüt üretilmez; konuşma bloğu 10/10 saat kapatılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`, `T3_ACT_09_KONUSMA_SONRASI`
- **Kullanılan formlar:** Yok

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| — | — |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE9_KONUSMA_RUBRIC` | `MAT_T3_KONUSMA_RUBRIC` | `DEFERRED` |

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

## 1. Ders — Tek iyileştirme hedefi için kontrollü prova ve mikro-düzeltme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Öğrencinin P04'te seçtiği tek gözlenebilir iyileştirme hedefini sunumun ilgili bölümünde denemesi; aynı anda çok sayıda davranışı değiştirmek yerine hedef davranış için bir veya iki mikro-düzeltme yapması.

### Derse giriş

Öğrenci P04 hedefini tek cümlede okur ve P03'te bu hedefe ilişkin ilk performans kanıtını yanına yazar. 'Tam olarak hangi davranışı değiştireceğim ve bunu dışarıdan nasıl görebileceğiz?' sorusu prova ölçütünü belirler.

### Öğretmenin yapacakları

1. Öğrenciden P04'te seçtiği tek hedefi korumasını iste; aynı provada bütün rubrik boyutlarını düzeltmeye çalışma.
2. Hedefi sunumun 45-90 saniyelik ilgili bölümüne bağla: karşılaştırma kanıtı, sonuç örgüsü, görsel geçişi, ses-vurgu-tonlama, beden dili veya süre yönetimi gibi.
3. İlk kısa provadan sonra yalnız hedef davranışa ilişkin bir somut geri bildirim ver veya öğrencinin kendi kaydından bulmasını iste.
4. İkinci provada en fazla bir veya iki mikro-düzeltme uygulat; içerik hedefiyse kanıt/bağlantı, performans hedefiyse gözlenebilir ses-beden-süre davranışı değişsin.
5. Approved TDE9_KONUSMA_RUBRIC'i yeni bir tam puanlama turu olarak kullanma; yalnız P03-P04'teki ölçüt kanıtıyla hedeflenen davranışın ilişkisini koru.
6. Provanın amacı ezberlenmiş kusursuz metin üretmek değil, geri bildirimi bilinçli performans değişikliğine dönüştürmektir.

### Öğrencinin yapacakları

- P04'te seçtiği tek iyileştirme hedefini ve ilk performans kanıtını yazar.
- Sunumun hedefle ilgili 45-90 saniyelik bölümünü kısa prova eder.
- İlk provada hedef davranışın nerede güçlenmediğini gözler.
- Bir veya iki mikro-düzeltme yapar.
- İkinci provada aynı bölümü yeniden deneyerek değişikliği gözlenebilir hâle getirir.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`, `T3_ACT_09_KONUSMA_SONRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Ana kanıt 'P03/P04 ilk davranış kanıtı → seçilen hedef → prova 1 → mikro-düzeltme → prova 2' kaydıdır. Başarı, bütün sunumu kusursuzlaştırmak değil seçilen tek davranışta gerekçeli ve gözlenebilir değişiklik oluşturmaktır.

### Kapanış

Öğrenci 'İlk performansta ... görünüyordu. Provada ... değiştirdim; ikinci denemede ... gözlenebilir hâle geldi.' ifadesini tamamlar.

### Materyaller

- P04 değerlendirme sentezi ve tek iyileştirme hedefi
- P03 canlı sunum/rubrik kanıtı
- Benim Mekânım sunum materyali
- Kısa prova gözlem kaydı

## 2. Ders — Kısa yeniden performans, önce-sonra karşılaştırması ve konuşma bloğu kapanışı

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Öğrencinin hedefle ilgili sunum bölümünü yeniden gerçekleştirmesi; ilk canlı performans ile yeni performansı aynı gözlenebilir davranış üzerinden karşılaştırması ve geri bildirimi nasıl kullandığını kanıta dayalı biçimde yansıtması.

### Derse giriş

İlk saat prova kaydı ve P03 ilk performans kanıtı yan yana getirilir. Öğrenci yeniden performansa 'Aynı davranışın önceki ve yeni hâlini karşılaştıracağım.' amacıyla girer.

### Öğretmenin yapacakları

1. Her öğrencinin yalnız seçtiği hedefle ilgili 45-90 saniyelik bölümü yeniden gerçekleştirmesini sağla; sınıf koşullarına göre bireysel, küçük grup veya rotasyon biçimi kullanılabilir.
2. Önce ve sonra kanıtını aynı ölçüt/davranış üzerinden karşılaştır; hedef dışı yeni ölçütlerle öğrenciyi tekrar değerlendirme.
3. Değişiklik gözlenmiyorsa bunu başarısızlık etiketi olarak kullanma; hangi mikro-düzeltmenin etkisiz kaldığını kanıtla belirlet ve sonraki sunuma aktarılacak hedef olarak kaydet.
4. Öğrenciden geri bildirimin hangi kaynaktan geldiğini ve hangi davranış değişikliğine yol açtığını açıklamasını iste.
5. T3_ACT_09'un yansıtma amacını bu kapanışta kullan; yeni öz/akran formu doldurtma ve yeni resmî puan üretme.
6. Saat sonunda BLOCK_T3_02_KONUSMA'yı kapat; Tema 3 Dinleme/İzleme içeriğine aynı saatte geçme.

### Öğrencinin yapacakları

- Hedefle ilgili sunum bölümünü yeniden gerçekleştirir.
- İlk performans ile yeniden performanstan aynı davranışa ilişkin iki kanıt seçer.
- Değişikliğin işe yarayıp yaramadığını kanıtla açıklar.
- Geri bildirimin hangi kaynaktan geldiğini ve hangi değişikliği tetiklediğini belirtir.
- Bir sonraki sözlü sunuma taşıyacağı tek stratejiyi kısa cümleyle kaydeder.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`, `T3_ACT_09_KONUSMA_SONRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Ana ürün önce-sonra performans kanıtıdır: 'ilk performans göstergesi → geri bildirim/hedef → yapılan değişiklik → yeniden performans göstergesi → sonuç'. Değişikliğin olumlu olması kadar öğrencinin kanıtla neden işe yarayıp yaramadığını açıklaması da kabul edilir.

### Kapanış

Öğrenci 'Geri bildirimden sonra ... davranışını ... biçimde değiştirdim. Önce ... iken şimdi ...; sonraki sunumda ... stratejisini koruyacağım.' cümlesiyle bloğu kapatır.

### Materyaller

- P03 ilk canlı performans kanıtı
- P04 akran/öz/öğretmen geri bildirim sentezi
- P05 ilk saat prova kaydı
- Benim Mekânım sunum materyali

## Öğretmen notu

Bu paket BLOCK_T3_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 9. ve 10. saatleridir; resmî MEB saat-saat alt sıralaması değildir. T3_ACT_08 canlı sunum görevini, T3_ACT_09 ise öz/akran değerlendirme ve yansıtmayı sağlar. P05 bu kaynakları yeni değerlendirme aracı üretmeden geri bildirimi performans değişikliğine dönüştürmek için kullanır. Approved TDE9_KONUSMA_RUBRIC'in P03-P04 kanıtı korunur; tam puanlama tekrarlanmaz. Paket sonunda Konuşma bloğu 10/10 saat tamamlanır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 0 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`, `T3_ACT_09_KONUSMA_SONRASI`
- **Sonraki adım:** BLOCK_T3_02_KONUSMA tamamlandı. Sonraki üretim paketi TEMA_03 / BLOCK_T3_03_DINLEME / P01 — 2 saattir. P01'de yalnız T3_ACT_10_DINLEME_ONCESI_VE_SIRASI kapsamında Nevruz Belgeseli için izleme amacı, kontrol listesi, ilk/ikinci izleme ve yapılandırılmış not alma yürütülmeli; T3_ACT_11 kültürel bellek tahlili P02'ye bırakılmalıdır.

---

<!-- TYMM_JSON_SHA256:8f43f3cd3f0afb645a343883d3e7017c886213a9af3f9d5ac274f1a9035816cc -->
