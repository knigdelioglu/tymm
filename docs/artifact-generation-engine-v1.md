# Artifact Generation Engine V1

Bu katman, P0 Production Gate sonrasında doğrulanmış üretim girdilerinden kontrollü ölçme-değerlendirme artifact'ı üretir.

## Akış

`P0_GATE → SELECT_ARTIFACT → BUILD_GENERATION_CONTEXT → VALIDATE_CONTEXT → GENERATE_DRAFT → STRUCTURAL_VALIDATION → PEDAGOGICAL_CONTRACT_VALIDATION → TEACHER_REVIEW_REQUIRED → APPROVE → FREEZE`

## Temel invariants

- Canonical üretim kimliği yalnızca `artifact_id`'dir. `MAT_*` kimlikleri provenance/alias'tır ve generator giriş kimliği olarak kabul edilmez.
- Generation context deterministiktir ve `context_hash` taşır. Aynı artifact + aynı context yeniden çalıştırıldığında yeni revision yaratılmaz.
- Context değişirse yeni revision oluşturulur; önceki revision arşivlenir.
- Çıktı, covered outcome/gap/source provenance ve kullanılan contract sürümlerini birlikte taşır.
- `GENERATE` hiçbir zaman `APPROVE` anlamına gelmez. İlk durum `REVIEW_REQUIRED` olur.
- `FROZEN` durumuna yalnız açık öğretmen onayından (`APPROVED`) sonra geçilebilir.
- Generator V1 sırasında `TDE9_YAZMA_RUBRIC` ve sonraki artifact'lar, `TDE9_KONUSMA_RUBRIC` pilotu öğretmen tarafından onaylanmadan üretilemez.

## Pilot

İlk acceptance artifact'ı `TDE9_KONUSMA_RUBRIC`'tir. Pilot için generator engineering gate şu kontrolleri zorunlu tutar:

- P0 index/production gate hazır ve `INDEX_FRESH`;
- 3 legacy konuşma gap alias'ı tek canonical artifact'a çözülüyor;
- 5 canonical konuşma ölçütü × 4 performans düzeyi matrisi eksiksiz;
- betimleyiciler `pedagogical_recommendation` provenance'ı taşıyor ve contract'ın yasaklı dil kalıplarını kullanmıyor;
- puanlama modeli `RAW_MEAN_1_TO_4`, eşit ağırlık ve yalnız yardımcı 100'lük gösterim mantığını koruyor;
- aynı context ile iki üretim idempotent;
- öğretmen incelemesi yapılmadan sonraki artifact seçimi kapalı.

Engineering gate'in `ENGINEERING_PASS_REVIEW_REQUIRED` sonucu başarılı bir teknik pilot anlamına gelir; nihai `GENERATOR_V1_GATE: PASS` ancak gerçek öğretmen onayından sonra mümkündür.
