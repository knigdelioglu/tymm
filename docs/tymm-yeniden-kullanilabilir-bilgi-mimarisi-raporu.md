# TYMM İçerik Üretim Sistemi — Yeniden Kullanılabilir Bilgi Mimarisi ve Kurulum Raporu

**Amaç:** Bu rapor, 9. sınıf Türk Dili ve Edebiyatı (TDE_9) için kurulan TYMM uyumlu bilgi tabanı + RAG + materyal üretim mimarisini başka ders ve sınıflarda aynı güvenlik ve izlenebilirlik düzeyiyle yeniden kurabilmek için hazırlanmıştır.

**Ana fikir:** Yapay zekâya doğrudan “programı ve kitabı oku, materyal üret” denmez. Önce resmî kaynaklar yapılandırılmış ve doğrulanmış bir bilgi tabanına dönüştürülür; ardından yalnız gerekli bağlam resolver aracılığıyla seçilir; üretim en son aşamada ve sözleşmeli kurallarla yapılır.

---

## 1. Sistemin temel prensibi

Sistemin değişmez çalışma sırası:

```text
PROGRAMI OKU
   ↓
DERS KİTABINI OKU
   ↓
ÖĞRENME İÇİN NE GEREKTİĞİNİ BELİRLE
   ↓
KİTAPTA KARŞILIĞI VAR MI KONTROL ET
   ↓
BOŞLUĞU BELİRLE
   ↓
YALNIZ GEREKLİ EKSİĞİ PLANLA / ÜRET
   ↓
TYMM + KAYNAK + QA DENETİMİ
```

En kritik kural:

> **Önce ne gerektiğini belirle, sonra kitapta olup olmadığına bak, sonra üret.**

Bu sıra tersine çevrilmez. Ders kitabında bir etkinliğin bulunması, o etkinliğin program gereksinimini tam karşıladığı anlamına gelmez; aynı şekilde kitapta bir şeyin eksik görünmesi de otomatik olarak yeni materyal üretme gerekçesi değildir.

---

## 2. Kaynak otoritesi

Bilgi kaynaklarının yetki sırası:

1. **Kullanıcı tarafından verilen resmî öğretim programı** — normatif birincil kaynak.
2. **Kullanıcı tarafından verilen resmî ders kitabı** — sınıf içi uygulama ve içerik çıpası.
3. Kullanıcı tarafından verilen diğer resmî MEB belgeleri.
4. Eksik, çelişkili veya güncelliği belirsiz durumlarda resmî MEB/TYMM doğrulaması.
5. Yalnız gerçek bir boşluk saptandıktan sonra güvenilir haricî kaynaklar.

Sistem hiçbir zaman kullanıcı tarafından verilen resmî program veya kitabı sessizce internetten bulunan başka bir sürümle değiştirmez.

---

## 3. Sistemin katmanları

Mimariyi bir kütüphane benzetmesiyle düşünmek en kolay yoldur.

### Katman 1 — Asıl belgeler

Program PDF ve ders kitabı PDF, “ıslak imzalı asıl evrak” gibidir.

```text
sources/
├── <course>_program.pdf
└── <course>_textbook.pdf
```

Bu belgeler nihai hakemdir. Yapılandırılmış bilgiyle kaynak arasında çelişki çıkarsa kaynağa dönülür.

### Katman 2 — Frozen knowledge base

PDF’ler doğrudan vector DB’ye atılmaz. Önce doğrulanmış, anlamlı kayıtlara dönüştürülür.

Örnek varlıklar:

- tema / ünite
- öğrenme çıktısı
- süreç bileşeni
- ders kitabı bölümü
- etkinlik
- değerlendirme formu
- program-kitap hizalama kaydı
- kalan boşluk
- öğretimsel ihtiyaç
- kaynak planı
- üretilecek materyal
- öğretim bloğu
- okul temelli planlama seçeneği

Bu JSON kayıtları **source of truth** kabul edilir.

### Katman 3 — Arama indeksi

`knowledge.sqlite` canonical bilgi değildir; yalnızca arama için türetilmiş cache’dir.

İçinde:

- structured metadata
- FTS5 lexical search
- sqlite-vec vector search
- embedding’ler

bulunur.

Bu dosya silinirse canonical JSON’lardan yeniden oluşturulabilir.

### Katman 4 — Knowledge Resolver

Arama motoru adayları bulur; **Resolver hangisinin gerçekten kullanılabileceğine karar verir.**

Resolver görevleri:

- exact ID çözümleme
- tema / ders / varlık kapsamı çözümleme
- ilişki takibi
- authority sıralaması
- FTS + vector retrieval
- canonical record’a geri çözümleme
- ambiguity tespiti
- conflict tespiti
- stale index kontrolü
- minimum sufficient context pack üretimi

### Katman 5 — Üretim sözleşmeleri

Bilgi tabanı “ne gerekli?” sorusunu çözer.

Assessment Design Contract gibi sözleşmeler ise “nasıl üretilecek?” sorusunu standardize eder.

### Katman 6 — Materyal üretimi

Üretici model tüm knowledge klasörünü okumaz. Yalnız Resolver’ın oluşturduğu **canonical_generation_context** paketini ve ilgili tasarım sözleşmesini görür.

---

## 4. Genel klasör mimarisi

Önerilen proje yapısı:

```text
<Project>/
├── sources/
│   ├── <COURSE_ID>_program.pdf
│   └── <COURSE_ID>_textbook.pdf
│
└── knowledge/
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
        │   ├── assessment_design_contract.json
        │   └── assessment_design_contract_report.md
        │
        └── index/
            ├── knowledge.sqlite
            ├── index_manifest.json
            └── index_validation_report.md
```

Buradaki `<COURSE_ID>` örnekleri:

```text
TDE_9
TDE_10
TARIH_9
COGRAFYA_9
FIZIK_9
BIYOLOJI_10
```

---

## 5. Global skill ile proje bilgisını ayırma

Metodoloji course-specific olmamalıdır.

Canonical global skill:

```text
~/.gemini/config/skills/tymm-material-planner/
├── SKILL.md
├── references/
├── scripts/
├── tests/
├── models/
└── .venv/
```

Burada yalnız yöntem, resolver, indexer, QA ve genel pedagojik kurallar bulunur.

Derse ait bilgi ise proje klasöründe kalır:

```text
<Project>/knowledge/<COURSE_ID>/
```

Kural:

> **Skill = nasıl çalışılacağını bilir. Knowledge = bu ders için neyin doğru olduğunu bilir.**

Bu ayrım sayesinde aynı skill TDE_9, TDE_10, Tarih 9 veya başka bir dersle çalışabilir.

---

## 6. Kaynak manifesti ve fingerprint sistemi

## Annual Course Timeline / Planned Progression Layer

Yeniden kullanılabilir bilgi mimarisine eklenen annual course timeline katmanı, öğretim programından türetilen **planlanan öğretim ilerlemesini** temsil eder; öğrenci öğrenmesi, mastery, başarı veya gerçek öğretmen konumu değildir. `planned_position`, `actual_teacher_position` ve `student_mastery` birbirinden ayrıdır; öğretmen override'ı course knowledge içine yazılmaz.

Timeline iki bağımsız katmanda modellenir: (1) dersin kalıcı stable instructional sequence katmanı (tema ve blok sırası, doğrulanmış zaman bilgileri) ve (2) akademik yıla bağlı, isteğe bağlı calendar binding katmanı (hafta/tarih → sequence position). Takvim değiştiğinde stable sequence yeniden yazılmaz; takvim verisi curriculum truth'e sessizce yükseltilmez.

Saat, haftalık ders sayısı, blok süresi veya tarih kaynağa dayanmıyorsa fail-closed olarak `null`/`UNRESOLVED` kalır. Uygulamalar bu katmandan deterministik `planned_position` çözebilir; tarih bağlama ise yalnızca doğrulanmış resmî akademik takvim ve ders çizelgesi bulunduğunda yapılır.

Her kaynak dosyanın:

- source_id
- file_path
- file hash / sha256
- sürüm / başlık bilgisi
- validation status

bilgileri `source_manifest.json` içinde tutulur.

Amaç:

```text
aynı kaynak → mevcut frozen map kullanılabilir
kaynak değişti → INDEX_STALE / map review gerekir
```

Bir kaynağın hash’i değiştiğinde eski index authoritative olarak kullanılmaz.

---

## 7. Curriculum Map

`curriculum_map.json`, resmî programın yapılandırılmış modelidir.

İçermesi gereken temel veriler:

- tema / ünite ID ve adları
- öğrenme çıktıları
- süreç bileşenleri
- resmî açıklamalar
- ölçme-değerlendirme hükümleri
- farklılaştırma / zenginleştirme hükümleri
- resmî saat bilgileri
- sayfa / locator
- verbatim alanlar

Kural:

> Resmî outcome code veya ifade uydurulmaz. Programdan alınan resmî metin, locator ile korunur.

---

## 8. Textbook Map

`textbook_map.json`, ders kitabının gerçek öğretim yapısını modeller.

İçerir:

- bölümler
- metinler / içerik bölümleri
- etkinlikler
- öğrenci eylemleri
- beklenen öğrenci kanıtları
- değerlendirme bağlantıları
- sayfa / locator

Her etkinlik mümkünse şu mantıkla ifade edilir:

```text
activity_id
→ öğrenci ne yapıyor?
→ hangi kanıt ortaya çıkıyor?
→ hangi outcome ile ilişkili olabilir?
→ hangi değerlendirme aracı bağlı?
```

---

## 9. Textbook Forms Index

Ders kitabındaki değerlendirme yapıları ayrıca indekslenir.

Örnek schema enum:

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

Bir aracın analytic rubric sayılabilmesi için gerçek performans düzeyleri ve düzey/hücre betimleyicileri bulunmalıdır.

Yanlış sınıflandırma sonraki gap analysis’i bozar.

---

## 10. Validation ve freeze aşaması

Curriculum map ve textbook map tamamlandıktan sonra hemen materyal üretimine geçilmez.

Önce:

```text
source_manifest
curriculum_map
textbook_map
textbook_forms_index
```

birlikte doğrulanır.

Kontrol örnekleri:

- kaynak sayfa numarası doğru mu?
- PDF page / printed page ayrımı doğru mu?
- outcome sayısı doğru mu?
- etkinlik ID’leri unique mi?
- form ID’leri unique mi?
- form → activity ilişkileri kırık mı?
- assessment type doğru mu?
- synthetic veri var mı?
- locator eksik mi?

Başarılı olduğunda map’ler **FROZEN** olur.

Frozen canonical kayıtlar sessizce değiştirilemez.

Çelişki çıkarsa:

```text
map_conflict
→ REVIEW_REQUIRED
```

---

## 11. Instructional Needs Analysis

Sistem önce “hangi materyali üretelim?” diye sormaz.

Önce her öğrenme çıktısı için:

- öğrenci ne yapmalı?
- hangi kanıt görünmeli?
- hangi yanlış anlamalar / destek ihtiyaçları olabilir?
- program özel bir ölçme aracı istiyor mu?

belirlenir.

Bu aşamada materyal türü henüz sonuç değildir.

---

## 12. Program–Textbook Alignment

Her target için program ve kitap karşılaştırılır.

Coverage enum:

```text
COVERED
PARTIALLY_COVERED
NOT_COVERED
```

Önemli:

Coverage yalnız “kitapta buna benzeyen etkinlik var mı?” demek değildir.

Şunlar birlikte değerlendirilir:

- beklenen öğrenci eylemi
- beklenen kanıt
- programın açık ölçme şartı
- gerekli öğretmen değerlendirme yapısı

Örneğin öğrenci yazma görevini kitapta yapıyor olabilir ama program açıkça “dereceli puanlama anahtarı” istiyorsa ve kitapta yalnız düzeysiz ölçüt tablosu varsa ilgili değerlendirme çıktısı `PARTIALLY_COVERED` olabilir.

---

## 13. Gap Analysis

Alignment sonucunda yalnız gerçek boşluklar çıkarılır.

Gap şu soruya cevap verir:

> Programın istediği öğrenci kanıtını veya değerlendirme yapısını kitap neden tam karşılamıyor?

Gap “kitapta benim hoşuma gitmeyen bir şey var” anlamına gelmez.

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

---

## 14. Resource Plan

Her ihtiyaca priority ve production decision atanır.

### Priority

```text
REQUIRED
RECOMMENDED
OPTIONAL
NOT_NEEDED
```

### Production Decision

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

> `GENERATE_*` kararı tek başına REQUIRED anlamına gelmez.

Necessity test:

> “Bu kaynak çıkarılırsa gerekli öğrenci kanıtı veya program gereksinimi karşılanamaz mı?”

Cevap hayırsa kaynak REQUIRED değildir.

---

## 15. Cross-Theme Assessment Consolidation ve Annual Assessment Stability

Her tema başlangıçta ayrı analiz edilir; ancak tespit edilen ölçme-değerlendirme açıkları doğrudan tema bazlı münferit rubrik üretimine yönlendirilmez. Temalar arası çapraz konsolidasyon ve yıllık kararlılık mimarisi işletilir.

### A. Temel Pedagojik İlke: `THEME_CHANGE_ALONE != NEW_RUBRIC`

Öğrenci yıl boyunca aynı sınıf düzeyi ve temel beceri alanında (konuşma/sunum, yazma) mümkün olduğunca aynı temel ölçütlerle değerlendirilmelidir. 
- Tema adının veya etkinlik görevinin değişmesi tek başına yeni bir rubrik üretme gerekçesi olamaz.
- Öğrencinin yıl boyunca karşılaşacağı başarı çıtası kararlı kalmalı, bilişsel yük ve kafa karışıklığı önlenmelidir.

### B. GAP INSTANCE ≠ ARTIFACT Ayrımı

Mimaride iki kavram kesin çizgilerle ayrılır:
- **`ASSESSMENT_GAP_INSTANCE`**: Belirli bir tema ve öğrenme çıktısında saptanan ölçme açığı (izlenebilirlik, provenance ve audit kaydı).
- **`ANNUAL_ASSESSMENT_ARTIFACT`**: Bir veya daha fazla gap instance'ı karşılayan gerçek, konsolide fiziksel öğretmen ve öğrenci materyali.

Örneğin TDE 9 için Tema 2, 3 ve 4'te ortaya çıkan 3 ayrı konuşma gap'i (`MAT_T2_KONUSMA_RUBRIC`, `MAT_T3_KONUSMA_RUBRIC`, `MAT_T4_KONUSMA_RUBRIC`) 3 ayrı materyal üretmez; tek bir `TDE9_KONUSMA_RUBRIC` yıllık çekirdek artifact'ına konsolide edilir.

```text
[GAP_T2_KONUSMA] ──┐
[GAP_T3_KONUSMA] ──┼──> [TDE9_KONUSMA_RUBRIC] (Annual Core Artifact)
[GAP_T4_KONUSMA] ──┘
```

Eski gap kayıtları audit kanıtı olarak korunur; ancak üretim kuyruğu `assessment_artifact_registry.json` üzerinden çalışır.

### C. Core Rubric + Task Binding Katmanları ve Normalized Shared Constructs

Cross-theme konsolidasyon, "temalardaki kriterler kelimesi kelimesine aynıdır" varsayımına değil; farklı temalardaki resmî ölçütlerin üst düzey kanıtlanabilir ortak boyutlar altında birleştirildiği **`NORMALIZED_SHARED_CONSTRUCT`** yaklaşımına dayanır.

Yıllık rubrik iki katmandan oluşur:
1. **ANNUAL CORE (Kararlı Çekirdek)**: Kanıtlanabilir ortak temel ölçüt seti (Konuşmada 5, Yazmada 4 construct-pure ölçüt), 4 düzeyli criterion-neutral semantik, ham ortalama (1.00-4.00) ve standart geri bildirim modeli (`EVIDENCE -> EFFECT -> NEXT STEP`).
2. **TASK BINDING (Görev Bağlamı)**: İlgili temanın atölye başlığı, gözlenen somut öğrenci eylemi, sayfa locator'ları ve göreve özgü uygulama notları (örn. şiir ritim/ahengi, infografik görsel modülleri, sunumda slayt kullanımı).

Task binding katmanı çekirdek ölçüt setini bozamaz veya değiştiremez.

### D. Yeniden Kullanım Öncelik Sırası, Criterion Extension ve Kapsam (Scope) Ayrımı

Değerlendirme açığında şu hiyerarşi zorunludur:
1. `REUSE_ANNUAL_CORE`
2. `REUSE_WITH_TASK_BINDING`
3. `REUSE_WITH_CRITERION_EXTENSION`
4. `GENERATE_NEW_ASSESSMENT`

Ayrıca araç kapsamlarında **`ANNUAL_CORE` ≠ `REUSABLE_ACROSS_THEMES`** ayrımı esastır:
- **`ANNUAL_CORE`**: Yıl boyu her temada notlandırma standardı oluşturan ve birden fazla temada REQUIRED açığı kapatan rubriklerdir (`TDE9_KONUSMA_RUBRIC`, `TDE9_YAZMA_RUBRIC`).
- **`REUSABLE_PROCESS_SUPPORT`**: Tek bir temada (`TEMA_04 / TDE4.1`) REQUIRED gap anchor'ına sahip olan, ancak 5 evrensel aşaması tüm temalarda biçimlendirici olarak serbestçe tekrar kullanılabilen süreç araçlarıdır (`TDE9_YAZMA_SUREC_KONTROL_LISTESI`).

Temada resmî ek bir zorunlu ölçüt varsa önce `REUSE_WITH_CRITERION_EXTENSION` değerlendirilir. `GENERATE_NEW_ASSESSMENT` yalnız resmî requirement gerçekten farklı bir construct ölçüyorsa ve explicit rationale + source locator ile fail-closed olarak uygulanabilir.

### E. Generation Öncesi Konsolidasyon Zorunluluğu

Pipeline akışı:

```text
gap_analysis → assessment_gap_instances → CROSS_THEME_ASSESSMENT_CONSOLIDATION → annual_assessment_artifact_registry → task_bindings → generation_context → material_generation
```

Konsolidasyondan geçmemiş hiçbir gap instance için materyal üretimi açılamaz.

---

## 16. School-Based Planning ayrı bir katmandır

Okul temelli planlama program boşluğu değildir.

Bu nedenle:

- REQUIRED değildir
- production manifest’e otomatik girmez
- öğretmen seçmeden üretilmez

Durumlar:

```text
selection_status = NOT_SELECTED
generation_status = NOT_REQUESTED
origin = pedagogical_recommendation
```

Vector search bu kayıtları aday olarak bulabilir; fakat seçilmedikçe canonical generation context’e giremez.

---

## 17. RAG mimarisi

### 17.1 Structured Retrieval

İlk tercih exact/structured çözümlemedir.

Örneğin:

```text
Tema 2 + TDE4.4
```

biliniyorsa vector search’e ihtiyaç yoktur.

### 17.2 FTS5

Kelime / exact phrase tabanlı arama sağlar.

### 17.3 Vector Search

Doğal dilde semantik benzerlik sağlar.

Örneğin:

```text
“şiir yazarken öğrenciyi nasıl değerlendireceğim?”
```

ifadesi doğrudan materyal ID’sini söylemese bile ilgili Tema 2 yazma zincirine ulaşabilir.

### 17.4 Hybrid Retrieval

Genel sıra:

```text
EXACT
→ STRUCTURED RELATIONS
→ METADATA FILTER
→ FTS5
→ VECTOR
→ CANONICAL RESOLUTION
```

Vector skor hiçbir zaman authority veya conflict çözmez.

---

## 18. Stable entity key

Outcome code’larının course genelinde unique olduğu varsayılmaz.

Örneğin aynı `TDE4.4` birden fazla temada bulunuyorsa stable key tema scoped olmalıdır:

```text
TDE_9::curriculum_outcome::TEMA_02::TDE4.4
```

Tema belirtilmeden yalnız:

```text
TDE4.4
```

sorgulanırsa Resolver tek kayıt seçmez.

Beklenen:

```text
AMBIGUOUS_ENTITY
```

ve aday temaları döndürür.

Silent overwrite ve silent ambiguity çözümü yasaktır.

---

## 19. Canonical generation context

Retrieval sonucu ile üretim bağlamı farklıdır.

### Retrieval Candidates

FTS/vector araması şunları bulabilir:

- ilgili form
- school-based option
- komşu activity
- başka materyal
- enrichment kaydı

Bunların hepsi yalnız adaydır.

### Canonical Generation Context

Üretici modele yalnız doğrulanmış minimum paket verilir.

Rubrik için örnek:

```text
material
outcome(s)
official requirement
remaining gap
textbook form
textbook activity
criterion sources
source locators
selected implementation
assessment contract profile
```

Checklist için:

```text
material
outcome
official process requirement
remaining gap
writing-process activity/evidence
process-stage sources
source locators
checklist contract profile
```

Kural:

> **retrieval_candidates ≠ canonical_generation_context**

---

## 20. Conflict ve fail-closed davranışı

Sistem belirsizliği gizlemek yerine durmalıdır.

### Ambiguity

```text
AMBIGUOUS_ENTITY
→ generation blocked
```

### Knowledge conflict

Örneğin alignment `COVERED`, gap analysis ise aynı target için ciddi `remaining_gap` iddia ediyorsa:

```text
KNOWLEDGE_CONFLICT
→ REVIEW_REQUIRED
→ material_generation_allowed = false
```

### Stale index

Source hash değiştiyse:

```text
INDEX_STALE
→ semantic index authoritative kullanılamaz
```

### Duplicate key

```text
DUPLICATE_CANONICAL_KEY
→ index build FAIL
```

---

## 21. Embedding ve vector backend

Mevcut örnek implementasyon:

```text
base model: intfloat/multilingual-e5-small
runtime artifact: Xenova/multilingual-e5-small
format: ONNX
quantization: quantized
embedding_dimension: 384
vector backend: sqlite-vec
lexical backend: SQLite FTS5
```

Bu değerler mimari zorunluluk değil, şu anki teknik tercihtir.

Yeni ortamda başka bir backend/model kullanılabilir; fakat değişiklik manifestte açıkça kaydedilmelidir.

Sessiz backend fallback yasaktır.

Index manifestte en az:

```text
base_embedding_model
runtime_model_repository
runtime_model_file
runtime_format
quantization
embedding_dimension
pooling_strategy
normalization
query_prefix
passage_prefix
model_file_sha256
vector_backend
vector_backend_version
sqlite_version
```

saklanmalıdır.

Model artifact değişirse vector index rebuild edilmelidir.

---

## 22. Assessment Design Contract

Ölçme materyali üretilecekse önce ortak tasarım sözleşmesi hazırlanmalıdır.

Sözleşme şu ayrımı korur:

```text
OFFICIAL_REQUIREMENT
TEXTBOOK_PROVIDES
REMAINING_GAP
SELECTED_IMPLEMENTATION
```

Örneğin:

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

Etkinlikten türetilen bilgi `official_textbook` olur; ayrıntı `derived_from` içinde tutulur.

### Rubric level model

Ortak düzey modeli criterion-neutral olmalıdır.

Örnek:

```text
LEVEL_4 → eksiksiz, doğru, tutarlı, bağımsız
LEVEL_3 → büyük ölçüde doğru ve tutarlı
LEVEL_2 → kısmi, belirgin eksiklikler, destek ihtiyacı
LEVEL_1 → sınırlı temel performans, yoğun destek ihtiyacı
```

“özgün”, “estetik”, “etkileyici” gibi nitelikler yalnız ilgili criterion gerçekten bunu ölçüyorsa descriptor’a girer.

### Scoring

Örnek mevcut standard:

```text
Primary: RAW_MEAN_1_TO_4
Optional: 100-scale display conversion
```

100’lük dönüşüm resmî MEB kuralı olarak sunulmaz.

### Teacher Review

Her generated assessment material:

```text
teacher_review_required = true
post_generation_status = REVIEW_REQUIRED
```

olmalıdır.

---

## 23. Rights / provenance sistemi

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

Yeni ve rastgele rights status üretilmez.

Kurallar:

- uzun telifli metinler artifact içine yeniden basılmaz
- locator tercih edilir
- hak durumu belirsiz uzun içerik embed edilmez
- attribution izin anlamına gelmez
- UNKNOWN_RIGHTS → review gerekebilir
- DO_NOT_USE → embed edilmez

---

## 24. Quality Gates

Genel QA katmanları:

```text
Curriculum QA
Textbook QA
Version QA
Needs QA
Resource Plan QA
Necessity QA
Alignment / Coverage QA
Content QA
Assessment QA
Differentiation QA
Accessibility QA
Copyright QA
Safety QA
Privacy QA
Teacher Review
```

Durumlar:

```text
PASS
FAIL
REVIEW
N/A
```

Nihai mantık:

```text
any FAIL → BLOCKED
no FAIL + at least one REVIEW → REVIEW_REQUIRED
all applicable PASS/N/A → PASS
```

---

## 25. Yeni bir ders için kurulum playbook’u

Aynı sistemi başka ders/sınıf için kurarken önerilen sıra:

### Faz 0 — Kaynak hazırlığı

1. Resmî programı ekle.
2. Resmî ders kitabını ekle.
3. `source_manifest.json` oluştur.
4. SHA-256 fingerprint üret.

### Faz 1 — Curriculum mapping

5. Tema/ünite yapısını çıkar.
6. Outcome ve süreç bileşenlerini verbatim çıkar.
7. Ölçme hükümlerini çıkar.
8. Saat / farklılaştırma / zenginleştirme kayıtlarını çıkar.
9. Locator ekle.

### Faz 2 — Textbook mapping

10. Kitap bölüm yapısını çıkar.
11. Etkinlikleri ID’le.
12. Her etkinliğin öğrenci eylemi ve evidence’ını çıkar.
13. Değerlendirme formlarını sınıflandır.
14. Form ↔ activity bağlantılarını kur.
15. Locator doğrula.

### Faz 3 — Validation / Freeze

16. Program–kitap sürüm uyumunu kontrol et.
17. Form classification doğrula.
18. Broken reference kontrolü yap.
19. Printed/PDF page mapping doğrula.
20. Frozen map statüsü ver.

### Faz 4 — Instructional analysis

21. Her outcome için instructional need çıkar.
22. Gereken öğrenci evidence’ını tanımla.
23. Kitap coverage’ını değerlendir.
24. Gap analysis üret.
25. Resource plan oluştur.

### Faz 5 — Cross-theme consolidation

26. Tema planlarını birleştir.
27. Duplicate resource’ları deduplicate et.
28. Priority ve production decision’ları dondur.
29. Production manifest oluştur.
30. Teaching blocks oluştur.

### Faz 6 — School-based layer

31. Varsa okul temelli planlama saatlerini ayrı modelle.
32. Seçenekleri recommendation olarak oluştur.
33. Varsayılan NOT_SELECTED / NOT_REQUESTED bırak.

### Faz 7 — Knowledge Index / RAG

34. Canonical entity’leri indexle.
35. Stable entity key üret.
36. FTS5 index oluştur.
37. Embedding üret.
38. Vector index oluştur.
39. Index manifest yaz.
40. Stale/conflict/ambiguity testleri çalıştır.

### Faz 8 — Resolver acceptance

41. Exact ID testleri.
42. Tema ambiguity testleri.
43. Natural-language semantic testleri.
44. Conflict fixture.
45. Stale fixture.
46. Duplicate key fixture.
47. Canonical resolution accuracy kontrolü.

### Faz 9 — Production contract

48. Üretilecek materyal ailesine uygun contract oluştur.
49. Provenance şeması belirle.
50. Shared vs theme-specific standardı ayır.
51. Generation context completeness doğrula.
52. Rights enum consistency kontrolü yap.
53. Generation gate aç.

### Faz 10 — Material generation

54. Her materyal için Resolver’dan canonical_generation_context üret.
55. Yalnız ilgili contract + minimum context ile materyali üret.
56. QA çalıştır.
57. Teacher Review = REVIEW_REQUIRED bırak.
58. Öğretmen onayından sonra final statü ver.

---

## 26. Yeni ders kurulumunda asla atlanmaması gereken kontroller

Aşağıdakiler “olursa iyi olur” değil, mimari güvenlik kontrolleridir:

```text
[ ] Kaynak hash’leri kayıtlı mı?
[ ] Program verbatim alanları locator taşıyor mu?
[ ] Kitap activity ID’leri unique mi?
[ ] Assessment form type gerçekten doğru mu?
[ ] Outcome code’ları theme scoped mı?
[ ] Silent overwrite engelli mi?
[ ] Vector DB source of truth yapılmamış mı?
[ ] Semantic result canonical record’a resolve oluyor mu?
[ ] Ambiguity fail-closed mu?
[ ] Knowledge conflict fail-closed mu?
[ ] INDEX_STALE testi gerçek fixture ile geçiyor mu?
[ ] DUPLICATE_CANONICAL_KEY testi var mı?
[ ] NOT_SELECTED okul seçenekleri production context’e girmiyor mu?
[ ] retrieval_candidates ile canonical_generation_context ayrı mı?
[ ] rights enum canonical mı?
[ ] teacher review gate var mı?
[ ] material generation yalnız REQUIRED + resolved + conflict-free context ile açılıyor mu?
```

---

## 27. Minimum Resolver context pack şeması

Örnek genel context pack:

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

Material generation aşamasında bundan da daha küçük bir `canonical_generation_context` türetilmesi tercih edilir.

---

## 28. Önerilen entity metadata şeması

Her index kaydı için genel alanlar:

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

`semantic_text` deterministik olarak canonical alanlardan üretilmelidir; LLM’in serbestçe uydurduğu özet kullanılmamalıdır.

---

## 29. Search benchmark standardı

Yeni ders için en az 10–15 Türkçe doğal dil sorgusu hazırlanmalıdır.

Sorgu tipleri:

- exact outcome
- theme + outcome
- “kitapta ne eksik?”
- “nasıl değerlendireceğim?”
- doğal dil / semantik
- form lookup
- school-based option lookup
- negative analytic rubric query
- ambiguity query
- conflict fixture
- stale fixture

Ölçümler:

```text
Hit@1
Hit@3
Hit@5
canonical_resolution_accuracy
ambiguity_detection_accuracy
conflict_detection_accuracy
stale_detection_accuracy
```

Safety metriclerinde hedef:

```text
canonical_resolution_accuracy = 100%
ambiguity_detection_accuracy = 100%
conflict_detection_accuracy = 100%
stale_detection_accuracy = 100%
```

Retrieval Hit@K düşük olabilir; fakat canonical safety testleri düşük olamaz.

---

## 30. Freeze kavramı

Sistem “bitti” demek yerine katman bazlı freeze kullanır.

Örnek:

```text
SOURCE MAPS                  FROZEN
CURRICULUM MAP               FROZEN
TEXTBOOK MAP                 FROZEN
ASSESSMENT FORMS INDEX       FROZEN
THEME ALIGNMENTS             FROZEN
GAP ANALYSIS                 FROZEN
RESOURCE PLANS               FROZEN
SCHOOL-BASED PLANNING        FROZEN
PRODUCTION MANIFEST          FROZEN
KNOWLEDGE BASE               FROZEN
KNOWLEDGE RESOLVER           FROZEN
HYBRID RAG                   FROZEN
ASSESSMENT DESIGN CONTRACT   FROZEN
```

Frozen kayıt yine değişebilir; fakat yalnız kontrollü version bump + revalidation yoluyla.

---

## 31. TDE_9 uygulamasından çıkan ana dersler

Bu projede özellikle şu hatalar erken aşamada yakalandı ve mimariye kalıcı kural olarak işlendi:

1. Ders kitabındaki ölçüt tablosunu yanlışlıkla analytic rubric saymamak.
2. Aynı outcome kodunun farklı temalarda tekrar edebileceğini kabul etmek.
3. Vector similarity ile ambiguity çözmemek.
4. Programın “dereceli puanlama anahtarı” ifadesini “analytic rubric” diye resmîleştirmemek.
5. `NOT_SELECTED` okul temelli seçenekleri production context’e sokmamak.
6. Retrieval candidate ile canonical generation context’i ayırmak.
7. Haricî veya yeniden türetilmiş rights status icat etmemek.
8. 100’lük puanlama dönüşümünü resmî kural gibi sunmamak.
9. Generated assessment aracını öğretmen görmeden PASS saymamak.
10. Vector DB’yi source of truth yapmamak.

---

## 32. Sistemin en kısa özeti

Bu mimariyi başka bir derste yeniden kurarken üç şeyi ayır:

```text
1. KAYNAK GERÇEĞİ
   Program + Ders Kitabı + Frozen Canonical Knowledge

2. BULMA / ÇÖZÜMLEME MOTORU
   SQLite + FTS5 + Vector + Knowledge Resolver

3. ÜRETİM KURALLARI
   Production Manifest + Design Contract + QA + Teacher Review
```

Başka bir ifadeyle:

> **Yapay zekâ kararın kaynağı değildir. Yapay zekâ, doğrulanmış bilgi tabanı ve açık üretim sözleşmeleri üzerinde çalışan üretim motorudur.**

## Runtime Course Package / Application Projection Layer

Uygulama istemcileri için canonical knowledge katmanı doğrudan tüketim
şeması değildir. Doğrulanmış canonical JSON/MD kayıtları deterministic bir
compiler ile `runtime/course_runtime.sqlite` içine derlenir:

```text
canonical knowledge → compiler → runtime SQLite → application
```

Runtime package source of truth değildir; derived, rebuildable ve read-only
course knowledge projection'ıdır. User state içermez, RAG/vector database
değildir ve embedding/model runtime gerektirmez. Stable canonical ID'leri,
source locator/provenance ve canonical source fingerprint'larını taşır; bu
sayede istemciler canonical analysis logic'ini yeniden uygulamak zorunda
kalmaz. Canonical dosyalar değiştiğinde fingerprint üzerinden
`RUNTIME_STALE` bildirimi üretilir.

Bu ayrım korunduğu sürece aynı sistem farklı derslere, sınıf düzeylerine ve materyal türlerine güvenli biçimde genişletilebilir.

---

# Ek A — Yeni ders için kısa başlangıç şablonu

```text
COURSE_ID = <ör. TARIH_9>

1. sources/<COURSE_ID>_program.pdf
2. sources/<COURSE_ID>_textbook.pdf
3. knowledge/<COURSE_ID>/source_manifest.json
4. curriculum_map.json
5. textbook_map.json
6. textbook_forms_index.json
7. validation_report.md
8. themes/*/alignment.json
9. themes/*/gap_analysis.json
10. themes/*/resource_plan.json
11. production/consolidated_resource_plan.json
12. production/production_manifest.json
13. production/production_readiness_report.md
14. index/knowledge.sqlite
15. index/index_manifest.json
16. index/index_validation_report.md
17. resolver safety tests
18. production design contract
19. canonical_generation_context
20. material generation + Teacher Review
```

---

# Ek B — “Hazır mı?” kontrolü

Bir ders için aşağıdaki cümleyi güvenle söyleyebiliyorsan sistem üretime hazırdır:

> “Bu materyalin hangi resmî program gereksinimini karşıladığı, ders kitabında hangi karşılığın bulunduğu, geriye hangi doğrulanmış boşluğun kaldığı, neden bu materyalin REQUIRED olduğu, hangi canonical kayıtlardan üretileceği ve hangi QA sözleşmesine uyacağı sistem tarafından tek tek gösterilebiliyor.”

Bu cümledeki halkalardan biri eksikse üretim gate’i açılmamalıdır.
