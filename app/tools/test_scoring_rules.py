import pytest

from app.tools.data_loader import build_learner_context
from app.tools.scheduling_rules import generate_study_plan_from_context
from app.tools.scoring_rules import (
    calculate_hours_completion_ratio,
    calculate_readiness_score,
    score_learner_from_context,
)


def score_learner(learner_id: str) -> dict:
    learner_context = build_learner_context(learner_id)
    study_plan = generate_study_plan_from_context(learner_context)

    return score_learner_from_context(
        learner_context=learner_context,
        capacity_risk=study_plan["capacity_risk"],
    )


def test_readiness_score_is_deterministic() -> None:
    assert calculate_readiness_score(67, 14, 24) == 64.4
    assert calculate_hours_completion_ratio(48, 24) == 1.0


def test_readiness_statuses_cover_demo_scenarios() -> None:
    assert score_learner("L-1001")["readiness_status"] == "Needs More Preparation"
    assert score_learner("L-1004")["readiness_status"] == "Ready"
    assert score_learner("L-1010")["readiness_risk"] == "High"


def test_ready_learner_includes_next_step_and_no_loopback() -> None:
    readiness = score_learner("L-1006")

    assert readiness["readiness_status"] == "Ready"
    assert readiness["loop_back_required"] is False
    assert readiness["next_step"] == "SC-200"
    assert "SC-200" in readiness["recommended_next_action"]


def test_invalid_score_inputs_raise_errors() -> None:
    with pytest.raises(ValueError, match="practice_score_avg"):
        calculate_readiness_score(120, 10, 20)

    with pytest.raises(ValueError, match="hours_studied"):
        calculate_hours_completion_ratio(-1, 20)
