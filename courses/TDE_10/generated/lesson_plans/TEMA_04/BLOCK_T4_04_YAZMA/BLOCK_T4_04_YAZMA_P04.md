# Şiiri Çok Kaynaklı Değerlendirmek: Akran, Öğretmen Rubriği ve Tek Revizyon Hedefi

> Bu Markdown, lesson-plan JSON dosyasından deterministik olarak üretilir. JSON authoritative kaynaktır; bu dosyada elle semantik değişiklik yapılmaz.

## Paket bilgisi

| Alan | Değer |
|---|---|
| Ders | `TDE_10` |
| Tema | `TEMA_04` |
| Blok | `BLOCK_T4_04_YAZMA` |
| Süre | 2 ders saati |
| Şema | `1.0.0` |

## Paket özeti

Tema 4 Yazma bloğunun 7-8. saatlerinde T4_ACT_18_SIIR_DEGERLENDIRME sürdürülür. Öğrenciler FORM_T4_YAZMA_AKRAN üzerinden somut metin kanıtına dayalı akran geri bildirimi verir. Öğretmen değerlendirmesinde LINK_T4_YAZMA_DPA resmî kaynak bağı korunur; exact EBA payload erişilebilir değilse repo tarafından owner-authorized application support olarak kabul edilen TDE10_YAZMA_RUBRIC / FORM_T10_T4_YAZMA_DPA_CANONICAL kullanılır ve bunun EBA exact eşdeğeri olduğu iddia edilmez. Akran, süreç checklist'i ve öğretmen rubriği tek puana karıştırılmaz; P05 için yalnız bir final revizyon önceliği seçilir.

## Öğrenme ve değerlendirme kapsamı

- **Öğrenme çıktıları:** `TDE4.2`, `TDE4.3`, `TDE4.4`
- **Kullanılan etkinlikler:** `T4_ACT_18_SIIR_DEGERLENDIRME`
- **Kullanılan formlar:** `FORM_T4_YAZMA_AKRAN`, `LINK_T4_YAZMA_DPA`

## Canonical referanslar

### Form referansları

| Form | Kullanım |
|---|---|
| `FORM_T10_T4_YAZMA_DPA_CANONICAL` | `USED` |
| `FORM_T4_YAZMA_AKRAN` | `USED` |
| `FORM_T4_YAZMA_KONTROL` | `REFERENCE_ONLY` |
| `LINK_T4_YAZMA_DPA` | `USED` |

### Değerlendirme artefakt referansları

| Artefakt | Binding | Kullanım |
|---|---|---|
| `TDE10_YAZMA_RUBRIC` | `REQ_T10_T4_YAZMA_DPA` | `USED` |

### Kaynak plan referansları

| Kaynak planı | Kullanım |
|---|---|
| — | — |

# Ders akışı

## 1. Ders — Akran geri bildirimi: kişiye değil metne

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE4.4`

### Hedef

Şiiri FORM_T4_YAZMA_AKRAN ile metin kanıtına dayalı biçimde değerlendirmek ve kullanılabilir geri bildirim üretmek.

### Derse giriş

P03 değerlendirme sürümü ve kaynak anlam kontrolü açılır.

### Öğretmenin yapacakları

1. Akran değerlendirmesini şiirde gözlenebilir unsurlara bağlat.
2. Genel beğeni, kişilik veya yazar niyeti tahmini yerine metin kanıtı iste.
3. Her gelişim önerisinde 'nerede/ne değişirse/ne kazanır?' yapısını kullandır.

### Öğrencinin yapacakları

- FORM_T4_YAZMA_AKRAN'ı doldurur.
- Bir güçlü yönü ve bir gelişim önerisini metin kanıtıyla gerekçelendirir.
- Kendi şiirine gelen geri bildirimi kanıtla karşılaştırır.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_18_SIIR_DEGERLENDIRME`
- **Formlar:** `FORM_T4_YAZMA_AKRAN`

### Ölçme / öğrenme kanıtı

metin kanıtı → akran yargısı → uygulanabilir öneri.

### Kapanış

Akran geri bildiriminden gerçekten işe yarayabilecek bir aday revizyon belirlenir.

### Materyaller

- Değerlendirme sürümü
- FORM_T4_YAZMA_AKRAN

## 2. Ders — Öğretmen değerlendirmesi ve tek final revizyon hedefi

**Süre:** 1 ders saati  
**Öğrenme çıktıları:** `TDE4.2`, `TDE4.3`, `TDE4.4`

### Hedef

Öğretmen rubriği, akran geri bildirimi ve süreç kanıtlarını rolleri karıştırmadan yorumlayıp P05 için tek gözlenebilir revizyon hedefi seçmek.

### Derse giriş

Akran geri bildirimi ile P03 süreç checklist'i yan yana getirilir.

### Öğretmenin yapacakları

1. Resmî DPA erişilebiliyorsa exact aracı kullan; erişilemiyorsa assessment_gate_audit'ın izin verdiği TDE10_YAZMA_RUBRIC / FORM_T10_T4_YAZMA_DPA_CANONICAL desteğini kullan.
2. Canonical desteğin exact EBA payload eşdeğeri olmadığını açık tut.
3. Akran, checklist ve öğretmen rubriğini aritmetik olarak birleştirme.
4. Öğrenciye yalnız bir final revizyon önceliği seçtir: tema aktarımı, içerik, etkililik, şiir dili, söz varlığı, üslup/estetik veya dil bilgisi gibi gözlenebilir bir alan.

### Öğrencinin yapacakları

- Farklı geri bildirim kaynaklarını ayrı okur.
- Tekrarlanan ve kaynağa özgü bulguları ayırır.
- P05 için tek revizyon hedefi ve kanıtını yazar.

### Kaynak bağları

- **Etkinlikler:** `T4_ACT_18_SIIR_DEGERLENDIRME`
- **Formlar:** `LINK_T4_YAZMA_DPA`

### Ölçme / öğrenme kanıtı

geri bildirim kaynağı → somut kanıt → tek revizyon önceliği.

### Kapanış

P05 öncesi hedef 'mevcut kanıt → değişecek bölüm → beklenen etki' biçiminde dondurulur.

### Materyaller

- FORM_T4_YAZMA_AKRAN
- FORM_T4_YAZMA_KONTROL
- LINK_T4_YAZMA_DPA
- TDE10_YAZMA_RUBRIC canonical support

## Öğretmen notu

assessment_gate_audit, TDE10_YAZMA_RUBRIC desteğini owner-authorized canonical uygulama desteği olarak açmıştır; EBA external target ile exact eşdeğerlik doğrulanmış değildir. Bu ayrım öğretmen notunda korunmalıdır. Akran ve süreç araçlarından yapay bir birleşik puan üretilmez.

## İlerleme ve devam

- **Bu pakette planlanan:** 2 saat
- **Blokta kalan:** 2 saat
- **Kapsanan çıktılar:** `TDE4.2`, `TDE4.3`, `TDE4.4`
- **Kullanılan etkinlikler:** `T4_ACT_18_SIIR_DEGERLENDIRME`
- **Sonraki adım:** P05'te yalnız seçilen tek final revizyonu uygula; ardından T4_ACT_19 ve T4_ACT_20 ile Tema 4 ve 10. sınıf çekirdek öğretimi kapat.

---

<!-- TYMM_JSON_SHA256:fe70d76fc524f8ea2f64cc056394db07bda92e886c4deb46a15bd4466971defb -->
