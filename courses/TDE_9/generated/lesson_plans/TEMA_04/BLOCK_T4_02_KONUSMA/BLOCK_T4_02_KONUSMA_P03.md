# Dilimizin Zenginlikleri Canlı Sunumu: Kanıttan Sözlü Performansa

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

10 saatlik 4. Tema Konuşma Atölyesi bloğunun 5. ve 6. ders saatlerinde öğrenciler P01-P02'de hazırladıkları kanıtlı karşılaştırma konuşmasını T4_ACT_08_KONUSMA_SIRASI kapsamında canlı olarak sunar. İlk saatte kısa son hazırlık kontrolünden sonra sunum rotasyonu başlatılır; ikinci saatte rotasyon sürdürülür. Her sunumda sosyal medya dili ile Türkçe/edebî dil kullanımı hakkındaki karşılaştırmaların kanıta dayanması, ana düşünceyi desteklemesi, dil tercihinin bağlam ve hedef kitleyle ilişkilendirilmesi, akış, süre, ses-diksiyon, beden dili ve varsa görsel kullanımının işlevi gözlenir. Öğretmen approved TDE9_KONUSMA_RUBRIC / RES_T4_SHARED_KONUSMA_RUBRIC ile gerçek performans kanıtını kaydeder. Sınıf mevcudu varsayılmaz; iki saatte tamamlanamayan sunumlar P04'ün başında tamamlanabilir. T4_ACT_09 öz ve akran değerlendirmesi P04'e bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Kullanılan formlar:** Yok

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_BOB_08_T4_KONUSMA_OZ` | `USED` |
| `FORM_BOB_10_T3_T4_AKRAN` | `USED` |
| `FORM_BOB_11_GENEL_GOZLEM` | `USED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE9_KONUSMA_RUBRIC` | `MAT_T4_KONUSMA_RUBRIC` | `DEFERRED` |

### Kaynak plan referansları

| Kaynak planı | Kullanım |
|---|---|
| `RES_T4_SHARED_KONUSMA_RUBRIC` | `DEFERRED` |

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

## 1. Ders — Son performans kontrolü ve Dilimizin Zenginlikleri sunum rotasyonunu başlatma

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`

### Hedef

Öğrencinin P02'de belirlediği tek geliştirme hedefini canlı sunum öncesi görünür kılması ve kanıta dayalı karşılaştırmalı konuşmasını planına bağlı fakat doğal sözlü icrayla sunmaya başlaması.

### Derse giriş

P02'de seçilen tek canlı sunum hedefi açılır. 'Sunum sırasında özellikle hangi gözlenebilir davranışını koruyacak veya geliştireceksin?' sorusuyla hazırlık tamamlanır; yeni içerik eklenmez.

### Öğretmenin yapacakları

1. Sunumdan hemen önce öğrencinin ana düşüncesini, 2-3 karşılaştırma kanıtını ve tek geliştirme hedefini hızlıca kontrol et; yeni metin yazdırma.
2. T4_ACT_08 kapsamında sunum rotasyonunu başlat; sınıf mevcudu ve sunum sayısı hakkında sayı varsayma.
3. Her performansta sosyal medya dili ile Türkçe/edebî dil örneklerinin bağlam, amaç, hedef kitle, anlaşılırlık ve sözcük tercihi üzerinden karşılaştırılıp karşılaştırılmadığını gözle.
4. Öğrencinin sosyal medya dilini bütünüyle yanlış veya yabancı kökenli her sözcüğü otomatik hata sayan genellemeler yapması hâlinde kanıt ve bağlam istemekle yetin; ideolojik bir dil temizliği ölçütü ekleme.
5. Approved TDE9_KONUSMA_RUBRIC / RES_T4_SHARED_KONUSMA_RUBRIC üzerinden İçerik ve Göreve Uygunluk, Yapı-Organizasyon-Zaman, Ses-Diksiyon-Akıcılık, Beden Dili-İletişim ve Türkçenin Doğru Kullanımı-Söz Varlığı ölçütlerinde gözlenebilir performans kanıtını kaydet.
6. Puanlama sırasında Tema 4 task-binding kanıtlarını yıllık çekirdek ölçütlerin içine yerleştir; yeni tema-özel rubrik ölçütü icat etme.

### Öğrencinin yapacakları

- Canlı sunum hedefini görünür hâle getirir.
- Ana düşüncesini kanıtlı sosyal medya dili ve Türkçe/edebî dil karşılaştırmalarıyla sunar.
- Sözcük ve dil tercihlerini bağlam, amaç ve hedef kitle açısından gerekçelendirir.
- Giriş-gelişme-sonuç akışını, süreyi, ses ve beden dilini yönetir.
- Varsa görsel desteği yalnız ilgili karşılaştırma kanıtını açıklamak için kullanır.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Ana kanıt canlı sunum performansı ve öğretmenin approved TDE9_KONUSMA_RUBRIC / RES_T4_SHARED_KONUSMA_RUBRIC üzerinde kaydettiği gözlenebilir performans bulgularıdır. Bu puanlama yıllık çekirdek rubriği kullanır; Tema 4 için yeni bir ölçek oluşturulmaz.

### Kapanış

Sunum yapan öğrenci yalnız bir cümlelik sıcak kayıt bırakır: 'Planımdaki ... kanıtını sunarken ... hedefimi ... biçimde uyguladım.' Ayrıntılı öz değerlendirme P04'e bırakılır.

### Materyaller

- P01 kanıt bankası ve karşılaştırma matrisi
- P02 konuşma akış planı ve prova hedefi
- TDE9_KONUSMA_RUBRIC / RES_T4_SHARED_KONUSMA_RUBRIC
- Varsa kaynak bilgisi kayıtlı görsel destek

## 2. Ders — Canlı sunum rotasyonunu sürdürme ve karşılaştırmalı dil kanıtını performansta gözleme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Öğrencilerin canlı sunum rotasyonunu sürdürmesi; öğretmenin yıllık rubrikle her performansın içerik, organizasyon, icra ve Türkçe/söz varlığı boyutlarına ilişkin kanıtı tutarlı biçimde kaydetmesi.

### Derse giriş

İkinci saat, ilk saatte kullanılan aynı performans ve kanıt standardı hatırlatılarak başlatılır; yeni ölçüt veya yeni sunum görevi eklenmez.

### Öğretmenin yapacakları

1. Sunum rotasyonunu aynı görev ve aynı rubrik koşullarıyla sürdür.
2. İçerik puanında yalnız iddia sayısına değil, örneklerin ana düşünceye ve göreve uygunluğuna bak.
3. Organizasyon puanında giriş-gelişme-sonuç akışı, geçişler ve süre yönetimini; icra boyutunda ses-diksiyon-akıcılık ile beden dili/iletişimi gözle.
4. Türkçe ve söz varlığı ölçütünde bağlama uygun kelime seçimi, cümle kuruluşu, bağdaşıklık/bağlaşıklık ve anlamı bozan dil hatalarını esas al; kelime kökenini tek başına hata ölçütü yapma.
5. Varsa görselin gösterişli olup olmadığına değil, karşılaştırma kanıtını açıklama işlevine bak.
6. İki saat sonunda tamamlanamayan sunumlar varsa yalnız kalan performansları P04'ün başına aktar; hiçbir öğrencinin değerlendirme kanıtını varsayımla tamamlamaya çalışma.

### Öğrencinin yapacakları

- Hazırladığı konuşmayı canlı olarak sunar.
- Karşılaştırma kanıtlarını ana düşünceyle ilişkilendirir.
- Dil ve söz varlığı tercihlerini iletişim bağlamında uygular.
- Dinleyiciyle göz teması ve beden dili üzerinden iletişim kurar.
- Sunum sonrası ayrıntılı öz/akran değerlendirmeyi P04'e bırakır.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Öğretmen her sunum için aynı approved yıllık rubrikte puan ve kısa kanıt notu kaydeder. Eksik sunumlar değerlendirilmiş sayılmaz; P04 başında tamamlanır.

### Kapanış

Sınıf düzeyinde yalnız süreç kapanışı yapılır: hangi sunumların tamamlandığı ve hangilerinin P04'e kaldığı belirlenir. Öz/akran/öğretmen geri bildirimlerinin birleştirilmesi henüz yapılmaz.

### Materyaller

- TDE9_KONUSMA_RUBRIC / RES_T4_SHARED_KONUSMA_RUBRIC
- Öğrenci sunum planları
- Varsa görsel sunum materyalleri
- Basit süre takip aracı

## Öğretmen notu

Bu paket BLOCK_T4_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 5. ve 6. saatleridir; resmî MEB saat-saat alt sıralaması değildir. T4_ACT_08 kaynakta sosyal medya dili ve Türkçe kelime kullanımı üzerine konuşma performansını doğrular. Teaching block, öğrencinin karşılaştırmalı sunum performansını ve RES_T4_SHARED_KONUSMA_RUBRIC ile derecelendirilmesini beklenen kanıt olarak tanımlar. Approved rubrik lifecycle kaydı current olduğu için bu pakette gerçek performans puanlaması yapılabilir. T4_ACT_09 öz/akran değerlendirme formları P04'e bırakılır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 4 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T4_ACT_08_KONUSMA_SIRASI`
- **Sonraki adım:** P04'ün başında varsa kalan sunumlar tamamlanmalı; ardından T4_ACT_09 kapsamında FORM_BOB_08_T4_KONUSMA_OZ, FORM_BOB_10_T3_T4_AKRAN ve FORM_BOB_11_GENEL_GOZLEM kullanılmalı. Öğretmen rubrik geri bildirimiyle birlikte öğrenci P05 için tek gözlenebilir gelişim hedefi seçmelidir.

---

<!-- TYMM_JSON_SHA256:18d4f9daa9fba08c82671da58f19d75941faeabe85e329f0e2a22004cfb7e869 -->
