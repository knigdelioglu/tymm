# Input resolution, knowledge base, and source caching

## İçindekiler

- Input authority ve manifest
- Desteklenen kaynak biçimleri
- Kalıcı Bilgi Tabanı ve Önbellek Protokolü (Cache Lifecycle)
- Kaynak Kimliği ve Parmak İzi (Fingerprint)
- Curriculum Resolver ve Verbatim Saklama
- Textbook Resolver ve Yapısal İndeksleme
- Tema Dilimleme (Slicing) ve Bütün kaynağı yeniden taramama
- Çelişki Yönetimi, Sessiz Üzerine Yazmama ve Fail-Closed
- Locator standardı

## Input authority

Kaynak önceliği:

1. Kullanıcının sağladığı resmî öğretim programı: normatif/birincil kaynak.
2. Kullanıcının sağladığı resmî ders kitabı: uygulama ve içerik kaynağı.
3. Kullanıcının sağladığı diğer resmî MEB belgeleri.
4. MEB/TYMM resmî web doğrulaması.
5. Haricî güvenilir kaynaklar.

"Kullanıcının sağladığı kaynak" yalnız tek bir yerel PDF anlamına gelmez. Kullanıcı açıkça resmî bir MEB/TYMM URL'si verdiğinde bu URL de supplied source locator kabul edilir. Kullanıcının sağladığı program veya kitap başka bir web sonucu ya da üçüncü taraf dosyayla sessizce değiştirilemez.

## Desteklenen kaynak biçimleri

Resolver aşağıdaki source input biçimlerini desteklemelidir:

1. **SINGLE_FILE** — tek PDF/dosya.
2. **MULTI_PART_SOURCE_BUNDLE** — aynı resmî kaynağın tema/ünite/bölüm bazında birden çok dosyaya ayrılmış seti.
3. **OFFICIAL_REMOTE_WEB** — kullanıcı tarafından açıkça verilen veya eksik dosya nedeniyle doğrulanan resmî MEB/TYMM web sayfası.
4. **OFFICIAL_REMOTE_ASSET** — resmî web sayfasının doğrudan açığa çıkardığı PDF/dijital kitap varlığı.

### Multi-part source bundle kuralı

Bir program tema bazında ayrı PDF'ler hâlinde verilmişse tek bir birleşik PDF beklenmez. `source_manifest.json` içinde:

- ortak `source_group_id`
- beklenen parça sayısı
- her parça için ayrı `source_id`
- tema/ünite kimliği
- dosya yolu
- fingerprint/provenance
- completeness ve verification status

tutulur.

Bundle ancak beklenen bütün parçalar mevcut ve her parçanın iç kimliği hedef sınıf/tema ile doğrulanmışsa `VERIFIED` kabul edilir. Bir parça eksik, yanlış sınıfa ait veya çelişkiliyse programın tamamı fail-closed kalır.

### Official remote source kuralı

Kullanıcı resmî ders kitabının TYMM/MEB URL'sini doğrudan verdiyse bu URL primary textbook locator olabilir. Bu durumda büyük binary kitabın GitHub'a kopyalanması zorunlu değildir.

- Exact supplied URL manifestte saklanır.
- Sayfanın açığa çıkardığı resmî indirme/okuma bağlantıları izlenebilir.
- Arama motoru sonucu, başka yayınevi, üçüncü taraf PDF veya farklı baskı sessizce primary source yerine geçirilemez.
- Kaynak erişilemiyorsa `REMOTE_SOURCE_UNAVAILABLE` / course-specific eşdeğer review durumu oluşturulur ve doğrulanmamış textbook map üretilmez.
- Erişim tarihi, kimlik/sürüm bilgisi ve mümkünse remote content fingerprint kaydedilir.

## Kalıcı Bilgi Tabanı ve Önbellek Protokolü (Cache Lifecycle)

Projede her ders ve sınıf düzeyi için standart `courses/<COURSE_GRADE>/` dizini (örnek: `courses/TDE_9/`, `courses/TDE_10/`) kullanılır.

1. **Birincil Çalışma Cache'i**: Doğrulanmış haritalar (`curriculum_map.json`, `textbook_map.json`, `textbook_forms_index.json`), tema analizi ve materyal üretiminden önce birincil çalışma önbelleğidir.
2. **Kalıcı Kaynak Çözümlemesi**: `curriculum_map` ve `textbook_map` kaynak verisinin kalıcı, yapılandırılmış çözümlemesidir. Tema hizalamaları ve ihtiyaç analizleri bu haritalardan türetilir.
3. **Tekrar Çözümlememe İlkesi**: Aynı resmî öğretim programı ve ders kitabı her tema analizinde sıfırdan taranmaz.
4. **Source form independence**: Canonical map yapısı kaynak taşıma biçiminden bağımsızdır; kaynak tek PDF, dört tema PDF'i veya resmî remote textbook olabilir.

## Kaynak Kimliği ve Parmak İzi (Fingerprint)

Her girdi için `source_manifest.json` dosyasında uygun olan alanlar tutulur:

- `source_id`
- `source_group_id` (multi-part bundle ise)
- `source_type`: `official_curriculum`, `official_textbook`, `official_meb_document`, `user_request`
- `input_locator_type`: file / bundle_part / official_remote_web / official_remote_asset
- dosya yolu ve dosya adı veya exact URL
- local dosya için `sha256` ve `size_bytes`
- remote kaynak için erişim zamanı, resolved official URL ve mümkünse content fingerprint
- başlık, ders, sınıf, kademe, okul türü
- program yılı veya kitap baskı/sürümü (yalnız kaynaktan doğrulanabiliyorsa)
- tema/ünite kimliği (parçalı kaynakta)
- authority rank
- identity status, conflict status, verification status
- son doğrulama zamanı (`last_validated`)

Git blob SHA gibi repository taşıma kimlikleri ayrıca kaydedilebilir ancak bunlar SHA-256 source fingerprint yerine geçirilmez.

### Önbellek Doğrulama Algoritması

**Local file:**
- Sağlanan dosyanın `sha256` değeri manifest kaydıyla eşleşiyor ve haritalar `VERIFIED` ise → **CACHE HIT**.
- Dosya yeni veya hash değişmişse → **CACHE MISS**; çözümle ve doğrula.

**Multi-part bundle:**
- Önce bundle completeness kontrol edilir.
- Her parçanın fingerprint'i ayrı doğrulanır.
- Yalnız değişen/yeni parçalar yeniden çözümlemeye alınabilir; ancak sonuçta bütün bundle identity consistency gate'i tekrar çalışır.

**Remote official source:**
- Exact manifest URL ve resolved official asset identity kontrol edilir.
- Daha önce doğrulanmış content fingerprint/metadata aynıysa map yeniden kullanılabilir.
- Remote identity veya sürüm değişmişse stale/review oluşturulur; sessiz overwrite yapılmaz.

## Curriculum Resolver ve Verbatim Saklama

1. Curriculum source tanımını `source_manifest.json` üzerinden çöz: tek dosya veya multi-part bundle olabilir.
2. Her local parçanın fingerprint'ini çıkar ve manifest kaydıyla karşılaştır.
3. Program adı, ders, sınıf, okul türü, program yılı/sürümü ve ünite/tema bilgilerini kaynağın kendisinden al.
4. Multi-part bundle kullanılıyorsa her parçanın iç tema/sınıf kimliğini manifestteki beklenen kimlikle çapraz doğrula.
5. **Resmî İfadeleri Verbatim Saklama**: Öğrenme çıktıları, kodlar, süreç bileşenleri, alan becerileri ve ilişkili program bileşenleri kesinlikle kısaltılmadan, yorumlanmadan ve değiştirilmeden **birebir (verbatim: true)** çıkarılır ve `curriculum_map.json` içine kaydedilir.
6. Her öğeyi source_id + tema/ünite + dosya sayfası/bölüm/başlık/kod locator'ıyla ilişkilendir.
7. Kimlik/sürüm/güncellik belirsizse MEB/TYMM resmî kaynağıyla doğrula.
8. Web doğrulaması supplied program source ile farklıysa `CONFLICTED` oluştur; dosyayı veya haritayı sessizce değiştirme.

Durumlar:
- `VERIFIED`: kimlik ve hedef bağlam yeterli biçimde doğrulandı.
- `AMBIGUOUS`: birden çok aday veya çözülemeyen kimlik var.
- `NOT_FOUND`: gerekli program verisi bulunamadı.
- `CONFLICTED`: supplied source ile resmî doğrulama veya diğer source parçaları arasında çelişki var.
- `INCOMPLETE_SOURCE_BUNDLE`: beklenen curriculum parçalarından biri veya daha fazlası eksik.

## Textbook Resolver ve Yapısal İndeksleme

Textbook input tek dosya olmak zorunda değildir. Kullanıcının verdiği exact resmî MEB/TYMM textbook URL'si `OFFICIAL_REMOTE_WEB` olarak primary input olabilir.

Resolver sırası:

1. `source_manifest.json` içindeki primary textbook locator'ını çöz.
2. Local/versioned textbook varsa fingerprint doğrula.
3. Remote official textbook ise exact supplied page'i kullan; sayfanın açığa çıkardığı resmî viewer/download asset'lerini takip et.
4. Exact remote source erişilemiyorsa üçüncü taraf kopyaya sessizce geçme; review/fail-closed oluştur.
5. Kaynağı genel `source_card` olarak bırakma; doğrulandıktan sonra yapılandırılmış `textbook_map.json` ve `textbook_forms_index.json` olarak kalıcılaştır.

Kalıcı textbook modelinde:

- kitap adı, ders, sınıf, okul türü, yayınevi, baskı/sürüm
- ünite/tema, sayfa aralıkları ve bölüm başlıkları
- metinler, türler, yazarlar, eserler, kavramlar, görseller ve medyalar
- mevcut etkinlikler, sorular, yönergeler ve öğrenciden beklenen ürünler
- mevcut ölçme-değerlendirme araçları (7 yapısal türe göre `textbook_forms_index.json` içinde ayrı indekslenir)
- destek, zenginleştirme, güvenlik ve erişilebilirlik unsurları
- programla açık bağlantılar ve telif/kullanım modu
- source_id, URL/dosya locator ve sayfa/bölüm provenance

tutulur.

Taranmış kitapta OCR kullanılırsa OCR belirsizliğini ve insan kontrolü gereğini kaydet. Sayfa numarasını mümkün olduğunca ünite adı ve bölüm başlığıyla birlikte tut.

## Tema Dilimleme (Slicing) ve bütün kaynağı yeniden taramama

Bir tema analizi yaparken:

1. Doğrulanmış `curriculum_map.json`, `textbook_map.json` ve `textbook_forms_index.json` varsa ham kaynakların tamamı yeniden çözülmez.
2. Yalnız hedef temanın kayıtları `themes/tema_XX/` için dilimlenir.
3. Curriculum source zaten tema bazında ayrı PDF ise ilgili PDF yalnız kaynak provenance/verification gerektiğinde kullanılır; her tema isteğinde diğer üç PDF tekrar okunmaz.
4. Remote textbook için de doğrulanmış map mevcutsa büyük dijital kitap her sorguda tekrar fetch edilmez.
5. Tema alignment'ı ve ihtiyaç analizi canonical dilimler üzerinden gerçekleştirilir.

## Çelişki Yönetimi, Sessiz Üzerine Yazmama ve Fail-Closed

1. **Sessizce Üzerine Yazmama**: Map'teki doğrulanmış bilgi ile yeni source okuması veya kullanıcı girdisi çelişirse, haritanın üzerine sessizce yazılmaz; `validation_report.md` içinde `REVIEW` kaydı oluşturulur.
2. **Uyuşmazlık Durumu**: Program ile kitap arasında sınıf, program yılı, ünite/tema yapısı veya baskı/sürüm uyuşmazlığı varsa `PROGRAM_TEXTBOOK_VERSION_MISMATCH` oluşturulur. Alignment Contract durumu `CONFLICTED` yapılır, öğretmen doğrulaması olmadan son materyal üretilmez.
3. **Bundle uyuşmazlığı**: Curriculum bundle parçalarının iç sınıf/tema kimliği beklenen manifest sırasıyla uyuşmazsa `CURRICULUM_SOURCE_BUNDLE_MISMATCH` oluşturulur.
4. **Remote kaynak erişimi**: Kullanıcı tarafından supplied official URL erişilemiyorsa doğrulanmamış alternatif source ile devam edilmez.
5. Program çözümleme `VERIFIED` değilse resmî kod, öğrenme çıktısı, süreç bileşeni, değer, SEL, okuryazarlık, ders saati veya sürüm tahmin edilmez.

## Locator standardı

Bir çıkarım mümkün olduğunca şu biçimde kaydedilir:

`source_id → program/book → unit/theme → section/activity → page/remote-section → figure/table/code`

Remote source için exact URL de locator'ın parçasıdır. Multi-part curriculum için source_id, parçanın tema kimliğini ayırt edecek şekilde zorunludur.

Locator olmadan program-kitap eşleştirmesi kesin kabul edilmez.
