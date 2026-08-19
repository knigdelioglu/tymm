# Yalnız Öğretim Programı ile Yeni Ders / Sınıf Bootstrap Promptu

Bu prompt, `knigdelioglu/tymm` reposunda **resmî öğretim programı mevcut fakat resmî ders kitabı henüz yayımlanmamış / sağlanmamış** bir ders veya sınıf kademesi için kullanılmalıdır.

Amaç, ders kitabını beklemeden yalnız öğretim programından güvenle üretilebilecek canonical katmanı tamamlamak; kitap yokluğunu yanlışlıkla `NOT_COVERED`, gap veya artifact ihtiyacı olarak yorumlamamaktır.

Kullanırken `<DERS/SINIF>` ve resmî program kaynaklarını değiştirin.

```text
knigdelioglu/tymm reposunda <DERS/SINIF> için yalnız resmî öğretim programına dayalı
curriculum-only canonical kurulumunu yap.

Önce:
@docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md
@docs/yeni-ders-sinif-bootstrap-promptu.md

ve mevcut shared engine/gate yapısını incele.

TDE_9 ve TDE_10'u İÇERİK KAYNAĞI olarak kullanma.
Bunlar yalnız mimari, şema, test ve davranış referansıdır.
Yeni ders/sınıfın canonical curriculum bilgisi yalnız bu ders/sınıfa ait resmî öğretim programından çıkarılacak.

ÖNEMLİ BAĞLAM:
Bu ders/sınıfın resmî ders kitabı henüz yayımlanmadı veya henüz repoya sağlanmadı.
Bu nedenle kitap eksikliği curriculum gap değildir.
Ders kitabı bulunmadığı için textbook coverage, gap analysis, resource production veya artifact kararı verme.

Aşağıdaki kuralları uygula:

1. Resmî öğretim programı kaynaklarını doğrula.
   - source identity
   - sınıf/ders kimliği
   - tema/ünite bütünlüğü
   - sürüm/yıl bilgisi
   - local/remote locator
   - mümkünse fingerprint/hash
   bilgilerini source manifestte kaydet.

2. Curriculum source bundle parçalıysa bütün parçaların tamamlığını doğrula.
   Eksik parça varsa bunu açıkça SOURCE_INCOMPLETE / REVIEW_REQUIRED olarak bırak.
   Eksik bölümü başka sınıftan veya başka kaynaktan tahmin etme.

3. `curriculum_map.json`ı mümkün olan en yüksek kanıt derinliğinde oluştur.
   Resmî kaynakta bulunan alanları verbatim + source locator ile kaydet.

4. En az şu program unsurlarını çıkar ve kaynakta varsa canonical olarak modelle:
   - tema / ünite kimliği ve adı
   - süre / ders saati
   - öğrenme çıktıları / outcomes
   - süreç bileşenleri
   - alan becerileri
   - kavramsal beceriler
   - eğilimler
   - sosyal-duygusal öğrenme becerileri
   - değerler
   - okuryazarlık becerileri
   - disiplinler arası ilişkiler
   - beceriler arası ilişkiler
   - içerik çerçevesi
   - anahtar kavramlar
   - öğrenme kanıtları
   - ölçme ve değerlendirme hükümleri
   - farklılaştırma / destek / zenginleştirme hükümleri
   - okul temelli planlama hükümleri
   - programda yer alan diğer normatif öğretim hükümleri.

5. Kaynakta yayımlanmayan alanı uydurma.
   Özellikle başka sınıftaki süreç alt kodlarını, outcome alt ID'lerini veya değerlendirme yapılarını kopyalama.
   Uygun durumda SOURCE_NOT_APPLICABLE / SOURCE_NOT_EXPLICIT / UNRESOLVED gibi açık durum kullan.

6. Her parent outcome için:
   - exact outcome code
   - outcome verbatim
   - theme/unit scope
   - source locator
   - verification status
   kaydet.

7. Programın açık assessment hükümlerini ayrıca canonical olarak yakala.
   Örneğin program belirli bir performans görevi, dereceli puanlama anahtarı, gözlem, öz değerlendirme veya başka bir değerlendirme yolu istiyorsa bunu kaydet.
   Ancak ders kitabı olmadığı için bunun kitapta karşılanıp karşılanmadığına karar verme.

8. Curriculum-only aşamada `needs.json` oluşturulacaksa yalnız PROGRAMDAN türeyen instructional requirement/need katmanı oluştur.
   Textbook coverage veya resource decision sonucu ekleme.
   Need kayıtlarını mümkün olduğunca outcome-level tut.

9. Ders kitabı bulunmadığı için aşağıdaki dosya/kararları TAMAMLANMIŞ gibi üretme:
   - textbook_map.json
   - textbook_forms_index.json
   - textbook coverage
   - alignment final kararları
   - gap_analysis final kararları
   - resource_plan production kararları
   - cross-theme gap consolidation
   - production artifact registry
   - REUSE_ONLY kararı
   - ARTIFACT_PRODUCING kararı.

10. Kitap yokluğunu kesinlikle şu şekilde yorumlama:
    - NOT_COVERED
    - verified gap
    - missing textbook resource
    - artifact required
    - generation required.

    Resmî kitap henüz mevcut değilse bu yalnız bir SOURCE LIFECYCLE durumudur.

11. Ders/sınıfın aşama durumunu açıkça:

    CURRICULUM_ONLY_AWAITING_TEXTBOOK

    olarak kaydet/raporla.

    Bu durum:
    - curriculum canonical katmanı hazır,
    - textbook analizi henüz başlamadı,
    - coverage/gap henüz hesaplanmadı,
    - production kararı henüz verilmedi
    anlamına gelir.

12. `CURRICULUM_ONLY_AWAITING_TEXTBOOK` durumunu:
    - `REUSE_ONLY_NO_NEW_ARTIFACTS`
    - `PARITY_REVIEW_BLOCKED`
    - `ARTIFACT_PRODUCING`
    durumlarından biriymiş gibi göstermeme.

13. Eğer mevcut production schema bu curriculum-only lifecycle durumunu doğrudan desteklemiyorsa,
    sırf P0 PASS almak için production manifest veya sahte textbook/gap kayıtları oluşturma.
    Curriculum-only validation ayrı tutulmalı.

14. Bu aşamada yalnız uygulanabilir testleri çalıştır:
    - source identity/completeness
    - curriculum schema
    - unique outcome IDs / scope safety
    - verbatim/source locator completeness
    - broken canonical references
    - duplicate canonical key kontrolü
    - sentetik alt kod / sentetik canonical fact kontrolü.

15. Ders kitabı gerektiren full P0, textbook runtime, alignment/gap ve production gate'lerini bu aşamada zorla çalıştırma.
    Bunları `DEFERRED_UNTIL_OFFICIAL_TEXTBOOK_AVAILABLE` olarak raporla.

16. Curriculum canonical verisini ileride tekrar kullanılabilecek şekilde freeze et.
    Ancak source fingerprint değişirse kitap aşamasına geçmeden önce curriculum revalidation yap.

17. Canonical JSON/MD source of truth olsun.
    Curriculum-only aşamada derived index/runtime kurulabiliyorsa yalnız desteklenen ve anlamlı kısmı üret;
    sırf tam course runtime bekleniyor diye placeholder textbook verisi ekleme.

18. TDE_9 ve TDE_10 shared engine/regression davranışlarını bozma.
    Yeni curriculum-only lifecycle ihtiyacı generic olarak çözülebiliyorsa shared çözüm tercih et.

19. Geçici extraction/diagnostic workflow'ları kullanılırsa iş sonunda temizle.

Final raporda açıkça şunları ver:
- course_id / sınıf / ders
- resmî program source status
- curriculum source completeness
- tema/ünite sayısı
- toplam outcome sayısı
- verbatim/locator validation status
- explicit process component durumu
- assessment requirement sayısı / özeti
- curriculum validation status
- textbook status = NOT_AVAILABLE / AWAITING_OFFICIAL_TEXTBOOK
- coverage status = NOT_EVALUATED
- gap status = NOT_EVALUATED
- production status = NOT_EVALUATED
- lifecycle status = CURRICULUM_ONLY_AWAITING_TEXTBOOK
- deferred aşamalar
- varsa gerçek curriculum blocker'ları.

En kritik kural:
Ders kitabının henüz yayımlanmamış olması bir curriculum gap değildir ve materyal üretme gerekçesi olamaz.
```

## Kısa kullanım örneği — 11. sınıf TDE

```text
knigdelioglu/tymm reposunda 11. Sınıf Türk Dili ve Edebiyatı için
@docs/yalniz-ogretim-programi-bootstrap-promptu.md kurallarını uygula.
Resmî öğretim programını canonical kaynak olarak kullan.
11. sınıf resmî ders kitabı henüz yayımlanmadığı için textbook/alignment/gap/production aşamalarını ertele.
```

## Kısa kullanım örneği — 12. sınıf TDE

```text
knigdelioglu/tymm reposunda 12. Sınıf Türk Dili ve Edebiyatı için
@docs/yalniz-ogretim-programi-bootstrap-promptu.md kurallarını uygula.
Resmî öğretim programını canonical kaynak olarak kullan.
12. sınıf resmî ders kitabı henüz yayımlanmadığı için textbook/alignment/gap/production aşamalarını ertele.
```

## Beklenen ara durum

```text
OFFICIAL CURRICULUM
        ↓
SOURCE MANIFEST
        ↓
CURRICULUM MAP
        ↓
CURRICULUM VALIDATION / FREEZE
        ↓
CURRICULUM_ONLY_AWAITING_TEXTBOOK
        │
        └── textbook yayımlandığında ikinci aşama promptuna geç
```
