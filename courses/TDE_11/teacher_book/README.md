# TDE 11 Öğretmen Kitabı

Bu dizin, 11. sınıf Türk Dili ve Edebiyatı için yeni öğretmen kitabının tek aktif authoring alanıdır.

## Temel ilke

Öğretmen kitabı geçmiş sürümlerin devamı olarak üretilmez. Aktif üretim yalnız şu kaynak katmanlarına dayanır:

1. resmî 11. sınıf ders kitabı PDF'si,
2. resmî öğretim programı ve curriculum map,
3. `textbook_map.json`,
4. `textbook_question_inventory.json`,
5. bu dizindeki nötr `source_index.json` dosyaları,
6. yalnız legacy bağı olmayan cevapları içeren `answer_bank.json` dosyaları.

Eski teacher-guide sürümleri, mirror/pedagogy çıktıları ve bunların ürettiği Markdown/EPUB dosyaları authoring kaynağı değildir.

## Yeni ürün sözleşmesi

Yeni öğretmen kitabı için hedef şema:

`skill/tymm-material-planner/schemas/teacher_book.schema.json`

Bir soru/görev kartında esas sıra şudur:

- kitaptaki soru/görev,
- kısa ve açık cevap,
- yalnız gerekiyorsa açıklama,
- en fazla üç somut sınıf içi hamle,
- yalnız gerçekten gerekiyorsa dikkat/yanılgı notu,
- yalnız ek bilgi sağlıyorsa öğretmen notu.

Bir alan önceki alanın söylediklerini tekrar ediyorsa üretilmez.

## Kaynak katmanı

Tema bazlı dosyalar:

`courses/TDE_11/teacher_book/source/TEMA_01..04/`

Her temada:

- `source_index.json`: ders kitabına dönük başlık, sayfa, soru/görev ve locator kayıtları,
- `answer_bank.json`: legacy teacher-guide kaynağına dayanmayan temiz cevap kayıtları.

Bu kaynaklar öğretmen kitabının üslubunu belirlemez; yalnız içerik doğrulama ve kaynak bağlama için kullanılır.
