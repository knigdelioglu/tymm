# Input resolution, knowledge base, and source caching

## İçindekiler

- Input authority ve manifest
- Kalıcı Bilgi Tabanı ve Önbellek Protokolü (Cache Lifecycle)
- Kaynak Kimliği ve Parmak İzi (Fingerprint)
- Curriculum Resolver ve Verbatim Saklama
- Textbook Resolver ve Yapısal İndeksleme
- Tema Dilimleme (Slicing) ve Bütün PDF'yi Yeniden Taramama
- Çelişki Yönetimi, Sessiz Üzerine Yazmama ve Fail-Closed
- Locator standardı

## Input authority

Kaynak önceliği:

1. Kullanıcının sağladığı resmî öğretim programı: normatif/birincil kaynak.
2. Kullanıcının sağladığı resmî ders kitabı: uygulama ve içerik kaynağı.
3. Kullanıcının sağladığı diğer resmî MEB belgeleri.
4. MEB/TYMM resmî web doğrulaması.
5. Haricî güvenilir kaynaklar.

Kullanıcının sağladığı program veya kitap, web sonucuyla sessizce değiştirilemez. Web yalnız eksik dosya, belirsiz kimlik/sürüm, güncellik şüphesi veya çelişki olduğunda kullanılır.

## Kalıcı Bilgi Tabanı ve Önbellek Protokolü (Cache Lifecycle)

Projede her ders ve sınıf düzeyi için standart `knowledge/<COURSE_GRADE>/` dizini (örnek: `knowledge/TDE_9/`) kullanılır.

1. **Birincil Çalışma Cache'i**: Doğrulanmış haritalar (`curriculum_map.json`, `textbook_map.json`, `textbook_forms_index.json`), tema analizi ve materyal üretiminden önce birincil çalışma önbelleğidir.
2. **Kalıcı Kaynak Çözümlemesi**: `curriculum_map` ve `textbook_map` kaynak verisinin kalıcı, yapılandırılmış çözümlemesidir. Tema hizalamaları ve ihtiyaç analizleri bu haritalardan türetilir.
3. **Tekrar Çözümlememe İlkesi**: Aynı resmî öğretim programı ve ders kitabı her tema analizinde sıfırdan taranmaz.

## Kaynak Kimliği ve Parmak İzi (Fingerprint)

Her girdi için `source_manifest.json` dosyasında şu alanlar tutulur:

- `source_id`
- `input_type`: `official_curriculum`, `official_textbook`, `official_meb_document`, `user_request`
- dosya yolu ve dosya adı
- `sha256` hash değeri ve `size_bytes`
- başlık, ders, sınıf, kademe, okul türü
- program yılı veya kitap baskı/sürümü
- authority rank
- identity status, conflict status, verification status
- son doğrulama zamanı (`last_validated`)

### Önbellek Doğrulama Algoritması:
- Sağlanan dosyanın `sha256` değeri `source_manifest.json` içindeki kayıtla eşleşiyorsa ve haritalar `VERIFIED` ise → **CACHE HIT**: Ham PDF taramasını atla, doğrulanmış harita kayıtlarını yükle.
- Dosya yeni eklenmişse veya hash değişmişse → **CACHE MISS**: Dosyayı çözümle, doğrula ve haritaları güncelle.

## Curriculum Resolver ve Verbatim Saklama

1. Kullanıcının program dosyasını bul, hash'ini çıkar ve manifest kaydıyla karşılaştır.
2. Program adı, ders, sınıf, okul türü, program yılı/sürümü ve ünite/tema bilgilerini dosyadan al.
3. **Resmî İfadeleri Verbatim Saklama**: Öğrenme çıktıları, kodlar, süreç bileşenleri, alan becerileri ve ilişkili program bileşenleri kesinlikle kısaltılmadan, yorumlanmadan ve değiştirilmeden **birebir (verbatim: true)** çıkarılır ve `curriculum_map.json` içine kaydedilir.
4. Her öğeyi dosya sayfası, bölüm, başlık, kod veya ünite locator'ıyla ilişkilendir.
5. Kimlik/sürüm/güncellik belirsizse MEB/TYMM resmî kaynağıyla doğrula.
6. Web kaynağı dosyadan farklıysa 'CONFLICTED' oluştur; dosyayı veya haritayı değiştirme.

Durumlar:
- `VERIFIED`: kimlik ve hedef bağlam yeterli biçimde doğrulandı.
- `AMBIGUOUS`: birden çok aday veya çözülemeyen kimlik var.
- `NOT_FOUND`: gerekli program verisi bulunamadı.
- `CONFLICTED`: program ile kitap veya resmî doğrulama arasında çelişki var.

## Textbook Resolver ve Yapısal İndeksleme

Ders kitabını genel `source_card` olarak değil, yapılandırılmış `textbook_map.json` ve `textbook_forms_index.json` olarak kalıcılaştır:

- kitap adı, ders, sınıf, okul türü, yayınevi, baskı/sürüm
- ünite/tema, sayfa aralıkları ve bölüm başlıkları
- metinler, türler, yazarlar, eserler, kavramlar, görseller ve medyalar
- mevcut etkinlikler, sorular, yönergeler ve öğrenciden beklenen ürünler
- mevcut ölçme-değerlendirme araçları (7 yapısal türe göre `textbook_forms_index.json` içinde ayrı indekslenir)
- destek, zenginleştirme, güvenlik ve erişilebilirlik unsurları
- programla açık bağlantılar ve telif/kullanım modu

Taranmış kitapta OCR kullanılırsa OCR belirsizliğini ve insan kontrolü gereğini kaydet. Sayfa numarasını mümkün olduğunca ünite adı ve bölüm başlığıyla birlikte tut.

## Tema Dilimleme (Slicing) ve Bütün PDF'yi Yeniden Taramama

Bir tema analizi yaparken (örneğin "9. sınıf TDE 2. tema için kaynak hazırla"):
1. Bütün PDF (ör. 45MB ders kitabı) tekrar taranmaz veya yeniden modellenmez.
2. `curriculum_map.json`, `textbook_map.json` ve `textbook_forms_index.json` içinden yalnızca hedef temanın (`theme_no`) kayıtları dilimlenir (`themes/tema_XX/`).
3. Tema alignment'ı ve ihtiyaç analizi bu dilimler üzerinden gerçekleştirilir.

## Çelişki Yönetimi, Sessiz Üzerine Yazmama ve Fail-Closed

1. **Sessizce Üzerine Yazmama**: Map'teki doğrulanmış bilgi ile yeni bir PDF okuması veya kullanıcı girdisi çelişirse, haritanın üzerine sessizce yazılmaz; `validation_report.md` içinde `REVIEW` kaydı oluşturulur.
2. **Uyuşmazlık Durumu**: Program ile kitap arasında sınıf, program yılı, ünite/tema yapısı veya baskı/sürüm uyuşmazlığı varsa `PROGRAM_TEXTBOOK_VERSION_MISMATCH` oluşturulur. Alignment Contract durumu `CONFLICTED` yapılır, öğretmen doğrulaması olmadan son materyal üretilmez.
3. Program çözümleme `VERIFIED` değilse resmî kod, öğrenme çıktısı, süreç bileşeni, değer, SEL, okuryazarlık, ders saati veya sürüm tahmin edilmez.

## Locator standardı

Bir çıkarım mümkün olduğunca şu biçimde kaydedilir:

input_id → program/book → unit/theme → section/activity → page → figure/table/code

Locator olmadan program-kitap eşleştirmesi kesin kabul edilmez.

