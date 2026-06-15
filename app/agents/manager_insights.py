from typing import Any

from app.tools.data_loader import (
    load_employees,
    load_work_signals,
    load_practice_history,
    load_team_progress,
)


AGENT_NAME = "manager-insights-agent"


def build_team_aggregate_context(team: str) -> dict[str, Any]:
    employees = load_employees()
    work_signals = load_work_signals()
    practice_history = load_practice_history()
    team_progress = load_team_progress()

    team_employees = employees[employees["team"] == team]

    if team_employees.empty:
        raise ValueError(f"No employees found for team: {team}")

    merged = (
        team_employees
        .merge(work_signals, on="employee_id", how="left")
        .merge(practice_history, on="learner_id", how="left")
    )

    readiness_counts = (
        merged["exam_outcome_simulated"]
        .fillna("Unknown")
        .value_counts()
        .to_dict()
    )

    role_distribution = merged["role"].value_counts().to_dict()
    certification_distribution = merged["target_certification"].value_counts().to_dict()

    top_weak_skills = (
        merged["weakest_skill"]
        .dropna()
        .value_counts()
        .head(3)
        .to_dict()
    )

    team_cert_breakdown = (
        team_progress[team_progress["team"] == team]
        .drop(columns=["team"], errors="ignore")
        .to_dict(orient="records")
    )

    high_workload_count = int((merged["workload_level"] == "High").sum())
    average_meeting_hours = round(float(merged["meeting_hours_per_week"].mean()), 1)
    average_focus_hours = round(float(merged["focus_hours_per_week"].mean()), 1)
    average_practice_score = round(float(merged["practice_score_avg"].mean()), 1)
    average_hours_studied = round(float(merged["hours_studied"].mean()), 1)

    if high_workload_count >= 2 or average_meeting_hours > 20:
        capacity_risk = "High"
    elif average_meeting_hours > 15 or average_focus_hours < 15:
        capacity_risk = "Medium"
    else:
        capacity_risk = "Low"

    return {
        "team": team,
        "total_learners": int(len(merged)),
        "role_distribution": role_distribution,
        "certification_distribution": certification_distribution,
        "readiness_counts": readiness_counts,
        "average_practice_score": average_practice_score,
        "average_hours_studied": average_hours_studied,
        "average_meeting_hours": average_meeting_hours,
        "average_focus_hours": average_focus_hours,
        "high_workload_count": high_workload_count,
        "capacity_risk": capacity_risk,
        "top_weak_skills": top_weak_skills,
        "certification_breakdown": team_cert_breakdown,
        "privacy_note": (
            "This context is aggregate-only. It excludes learner IDs, employee IDs, "
            "names, emails, and individual performance records."
        ),
    }


def build_manager_insights_prompt(team: str) -> str:
    aggregate_context = build_team_aggregate_context(team)

    return f"""
Generate privacy-safe manager insights using only the aggregate synthetic team context below and the approved Foundry IQ knowledge base.

Aggregate team context:
{aggregate_context}

Task:
Create a manager-level summary of team certification readiness, learning risk, capacity constraints, and recommended actions.

Rules:
- Use only aggregate team-level data.
- Do not expose learner IDs, employee IDs, names, emails, personal schedules, or individual performance details.
- Do not invent metrics.
- Highlight team-level readiness, weak skill trends, capacity risk, and recommended support actions.
- Use the approved knowledge base for manager visibility, privacy guidance, workload-aware learning, and readiness guidance.
- Include source references.

Output format:
1. Team summary
2. Certification readiness overview
3. Capacity risk
4. Main weak skill areas
5. Manager recommendations
6. Privacy-safe note
7. Source references
""".strip()