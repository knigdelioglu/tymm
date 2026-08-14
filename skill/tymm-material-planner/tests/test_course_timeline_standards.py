import copy
import json
from pathlib import Path

import pytest


ROOT = Path("/Users/kadir/Desktop/tymm")
TIMELINE_PATH = ROOT / "courses" / "TDE_9" / "planning" / "course_timeline.json"


def validate_timeline(data):
    themes = data["themes"]
    theme_orders = [theme["theme_order"] for theme in themes]
    if len(theme_orders) != len(set(theme_orders)):
        raise ValueError("duplicate theme order")
    block_ids = []
    for theme in themes:
        orders = [block["block_order"] for block in theme["blocks"]]
        if len(orders) != len(set(orders)):
            raise ValueError("duplicate block order")
        block_ids.extend(block["block_id"] for block in theme["blocks"])
    if len(block_ids) != len(set(block_ids)):
        raise ValueError("duplicate block id")
    known_theme_hours = sum(theme["official_total_hours"] for theme in themes)
    if known_theme_hours != data["annual_hours"]["core_instruction_hours"]:
        raise ValueError("theme totals conflict with annual core hours")
    if data["calendar_binding"]["status"] == "RESOLVED" and not data["calendar_binding"].get("week_mappings"):
        raise ValueError("calendar resolved without mappings")
    if data.get("timeline_semantics", {}).get("planned_position_is_not_student_mastery") is not True:
        raise ValueError("timeline must not be mastery")
    return True


@pytest.fixture
def timeline():
    return json.loads(TIMELINE_PATH.read_text(encoding="utf-8"))


def test_case_1_theme_hours_do_not_invent_block_hours(timeline):
    assert all(block["planned_hours"] is None for theme in timeline["themes"] for block in theme["blocks"])
    assert all(block["time_status"] == "ORDER_ONLY" for theme in timeline["themes"] for block in theme["blocks"])


def test_case_2_annual_division_does_not_declare_weekly_hours(timeline):
    assert timeline["calendar_binding"]["weekly_lesson_hours"] is None
    assert timeline["source_basis"]["temporal_fact_audit"]["weekly_lesson_hours"]["status"] == "UNRESOLVED"


def test_case_3_school_based_hours_stay_separate(timeline):
    assert timeline["annual_hours"]["core_instruction_hours"] == 172
    assert timeline["annual_hours"]["school_based_hours"] == 8
    assert all(theme["school_based_hours"] is None for theme in timeline["themes"])


def test_case_4_missing_calendar_is_unresolved(timeline):
    assert timeline["calendar_binding"]["status"] == "UNRESOLVED"
    assert timeline["calendar_binding"]["week_mappings"] == []


def test_case_5_planned_progress_is_not_mastery(timeline):
    assert timeline["timeline_semantics"]["meaning"] == "PLANNED_INSTRUCTIONAL_PROGRESSION"
    assert timeline["timeline_semantics"]["planned_position_is_not_student_mastery"] is True


def test_case_6_duplicate_block_order_fails(timeline):
    broken = copy.deepcopy(timeline)
    broken["themes"][0]["blocks"][1]["block_order"] = 1
    with pytest.raises(ValueError, match="duplicate block order"):
        validate_timeline(broken)


def test_case_7_conflicting_theme_totals_fail_closed(timeline):
    broken = copy.deepcopy(timeline)
    broken["themes"][0]["official_total_hours"] = 44
    with pytest.raises(ValueError, match="theme totals conflict"):
        validate_timeline(broken)


def test_case_8_not_selected_school_based_options_are_not_auto_selected(timeline):
    assert timeline["school_based_options_policy"]["auto_selected"] is False
    assert timeline["school_based_options_policy"]["selection_status"] == "NOT_SELECTED"


def test_canonical_timeline_validates(timeline):
    assert validate_timeline(timeline)
