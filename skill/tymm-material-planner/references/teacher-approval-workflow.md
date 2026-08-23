# Teacher Approval Workflow

Bu akış, Artifact Generation Engine V1'in `generation != approval` ilkesini korurken öğretmen onayını temiz checkout'larda yeniden üretilebilir hâle getirir.

## Temel ilke

- `REVIEW.md` insan-okunur inceleme görünümüdür; lifecycle kaynağı değildir.
- Öğretmen onayı yalnız açık bir karar sonrasında kaydedilir.
- Kalıcı onay kaydı `courses/<COURSE_ID>/production/teacher_approvals/<ARTIFACT_ID>.json` altında tutulur.
- Kayıt `generation_context_hash` ile canonical generation context'e bağlanır.
- Kaynak/registry/contract değişirse hash değişir ve eski onay otomatik olarak `TEACHER_APPROVAL_CONTEXT_STALE` ile reddedilir.

## Komutlar

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

## Generator sırası

Pilot konuşma rubriği onaylandıktan sonra:

```bash
python skill/tymm-material-planner/scripts/artifact_generator.py \
  generate --artifact-id TDE9_YAZMA_RUBRIC
```

Bu yeni artifact kendi sözleşmesi gereği yine `REVIEW_REQUIRED` olarak doğar. Pilot onayı sonraki artifact'ın kendiliğinden öğretmen tarafından onaylandığı anlamına gelmez.

## Güvenlik/kalite kuralları

1. `Devam`, `üret`, `generate` gibi genel komutlar öğretmen onayı olarak kaydedilmez.
2. Reviewer alanı boş bırakılamaz.
3. Approval record elle başka artifact kimliğine taşınamaz.
4. Context hash değişmiş approval record yeniden kullanılamaz.
5. `REVIEW.md` veya lesson-plan metadata üzerinde yalnız metinsel `APPROVED` yazmak lifecycle onayı sayılmaz.
6. Üretim sırası gate'i kaldırılmaz; onay kaydı gate'i kanıtlı ve yeniden üretilebilir biçimde açmak için kullanılır.
