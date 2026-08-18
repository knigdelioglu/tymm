# TYMM İçerik Üretim Sistemi — Yeniden Kullanılabilir Bilgi Mimarisi ve Kurulum Raporu

**Amaç:** Bu rapor, TYMM uyumlu bilgi tabanı + Hybrid RAG + resolver + runtime projection + kontrollü artifact generation mimarisini başka ders ve sınıflarda aynı güvenlik, izlenebilirlik ve yeniden üretilebilirlik düzeyiyle kurmak için hazırlanmıştır.

**Referans implementasyon:** `TDE_9`

**Güncel mimari ilkesi:** Yapay zekâya doğrudan “programı ve kitabı oku, materyal üret” denmez. Önce resmî kaynaklar doğrulanır ve canonical knowledge'a dönüştürülür; ihtiyaç, coverage ve gap katmanları çıkarılır; production planı konsolide edilir; index/resolver/runtime gate'leri geçilir; ancak bundan sonra Artifact Generation Engine doğrulanmış bir generation context snapshot'ından taslak üretir. Üretim hiçbir zaman otomatik onay anlamına gelmez.

---

## 1. Sistemin temel prensibi

Sistemin değişmez çalışma sırası:

```text
RESMÎ KAYNAĞI ÇÖZ / DOĞRULA
   ↓
PROGRAMI YAPILANDIR
   ↓
DERS KİTABINI YAPILANDIR
   ↓
ÖĞRENME İÇİN NE GEREKTİĞİNİ BELİRLE
   ↓
KİTAPTA KARŞILIĞI VAR MI KONTROL ET
   ↓
GERÇEK BOŞLUĞU BELİRLE
   ↓
YALNIZ GEREKLİ EKSİĞİ PLANLA
   ↓
CROSS-THEME CONSOLIDATION
   ↓
PRODUCTION CONTRACT + P0 GATE
   ↓
ARTIFACT GENERATOR
   ↓
VALIDATION
   ↓
TEACHER REVIEW
   ↓
APPROVE / FREEZE
```

En kritik kural:

> **Önce ne gerektiğini belirle, sonra kitapta olup olmadığına bak, sonra üret.**

Ders kitabında bir etkinliğin bulunması, program gereksinimini tam karşıladığı anlamına gelmez. Kitapta bir şeyin eksik görünmesi de otomatik olarak yeni materyal üretme gerekçesi değildir.

---

## 2. Kaynak otoritesi ve desteklenen kaynak biçimleri

Bilgi kaynaklarının yetki sırası:

1. Kullanıcının sağladığı resmî öğretim programı — normatif birincil kaynak.
2. Kullanıcının sağladığı resmî ders kitabı — sınıf içi uygulama ve içerik çıpası.
3. Kullanıcının sağladığı diğer resmî MEB belgeleri.
4. Eksik, çelişkili veya güncelliği belirsiz durumda resmî MEB/TYMM doğrulaması.
5. Yalnız gerçek bir boşluk saptandıktan sonra güvenilir haricî kaynaklar.

“Kullanıcının sağladığı kaynak” yalnız tek bir yerel PDF anlamına gelmez. Sistem şu source input biçimlerini desteklemelidir:

```text
SINGLE_FILE
MULTI_PART_SOURCE_BUNDLE
OFFICIAL_REMOTE_WEB
OFFICIAL_REMOTE_ASSET
```

### Single file

Tek bir program veya kitap dosyasıdır. Dosyanın SHA-256 fingerprint'i, kimliği ve sürümü manifestte tutulur.

### Multi-part source bundle

Aynı resmî kaynağın tema/ünite/bölüm bazında birden çok dosyaya ayrılmış hâlidir. Tek bir birleşik PDF beklenmez.

Manifestte en az:

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

saklanır.

Bundle ancak beklenen parçaların tamamı mevcut ve her parçanın iç kimliği hedef ders/sınıf/tema ile doğrulanmışsa `VERIFIED` kabul edilir.

### Official remote source

Kullanıcı resmî MEB/TYMM URL'si verdiyse bu URL primary source locator olabilir. Büyük binary kitabın GitHub'a kopyalanması zorunlu değildir.

Kurallar:

- supplied exact URL korunur,
- yalnız resmî sayfanın açığa çıkardığı resmî asset/viewer bağlantıları izlenir,
- üçüncü taraf PDF sessizce primary source yerine geçirilmez,
- erişim tarihi ve mümkünse content fingerprint tutulur,
- kaynak erişilemiyorsa fail-closed review durumu oluşur.

> Sistem, kullanıcı tarafından verilen resmî program veya kitabı başka bir web sonucu ya da farklı baskıyla sessizce değiştirmez.

---

## 3. Sistemin katmanları

### Katman 1 — Source Resolution

Ham kaynak biçimi dosya, bundle veya resmî remote asset olabilir. İlk iş kaynağın kimliğini, bütünlüğünü, ders/sınıf uyumunu ve fingerprint'ini doğrulamaktır.

### Katman 2 — Frozen Canonical Knowledge

Ham kaynak doğrudan vector DB'ye atılmaz. Önce doğrulanmış ve anlamlı kayıtlara dönüştürülür.

Örnek varlıklar:

- tema / ünite
- öğrenme çıktısı
- süreç bileşeni
- program hükmü
- ders kitabı bölümü
- etkinlik
- öğrenci eylemi / evidence
- değerlendirme formu
- program-kitap alignment
- remaining gap
- instructional need
- resource plan
- teaching block
- school-based planning option
- assessment gap instance
- annual assessment artifact

Canonical JSON/MD kayıtları **source of truth** kabul edilir.

### Katman 3 — Knowledge Index

`knowledge.sqlite` canonical bilgi değildir; yalnız retrieval için türetilmiş cache'tir.

İçinde:

- structured metadata
- SQLite FTS5
- sqlite-vec
- embedding'ler

bulunur.

Silinirse canonical kayıtlardan sıfırdan rebuild edilmelidir.

### Katman 4 — Knowledge Resolver

Arama adayları bulur; Resolver hangi bilginin gerçekten kullanılabileceğine karar verir.

Görevleri:

- exact ID çözümleme
- alias → canonical artifact çözümleme
- theme/course/entity scope çözümleme
- ilişki genişletme
- authority sıralaması
- FTS + vector retrieval
- canonical record'a geri çözümleme
- ambiguity tespiti
- knowledge conflict tespiti
- stale index kontrolü
- minimum sufficient context pack üretimi

### Katman 5 — Production Schema ve Contracts

Bilgi tabanı **“ne gerekli?”**, production/assessment contract ise **“hangi canonical artifact bunu karşılayacak ve hangi kurallarla üretilecek?”** sorusunu çözer.

Temel dosyalar:

```text
production_manifest.json
assessment_artifact_registry.json
assessment_design_contract.json
```

### Katman 6 — P0 Production Gate

Artifact generation açılmadan önce production planı, canonical artifact kimlikleri, legacy alias mapping, index freshness, retrieval ve fail-closed davranışlar doğrulanır.

P0 PASS şu anlama gelir:

> Üretim için kullanılacak bilgi, ilişkiler ve güvenlik kontrolleri tutarlıdır.

Şu anlama gelmez:

> Materyaller üretildi veya öğretmen tarafından onaylandı.

### Katman 7 — Artifact Generation Engine

Generator kendi pedagojisini veya canonical kimliği uydurmaz. Production registry + contract + doğrulanmış knowledge üzerinden deterministik bir `generation_context` snapshot'ı oluşturur ve yalnız bu bağlamdan draft artifact üretir.

### Katman 8 — Generated Artifact Lifecycle

Generation ile approval ayrıdır:

```text
REVIEW_REQUIRED
   ↓ teacher review
APPROVED
   ↓ explicit freeze
FROZEN
```

Generator doğrudan `APPROVED` veya `FROZEN` üretemez.

### Katman 9 — Runtime Course Package

Uygulama istemcileri canonical knowledge'ı doğrudan okumak zorunda değildir. Deterministik compiler ile read-only runtime SQLite projection üretilir:

```text
canonical knowledge
   ↓ compiler
runtime/course_runtime.sqlite
   ↓
application
```

Runtime source of truth değildir ve user state içermez.

---

## 4. Genel klasör mimarisi

Güncel repository standardı:

```text
<Project>/
├── docs/
├── skill/
│   └── tymm-material-planner/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       ├── tests/
│       └── models/              # local/CI runtime, source of truth değil
│
├── local_sources/               # gerektiğinde gitignored ham kaynaklar
├── local_materials/             # gerektiğinde gitignored yerel materyaller
│
└── courses/
    └── <COURSE_ID>/
        ├── source_manifest.json
        ├── curriculum_map.json
        ├── textbook_map.json
        ├── textbook_forms_index.json
        ├── validation_report.md
        │
        ├── themes/
        │   ├── tema_01/
        │   │   ├── alignment.json
        │   │   ├── gap_analysis.json
        │   │   └── resource_plan.json
        │   ├── tema_02/
        │   └── ...
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
        │   ├── knowledge.sqlite          # derived / rebuildable
        │   ├── index_manifest.json
        │   ├── index_validation_report.md
        │   └── p0_gate_report.json
        │
        ├── runtime/
        │   └── course_runtime.sqlite     # derived / read-only projection
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

Örnek course ID'leri:

```text
TDE_9
TDE_10
TARIH_9
COGRAFYA_9
FIZIK_9
BIYOLOJI_10
```

---

## 5. Global skill ile course knowledge'ı ayırma

Metodoloji course-specific olmamalıdır.

Repository içindeki reusable engine:

```text
skill/tymm-material-planner/
├── SKILL.md
├── references/
├── scripts/
├── tests/
└── models/
```

Derse ait canonical bilgi:

```text
courses/<COURSE_ID>/
```

Kural:

> **Skill = nasıl çalışılacağını bilir. Course knowledge = bu ders için neyin doğru olduğunu bilir.**

Aynı skill farklı course paketlerinde kullanılabilir.

---

## 6. Source manifest ve fingerprint sistemi

Her source için uygun olan metadata tutulur:

```text
source_id
source_group_id                # bundle ise
source_type
input_locator_type
file_path / exact_url
sha256 / content fingerprint
size_bytes                     # local ise
course / grade / school type
program year / edition         # kaynaktan doğrulanabiliyorsa
theme / unit identity          # bundle part ise
authority rank
identity status
verification status
last_validated
```

Git blob SHA gibi repository taşıma kimlikleri tutulabilir; ancak source SHA-256 yerine geçirilmez.

### Cache lifecycle

**Local file:** fingerprint aynı + map `VERIFIED` → cache hit.

**Bundle:** önce completeness; sonra her part fingerprint'i; değişen part yeniden çözümlenebilir ama bütün bundle identity gate tekrar çalışır.

**Remote:** supplied/resolved official URL + content fingerprint/metadata doğrulanır; kimlik/sürüm değişirse stale/review oluşur.

Amaç:

```text
aynı doğrulanmış kaynak → mevcut frozen map kullanılabilir
kaynak değişti          → map/index/runtime review veya rebuild gerekir
```

---

## 7. Annual Course Timeline / Planned Progression Layer

Annual course timeline, öğretim programından türetilen **planlanan öğretim ilerlemesini** temsil eder; öğrenci mastery, başarı veya öğretmenin gerçek konumu değildir.

Ayrım:

```text
planned_position
actual_teacher_position
student_mastery
```

Timeline iki bağımsız katmandır:

1. stable instructional sequence — tema/blok sırası ve doğrulanmış süreler,
2. optional calendar binding — akademik yıl hafta/tarih → sequence position.

Takvim değiştiğinde stable sequence yeniden yazılmaz. Saat, haftalık ders sayısı veya tarih kaynağa dayanmıyorsa fail-closed `null` / `UNRESOLVED` kalır.

---

## 8. Curriculum Map

`curriculum_map.json`, resmî programın yapılandırılmış modelidir.

İçermesi gereken temel veriler:

- tema / ünite ID ve adları
- öğrenme çıktıları
- süreç bileşenleri
- resmî açıklamalar
- ölçme-değerlendirme hükümleri
- farklılaştırma / zenginleştirme hükümleri
- resmî saat bilgileri
- source_id + locator
- verbatim alanlar

Multi-part program kullanılıyorsa her kayıt kendi bundle part `source_id`'sine bağlanmalıdır.

Kural:

> Resmî outcome code veya ifade uydurulmaz. Programdan alınan resmî metin locator ve provenance ile korunur.

---

## 9. Textbook Map

`textbook_map.json`, ders kitabının gerçek öğretim yapısını modeller.

İçerir:

- bölümler
- metin / içerik bölümleri
- etkinlikler
- öğrenci eylemleri
- beklenen öğrenci evidence'ları
- değerlendirme bağlantıları
- source locator

Her etkinlik mümkünse:

```text
activity_id
→ öğrenci ne yapıyor?
→ hangi evidence ortaya çıkıyor?
→ hangi outcome ile ilişkili?
→ hangi değerlendirme aracı bağlı?
```

mantığıyla modellenir.

Remote textbook kullanılması textbook map üretme zorunluluğunu ortadan kaldırmaz; doğrulanmış remote source da canonical map'e dönüştürülür.

---

## 10. Textbook Forms Index

Ders kitabındaki değerlendirme yapıları ayrıca sınıflandırılır.

Örnek enum:

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
```

Kritik ilke:

> Görüntüde “ölçütler + açıklama” tablosu bulunması otomatik olarak analytic rubric demek değildir.

Gerçek analytic rubric için performans düzeyleri ve criterion × level hücre betimleyicileri bulunmalıdır.

---

## 11. Validation ve Freeze

Curriculum map ve textbook map tamamlanınca hemen generation'a geçilmez.

Birlikte doğrulanır:

```text
source_manifest
curriculum_map
textbook_map
textbook_forms_index
```

Kontrol örnekleri:

- source identity ve bundle completeness doğru mu?
- printed/PDF/remote locator doğru mu?
- outcome ve activity ID'leri unique mi?
- form → activity ilişkileri kırık mı?
- assessment type doğru mu?
- synthetic veri canonical fact gibi sunulmuş mu?
- source locator eksik mi?

Başarılı olduğunda map'ler `FROZEN` olur.

Frozen canonical kayıtlar yalnız version bump + revalidation yoluyla değiştirilebilir.

---

## 12. Instructional Needs Analysis

Sistem önce “hangi materyali üretelim?” diye sormaz.

Her öğrenme çıktısı için:

- öğrenci ne yapmalı?
- hangi evidence gözlenmeli?
- hangi yanlış anlama / destek ihtiyacı olabilir?
- program özel bir ölçme aracı veya süreç istiyor mu?

belirlenir.

Bu aşamada materyal türü henüz sonuç değildir.

---

## 13. Program–Textbook Alignment

Coverage enum:

```text
COVERED
PARTIALLY_COVERED
NOT_COVERED
```

Coverage yalnız “kitapta benzeri etkinlik var mı?” değildir.

Birlikte değerlendirilir:

- beklenen öğrenci eylemi
- beklenen evidence
- programın açık ölçme şartı
- kitabın sunduğu değerlendirme yapısı

Örneğin program “dereceli puanlama anahtarı” istiyor, kitap ise yalnız düzeysiz ölçüt tablosu sunuyorsa değerlendirme ihtiyacı `PARTIALLY_COVERED` olabilir.

---

## 14. Gap Analysis

Gap şu soruya cevap verir:

> Programın istediği öğrenci evidence'ını veya değerlendirme yapısını kitap neden tam karşılamıyor?

Her gap mümkünse:

```text
gap_id
outcome_id
theme_id
coverage_status
program_requirement
textbook_provides
remaining_gap
source_locators
```

ile saklanır.

Gap, doğrudan fiziksel artifact kimliği değildir.

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

Kural:

> `GENERATE_*` tek başına `REQUIRED` anlamına gelmez.

Necessity test:

> Bu kaynak çıkarılırsa gerekli öğrenci evidence'ı veya program gereksinimi karşılanamaz mı?

Cevap hayırsa kaynak REQUIRED değildir.

---

## 16. Cross-Theme Assessment Consolidation ve Annual Assessment Stability

Her tema önce bağımsız analiz edilir; assessment gap'leri doğrudan tema başına ayrı rubriğe dönüşmez.

### 16.1 `THEME_CHANGE_ALONE != NEW_RUBRIC`

Tema veya görev adının değişmesi tek başına yeni rubrik gerekçesi değildir. Aynı beceri alanında mümkün olduğunca yıllık kararlı core değerlendirme standardı kullanılır.

### 16.2 GAP INSTANCE ≠ ARTIFACT

İki kavram kesin ayrılır:

- **ASSESSMENT_GAP_INSTANCE:** Belirli tema/outcome bağlamındaki izlenebilir açık.
- **ANNUAL_ASSESSMENT_ARTIFACT:** Bir veya daha fazla gap instance'ı karşılayan canonical artifact.

TDE_9 örneği:

```text
MAT_T2_KONUSMA_RUBRIC ──┐
MAT_T3_KONUSMA_RUBRIC ──┼──> TDE9_KONUSMA_RUBRIC
MAT_T4_KONUSMA_RUBRIC ──┘
```

Legacy `MAT_*` kayıtları provenance/alias olarak korunur; canonical artifact identity olarak kullanılmaz.

### 16.3 7 gap → 3 canonical artifact modeli

TDE_9 production schema 1.1'de:

```text
7 REQUIRED gap instance
        ↓ consolidation
3 canonical artifact
```

Canonical artifact set:

```text
TDE9_KONUSMA_RUBRIC
TDE9_YAZMA_RUBRIC
TDE9_YAZMA_SUREC_KONTROL_LISTESI
```

### 16.4 Annual Core + Task Binding

Yıllık rubrik iki katmandır:

1. **ANNUAL CORE:** kararlı criterion seti, level model ve scoring semantics.
2. **TASK BINDING:** tema/görev başlığı, somut evidence, locator ve göreve özgü notlar.

Task binding çekirdek criterion setini sessizce değiştiremez.

### 16.5 Yeniden kullanım önceliği

```text
REUSE_ANNUAL_CORE
→ REUSE_WITH_TASK_BINDING
→ REUSE_WITH_CRITERION_EXTENSION
→ GENERATE_NEW_ASSESSMENT
```

`GENERATE_NEW_ASSESSMENT` yalnız gerçekten farklı construct + explicit rationale + source locator ile açılır.

### 16.6 Generation öncesi consolidation zorunluluğu

```text
gap_analysis
→ assessment_gap_instances
→ CROSS_THEME_ASSESSMENT_CONSOLIDATION
→ assessment_artifact_registry
→ task_bindings
→ production_manifest
```

Konsolidasyondan geçmemiş gap için generation açılamaz.

---

## 17. School-Based Planning ayrı katmandır

Okul temelli planlama program boşluğu değildir.

Varsayılan:

```text
selection_status = NOT_SELECTED
generation_status = NOT_REQUESTED
origin = pedagogical_recommendation
```

Öğretmen seçmeden canonical production context'e girmez.

---

## 18. Hybrid RAG mimarisi

Genel retrieval sırası:

```text
EXACT
→ STRUCTURED RELATIONS
→ METADATA FILTER
→ FTS5
→ VECTOR
→ CANONICAL RESOLUTION
```

Vector similarity authority, ambiguity veya conflict çözmez.

Natural-language sorgu aday bulabilir; generation kararı yine canonical çözümden gelir.

---

## 19. Stable Entity Key ve Canonical Artifact Identity

Outcome code'larının course genelinde unique olduğu varsayılmaz.

Örnek stable key:

```text
TDE_9::curriculum_outcome::TEMA_02::TDE4.4
```

Tema belirtilmeyen ve birden fazla aday taşıyan sorgu fail-closed `AMBIGUOUS_ENTITY` döndürmelidir.

Assessment artifact için canonical identity:

```text
TDE_9::assessment_artifact::TDE9_KONUSMA_RUBRIC
```

`MAT_T2_KONUSMA_RUBRIC` gibi gap ID'leri yalnız alias/provenance'dır.

---

## 20. Canonical Generation Context

Retrieval sonucu ile generation context farklıdır.

### Retrieval candidates

FTS/vector araması ilgili formu, school-based option'ı, komşu activity'yi veya başka artifact'ı aday olarak bulabilir.

### Generation context snapshot

Generator önce deterministik bir snapshot oluşturur. Minimum alanlar:

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
source versions / fingerprints
knowledge index status
context_hash
```

Kural:

> **retrieval_candidates ≠ generation_context**

ve

> **generation_context hash'lenebilir, reproducible ve audit edilebilir olmalıdır.**

---

## 21. Context Hash, Idempotency ve Revision

Artifact Generation Engine'de canonical identity ile revision ayrılır.

```text
artifact_id = kalıcı kimlik
artifact_revision = içerik revision'ı
context_hash = üretim girdisinin deterministik fingerprint'i
```

### Idempotency

Aynı artifact aynı context hash ile yeniden çalıştırılırsa yeni artifact veya revision yaratılmaz.

Yanlış örnekler:

```text
TDE9_KONUSMA_RUBRIC_2
TDE9_KONUSMA_RUBRIC_NEW
```

### Revision

Canonical context değişmişse yeni revision üretilebilir. Önceki artifact/context snapshot'ı `revisions/` altında korunur.

Bu sayede:

- aynı input ile çift üretim engellenir,
- source/contract değişikliği izlenebilir,
- geçmiş artifact provenance kaybolmaz.

---

## 22. Conflict ve Fail-Closed Davranışı

### Ambiguity

```text
AMBIGUOUS_ENTITY
→ generation blocked
```

### Knowledge conflict

```text
KNOWLEDGE_CONFLICT
→ REVIEW_REQUIRED
→ material_generation_allowed = false
```

### Stale index

```text
INDEX_STALE
→ generation blocked
→ rebuild/revalidation required
```

### Missing / mismatched runtime dependency

Index veya embedding backend/model uyumsuzluğu generation kapısını açamaz.

### Duplicate key

```text
DUPLICATE_CANONICAL_KEY
→ index build FAIL
```

### Legacy artifact identity

```text
MAT_* used as artifact_id
→ BLOCKED
```

---

## 23. Embedding ve Vector Backend

Mevcut referans implementasyon:

```text
base model: intfloat/multilingual-e5-small
runtime artifact: Xenova/multilingual-e5-small
format: ONNX
quantization: quantized
embedding_dimension: 384
vector backend: sqlite-vec
lexical backend: SQLite FTS5
```

Bunlar mimari zorunluluk değil, teknik tercihtir.

Backend/model değişikliği manifestte açıkça versionlanmalı; embedding artifact değişirse index rebuild edilmelidir. Sessiz fallback yasaktır.

---

## 24. Assessment Design Contract

Assessment artifact üretilecekse ortak tasarım sözleşmesi hazırlanır.

Sözleşme şu ayrımı korur:

```text
OFFICIAL_REQUIREMENT
TEXTBOOK_PROVIDES
REMAINING_GAP
SELECTED_IMPLEMENTATION
```

Örnek:

```text
OFFICIAL_REQUIREMENT = “dereceli puanlama anahtarı”
SELECTED_IMPLEMENTATION = analytic_rubric
```

Programın “analytic rubric istediği” iddia edilmez.

### Criterion provenance

İzin verilen origin enum:

```text
official_curriculum
official_textbook
pedagogical_recommendation
```

Criterion kaynağı ile descriptor kaynağı ayrılır. Rubric hücre descriptor'ları pedagojik türetimdir.

### Shared level model

Referans:

```text
LEVEL_4 → ileri düzey gözlenebilir performans
LEVEL_3 → büyük ölçüde doğru/tutarlı
LEVEL_2 → kısmi + belirgin destek ihtiyacı
LEVEL_1 → sınırlı temel performans + yoğun destek ihtiyacı
```

Criterion-neutral genel semantik korunur.

### Scoring

Referans model:

```text
Primary: RAW_MEAN_1_TO_4
Optional: 100-scale display conversion
```

100'lük dönüşüm resmî MEB puanlama kuralı olarak sunulmaz.

---

## 25. Artifact Generator V1

Generator'ın görevi kendi pedagojisini uydurmak değil; canonical production inputlarından kontrollü draft üretmektir.

Minimum pipeline:

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
PEDAGOGICAL_CONTRACT_VALIDATION
  ↓
PROVENANCE_VALIDATION
  ↓
TEACHER_REVIEW_REQUIRED
  ↓
APPROVE
  ↓
FREEZE
```

### Canonical artifact ID

Generator inputu `artifact_id` olmak zorundadır.

Doğru:

```text
TDE9_KONUSMA_RUBRIC
```

Yanlış:

```text
MAT_T2_KONUSMA_RUBRIC
```

### Deterministic validation

LLM'nin kendi çıktısını yalnız yine LLM'e kontrol ettirmek yeterli değildir. Kod seviyesinde en az:

- artifact identity,
- context hash,
- required sections,
- criterion ID'leri,
- 4-level matrix completeness,
- descriptor origin,
- forbidden phrasing,
- scoring dimensions,
- gap provenance,
- teacher review state,
- idempotency

kontrol edilir.

---

## 26. Generation ≠ Approval Lifecycle

Generated artifact'ın varsayılan durumu:

```text
REVIEW_REQUIRED
```

Explicit öğretmen onayı olmadan:

```text
REVIEW_REQUIRED → APPROVED
```

geçişi yapılamaz.

`FROZEN` yalnız `APPROVED` artifact için mümkündür.

```text
GENERATED_DRAFT
→ REVIEW_REQUIRED
→ APPROVED
→ FROZEN
```

Bu lifecycle yalnız metadata tavsiyesi değil; generator API/gate seviyesinde zorlanmalıdır.

---

## 27. Generator V1 Pilot Gate

Yeni generator'ın ilk canlı artifact'ı acceptance test olarak kullanılır.

TDE_9 için pilot:

```text
TDE9_KONUSMA_RUBRIC
```

Pilot sırası:

```text
Generator implementation
        ↓
TDE9_KONUSMA_RUBRIC pilot generation
        ↓
Structural validation
        ↓
Pedagogical contract validation
        ↓
Provenance validation
        ↓
Idempotency regression
        ↓
ENGINEERING_PASS_REVIEW_REQUIRED
        ↓ teacher approval
GENERATOR_V1_GATE = PASS
        ↓
TDE9_YAZMA_RUBRIC
        ↓
TDE9_YAZMA_SUREC_KONTROL_LISTESI
```

Pilot `REVIEW_REQUIRED` iken diğer artifact'ların normal generation sırası kapalı kalır.

Bu gate, “kod teknik olarak çalışıyor” ile “generator öğretmen tarafından kabul edilmiş pilot üzerinden production'a açıldı” durumlarını ayırır.

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
- hak durumu belirsiz uzun içerik embed edilmez,
- attribution izin anlamına gelmez,
- `UNKNOWN_RIGHTS` review gerektirebilir,
- `DO_NOT_USE` içerik generation context'e gövde olarak girmez.

Generated artifact provenance'ı en az şunları korumalıdır:

```text
artifact_id
context_hash
covered_gap_instances
covered_outcomes
source locators
gap provenance
contract/source version metadata
```

---

## 29. Quality Gates

Genel QA katmanları:

```text
Source Identity QA
Curriculum QA
Textbook QA
Version QA
Needs QA
Resource Plan QA
Necessity QA
Alignment / Coverage QA
Production Schema QA
Index / Resolver QA
Runtime Projection QA
Generation Context QA
Structural Artifact QA
Assessment Contract QA
Provenance QA
Accessibility QA
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

## 30. Yeni Bir Ders İçin Kurulum Playbook'u

### Faz 0 — Source resolution

1. Program source'unu tanımla: file / bundle / official remote.
2. Ders kitabı source'unu tanımla.
3. `source_manifest.json` oluştur.
4. Local fingerprint / remote provenance kaydet.
5. Bundle completeness ve source identity doğrula.

### Faz 1 — Curriculum mapping

6. Tema/ünite yapısını çıkar.
7. Outcome ve süreç bileşenlerini verbatim çıkar.
8. Ölçme hükümlerini çıkar.
9. Saat / farklılaştırma / zenginleştirme kayıtlarını çıkar.
10. Source locator ekle.

### Faz 2 — Textbook mapping

11. Kitap bölüm yapısını çıkar.
12. Etkinlikleri ID'le.
13. Öğrenci eylemi ve evidence çıkar.
14. Assessment formlarını sınıflandır.
15. Form ↔ activity bağlarını kur.
16. Locator doğrula.

### Faz 3 — Validation / Freeze

17. Program–kitap kimlik/sürüm uyumunu kontrol et.
18. Form classification doğrula.
19. Broken reference kontrolü yap.
20. Printed/PDF/remote locator doğrula.
21. Frozen map statüsü ver.

### Faz 4 — Instructional analysis

22. Instructional need çıkar.
23. Beklenen evidence tanımla.
24. Textbook coverage değerlendir.
25. Gap analysis üret.
26. Resource plan oluştur.

### Faz 5 — Cross-theme consolidation

27. Tema planlarını birleştir.
28. Duplicate kaynakları deduplicate et.
29. Assessment gap instance'ları konsolide et.
30. Canonical `assessment_artifact_registry` oluştur.
31. Production manifest oluştur.
32. Teaching blocks oluştur.

### Faz 6 — School-based layer

33. School-based saatleri ayrı modelle.
34. Seçenekleri recommendation olarak oluştur.
35. Varsayılan `NOT_SELECTED / NOT_REQUESTED` bırak.

### Faz 7 — Knowledge Index / RAG

36. Canonical entity'leri indexle.
37. Stable entity key üret.
38. FTS5 index oluştur.
39. Embedding üret.
40. Vector index oluştur.
41. Index manifest yaz.
42. Stale/conflict/ambiguity testleri çalıştır.

### Faz 8 — Resolver acceptance

43. Exact ID ve alias testleri.
44. Theme ambiguity testleri.
45. Natural-language semantic testleri.
46. Conflict fixture.
47. Stale fixture.
48. Duplicate key fixture.
49. Canonical resolution accuracy kontrolü.

### Faz 9 — Runtime projection

50. Canonical knowledge → runtime SQLite compiler çalıştır.
51. Source fingerprint doğrula.
52. Orphan/FK/runtime query regression'larını çalıştır.
53. Runtime package'ın user state/vector dependency içermediğini doğrula.

### Faz 10 — Production Contract + P0 Gate

54. Assessment Design Contract oluştur.
55. Provenance şeması belirle.
56. Shared vs task-specific standardı ayır.
57. Production schema ve canonical artifact IDs dondur.
58. `knowledge.sqlite` sıfırdan rebuild et.
59. P0 Production Gate'i PASS et.

### Faz 11 — Artifact Generator

60. Canonical `artifact_id` seç.
61. Deterministik generation context oluştur.
62. Context hash doğrula.
63. Draft üret.
64. Structural + contract + provenance validation çalıştır.
65. Idempotency regression'ı çalıştır.

### Faz 12 — Pilot Acceptance

66. İlk yüksek-değer reusable artifact'ı pilot seç.
67. Pilot generation yap.
68. Generator engineering gate'i çalıştır.
69. `REVIEW_REQUIRED` bırak.
70. Öğretmen review tamamla.
71. Explicit approve/freeze yap.
72. Generator V1 Final Gate PASS olmadan kalan queue'yu açma.

### Faz 13 — Kalan Production Queue

73. Kalan canonical artifact'ları sırayla üret.
74. Her artifact için aynı lifecycle/gate kurallarını uygula.
75. Revision/provenance history'yi koru.

---

## 31. Asla Atlanmaması Gereken Güvenlik Kontrolleri

```text
[ ] Source identity/fingerprint kayıtlı mı?
[ ] Multi-part bundle completeness doğrulandı mı?
[ ] Remote source exact official provenance taşıyor mu?
[ ] Program verbatim alanları locator taşıyor mu?
[ ] Activity/form ID'leri unique mi?
[ ] Assessment form classification doğru mu?
[ ] Outcome stable key'leri uygun scope'ta mı?
[ ] Silent overwrite engelli mi?
[ ] Vector DB source of truth yapılmamış mı?
[ ] Semantic result canonical record'a resolve oluyor mu?
[ ] Ambiguity fail-closed mu?
[ ] Knowledge conflict fail-closed mu?
[ ] INDEX_STALE fixture PASS mı?
[ ] DUPLICATE_CANONICAL_KEY fixture var mı?
[ ] NOT_SELECTED okul seçenekleri generation context'e girmiyor mu?
[ ] GAP INSTANCE ile canonical ARTIFACT ayrılmış mı?
[ ] MAT_* yalnız provenance/alias mı?
[ ] Canonical artifact identity artifact_id mı?
[ ] 7→3 mapping gibi consolidation invariant'ları gate'lenmiş mi?
[ ] P0 gate fresh rebuild yapıyor mu?
[ ] Runtime projection stale/orphan kontrolleri PASS mı?
[ ] retrieval_candidates ile generation_context ayrı mı?
[ ] generation context deterministik ve hash'li mi?
[ ] Aynı context tekrar generation idempotent mi?
[ ] Context değişiminde revision history korunuyor mu?
[ ] Generated artifact otomatik APPROVED/FROZEN olmuyor mu?
[ ] Structural validation deterministik mi?
[ ] Contract/provenance validation var mı?
[ ] Teacher review gate var mı?
[ ] Pilot onaylanmadan sonraki production queue kapalı mı?
```

---

## 32. Minimum Resolver Context Pack

Örnek genel resolver pack:

```json
{
  "course_id": "<COURSE_ID>",
  "query": "...",
  "query_intent": "MATERIAL_GENERATION",
  "resolution_status": "RESOLVED",
  "resolution_mode": ["EXACT", "STRUCTURED", "FTS", "VECTOR"],
  "resolved_entities": [],
  "curriculum_context": [],
  "textbook_context": [],
  "assessment_context": [],
  "alignment_context": [],
  "production_context": [],
  "remaining_gaps": [],
  "pedagogical_recommendations": [],
  "source_fallback_required": false,
  "external_lookup_required": false,
  "conflicts": [],
  "retrieval_trace": []
}
```

Bu resolver pack generator inputu değildir. Generator bundan ve production contracts'tan daha dar bir deterministik `generation_context` snapshot'ı türetir.

---

## 33. Önerilen Entity Metadata Şeması

Index kaydı için genel alanlar:

```text
id
course_id
entity_type
entity_id
theme_id
entity_key
canonical_source_file
canonical_json_path_or_record_key
authority_level
origin
validation_status
freeze_status
printed_page
pdf_page
source_locator
content_hash
source_file_hash
embedding_model
embedding_dimension
semantic_text
embedding
created_at
updated_at
```

`semantic_text` canonical alanlardan deterministik üretilmelidir; serbest LLM özeti source of truth olamaz.

---

## 34. Search Benchmark Standardı

Yeni ders için en az 10–15 Türkçe doğal dil sorgusu hazırlanmalıdır.

Sorgu tipleri:

- exact outcome
- theme + outcome
- gap alias
- canonical artifact ID
- “kitapta ne eksik?”
- “nasıl değerlendireceğim?”
- doğal dil / semantic
- form lookup
- school-based option lookup
- negative analytic rubric query
- ambiguity query
- conflict fixture
- stale fixture

Safety hedefleri:

```text
canonical_resolution_accuracy = 100%
ambiguity_detection_accuracy = 100%
conflict_detection_accuracy = 100%
stale_detection_accuracy = 100%
```

Retrieval Hit@K düşük olabilir; safety metricleri düşük olamaz.

---

## 35. Freeze Kavramı

Sistem tek bir “bitti” bayrağı yerine katman bazlı freeze kullanır.

Örnek:

```text
SOURCE MAPS                  FROZEN
CURRICULUM MAP               FROZEN
TEXTBOOK MAP                 FROZEN
ASSESSMENT FORMS INDEX       FROZEN
THEME ALIGNMENTS             FROZEN
GAP ANALYSIS                 FROZEN
RESOURCE PLANS               FROZEN
PRODUCTION MANIFEST          FROZEN
ASSESSMENT ARTIFACT REGISTRY FROZEN
KNOWLEDGE BASE               FROZEN
KNOWLEDGE RESOLVER           FROZEN
HYBRID RAG                   FROZEN
ASSESSMENT DESIGN CONTRACT   FROZEN
RUNTIME PROJECTION           REBUILDABLE
GENERATED ARTIFACT           PER-ARTIFACT LIFECYCLE
```

Generated artifact için `FROZEN`, yalnız teacher-approved revision'a verilir.

---

## 36. TDE_9 Uygulamasından Çıkan Ana Dersler

1. Ders kitabındaki ölçüt tablosunu yanlışlıkla analytic rubric saymamak.
2. Aynı outcome kodunun farklı temalarda tekrar edebileceğini kabul etmek.
3. Vector similarity ile ambiguity çözmemek.
4. Programın “dereceli puanlama anahtarı” ifadesini “analytic rubric” diye resmîleştirmemek.
5. `NOT_SELECTED` school-based seçenekleri production context'e sokmamak.
6. Retrieval candidate ile generation context'i ayırmak.
7. Rights status icat etmemek.
8. 100'lük dönüşümü resmî kural gibi sunmamak.
9. Generated assessment aracını öğretmen görmeden PASS saymamak.
10. Vector DB'yi source of truth yapmamak.
11. Gap ID ile artifact ID'yi ayırmak; 7 gap'i 7 fiziksel materyale dönüştürmemek.
12. Production schema ile indexer/resolver arasında schema drift oluşmasını CI gate ile engellemek.
13. `knowledge.sqlite` rebuildability'yi gerçek CI gate ile test etmek.
14. Generation context'i deterministik/hash'li snapshot yapmak.
15. Artifact generation'ı idempotent kılmak.
16. Generation, approval ve freeze işlemlerini ayrı lifecycle yapmak.
17. İlk gerçek artifact'ı generator acceptance testi olarak kullanmak.
18. Tek-PDF varsayımından kaçınmak; multi-part ve official remote source'ları canonical source modeline dahil etmek.

---

## 37. Sistemin En Kısa Özeti

Mimari beş şeyi birbirinden ayırır:

```text
1. SOURCE TRUTH
   Program + Ders Kitabı + Source Manifest

2. CANONICAL KNOWLEDGE
   Curriculum/Textbook Maps + Alignment + Gap + Resource Plan

3. FIND / RESOLVE
   SQLite + FTS5 + Vector + Knowledge Resolver

4. PRODUCTION CONTRACT
   Production Manifest + Artifact Registry + Design Contract + P0 Gate

5. GENERATE / REVIEW
   Generation Context + Artifact Generator + Validation + Teacher Review + Freeze
```

Başka bir ifadeyle:

> **Yapay zekâ kararın kaynağı değildir. Yapay zekâ, doğrulanmış bilgi tabanı ve açık üretim sözleşmeleri üzerinde çalışan kontrollü üretim motorudur.**

---

## 38. Runtime Course Package / Application Projection Layer

Canonical knowledge doğrudan uygulama tüketim şeması değildir.

```text
canonical knowledge → deterministic compiler → runtime SQLite → application
```

Runtime package:

- source of truth değildir,
- derived/rebuildable'dır,
- read-only course knowledge projection'dır,
- user state içermez,
- RAG/vector database değildir,
- embedding/model runtime gerektirmez,
- stable canonical ID ve source locator/provenance taşır.

Canonical dosyalar değiştiğinde fingerprint üzerinden `RUNTIME_STALE` üretilebilmelidir.

---

## 39. Güncel TDE_9 Implementasyon Durumu — 2026-08-18

Mevcut `main` durumu:

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

İlk pilot artifact'ın structural, contract, provenance ve idempotency kontrolleri geçmiştir. Bu teknik PASS öğretmen onayı değildir. Pilot açıkça `APPROVED`/`FROZEN` durumuna geçirilmeden kalan iki canonical artifact'ın normal production sırası açılmaz.

---

# Ek A — Yeni Ders İçin Kısa Başlangıç Şablonu

```text
COURSE_ID = <ör. TDE_10>

1.  courses/<COURSE_ID>/source_manifest.json
2.  source input: SINGLE_FILE | MULTI_PART_SOURCE_BUNDLE | OFFICIAL_REMOTE_*
3.  curriculum_map.json
4.  textbook_map.json
5.  textbook_forms_index.json
6.  validation_report.md
7.  themes/*/alignment.json
8.  themes/*/gap_analysis.json
9.  themes/*/resource_plan.json
10. production/consolidated_resource_plan.json
11. production/assessment_artifact_registry.json
12. production/production_manifest.json
13. production/assessment_design_contract.json
14. index/knowledge.sqlite
15. index/index_manifest.json
16. resolver safety tests
17. runtime/course_runtime.sqlite
18. P0 Production Gate
19. generation_context
20. Artifact Generator
21. pilot generation + Generator V1 Gate
22. Teacher Review
23. approve/freeze
24. remaining production queue
```

---

# Ek B — “Üretime Hazır mı?” Kontrolü

Bir course için aşağıdaki cümleyi güvenle söyleyebiliyorsan **production input layer** hazırdır:

> “Bu artifact'ın hangi resmî program gereksinimini karşıladığı, ders kitabında hangi karşılığın bulunduğu, geriye hangi doğrulanmış boşluğun kaldığı, neden REQUIRED olduğu, hangi canonical artifact kimliğine konsolide edildiği, hangi generation context ve contract ile üretileceği ve hangi QA gate'lerinden geçeceği sistem tarafından tek tek gösterilebiliyor.”

Bu cümledeki halkalardan biri eksikse P0 production gate açılmamalıdır.

Artifact'ın gerçekten production-ready/frozen kabul edilmesi için ayrıca:

```text
P0_GATE = PASS
+ deterministic generation context
+ structural/contract/provenance validation PASS
+ teacher review APPROVED
+ explicit FROZEN lifecycle
```

gerekir.
