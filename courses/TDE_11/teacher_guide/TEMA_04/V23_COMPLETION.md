# Tema 4 Teacher Guide V2.3 — Tam Kapsam Checkpointi

## Kapsam

- Basılı sayfa: **236–307**
- Book-first mirror fragmentı: **7**
- Hedef birleşik entry: **143**
- Hedef QUESTION: **105**
- Tanınabilir QUESTION hedefi: **105/105**
- `LOCATOR_ONLY` hedefi: **0**
- Source-verified component hedefi: **65/65**

## Fragmentlar

| Aralık | İçerik | Entry | QUESTION | Durum |
|---|---|---:|---:|---|
| 236–239 | Tema açılışı | 7 | 5 | PILOT |
| 240–262 | Ben, Mimar Sinan / tiyatro | 32 | 22 | REFERENCE_QUALITY |
| 263–279 | Merdiven / küçürek hikâye | 34 | 22 | REFERENCE_QUALITY |
| 280–283 | Konuşma / canlandırma | 10 | 7 | REVIEW_REQUIRED |
| 284–297 | Dinleme-izleme / Fedakârlık | 33 | 29 | REVIEW_REQUIRED |
| 298–302 | Yazma / afiş | 13 | 6 | REVIEW_REQUIRED |
| 303–307 | Tema ölçme ve değerlendirme | 14 | 14 | REFERENCE_QUALITY |

## Kaynak-parity kilitleri

- s.237 Yunus Emre geçişi QUESTION değildir.
- s.251–252 kaynakta üç gerçek `Metni Anlayalım` sorusu vardır; konu/amaç/yazar ilişkisi yapay biçimde ayrı sorulara bölünmez.
- s.262 iki gerçek `Sıra Sizde` sorusu görünürdür.
- s.269–270 `Metni Anlayalım` 1–8 ayrı soru kartlarıdır.
- s.274 karakter çözümleme ve s.276–277 çatışma çalışması doğal PROCESS bloklarıdır.
- s.280–283 dört hazırlık + üç yansıtma sorusu ayrı görünür; performans adımları soru bankasına çevrilmez.
- s.287–291 dinleme/izleme `Metni Anlayalım` 1–11 ayrı görünür.
- s.294–296 çözümleme 1–14 ayrı görünür.
- `Fedakârlık`, `Çalışkanlık` ve `Aidiyet` dış QR videolarında görülmeyen sahne/kişi/olay ayrıntısı üretilmez.
- s.299 üç hazırlık sorusu ve s.302 ilk üç değerlendirme sorusu ayrı görünür; paylaşım maddesi PROCESS olarak kalır.
- s.303–307 tema sonundaki 14 soru 14 ayrı QUESTION kartıdır.
- s.305 Q5 görsel seçenekleri PDF görsel katmanına bağlıdır; tek görsel anahtarı uydurulmaz.
- s.307 Q13–14 `Aidiyet` videosuna bağlıdır; cevap yalnız gerçek medya kanıtıyla kabul edilir.

## Altyapı

`book_components_v23*.json` parçalı registry desteği eklenmiştir. Aynı canonical item/key iki fragmentte tanımlanırsa build/validator bunu hata sayar; registry componentlerinin tamamı mirror projeksiyonunda kullanılmalıdır.

## CI durumu

Themes 1–3 son doğrulanmış checkpointlerde tam PASS durumundadır. Tema 4 final validatorı ve tam-kapsam kontratı branch'e eklenmiştir. Son Theme 4 CI denemelerinde GitHub Actions job'ları checkout başlamadan `steps=null` ile sonlanmıştır; dolayısıyla Tema 4 final hedef sayıları henüz runner üzerinde çalıştırılarak teyit edilememiştir. Bu altyapı durumu içerik PASS olarak yorumlanmaz.
