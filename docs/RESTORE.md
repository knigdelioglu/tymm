# TYMM Backup Restore

Bu repository, TYMM course knowledge ve material-planner skill yedeğini içerir.

## Yapı

- `courses/TDE_9/`: frozen TDE_9 canonical ve validated knowledge
- `skill/tymm-material-planner/`: reusable global skill kopyası
- `local_sources/`: yerel PDF ve diğer ham kaynaklar; Git dışıdır
- `local_materials/`: eski/deneme materyalleri; Git dışıdır
- `knowledge.sqlite`: türetilmiş cache; source of truth değildir ve Git'e alınmaz

## Restore ilkeleri

1. `courses/TDE_9/` içindeki canonical ve validated dosyaları byte-preserving olarak kullanın.
2. `skill/tymm-material-planner/` içindeki skill, references, scripts, tests ve agents yapısını koruyun.
3. `local_sources/` ve `local_materials/` içerikleri yerel kalır; Git'e eklenmez.
4. `knowledge.sqlite` yeniden üretilebilir bir cache'tir; canonical knowledge yerine kullanılmaz.
5. Restore sırasında JSON/Markdown yeniden biçimlendirmesi, canonical knowledge değişikliği, index rebuild veya material generation yapılmaz.
