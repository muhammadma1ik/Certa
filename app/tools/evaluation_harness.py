import argparse
import json
from pathlib import Path
from typing import Any

from app.orchestration import run_enterprise_learning_workflow


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CASES_PATH = BASE_DIR / "evals" / "test_cases.jsonl"


def load_eval_cases(path: Path = DEFAULT_CASES_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing eval case file: {path}")

    cases: list[dict[str, Any]] = []

    with open(path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()

            if not stripped:
                continue

            try:
                cases.append(json.loads(stripped))
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on line {line_number}: {error}") from error

    return cases


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    result = run_enterprise_learning_workflow(
        learner_id=case["learner_id"],
        team=case.get("team"),
        learner_request=case.get("learner_request"),
        live=False,
        save_trace=False,
    )

    readiness = result["deterministic_outputs"]["readiness"]
    study_plan = result["deterministic_outputs"]["study_plan_constraints"]
    verifier_decision = result["verifier_decision"]

    checks = {
        "readiness_status": readiness["readiness_status"] == case["expected_readiness_status"],
        "capacity_risk": study_plan["capacity_risk"] == case["expected_capacity_risk"],
        "verifier_parseable": "parse_error" not in verifier_decision,
        "agent_event_count": result["trace"]["agent_event_count"] == 6,
    }

    return {
        "case_id": case["case_id"],
        "learner_id": case["learner_id"],
        "passed": all(checks.values()),
        "checks": checks,
        "actual": {
            "readiness_status": readiness["readiness_status"],
            "capacity_risk": study_plan["capacity_risk"],
            "verifier_action": verifier_decision.get("recommended_action"),
            "agent_event_count": result["trace"]["agent_event_count"],
        },
    }


def run_evaluation(cases_path: Path = DEFAULT_CASES_PATH) -> dict[str, Any]:
    cases = load_eval_cases(cases_path)
    results = [evaluate_case(case) for case in cases]
    passed_count = sum(1 for result in results if result["passed"])

    return {
        "cases": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local Certa workflow eval cases.")
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Path to JSONL eval cases.",
    )
    args = parser.parse_args()

    summary = run_evaluation(args.cases)
    print(json.dumps(summary, indent=2))

    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
