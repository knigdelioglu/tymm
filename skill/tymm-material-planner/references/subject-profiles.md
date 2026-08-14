# Subject profiles as deterministic decision rules

## Amaç ve ortak karar şeması

Subject-profile, belge türü kataloğu değil; öğrenme çıktısı ve beklenen kanıttan öğretimsel kaynak kararına giden alan motorudur. Profil seçimi ders adına göre değil, resmî program, sınıf/konu, ders kitabı ve beklenen kanıt birlikte incelenerek yapılır.

Her profil aşağıdaki alanları uygular:

1. temel öğrenme eylemleri,
2. beklenen öğrenci kanıtları,
3. yaygın yanlış öğrenmeler/kavram yanılgıları,
4. hangi durumda hangi kaynak işlevinin gerektiği,
5. kanıt–ölçme aracı eşleşmesi,
6. REQUIRED / RECOMMENDED / OPTIONAL / NOT_NEEDED kararı,
7. destek ve zenginleştirme,
8. erişilebilirlik,
9. güvenlik ve mahremiyet,
10. anti-pattern'ler.

### Öncelik mantığı

- REQUIRED: Resmî çıktı/süreç bileşeni için gereken eylem veya kanıt, kaynak olmadan gerçekleştirilemiyor ve kitapta yeterli karşılık yok. Zorunlu ön koşul, güvenlik veya erişilebilirlik desteği de bu kararı doğurabilir.
- RECOMMENDED: Kitapta kısmi karşılık var veya kaynak uygulama, geri bildirim ya da farklılaştırmayı güçlendiriyor; çekirdek kanıt başka yolla elde edilebilir.
- OPTIONAL: Çekirdek çıktının dışında zenginleştirme, alternatif bağlam, bağımsız araştırma veya ileri ürün sağlar.
- NOT_NEEDED: İlgili need_id, beklenen kanıt veya alan kuralı bağlantısı yoktur ya da kitapta yeterli karşılık vardır. Kaynak paketi büyüsün diye üretilmez.

### Ortak kanıt–araç eşleşmesi

- Bilgi/terim → kısa cevap veya seçilmiş yanıt.
- Süreç gözlemi → kontrol listesi/gözlem formu.
- Çok boyutlu yazılı/görsel ürün → analitik dereceli puanlama anahtarı.
- Performans/sunum/uygulama → performans rubriği veya gözlem formu.
- Tartışma/etkileşim → katılım ve gerekçelendirme ölçütleri.
- Yansıtma → öz değerlendirme/öğrenme günlüğü.
- Gelişim → portfolyo.
- Hızlı ders sonu kanıtı → çıkış bileti.

Kanıt belirlenmeden rubrik, test veya çalışma kâğıdı seçilmez.

## Erken yaş ve hayat bilgisi

- Öğrenme eylemleri: oyun, keşif, hareket, rutin, rol oynama, iletişim, seçim ve iş birliği.
- Kanıtlar: davranış gözlemi, sözlü ifade, görsel seçim, somut ürün, performans ve portfolyo.
- Yanlış öğrenmeler: doğru cevabı tekrarlamanın genelleme olduğu; tek ürünün gelişimi tam gösterdiği; uzun yazılı çalışmanın bağımsızlığı ölçtüğü varsayımı.
- Kaynak kararı: görsel yönerge/oyun/istasyon/somut materyal eylem olmadan öğrenme gerçekleşmiyorsa REQUIRED; kitapta yeterliyse REUSE_TEXTBOOK. Gözlem formu davranış veya süreç kanıtı için REQUIRED. Kavram kartı, rutin görseli ve sözel model dilsel/erişilebilirlik ihtiyacında RECOMMENDED, temel katılımı sağlıyorsa REQUIRED. Açık uçlu keşif OPTIONAL; yoğun metin ve hedefe bağlanmayan boyama NOT_NEEDED.
- Ölçme: gözlem formu, performans kaydı, ürün ve portfolyo. Yazılı test tek başına uygun değildir.
- Destek/erişilebilirlik: küçük adım, model, tekrar, sözlü-görsel alternatif, açık alan, erişilebilir materyal; renk tek anlam taşıyıcı değildir.
- Güvenlik/anti-pattern: hareket, küçük parça ve aile etkinliğinde gözetim, malzeme ve güvenli alternatif belirtilir. Gereksiz rekabet, tek doğru ürün ve gereksiz kişisel veri sınıflandırması yapılmaz.

## TDE / Türkçe

- Öğrenme eylemleri: okuma, dinleme/izleme, yakın okuma, anlamlandırma, metinler arası ilişki, konuşma, sunum, yazma ve yansıtma.
- Kanıtlar: gerekçeli anlama yanıtı, karşılaştırma, sözlü sunum/etkileşim, yazılı ürün, söz varlığı kullanımı ve öz değerlendirme.
- Yanlış öğrenmeler: özetin çıkarımla aynı olduğu; görüşün kanıt gerektirmediği; dil bilgisinin metin içi kullanımı tek başına gösterdiği; akıcı okumanın anlamayı kanıtladığı varsayımı.
- Kaynak kararı: temel metin/ses/görsel girdi kitapta yoksa veya uygun değilse REQUIRED; varsa REUSE_TEXTBOOK veya REUSE_WITH_TEACHER_GUIDE. Yakın okuma, kavram/kelime ve soru basamakları hedef eylem kitapta yoksa REQUIRED, kısmi ise RECOMMENDED. Konuşma/yazma görevi çıktı bunu istiyorsa REQUIRED, yalnız okuma hedefinde NOT_NEEDED. Çok boyutlu ürün için başarı ölçütü ve geri bildirim REQUIRED. Karşılaştırma/alternatif medya çekirdek dışıysa OPTIONAL. Uzun telifli metni yeniden basmak NOT_NEEDED.
- Ölçme: anlama için açık uçlu yanıt/zihin haritası; konuşma için performans gözlemi/rubrik; yazma için ölçütlü rubrik ve taslak geri bildirimi; gelişim için günlük/portfolyo.
- Destek/erişilebilirlik: kelime havuzu, cümle başlangıcı, örnek ürün, sesli/görsel alternatif, seçilebilir metin, transkript, okunabilir düzen ve renk dışı işaretleme.
- Güvenlik/anti-pattern: kayıt ve çevrim içi paylaşımda izin/mahremiyet kontrolü. Konuşma/yazmayı yalnız yazılı testle ölçme, hedef kanıtı olmadan rubrik üretme ve uzun metin çoğaltma yapılmaz.

## Matematik

- Öğrenme eylemleri: problem kurma/çözme, tahmin, temsil değiştirme, modelleme, akıl yürütme, gerekçelendirme, strateji karşılaştırma, hata analizi ve veriyle karar verme.
- Kanıtlar: çözüm yolu, tablo/şema/grafik/sembol, model, açıklama, hata düzeltme, alternatif strateji ve veri yorumu.
- Yanlış öğrenmeler: yalnız sonucun yeterli olduğu; tek temsilin kavramı gösterdiği; doğru yöntemin tek olduğu; hatanın yalnız dikkatsizlikten kaynaklandığı varsayımı.
- Kaynak kararı: problem durumu/modelleme hedefi varsa REQUIRED; kitapta yeterliyse REUSE_TEXTBOOK. Çoklu temsil/modelleme hedefinde temsil REQUIRED. Hata analizi ve strateji karşılaştırması muhakeme hedefinde RECOMMENDED, yanılgı kanıtında REQUIRED. İşlemsel pratik yalnız akıcılık/işlem çıktısı ve kanıt bunu gerektiriyorsa REQUIRED; aksi OPTIONAL veya NOT_NEEDED. Teknoloji ancak program ve kanıt gerektiriyorsa RECOMMENDED/REQUIRED; düğme ezberi NOT_NEEDED.
- Ölçme: çözüm yolu/gerekçe için açık uçlu görev; süreç için gözlem; kavram için kısa cevap/çıkış bileti; gelişim için portfolyo.
- Destek/erişilebilirlik: ön bilgi, adım kartı, örnek temsil, sayı doğrusu, sözlü açıklama, farklı ürün; büyük okunabilir gösterim, sembol açıklaması, klavye/ekran okuyucu ve renk dışı gösterim.
- Güvenlik/anti-pattern: fiziksel araç/saha verisinde güvenlik. Otomatik işlem sayfası, yalnız sonuca puan, tek strateji zorlama ve çıktısız teknoloji ekleme yapılmaz.

## Fen bilimleri: fizik, kimya, biyoloji

### Ortak karar motoru

- Öğrenme eylemleri: olguyu gözleme, soru/tahmin, hipotez, değişken belirleme, deney/araştırma, veri toplama, modelleme, kanıtla açıklama, tasarım ve yansıtma.
- Kanıtlar: gözlem kaydı, veri tablosu/grafik, model, çıkarım, iddia–kanıt–gerekçe, prototip, deney raporu ve yansıtma.
- Yanlış öğrenmeler: gözlem ile çıkarımın aynı olduğu; korelasyonun neden olduğu; tek ölçümün yeterli olduğu; modelin gerçeğin aynısı olduğu; terim bilmenin açıklama olduğu varsayımı.
- Kaynak kararı: sorgulama için olgu/soru kartı REQUIRED. Gözlem/veri/deney kanıtı için deney veya veri föyü REQUIRED; kitapta güvenli ve yeterliyse REUSE_TEXTBOOK. Deney, saha veya malzemede güvenlik notu REQUIRED; güvenlik belirsizse Safety QA REVIEW ve üretim durur. Grafik/model/simülasyon soyut süreci görünür kılıyorsa RECOMMENDED, başka kanıt yolu yoksa REQUIRED, süs amaçlıysa NOT_NEEDED. İddia–kanıt–gerekçe ve yanılgı kontrolü açıklama hedefinde RECOMMENDED, kanıtın parçasıysa REQUIRED. İleri veri/tasarım OPTIONAL.
- Ölçme: veri/grafik yorumu; deney gözlem formu/raporu; model/prototip rubriği; kavram kısa yanıtı/çıkış bileti; süreç kontrol listesi.
- Destek/erişilebilirlik: şema açıklaması, dokunsal/işitsel alternatif, transkript, büyük yazı ve renk dışı gösterim.
- Güvenlik/anti-pattern: risk, gözetim, ekipman ve güvenli alternatif açık değilse PASS verilmez. Güvenliksiz ev deneyi, yalnız terim testi ve kaynaksız sağlık/çevre iddiası yapılmaz.

### Alan özel kuralları

- Fizik: hareket/kuvvet/enerji için diyagram, grafik, ölçüm ve birim kontrolü; serbest cisim veya çoklu temsil çıktısı varsa REQUIRED.
- Kimya: makro–mikro–sembolik temsil, gözlem–yorum ayrımı ve laboratuvar güvenliği; güvenli uygulama yoksa güvenli alternatif gerekir.
- Biyoloji: yapı–işlev, sistem, gözlem/model ve etik; canlı materyal/saha işinde bakım, izin ve zarar vermeyen alternatif değerlendirilir.

## Tarih / sosyal bilgiler / coğrafya

- Öğrenme eylemleri: kaynak inceleme, provenans sorgulama, kronoloji, karşılaştırma, perspektif alma, harita/veri okuma, mekânsal ilişki ve iddia–kanıt kurma.
- Kanıtlar: kaynak analiz formu, zaman çizelgesi, harita/grafik yorumu, kanıt temelli açıklama, tarihsel anlatı, yurttaşlık ürünü veya mekânsal analiz.
- Yanlış öğrenmeler: kitap anlatısının tek kaynak olduğu; iddianın kaynaksız kurulabileceği; kronolojinin neden-sonuç olduğu; haritanın yer adı ezberi olduğu; tek bakış açısının tarafsız olduğu varsayımı.
- Kaynak kararı: kaynak değerlendirme veya iddia–kanıt hedefinde birincil/ikincil kaynak ve provenance kartı REQUIRED. Kaynak/locator yoksa Needs QA veya Alignment/Coverage QA FAIL. Kronoloji, harita, veri/grafik beklenen kanıtsa REQUIRED, destekse RECOMMENDED. Farklı perspektif çıktı parçasıysa REQUIRED, ileri tartışmaysa OPTIONAL. Kitap anlatısını kaynak yerine çoğaltmak NOT_NEEDED. Yerel/güncel veri çekirdek kanıt için gerekiyorsa REQUIRED; haricî kaynak yalnız gerekçeli gap ile alınır.
- Alan özel kuralları: tarih için kronoloji/provenans/değişim-süreklilik; sosyal bilgiler için vaka, karar, yurttaşlık ve iş birliği ürünü; coğrafya için harita, ölçek, grafik, mekânsal veri ve saha alternatifi.
- Ölçme: kaynak analizi rubriği/kontrol listesi; vaka/rol performans gözlemi; harita/veri açık uçlu yanıt veya rubrik.
- Destek/erişilebilirlik/güvenlik: metin locator'ı, harita metin açıklaması, yüksek kontrast, sembol açıklaması, seçilebilir kaynak, saha için gezisiz alternatif ve güvenlik.
- Anti-pattern: provenanssuz tarihsel iddia, tek görüşü kesin gerçek sunma, yalnız ezber testi ve sürümsüz güncel veri.

## Felsefe

- Öğrenme eylemleri: felsefi soru, kavramlaştırma, örnek/karşı örnek, gerekçelendirme, karşı görüş, diyalog ve yansıtma.
- Kanıtlar: kavram/argüman haritası, tartışma katkısı, gerekçeli yazı, soru üretimi ve düşünce günlüğü.
- Yanlış öğrenmeler: kişisel görüşün argüman olduğu; filozof adının düşünmeyi gösterdiği; her görüşün eşit kanıtlı olduğu; tartışmada kazanmanın düşünme kanıtı olduğu varsayımı.
- Kaynak kararı: uyaran/soru hedef düşünmeyi başlatmak için REQUIRED. Kavram/argüman düzenleyici ve diyalog protokolü etkileşim/gerekçe kanıtında RECOMMENDED, kanıtın kendisiyse REQUIRED. Gerekçeli yazı ölçütü REQUIRED. Alternatif görüş çekirdek perspektif hedefindeyse REQUIRED, ileri araştırmada OPTIONAL. İsim/tanım listesi NOT_NEEDED.
- Ölçme: argüman haritası, tartışma gözlemi, açık uçlu yazı rubriği, yansıtma günlüğü; içerikten çok soru, gerekçe, karşı görüş ve tutarlılık ölçülür.
- Destek/erişilebilirlik/anti-pattern: örnek, şema, sözlü alternatif ve düşünme süresi; kişisel inancı açıklamaya zorlama, tek görüşü doğru cevap yapma ve yalnız bilgi testi kullanılmaz.

## Yabancı dil

- Öğrenme eylemleri: dinleme/izleme, okuma, hedef dilde etkileşim, söz varlığı/yapı kullanımı, konuşma, yazma ve öz değerlendirme.
- Kanıtlar: düzeye uygun anlama yanıtı, hedef dilde sözlü etkileşim, konuşma performansı/kaydı, yazılı iletişim ürünü ve yansıtma.
- Yanlış öğrenmeler: dil bilgisi kuralının iletişim olduğunu; çevirinin hedef dilde anlamayı kanıtladığını; akıcılığın doğrulukla aynı olduğunu; yazılı testin konuşmayı ölçtüğünü sanma.
- Kaynak kararı: düzeye uygun girdi anlama/iletişim için REQUIRED; kitapta yeterliyse REUSE_TEXTBOOK. Kelime/ifade desteği, model diyalog ve cümle başlangıcı üretim için RECOMMENDED, temel erişimde REQUIRED. Eşli etkileşim ve konuşma görevi sözlü çıktı için REQUIRED. Konuşma ölçütü/performance görevi REQUIRED; yazılı test tek araç olamaz. Transkript/altyazı ve görsel sözlük erişim için RECOMMENDED; çıktı olmayan video NOT_NEEDED. Rol oyunu/proje çekirdek iletişim için REQUIRED, genişletmeyse OPTIONAL.
- Ölçme: dinleme/okuma anlama görevi; konuşma performans gözlemi/rubriği; yazma ürün rubriği; süreç öz/akran değerlendirmesi.
- Destek/erişilebilirlik/güvenlik: kelime havuzu, model, tekrar, bekleme ve seviyeli görev; transkript, altyazı, görsel destek, kayıt yerine yerel alternatif. Kayıt/platform/hesapta izin ve mahremiyet kontrol edilir.
- Anti-pattern: dilbilgisi sayfasını iletişim yerine koyma, yalnız çeviri, konuşmayı yazılı testle ölçme, düzey dışı metin ve izinsiz kayıt.

## Din eğitimi / DKAB

- Öğrenme eylemleri: uygun/resmî kaynağı okuma-yorumlama, kavram ilişkisi, soru, değer/ahlak durumunu değerlendirme, günlük yaşamla ilişkilendirme, saygılı diyalog ve program açıkça istiyorsa tilavet/ezber/hitabet/uygulama.
- Kanıtlar: kaynak anlamlandırma, kavram haritası, gerekçeli durum analizi, saygılı sözlü katkı, yansıtma ve gerekiyorsa uygulama/performans.
- Yanlış öğrenmeler: ezberin anlamayı kanıtladığı; kişisel inanç beyanının akademik kanıt olduğu; farklı inanç/yorumları stereotipleştirmenin karşılaştırma olduğu; kaynaksız alıntının doğru olduğu varsayımı.
- Kaynak kararı: programın işaret ettiği kaynak/kavram kitapta yetersizse REQUIRED; alıntı/provenance ve kaynak sadakati zorunlu. Kavram haritası, vaka ve diyalog düzenleyicisi anlamlandırma/muhakeme için RECOMMENDED, kanıtın parçasıysa REQUIRED. Tilavet/ezber/hitabet/uygulama yalnız çıktı açıkça istiyorsa REQUIRED, aksi NOT_NEEDED. Farklı yorum/bağımsız araştırma perspektif çıktısıysa REQUIRED, genişletmeyse OPTIONAL. Kişisel inancı ölçen veya doğrulanmamış içerik NOT_NEEDED/DO_NOT_USE.
- Ölçme: kaynak yorumu için açık uçlu yanıt; kavram için şema; vaka için rubrik; sözlü/tilavet/hitabet için performans gözlemi; yansıtma için öz değerlendirme.
- Destek/erişilebilirlik/güvenlik: terim sözlüğü, sade dil, sesli/görsel metin ve alternatif ifade; alıntılar doğru kaynak/telif kontrolünden geçer, kişisel inanç açıklaması zorunlu değildir.
- Anti-pattern: inanç dayatması, kimlik/mezhep puanlaması, karikatürleştirme, kaynaksız kesin hüküm ve yalnız ezber testi.

## Görsel sanatlar

- Öğrenme eylemleri: gözlem, betimleme, yorum, teknik deneme, tasarım, üretim, revizyon, bağlamlandırma ve eleştiri.
- Kanıtlar: eskiz/süreç günlüğü, sanat ürünü, teknik uygulama, bağlam açıklaması, akran/öz değerlendirme ve portfolyo.
- Yanlış öğrenmeler: tek doğru/estetik ürün olduğu; tekniğin yaratıcılık olduğu; son ürünün süreci tam gösterdiği; kişisel tarzın puanlanabileceği sanısı.
- Kaynak kararı: görsel uyaran/eser/bağlam/teknik yönerge görsel okuma veya üretim için REQUIRED. Malzeme/araç alternatifi ve adım kartı erişim/süreç için REQUIRED veya RECOMMENDED. Eskiz/süreç günlüğü/portfolyo süreç kanıtı için REQUIRED. Galeri veya sanatçı karşılaştırması çekirdek bağlamdaysa RECOMMENDED, genişletmeyse OPTIONAL. Süs posteri, tek estetik şablon ve uzun tarih özeti NOT_NEEDED.
- Ölçme: ürün/süreç rubriği veya portfolyo; teknik gözlem; görsel yorum için açık uçlu yanıt.
- Destek/erişilebilirlik/güvenlik: alt metin/sözlü açıklama, yüksek kontrast, dokunsal/işitsel alternatif, motor uyarlama; kesici, boya, toz, alerjen için risk/gözetim/güvenli alternatif.
- Anti-pattern: tek estetik standarda puan, örneği kopyalatma ve malzeme güvenliğini atlama.

## Müzik

- Öğrenme eylemleri: dinleme, ayırt etme, ritim/melodi, söyleme, çalma, hareket, notasyon, doğaçlama, besteleme ve müzik hakkında konuşma.
- Kanıtlar: dinleme analizi, ritim/notasyon, ses/video performansı, grup uygulaması, beste/doğaçlama ve portfolyo.
- Yanlış öğrenmeler: notasyonun müzik yapmayı tek başına gösterdiği; tek doğru yorum olduğu; doğruluğun müzikal düşünmenin tamamı olduğu; yalnız dinlemenin uygulama kanıtı olduğu varsayımı.
- Kaynak kararı: dinleme/ritim/notasyon/eser girdisi hedef ayırt etme/uygulama için REQUIRED; kitapta varsa REUSE_TEXTBOOK. Seslendirme/çalgı ve uygun alternatif performans çıktısı için REQUIRED. Görsel nota, beden perküsyonu ve çevrim dışı ses alternatifi erişim için RECOMMENDED, temel eylem mümkün değilse REQUIRED. Beste/doğaçlama yaratıcılık çıktısıysa REQUIRED, genişletmeyse OPTIONAL. Yalnız tarih bilgi testi performans/işitme kanıtı beklenirken NOT_NEEDED.
- Ölçme: performans gözlemi/rubriği; dinleme yapılandırılmış yanıt; notasyon kısa ürün; gelişim portfolyosu.
- Destek/erişilebilirlik/güvenlik: görsel notasyon, titreşim/hareket, farklı çalgı/rol; ses düzeyi, kulak sağlığı, ekipman ve grup alanı.
- Anti-pattern: yalnız yetenek/estetik puanı, tek çalgı zorunluluğu, performansı yazılı testle ölçme ve izinsiz kayıt.

## Beden eğitimi / oyun / spor

- Öğrenme eylemleri: hareketi gözleme/deneme, beceri uygulama, kurala göre oyun, strateji, iş birliği, adil oyun, kişisel ilerleme ve yansıtma.
- Kanıtlar: hareket performansı, öğretmen/akran gözlemi, ilerleme kaydı, kural/strateji açıklaması, iş birliği ve öz değerlendirme.
- Yanlış öğrenmeler: kazanmanın öğrenme olduğu; uygunluk normunun beceriyi gösterdiği; tek doğru beden/tempo olduğu; sakatlık riskinin göz ardı edilebileceği.
- Kaynak kararı: hareket gösterimi, istasyon, alan/ekipman ve güvenlik yönergesi uygulamalı çıktı için REQUIRED. Görsel ipucu, basamak ve kapsayıcı uyarlama katılım/güvenlik için REQUIRED, kolaylaştırıcıysa RECOMMENDED. Kural/rol/strateji kartı oyun hedefinde RECOMMENDED veya REQUIRED. İleri turnuva/fitness günlüğü çekirdek çıktıdaysa REQUIRED, genişletmeyse OPTIONAL. Uzun teori, güvenliksiz etkinlik ve yalnız performans normu NOT_NEEDED.
- Ölçme: canlı gösterim gözlem/rubriği; kural-strateji kısa açıklaması; kişisel gelişim öz değerlendirme/portfolyo.
- Destek/erişilebilirlik/güvenlik: tempo, hareket açıklığı, ekipman, rol ve alan uyarlaması; ısınma, alan, ekipman, gözetim, risk ve güvenli alternatif. Koşullar yoksa Safety QA FAIL, belirsizse REVIEW.
- Anti-pattern: kazanana puan verme, herkesi aynı normla kıyaslama, sakatlığı görmezden gelme ve yalnız yazılı sınav.

## Bilişim / yazılım / tasarım / teknoloji

- Öğrenme eylemleri: problemi/kullanıcıyı tanımlama, kısıt, parçalama, algoritma/tasarım, kod/prototip, test, hata ayıklama, veri, değerlendirme ve yineleme.
- Kanıtlar: problem tanımı, akış/algoritma, ürün, test senaryosu/logu, hata düzeltme izi, kullanıcı geri bildirimi, demo ve yansıtma.
- Yanlış öğrenmeler: sözdiziminin algoritmik düşünme olduğu; bir kez çalışmanın test olduğu; araç düğmelerinin tasarım becerisi olduğu; kopya kodun öğrenme kanıtı olduğu; veri/gizliliğin teknik işten ayrı olduğu.
- Kaynak kararı: problem bağlamı, kullanıcı ihtiyacı ve kısıt tasarım çıktısı için REQUIRED. Algoritma/akış, örnek veri ve prototip planı planlama/modelleme kanıtında REQUIRED veya RECOMMENDED. Test planı, hata ayıklama ve geri bildirim ürün kalitesi/yineleme kanıtında REQUIRED. Araç yönergesi yalnız program/görev belirli araç gerektiriyorsa RECOMMENDED/REQUIRED; düğme ezberi NOT_NEEDED. Çevrim dışı alternatif/erişilebilir arayüz koşula göre RECOMMENDED, genişletilmiş senaryo OPTIONAL.
- Ölçme: ürün/demo performans rubriği; algoritma açıklaması/akış; test kontrol listesi; süreç günlüğü/portfolyo; veri açık uçlu görevi.
- Destek/erişilebilirlik/güvenlik: blok/metin/kâğıt alternatifleri, örnek hata, ekran okuyucu/klavye erişimi; hesap, kişisel veri, paylaşım, haricî servis, yapay zekâ ve cihaz için izin/mahremiyet/güvenlik/çevrim dışı plan.
- Anti-pattern: araç öğretimini hedef sanma, kişisel veri toplama, kaynağı belirsiz kod/veri, testsiz kalite iddiası ve tek erişilemez platform.

## Profil → Quality Report bağlantısı

- Fen deneyinde risk, ekipman, gözetim veya güvenli alternatif yoksa Safety QA = FAIL; bağlam/risk belirsizse REVIEW.
- TDE, yabancı dil, müzik veya beden gibi sözlü/performance çıktısında yalnız yazılı test varsa Assessment QA = FAIL.
- Tarihsel kaynak analizi hedefinde source_card, provenance veya locator yoksa Needs QA veya Alignment/Coverage QA = FAIL.
- TDE yazma ürününde başarı ölçütü ve geri bildirim kanıtı yoksa Assessment QA = FAIL.
- Görsel sanatlar, müzik veya erken yaşta süreç/performans kanıtı yalnız son ürün/bilgi testiyle temsil ediliyorsa Needs QA = REVIEW; kanıt hiç elde edilemiyorsa Alignment/Coverage QA = FAIL.
- Bilişim veya yabancı dilde kayıt/hesap kullanımı için mahremiyet ve erişilebilirlik çözümü yoksa Privacy QA veya Accessibility QA = FAIL.

Profil kuralı hedeflenen çıktı ve kitap bağlamında uygulanmıyorsa kaynak üretilmez; karar NOT_NEEDED olarak gerekçelendirilir.

