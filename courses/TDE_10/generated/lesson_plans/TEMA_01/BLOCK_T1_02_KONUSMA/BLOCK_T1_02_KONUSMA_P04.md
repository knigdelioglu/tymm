# Şiir Dinletisini Değerlendirmek: Akran Formu, Resmî DPA ve Gelişim Hedefi

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

Tema 1 Konuşma bloğunun 7. ve 8. saatlerinde öğrenciler T1_ACT_10_KONUSMA_DEGERLENDIRME kapsamında varsa P03'ten kalan dinleti performanslarını tamamlar, ardından FORM_T1_KONUSMA_AKRAN'ın basılı ölçütlerini aynen kullanarak kanıta dayalı akran değerlendirmesi yapar. Öğretmenin yetkili EBA erişimi varsa LINK_T1_KONUSMA_DPA resmî yapısıyla uygulanır; erişim yoksa kriter/puan üretilmez. İkinci saatte akran geri bildirimi, öğretimsel performans gözlemi ve varsa resmî DPA sonucu birlikte incelenir; her grup P05 için tek, gözlenebilir ve yeniden performansta sınanabilir gelişim hedefi seçer.

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
- **Uygulandığı dersler:** `1`
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

## 1. Ders — Kalan dinletileri tamamlama ve basılı akran formuyla kanıtlı değerlendirme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Varsa kalan canlı performansların aynı görev koşullarıyla tamamlanması; öğrencilerin FORM_T1_KONUSMA_AKRAN'ı kişisel beğeni yerine gözlenebilir performans kanıtına dayanarak kullanması.

### Derse giriş

P03 sonunda kalan performanslar kontrol edilir. Varsa önce aynı görev koşullarıyla tamamlanır; ardından T1_ACT_10 değerlendirme aşamasına geçilir.

### Öğretmenin yapacakları

1. P03'ten kalan dinletileri tamamlat; sunulmayan performansı değerlendirilmiş sayma.
2. FORM_T1_KONUSMA_AKRAN'ı ders kitabındaki 11 basılı ölçütüyle aynen kullandır; ölçüt ekleme, çıkarma veya yeniden adlandırma.
3. Akran değerlendirmesini konuşmacının/şiirin kişisel beğenisine değil gözlenebilir dinleti davranışına dayandır.
4. Her akran değerlendirmesinde en az bir somut performans kanıtı veya örneği iste.
5. LINK_T1_KONUSMA_DPA'ya yetkili erişim varsa resmî aracı aynen kullan; erişim yoksa puan/ölçüt üretme.
6. Saat sonunda grupların bir güçlü yön ve bir gelişim alanı için performans kanıtı toplamasını sağla.

### Öğrencinin yapacakları

- Varsa kalan dinleti performansını gerçekleştirir.
- FORM_T1_KONUSMA_AKRAN'ı basılı ölçütleriyle doldurur.
- Akran yorumunu somut performans kanıtıyla gerekçelendirir.
- Bir güçlü yön ve bir gelişim alanı belirler.
- Kişisel beğeni ile performans değerlendirmesini ayırır.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_09_SIIR_DINLETISI_SUNUM`, `T1_ACT_10_KONUSMA_DEGERLENDIRME`
- **Formlar:** `FORM_T1_KONUSMA_AKRAN`, `LINK_T1_KONUSMA_DPA`

### Ölçme / öğrenme kanıtı

Doldurulmuş FORM_T1_KONUSMA_AKRAN ve her değerlendirmeyi destekleyen en az bir somut performans kanıtı; erişim varsa resmî DPA kaydı.

### Kapanış

Grup 'Dinletimizde güçlü bulduğumuz ... davranışını ... kanıtı gösteriyor; geliştirmek istediğimiz ... alanını ise ... kanıtı gösteriyor.' cümlesini tamamlar.

### Materyaller

- FORM_T1_KONUSMA_AKRAN — s.56-57
- P03 performans gözlem notları
- LINK_T1_KONUSMA_DPA — resmî EBA bağlantısı

## 2. Ders — Geri bildirimleri sentezleme ve tek yeniden-performans hedefi seçme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.4`

### Hedef

Grubun akran değerlendirmesi, öğretimsel performans gözlemi ve varsa resmî DPA geri bildirimini aynı performans üzerinde karşılaştırarak P05 için tek, gözlenebilir gelişim hedefi seçmesi.

### Derse giriş

Akran formu, P03/P04 öğretimsel gözlem notları ve erişim varsa resmî DPA sonucu yan yana getirilir. 'Hangi bulgu birden fazla kaynakta tekrar ediyor?' sorusuyla sentez başlatılır.

### Öğretmenin yapacakları

1. Akran formu, öğretimsel gözlem ve varsa DPA sonucunu tek bir yeni puan ortalamasına dönüştürme.
2. DPA erişimi yoksa onun yerine uydurma öğretmen puanı üretme; yalnız mevcut kanıt kaynaklarını kullan.
3. Tekrarlanan güçlü/gelişim bulgularını işaretlet.
4. P05 hedefini tek davranışa indir: akış/geçiş, süre, ses-söyleyiş, beden dili, grup koordinasyonu, Türkçe kullanım veya benzeri gözlenebilir alan.
5. 'Daha iyi sunacağız' gibi belirsiz hedefi kabul etme; 'mevcut kanıt → seçilen davranış → P05'te gözlenecek değişim' zinciri kurdur.
6. P05'te bütün dinletinin yeniden yapılmayacağını, hedefle ilgili kısa bölümün yeniden icra edileceğini belirt.

### Öğrencinin yapacakları

- Akran ve öğretimsel gözlem kanıtlarını karşılaştırır.
- Varsa resmî DPA geri bildirimini ayrı kaynak olarak inceler.
- Tekrarlanan bulguları belirler.
- Tek gözlenebilir gelişim hedefi seçer.
- P05'te hangi değişikliğin gözleneceğini yazar.

### Kaynak bağları

- **Etkinlikler:** `T1_ACT_10_KONUSMA_DEGERLENDIRME`
- **Formlar:** `FORM_T1_KONUSMA_AKRAN`, `LINK_T1_KONUSMA_DPA`

### Ölçme / öğrenme kanıtı

'Geri bildirim kaynağı → performans kanıtı → ortak/farklı bulgu → tek P05 hedefi' sentez kaydı.

### Kapanış

Grup 'P05'te ... davranışını değiştireceğiz; bunu seçmemizin kanıtı ...; değişimi ... üzerinden gözleyeceğiz.' cümlesini tamamlar.

### Materyaller

- FORM_T1_KONUSMA_AKRAN
- P03-P04 öğretimsel gözlem notları
- Varsa resmî DPA geri bildirimi

## Öğretmen notu

FORM_T1_KONUSMA_AKRAN yapısı yerel MEB PDF'de doğrulanmıştır. LINK_T1_KONUSMA_DPA'nın varlığı ve resmî EBA hedefi doğrulanmış, fakat hedef yapısı authentication-gated olduğundan plan hiçbir DPA kriterini veya puanlama modelini türetmez.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 2 saat
- **Kapsanan çıktılar:** `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T1_ACT_09_SIIR_DINLETISI_SUNUM`, `T1_ACT_10_KONUSMA_DEGERLENDIRME`
- **Sonraki adım:** P05'te tek gelişim hedefi için kısa prova ve kısa yeniden performans yap; yeni DPA kriteri veya ikinci tam puanlama turu oluşturma.

---

<!-- TYMM_JSON_SHA256:adfa450cca859ab2bc115082908fffcfe035f8529c3178eadeab5b5e87a43d0f -->
