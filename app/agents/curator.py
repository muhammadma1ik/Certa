from typing import Any


AGENT_NAME = "learning-path-curator-agent"


def build_curator_prompt(learner_context: dict[str, Any], learner_request: str | None = None) -> str:
    employee = learner_context["employee"]
    certification = learner_context["certification"]
    learner_request = learner_request or "No explicit learner request was provided."

    return f"""
A learner wants help preparing for a certification.

Learner context:
- Role: {employee["role"]}
- Experience level: {employee["experience_level"]}
- Team: {employee["team"]}
- Target certification: {certification["id"]} ({certification["name"]})

Learner request:
{learner_request}

Task:
Recommend a role-aligned learning path using the learner request, role, target certification, and only the approved Foundry IQ knowledge base.

Include:
1. Role
2. Target certification
3. Learner-requested topics mapped to recommended skill areas
4. Suggested study sequence
5. Why this path fits the learner's role
6. Source references

Rules:
- Use only the approved knowledge base.
- Do not invent certification requirements.
- If the knowledge base does not contain enough information, say:
  "I don't know based on the approved knowledge base."
- Include source references.
""".strip()
