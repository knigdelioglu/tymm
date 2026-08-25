# P10 — CI / Finalizer Sertleştirme Durumu

## Sonuç

P10'un **kod ve workflow düzeyindeki finalizer güvenliği tamamlandı**. Kalan tek açık, GitHub repository ayarında `main` için branch protection / ruleset enforcement'ın etkin olmamasıdır.

Bu nedenle `YELLOW-CI-FINALIZER` tek parça `CLOSED` sayılmaz:

- `FINALIZER_BINDING`: `CLOSED`
- `PR_VALIDATION_EXECUTION`: `CLOSED`
- `PR_REQUIRED_CHECK_ENFORCEMENT`: `OPEN — REPOSITORY SETTING`

## Uygulanan güvenlik modeli

### 1. Pull request full validation

`.github/workflows/tymm-lesson-plan-validation.yml` artık `pull_request -> main` olayında çalışır. Validation job adı `Full validation gate` ve job'ın varsayılan token yetkisi yalnız `contents: read` düzeyindedir.

Bu, lesson-plan kapsamına giren bir PR açıldığında 176 paketin full validation zincirinin PR üzerinde çalışmasını sağlar.

### 2. SHA + content fingerprint bağlı validation report

`validate_all_lesson_plans.py` validation report'a `binding` ekler:

- `commit_sha`
- `content_fingerprint`
- `fingerprinted_files`
- `algorithm`
- `schema_version`

Fingerprint mutlak checkout yoluna bağlı değildir; repo-içi mantıksal yollar kullanılır.

Fingerprint kapsamı lesson-plan üretimini belirleyen committed canonical veri ve çıktıları içerir. Geçici/generated `planning/course_timeline.json` kapsam dışıdır. `lesson_plan_production_plan.json` içindeki finalizer'ın kendi yazdığı `status`, `engineering_validation` ve `last_completed.validation_status` alanları hash döngüsü yaratmaması için normalize edilir.

### 3. PASS report olmadan finalization yok

`finalize_lesson_plan_production.py` artık zorunlu olarak:

- `--validation-report`
- `--expected-head`

alır ve aşağıdakilerden biri uyuşmazsa `FAIL_CLOSED` verir:

- validation report `PASS` değilse,
- failure veya warning kaydı varsa,
- rapordaki ders kümesi istenen derslerle aynı değilse,
- checkout HEAD beklenen SHA değilse,
- report `commit_sha` beklenen SHA değilse,
- yeniden hesaplanan content fingerprint raporla aynı değilse,
- fingerprint dosya sayısı / algoritması / schema sürümü değişmişse.

Finalizer ayrıca kullanılan report'un kendi `SHA-256` hash'ini production plan metadata'sına yazar.

### 4. Validation ve write permission ayrıldı

Workflow iki job'a ayrıldı:

1. `Full validation gate` — yalnız okuma yetkisiyle validation ve artifact üretir.
2. `Finalize validated main snapshot` — yalnız başarılı validation'dan sonra `contents: write` yetkisi alır, exact `${github.sha}` checkout eder ve ilk job'ın PASS report artifact'ını indirir.

### 5. Unvalidated rebase yasak

Eski finalizer akışındaki `git pull --rebase origin main` kaldırıldı.

Publish öncesi `origin/main` tekrar okunur. Remote HEAD validation sırasında doğrulanan `${GITHUB_SHA}` ile aynı değilse finalization push edilmez. Böylece eski PASS sonucu daha yeni ve doğrulanmamış içeriğin üstüne taşınamaz.

### 6. Self-trigger döngüsü kapatıldı

Finalizer yalnız production-plan validation metadata'sını güncellediği için aynı workflow'u tekrar tekrar tetikleme riski vardı. Finalizer commit mesajı artık `[skip ci]` içerir:

`chore(validation): bind production completion to validated snapshot [skip ci]`

Bu commit validation metadata'sını kaydeder fakat yeni bir validation/finalization döngüsü başlatmaz.

## Regression kapsamı

`test_validation_binding.py` şu durumları kapsar:

- exact SHA + fingerprint report -> PASS,
- validation sonrası plan içeriğini değiştirme -> FAIL,
- başka commit'e ait PASS report -> FAIL,
- checkout HEAD mismatch -> FAIL,
- finalizer metadata değişikliklerinin canonical content fingerprint'i bozmaması,
- generated course timeline değişikliğinin fingerprint'i bozmaması.

İlk gerçek CI koşusu checkout-root bağımlı fingerprint kusurunu yakaladı. Test gevşetilmedi; fingerprint repo-içi logical path kullanacak şekilde düzeltildi.

## Kabul koşusu

`TYMM Lesson Plan Full Validation` run `32877505053`:

- validation-binding regression tests: `SUCCESS`
- deterministic JSON-Markdown parity: `SUCCESS`
- package topology: `SUCCESS`
- grounded references: `SUCCESS`
- classroom adaptations: `SUCCESS`
- closure time budget: `SUCCESS`
- large-class route: `SUCCESS`
- `Validate all 176 lesson-plan packages`: `SUCCESS`
- `Finalize validated main snapshot`: `SUCCESS`

Validated source snapshot: `f59ef761200b65bc9eec2551545f8f96c187b106`.

Finalizer commit: `ea4d72bb5f771b460f5e7000bd419361312ba4f4` (`[skip ci]`). Bu committen sonra yeni `TYMM Lesson Plan Full Validation` run'ı oluşmadı; self-trigger kapısı doğrulandı.

Her iki production plan da aynı validated source snapshot için SHA/fingerprint/report binding taşır. Son acceptance fingerprint'i:

`sha256:c0b63624ce313c518ec0b278390b4c3c6df584b09bc512cc7e4dcf35208fffde`

## Kalan repository-level enforcement

`main` şu anda GitHub açısından `protected=false`; required status checks enforcement kapalıdır. Dolayısıyla `Full validation gate` PR'de çalışsa da repository ayarı merge'i bu check'e teknik olarak bağlamamaktadır ve doğrudan `main` push'u da branch rule tarafından engellenmemektedir.

P10'un tamamen `CLOSED` olabilmesi için GitHub branch protection/ruleset içinde en az şu koşul etkinleştirilmelidir:

- target: `main`
- require pull request before merge
- require status checks before merge
- required check: `Full validation gate`
- tercihen direct/bypass push istisnalarını yalnız açıkça gerekli aktörlerle sınırla

Bu repository setting, mevcut bağlı GitHub aracının yazabildiği endpointler arasında değildir; bu nedenle kod tarafından sahte bir enforcement uygulanmamıştır.
