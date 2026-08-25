# Ders Planları — Sarı Risk Düzeltme Planı

Bu belge, `TDE_9` ve `TDE_10` için üretilmiş ders planlarının dağıtıma hazırlık incelemesinde **sarı** olarak sınıflandırılan konuları tek bir düzeltme kuyruğunda tutar.

## Saat sözleşmesi

Bütün temalarda değişmez saat modeli:

```text
43 saat çekirdek öğretim
+ 2 saat okul temelli planlama
= 45 saat toplam
```

Yıllık planın hafta/tarih yerleşiminden doğan artık satırlar canonical konu veya blok süresine eklenmez. Bu nedenle Tema 4 için geçmişte görülen 46 saatlik ham yıllık-plan toplamı bir pedagojik risk, tema süresi veya blok normalizasyon gerekçesi değildir.

## P0 — Sarıları yeniden sınıflandır — TAMAMLANDI

### Kapatılan risk

**YELLOW-HOURS-46 — Tema 4'te 46 saat / 46→43 normalizasyonu**

Durum: `CLOSED`

Gerekçe:

- `TDE_9` ve `TDE_10` canonical dağılımı tema başına 43 çekirdek saat olarak tutulur.
- Her temada ayrıca 2 saat okul temelli planlama vardır.
- Tema toplamı 45 saattir.
- Haftalık/takvim yerleşiminden doğan artık satır canonical saate alınmaz.
- Tema 4 block-hour binding'lerinde `NORMALIZED_*` çözümü kullanılmaz; bağlamalar doğrudan canonical 43 saat üzerinden yapılır.

P0 regression kapısı `test_theme_hour_contract.py` ile `43+2=45`, yıllık `172+8=180`, doğrudan 43 saatlik block binding ve calendar residual exclusion invariant'larını doğrular.

## P1 — Okul temelli 2 saati yerleşim katmanına bağla — TAMAMLANDI

### Kapatılan risk

**YELLOW-SBP-PLACEMENT — Okul temelli 2 saatin plan içindeki önerilen yerleşimi first-class değil**

Durum: `CLOSED`

Uygulama:

- `courses/TDE_9/production/school_based_planning_placements.json`
- `courses/TDE_10/production/school_based_planning_placements.json`

Her okul-temelli seçenek için `identified_need`, gerçek `target_block_id`/`anchor_package_id`, `activation_condition` ve `impact_evaluation` tutulur. Yerleşim bir öneridir; otomatik seçim değildir. Okul-temelli saatler çekirdek 43 saati veya 172 saatlik varsayılan üretim kuyruğunu değiştirmez.

`validate_school_based_planning_placements.py` option-placement birebirliği, gerçek package anchor, tema/süre uyumu ve çekirdek saat izolasyonunu fail-closed doğrular. `.github/workflows/tymm-school-based-planning.yml` push ve pull request üzerinde bu sözleşmeyi çalıştırır.

## P2 — TDE10 okul-temelli kariyer uyumunu düzelt — TAMAMLANDI

### Kapatılan risk

**YELLOW-TDE10-SBP-PURPOSE — TDE10 okul temelli seçenekleri kariyer/mesleki rehberlik amacını sistematik taşımıyor**

Durum: `CLOSED`

### Resmî politika

10. sınıfta okul-temelli planlama saatleri öğrencilerin meslek seçimi ve kariyer planlamasına rehberlik edecek şekilde kullanılmalı; faaliyetler mesleki rehberlik ve kariyer danışmanlığı bağlamında yürütülmelidir. Bu grade-wide kural `courses/TDE_10/production/school_based_planning_options.json` içindeki `career_guidance_policy` alanına provenance ile bağlandı.

### Uygulanan pedagojik model

TDE10 için 4 tema × 2 saat = 8 saatin tamamı kariyer rehberliği bağlamında yeniden tasarlandı. Her seçenek yalnız meslek adı eklenmiş bir edebiyat etkinliği değildir; aşağıdaki üçlü zorunludur:

1. **TDE beceri köprüsü** — etkinlik gerçek bir TDE öğrenme çıktısına bağlanır.
2. **Meslek keşfi** — öğrenci ilgili meslek rollerinin görevlerini ve çalışma biçimlerini karşılaştırır.
3. **Kariyer kanıtı** — öğrenci kendi ilgi/beceri uyumuna dair somut bir öz-farkındalık/karar kanıtı üretir.

Tema bazındaki kariyer kümeleri:

| Tema | Kariyer ekseni |
|---|---|
| TEMA_01 — Sözün Ezgisi | Spikerlik, seslendirme, podcast/sesli medya; halkbilim, arşiv ve kültür araştırmacılığı |
| TEMA_02 — Kelimelerin Ritmi | Editörlük, redaktörlük, yayıncılık; podcast ve dijital içerik üretim rolleri |
| TEMA_03 — Dünden Bugüne | Senaristlik, dramaturji; müze eğitimi, arşiv ve kültürel miras projeleri |
| TEMA_04 — Nesillerin Mirası | Kültür haberciliği, belgesel/sözlü tarih; yayın editörlüğü, uyarlama ve kültürel içerik tasarımı |

Her option içinde first-class `career_guidance_alignment` tutulur:

- `career_guidance_required`
- `career_domains`
- `tde_skill_bridge`
- `career_exploration_action`
- `student_career_evidence`
- `self_awareness_prompt`
- `decision_support_question`

Her tema tam 2 saatlik kariyer seçeneği kapasitesi taşır; yıllık toplam 8 saattir. Bu katman yine çekirdek 172 saatten ayrıdır.

### P2 fail-closed doğrulama

`validate_school_based_planning_placements.py`, `TDE_10` için ayrıca şu koşulları zorunlu kılar:

1. Tüm seçeneklerin kategorisi `CAREER_GUIDANCE` olmalıdır.
2. Her seçenek en az bir TDE öğrenme çıktısına bağlı olmalıdır.
3. `career_guidance_alignment` ve meslek alanları boş olamaz.
4. TDE beceri köprüsü, meslek keşfi, kariyer kanıtı, öz farkındalık ve karar desteği alanları zorunludur.
5. Her tema tam 2 saat, yıllık toplam tam 8 saat kariyer-uyumlu option temsil etmelidir.
6. Placement policy `career_guidance_required=true` olmadan geçemez.

Negatif regression testleri generic `SCHOOL_BASED_PLANNING` kategorisine geri dönüşü, career alignment silinmesini, kariyer kanıtının boşaltılmasını, TDE outcome bağının kaldırılmasını, tema saatinin 2'yi aşmasını ve placement katmanında kariyer zorunluluğunun kapatılmasını beklenen FAIL olarak doğrular.

## Aktif sarı riskler

P0, P1 ve P2 kapatıldıktan sonra aktif sarılar aşağıdaki risklerle sınırlıdır.

| ID | Faz | Risk | Etkilenen kapsam | Hedef |
|---|---|---|---|---|
| `YELLOW-ASSESSMENT-SCOPE` | P3 | Tema sonu ölçme bazı son konuşma/yazma bloklarının outcome kapsamına gömülü | Tema sonu paketleri | `assessment_scope=THEME` + `assessed_outcome_codes` |
| `YELLOW-LARGE-CLASS` | P4 | Bireysel konuşma/yeniden performans akışı kalabalık sınıfta süreye sığmayabilir | Özellikle konuşma P05'leri | `large_class_route` |
| `YELLOW-CLOSURE-LOAD` | P5 | Test + günlük + düzeltme + kapanış aynı ders saatine yığılabiliyor | Tema/yıl sonu paketleri | Gerçekçi zaman bütçesi ve opsiyonel okul-temelli genişletme |
| `YELLOW-ADAPTATION` | P6 | Farklılaştırma, erişilebilirlik ve medya fallback'i lesson-plan schema'da first-class değil | Kritik paketler | Yapısal `classroom_adaptations` |
| `YELLOW-REF-GROUNDING` | P7 | Rubrik/resource/artifact kimlikleri prose içinde kalabiliyor | Rubrik/materyal kullanan paketler | Structured refs + canonical grounding |
| `YELLOW-PACKAGE-TOPOLOGY` | P8 | 88 paket/172 saat toplamı exact paket topolojisini kanıtlamıyor | TDE9/TDE10 | Exact manifest, sıra, saat aralığı, gap/overlap kontrolü |
| `YELLOW-MD-PARITY` | P9 | JSON ve Markdown için yalnız eş dosya varlığı doğrulanıyor | 176 paket | Deterministik JSON→Markdown parity |
| `YELLOW-CI-FINALIZER` | P10 | Full validation PR gate değil; finalizer validation report/HEAD fingerprint'e bağlı değil | Engineering/release gate | PR gate + SHA/fingerprint-bound PASS |
| `YELLOW-MUTATION-COVERAGE` | P11 | Semantik/topolojik hatalar için negatif mutation kapsamı eksik | CI | Bilinçli bozuk fixture'ların beklenen FAIL testleri |

## Sınıflandırma kuralı

Bir paket yalnız aşağıdaki koşullardan biri mevcutsa sarı tutulur:

- sınıf içinde gerçek uygulanabilirlik riski,
- ölçme kapsamı ile metadata arasında semantik uyumsuzluk,
- canonical referansın yapısal olarak doğrulanamaması,
- paket topolojisinin veya görünüm parity'sinin CI tarafından kanıtlanamaması,
- release/finalization zincirinde PASS'in mevcut commit ve canonical fingerprint'e bağlanamaması.

Ham yıllık-plan hafta yerleşimi, tek başına sarı sınıflandırma gerekçesi değildir.

## Faz sırası

```text
P0  Saat kaynaklı yanlış sarıları temizle          ✅ TAMAMLANDI
P1  Okul temelli 2 saati yerleşim katmanına bağla  ✅ TAMAMLANDI
P2  TDE10 okul temelli kariyer uyumunu düzelt       ✅ TAMAMLANDI
P3  Tema değerlendirmesi semantiğini düzelt
P4  Kalabalık sınıf rotalarını ekle
P5  Aşırı yüklü kapanışları sadeleştir
P6  Farklılaştırma / erişilebilirlik / fallback
P7  Rubrik-resource-artifact grounding
P8  Paket topolojisi
P9  JSON-Markdown parity
P10 CI / finalizer sertleştirme
P11 Mutation testleri ve final kabul
```

Her faz tamamlandığında bu belge güncellenir; kapatılan risk `CLOSED` olarak tutulur, sessizce silinmez. Böylece dağıtım kararının gerekçesi izlenebilir kalır.
