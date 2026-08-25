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

- Tema başına 43 çekirdek + 2 okul-temelli = 45 saat korunur.
- Yıllık toplam 172 + 8 = 180 saattir.
- Haftalık/takvim artıkları canonical saate girmez.
- `test_theme_hour_contract.py` bu sözleşmeyi regression kapısı olarak korur.

## P1 — Okul temelli 2 saati yerleşim katmanına bağla — TAMAMLANDI

### Kapatılan risk

**YELLOW-SBP-PLACEMENT — Okul temelli 2 saatin plan içindeki önerilen yerleşimi first-class değil**

Durum: `CLOSED`

`courses/TDE_9/production/school_based_planning_placements.json` ve `courses/TDE_10/production/school_based_planning_placements.json` ile her seçenek için ihtiyaç, gerçek block/package anchor, aktivasyon koşulu ve etki değerlendirmesi tutulur. Yerleşim öneridir; otomatik seçim değildir ve 172 saatlik çekirdek kuyruğu değiştirmez.

`validate_school_based_planning_placements.py` option-placement birebirliğini, gerçek anchor'ları ve çekirdek saat izolasyonunu fail-closed doğrular.

## P2 — TDE10 okul-temelli kariyer uyumunu düzelt — TAMAMLANDI

### Kapatılan risk

**YELLOW-TDE10-SBP-PURPOSE — TDE10 okul temelli seçenekleri kariyer/mesleki rehberlik amacını sistematik taşımıyor**

Durum: `CLOSED`

10. sınıftaki 4 tema × 2 saat = 8 okul-temelli saatin tamamı kariyer rehberliği bağlamında yeniden tasarlandı. Her seçenek üç zorunlu katman taşır:

1. **TDE beceri köprüsü** — gerçek TDE öğrenme çıktısı.
2. **Meslek keşfi** — ilgili meslek rollerinin görev ve çalışma biçimlerini inceleme.
3. **Kariyer kanıtı** — öğrencinin kendi ilgi/beceri uyumuna ilişkin somut öz-farkındalık/karar kanıtı.

Tema eksenleri sesli medya ve halkbilim; editörlük-yayıncılık ve dijital içerik; senaristlik-dramaturji ve kültürel miras; kültür haberciliği ve uyarlama/yayıncılıktır.

Validator, `CAREER_GUIDANCE`, TDE outcome bağı, meslek alanı, beceri köprüsü, kariyer kanıtı, öz-farkındalık, karar desteği ve tam 8 saat temsilini zorunlu kılar.

## P3 — Tema değerlendirmesi semantiğini düzelt — TAMAMLANDI

### Kapatılan risk

**YELLOW-ASSESSMENT-SCOPE — Tema sonu ölçme son konuşma/yazma bloğunun outcome kapsamına gömülü**

Durum: `CLOSED`

### Yeni kapsam modeli

Ders planı sözleşmesi öğretim kapsamı ile ölçme kapsamını artık birbirinden ayırır:

- `outcome_codes`: mevcut davranışı koruyarak **blok içindeki öğretim kapsamını** gösterir.
- `instruction_scope`: `BLOCK`.
- `assessment_scope`: `BLOCK | THEME`.
- `assessed_outcome_codes`: ölçme/yansıtmanın gerçekten kapsadığı öğrenme çıktılarını gösterir.

Bu ekleme geriye dönük uyumludur; tema-geneli ölçme taşımayan mevcut paketlerin tümünü yeniden yazmayı gerektirmez.

### Context grounding

`lesson_plan_context.py` context v1.2 ile artık son blok çıktılarının yanında bütün temanın çıktılarını da verir:

- `theme_outcomes`
- `allowed_references.theme_outcome_codes`

Böylece bir tema testi yalnız son yazma/konuşma bloğunun çıktılarıyla etiketlenemez; tema-geneli assessed kodlar canonical runtime'dan türetilir.

### Migrate edilen paketler

Her iki sınıfta dört tema olmak üzere **8 tema-kapanış P05 paketi** migrate edildi.

- TDE9 tema-geneli kapsam: 12 öğrenme çıktısı.
- TDE10 tema-geneli kapsam: 16 öğrenme çıktısı.
- Nihai ürün/revizyon saati gerçekten blok değerlendirmesiyse `assessment_scope=BLOCK` kalır.
- Tema sonu test/öğrenme günlüğü/yansıtma saati `assessment_scope=THEME` taşır.
- TDE9 Tema 1 P05'in iki saati de doğrudan tema kapanışı olduğu için iki ders de `THEME` kapsamındadır.

### P3 fail-closed doğrulama

`validate_lesson_plan.py` artık:

1. Tema sonu ölçme/yansıtma kaynağı kullanıldığında `assessment_scope=THEME` ister.
2. `assessed_outcome_codes` değerlerini yalnız aynı temanın canonical outcome kümesine karşı doğrular.
3. Tema kapsamı iddia edilip assessed kodlar yalnız son bloğun çıktılarından oluşuyorsa `THEME_ASSESSMENT_OUTCOMES_TOO_NARROW` ile FAIL verir.
4. Blok değerlendirmesinin tema dışı outcome kullanmasına izin vermez.
5. Tema-geneli öğrenme günlüğünü, activity ID'sinde ayrıca `TEMA` sözcüğü bulunmasa da tema kapanış kanıtı olarak tanır.

Regression testleri açık theme scope eksikliğini, daraltılmış outcome kapsamını ve bağımsız `OGRENME_GUNLUGU` sinyalini kapsar.

### P3 kabul sonucu

`TYMM Lesson Plan Full Validation` bütün **176 paket / 344 çekirdek ders saati** üzerinde başarıyla tamamlandı; `Validate all 176 lesson-plan packages` ve finalization adımları `SUCCESS` verdi.

## P4 — Kalabalık sınıf rotalarını ekle — TAMAMLANDI

### Kapatılan risk

**YELLOW-LARGE-CLASS — Bireysel konuşma/yeniden performans akışı kalabalık sınıfta süreye sığmayabilir**

Durum: `CLOSED`

### Uygulanabilirlik modeli

Konuşma bloklarında gerçek canlı performans etkinliği kullanan paketlere first-class `large_class_route` eklendi. Hazırlık, planlama veya yalnız yansıtma yapan paketler sırf konuşma bloğunda oldukları için bu rotayı taşımak zorunda değildir.

Performans sinyalleri kaynak etkinlik kimliklerinden fail-closed belirlenir: `KONUSMA_SIRASI`, canlı `SUNUM`, `PODCAST_URETIM`, `CANLANDIR` ve `DINLETI` türleri.

`large_class_route` şu sözleşmeyi taşır:

- `mode=PARALLEL_GROUPS`
- gerçek ders numaralarını belirleyen `applies_to_lesson_numbers`
- 2–8 arası `parallel_group_count`
- grup içi konuşmacı/gözlemci rollerinin döndürülmesi
- öğretmenin gruplar arasında planlı rotasyonu ve her öğrenciden doğrudan kanıt toplaması
- akran gözlemcinin kişilik yorumu yerine mevcut performans ölçütlerinden gözlenebilir kanıt kaydetmesi
- 30–300 saniye arası performans zaman sınırı
- standart rota ile aynı etkinlik, outcome, ölçüt ve kanıtların korunmasını garanti eden `evidence_equivalence`
- `core_hours_independent_of_school_based_extension=true`

Okul-temelli ek saat yalnız hedefli ek prova veya kısa yeniden performans için **opsiyonel** olabilir. Hiçbir çekirdek konuşma paketi, tamamlanabilmek için okul-temelli saate bağımlı hâle getirilemez.

### Migrate edilen paketler

Validatorın gerçek performans sinyaliyle belirlediği toplam **29 paket** migrate edildi:

- TDE9: 16 paket
- TDE10: 13 paket

Bu kapsam şiir/dinleti ve hazırlıklı konuşma performanslarını, podcast üretimini, destan sunumlarını, canlandırmaları ve kısa yeniden performans içeren paketleri kapsar.

Örneğin tek sıra sınıf önü sunum yerine 4–6 kişilik paralel gruplar kullanılabilir; öğretmen gruplar arasında dönerken akran gözlemciler aynı canonical ölçütlerden kanıt toplar. Bu, etkinliğin içeriğini veya değerlendirme ölçütlerini değiştirmez; yalnız yürütme topolojisini kalabalık sınıfa uyarlayarak süre riskini azaltır.

### P4 fail-closed doğrulama

`validate_lesson_plan.py` artık gerçek konuşma performansı içeren bir paket için:

1. `large_class_route` yoksa `LARGE_CLASS_ROUTE_REQUIRED` ile FAIL verir.
2. Route'un performans içeren bütün ders saatlerini kapsamasını zorunlu kılar.
3. Grup sayısı, performans zaman sınırı ve required strateji alanlarını doğrular.
4. Route'un çekirdek planı okul-temelli saate bağlamasına izin vermez.
5. Hazırlık/planlama paketlerine gereksiz route zorunluluğu getirmez.

`test_large_class_route.py` route eksikliği, eksik ders kapsamı ve okul-temelli saate bağımlı çekirdek rota için beklenen FAIL; geçerli paralel grup rotası için PASS regression testleri içerir. Bu test artık `TYMM Lesson Plan Full Validation` içinde doğrudan çalışır.

### P4 kabul sonucu

Geçici migration adımıyla 29 route materialize edildikten sonra auto-migration workflow'dan kaldırıldı. Ardından strict doğrulamada:

- `Run large-class route regression tests`: `SUCCESS`
- `Validate all 176 lesson-plan packages`: `SUCCESS`
- finalization: `SUCCESS`

Böylece doğrulama artık eksik route'u sessizce üretmiyor; repoya commitlenmiş veriyi doğrudan fail-closed denetliyor.

## Aktif sarı riskler

P0–P4 kapatıldıktan sonra aktif sarılar:

| ID | Faz | Risk | Etkilenen kapsam | Hedef |
|---|---|---|---|---|
| `YELLOW-CLOSURE-LOAD` | P5 | Test + günlük + düzeltme + kapanış aynı ders saatine yığılabiliyor | Tema/yıl sonu paketleri | Gerçekçi zaman bütçesi ve opsiyonel okul-temelli genişletme |
| `YELLOW-ADAPTATION` | P6 | Farklılaştırma, erişilebilirlik ve medya fallback'i lesson-plan schema'da first-class değil | Kritik paketler | Yapısal `classroom_adaptations` |
| `YELLOW-REF-GROUNDING` | P7 | Rubrik/resource/artifact kimlikleri prose içinde kalabiliyor | Rubrik/materyal kullanan paketler | Structured refs + canonical grounding |
| `YELLOW-PACKAGE-TOPOLOGY` | P8 | 88 paket/172 saat toplamı exact paket topolojisini kanıtlamıyor | TDE9/TDE10 | Exact manifest, sıra, saat aralığı, gap/overlap kontrolü |
| `YELLOW-MD-PARITY` | P9 | JSON ve Markdown için yalnız eş dosya varlığı doğrulanıyor | 176 paket | Deterministik JSON→Markdown parity |
| `YELLOW-CI-FINALIZER` | P10 | Full validation PR gate değil; finalizer validation report/HEAD fingerprint'e bağlı değil | Engineering/release gate | PR gate + SHA/fingerprint-bound PASS |
| `YELLOW-MUTATION-COVERAGE` | P11 | Semantik/topolojik hatalar için negatif mutation kapsamı eksik | CI | Bilinçli bozuk fixture'ların beklenen FAIL testleri |

## Sınıflandırma kuralı

Bir paket yalnız gerçek sınıf uygulanabilirlik riski, ölçme/metadata semantik uyumsuzluğu, canonical referansın doğrulanamaması, paket/parity doğrulama açığı veya release/finalization zinciri riski varsa sarı tutulur. Ham yıllık-plan hafta yerleşimi tek başına sarı gerekçesi değildir.

## Faz sırası

```text
P0  Saat kaynaklı yanlış sarıları temizle           ✅ TAMAMLANDI
P1  Okul temelli 2 saati yerleşim katmanına bağla   ✅ TAMAMLANDI
P2  TDE10 okul temelli kariyer uyumunu düzelt        ✅ TAMAMLANDI
P3  Tema değerlendirmesi semantiğini düzelt          ✅ TAMAMLANDI
P4  Kalabalık sınıf rotalarını ekle                   ✅ TAMAMLANDI
P5  Aşırı yüklü kapanışları sadeleştir
P6  Farklılaştırma / erişilebilirlik / fallback
P7  Rubrik-resource-artifact grounding
P8  Paket topolojisi
P9  JSON-Markdown parity
P10 CI / finalizer sertleştirme
P11 Mutation testleri ve final kabul
```

Her faz tamamlandığında bu belge güncellenir; kapatılan risk `CLOSED` olarak tutulur, sessizce silinmez. Böylece dağıtım kararının gerekçesi izlenebilir kalır.
