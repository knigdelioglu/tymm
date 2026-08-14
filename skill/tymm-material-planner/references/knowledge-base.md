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
│  ├── textbook_map.json (Rank 2)      │ │  ├── sqlite-vec (384-dim E5)  │
│  ├── textbook_forms_index.json (R.3) │ │  ├── index_manifest.json      │
│  ├── themes/ (Rank 4, 5, 6)          │ │  └── index_validation_report  │
│  └── production/ (Rank 7, 8)         │ │                               │
└──────────────────────────────────────┘ └───────────────────────────────┘
                    ▲
                    │ (Frozen extracts)
┌───────────────────┴────────────────────────────────────────────────────┐
│                    5. ORIGINAL OFFICIAL SOURCES                        │
│  (Raw PDF / Word documents: öğretim programı.pdf, 9edb.pdf)            │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **TEK DOĞRULUK KAYNAĞI KURALI (SINGLE SOURCE OF TRUTH INVARIANT)**
> - Vektör Veritabanı (`knowledge.sqlite` / `sqlite-vec`) **kesinlikle doğruluk kaynağı (source of truth) DEĞİLDİR**.
> - Tek yetkili kaynak: `knowledge/<course_id>/` altındaki dondurulmuş ve doğrulanmış yapılandırılmış JSON dosyalarıdır.
> - Vektör DB yalnızca anlamsal aday bulucu / hızlandırıcıdır (`retrieval accelerator / semantic candidate finder`).
> - Semantik arama sonuçları kanonik JSON kaydına resolve edilmeden asla resmî olgu olarak kullanılamaz.

---

## 2. Dizin Yapısı

```text
knowledge/
└── <COURSE_GRADE>/                    # Örnek: TDE_9, MAT_10, FIZ_9
    ├── source_manifest.json           # Resmî kaynak kimlikleri ve SHA-256 parmak izleri
    ├── curriculum_map.json            # [Rank 1] Resmî program verbatim dökümü ve süreç bileşenleri
    ├── textbook_map.json              # [Rank 2] Ders kitabı bölümleri, metinler, etkinlikler
    ├── textbook_forms_index.json      # [Rank 3] 28 ölçme-değerlendirme aracının 7 yapısal sınıfı
    ├── themes/                        # [Rank 4, 5, 6] Tema düzeyinde hizalama ve planlar
    │   ├── tema_01/
    │   │   ├── alignment.json         # [Rank 4] Program-kitap eşleşmesi
    │   │   ├── gap_analysis.json      # [Rank 5] Yapısal boşluk analizi
    │   │   ├── needs.json             # [Rank 6] Öğretimsel ihtiyaç analizi
    │   │   └── resource_plan.json     # [Rank 6] Kaynak planı
    │   ├── tema_02/
    │   ├── tema_03/
    │   └── tema_04/
    ├── production/                    # [Rank 7, 8] Üretim kuyruğu ve pedagojik öneriler
    │   ├── production_manifest.json   # [Rank 7] Üretilecek materyal kuyruğu
    │   ├── teaching_blocks.json       # [Rank 7] Öğretim blokları ve ders saati dağılımı
    │   └── school_based_planning_options.json # [Rank 8] Okul temelli planlama seçenekleri
    └── index/                         # Yerel Hibrit RAG Arama İndeksi (Türetilmiş)
        ├── knowledge.sqlite           # SQLite3 + sqlite-vec v0.1.9 + FTS5
        ├── index_manifest.json        # İndeks parmak izi, kaynak dosya hash'leri ve model bilgisi
        └── index_validation_report.md # İndeks doğrulama metrikleri ve kayıt dağılımı
```

---

## 3. Otorite Sıralaması (Authority Ordering)

Knowledge Resolver, kanonik kayıtları çözümlerken şu hiyerarşiyi uygular:

1. **`OFFICIAL_CURRICULUM_FROZEN`** (Seviye 1, `curriculum_map.json`): Resmî öğrenme çıktıları, süreç bileşenleri, verbatim şartlar. En yüksek öncelik.
2. **`OFFICIAL_TEXTBOOK_FROZEN`** (Seviye 2, `textbook_map.json`): Resmî MEB ders kitabı içerik ve etkinlikleri.
3. **`OFFICIAL_TEXTBOOK_FORM_FROZEN`** (Seviye 3, `textbook_forms_index.json`): Kitaptaki ölçme formları ve 7 yapısal türü.
4. **`VALIDATED_ALIGNMENT`** (Seviye 4, `themes/tema_XX/alignment.json`): Doğrulanmış program-kitap kapsaması.
5. **`VALIDATED_GAP`** (Seviye 5, `themes/tema_XX/gap_analysis.json`): Doğrulanmış kalan boşluklar.
6. **`VALIDATED_RESOURCE_PLAN`** (Seviye 6, `themes/tema_XX/resource_plan.json`): Kaynak planları.
7. **`VALIDATED_PRODUCTION_PLAN`** (Seviye 7, `production/production_manifest.json`): Onaylanmış üretim kuyruğu.
8. **`PEDAGOGICAL_RECOMMENDATION`** (Seviye 8, `production/school_based_planning_options.json`): Okul temelli seçenekler.

> [!CAUTION]
> Seviye 8 pedagojik öneriler, ne kadar yüksek anlamsal benzerlik puanı alırsa alsın, Seviye 1–7 resmî olguları geçersiz kılamaz veya değiştiremez.

---

## 4. Kaynak Parmak İzi ve Tazelik Protokolü

1. **Parmak İzi Hesaplama**: `source_manifest.json` ve `index/index_manifest.json` dosyalarında her kaynak JSON dosyasının SHA-256 hash'i saklanır.
2. **Tazelik Durumları**:
   - `INDEX_FRESH`: Tüm kaynak dosyalarının hash'leri indeksteki parmak izleriyle tam uyuşuyor.
   - `INDEX_STALE`: Bir veya daha fazla kaynak JSON dosyası güncellenmiş. İndeksin yeniden oluşturulması gerekir (`knowledge_index.py rebuild`).
   - `INDEX_MISSING`: İndeks SQLite veritabanı veya manifest mevcut değil.
   - `EMBEDDING_MODEL_MISMATCH`: İndekslenen model/boyut ile çalışma zamanı modeli uyuşmuyor.
3. **Çelişki Durumu (`KNOWLEDGE_CONFLICT`)**:
   - Haritadaki doğrulanmış veri ile yeni bir kaynak okuması çelişirse sessizce üzerine yazılmaz; `resolution_status = "REVIEW_REQUIRED"` olarak işaretlenir.

---

## 5. CLI Araçları

```bash
# 1. İndeks Tazelik Kontrolü
~/.gemini/config/skills/tymm-material-planner/.venv/bin/python3 \
  ~/.gemini/config/skills/tymm-material-planner/scripts/knowledge_index.py status \
  --knowledge-root knowledge/TDE_9

# 2. İndeks İnşası
~/.gemini/config/skills/tymm-material-planner/.venv/bin/python3 \
  ~/.gemini/config/skills/tymm-material-planner/scripts/knowledge_index.py build \
  --knowledge-root knowledge/TDE_9

# 3. Knowledge Resolver Sorgulama
~/.gemini/config/skills/tymm-material-planner/.venv/bin/python3 \
  ~/.gemini/config/skills/tymm-material-planner/scripts/knowledge_resolver.py resolve \
  --knowledge-root knowledge/TDE_9 \
  --query "Tema 2 TDE4.4 için kitapta ne eksik?"
```
