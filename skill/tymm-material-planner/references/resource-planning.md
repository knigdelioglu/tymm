# Instructional resource planning

## İçindekiler

- Kaynak işlevi
- Öncelik
- Üretim kararı
- Planlama algoritması
- Öğretmene gösterilecek plan

## Kaynak işlevi

'resource_type' dosya formatı değil, öğretimsel işlevdir. Bir işlev daha sonra çalışma kâğıdı, kart, sunum, PDF, dijital sayfa veya öğretmen eki olarak üretilebilir.

Kullanılabilecek işlevler:

- 'learning_input_or_representation'
- 'scaffold_or_concept_support'
- 'guided_practice'
- 'student_production_task'
- 'feedback_support'
- 'assessment_support'
- 'differentiation_support'
- 'enrichment'
- 'teacher_implementation_support'
- 'accessibility_support'
- 'safety_support'
- 'external_content'

## instructional_resource_plan alanları

- 'resource_plan_id'
- 'need_id'
- 'resource_type'
- 'target_outcomes'
- 'purpose'
- 'expected_student_evidence'
- 'priority'
- 'rationale'
- 'textbook_coverage'
- 'reuse_existing_resource'
- 'production_decision'
- 'external_source_needed'
- 'teacher_review_required'

## Öncelik

Yalnız şu değerleri kullan:

- 'REQUIRED': hedefin beklenen kanıtla gerçekleşmesi için gerekli.
- 'RECOMMENDED': öğrenmeyi veya uygulamayı belirgin biçimde güçlendirir.
- 'OPTIONAL': anlamlı bir genişletme; temel hedef için zorunlu değil.
- 'NOT_NEEDED': bu hedef ve bağlam için üretme/kullanma.

Priority, belge türüne değil ihtiyaç ve kanıta göre verilir.

## Üretim kararı

Yalnız şu değerleri kullan:

- 'REUSE_TEXTBOOK'
- 'REUSE_WITH_TEACHER_GUIDE'
- 'ADAPT_TEXTBOOK_ACTIVITY'
- 'GENERATE'
- 'GENERATE_ASSESSMENT_SUPPORT'
- 'GENERATE_DIFFERENTIATION'
- 'GENERATE_ENRICHMENT'
- 'NO_ACTION'

Karar mantığı:

1. Kitapta yeterli kaynak ve öğrenci kanıtı varsa 'REUSE_TEXTBOOK'.
2. Kaynak yeterli, fakat uygulama/geri bildirim/izleme eksikse 'REUSE_WITH_TEACHER_GUIDE'.
3. Küçük, açık ve telif açısından güvenli uyarlama yeterliyse 'ADAPT_TEXTBOOK_ACTIVITY'.
4. Gerekli kaynak eksikse 'GENERATE'.
5. Yalnız ölçme, destek veya zenginleştirme eksikse ilgili özel 'GENERATE_*' kararını kullan.
6. Gerekçe yoksa 'NO_ACTION'.

## Planlama algoritması

1. Her instructional need için beklenen kanıtı yaz.
2. Bu kanıtı üretmek için gereken kaynak işlevlerini aday olarak çıkar.
3. Kitapta işlevi karşılayan etkinlik, metin, araç veya rehber olup olmadığını locator'la kontrol et.
4. Kitap karşılığının yalnız konuya değinip değinmediğini değil, beklenen öğrenci eylemini sağlayıp sağlamadığını değerlendir.
5. Her aday kaynağa priority ve production_decision ata.
6. Aynı işlevi tekrarlayan kaynakları birleştir.
7. 'REQUIRED' ve 'RECOMMENDED' planı üret; 'OPTIONAL' kaynakları ayrı göster.
8. Üretimden önce öğretmene planı göster, ancak her madde için ayrı onay isteme.

## Öğretmene gösterilecek plan

ÖĞRETİM KAYNAK PLANI
Hedef: ...
İhtiyaç: ...
Kaynak işlevi: ...
Öncelik: REQUIRED
Kitap karşılığı: s. ... / PARTIALLY_COVERED
Karar: GENERATE_ASSESSMENT_SUPPORT
Beklenen kanıt: ...
Gerekçe: ...

Kullanıcı yalnız “9. sınıf TDE 2. tema için kaynak hazırla” dediğinde bu planı Knowledge Resolver (`scripts/knowledge_resolver.py`) doğrulanmış `resource_plan.json` ve `production_manifest.json` kayıtlarından otomatik olarak çözer; kullanıcıdan belge türü seçmesini beklemez.
