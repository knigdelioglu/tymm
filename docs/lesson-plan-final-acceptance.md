# Ders Planları — Final Mühendislik Kabulü

Tarih: 2026-08-25

## Karar

`TDE_9` ve `TDE_10` ders planı üretim seti, lesson-plan artefaktı ve mühendislik doğrulaması açısından **ACCEPTED** durumundadır.

Bu karar içeriklerin değişmez olduğu anlamına gelmez. Bundan sonraki değişiklikler mevcut fail-closed doğrulama zincirinden geçmek zorundadır.

## Kabul edilen kapsam

| Kapsam | TDE9 | TDE10 | Toplam |
|---|---:|---:|---:|
| Tema | 4 | 4 | 8 |
| Çekirdek paket | 88 | 88 | 176 |
| Çekirdek ders saati | 172 | 172 | 344 |
| JSON plan | 88 | 88 | 176 |
| Canonical Markdown eş | 88 | 88 | 176 |

Saat sözleşmesi değişmemiştir: her tema 43 çekirdek + 2 okul-temelli = 45 saat; yıllık 172 çekirdek + 8 okul-temelli = 180 saattir. Okul-temelli saat, çekirdek planın tamamlanma şartı değildir.

## Final mutation kabulü

Final mutation matrisi şu dosyalarda first-class tutulur:

- `skill/tymm-material-planner/tests/final_mutation_manifest.json`
- `skill/tymm-material-planner/scripts/run_final_mutation_suite.py`

Final matrix sonucu:

- Risk ailesi: **8**
- Bilinçli bozuk mutation: **27**
- Öldürülen mutation: **27**
- Surviving mutation: **0**
- Mutation score: **1.0 / %100**

Temsil edilen risk aileleri:

1. P3 — assessment scope
2. P4 — large-class execution
3. P5 — closure time/load
4. P6 — differentiation/accessibility/media fallback
5. P7 — canonical reference grounding
6. P8 — exact package topology
7. P9 — JSON→Markdown parity
8. P10 — validation report / SHA / fingerprint binding

Runner yalnız test adını çalıştırmakla yetinmez; manifestte beklenen detector kodunun referans verilen negatif test tarafından gerçekten assert edildiğini de denetler. Herhangi bir testin kaybolması, detector assert'inin silinmesi, risk ailesinin manifestten düşmesi veya mutation'ın hayatta kalması final suite'i FAIL yapar.

## Final strict kabul koşusu

`TYMM Lesson Plan Full Validation` run **32879219460**:

- validation-binding regression: `SUCCESS`
- deterministic JSON↔Markdown parity: `SUCCESS`
- package topology regression/contract: `SUCCESS`
- grounded reference regression/contract: `SUCCESS`
- classroom adaptation regression/contract: `SUCCESS`
- closure time-budget regression/contract: `SUCCESS`
- large-class route regression: `SUCCESS`
- final mutation coverage: `SUCCESS`
- **176/176 lesson-plan package validation: `SUCCESS`**
- failure records: **0**
- warning records: **0**
- finalizer: `SUCCESS`

Final validation binding:

- validated commit: `3702bab26f47c7e1dc87091c669b00278e2fff37`
- content fingerprint: `sha256:c0b63624ce313c518ec0b278390b4c3c6df584b09bc512cc7e4dcf35208fffde`
- fingerprinted files: `440`
- TDE9/TDE10 production planlarında binding first-class `engineering_validation.validation_binding` altında tutulur.

Finalizer bu PASS raporunu, commit SHA'yı ve yeniden hesaplanan içerik fingerprint'ini exact eşleştirmeden üretim planlarına PASS yazamaz.

## CI yarış koşulu kabulü

P11 ilk finalizer denemesinde P10 güvenliği doğru biçimde devreye girdi ve validation sonrasında `main` ilerlediği için publish işlemini fail-closed durdurdu. İlerlemeyi yaratan değişiklik, P0 workflow'unun yalnız index/runtime build timestamp'lerini yeniden yayımlamasıydı.

`.github/workflows/tymm-p0-production-gate.yml` düzeltildi:

- yalnız `index_created_at`, `index_updated_at`, `Build Timestamp` ve `build_timestamp` değişmişse yeni derived commit üretilmez;
- gerçek derived içerik değişikliği varsa publish davranışı korunur.

Gerçek P0 run **32879032531**, rebuild sonrası yalnız volatile timestamp farkını tespit etmiş ve `Only volatile derived timestamps changed; skipping publish.` ile commit üretmeden `SUCCESS` tamamlanmıştır.

Ayrıca `.github/workflows/tymm-p0-production-gate.yml` artık lesson-plan full validation path kapsamındadır. P0 publish politikasındaki gelecekteki değişiklikler de `Full validation gate` çalıştırır.

## Dağıtım yönetişimi notu

Kod ve CI sözleşmesi PR üzerinde `Full validation gate` çalıştıracak şekilde hazırdır. Ancak GitHub repo ayarında `main` halen `protected=false` ve required status checks enforcement kapalıdır.

Bu nedenle **artefakt seti teknik olarak kabul edilmiştir**, fakat organizasyonel merge yönetişiminin tam olması için GitHub repo ayarında ayrıca:

1. `main` için branch protection/ruleset etkinleştirilmeli,
2. pull request zorunlu tutulmalı,
3. `Full validation gate` required status check yapılmalıdır.

Bu repo ayarı mevcut bağlı GitHub aracının yazma yetenekleri arasında olmadığı için kod içinden taklit edilmemiştir. Bu durum lesson-plan içeriğinde açık sarı kalite riski değildir; kalan bir repository-governance kontrolüdür.

## Sonuç

P0–P9 içerik ve plan sözleşmesi riskleri kapalıdır. P10'un SHA/fingerprint-bound finalizer mühendisliği tamamlanmıştır. P11 mutation kapsamı **27/27 killed** ile kapalıdır. Lesson-plan seti teknik dağıtım/pilot kullanımı açısından **ACCEPTED** durumundadır; tek dış aksiyon GitHub branch-protection enforcement ayarıdır.
