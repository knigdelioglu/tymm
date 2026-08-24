# Yalnız Öğretim Programı ile Yeni Ders / Sınıf Bootstrap Promptu

Bu prompt, `knigdelioglu/tymm` reposunda **resmî öğretim programı mevcut fakat resmî ders kitabı henüz yayımlanmamış / sağlanmamış** bir ders veya sınıf kademesi için kullanılır.

Amaç, ders kitabını beklemeden yalnız öğretim programından güvenle üretilebilecek canonical katmanı tamamlamak; kitap yokluğunu yanlışlıkla `NOT_COVERED`, gap veya artifact ihtiyacı olarak yorumlamamaktır.

## Zorunlu canonical invariantlar

İşe başlamadan önce mutlaka oku:

- `@docs/canonical-process-component-inheritance.md`
- `@docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md`
- `@docs/yeni-ders-sinif-bootstrap-promptu.md`

Özellikle süreç bileşenlerinde şu varsayım yasaktır:

> Tema/ünite sayfasında subordinate süreç maddeleri tekrar yazılmamışsa süreç bileşeni yoktur.

TDE için doğrulanmış çözümleme sırası:

```text
verified THEME_EXPLICIT varsa
    effective = THEME_EXPLICIT
aksi halde shared normative ROOF varsa
    effective = ROOF_INHERITED
aksi halde SOURCE_VERIFIED_NONE varsa
    effective = []
aksi halde
    REVIEW_REQUIRED / FAIL
```

`process_components_verbatim: []` tek başına effective empty anlamına gelemez. Başka sınıfın tema verisi inheritance kaynağı olamaz. Shared roof yalnız ilgili dersin resmî ortak program bölümünden çıkarılır.

## Uygulanacak prompt

```text
knigdelioglu/tymm reposunda <DERS/SINIF> için yalnız resmî öğretim programına dayalı
curriculum-only canonical kurulumunu yap.

Önce:
@docs/canonical-process-component-inheritance.md
@docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md
@docs/yeni-ders-sinif-bootstrap-promptu.md
ve mevcut shared engine/gate yapısını incele.

Başka sınıfları İÇERİK KAYNAĞI olarak kullanma.
Bunlar yalnız mimari, şema, test ve davranış referansı olabilir.
Yeni ders/sınıfın canonical curriculum bilgisi yalnız ilgili resmî öğretim programından çıkarılacak.

1. Resmî öğretim programı kaynaklarını doğrula:
   - source identity
   - ders/sınıf kimliği
   - tema/ünite bütünlüğü
   - sürüm/yıl
   - local/remote locator
   - mümkünse fingerprint/hash.

2. Curriculum source bundle parçalıysa bütün parçaların tamamlığını doğrula.
   Eksik parçayı başka sınıftan tahmin etme; SOURCE_INCOMPLETE / REVIEW_REQUIRED bırak.

3. Programın ortak/çatı bölümünü tema sayfalarından ayrı incele.
   Parent outcome → process component hierarchy varsa bunu canonical shared roof katmanı olarak modelle.
   Tema sayfasında alt maddeler tekrar yazılmaması, roof inheritance'ı ortadan kaldırmaz.

4. Her theme/unit outcome için süreç bileşeni resolution originini açıkça belirle:
   - THEME_EXPLICIT
   - ROOF_INHERITED
   - SOURCE_VERIFIED_NONE
   - UNRESOLVED

5. Verified tema-spesifik süreç bileşeni varsa roof'a göre önceliklidir.
   Theme explicit set ile roof seti sessizce merge etme.
   Aynı subordinate kodun tema bağlamında daha özel resmî ifadeyle kullanılması tek başına conflict değildir.

6. `curriculum_map.json`ı mümkün olan en yüksek kanıt derinliğinde oluştur.
   Resmî kaynakta bulunan alanları verbatim + locator ile kaydet.

7. En az şu unsurları kaynakta varsa canonical olarak modelle:
   - tema/ünite kimliği ve adı
   - süre/ders saati
   - öğrenme çıktıları
   - süreç bileşenleri ve inheritance provenance
   - alan becerileri
   - kavramsal beceriler
   - eğilimler
   - sosyal-duygusal beceriler
   - değerler
   - okuryazarlık becerileri
   - disiplinler arası / beceriler arası ilişkiler
   - içerik çerçevesi
   - anahtar kavramlar
   - öğrenme kanıtları
   - ölçme/değerlendirme hükümleri
   - farklılaştırma/destek/zenginleştirme
   - okul temelli planlama
   - diğer normatif öğretim hükümleri.

8. Kaynakta yayımlanmayan alanı uydurma.
   Başka sınıftaki outcome alt ID'lerini, tema-spesifik process metinlerini veya assessment yapılarını kopyalama.

9. Her parent outcome için:
   - exact code
   - outcome verbatim
   - theme/unit scope
   - source locator
   - verification status
   - process resolution origin
   kaydet.

10. Curriculum validation mutlaka process-component completeness ölçsün:
    - total outcomes
    - outcomes_with_roof_components
    - explicit_component_outcomes
    - inherited_component_outcomes
    - verified_no_component_outcomes
    - unresolved_component_outcomes
    - inheritance_missing_count
    - structural_error_count.

    inheritance_missing_count > 0 veya unresolved_component_outcomes > 0 ise PASS/FROZEN verme.

11. Programın açık assessment hükümlerini canonical olarak yakala; fakat ders kitabı bulunmadığı için textbook coverage kararı verme.

12. `needs.json` oluşturulacaksa yalnız PROGRAMDAN türeyen instructional requirement/need katmanını oluştur.

13. Ders kitabı yokken aşağıdakileri tamamlanmış gibi üretme:
    - textbook_map / textbook_forms_index
    - textbook coverage
    - final alignment/gap
    - production/resource kararları
    - artifact registry
    - REUSE_ONLY / ARTIFACT_PRODUCING kararı.

14. Kitap yokluğunu NOT_COVERED, verified gap, missing resource veya generation required sayma.

15. Lifecycle status:

    CURRICULUM_ONLY_AWAITING_TEXTBOOK

16. Curriculum-only validationda çalıştır:
    - source identity/completeness
    - curriculum schema
    - unique IDs / scope safety
    - verbatim/locator completeness
    - shared roof catalog structure
    - process component inheritance gate
    - broken canonical references
    - duplicate canonical key
    - sentetik canonical fact/subcode kontrolü.

17. Ders kitabı gerektiren full P0/alignment/gap/production aşamalarını
    DEFERRED_UNTIL_OFFICIAL_TEXTBOOK_AVAILABLE olarak raporla.

18. Canonical JSON/MD source of truth olsun. Derived index/runtime yalnız rebuildable projection olsun.

19. Shared/generic çözüm tercih et. TDE_9/TDE_10 gibi mevcut sınıflardan tema içeriği kopyalama.

20. Geçici extraction/diagnostic workflowlarını iş sonunda temizle.

Final raporda açıkça ver:
- course_id / sınıf / ders
- resmî program source status
- source completeness
- tema/ünite sayısı
- toplam outcome
- explicit/inherited/verified-none/unresolved process component outcome sayıları
- inheritance_missing_count
- assessment requirement özeti
- curriculum validation status
- textbook status = AWAITING_OFFICIAL_TEXTBOOK
- coverage/gap/production = NOT_EVALUATED
- lifecycle = CURRICULUM_ONLY_AWAITING_TEXTBOOK
- deferred aşamalar
- gerçek blockerlar.
```

## Kritik ilke

Ders kitabının henüz yayımlanmamış olması curriculum gap değildir. Aynı şekilde tema sayfasında roof süreç bileşenlerinin tekrar edilmemesi de process-component yokluğu değildir.
