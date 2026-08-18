# TDE_10

10. sınıf Türk Dili ve Edebiyatı course knowledge alanı.

Bu klasör, TDE_9 ile aynı bilgi üretim zincirini izler:

`source inputs → curriculum/textbook canonical maps → themes → production → planning → index → runtime`

## TDE_10 kaynak sözleşmesi

TDE_10 için kaynak biçimi TDE_9'dan farklıdır:

- **Öğretim programı:** `source_docs/` altında tema bazında dört ayrı resmî PDF bulunur ve bunlar birlikte tek curriculum source bundle kabul edilir.
- **Ders kitabı:** GitHub'a binary PDF olarak kopyalanmaz. Kullanıcı tarafından sağlanan resmî TYMM/MEB kitap sayfası birincil `official_textbook` locator'ıdır:
  `https://tymm.meb.gov.tr/kitap/78/turk-dili-ve-edebiyati-10.sinif-ders-kitabi`

Kaynakların tam sözleşmesi `source_manifest.json` ve `source_docs/README.md` içinde tutulur.

Canonical içerik, kaynaklar okunup doğrulanmadan TDE_9'dan kopyalanmaz veya tahmin edilmez. Dört curriculum parçasından biri eksik/uyuşmaz ise curriculum `VERIFIED` kabul edilmez. Resmî textbook URL erişilemezse başka bir baskı veya üçüncü taraf kaynak sessizce ikame edilmez.
