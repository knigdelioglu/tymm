# TDE_10

10. sınıf Türk Dili ve Edebiyatı course knowledge alanı.

Bu klasör, TDE_9 ile aynı bilgi üretim zincirini izler:

`source inputs → curriculum/textbook canonical maps → themes → production → planning → index → runtime`

## TDE_10 kaynak sözleşmesi

TDE_10 için kaynak biçimi TDE_9'dan farklıdır:

- **Öğretim programı:** `source_docs/` altında tema bazında dört ayrı resmî kaynak snapshot'ı bulunur ve bunlar birlikte tek curriculum source bundle kabul edilir.
- **Ders kitabı primary locator:** kullanıcı tarafından sağlanan resmî TYMM/MEB kitap sayfasıdır:
  `https://tymm.meb.gov.tr/kitap/78/turk-dili-ve-edebiyati-10.sinif-ders-kitabi`
- **Ders kitabı supporting assets:** OGM Materyal üzerinde dört resmî MEB tema önizlemesi çözülmüştür. Bunlar mapping desteğidir; primary locator'ın sessiz ikamesi değildir.

Canonical içerik TDE_9'dan kopyalanmaz veya tahmin edilmez. TDE_9 yalnız şema, gate ve mimari davranış için referanstır.

## Güncel üretim durumu

```text
Canonical curriculum                 VERIFIED / FROZEN
Local official textbook PDF          VERIFIED / FROZEN
Program-textbook alignment           64/64 COVERED
Verified resource gaps               0
Production mode                      REUSE_ONLY_NO_NEW_ARTIFACTS
Teaching blocks                      16
Knowledge index                      INDEX_FRESH
Runtime projection                   PASS
P0 gate                              PASS
Generated new artifacts              0
```

Her tema 45 saatlik dış bloktur: 43 saat resmî tema öğretimi + 2 saat okul temelli planlama. Okul temelli planlama ayrı pedagojik katmandır ve curriculum gap değildir. `knowledge.sqlite` ile runtime SQLite yalnız yeniden üretilebilir projection/cache katmanıdır; canonical JSON/MD source of truth olarak kalır.
