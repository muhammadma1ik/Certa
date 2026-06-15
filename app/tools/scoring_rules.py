from typing import Any


def validate_score_range(score: float, score_name: str) -> None:
    """
    Validate that a score is between 0 and 100.
    """
    if score < 0 or score > 100:
        raise ValueError(f"{score_name} must be between 0 and 100. Received: {score}")


def calculate_hours_completion_ratio(
    hours_studied: float,
    recommended_hours: float,
) -> float:
    """
    Calculate how much of the recommended study time the learner has completed.
    Capped at 1.0 so extra hours do not unfairly inflate readiness.
    """
    if recommended_hours <= 0:
        raise ValueError("recommended_hours must be greater than 0")

    if hours_studied < 0:
        raise ValueError("hours_studied cannot be negative")

    return min(hours_studied / recommended_hours, 1.0)


def calculate_readiness_score(
    practice_score_avg: float,
    hours_studied: float,
    recommended_hours: float,
) -> float:
    """
    Calculate readiness score using deterministic rules.

    Weighting:
    - Practice performance contributes 70 points.
    - Study-hour completion contributes 30 points.

    Final score is out of 100.
    """
    validate_score_range(practice_score_avg, "practice_score_avg")

    hours_completion_ratio = calculate_hours_completion_ratio(
        hours_studied=hours_studied,
        recommended_hours=recommended_hours,
    )

    hours_factor = hours_completion_ratio * 30
    practice_factor = practice_score_avg * 0.70

    return round(hours_factor + practice_factor, 1)


def readiness_status(score: float, threshold: float) -> str:
    """
    Convert readiness score into a readiness label.
    """
    validate_score_range(score, "score")
    validate_score_range(threshold, "threshold")

    if score >= threshold:
        return "Ready"

    if score >= threshold - 10:
        return "Almost Ready"

    return "Needs More Preparation"


def calculate_readiness_gap(score: float, threshold: float) -> float:
    """
    Calculate how many points the learner is below or above the threshold.
    Positive number means above threshold.
    Negative number means below threshold.
    """
    validate_score_range(score, "score")
    validate_score_range(threshold, "threshold")

    return round(score - threshold, 1)


def identify_readiness_risk(
    status: str,
    capacity_risk: str,
    practice_score_avg: float,
    hours_completion_ratio: float,
) -> str:
    """
    Determine overall readiness risk using readiness status and workload/capacity signals.
    """
    if status == "Needs More Preparation":
        return "High"

    if capacity_risk == "High" and status != "Ready":
        return "High"

    if practice_score_avg < 70:
        return "High"

    if hours_completion_ratio < 0.60:
        return "Medium"

    if status == "Almost Ready":
        return "Medium"

    return "Low"


def recommend_next_action(
    status: str,
    weakest_skill: str,
    readiness_gap: float,
    next_step: str | None = None,
) -> str:
    """
    Recommend the next action based on readiness.
    """
    if status == "Ready":
        recommendation = "Recommend final review and exam scheduling readiness check."

        if next_step:
            recommendation += f" After that, consider the next learning step: {next_step}."

        return recommendation

    if status == "Almost Ready":
        return (
            f"Continue targeted revision on {weakest_skill}. "
            f"The learner is {abs(readiness_gap)} points below the readiness threshold."
        )

    return (
        f"Loop back into the study plan with extra focus on {weakest_skill}. "
        f"The learner is {abs(readiness_gap)} points below the readiness threshold."
    )


def generate_readiness_explanation(
    practice_score_avg: float,
    hours_studied: float,
    recommended_hours: float,
    readiness_score: float,
    threshold: float,
    status: str,
) -> str:
    """
    Create a human-readable explanation for why the learner received the score.
    """
    hours_completion_ratio = calculate_hours_completion_ratio(
        hours_studied=hours_studied,
        recommended_hours=recommended_hours,
    )

    hours_percentage = round(hours_completion_ratio * 100, 1)

    return (
        f"The learner has an average practice score of {practice_score_avg}% and has completed "
        f"{hours_studied} of {recommended_hours} recommended study hours "
        f"({hours_percentage}% of recommended time). "
        f"The deterministic readiness score is {readiness_score}, compared with a threshold of "
        f"{threshold}. Status: {status}."
    )


def score_learner_from_context(
    learner_context: dict[str, Any],
    capacity_risk: str = "Medium",
) -> dict[str, Any]:
    """
    Score learner readiness using combined learner context from data_loader.py.

    Expected learner_context:
    {
        "employee": {...},
        "work_signal": {...},
        "practice_history": {...},
        "certification": {...}
    }
    """
    employee = learner_context["employee"]
    practice_history = learner_context["practice_history"]
    certification = learner_context["certification"]

    practice_score_avg = float(practice_history["practice_score_avg"])
    hours_studied = float(practice_history["hours_studied"])
    recommended_hours = float(certification["recommended_hours"])
    threshold = float(certification["readiness_threshold"])
    weakest_skill = practice_history["weakest_skill"]
    next_step = certification.get("next_step")

    score = calculate_readiness_score(
        practice_score_avg=practice_score_avg,
        hours_studied=hours_studied,
        recommended_hours=recommended_hours,
    )

    status = readiness_status(
        score=score,
        threshold=threshold,
    )

    gap = calculate_readiness_gap(
        score=score,
        threshold=threshold,
    )

    hours_completion_ratio = calculate_hours_completion_ratio(
        hours_studied=hours_studied,
        recommended_hours=recommended_hours,
    )

    readiness_risk = identify_readiness_risk(
        status=status,
        capacity_risk=capacity_risk,
        practice_score_avg=practice_score_avg,
        hours_completion_ratio=hours_completion_ratio,
    )

    next_action = recommend_next_action(
        status=status,
        weakest_skill=weakest_skill,
        readiness_gap=gap,
        next_step=next_step,
    )

    explanation = generate_readiness_explanation(
        practice_score_avg=practice_score_avg,
        hours_studied=hours_studied,
        recommended_hours=recommended_hours,
        readiness_score=score,
        threshold=threshold,
        status=status,
    )

    return {
        "learner_id": employee["learner_id"],
        "employee_id": employee["employee_id"],
        "team": employee["team"],
        "role": employee["role"],
        "target_certification": certification["id"],
        "certification_name": certification["name"],
        "practice_score_avg": practice_score_avg,
        "hours_studied": hours_studied,
        "recommended_hours": recommended_hours,
        "hours_completion_ratio": round(hours_completion_ratio, 2),
        "readiness_score": score,
        "readiness_threshold": threshold,
        "readiness_gap": gap,
        "readiness_status": status,
        "readiness_risk": readiness_risk,
        "weakest_skill": weakest_skill,
        "loop_back_required": status != "Ready",
        "next_step": next_step,
        "recommended_next_action": next_action,
        "explanation": explanation,
    }
