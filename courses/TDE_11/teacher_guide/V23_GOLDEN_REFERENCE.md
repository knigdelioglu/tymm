# Teacher Guide V2.3 — Golden Reference Contract

Bu belge 11. sınıf öğretmen rehberinde kalite düşüşünü erken durdurmak için sabit referans noktasıdır.

## Golden sample

Referans deneyim: `TDE_11_TEMA_01_OGRETMEN_REHBERI.epub` içindeki Tema 1, özellikle basılı s.12–52 akışı.

V2.3, EPUB metnini birebir kopyalamayı değil aşağıdaki kullanım kalitesini korumayı hedefler.

EPUB kapsamı s.52'de biter. **s.53 ve sonrasında kalite çıtası düşmez; kaynak çıtası değişir.** Bu noktadan sonra resmî ders kitabı PDF'si ve `textbook_map.json` içindeki `EXACT_PRINTED_HEADING` kayıtları kitap akışının birincil doğrulama kaynağıdır. Canonical teacher-guide verisi cevap ve öğretmen kararı desteği sağlar; kitap başlığını yeniden adlandırmaz.

Tema 1'in tamamı, basılı **s.12–83**, V2.3'ün ilk tam tema referansıdır. Tema 2–4 bu referanstan daha az kitap-merkezli, daha az tanınabilir veya daha fazla generic pedagojik dolgu içeren bir yola genişletilemez.

## Değişmez ilkeler

1. **Kitap önce gelir.** Ana navigasyon ders kitabının sayfa, başlık ve etkinlik sırasıdır.
2. **Soru tanınabilir olmalıdır.** `Ders kitabı s.X — Y. soru` tek başına yeterli değildir. Kısa doğrulanmış soru/görev tanımı gösterilir.
3. **Uzun kitap metni yeniden basılmaz.** Kısa doğrulanmış başlık veya soru özeti, sayfa konumu ve provenance kullanılır.
4. **Cevap hemen sorunun altında bulunur.** Öğretmen cevap ile soruyu zihninde tekrar eşlemek zorunda kalmaz.
5. **Pedagoji seçicidir.** Her item için teacher move / follow-up / support / enrichment doldurulmaz. Yalnız öğretmene somut değer veren not gösterilir.
6. **Genel pedagojik rutinler tekrar edilmez.** Metin kanıtı, gerekçe, kişisel tercihlerin değerlendirilmesi gibi ortak ilkeler rehber başında bir kez verilir.
7. **Öğretmen notu içerik-özgü olmalıdır.** Görev adını çıkardığımızda not başka onlarca etkinlikte aynen kullanılabiliyorsa not fazla generiktir.
8. **Sunum içeriğe uyar.** Soru-cevap, söz varlığı, karşılaştırma, tablo, süreç ve değerlendirme aynı görsel şablona zorlanmaz.
9. **Kitapta soru olmayan sayfa soru gibi modellenmez.** Bilgi köşesi, metin sayfası ve öğretmen zenginleştirmesi açıkça ayrılır.
10. **Tema sonunda hızlı kontrol bulunur.** Öğretmenin ders akışını sayfa bazında denetleyebileceği kısa checklist korunur.
11. **Gruplanmış canonical item kitap akışını ezemez.** Kitapta ayrı sorular varsa `answer_keys` ile canonical cevap bileşenleri ayrı kartlara yansıtılır; cevap metni kopyalanarak yeni canonical nesneler üretilmez.
12. **Mirror parçalı büyüyebilir.** Yeni sayfa aralıkları `book_mirror_v23_*.json` fragmentlarıyla eklenebilir; fragmentlar çakışmaz, arada sayfa boşluğu bırakmaz ve birleşik çıktı tek kitap akışı gibi render edilir.
13. **Kaynakta olmayan değerlendirme düzeyi üretilmez.** Kitap bir dış QR/rubriğe yönlendiriyor ancak ölçüt×düzey matrisi yerel resmî PDF'de görünmüyorsa bu sınır `REVIEW_REQUIRED` olarak korunur; tahminî rubrik yazılmaz.
14. **Üretim becerisinde gerçek kanıt korunur.** Konuşma için yazılı senaryo canlı sözlü performansın; yazma için taslak nihai ürünün yerine geçirilmez.
15. **Dış medya kanıtı uydurulmaz.** Dinleme/izleme veya QR medya sorusunda rehber kabul çerçevesini verir; oynatılan sürüm görülmeden belirli replik, müzik, görsel veya ses ayrıntısını resmî cevap gibi yazmaz.
16. **Kitabın numaralı süreç basamakları başlık değiştirmez.** Bir basamak sonraki sayfaya taşıyorsa sırf sayfa değişti diye başka beceri/aşama altına geçirilmez.

## Prompt politikası

- `VERBATIM_SHORT`: kısa soru/yönerge güvenilir biçimde doğrulanmışsa.
- `VERIFIED_SUMMARY`: uzun veya telif açısından yeniden basılması gereksiz içeriğin öğretmenin tanıyacağı sadık kısa tanımı.
- `LOCATOR_ONLY`: yalnız güvenilir tanım üretilemediğinde geçici REVIEW durumu. QUESTION için normal üretim modu değildir.

## Canonical component projection

`answer_keys`, canonical itemın `expected_answer` nesnesindeki belirli bileşenleri seçer. Bu özellikle aynı canonical item içinde toplanmış birden fazla kitap sorusunu yeniden kitap sırasına ayırmak için kullanılır.

Kurallar:

- `answer_keys` kullanılan entry tek canonical item referans eder.
- Aynı canonical item farklı entry'lerde kullanılacaksa her entry farklı, çakışmayan cevap bileşenlerini seçer.
- Component projection yalnız görünümü ayırır; canonical cevabı çoğaltmaz veya değiştirmez.
- Kitaptaki gerçek soru ayrımı korunabiliyorsa `3 soru` / `4 soru` gibi toplu kart geriye gidiş kabul edilir.

## s.36–52 için özel golden noktalar

- s.36 hazırlık soruları ayrı görünür.
- s.37–38'de mektup metni ile biyografi bilgisi iki ayrı kaynak olarak tutulur; D-G-E-İ yalnız isteğe bağlı öğretmen stratejisidir.
- s.40'taki dört Metni Anlayalım sorusu ayrı karttır.
- s.42 ve s.43, mektup türleri ile karşılaştırma olarak ayrı kitap başlıklarıdır.
- s.44'te yapı unsurları ve devamındaki sorular ayrı görünür; mektupta görünmeyen yer/tarih bilgisi dış kaynaktan tamamlanmaz.
- s.51 bilgi bölümüdür, soru değildir.
- s.52 dilekçe yazma görevi ile Huzur ileri okuma hazırlığı birlikte görünür; örnek öğretmen ürünü kitabın basılı cevabı gibi sunulmaz.

## s.53–58 konuşma/drama için özel kalite noktaları

`textbook_map.json` tarafından doğrulanmış basılı aşama başlıkları aynen korunur:

- s.54: **Konuşmayı Yönetebilme**
- s.55–56: **İçerik Oluşturabilme**
- s.57: **Kural Uygulayabilme**
- s.58: **Süreci Değerlendirebilme**

Ek kurallar:

- s.53'te iletişim engeli yalnız adlandırılmaz; davranış → etki → alternatif doğru davranış bağı görünürdür.
- s.54'te kitabın açıkça istediği altışar kişilik grup ve planlama kararları kaybolmaz.
- s.55–56'da senaryo taslağının nedeni, sonucu, çözümü ve hedef kitleye uygun dil görünürdür; hata–çözüm tablosu ayrı sunulur.
- s.57'de yazılı senaryo canlı sözlü performans yerine geçmez; performans ölçütleri rehberde görünür kalır.
- s.58'de görünür öz değerlendirme ölçütleri kullanılabilir; dış QR içindeki görünmeyen dereceli puanlama matrisi üretilmez. Bu kaynak sınırı çözülene kadar konuşma fragmentı `REVIEW_REQUIRED` kalır.

## s.59–73 dinleme/izleme için özel kalite noktaları

- s.59–73 akışı 2026 resmî ders kitabı PDF'sinden sayfa düzeyinde yeniden doğrulanır; yalnız eski canonical özetine güvenilmez.
- s.66–67'deki **dokuz Metni Anlayalım sorusu dokuz ayrı QUESTION kartıdır**.
- Öğrenciden videodan/sesten örnek isteyen kartlarda rehberdeki cevap, gerçek medya kanıtının yerine geçmez.
- `Birlikte Çalışalım`, `Sıra Sizde`, `Çözümleyebilme` ve `Süreci Değerlendirebilme` kitapta bulunduğu başlık altında kalır.
- s.73'te değerlendirme soruları ile 3-2-1 Çıkış Kartı birbirine eritilmez.

## s.74–78 e-posta yazma için özel kalite noktaları

- s.74'teki beş numaralı soru yapısı, 5a/5b ayrımı nedeniyle rehberde **altı tanınabilir soru kartı** olarak görünür.
- s.75 performans görevinde amaç, alıcı/hedef kitle, olası engel ve strateji kararı nihai e-postadan önce görünürdür.
- s.76–77'deki **13 İçerik Oluşturabilme basamağı** korunur. Özellikle 10–13. basamaklar s.77'de bulunmasına rağmen `Kural Uygulayabilme` başlığına taşınmaz.
- s.77 Kural Uygulayabilme, yalnız yazım/noktalama değil amaç, alıcı, hitap, bütünlük, söz varlığı ve dil işlevini de ürün üzerinde kontrol eder.
- s.78 Öz Değerlendirme Formu ve Çıkış Kartı öğrencinin yerine doldurulmaz.
- s.78'de kitapta görünür genel değerlendirme ölçütleri kullanılabilir; dış QR'deki görünmeyen dereceli puanlama düzeyleri üretilmez. Yazma fragmentı bu sınır çözülene kadar `REVIEW_REQUIRED` kalır.

## s.79–83 tema ölçme ve değerlendirme için özel kalite noktaları

- Resmî PDF'de doğrulanan **13 soru 13 ayrı soru kartıdır**.
- Çoktan seçmeli soruda seçenek anahtarı yanında gerekçe; açık uçlu soruda kabul ölçütü ve metin kanıtı verilir.
- Özgün diyalog veya çağdaş sanatçı karşılaştırması gibi sorularda rehber örneği tek doğru ürün hâline getirilmez.
- Soru 12'de `Bilgi yok`, metnin açıkça yanlışladığı cümle için değil, metnin doğrulamadığı ve çürütmediği cümle için kullanılır.
- Soru 13'ün EBA/Olvido kaynağı dış medyadır; oynatılan sürüm görülmeden belirli müzik, görsel, renk veya ses ayrıntısı uydurulmaz. Bu nedenle tema değerlendirme fragmentı kaynak sınırı çözülene kadar `REVIEW_REQUIRED` kalır.

## Tam Tema 1 referans checkpointi

Son yeşil checkpointte birleşik V2.3 çıktısı:

- kapsam: **basılı s.12–83**,
- mirror fragmentı: **6**,
- kitap-akışı entry: **126**,
- QUESTION kartı: **78**,
- tanınabilir QUESTION: **78/78**,
- `LOCATOR_ONLY` QUESTION: **0**,
- canonical component projection: **83**,
- birden fazla karta ayrılan canonical item: **17**,
- öğretmen notu yoğunluğu: **0.508**,
- PDF-doğrulanmış dinleme sorusu: **9**,
- PDF-doğrulanmış yazma sorusu: **6**,
- PDF-doğrulanmış tema sonu sorusu: **13**,
- V2.3 quality warnings: **0**,
- V2.3 quality failures: **0**,
- TDE11 generic P0: **PASS**,
- TDE9/TDE10 regression guard: **PASS**.

Bu sayılar hedef üretim kotası değildir; **regresyon işaretidir**. Sonraki temada daha az entry olması doğrudan hata değildir, fakat soru görünürlüğü, kaynak sadakati veya öğretmen kullanılabilirliği düşüyorsa kapsam genişletilmez.

## Kalite düştüğünde durma koşulları

Aşağıdakilerden biri görülürse kapsam genişletilmez:

- QUESTION öğelerinde `LOCATOR_ONLY` yeniden normalleşirse,
- kitapta ayrı sorular varken bunlar yalnız canonical gruplama kolaylığı nedeniyle tek kartta birleştirilirse,
- aynı canonical cevap bileşeni birden fazla karta yansıtılırsa,
- aynı öğretmen notu yalnız görev adı değiştirilerek tekrarlanırsa,
- `Pedagojik amaç / Takip soruları / Destek / Zenginleştirme` gibi sabit V2.2 bölümleri her blokta yeniden görünürse,
- kitap başlıkları ve sayfa akışı ikinci plana düşerse,
- `EXACT_PRINTED_HEADING` ile doğrulanmış aşama başlıkları yeniden adlandırılırsa,
- kaynakta görünmeyen QR/rubrik ayrıntıları tahmin edilirse,
- dış medya görülmeden replik/müzik/görsel/ses ayrıntısı resmî cevap gibi yazılırsa,
- konuşma görevi yazılı senaryoya indirgenip canlı performans kanıtı kaybolursa,
- yazma sürecinin numaralı basamakları sayfa değişimi nedeniyle yanlış aşama başlığına taşınırsa,
- canonical coverage artarken öğretmenin soruyu bulma süresi uzarsa,
- sırf alan boş kalmasın diye pedagojik metin üretilirse,
- EPUB golden sample'a göre çıktı daha uzun fakat daha az kullanılabilir hâle gelirse.

Bu durumda önce bu belge, ilgili `book_mirror_v23*.json` fragmentları ve (kapsama göre) golden EPUB / resmî PDF + `textbook_map.json` yeniden okunur; sorun giderilmeden sonraki tema veya bölüme geçilmez.
