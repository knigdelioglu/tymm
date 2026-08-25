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

## P5 — Aşırı yüklü kapanışları sadeleştir — TAMAMLANDI

### Kapatılan risk

**YELLOW-CLOSURE-LOAD — Test + günlük + düzeltme + kapanış aynı ders saatine yığılabiliyor**

Durum: `CLOSED`

### Süre bütçesi modeli

Tema kapanışları için ayrı, makine-okunur bir operasyon katmanı oluşturuldu:

- `courses/TDE_9/production/closure_time_budgets.json`
- `courses/TDE_10/production/closure_time_budgets.json`

Bu katman her iki sınıftaki **8 tema-kapanış P05 paketi** ve tema-geneli ölçme/yansıtma taşıyan gerçek ders saatlerini package/path/theme/block düzeyinde bağlar. TDE9 Tema 1'de ölçme ve öğrenme günlüğü ayrı iki ders olduğu için toplam budget edilen tema-kapanış dersi sayısı **9**'dur.

`40 dakika`, burada resmî MEB süre iddiası değil, repo içindeki **nominal pedagojik ders periyodu bütçesidir**. Amaç, tek ders saatine sınırsız görev yığılmasını teknik olarak engellemektir.

Hem tema ölçme hem öğrenme günlüğü/yansıtma taşıyan karma kapanış saatlerinde çekirdek bütçe sabittir:

```text
25 dk  tema sonu ölçme
10 dk  çekirdek öğrenme günlüğü / yansıtma
 3 dk  kısa tema/yıl kapanışı
 2 dk  tampon
= 40 dk
```

Tek odaklı kapanışlarda — yalnız tema ölçme veya yalnız öğrenme günlüğü — çekirdek görev 32 dakika, kısa kapanış 5 dakika ve tampon 3 dakikadır.

### Çekirdek ile opsiyonel genişletmenin ayrılması

Aşağıdaki işler aynı 40 dakikalık çekirdek kapanışın zorunlu parçası değildir:

- ayrıntılı yanlış/kararsız cevap düzeltmesi (`ANSWER_CORRECTION`)
- çoklu ürün/performans üzerinden genişletilmiş günlük ve portfolyo taraması (`EXTENDED_REFLECTION`)
- sonraki temaya ayrıntılı ön hazırlık (`NEXT_THEME_PREP`)
- yıl sonu dört beceri alanını kapsayan ayrıntılı portfolyo sentezi (`YEAR_PORTFOLIO_REVIEW`)

Bu rotaların tamamında `placement=SCHOOL_BASED_IF_SELECTED` ve `required_for_core_completion=false` zorunludur. Yani öğretmen/zümre gerçek bir ihtiyaç görür ve ilgili okul-temelli saati seçerse kullanılabilir; **43 saatlik çekirdek tema öğretimi bunlara bağlı değildir**.

Süre sözleşmesi yalnız sidecar dosyada kalmaz. İlgili kapanış dersinin `teacher_actions` alanındaki ilk yönerge de gerçek dakika bütçesini açıkça gösterir. Böylece öğretmen-facing plan ile machine-readable bütçenin sessizce ayrışması engellenir.

### P5 fail-closed doğrulama

`validate_closure_time_budgets.py` artık:

1. Her sınıfta tam 4 tema-kapanış paketini otomatik keşfeder ve contract paket kümesiyle birebir eşler.
2. Package path, theme, block ve gerçek tema-kapanış ders numaralarını doğrular.
3. Zorunlu segmentlerin dakika toplamı + tamponun tam bir nominal ders periyoduna eşit olmasını zorunlu kılar.
4. Karma kapanışta 25/10/3/2 dağılımını fail-closed sabitler.
5. Tema ölçmeye en az 20 dakika, yansıtmaya en az 5 dakika ayrılmasını korur.
6. Opsiyonel genişletmenin çekirdek tamamlanma koşuluna dönüşmesine izin vermez.
7. Karma kapanışlarda cevap düzeltme + genişletilmiş yansıtma + tema/yıl geçiş rotalarının gerçekten opsiyonel olarak tanımlanmasını ister.
8. Öğretmen planında `Süre bütçesi:` yönergesi kaybolursa FAIL verir.

`test_closure_time_budgets.py` özellikle şu mutation'ları kapsar:

- 40 dakikayı aşan zorunlu görev bütçesi
- opsiyonel genişletmenin `required_for_core_completion=true` yapılması
- bir tema-kapanış paketinin contract'tan silinmesi
- öğretmen-facing süre yönergesinin kaldırılması

Bu test ve contract validator artık `TYMM Lesson Plan Full Validation` içinde doğrudan çalışır.

### P5 kabul sonucu

Geçici materialization adımıyla budget dosyaları ve öğretmen-facing süre yönergeleri repoya yazıldıktan sonra auto-migration workflow'dan kaldırıldı. Strict doğrulamada:

- `Run closure time-budget regression tests`: `SUCCESS`
- `Validate closure time-budget contracts`: `SUCCESS`
- `Run large-class route regression tests`: `SUCCESS`
- `Validate all 176 lesson-plan packages`: `SUCCESS`
- finalization: `SUCCESS`

Böylece tema/yıl kapanışı artık “test + günlük + düzeltme + portfolyo + geçiş hazırlığı”nın aynı çekirdek saatte zorunlu kabul edildiği açık uçlu bir iş listesi değildir; çekirdek ile ihtiyaç-temelli genişletme teknik olarak ayrılmıştır.

## P6 — Farklılaştırma, erişilebilirlik ve medya fallback — TAMAMLANDI

### Kapatılan risk

**YELLOW-ADAPTATION — Farklılaştırma, erişilebilirlik ve medya fallback'i lesson-plan schema'da first-class değil**

Durum: `CLOSED`

### Seçici kritik-paket modeli

`classroom_adaptations` bütün 176 pakete boilerplate olarak eklenmez. Fail-closed detector yalnız iki gerçek uygulama sinyalini hedefler:

- `MEDIA_DEPENDENT`: dinleme/izleme bloğu veya gerçek activity/material referansında podcast, video, belgesel, ses kaydı/karekod gibi medya gereksinimi.
- `LIVE_PERFORMANCE`: P4'te gerçek canlı sözlü performans olarak belirlenmiş ve `large_class_route` taşıyan paket.

Narrative `plan_summary` veya objective içinde başka bir beceriden söz edilmesi tek başına medya bağımlılığı sayılmaz. Detector bu nedenle blok kimliği + gerçek activity/material yürütme kanıtından türetilir.

Kesin manifest kapsamı:

- **TDE9:** 36 kritik paket = 20 medya-bağımlı + 16 canlı performans, overlap 0.
- **TDE10:** 32 kritik paket = 21 medya-bağımlı + 13 canlı performans, overlap 2.
- **Toplam:** 68 benzersiz kritik paket; 41 medya-bağımlı, 29 canlı performans, 2 paket iki kategoriye birden girer.

Manifestler:

- `courses/TDE_9/production/classroom_adaptation_manifest.json`
- `courses/TDE_10/production/classroom_adaptation_manifest.json`

### First-class `classroom_adaptations` sözleşmesi

Lesson-plan schema kritik paketlerde aşağıdaki katmanları temsil edebilir; validator bunların hedef paketlerde gerçekten bulunmasını zorunlu kılar:

1. **Farklılaştırma**
   - `scaffold_route`
   - `enrichment_route`
   - `outcomes_unchanged=true`
2. **Erişilebilirlik**
   - `representation_supports`
   - `participation_supports`
   - `environment_supports`
   - `assessment_construct_preserved=true`
3. **Kanıt eşdeğerliği**
   - uyarlama temsil/süreç/ortam/katılım yolunu değiştirebilir; canonical çıktı ve değerlendirmede aranan temel kanıtı düşüremez.

### Medya fallback güvenlik kuralları

`MEDIA_DEPENDENT` paketlerde `media_fallback` zorunludur:

- çekirdek rota internet bağlantısına bağımlı olamaz (`network_independent_core_route=true`);
- mümkünse aynı kaynağın yerel/çevrimdışı kopyası, değilse aynı öğrenme kanıtını taşıyan öğretmen-onaylı eşdeğer kullanılmalıdır;
- altyazı/transkript, yeniden oynatma ve sözel/görsel açıklama erişim desteği olabilir;
- **dinleme/izleme becerisinin kendisi hedef veya ölçme nesnesiyse transkript varsayılan ikame değildir** (`transcript_is_support_not_default_substitute=true`).

Bu ayrım, erişilebilirlik sağlarken ölçülen construct'ın sessizce “dinleme yerine okuma”ya dönüşmesini engeller.

### Canlı performans erişim rotası

`LIVE_PERFORMANCE` paketlerde `live_performance_access` zorunludur. Desteklenen eşdeğer yürütmeler:

- küçük grupta canlı performans (`SMALL_GROUP_LIVE`)
- öğretmenin doğrudan gözlediği canlı performans (`TEACHER_OBSERVED_LIVE`)
- kurum/öğretmen uygulaması izin veriyorsa ve kayıt için gerekli onay/rıza varsa kayıtlı sözlü performans (`RECORDED_ORAL_IF_ALLOWED`)

Aynı sözlü performans kanıtı korunur; **yalnız yazılı ürünle konuşma performansı ikamesi yasaktır** (`written_only_substitution_allowed=false`). Kayıt rotasında `recording_requires_consent=true` zorunludur.

### P6 fail-closed doğrulama

`validate_classroom_adaptations.py` artık:

1. Kritik paket kümesini source-grounded detector ile yeniden keşfeder ve manifestle birebir eşler.
2. Kritik olmayan pakete gereksiz adaptation eklenirse FAIL verir.
3. Kritik pakette `classroom_adaptations` yoksa FAIL verir.
4. Farklılaştırmanın öğrenme çıktılarını, erişilebilirliğin assessment construct'ını koruduğunu zorunlu kılar.
5. Medya paketinde çevrimdışı rota, aynı/eşdeğer kaynak kanıtı ve transkript güvenlik kuralını doğrular.
6. Canlı performansta eşdeğer sözlü rota, yazılı-only ikame yasağı ve kayıt rızasını doğrular.
7. Manifest summary ve package/path/theme/block/trigger/media-type alanlarını gerçek planlarla exact eşler.

`test_classroom_adaptations.py` şu negatif mutation'ları kapsar:

- kritik paketten adaptation alanını silme
- transkripti varsayılan dinleme ikamesine dönüştürme
- sözlü performansı yalnız yazılı ürüne çevirmeye izin verme
- kritik paketi manifestten çıkarma

### P6 kabul sonucu

İlk materialization sonrasında detector narrative özetlerden etkilenmeyecek şekilde daraltıldı ve kapsam yeniden üretildi. Daha sonra auto-materialization/publish adımları workflow'dan kaldırıldı. Strict doğrulamada:

- `Run classroom adaptation regression tests`: `SUCCESS`
- `Validate classroom adaptation contracts`: `SUCCESS`
- `Run closure time-budget regression tests`: `SUCCESS`
- `Validate closure time-budget contracts`: `SUCCESS`
- `Run large-class route regression tests`: `SUCCESS`
- `Validate all 176 lesson-plan packages`: `SUCCESS`
- finalization: `SUCCESS`

Böylece CI artık eksik/bozuk adaptation'ı kendisi tamamlamıyor; repoya commitlenmiş 68 kritik paketin sözleşmesini doğrudan fail-closed doğruluyor.

## P7 — Rubrik / resource / artifact grounding — TAMAMLANDI

### Kapatılan risk

**YELLOW-REF-GROUNDING — Rubrik/resource/artifact kimlikleri prose içinde kalabiliyor**

Durum: `CLOSED`

### First-class referans modeli

Lesson-plan schema'ya opsiyonel fakat hedef paketlerde validator tarafından zorunlu tutulan `grounded_references` alanı eklendi. Üç canonical referans ailesi ayrı tutulur:

- `form_refs`: `form_id` + `usage`
- `assessment_artifact_refs`: `artifact_id` + gerçek `binding_key` + `usage`
- `resource_refs`: `resource_plan_id` + `usage`

`usage` semantiği üç değerden biridir:

- `USED`: bu pakette gerçekten kullanıldı.
- `DEFERRED`: canonical referans geçiyor ancak kullanım sonraki paket/aşamaya bırakıldı.
- `REFERENCE_ONLY`: kimlik bağlam veya doğrulama amacıyla anılıyor; bu pakette kullanım iddiası yok.

Böylece “rubrik adı prose içinde geçti” ile “rubrik gerçekten bu derste kullanıldı” aynı şey olmaktan çıktı. Mevcut `used_form_ids` korunur; burada kullanılan formun structured ref karşılığı `USED` olmak zorundadır.

### Canonical kaynak zinciri

Grounding detector ve validator referansları şu kaynaklardan çözer:

- ders kitabı formları: `textbook_forms_index.json`
- materialize edilmiş canonical değerlendirme formları: `production/assessment_form_registry.json`
- yıllık değerlendirme artifact'ları ve task binding'leri: `production/assessment_artifact_registry.json`
- resource plan kimlikleri ve tema bağları: `production/consolidated_resource_plan.json`

`lesson_plan_context.py` context v1.3 ile ayrıca şunları üretim context'ine çıkarır:

- `allowed_references.resource_plan_ids`
- `allowed_references.assessment_artifact_ids`
- `allowed_references.assessment_binding_keys`
- artifact `generation_status`, `teacher_review_required`, `source_equivalence_status`, `binding_key_semantics`

Generation contract canonical ID'nin prose-only bırakılmasını, current block dışı artifact binding'i kullanılmasını ve lifecycle/equivalence bilgisinin uydurulmasını yasaklar.

### Migration kapsamı

Grounding manifestleri:

- `courses/TDE_9/production/grounded_reference_manifest.json`
- `courses/TDE_10/production/grounded_reference_manifest.json`

Kesin kapsam:

- **TDE9:** 49 paket; 95 form ref + 36 assessment artifact ref + 15 resource ref = **146 structured canonical referans**.
- **TDE10:** 33 paket; 64 form ref + 2 assessment artifact ref = **66 structured canonical referans**.
- **Toplam:** 82 paket ve **212 structured canonical referans**.

TDE9 kullanım dağılımı 89 `USED`, 52 `DEFERRED`, 5 `REFERENCE_ONLY`; TDE10 dağılımı 52 `USED`, 7 `DEFERRED`, 7 `REFERENCE_ONLY` olarak manifestte exact tutulur.

### Lifecycle ve equivalence güvenliği

Planın structured ref alanına artifact başlığı, generation status veya approval durumu kopyalanmaz. Bunlar değişebilir canonical metadata olduğundan kullanım anında registry/approval kaydından okunur. Böylece planın aylar sonra “henüz üretilmemiş” gibi bayat bir durum cümlesini authoritative gerçek kabul etmesi engellenir.

Bu faz sırasında TDE9 Tema 2 Yazma P03'teki eski `TDE9_YAZMA_RUBRIC henüz üretilmiş görünmedi` iddiası da kaldırıldı; canonical teacher-approval kaydı mevcut olduğundan plan artık lifecycle bilgisini prose'a sabitlemek yerine canonical registry/approval kaydından doğrulama talimatı taşır.

TDE10'da auth-gated EBA provenance için exact dış kaynak eşdeğerliği doğrulanmamışsa plan “EBA ile aynı / birebir EBA rubriği” iddiasında bulunamaz. `source_equivalence_status` içindeki `UNVERIFIED`/`UNRESOLVED` durumları bu iddiayı fail-closed engeller.

### P7 fail-closed doğrulama

`validate_grounded_references.py` artık:

1. Prose'daki canonical form/artifact/resource kimliklerini tekrar keşfeder ve structured refs ile exact eşler.
2. `used_form_ids` içindeki formun `USED` structured ref'ini zorunlu kılar.
3. Artifact için current block/theme binding ve `binding_key` doğrular.
4. Resource kimliğinin planın temasına bağlı olmasını zorunlu kılar.
5. Uydurulmuş canonical-looking ID'lerde FAIL verir.
6. Gereksiz/ekstra structured ref'e izin vermez.
7. Manifest package/path/theme/block ve referans sayılarını exact doğrular.
8. Unverified dış değerlendirme eşdeğerliği için kesinlik iddiasını engeller.

Kaynakta tarihsel olarak kullanılan `FORM_BOB_02` gibi kısa kimlik yalnız canonical katalogda tek bir tam ID'ye benzersiz prefix olarak çözülüyorsa tolere edilir; structured kimlik yine tam canonical ID'dir. Belirsiz veya karşılığı olmayan kısaltma fail-closed kalır.

`test_grounded_references.py` şu negatif mutation'ları kapsar:

- kullanılan formun structured ref'ini silme
- prose'da artifact anıp structured artifact ref'i kaldırma
- uydurma canonical-looking ID kullanma
- artifact binding key'i bozma
- unverified EBA equivalence'i kesin eşdeğerlik gibi sunma

### P7 kabul sonucu

İlk migration koşuları iki gerçek katalog açığını yakaladı: benzersiz historical form shorthand'i ve TDE10 `assessment_form_registry.json` içindeki materialize canonical formlar. Detector bunları source-grounded biçimde kapsayacak şekilde düzeltildikten sonra 82 hedef paket materialize edildi. Ardından auto-materialization/publish adımları workflow'dan kaldırıldı.

Strict `TYMM Lesson Plan Full Validation` run `32854223974` sonucunda:

- `Run grounded-reference regression tests`: `SUCCESS`
- `Validate grounded-reference contracts`: `SUCCESS`
- `Run classroom adaptation regression tests`: `SUCCESS`
- `Validate classroom adaptation contracts`: `SUCCESS`
- `Run closure time-budget regression tests`: `SUCCESS`
- `Validate closure time-budget contracts`: `SUCCESS`
- `Run large-class route regression tests`: `SUCCESS`
- `Validate all 176 lesson-plan packages`: `SUCCESS`
- finalization: `SUCCESS`

CI artık eksik grounded ref'i kendi kendine üretmez; committed plan ve manifest verisini doğrudan fail-closed doğrular.

## P8 — Exact paket topolojisi — TAMAMLANDI

### Kapatılan risk

**YELLOW-PACKAGE-TOPOLOGY — 88 paket / 172 saat toplamı exact paket sırasını ve saat kaplamasını kanıtlamıyor**

Durum: `CLOSED`

### Canonical topoloji modeli

Her sınıf için takvimden bağımsız, makine-okunur bir exact topoloji manifesti oluşturuldu:

- `courses/TDE_9/production/lesson_package_topology.json`
- `courses/TDE_10/production/lesson_package_topology.json`

Manifest tek bir kaynağın kendi kendini doğrulamasına dayanmaz. Üç ayrı canonical/committed katman çapraz bağlanır:

1. blok sırası: `production/teaching_blocks.json:block_sequence`
2. blok saatleri: `planning/block_hour_bindings.json:planned_hours`
3. paketleme bölümü: `planning/lesson_plan_production_plan.json:package_hours`
4. gerçek çıktı kümesi: `generated/lesson_plans/**/*.json`

Üretim planındaki `package_hours` ancak canonical blok saatiyle tam eşleşiyorsa kabul edilir. Varsayılan paket boyu 2 saattir; 15 saatlik bloklarda kalan son saat uydurulmadan 1 saatlik son pakete dönüşür.

### Saat aralığı sözleşmesi

Bütün aralıklar `ONE_BASED_INCLUSIVE` semantiği taşır. Her paket için üç bağımsız saat aralığı tutulur:

- `course_hour_range`
- `theme_hour_range`
- `block_hour_range`

Tema course aralıkları her iki sınıfta da kesin olarak:

```text
TEMA_01   1–43
TEMA_02  44–86
TEMA_03  87–129
TEMA_04 130–172
```

Tema içinde sayaç yeniden 1–43'e, blok içinde 1–blok_süresi aralığına döner. Böylece yalnız toplam 172 saat değil, her paketin çekirdek öğretim dizisindeki kesin yeri de doğrulanabilir.

Okul-temelli 2 saatler bu topolojiye bilinçli olarak dahil değildir; manifest yalnız 43 × 4 = 172 saatlik çekirdek kuyruğu temsil eder.

### Exact kapsam

Her iki sınıf için ayrı ayrı:

- 4 tema
- 16 blok
- 88 paket
- 172 çekirdek ders saati
- `gaps=0`
- `overlaps=0`

Toplam doğrulanan set **176 paket / 344 çekirdek ders saatidir**.

### P8 fail-closed doğrulama

`build_package_topology_manifest.py` manifesti üretmeden önce:

1. `teaching_blocks`, `block_hour_bindings` ve production-plan theme/block sıralarını exact karşılaştırır.
2. Her blokta canonical saat ile `planned_hours` değerini eşler.
3. Paket partition'ının 2 saatlik paketler + yalnız gerekli yerde 1 saatlik remainder biçiminde olmasını zorunlu kılar.
4. Beklenen package ID/path kümesini gerçek generated JSON kümesiyle birebir karşılaştırır; eksik veya ekstra JSON paketi kabul etmez.
5. Her planın `course_id`, `theme_id`, `block_id`, `lesson_hours` ve iç lesson duration toplamını topolojiyle eşler.
6. Production progress değerlerinin 88 paket / 172 saat tamamlanma iddiasıyla tutarlı olmasını zorunlu kılar.

`validate_package_topology.py` committed manifesti aynı canonical kaynaklardan yeniden türetilen deterministik beklenen topolojiye karşı fail-closed denetler. Package order, ordinal, path, saat, theme/block ilişkisi ve course/theme/block hour-range değerlerinden herhangi biri kayarsa FAIL verir.

`test_package_topology.py` özellikle şu mutation'ları kapsar:

- bir paketin manifestten silinmesi
- course saat aralığında overlap/gap oluşturulması
- paket sırasının değiştirilmesi
- package path'in bozulması
- package lesson-hour değerinin değiştirilmesi
- 15 saatlik blokların 1 saatlik son paket sözleşmesinin korunması

### P8 kabul sonucu

İlk CI koşusunda manifestler materialize edilip repoya commitlendi. Daha sonra materialization/publish adımları workflow'dan kaldırıldı; CI eksik manifesti kendi kendine onaramaz.

Strict `TYMM Lesson Plan Full Validation` run `32862686503` sonucunda:

- `Run package-topology regression tests`: `SUCCESS`
- `Validate package-topology contracts`: `SUCCESS`
- `Run grounded-reference regression tests`: `SUCCESS`
- `Validate grounded-reference contracts`: `SUCCESS`
- `Run classroom adaptation regression tests`: `SUCCESS`
- `Validate classroom adaptation contracts`: `SUCCESS`
- `Run closure time-budget regression tests`: `SUCCESS`
- `Validate closure time-budget contracts`: `SUCCESS`
- `Run large-class route regression tests`: `SUCCESS`
- `Validate all 176 lesson-plan packages`: `SUCCESS`
- finalization: `SUCCESS`

Böylece “88 paket ve toplam 172 saat var” düzeyindeki zayıf kabul, artık exact sıra + saat aralığı + kaynak çapraz kontrolü + gap/overlap denetimine yükseltildi.

## Aktif sarı riskler

P0–P8 kapatıldıktan sonra aktif sarılar:

| ID | Faz | Risk | Etkilenen kapsam | Hedef |
|---|---|---|---|---|
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
P5  Aşırı yüklü kapanışları sadeleştir                ✅ TAMAMLANDI
P6  Farklılaştırma / erişilebilirlik / fallback       ✅ TAMAMLANDI
P7  Rubrik-resource-artifact grounding                ✅ TAMAMLANDI
P8  Paket topolojisi                                  ✅ TAMAMLANDI
P9  JSON-Markdown parity
P10 CI / finalizer sertleştirme
P11 Mutation testleri ve final kabul
```

Her faz tamamlandığında bu belge güncellenir; kapatılan risk `CLOSED` olarak tutulur, sessizce silinmez. Böylece dağıtım kararının gerekçesi izlenebilir kalır.
