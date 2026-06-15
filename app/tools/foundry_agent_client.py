import os
from dataclasses import asdict, dataclass
from typing import Any

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


@dataclass
class FoundryAgentCallResult:
    agent_name: str
    prompt: str
    output_text: str | None
    conversation_id: str | None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_project_client() -> AIProjectClient:
    load_dotenv()

    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")

    if not project_endpoint:
        raise ValueError("Missing AZURE_AI_PROJECT_ENDPOINT in .env")

    return AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )


def call_foundry_agent(agent_name: str, prompt: str) -> FoundryAgentCallResult:
    """
    Calls an existing Foundry prompt agent by name.

    This uses:
    - Azure AI Projects client
    - OpenAI-compatible responses API
    - agent_reference to target the specific Foundry agent
    """
    try:
        project_client = get_project_client()
        openai_client = project_client.get_openai_client()

        conversation = openai_client.conversations.create()

        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {
                    "name": agent_name,
                    "type": "agent_reference",
                }
            },
            input=prompt,
        )

        return FoundryAgentCallResult(
            agent_name=agent_name,
            prompt=prompt,
            output_text=response.output_text,
            conversation_id=conversation.id,
            error=None,
        )

    except Exception as exc:
        return FoundryAgentCallResult(
            agent_name=agent_name,
            prompt=prompt,
            output_text=None,
            conversation_id=None,
            error=str(exc),
        )