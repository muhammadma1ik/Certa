from typing import Any


def normalize_workload_level(workload_level: str) -> str:
    """
    Normalizes workload level values so the rest of the logic is consistent.
    """
    if not workload_level:
        return "Medium"

    workload_level = workload_level.strip().title()

    if workload_level not in {"Low", "Medium", "High"}:
        return "Medium"

    return workload_level


def calculate_weekly_study_capacity(
    meeting_hours: float,
    focus_hours: float,
    workload_level: str,
) -> float:
    """
    Calculate a realistic weekly study capacity based on synthetic work signals.

    High workload or high meeting load = lighter study plan.
    Medium workload = balanced plan.
    Low workload = more available learning capacity.
    """
    workload_level = normalize_workload_level(workload_level)

    if workload_level == "High" or meeting_hours > 20:
        return round(min(4, max(2, focus_hours * 0.25)), 1)

    if workload_level == "Medium":
        return round(min(6, max(3, focus_hours * 0.35)), 1)

    return round(min(8, max(4, focus_hours * 0.40)), 1)


def calculate_capacity_risk(
    meeting_hours: float,
    focus_hours: float,
    missed_sessions_last_14_days: int,
) -> str:
    """
    Calculates risk that the learner may struggle to complete the study plan.
    """
    if meeting_hours > 22 or focus_hours < 10 or missed_sessions_last_14_days >= 4:
        return "High"

    if meeting_hours > 16 or focus_hours < 15 or missed_sessions_last_14_days >= 2:
        return "Medium"

    return "Low"


def choose_study_slot(
    preferred_slot: str,
    meeting_hours: float,
    focus_hours: float,
) -> str:
    """
    Recommend a study timing strategy based on focus availability.
    """
    preferred_slot = preferred_slot.strip().lower() if preferred_slot else "flexible"

    if focus_hours < 12:
        return f"Short {preferred_slot} sessions, 25–30 minutes each"

    if meeting_hours > 20:
        return f"Protected {preferred_slot} sessions, 30–45 minutes each"

    return f"Deep work block during {preferred_slot}, 60–90 minutes"


def recommend_session_frequency(capacity_risk: str) -> str:
    """
    Recommend how often the learner should study.
    """
    if capacity_risk == "High":
        return "3 short sessions per week"

    if capacity_risk == "Medium":
        return "3–4 focused sessions per week"

    return "4–5 focused sessions per week"


def split_hours_across_weeks(
    total_hours: float,
    weekly_capacity: float,
) -> list[dict[str, Any]]:
    """
    Split total recommended certification hours across realistic weekly capacity.
    """
    if total_hours <= 0:
        raise ValueError("total_hours must be greater than 0")

    if weekly_capacity <= 0:
        raise ValueError("weekly_capacity must be greater than 0")

    weeks = []
    remaining = total_hours
    week = 1

    while remaining > 0:
        hours = min(weekly_capacity, remaining)

        weeks.append(
            {
                "week": week,
                "planned_hours": round(hours, 1),
            }
        )

        remaining -= hours
        week += 1

    return weeks


def assign_skills_to_weeks(
    weekly_plan: list[dict[str, Any]],
    skills: list[str],
    priority_skill: str | None = None,
) -> list[dict[str, Any]]:
    """
    Assign certification skills across the weekly study plan.
    """
    if not skills:
        return weekly_plan

    ordered_skills = list(skills)

    if priority_skill in ordered_skills:
        ordered_skills.remove(priority_skill)
        ordered_skills.insert(0, priority_skill)

    updated_plan = []

    for index, week in enumerate(weekly_plan):
        skill = ordered_skills[index % len(ordered_skills)]

        updated_week = {
            **week,
            "focus_skill": skill,
            "checkpoint": f"Complete practice checkpoint for {skill}",
        }

        updated_plan.append(updated_week)

    return updated_plan


def generate_study_plan_from_context(learner_context: dict[str, Any]) -> dict[str, Any]:
    """
    Generate a complete deterministic study plan from the combined learner context.

    Expected learner_context structure:
    {
        "employee": {...},
        "work_signal": {...},
        "practice_history": {...},
        "certification": {...}
    }
    """
    employee = learner_context["employee"]
    work_signal = learner_context["work_signal"]
    practice_history = learner_context["practice_history"]
    certification = learner_context["certification"]

    meeting_hours = float(work_signal["meeting_hours_per_week"])
    focus_hours = float(work_signal["focus_hours_per_week"])
    workload_level = work_signal["workload_level"]
    preferred_slot = work_signal["preferred_learning_slot"]
    missed_sessions = int(work_signal["missed_learning_sessions_last_14_days"])

    recommended_hours = float(certification["recommended_hours"])
    skills = certification["skills"]

    weekly_capacity = calculate_weekly_study_capacity(
        meeting_hours=meeting_hours,
        focus_hours=focus_hours,
        workload_level=workload_level,
    )

    capacity_risk = calculate_capacity_risk(
        meeting_hours=meeting_hours,
        focus_hours=focus_hours,
        missed_sessions_last_14_days=missed_sessions,
    )

    study_slot = choose_study_slot(
        preferred_slot=preferred_slot,
        meeting_hours=meeting_hours,
        focus_hours=focus_hours,
    )

    session_frequency = recommend_session_frequency(capacity_risk)

    weekly_plan = split_hours_across_weeks(
        total_hours=recommended_hours,
        weekly_capacity=weekly_capacity,
    )

    weekly_plan = assign_skills_to_weeks(
        weekly_plan=weekly_plan,
        skills=skills,
        priority_skill=practice_history["weakest_skill"],
    )

    return {
        "learner_id": employee["learner_id"],
        "employee_id": employee["employee_id"],
        "team": employee["team"],
        "role": employee["role"],
        "target_certification": certification["id"],
        "certification_name": certification["name"],
        "recommended_total_hours": recommended_hours,
        "weekly_study_capacity": weekly_capacity,
        "estimated_weeks": len(weekly_plan),
        "capacity_risk": capacity_risk,
        "recommended_study_slot": study_slot,
        "recommended_session_frequency": session_frequency,
        "current_weakest_skill": practice_history["weakest_skill"],
        "weekly_plan": weekly_plan,
        "planning_reason": build_planning_reason(
            meeting_hours=meeting_hours,
            focus_hours=focus_hours,
            workload_level=workload_level,
            capacity_risk=capacity_risk,
            weekly_capacity=weekly_capacity,
        ),
    }


def build_planning_reason(
    meeting_hours: float,
    focus_hours: float,
    workload_level: str,
    capacity_risk: str,
    weekly_capacity: float,
) -> str:
    """
    Explain why the schedule was created this way.
    """
    return (
        f"The learner has {meeting_hours} meeting hours and {focus_hours} focus hours per week. "
        f"Their workload level is {workload_level}, producing a {capacity_risk.lower()} capacity risk. "
        f"The weekly study load is therefore limited to {weekly_capacity} hours to keep the plan realistic."
    )
