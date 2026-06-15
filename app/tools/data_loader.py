from pathlib import Path
import json
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
SYNTHETIC_DATA_DIR = BASE_DIR / "data" / "synthetic"


def _read_csv(file_name: str) -> pd.DataFrame:
    """
    Read a CSV file from data/synthetic.
    Raises a clear error if the file is missing.
    """
    file_path = SYNTHETIC_DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"Missing synthetic data file: {file_path}")

    return pd.read_csv(file_path)


def _read_json(file_name: str) -> dict[str, Any]:
    """
    Read a JSON file from data/synthetic.
    Raises a clear error if the file is missing.
    """
    file_path = SYNTHETIC_DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"Missing synthetic data file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_employees() -> pd.DataFrame:
    return _read_csv("employees.csv")


def load_work_signals() -> pd.DataFrame:
    return _read_csv("work_signals.csv")


def load_practice_history() -> pd.DataFrame:
    return _read_csv("practice_history.csv")


def load_team_progress() -> pd.DataFrame:
    return _read_csv("team_progress.csv")


def load_certifications() -> dict[str, Any]:
    return _read_json("certifications.json")


def get_employee_by_learner_id(learner_id: str) -> dict[str, Any]:
    employees = load_employees()
    match = employees[employees["learner_id"] == learner_id]

    if match.empty:
        raise ValueError(f"No learner found with learner_id: {learner_id}")

    return match.iloc[0].to_dict()


def get_work_signal_by_employee_id(employee_id: str) -> dict[str, Any]:
    work_signals = load_work_signals()
    match = work_signals[work_signals["employee_id"] == employee_id]

    if match.empty:
        raise ValueError(f"No work signal found for employee_id: {employee_id}")

    return match.iloc[0].to_dict()


def get_practice_history_by_learner_id(learner_id: str) -> dict[str, Any]:
    practice_history = load_practice_history()
    match = practice_history[practice_history["learner_id"] == learner_id]

    if match.empty:
        raise ValueError(f"No practice history found for learner_id: {learner_id}")

    return match.iloc[0].to_dict()


def get_certification_by_id(certification_id: str) -> dict[str, Any]:
    certifications_data = load_certifications()
    certifications = certifications_data.get("certifications", [])

    for certification in certifications:
        if certification.get("id") == certification_id:
            return certification

    raise ValueError(f"No certification found with id: {certification_id}")


def get_team_progress(team: str) -> pd.DataFrame:
    team_progress = load_team_progress()
    match = team_progress[team_progress["team"] == team]

    if match.empty:
        raise ValueError(f"No team progress found for team: {team}")

    return match


def build_learner_context(learner_id: str) -> dict[str, Any]:
    """
    Builds one combined learner context object.

    This will later be passed to:
    - Study Plan Generator
    - Engagement Agent
    - Manager Insights Agent
    - Verifier Agent
    """
    employee = get_employee_by_learner_id(learner_id)
    work_signal = get_work_signal_by_employee_id(employee["employee_id"])
    practice_history = get_practice_history_by_learner_id(learner_id)
    certification = get_certification_by_id(employee["target_certification"])

    return {
        "employee": employee,
        "work_signal": work_signal,
        "practice_history": practice_history,
        "certification": certification,
    }


def list_available_learners() -> list[str]:
    employees = load_employees()
    return employees["learner_id"].tolist()


def list_available_certifications() -> list[str]:
    certifications_data = load_certifications()
    certifications = certifications_data.get("certifications", [])
    return [certification["id"] for certification in certifications]


def list_available_teams() -> list[str]:
    employees = load_employees()
    return sorted(employees["team"].unique().tolist())