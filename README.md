# TYMM

`skill/` = reusable TYMM material-planner engine

`courses/` = course-specific frozen knowledge

`courses/TDE_9/` = mevcut ilk frozen course knowledge

`local_sources/` = raw PDF/local source files; Git ignored

`local_materials/` = eski/deneme materyalleri; Git ignored

`knowledge.sqlite` = derived cache; source of truth değildir ve Git'e alınmaz

## Kritik canonical invariant

TYMM süreç bileşenleri tema sayfasında tekrar yazılmadığında `process_components_verbatim: []` effective boşluk olarak yorumlanamaz. İlgili parent/çatı outcome resmî programın ortak bölümünde süreç bileşenleri tanımlıyorsa bunlar provenance korunarak tema outcome'una inherit edilir.

Ayrıntı ve migration kaydı:

- [Canonical Süreç Bileşeni Inheritance Kuralı](docs/canonical-process-component-inheritance.md)
- [Süreç Bileşeni Inheritance Düzeltme Planı](docs/process-component-inheritance-migration-plan.md)
- [Cross-grade Inheritance Audit](docs/process-component-inheritance-audit.json)

Migration 24 Ağustos 2026 itibarıyla tamamlanmıştır ve CI tarafından fail-closed enforce edilir:

- TDE_9: `54` outcome → `2 THEME_EXPLICIT + 52 ROOF_INHERITED`
- TDE_10: `64` outcome → `64 ROOF_INHERITED`
- TDE_11: `64` outcome → `64 ROOF_INHERITED`
- TDE_12: `64` outcome → `64 ROOF_INHERITED`
- unresolved: `0`
- inheritance missing: `0`

Shared roof catalog veya course resolution contract değişirse derived index/runtime fresh rebuild edilmeden PASS verilemez.

## Mevcut milestone

- TDE_9 knowledge architecture frozen
- Hybrid RAG / Knowledge Resolver frozen
- Assessment Design Contract frozen
- Process-component inheritance migration: COMPLETE / PASS

## `main` branch protection ve `Full validation gate`

Amaç: `main` branch'e hatalı, yarım veya doğrulanmamış değişikliğin girmesini teknik olarak engellemek.

Beklenen geliştirme akışı:

```text
ayrı branch
    ↓
Pull Request → main
    ↓
Full validation gate
    ↓
PASS → merge edilebilir
FAIL → merge engellenir
```

`Full validation gate`, `.github/workflows/tymm-lesson-plan-validation.yml` içindeki zorunlu PR check'idir. PR yalnız README gibi lesson-plan dışı bir dosyayı değiştirse bile check mutlaka oluşur; böylece required-check `Pending` durumunda takılmaz.

Gate başlıca şunları doğrular:

- 176/176 generated ders planı
- 344 çekirdek ders saati
- JSON ↔ Markdown deterministik parity
- exact package topology ve gap/overlap kontrolü
- canonical rubrik/resource/artifact grounding
- classroom adaptation / accessibility / media fallback sözleşmeleri
- closure time-budget sözleşmeleri
- large-class execution rotaları
- final mutation coverage suite
- validation report + commit SHA + content fingerprint binding

### GitHub Ruleset ayarı

Repo: `Settings → Rules → Rulesets → Protect main`

Önerilen nihai ayar:

```text
Ruleset name: Protect main
Enforcement status: Active
Target: Default (main)
Bypass list: boş

✅ Restrict deletions
✅ Require a pull request before merging
   Required approvals: 0

✅ Require status checks to pass
   ✅ Require branches to be up to date before merging
   Required check:
      ✅ Full validation gate

✅ Block force pushes

❌ Restrict creations
❌ Restrict updates
❌ Require linear history
❌ Require deployments to succeed
❌ Require signed commits
❌ Require code scanning results
❌ Require code quality results
```

Özellikle `Restrict updates` açılmamalıdır; normal PR merge akışını gereksiz biçimde bypass yetkisine bağlar. `Require a pull request before merging` zaten doğrudan `main` güncellemelerini engelleyen doğru kontroldür.

`Full validation gate` required check yapılınca PR, güncel `main` üzerinde bu check'i PASS etmeden merge edilemez. `Block force pushes` da branch geçmişinin zorla yeniden yazılarak bu güvenlik zincirinin aşılmasını engeller.

CI workflow'ları protected-main ile uyumludur: validation/finalizer ve P0 gate `main`e doğrudan bot push'u yapmaz; türetilmiş çıktılar doğrulanır ve validation binding artifact olarak korunur.

## Dokümantasyon

- [Yeniden Kullanılabilir Bilgi Mimarisi](docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md)
- [Sistemi Geri Yükleme](docs/RESTORE.md)
