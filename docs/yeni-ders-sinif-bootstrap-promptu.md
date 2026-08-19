# Yeni Ders / Sınıf Bootstrap Promptu

Bu prompt, `knigdelioglu/tymm` reposunda yeni bir ders veya sınıf kademesi için TDE_9 ve TDE_10 ile aynı doğrulama derinliğinde canonical bilgi tabanı, coverage/gap analizi, production contract, index, resolver, runtime ve P0 gate kurulumu yapmak için kullanılmalıdır.

## Kaynak durumuna göre doğru promptu seç

Resmî öğretim programı **ve resmî ders kitabı birlikte mevcutsa** aşağıdaki tam bootstrap promptunu kullan.

Resmî öğretim programı mevcut fakat ders kitabı henüz yayımlanmadı / sağlanmadıysa:

`@docs/yalniz-ogretim-programi-bootstrap-promptu.md`

kullanılmalıdır. Bu durumda kitap yokluğu gap sayılmaz; course `CURRICULUM_ONLY_AWAITING_TEXTBOOK` durumunda bırakılır.

Daha önce curriculum-only kurulmuş bir ders/sınıfın resmî ders kitabı sonradan geldiyse:

`@docs/ders-kitabi-geldiginde-tamamlama-promptu.md`

kullanılmalıdır. Bu ikinci aşama textbook → alignment → gap → production → index → runtime → P0 zincirini tamamlar.

Kullanırken `<DERS/SINIF>` ve resmî kaynak bilgilerini değiştirin.

```text
knigdelioglu/tymm reposunda <DERS/SINIF> için TDE_9 ve TDE_10'da kurduğumuz
yeniden kullanılabilir bilgi mimarisini uygula.

Önce:
@docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md
dosyasını ve mevcut shared engine/gate kodlarını incele.

TDE_9 ve TDE_10'u İÇERİK KAYNAĞI olarak kullanma.
Bunlar yalnız mimari, şema, test ve davranış referansıdır.
Yeni ders/sınıfın canonical bilgisi yalnız o ders/sınıfa ait resmî program,
resmî ders kitabı ve diğer resmî kaynaklardan çıkarılacak.

Aşağıdaki kuralları eksiksiz uygula:

1. Önce resmî kaynakları doğrula ve source manifest oluştur.
2. Curriculum map'i çıkar. Kaynakta yayımlanmayan outcome/process alt kodlarını uydurma.
3. Ders kitabını section/activity/form düzeyinde yapılandır.
4. Her outcome için ayrı ayrı:
   need → textbook coverage → gap → resource decision
   zincirini kur.
5. COVERED / PARTIALLY_COVERED / NOT_COVERED ayrımını kanıta dayalı yap.
6. Bir resmî değerlendirme aracı/linki varsa fakat iç yapısı görülemiyorsa
   bunu COVERED sayma. UNRESOLVED ≠ COVERED.
7. Cross-theme consolidation yap.
   Gap instance ile fiziksel artifact'ı birbirine eşitleme.
8. Production kararında şu kural zorunlu:

   verified_resource_gap_count > 0
   → ARTIFACT_PRODUCING

   verified_resource_gap_count = 0
   VE unresolved_assessment_target_count = 0
   → REUSE_ONLY_NO_NEW_ARTIFACTS

   verified_resource_gap_count = 0
   VE unresolved_assessment_target_count > 0
   → PARITY_REVIEW_BLOCKED

9. PARITY_REVIEW_BLOCKED durumunda:
   - production_queue boş olabilir,
   - yeni artifact üretme,
   - generation fail-closed olsun,
   - block reason = UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS,
   - bunu reuse-only / tam parity olarak raporlama.

10. REUSE_ONLY yalnız bütün scoped normatif ihtiyaçlar yapısal olarak doğrulandığında verilebilir.
11. Canonical JSON/MD source of truth olsun. knowledge.sqlite ve runtime SQLite yalnız derived/rebuildable projection olsun.
12. Shared engine'i kullan. Ders/sınıfa özel mantık yerine mümkün olduğunca generic çözüm üret.
13. P0 gate'te source/canonical validation, production schema, fresh index rebuild, duplicate check, ambiguity/stale/conflict fail-closed, generation authorization ve runtime build/validation kontrolleri zorunlu olsun.
14. TDE_9 regresyonunu çalıştır: 7 gap instance → 3 canonical artifact davranışı korunmalı.
15. TDE_10 regresyonunu çalıştır: PARITY_REVIEW_BLOCKED ve unresolved assessment target davranışı korunmalı.
16. Canonical metadata değişirse index/runtime final metadata üzerinden yeniden build edilmeden PASS verme.
17. CI workflow'larında eşzamanlı push/rebase sorunlarına karşı güvenli yayınlama kullan; derived çıktı stale ise yayınlama.
18. Geçici extraction/diagnostic workflow'larını iş sonunda temizle; yalnız kalıcı generic workflow'ları bırak.

Süreci tamamlamak için veri, gap, artifact, rubric tipi, outcome alt kodu veya değerlendirme yapısı tahmin etme.

Final doğrulamadan önce bütün canonical analiz ve kurulum adımlarını tamamla; ardından testleri çalıştır ve çıkan teknik hataları gider.

Final raporda açıkça şunları ver:
- toplam outcome
- COVERED
- PARTIALLY_COVERED
- NOT_COVERED
- confirmed gap
- unresolved normative target
- production mode
- authorized artifact count
- index status
- runtime status
- P0 status
- parity certification status
- varsa gerçek dış blocker'lar
```

## Kısa kullanım örneği

```text
knigdelioglu/tymm reposunda 11. Sınıf Türk Dili ve Edebiyatı için
@docs/yeni-ders-sinif-bootstrap-promptu.md kurallarını uygula.
Resmî program ve ders kitabı kaynaklarını yalnız bu sınıfa ait kaynaklardan kullan.
```

## Kritik ilke

`verified_resource_gap_count = 0` tek başına `REUSE_ONLY_NO_NEW_ARTIFACTS` demek değildir. Normatif bir assessment/support hedefi yapısal olarak doğrulanmamışsa sonuç `PARITY_REVIEW_BLOCKED` kalmalı ve generation fail-closed kapanmalıdır.
