import json
from typing import Any

from app.agents.manager_insights import build_team_aggregate_context


CERT_GUIDE_BY_ID = {
    "AZ-204": "cloud_engineer_az204_guide.md",
    "AZ-400": "devops_az400_guide.md",
    "SC-900": "security_sc900_guide.md",
    "DP-203": "data_engineer_dp203_guide.md",
}


def format_sources(*file_names: str) -> str:
    unique_names = list(dict.fromkeys(file_names))
    return "\n".join(f"- data/approved_docs/{file_name}" for file_name in unique_names)


def build_curator_preview_output(learner_context: dict[str, Any], learner_request: str) -> str:
    employee = learner_context["employee"]
    certification = learner_context["certification"]
    cert_guide = CERT_GUIDE_BY_ID.get(certification["id"], "engineering_certification_guide.md")
    skills = certification["skills"]
    study_sequence = "\n".join(
        f"{index}. {skill}" for index, skill in enumerate(skills, start=1)
    )

    return f"""
### Role-aligned learning path

**Learner role:** {employee["role"]}
**Target certification:** {certification["id"]} - {certification["name"]}
**Learner request:** {learner_request}

The approved learning path starts with the learner's required role skills and keeps the focus on certification-aligned material. For this learner, the highest-value sequence is:

{study_sequence}

This path fits the learner because {certification["id"]} is mapped to {employee["role"]} in the synthetic certification guide, and the recommended skills match the role's day-to-day cloud enablement responsibilities.

**Source references**
{format_sources("engineering_certification_guide.md", cert_guide)}
""".strip()


def build_planner_preview_output(
    learner_context: dict[str, Any],
    study_plan: dict[str, Any],
    learner_request: str,
) -> str:
    certification = learner_context["certification"]
    weekly_lines = "\n".join(
        "- Week {week}: {planned_hours} hours, focus on {focus_skill}. {checkpoint}".format(
            **week
        )
        for week in study_plan["weekly_plan"]
    )

    return f"""
### Capacity-aware study plan

**Target certification:** {certification["id"]} - {certification["name"]}
**Learner request:** {learner_request}
**Weekly study capacity:** {study_plan["weekly_study_capacity"]} hours
**Estimated duration:** {study_plan["estimated_weeks"]} weeks
**Capacity risk:** {study_plan["capacity_risk"]}

{weekly_lines}

The plan protects the learner's work capacity by using synthetic meeting load, focus-hour availability, preferred study slot, and missed-session signals. The weakest skill is scheduled early so the loop-back path is visible when the learner is not ready.

**Source references**
{format_sources("internal_learning_policy.md", "workload_learning_report.md", CERT_GUIDE_BY_ID.get(certification["id"], "engineering_certification_guide.md"))}
""".strip()


def build_engagement_preview_output(
    learner_context: dict[str, Any],
    study_plan: dict[str, Any],
    learner_request: str,
) -> str:
    work_signal = learner_context["work_signal"]

    if study_plan["capacity_risk"] == "High":
        escalation = "If two more sessions are missed, flag a manager-level capacity review without exposing individual scores."
        style = "short, supportive nudges that protect focus time"
    elif study_plan["capacity_risk"] == "Medium":
        escalation = "If the learner misses two planned checkpoints, suggest a lighter week and targeted revision."
        style = "focused reminders with one weekly checkpoint"
    else:
        escalation = "No escalation needed; keep weekly progress confirmation."
        style = "standard progress reminders and checkpoint prompts"

    return f"""
### Supportive engagement strategy

**Reminder timing:** {study_plan["recommended_study_slot"]}
**Reminder frequency:** {study_plan["recommended_session_frequency"]}
**Reminder style:** {style}
**Learner request:** {learner_request}

The learner has {work_signal["meeting_hours_per_week"]} meeting hours, {work_signal["focus_hours_per_week"]} focus hours, and prefers {work_signal["preferred_learning_slot"].lower()} learning. Reminders reinforce the next small action without pressuring the learner or exposing performance details.

**Escalation rule:** {escalation}

**Privacy note:** Engagement uses synthetic work-context signals only. It does not include real calendar data, personal messages, or individual performance disclosure to managers.

**Source references**
{format_sources("workload_learning_report.md", "internal_learning_policy.md")}
""".strip()


def build_assessment_preview_output(
    learner_context: dict[str, Any],
    readiness: dict[str, Any],
    learner_request: str,
) -> str:
    certification = learner_context["certification"]
    cert_guide = CERT_GUIDE_BY_ID.get(certification["id"], "engineering_certification_guide.md")
    questions = []

    for index, skill in enumerate(certification["skills"], start=1):
        questions.append(
            f"{index}. Scenario question: A learner is preparing for {certification['id']} and needs to reason about {skill}. Which design choice best demonstrates that skill in a safe enterprise setting?\n"
            f"   - Correct answer: Choose the option that applies the approved {skill} guidance and explains the operational tradeoff.\n"
            f"   - Explanation: The approved guide requires understanding {skill} in context, not memorizing isolated facts.\n"
            f"   - Source: data/approved_docs/{cert_guide}"
        )

    return f"""
### Grounded readiness assessment

**Target certification:** {certification["id"]} - {certification["name"]}
**Learner request:** {learner_request}
**Deterministic readiness status:** {readiness["readiness_status"]}
**Readiness score:** {readiness["readiness_score"]} / 100
**Threshold:** {readiness["readiness_threshold"]}

{chr(10).join(questions[:5])}

**Readiness guidance:** {readiness["recommended_next_action"]}
**Weak area to revisit:** {readiness["weakest_skill"]}

The assessment uses deterministic readiness scoring for the decision and approved synthetic documents for practice-question topics.

**Source references**
{format_sources("assessment_rules.md", cert_guide)}
""".strip()


def build_manager_preview_output(team: str) -> str:
    aggregate_context = build_team_aggregate_context(team)

    return f"""
### Manager readiness insight

**Team:** {team}
**Learners represented:** {aggregate_context["total_learners"]}
**Capacity risk:** {aggregate_context["capacity_risk"]}
**Average practice score:** {aggregate_context["average_practice_score"]}%
**Average study hours:** {aggregate_context["average_hours_studied"]}

**Readiness bands:** {aggregate_context["readiness_counts"]}
**Main weak skill trends:** {aggregate_context["top_weak_skills"]}

Recommended manager actions:
- Protect focus time for teams with medium or high capacity risk.
- Use skill trends to schedule team study clinics.
- Review certification readiness at the team level, not by exposing individual records.

**Privacy-safe note:** {aggregate_context["privacy_note"]}

**Source references**
{format_sources("internal_learning_policy.md", "workload_learning_report.md", "assessment_rules.md")}
""".strip()


def build_verifier_preview_output(
    readiness: dict[str, Any],
    study_plan: dict[str, Any],
) -> str:
    risk_level = "low"
    issues: list[str] = []

    if readiness["readiness_risk"] == "High" or study_plan["capacity_risk"] == "High":
        risk_level = "medium"
        issues.append("Learner or team capacity risk requires careful pacing and review.")

    decision = {
        "approved": True,
        "risk_level": risk_level,
        "issues": issues,
        "human_review_required": bool(issues),
        "recommended_action": "publish" if not issues else "revise",
    }

    return json.dumps(decision, indent=2)


def build_deterministic_preview_agent_output(
    agent_key: str,
    learner_context: dict[str, Any],
    study_plan: dict[str, Any],
    readiness: dict[str, Any],
    team: str,
    learner_request: str | None = None,
) -> str:
    """
    Build an offline preview response when live Azure calls are unavailable.

    The preview path uses the same synthetic data, deterministic rules, prompts, and
    source references as the live workflow, but it does not call Foundry agents.
    """
    learner_request = learner_request or "No explicit learner request was provided."

    builders = {
        "curator": lambda: build_curator_preview_output(learner_context, learner_request),
        "planner": lambda: build_planner_preview_output(learner_context, study_plan, learner_request),
        "engagement": lambda: build_engagement_preview_output(learner_context, study_plan, learner_request),
        "assessment": lambda: build_assessment_preview_output(learner_context, readiness, learner_request),
        "manager": lambda: build_manager_preview_output(team),
        "verifier": lambda: build_verifier_preview_output(readiness, study_plan),
    }

    if agent_key not in builders:
        raise ValueError(f"Unknown deterministic preview agent key: {agent_key}")

    return builders[agent_key]()
