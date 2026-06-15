from app.orchestration import run_enterprise_learning_workflow


def test_deterministic_preview_workflow_returns_complete_agent_outputs() -> None:
    learner_request = "I want to focus on Azure Functions and monitoring."

    result = run_enterprise_learning_workflow(
        learner_id="L-1001",
        team="TEAM-A",
        learner_request=learner_request,
        live=False,
        save_trace=False,
    )

    assert result["mode"] == "deterministic_preview"
    assert result["learner_request"] == learner_request
    assert result["target_certification"] == "AZ-204"
    assert set(result["agent_outputs"]) == {
        "curator",
        "study_plan_generator",
        "engagement",
        "assessment",
        "manager_insights",
        "verifier",
    }
    assert result["trace"]["agent_event_count"] == 6
    assert result["trace_path"] is None
    assert result["verifier_decision"]["recommended_action"] in {"publish", "revise"}
    assert learner_request in result["agent_outputs"]["curator"]["prompt"]
    assert learner_request in result["agent_outputs"]["curator"]["output_text"]


def test_workflow_defaults_manager_team_to_learner_team() -> None:
    result = run_enterprise_learning_workflow(
        learner_id="L-1005",
        live=False,
        save_trace=False,
    )

    assert result["team"] == "TEAM-B"
    assert result["deterministic_outputs"]["readiness"]["target_certification"] == "SC-900"
