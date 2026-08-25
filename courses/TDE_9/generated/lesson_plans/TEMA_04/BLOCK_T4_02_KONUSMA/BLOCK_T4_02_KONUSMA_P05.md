# Geri Bildirimi Performans Değişimine Dönüştürmek: Hedefli Prova ve Yeniden Sunum

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

10 saatlik 4. Tema Konuşma Atölyesi bloğunun 9. ve 10. ders saatlerinde öğrenciler P04'te seçtikleri tek gözlenebilir gelişim hedefini T4_ACT_08_KONUSMA_SIRASI ve T4_ACT_09_KONUSMA_SONRASI bağlamında performans değişimine dönüştürür. İlk saatte yalnız seçilen hedef için kısa ve kontrollü prova yapılır; konuşmanın bütünü yeniden yazılmaz ve yeni konu eklenmez. İkinci saatte öğrenciler aynı Dilimizin Zenginlikleri konuşmasının hedefle doğrudan ilişkili 45-90 saniyelik bölümünü yeniden icra eder. P03 performans kanıtı ile P05 yeniden performans kanıtı karşılaştırılır; değişim varsa hangi davranışta ve hangi gözlenebilir kanıtla ortaya çıktığı, yoksa hangi stratejinin yeniden düzenlenmesi gerektiği kaydedilir. Yeni kapsamlı rubrik puanı üretilmez; amaç mevcut geri bildirimin öğrenme döngüsünü kapatmasıdır. Saat sonunda BLOCK_T4_02_KONUSMA 10/10 saat tamamlanır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`, `T4_ACT_09_KONUSMA_SONRASI`
- **Kullanılan formlar:** Yok

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_IN_T4_DINLEME_GOZLEM` | `DEFERRED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE9_KONUSMA_RUBRIC` | `MAT_T4_KONUSMA_RUBRIC` | `USED` |

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

## 1. Ders — Tek gelişim hedefi için kontrollü prova ve mikro-düzeltme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Öğrencinin P04'te seçtiği tek gözlenebilir gelişim hedefini mevcut konuşmanın ilgili bölümünde çalışması; hedefe uymayan geniş çaplı değişiklikler yapmadan bir mikro-düzeltme stratejisi geliştirip prova etmesi.

### Derse giriş

P04 hedef kaydı açılır. Öğrenci 'Değiştireceğim tek davranış nedir ve bunu P03'te hangi kanıt nedeniyle seçtim?' sorusuna cevap verir; konuşma konusu ve ana düşünce değiştirilmez.

### Öğretmenin yapacakları

1. Her öğrencinin yalnız P04'te seçtiği tek gelişim hedefi üzerinde çalışmasını sağla; hedef dışındaki tüm rubrik boyutlarını aynı anda yeniden düzeltmeye çalışma.
2. Hedef içerik/geçiş ise 45-90 saniyelik ilgili bölümde iddia-kanıt-bağlantı veya geçiş ifadesini; süre ise aynı bölümün ritmini; ses/diksiyon ise telaffuz-vurgu-tonlamayı; beden dili ise göz teması/duruş/jest kullanımını; kelime/dil hedefiyse bağlama uygun sözcük ve cümle kuruluşunu çalıştır.
3. Sosyal medya dili ve Türkçe kelime tercihine ilişkin içerikte yeni ideolojik genelleme veya kaynaksız örnek ekletme; P01-P03 kanıt bankasıyla sınırlı kal.
4. Öğrenciden birinci mikro-prova sonrasında yalnız hedef davranışa ilişkin öz gözlem yapmasını iste.
5. Gerekirse tek bir düzeltme daha yaptır ve ikinci mikro-provada aynı davranışı yeniden sınat.
6. İkinci ders saatindeki yeniden performans için hangi 45-90 saniyelik bölümün seçildiğini ve hangi davranışın gözleneceğini kaydettir.

### Öğrencinin yapacakları

- P04'teki tek gelişim hedefini ve P03 kanıtını yeniden okur.
- Konuşmasının hedefle ilişkili 45-90 saniyelik bölümünü seçer.
- Yalnız seçilen davranış için mikro-düzeltme yapar.
- İki kısa prova turunda aynı hedef davranışı sınar.
- Yeniden performansta neyin gözleneceğini açık biçimde kaydeder.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`, `T4_ACT_09_KONUSMA_SONRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Ana kanıt 'P03 mevcut davranış → P04 hedefi → seçilen mikro-düzeltme → prova 1 gözlemi → prova 2 gözlemi' kaydıdır. Başarı tüm konuşmayı yeniden üretmekle değil tek hedef davranışta izlenebilir değişim hazırlamakla tanımlanır.

### Kapanış

Öğrenci 'Yeniden performansta ... davranışımı değiştirmeye çalışacağım; uyguladığım mikro-düzeltme ... ve bunun işe yarayıp yaramadığını ... kanıtından anlayacağım.' cümlesini tamamlar.

### Materyaller

- P03 canlı sunum/rubrik kanıtı
- P04 akran-öz-öğretmen geri bildirim sentezi
- P04 tek gelişim hedefi
- P02 konuşma akış planı

## 2. Ders — 45-90 saniyelik yeniden performans ve önce/sonra kanıtıyla konuşma bloğunu kapatma

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Öğrencinin aynı konuşmanın hedefle ilgili kısa bölümünü yeniden sunması; P03 ile P05 performansını yalnız seçilen davranış bakımından karşılaştırması ve geri bildirimden performans değişimine uzanan öğrenme döngüsünü kanıtla yansıtması.

### Derse giriş

Yeniden performans ölçütü tek cümlede netleştirilir: 'Bugün bütün sunumu yeniden puanlamıyoruz; yalnız ... davranışında P03'e göre gözlenebilir değişim var mı?'

### Öğretmenin yapacakları

1. Öğrencilerin seçilen 45-90 saniyelik bölümü yeniden icra etmesini sağla; sınıf mevcudu için sayı varsayma ve süreyi öğrenciler arasında adil rotasyonla yönet.
2. Her öğrenci için yalnız seçilen gelişim hedefinde P03 kanıtı ile P05 yeniden performans kanıtını karşılaştır.
3. Değişim gözleniyorsa 'önceki kanıt → yeni kanıt → değişimin yönü' biçiminde kaydet; gözlenmiyorsa başarısızlık etiketi yerine kullanılan stratejinin neden yeterli görünmediğini belirlet.
4. Yeni bir tam TDE9_KONUSMA_RUBRIC puanlaması yapma; P03 rubrik sonucu ana performans kaydı olarak kalsın.
5. Öğrenciden sosyal medya dili/Türkçe kullanımına ilişkin içerik görüşünü değil, kendi konuşma performansındaki öğrenme değişimini yansıtmasını iste.
6. Saat sonunda Tema 4 Konuşma bloğunu 10/10 saat kapat ve sonraki Dinleme/İzleme bloğuna içerik taşımadan yalnız süreç geçişini belirt.

### Öğrencinin yapacakları

- Seçilen konuşma bölümünü 45-90 saniye yeniden sunar.
- P03 ve P05 performansını yalnız seçilen hedef davranış açısından karşılaştırır.
- Önce/sonra kanıtını açık biçimde yazar.
- Değişim görülmediyse bir sonraki benzer konuşma görevinde kullanacağı farklı stratejiyi belirler.
- Geri bildirimden yeniden performansa uzanan öğrenme döngüsünü bir cümleyle yansıtır.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`, `T4_ACT_09_KONUSMA_SONRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Ana kapanış kanıtı 'P03 önce → P04 geri bildirim/hedef → P05 mikro-düzeltme → P05 yeniden performans → gözlenen değişim' zinciridir. Yeni tam rubrik puanı üretilmez.

### Kapanış

Öğrenci 'P03'te ... görünüyordu; geri bildirimden sonra ... stratejisini kullandım; P05'te ... kanıtı değişimin ... olduğunu gösterdi. Benzer bir konuşmada bunu ... biçimde sürdüreceğim.' cümlesiyle bloğu kapatır.

### Materyaller

- P03 canlı performans ve rubrik kanıtı
- P04 tek gelişim hedefi
- P05 ilk saat mikro-prova kaydı
- Basit süre takip aracı

## Öğretmen notu

Bu paket BLOCK_T4_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 9. ve 10. saatleridir; resmî MEB saat-saat alt sıralaması değildir. P05 yeni bir resmî etkinlik veya ikinci summative puanlama icat etmez; T4_ACT_08 performansı ile T4_ACT_09 yansıtmasını öğretimsel geri bildirim döngüsüne bağlayan pedagojik kapanıştır. P03'te approved yıllık rubrikle kaydedilen ana performans puanı korunur. Tema 4 Konuşma bloğu bu paket sonunda 10/10 saat tamamlanır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 0 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`, `T4_ACT_09_KONUSMA_SONRASI`
- **Sonraki adım:** BLOCK_T4_02_KONUSMA tamamlandı. Sonraki paket BLOCK_T4_03_DINLEME_P01 olmalıdır. Tema 4 Dinleme/İzleme başlangıcında T4_ACT_10_DINLEME_ONCESI_VE_SIRASI, Âşık Veysel Belgeseli ve FORM_IN_T4_DINLEME_GOZLEM kaynakları fresh-read edilmeden yeni içerik üretilmemelidir.

---

<!-- TYMM_JSON_SHA256:9fbf904722b5bf631314ab6502acb45dfc6983edd983b5a6abf73e903903bc23 -->
