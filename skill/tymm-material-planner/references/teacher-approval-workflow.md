# Teacher Approval Workflow

Bu akış, Artifact Generation Engine V1'in `generation != approval` ilkesini korurken öğretmen onayını temiz checkout'larda yeniden üretilebilir hâle getirir.

## Temel ilke

- `REVIEW.md` insan-okunur inceleme görünümüdür; lifecycle kaynağı değildir.
- Öğretmen onayı yalnız açık bir karar sonrasında kaydedilir.
- Kalıcı onay kaydı `courses/<COURSE_ID>/production/teacher_approvals/<ARTIFACT_ID>.json` altında tutulur.
- Kayıt `generation_context_hash` ile canonical generation context'e bağlanır.
- Kaynak/registry/contract değişirse hash değişir ve eski onay otomatik olarak `TEACHER_APPROVAL_CONTEXT_STALE` ile reddedilir.
- Her `teacher_review_required: true` artifact bağımsız onay ister; bir artifact'ın onayı başka artifact'a devredilmez.

## 1. Konuşma rubriği pilot onayı

Durum kontrolü:

```bash
python skill/tymm-material-planner/scripts/teacher_approval.py \
  status --artifact-id TDE9_KONUSMA_RUBRIC
```

Öğretmen açıkça onay verdikten sonra kalıcı kayıt oluşturma:

```bash
python skill/tymm-material-planner/scripts/teacher_approval.py \
  record \
  --artifact-id TDE9_KONUSMA_RUBRIC \
  --reviewer "<öğretmen adı>" \
  --note "Pilot rubrik incelendi ve onaylandı."
```

Kaydı mevcut checkout'taki generated artifact'a uygulama:

```bash
python skill/tymm-material-planner/scripts/teacher_approval.py \
  apply --artifact-id TDE9_KONUSMA_RUBRIC
```

`apply`, gerekli draft artifact'ı canonical generator ile yeniden oluşturur; kayıt güncel context hash ile eşleşiyorsa mevcut `approve_artifact` fonksiyonunu kullanarak lifecycle'ı `APPROVED` yapar.

## 2. Yazma rubriğini üretme ve ayrı onaylama

Konuşma pilotu onaylandıktan sonra order gate açılır ve yazma rubriği üretilebilir:

```bash
python skill/tymm-material-planner/scripts/artifact_generator.py \
  generate --artifact-id TDE9_YAZMA_RUBRIC
```

Bu artifact kendi sözleşmesi gereği `REVIEW_REQUIRED` olarak doğar. Generation/validation, öğretmen onayı değildir ve Tema 2 Yazma P05'i tek başına açmaz.

Yazma rubriği öğretmen tarafından incelenip açıkça onaylandıktan sonra:

```bash
python skill/tymm-material-planner/scripts/teacher_approval.py \
  record \
  --artifact-id TDE9_YAZMA_RUBRIC \
  --reviewer "<öğretmen adı>" \
  --note "Yıllık yazma rubriği incelendi ve onaylandı."
```

Ardından kayıt uygulanabilir:

```bash
python skill/tymm-material-planner/scripts/teacher_approval.py \
  apply --artifact-id TDE9_YAZMA_RUBRIC
```

Temiz checkout'ta iki gate'i denetlemek/uygulamak için:

```bash
python skill/tymm-material-planner/scripts/resume_after_teacher_approval.py preflight
python skill/tymm-material-planner/scripts/resume_after_teacher_approval.py run
```

`run` davranışı:

1. Konuşma rubriği onayı yoksa hiçbir artifact onayı üretmeden bloklanır.
2. Konuşma rubriği onaylıysa yazma rubriğini üretir ve doğrular.
3. Yazma rubriği için açık öğretmen onayı henüz yoksa `AWAITING_WRITING_RUBRIC_TEACHER_APPROVAL` döner; P05 kapalı kalır.
4. Her iki approval kaydı da current ise ikisini checkout'a uygular ve `READY_FOR_T2_WRITING_P05` döner.

## Güvenlik/kalite kuralları

1. `Devam`, `üret`, `generate` gibi genel komutlar öğretmen onayı olarak kaydedilmez.
2. Reviewer alanı boş bırakılamaz.
3. Approval record elle başka artifact kimliğine taşınamaz.
4. Context hash değişmiş approval record yeniden kullanılamaz.
5. `REVIEW.md` veya lesson-plan metadata üzerinde yalnız metinsel `APPROVED` yazmak lifecycle onayı sayılmaz.
6. Üretim sırası gate'i kaldırılmaz; onay kaydı gate'i kanıtlı ve yeniden üretilebilir biçimde açmak için kullanılır.
7. `TDE9_KONUSMA_RUBRIC` onayı yalnız yazma rubriğinin üretilmesini açar; `TDE9_YAZMA_RUBRIC` ayrıca açık öğretmen onayı gerektirir.
