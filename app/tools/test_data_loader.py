import pytest

from app.tools.data_loader import (
    build_learner_context,
    get_employee_by_learner_id,
    list_available_certifications,
    list_available_learners,
    list_available_teams,
    load_certifications,
    load_employees,
    load_practice_history,
    load_team_progress,
    load_work_signals,
)


def test_synthetic_data_loads() -> None:
    assert len(load_employees()) == 10
    assert len(load_work_signals()) == 10
    assert len(load_practice_history()) == 10
    assert len(load_team_progress()) == 7
    assert len(load_certifications()["certifications"]) == 4


def test_available_ids_are_stable_for_demo() -> None:
    assert list_available_learners()[0] == "L-1001"
    assert set(list_available_certifications()) == {"AZ-204", "AZ-400", "SC-900", "DP-203"}
    assert list_available_teams() == ["TEAM-A", "TEAM-B", "TEAM-C"]


def test_build_learner_context_joins_employee_work_practice_and_certification() -> None:
    context = build_learner_context("L-1001")

    assert context["employee"]["employee_id"] == "EMP-001"
    assert context["work_signal"]["workload_level"] == "High"
    assert context["practice_history"]["weakest_skill"] == "Azure Functions"
    assert context["certification"]["id"] == "AZ-204"


def test_unknown_learner_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="No learner found"):
        get_employee_by_learner_id("L-9999")
