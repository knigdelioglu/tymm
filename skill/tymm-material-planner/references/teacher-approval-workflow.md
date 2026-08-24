# Teacher Approval Workflow

Bu akış, Artifact Generation Engine V1'in `generation != approval` ilkesini korurken öğretmen onayını temiz checkout'larda yeniden üretilebilir ve Git üzerinden denetlenebilir hâle getirir.

## Temel ilke

- `REVIEW.md` öğretmenin fiilen incelediği insan-okunur snapshot'tır; tek başına lifecycle onayı değildir.
- Öğretmen onayı yalnız karar bağlamı açık ve denetlenebilir olduğunda kaydedilir.
- Kalıcı onay kaydı `courses/<COURSE_ID>/production/teacher_approvals/<ARTIFACT_ID>.json` altında tutulur.
- Approval schema `1.3`, onayı şu exact Git-blob kimliklerine bağlar:
  - ilgili `REVIEW.md`,
  - `artifact_generation.py`,
  - `production_manifest.json`,
  - `assessment_artifact_registry.json`,
  - `assessment_design_contract.json`.
- Bu dosyalardan biri değişirse eski onay `INVALID_OR_STALE` olur; hangi eksenin değiştiği ayrı hata koduyla raporlanır.
- Kaynak blob'ları eşleşse dahi `validate_record()` ayrıca `build_generation_context()` çalıştırır; knowledge index/runtime semantik kapısı yine geçilmek zorundadır.
- Her `teacher_review_required: true` artifact bağımsız onay ister; bir artifact'ın onayı başka artifact'a devredilmez.

## 1. Konuşma rubriği pilot onayı

Durum kontrolü:

```bash
python skill/tymm-material-planner/scripts/teacher_approval.py \
  status --artifact-id TDE9_KONUSMA_RUBRIC
```

Öğretmen kararı kaydedilecekse:

```bash
python skill/tymm-material-planner/scripts/teacher_approval.py \
  record \
  --artifact-id TDE9_KONUSMA_RUBRIC \
  --reviewer "<öğretmen adı>" \
  --note "Pilot rubrik incelendi ve onaylandı."
```

Kaydı checkout'taki generated artifact'a uygulama:

```bash
python skill/tymm-material-planner/scripts/teacher_approval.py \
  apply --artifact-id TDE9_KONUSMA_RUBRIC
```

`apply`, önce approval snapshot + canonical source kimliklerini doğrular; ardından güncel generation context'i yeniden kurar, canonical artifact'ı üretir/doğrular ve mevcut `approve_artifact` fonksiyonu üzerinden lifecycle'ı `APPROVED` yapar.

## 2. Yazma rubriğini üretme ve ayrı onaylama

Konuşma pilotu onaylandıktan sonra order gate açılır. Yıllık yazma rubriğinde generic descriptor fallback yerine ölçüte özgü `TDE9_WRITING_OBSERVABLE_4X4_V1` profili kullanılır:

```bash
python skill/tymm-material-planner/scripts/writing_rubric_generation.py
```

Bu komut:

1. canonical `TDE9_YAZMA_RUBRIC` context'ini kurar,
2. dört yıllık çekirdek yazma ölçütünü aynen korur,
3. her ölçüt için dört gözlenebilir performans düzeyi betimleyicisi uygular,
4. artifact'ı canonical validator ile doğrular,
5. `courses/TDE_9/generated/TDE9_YAZMA_RUBRIC/REVIEW.md` snapshot'ını üretir.

Yazma artifact'ı kendi sözleşmesi gereği `REVIEW_REQUIRED` olarak doğar. Generation/validation, öğretmen onayı değildir ve Tema 2 Yazma P05'i tek başına açmaz.

Yazma rubriği incelenip onaylandıktan sonra:

```bash
python skill/tymm-material-planner/scripts/teacher_approval.py \
  record \
  --artifact-id TDE9_YAZMA_RUBRIC \
  --reviewer "<öğretmen adı>" \
  --note "Yıllık yazma rubriği incelendi ve onaylandı."
```

## 3. İki gate'i resume helper ile yürütme

```bash
python skill/tymm-material-planner/scripts/resume_after_teacher_approval.py preflight
python skill/tymm-material-planner/scripts/resume_after_teacher_approval.py run
```

`run` davranışı:

1. Konuşma rubriği onayı yok/stale ise lifecycle değiştirmeden bloklanır.
2. Konuşma rubriği current ise onayı checkout'a uygular.
3. Specialized yıllık yazma rubriğini ve `REVIEW.md` snapshot'ını üretip doğrular.
4. Yazma approval kaydı yok/stale ise `AWAITING_WRITING_RUBRIC_TEACHER_APPROVAL` döner; P05 kapalı kalır.
5. Her iki approval kaydı current ise yazma onayını da uygular ve `READY_FOR_T2_WRITING_P05` döner.

## Güvenlik/kalite kuralları

1. Belirsiz bir `devam`, `üret` veya `generate` komutu tek başına yeni bir öğretmen değerlendirme kararını uydurmak için kullanılamaz; karar bağlamı artifact ve geçilecek gate açısından tek anlamlı olmalıdır.
2. Reviewer alanı boş bırakılamaz.
3. Approval record başka artifact kimliğine taşınamaz.
4. Reviewed `REVIEW.md` snapshot'ı değişmişse onay yeniden kullanılamaz.
5. Generator implementation değişmişse onay yeniden kullanılamaz.
6. Manifest, registry veya assessment contract değişmişse onay yeniden kullanılamaz.
7. `REVIEW.md` ya da lesson-plan metadata içine yalnız metinsel `APPROVED` yazmak lifecycle onayı sayılmaz.
8. Üretim sırası gate'i kaldırılmaz; approval record gate'i kanıtlı ve yeniden üretilebilir biçimde açar.
9. `TDE9_KONUSMA_RUBRIC` onayı yalnız yazma rubriğinin üretim kapısını açar; `TDE9_YAZMA_RUBRIC` ayrıca bağımsız öğretmen onayı gerektirir.
