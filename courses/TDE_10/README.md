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
Source registration                         PASS
Curriculum map draft                        CREATED
Official TYMM theme identity                PASS
64 scoped learning outcomes                 MAPPED
Stable entity keys                          UNIQUE
Theme time model                            45 = 43 + 2
Annual time model                           180 = 172 + 8
Process-component audit                     PARTIAL / FAIL-CLOSED
Theme 1 instructional needs                 CREATED
Theme 2 instructional needs                 CREATED
Theme 3 instructional needs                 CREATED
Theme 4 instructional needs                 CREATED
Official OGM textbook theme assets          RESOLVED AS SUPPORTING
Textbook source-structure map               CREATED / NOT FROZEN
Textbook page-level sections/activities     PENDING
Textbook forms index                        PENDING
Theme alignment / gap analysis              BLOCKED BY TEXTBOOK CONTENT MAP
Production / index / runtime / P0           NOT STARTED
```

## Zaman modeli

```text
Her tema dış toplamı = 45 saat
                      = 43 saat tema öğretimi
                      + 2 saat okul temelli planlama

Yıllık toplam        = 180 saat
                      = 172 + 8
```

Okul temelli planlama program boşluğu değildir; ayrı pedagojik katman olarak tutulur.

## Oluşturulan ana dosyalar

```text
source_manifest.json
curriculum_map.json
textbook_map.json
validation_report.md
planning/course_timeline.json
source_docs/curriculum_process_component_audit.json
themes/tema_01/needs.json
themes/tema_02/needs.json
themes/tema_03/needs.json
themes/tema_04/needs.json
```

`curriculum_map.json` ve `textbook_map.json` henüz `FROZEN` değildir. Textbook content map tamamlanmadan `alignment → gap → resource_plan → production` zinciri açılmaz.

Ayrıntılı gate durumu için `validation_report.md` kullanılır.
