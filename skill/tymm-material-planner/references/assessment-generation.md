# Assessment Generation Standard & Invariant Specification

`ASSESSMENT_GENERATION_STANDARD_VERSION: 1.1.1`

## 1. Scope and Purpose

Bu doküman, Türkiye Yüzyılı Maarif Modeli (TYMM) materyal üretim ekosisteminde üretilecek tüm ölçme-değerlendirme araçları (dereceli puanlama anahtarı / analitik rubrik, süreç kontrol listesi, dereceleme ölçeği, öz / akran değerlendirme formu, öğretmen gözlem formu, biçimlendirici değerlendirme ve öğretmen değerlendirme destekleri) için bağlayıcı, tekil ve evrensel kalite standardıdır.

Bu standart:
- Tek bir derse (TDE, Fizik, Matematik, Tarih vb.) veya kademeye özel değildir; tüm ders ve sınıf düzeylerine uygulanır.
- Yalnızca analitik rubriklere değil, tüm değerlendirme araç ailelerine (`analytic_rubric`, `checklist`, `rating_scale`, `assessment_criteria`, `self_assessment`, `peer_assessment`, `teacher_evaluation_form`) uygulanır.
- Modelin serbest metin üretimindeki halüsinasyon, kaynak dışı nicel parametre uydurma, yapay puan bandı/baraj türetme ve ölçüt kapsam kirlenmesini engellemek üzere **fail-closed** mimariyle çalışır.
- Yıllık değerlendirme kararlılığını (`ANNUAL_ASSESSMENT_STABILITY`) ve temalar arası konsolidasyonu (`CROSS_THEME_CONSOLIDATION`) zorunlu kılar.

---

## 2. Core Invariant — Source-Bound Parameter Generation

Ölçme-değerlendirme materyali üretimi sırasında **kaynakta veya onaylı Assessment Design Contract'ta açıkça tanımlanmamış hiçbir değerlendirme parametresi üretilemez**.

Model kendiliğinden kesinlikle aşağıdaki parametreleri **icat edemez**:
1. **Süre ve Zaman Aralıkları**: Dakika, saniye, süre aralığı (örn. "3–5 dakika", "10-15 dk.").
2. **Süre ve Performans Toleransları**: Tolerans değerleri (örn. "±30 saniye tolerans", "±10 kelime").
3. **Miktar ve Sayı Sınırları**: Soru sayısı, adım sayısı, dize/dörtlük/sayfa sayısı, asgari/azami sözcük sayısı (örn. "en az 4 dörtlük", "en az 200 kelime").
4. **Başarı Eşikleri ve Barajlar**: Pass/fail barajı, başarı eşiği (örn. "70 alan geçer", "en az %60 başarı").
5. **Puan Bantları ve Düzey Sınırları**: Yapay aralıklar (örn. "85-100: İleri Düzey", "50-69: Orta").
6. **Ağırlık Katsayıları**: Ölçüt ağırlıkları (örn. "%30 içerik, %20 dil"), aksi sözleşmede belirtilmedikçe eşit ağırlık (`EQUAL_WEIGHT_DEFAULT`) esastır.
7. **Ceza ve Bonus Puanları**: Ek puan, ceza puanı, kırpma veya gecikme cezası.
8. **Tekrar ve Hak Sayısı**: Yeniden deneme hakkı, telafi oturum sayısı (örn. "2 tekrar hakkı verilir").
9. **Gelişim / Yaş Normları**: Kaynakta yer almayan yaş/sınıf performans norm kabulleri.

### Kural ve Güvenli İfade Standardı (Source-Safe Formulations)

Bir nicel değerin materyalde yer alabilmesi için:
- `canonical_generation_context` içinde açıkça doğrulanmış olmalı **VEYA**
- İlgili dersin `Assessment Design Contract` belgesinde açıkça kurala bağlanmış olmalıdır.

Her iki kaynakta da açıkça bulunmayan tüm parametreler için **kaynak-güvenli (parameterized/source-safe)** ifadeler kullanılır:

| YASAK / UYDURMA İFADE | DOĞRU / KAYNAK-GÜVENLİ İFADE |
| :--- | :--- |
| "Konuşmasını 3–5 dakika içinde tamamlar." | "Konuşmasını etkinlik için belirlenen süre içinde tamamlar." |
| "±30 saniyelik süre toleransına uyar." | "Belirlenen süreyi dengeli ve amaca uygun kullanır." |
| "En az 4 dörtlükten oluşan şiir yazar." | "Görev yönergesinde belirtilen yapı ve uzunluğa uygun şiir yazar." |
| "En az 3 farklı edebî sanat kullanır." | "İçerik ve türe uygun edebî sanatlara yer verir." |
| "70 ve üzeri puan alan öğrenci başarılı sayılır." | "Ölçütler düzey bazında biçimlendirici olarak değerlendirilir." |

---

## 3. No Invented Score Bands (Puan Dönüşümü ≠ Başarı Standardı)

Bir değerlendirme sözleşmesi veya materyal standardı `RAW_MEAN_1_TO_4` (1.00–4.00 ham ortalama) ve isteğe bağlı `OPTIONAL_100_SCALE` gibi matematiksel dönüşümler tanımlayabilir.

**Kritik İlke:** Matematiksel dönüşüm cetveli, yeni bir başarı standardı veya geçme/kalma barajı değildir.
- Model, sözleşmede ve resmî programda açıkça yer almayan başarı etiketleri (örn. "89 ve üstü = İleri", "70–84 = Yetkin", "50 = Geçer", "50 altı = Başarısız") **türetemez**.
- Dönüşüm cetvelleri yalnızca sayısal eşdeğerlikleri (örn. 16 ham puan = 100, 15 ham puan = 94, 4 ham puan = 25) gösterebilir.
- Tüm ölçütlerden LEVEL_1 (1 puan) alan bir performansın matematiksel formül gereği 25/100 üretmesi bir mekanik hesaplama sonucudur; bu durum öğrencinin "%25 başarı kazandığı" şeklinde pedagojik olarak yorumlanamaz.

---

## 4. Shared Level Semantics (Ölçüt-Bağımsız Düzey Tanımları)

Ortak performans düzeyleri (örn. LEVEL_1 ila LEVEL_4), tüm değerlendirme araçlarında **ölçüt-bağımsız (criterion-neutral)** kalmalıdır.

### İzin Verilen Evrensel Düzey Eksenleri:
1. **Completeness (Tamlık / Bütünlük)**: Görevin veya ölçütün ne derece eksiksiz yerine getirildiği.
2. **Correctness (Doğruluk)**: İlke, kural ve yöntemlere uygunluk derecesi.
3. **Consistency (Tutarlılık)**: Performansın sürecin/ürünün bütününe yayılma derecesi.
4. **Independence (Bağımsızlık)**: Öğrencinin işlemi kendi başına yürütebilme derecesi.
5. **Support / Guidance Need (Destek ve Yönlendirme İhtiyacı)**: İhtiyaç duyulan öğretimsel rehberlik düzeyi.

### Genel Düzey Tanımlarında Yasaklanan Kavramlar:
Genel düzey tanımının içine alana, türe veya ölçüte özgü yapılar sokulamaz:
- ❌ "özgünlük", "yaratıcılık", "estetik", "etkileyicilik", "zenginlik", "akıcılık", "hız".
Bu kavramlar yalnızca ilgili ölçüt (criterion) bizzat bunları ölçüyorsa o ölçütün kendi hücre betimleyicisi içinde yer alabilir.

### Öğretmen ve Öğrenci Görünümlerinde Anlam Eşitliği:
- Öğretmen rubriğindeki LEVEL_4 anlamı ile öğrenci rubric/checklist görünümündeki LEVEL_4 anlamı **aynı bilişsel ve performans standardını** ifade etmek zorundadır.
- Öğrenci dostu dil sadeleştirme yapabilir; ancak başarı standardını düşüremez veya yeni koşul ekleyemez.

---

## 5. Criterion Scope Purity (Ölçüt Kapsam Saflığı)

Her ölçüt (criterion), yalnızca ve kesinlikle kendi tanımlı boyutunu (construct) ölçmelidir.

### Yapısal Kirlenme (Construct Contamination) Yasağı:
- Bir ölçütün hücre betimleyicisine gizlice başka bir değerlendirme boyutu eklenemez.
- **Örnek 1 (Kapsam Kirlenmesi):** "Türkçenin Doğru Kullanımı" ölçütü dil bilgisi, imla, sözcük uyumu ve cümle yapısını ölçer. Bunun içine kaynakta olmayan zorunlu "zengin edebî söz varlığı ve mecazlar kullanır" şartı eklenemez.
- **Örnek 2 (Kapsam Kirlenmesi):** "İçeriğin Kurgusallığı" ölçütü olay örgüsü, karakter ve mekân tutarlılığını ölçer. Bunun içine "estetik anlatım ve özgün benzetmeler yapar" şartı eklenemez.

### Pre-Generation Scope Kontrolü:
Materyal üretilmeden önce her ölçüt için `CRITERION_SCOPE` netleştirilir:
- *Bu ölçüt tam olarak neyi ölçüyor?*
- *Bu hücredeki her ifade doğrudan bu ölçüte mi ait, yoksa başka bir ölçütün konusu mu?*
- Başka bir ölçüte aitse o ölçüte devredilir; hiçbir resmî ölçüte ait değilse ve kaynakta yoksa metinden çıkarılır.

---

## 6. Observable Descriptor Standard (Gözlenebilir Betimleyici Standardı)

Hücre betimleyicileri somut, gözlenebilir öğrenci eylemine veya ürün kanıtına dayanmalıdır.

### A. Aşırı Mutlaklık ve Kesinlik Yasağı (Absolutism Prohibited):
Öğrencinin performansını siyah-beyaz veya imkânsız uçlara çeken aşırı mutlak ifadeler yasaktır:
- ❌ *Yasak kelimeler:* kusursuz, mükemmel, tamamen, hiçbir, hiç, daima, asla, tüm sınıf, sınıfın ilgisini tamamen kaybeder, hiçbir olumlu etki oluşturamaz.
- ✅ *Önerilen davranışsal niteleyiciler:* çoğunlukla, belirgin biçimde, zaman zaman, sıkça, sınırlı düzeyde, gözlenebilir şekilde, anlatımın takibini zorlaştırır, iletişimi belirgin biçimde aksatır.

### B. Zihin Okuma ve İçsel Durum Tahmini Yasağı (No Mind-Reading):
Öğrencinin iç psikolojisini, motivasyonunu veya duygusal niyetini varsayan ifadeler yasaktır:
- ❌ *Yasak ifadeler:* özgüvensizdir, isteksizdir, ilgisizdir, dikkatsizdir, heyecanına yenik düşer, umursamazdır.
- ✅ *Önerilen eylem ifadeleri:* ses tonunu ortama göre ayarlamakta zorlanır, göz temasını sürdürmekte desteğe ihtiyaç duyar, hazırlık notlarına sık sık başvurur.

---

## 7. Adjacent Level Distinction (Komşu Düzey Ayrımı)

Performans basamakları (`LEVEL_4` → `LEVEL_3` → `LEVEL_2` → `LEVEL_1`) yalnızca yüzeysel sıfat değişiklikleriyle türetilemez.

- ❌ **Yasak Yapı:** "Çok iyi yapar" → "İyi yapar" → "Orta düzeyde yapar" → "Zayıf yapar".
- ✅ **Doğru Yapı:** Her komşu düzey arasında gözlemcinin açıkça ayırt edebileceği niteliksel/davranışsal bir eşik bulunmalıdır:
  - `LEVEL_4`: Ölçütü eksiksiz ve bağımsız sergiler; aksama gözlenmez.
  - `LEVEL_3`: Ölçütü genel olarak başarıyla sergiler; küçük aksamalar genel anlam akışını/bütünlüğü bozmaz.
  - `LEVEL_2`: Ölçütü kısmen sergiler; aksamalar anlatımın takibini güçleştirir ve yönlendirmeye ihtiyaç duyar.
  - `LEVEL_1`: Ölçüte ilişkin performans sınırlıdır; iletişimi/bütünlüğü belirgin biçimde kesintiye uğratır ve doğrudan rehberlik gerektirir.

---

## 8. Feedback Standard (Gözlenen Kanıt Modeli)

Öğretmen geri bildirim alanları ve örnekleri genel övgü veya kişilik etiketlemesi içeremez.

### Formülasyon: `OBSERVED EVIDENCE → EFFECT → NEXT STEP`
1. **Observed Evidence (Gözlenen Somut Kanıt)**: Öğrencinin yaptığı somut eylem veya üründeki durum.
2. **Effect (Öğrenme/İletişim Üzerindeki Etkisi)**: Bu eylemin anlama, dinleyiciye veya metin akışına etkisi.
3. **Next Step (Geliştirici Sonraki Adım)**: Öğrencinin bir sonraki çalışmada uygulayacağı net pedagojik öneri.

- ❌ **Yasak:** "Çok başarılı bir sunum yaptın, tebrikler." / "Sunumun yetersizdi."
- ✅ **Örnek:** "Karakterin duygu değişimlerini ses tonuna tutarlı biçimde yansıttın; bu durum anlatımın takip edilmesini kolaylaştırdı. Bir sonraki sunumunda göz temasını sınıfın farklı bölümlerine daha dengeli dağıtmayı dene."

---

## 9. Student-Facing View Consistency

Öğrenciye yönelik rubrik, kontrol listesi veya kılavuz görünümleri üretilirken:
1. Öğretmen rubriğindeki ölçüt setinin birebir aynısı kullanılır.
2. Düzey anlamları (level semantics) korunur.
3. Teknik provenance alanları (origin, hash, locator, derived_from) öğrenci görünümüne basılmaz.
4. Öğrenciye sözleşmede veya resmî görevde bulunmayan ek yükümlülükler getirilemez.
5. İfadeler anlaşılır ve motive edici şekilde sadeleştirilebilir; ancak ölçme çıtası değiştirilemez.

---

## 10. Provenance Boundary Specification

Ölçme materyallerinde kaynak kategorileri birbirine karıştırılamaz:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. OFFICIAL REQUIREMENT (Resmî Program Hükmü - Rank 1)      │
│    Verbatim: "Öğretmen değerlendirmesi dereceli puanlama    │
│    anahtarı ile gerçekleştirilir."                          │
├─────────────────────────────────────────────────────────────┤
│ 2. TEXTBOOK PROVIDES (Ders Kitabı Karşılığı - Rank 2)       │
│    Örn: assessment_criteria_table (s. 129)                  │
├─────────────────────────────────────────────────────────────┤
│ 3. REMAINING GAP (Yapısal Boşluk - Rank 5)                  │
│    Kitaptaki formun düzey betimleyicisi barındırmaması      │
├─────────────────────────────────────────────────────────────┤
│ 4. SELECTED IMPLEMENTATION (Seçilen Pedagojik Format)       │
│    analytic_rubric / process_checklist                      │
├─────────────────────────────────────────────────────────────┤
│ 5. CRITERION ORIGIN (Ölçüt Kökeni)                          │
│    official_curriculum | official_textbook |                │
│    pedagogical_recommendation                               │
├─────────────────────────────────────────────────────────────┤
│ 6. DESCRIPTOR ORIGIN (Hücre Betimleyici Kökeni)             │
│    Kesinlikle: pedagogical_recommendation                   │
├─────────────────────────────────────────────────────────────┤
│ 7. SCORING DISPLAY (Puanlama Gösterimi)                     │
│    RAW_MEAN_1_TO_4 (asıl) + OPTIONAL_100_SCALE (yardımcı)  │
└─────────────────────────────────────────────────────────────┘
```

- Program "dereceli puanlama anahtarı" diyorsa "Program analitik rubrik istemektedir" denilemez; `analytic_rubric` yalnızca `selected_implementation` olarak kayda geçer.
- Hücre betimleyicileri resmî metinde harfi harfine yer almıyorsa daima `descriptor_origin: pedagogical_recommendation` olarak işaretlenir.

---

## 11. Pre-Generation Assertions (Üretim Öncesi Kesin Kontroller)

Materyal üretilmeden önce aşağıdaki 12 ön koşul doğrulanmalıdır:

```
[Pre-Generation Assertion Gate]
 ├── 1. SOURCE_BOUND_PARAMETERS: Tüm süre, miktar, baraj ve ağırlıklar doğrulanmış mı?
 ├── 2. CRITERION_SCOPE_RESOLVED: Her ölçütün ölçtüğü boyut net ve saf mı?
 ├── 3. LEVEL_MODEL_RESOLVED: 4 düzeyli model criterion-neutral tanımlandı mı?
 ├── 4. SCORING_MODEL_RESOLVED: 1-4 ham ortalama ve opsiyonel 100 gösterimi ayrıldı mı?
 ├── 5. STUDENT_TEACHER_SEMANTICS_RESOLVED: İki görünümde de standart aynı mı?
 ├── 6. PROVENANCE_RESOLVED: Origin enum ve descriptor origin doğru ayrıldı mı?
 ├── 7. CROSS_THEME_CONSOLIDATION_COMPLETE: Temalar arası konsolidasyon yapıldı mı?
 ├── 8. ANNUAL_REUSE_CHECK_COMPLETE: Yıllık yeniden kullanım önceliği değerlendirildi mi?
 ├── 9. GAP_TO_ARTIFACT_MAPPING_COMPLETE: Tüm gap instance'lar tekil artifact'lara bağlandı mı?
 ├── 10. TASK_BINDING_RESOLVED: Görev bağlamı core criteria'yı bozmadan izole edildi mi?
 ├── 11. CORE_CRITERIA_STABILITY_RESOLVED: Yıllık ölçüt kararlılığı doğrulandı mı?
 └── 12. NEW_ARTIFACT_JUSTIFICATION_RESOLVED: Yeni artifact varsa resmî gerekçe ve locator doğrulandı mı?
```

Herhangi bir ön koşul sağlanamazsa üretim başlatılmaz (**FAIL CLOSED**).

---

## 12. Post-Generation Multi-Dimensional QA Suite

Üretilen her değerlendirme materyali aşağıdaki 19 QA denetiminden geçmek zorundadır:

1. **UNSUPPORTED_PARAMETER_QA**: Kaynakta veya sözleşmede olmayan süre, miktar, soru sayısı, tolerans, baraj veya katsayı var mı? (PASS / FAIL)
2. **NO_INVENTED_SCORE_BANDS_QA**: Sayısal dönüşümden yetkisiz başarı seviyesi/barajı (örn. "70=başarılı") türetilmiş mi? (PASS / FAIL)
3. **SHARED_LEVEL_SEMANTICS_QA**: Genel düzey tanımları criterion-neutral eksenlerde kalmış mı? (PASS / FAIL)
4. **STUDENT_LEVEL_SEMANTICS_QA**: Öğrenci görünümü öğretmen rubriği ile aynı başarı standardını koruyor mu? (PASS / FAIL)
5. **DESCRIPTOR_OBSERVABILITY_QA**: Betimleyiciler içsel zihin okuma yerine somut gözlenebilir eylemlere dayanıyor mu? (PASS / FAIL)
6. **DESCRIPTOR_ABSOLUTISM_QA**: "Kusursuz", "hiçbir", "tamamen", "asla" gibi aşırı mutlak ifadelerden arındırılmış mı? (PASS / FAIL)
7. **ADJACENT_LEVEL_DISTINCTION_QA**: Komşu düzeyler yalnızca sıfatla değil, belirgin niteliksel/davranışsal farkla ayrılmış mı? (PASS / FAIL)
8. **CRITERION_SCOPE_PURITY_QA**: Ölçütler arasına yabancı yapılar veya gizli ek şartlar karışmış mı? (PASS / FAIL)
9. **FEEDBACK_EVIDENCE_QA**: Geri bildirimler `EVIDENCE → EFFECT → NEXT STEP` yapısına uyuyor mu? (PASS / FAIL)
10. **PROVENANCE_BOUNDARY_QA**: Resmî gereksinim, seçilen format, ölçüt kaynağı ve betimleyici kökeni doğru etiketlenmiş mi? (PASS / FAIL)
11. **SOURCE_RIGHTS_QA**: Uzun telifli metin kopyalanmadan sayfa/locator referansı verilmiş mi? (PASS / FAIL)
12. **TEACHER_REVIEW_GATE_QA**: Materyal `REVIEW_REQUIRED` statüsüyle öğretmene teslim edilmiş mi? (PASS / REVIEW_REQUIRED)
13. **ANNUAL_ASSESSMENT_STABILITY_QA**: Aynı ders, sınıf ve beceri alanında yıllık kararlı ölçüt seti korunmuş mu? (PASS / FAIL)
14. **CROSS_THEME_DUPLICATION_QA**: Aynı beceri yapısını ölçen gereksiz tema bazlı yinelenen rubrikler engellenmiş mi? (PASS / FAIL)
15. **GAP_ARTIFACT_MAPPING_QA**: Her gap instance tekil bir yıllık artifact'a açıkça haritalanmış mı? (PASS / FAIL)
16. **CORE_CRITERIA_STABILITY_QA**: Yıllık core ölçüt seti tema/görev değişimleriyle sessizce bozulmamış mı? (PASS / FAIL)
17. **TASK_BINDING_ISOLATION_QA**: Göreve özgü yönergeler core ölçüt setini değiştirmeden task binding katmanında tutulmuş mu? (PASS / FAIL)
18. **CRITERION_EXTENSION_JUSTIFICATION_QA**: Temaya özgü ek ölçütler resmî kaynakça gerekçelendirilmiş ve izole edilmiş mi? (PASS / FAIL)
19. **NEW_ARTIFACT_JUSTIFICATION_QA**: Yeni artifact türetimi yalnız construct farkı durumunda ve explicit locator ile yapılmış mı? (PASS / FAIL)

### Sonuç Durumu:
- Herhangi bir FAIL → **BLOCKED**
- Sıfır FAIL ve öğretmen inceleme gereksinimi → **REVIEW_REQUIRED**

---

## 13. Annual Assessment Stability and Cross-Theme Reuse

### A. Temel Pedagojik Karar ve Invariant: `ANNUAL_ASSESSMENT_STABILITY`
Aynı ders (`course`), sınıf düzeyi (`grade`), temel beceri alanı (`skill domain`) ve ölçülen yapı (`core construct`) içindeki değerlendirme araçları varsayılan olarak **YILLIK ve KARARLI** olmalıdır.

> **Kritik Kural:** Tema veya görev değişikliği tek başına `GENERATE_NEW_ASSESSMENT` kararı **DOĞURAMAZ** (`THEME_CHANGE_ALONE != NEW_RUBRIC`).

Öğrencinin yıl boyunca konuşma ve yazmada mümkün olduğunca aynı temel ölçütlerle değerlendirilmesi, değerlendirme ölçütlerini önceden bilmesi ve bilişsel tutarlılığın sağlanması hedeflenir.

### B. Karar ve Öncelik Hiyerarşisi (Reuse Priority Hierarchy):
Bir değerlendirme açığı tespit edildiğinde şu öncelik sırası işletilir:
1. `REUSE_ANNUAL_CORE`: Mevcut yıllık core rubrik/araç doğrudan kullanılır.
2. `REUSE_WITH_TASK_BINDING`: Yıllık core rubrik korunur; ilgili tema/etkinliğin görev bağlamı (task binding) eklenir.
3. `REUSE_WITH_CRITERION_EXTENSION`: Resmî kaynakta temaya özgü ek bir zorunlu ölçüt varsa, core seti bozmadan temaya özgü ek ölçüt bağlanır.
4. `GENERATE_NEW_ASSESSMENT`: Yalnızca resmî requirement **gerçekten farklı bir construct** ölçüyorsa VEYA mevcut yıllık core artifact resmî zorunlu ölçütleri karşılayamıyorsa yeni artifact üretilir (Zorunlu: explicit rationale + source locator + FAIL-CLOSED).

### C. GAP INSTANCE ≠ ARTIFACT Ayrımı:
Mimaride iki kavram kesin sınırlarla ayrılır:
- `ASSESSMENT_GAP_INSTANCE`: Belirli tema/çıktıda tespit edilmiş değerlendirme desteği açığı (audit, provenance ve izlenebilirlik kaydı).
- `ANNUAL_ASSESSMENT_ARTIFACT`: Bir veya daha fazla gap instance'ı karşılayan gerçek, konsolide öğretmen ve öğrenci değerlendirme materyali.

```
[GAP_T2_KONUSMA] ──┐
[GAP_T3_KONUSMA] ──┼──> [TDE9_KONUSMA_RUBRIC] (Annual Core Artifact)
[GAP_T4_KONUSMA] ──┘
```

Eski gap kayıtları audit kanıtı olarak korunur; ancak üretim kuyruğu consolidated artifact registry üzerinden çalışır.

### D. Core Rubric + Task Binding Mimarisi:
Yıllık bir rubrik iki katmandan oluşur:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ANNUAL CORE (Kararlı Yıllık Çekirdek)                   │
│    - Stable criterion set (Kararlı ölçüt seti)              │
│    - Stable 4-level semantics (Kararlı düzey semantiği)     │
│    - Stable scoring mechanics (1.00-4.00 + opsiyonel 100)   │
│    - Stable feedback structure (EVIDENCE -> EFFECT -> NEXT) │
├─────────────────────────────────────────────────────────────┤
│ 2. TASK BINDING (Görev Bağlamı Katmanı)                    │
│    - theme_id / activity_id / block_id                      │
│    - task_title (Görev / Atölye başlığı)                   │
│    - evidence_being_observed (Gözlenen somut eylem/kanıt)   │
│    - source_locators (Program ve kitap sayfa referansı)     │
│    - task_specific_instructional_note                       │
└─────────────────────────────────────────────────────────────┘
```

Task binding katmanı çekirdek ölçüt setini keyfi olarak değiştiremez. Görev başlığı veya konusu değişti diye temel başarı ölçütleri baştan yazılmaz.

### E. Criterion Extension Politikası (`REUSE_WITH_CRITERION_EXTENSION`):
Bir temada resmî kaynakta gerçekten ek bir zorunlu ölçüt varsa:
- Hemen yeni rubrik oluşturulmaz.
- Ölçüt `CRITERION_EXTENSION` olarak tanımlanır ve yalnızca ilgili temaya/göreve scope edilir.
- Extension mutlaka resmî kaynak locator'ı ve verbatim dayanak taşımalıdır.
- Annual core ölçüt setini sessizce değiştiremez.
- Extension sayısı veya yapısı ana aracı anlamsız kılacak düzeye ulaşmadıkça yeni artifact üretilmez.

### F. Öğrenci Açısından Stabilite:
- Teacher-facing ve student-facing ölçüt setleri annual core seviyesinde kararlıdır.
- Tema değiştiğinde öğrenci "bu temada bambaşka ölçütlerle puanlanacağım" algısına düşürülmez; yalnızca görevin nasıl uygulanacağı değişir.

### G. Assessment Üretim Pipeline'ı:
Assessment materyal üretim akışı şu zorunlu adımları izler:

```
gap_analysis
    ↓
assessment_gap_instances
    ↓
CROSS_THEME_ASSESSMENT_CONSOLIDATION
    ↓
annual_assessment_artifact_registry
    ↓
task_bindings
    ↓
generation_context
    ↓
material_generation
```
Değerlendirme açığı tespit edildikten hemen sonra doğrudan materyal üretimi yapılamaz; önce temalar arası konsolidasyon (`CROSS_THEME_CONSOLIDATION`) zorunludur.

### H. Normalized Shared Constructs vs. Exact Criterion Match
Cross-theme yıllık dereceli puanlama anahtarı konsolidasyonunda iki kavram kesinlikle ayrılır:
1. **`EXACT_CRITERION_MATCH`**: Ölçüt adı, resmî tanımı ve kapsamı farklı temalar arasında harfi harfine aynı olduğunda kullanılır.
2. **`NORMALIZED_SHARED_CONSTRUCT`**: Farklı temalarda farklı ifadelerle (örn. "içeriğin kurgusallığı", "içeriğe uygunluk", "bilgilerin doğruluğu") ifade edilen resmî ölçütlerin üst düzey, kanıtlanabilir ortak bir değerlendirme boyutu altında normalize edilmesidir.

> **Kritik Kurallar:**
> - Cross-theme konsolidasyon "kriterler tamamen aynı / %100 birebir örtüşüyor" varsayımına dayandırılamaz; kanıtlanabilir `NORMALIZED_SHARED_CONSTRUCT` yaklaşımı esas alınmalıdır.
> - Bir construct'ın `ANNUAL_CORE` kabul edilebilmesi için tüm konsolide temalarda güçlü kanıtının bulunması şarttır. Yalnızca tek bir temaya/türe özgü olan unsurlar (örn. şiir ahenk ögeleri, otobiyografi gerçekliği/kronolojisi, sunumda görsel/slayt kullanımı) yıllık core ölçüt hücre betimleyicilerine zorunlu şart olarak gömülemez; bunlar kesinlikle `TASK_SPECIFIC_BINDING` katmanında tutulur.
> - Yıllık core ölçüt sayısı yapay olarak sabitlenemez (örn. "mutlaka 5 ölçüt olmalı" kuralı yoktur). Kanıtlanan geçerli core construct sayısı 4 ise yıllık rubrik 4 ölçütlü olarak yapılandırılır.

### I. Process Support vs. Annual Core Scope Ayrımı
Bir ölçme-değerlendirme aracının kapsamı (scope) belirlenirken:
1. **`ANNUAL_CORE`**: Yıl boyunca her temada karne/derecelendirme ve temel performans standardı olarak işletilen, birden fazla temada REQUIRED açığı kapatan konsolide araçlardır.
2. **`REUSABLE_PROCESS_SUPPORT`**: Belirli bir temada (`REQUIRED`) doğan ancak süreç aşamaları (örn. yazma sürecinin 5 evrensel basamağı: Hazırlık, Planlama, Taslak, Redaksiyon, Paylaşım) tüm temalarda biçimlendirici ve notsuz olarak tekrar kullanılabilir (`REUSABLE_ACROSS_THEMES`) olan süreç araçlarıdır. Tek bir temada açık kapatan süreç araçları yapay biçimde `ANNUAL_CORE` olarak adlandırılamaz.
