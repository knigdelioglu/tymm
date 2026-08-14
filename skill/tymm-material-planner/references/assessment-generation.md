# Assessment Generation Standard & Invariant Specification

`ASSESSMENT_GENERATION_STANDARD_VERSION: 1.0.0`

## 1. Scope and Purpose

Bu doküman, Türkiye Yüzyılı Maarif Modeli (TYMM) materyal üretim ekosisteminde üretilecek tüm ölçme-değerlendirme araçları (dereceli puanlama anahtarı / analitik rubrik, süreç kontrol listesi, dereceleme ölçeği, öz / akran değerlendirme formu, öğretmen gözlem formu, biçimlendirici değerlendirme ve öğretmen değerlendirme destekleri) için bağlayıcı, tekil ve evrensel kalite standardıdır.

Bu standart:
- Tek bir derse (TDE, Fizik, Matematik, Tarih vb.) veya kademeye özel değildir; tüm ders ve sınıf düzeylerine uygulanır.
- Yalnızca analitik rubriklere değil, tüm değerlendirme araç ailelerine (`analytic_rubric`, `checklist`, `rating_scale`, `assessment_criteria`, `self_assessment`, `peer_assessment`, `teacher_evaluation_form`) uygulanır.
- Modelin serbest metin üretimindeki halüsinasyon, kaynak dışı nicel parametre uydurma, yapay puan bandı/baraj türetme ve ölçüt kapsam kirlenmesini engellemek üzere **fail-closed** mimariyle çalışır.

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

Materyal üretilmeden önce aşağıdaki 6 ön koşul doğrulanmalıdır:

```
[Pre-Generation Assertion Gate]
 ├── 1. SOURCE_BOUND_PARAMETERS: Tüm süre, miktar, baraj ve ağırlıklar doğrulanmış mı?
 ├── 2. CRITERION_SCOPE_RESOLVED: Her ölçütün ölçtüğü boyut net ve saf mı?
 ├── 3. LEVEL_MODEL_RESOLVED: 4 düzeyli model criterion-neutral tanımlandı mı?
 ├── 4. SCORING_MODEL_RESOLVED: 1-4 ham ortalama ve opsiyonel 100 gösterimi ayrıldı mı?
 ├── 5. STUDENT_TEACHER_SEMANTICS_RESOLVED: İki görünümde de standart aynı mı?
 └── 6. PROVENANCE_RESOLVED: Origin enum ve descriptor origin doğru ayrıldı mı?
```

Herhangi bir ön koşul sağlanamazsa üretim başlatılmaz (**FAIL CLOSED**).

---

## 12. Post-Generation Multi-Dimensional QA Suite

Üretilen her değerlendirme materyali aşağıdaki 12 QA denetiminden geçmek zorundadır:

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

### Sonuç Durumu:
- Herhangi bir FAIL → **BLOCKED**
- Sıfır FAIL ve öğretmen inceleme gereksinimi → **REVIEW_REQUIRED**
