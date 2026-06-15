from app.tools.data_loader import build_learner_context
from app.tools.scheduling_rules import generate_study_plan_from_context


AGENT_NAME = "study-plan-generator-agent"


def build_study_plan_prompt(learner_id: str, learner_request: str | None = None) -> str:
    learner_context = build_learner_context(learner_id)
    study_plan = generate_study_plan_from_context(learner_context)
    learner_request = learner_request or "No explicit learner request was provided."

    employee = learner_context["employee"]
    certification = learner_context["certification"]
    practice_history = learner_context["practice_history"]

    return f"""
Create a practical study plan for the learner using the approved Foundry IQ knowledge base and the deterministic scheduling constraints below.

Learner context:
- Learner role: {employee["role"]}
- Experience level: {employee["experience_level"]}
- Team: {employee["team"]}
- Target certification: {certification["id"]} ({certification["name"]})
- Certification difficulty: {certification["difficulty"]}
- Required skills: {certification["skills"]}
- Prerequisites: {certification["prerequisites"]}
- Recommended total study hours: {certification["recommended_hours"]}
- Current weakest skill: {practice_history["weakest_skill"]}

Learner request:
{learner_request}

Deterministic scheduling constraints:
- Weekly study capacity: {study_plan["weekly_study_capacity"]} hours
- Estimated weeks: {study_plan["estimated_weeks"]}
- Capacity risk: {study_plan["capacity_risk"]}
- Recommended study slot: {study_plan["recommended_study_slot"]}
- Recommended session frequency: {study_plan["recommended_session_frequency"]}
- Weekly plan: {study_plan["weekly_plan"]}

Task:
Turn these constraints and the learner request into a clear weekly study plan.

Important:
- Do not recalculate weekly capacity.
- Do not override estimated weeks.
- Do not invent certification requirements.
- Use the approved knowledge base for study guidance.
- Include source references when using knowledge base guidance.

Output format:
1. Learner role
2. Target certification
3. Study objective
4. Weekly study plan
5. Milestones and checkpoints
6. Workload-aware explanation
7. Source references
""".strip()
