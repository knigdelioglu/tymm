# TDE 11 / Tema 1 — Teacher Guide V2

Bu klasörde Tema 1 öğretmen rehberi iki katmanlı tutulur.

## 1. Canonical kitap/cevap katmanı

- `teacher_guide.json`
- `sections/*.json`

Bu katman resmî ders kitabı PDF'sine, `textbook_map.json` dosyasına, programa ve doğrulanmış diğer kaynaklara dayanır. Sayfa, etkinlik, cevap, kabul ölçütü, provenance ve çıktı bağlantılarının canonical kaynağıdır.

## 2. Pedagojik V2 katmanı

- `pedagogy_v2.json` — makinece işlenebilir pedagojik katman
- `TEACHER_GUIDE_V2.md` — öğretmenin doğrudan okuyup kullanacağı sürüm

Pedagojik V2 katmanı canonical içeriği değiştirmez. Onun üzerine şu öğretmen desteğini ekler:

- kitaptaki görev/soru odağının görünürleştirilmesi,
- pedagojik amaç,
- öğretmen hamleleri,
- takip soruları,
- yanlış cevap/kavram yanılgısı müdahaleleri,
- `Tahtaya yaz:` notları,
- gözlenebilir ölçme kanıtları,
- destek ve zenginleştirme,
- kaynak sınırları.

## Kaynak otoritesi

Pedagojik V2, ders kitabının yerine geçmez. Çatışma hâlinde sıra şöyledir:

1. öğretim programı,
2. resmî ders kitabı PDF'si,
3. doğrulanmış textbook map / form indeksleri,
4. program-kitap eşleştirmesi,
5. ders planları,
6. öğretmen rehberi pedagojik zenginleştirmesi.

Kitaptaki bir soru/yönergenin birebir metni canonical kaynakta doğrulanmamışsa V2 yeni bir resmî soru metni uydurmaz. Görevi kısa biçimde özetler ve öğretmeni doğrudan ilgili kitap sayfasına yönlendirir.

## Pedagojik kalite doğrulaması

Şema:

```text
skill/tymm-material-planner/schemas/teacher_guide_pedagogy_overlay.schema.json
```

Validator:

```bash
python skill/tymm-material-planner/scripts/validate_teacher_guide_pedagogy_overlay.py \
  --repo-root . \
  --overlay courses/TDE_11/teacher_guide/TEMA_01/pedagogy_v2.json \
  --manifest courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json
```

Validator yalnız JSON biçimini kontrol etmez. Ayrıca:

- bütün canonical guide item'larının V2 tarafından kapsanmasını,
- dangling item/section referansı olmamasını,
- item'ın yanlış section veya sayfa bloğuna bağlanmamasını,
- her blokta öğretmen hamlesi bulunmasını,
- her blokta ölçme kanıtı bulunmasını,
- destek ve zenginleştirme alanlarının boş olmamasını,
- tahta notlarının açıkça `Tahtaya yaz:` etiketi taşımasını

kontrol eder.

## Bilinen kaynak sınırları

- Konuşma ve yazma bölümlerindeki bazı dış QR rubriklerinin tam ölçüt × düzey matrisi yerel PDF'de görünür değildir; rehber görünmeyen içeriği uydurmaz.
- Dinleme/izleme s.65-71 alt sorularının birebir soru metinleri mevcut canonical guide'da ayrı item'lar hâlinde doğrulanmış değildir; ilgili sorular ders kitabından izlenir.
- Tema sonundaki `Olvido` sorusu dış EBA çok modlu içeriğine bağlıdır; medya ayrıntıları gerçek oynatım üzerinden gözlenmelidir.

## V2 kalite ilkesi

Her ek içerik şu soruyu geçmelidir:

> Bu bilgi öğretmenin sınıfta ne yapacağını veya öğrencinin cevabını nasıl değerlendireceğini değiştiriyor mu?

Cevap hayırsa öğretmen rehberine eklenmemelidir.
