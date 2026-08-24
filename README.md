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

## Dokümantasyon

- [Yeniden Kullanılabilir Bilgi Mimarisi](docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md)
- [Sistemi Geri Yükleme](docs/RESTORE.md)
