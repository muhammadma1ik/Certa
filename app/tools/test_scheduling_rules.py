import pytest

from app.tools.data_loader import build_learner_context
from app.tools.scheduling_rules import (
    calculate_capacity_risk,
    calculate_weekly_study_capacity,
    generate_study_plan_from_context,
    split_hours_across_weeks,
)


def test_weekly_capacity_respects_workload() -> None:
    assert calculate_weekly_study_capacity(22, 10, "High") == 2.5
    assert calculate_weekly_study_capacity(15, 18, "Medium") == 6
    assert calculate_weekly_study_capacity(10, 20, "Low") == 8


def test_capacity_risk_uses_meeting_focus_and_missed_sessions() -> None:
    assert calculate_capacity_risk(24, 9, 1) == "High"
    assert calculate_capacity_risk(18, 14, 2) == "Medium"
    assert calculate_capacity_risk(10, 20, 0) == "Low"


def test_study_plan_prioritizes_current_weakest_skill() -> None:
    context = build_learner_context("L-1001")
    study_plan = generate_study_plan_from_context(context)

    assert study_plan["capacity_risk"] == "Medium"
    assert study_plan["weekly_plan"][0]["focus_skill"] == "Azure Functions"
    assert sum(week["planned_hours"] for week in study_plan["weekly_plan"]) == pytest.approx(
        study_plan["recommended_total_hours"]
    )


def test_split_hours_validates_inputs() -> None:
    with pytest.raises(ValueError, match="total_hours"):
        split_hours_across_weeks(0, 4)

    with pytest.raises(ValueError, match="weekly_capacity"):
        split_hours_across_weeks(20, 0)
