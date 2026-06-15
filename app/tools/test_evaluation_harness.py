from app.tools.evaluation_harness import run_evaluation


def test_local_evaluation_cases_pass() -> None:
    summary = run_evaluation()

    assert summary["cases"] == 3
    assert summary["failed"] == 0
