# TDE 11 textbook question inventory contract

`courses/TDE_11/textbook_question_inventory.json` is the canonical, source-verified
question inventory for the 11. sınıf ders kitabı. It is independent from any
teacher-book rendering or pedagogy model.

The active source chain is:

```text
official textbook PDF
        ↓
textbook_map.json + textbook_question_inventory.json
        ↓
teacher_book/source/TEMA_01..04/source_index.json
        ↓
new teacher-book authoring
```

Each inventory row carries question identity, theme/section, printed and PDF
page ranges, question number, prompt/prompt mode, source locator, official PDF
SHA-256 and verification provenance.

The neutral teacher-book source layer is validated with:

```bash
python skill/tymm-material-planner/scripts/validate_teacher_book_source.py --repo-root .
```

Activity and non-question task coverage continues to come from
`textbook_map.json` and the neutral source indexes. Teacher-book prose is not
allowed to redefine textbook prompts or locators.
