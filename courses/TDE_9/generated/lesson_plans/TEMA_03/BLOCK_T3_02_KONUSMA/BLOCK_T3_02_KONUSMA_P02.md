# Benim Mekânım’ı Sunuma Dönüştürmek: İçerik Kurgusu, Görsel Akış ve Kontrollü Prova

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

10 saatlik 3. Tema Konuşma Atölyesi bloğunun 3. ve 4. ders saatlerinde öğrenciler P01’de oluşturdukları kanıtlı karşılaştırma matrisini T3_ACT_08_KONUSMA_SIRASI kapsamında bütünlüklü konuşma akışına dönüştürür. İlk saatte giriş-gelişme-sonuç düzeni, betimleme/karşılaştırma ifadeleri, geçişler ve görsel/slayt akışı tamamlanır. İkinci saatte FORM_IN_T3_KONUSMA_CRITERIA hazırlık ölçütleriyle ses tonu, vurgu-tonlama, akıcılık, beden dili, Türkçe kullanımı, görsel yönetimi ve süre için kısa prova döngüleri yürütülür. Paket canlı final sunumu veya öz/akran değerlendirmesi değildir; P03 performansına hazır, kanıtlı ve prova edilmiş sunum üretir.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`
- **Kullanılan formlar:** `FORM_IN_T3_KONUSMA_CRITERIA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_IN_T3_KONUSMA_CRITERIA` | `USED` |

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

## 1. Ders — Karşılaştırma matrisinden bütünlüklü konuşma ve görsel akışa

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`

### Hedef

Öğrencinin P01’deki mekân karşılaştırma kanıtlarını giriş-gelişme-sonuç düzeninde, betimleme ve karşılaştırma ifadeleriyle birbirine bağlayarak tutarlı bir sözlü sunum akışı ve işlevsel görsel düzen oluşturması.

### Derse giriş

P01 ana düşüncesi ve karşılaştırma matrisi açılır. ‘Dinleyici sunumun sonunda hangi tek düşünceyi hatırlamalı ve her bölüm bu düşünceye nasıl hizmet etmeli?’ sorusuyla konuşma kurgusuna geçilir.

### Öğretmenin yapacakları

1. Öğrenciden girişte iki mekânı ve karşılaştırma amacını kısa biçimde kurmasını, gelişmede P01’deki 3 veya daha fazla karşılaştırma boyutunu kanıtlarla işlemesini, sonuçta ana düşünceyi yeniden anlamlandırmasını iste.
2. Betimleme ve karşılaştırma ifadelerini yalnız süslü anlatım için değil, mekânların yapısal/duygusal/işlevsel farklılıklarını görünür kılmak için kullandır.
3. Her bölüm için ‘iddia/karşılaştırma → metin veya gözlem kanıtı → yorum → ana düşünceye bağlantı’ zincirini kontrol et.
4. P01 görsel planını sunum akışıyla eşleştir; bir slayt/görsel yalnız ilgili sözlü içeriği destekliyorsa kalsın, konuşmanın yerine geçen uzun metin bloklarını azalt.
5. Türkçe karşılığı yerleşmiş sözcüklerde gereksiz yabancı kullanım varsa öğrenciden bağlama uygun Türkçe karşılığını tercih etmesini iste; kaynakta olmayan yapay kelime listeleri oluşturma.
6. Saat sonunda öğrencinin konuşma notlarını tam metin ezberine değil, anahtar ifade/kanıt/akış desteğine dönüştürmesini sağla.

### Öğrencinin yapacakları

- Sunumunu giriş-gelişme-sonuç düzeninde planlar.
- En az üç karşılaştırma boyutunu kanıtlarla konuşma akışına yerleştirir.
- Betimleme ve karşılaştırma ifadelerini anlam işlevine göre seçer.
- Görselleri ilgili konuşma bölümleriyle eşleştirir ve gereksiz metin/görsel yükünü azaltır.
- Konuşma notlarını anahtar sözcük, kanıt ve geçişlerden oluşan kısa sunucu notlarına dönüştürür.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T3_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana ürün konuşma akış planıdır: ‘bölüm → ana iddia/karşılaştırma → kanıt → görsel → geçiş → ana düşünceye katkı’. Sunumun görsel metin okumasına dönüşmemesi ve karşılaştırma kanıtlarının açık olması beklenir.

### Kapanış

Öğrenci ‘Sunumumun girişinde …, gelişmede … kanıtlarıyla … karşılaştırmasını, sonuçta ise … ana düşüncesini kuracağım.’ ifadesini tamamlar.

### Materyaller

- P01 karşılaştırma matrisi ve görsel-kaynak planı
- T3_ACT_08_KONUSMA_SIRASI — s.193–196
- FORM_IN_T3_KONUSMA_CRITERIA — s.195
- Öğrencinin sunum/slayt taslağı

## 2. Ders — Ses, akıcılık, beden dili, görsel yönetimi ve süre için kontrollü prova

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.3`

### Hedef

Öğrencinin hazırladığı sunumu kısa prova döngülerinde uygulaması; ses tonu-vurgu-tonlama, akıcılık, beden dili, görsel kullanımı, Türkçe ve süre yönetiminden gözlenebilir performans hedefleri seçerek ikinci provada somut iyileştirme göstermesi.

### Derse giriş

FORM_IN_T3_KONUSMA_CRITERIA’daki beklentiler performans öncesi kontrol listesi olarak açılır. ‘Bir provada her şeyi düzeltmeye çalışmak yerine hangi iki gözlenebilir davranışı iyileştirirsek farkı gerçekten görebiliriz?’ sorusuyla prova başlatılır.

### Öğretmenin yapacakları

1. 30–60 saniyelik prova kesitleri kullandır; her döngüde en fazla iki odak seç: ses/vurgu-tonlama-akıcılık, beden dili/göz teması, görsel geçiş, Türkçe kullanımı veya süre.
2. Geri bildirimi ‘iyi/kötü’ yargısından çıkar; ‘ses son cümlede düştü’, ‘görsele döndüğünde dinleyiciyle göz teması kesildi’, ‘karşılaştırma kanıtı söylenmeden yorum yapıldı’ gibi gözlenebilir davranışlara bağla.
3. Görsel yönetiminde öğrencinin ekranı okumamasını; görseli gösterip sözel açıklamayı dinleyiciye dönük sürdürmesini prova ettir.
4. Süreyi kaynakta belirtilmeyen sabit bir dakika sayısına bağlama; sınıf için belirlenen sunum süresi varsa ona göre, yoksa öğretmenin belirlediği makul sınıf içi süre hedefiyle prova yaptır.
5. İkinci prova öncesinde öğrenciden değiştireceği bir veya iki davranışı açıkça yazmasını, ikinci provada da ‘önce → değişiklik → gözlenen fark’ kaydı oluşturmasını iste.
6. T3_ACT_09 öz/akran değerlendirmesini bu saatte başlatma; bu yalnız performans öncesi prova ve öz-kontrol aşamasıdır.

### Öğrencinin yapacakları

- Sunumunun 30–60 saniyelik bir bölümünü prova eder.
- FORM_IN_T3_KONUSMA_CRITERIA beklentilerinden bir veya iki performans odağı seçer.
- Gözlenebilir geri bildirimi kaydeder ve hangi davranışı değiştireceğini belirler.
- İkinci prova turunda seçtiği davranışı bilinçli biçimde değiştirir.
- İki prova arasındaki farkı ‘önce → değişiklik → sonra’ biçiminde kaydeder ve P03 için tek kişisel performans hedefi belirler.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`
- **Formlar:** `FORM_IN_T3_KONUSMA_CRITERIA`

### Ölçme / öğrenme kanıtı

Ana kanıt iki kısa prova arasındaki gözlenebilir farktır. Öğrencinin en az bir performans davranışını kanıtla değiştirmesi ve P03 canlı sunumu için tek hedef belirlemesi beklenir; bu prova nihai rubrik puanı değildir.

### Kapanış

Öğrenci ‘İlk provada …; ikinci provada … davranışını değiştirdim ve … farkını gözledim. Canlı sunumda özellikle … hedefini koruyacağım.’ cümlesini tamamlar.

### Materyaller

- P02 ilk saat konuşma ve görsel akış planı
- FORM_IN_T3_KONUSMA_CRITERIA
- Sunum/slayt dosyası veya eşdeğer görsel materyal
- Kısa prova gözlem kaydı

## Öğretmen notu

Bu paket BLOCK_T3_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 3. ve 4. saatleridir; resmî MEB saat-saat alt sıralaması değildir. Tema 3 alignment TDE3.2 için mekân karşılaştırma/betimleme içerik kurgusunu; TDE3.3 için ses tonu, vurgu-tonlama, beden dili, dil kuralları ve canlı sunum performansını bekler. FORM_IN_T3_KONUSMA_CRITERIA burada biçimlendirici prova ölçütüdür; T3_ACT_09 değerlendirmesi ve yıllık analitik rubrik sonucu P03-P05 performans/yansıtma zincirinde ele alınacaktır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 6 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`
- **Kullanılan etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`
- **Sonraki adım:** P03’te ‘Benim Mekânım’ canlı sunumları başlatılmalı ve approved TDE9_KONUSMA_RUBRIC ile öğretmen performans kanıtı toplanmalıdır. Rubrik geri bildirimi sunum sürerken öğrencinin performansını bozacak biçimde anlık ayrıntılı sonuç açıklamasına dönüşmemeli; T3_ACT_09 öz/akran yansıtması P04’e bırakılmalıdır.

---

<!-- TYMM_JSON_SHA256:15b5513c3e99e8a105b532824fd7e0323911acd30a790c00ebd9f51f59824336 -->
