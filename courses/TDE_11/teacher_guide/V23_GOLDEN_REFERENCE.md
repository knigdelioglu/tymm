# Teacher Guide V2.3 — Golden Reference Contract

Bu belge 11. sınıf öğretmen rehberinde kalite düşüşünü erken durdurmak için sabit referans noktasıdır.

## Golden sample

Referans deneyim: `TDE_11_TEMA_01_OGRETMEN_REHBERI.epub` içindeki Tema 1, özellikle basılı s.12–52 akışı.

V2.3, EPUB metnini birebir kopyalamayı değil aşağıdaki kullanım kalitesini korumayı hedefler.

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

## Kalite düştüğünde durma koşulları

Aşağıdakilerden biri görülürse kapsam genişletilmez:

- QUESTION öğelerinde `LOCATOR_ONLY` yeniden normalleşirse,
- kitapta ayrı sorular varken bunlar yalnız canonical gruplama kolaylığı nedeniyle tek kartta birleştirilirse,
- aynı canonical cevap bileşeni birden fazla karta yansıtılırsa,
- aynı öğretmen notu yalnız görev adı değiştirilerek tekrarlanırsa,
- `Pedagojik amaç / Takip soruları / Destek / Zenginleştirme` gibi sabit V2.2 bölümleri her blokta yeniden görünürse,
- kitap başlıkları ve sayfa akışı ikinci plana düşerse,
- canonical coverage artarken öğretmenin soruyu bulma süresi uzarsa,
- sırf alan boş kalmasın diye pedagojik metin üretilirse,
- EPUB golden sample'a göre çıktı daha uzun fakat daha az kullanılabilir hâle gelirse.

Bu durumda önce bu belge, ilgili `book_mirror_v23*.json` fragmentları ve golden EPUB yeniden okunur; sorun giderilmeden Tema 1'in sonraki bölümüne veya Tema 2–4'e geçilmez.
