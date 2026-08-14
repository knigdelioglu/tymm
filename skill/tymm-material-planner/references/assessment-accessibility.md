# Assessment, differentiation, accessibility, and quality

## Evidence → assessment instrument

Önce beklenen öğrenci kanıtını belirle, sonra aracı seç:

- kısa bilgi/terim kanıtı → kısa cevap veya seçilmiş yanıt,
- süreç gözlemi → kontrol listesi / gözlem formu (`checklist` / `teacher_evaluation_form`),
- çok boyutlu yazılı/görsel ürün → analitik dereceli puanlama anahtarı (`analytic_rubric`),
- performans/sunum/uygulama → performans rubriği veya gözlem formu,
- tartışma/etkileşim → katılım ve gerekçelendirme ölçütleri (`assessment_criteria`),
- yansıtma → öz değerlendirme / öğrenme günlüğü (`self_assessment`),
- akran etkileşimi/ürünü → akran değerlendirme formu (`peer_assessment`),
- sıklık/düzey derecelendirmesi → dereceleme ölçeği (`rating_scale`),
- biriken ürün/gelişim → portfolyo,
- ders sonu hızlı kanıt → çıkış bileti.

Rubrik varsayılan araç değildir. Araç, kanıtın ve subject-profile kararının gerektirdiği gözlenebilir eyleme göre seçilir. Konuşma, performans, müzik, beden, sanat veya deney kanıtı yalnız yazılı testle temsil edilemez.

## Kitap Ölçme Araçlarının Yapısal Sınıflandırması (7 Temel Tür)

Ders kitabında ve üretilen materyallerde yer alan ölçme-değerlendirme araçları aşağıdaki 7 ayrı türe göre yapısal olarak sınıflandırılır:

1. `assessment_criteria` (Değerlendirme Ölçütleri):
   - Belirli bir görev veya ürün için beklenen ölçütlerin ve açıklamalarının listelendiği, ancak düzey basamakları (puan 1-4 vb.) veya dereceleme sütunları içermeyen ölçüt tablosudur.
2. `checklist` (Kontrol Listesi):
   - Ölçütlerin ikili (binary) düzeyde ("Evet / Hayır", "Var / Yok", "Gözlendi / Gözlenmedi") işaretlendiği formdur.
3. `self_assessment` (Öz Değerlendirme Formu):
   - Öğrencinin kendi öğrenme sürecini, ürününü veya becerisini bizzat değerlendirdiği formdur (yapı olarak kontrol listesi, ölçek veya yansıtma maddeleri içerebilir).
4. `peer_assessment` (Akran Değerlendirme Formu):
   - Bir öğrencinin sınıf arkadaşının sunumunu, metnini, performansını veya grup çalışmasına katkısını değerlendirdiği formdur.
5. `teacher_evaluation_form` (Öğretmen Değerlendirme / Gözlem Formu):
   - Öğretmenin sınıf içi gözlem, performans, tartışma veya ürün değerlendirmesinde kullandığı resmi/yarı resmi kayıt formudur.
6. `analytic_rubric` (Analitik Dereceli Puanlama Anahtarı):
   - Çok boyutlu ölçütlerin her biri için farklı performans düzeylerinin (örneğin Başlangıç, Gelişmekte, Yetkin, İleri Düzey ya da 1-4 puan) her hücresinde **açık ve ayırt edici betimleyiciler (descriptors)** içeren matris yapısındaki araçtır.
7. `rating_scale` (Dereceleme Ölçeği):
   - Ölçütlerin çok basamaklı bir sıklık veya derece skalası üzerinde (örneğin "Her zaman / Bazen / Hiçbir zaman" veya 1'den 5'e puan) derecelendirildiği, ancak analitik rubrikteki gibi her hücre için ayrıntılı performans betimleyicisi barındırmayan formdur.

### Yapısal Sınıflandırma Kuralı (Title vs. Structure)

- Bir değerlendirme aracı **asla yalnızca başlığından sınıflandırılmaz; yapısından sınıflandırılır**.
- Kitapta başlığı "Dereceli Puanlama Anahtarı" veya "Rubrik" olarak yazılmış olsa dahi; eğer tabloda yalnız ölçüt ve genel açıklama varsa ve performans düzeyleri/hücre betimleyicileri yoksa bu araç **analitik rubrik (`analytic_rubric`) sayılamaz**; yapısına göre `assessment_criteria` veya `rating_scale` olarak sınıflandırılır.
- Formlar `textbook_forms_index.json` içerisinde bu 7 yapısal tür ve değerlendirici kimliği (`evaluator`) ile indekslenir.


## Farklılaştırma

İhtiyaca göre:

- içerik: ön bilgi, sadeleştirme, görsel/işitsel alternatif,
- süreç: küçük adım, model, tekrar, esnek grup, ek süre,
- ürün: yazılı, sözlü, görsel, performatif veya dijital seçenek,
- ortam: sessiz alan, azaltılmış dikkat dağıtıcı, erişilebilir araç,
- zenginleştirme: karmaşık bağlam, bağımsız araştırma, alternatif çözüm, tasarım veya eleştiri.

Destek ve zenginleştirme yalnız instructional_needs_analysis ve resource_plan'da gerekçelendirilmişse üretilir; her pakete otomatik eklenmez.

## Erişilebilirlik kontrolleri

Uygulanabildiği ölçüde kontrol et:

- görsel için alt metin veya eşdeğer açıklama,
- ses/video için altyazı ve/veya transkript,
- renk dışı etiket, desen veya sembol,
- okunabilir kontrast ve seçilebilir metin,
- erişilebilir tablo başlıkları,
- gri tonlu baskı,
- yeterli yazma/işaretleme alanı,
- dijital çıktıda yeniden boyutlandırma, klavye ve ekran okuyucu uygunluğu,
- performans/uygulamada alternatif katılım yolu.

Bir medya türü yoksa ilgili alt kontrol N/A olur; bütün erişilebilirlik denetimi gerekçesiz atlanamaz.

## Güvenlik ve mahremiyet

Deney, laboratuvar, spor, saha/gezi, sanat malzemesi, müzik ekipmanı ve dijital etkinliklerde:

- risk/hazard,
- gözetim,
- ekipman ve malzeme,
- güvenli alternatif,
- veri/hesap gereksinimi,
- kişisel veri toplamama,
- kayıt/paylaşım izni

kontrol edilir. Güvenlik veya mahremiyet belirsizse üretim PASS değildir; REVIEW ve öğretmen onayı gerekir. Açık ve ciddi güvenlik eksikliği FAIL'dir.

## Quality Report sözleşmesi

Her üretimde aşağıdaki 15 başlık ayrı raporlanır. Her başlık için yalnız PASS, FAIL, REVIEW veya N/A kullanılabilir. N/A yazılıyorsa neden uygulanmadığı belirtilir.

### Curriculum QA

PASS:

- Kullanıcının sağladığı resmî program VERIFIED olarak çözümlenmiş.
- Her hedef öğrenme çıktısı/süreç bileşeni exact ifade, kod varsa kod ve source locator ile bağlı.
- Resmî alanlar extract edilmiş; generated_activity ile doldurulmamış.

FAIL:

- Öğrenme çıktısı, kod, süreç bileşeni, değer, ders saati veya sürüm uydurulmuş/değiştirilmiş.
- Program kimliği belirsizken veya doğrulanmamışken TYMM hizalaması kesin sunulmuş.
- Öğretim programı yerine araştırma notu, genel bilgi veya web sonucu normatif kaynak yapılmış.

REVIEW:

- OCR, locator, kimlik veya program ifadesi kısmen okunuyor.
- Aynı hedef için kaynaklar arasında çözülmemiş ifade/sürüm çelişkisi var.

N/A:

- Yalnız açıkça TYMM hizalaması iddiası taşımayan, program dışı bir taslak istenmişse. TYMM materyal üretiminde bu istisna gerekçesiz kullanılamaz.

### Textbook QA

PASS:

- Sağlanan resmî ders kitabı kimliği, sınıf/ders, baskı/sürüm ve ilgili sayfa/ünite locator'ları çıkarılmış.
- Mevcut metin, etkinlik, soru, ürün, ölçme, destek ve zenginleştirme unsurları analiz edilmiş.
- Kitapta zaten yeterli karşılık bulunan kaynaklar REUSE_TEXTBOOK veya uygun reuse kararıyla gösterilmiş.

FAIL:

- Normal kitap-temelli istekte kitap yokken veya kitap okunmadan üretim yapılmış.
- Kitapta olmayan etkinlik/ürün/ölçme aracı varmış gibi gösterilmiş.
- Yeterli kitap etkinliği yok sayılarak aynı kaynak yeniden üretilmiş.

REVIEW:

- OCR, sayfa sırası, sürüm veya etkinlik kapsamı belirsiz.
- Bir etkinliğin beklenen kanıtı kesin belirlenemiyor.

N/A:

- Kullanıcı açıkça yalnız program-temelli tanı/plan istemişse; bu durumda kitap yokluğunun sonuçları rapora yazılır ve kitap içeriği iddia edilmez.

### Version QA

PASS:

- Program ve kitap sınıf, ders, program yılı, tema/ünite yapısı ve sürüm bakımından uyumlu veya uyum açıklaması VERIFIED.

FAIL:

- PROGRAM_TEXTBOOK_VERSION_MISMATCH varken sessiz uzlaştırma veya nihai üretim yapılmış.
- Web sonucu kullanıcı dosyasının yerine geçirilmiş.

REVIEW:

- Kimlik veya güncellik doğrulaması eksik; MEB/TYMM kontrolü gerekiyor.

N/A:

- Açıkça program-only çalışma ve ders kitabı kullanılmıyorsa.

### Needs QA

PASS:

- Her instructional need, hedef çıktı/süreç, alan profili, beklenen öğrenci eylemi ve kanıtla bağlı.
- Ön koşul, yanılgı, etkileşim, temsil, pratik, geri bildirim, ölçme, farklılaştırma, erişilebilirlik, güvenlik ve haricî içerik alanları uygun biçimde doldurulmuş veya N/A gerekçeli.
- Karar sırası program → subject-profile → kitap → kanıt → gerekçeli pedagojik kaynak olarak izlenmiş.

FAIL:

- Need yalnız genel pedagojik tahmine veya ders adına dayanıyor.
- Beklenen öğrenci kanıtı belirlenmeden kaynak/ölçme planlanmış.
- Alan profilinin zorunlu eylemi yok sayılmış veya resmî çıktı ile ilişki kurulmamış.

REVIEW:

- Kitap etkinliğinin gerçek öğrenci eylemi/kanıtı kısmen okunuyor.
- Yanılgı, güvenlik veya erişilebilirlik ihtiyacı öğretmen bağlamına bağlı ve doğrulanamıyor.

N/A:

- Öğretimsel ihtiyaç analizi gerektirmeyen açıkça kataloglama veya yalnız mevcut materyal listesi istenmişse.

### Resource Plan QA

PASS:

- Her plan öğesi need_id, hedef çıktı, amaç, beklenen kanıt, textbook_coverage, priority, production_decision ve teacher_review_required alanlarını taşır.
- priority yalnız REQUIRED, RECOMMENDED, OPTIONAL, NOT_NEEDED; production_decision yalnız SKILL.md'deki kontrollü enum'lardandır.
- Plan belge formatından önce instructional function seçer ve kullanıcıdan gereksiz tür seçimi istemez.

FAIL:

- Kaynak türü yalnız ders adına göre seçilmiş veya her konuya aynı paket atanmış.
- Priority/production_decision eksik ya da enum dışı.
- Kitaptaki yeterli kaynağı yeniden üretme kararı verilmiş.

REVIEW:

- Kitap kapsaması, dış kaynak ihtiyacı veya öğretmen incelemesi kesinleşmemiş.

N/A:

- Üretim planında yeni veya uyarlanmış kaynak yoksa ve tüm kararlar REUSE_TEXTBOOK/NO_ACTION olarak kayda geçirilmişse.

### Necessity QA

PASS:

- Her yeni materyal bir need_id, resource_plan_id ve remaining_gap ile gerekçelendirilmiş.
- Kitapta yeterli ve uygun materyal varsa yeniden üretim yapılmamış.

FAIL:

- Kitapta yeterli karşılık varken gereksiz yeni materyal üretilmiş.
- Üretilen materyalin açık instructional need dayanağı yok.
- Kaynak yalnız çıktı paketini büyütmek için eklenmiş.

REVIEW:

- Kitap kapsaması veya pedagojik gereklilik kesin belirlenemiyor.

N/A:

- Yeni materyal üretilmemiş ve yalnız mevcut kitap kaynağı yeniden kullanılmışsa.

### Alignment/Coverage QA

PASS:

- Coverage Matrix şu zinciri locator'larla gösterir: program hedefi → instructional need → önerilen kaynak → kitap karşılığı → kalan gap → üretilen/reuse materyal → öğrenci kanıtı → ölçme aracı.
- Her coverage state COVERED, PARTIALLY_COVERED veya NOT_COVERED; ek need tag'leri kontrollüdür.
- COVERED kararı konu adıyla değil, beklenen öğrenci kanıtıyla doğrulanmıştır.

FAIL:

- Hedef, etkinlik veya ürün zincirin bir halkasına bağlanmamış.
- Kitap konuyu anıyor diye kanıt yokken COVERED denmiş.
- Program/kitap uyuşmazlığı veya unresolved provenance gizlenmiş.

REVIEW:

- Kanıtın yeterliliği, locator veya gap kapsamı tam belirlenemiyor.

N/A:

- Yalnız teşhis/planlama raporu üretilmiş ve henüz materyal/coverage iddiası yapılmamışsa.

### Content QA

PASS:

- İçerik program, kitap ve source_card/provenance ile tutarlı; yaş/ders düzeyine uygun.
- Üretilen pedagojik görev ile resmî içerik açıkça ayrılmış.
- Tarih, veri, alıntı, formül, terminoloji ve medya için kaynak/locator veya doğrulanmış türetim mevcut.

FAIL:

- Uydurma resmî bilgi, kod, alıntı, veri, kaynak veya kesin iddia var.
- İçerik kaynakla çelişiyor veya öğrenci düzeyine açıkça uygunsuz.
- AI tasarımı resmî program ifadesi gibi yazılmış.

REVIEW:

- Kaynaklar arasında çözülmemiş olgusal/terminolojik çelişki veya OCR belirsizliği var.

N/A:

- İçerik üretimi yapılmamış, yalnız kaynak planı/teşhis sunulmuşsa.

### Assessment QA

PASS:

- Beklenen öğrenci kanıtı açık ve gözlenebilir.
- Ölçme aracı bu kanıta ve subject-profile kararına uygun.
- Kitap içi ölçme araçları 7 temel yapısal türe (`assessment_criteria`, `checklist`, `self_assessment`, `peer_assessment`, `teacher_evaluation_form`, `analytic_rubric`, `rating_scale`) göre ve başlığına değil yapısına bakılarak doğru sınıflandırılmış.
- Başarı ölçütleri öğrenci ürünü/eylemiyle uyumlu; geri bildirim yolu belirtilmiş.
- Konuşma, performans, deney, sanat, müzik, beden veya tasarım kanıtı uygun performans/gözlem aracıyla ölçülmüş.

FAIL:

- Kanıt belirlenmeden rubrik/test üretilmiş.
- Araç ölçülmek istenen beceriyi göstermiyor.
- Performans düzeyi veya hücre betimleyicisi olmayan bir tablo yalnızca başlığına bakılarak analitik rubrik (`analytic_rubric`) olarak etiketlenmiş.
- TDE/yabancı dilde konuşma, müzikte performans, bedende hareket, fende deney veya sanatta süreç yalnız yazılı testle ölçülmüş.
- TDE yazma ürününde başarı ölçütü veya geri bildirim kanıtı yok.

REVIEW:

- Ölçütlerin sınıf bağlamına uyarlanması veya performansın gözlemlenmesi öğretmen kararına bağlı.
- Kitaptaki ölçme formunun yapısı veya değerlendirici rolü tam okunamıyor.

N/A:

- Öğrenciden ölçülebilir yeni kanıt istenmeyen yalnız öğretmen uygulama notu üretilmişse.

### Differentiation QA

PASS:

- Need varsa destek/zenginleştirme içerik, süreç, ürün veya ortam düzeyinde somutlaştırılmış.
- Destek hedefi düşürmeden erişimi kolaylaştırıyor; zenginleştirme çekirdek kanıtın yerine geçmiyor.
- İlgili resource_plan ve expected evidence bağlantısı var.

FAIL:

- Gereken destek/zenginleştirme yok veya yalnız kolay/zor soru olarak sunulmuş.
- Farklılaştırma öğrenciyi hedef kanıttan koparıyor ya da ayrıcalıklı/cezalandırıcı tasarlanmış.
- Subject-profile'ın açık erişim ihtiyacı yok sayılmış.

REVIEW:

- Öğrencinin bireysel ihtiyacı, cihazı veya öğrenme ortamı bilinmiyor.

N/A:

- Need analizi ilgili farklılaştırma ihtiyacı olmadığını gerekçeli biçimde gösteriyorsa.

### Accessibility QA

PASS:

- Uygulanabilir her medya için alternatif açıklama, transkript/altyazı, renk dışı anlam, kontrast, seçilebilir metin, tablo başlığı, yazma alanı ve dijital erişim kontrolleri yapılmış.
- Performans/uygulama için güvenli ve erişilebilir katılım alternatifi bulunuyor.

FAIL:

- Anlamlı görsel alt metinsiz, ses/video transkriptsiz veya renk tek anlam taşıyıcı bırakılmış.
- Öğrencinin kullanamayacağı biçim üretilmiş ve eşdeğer alternatif yok.
- Erişilebilirlik ihtiyacı resource plan'da gerekli olduğu halde karşılanmamış.

REVIEW:

- Kaynak dosyanın görsel/OCR özellikleri, medya erişimi veya yardımcı teknoloji uyumu doğrulanamıyor.

N/A:

- İlgili medya/özellik gerçekten yoksa yalnız o alt kontrol için; tüm QA'nın atlanması için değil.

### Copyright QA

PASS:

- Her source_card license_or_copyright değeri kontrollü enum'dan seçilmiş.
- Kullanım kapsamı, alıntı/dönüşüm ve locator belirtilmiş; uzun kısıtlı metin kopyalanmamış.
- Kullanıcı yüklemesi telif izni gibi yorumlanmamış.

FAIL:

- UNKNOWN_RIGHTS veya DO_NOT_USE içerik öğrenci materyaline gömülmüş.
- Uzun telifli ders kitabı/edebî metin otomatik çoğaltılmış.
- Kaynak/lisans/alıntı kapsamı yok veya materyal resmî onaylı gibi sunulmuş.

REVIEW:

- Rights durumu, yeniden kullanım kapsamı veya alıntı sınırı doğrulanamıyor.

N/A:

- Sourced content, alıntı, görsel, veri, medya veya kitap yönlendirmesi kullanılmamışsa.

### Safety QA

PASS:

- Deney, spor, saha, sanat malzemesi, müzik ekipmanı veya dijital etkinlik için risk, gözetim, ekipman, güvenli alternatif ve öğretmen uygulama notu bulunuyor.
- Sağlık/çevre/kimya/fizik iddiaları uygun kaynakla ve güvenli çerçevede verilmiş.

FAIL:

- Güvenlik gerektiren etkinlikte risk veya gözetim yok.
- Güvenli olmayan ev deneyi, yanlış ekipman veya tehlikeli uygulama önerilmiş.
- Fen/beden/sanat/müzik/dijital profilinin açık güvenlik ihtiyacı yok sayılmış.

REVIEW:

- Risk, malzeme, yaş, mekân veya gözetim koşulu kullanıcı dosyasından doğrulanamıyor.

N/A:

- Güvenlik duyarlı deney, hareket, saha, malzeme, ekipman veya dijital işlem yoksa.

### Privacy QA

PASS:

- Gereksiz kişisel veri, hesap, kimlik, sağlık bilgisi veya kamuya açık kayıt istenmiyor.
- Ses/video/ürün paylaşımı için yerel veya izinli alternatif var; veri minimizasyonu uygulanıyor.

FAIL:

- Öğrenciden gereksiz kişisel veri/hesap veya izinsiz kayıt istenmiş.
- Kimliklenebilir içerik kamuya açık platforma yönlendirilmiş.
- Haricî servis/yapay zekâ kullanımı ve veri akışı açıklanmamış.

REVIEW:

- Kayıt, platform, cihaz, hesap veya veli/öğrenci izni bağlama göre netleştirilmeli.

N/A:

- Kayıt, hesap, çevrim içi servis veya kişisel veri işleme yoksa.

### Teacher Review

PASS:

- Öğretmen için kaynak sınırları, kitap locator'ları, gap gerekçesi, uygulama notu ve unresolved alanlar açık.
- Blocking FAIL yok; zorunlu öğretmen kararı gerektiren konu kalmamış.

FAIL:

- Mismatch, rights, safety, privacy veya doğrulanmamış resmî alan varken üretim nihai kabul edilmiş.
- Teacher_review_required=true olduğu halde doğrulama/handoff notu verilmemiş.

REVIEW:

- Öğretmenin sınıf, cihaz, süre, güvenlik, kültürel bağlam veya öğrenci ihtiyacına göre son kararı gerekiyor.

N/A:

- Tüm ilgili QA'lar PASS/N/A, materyal düşük riskli ve ek öğretmen doğrulaması gerektirmiyorsa.

## Subject-profile → QA bağları

- Fen deneyinde safety değerlendirilmemişse Safety QA FAIL; risk bağlamı belirsizse REVIEW.
- TDE, yabancı dil, müzik veya beden çıktısı sözlü/performance olduğu halde yalnız yazılı test kullanılmışsa Assessment QA FAIL.
- Tarihsel kaynak analizi hedefinde source_card, provenance veya locator yoksa Needs QA veya Alignment/Coverage QA FAIL.
- TDE yazma ürününde ölçüt/geri bildirim yoksa Assessment QA FAIL.
- Görsel sanatlar, müzik veya erken yaşta süreç/performans kanıtı yalnız son ürün/bilgi testiyle temsil ediliyorsa Needs QA REVIEW; kanıt yoksa Alignment/Coverage QA FAIL.
- Bilişim/yabancı dilde kayıt veya hesap için mahremiyet ve erişilebilirlik çözümü yoksa Privacy QA veya Accessibility QA FAIL.

## Nihai quality_report durumu

- BLOCKED: Herhangi bir uygulanabilir QA başlığı FAIL ise materyal teslim edilmez veya üretim yeniden planlanır.
- REVIEW_REQUIRED: FAIL yoktur, ancak en az bir uygulanabilir başlık REVIEW'dir; öğretmen onayı ve açık uyarı gerekir.
- PASS: Tüm uygulanabilir başlıklar PASS veya gerekçeli N/A'dır.

