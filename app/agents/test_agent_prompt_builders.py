import json

from app.agents.assessment import build_assessment_prompt
from app.agents.curator import build_curator_prompt
from app.agents.engagement import build_engagement_prompt
from app.agents.manager_insights import build_manager_insights_prompt
from app.agents.planner import build_study_plan_prompt
from app.agents.verifier import build_verifier_prompt
from app.tools.data_loader import build_learner_context


def test_agent_prompts_include_grounding_and_safety_instructions() -> None:
    learner_context = build_learner_context("L-1001")
    learner_request = "I want to focus on Azure Functions and monitoring."

    prompts = [
        build_curator_prompt(learner_context, learner_request),
        build_study_plan_prompt("L-1001", learner_request),
        build_engagement_prompt("L-1001", learner_request),
        build_assessment_prompt("L-1001", learner_request),
        build_manager_insights_prompt("TEAM-A"),
    ]

    combined = "\n".join(prompts)

    assert "approved Foundry IQ knowledge base" in combined
    assert "Source references" in combined or "source references" in combined
    assert "Do not invent" in combined
    assert "privacy" in combined.lower()
    assert learner_request in combined


def test_verifier_prompt_requires_json_only() -> None:
    prompt = build_verifier_prompt(
        {
            "curator": {"output_text": "Uses approved source references."},
            "assessment": {"deterministic_readiness": {"readiness_status": "Ready"}},
        }
    )

    assert "Return JSON only" in prompt
    assert json.dumps({"approved": True})[:1] == "{"
