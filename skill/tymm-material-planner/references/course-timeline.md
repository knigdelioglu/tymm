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

## Resolution model

```text
official curriculum → stable instructional sequence → optional calendar binding
```

The stable layer may contain themes, blocks, outcomes, order, and explicitly supported theme or annual hours. The optional calendar layer may contain academic year, dates, weeks, and mappings only when supported by an official calendar and an official/verified schedule. Date-bound data must carry provenance and retrieval metadata.

## Fail-closed rules

- Do not distribute a theme total among blocks without explicit source support.
- Do not infer weekly lesson hours from annual hours and an assumed number of weeks.
- Do not fill school-based slots with `NOT_SELECTED` or otherwise optional recommendations.
- Do not bind dates when the academic calendar is absent or incomplete.
- If known theme totals conflict with the annual total, validation fails closed.
- Duplicate theme or block order/identity fails validation.
