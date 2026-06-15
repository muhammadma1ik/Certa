from app.tools.data_loader import build_learner_context
from app.tools.scheduling_rules import generate_study_plan_from_context


AGENT_NAME = "engagement-agent"


def build_engagement_prompt(learner_id: str, learner_request: str | None = None) -> str:
    learner_context = build_learner_context(learner_id)
    study_plan = generate_study_plan_from_context(learner_context)
    learner_request = learner_request or "No explicit learner request was provided."

    employee = learner_context["employee"]
    certification = learner_context["certification"]
    work_signal = learner_context["work_signal"]

    return f"""
Create a supportive engagement and reminder strategy for the learner.

Learner context:
- Role: {employee["role"]}
- Experience level: {employee["experience_level"]}
- Team: {employee["team"]}
- Target certification: {certification["id"]} ({certification["name"]})

Learner request:
{learner_request}

Synthetic work-context signals:
- Meeting hours per week: {work_signal["meeting_hours_per_week"]}
- Focus hours per week: {work_signal["focus_hours_per_week"]}
- Preferred learning slot: {work_signal["preferred_learning_slot"]}
- Workload level: {work_signal["workload_level"]}
- Missed learning sessions in last 14 days: {work_signal["missed_learning_sessions_last_14_days"]}

Deterministic plan summary:
- Capacity risk: {study_plan["capacity_risk"]}
- Recommended study slot: {study_plan["recommended_study_slot"]}
- Recommended session frequency: {study_plan["recommended_session_frequency"]}
- Estimated weeks: {study_plan["estimated_weeks"]}

Task:
Create an engagement strategy that keeps the learner progressing on the requested topics without disrupting work.

Rules:
- Do not invent work signals.
- Do not create aggressive or punitive reminders.
- Adapt reminder timing to workload, focus hours, preferred slot, and capacity risk.
- Keep the tone supportive.
- Include a privacy-conscious escalation rule if needed.
- Use the approved knowledge base for workload-aware learning and engagement guidance.
- Include source references.

Output format:
1. Engagement goal
2. Reminder timing
3. Reminder frequency
4. Reminder style
5. Escalation rule
6. Privacy note
7. Source references
""".strip()
