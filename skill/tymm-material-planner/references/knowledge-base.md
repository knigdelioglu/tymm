# Knowledge Base, Caching, Resolver, and Local Hybrid Index

## 1. Amaç ve Mimari Hiyerarşi

Bu doküman, Türkiye Yüzyılı Maarif Modeli (TYMM) öğretim programları ve resmî ders kitaplarının bilgi tabanı (`knowledge/`) mimarisini, kaynak parmak izi (fingerprint/hash) kontrolünü, harita şemalarını, Knowledge Resolver orkestrasyonunu ve yerel hibrit RAG indeksini tanımlar.

### Katman Hiyerarşisi

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. SKILL WORKFLOW & GATES                       │
│  (Orchestrates Gates 0-7, pedagogical rules, prompt routing)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        2. KNOWLEDGE RESOLVER                           │
│  (Deterministic 7-stage pipeline, exact lookup, graph expansion,      │
│   intent classification, authority ordering, context pack assembly)   │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │ (Exact/Graph)                  │ (Semantic/Hybrid)
                    ▼                                ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│     3. CANONICAL KNOWLEDGE BASE      │ │   4. LOCAL HYBRID RAG INDEX   │
│        (SINGLE SOURCE OF TRUTH)      │ │   (RETRIEVAL ACCELERATOR)     │
│  knowledge/<course_id>/              │ │  knowledge/<course_id>/index/ │
│  ├── curriculum_map.json (Rank 1)    │ │  ├── knowledge.sqlite (FTS5)  │
│  ├── curriculum_process_component_   │ │  ├── sqlite-vec (384-dim E5)  │
│  │   resolution.json                 │ │  ├── index_manifest.json      │
│  ├── textbook_map.json (Rank 2)      │ │  └── index_validation_report  │
│  ├── textbook_forms_index.json (R.3) │ │                               │
│  ├── themes/ (Rank 4, 5, 6)          │ │                               │
│  └── production/ (Rank 7, 8)         │ │                               │
└──────────────────────────────────────┘ └───────────────────────────────┘
                    ▲
                    │
┌───────────────────┴────────────────────────────────────────────────────┐
│             SHARED NORMATIVE COURSE-FAMILY CATALOGS                   │
│  courses/TDE_SHARED/curriculum_process_component_catalog.json         │
└────────────────────────────────────────────────────────────────────────┘
                    ▲
                    │ (Frozen extracts)
┌───────────────────┴────────────────────────────────────────────────────┐
│                    5. ORIGINAL OFFICIAL SOURCES                        │
│  (Raw PDF / Word documents: öğretim programı.pdf, ders kitabı PDFs)    │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **TEK DOĞRULUK KAYNAĞI KURALI (SINGLE SOURCE OF TRUTH INVARIANT)**
> - Vektör Veritabanı (`knowledge.sqlite` / `sqlite-vec`) **kesinlikle doğruluk kaynağı (source of truth) DEĞİLDİR**.
> - Tek yetkili kaynak: `knowledge/<course_id>/` altındaki dondurulmuş ve doğrulanmış yapılandırılmış JSON dosyaları ile açıkça bağlanmış ortak normatif kataloglardır.
> - Vektör DB yalnızca anlamsal aday bulucu / hızlandırıcıdır (`retrieval accelerator / semantic candidate finder`).
> - Semantik arama sonuçları kanonik JSON kaydına resolve edilmeden asla resmî olgu olarak kullanılamaz.
> - `curriculum_process_component_resolution.json` bulunan TDE derslerinde `process_components_verbatim` alanının boşluğu efektif süreç bileşeni yokluğu anlamına gelmez. Efektif set `THEME_EXPLICIT -> ROOF_INHERITED -> SOURCE_VERIFIED_NONE` sırasıyla çözülür.

---

## 2. Dizin Yapısı

```text
knowledge/
└── <COURSE_GRADE>/
    ├── source_manifest.json
    ├── curriculum_map.json
    ├── curriculum_process_component_resolution.json # varsa inheritance contract
    ├── textbook_map.json
    ├── textbook_forms_index.json
    ├── themes/
    │   ├── tema_01/
    │   │   ├── alignment.json
    │   │   ├── gap_analysis.json
    │   │   ├── needs.json
    │   │   └── resource_plan.json
    │   ├── tema_02/
    │   ├── tema_03/
    │   └── tema_04/
    ├── production/
    │   ├── production_manifest.json
    │   ├── teaching_blocks.json
    │   └── school_based_planning_options.json
    └── index/
        ├── knowledge.sqlite
        ├── index_manifest.json
        └── index_validation_report.md

courses/TDE_SHARED/
└── curriculum_process_component_catalog.json
```

---

## 3. Otorite Sıralaması (Authority Ordering)

Knowledge Resolver, kanonik kayıtları çözümlerken şu hiyerarşiyi uygular:

1. **`OFFICIAL_CURRICULUM_FROZEN` / `OFFICIAL_CURRICULUM_ROOF_INHERITED`** (Seviye 1): Resmî öğrenme çıktıları ve efektif süreç bileşenleri. Tema-spesifik explicit kayıt varsa shared roof'a üstün gelir; aksi durumda doğrulanmış shared roof bileşeni inherit edilir.
2. **`OFFICIAL_TEXTBOOK_FROZEN`** (Seviye 2): Resmî MEB ders kitabı içerik ve etkinlikleri.
3. **`OFFICIAL_TEXTBOOK_FORM_FROZEN`** (Seviye 3): Kitaptaki ölçme formları ve yapısal türleri.
4. **`VALIDATED_ALIGNMENT`** (Seviye 4): Doğrulanmış program-kitap kapsaması.
5. **`VALIDATED_GAP`** (Seviye 5): Doğrulanmış kalan boşluklar.
6. **`VALIDATED_RESOURCE_PLAN`** (Seviye 6): Kaynak planları.
7. **`VALIDATED_PRODUCTION_PLAN`** (Seviye 7): Onaylanmış üretim kuyruğu.
8. **`PEDAGOGICAL_RECOMMENDATION`** (Seviye 8): Okul temelli seçenekler.

> [!CAUTION]
> Seviye 8 pedagojik öneriler, ne kadar yüksek anlamsal benzerlik puanı alırsa alsın, Seviye 1–7 resmî olguları geçersiz kılamaz veya değiştiremez.

---

## 4. Kaynak Parmak İzi ve Tazelik Protokolü

1. **Parmak İzi Hesaplama**: `source_manifest.json` ve `index/index_manifest.json` dosyalarında kanonik kaynak dosyalarının SHA-256 hash'i saklanır. Process-component resolution contract bulunan derslerde hem `curriculum_process_component_resolution.json` hem de `../TDE_SHARED/curriculum_process_component_catalog.json` index fingerprint kapsamındadır.
2. **Tazelik Durumları**:
   - `INDEX_FRESH`: Tüm kaynak dosyalarının hash'leri indeksteki parmak izleriyle tam uyuşuyor.
   - `INDEX_STALE`: Bir veya daha fazla kaynak JSON dosyası güncellenmiş. İndeksin yeniden oluşturulması gerekir.
   - `INDEX_MISSING`: İndeks SQLite veritabanı veya manifest mevcut değil.
   - `EMBEDDING_MODEL_MISMATCH`: İndekslenen model/boyut ile çalışma zamanı modeli uyuşmuyor.
3. **Çelişki Durumu (`KNOWLEDGE_CONFLICT`)**:
   - Haritadaki doğrulanmış veri ile yeni bir kaynak okuması çelişirse sessizce üzerine yazılmaz; `resolution_status = "REVIEW_REQUIRED"` olarak işaretlenir.

### Process-component-aware index build invariant

`curriculum_process_component_resolution.json` bulunan derslerde üretim/rebuild yolu `effective_knowledge_index.py` olmalıdır. Bu wrapper build öncesinde shared roof inheritance'ı memory'de çözer, inherited process-component kayıtlarının provenance'ını shared kataloğa taşır ve hem contract hem shared catalog hash'ini index manifestine ekler. `knowledge_index.py` doğrudan rebuild komutu process-component-aware üretim yolu olarak kullanılmamalıdır.

---

## 5. CLI Araçları

```bash
# 1. İndeks Tazelik Kontrolü
~/.gemini/config/skills/tymm-material-planner/.venv/bin/python3 \
  ~/.gemini/config/skills/tymm-material-planner/scripts/effective_knowledge_index.py status \
  --knowledge-root knowledge/TDE_9

# 2. İndeks İnşası / Rebuild
~/.gemini/config/skills/tymm-material-planner/.venv/bin/python3 \
  ~/.gemini/config/skills/tymm-material-planner/scripts/effective_knowledge_index.py build \
  --knowledge-root knowledge/TDE_9

# 3. Knowledge Resolver Sorgulama
~/.gemini/config/skills/tymm-material-planner/.venv/bin/python3 \
  ~/.gemini/config/skills/tymm-material-planner/scripts/knowledge_resolver.py resolve \
  --knowledge-root knowledge/TDE_9 \
  --query "Tema 2 TDE4.4 için kitapta ne eksik?"
```
