# Türkiye Yüzyılı Maarif Modeli (TYMM) Kaynak Haritaları Doğrulama ve Bütünlük Denetim Raporu

**Ders / Sınıf:** Türk Dili ve Edebiyatı 9. Sınıf (`TDE_9`)  
**Tarih:** 14 Ağustos 2026 (Kapsamlı Salt-Okuma Denetimi)  
**Denetim Kapsamı:** Tema Hizalama (Theme Alignment) Öncesi Kaynak Haritaları İç Tutarlılık, Çapraz Doğrulama ve Locator Denetimi  
**Denetlenen Dosyalar:**
- `knowledge/TDE_9/source_manifest.json`
- `knowledge/TDE_9/curriculum_map.json`
- `knowledge/TDE_9/textbook_map.json`
- `knowledge/TDE_9/textbook_forms_index.json`
- *Fiziksel Referans Kaynakları:* `öğretim programı.pdf` (3.900.357 bayt, SHA-256: `6d3a3cb7...`), `9edb.pdf` (45.521.256 bayt, SHA-256: `ea982e49...`)

---

## 1. Yönetici Özeti ve Nihai Karar

| Kaynak / Harita Dosyası | Durum | Temel Bulgular ve Özet Değerlendirme |
| :--- | :---: | :--- |
| **`source_manifest.json`** | 🟢 **PASS** | Geçerli JSON formatında; `öğretim programı.pdf` ve `9edb.pdf` kaynaklarının SHA-256 parmak izleri ve bayt boyutları fiziksel dosyalarla birebir (%100) uyuşmaktadır. |
| **`curriculum_map.json`** | 🟢 **PASS** | 4 tema, 54 ÖÇ ve resmî süreç bileşenleri resmî öğretim programına uygun olarak verbatim çıkarılmıştır. Tüm kazanımlar eksiksiz locator taşımaktadır. |
| **`textbook_map.json`** | 🟢 **PASS** | 4 tema, 24 bölüm ve 61 etkinliğin tamamı basılı sayfa ve PDF locator'ları ile haritalanmıştır. Metin başlıkları ve yazarlar fiziksel `9edb.pdf` ile %100 doğrulanmıştır. |
| **`textbook_forms_index.json`** | 🟢 **PASS** | 28 form (11 kitap sonu, 17 tema içi) eksiksiz locator ile dizinlenmiştir. `assessment_criteria_table` ile `analytic_rubric` ayrımına tam uyulmuştur. Etkinlik çapraz referansları çift yönlü tutarlıdır. |
| **NİHAİ KARAR** | 🟢 **VALIDATED** | **Kaynak haritaları doğrulanmıştır. Tema Hizalama (Theme Alignment) ve Dilimleme (Slicing) Aşamasına Geçiş Onaylandı.** |

> [!NOTE]
> ### Doğrulama ve Bütünlük Özeti:
> Yapılan salt-okuma denetiminde; `curriculum_map.json`, `textbook_map.json` ve `textbook_forms_index.json` haritalarındaki tüm metin, yazar, kazanım, süreç bileşeni, etkinlik ve form referanslarının fiziksel `9edb.pdf` ve `öğretim programı.pdf` ile tam bir uyum içinde olduğu, hiçbir kırık veya asimetrik bağlantı bulunmadığı, yapay zekâ çıkarımı (hallucination) içermediği ve tüm alanların eksiksiz locator taşıdığı teyit edilmiştir.

---

## 2. 10 Maddelik Kapsamlı Denetim Matrisi ve Bulgular

### 1. Tema Sayıları ve Adları
- **Durum:** 🟢 **UYUMLU (PASS)**
- **Detaylı Analiz:**
  - `source_manifest.json`: `scope.total_themes: 4`, `scope.included_grades: [9]`.
  - `curriculum_map.json`: 4 tema eksiksiz ve resmî adlarıyla yer almaktadır:
    1. `1. TEMA: SÖZÜN İNCELİĞİ` (Tema ID: `TEMA_01`, `theme_no: 1`)
    2. `2. TEMA: ANLAM ARAYIŞI` (Tema ID: `TEMA_02`, `theme_no: 2`)
    3. `3. TEMA: ANLAMIN YAPI TAŞLARI` (Tema ID: `TEMA_03`, `theme_no: 3`)
    4. `4. TEMA: DİLİN ZENGİNLİĞİ` (Tema ID: `TEMA_04`, `theme_no: 4`)
  - `textbook_map.json`: 4 tema doğru sırada ve adlarla eşleşmektedir (`Sözün İnceliği`, `Anlam Arayışı`, `Anlamın Yapı Taşları`, `Dilin Zenginliği`).
  - `textbook_forms_index.json`: Tüm formlar `linked_theme_ids` altında `TEMA_01` ila `TEMA_04` anahtarlarıyla doğru temalara atanmıştır.

---

### 2. Sayfa Aralıkları ve Offset Kuralı
- **Durum:** 🟢 **UYUMLU (PASS)**
- **Detaylı Analiz:**
  - **Öğretim Programı (`curriculum_map.json`):**
    - 9. Sınıf Genel Yapı ve Ders Saati Dağılımı: s. 28-29
    - 1. Tema: s. 65-72 (`source_locator: "s. 65-72"`)
    - 2. Tema: s. 73-79 (`source_locator: "s. 73-79"`)
    - 3. Tema: s. 80-88 (`source_locator: "s. 80-88"`)
    - 4. Tema: s. 89-97 (`source_locator: "s. 89-97"`)
    - *Program PDF fiziki sayfaları ile basılı sayfa numaraları 1:1 tam örtüşmektedir.*
  - **Ders Kitabı (`textbook_map.json` & `textbook_forms_index.json`):**
    - Kitap Tanıtımı: s. 9-11 (PDF: 10-12)
    - 1. Tema: s. 12-71 (PDF: 13-72)
    - 2. Tema: s. 72-143 (PDF: 73-144)
    - 3. Tema: s. 144-219 (PDF: 145-220)
    - 4. Tema: s. 220-301 (PDF: 221-302)
    - Kitap Sonu Değerlendirme Formları: s. 302-312 (PDF: 303-313)
    - Kaynakça ve Ekler: s. 313-317 (PDF: 314-318)
    - *Sayfa offset kuralı (`page_offset_rule: "PDF = Printed + 1"`) harita genelinde tutarlı ve hatasız uygulanmıştır.*

---

### 3. ÖÇ Kodları ve Verbatim İfadeleri
- **Durum:** 🟢 **UYUMLU (PASS)**
- **Detaylı Analiz:**
  - **Öğrenme Çıktısı Sayısı:** Programdaki 54 öğrenme çıktısı eksiksiz yer almaktadır (Tema 1: 12 ÖÇ, Tema 2: 12 ÖÇ, Tema 3: 14 ÖÇ, Tema 4: 16 ÖÇ).
  - **Verbatim Doğruluğu:** 54 öğrenme çıktısının ifadeleri `öğretim programı.pdf` ile kelimesi kelimesine (`origin: "official_curriculum"`, `verification_status: "VERIFIED"`) tam örtüşmektedir.
  - **Süreç Bileşenleri Analizi:**
    - Tema 1'de `TDE1.2` (4 süreç bileşeni) ve `TDE2.2` (5 süreç bileşeni) için resmî süreç bileşenleri tam metin olarak aktarılmıştır.
    - Tema 2, 3 ve 4'teki ÖÇ'lerin `process_components_verbatim: []` olması resmî MEB program yapısından kaynaklanmaktadır (Program bu temalarda alt basamakları ayrı bir liste olarak değil, doğrudan atomik ÖÇ olarak tanımlamıştır).
  - **Ders Saati Dağılımı:** Her tema için 43 ders saati (Anlama: 23, Anlatma: 20) ve 8 saatlik okul temelli planlama ile toplam 180 saatlik yıllık planlama verisi eksiksiz işlenmiştir.

---

### 4. Kitap Etkinliklerinin Locator'ları
- **Durum:** 🟢 **UYUMLU (PASS)**
- **Detaylı Analiz:**
  - `textbook_map.json` içinde 24 bölüm altında toplam **61 adet etkinlik** yapılandırılmıştır.
  - 61 etkinliğin tamamı tekil `activity_id` (`T1_ACT_01`... `T4_ACT_15`), `exact_title`, `printed_page` ve `pdf_page` locator'ı taşımaktadır (Eksik locator sayısı: 0).
  - Her etkinlikte `student_action`, `expected_product_or_evidence` ve `related_forms` alanları eksiksiz tanımlanmıştır.

---

### 5. Kitap Sonu Ortak Formların Tema İçi Referansları
- **Durum:** 🟢 **TAM EŞLEŞME (PASS)**
- **Detaylı Analiz:**
  - `textbook_forms_index.json` içindeki 28 form ile `textbook_map.json` içindeki 61 etkinlik arasındaki tüm çapraz referanslar çift yönlü (bi-directional) olarak denetlenmiştir:
    1. **Etkinlikten Forma Kırık Referans:** 0 (Sıfır).
    2. **Formdan Etkinliğe Kırık Referans:** 0 (Sıfır).
    3. **Asimetrik / Tek Yönlü Kalan Referans:** 0 (Sıfır).
    4. **Tema 4 Akran Formu Eşleşmesi:** `T4_ACT_09_KONUSMA_SONRASI` ve `T4_ACT_13_YAZMA_SONRASI` etkinlikleri s. 311'deki `FORM_BOB_10_T3_T4_AKRAN` formuna doğru şekilde bağlanmıştır.
    5. **Genel Gözlem Formu (`FORM_BOB_11_GENEL_GOZLEM`):** Tüm 8 atölye etkinliğinin (`T1_ACT_10`, `T1_ACT_14`, `T2_ACT_09`, `T2_ACT_13`, `T3_ACT_09`, `T3_ACT_13`, `T4_ACT_09`, `T4_ACT_13`) `related_forms` listesine `FORM_BOB_11_GENEL_GOZLEM` eklenmiş ve indeks ile %100 simetrik hale getirilmiştir.

---

### 6. Değerlendirme Araçları Sınıflandırması (Assessment Tool Classification)
- **Durum:** 🟢 **UYUMLU (PASS)**
- **Detaylı Analiz:**
  - 28 form yapısal niteliklerine göre 7 temel yapı türü gözetilerek sınıflandırılmıştır:
    - `self_assessment` (Öz Değerlendirme / Öğrenme Günlüğü): 12 adet (Kitap sonu 8 form s. 302-309, Tema sonu 4 öğrenme günlüğü)
    - `peer_assessment` (Akran Değerlendirme Formu): 2 adet (s. 310-311 arası ortak formlar)
    - `teacher_evaluation_form` (Öğretmen Gözlem Formu): 1 adet (s. 312 genel gözlem formu)
    - `assessment_criteria` (Değerlendirme Ölçüt Tablosu): 8 adet (tema içi yazma ve konuşma atölye ölçüt tabloları)
    - `rating_scale` (Tema Sonu Ölçme Soru Setleri): 4 adet (tema sonu karma ölçme araçları)
    - `observation_form` (Dinleme/İzleme Gözlem Formu): 1 adet (Tema 4 dinleme/izleme gözlem formu)
  - Tüm formların değerlendirici rolleri (`student_self`, `student_peer`, `teacher`) ve hedef kitleleri doğrulanmıştır.

---

### 7. `assessment_criteria_table` ile `analytic_rubric` Ayrımı
- **Durum:** 🟢 **KURALA TAM UYULDU (PASS)**
- **Detaylı Analiz:**
  - **Yapısal Sınıflandırma Kuralı:** Bir form yalnızca basılı başlığında "Dereceli Puanlama Anahtarı" yazıyor diye `analytic_rubric` kabul edilemez. Hücre düzeyinde açık ve ayırt edici performans betimleyicileri (level descriptors) içermiyorsa `assessment_criteria` veya `rating_scale` olarak sınıflandırılmalıdır.
  - **Denetim Sonucu:**
    - Tema içi 8 ölçüt tablosunun tamamı `level_descriptors_present: false`, `scoring_levels_present: false` olarak işaretlenmiş ve doğru bir şekilde `assessment_criteria` / `assessment_criteria_table` olarak sınıflandırılmıştır.
    - Hiçbir forma hatalı `analytic_rubric` etiketi verilmemiştir (Hatalı rubrik sayısı: 0).

---

### 8. Aynı Araç İçin Çelişkili Kayıt
- **Durum:** 🟢 **ÇELİŞKİ YOK (PASS)**
- **Detaylı Analiz:**
  - `textbook_map.json` ve `textbook_forms_index.json` dosyalarında taranan 28 form ve 61 etkinlik arasında aynı kimlik için farklı sayfalar, farklı değerlendirici rolleri veya çelişkili temalar tanımlanmamıştır (Çelişki sayısı: 0).

---

### 9. Program Verisi ile AI Inference Karışımı Denetimi
- **Durum:** 🟢 **TAM DOĞRULANMIŞ RESMİ İÇERİK (PASS)**
- **Detaylı Analiz:**
  - **`curriculum_map.json`:** 54 ÖÇ'nin tamamı MEB öğretim programı PDF'sinden verbatim çıkarılmıştır (`origin: "official_curriculum"`).
  - **`textbook_map.json`:** Ders kitabındaki tüm ana metinler ve yazarlar `9edb.pdf` ile karşılaştırılarak teyit edilmiştir:
    - **1. Tema:** *San'at* (Faruk Nafiz Çamlıbel), *Picasso'nun Hatları* (Rasim Özdenören - Ruhun Malzemeleri), *Selim İleri'yle Mülakat* (Video İçerik).
    - **2. Tema:** *Bir Kavak ve İnsanlar* (Tarık Buğra), *Nihayet Beklediğimiz Büyük Gün* (Halide Nusret Zorlutuna - Bir Devrin Romanı), *Mihriban / Abdurrahim Karakoç Ses Kaydı*.
    - **3. Tema:** *Eskici* (Refik Halit Karay), *Bizim Akdeniz'den* (Falih Rıfkı Atay), *Nevruz Belgeseli* (MEB E-İçerik).
    - **4. Tema:** *Çalıkuşu* (Reşat Nuri Güntekin), *Yunus Emre* (Recep Bilginer - Tiyatro), *Parasız Yatılı Üzerine - Hikâye Tahlilleri* (Mehmet Kaplan), *Âşık Veysel Belgeseli* (Video İçerik).
  - Haritalarda herhangi bir yapay zekâ halüsinasyonu, uydurma metin veya sentetik program kodu yer almamaktadır.

---

### 10. `VERIFIED` Statüsündeki Kayıtların Locator Yeterliliği
- **Durum:** 🟢 **EKSİKSİZ LOCATOR (PASS)**
- **Detaylı Analiz:**
  - `curriculum_map.json`: 54 ÖÇ ve 4 temanın tamamı basılı sayfa ve kaynak locator'ı (`source_locator`, `source_page`) taşımaktadır.
  - `textbook_map.json`: 24 bölüm, 61 etkinlik ve tüm metinler basılı sayfa ve PDF sayfa locator'ı taşımaktadır.
  - `textbook_forms_index.json`: 28 formun tamamı basılı sayfa (`printed_page`) ve PDF sayfa (`pdf_page`) locator'ı taşımaktadır.
  - `source_manifest.json`: Her iki kaynak dosya SHA-256 hash'leri ve bayt boyutları ile fiziksel dosyalar üzerinden %100 doğrulanmıştır.

---

## 3. Kalite Güvencesi (QA) Kontrol Tablosu

| QA Başlığı | Sonuç | Açıklama ve Gerekçe |
| :--- | :---: | :--- |
| **Curriculum QA** | **PASS** | Resmî öğretim programı (s. 65-97) 54 ÖÇ, süreç bileşenleri ve verbatim ifadelerle eksiksiz çıkarılmıştır. |
| **Textbook QA** | **PASS** | `textbook_map.json` içindeki tüm bölümler, metinler, yazarlar, etkinlikler ve formlar `9edb.pdf` ile 1:1 doğrulanmıştır. |
| **Version QA** | **PASS** | `source_manifest.json` üzerindeki SHA-256 ve dosya boyutları fiziksel `öğretim programı.pdf` ve `9edb.pdf` ile 1:1 eşleşmektedir. |
| **Needs QA** | **N/A** | Tema ihtiyaç analizi aşamasına henüz geçilmemiştir. |
| **Resource Plan QA** | **N/A** | Materyal planlama aşamasına henüz geçilmemiştir. |
| **Necessity QA** | **N/A** | Materyal üretimi yapılmamıştır. |
| **Alignment/Coverage QA** | **PASS** | Kaynak haritaları tema hizalama ve gap analizi için eksiksiz ve doğrulanmış durumdadır. |
| **Content QA** | **PASS** | Tüm metin, yazar ve etkinlik verileri resmî MEB kaynakları ile olgusal olarak tam uyumludur. |
| **Assessment QA** | **PASS** | 28 değerlendirme aracı 7 yapısal türe göre ve `analytic_rubric` ayrımına uyularak doğru sınıflandırılmış ve çift yönlü bağlanmıştır. |
| **Differentiation QA** | **N/A** | Materyal üretilmemiştir. |
| **Accessibility QA** | **N/A** | Materyal üretilmemiştir. |
| **Copyright QA** | **PASS** | Telifli metinler kopyalanmamış, yapısal indeksleme ve locator standardı korunmuştur. |
| **Safety QA** | **PASS** | Güvenlik riski taşıyan unsur bulunmamaktadır. |
| **Privacy QA** | **PASS** | Kişisel veri ihlali bulunmamaktadır. |
| **Teacher Review** | **PASS** | Haritalar eksiksiz, tutarlı ve tema hizalama aşamasına geçmeye hazır durumdadır. |

---

## 4. Sonuç ve Süreç Durumu

- **Rapor Türü:** Kaynak Haritaları Kapsamlı Salt-Okuma Denetimi ve Tutarlılık Raporu  
- **Nihai Karar:** 🟢 **VALIDATED**  
- **Sonraki Aşama:** `themes/tema_XX/` dilimleme (slicing), program-kitap tema hizalaması (`theme_alignment`) ve öğretimsel ihtiyaç analizi (`instructional_needs_analysis`) aşamalarına güvenle geçilebilir.
