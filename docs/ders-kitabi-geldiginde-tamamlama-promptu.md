# Ders Kitabı Geldiğinde Tamamlama Promptu

Bu prompt, `knigdelioglu/tymm` reposunda daha önce **yalnız öğretim programı ile `CURRICULUM_ONLY_AWAITING_TEXTBOOK` durumuna kadar kurulmuş** bir ders veya sınıf kademesinin resmî ders kitabı yayımlandığında kullanılmalıdır.

Amaç; mevcut curriculum canonical katmanını korumak, yeni resmî ders kitabını doğrulamak ve bundan sonra textbook → forms → needs → alignment → gap → resource plan → cross-theme consolidation → production → index → runtime → P0 zincirini tamamlamaktır.

Kullanırken `<DERS/SINIF>` ve resmî ders kitabı kaynağını değiştirin.

```text
knigdelioglu/tymm reposunda <DERS/SINIF> için daha önce yalnız öğretim programıyla kurduğumuz
CURRICULUM_ONLY_AWAITING_TEXTBOOK durumunu devam ettir.

Şimdi bu ders/sınıfın resmî ders kitabı yayımlandı / repoya sağlandı.

Önce:
@docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md
@docs/yeni-ders-sinif-bootstrap-promptu.md
@docs/yalniz-ogretim-programi-bootstrap-promptu.md

ve bu course için mevcut source_manifest, curriculum_map, curriculum validation/freeze kayıtlarını incele.

TDE_9 ve TDE_10'u İÇERİK KAYNAĞI olarak kullanma.
Bunlar yalnız mimari, şema, test ve davranış referansıdır.
Bu ders/sınıfın textbook ve alignment bilgisi yalnız kendi resmî ders kitabı ve kendi resmî öğretim programından çıkarılacak.

Aşağıdaki kuralları uygula:

1. Önce mevcut curriculum canonical katmanının hâlâ geçerli olduğunu doğrula.
   - curriculum source fingerprint / source identity değişmiş mi?
   - program sürümü/yılı değişmiş mi?
   - theme/unit/outcome yapısında değişiklik var mı?

2. Curriculum source değişmemişse mevcut frozen curriculum_map'i yeniden kullan.
   Gereksiz yere sıfırdan üretme.
   Kaynak değişmişse önce curriculum revalidation yap ve yalnız sonra textbook aşamasına geç.

3. Yeni resmî ders kitabını doğrula ve source manifest'e ekle/güncelle:
   - source identity
   - ders/sınıf uyumu
   - baskı/yıl/ISBN/TTKB bilgisi varsa
   - local file path veya exact official URL
   - fingerprint/hash
   - verification status.

4. Resmî ders kitabı primary analysis source olsun.
   Başka sınıf kitabı, üçüncü taraf PDF veya benzer içerik sessiz ikame olarak kullanılmasın.

5. `textbook_map.json`ı gerçek kitap yapısına göre section/activity düzeyinde oluştur.
   Her activity mümkün olduğunca şunları taşısın:
   - activity_id
   - exact title/label veya NOT_SEPARATELY_TITLED
   - section/theme
   - printed page
   - PDF page
   - source locator
   - detailed student_action
   - expected_product_or_evidence
   - related outcome IDs
   - related forms
   - verification status.

6. Genel ve yüzeysel activity özetleriyle yetinme.
   Öğrencinin gerçekten ne yaptığı ve hangi evidence'ı ürettiği görünür olmalı.

7. `textbook_forms_index.json`ı oluştur/güncelle.
   Formları başlığa göre değil gerçek yapısına göre sınıflandır.

8. Bir formun adı “Dereceli Puanlama Anahtarı”, “Rubrik” vb. olsa bile iç yapısı görülmeden `analytic_rubric` deme.
   Criterion × level descriptors gerçekten doğrulanmalı.

9. Kitaptaki QR/EBA veya diğer resmî dış assessment linklerini ayrı provenance ile kaydet.
   Link resmî olsa bile hedef yapısı görülmüyorsa:
   UNRESOLVED ≠ COVERED.

10. Daha önce curriculum-only aşamada çıkarılmış instructional need/requirement kayıtlarını yeniden kullan ve gerekiyorsa outcome-level olarak tamamla.
    Her outcome için ayrı izlenebilir zincir kur:

    official curriculum requirement
    → instructional need
    → expected evidence
    → textbook activity
    → textbook form / assessment path
    → coverage decision
    → remaining gap
    → resource decision.

11. Coverage enum yalnız şu üç değer olsun:
    - COVERED
    - PARTIALLY_COVERED
    - NOT_COVERED

12. COVERED kararı yalnız konu kitapta geçti diye verilmesin.
    Bir requirement'ın COVERED olması için gerekli öğrenci eylemi, expected evidence ve gerekiyorsa assessment/feedback yolu gerçekten desteklenmiş olmalı.

13. Normatif bir assessment hedefi/linki var fakat hedef yapısı doğrulanamıyorsa ilgili outcome'u COVERED yapma.
    Uygun durumda PARTIALLY_COVERED + REVIEW_REQUIRED/UNRESOLVED olarak bırak.

14. `gap_analysis.json`ı kanıttan türet.
    Kitapta neyin eksik olduğu exact locator ve program requirement ile açıklanmalı.
    Gap ID ile fiziksel artifact ID'yi aynı şey kabul etme.

15. `resource_plan.json`ı coverage kararından sonra üret.
    Resource plan alignment kararını önceden varsaymasın.

16. Priority ve production decision kuralları TDE_9/TDE_10 shared standardıyla uyumlu olsun:
    - REQUIRED
    - RECOMMENDED
    - OPTIONAL
    - NOT_NEEDED

17. Dört tema/ünite veya tüm course çapında gerçek cross-theme consolidation yap.
    Yalnız gap sayısı toplama.
    Ortak assessment/support ihtiyacını karşılaştır ve tekrar eden gap instance'ları reusable canonical artifactlara konsolide et.

18. Production kararında şu üç-durumlu fail-closed kural zorunlu:

    verified_resource_gap_count > 0
    → ARTIFACT_PRODUCING

    verified_resource_gap_count = 0
    VE unresolved_assessment_target_count = 0
    → REUSE_ONLY_NO_NEW_ARTIFACTS

    verified_resource_gap_count = 0
    VE unresolved_assessment_target_count > 0
    → PARITY_REVIEW_BLOCKED

19. `PARITY_REVIEW_BLOCKED` durumunda:
    - production_queue boş olabilir,
    - artifact üretme,
    - generation authorization false olsun,
    - block reason = UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS,
    - bunu tam parity/reuse-only olarak raporlama.

20. `REUSE_ONLY_NO_NEW_ARTIFACTS` yalnız bütün scoped normatif ihtiyaçlar yapısal olarak doğrulanıp unresolved hedef sayısı sıfır olduğunda verilebilir.

21. `ARTIFACT_PRODUCING` yalnız doğrulanmış gerçek gap varsa açılabilir.
    Sahte gap/artifact oluşturma.

22. Production manifest, assessment artifact registry ve assessment design contract'ı gerçek cross-theme sonucundan türet.

23. Canonical JSON/MD source of truth olsun.
    knowledge.sqlite ve runtime SQLite yalnız derived/rebuildable projection olsun.

24. Final canonical metadata tamamlandıktan sonra index'i sıfırdan rebuild et.
    Duplicate canonical key, stale fingerprint ve source drift kontrollerini çalıştır.

25. Resolver testlerinde en az şunları doğrula:
    - exact outcome lookup
    - theme/unit scoped lookup
    - ambiguity fail-closed
    - stale fail-closed
    - knowledge conflict fail-closed
    - gap query
    - assessment/form query
    - production/generation authorization.

26. Runtime projection'ı final canonical metadata üzerinden yeniden oluştur.
    Placeholder textbook verisi bırakma.

27. Full P0 gate'i ancak textbook + alignment + gap + production zinciri tamamlandıktan sonra çalıştır.

28. TDE_9 regresyonunu çalıştır:
    7 gap instance → 3 canonical artifact davranışı korunmalı.

29. TDE_10 regresyonunu çalıştır:
    PARITY_REVIEW_BLOCKED / unresolved assessment target fail-closed davranışı korunmalı.

30. CI workflow'larında eşzamanlı push/rebase durumunda stale derived çıktı yayınlama.
    Canonical/shared input değişmişse eski koşunun çıktısını push etme.

31. Geçici extraction/diagnostic workflow'larını iş sonunda temizle.
    Kalıcı shared/generic workflow'ları bırak.

32. Curriculum-only lifecycle durumunu iş sonunda kaldır/güncelle:
    `CURRICULUM_ONLY_AWAITING_TEXTBOOK` artık final course durumu olmamalı.
    Bunun yerine gerçek sonuçlardan biri seçilmeli:
    - ARTIFACT_PRODUCING
    - REUSE_ONLY_NO_NEW_ARTIFACTS
    - PARITY_REVIEW_BLOCKED.

Final raporda açıkça şunları ver:
- curriculum source status
- textbook source status
- tema/ünite sayısı
- toplam outcome
- textbook section count
- textbook activity count
- forms count
- COVERED
- PARTIALLY_COVERED
- NOT_COVERED
- confirmed gap count
- unresolved normative target count
- cross-theme gap cluster count
- canonical artifact count
- production mode
- generation authorization status/reason
- knowledge index status
- runtime status
- P0 status
- TDE_9 regression status
- TDE_10 regression status
- parity certification status
- varsa gerçek dış blocker'lar.

En kritik kural:
Önceden curriculum-only hazırlanmış olması, kitabın programı karşıladığı anlamına gelmez.
Kitap geldikten sonra coverage/gap/production kararlarını sıfır varsayımla, doğrudan program requirement + gerçek textbook evidence üzerinden üret.
```

## Kısa kullanım örneği — 11. sınıf TDE kitabı yayımlandığında

```text
11. Sınıf Türk Dili ve Edebiyatı resmî ders kitabını repoya ekledim.
knigdelioglu/tymm reposunda
@docs/ders-kitabi-geldiginde-tamamlama-promptu.md kurallarını uygula.
Mevcut TDE_11 curriculum-only canonical katmanını koru; resmî kitabı doğrula ve textbook/alignment/gap/production/index/runtime/P0 aşamalarını tamamla.
```

## Kısa kullanım örneği — 12. sınıf TDE kitabı yayımlandığında

```text
12. Sınıf Türk Dili ve Edebiyatı resmî ders kitabını repoya ekledim.
knigdelioglu/tymm reposunda
@docs/ders-kitabi-geldiginde-tamamlama-promptu.md kurallarını uygula.
Mevcut TDE_12 curriculum-only canonical katmanını koru; resmî kitabı doğrula ve textbook/alignment/gap/production/index/runtime/P0 aşamalarını tamamla.
```

## İki aşamalı lifecycle

```text
AŞAMA 1
OFFICIAL CURRICULUM
      ↓
CURRICULUM CANONICAL / FREEZE
      ↓
CURRICULUM_ONLY_AWAITING_TEXTBOOK

             kitap yayımlanır
                    ↓

AŞAMA 2
OFFICIAL TEXTBOOK
      ↓
TEXTBOOK MAP + FORMS
      ↓
OUTCOME-LEVEL ALIGNMENT
      ↓
GAP + RESOURCE PLAN
      ↓
CROSS-THEME CONSOLIDATION
      ↓
┌──────────────────────────────┬───────────────────────────────┬─────────────────────────────┐
│ ARTIFACT_PRODUCING           │ REUSE_ONLY_NO_NEW_ARTIFACTS   │ PARITY_REVIEW_BLOCKED       │
│ verified gap > 0             │ gap=0 / unresolved=0          │ gap=0 / unresolved>0        │
└──────────────────────────────┴───────────────────────────────┴─────────────────────────────┘
      ↓
INDEX + RESOLVER + RUNTIME + P0
```
