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

Bu nedenle hiçbir ders planı yalnız Tema 4'ün geçmişte 46 saat görünmesi nedeniyle sarı kabul edilmeyecektir.

### P0 regression kapısı

`skill/tymm-material-planner/tests/test_theme_hour_contract.py` aşağıdaki invariant'ları doğrular:

1. Her tema `43 + 2 = 45`.
2. Her sınıf `172 + 8 = 180`.
3. Topic allocation toplamı tema başına 43.
4. Block binding toplamı tema başına 43.
5. Block binding çözümünde `NORMALIZED` kullanılmaz.
6. Tema 4 takvim artığı açıkça `calendar_residual_source_rows_excluded` ile dışlanır.

Test `TYMM Block-Hour Runtime Projection` CI akışının zorunlu regression setine eklenmiştir.

## P1 — Okul temelli 2 saati yerleşim katmanına bağla — TAMAMLANDI

### Kapatılan risk

**YELLOW-SBP-PLACEMENT — Okul temelli 2 saatin plan içindeki önerilen yerleşimi first-class değil**

Durum: `CLOSED`

Uygulama:

- `courses/TDE_9/production/school_based_planning_placements.json`
- `courses/TDE_10/production/school_based_planning_placements.json`

Her okul-temelli seçenek için artık aşağıdakiler yapısal olarak tutulur:

- `identified_need`
- `recommended_insertion_point.target_block_id`
- `recommended_insertion_point.anchor_package_id`
- `recommended_insertion_point.relation = AFTER_PACKAGE`
- `activation_condition`
- `impact_evaluation.method`
- `impact_evaluation.success_indicator`

Yerleşim bir **öneridir**, otomatik seçim değildir. Öğretmen/zümre tema başına en fazla 2 saati ihtiyaca göre seçer. Okul-temelli saatler çekirdek 43 saatin içine eklenmez, çekirdek paket sürelerini uzatmaz ve varsayılan 172 saatlik ders planı kuyruğuna girmez.

### P1 fail-closed doğrulama

`skill/tymm-material-planner/scripts/validate_school_based_planning_placements.py` şu invariant'ları doğrular:

1. Yıllık çekirdek kuyruk 172 saattir; okul-temelli saat 8'dir.
2. Her tema 43 çekirdek + 2 okul-temelli saat olarak kalır.
3. Her mevcut okul-temelli seçenek için tam bir placement kaydı vardır; fazladan veya eksik kayıt olamaz.
4. Placement tema ve süre bilgisi option kaydıyla birebir uyuşur.
5. `target_block_id` ve `anchor_package_id` gerçek üretim topolojisine karşı doğrulanır.
6. İhtiyaç, aktivasyon koşulu ve etki değerlendirmesi boş bırakılamaz.
7. Okul-temelli saatler 180 saatlik varsayılan üretim kuyruğuna sokulursa validation fail-closed olur.

Negatif regression testleri bilinmeyen package anchor, eksik option placement, okul-temelli saatlerin core queue'ya eklenmesi ve core saat politikasının değiştirilmesini beklenen FAIL olarak doğrular.

CI: `.github/workflows/tymm-school-based-planning.yml` push ve pull request üzerinde placement contract'ını zorunlu olarak doğrular.

Not: `TDE_10` okul-temelli seçeneklerinin 10. sınıf kariyer/mesleki rehberlik amacıyla içeriksel yeniden tasarımı **P2 kapsamıdır**; P1 yalnız güvenli ve gerçek uygulanabilir placement katmanını kurmuştur.

## Aktif sarı riskler

P0 ve P1 kapatıldıktan sonra aktif sarılar aşağıdaki risklerle sınırlıdır.

| ID | Faz | Risk | Etkilenen kapsam | Hedef |
|---|---|---|---|---|
| `YELLOW-TDE10-SBP-PURPOSE` | P2 | TDE10 okul temelli seçenekleri kariyer/mesleki rehberlik amacını sistematik taşımıyor | TDE10, 4 tema | 8 saatin kariyer rehberliği bağlamında yeniden tasarlanması |
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
P0  Saat kaynaklı yanlış sarıları temizle         ✅ TAMAMLANDI
P1  Okul temelli 2 saati yerleşim katmanına bağla ✅ TAMAMLANDI
P2  TDE10 okul temelli kariyer uyumunu düzelt
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
