# Course Timeline Standard

## Purpose

A course timeline models planned instructional progression from authoritative curriculum evidence. It is planning data, not a record of student learning, mastery, achievement, or actual teacher position.

## Invariants

1. Explicit official values outrank deterministic derivations; unsupported fields remain `UNRESOLVED`.
2. Missing hours, dates, weekly schedules, block durations, and placement rules must never be guessed.
3. Theme/block order and time allocation are separate concepts. An ordered block does not imply a duration.
4. A stable instructional sequence and a year-specific calendar binding are separate layers.
5. School-based hours remain distinct from core instruction and may not be silently assigned to optional activities.
6. Calendar-specific facts must not silently become timeless curriculum truth.
7. A reusable timeline may use these resolutions: `ORDER_ONLY`, `THEME_TIME_RESOLVED`, `BLOCK_TIME_RESOLVED`, `CALENDAR_RESOLVED`.
8. `planned_position` is not `actual_teacher_position` and neither is `student_mastery`; teacher overrides are external user state.
9. A verified MEB annual/draft annual plan may refine **topic/content hour distribution** only after course, grade, program/theme identity and source version are matched to canonical curriculum knowledge.
10. Annual-plan calendar metadata (month, date range, break rows, holidays, special days/weeks) is not part of the reusable topic-hour layer unless an explicit calendar-binding task requests it.
11. If an annual plan belongs to a different program structure (for example legacy unit structure vs current TYMM themes), ingestion must fail closed with `PROGRAM_ANNUAL_PLAN_VERSION_MISMATCH`.
12. For TYMM grades, canonical curriculum theme/annual hour totals remain normative. A year-specific annual plan can supply finer-grained planning weights, but cannot override those totals when its published row-hour sum is calendar-shaped or otherwise differs.

## Resolution model

```text
official curriculum
      ↓
stable instructional sequence
      ↓
verified annual-plan topic/hour distribution (optional, calendar-neutral)
      ↓
optional academic-calendar binding
```

The stable layer may contain themes, blocks, outcomes, order, and explicitly supported theme or annual hours. A verified annual/draft annual plan may add topic/content ordering and published lesson-hour weights after identity validation. The optional calendar layer may contain academic year, dates, weeks, breaks, holidays, and mappings only when explicitly needed and supported by an official calendar and an official/verified schedule.

### Calendar-neutral annual-plan extraction

When the goal is reusable lesson planning rather than a year-specific calendar:

- retain source row order,
- retain theme/unit identity,
- retain topic/content frame,
- retain published lesson-hour notation,
- preserve compound hour notation such as `3+2` without inventing a semantic binding between the numeric components and content domains,
- keep school-based planning separate,
- discard month/date ranges, break rows, holiday rows and special-day/week metadata,
- record source path, worksheet identity and fingerprint,
- validate the source program structure against canonical curriculum before any binding.

If a published annual-plan row distribution sums differently from an explicit canonical curriculum total, the annual-plan values are treated as **planning weights** and the canonical curriculum total remains authoritative.

## Fail-closed rules

- Do not distribute a theme total among blocks without explicit source support or a verified annual-plan distribution layer.
- Do not infer weekly lesson hours from annual hours and an assumed number of weeks.
- Do not fill school-based slots with `NOT_SELECTED` or otherwise optional recommendations.
- Do not bind dates when the academic calendar is absent or incomplete.
- Do not import break/holiday/date placement into reusable course knowledge merely because it appears in an annual plan.
- Do not bind a legacy annual plan to a current TYMM course with different theme/unit identities.
- If known theme totals conflict with the annual total, validation fails closed unless the conflicting year-specific annual-plan values are explicitly classified as non-normative planning weights.
- Duplicate theme or block order/identity fails validation.
