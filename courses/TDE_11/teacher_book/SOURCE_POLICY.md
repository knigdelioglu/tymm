# TDE 11 Teacher Book — Source Policy

## Otorite sırası

1. **Resmî öğretim programı** — öğrenme çıktıları ve normatif gereklilikler.
2. **Resmî ders kitabı PDF'si** — soru, yönerge, metin bağlamı, sayfa ve öğrenci görevi.
3. **textbook_map / textbook_question_inventory** — resmî kitaptan türetilmiş doğrulanmış indeksler.
4. **teacher_book/source** — yukarıdaki kaynaklardan taşınmış nötr locator/prompt katmanı.
5. **teacher_book/source/*/answer_bank.json** — yalnız legacy teacher-guide bağı olmayan cevap desteği.

## Yasak authoring kaynakları

Aktif öğretmen kitabı üretimi şu legacy artefaktları kullanamaz:

- V2 / V2.2 pedagogy overlay veya çıktıları,
- V2.3 book mirror / golden-reference / pilot çıktıları,
- V3 teacher-guide JSON, Markdown, task-index veya Kindle çıktıları,
- geçmiş sürümlerin builder, validator, profil veya schema sözleşmeleri.

Bu artefaktlar Git geçmişinden gerektiğinde incelenebilir; aktif working tree'de authoring kaynağı olarak tutulmaz.

## Cevap bankası kuralı

Yeni cevap bankasına yalnız provenance'ı `legacy_teacher_guide` içermeyen ve `PEDAGOGICAL_ENRICHMENT` sınıfında olmayan cevaplar taşınır.

Cevap bankası:
- üslup şablonu değildir,
- pedagojik paragraf üretmek için kullanılmaz,
- yalnız doğruluk/kapsam kontrolü ve gerekli olduğunda kısa cevap desteği sağlar.

## İçerik yoğunluğu kuralı

Yeni öğretmen kitabında alan doldurmak başlı başına amaç değildir.

- Cevap, soruyu doğrudan karşılar.
- Açıklama, cevaba yeni bilgi ekliyorsa yazılır.
- Sınıf içi hamleler göreve özgü ve en fazla üçtür.
- Yanılgı/dikkat notu gerçek bir risk varsa eklenir.
- Öğretmen notu, öğretmenin bilmesi gereken ek alan bilgisini sağlıyorsa eklenir.
- Aynı fikir farklı başlıklar altında yeniden yazılmaz.
