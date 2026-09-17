# TDE 11 Öğretmen Kitabı V3

Teacher Guide V3, 11. sınıf Türk Dili ve Edebiyatı ders kitabını öğretmen kitabının birincil düzenleme ekseni yapar. Tema 1 ayrı bir altın örnek değildir; Tema 1–4 aynı motor, şema, provenance zinciri ve kalite sözleşmesiyle üretilir.

## Yetki ve kaynak zinciri

Bir görevin kitap metni ve sayfası resmî ders kitabı PDF'sinden gelen V2.3 mirror kayıtlarıyla izlenir. Ders kitabı prompt'u bulunabildiğinde `book_prompt` alanına aktarılır; kısa doğrulanmış ifade `VERIFIED_SUMMARY`, kaynaktan doğrulanmış kısa birebir ifade `VERBATIM_SHORT` olarak işaretlenir. Soru metni çözülemiyorsa sistem metin uydurmaz ve `REVIEW_REQUIRED` üretir. `LOCATOR_ONLY`, soru görevi için release çıktısında kabul edilen bir temsil biçimi değildir.

Beklenen cevap, mevcut canonical teacher guide item'larından ve source-verified component registry'lerinden projekte edilir. V3, canonical answer'ı yeniden yazıp sessizce değiştirmez; `answer_component_keys` ile gruplandırılmış cevap parçalarının hangi alt soruya gittiğini açıkça kaydeder. Pedagojik alanlar bu cevaba, kitap bağlamına, metin/görsel türüne ve görevin öğretim amacına göre türetilir.

Kavramsal zincir şöyledir:

```text
resmî ders kitabı PDF'si
        ↓
textbook_map + source-verified book mirror
        ↓
textbook_task_index / V3 task kaydı
        ↓
canonical answer projection
        ↓
göreve özgü açıklama, alan bilgisi ve müdahale
        ↓
TEACHER_GUIDE_V3.md
```

Her görevde kullanılan provenance; ders kitabı, textbook map, canonical kayıt ve gerekli supporting locator'ları korur. Alan bazlı provenance, `book_prompt` için resmî textbook; cevap ve pedagojik alanlar için canonical/pedagojik türetim ayrımını gösterir.

## Görev kaydı

`teacher_guide_v3.schema.json` ortak sözleşmesi, bir ders kitabı görevini birinci sınıf kayıt olarak tanımlar. Temel öğretmen kitabı alanları şunlardır:

- `book_prompt`, `source_context`, `source_locators`
- `expected_answer`, `acceptable_answers`, `answer_explanation`
- `teacher_background`, `student_explanation`, `why_it_matters`
- `teacher_moves`, gerektiğinde `follow_up_questions`
- `common_misconceptions`, `misconception_interventions`
- `assessment_look_fors`, `support`, `enrichment`, seçici `board_notes`

Alanların tamamı her görev türü için zorunlu değildir. Motor; cevap gerektiren sorularda açıklama ve değerlendirme paketini, ürün/süreç görevlerinde ürün ölçütünü, kaynak veya QR sınırında ise görünmeyen içeriği doldurmak yerine sınırı gösterir. `answer_explanation`, cevabı tekrar etmez; cevabın metin/görsel/etkinlik kanıtıyla neden savunulabildiğini açıklar.

## Ortak motor ve profile rolü

V3 üretim önceliği şöyledir:

1. gerçek kitap görevi ve doğrulanmış kısa prompt,
2. kaynak metin/görsel/etkinlik bağlamı,
3. canonical answer ve varsa kabul ölçütleri,
4. öğretim programı bağlantıları,
5. göreve özgü alan bilgisi ve sınıf içi açıklama,
6. yalnız gerektiğinde domain router fallback'i.

Eski `opening`, `manage`, `meaning`, `analyze_apply`, `reflect` ve `assessment` phase-profile dosyaları V3'ün authoring kaynağı değildir. V3'teki deterministik domain router yalnız gerçek görevin kavram alanına uygun dil seçer; genel phase cümlesiyle görev üretmez. `text_analysis` fallback'i release raporunda sayılır ve toplam görevlerin %10'unu aşarsa kalite kapısı kapanır.

## Parity ve kalite kapıları

`validate_teacher_guide_v3.py` şunları birlikte kontrol eder:

- textbook mirror → guide → task index soru parity'si,
- 84 textbook activity'nin tamamının rehberde bulunması,
- grouped question alt sorularının ayrı ve doğru answer component ile eşleşmesi,
- prompt, answer, locator, printed→PDF offset ve provenance doğruluğu,
- `LOCATOR_ONLY`, unresolved prompt, duplicate item ve stale Markdown,
- açıklamanın cevap parafrazına indirgenmemesi,
- alan bilgisi, öğrenci açıklaması, öğretmen hamlesi ve değerlendirme kanıtı,
- uygulanabilir ve kavramsal misconception intervention,
- aynı follow-up/intervention/background/board-note paketinin tekrar kullanımı,
- deterministik Markdown renderer ve schema doğrulaması.

`release` seviyesi kaynak sınırı açıkça kaydedilmiş bounded review item'ları `PASS_WITH_REVIEW` olarak raporlar. `strict-review` aynı item'larda başarısız olur; bu, QR/video/rubrik içeriği yerel PDF'de yokken tahmin yürütülmesini engeller.

## Üretilen çıktı ve mevcut kapsam

Her tema için ortak JSON ve öğretmen kitabı biçiminde Markdown üretilir:

```text
courses/TDE_11/teacher_guide/TEMA_01/teacher_guide_v3.json
courses/TDE_11/teacher_guide/TEMA_01/TEACHER_GUIDE_V3.md
...
courses/TDE_11/teacher_guide_v3/textbook_task_index.json
```

Mevcut release kapsamı 407 textbook question, 84 textbook activity ve 576 görev kartıdır. Soru dağılımı Tema 1–4 için sırasıyla 81, 107, 114 ve 105'tir. Yerel PDF'de bulunmayan dış medya/QR veya rubrik sınırı nedeniyle 8 kayıt `REVIEW_REQUIRED` durumundadır; bunlar içerik uydurulmadan kaynak sınırıyla görünür bırakılmıştır. `LOCATOR_ONLY` ve unresolved prompt sayısı sıfırdır.

## Yerel çalıştırma

```bash
python skill/tymm-material-planner/scripts/build_teacher_guide_v3.py --repo-root .
python skill/tymm-material-planner/scripts/validate_teacher_guide_v3.py \
  --repo-root . --course TDE_11 --quality-level release \
  --report courses/TDE_11/teacher_guide_v3/validation_report.json
```

CI, tam Draft 2020-12 schema kontrolü için pinned `jsonschema` bağımlılığını kurar; local ortamda bu bağımlılık yoksa validator bunu warning olarak raporlar, parity ve deterministik içerik kapılarını yine çalıştırır.
