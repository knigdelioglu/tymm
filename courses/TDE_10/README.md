# TDE_10

10. sınıf Türk Dili ve Edebiyatı course knowledge alanı.

Bu klasör, TDE_9 ile aynı bilgi üretim zincirini ve aynı fail-closed doğrulama ilkelerini izler:

`source inputs → curriculum/textbook canonical maps → needs → resource plan → alignment → gap analysis → cross-theme audit → production → planning → index → runtime`

## TDE_10 kaynak sözleşmesi

TDE_10 için kaynak biçimi TDE_9'dan farklıdır:

- **Öğretim programı:** `source_docs/` altında tema bazında dört ayrı resmî kaynak snapshot'ı bulunur ve bunlar birlikte tek curriculum source bundle kabul edilir.
- **Ders kitabı primary analysis snapshot:** `source_docs/turk-dili-ve-edebiyati-10.pdf` yerel resmî MEB PDF'sidir.
- **Remote resmî kaynaklar:** TYMM ve OGM bağlantıları identity/provenance cross-check amacıyla tutulur; yerel resmî PDF'nin sessiz ikamesi değildir.

Canonical içerik TDE_9'dan kopyalanmaz veya tahmin edilmez. TDE_9 yalnız şema, doğrulama derinliği ve gate davranışı için referanstır. Resmî TDE_10 snapshot'larında yayımlanmayan alt süreç kodları sentezlenmez.

## Güncel doğrulama durumu

```text
Canonical curriculum                 VERIFIED / FROZEN
Parent learning outcomes             64/64 VERIFIED
Local official textbook PDF          VERIFIED / FROZEN
Textbook sections                    24
Textbook activities                  75
Indexed assessment/form records      35
Alignment                            56 COVERED / 8 PARTIALLY_COVERED / 0 NOT_COVERED
Confirmed resource gaps              0
Unresolved normative targets         8 authenticated EBA DPA targets
Production mode                      PARITY_REVIEW_BLOCKED
Generation                           BLOCKED / UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS
Teaching blocks                      16
Knowledge index                      INDEX_FRESH
Runtime projection                   PASS
Technical P0                         PASS
TDE_9 regression                     PASS (7 gap instances → 3 canonical artifacts)
Parity certification                 WITHHELD pending 8 EBA target structures
Generated new artifacts              0
```

`0 confirmed gap`, tek başına `NO_REQUIRED_ARTIFACTS` anlamına gelmez. Sekiz resmî EBA Dereceli Puanlama Anahtarı bağlantısının hedef içerikleri authentication arkasında kaldığı için yapısal türleri henüz doğrulanamamıştır. Bu sekiz requirement `PARTIALLY_COVERED / REVIEW_REQUIRED` tutulur ve bağlantının varlığı coverage kapatmak için yeterli sayılmaz.

Her tema 45 saatlik dış bloktur: 43 saat resmî tema öğretimi + 2 saat okul temelli planlama. Okul temelli planlama ayrı pedagojik katmandır ve curriculum gap değildir. `knowledge.sqlite` ile runtime SQLite yalnız yeniden üretilebilir projection/cache katmanıdır; canonical JSON/MD source of truth olarak kalır.
