import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
TRACE_DIR = BASE_DIR / "data" / "traces"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_workflow_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    short_id = uuid.uuid4().hex[:8]
    return f"run-{timestamp}-{short_id}"


def safe_text_length(value: str | None) -> int:
    if not value:
        return 0

    return len(value)


def parse_verifier_decision(output_text: str | None) -> dict[str, Any]:
    """
    Tries to parse verifier JSON.

    If parsing fails, returns a safe fallback so the UI can still display something.
    """
    if not output_text:
        return {
            "approved": None,
            "risk_level": "unknown",
            "issues": [],
            "human_review_required": None,
            "recommended_action": "unknown",
            "parse_error": "No verifier output text.",
        }

    try:
        return json.loads(output_text)
    except json.JSONDecodeError as error:
        return {
            "approved": None,
            "risk_level": "unknown",
            "issues": ["Verifier output was not valid JSON."],
            "human_review_required": True,
            "recommended_action": "review",
            "parse_error": str(error),
            "raw_output": output_text,
        }


class WorkflowTrace:
    """
    Lightweight local workflow trace recorder.

    This records workflow-level observability for the Python orchestrator.
    It does not replace Foundry portal traces; it complements them.
    """

    def __init__(
        self,
        learner_id: str,
        team: str,
        mode: str,
    ) -> None:
        self.workflow_run_id = generate_workflow_run_id()
        self.learner_id = learner_id
        self.team = team
        self.mode = mode
        self.started_at = utc_now_iso()
        self.ended_at: str | None = None
        self.total_duration_seconds: float | None = None
        self.events: list[dict[str, Any]] = []
        self.verifier_decision: dict[str, Any] | None = None

    def record_agent_call(
        self,
        step_order: int,
        agent_name: str,
        mode: str,
        prompt: str,
        output_text: str | None,
        conversation_id: str | None,
        error: str | None,
        duration_seconds: float,
    ) -> None:
        status = "failed" if error else "success"

        self.events.append(
            {
                "step_order": step_order,
                "agent_name": agent_name,
                "mode": mode,
                "status": status,
                "duration_seconds": round(duration_seconds, 2),
                "prompt_length": safe_text_length(prompt),
                "output_length": safe_text_length(output_text),
                "conversation_id": conversation_id,
                "error": error,
                "recorded_at": utc_now_iso(),
            }
        )

    def finalize(
        self,
        total_duration_seconds: float,
        verifier_decision: dict[str, Any] | None = None,
    ) -> None:
        self.ended_at = utc_now_iso()
        self.total_duration_seconds = round(total_duration_seconds, 2)
        self.verifier_decision = verifier_decision

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_run_id": self.workflow_run_id,
            "learner_id": self.learner_id,
            "team": self.team,
            "mode": self.mode,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "total_duration_seconds": self.total_duration_seconds,
            "agent_event_count": len(self.events),
            "events": self.events,
            "verifier_decision": self.verifier_decision,
        }

    def save(self) -> Path:
        TRACE_DIR.mkdir(parents=True, exist_ok=True)

        file_path = TRACE_DIR / f"{self.workflow_run_id}.json"

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2, default=str)

        return file_path


class Timer:
    """
    Simple elapsed-time helper.
    """

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        self.end = time.perf_counter()
        self.duration_seconds = self.end - self.start