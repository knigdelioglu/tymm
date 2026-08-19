#!/usr/bin/env python3
from pathlib import Path
import re

p = Path('docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md')
text = p.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'missing architecture anchor: {label}')
    text = text.replace(old, new, 1)


replace_once(
    '- `TDE_10` — tüm scoped ihtiyaçları kitapta karşılanan, `zero-gap / reuse-only` model.',
    '- `TDE_10` — `0 confirmed gap + 8 structurally unresolved normative assessment target` bulunan, generation\'ı fail-closed tutan `PARITY_REVIEW_BLOCKED` model. Unresolved hedefler kapandıktan sonra gerçek reuse-only veya artifact-producing sonuca geçebilir.',
    'reference implementation',
)
replace_once(
    '> **Doğrulanmış gap sayısı `0` ise doğru production sonucu yeni materyal üretmek değil, `REUSE_ONLY_NO_NEW_ARTIFACTS` durumudur.**',
    '> **`verified_resource_gap_count = 0` tek başına `REUSE_ONLY_NO_NEW_ARTIFACTS` için yeterli değildir. Normatif bir assessment/support hedefi yapısal olarak unresolved ise production `PARITY_REVIEW_BLOCKED` kalır ve generation `UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS` ile kapanır.**',
    'zero gap principle',
)

text = re.sub(
    r'┌───────────────────────────────┬────────────────────────────────┐.*?└───────────────────────────────┴────────────────────────────────┘',
    '''┌────────────────────────────┬──────────────────────────────┬─────────────────────────────────┐
│ verified gap > 0           │ gap = 0, unresolved = 0      │ gap = 0, unresolved > 0         │
│ ARTIFACT_PRODUCING         │ REUSE_ONLY_NO_NEW_ARTIFACTS  │ PARITY_REVIEW_BLOCKED           │
│ Artifact Generator         │ NO_VERIFIED_RESOURCE_GAP     │ UNRESOLVED_NORMATIVE_           │
│ Validation / Review        │ generation blocked           │ ASSESSMENT_TARGETS              │
│ APPROVE / FREEZE           │                              │ generation blocked              │
└────────────────────────────┴──────────────────────────────┴─────────────────────────────────┘''',
    text,
    count=1,
    flags=re.S,
)

replace_once('Production contract iki geçerli biçimden birine sahiptir:', 'Production contract üç güvenli durumdan birine sahiptir:', 'production states intro')
replace_once(
    '''REUSE_ONLY_NO_NEW_ARTIFACTS
  verified_resource_gap_count = 0
  production_queue = []''',
    '''REUSE_ONLY_NO_NEW_ARTIFACTS
  verified_resource_gap_count = 0
  unresolved_assessment_target_count = 0
  production_queue = []

PARITY_REVIEW_BLOCKED
  verified_resource_gap_count = 0
  unresolved_assessment_target_count > 0
  production_queue = []
  generation_authorization.allowed = false''',
    'production state block',
)
replace_once(
    'Boş queue yalnız ikinci durumda geçerlidir. `verified_resource_gap_count > 0` iken boş queue schema/gate hatasıdır.',
    'Boş queue yalnız doğrulanmış reuse-only veya fail-closed parity-review-blocked durumda geçerlidir. `verified_resource_gap_count > 0` iken boş queue schema/gate hatasıdır; unresolved normatif hedef varken reuse-only sertifikası da hatadır.',
    'empty queue rule',
)

text, n = re.subn(
    r'### 16\.5 Zero-gap / Reuse-only production\n.*?TDE_10 bu modelin referans implementasyonudur\.\n',
    '''### 16.5 Zero-gap / Reuse-only production

Gerçek reuse-only sonucu için iki ayrı sıfır birlikte gerekir:

```text
verified_resource_gap_count = 0
unresolved_assessment_target_count = 0
        ↓
production_mode = REUSE_ONLY_NO_NEW_ARTIFACTS
production_queue = []
        ↓
MATERIAL_GENERATION
→ NO_VERIFIED_RESOURCE_GAP
```

### 16.6 Parity-review-blocked production

Bir normatif assessment/support hedefinin varlığı doğrulanmış fakat yapısı doğrulanamamışsa `0 confirmed gap` reuse-only sertifikası vermez.

```text
verified_resource_gap_count = 0
unresolved_assessment_target_count > 0
        ↓
production_mode = PARITY_REVIEW_BLOCKED
production_queue = []
generation_authorization.allowed = false
        ↓
MATERIAL_GENERATION
→ UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS
```

Kurallar:

- `UNRESOLVED ≠ COVERED`,
- resmî link varlığı tek başına assessment requirement'ı kapatmaz,
- unresolved hedef çözülmeden artifact uydurulmaz,
- hedefler yeterli çıkarsa reuse-only, yetersiz çıkarsa gap analysis + cross-theme consolidation üzerinden artifact-producing moda geçilir.

TDE_10 bu fail-closed ara durumun referans implementasyonudur.
''',
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f'section 16 migration count={n}')

replace_once(
    '''### Zero-gap generation

```text
production_mode = REUSE_ONLY_NO_NEW_ARTIFACTS
verified_resource_gap_count = 0
+ MATERIAL_GENERATION intent
→ NO_VERIFIED_RESOURCE_GAP
→ generation blocked
```''',
    '''### Zero-gap generation

```text
production_mode = REUSE_ONLY_NO_NEW_ARTIFACTS
verified_resource_gap_count = 0
unresolved_assessment_target_count = 0
+ MATERIAL_GENERATION intent
→ NO_VERIFIED_RESOURCE_GAP
→ generation blocked
```

### Unresolved normative target generation

```text
production_mode = PARITY_REVIEW_BLOCKED
unresolved_assessment_target_count > 0
+ MATERIAL_GENERATION intent
→ UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS
→ generation blocked
```''',
    'resolver generation gates',
)

replace_once('Schema iki durumu destekler:', 'Schema üç durumu destekler:', 'schema state count')
replace_once(
    'Gap count sıfır değilse empty queue kabul edilmez.',
    '''Gap count sıfır değilse empty queue kabul edilmez.

### Parity-review-blocked course

```text
production_mode = PARITY_REVIEW_BLOCKED
verified_resource_gap_count = 0
unresolved_assessment_target_count > 0
production_queue = []
generation_authorization.allowed = false
generation_authorization.reason = UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS
```

Bu durum `NO_REQUIRED_ARTIFACTS` sertifikası değildir; unresolved normatif hedefler çözülene kadar güvenli ara durumdur.''',
    'schema parity blocked',
)

replace_once(
    '''gap > 0 → ARTIFACT_PRODUCING
gap = 0 → REUSE_ONLY_NO_NEW_ARTIFACTS''',
    '''gap > 0 → ARTIFACT_PRODUCING
gap = 0 + unresolved = 0 → REUSE_ONLY_NO_NEW_ARTIFACTS
gap = 0 + unresolved > 0 → PARITY_REVIEW_BLOCKED''',
    'playbook branch',
)
replace_once('TDE_10: 0 gap → 0 artifact', 'TDE_10: 0 confirmed gap + 8 unresolved target → PARITY_REVIEW_BLOCKED / 0 authorized artifact', 'P0 invariant')
replace_once('Reuse-only course bu fazı atlar.', 'Reuse-only ve parity-review-blocked course bu fazı atlar; generator yalnız verified gap sonrası artifact-producing moda geçen course için açılır.', 'generator skip')
replace_once('[ ] gap=0 ise empty queue yalnız reuse-only modunda mı kabul ediliyor?', '[ ] Empty queue yalnız verified reuse-only veya fail-closed parity-review-blocked modunda mı kabul ediliyor?', 'checklist queue')
replace_once('[ ] Zero-gap generation isteği NO_VERIFIED_RESOURCE_GAP ile kapanıyor mu?', '[ ] Reuse-only generation `NO_VERIFIED_RESOURCE_GAP`, parity-blocked generation `UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS` ile kapanıyor mu?', 'checklist gate')

text, n = re.subn(
    r'## 36\. TDE_10\x27dan çıkan yeni ana dersler\n.*?\n---\n\n## 37\.',
    '''## 36. TDE_10'dan çıkan yeni ana dersler

1. Başka sınıfın alt süreç kodlarını kopyalamamak; resmî kaynak yayımlamıyorsa sentezlememek.
2. Yerel resmî textbook PDF'yi primary analysis snapshot olarak desteklemek.
3. QR/EBA scoring-guide link varlığını hedef yapısının doğrulanmasından ayırmak.
4. **`UNRESOLVED ≠ COVERED`.** Auth-gated normatif hedef `PARTIALLY_COVERED / REVIEW_REQUIRED` kalır.
5. **`gap=0 ≠ NO_REQUIRED_ARTIFACTS`.** Reuse-only için unresolved normatif hedef sayısı da `0` olmalıdır.
6. **`PARITY_REVIEW_BLOCKED` birinci sınıf güvenli durumdur.** Empty queue geçerli, generation kapalıdır.
7. Outcome-level need/resource/alignment/gap izini domain-level özetlerle kaybetmemek.
8. Cross-theme audit'i yalnız declared gap sayımına indirgememek; ortak assessment construct'larını da karşılaştırmak.
9. TDE_9 7→3 ve TDE_10 parity-blocked invariantlarını aynı shared engine'de regression ile korumak.
10. Canonical contract/registry/manifest değişiminden sonra index/runtime'ı final fingerprint üzerinden rebuild etmek.

---

## 37.''',
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f'section 36 migration count={n}')

text, n = re.subn(
    r'## 37\. Mimari özet\n.*?\n---\n\n## 38\.',
    '''## 37. Mimari özet

```text
1. SOURCE TRUTH
   Official Program + Official Textbook + Source Manifest

2. CANONICAL KNOWLEDGE
   Curriculum/Textbook Maps + Needs + Alignment + Gap + Resource Plan

3. FIND / RESOLVE
   SQLite FTS5 + Vector + Resolver

4. PRODUCTION CONTRACT
   Consolidation + Production Mode + Registry + Contract + P0

5A. GAP > 0
   ARTIFACT_PRODUCING → Generator → Validation → Teacher Review

5B. GAP = 0 / UNRESOLVED = 0
   REUSE_ONLY_NO_NEW_ARTIFACTS → NO_VERIFIED_RESOURCE_GAP

5C. GAP = 0 / UNRESOLVED > 0
   PARITY_REVIEW_BLOCKED → UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS

6. APPLICATION
   Deterministic Runtime SQLite Projection
```

> **Yapay zekâ kararın kaynağı değildir. Yapay zekâ, doğrulanmış canonical bilgi ve açık production contract üzerinde çalışan kontrollü üretim motorudur.**

---

## 38.''',
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f'section 37 migration count={n}')

text, n = re.subn(
    r'## 39\. Güncel TDE_10 implementasyon durumu — 2026-08-18\n.*?\n---\n\n## 40\.',
    '''## 39. Güncel TDE_10 implementasyon durumu — 2026-08-19

```text
Official curriculum snapshots        PASS (4/4)
Canonical learning outcomes          PASS (64/64)
Curriculum canonical map             VERIFIED / FROZEN
Official local textbook PDF          VERIFIED / FROZEN
Textbook sections                    24
Textbook activities                  75
Assessment/form records              35
Program-textbook alignment           56 COVERED / 8 PARTIALLY_COVERED / 0 NOT_COVERED
Confirmed remaining resource gaps    0
Unresolved normative targets         8 authenticated EBA DPA targets
Production mode                      PARITY_REVIEW_BLOCKED
Canonical new artifacts authorized   0
Teaching blocks                      16
Knowledge index                      INDEX_FRESH / 482 records
Duplicate canonical keys             0
Resolver ambiguity/stale/conflict    PASS
Generation gate                      PASS / UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS
Runtime projection                   PASS
Technical P0                         PASS
TDE_9 regression                     PASS / 7 gap → 3 artifact preserved
Parity certification                 WITHHELD pending 8 EBA target structures
```

Runtime projection includes 64 resource decisions, 75 activities, 35 forms and 0 authorized assessment artifacts. `0 assessment_artifact` is a correct fail-closed result, but it is not called verified reuse-only until all eight unresolved targets are structurally resolved.

---

## 40.''',
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f'section 39 migration count={n}')

text = text.replace('→ TDE_10 generic zero-gap P0', '→ TDE_10 parity-aware generic P0')
text = text.replace('→ index/runtime rebuild\n→ final canonical metadata sonrası ikinci rebuild/freshness doğrulaması', '→ reuse-only / PARITY_REVIEW_BLOCKED contract validation\n→ index/runtime rebuild\n→ final canonical metadata sonrası ikinci rebuild/freshness doğrulaması', 1)

replace_once(
    '''### Zero-gap / reuse-only course

Aşağıdaki zincir gösterilebiliyorsa production input hazırdır:

> “Scoped program gereksinimlerinin tamamı için textbook action/evidence yolu doğrulandı; remaining gap sayısı `0`; production contract `REUSE_ONLY_NO_NEW_ARTIFACTS`; empty queue doğrulanmış; material-generation isteği `NO_VERIFIED_RESOURCE_GAP` ile fail-closed; index/runtime final canonical fingerprintten rebuild edilebilir.”

Bu iki modelden uygun olanındaki bir halka eksikse P0 açılmamalıdır.''',
    '''### Zero-gap / reuse-only course

Aşağıdaki zincir gösterilebiliyorsa production input hazırdır:

> “Scoped program gereksinimlerinin tamamında textbook action/evidence ve normatif assessment yapıları doğrulandı; remaining gap `0`; unresolved target `0`; contract `REUSE_ONLY_NO_NEW_ARTIFACTS`; generation `NO_VERIFIED_RESOURCE_GAP` ile kapalı.”

### Parity-review-blocked course

Aşağıdaki zincir gösterilebiliyorsa güvenli ara durum doğrudur:

> “Confirmed gap `0` fakat en az bir normatif assessment/support hedefi yapısal olarak unresolved; bu hedef COVERED sayılmıyor; contract `PARITY_REVIEW_BLOCKED`; queue boş; generation `UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS` ile kapalı; hedef çözülmeden reuse-only sertifikası veya artifact verilmiyor.”

Bu üç modelden uygun olanındaki bir halka eksikse P0 açılmamalıdır.''',
    'appendix readiness',
)

p.write_text(text, encoding='utf-8')
print('TDE10 architecture report migration: PASS')
