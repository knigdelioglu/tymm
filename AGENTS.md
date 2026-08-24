# Repository Agent Rules

## Canonical process-component inheritance — mandatory

Before creating, editing, validating, freezing, indexing, or compiling any TYMM `curriculum_map.json`, read:

- `docs/canonical-process-component-inheritance.md`
- `docs/process-component-inheritance-migration-plan.md`

Critical invariant:

> A process component omitted from a theme/unit page is **not** evidence that the component does not exist. If the official curriculum defines process components under the matching parent/roof outcome (`TDE*.x`), the theme outcome must resolve/inherit those components unless the theme explicitly defines its own verified theme-specific components.

Do **not** infer `process_components_verbatim: []` merely because the theme page does not repeat the hierarchy.

Resolution precedence is mandatory:

1. verified theme-specific explicit components,
2. otherwise the shared normative roof catalog,
3. empty only when the normative source explicitly verifies that no component exists.

A verified theme-specific component definition is allowed to specialize the same subordinate code differently from the roof catalog. Do not treat that alone as a conflict and do not merge roof components into an explicit theme-specific set.

Validation must fail with `PROCESS_COMPONENT_INHERITANCE_MISSING` when the shared roof catalog has components for a parent outcome but a theme outcome with no explicit override resolves to an empty effective component set.

The TDE roof hierarchy is course-wide normative knowledge from the official TDE curriculum and is shared by the applicable grades/themes. Do not copy process-component content from another grade's theme data. Theme-specific facts remain grade/theme scoped; the shared roof catalog is the only cross-grade inheritance source.

Existing TDE_9–TDE_12 PASS/FROZEN states created before this invariant do not prove process-component completeness and must be revalidated during the migration.
