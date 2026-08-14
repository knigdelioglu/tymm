# Türkiye Yüzyılı Maarif Modeli (TYMM) Program ↔ Ders Kitabı Hizalama Raporu

**Ders / Sınıf:** Türk Dili ve Edebiyatı 9. Sınıf (`TDE_9`)  
**Tema:** 3. Tema: Anlamın Yapı Taşları (`TEMA_03`)  
**Tarih:** 14 Ağustos 2026  
**Yetkili Kaynak Haritaları:**
- `knowledge/TDE_9/source_manifest.json` (VERIFIED, SHA-256 doğrulandı)
- `knowledge/TDE_9/curriculum_map.json` (s. 80-88, verbatim)
- `knowledge/TDE_9/textbook_map.json` (s. 144-219, PDF: 145-220)
- `knowledge/TDE_9/textbook_forms_index.json` (8 form)
- `knowledge/TDE_9/validation_report.md`

---

## 1. Yönetici Özeti ve Temel Metrikler

| Metrik | Değer | Açıklama |
| :--- | :---: | :--- |
| **Toplam Program Hedefi (ÖÇ)** | **14** | Dinleme/İzleme: 3, Okuma: 3, Konuşma: 4, Yazma: 4 |
| **Toplam Süreç Bileşeni** | **0** | Program bu temada tüm hedefleri atomik ÖÇ olarak tanımlamıştır |
| **COVERED (Tam Karşılanan)** | **12** | 12 hedef ders kitabı metinleri ve etkinlikleriyle tam karşılanmaktadır |
| **PARTIALLY_COVERED** | **2** | **TDE3.4** ve **TDE4.4** (Kitapta dereceli puanlama anahtarı yapısının bulunmaması nedeniyle) |
| **NOT_COVERED** | **0** | Tamamen karşılanmayan hedef bulunmamaktadır |
| **REQUIRED Resource Count** | **2** | TDE3.4 Konuşma ve TDE4.4 Yazma için Dereceli Puanlama Anahtarı (Necessity Test: PASS) |
| **RECOMMENDED Resource Count** | **0** | Bu aşamada planlanan ek öneri kaynak bulunmamaktadır |
| **OPTIONAL Resource Count** | **0** | Bu aşamada planlanan isteğe bağlı kaynak bulunmamaktadır |
| **REUSE_TEXTBOOK Count** | **12** | 12 hedefin tamamında mevcut ders kitabı etkinlik ve metinleri yeniden kullanılmaktadır |
| **REUSE_WITH_TEACHER_GUIDE Count** | **0** | Kitap içi yönergeler yeterlidir |
| **GENERATE_ASSESSMENT_SUPPORT Count** | **2** | TDE3.4 ve TDE4.4 için öğretmen dereceli puanlama anahtarı (rubrik) desteği |
| **Diğer GENERATE Kararları Sayısı** | **0** | Kitapta mevcut etkinlikler için mükerrer üretim yapılmamıştır |
| **map_conflict Count** | **0** | Haritalar arasında çelişki tespit edilmemiştir |
| **unresolved Count** | **0** | Çözülmemiş alan bulunmamaktadır |
| **ALIGNMENT_STATUS** | 🟢 **PASS** | **Program ve ders kitabı hizalaması dondurulmuştur.** |

---

## 2. TDE3.4 ve TDE4.4 Alt Bileşen Analizi ve Kapsama Kararı

Programın açık `assessment/evaluation requirement`, `learning evidence requirement` ve `teacher assessment requirement` hükümleri öğretim programı beklentisinin zorunlu parçasıdır. Program açıkça *"Sunumlar, dereceli puanlama anahtarı ile puanlanır"* veya *"Öğrencinin yazılı ürünleri dereceli puanlama anahtarı ile puanlanır"* dediğinde, bu gereksinim tek başına öz/akran değerlendirmesi veya ölçüt tablosu ile ikame edilemez (`assessment_criteria_table ≠ analytic_rubric`). Çok boyutlu program ölçütleri nedeniyle `analytic_rubric`, eksikliği tamamlamak için seçilen pedagojik/teknik uygulama biçimidir.

### A. TDE3.4 Alt Bileşen Değerlendirmesi
**Hedef:** TDE3.4. Edebî metinlerdeki yapısal inceliklerin konuşmaya etkisine yönelik değerlendirmelerini yansıtabilme

1. **student speaking performance**
   - **PROGRAM_REQUIRES:** Okunan metinlerdeki mekânları kendi çevresiyle karşılaştıran bir sunum gerçekleştirme (s. 81, 85-86).
   - **TEXTBOOK_PROVIDES:** s. 193-196'da "Benim Mekânım" sunumu hazırlık ve canlı sunum icra etkinliği (`T3_ACT_08_KONUSMA_SIRASI`).
   - **STRUCTURAL_MATCH:** MATCH (`student_production_task`)
   - **COMPONENT_COVERAGE:** COVERED

2. **self-reflection**
   - **PROGRAM_REQUIRES:** Öğrencinin konuşma sürecine ve edindiği bilgilere ilişkin öz yansıtma yapması (s. 81, 85).
   - **TEXTBOOK_PROVIDES:** Kitap sonu s. 307'deki Öz Değerlendirme Formu (`FORM_BOB_06_T3_KONUSMA_OZ`) ve 3 açık uçlu yansıtma sorusu (`T3_ACT_09`).
   - **STRUCTURAL_MATCH:** MATCH (`self_assessment_form`)
   - **COMPONENT_COVERAGE:** COVERED

3. **peer assessment**
   - **PROGRAM_REQUIRES:** Akran değerlendirmesi yapabilme (s. 81, 82).
   - **TEXTBOOK_PROVIDES:** Kitap sonu s. 311'deki Akran Değerlendirme Formu (`FORM_BOB_10_T3_T4_AKRAN`) nitel geri bildirim alanları (`T3_ACT_09`).
   - **STRUCTURAL_MATCH:** MATCH (`peer_assessment_form`)
   - **COMPONENT_COVERAGE:** COVERED

4. **teacher assessment**
   - **PROGRAM_REQUIRES:** Öğretmenin öğrenci konuşma sunumlarını değerlendirmesi ve puanlaması (s. 81, 82, 85-86).
   - **TEXTBOOK_PROVIDES:** Kitap sonu s. 312'deki Gözlem / Değerlendirme Formu (`FORM_BOB_11_GENEL_GOZLEM` -> Gözlendi / Geliştirilmeli / Gözlenmedi).
   - **STRUCTURAL_MATCH:** PARTIAL_MATCH (Genel gözlem skalası mevcuttur ancak dereceli puanlama yapısı içermez)
   - **COMPONENT_COVERAGE:** PARTIALLY_COVERED

5. **assessment criteria**
   - **PROGRAM_REQUIRES:** İçerik (doğruluk, karşılaştırma/betimleme), anlatım (akıcılık, bağdaşıklık), organizasyon (zaman/mekân yönetimi, materyal desteği), iletişim (ses/tonlama, beden dili, jest-mimik), Türkçenin doğru kullanımı ölçütleri (s. 82, 86).
   - **TEXTBOOK_PROVIDES:** s. 195'te yer alan Değerlendirme Ölçütleri tablosu (`FORM_IN_T3_KONUSMA_CRITERIA`) ölçüt ve açıklamaları sunmaktadır.
   - **STRUCTURAL_MATCH:** MATCH (`assessment_criteria_table`)
   - **COMPONENT_COVERAGE:** COVERED

6. **required rated/rubric structure**
   - **PROGRAM_REQUIRES:** "Sunumlar, dereceli puanlama anahtarı ile puanlanır." (s. 82, 86) [Programın verbatim gereksinimi: dereceli puanlama anahtarı]
   - **TEXTBOOK_PROVIDES:** `assessment_criteria_table` (s. 195), `self_assessment_form` (s. 307), `peer_assessment_form` (s. 311), `teacher_evaluation_form` (s. 312) [Mevcut structural_type kayıtları]
   - **STRUCTURAL_MATCH:** MISMATCH (Kitaptaki ölçüt tablosu, öz/akran formları ve gözlem formu dereceli puanlama anahtarı yapısını içermez)
   - **COMPONENT_COVERAGE:** NOT_COVERED

- **TDE3.4 Nihai Kapsama (Final Coverage):** **PARTIALLY_COVERED**
- **Exact Remaining Gap:** Kitapta programın istediği dereceli puanlama anahtarı yapısının bulunmaması (Programın çok boyutlu ölçütlerini derecelendirmek üzere analitik rubrik desteği gereklidir).
- **Üretim Kararı:** **GENERATE_ASSESSMENT_SUPPORT** (Öncelik: **REQUIRED**)

---

### B. TDE4.4 Alt Bileşen Değerlendirmesi
**Hedef:** TDE4.4. Yapısını incelikle ördüğü yazısına yönelik değerlendirmelerini yansıtabilme

1. **written product**
   - **PROGRAM_REQUIRES:** Dinlenen/izlenen belgeseli infografik bir metne dönüştürerek yazılı anlatım gerçekleştirme (s. 81, 82, 87-88).
   - **TEXTBOOK_PROVIDES:** s. 203-205'te "Nevruz'un İzinde: Bir Belgeselin İnfografiği" yazma görevi (`T3_ACT_12_YAZMA_SIRASI`).
   - **STRUCTURAL_MATCH:** MATCH (`student_production_task`)
   - **COMPONENT_COVERAGE:** COVERED

2. **self-reflection**
   - **PROGRAM_REQUIRES:** Öz değerlendirme yapabilme ve süreci değerlendirme (s. 81, 82).
   - **TEXTBOOK_PROVIDES:** Kitap sonu s. 306'daki Öz Değerlendirme Formu (`FORM_BOB_05_T3_YAZMA_OZ`) ve 3 yansıtma sorusu (`T3_ACT_13`).
   - **STRUCTURAL_MATCH:** MATCH (`self_assessment_form`)
   - **COMPONENT_COVERAGE:** COVERED

3. **peer assessment**
   - **PROGRAM_REQUIRES:** Akran ve grup değerlendirmesi yapılabilmesi (s. 81, 82).
   - **TEXTBOOK_PROVIDES:** Kitap sonu s. 311'deki Akran Değerlendirme Formu (`FORM_BOB_10_T3_T4_AKRAN`) nitel geri bildirim alanları (`T3_ACT_13`).
   - **STRUCTURAL_MATCH:** MATCH (`peer_assessment_form`)
   - **COMPONENT_COVERAGE:** COVERED

4. **teacher feedback**
   - **PROGRAM_REQUIRES:** "Değerlendirme sonrasında öğretmen öğrencilere geri bildirim verir." (s. 82, 88)
   - **TEXTBOOK_PROVIDES:** Kitap sonu s. 312'deki Gözlem / Değerlendirme Formu (`FORM_BOB_11_GENEL_GOZLEM`) ve öğretmen dönüt yönergeleri (`T3_ACT_13`).
   - **STRUCTURAL_MATCH:** MATCH (`teacher_evaluation_form`)
   - **COMPONENT_COVERAGE:** COVERED

5. **assessment criteria**
   - **PROGRAM_REQUIRES:** Anlam, dil ve görsel ögelerin kullanımı, özgünlük, tutarlılık, doğruluk, yazım ve noktalama ölçütleri (s. 82, 88).
   - **TEXTBOOK_PROVIDES:** s. 205'teki Değerlendirme Ölçütleri tablosu (`FORM_IN_T3_YAZMA_CRITERIA`) ölçüt ve açıklamaları sunmaktadır.
   - **STRUCTURAL_MATCH:** MATCH (`assessment_criteria_table`)
   - **COMPONENT_COVERAGE:** COVERED

6. **required rated/rubric structure**
   - **PROGRAM_REQUIRES:** "Öğrencinin yazılı ürünleri dereceli puanlama anahtarı ile puanlanır." (s. 82, 88) [Programın verbatim gereksinimi: dereceli puanlama anahtarı]
   - **TEXTBOOK_PROVIDES:** `assessment_criteria_table` (s. 205), `self_assessment_form` (s. 306), `peer_assessment_form` (s. 311), `teacher_evaluation_form` (s. 312) [Mevcut structural_type kayıtları]
   - **STRUCTURAL_MATCH:** MISMATCH (Kitaptaki ölçüt tablosu, öz/akran formları, gözlem formu ve revizyon basamakları dereceli puanlama anahtarı yapısını içermez)
   - **COMPONENT_COVERAGE:** NOT_COVERED

7. **feedback sonrası revision/finalization**
   - **PROGRAM_REQUIRES:** "Yazım ve noktalama kurallarına göre düzenlemeler yaparak anlatımına son şeklini verir ve bunu sınıfta paylaşır" (s. 88).
   - **TEXTBOOK_PROVIDES:** s. 206'da "Yazma Sonrası" (`T3_ACT_13`) aşamasında metni düzenleme ve son şeklini verme basamakları mevcuttur.
   - **STRUCTURAL_MATCH:** MATCH (`revision_and_finalization_task`)
   - **COMPONENT_COVERAGE:** COVERED

- **TDE4.4 Nihai Kapsama (Final Coverage):** **PARTIALLY_COVERED**
- **Exact Remaining Gap:** Kitapta programın istediği dereceli puanlama anahtarı yapısının bulunmaması (Programın çok boyutlu ölçütlerini derecelendirmek üzere analitik rubrik desteği gereklidir).
- **Üretim Kararı:** **GENERATE_ASSESSMENT_SUPPORT** (Öncelik: **REQUIRED**)

---

## 3. Program ↔ Ders Kitabı Hizalama Matrisi (14 Öğrenme Çıktısı)

| Kod | Program Hedefi (Verbatim) | Beklenen Öğrenci Eylemi ve Kanıtı | Ders Kitabı Karşılığı ve Locator | Mevcut Etkinlik ve Ölçme Aracı | Kapsama | Kalan Gap | Üretim Kararı |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| **TDE1.1** | TDE1.1. “Anlamın Yapı Taşları” temasında ele alınan metinlerde dinlemeyi/izlemeyi yönetebilme (s. 81) | Karekoddan Nevruz Belgeseli'ni amaç belirleyerek izleme, not alma. **Kanıt:** İzleme öncesi/sırası notları. | `T3_SEC_04_DINLEME_IZLEME`<br>`T3_TXT_03` (s. 200)<br>`T3_ACT_10` (s. 199-200) | Metin öncesi hazırlık soruları, karekodlu video bağlantısı ve not alma rehberliği | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE1.2** | TDE1.2. “Anlamın Yapı Taşları” temasında ele alınan metinlerde anlam oluşturabilme (s. 81) | Belgeseldeki açık/örtük iletileri tespit etme, kültürel ögeleri anlamlandırma. **Kanıt:** Tahlil soruları cevapları. | `T3_SEC_04_DINLEME_IZLEME`<br>`T3_ACT_10`, `T3_ACT_11` (s. 199-202) | Açık ve örtük ileti tespit soruları, belgesel anlamlandırma soruları | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE1.3** | TDE1.3. “Anlamın Yapı Taşları” temasında ele alınan metinleri çözümleyebilme (s. 81) | Belgeseldeki çok modlu unsurların (görsel, işitsel, kurgu) kültürel aktarımdaki işlevini tahlil etme. **Kanıt:** Çözümleme yanıtları. | `T3_SEC_04_DINLEME_IZLEME`<br>`T3_ACT_11` (s. 200-202) | Görsel ve işitsel unsurların kültürel belleğe etkisini irdeleyen tahlil soruları | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE2.1** | TDE2.1. “Anlamın Yapı Taşları” temasında ele alınan metinlerde okumayı yönetebilme (s. 81) | Hikâye ve gezi yazısı öncesi hazırlık, tahmin yapma, okuma sırası işaretleme. **Kanıt:** Ön hazırlık ve metin üzeri işaretlemeler. | `T3_SEC_01_OKUMA_HIKAYE`<br>`T3_SEC_02_OKUMA_GEZI_YAZISI`<br>`T3_ACT_01`, `T3_ACT_02`, `T3_ACT_05` (s. 154-158, 183) | 'Eskici' ve 'Bizim Akdeniz'den' metinleri öncesi hazırlık soruları ve işaretleme yönergeleri | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE2.2** | TDE2.2. “Anlamın Yapı Taşları” temasında ele alınan metinlerde anlam oluşturabilme (s. 81) | Bilinmeyen kelimeleri bağlamdan çıkarma, açık/örtük iletileri ve tür özelliklerini belirleme. **Kanıt:** Tahlil soruları cevapları. | `T3_SEC_01_OKUMA_HIKAYE`<br>`T3_SEC_02_OKUMA_GEZI_YAZISI`<br>`T3_ACT_03`, `T3_ACT_06` (s. 159-175, 185-192) | Söz varlığı çözümlemeleri, anlama ve yorumlama soruları | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE2.3** | TDE2.3. “Anlamın Yapı Taşları” temasında ele alınan metinleri çözümleyebilme (s. 81) | Yapı unsurlarını (olay, kişi, mekân, zaman, anlatıcı, bakış açısı), anlatım tekniklerini (iç konuşma, diyalog) ve belirteçleri çözümleme. **Kanıt:** Yapı tabloları, kontrol listeleri. | `T3_SEC_01_OKUMA_HIKAYE`<br>`T3_SEC_02_OKUMA_GEZI_YAZISI`<br>`T3_ACT_03`, `T3_ACT_04`, `T3_ACT_06`, `T3_ACT_07` (s. 159-193) | Yapı çözümleme tabloları, anlatım tekniği analizleri, belirteç alıştırmaları, s. 182 ve 193 kontrol noktaları | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE3.1** | TDE3.1. Edebî metinlerde yapısal inceliklere odaklanan akıcı bir konuşma sürecini yönetebilme (s. 81) | 'Benim Mekânım' sunumu için konu ve mekân seçimi yapma, dijital görsel toplama ve telif haklarına uyma. **Kanıt:** Sunum hazırlık planı. | `T3_SEC_03_KONUSMA_ATOLYESI`<br>`T3_ACT_08` (s. 193-196) | Sunum hazırlık adımları, görsel toplama ve telif yönergeleri, `FORM_IN_T3_KONUSMA_CRITERIA` (s. 195) | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE3.2** | TDE3.2. Benzetme, karşılaştırma yaparak yapısal özellikleri ortaya koyduğu bir konuşma içeriği oluşturabilme (s. 81) | Metindeki mekân ile kendi çevresindeki mekânı karşılaştıran sunum kurgusu tasarlama. **Kanıt:** Mekân karşılaştırma sunum taslağı. | `T3_SEC_03_KONUSMA_ATOLYESI`<br>`T3_ACT_08` (s. 193-196) | Mekân karşılaştırma basamakları, görsel slayt kurgusu, `FORM_IN_T3_KONUSMA_CRITERIA` (s. 195) | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE3.3** | TDE3.3. Benzetme, karşılaştırma yaparak yapısal özellikleri ortaya koyduğu bir konuşmada kural uygulayabilme (s. 81) | Ses, tonlama, vurgu, beden dili ve dil kurallarına uyarak sunum yapma. **Kanıt:** Canlı sunum performansı. | `T3_SEC_03_KONUSMA_ATOLYESI`<br>`T3_ACT_08` (s. 193-196) | Sunum icra yönergeleri, ses ve beden dili ilkeleri, `FORM_IN_T3_KONUSMA_CRITERIA` (s. 195) | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE3.4** | TDE3.4. Edebî metinlerdeki yapısal inceliklerin konuşmaya etkisine yönelik değerlendirmelerini yansıtabilme (s. 81) | Sunum sonrası öz değerlendirme formunu doldurma, yansıtma sorularını yanıtlama, akran geri bildirimi verme ve öğretmen dereceli puanlama anahtarı değerlendirmesi alma. **Kanıt:** Doldurulmuş formlar ve puanlama çıktısı. | `T3_SEC_03_KONUSMA_ATOLYESI`<br>`T3_ACT_09` (s. 197)<br>Ekler: s. 307, 311, 312 | `FORM_BOB_06_T3_KONUSMA_OZ` (s. 307), `FORM_BOB_10_T3_T4_AKRAN` (s. 311), `FORM_BOB_11_GENEL_GOZLEM` (s. 312) | **PARTIALLY_COVERED** | Kitapta programın istediği dereceli puanlama anahtarı yapısının bulunmaması | `GENERATE_ASSESSMENT_SUPPORT` |
| **TDE4.1** | TDE4.1. Yapısını incelikle ördüğü bir yazılı anlatım sürecini yönetebilme (s. 81) | Nevruz belgeselinden hareketle infografik metin planlama, bilgi ve görsel seçimi yapma. **Kanıt:** İnfografik planlama taslağı. | `T3_SEC_05_YAZMA_ATOLYESI`<br>`T3_ACT_12` (s. 203-205) | İnfografik metin hazırlık adımları, bilgi ve görsel seçimi yönergeleri, `FORM_IN_T3_YAZMA_CRITERIA` (s. 205) | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE4.2** | TDE4.2. Yapısı incelikle örülmüş edebî metinlerden edindiği söz varlığını kullanarak yazısı için içerik oluşturabilme (s. 81) | Belgeselden ve metinlerden edinilen kültürel söz varlığını, deyim ve atasözlerini infografik metne yerleştirme. **Kanıt:** İnfografik metin taslağı. | `T3_SEC_05_YAZMA_ATOLYESI`<br>`T3_ACT_12` (s. 203-205) | İçerik kurgusu adımları, söz varlığı ve görsel uyum yönergeleri, `FORM_IN_T3_YAZMA_CRITERIA` (s. 205) | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE4.3** | TDE4.3. Yapısını incelikle ördüğü yazısında kural uygulayabilme (s. 81) | İnfografik metinde dil bilgisi, yazım ve noktalama kurallarını uygulama, metni düzenleme. **Kanıt:** Son şekli verilmiş infografik metin. | `T3_SEC_05_YAZMA_ATOLYESI`<br>`T3_ACT_12`, `T3_ACT_13` (s. 203-206) | Metin düzeltme/revizyon yönergeleri, `FORM_IN_T3_YAZMA_CRITERIA` (s. 205) | **COVERED** | Yok | `REUSE_TEXTBOOK` |
| **TDE4.4** | TDE4.4. Yapısını incelikle ördüğü yazısına yönelik değerlendirmelerini yansıtabilme (s. 81) | İnfografik metin çalışmasını öz değerlendirme formuyla değerlendirme, yansıtma sorularını cevaplama, akran değerlendirmesi yapma, metne son şeklini verme ve öğretmen dereceli puanlama anahtarı değerlendirmesini alma. **Kanıt:** Doldurulmuş formlar, revize metin, puanlama çıktısı. | `T3_SEC_05_YAZMA_ATOLYESI`<br>`T3_ACT_13` (s. 206)<br>Ekler: s. 306, 311, 312 | `FORM_BOB_05_T3_YAZMA_OZ` (s. 306), `FORM_BOB_10_T3_T4_AKRAN` (s. 311), `FORM_BOB_11_GENEL_GOZLEM` (s. 312) | **PARTIALLY_COVERED** | Kitapta programın istediği dereceli puanlama anahtarı yapısının bulunmaması | `GENERATE_ASSESSMENT_SUPPORT` |

---

## 4. Ölçme ve Değerlendirme Araçlarının Yapısal Sınıflandırması

Tema 3 kapsamında ders kitabında yer alan ve indekslenen 8 değerlendirme aracı yapısal olarak incelenmiştir:

| Form ID | Basılı Başlık / Konum | Yapısal Tür (`structural_type`) | Değerlendirici Rolü (`evaluator`) | Düzey Betimleyicisi | Ölçek / Yapı Özelliği |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FORM_IN_T3_KONUSMA_CRITERIA` | Değerlendirme Ölçütleri (s. 195) | `assessment_criteria_table` | Öğretmen ve Akran | Yok | Ölçüt ve açıklama listesi; düzey basamağı veya hücre betimleyicisi içermez. |
| `FORM_IN_T3_YAZMA_CRITERIA` | Değerlendirme Ölçütleri (s. 205) | `assessment_criteria_table` | Öğretmen ve Akran | Yok | Ölçüt ve açıklama listesi; düzey basamağı veya hücre betimleyicisi içermez. |
| `FORM_BOB_06_T3_KONUSMA_OZ` | Öz Değerlendirme Formu (s. 307) | `self_assessment_form` | Öğrencinin Kendisi | Yok | 3'lü dereceleme ölçeği (`Evet / Kısmen / Hayır`) + 3 açık uçlu yansıtma sorusu. |
| `FORM_BOB_05_T3_YAZMA_OZ` | Öz Değerlendirme Formu (s. 306) | `self_assessment_form` | Öğrencinin Kendisi | Yok | 3'lü dereceleme ölçeği (`Evet / Kısmen / Hayır`) + 3 açık uçlu yansıtma sorusu. |
| `FORM_BOB_10_T3_T4_AKRAN` | Akran Değerlendirme Formu (s. 311) | `peer_assessment_form` | Sınıf Arkadaşı (Akran) | Yok | Nitel yapılandırılmış geri bildirim (en iyi yan, 3 beğeni, 3 geliştirilecek yön). |
| `FORM_BOB_11_GENEL_GOZLEM` | Gözlem / Değerlendirme Formu (s. 312) | `teacher_evaluation_form` | Öğretmen | Yok | 3 basamaklı gözlem matrisi (`Gözlendi / Geliştirilmeli / Gözlenmedi`). |
| `FORM_IN_T3_TEMA_SONU_TEST` | Tema Sonu Ölçme ve Değ. (s. 207-210) | `test_question_set` | Öğretmen / Öğrenci | Yok | Çoktan seçmeli ve açık uçlu karma soru seti + karekodlu ek sorular. |
| `FORM_IN_T3_OGRENME_GUNLUGU` | Öğrenme Günlüğü (s. 211) | `learning_journal` | Öğrencinin Kendisi | Yok | Tema sonu açık uçlu bireysel yansıtma alanı. |

> [!IMPORTANT]
> **Yapısal Araç Ayrımı:**  
> `assessment_criteria_table ≠ analytic_rubric`  
> `teacher_evaluation_form ≠ analytic_rubric`  
> `rating_scale ≠ analytic_rubric`  
> Ders kitabında yer alan ölçüt tabloları (`FORM_IN_T3_KONUSMA_CRITERIA`, `FORM_IN_T3_YAZMA_CRITERIA`), öz değerlendirme formları, akran formu ve genel gözlem formu öğrencinin eylemini ve yansıtmasını destekler; ancak programın açıkça şart koştuğu dereceli puanlama anahtarı yapısını içermez. Programdaki çok boyutlu ölçütler doğrultusunda bu eksiklik `analytic_rubric` formatında `GENERATE_ASSESSMENT_SUPPORT` desteği ile giderilecektir.

---

## 5. Zorunluluk Testi (Necessity Test) Denetimi

Program kuralı: *"Her REQUIRED kaynak için şu soruyu cevapla: 'Bu kaynak üretilmezse hangi açık program gereksinimi veya gerekli öğrenci kanıtı karşılanmamış kalır?' Somut cevap verilemiyorsa REQUIRED verme."*

1. **Konuşma Becerisi Dereceli Puanlama Anahtarı (RES_T3_05_KONUSMA_RUBRIC):**
   - *Hangi açık program gereksinimi karşılanmamış kalır?* Öğretim programı s. 82 ve s. 86'da *"Sunumlar, dereceli puanlama anahtarı ile puanlanır."* hükmünü koymuştur. Bu kaynak üretilmezse öğretmenin içerik, anlatım, organizasyon ve iletişim alt boyutlarında derecelendirilmiş standartlara dayalı puanlama yapabilmesi mümkün olmaz. Kitaptaki mevcut sunum görevi, ölçüt tablosu, öz değerlendirme, akran ve gözlem formları korunarak yalnızca eksik olan dereceli puanlama anahtarı matrisi üretilecektir. -> **Necessity Test: PASS (REQUIRED)**

2. **İnfografik Metin Yazma Becerisi Dereceli Puanlama Anahtarı (RES_T3_06_YAZMA_RUBRIC):**
   - *Hangi açık program gereksinimi karşılanmamış kalır?* Öğretim programı s. 82 ve s. 88'de *"Öğrencinin yazılı ürünleri dereceli puanlama anahtarı ile puanlanır."* şartını koşmuştur. Bu kaynak üretilmezse infografik metin ürününün anlam, dil ve görsel ögelerin kullanımı, özgünlük, tutarlılık, doğruluk, yazım ve noktalama ölçütlerinde derecelendirilmiş puanlanması karşılanmamış kalır. Kitaptaki mevcut yazma görevi, revizyon adımları, öz/akran formları korunarak yalnızca dereceli puanlama anahtarı üretilecektir. -> **Necessity Test: PASS (REQUIRED)**

3. **Diğer 12 Öğrenme Çıktısı:**
   - Kitaptaki metinler ve etkinlikler öğrenci eylemlerini ve kanıtlarını eksiksiz karşılamaktadır (`REUSE_TEXTBOOK`, Priority: `NOT_NEEDED`).

---

## 6. Kalite Güvencesi (Quality Assurance - QA) Matrisi

| QA Başlığı | Sonuç | Gerekçe ve Doğrulama Notu |
| :--- | :---: | :--- |
| **Curriculum QA** | 🟢 **PASS** | 14 ÖÇ, sayfa aralıkları (s. 80-88) ve ders saatleri (43 saat) `curriculum_map.json` üzerinden verbatim doğrulanmıştır. |
| **Textbook QA** | 🟢 **PASS** | Kitap s. 144-219 arasındaki 6 bölüm, 3 metin, 15 etkinlik ve 8 form `textbook_map.json` ile %100 eşleştirilmiştir. |
| **Version QA** | 🟢 **PASS** | Program yılı (2024) ve ders kitabı sürümü (MEB 2024) tam uyumludur; sürüm çelişkisi yoktur. |
| **Needs QA** | 🟢 **PASS** | 4 temel alan ihtiyacı (`NEED_T3_01` ila `04`) ön bilgi, yanılgı, eylem, kanıt ve dereceli puanlama anahtarı ihtiyacıyla eksiksiz tanımlanmıştır. |
| **Resource Plan QA** | 🟢 **PASS** | 6 kaynak planı (4 `REUSE_TEXTBOOK`, 2 `GENERATE_ASSESSMENT_SUPPORT`) doğru önceliklerle (`REQUIRED: 2`, `NOT_NEEDED: 4`) yapılandırılmıştır. |
| **Necessity QA** | 🟢 **PASS** | Yalnızca programın zorunlu kıldığı eksik dereceli puanlama anahtarları `REQUIRED` yapılmış, kitapta mevcut etkinlikler mükerrer üretilmemiştir. |
| **Alignment/Coverage QA** | 🟢 **PASS** | 12 COVERED, 2 PARTIALLY_COVERED (TDE3.4, TDE4.4) durumundadır; locator ve gerekçe zinciri tamdır. |
| **Content QA** | 🟢 **PASS** | Tüm metinler ('Eskici', 'Bizim Akdeniz'den', 'Nevruz Belgeseli') resmî MEB haritalarıyla olgusal olarak tam örtüşmektedir. |
| **Assessment QA** | 🟢 **PASS** | 8 form yapısal türlerine göre doğru sınıflandırılmış, `assessment_criteria_table` ile `analytic_rubric` ayrımına tam uyulmuştur. |
| **Differentiation QA** | 🟢 **PASS** | Destekleme/zenginleştirme notları incelenmiş, temel hedeflerin kapsama durumunu düşürmediği teyit edilmiştir. |
| **Accessibility QA** | 🟢 **PASS** | Çok modlu video karekodu, basılı metin okunabilirliği ve form erişilebilirliği doğrulanmıştır. |
| **Copyright QA** | 🟢 **PASS** | Kitap metinleri kopyalanmamış, salt yapısal locator ve başlık referansları kullanılmıştır. |
| **Safety QA** | 🟢 **PASS** | Fiziksel veya dijital güvenlik riski taşıyan etkinlik bulunmamaktadır. |
| **Privacy QA** | 🟢 **PASS** | Öğrenciden gereksiz kişisel veri veya hesap kaydı talep edilmemektedir. |
| **Teacher Review** | 🟢 **PASS** | Öğretmen değerlendirme araçları ve puanlama gereksinimleri netleştirilmiştir. |

---

## 7. Nihai Değerlendirme ve Karar

- **Analiz Edilen Tema:** 9. Sınıf Türk Dili ve Edebiyatı — 3. Tema: Anlamın Yapı Taşları
- **Toplam Hedef:** 14 Öğrenme Çıktısı
- **Coverage Durumu:** 12 COVERED / 2 PARTIALLY_COVERED (TDE3.4, TDE4.4) / 0 NOT_COVERED
- **Üretim Kararı Dağılımı:** 12 REUSE_TEXTBOOK / 2 GENERATE_ASSESSMENT_SUPPORT (Planlanan: 4 REUSE, 2 GENERATE_ASSESSMENT_SUPPORT)
- **Kaynak Öncelikleri Dağılımı:** 2 REQUIRED / 0 RECOMMENDED / 0 OPTIONAL / 4 NOT_NEEDED
- **Çelişki / Belirsizlik:** 0 map_conflict / 0 unresolved
- **NİHAİ TEMA DONDURMA DURUMU (THEME_03_FREEZE_FINAL):** 🟢 **PASS**
