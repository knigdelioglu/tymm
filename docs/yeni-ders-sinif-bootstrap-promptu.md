# Yeni Ders / Sınıf Bootstrap Promptu

Bu prompt, `knigdelioglu/tymm` reposunda yeni bir ders veya sınıf kademesi için canonical bilgi tabanı, coverage/gap analizi, production contract, index, resolver, runtime ve P0 gate kurulumu yapmak için kullanılır.

## Kaynak durumuna göre doğru akış

Resmî öğretim programı **ve resmî ders kitabı birlikte mevcutsa** bu tam bootstrap akışını kullan.

Resmî öğretim programı mevcut fakat ders kitabı henüz yayımlanmadı / sağlanmadıysa:

`@docs/yalniz-ogretim-programi-bootstrap-promptu.md`

kullan. Kitap yokluğu gap değildir; lifecycle `CURRICULUM_ONLY_AWAITING_TEXTBOOK` kalır.

Daha önce curriculum-only kurulmuş sınıfın resmî ders kitabı sonradan geldiyse:

`@docs/ders-kitabi-geldiginde-tamamlama-promptu.md`

kullan.

## Zorunlu canonical invariant

İşe başlamadan önce mutlaka:

`@docs/canonical-process-component-inheritance.md`

oku.

Tema/ünite sayfasında süreç bileşeninin tekrar edilmemesi effective süreç bileşeni olmadığı anlamına gelmez. İlgili dersin resmî programında shared/roof hiyerarşi varsa:

```text
verified THEME_EXPLICIT varsa
    effective = THEME_EXPLICIT
aksi halde shared normative ROOF varsa
    effective = ROOF_INHERITED
aksi halde SOURCE_VERIFIED_NONE varsa
    effective = []
aksi halde
    FAIL / REVIEW_REQUIRED
```

Başka sınıfın tema verisi inheritance kaynağı olamaz. Verified theme specialization ile roof set merge edilmez.

## Uygulanacak prompt

```text
knigdelioglu/tymm reposunda <DERS/SINIF> için yeniden kullanılabilir bilgi mimarisini uygula.

Önce:
@docs/canonical-process-component-inheritance.md
@docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md
ve mevcut shared engine/gate kodlarını incele.

Mevcut sınıfları İÇERİK KAYNAĞI olarak kullanma.
Bunlar yalnız mimari, şema, test ve davranış referansıdır.
Yeni ders/sınıfın canonical bilgisi yalnız o ders/sınıfa ait resmî program,
resmî ders kitabı ve diğer resmî kaynaklardan çıkarılacak.

1. Resmî kaynakları doğrula ve source manifest oluştur.

2. Curriculum map'i çıkarırken tema sayfaları ile programın ortak/çatı bölümünü ayrı denetle.
   Parent outcome için shared process-component hierarchy varsa canonical roof katmanını kur/yeniden kullan.
   Tema sayfasında subordinate kod görünmemesini `[] = no components` diye yorumlama.

3. Her outcome için effective process-component resolution originini kaydet:
   THEME_EXPLICIT | ROOF_INHERITED | SOURCE_VERIFIED_NONE | UNRESOLVED.

4. Tema-spesifik explicit süreç bileşeni varsa roof'a üstün gelir.
   Explicit set ile roof set merge edilmez.
   Resmî theme specialization'ın aynı subordinate kodu farklı bağlamsal ifadeyle kullanması tek başına conflict değildir.

5. Curriculum validationda en az şu metrikleri zorunlu tut:
   - total outcomes
   - outcomes_with_roof_components
   - explicit_component_outcomes
   - inherited_component_outcomes
   - verified_no_component_outcomes
   - unresolved_component_outcomes
   - inheritance_missing_count
   - structural_error_count.

   inheritance_missing_count > 0 veya unresolved > 0 ise PASS/FROZEN verme.

6. Kaynakta yayımlanmayan outcome/process alt kodlarını veya tema-spesifik metni uydurma.
   Başka grade'in theme kayıtlarını canonical içerik olarak kopyalama.

7. Ders kitabını section/activity/form düzeyinde yapılandır.

8. Her outcome için ayrı ayrı:
   need → textbook coverage → gap → resource decision
   zincirini kur.

9. COVERED / PARTIALLY_COVERED / NOT_COVERED ayrımını kanıta dayalı yap.

10. Bir resmî değerlendirme aracı/linki varsa fakat yapısı görülemiyorsa COVERED sayma.
    UNRESOLVED ≠ COVERED.

11. Cross-theme consolidation yap. Gap instance ile fiziksel artifact'ı eşitleme.

12. Production kararında:

    verified_resource_gap_count > 0
    → ARTIFACT_PRODUCING

    verified_resource_gap_count = 0
    VE unresolved_assessment_target_count = 0
    → REUSE_ONLY_NO_NEW_ARTIFACTS

    verified_resource_gap_count = 0
    VE unresolved_assessment_target_count > 0
    → PARITY_REVIEW_BLOCKED

13. PARITY_REVIEW_BLOCKED durumunda generation fail-closed olsun;
    block reason = UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS.

14. REUSE_ONLY yalnız bütün scoped normatif ihtiyaçlar yapısal olarak doğrulandığında verilebilir.

15. Canonical JSON/MD source of truth olsun. knowledge.sqlite ve runtime SQLite yalnız derived/rebuildable projection olsun.

16. Shared engine kullan. Ders/sınıfa özel hard-code yerine generic çözüm tercih et.

17. P0 gate zorunlu olarak şunları içersin:
    - source/canonical validation
    - shared roof/process-component inheritance validation
    - production schema
    - fresh index rebuild
    - duplicate check
    - ambiguity/stale/conflict fail-closed
    - generation authorization
    - runtime build/validation.

18. Canonical metadata, shared roof catalog veya resolution contract değişirse index/runtime yeniden build edilmeden PASS verme.

19. CI'da derived çıktı stale ise yayınlama.

20. Geçici extraction/diagnostic workflowlarını iş sonunda temizle.

Final raporda açıkça ver:
- toplam outcome
- explicit/inherited/verified-none/unresolved process-component outcome sayıları
- inheritance_missing_count
- COVERED / PARTIALLY_COVERED / NOT_COVERED
- confirmed gap
- unresolved normative target
- production mode
- authorized artifact count
- index status
- runtime status
- P0 status
- parity certification status
- gerçek blockerlar.
```

## Kritik ilkeler

`verified_resource_gap_count = 0` tek başına `REUSE_ONLY_NO_NEW_ARTIFACTS` demek değildir.

Aynı şekilde `process_components_verbatim: []` tek başına süreç bileşeni olmadığı anlamına gelmez; effective resolution shared roof invariantına göre yapılmalıdır.
