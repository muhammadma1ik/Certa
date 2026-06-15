from pathlib import Path
import json

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

SYNTHETIC_DIR = BASE_DIR / "data" / "synthetic"
APPROVED_DOCS_DIR = BASE_DIR / "data" / "approved_docs"

REQUIRED_SYNTHETIC_FILES = [
    "employees.csv",
    "work_signals.csv",
    "certifications.json",
    "practice_history.csv",
    "team_progress.csv",
]

REQUIRED_APPROVED_DOCS = [
    "engineering_certification_guide.md",
    "cloud_engineer_az204_guide.md",
    "devops_az400_guide.md",
    "security_sc900_guide.md",
    "data_engineer_dp203_guide.md",
    "internal_learning_policy.md",
    "assessment_rules.md",
    "workload_learning_report.md",
]


def validate_required_files() -> None:
    missing_files = []

    for file_name in REQUIRED_SYNTHETIC_FILES:
        file_path = SYNTHETIC_DIR / file_name
        if not file_path.exists():
            missing_files.append(str(file_path))

    for file_name in REQUIRED_APPROVED_DOCS:
        file_path = APPROVED_DOCS_DIR / file_name
        if not file_path.exists():
            missing_files.append(str(file_path))

    if missing_files:
        raise FileNotFoundError(f"Missing required files: {missing_files}")


def validate_csv_columns() -> None:
    employees = pd.read_csv(SYNTHETIC_DIR / "employees.csv")
    work_signals = pd.read_csv(SYNTHETIC_DIR / "work_signals.csv")
    practice_history = pd.read_csv(SYNTHETIC_DIR / "practice_history.csv")
    team_progress = pd.read_csv(SYNTHETIC_DIR / "team_progress.csv")

    required_employee_columns = {
        "employee_id",
        "learner_id",
        "team",
        "role",
        "target_certification",
        "experience_level",
    }

    required_work_signal_columns = {
        "employee_id",
        "meeting_hours_per_week",
        "focus_hours_per_week",
        "preferred_learning_slot",
        "workload_level",
        "missed_learning_sessions_last_14_days",
    }

    required_practice_columns = {
        "learner_id",
        "certification",
        "practice_score_avg",
        "hours_studied",
        "last_assessment_score",
        "weakest_skill",
        "exam_outcome_simulated",
    }

    required_team_columns = {
        "team",
        "certification",
        "total_learners",
        "ready_count",
        "almost_ready_count",
        "not_ready_count",
        "average_practice_score",
        "average_hours_studied",
        "capacity_risk",
    }

    checks = [
        ("employees.csv", employees, required_employee_columns),
        ("work_signals.csv", work_signals, required_work_signal_columns),
        ("practice_history.csv", practice_history, required_practice_columns),
        ("team_progress.csv", team_progress, required_team_columns),
    ]

    for file_name, dataframe, required_columns in checks:
        missing = required_columns - set(dataframe.columns)
        if missing:
            raise ValueError(f"{file_name} is missing columns: {missing}")

        if dataframe.empty:
            raise ValueError(f"{file_name} should not be empty")


def validate_certifications_json() -> None:
    cert_path = SYNTHETIC_DIR / "certifications.json"

    with open(cert_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if "certifications" not in data:
        raise ValueError("certifications.json must contain a 'certifications' key")

    if not data["certifications"]:
        raise ValueError("certifications.json must contain at least one certification")

    required_cert_keys = {
        "id",
        "name",
        "primary_roles",
        "skills",
        "recommended_hours",
        "readiness_threshold",
        "difficulty",
        "prerequisites",
        "next_step",
    }

    for cert in data["certifications"]:
        missing = required_cert_keys - set(cert.keys())
        if missing:
            raise ValueError(f"Certification {cert.get('id', 'UNKNOWN')} is missing keys: {missing}")


def validate_docs_are_synthetic() -> None:
    required_notice_terms = [
        "Synthetic content notice",
        "does not contain real employee data",
        "PII",
    ]

    for file_name in REQUIRED_APPROVED_DOCS:
        file_path = APPROVED_DOCS_DIR / file_name
        content = file_path.read_text(encoding="utf-8")

        for term in required_notice_terms:
            if term not in content:
                raise ValueError(f"{file_name} is missing synthetic notice term: {term}")


def main() -> None:
    validate_required_files()
    validate_csv_columns()
    validate_certifications_json()
    validate_docs_are_synthetic()
    print("Synthetic data and approved document validation passed.")


if __name__ == "__main__":
    main()