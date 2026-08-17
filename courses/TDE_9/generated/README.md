# Generated Artifacts

Bu dizin Artifact Generation Engine tarafından üretilen ve henüz canonical/frozen kabul edilmeyen ölçme-değerlendirme çıktılarının review alanıdır.

Lifecycle: `REVIEW_REQUIRED → APPROVED → FROZEN`.

- `REVIEW_REQUIRED`: üretim ve deterministik doğrulamalar tamamlanmıştır; gerçek öğretmen incelemesi beklenir.
- `APPROVED`: öğretmen açıkça onaylamıştır.
- `FROZEN`: onaylı revision üretim için dondurulmuştur.

`MAT_*` kimlikleri burada artifact identity olarak kullanılamaz. Canonical kimlik yalnızca production schema içindeki `artifact_id` değeridir.

Generator V1 pilotu: `TDE9_KONUSMA_RUBRIC`. Pilot öğretmen tarafından onaylanmadan sonraki iki artifact'ın üretim kapısı kapalıdır.
