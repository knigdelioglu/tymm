# TDE9_KONUSMA_RUBRIC — Öğretmen İnceleme Paketi

**Karar durumu:** `AWAITING_EXPLICIT_TEACHER_APPROVAL`  
**Artifact:** `TDE9_KONUSMA_RUBRIC`  
**Mevcut lifecycle:** `REVIEW_REQUIRED`  
**Bu belge lifecycle onayı değildir.**

## 1. Teknik/pedagojik ön inceleme sonucu

Pilot rubrik, yıllık konuşma/sunum performansını beş çekirdek ölçütte toplar:

1. İçerik ve Göreve Uygunluk
2. Yapı, Organizasyon ve Zaman Yönetimi
3. Ses, Diksiyon ve Akıcılık
4. Beden Dili, Jest-Mimik ve İletişim
5. Türkçenin Doğru Kullanımı ve Söz Varlığı

Bu beş ölçüt registry'deki `TDE9_KONUSMA_RUBRIC` tanımı ve Tema 2–4 konuşma gap provenance'ı ile uyumludur. Dört performans düzeyi her ölçüt için ayrı betimleyici taşır. Birincil puanlama modeli eşit ağırlıklı `1–4` ham ortalamadır; 100'lük dönüşüm yalnız yardımcı gösterimdir ve resmî MEB puanlama kuralı olarak sunulmaz.

## 2. İncelenen kalite başlıkları

### Kapsam geçerliği

- Tema 2 için programda açıkça beklenen içerik kurgusu/etkileyicilik, zaman yönetimi, ses-diksiyon, akıcılık, beden dili ve Türkçenin doğru kullanımı çekirdek ölçütlerde temsil edilmektedir.
- Tema 3 ve Tema 4 görevleri aynı yıllık çekirdek construct'lara bağlanmış; görev-özel ayrıntılar task binding katmanında tutulmuştur.
- Rubrik, ders kitabındaki basit ölçüt tablosunu resmî bir analitik rubrikmiş gibi yeniden adlandırmaz; üretilen performans düzeyi betimleyicilerinin pedagojik türetim olduğu korunur.

### Düzey ayırt ediciliği

- 4 → 3 → 2 → 1 düzeylerinde tamlık, tutarlılık ve iletişime etkide kademeli azalma görünürdür.
- `yönlendirmeye ihtiyaç duyar` ifadesi bazı 1–2 düzeylerinde yer almaktadır. Bu ifade shared 4-level modelin destek gereksinimi boyutuyla uyumludur; ancak uygulamada puan verirken asıl kanıt her zaman gözlenen performans davranışı olmalıdır. Öğretmenin varsayımsal destek ihtiyacını değil, performansta gerçekten görülen sonucu esas alması önerilir.

### Uygulanabilirlik

- 5 ölçüt × 4 düzey, sınıf içi kullanım için yönetilebilir büyüklüktedir.
- Her ölçüt bağımsız puanlandığından tek bir güçlü/zayıf boyutun tüm performansı gizlemesi azaltılır.
- Öğretmen geri bildirimi için güçlü yön + tek gelişim odağı yaklaşımı uygulanabilir görünmektedir.

## 3. Ön inceleme kararı

**Ön inceleme sonucu: `READY_FOR_TEACHER_DECISION`.**

Bloke edici bir kaynak, kapsam veya puanlama mimarisi hatası tespit edilmemiştir. Bununla birlikte Generator V1 sözleşmesi gereği bu teknik/pedagojik ön inceleme, gerçek öğretmen onayının yerine geçmez.

Öğretmen onayı verilene kadar:

- `TDE9_KONUSMA_RUBRIC` → `REVIEW_REQUIRED` kalır.
- `TDE9_YAZMA_RUBRIC` üretim gate'i açılmaz.
- Tema 2 Yazma P05'te zorunlu öğretmen dereceli puanlama anahtarı sonucu varmış gibi davranılmaz.

## 4. Onaydan sonra izlenecek deterministik sıra

1. `TDE9_KONUSMA_RUBRIC` gerçek öğretmen kaydıyla `APPROVED` yapılır.
2. Generator V1 order gate açılır.
3. `TDE9_YAZMA_RUBRIC` (`RES_T2_12` dahil yıllık yazma rubriği) üretilir.
4. Yazma rubriği `REVIEW_REQUIRED` statüsünde doğrulanır; öğretmen kullanımında lifecycle açıkça korunur.
5. `BLOCK_T2_04_YAZMA_P05` içinde öğretmen rubrik geri bildirimi → gerekçeli nihai şiir revizyonu → `T2_ACT_14_TEMA_SONU_OLCME` → `T2_ACT_15_OGRENME_GUNLUGU` sırası tamamlanır.
6. Tema 2 43/43 saat kapanır ve cursor Tema 3 Okuma P01'e ilerler.

## 5. Yeniden üretilebilirlik notu

Repository'de pilot klasörde şu anda insan-okunur `REVIEW.md` izlenmektedir. Generator V1'in `approve` fonksiyonu çalışma dizininde `artifact.json` beklediği için gerçek lifecycle değişikliği yapılmadan önce artifact'ın canonical generator ile aynı checkout'ta üretilmiş ve doğrulanmış olması gerekir. Yalnız `REVIEW.md` metnini değiştirerek `APPROVED` taklidi yapılmamalıdır.
