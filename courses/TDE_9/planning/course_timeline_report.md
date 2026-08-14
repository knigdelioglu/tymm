# TDE_9 Annual Course Timeline Report

## Scope and semantics

This artifact represents planned instructional progression. It does not represent student learning, mastery, achievement, or actual teacher position.

`PLANNED_POSITION != ACTUAL_TEACHER_POSITION != STUDENT_MASTERY`

The stable instructional sequence is separated from the year-specific `calendar_binding`. Teacher overrides remain external user state and are not written into this canonical artifact.

## WHAT WE KNOW

- Annual hours: **180** official hours.
- Core instruction: **172** annual hours, derived as 4 × 43 explicit theme hours.
- School-based planning capacity: **8** annual hours, explicit in `curriculum_map.json`.
- Theme count and order: **4**, in the canonical order TEMA_01 → TEMA_02 → TEMA_03 → TEMA_04.
- Theme core hours: **43 per theme** (Anlama 23 + Anlatma 20), explicit at curriculum locators s. 65, 73, 80, 89.
- Stable block sequence: **16 blocks**, four per theme, from `production/teaching_blocks.json`.
- School-based options: all remain `NOT_SELECTED`; none is automatically included.

## WHAT WE DERIVE

- 172 core instructional hours = 43 × 4.
- 16-block count and per-theme block order are deterministic derivations from the verified teaching-block artifact.
- Block-hour resolution is **ORDER_ONLY**: block order is usable, but no block duration is allocated.
- Theme sequence is stable course knowledge; calendar binding is a separate optional layer.

## WHAT WE DO NOT KNOW

- A canonical source does not explicitly allocate the 8 annual school-based hours as 2 hours inside each individual theme. Therefore `school_based_hours` is `null` at theme level; only annual capacity 8 is asserted.
- No official block-specific hour distribution is available. No hours are invented for reading, listening, writing, or speaking blocks.
- Weekly lesson hours are unresolved. 180 divided by a possible week count is not treated as evidence.
- No official academic-year/week/date mapping is present in the project source set. `calendar_binding.status = UNRESOLVED`.
- Learning-area-specific hours and school-based placement rules are unresolved.

## Temporal fact audit

| Value | Source | Source locator | Status |
|---|---|---|---|
| 180 annual hours | `curriculum_map.json` | `scope_summary.allocated_lesson_hours`; PDF s. 28-29 | EXPLICIT_OFFICIAL |
| 4 themes | `curriculum_map.json` | `scope_summary.total_themes` | EXPLICIT_OFFICIAL |
| Official theme order | `curriculum_map.json` | `themes[].theme_no` | EXPLICIT_OFFICIAL |
| 43 hours per theme | `curriculum_map.json` | `themes[].allocated_lesson_hours.total`; s. 65/73/80/89 | EXPLICIT_OFFICIAL |
| 43 core hours per theme | `curriculum_map.json` | `allocated_lesson_hours.total` | EXPLICIT_OFFICIAL |
| 8 annual school-based hours | `curriculum_map.json` | `scope_summary.allocated_lesson_hours.school_based_planning_hours` | EXPLICIT_OFFICIAL |
| 16 blocks | `production/teaching_blocks.json` | `summary.total_teaching_blocks`; `blocks[]` | DETERMINISTIC_DERIVATION |
| Block order | `production/teaching_blocks.json` | `blocks[].block_sequence` | DETERMINISTIC_DERIVATION |
| Block-specific hours | `production/teaching_blocks.json` | `summary.block_lesson_hours_status` | UNRESOLVED |
| Learning-area hours | project source set | no supporting locator | UNRESOLVED |
| Weekly lesson hours | project source set | no official schedule | UNRESOLVED |
| Academic year/week mapping | project source set | no official calendar | UNRESOLVED |
| School-based hours per theme | project source set | annual 8 is known; per-theme placement absent | UNRESOLVED |

## Validation summary

- Annual hours: **PASS** (180 = 172 core + 8 annual school-based capacity).
- Theme hours: **PASS** (4 × 43 = 172 core hours).
- School-based hours: **PASS / ANNUAL-ONLY** (8 retained separately; per-theme placement unresolved).
- Block count: **PASS** (16).
- Block order completeness: **PASS** (1-4 unique within each theme; no duplicate block IDs).
- Block-hour resolution: **ORDER_ONLY**.
- Weekly-hour resolution: **UNRESOLVED**.
- Calendar resolution: **UNRESOLVED**.
- Unsupported assumptions: **NONE**. In particular, no block durations, weekly hours, dates, or calendar mappings were guessed.
- Unresolved temporal fields: block hours, per-theme school-based placement, learning-area hours, weekly hours, academic-year dates/weeks.
- Source locators: **PASS** for all known facts.
- Overall readiness: **PASS for stable sequence and theme-time layer; REVIEW_REQUIRED for date-bound behavior**.

The existing `teaching_blocks.json` and `school_based_planning_options.json` contain a 45/43+2 theme policy in a lower-level production artifact, but the higher-authority `curriculum_map.json` explicitly records 43 per theme and 8 annual school-based hours. The timeline does not promote the lower-level 2-hours-per-theme policy to official per-theme fact.
