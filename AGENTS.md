# Repository Agent Rules

## Canonical process-component inheritance — mandatory

Before creating, editing, validating, freezing, indexing, or compiling any TYMM `curriculum_map.json`, read:

- `docs/canonical-process-component-inheritance.md`
- `docs/process-component-inheritance-migration-plan.md`

Critical invariant:

> A process component omitted from a theme/unit page is **not** evidence that the component does not exist. If the official curriculum defines process components under the matching parent/roof outcome (`TDE*.x`), the theme outcome must resolve/inherit those components unless the theme explicitly defines its own verified components.

Do **not** infer `process_components_verbatim: []` merely because the theme page does not repeat the hierarchy.

Validation must fail with `PROCESS_COMPONENT_INHERITANCE_MISSING` when a verified roof catalog has components for a parent outcome but the theme outcome's effective component set is empty.

Do not copy process-component content across grades. The relevant grade's official curriculum remains normative; other MEB sources are cross-check evidence only.

Existing TDE_9–TDE_12 PASS/FROZEN states created before this invariant do not prove process-component completeness and must be revalidated during the migration.
