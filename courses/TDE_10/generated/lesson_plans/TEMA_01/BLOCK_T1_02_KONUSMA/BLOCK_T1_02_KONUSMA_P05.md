# Geri Bildirimden Yeniden Performansa: Şiir Dinletisi Hedefli Kapanış

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_10` |
| Tema | `TEMA_01` |
| Blok | `BLOCK_T1_02_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

Tema 1 Konuşma bloğunun 9. ve 10. saatlerinde öğrenciler P04'te seçtikleri tek gözlenebilir gelişim hedefini kısa prova ve yeniden performansla sınar. İlk saatte yalnız hedef davranış üzerinde mikro-düzeltme yapılır; bütün dinleti yeniden kurgulanmaz. İkinci saatte grubun dinletisinden hedefle doğrudan ilişkili kısa bir bölüm yeniden icra edilir ve önce/sonra kanıtı karşılaştırılır. Yeni bir resmî DPA puanı veya kriter seti üretilmez. Bu paket sonunda BLOCK_T1_02_KONUSMA 10/10 saat tamamlanır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T1_ACT_09_SIIR_DINLETISI_SUNUM`, `T1_ACT_10_KONUSMA_DEGERLENDIRME`
- **Kullanılan formlar:** `FORM_T1_KONUSMA_AKRAN`, `LINK_T1_KONUSMA_DPA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_T1_KONUSMA_AKRAN` | `USED` |
| `LINK_T1_KONUSMA_DPA` | `USED` |

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

## 1. Ders — Tek gelişim hedefi için mikro-prova ve düzeltme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Grubun P04'te seçtiği tek gelişim hedefini dinletinin ilgili bölümünde çalışması ve hedefe yönelik uygulanabilir bir mikro-düzeltme geliştirmesi.

### Derse giriş

P04 hedef kaydı açılır. Grup 'Değiştireceğimiz tek davranış nedir ve bunu hangi performans kanıtı nedeniyle seçtik?' sorusunu yanıtlar.

### Öğretmenin yapacakları

1. Her grubun yalnız seçtiği tek hedef üzerinde çalışmasını sağla; bütün dinletiyi yeniden tasarlatıp odağı dağıtma.
2. Hedef akış/geçiş ise ilgili geçişi; süre ise ilgili bölümü; ses/söyleyiş ise seçilen okuma kesitini; beden dili ise aynı kesitteki göz teması/duruşu; grup koordinasyonu ise görev geçişini çalıştır.
3. Hedef Türkçe kullanımıysa yalnız sunucu/geçiş dilini düzenlet; şiir metninin özgün dilini keyfî biçimde değiştirtme.
4. Birinci mikro-prova sonrası yalnız hedef davranışa ilişkin öz gözlem yaptır.
5. Gerekirse tek ek düzeltme yaptır ve ikinci kısa provada aynı davranışı yeniden sınat.
6. İkinci saat için yeniden icra edilecek kısa bölümü ve gözlenecek davranışı kaydettir.

### Öğrencinin yapacakları

- P04 hedefini ve kanıtını yeniden okur.
- Hedefle ilgili dinleti bölümünü seçer.
- Tek mikro-düzeltme uygular.
- Kısa prova yapar ve hedef davranışı gözler.
- Yeniden performansta hangi değişimin aranacağını belirler.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_09_SIIR_DINLETISI_SUNUM`, `T1_ACT_10_KONUSMA_DEGERLENDIRME`
- **Formlar:** `FORM_T1_KONUSMA_AKRAN`, `LINK_T1_KONUSMA_DPA`

### Ölçme / öğrenme kanıtı

'P03/P04 mevcut kanıt → P04 hedefi → mikro-düzeltme → prova gözlemi' kaydı.

### Kapanış

Grup 'Yeniden performansta ... davranışında ... değişimini arayacağız; yaptığımız mikro-düzeltme ...' cümlesini tamamlar.

### Materyaller

- P04 geri bildirim sentezi
- P01-P02 dinleti planı
- Kısa prova alanı

## 2. Ders — Kısa yeniden performans, önce/sonra kanıtı ve konuşma bloğunu kapatma

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.3`, `TDE3.4`

### Hedef

Grubun aynı dinletinin hedefle ilgili kısa bölümünü yeniden icra etmesi; yalnız seçilen davranış bakımından önce/sonra kanıtını karşılaştırması ve konuşma sürecini yansıtması.

### Derse giriş

Ölçüt tek cümleyle netleştirilir: 'Bütün dinletiyi yeniden puanlamıyoruz; yalnız seçtiğimiz davranışta önceye göre gözlenebilir değişim var mı?'

### Öğretmenin yapacakları

1. Grupların hedefle ilgili kısa bölümü yeniden icra etmesini sağla; sabit dakika uydurma, sınıf koşullarına göre kısa ve karşılaştırılabilir bir kesit kullan.
2. Yalnız seçilen davranış için önceki ve yeni performans kanıtını karşılaştır.
3. Değişim varsa 'önceki kanıt → yeni kanıt → değişimin yönü' biçiminde kaydet.
4. Değişim yoksa başarısızlık etiketi yerine kullanılan mikro-stratejinin neden yeterli olmadığını belirlet.
5. Yeni bir LINK_T1_KONUSMA_DPA kriter seti veya ikinci tam resmî puanlama oluşturma; erişilmiş resmî değerlendirme varsa önceki kayıt olarak koru.
6. Saat sonunda Tema 1 Konuşma bloğunu 10/10 saat kapat ve Dinleme/İzleme bloğuna yalnız süreç geçişi yap.

### Öğrencinin yapacakları

- Seçilen dinleti bölümünü yeniden icra eder.
- Önce/sonra performans kanıtını karşılaştırır.
- Değişimin yönünü gerekçelendirir.
- Değişim yoksa alternatif strateji belirler.
- Şiir dinletisi sürecinden bir aktarılabilir konuşma stratejisi çıkarır.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_09_SIIR_DINLETISI_SUNUM`, `T1_ACT_10_KONUSMA_DEGERLENDIRME`
- **Formlar:** `FORM_T1_KONUSMA_AKRAN`, `LINK_T1_KONUSMA_DPA`

### Ölçme / öğrenme kanıtı

Kapanış kanıtı 'önceki performans → geri bildirim → tek hedef → mikro-düzeltme → yeniden performans → gözlenen değişim' zinciridir.

### Kapanış

Grup 'İlk performansta ... görülüyordu; ... stratejisini uyguladık; yeniden performansta ... kanıtı ... yönde değişim olduğunu gösterdi.' cümlesiyle bloğu kapatır.

### Materyaller

- P03-P04 performans/geri bildirim kayıtları
- P05 mikro-prova kaydı
- Dinleti planı

## Öğretmen notu

P05 pedagojik geri bildirim döngüsü kapanışıdır. Resmî DPA'nın authentication-gated yapısı nedeniyle kriter veya puanlama modeli türetilmez. P05 sonunda Tema 1 Konuşma bloğu 10/10 tamamlanır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 0 saat
- **Kapsanan çıktılar:** `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T1_ACT_09_SIIR_DINLETISI_SUNUM`, `T1_ACT_10_KONUSMA_DEGERLENDIRME`
- **Sonraki adım:** BLOCK_T1_02_KONUSMA tamamlandı. Sonraki paket BLOCK_T1_03_DINLEME_P01 olmalıdır; T1_ACT_11_MASAL_HAZIRLIK ve Mercan Kız kaynakları fresh-read edilmelidir.

---

<!-- TYMM_JSON_SHA256:6135572cae1ce57ff77b7a3dc6ed1f929ec9d4e655489b04a1da8c7c839fc754 -->
