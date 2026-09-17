# TDE 11 Teacher Guide V3 — Kindle çıktı katmanı

Bu klasör, `courses/TDE_11/teacher_guide/TEMA_01..04/teacher_guide_v3.json` dosyalarını **tek doğruluk kaynağı** kabul ederek Kindle/e-ink için yeniden düzenlenebilir (reflowable) EPUB 3 üretir.

Amaç yeni öğretmen rehberi verisi üretmek değildir. V3'teki soru, cevap ve pedagojik alanları sınıfta hızlı başvuru yapılabilecek bir okuma düzenine projekte etmektir.

## Okuma düzeni

Her görev kartı önce hızlı kullanım alanlarını gösterir:

1. **Soru / görev**
2. **Kısa cevap**
3. **Sınıfta nasıl açıklarım?**
4. **Öğretmen hamlesi**

Ardından ayrıntılı katman gelir:

- Açıklama ve gerekçe
- Öğretmenin bilmesi gerekenler
- Bu görev neden burada?
- Takip soruları
- Sık yanılgılar ve müdahale
- Cevapta ne arayacağım?
- Destek / zenginleştirme
- Tahta notu
- Kaynak / durum

Başlıklar ders kitabının basılı sayfa numarasını korur. Örnek:

```text
s. 87 · Metin Tahlili · Soru 2
```

EPUB içindekiler tablosu `Tema → kitap bölümü` hiyerarşisindedir; yüzlerce görev Kindle menüsünü doldurmaz. Görevlerin tamamı kitap içinde aranabilir.

## Üretim

Repo kökünden:

```bash
python skill/tymm-material-planner/scripts/build_teacher_guide_kindle.py --repo-root .
```

Çıktılar:

```text
courses/TDE_11/teacher_guide_kindle/output/
├── TDE_11_OGRETMEN_REHBERI_V3.epub
├── TDE_11_TEMA_01_OGRETMEN_REHBERI_V3.epub
├── TDE_11_TEMA_02_OGRETMEN_REHBERI_V3.epub
├── TDE_11_TEMA_03_OGRETMEN_REHBERI_V3.epub
└── TDE_11_TEMA_04_OGRETMEN_REHBERI_V3.epub
```

Üretici yalnız Python standart kütüphanesini kullanır; Calibre/Pandoc bağımlılığı yoktur.

## Doğrulama

```bash
python skill/tymm-material-planner/scripts/validate_teacher_guide_kindle.py --repo-root .
```

Validator şunları kontrol eder:

- EPUB `mimetype` dosyasının ilk ve sıkıştırılmamış olması,
- `container.xml`, OPF, nav ve XHTML yapılarının okunabilmesi,
- OPF manifest/spine hedeflerinin bulunması,
- V3 canonical görevlerinin EPUB içinde **eksiksiz, fazlasız ve tekrarsız** bulunması,
- birleşik kitap ile tema kitaplarının kendi doğru görev kapsamını taşıması.

## Yapılandırma

`kindle_profile.json` başlıkları, tema listesini, hızlı/ayrıntılı alan etiketlerini ve çıktı davranışını tutar. V3 canonical JSON veya V3 Markdown dosyaları bu katman tarafından değiştirilmez.

## Kindle'a gönderme

Üretilen `.epub` dosyası Send to Kindle ile kişisel Kindle kütüphanesine eklenebilir. Bu klasördeki EPUB, sabit sayfalı PDF değildir; Kindle yazı boyutu ve ekran genişliğine göre yeniden akar.
