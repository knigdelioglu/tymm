# Geri Bildirimi Performansa Dönüştürmek: Telafi, Yeniden Sunum ve Blok Kapanışı

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_9` |
| Tema | `TEMA_02` |
| Blok | `BLOCK_T2_02_KONUSMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

10 saatlik 2. Tema Konuşma Atölyesi bloğunun son iki ders saatinde yeni konuşma içeriği öğretilmez. Öğrenciler P04'te öz, akran ve öğretmen kanıtlarından seçtikleri tek geliştirme hedefi için kısa odaklı prova yapar; ardından aynı konuşmanın seçilmiş bir bölümünü yeniden sunarak önce/sonra performans farkını gözlenebilir kanıtla değerlendirir. Son bölümde öğrenciler hangi geri bildirimi neden kullandıklarını ve sonraki konuşmalara taşıyacakları stratejiyi açıklar. T2_ACT_08 yeniden performans, T2_ACT_09 ise yansıtma bağlamında kullanılır. Böylece BLOCK_T2_02_KONUSMA 10/10 saat tamamlanır.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`, `T2_ACT_09_KONUSMA_SONRASI`
- **Kullanılan formlar:** `FORM_BOB_04_T2_KONUSMA_OZ`, `FORM_BOB_09_T1_T2_AKRAN`, `FORM_BOB_11_GENEL_GOZLEM`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_BOB_04_T2_KONUSMA_OZ` | `USED` |
| `FORM_BOB_09_T1_T2_AKRAN` | `USED` |
| `FORM_BOB_11_GENEL_GOZLEM` | `USED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE9_KONUSMA_RUBRIC` | `MAT_T2_KONUSMA_RUBRIC` | `DEFERRED` |

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

## 1. Ders — Tek telafi hedefi için odaklı prova ve yeniden performans

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.3`, `TDE3.4`

### Hedef

Öğrencinin P04'te belirlediği tek geliştirme hedefini kısa prova döngüsünde uygulaması; ardından karakter sunumunun seçilmiş bir bölümünü yeniden sergileyerek hedef davranışta gözlenebilir değişim oluşturması.

### Derse giriş

P04 hedefleri açılır. Her öğrenci yalnız tek hedefini görünür biçimde yazar. ‘Bir anda her şeyi düzeltmeye çalışmak mı, tek davranışı bilinçli değiştirmek mi daha ölçülebilir?’ sorusuyla telafi döngüsü başlatılır.

### Öğretmenin yapacakları

1. P04'te seçilen tek hedefi temel al; öğrenciye yeni bir hedef ekleme.
2. 30-60 saniyelik prova yaptır ve yalnız seçilen davranışa ilişkin gözlenebilir geri bildirim ver.
3. Ardından öğrencinin P03'teki konuşmasının aynı veya eşdeğer kısa bölümünü yeniden sunmasını sağla; içerik değiştirmek yerine hedef davranışın uygulanmasına odaklan.
4. Önce/sonra karşılaştırmasını ‘ilkinde ne gözlendi → ne değiştirildi → ikincide ne gözlendi’ biçiminde kaydet.
5. TDE9_KONUSMA_RUBRIC REVIEW_REQUIRED ise yeniden performansı puanlamak için zorunlu araç gibi kullanma; gözlenebilir kanıt ve mevcut formlar yeterli süreç kanıtıdır.

### Öğrencinin yapacakları

- P04'teki tek telafi hedefini hatırlar.
- Hedef davranış için kısa prova yapar.
- Geri bildirime göre tek bir performans davranışını bilinçli değiştirir.
- Konuşmasının seçilmiş bölümünü yeniden sunar.
- İlk ve ikinci performans arasındaki farkı gözlenebilir kanıtla açıklar.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`, `T2_ACT_09_KONUSMA_SONRASI`
- **Formlar:** Yok

### Ölçme / öğrenme kanıtı

Ana kanıt bir ‘önce → hedef → uygulanan değişiklik → sonra’ performans kaydıdır. Başarı mutlak kusursuzluk değil, seçilen davranışın kanıtlanabilir biçimde iyileştirilmesi veya neden iyileşmediğinin doğru teşhis edilmesidir.

### Kapanış

Öğrenci ‘İlk performansta … gözleniyordu; geri bildirimden sonra … yaptım ve ikinci performansta … değişti/değişmedi.’ cümlesini tamamlar.

### Materyaller

- P03 canlı sunum gözlemleri
- P04 öz/akran/öğretmen değerlendirme kayıtları
- Karakter sunumunun kısa yeniden performans bölümü

## 2. Ders — Geri bildirim kullanımını yansıtma ve konuşma bloğunu kapatma

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE3.4`

### Hedef

Öğrencinin öz, akran ve öğretmen geri bildirimlerinden hangisini nasıl kullandığını açıklaması; karakter sunumu sürecinde planlama, içerik oluşturma, kural uygulama ve yansıtma deneyimini kanıtlarla sentezleyerek sonraki sözlü anlatım görevine aktaracağı stratejiyi belirlemesi.

### Derse giriş

Önce/sonra performans kayıtları ve P04 formları yan yana getirilir. ‘Bir geri bildirim yararlı olduğunu nasıl kanıtlar?’ sorusu üzerinden geri bildirimin davranış değişikliğine dönüşmesi tartışılır.

### Öğretmenin yapacakları

1. Öğrenciden P04'te aldığı akran, öz ve öğretmen geri bildirimlerinden hangisinin P05 değişikliğini doğrudan etkilediğini belirtmesini iste.
2. Geri bildirimin etkisini sonuç cümlesiyle değil performans kanıtıyla gerekçelendirt.
3. P01-P05 ürünlerini dört süreç başlığında kısa sentezlet: planlama, içerik kurma, performans/kural uygulama, yansıtma-düzeltme.
4. Öğrencinin sonraki konuşma görevine taşıyacağı tek stratejiyi gözlenebilir davranış biçiminde yazmasını sağla.
5. Yeni Dinleme/İzleme bloğuna içerik olarak geçme; yalnız konuşma continuation'ını kapat.

### Öğrencinin yapacakları

- Kullandığı geri bildirimin kaynağını ve etkisini açıklar.
- Geri bildirimin davranış değişikliğine nasıl dönüştüğünü kanıtlar.
- P01-P05 sürecinden bir planlama, bir performans ve bir yansıtma kanıtı seçer.
- Konuşma becerisindeki güçlü yön ve devam eden ihtiyacını ayırır.
- Sonraki sözlü anlatım görevine taşıyacağı tek stratejiyi belirler.

### Kaynak bağları

- **Etkinlikler:** `T2_ACT_09_KONUSMA_SONRASI`
- **Formlar:** `FORM_BOB_04_T2_KONUSMA_OZ`, `FORM_BOB_09_T1_T2_AKRAN`, `FORM_BOB_11_GENEL_GOZLEM`

### Ölçme / öğrenme kanıtı

Ana ürün kısa blok sentezidir: ‘kullandığım geri bildirim → yaptığım değişiklik → önce/sonra kanıtı → sonraki görev stratejim’. Bu ürün TDE3.4 yansıtma boyutunu görünür kılar.

### Kapanış

BLOCK_T2_02_KONUSMA 10/10 saat tamamlanır. Öğrenci ‘Sonraki konuşmamda özellikle … stratejisini kullanacağım; çünkü bu blokta … kanıtı bunun benim için işe yaradığını gösterdi.’ cümlesini tamamlar.

### Materyaller

- P01-P05 konuşma ürünleri
- FORM_BOB_04_T2_KONUSMA_OZ
- FORM_BOB_09_T1_T2_AKRAN
- FORM_BOB_11_GENEL_GOZLEM

## Öğretmen notu

Bu paket BLOCK_T2_02_KONUSMA bloğunun pedagojik olarak tasarlanmış 9. ve 10. saatleridir; resmî MEB saat-saat alt sıralaması değildir. Yeni içerik eklenmemiş; P04 değerlendirme kanıtı hedefli telafi, kısa yeniden performans ve yansıtma döngüsüne dönüştürülmüştür. TDE9_KONUSMA_RUBRIC lifecycle REVIEW_REQUIRED olduğu sürece onaylı/resmî puanlama aracı gibi kullanılmaz. Paket sonunda konuşma continuation'ı kapanır; sonraki blok BLOCK_T2_03_DINLEME_P01'dir.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 0 saat
- **Kapsanan çıktılar:** `TDE3.1`, `TDE3.2`, `TDE3.3`, `TDE3.4`
- **Kullanılan etkinlikler:** `T2_ACT_08_KONUSMA_SIRASI`, `T2_ACT_09_KONUSMA_SONRASI`
- **Sonraki adım:** BLOCK_T2_02_KONUSMA tamamlandı. Sonraki paket TEMA_02 / BLOCK_T2_03_DINLEME / P01 olmalıdır. Yeni blokta continuation state sıfırlanmalı; TDE1.1-TDE1.2 ve yalnız T2_ACT_10_DINLEME_ONCESI_VE_SIRASI ile başlanmalı, T2_ACT_11 ayrıntılı tahlil sonraki paketlere bırakılmalıdır.

---

<!-- TYMM_JSON_SHA256:a8db0c5b61923462f15b9660edbdc9a4c65639dff00d2fe729c274b4b219a1d7 -->
