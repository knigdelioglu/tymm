# TYMM Lesson Planning Engine V1

## Amaç

AI Lesson Generator, canonical TYMM bilgisini değiştirmeden öğretmen için uygulanabilir ders akışı üretir. Model doğrudan öğretim programını, ders kitabını veya yıllık plan Excel'ini yorumlamaz. Önce `lesson_plan_context.py` tarafından doğrulanmış minimum context pack oluşturulur.

Akış:

```text
course_runtime.sqlite
  -> lesson_plan_context.py
  -> immutable model request
  -> LLM/provider
  -> lesson_plan.schema.json
  -> validate_lesson_plan.py + generator validation
  -> PASS | REPAIR (en fazla 2 varsayılan) | BLOCKED
```

## Kaynak otoritesi

Generator şu alanları immutable kabul eder:

- `course_id`
- `theme_id`
- `block_id`
- istenen ders saati
- izin verilen öğrenme çıktıları
- izin verilen ders kitabı etkinlikleri
- izin verilen değerlendirme formları
- runtime kaynak/provenance bilgisi

Model bunları genişletemez veya değiştiremez.

## Takvim politikası

Yıllık plan yalnız konu/saat dağılımı için kullanılır. Generator:

- tarih,
- hafta numarası,
- akademik yıl,
- ara tatil,
- yarıyıl tatili,
- resmî tatil yerleşimi

üretmez ve bunları canonical planlama girdisi saymaz.

## Çıktı sözleşmesi

Model yalnız `schemas/lesson_plan.schema.json` ile uyumlu JSON döndürmelidir. Plan her ders için en az şu pedagojik alanları taşır:

- amaç,
- giriş,
- öğretmen eylemleri,
- öğrenci eylemleri,
- kullanılan canonical etkinlik/form kimlikleri,
- ölçme/değerlendirme,
- kapanış,
- materyaller.

Toplam `duration_lesson_hours`, istenen `lesson_hours` değerine eşit olmalıdır.

## Repair döngüsü

İlk model çıktısı geçmezse generator:

1. Şema hatalarını toplar.
2. Grounding validator hatalarını toplar.
3. Önceki adayı ve yalnız hata listesini modele geri verir.
4. Canonical context'i değiştirmeden tam JSON planı yeniden ister.

Varsayılan `max_repairs=2` değeridir. Bu bütçe sonunda plan geçmezse kullanıcıya geçersiz plan verilmez; sonuç `BLOCKED` olur.

## Provider sözleşmesi

Generator provider bağımsızdır. `--provider-command` ile verilen süreç:

- stdin'den tek JSON model request alır,
- stdout'a model yanıtını yazar,
- başarılı durumda exit code `0` döndürür.

Yanıt doğrudan plan JSON'u, JSON içeren metin veya `plan` / `output` / `result` zarfı olabilir.

Örnek çağrı:

```bash
python skill/tymm-material-planner/scripts/lesson_plan_generator.py \
  --knowledge-root courses/TDE_9 \
  --block-id BLOCK_T1_01_OKUMA \
  --lesson-hours 2 \
  generate \
  --provider-command "python /path/to/llm_bridge.py" \
  --output /tmp/lesson-plan.json \
  --trace-output /tmp/lesson-plan-trace.json
```

Sadece modele gönderilecek request'i görmek için:

```bash
python skill/tymm-material-planner/scripts/lesson_plan_generator.py \
  --knowledge-root courses/TDE_9 \
  --block-id BLOCK_T1_01_OKUMA \
  --lesson-hours 2 \
  request
```

Hazır bir planı aynı gate'lerle doğrulamak için:

```bash
python skill/tymm-material-planner/scripts/lesson_plan_generator.py \
  --knowledge-root courses/TDE_9 \
  --block-id BLOCK_T1_01_OKUMA \
  --lesson-hours 2 \
  validate \
  --plan /tmp/lesson-plan.json
```

## Continuation state

Blok birden fazla üretimde işlenebilir. İsteğe bağlı continuation state:

```json
{
  "completed_hours_before_this_plan": 4,
  "previously_used_activity_ids": ["..."],
  "previously_covered_outcome_codes": ["TDE2.1"],
  "previous_plan_summary": "İlk dört saatte temel okuma ve ilk tahlil tamamlandı."
}
```

Generator `completed + requested > block planned_hours` olduğunda fail-closed davranır. Önceden kullanılan canonical kimlikler de aynı bloğun izin verilen referans kümesinden olmak zorundadır.

## Güven sınırı

Generator'ın pedagojik metni AI üretimidir. Öğrenme çıktısı, ders kitabı etkinliği, form, süre ve provenance canonical katmandan gelir; üretilen öğretim sırası resmî MEB alt-saat sırası olarak temsil edilmez.
