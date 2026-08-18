# TDE_10 Source Documents

Bu klasör, GitHub üzerinden çalışan agent'ların doğrudan erişmesi gereken 10. sınıf resmî öğretim programı kaynaklarını içerir.

## Öğretim programı kaynak modeli

10. sınıf Türk Dili ve Edebiyatı öğretim programı tek PDF olarak değil, tema bazında dört ayrı resmî PDF olarak sağlanmıştır:

1. `Türk Dili Ve Edebiyatı Dersi 10.Sınıf 1.PDF` → `TEMA_01` — beklenen resmî tema adı: `SÖZÜN EZGİSİ`
2. `Türk Dili Ve Edebiyatı Dersi 10.Sınıf 2.PDF` → `TEMA_02` — beklenen resmî tema adı: `KELİMELERİN RİTMİ`
3. `Türk Dili Ve Edebiyatı Dersi 10.Sınıf 3.PDF` → `TEMA_03` — beklenen resmî tema adı: `DÜNDEN BUGÜNE`
4. `Türk Dili Ve Edebiyatı Dersi 10.Sınıf 4.PDF` → `TEMA_04` — beklenen resmî tema adı: `NESİLLERİN MİRASI`

Bu dört dosya birlikte tek bir `official_curriculum` source bundle oluşturur. Her dosyanın kimliği ve iç başlığı ayrı doğrulanır; bundle eksikse curriculum çözümlemesi `VERIFIED` sayılmaz.

## Ders kitabı kaynak modeli

123 MB ders kitabı GitHub'a yüklenmez. Birincil kitap kaynağı kullanıcı tarafından verilen resmî TYMM/MEB sayfasıdır:

`https://tymm.meb.gov.tr/kitap/78/turk-dili-ve-edebiyati-10.sinif-ders-kitabi`

Agent bu URL'yi `official_textbook` kaynağı olarak kullanır. Sayfa bir resmî indirme/okuma varlığına yönlendiriyorsa yalnız bu sayfadan türetilen resmî bağlantılar izlenebilir. Kaynak erişilemezse başka baskı veya üçüncü taraf PDF sessizce ikame edilmez; `TEXTBOOK_REMOTE_SOURCE_UNAVAILABLE` / review durumu oluşturulur.

## Provenance

Bu dosyalar ve URL canonical knowledge değildir. `curriculum_map.json`, `textbook_map.json` ve `textbook_forms_index.json` yalnız kaynaklar doğrulanıp yapılandırılmış biçimde çıkarıldıktan sonra canonical çalışma verisi olur.

Repo public olduğu için yalnız dağıtma yetkisi bulunan dosyalar GitHub'da tutulmalıdır; büyük ders kitabı bu nedenle de repoya kopyalanmaz.
