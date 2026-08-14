# Sources, provenance, and rights

## Amaç

Bu reference, input authority, kaynak edinimi, provenance ve telif kararlarını tek bir veri sözleşmesinde toplar. Kullanıcının sağladığı resmî öğretim programı ve resmî ders kitabı temel grounding katmanıdır; haricî kaynak yalnız program–kitap analizi sonunda doğrulanmış bir gap için edinilir.

Araştırma notu tasarım kaynağıdır; çalışma sırasında resmî program veya ders kitabının yerine geçmez.

## Input authority ve kaynak hiyerarşisi

Öncelik sırası:

1. kullanıcının sağladığı resmî öğretim programı — normatif/birincil,
2. kullanıcının sağladığı resmî ders kitabı — uygulama ve içerik,
3. kullanıcının sağladığı diğer resmî MEB belgeleri,
4. gerektiğinde MEB/TYMM/TTKB web doğrulaması,
5. gap için seçilen güvenilir haricî kaynak.

Kullanıcı program veya kitap dosyasını sağlamışsa web sonucu onun yerine sessizce geçirilemez. Web doğrulaması yalnız dosya eksikse, kimlik/sürüm/güncellik belirsizse, program–kitap çelişiyorsa veya açık doğrulama gerekiyorsa kullanılır.

Haricî kaynak hiyerarşisi:

- A: MEB/TYMM/TTKB/mevzuat ve ilgili resmî kurumlar,
- B: resmî istatistik, kamu/bilim kurumu, arşiv, kütüphane veya özgün veri,
- C: üniversite, akademik yayın veya güvenilir kurumsal kaynak,
- D: blog, genel web veya arama sonucu.

D seviyesi tek başına doğrulama kaynağı olamaz. Haricî kaynakta authority, tarih, bağlam, yaş/ders uygunluğu ve haklar kaydedilmeden kullanım kararı verilmez.

## Provenance modeli

Her provenance kaydı aşağıdaki alanları içerir:

- item_id
- origin
- source_id
- source_url_or_file
- source_locator
- retrieved_at
- verbatim
- derived_from
- transformation
- verification_status

### Alan kuralları

- item_id: çıkarılan veya üretilen bilginin kararlı kimliği.
- origin: aşağıdaki kontrollü değerlerden biri.
- source_id: kaynak kartındaki kimlik; doğrudan kullanıcı dosyası için de oluşturulur.
- source_url_or_file: URL veya tam/çalışma alanına göre çözümlenebilir dosya konumu.
- source_locator: sayfa, ünite/tema, bölüm, tablo, şekil, etkinlik, paragraf veya dosya aralığı; belirsizse REVIEW.
- retrieved_at: dosyanın alındığı veya web kaynağının erişildiği zaman.
- verbatim: doğrudan aktarım için true; çıkarım/yeniden ifade için false.
- derived_from: dayanak item_id/source_id listesi; doğrudan resmî extract için boş liste kullanılabilir, AI eşleştirmesinde boş bırakılamaz.
- transformation: NONE, EXTRACTED, SUMMARIZED, NORMALIZED, TRANSLATED veya türetilen işlemin kısa açıklaması.
- verification_status: VERIFIED, REVIEW, UNVERIFIED, CONFLICTED veya NOT_FOUND.

### origin kontrollü değerleri

- official_curriculum
- official_textbook
- official_meb_document
- official_regulation
- authoritative_external_source
- generated_activity
- pedagogical_recommendation

### Değişmezler

- Resmî kodlar, öğrenme çıktıları, süreç bileşenleri, değerler ve program ifadeleri generate edilmez; extract edilir ve locator ile saklanır.
- generated_activity veya pedagogical_recommendation, resmî hizalama iddiasında bulunuyorsa non-empty derived_from taşır. derived_from yoksa yalnız AI tasarımı/önerisi olarak etiketlenir; resmî kaynak gibi sunulamaz.
- Bir öğe resmî kaynaktan özetlenmişse verbatim=false ve transformation açıkça yazılır; özgün ifade ile özet karıştırılmaz.
- source locator veya verification_status unresolved ise ilgili resmî alan doldurulmuş kabul edilmez; fail-closed uygulanır.
- Provenance, materyalin hangi kısmının resmî extract, kitap içeriği, haricî kaynak veya üretilmiş pedagojik tasarım olduğunu ayırabilmelidir.

## source_card modeli

Her source_card en az şu alanları taşır:

- source_id
- title
- creator_or_institution
- source_type
- url_or_file
- publication_date
- retrieved_at
- authority_level
- license_or_copyright
- usable_scope
- curriculum_relevance
- student_level
- excerpt_or_data_used
- transformation_needed
- linked_need_id
- linked_resource_plan_id
- verification_status
- notes

### Alanların işletim anlamı

- source_id: kaynak kartının tekil kimliği.
- title: kitap, belge, veri seti, medya veya sayfa başlığı.
- creator_or_institution: yazar, kurum, arşiv veya yayımlayan kuruluş.
- source_type: curriculum, textbook, regulation, official_document, dataset, primary_source, secondary_source, media veya benzeri açık sınıf.
- url_or_file: web URL'si veya kullanıcı tarafından sağlanan dosyanın çözümlenebilir konumu.
- publication_date: biliniyorsa tarih; bilinmiyorsa UNKNOWN, tahmin edilmez.
- retrieved_at: erişim/alım zamanı.
- authority_level: A, B, C veya D.
- license_or_copyright: aşağıdaki kontrollü hak durumlarından biri.
- usable_scope: sınıfta kullanılabilecek bölüm, sayfa, veri aralığı, bağlantı veya dönüşüm sınırı.
- curriculum_relevance: ilgili program item, need_id veya gap ile gerekçeli ilişki.
- student_level: kademe, sınıf, ders ve dil/erişilebilirlik uygunluğu.
- excerpt_or_data_used: gerçekten kullanılacak kısa alıntı veya veri; kullanılmayacak içerik yazılmaz.
- transformation_needed: link-only, sınırlı alıntı, özet, veri dönüştürme, özgünleştirme veya benzeri işlem.
- linked_need_id: kaynağı gerektiren need_id veya need_id listesi.
- linked_resource_plan_id: kaynağı kullanan resource_plan_id veya liste.
- verification_status: VERIFIED, REVIEW, UNVERIFIED, CONFLICTED veya NOT_FOUND.
- notes: çelişki, OCR, hak belirsizliği, öğretmen incelemesi veya kullanım sınırı.

source_card doğrudan kullanılacaksa linked_need_id ve linked_resource_plan_id boş bırakılamaz; kaynak yalnız keşif içinse usable_scope içinde keşif olduğu yazılır ve öğrenci materyaline aktarılmaz.

## Telif ve yeniden kullanım

license_or_copyright yalnız şu değerlerden biri olabilir:

- PUBLIC_DOMAIN
- OPEN_LICENSE
- OFFICIAL_REUSE_ALLOWED
- LIMITED_QUOTATION
- LINK_ONLY
- UNKNOWN_RIGHTS
- DO_NOT_USE

### Hak invariant'ları

- UNKNOWN_RIGHTS ve DO_NOT_USE içerik öğrenci materyaline gömülmez.
- Kullanıcının kitabı veya dosyayı yüklemiş olması telif hakkını ortadan kaldırmaz.
- Resmî ders kitabı için sayfa/bölüm referansı, kitaba dayalı yeni ve bağımsız görev veya gerekli sınırlı alıntı tercih edilir.
- Hakları doğrulanmamış uzun edebî metin, görsel, ses veya video otomatik çoğaltılmaz.
- LINK_ONLY kaynak öğrenci belgesine tam içerik olarak değil, öğretmen yönlendirmesi olarak eklenebilir.
- LIMITED_QUOTATION yalnız amacı ve kapsamı gerekçelendirilmiş kısa alıntı için kullanılır; alıntı kaynağı ve locator ile verilir.
- Kaynağın rights durumu REVIEW/UNKNOWN ise quality_report Copyright QA = REVIEW; DO_NOT_USE ise FAIL ve içerik çıkarılır.

### Ders kitabı kullanım modları

Ders kitabı içeriği için kullanım biçimi de kaydedilir:

- PAGE_REFERENCE
- DERIVED_ACTIVITY
- LIMITED_QUOTATION
- REPRODUCTION_NOT_ALLOWED

Tercih sırası: kitap sayfasına/bölümüne referans, kitaptaki içeriğe dayalı özgün görev, gerekçeli sınırlı alıntı. Uzun metnin otomatik yeniden basılması kullanılmaz.

## Haricî kaynak edinim protokolü

Haricî arama, input_manifest, curriculum_model, textbook_model, instructional_needs_analysis ve gap_analysis sonrasında başlar. Her haricî source_card şu sorulara cevap vermelidir:

1. Hangi remaining_gap veya resource_plan ihtiyacını karşılıyor?
2. Otoritesi ve yayın tarihi nedir?
3. Sınıf/ders/öğrenci düzeyi uygun mudur?
4. Gerçekten hangi veri/alinti/bölüm kullanılacak?
5. Dönüşüm ve lisans sınırı nedir?
6. verification_status nedir?

Bir kaynak bu zincire bağlanamıyorsa external_source_needed=false ve production_decision haricî kaynak kullanımına çevrilmez.

## Fail-closed kuralları

- Resmî program veya gerekli ders kitabı kimliği/sürümü VERIFIED değilse, normal TYMM-aligned üretim tamamlanmaz.
- Program–kitap sınıf, program yılı, tema/ünite yapısı veya sürüm bakımından uyuşmuyorsa PROGRAM_TEXTBOOK_VERSION_MISMATCH verilir; sessiz uzlaştırma yapılmaz.
- Resmî bir alan source locator veya provenance olmadan üretilemez.
- Haricî kaynak yalnız gerekçeli gap'e bağlanabilir.
- Rights, doğruluk, yaş uygunluğu veya güvenlik belirsizliği çözümlenmeden içerik öğrenci materyaline gömülmez.

