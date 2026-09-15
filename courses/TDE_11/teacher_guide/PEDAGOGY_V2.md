# TDE 11 Teacher Guide V2 — Pedagoji Katmanı

Bu dizindeki mevcut `teacher_guide.json` ve `sections/*.json` dosyaları ders kitabı sayfası, görev, cevap, kaynak/provenance ve öğrenme çıktısı ilişkilerinin canonical katmanıdır.

Teacher Guide V2 bu katmanı silmez veya yeniden yorumlayarak kaynak gerçeğinin yerine geçmez. V2, öğretmenin sınıf içinde ihtiyaç duyduğu pedagojik uygulama katmanını ekler:

- kitaptaki görevlerin görünür listesi,
- pedagojik amaç,
- uygulanabilir öğretmen hamleleri,
- derinleştirici takip soruları,
- yanlış/kısmi cevapta müdahale,
- gerektiğinde `Tahtaya yaz:` notları,
- ölçmede bakılacak gözlenebilir kanıtlar,
- destek ve zenginleştirme,
- dış QR/video/rubrik gibi kaynak sınırları.

## Kaynak politikası

1. Resmî ders kitabı PDF'si kitap sorusu, yönergesi ve sayfa akışında birincil kaynaktır.
2. Canonical section JSON'ları V2'nin item ve sayfa referansını sağlar.
3. Canonical kaynak birebir soru metnini taşımıyorsa V2 soru metni uydurmaz; görev etiketi, soru numarası ve sayfa konumu kullanılır.
4. Dış video veya QR içeriğinde gözlenmeyen ayrıntılar cevap anahtarına eklenmez.
5. Açık uçlu sorularda tek kalıp cevap yerine ölçüt, kanıt ve gerekçeye dayalı alternatifler kabul edilir.

## Üretim

Tema 1, referans kalite örneği olarak izlenen `pedagogy_v2.json` ve `TEACHER_GUIDE_V2.md` dosyalarına sahiptir.

Tema 2–4 pedagojik katmanları canonical section dosyalarından deterministik olarak üretilebilir:

```bash
python skill/tymm-material-planner/scripts/build_teacher_guide_pedagogy_v2.py --repo-root .
```

Üretici şu dosyaları oluşturur:

```text
courses/TDE_11/teacher_guide/TEMA_02/pedagogy_v2.json
courses/TDE_11/teacher_guide/TEMA_02/TEACHER_GUIDE_V2.md
courses/TDE_11/teacher_guide/TEMA_03/pedagogy_v2.json
courses/TDE_11/teacher_guide/TEMA_03/TEACHER_GUIDE_V2.md
courses/TDE_11/teacher_guide/TEMA_04/pedagogy_v2.json
courses/TDE_11/teacher_guide/TEMA_04/TEACHER_GUIDE_V2.md
```

Pedagojik içerik profilleri:

```text
skill/tymm-material-planner/data/teacher_guide_v2_profiles.json
```

## Kalite kapısı

`validate_teacher_guide_pedagogy_overlay.py` aşağıdakileri doğrular:

- canonical guide itemlerinin tamamı V2 tarafından kapsanır,
- her canonical item tam bir kez kapsanır,
- section ve sayfa referansları geçerlidir,
- öğretmen hamlesi boş değildir,
- ölçme kanıtı/`assessment_look_fors` boş değildir,
- destek ve zenginleştirme boş değildir,
- bütün tahta notları `Tahtaya yaz:` biçimindedir.

TDE11 P0 CI, Tema 2–4'ü yeniden üretir ve Tema 1–4 V2 pedagojik katmanlarını bu kapıdan geçirir.

## Pedagojik ilke

Amaç daha uzun bir öğretmen kitabı üretmek değil, öğretmenin ders sırasında karar vermesini kolaylaştırmaktır. Her V2 blok şu sorulara cevap vermelidir:

> Kitap burada öğrenciden ne istiyor? Öğretmen ne yapmalı? Öğrencinin düşünmesini hangi soruyla derinleştirmeli? Yanlış cevapta cevabı vermeden nasıl yönlendirmeli? Tahtaya ne yazmak gerçekten yararlı? Öğrenmenin gerçekleştiğini hangi kanıttan anlayacak?
