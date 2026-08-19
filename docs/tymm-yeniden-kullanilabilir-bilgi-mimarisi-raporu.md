# TYMM İçerik Üretim Sistemi — Yeniden Kullanılabilir Bilgi Mimarisi ve Kurulum Raporu

**Amaç:** Bu rapor, TYMM uyumlu canonical bilgi tabanı + Hybrid RAG + resolver + runtime projection + kontrollü artifact generation mimarisini başka ders ve sınıflarda aynı güvenlik, izlenebilirlik ve yeniden üretilebilirlik düzeyiyle kurmak için hazırlanmıştır.

**Referans implementasyonları:**

- `TDE_9` — doğrulanmış gap bulunan ve canonical artifact üreten model.
- `TDE_10` — `0 confirmed gap + 8 structurally unresolved normative assessment target` bulunan, generation'ı fail-closed tutan `PARITY_REVIEW_BLOCKED` model. Unresolved hedefler kapandıktan sonra gerçek reuse-only veya artifact-producing sonuca geçebilir.

**Güncel mimari ilkesi:** Yapay zekâya doğrudan “programı ve kitabı oku, materyal üret” denmez. Önce resmî kaynaklar doğrulanır ve canonical knowledge'a dönüştürülür; ihtiyaç, coverage ve gap katmanları çıkarılır; cross-theme consolidation yapılır; production contract belirlenir; index/resolver/runtime/P0 gate'leri geçilir. Yalnız doğrulanmış gerçek bir gap varsa Artifact Generation Engine açılır.

> **`verified_resource_gap_count = 0` tek başına `REUSE_ONLY_NO_NEW_ARTIFACTS` için yeterli değildir. Normatif bir assessment/support hedefi yapısal olarak unresolved ise production `PARITY_REVIEW_BLOCKED` kalır ve generation `UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS` ile kapanır.**

---

## 1. Değişmez çalışma sırası

```text
RESMÎ KAYNAĞI ÇÖZ / DOĞRULA
   ↓
PROGRAMI YAPILANDIR
   ↓
DERS KİTABINI YAPILANDIR
   ↓
ÖĞRENME İHTİYACINI BELİRLE
   ↓
KİTAP COVERAGE'INI DOĞRULA
   ↓
GERÇEK GAP'İ BELİRLE
   ↓
RESOURCE PLAN
   ↓
CROSS-THEME CONSOLIDATION
   ↓
PRODUCTION CONTRACT
   ↓
P0 GATE
   ↓
┌────────────────────────────┬──────────────────────────────┬─────────────────────────────────┐
│ verified gap > 0           │ gap = 0, unresolved = 0      │ gap = 0, unresolved > 0         │
│ ARTIFACT_PRODUCING         │ REUSE_ONLY_NO_NEW_ARTIFACTS  │ PARITY_REVIEW_BLOCKED           │
│ Artifact Generator         │ NO_VERIFIED_RESOURCE_GAP     │ UNRESOLVED_NORMATIVE_           │
│ Validation / Review        │ generation blocked           │ ASSESSMENT_TARGETS              │
│ APPROVE / FREEZE           │                              │ generation blocked              │
└────────────────────────────┴──────────────────────────────┴─────────────────────────────────┘
```

En kritik kural:

> **Önce ne gerektiğini belirle, sonra kitapta olup olmadığına bak, sonra üret.**

Kitapta bir etkinliğin bulunması program gereksinimini otomatik karşılamaz. Kitapta eksik gibi görünen bir şey de otomatik generation gerekçesi değildir. Aynı şekilde gerekli action/evidence yollarının tamamı doğrulanmışsa sistem sırf production queue boş kalmasın diye yeni artifact üretemez.

---

## 2. Kaynak otoritesi

Yetki sırası:

1. Kullanıcının sağladığı resmî öğretim programı.
2. Kullanıcının sağladığı resmî ders kitabı.
3. Kullanıcının sağladığı diğer resmî MEB belgeleri.
4. Eksik/çelişkili durumda resmî MEB/TYMM doğrulaması.
5. Yalnız gerçek gap doğrulandıktan sonra güvenilir haricî kaynaklar.

Desteklenen source input modelleri:

```text
SINGLE_FILE
MULTI_PART_SOURCE_BUNDLE
OFFICIAL_REMOTE_WEB
OFFICIAL_REMOTE_ASSET
```

### 2.1 Single file

Tek program/kitap dosyasıdır. Kimlik, sürüm, dosya yolu ve mümkünse SHA-256 fingerprint manifestte tutulur.

### 2.2 Multi-part source bundle

Aynı resmî kaynağın tema/ünite bazında parçalı sunulmasıdır. Tek birleşik PDF zorunlu değildir.

Minimum metadata:

```text
source_group_id
expected_part_count
source_id
part/theme/unit identity
file_path
sha256
verification_status
bundle_completeness_status
```

Bundle ancak beklenen tüm parçalar mevcut ve her parçanın iç kimliği hedef ders/sınıf/tema ile uyumluysa `VERIFIED` olur.

### 2.3 Official remote source

Resmî URL primary locator olabilir. Kurallar:

- kullanıcının verdiği exact URL korunur,
- yalnız resmî sayfanın açığa çıkardığı resmî asset/viewer takip edilir,
- üçüncü taraf PDF sessizce primary source yapılamaz,
- erişim/provenance metadata tutulur,
- kaynak çözülemiyorsa fail-closed review oluşur.

### 2.4 Local official snapshot

Kullanıcı resmî kitabın PDF'sini repoya sağladıysa bu dosya doğrudan primary analysis snapshot olabilir. Remote TYMM/MEB sayfası identity/provenance crosscheck olarak tutulabilir.

TDE_10 bu modelin referansıdır:

```text
primary textbook snapshot:
courses/TDE_10/source_docs/turk-dili-ve-edebiyati-10.pdf
```

---

## 3. Canonical bilgi ile türetilmiş katmanları ayırma

```text
OFFICIAL SOURCES
      ↓
CANONICAL JSON / MD           ← SOURCE OF TRUTH
      ↓
├── knowledge.sqlite          ← DERIVED / REBUILDABLE RETRIEVAL CACHE
└── runtime/course_runtime.sqlite
                               ← DERIVED / READ-ONLY APP PROJECTION
```

Canonical kayıtlar source of truth'tur. `knowledge.sqlite` veya runtime SQLite silinse bile canonical dosyalardan yeniden üretilebilmelidir.

---

## 4. Sistemin katmanları

### Katman 1 — Source Resolution

Kaynağın kimliği, bütünlüğü, ders/sınıf uyumu ve provenance'ı doğrulanır.

### Katman 2 — Frozen Canonical Knowledge

Ham kaynak anlamlı canonical kayıtlara dönüştürülür:

- tema/ünite,
- learning outcome,
- süreç bileşeni veya kaynaktaki resmî süreç temsili,
- assessment hükmü,
- textbook section/activity,
- student action/evidence,
- form,
- alignment,
- gap,
- instructional need,
- resource plan,
- teaching block,
- school-based planning option,
- assessment gap instance,
- annual assessment artifact.

### Katman 3 — Knowledge Index

`knowledge.sqlite` içinde:

- structured metadata,
- SQLite FTS5,
- sqlite-vec,
- embeddings

bulunur. Canonical veri değildir.

### Katman 4 — Knowledge Resolver

Görevleri:

- exact ID çözümleme,
- theme/course scope çözümleme,
- alias → canonical artifact çözümleme,
- structured relation expansion,
- FTS/vector candidate retrieval,
- canonical record'a geri çözümleme,
- authority sıralaması,
- ambiguity tespiti,
- conflict tespiti,
- stale index kontrolü,
- generation gate kararı,
- minimum sufficient context pack üretimi.

### Katman 5 — Production Schema / Contract

Production contract üç güvenli durumdan birine sahiptir:

```text
ARTIFACT_PRODUCING
  verified_resource_gap_count > 0
  production_queue = [canonical artifacts]

REUSE_ONLY_NO_NEW_ARTIFACTS
  verified_resource_gap_count = 0
  unresolved_assessment_target_count = 0
  production_queue = []

PARITY_REVIEW_BLOCKED
  verified_resource_gap_count = 0
  unresolved_assessment_target_count > 0
  production_queue = []
  generation_authorization.allowed = false
```

Boş queue yalnız doğrulanmış reuse-only veya fail-closed parity-review-blocked durumda geçerlidir. `verified_resource_gap_count > 0` iken boş queue schema/gate hatasıdır; unresolved normatif hedef varken reuse-only sertifikası da hatadır.

Temel dosyalar:

```text
production/production_manifest.json
production/assessment_artifact_registry.json
production/assessment_design_contract.json
```

### Katman 6 — P0 Gate

P0 şu güvenlikleri doğrular:

- canonical maps verified/frozen mı,
- production schema tutarlı mı,
- artifact identity canonical mı,
- alias/provenance ilişkileri doğru mu,
- zero-gap invariant doğru mu,
- index sıfırdan rebuild edilebiliyor mu,
- index fresh mi,
- duplicate entity key var mı,
- resolver ambiguity/conflict/stale durumunda fail-closed mu,
- zero-gap generation isteği engelleniyor mu,
- runtime projection tutarlı mı.

`P0 PASS`, materyalin öğretmen tarafından onaylandığı anlamına gelmez.

### Katman 7 — Artifact Generation Engine

Generator yalnız `ARTIFACT_PRODUCING` course/context için canonical `artifact_id` üzerinden çalışır. Production registry + contract + verified knowledge'tan deterministik generation context üretir.

### Katman 8 — Generated Artifact Lifecycle

```text
GENERATED_DRAFT
   ↓
REVIEW_REQUIRED
   ↓ explicit teacher approval
APPROVED
   ↓ explicit freeze
FROZEN
```

Generator doğrudan `APPROVED` veya `FROZEN` üretemez.

### Katman 9 — Runtime Course Package

```text
canonical knowledge
   ↓ deterministic compiler
runtime/course_runtime.sqlite
   ↓
application
```

Runtime:

- source of truth değildir,
- read-only course knowledge projection'dır,
- user state içermez,
- vector/model runtime gerektirmez,
- canonical IDs ve provenance taşır,
- canonical fingerprint değiştiğinde stale olabilmelidir.

---

## 5. Repository standardı

```text
<Project>/
├── docs/
├── skill/
│   └── tymm-material-planner/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       ├── tests/
│       └── models/                  # runtime/dependency, source of truth değil
│
└── courses/
    └── <COURSE_ID>/
        ├── README.md
        ├── source_manifest.json
        ├── curriculum_map.json
        ├── textbook_map.json
        ├── textbook_forms_index.json
        ├── validation_report.md
        │
        ├── source_docs/
        │
        ├── themes/
        │   └── tema_XX/
        │       ├── needs.json
        │       ├── alignment.json
        │       ├── gap_analysis.json
        │       └── resource_plan.json
        │
        ├── planning/
        │   └── course_timeline.json
        │
        ├── production/
        │   ├── cross_theme_audit.json
        │   ├── consolidated_resource_plan.json
        │   ├── teaching_blocks.json
        │   ├── production_manifest.json
        │   ├── production_readiness_report.md
        │   ├── school_based_planning_options.json
        │   ├── assessment_artifact_registry.json
        │   ├── assessment_design_contract.json
        │   └── assessment_design_contract_report.md
        │
        ├── index/
        │   ├── knowledge.sqlite
        │   ├── index_manifest.json
        │   ├── index_validation_report.md
        │   └── p0_gate_report.json
        │
        ├── runtime/
        │   ├── course_runtime.sqlite
        │   ├── runtime_manifest.json
        │   └── runtime_validation_report.md
        │
        └── generated/
            └── <ARTIFACT_ID>/
                ├── generation_context.json
                ├── artifact.json
                ├── generation_state.json
                ├── generator_v1_gate_report.json
                ├── REVIEW.md
                └── revisions/
```

Kural:

> **Skill = nasıl çalışılacağını bilir. Course knowledge = bu ders için neyin doğru olduğunu bilir.**

---

## 6. Source manifest ve fingerprint sistemi

Uygun olduğu ölçüde:

```text
source_id
source_group_id
source_type
input_locator_type
file_path / exact_url
sha256 / content fingerprint
size_bytes
course / grade
program year / edition
theme / unit identity
authority rank
identity status
verification status
last_validated
```

saklanır.

Git blob SHA repository taşıma kimliğidir; source SHA-256 yerine geçirilmez.

Lifecycle:

```text
same verified source fingerprint
→ frozen map/cache reuse mümkün

source fingerprint / identity changed
→ canonical review/revalidation
→ knowledge index rebuild
→ runtime rebuild
```

---

## 7. Annual Course Timeline

Timeline planlanan öğretim ilerlemesini temsil eder; student mastery veya öğretmenin gerçek sınıf konumu değildir.

```text
planned_position
actual_teacher_position
student_mastery
```

ayrı kavramlardır.

Timeline:

1. stable instructional sequence,
2. optional academic-calendar binding

olarak iki katmanlı tutulur.

Kaynağa dayanmayan saat/hafta bilgileri `null / UNRESOLVED` kalır; uydurulmaz.

---

## 8. Curriculum Map

`curriculum_map.json` minimum olarak:

- tema/ünite ID ve adları,
- learning outcomes,
- kaynakta açıkça bulunan süreç bileşenleri,
- resmî assessment hükümleri,
- differentiation/enrichment hükümleri,
- saat bilgileri,
- source locator/provenance

barındırır.

### 8.1 Süreç bileşeni fail-closed kuralı

Başka sınıfın alt süreç kodları hedef sınıfa taşınamaz.

Örneğin hedef resmî snapshot'ta yalnız:

```text
TDE1.1
TDE1.2
...
```

yayımlanıyor, fakat `TDE1.2.1` gibi alt ID'ler açıkça yayımlanmıyorsa sistem bu alt ID'leri canonical veri olarak sentetik üretmez.

TDE_10'da dört resmî tema snapshot'ının her birinde 16 parent outcome doğrulanmış; kayıtlı snapshot'larda `TDE*.x.y` alt ID'leri yayımlanmadığı için canonical map bunları uydurmadan freeze edilmiştir.

---

## 9. Textbook Map

`textbook_map.json` kitabın gerçek öğretim yapısını modeller:

- sections,
- texts/genres,
- activities,
- student actions,
- expected evidence,
- assessment links,
- page/source locators.

Her activity mümkünse:

```text
activity_id
→ öğrenci ne yapıyor?
→ hangi evidence oluşuyor?
→ hangi outcome ile ilişkili?
→ hangi form/evaluation yolu bağlı?
```

şeklinde modellenir.

---

## 10. Textbook Forms Index

Değerlendirme yapıları structural type olarak ayrıca sınıflandırılır.

Örnekler:

```text
assessment_criteria_table
checklist
self_assessment_form
peer_assessment_form
teacher_evaluation_form
analytic_rubric
holistic_rubric
rating_scale
observation_form
exit_ticket
learning_journal
test_question_set
external_official_scoring_guide
```

Kritik ilke:

> “Dereceli puanlama anahtarı” ifadesi tek başına `analytic_rubric` demek değildir.

Analitik rubrik demek için criterion × level yapısı ve performans düzeyi descriptor'ları kanıtlanmalıdır. Dış EBA bağlantısının yapısal tipi açılmamışsa yalnız resmî scoring guide/link varlığı canonical fact olarak tutulur.

---

## 11. Validation ve Freeze

Birlikte doğrulanır:

```text
source_manifest
curriculum_map
textbook_map
textbook_forms_index
```

Kontroller:

- source identity/completeness,
- grade/theme identity,
- locator doğruluğu,
- unique IDs,
- broken references,
- form classification,
- canonical provenance,
- sentetik verinin canonical fact gibi sunulmaması.

Başarılı olduğunda canonical map'ler `FROZEN` olur.

---

## 12. Instructional Needs Analysis

Önce şu sorular cevaplanır:

- öğrenci ne yapmalı,
- hangi evidence görülmeli,
- program özel ölçme aracı/süreç istiyor mu,
- hangi destek/differentiation ihtiyacı var.

Bu aşamada materyal türü henüz sonuç değildir.

---

## 13. Program–Textbook Alignment

Coverage enum:

```text
COVERED
PARTIALLY_COVERED
NOT_COVERED
```

Coverage değerlendirmesinde birlikte bakılır:

- öğrenci eylemi,
- expected evidence,
- programın explicit requirement'ı,
- kitabın sunduğu task/form/scoring yolu.

---

## 14. Gap Analysis

Gap şu soruya cevap verir:

> Programın istediği evidence veya değerlendirme yapısını kitap neden tam karşılamıyor?

Örnek alanlar:

```text
gap_id
outcome_code
theme_id
coverage_status
program_requirement
textbook_provides
remaining_gap
source_locators
```

**Gap ID fiziksel artifact ID değildir.**

---

## 15. Resource Plan

Priority:

```text
REQUIRED
RECOMMENDED
OPTIONAL
NOT_NEEDED
```

Production decision:

```text
REUSE_TEXTBOOK
REUSE_WITH_TEACHER_GUIDE
ADAPT_TEXTBOOK_ACTIVITY
GENERATE
GENERATE_ASSESSMENT_SUPPORT
GENERATE_DIFFERENTIATION
GENERATE_ENRICHMENT
NO_ACTION
```

Necessity test:

> Bu kaynak çıkarılırsa programın gerekli evidence'ı gerçekten karşılanamaz mı?

Cevap hayırsa yeni kaynak `REQUIRED` değildir.

---

## 16. Cross-Theme Consolidation

Her tema bağımsız analiz edilir; ancak gap'ler doğrudan tema başına ayrı artifact'a dönüştürülmez.

### 16.1 GAP INSTANCE ≠ ARTIFACT

```text
ASSESSMENT_GAP_INSTANCE
= belirli tema/outcome bağlamındaki açık

ANNUAL_ASSESSMENT_ARTIFACT
= bir veya daha fazla gap instance'ı karşılayan canonical artifact
```

### 16.2 TDE_9 — 7 gap → 3 artifact

```text
7 REQUIRED gap instance
        ↓ consolidation
3 canonical artifact
```

Canonical set:

```text
TDE9_KONUSMA_RUBRIC
TDE9_YAZMA_RUBRIC
TDE9_YAZMA_SUREC_KONTROL_LISTESI
```

Legacy `MAT_*` kimlikleri provenance/alias'tır; canonical artifact identity değildir.

### 16.3 Annual Core + Task Binding

Yıllık reusable assessment iki katmanlıdır:

1. annual core — stabil criterion/level/scoring standardı,
2. task binding — tema/görev/evidence/locator.

Tema değişikliği tek başına yeni rubrik gerekçesi değildir.

### 16.4 Yeniden kullanım önceliği

```text
REUSE_ANNUAL_CORE
→ REUSE_WITH_TASK_BINDING
→ REUSE_WITH_CRITERION_EXTENSION
→ GENERATE_NEW_ASSESSMENT
```

### 16.5 Zero-gap / Reuse-only production

Gerçek reuse-only sonucu için iki ayrı sıfır birlikte gerekir:

```text
verified_resource_gap_count = 0
unresolved_assessment_target_count = 0
        ↓
production_mode = REUSE_ONLY_NO_NEW_ARTIFACTS
production_queue = []
        ↓
MATERIAL_GENERATION
→ NO_VERIFIED_RESOURCE_GAP
```

### 16.6 Parity-review-blocked production

Bir normatif assessment/support hedefinin varlığı doğrulanmış fakat yapısı doğrulanamamışsa `0 confirmed gap` reuse-only sertifikası vermez.

```text
verified_resource_gap_count = 0
unresolved_assessment_target_count > 0
        ↓
production_mode = PARITY_REVIEW_BLOCKED
production_queue = []
generation_authorization.allowed = false
        ↓
MATERIAL_GENERATION
→ UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS
```

Kurallar:

- `UNRESOLVED ≠ COVERED`,
- resmî link varlığı tek başına assessment requirement'ı kapatmaz,
- unresolved hedef çözülmeden artifact uydurulmaz,
- hedefler yeterli çıkarsa reuse-only, yetersiz çıkarsa gap analysis + cross-theme consolidation üzerinden artifact-producing moda geçilir.

TDE_10 bu fail-closed ara durumun referans implementasyonudur.

---

## 17. School-Based Planning ayrı katmandır

School-based planning program gap'i değildir.

```text
selection_status = NOT_SELECTED
generation_status = NOT_REQUESTED
origin = pedagogical_recommendation
```

Öğretmen seçmeden canonical artifact production queue'ya giremez.

### TDE_10 saat semantiği

```text
Her tema dış blok = 45 saat
                   = 43 saat resmî tema öğretimi
                   + 2 saat okul temelli planlama

4 tema            = 180 saat
                   = 172 + 8
```

8 school-based saat tek detached annual block değildir; her temaya bağlı 2 saatlik ayrı pedagojik katmandır.

---

## 18. Hybrid RAG

Retrieval sırası:

```text
EXACT
→ STRUCTURED RELATIONS
→ METADATA FILTER
→ FTS5
→ VECTOR
→ CANONICAL RESOLUTION
```

Vector similarity authority/ambiguity/conflict çözmez; yalnız candidate bulur.

---

## 19. Stable Entity Key

Outcome code'larının course genelinde unique olduğu varsayılmaz.

```text
TDE_10::curriculum_outcome::TEMA_02::TDE4.4
```

Tema belirtilmeden aynı outcome birden çok temada bulunuyorsa:

```text
AMBIGUOUS_ENTITY
→ generation blocked
```

Assessment artifact için canonical identity:

```text
TDE_9::assessment_artifact::TDE9_KONUSMA_RUBRIC
```

---

## 20. Resolver fail-closed davranışları

### Ambiguity

```text
AMBIGUOUS_ENTITY
→ material_generation_allowed = false
```

### Knowledge conflict

```text
KNOWLEDGE_CONFLICT
→ REVIEW_REQUIRED
→ generation blocked
```

### Stale index

```text
INDEX_STALE
→ generation blocked
→ rebuild required
```

### Duplicate canonical key

```text
DUPLICATE_CANONICAL_KEY
→ index build FAIL
```

### Legacy artifact identity

```text
MAT_* used as artifact_id
→ BLOCKED
```

### Zero-gap generation

```text
production_mode = REUSE_ONLY_NO_NEW_ARTIFACTS
verified_resource_gap_count = 0
unresolved_assessment_target_count = 0
+ MATERIAL_GENERATION intent
→ NO_VERIFIED_RESOURCE_GAP
→ generation blocked
```

### Unresolved normative target generation

```text
production_mode = PARITY_REVIEW_BLOCKED
unresolved_assessment_target_count > 0
+ MATERIAL_GENERATION intent
→ UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS
→ generation blocked
```

---

## 21. Production Schema 1.1

Canonical artifact identity `artifact_id`'dir.

Schema üç durumu destekler:

### Artifact-producing course

- `production_queue` non-empty,
- gap aliases canonical artifactlara resolve olur,
- provenance registry alias mapping ile birebir tutarlıdır.

### Reuse-only course

Aşağıdaki üç koşul birlikte zorunludur:

```text
production_mode = REUSE_ONLY_NO_NEW_ARTIFACTS
verified_resource_gap_count = 0
production_queue = []
```

Gap count sıfır değilse empty queue kabul edilmez.

### Parity-review-blocked course

```text
production_mode = PARITY_REVIEW_BLOCKED
verified_resource_gap_count = 0
unresolved_assessment_target_count > 0
production_queue = []
generation_authorization.allowed = false
generation_authorization.reason = UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS
```

Bu durum `NO_REQUIRED_ARTIFACTS` sertifikası değildir; unresolved normatif hedefler çözülene kadar güvenli ara durumdur.

---

## 22. Embedding / Vector Backend

Referans implementasyon:

```text
base model: intfloat/multilingual-e5-small
runtime artifact: Xenova/multilingual-e5-small
format: ONNX
quantization: quantized
embedding_dimension: 384
vector backend: sqlite-vec
lexical backend: SQLite FTS5
```

Bunlar teknik tercihtir, canonical mimari zorunluluğu değildir. Model/backend değişirse açıkça versionlanmalı ve index rebuild edilmelidir.

---

## 23. Generation Context

Retrieval candidate ile generation context aynı değildir.

Minimum deterministik snapshot:

```text
context_schema_version
generator_version
course_id
artifact_id
artifact_family
artifact_scope
artifact registry record
production record
covered themes
covered outcomes
covered gap instances
gap provenance
contract profile
source locators
source fingerprints
knowledge index status
context_hash
```

> **retrieval_candidates ≠ generation_context**

---

## 24. Idempotency ve revision

```text
artifact_id       = kalıcı canonical kimlik
artifact_revision = içerik revision'ı
context_hash      = deterministic input fingerprint
```

Aynı artifact + aynı context hash yeniden çalıştırıldığında yeni artifact/revision oluşturulmamalıdır.

Context değişirse yeni revision üretilebilir ve önceki snapshot `revisions/` altında korunur.

---

## 25. Assessment Design Contract

Contract şu ayrımı korur:

```text
OFFICIAL_REQUIREMENT
TEXTBOOK_PROVIDES
REMAINING_GAP
SELECTED_IMPLEMENTATION
```

Örneğin:

```text
OFFICIAL_REQUIREMENT = dereceli puanlama anahtarı
SELECTED_IMPLEMENTATION = analytic_rubric
```

olabilir; ancak bu, programın literal olarak analytic rubric istediği anlamına gelmez.

Criterion origin enum:

```text
official_curriculum
official_textbook
pedagogical_recommendation
```

Descriptor'ların pedagojik türetim olduğu açıkça ayrılır.

---

## 26. Artifact Generator V1

```text
P0_GATE
  ↓ PASS
SELECT_ARTIFACT
  ↓
BUILD_GENERATION_CONTEXT
  ↓
VALIDATE_CONTEXT
  ↓
GENERATE_DRAFT
  ↓
STRUCTURAL_VALIDATION
  ↓
CONTRACT_VALIDATION
  ↓
PROVENANCE_VALIDATION
  ↓
REVIEW_REQUIRED
```

Kod seviyesinde en az:

- canonical artifact ID,
- context hash,
- required sections,
- criterion/level completeness,
- provenance,
- scoring dimensions,
- teacher review state,
- idempotency

kontrol edilir.

Generator zero-gap course'ta artifact uydurmak için kullanılamaz.

---

## 27. Generator pilot gate

TDE_9 pilot artifact:

```text
TDE9_KONUSMA_RUBRIC
```

Pilot teknik validation geçse bile teacher review tamamlanmadan kalan queue açılmaz.

```text
ENGINEERING_PASS_REVIEW_REQUIRED
≠ APPROVED
≠ FROZEN
```

---

## 28. Rights / Provenance

Global rights enum:

```text
PUBLIC_DOMAIN
OPEN_LICENSE
OFFICIAL_REUSE_ALLOWED
LIMITED_QUOTATION
LINK_ONLY
UNKNOWN_RIGHTS
DO_NOT_USE
```

Kurallar:

- uzun telifli metin artifact içine yeniden basılmaz,
- locator tercih edilir,
- attribution izin anlamına gelmez,
- hak durumu uydurulmaz,
- `DO_NOT_USE` body generation context'e gövde olarak girmez.

---

## 29. Quality Gates

```text
Source Identity QA
Curriculum QA
Textbook QA
Version QA
Needs QA
Alignment / Coverage QA
Gap QA
Resource Plan / Necessity QA
Cross-Theme Consolidation QA
Production Schema QA
Index / Resolver QA
Runtime Projection QA
Generation Context QA
Structural Artifact QA
Assessment Contract QA
Provenance QA
Copyright QA
Safety QA
Privacy QA
Teacher Review
```

Durum mantığı:

```text
any FAIL → BLOCKED
no FAIL + at least one REVIEW → REVIEW_REQUIRED
all applicable PASS/N/A → PASS
```

---

## 30. Yeni Ders İçin Kurulum Playbook'u

### Faz 0 — Source resolution

1. Program source modelini belirle.
2. Textbook source modelini belirle.
3. `source_manifest.json` oluştur.
4. Identity/fingerprint/provenance kaydet.
5. Bundle completeness doğrula.

### Faz 1 — Curriculum mapping

6. Tema/ünite yapısını çıkar.
7. Parent outcomes'ları verbatim çıkar.
8. Kaynakta açıkça yayımlanan süreç bileşenlerini çıkar; yayımlanmayan alt ID'leri uydurma.
9. Assessment/differentiation/saat hükümlerini çıkar.
10. Locator ekle.

### Faz 2 — Textbook mapping

11. Bölüm yapısını çıkar.
12. Activities'leri ID'le.
13. Student action/evidence çıkar.
14. Forms index oluştur.
15. Activity ↔ form/outcome ilişkilerini kur.
16. Locator doğrula.

### Faz 3 — Validation / freeze

17. Source identity/version uyumu.
18. Form classification.
19. Broken reference.
20. Locator audit.
21. Canonical freeze.

### Faz 4 — Instructional analysis

22. Needs çıkar.
23. Evidence tanımla.
24. Coverage değerlendir.
25. Gap analysis.
26. Resource plan.

### Faz 5 — Cross-theme consolidation

27. Tema resource planlarını birleştir.
28. Duplicate kaynakları deduplicate et.
29. Gap instance'ları consolidate et.
30. `verified_resource_gap_count` belirle.
31. Production mode seç:

```text
gap > 0 → ARTIFACT_PRODUCING
gap = 0 + unresolved = 0 → REUSE_ONLY_NO_NEW_ARTIFACTS
gap = 0 + unresolved > 0 → PARITY_REVIEW_BLOCKED
```

32. Production manifest/registry/teaching blocks oluştur.

### Faz 6 — School-based layer

33. School-based saatleri ayrı modelle.
34. Recommendation seçenekleri oluştur.
35. Varsayılan NOT_SELECTED / NOT_REQUESTED bırak.

### Faz 7 — Knowledge Index

36. Stable entity key üret.
37. FTS5 + vector index kur.
38. Manifest/fingerprint yaz.
39. Index'i sıfırdan rebuild et.
40. Duplicate/stale gate çalıştır.

### Faz 8 — Resolver acceptance

41. Exact ID testleri.
42. Alias testleri applicable ise.
43. Theme ambiguity.
44. Natural-language probes.
45. Conflict fixture.
46. Stale fixture.
47. Zero-gap generation fixture applicable ise.

### Faz 9 — Runtime projection

48. Canonical → runtime SQLite compiler.
49. FK/orphan/unique ID testleri.
50. App acceptance queries.
51. User state/vector dependency exclusion.
52. Runtime freshness.

### Faz 10 — P0

53. Production schema validate.
54. Knowledge index fresh rebuild.
55. Resolver safety gates.
56. Runtime projection.
57. Course-specific invariant'lar:

```text
TDE_9: 7 gap → 3 artifact
TDE_10: 0 confirmed gap + 8 unresolved target → PARITY_REVIEW_BLOCKED / 0 authorized artifact
```

58. P0 PASS.

### Faz 11 — Artifact Generator

Yalnız `ARTIFACT_PRODUCING` course için:

59. Canonical artifact seç.
60. Context snapshot/hash oluştur.
61. Draft üret.
62. Structural/contract/provenance validation.
63. Idempotency.
64. REVIEW_REQUIRED.

Reuse-only ve parity-review-blocked course bu fazı atlar; generator yalnız verified gap sonrası artifact-producing moda geçen course için açılır.

### Faz 12 — Teacher Review / Freeze

65. Pilot artifact review.
66. Explicit approve.
67. Explicit freeze.
68. Kalan queue applicable ise açılır.

---

## 31. Güvenlik checklist'i

```text
[ ] Source identity/fingerprint kayıtlı mı?
[ ] Multi-part bundle completeness doğrulandı mı?
[ ] Remote source exact official provenance taşıyor mu?
[ ] Program verbatim/official fields locator taşıyor mu?
[ ] Kaynakta yayımlanmayan outcome/process ID uydurulmuş mu? → olmamalı
[ ] Activity/form ID'leri unique mi?
[ ] Form classification kanıtlı mı?
[ ] Stable entity keys scope-safe mi?
[ ] Canonical JSON/MD source of truth mı?
[ ] knowledge.sqlite yalnız derived/cache mi?
[ ] Runtime yalnız derived projection mı?
[ ] Semantic result canonical record'a resolve oluyor mu?
[ ] Ambiguity fail-closed mu?
[ ] Conflict fail-closed mu?
[ ] INDEX_STALE fixture PASS mı?
[ ] DUPLICATE_CANONICAL_KEY fixture var mı?
[ ] School-based option'lar gap sayılmıyor mu?
[ ] GAP INSTANCE ile ARTIFACT identity ayrılmış mı?
[ ] MAT_* yalnız alias/provenance mı?
[ ] Consolidation invariant gate'lenmiş mi?
[ ] Empty queue yalnız verified reuse-only veya fail-closed parity-review-blocked modunda mı kabul ediliyor?
[ ] Reuse-only generation `NO_VERIFIED_RESOURCE_GAP`, parity-blocked generation `UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS` ile kapanıyor mu?
[ ] P0 fresh rebuild yapıyor mu?
[ ] Runtime final canonical fingerprintten rebuild ediliyor mu?
[ ] retrieval_candidates ile generation_context ayrı mı?
[ ] Context deterministic/hash'li mi?
[ ] Idempotency var mı?
[ ] Revision history korunuyor mu?
[ ] Generated artifact otomatik APPROVED/FROZEN olmuyor mu?
[ ] Teacher review gate var mı?
```

---

## 32. Minimum Resolver Context Pack

```json
{
  "course_id": "<COURSE_ID>",
  "query": "...",
  "query_intent": "MATERIAL_GENERATION",
  "resolution_status": "RESOLVED",
  "resolution_mode": ["EXACT", "STRUCTURED", "FTS", "VECTOR"],
  "ambiguity_status": "UNAMBIGUOUS",
  "index_freshness": "INDEX_FRESH",
  "canonical_resolution_verified": true,
  "material_generation_allowed": false,
  "material_generation_block_reason": "NO_VERIFIED_RESOURCE_GAP",
  "resolved_entities": [],
  "curriculum_context": [],
  "textbook_context": [],
  "assessment_context": [],
  "alignment_context": [],
  "production_context": [],
  "remaining_gaps": [],
  "pedagogical_recommendations": [],
  "conflicts": [],
  "retrieval_trace": []
}
```

Bu pack generator inputu değildir; artifact-producing durumda daha dar deterministic `generation_context` türetilir.

---

## 33. Search benchmark standardı

Yeni course için en az 10–15 doğal dil sorgusu önerilir:

- exact outcome,
- theme + outcome,
- canonical artifact,
- alias applicable ise,
- “kitapta ne eksik?”,
- “nasıl değerlendireceğim?”,
- form lookup,
- school-based option,
- negative rubric query,
- ambiguity,
- conflict,
- stale,
- zero-gap generation probe.

Safety hedefleri:

```text
canonical_resolution_accuracy = 100%
ambiguity_detection_accuracy = 100%
conflict_detection_accuracy = 100%
stale_detection_accuracy = 100%
production-mode gate accuracy = 100%
```

Retrieval Hit@K düşük olabilir; safety metricleri düşük olamaz.

---

## 34. Freeze modeli

```text
SOURCE MAPS                  FROZEN
CURRICULUM MAP               FROZEN
TEXTBOOK MAP                 FROZEN
ASSESSMENT FORMS INDEX       FROZEN
THEME ALIGNMENTS             FROZEN
GAP ANALYSIS                 FROZEN
RESOURCE PLANS               FROZEN
PRODUCTION MANIFEST          FROZEN
ASSESSMENT ARTIFACT REGISTRY FROZEN / EMPTY-VALID-IN-REUSE-ONLY
KNOWLEDGE BASE               FROZEN CANONICAL / DERIVED INDEX
KNOWLEDGE RESOLVER           SHARED ENGINE
HYBRID RAG                   DERIVED INDEX
RUNTIME PROJECTION           REBUILDABLE
GENERATED ARTIFACT           PER-ARTIFACT LIFECYCLE
```

---

## 35. TDE_9'dan çıkan ana dersler

1. Ders kitabındaki ölçüt tablosunu otomatik analytic rubric saymamak.
2. Aynı outcome code'un farklı temalarda tekrar edebileceğini kabul etmek.
3. Vector similarity ile ambiguity çözmemek.
4. “Dereceli puanlama anahtarı”nı otomatik analytic rubric diye resmîleştirmemek.
5. School-based recommendation'ı gap/production requirement yapmamak.
6. Retrieval candidate ile generation context'i ayırmak.
7. Rights status uydurmamak.
8. 100'lük dönüşümü resmî kural gibi sunmamak.
9. Teacher review olmadan artifact'ı approved/frozen saymamak.
10. Vector DB'yi source of truth yapmamak.
11. Gap ID ile artifact ID'yi ayırmak.
12. 7 gap'i 7 fiziksel materyale çevirmemek.
13. Production schema/indexer/resolver drift'ini CI ile gate'lemek.
14. `knowledge.sqlite` rebuildability'yi gerçek gate ile test etmek.
15. Generation context'i deterministic/hash'li yapmak.
16. Artifact generation'ı idempotent yapmak.
17. Generation/approval/freeze lifecycle'larını ayırmak.

---

## 36. TDE_10'dan çıkan yeni ana dersler

1. Başka sınıfın alt süreç kodlarını kopyalamamak; resmî kaynak yayımlamıyorsa sentezlememek.
2. Yerel resmî textbook PDF'yi primary analysis snapshot olarak desteklemek.
3. QR/EBA scoring-guide link varlığını hedef yapısının doğrulanmasından ayırmak.
4. **`UNRESOLVED ≠ COVERED`.** Auth-gated normatif hedef `PARTIALLY_COVERED / REVIEW_REQUIRED` kalır.
5. **`gap=0 ≠ NO_REQUIRED_ARTIFACTS`.** Reuse-only için unresolved normatif hedef sayısı da `0` olmalıdır.
6. **`PARITY_REVIEW_BLOCKED` birinci sınıf güvenli durumdur.** Empty queue geçerli, generation kapalıdır.
7. Outcome-level need/resource/alignment/gap izini domain-level özetlerle kaybetmemek.
8. Cross-theme audit'i yalnız declared gap sayımına indirgememek; ortak assessment construct'larını da karşılaştırmak.
9. TDE_9 7→3 ve TDE_10 parity-blocked invariantlarını aynı shared engine'de regression ile korumak.
10. Canonical contract/registry/manifest değişiminden sonra index/runtime'ı final fingerprint üzerinden rebuild etmek.

---

## 37. Mimari özet

```text
1. SOURCE TRUTH
   Official Program + Official Textbook + Source Manifest

2. CANONICAL KNOWLEDGE
   Curriculum/Textbook Maps + Needs + Alignment + Gap + Resource Plan

3. FIND / RESOLVE
   SQLite FTS5 + Vector + Resolver

4. PRODUCTION CONTRACT
   Consolidation + Production Mode + Registry + Contract + P0

5A. GAP > 0
   ARTIFACT_PRODUCING → Generator → Validation → Teacher Review

5B. GAP = 0 / UNRESOLVED = 0
   REUSE_ONLY_NO_NEW_ARTIFACTS → NO_VERIFIED_RESOURCE_GAP

5C. GAP = 0 / UNRESOLVED > 0
   PARITY_REVIEW_BLOCKED → UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS

6. APPLICATION
   Deterministic Runtime SQLite Projection
```

> **Yapay zekâ kararın kaynağı değildir. Yapay zekâ, doğrulanmış canonical bilgi ve açık production contract üzerinde çalışan kontrollü üretim motorudur.**

---

## 38. Güncel TDE_9 implementasyon durumu — 2026-08-18

```text
Canonical Knowledge            FROZEN / VERIFIED
Production Schema 1.1          VERIFIED
7 gap → 3 artifact mapping     VERIFIED
Knowledge Index                PASS / REBUILDABLE
Knowledge Resolver             PASS
Runtime Projection             PASS
P0 Production Gate             PASS
Artifact Generator V1          IMPLEMENTED
TDE9_KONUSMA_RUBRIC            GENERATED / REVIEW_REQUIRED
Generator V1 Engineering Gate  ENGINEERING_PASS_REVIEW_REQUIRED
TDE9_YAZMA_RUBRIC              ORDER-GATED / LOCKED
TDE9_YAZMA_SUREC_KONTROL...    ORDER-GATED / LOCKED
```

Pilot teknik PASS öğretmen onayı değildir.

---

## 39. Güncel TDE_10 implementasyon durumu — 2026-08-19

```text
Official curriculum snapshots        PASS (4/4)
Canonical learning outcomes          PASS (64/64)
Curriculum canonical map             VERIFIED / FROZEN
Official local textbook PDF          VERIFIED / FROZEN
Textbook sections                    24
Textbook activities                  75
Assessment/form records              35
Program-textbook alignment           56 COVERED / 8 PARTIALLY_COVERED / 0 NOT_COVERED
Confirmed remaining resource gaps    0
Unresolved normative targets         8 authenticated EBA DPA targets
Production mode                      PARITY_REVIEW_BLOCKED
Canonical new artifacts authorized   0
Teaching blocks                      16
Knowledge index                      INDEX_FRESH / 482 records
Duplicate canonical keys             0
Resolver ambiguity/stale/conflict    PASS
Generation gate                      PASS / UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS
Runtime projection                   PASS
Technical P0                         PASS
TDE_9 regression                     PASS / 7 gap → 3 artifact preserved
Parity certification                 WITHHELD pending 8 EBA target structures
```

Runtime projection includes 64 resource decisions, 75 activities, 35 forms and 0 authorized assessment artifacts. `0 assessment_artifact` is a correct fail-closed result, but it is not called verified reuse-only until all eight unresolved targets are structurally resolved.

---

## 40. Kalıcı CI workflow seti

Kurulum sırasında kullanılan extraction/freeze/diagnostic/patch workflow'ları kalıcı architecture değildir. TDE_10 kurulumu tamamlandıktan sonra temizlenmiştir.

Kalıcı workflow seti:

```text
.github/workflows/tymm-p0-production-gate.yml
→ TDE_9 7-gap / 3-artifact P0 regresyonu

.github/workflows/tymm-tde10-p0.yml
→ TDE_10 parity-aware generic P0
→ reuse-only / PARITY_REVIEW_BLOCKED contract validation
→ index/runtime rebuild
→ final canonical metadata sonrası ikinci rebuild/freshness doğrulaması

.github/workflows/tymm-artifact-generator-v1.yml
→ artifact-producing course için generator lifecycle gate
```

Shared engine:

```text
skill/tymm-material-planner/scripts/production_schema.py
skill/tymm-material-planner/scripts/knowledge_index.py
skill/tymm-material-planner/scripts/knowledge_resolver.py
skill/tymm-material-planner/scripts/build_runtime_course_package.py
skill/tymm-material-planner/scripts/generic_p0_course_gate.py
```

Önemli invariant:

> P0 sırasında `source_manifest.json` veya başka canonical metadata değiştirilirse `knowledge.sqlite` ve runtime SQLite **final metadata üzerinden tekrar rebuild edilmeden** sonuç yayımlanmamalıdır.

---

# Ek A — Yeni Ders İçin kısa başlangıç şablonu

```text
COURSE_ID = <ör. TDE_10>

1.  source_manifest.json
2.  source identity/fingerprint verification
3.  curriculum_map.json
4.  textbook_map.json
5.  textbook_forms_index.json
6.  validation/freeze
7.  themes/*/needs.json
8.  themes/*/alignment.json
9.  themes/*/gap_analysis.json
10. themes/*/resource_plan.json
11. cross-theme consolidation
12. verified_resource_gap_count
13. production_mode
14. production_manifest.json
15. assessment_artifact_registry.json
16. assessment_design_contract.json
17. teaching_blocks.json
18. knowledge index rebuild
19. resolver safety tests
20. runtime projection
21. P0
22A. artifact-producing ise generation context + generator
22B. reuse-only ise NO_VERIFIED_RESOURCE_GAP gate
23. teacher review/freeze applicable ise
```

---

# Ek B — “Üretime hazır mı?” kontrolü

### Artifact-producing course

Aşağıdaki zincir gösterilebiliyorsa production input hazırdır:

> “Bu artifact'ın hangi resmî requirement'ı karşıladığı, kitapta hangi karşılığın bulunduğu, hangi remaining gap'in kaldığı, neden REQUIRED olduğu, hangi canonical artifact'a konsolide edildiği, hangi contract/context ile üretileceği ve hangi QA gate'lerinden geçeceği gösterilebiliyor.”

### Zero-gap / reuse-only course

Aşağıdaki zincir gösterilebiliyorsa production input hazırdır:

> “Scoped program gereksinimlerinin tamamında textbook action/evidence ve normatif assessment yapıları doğrulandı; remaining gap `0`; unresolved target `0`; contract `REUSE_ONLY_NO_NEW_ARTIFACTS`; generation `NO_VERIFIED_RESOURCE_GAP` ile kapalı.”

### Parity-review-blocked course

Aşağıdaki zincir gösterilebiliyorsa güvenli ara durum doğrudur:

> “Confirmed gap `0` fakat en az bir normatif assessment/support hedefi yapısal olarak unresolved; bu hedef COVERED sayılmıyor; contract `PARITY_REVIEW_BLOCKED`; queue boş; generation `UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS` ile kapalı; hedef çözülmeden reuse-only sertifikası veya artifact verilmiyor.”

Bu üç modelden uygun olanındaki bir halka eksikse P0 açılmamalıdır.

Artifact-producing course'ta gerçek artifact'ın production-ready/frozen olması için ayrıca:

```text
P0_GATE = PASS
+ deterministic generation context
+ structural/contract/provenance validation PASS
+ teacher review APPROVED
+ explicit FROZEN lifecycle
```

gerekir.
