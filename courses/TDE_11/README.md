# TDE_11 — 11. Sınıf Türk Dili ve Edebiyatı

Bu klasör 11. sınıf Türk Dili ve Edebiyatı için **program + resmî ders kitabı hizalanmış canonical bilgi katmanıdır**.

## Lifecycle

`TEXTBOOK_ALIGNED_PARITY_REVIEW_BLOCKED`

Resmî TYMM öğretim programı ile 2026 MEB 11. sınıf ders kitabı eşlenmiştir. Canonical curriculum **4 tema / 64 parent outcome** olarak korunur. Ders kitabı **24 bölüm, 84 aşama/ölçme etkinliği ve 43 form/değerlendirme kaydı** düzeyinde haritalanmıştır.

Yıllık outcome kapsamı:

- **56 `COVERED`**
- **8 `PARTIALLY_COVERED`**
- **0 `NOT_COVERED`**
- **0 doğrulanmış materyal açığı**
- **8 çözümlenmemiş normatif değerlendirme hedefi**

Sekiz kısmi kayıt, her temadaki `TDE3.4` ve `TDE4.4` için kitapta bulunan resmî QR bağlantılı **Dereceli Puanlama Anahtarı** hedefleridir. Yerel resmî PDF hedeflerin ölçüt×düzey içeriğini göstermediğinden bunlar fail-closed biçimde çözümlenmemiş tutulur. Bu durum doğrulanmış materyal açığı değildir ve yeni rubrik/artifact üretimini yetkilendirmez.

## Üretim durumu

`PARITY_REVIEW_BLOCKED`

- `verified_resource_gap_count = 0`
- `unresolved_assessment_target_count = 8`
- `expected_new_artifact_count = 0`
- `generation_authorization.allowed = false`
- blok nedeni: `UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS`

## Zaman modeli

Her tema **45 saatlik planlama bloğudur**:

- **43 saat** resmî TYMM tema öğretimi
- **2 saat** okul temelli planlama
- **45 saat** tema toplamı

Yıllık toplam: **172 saat tema öğretimi + 8 saat okul temelli planlama = 180 saat**. Okul temelli planlama curriculum gap değildir.

## Ana canonical ve türetilmiş katmanlar

- `source_manifest.json` — program + kitap kaynak kimliği, fingerprint ve lifecycle
- `curriculum_map.json` — 4 tema / 64 outcome canonical program katmanı
- `textbook_map.json` — kitap bölüm/etkinlik/sayfa eşlemesi
- `textbook_forms_index.json` — gözlenen form ve değerlendirme yapıları
- `themes/tema_*/needs.json` — curriculum-first ihtiyaçlar
- `themes/tema_*/alignment.json` — outcome → kitap kanıtı hizalaması
- `themes/tema_*/gap_analysis.json` — kapsam ve kalan boşluk analizi
- `themes/tema_*/resource_plan.json` — coverage sonrası kaynak kararı
- `production/` — cross-theme audit, production contract/manifest ve teaching blocks
- `planning/course_timeline.json` — sıralı yıllık tema/block zaman katmanı
- `index/` — canonical bilgi indeksi ve P0 raporu
- `runtime/course_runtime.sqlite` — canonical JSON/MD'den türetilmiş runtime veritabanı

## Doğrulama

Kalıcı doğrulama `.github/workflows/tymm-tde11-p0.yml` üzerinden `generic_p0_course_gate.py` ile fail-closed çalışır. Gate canonical sözleşme, production mode, indeks tazeliği, resolver, tema belirsizliği, stale/conflict korumaları ve runtime SQLite katmanını doğrular. TDE_9 ve TDE_10 regresyon sözleşmeleri de aynı workflow içinde korunur.

Parite sertifikası, sekiz resmî QR bağlantılı değerlendirme hedefinin doğrudan yapısal doğrulaması tamamlanana kadar verilmez.
