# TDE_10

10. sınıf Türk Dili ve Edebiyatı course knowledge alanı.

Bu klasör, TDE_9 ile aynı bilgi üretim zincirini izler:

`source inputs → curriculum/textbook canonical maps → themes → production → planning → index → runtime`

## TDE_10 kaynak sözleşmesi

TDE_10 için kaynak biçimi TDE_9'dan farklıdır:

- **Öğretim programı:** `source_docs/` altında tema bazında dört ayrı resmî kaynak snapshot'ı bulunur ve bunlar birlikte tek curriculum source bundle kabul edilir.
- **Ders kitabı:** GitHub'a binary PDF olarak kopyalanmaz. Kullanıcı tarafından sağlanan resmî TYMM/MEB kitap sayfası birincil `official_textbook` locator'ıdır:
  `https://tymm.meb.gov.tr/kitap/78/turk-dili-ve-edebiyati-10.sinif-ders-kitabi`

Kaynakların tam sözleşmesi `source_manifest.json` ve `source_docs/README.md` içinde tutulur.

Canonical içerik, kaynaklar okunup doğrulanmadan TDE_9'dan kopyalanmaz veya tahmin edilmez. Dört curriculum parçasından biri eksik/uyuşmaz ise curriculum `VERIFIED` kabul edilmez. Resmî textbook URL erişilemezse başka bir baskı veya üçüncü taraf kaynak sessizce ikame edilmez.

## Güncel üretim durumu

```text
Source registration                  PASS
Curriculum map draft                 CREATED
Official web theme identity          PASS
64 scoped learning outcomes          MAPPED
Stable entity keys                   UNIQUE
Theme time model                     45 = 43 + 2
Annual time model                    180 = 172 + 8
Curriculum process components        PENDING PDF EXTRACTION
Curriculum freeze                    NOT FROZEN
Textbook map                         PENDING
Textbook forms index                 PENDING
Theme alignment / gap analysis       BLOCKED BY TEXTBOOK MAP
Production / index / runtime / P0    NOT STARTED
```

`curriculum_map.json` şu anda kaynak-doğrulanmış bir **draft canonical map** durumundadır. Süreç bileşenleri ve snapshot/page locator doğrulaması bitmeden `FROZEN` yapılmaz.

Zaman modeli:

```text
Her tema dış toplamı = 45 saat
                      = 43 saat tema öğretimi
                      + 2 saat okul temelli planlama

Yıllık toplam        = 180 saat
                      = 172 + 8
```

Okul temelli planlama program boşluğu değildir; ayrı pedagojik katman olarak tutulur.

Ayrıntılı güncel durum için `validation_report.md`, zaman modeli için `planning/course_timeline.json` kullanılır.
