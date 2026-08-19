# TDE_11 Source Documents

Bu klasör, 11. sınıf Türk Dili ve Edebiyatı için resmî öğretim programı kaynaklarının yükleme alanıdır.

## Buraya ne eklenecek?

Yalnız 11. sınıf Türk Dili ve Edebiyatı dersine ait resmî öğretim programı PDF dosyaları.

Program tek PDF ise o dosyayı; tema/ünite bazında birden fazla PDF olarak yayımlanmışsa bütün parçaları bu klasöre ekleyin.

## Bu aşamada ne eklenmeyecek?

- Ders kitabı türevi veriler
- `curriculum_map.json`
- `source_manifest.json`
- textbook map/index dosyaları
- coverage veya gap çıktıları
- production artifactları
- başka sınıflardan kopyalanmış içerik

Bunlar kaynaklar yüklendikten ve `docs/yalniz-ogretim-programi-bootstrap-promptu.md` çalıştırıldıktan sonra, yalnız doğrulanmış 11. sınıf kaynaklarından türetilecektir.

## Kaynak bütünlüğü

Birden fazla program PDF'i varsa bütün parçalar birlikte tek curriculum source bundle olarak ele alınacaktır. Eksik parça varsa bootstrap sırasında kaynak `SOURCE_INCOMPLETE / REVIEW_REQUIRED` durumunda bırakılmalıdır; eksik içerik başka sınıftan tahmin edilmemelidir.
