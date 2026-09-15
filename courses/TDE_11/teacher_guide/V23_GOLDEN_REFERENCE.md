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

## Prompt politikası

- `VERBATIM_SHORT`: kısa soru/yönerge güvenilir biçimde doğrulanmışsa.
- `VERIFIED_SUMMARY`: uzun veya telif açısından yeniden basılması gereksiz içeriğin öğretmenin tanıyacağı sadık kısa tanımı.
- `LOCATOR_ONLY`: yalnız güvenilir tanım üretilemediğinde geçici REVIEW durumu. QUESTION için normal üretim modu değildir.

## Kalite düştüğünde durma koşulları

Aşağıdakilerden biri görülürse kapsam genişletilmez:

- QUESTION öğelerinde `LOCATOR_ONLY` yeniden normalleşirse,
- aynı öğretmen notu yalnız görev adı değiştirilerek tekrarlanırsa,
- `Pedagojik amaç / Takip soruları / Destek / Zenginleştirme` gibi sabit V2.2 bölümleri her blokta yeniden görünürse,
- kitap başlıkları ve sayfa akışı ikinci plana düşerse,
- canonical coverage artarken öğretmenin soruyu bulma süresi uzarsa,
- sırf alan boş kalmasın diye pedagojik metin üretilirse,
- EPUB golden sample'a göre çıktı daha uzun fakat daha az kullanılabilir hâle gelirse.

Bu durumda önce bu belge, `book_mirror_v23.json` ve golden EPUB yeniden okunur; sorun giderilmeden Tema 1'in sonraki bölümüne veya Tema 2–4'e geçilmez.
