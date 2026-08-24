# TYMM

`skill/` = reusable TYMM material-planner engine

`courses/` = course-specific frozen knowledge

`courses/TDE_9/` = mevcut ilk frozen course knowledge

`local_sources/` = raw PDF/local source files; Git ignored

`local_materials/` = eski/deneme materyalleri; Git ignored

`knowledge.sqlite` = derived cache; source of truth değildir ve Git'e alınmaz

## Kritik canonical not

TYMM süreç bileşenleri tema sayfasında tekrar yazılmadığında `process_components_verbatim: []` kabul edilmez. İlgili parent/çatı outcome resmî programın genel bölümünde süreç bileşenleri tanımlıyorsa bunlar provenance korunarak tema outcome'una inherit edilmelidir. Ayrıntı ve migration planı:

- [Canonical Süreç Bileşeni Inheritance Kuralı](docs/canonical-process-component-inheritance.md)
- [Süreç Bileşeni Inheritance Düzeltme Planı](docs/process-component-inheritance-migration-plan.md)

Bu invariant eklenmeden üretilmiş TDE_9–TDE_12 PASS/FROZEN durumları süreç bileşeni completeness açısından yeniden doğrulanmalıdır.

## Mevcut milestone

- TDE_9 knowledge architecture frozen
- Hybrid RAG / Knowledge Resolver frozen
- Assessment Design Contract frozen
- 7 REQUIRED gerçek materyalin production aşaması henüz başlamadı

## Dokümantasyon

- [Yeniden Kullanılabilir Bilgi Mimarisi](docs/tymm-yeniden-kullanilabilir-bilgi-mimarisi-raporu.md)
- [Sistemi Geri Yükleme](docs/RESTORE.md)
