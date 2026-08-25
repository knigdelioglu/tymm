# Benim Mekânım Canlı Sunumları: Karşılaştırma, Görsel Anlatım ve Rubrik Kanıtı

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

10 saatlik 3. Tema Konuşma Atölyesi bloğunun 5. ve 6. ders saatlerinde öğrenciler P01-P02’de hazırlayıp prova ettikleri ‘Benim Mekânım’ sunumlarını T3_ACT_08_KONUSMA_SIRASI kapsamında canlı olarak gerçekleştirir. Sunan her öğrenci için öğretmen, current ve approved TDE9_KONUSMA_RUBRIC/RES_T3_05 bağlamında içerik-görev uyumu, organizasyon-zaman, ses/diksiyon/akıcılık, beden dili-iletişim ve doğru Türkçe/söz varlığı boyutlarında performans kanıtı kaydeder. Sınıf mevcuduna göre iki saatte sunumunu gerçekleştiremeyen öğrenciler P04’ün başlangıcında tamamlayabilir; hiçbir sabit öğrenci sayısı varsayılmaz. Ayrıntılı rubrik geri bildirimi, öz/akran değerlendirmesi ve yansıtma T3_ACT_09 ile P04’e bırakılır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`
- **Kullanılan formlar:** Yok

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_BOB_06_T3_KONUSMA_OZ` | `USED` |
| `FORM_BOB_10_T3_T4_AKRAN` | `DEFERRED` |
| `FORM_BOB_11_GENEL_GOZLEM` | `USED` |

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

## 1. Ders — Canlı sunum rotasyonunu başlatma ve performans kanıtı toplama

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

Öğrencilerin ‘Benim Mekânım’ sunumlarını karşılaştırma/betimleme içeriği, görsel destek ve sözlü anlatım kurallarını uygulayarak gerçekleştirmesi; öğretmenin her sunum için yıllık analitik rubriğin ölçütlerine dayalı somut performans kanıtı toplaması.

### Derse giriş

P02’de belirlenen kişisel performans hedefleri sessizce gözden geçirilir. Dinleyicilere ‘Bu saatte göreviniz konuşmacının kişiliğini değil, sunumda gözlenebilen içerik ve anlatım davranışlarını izlemek.’ hatırlatması yapılır.

### Öğretmenin yapacakları

1. T3_ACT_08_KONUSMA_SIRASI kapsamında sunum rotasyonunu başlat; sıra ve süre yönetimini sınıf koşullarına göre uygula, kaynakta olmayan sabit öğrenci sayısı veya dakika kuralı icat etme.
2. Sunan her öğrenci için approved TDE9_KONUSMA_RUBRIC’in beş çekirdek boyutunda kanıt kaydet: içerik/görev uyumu; yapı-organizasyon-zaman; ses/diksiyon/akıcılık; beden dili/iletişim; doğru Türkçe/söz varlığı.
3. Tema 3 görevine özgü kanıtları çekirdek ölçütlerin içinde yorumla: iki mekânın karşılaştırılması/betimlenmesi, görsellerin düşünceyi destekleme işlevi, kaynak/telif duyarlılığı ve mekân kanıtlarının doğruluğu.
4. Rubrik puanını yalnız gözlenebilir performans kanıtına dayandır; öğrencinin kişiliği, çekingenliği veya genel izlenimi için ayrı puan üretme.
5. Sunum sırasında ayrıntılı puan sonucunu açıklayıp öğrencinin sonraki performansını bozma; yalnız süreç güvenliği veya sunumu sürdürebilmek için zorunlu kısa yönlendirme gerekiyorsa müdahale et.
6. Dinleyicilerden bir güçlü davranış ve bir açıklayıcı soru not etmelerini iste; bunu henüz FORM_BOB_10_T3_T4_AKRAN ile tam akran değerlendirmesine dönüştürme.

### Öğrencinin yapacakları

- P02’de hazırladığı konuşma ve görsel akışa göre canlı sunumunu gerçekleştirir.
- İki mekânı kanıtlarla karşılaştırır ve betimleyici anlatım kullanır.
- Görselleri konuşmanın yerine geçirmek yerine ilgili düşünceleri desteklemek için kullanır.
- Ses, vurgu-tonlama, beden dili, Türkçe ve süre yönetimi hedeflerini uygular.
- Dinleyici olduğunda bir gözlenebilir güçlü davranış ve bir açıklayıcı soru not eder.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Ana kanıt canlı sunum performansı ve öğretmenin approved TDE9_KONUSMA_RUBRIC için tuttuğu ölçüt-kanıt kayıtlarıdır. Her düzey/puan gözlenebilir sunum davranışına bağlanmalıdır. Dinleyici notları biçimlendirici kanıttır; henüz resmî akran formu değildir.

### Kapanış

Sunum yapan öğrenci yalnız kısa bir ilk izlenim yazar: ‘Canlı sunumda P02 hedefim olan … konusunda … gözledim.’ Ayrıntılı öz değerlendirme yapılmaz.

### Materyaller

- P01-P02 sunum hazırlık ve prova kayıtları
- Öğrencinin Benim Mekânım görsel/sunum materyali
- T3_ACT_08_KONUSMA_SIRASI — s.193–196
- Approved TDE9_KONUSMA_RUBRIC / RES_T3_05 öğretmen değerlendirme aracı

## 2. Ders — Canlı sunum rotasyonunu sürdürme ve rubrik kanıtlarını düzenleme

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.2`, `TDE3.3`, `TDE3.4`

### Hedef

İkinci sunum rotasyonunda öğrencilerin karşılaştırmalı mekân sunumlarını gerçekleştirmesi; öğretmenin rubrik ölçütlerindeki kanıtları tutarlı biçimde tamamlaması ve P04’te yapılacak öz/akran değerlendirme ile geri bildirim için düzenlemesi.

### Derse giriş

İlk saatte ortak görülen bir süreç noktası varsa öğrenci adı vermeden yalnız davranış düzeyinde hatırlatılır; örneğin ‘görseli gösterdikten sonra dinleyiciye dönmek’ veya ‘karşılaştırmayı kanıtla tamamlamak’. Rubrik puanları açıklanmaz.

### Öğretmenin yapacakları

1. Sunum rotasyonunu sınıf koşullarına göre sürdür ve sunan her öğrenci için aynı rubrik ölçütlerini kullanarak kanıt toplamaya devam et.
2. Kanıt dilini ‘etkileyiciydi/zayıftı’ gibi genel yargılardan çıkar; ‘iki mekân için iki ayrı kanıt kullandı’, ‘görsel değişiminde konuşma akışı kesildi’, ‘sonuç ana düşünceye geri döndü’ gibi gözlenebilir ifadelere çevir.
3. Sunum sayısı iki ders saatine sığmıyorsa kalan öğrencileri P04’ün başlangıcına aktar; hiçbir öğrenciyi yalnız zaman baskısıyla eksik performansa zorlayarak değerlendirme.
4. Rubrik kayıtlarını P04 için ölçüt bazında düzenle; öğrenciye ayrıntılı düzey/puan ve geliştirme hedefini öz/akran değerlendirmesinden önce açıklama.
5. Dinleyici notlarını kişilik veya zevk yargılarından arındır; yalnız konuşma içeriği, kanıt, görsel ve performans davranışlarına ilişkin notları koru.
6. T3_ACT_09, FORM_BOB_06_T3_KONUSMA_OZ, FORM_BOB_10_T3_T4_AKRAN ve FORM_BOB_11_GENEL_GOZLEM uygulamasını bu saatte başlatma.

### Öğrencinin yapacakları

- Sunum sırası kendisine geldiğinde hazırlıklı canlı performansını gerçekleştirir.
- Sunumunda karşılaştırma ve betimlemeyi metin/gözlem kanıtlarıyla ilişkilendirir.
- Görsel araçları ve sözlü anlatımı eşgüdümlü kullanır.
- Dinleyici olarak gözlenebilir performans notu tutar.
- Sunum sonrası yalnız kısa ilk izlenim kaydı yapar; tam öz/akran değerlendirmesini P04’e bırakır.

### Kaynak bağları

- **Etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

P03 sonunda sunum yapan her öğrenci için rubriğin beş çekirdek boyutunda en az bir gözlenebilir kanıt bulunması hedeflenir. Sunumu henüz gerçekleşmeyen öğrenciler için puan uydurulmaz; performans P04 başlangıcında tamamlandıktan sonra değerlendirilir.

### Kapanış

Öğretmen P04’e aktarılacak üç veri grubunu düzenler: ‘canlı performans → rubrik ölçüt kanıtları → dinleyici gözlem notları’. Öğrenci ise ayrıntılı değerlendirme yapmadan performans kaydını saklar.

### Materyaller

- Approved TDE9_KONUSMA_RUBRIC / RES_T3_05
- Öğrenci sunumları ve görselleri
- P02 kişisel performans hedefleri
- Dinleyici kısa gözlem notları

## Öğretmen notu

Bu paket BLOCK_T3_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 5. ve 6. saatleridir; resmî MEB saat-saat alt sıralaması değildir. TDE9_KONUSMA_RUBRIC approval kaydı current canonical kaynaklar, REVIEW snapshot ve generator kimliğiyle uyuşmaktadır. Rubrik Tema 2-4 yıllık konuşma/sunum görevlerinde yeniden kullanılan analitik araçtır; Tema 3’e özgü karşılaştırma, betimleme, görsel ve mekân kanıtları task-binding bağlamında yorumlanır. T3_ACT_09 öz/akran değerlendirme ve yansıtma P04’e bırakılmıştır.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 4 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T3_ACT_08_KONUSMA_SIRASI`
- **Sonraki adım:** P04’ün başlangıcında sınıf mevcudu nedeniyle kalan canlı sunumlar varsa tamamla. Ardından T3_ACT_09 kapsamında FORM_BOB_10_T3_T4_AKRAN ile kanıta dayalı akran değerlendirmesi, FORM_BOB_06_T3_KONUSMA_OZ ile öz değerlendirme ve FORM_BOB_11_GENEL_GOZLEM ile öğretmen gözlemini birleştir; approved rubrik geri bildirimini bu yansıtma sürecine dahil et. P05 için tek telafi/iyileştirme hedefi seç.

---

<!-- TYMM_JSON_SHA256:1f046b9076b1cd47f49a2e3191f9d5dcedca97b7950f2a5d04358b9215753ce2 -->
