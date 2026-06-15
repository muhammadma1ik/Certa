from typing import Any
import json


AGENT_NAME = "verifier-agent"


def build_verifier_prompt(workflow_outputs: dict[str, Any]) -> str:
    serialized_outputs = json.dumps(workflow_outputs, indent=2, default=str)

    return f"""
Review the following multi-agent workflow output before it is shown to the learner or manager.

Check:
1. Are learning recommendations grounded in the approved knowledge base?
2. Are source references included where needed?
3. Are readiness decisions based on deterministic scoring rather than unsupported LLM judgment?
4. Is the study plan realistic based on workload context?
5. Are engagement recommendations supportive and non-punitive?
6. Are manager insights aggregate-only and privacy-safe?
7. Is there any real employee data, customer data, credentials, confidential information, or PII?
8. Should a human review be required before publishing?

Return JSON only with this structure:
{{
  "approved": true or false,
  "risk_level": "low" | "medium" | "high",
  "issues": [],
  "human_review_required": true or false,
  "recommended_action": "publish" | "revise" | "send_back_to_agent"
}}

Workflow outputs:
{serialized_outputs}
""".strip()