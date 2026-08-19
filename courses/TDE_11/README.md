# TDE_11 — 11. Sınıf Türk Dili ve Edebiyatı

Bu klasör, 11. sınıf Türk Dili ve Edebiyatı için curriculum-only canonical katmandır.

## Lifecycle

`CURRICULUM_ONLY_AWAITING_TEXTBOOK`

Resmî öğretim programı doğrulanmış ve canonical curriculum katmanı kurulmuştur. Resmî 11. sınıf ders kitabı henüz bu çalışma için mevcut olmadığı için textbook, coverage, alignment, gap ve production aşamaları başlatılmamıştır.

## Zaman modeli

Her tema **45 saatlik planlama bloğudur**:

- **43 saat** resmî TYMM tema öğretimi
- **2 saat** okul temelli planlama
- **45 saat** tema toplamı

Yıllık toplam: **172 saat tema öğretimi + 8 saat okul temelli planlama = 180 saat**.

Okul temelli planlama ayrı pedagojik katmandır; curriculum gap olarak değerlendirilmez. `curriculum_map.json` içindeki resmî 43 saatlik verbatim kaynak kaydı korunur, 2 saatlik okul temelli planlama `source_manifest.json` zaman modelinde ayrıca tanımlanır.

## Canonical dosyalar

- `source_manifest.json` — resmî program kaynak kimliği, yerel PDF eşleştirmesi, zaman modeli, bütünlük ve lifecycle bilgisi
- `curriculum_map.json` — 4 tema, 64 parent outcome, program bileşenleri, ölçme-değerlendirme ve farklılaştırma hükümleri
- `curriculum_normative_text.json` — yerel resmî program PDF’lerinin sayfa bazlı kaynak-bağlı metin kanıtı
- `curriculum_validation_report.json` — curriculum-only doğrulama sonucu
- `validation_report.md` — insan tarafından okunabilir kısa doğrulama raporu
- `source_docs/` — tema adıyla eşleştirilmiş yerel resmî program PDF snapshotları

## Kaynak politikası

Canonical içerik yalnız 11. sınıf resmî TYMM öğretim programından çıkarılır. TDE_9 ve TDE_10 içerik kaynağı değildir; yalnız mimari/şema davranışı referansı olabilir.

Yerel PDF kimliği, PDF içindeki resmî TYMM `unite/<id>` bağlantısıyla doğrulanmıştır; dosya boyutu veya yükleme sırası üzerinden tahmin yapılmamıştır.

Ders kitabı bulunmadığı için kitap eksikliği `NOT_COVERED`, verified gap veya artifact ihtiyacı olarak yorumlanmaz.

## Doğrulama

Curriculum-only paket `skill/tymm-material-planner/scripts/curriculum_only_gate.py` ile fail-closed doğrulanır. Ders kitabı gelene kadar full textbook P0 zorlanmaz.
