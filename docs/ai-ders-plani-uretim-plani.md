# AI Ders Planı Üretim Planı — 9. ve 10. Sınıf

## Amaç

Bu plan, ders planlarının bir API üzerinden otomatik üretilmesi yerine ChatGPT ile etkileşimli olarak, kontrollü ve parça parça üretilmesini tanımlar. Üretim; TYMM canonical bilgi, ders kitabı eşleştirmeleri, yıllık plandan alınmış takvimden arındırılmış saat dağılımı ve runtime context üzerinden yapılır.

## Neden hafta hafta değil?

Hafta, tarih, ara tatil, yarıyıl, resmî tatil ve benzeri takvim yerleşimleri yıldan yıla değişir. Bu nedenle üretim sırası haftaya bağlanmaz. Konu başlığı tek başına da yeterli üretim birimi değildir; aynı konu/blok farklı sayıda ders saatine yayılabilir.

Varsayılan üretim birimi **blok içi ders saati paketi**dir.

- Normal paket: 2 ders saati
- 15 saatlik blok: `2+2+2+2+2+2+2+1`
- 10 saatlik blok: `2+2+2+2+2`
- 8 saatlik blok: `2+2+2+2`
- Okul temelli planlama saatleri varsayılan ders planı kuyruğuna dahil değildir.

Bu yöntem, takvimden bağımsız kalırken öğretmenin gerçek sınıf uygulamasında kullanılabilecek kadar küçük ve devam ettirilebilir üretim parçaları sağlar.

## Üretim sırası

Varsayılan master sıra:

1. `TDE_9`
2. `TDE_10`

Her sınıf içinde sıra değişmez:

1. Tema sırası
2. `production/teaching_blocks.json` içindeki block sequence
3. Paket numarası

Bir blok bitmeden sonraki bloğa geçilmez. Bir tema bitmeden sonraki temaya geçilmez.

## Kapsam

Her sınıfta:

- 4 tema
- Tema başına 43 çekirdek öğretim saati
- Yıllık 172 çekirdek öğretim saati
- Tema başına ayrıca 2 saat okul temelli planlama, yıllık 8 saat
- Varsayılan ders planı kuyruğu yalnız 172 çekirdek saati kapsar
- Toplam 88 üretim paketi

İki sınıf birlikte toplam **176 ders planı paketi** üretilecektir.

## Kullanıcı komutlarının anlamı

### `planı uygula`

Sınıf belirtilmemişse master sıradaki ilk tamamlanmamış paket üretilir. Başlangıçta bu:

`TDE_9 → TEMA_01 → BLOCK_T1_01_OKUMA → P01 → 2 ders saati`

Bir komutta varsayılan olarak yalnız **bir paket** üretilir. Paket repoya eklendikten ve progress cursor güncellendikten sonra durulur.

### `devam et`

Son aktif üretim kuyruğundaki sıradaki paket üretilir.

### `10. sınıf planını uygula`

`TDE_10` içindeki ilk tamamlanmamış paketten başlanır veya mevcut cursor'dan devam edilir.

### `9. sınıfa devam et`

`TDE_9` üretim planındaki `progress.next` alanı esas alınır.

## Her paket nasıl üretilecek?

1. İlgili course production planından sıradaki paket belirlenir.
2. `lesson_plan_context.py` ile blok için source-bound context hazırlanır.
3. ChatGPT, `lesson_plan.schema.json` sözleşmesine göre plan JSON'unu yazar.
4. Plan yalnız context içindeki kazanım, etkinlik ve form kimliklerini kullanır.
5. Plan takvim/tarih/hafta bilgisi içermez.
6. `validate_lesson_plan.py` kurallarıyla grounding ve süre mantığı kontrol edilir.
7. Geçerli planın iki görünümü repoya eklenir:
   - machine-readable JSON
   - öğretmen-okunur Markdown
8. Course production planındaki progress cursor ilerletilir.

## Çıktı yolları

9. sınıf:

```text
courses/TDE_9/generated/lesson_plans/{theme_id}/{block_id}/{package_id}.json
courses/TDE_9/generated/lesson_plans/{theme_id}/{block_id}/{package_id}.md
```

10. sınıf:

```text
courses/TDE_10/generated/lesson_plans/{theme_id}/{block_id}/{package_id}.json
courses/TDE_10/generated/lesson_plans/{theme_id}/{block_id}/{package_id}.md
```

## Paket içeriği

Her pakette en az şunlar bulunur:

- sınıf / tema / blok kimliği
- paket süresi
- kullanılan resmî öğrenme çıktıları
- planın amacı ve kısa özeti
- ders saati bazında akış
- öğretmen eylemleri
- öğrenci eylemleri
- kullanılan ders kitabı etkinlikleri
- kullanılan değerlendirme formları
- ölçme/değerlendirme yaklaşımı
- materyaller
- öğretmen notu
- blokta kalan saat
- sonraki paket için devam ipucu

## Resmî bilgi ile pedagojik üretimin ayrımı

Resmî/canonical kabul edilenler:

- tema ve blok kimliği
- blok sırası
- blok toplam saati
- öğrenme çıktıları
- ders kitabı etkinlik/form kimlikleri ve kaynak lokasyonları

ChatGPT tarafından pedagojik olarak üretilenler:

- iki saatlik paketin ders içi alt akışı
- giriş soruları
- öğretmen yönergeleri
- etkinliklerin o paket içindeki sıralanışı
- geçişler
- kapanış ve öğretmen notları

Bu pedagojik alt sıralama **MEB'in resmî saat-saat sıralaması gibi sunulmaz**.

## Progress kaynakları

- `courses/TDE_9/planning/lesson_plan_production_plan.json`
- `courses/TDE_10/planning/lesson_plan_production_plan.json`

Bu dosyalardaki `progress.next`, üretime devam edilirken tek kaynak kabul edilir. Üretilmiş dosyalarla progress bilgisi çelişirse üretim durdurulur ve önce progress düzeltilir.

## İlk üretim noktası

```text
TDE_9
TEMA_01 — SÖZÜN İNCELİĞİ
BLOCK_T1_01_OKUMA
P01
2 ders saati
```

Bu paket tamamlandıktan sonra aynı blokta `P02` üretilecektir.
