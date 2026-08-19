# TDE_11 Curriculum-Only Validation Report

**Lifecycle:** `CURRICULUM_ONLY_AWAITING_TEXTBOOK`  
**Curriculum validation:** PASS  
**Gate:** `curriculum_only_gate.py` PASS  
**Validated:** 2026-08-19

## Sonuç

- Course: `TDE_11` — 11. Sınıf Türk Dili ve Edebiyatı
- Resmî program source status: **VERIFIED_OFFICIAL_REMOTE_AND_LOCAL**
- Curriculum source completeness: **PASS — 4/4 tema**
- Tema sayısı: **4**
- Zaman modeli: **45 saat/tema = 43 saat resmî öğretim + 2 saat okul temelli planlama**
- Yıllık toplam: **180 saat = 172 + 8**
- Parent outcome: **64** (16/tema)
- Outcome scope/unique ID: **PASS**
- Verbatim/locator kanıtı: **PASS — full local PDF page text evidence + outcome local page locators**
- Explicit process component alt ID durumu: **SOURCE_COMPLETE_NO_EXPLICIT_SUBCOMPONENT_IDS**
- Sentetik alt kod üretimi: **YOK**
- Assessment requirement: **12** — 8 performans görevi + 4 tema sonu değerlendirme
- Source fingerprint: **PASS — 4/4 SHA-256 + bundle fingerprint**
- TDE_9 regression: **PASS — 7 gap instance → 3 canonical artifact**
- TDE_10 regression: **PASS — PARITY_REVIEW_BLOCKED fail-closed davranışı korunuyor**
- Textbook status: **AWAITING_OFFICIAL_TEXTBOOK**
- Coverage status: **NOT_EVALUATED**
- Gap status: **NOT_EVALUATED**
- Production status: **NOT_EVALUATED**
- Full textbook P0/runtime: **DEFERRED_UNTIL_OFFICIAL_TEXTBOOK_AVAILABLE**

## Kaynak fingerprintleri

- `TEMA_01` — `66d997920f0589cd19f735f1fce820916eafcf26412ab19091811f7248a55482` — `Türk Dili Ve Edebiyatı Dersi 11.Sınıf 1. TEMA - BİR DİYECEĞİM VAR!.PDF`
- `TEMA_02` — `2dd813e521d110d165fa93965189e6ed619ffb4da04b48d6616ab1b9f915cf58` — `Türk Dili Ve Edebiyatı Dersi 11.Sınıf 2. TEMA - KÜLTÜR YOLCULUĞU.PDF`
- `TEMA_03` — `d9d414bd2dc9fdc7852ee7c66a421a8a146c0560d56b4025690ce988458de04e` — `Türk Dili Ve Edebiyatı Dersi 11.Sınıf 3. TEMA - YAŞAMIN İZİNDE.PDF`
- `TEMA_04` — `14a5e5e17919c801127e9c157ef7bc1c947a0d3bcad0d8654cfc3a514aa147f5` — `Türk Dili Ve Edebiyatı Dersi 11.Sınıf 4. TEMA - HAYATIN AYNASI.PDF`

## Canonical kanıt derinliği

`curriculum_normative_text.json`, dört resmî yerel PDF’nin `pdftotext -layout` ile sayfa bazlı kaynak-bağlı metin çıkarımını tutar. `curriculum_map.json` tema ve outcome kayıtları bu dosyaya ve SHA-256 fingerprintlerine bağlanmıştır. PDF asıl resmî snapshot olarak kalır; metin çıkarımı kanıt/erişim katmanıdır.

## Ertelenen aşamalar

- textbook map / forms index
- textbook coverage
- alignment
- gap analysis
- resource/production kararları
- full textbook runtime ve production gate

Ders kitabının mevcut olmaması curriculum gap olarak değerlendirilmemiştir.

## Gerçek curriculum blocker

**Yok.** Curriculum-only bootstrap gate PASS durumundadır.
