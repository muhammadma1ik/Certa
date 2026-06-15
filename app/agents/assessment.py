from app.tools.data_loader import build_learner_context
from app.tools.scheduling_rules import generate_study_plan_from_context
from app.tools.scoring_rules import score_learner_from_context


AGENT_NAME = "assessment-agent"


def build_assessment_prompt(learner_id: str, learner_request: str | None = None) -> str:
    learner_context = build_learner_context(learner_id)
    study_plan = generate_study_plan_from_context(learner_context)
    learner_request = learner_request or "No explicit learner request was provided."

    readiness = score_learner_from_context(
        learner_context=learner_context,
        capacity_risk=study_plan["capacity_risk"],
    )

    employee = learner_context["employee"]
    certification = learner_context["certification"]

    return f"""
Generate grounded practice questions and assessment guidance for the learner.

Learner context:
- Role: {employee["role"]}
- Target certification: {certification["id"]} ({certification["name"]})
- Required skills: {certification["skills"]}

Learner request:
{learner_request}

Deterministic readiness result:
- Practice score average: {readiness["practice_score_avg"]}
- Hours studied: {readiness["hours_studied"]}
- Recommended hours: {readiness["recommended_hours"]}
- Readiness score: {readiness["readiness_score"]}
- Readiness threshold: {readiness["readiness_threshold"]}
- Readiness status: {readiness["readiness_status"]}
- Readiness risk: {readiness["readiness_risk"]}
- Weakest skill: {readiness["weakest_skill"]}
- Loop-back required: {readiness["loop_back_required"]}
- Recommended next learning step if ready: {readiness["next_step"]}
- Recommended next action: {readiness["recommended_next_action"]}

Task:
Generate five grounded practice questions for the requested topics using only the approved Foundry IQ knowledge base.

Important:
- Do not recalculate readiness.
- Do not invent certification facts.
- Do not copy real exam questions.
- Do not create exam-dump style content.
- Use the deterministic readiness result above when giving readiness guidance.
- Include source references for each question or recommendation.
- If the learner is not ready, recommend loop-back study focus areas.

Output format:
1. Target certification
2. Five practice questions
3. Correct answer for each question
4. Short explanation for each answer
5. Source reference for each question
6. Readiness guidance
7. Weak areas to revisit
""".strip()
