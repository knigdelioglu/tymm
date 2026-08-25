#!/usr/bin/env python3
"""One-shot updater for closing P9 in the remediation audit document."""
from pathlib import Path

PATH = Path("docs/lesson-plan-yellow-remediation-plan.md")
ANCHOR = "## Aktif sarı riskler\n\nP0–P8 kapatıldıktan sonra aktif sarılar:\n"
ROW = "| `YELLOW-MD-PARITY` | P9 | JSON ve Markdown için yalnız eş dosya varlığı doğrulanıyor | 176 paket | Deterministik JSON→Markdown parity |\n"
PHASE = "P9  JSON-Markdown parity\n"

SECTION = """## P9 — Deterministik JSON→Markdown parity — TAMAMLANDI

### Kapatılan risk

**YELLOW-MD-PARITY — JSON ve Markdown için yalnız eş dosya varlığı doğrulanıyor**

Durum: `CLOSED`

### Canonical render modeli

`skill/tymm-material-planner/scripts/render_lesson_plan_markdown.py` ile lesson-plan JSON artık Markdown'ın tek authoritative girdisidir. Renderer öğretmen-okunur başlık, kapsam, ders akışı, canonical referanslar, kalabalık sınıf rotası, sınıf uyarlamaları, medya fallback'i, ölçme kanıtı, materyaller ve devam bilgisini deterministik sırada üretir.

Renderer fail-closed çalışır: plan verisine renderer tarafından temsil edilmeyen yeni bir alan eklenirse `UNRENDERED_FIELDS` ile durur. Böylece yeni JSON alanı Markdown'da sessizce kaybolamaz. Her Markdown ayrıca canonical, key-sorted JSON içeriğinin `SHA-256` parmak izini taşır.

### Exact parity sözleşmesi

`validate_lesson_plan_markdown.py` her `*.json` için canonical Markdown'ı yeniden üretir ve committed `*.md` ile **byte-exact** karşılaştırır. Aşağıdaki durumlar FAIL'dir:

- JSON değişmiş fakat Markdown yeniden üretilmemişse
- Markdown elle değiştirilmişse
- JSON'a renderer'ın bilmediği alan eklenmişse
- Markdown eksikse
- karşılığında JSON bulunmayan orphan Markdown varsa

`validate_all_lesson_plans.py` içindeki eski yalnız-varlık kontrolü de kaldırıldı; aynı parity validator artık full-plan doğrulamasının doğrudan parçasıdır. JSON ve Markdown paket sayıları ayrıca exact eşlenir.

### Migration ve regression kapsamı

Her iki sınıftaki **176 Markdown** bir kez canonical renderer ile yeniden üretildi ve repoya commitlendi. Sonrasında auto-render/publish adımları workflow'dan kaldırıldı; CI committed Markdown'ı kendi kendine düzeltmez.

`test_lesson_plan_markdown_parity.py` şu negatif mutasyonları kapsar:

- JSON özetini değiştirip Markdown'ı eski bırakma
- Markdown'a manuel içerik ekleme
- bilinmeyen JSON alanı ekleme
- orphan Markdown oluşturma

Geçerli canonical render için ayrıca pozitif PASS testi vardır.

### P9 kabul sonucu

Strict `TYMM Lesson Plan Full Validation` run `32869470589` sonucunda:

- `Run JSON-Markdown parity regression tests`: `SUCCESS`
- `Validate deterministic JSON-Markdown parity`: `SUCCESS`
- `Run package-topology regression tests`: `SUCCESS`
- `Validate package-topology contracts`: `SUCCESS`
- P7/P6/P5/P4 contract ve regression kapıları: `SUCCESS`
- `Validate all 176 lesson-plan packages`: `SUCCESS`
- finalization: `SUCCESS`

Böylece Markdown artık JSON'dan bağımsız elle sürdürülen ikinci bir gerçeklik katmanı değildir; JSON değiştiği anda committed öğretmen görünümü de deterministik olarak aynı semantiğe gelmek zorundadır.

"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    if "## P9 — Deterministik JSON→Markdown parity — TAMAMLANDI" in text:
        print("P9 audit record already closed.")
        return 0
    if ANCHOR not in text or ROW not in text or PHASE not in text:
        raise SystemExit("P9 audit anchors do not match current remediation document")
    text = text.replace(ANCHOR, SECTION + "## Aktif sarı riskler\n\nP0–P9 kapatıldıktan sonra aktif sarılar:\n", 1)
    text = text.replace(ROW, "", 1)
    text = text.replace(PHASE, "P9  JSON-Markdown parity                              ✅ TAMAMLANDI\n", 1)
    PATH.write_text(text, encoding="utf-8")
    print("P9 audit record closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
