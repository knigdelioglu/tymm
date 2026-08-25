# Ders Planları — Sarı Risk Düzeltme Planı

Bu belge, `TDE_9` ve `TDE_10` için lesson-plan dağıtım incelemesinde açılan sarı risklerin güncel ve izlenebilir kapanış kaydıdır. Ayrıntılı final kabul sonucu ayrıca `docs/lesson-plan-final-acceptance.md` içinde tutulur.

## Değişmez saat sözleşmesi

```text
43 saat çekirdek öğretim
+ 2 saat okul temelli planlama
= 45 saat / tema

172 saat çekirdek
+ 8 saat okul temelli planlama
= 180 saat / yıl
```

Okul-temelli saatler ihtiyaç-temelli ve opsiyoneldir. 43 saatlik çekirdek tema planı bunlara bağlı olmadan tamamlanabilir. Geçmişte Tema 4 için görülen 46 saat, haftalık/takvim yerleşiminden doğan bir artık olup pedagojik blok süresi değildir; `46→43` normalizasyonu kullanılmaz.

---

## P0 — Saat kaynaklı yanlış sarıları temizle — TAMAMLANDI

**Risk:** `YELLOW-HOURS-46`

**Durum:** `CLOSED`

Tema başına 43 çekirdek + 2 okul-temelli, yıllık 172 + 8 sözleşmesi canonical hâle getirildi. Takvim artıkları instructional allocation'a giremez. Saat sözleşmesi regression testleriyle korunur.

## P1 — Okul-temelli yerleşim katmanı — TAMAMLANDI

**Risk:** `YELLOW-SBP-PLACEMENT`

**Durum:** `CLOSED`

Her iki sınıf için `production/school_based_planning_placements.json` oluşturuldu. Her seçenek gerçek theme/block/package anchor'ı, aktivasyon koşulu, ihtiyaç ve etki değerlendirmesi taşır. Yerleşim öneridir; çekirdek kuyruğa otomatik eklenmez.

## P2 — TDE10 okul-temelli kariyer uyumu — TAMAMLANDI

**Risk:** `YELLOW-TDE10-SBP-PURPOSE`

**Durum:** `CLOSED`

TDE10'daki 8 okul-temelli saatin tamamı `CAREER_GUIDANCE` bağlamında; TDE beceri köprüsü, meslek keşfi, kariyer kanıtı, öz-farkındalık ve karar desteği katmanlarıyla yeniden tasarlandı.

## P3 — Assessment scope semantiği — TAMAMLANDI

**Risk:** `YELLOW-ASSESSMENT-SCOPE`

**Durum:** `CLOSED`

Öğretim kapsamı ile ölçme kapsamı ayrıldı:

- `outcome_codes` / `instruction_scope=BLOCK`
- `assessment_scope=BLOCK|THEME`
- `assessed_outcome_codes`

Tema sonu ölçme ve yansıtma, yalnız son blok çıktılarıyla yanlış biçimde tema-geneli gösterilemez. 8 tema-kapanış P05 paketi migrate edildi. TDE9 tema union'ı 12, TDE10 tema union'ı 16 outcome'dur.

## P4 — Kalabalık sınıf yürütme rotaları — TAMAMLANDI

**Risk:** `YELLOW-LARGE-CLASS`

**Durum:** `CLOSED`

Gerçek canlı performans içeren **29 paket** (`TDE9=16`, `TDE10=13`) `large_class_route` aldı. Paralel gruplar, teacher rotation, peer-observer kanıtı ve bireysel performans eşdeğerliği zorunludur. Çekirdek yürütme okul-temelli saate bağımlı olamaz.

## P5 — Tema/yıl kapanış yükü — TAMAMLANDI

**Risk:** `YELLOW-CLOSURE-LOAD`

**Durum:** `CLOSED`

8 tema-kapanış P05 için `closure_time_budgets.json` katmanı oluşturuldu. Karma kapanışta nominal çekirdek bütçe:

```text
25 dk tema ölçme
10 dk çekirdek yansıtma
 3 dk kapanış
 2 dk tampon
= 40 dk
```

Ayrıntılı yanlış düzeltme, genişletilmiş portfolyo/yansıtma ve sonraki tema hazırlığı zorunlu çekirdek iş değildir; yalnız seçilirse okul-temelli genişletme olabilir.

## P6 — Farklılaştırma / erişilebilirlik / medya fallback — TAMAMLANDI

**Risk:** `YELLOW-ADAPTATION`

**Durum:** `CLOSED`

`classroom_adaptations` first-class schema alanına dönüştürüldü; boilerplate olarak 176 pakete değil yalnız gerçek kritik paketlere uygulanır.

Kesin kapsam:

- TDE9: 36 kritik paket
- TDE10: 32 kritik paket
- toplam: **68 benzersiz paket**
- 41 medya-bağımlı
- 29 canlı performans
- 2 overlap

Dinleme hedefi transkripte varsayılan olarak indirgenemez; sözlü performans yalnız yazılı ürünle ikame edilemez; kayıtlı sözlü rota rıza gerektirir; outcome ve assessment construct korunur.

## P7 — Rubrik / resource / artifact grounding — TAMAMLANDI

**Risk:** `YELLOW-REF-GROUNDING`

**Durum:** `CLOSED`

`grounded_references` ile `form_refs`, `assessment_artifact_refs` ve `resource_refs` canonical registry/indexlere bağlandı. `USED`, `DEFERRED`, `REFERENCE_ONLY` kullanım semantiği ayrıldı.

Kesin kapsam:

- TDE9: 49 paket / 146 structured ref
- TDE10: 33 paket / 66 structured ref
- toplam: **82 paket / 212 canonical structured ref**

Yanlış binding key, uydurma canonical ID ve doğrulanmamış dış kaynak eşdeğerliği fail-closed reddedilir.

## P8 — Exact paket topolojisi — TAMAMLANDI

**Risk:** `YELLOW-PACKAGE-TOPOLOGY`

**Durum:** `CLOSED`

Her sınıfta machine-readable exact topology manifesti vardır. `teaching_blocks`, `block_hour_bindings`, production package partition ve gerçek generated JSON seti çapraz doğrulanır.

Her sınıf için:

- 4 tema
- 16 blok
- 88 paket
- 172 çekirdek saat
- `gaps=0`
- `overlaps=0`

Course/theme/block saat aralıkları `ONE_BASED_INCLUSIVE` olarak exact tutulur. 15 saatlik blokların son 1 saatlik paketi uydurulmadan korunur.

## P9 — Deterministik JSON→Markdown parity — TAMAMLANDI

**Risk:** `YELLOW-MD-PARITY`

**Durum:** `CLOSED`

JSON authoritative kaynaktır. `render_lesson_plan_markdown.py` canonical Markdown üretir ve `validate_lesson_plan_markdown.py` committed Markdown'ı yeniden üretilen çıktı ile **byte-exact** karşılaştırır.

176 JSON ↔ 176 Markdown çifti exact parity taşır. Stale Markdown, manuel Markdown değişikliği, orphan Markdown ve renderer'ın bilmediği JSON alanı FAIL'dir.

## P10 — CI / finalizer sertleştirme — MÜHENDİSLİK TAMAMLANDI, REPO AYARI AÇIK

**Risk:** `YELLOW-CI-FINALIZER`

**Kod/CI durumu:** `ENGINEERING_CLOSED`

**Repository-governance durumu:** `EXTERNAL_ACTION_REQUIRED`

Yapılanlar:

- Full validation `pull_request -> main` üzerinde `Full validation gate` olarak çalışır.
- Validation job yalnız `contents: read` yetkisi kullanır.
- Rapor validated `commit_sha` + deterministic SHA-256 content fingerprint taşır.
- Finalizer PASS raporu, checkout HEAD ve recomputed fingerprint exact eşleşmeden çalışamaz.
- Validation sonrasında `main` ilerlerse publish `FAIL_CLOSED` olur; unvalidated içeriğe rebase edilmez.
- Finalizer'ın kendi metadata commit'i `[skip ci]` ile self-trigger döngüsü yaratmaz.
- Production planları `engineering_validation.validation_binding` altında validated SHA, content fingerprint ve report SHA taşır.
- P0 derived workflow'un yalnız volatile build timestamp'leri değiştiğinde yeni commit üretmesi engellendi. Gerçek run `32879032531`, `Only volatile derived timestamps changed; skipping publish.` ile `SUCCESS` verdi.
- P0 publish policy dosyası da artık `Full validation gate` path kapsamındadır.

Final strict acceptance run `32879219460` içinde validation job ve SHA/fingerprint-bound finalizer job'u `SUCCESS` tamamlandı.

Kalan tek nokta kod içinde değildir: GitHub `main` branch halen `protected=false`, required status checks enforcement kapalıdır. Tam merge yönetişimi için repo ayarında pull request zorunluluğu ve `Full validation gate` required status check olarak etkinleştirilmelidir. Bağlı GitHub aracı bu branch-protection/ruleset ayarını yazamadığı için durum gizlenmemiştir.

## P11 — Mutation testleri ve final kabul — TAMAMLANDI

**Risk:** `YELLOW-MUTATION-COVERAGE`

**Durum:** `CLOSED`

Merkezi mutation sözleşmesi eklendi:

- `skill/tymm-material-planner/tests/final_mutation_manifest.json`
- `skill/tymm-material-planner/scripts/run_final_mutation_suite.py`

Manifest P3–P10 arasındaki **8 risk ailesini 27 bilinçli bozuk mutation** ile kapsar. Runner:

1. manifest şemasını ve exact risk-family kapsamını doğrular,
2. mutation ID'lerinin benzersizliğini zorunlu kılar,
3. referans verilen negatif unittest'i tekil çalıştırır,
4. manifestte beklenen detector kodunun test metodunda gerçekten assert edildiğini denetler,
5. herhangi bir survivor veya eksik risk ailesinde FAIL verir.

Final sonuç:

```text
risk_families       = 8
mutation_cases      = 27
killed_mutations    = 27
surviving_mutations = 0
mutation_score      = 1.0 (%100)
```

Kapsam aileleri:

- P3 assessment scope
- P4 large-class route
- P5 closure load/time budget
- P6 adaptation/accessibility/media fallback
- P7 canonical reference grounding
- P8 package topology
- P9 JSON↔Markdown parity
- P10 validation SHA/fingerprint binding

Final strict run `32879219460` ayrıca:

- **176/176 generated lesson-plan package PASS**
- **344/344 çekirdek ders saati**
- **176/176 Markdown parity**
- failure records: **0**
- warning records: **0**
- finalizer: **SUCCESS**

Final binding snapshot:

- validated commit: `3702bab26f47c7e1dc87091c669b00278e2fff37`
- content fingerprint: `sha256:c0b63624ce313c518ec0b278390b4c3c6df584b09bc512cc7e4dcf35208fffde`
- fingerprinted files: `440`

Final mühendislik kabul belgesi: `docs/lesson-plan-final-acceptance.md`.

---

## Aktif durum

İçerik/lesson-plan mühendislik riskleri açısından **aktif sarı kalmamıştır**. P0–P9 ve P11 `CLOSED`; P10'un kod/CI kısmı `ENGINEERING_CLOSED` durumundadır.

Açık kalan tek kontrol bir **repository-governance ayarıdır**, lesson-plan artefaktı kalite açığı değildir:

| Kontrol | Durum | Gerekli işlem |
|---|---|---|
| `main` branch protection / required check enforcement | `EXTERNAL_ACTION_REQUIRED` | GitHub repo ayarında PR zorunluluğu + `Full validation gate` required status check |

## Faz sırası

```text
P0  Saat kaynaklı yanlış sarıları temizle            ✅ TAMAMLANDI
P1  Okul temelli 2 saati yerleşim katmanına bağla    ✅ TAMAMLANDI
P2  TDE10 okul temelli kariyer uyumunu düzelt         ✅ TAMAMLANDI
P3  Tema değerlendirmesi semantiğini düzelt           ✅ TAMAMLANDI
P4  Kalabalık sınıf rotalarını ekle                    ✅ TAMAMLANDI
P5  Aşırı yüklü kapanışları sadeleştir                 ✅ TAMAMLANDI
P6  Farklılaştırma / erişilebilirlik / fallback        ✅ TAMAMLANDI
P7  Rubrik-resource-artifact grounding                 ✅ TAMAMLANDI
P8  Paket topolojisi                                   ✅ TAMAMLANDI
P9  JSON-Markdown parity                               ✅ TAMAMLANDI
P10 CI / finalizer sertleştirme                        ✅ ENGINEERING_CLOSED / ⚠ REPO AYARI
P11 Mutation testleri ve final kabul                  ✅ TAMAMLANDI
```

Bu kayıt kapatılan riskleri silmez; her riskin sonucu ve kalan dış yönetişim kontrolü açık biçimde tutulur.
