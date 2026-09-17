# TDE 11 textbook question inventory contract

`courses/TDE_11/textbook_question_inventory.json` is the runtime canonical
question inventory for the TDE 11 Teacher Guide V3 chain. It is not a cache of
the V2.3 mirror and it is not regenerated from the guide outputs during
validation.

The source chain is:

```text
official textbook PDF identity
        ↓
textbook_question_inventory.json
        ↓
book_mirror_v23* projection
        ↓
teacher_guide_v3.json
        ↓
textbook_task_index.json
        ↓
TEACHER_GUIDE_V3.md
```

Each inventory row carries the question identity, theme/section, printed and
PDF page ranges, question number, prompt and prompt mode, the primary source
locator, the official PDF SHA-256, and source verification provenance. The
validator checks these fields before it evaluates any projection. A
`VERBATIM_SHORT` row also requires `provenance.verbatim: true` and exact prompt
fidelity.

## Bootstrap history versus runtime authority

The current 407 verified rows may have been bootstrapped during the earlier
migration from an already source-verified mirror because that mirror had the
reviewed textbook locators and prompt records. That bootstrap history is not a
runtime dependency and does not make the mirror authoritative. The inventory
now owns the canonical question set and its source contract; the mirror is a
rebuildable teacher-guide projection.

The inventory validator can run independently with:

```bash
python3 skill/tymm-material-planner/scripts/validate_teacher_guide_v3.py \
  --repo-root . --course TDE_11 --inventory-only
```

The full V3 validator then requires exact question-set equality between the
inventory, mirror, guide, and task index, plus field-level parity for theme,
section, page/locator, question number, prompt, prompt mode, and source
locator. Activity coverage remains owned by `textbook_map.json`.
