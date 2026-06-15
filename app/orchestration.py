import os
import time
from typing import Any

from dotenv import load_dotenv

from app.tools.data_loader import build_learner_context
from app.tools.scheduling_rules import generate_study_plan_from_context
from app.tools.scoring_rules import score_learner_from_context
from app.tools.foundry_agent_client import call_foundry_agent
from app.tools.deterministic_preview_outputs import build_deterministic_preview_agent_output
from app.tools.tracing import WorkflowTrace, parse_verifier_decision

from app.agents.curator import build_curator_prompt
from app.agents.planner import build_study_plan_prompt
from app.agents.engagement import build_engagement_prompt
from app.agents.assessment import build_assessment_prompt
from app.agents.manager_insights import build_manager_insights_prompt
from app.agents.verifier import build_verifier_prompt

def get_agent_names() -> dict[str, str]:
    load_dotenv()

    return {
        "curator": os.getenv("FOUNDRY_AGENT_CURATOR", "learning-path-curator-agent"),
        "planner": os.getenv("FOUNDRY_AGENT_PLANNER", "study-plan-generator-agent"),
        "engagement": os.getenv("FOUNDRY_AGENT_ENGAGEMENT", "engagement-agent"),
        "assessment": os.getenv("FOUNDRY_AGENT_ASSESSMENT", "assessment-agent"),
        "manager": os.getenv("FOUNDRY_AGENT_MANAGER", "manager-insights-agent"),
        "verifier": os.getenv("FOUNDRY_AGENT_VERIFIER", "verifier-agent"),
    }


def build_default_learner_request(learner_context: dict[str, Any]) -> str:
    """
    Build a sensible baseline learner request when the user has not typed one.
    """
    certification = learner_context["certification"]
    practice_history = learner_context["practice_history"]

    return (
        f"I want a practical study plan for {certification['id']} with extra help on "
        f"{practice_history['weakest_skill']}."
    )


def run_agent_or_preview(
    agent_name: str,
    prompt: str,
    live: bool,
    preview_output_text: str | None = None,
    tracer: WorkflowTrace | None = None,
    step_order: int = 0,
    verbose: bool = False,
) -> dict[str, Any]:
    """
    If live=False, returns a deterministic preview output plus the prompt.
    If live=True, calls the actual Foundry agent.

    Also records a trace event when tracer is provided.
    """
    if verbose:
        print(f"\nStarting agent: {agent_name}", flush=True)

    start_time = time.perf_counter()

    if not live:
        result = {
            "agent_name": agent_name,
            "mode": "deterministic_preview",
            "prompt": prompt,
            "output_text": preview_output_text,
            "conversation_id": None,
            "error": None,
        }

        duration_seconds = time.perf_counter() - start_time

        if verbose:
            print(f"Deterministic preview output prepared for: {agent_name}", flush=True)

    else:
        foundry_result = call_foundry_agent(
            agent_name=agent_name,
            prompt=prompt,
        )

        duration_seconds = time.perf_counter() - start_time

        result = {
            **foundry_result.to_dict(),
            "mode": "live_foundry",
        }

        if result["error"]:
            if verbose:
                print(f"Agent failed: {agent_name} after {duration_seconds:.1f}s", flush=True)
                print(f"Error: {result['error']}", flush=True)
        else:
            if verbose:
                print(f"Agent completed: {agent_name} in {duration_seconds:.1f}s", flush=True)

    if tracer is not None:
        tracer.record_agent_call(
            step_order=step_order,
            agent_name=agent_name,
            mode=result["mode"],
            prompt=prompt,
            output_text=result.get("output_text"),
            conversation_id=result.get("conversation_id"),
            error=result.get("error"),
            duration_seconds=duration_seconds,
        )

    return result

def build_agent_output_summary(agent_result: dict[str, Any]) -> dict[str, Any]:
    """
    Keeps only the fields needed by the verifier.
    """
    return {
        "agent_name": agent_result["agent_name"],
        "mode": agent_result["mode"],
        "output_text": agent_result.get("output_text"),
        "error": agent_result.get("error"),
    }


def run_enterprise_learning_workflow(
    learner_id: str,
    team: str | None = None,
    learner_request: str | None = None,
    live: bool = True,
    save_trace: bool = True,
    verbose: bool = False,
) -> dict[str, Any]:
    """
    Main orchestrator for the Enterprise Learning Agent system.

    Flow:
    1. Load learner context.
    2. Call Learning Path Curator Agent.
    3. Generate deterministic study plan constraints.
    4. Call Study Plan Generator Agent.
    5. Call Engagement Agent.
    6. Call Assessment Agent.
    7. Calculate deterministic readiness.
    8. Call Manager Insights Agent.
    9. Call Verifier Agent.
    10. Return complete workflow result.
    """
    agent_names = get_agent_names()
    workflow_start_time = time.perf_counter()
    workflow_mode = "live_foundry" if live else "deterministic_preview"
    learner_context = build_learner_context(learner_id)
    learner_request = (learner_request or "").strip() or build_default_learner_request(learner_context)

    if team is None:
        team = learner_context["employee"]["team"]

    tracer = WorkflowTrace(
        learner_id=learner_id,
        team=team,
        mode=workflow_mode,
    )

    deterministic_study_plan = generate_study_plan_from_context(learner_context)

    deterministic_readiness = score_learner_from_context(
        learner_context=learner_context,
        capacity_risk=deterministic_study_plan["capacity_risk"],
    )

    # 1. Learning Path Curator
    curator_prompt = build_curator_prompt(learner_context, learner_request)
    curator_result = run_agent_or_preview(
        agent_name=agent_names["curator"],
        prompt=curator_prompt,
        live=live,
        preview_output_text=build_deterministic_preview_agent_output(
            agent_key="curator",
            learner_context=learner_context,
            study_plan=deterministic_study_plan,
            readiness=deterministic_readiness,
            team=team,
            learner_request=learner_request,
        ),
        tracer=tracer,
        step_order=1,
        verbose=verbose,
    )

    # 2. Study Plan Generator
    planner_prompt = build_study_plan_prompt(learner_id, learner_request)
    planner_result = run_agent_or_preview(
        agent_name=agent_names["planner"],
        prompt=planner_prompt,
        live=live,
        preview_output_text=build_deterministic_preview_agent_output(
            agent_key="planner",
            learner_context=learner_context,
            study_plan=deterministic_study_plan,
            readiness=deterministic_readiness,
            team=team,
            learner_request=learner_request,
        ),
        tracer=tracer,
        step_order=2,
        verbose=verbose,
    )

    # 3. Engagement Agent
    engagement_prompt = build_engagement_prompt(learner_id, learner_request)
    engagement_result = run_agent_or_preview(
        agent_name=agent_names["engagement"],
        prompt=engagement_prompt,
        live=live,
        preview_output_text=build_deterministic_preview_agent_output(
            agent_key="engagement",
            learner_context=learner_context,
            study_plan=deterministic_study_plan,
            readiness=deterministic_readiness,
            team=team,
            learner_request=learner_request,
        ),
        tracer=tracer,
        step_order=3,
        verbose=verbose,
    )

    # 4. Assessment Agent
    assessment_prompt = build_assessment_prompt(learner_id, learner_request)
    assessment_result = run_agent_or_preview(
        agent_name=agent_names["assessment"],
        prompt=assessment_prompt,
        live=live,
        preview_output_text=build_deterministic_preview_agent_output(
            agent_key="assessment",
            learner_context=learner_context,
            study_plan=deterministic_study_plan,
            readiness=deterministic_readiness,
            team=team,
            learner_request=learner_request,
        ),
        tracer=tracer,
        step_order=4,
        verbose=verbose,
    )

    # 5. Manager Insights Agent
    manager_prompt = build_manager_insights_prompt(team)
    manager_result = run_agent_or_preview(
        agent_name=agent_names["manager"],
        prompt=manager_prompt,
        live=live,
        preview_output_text=build_deterministic_preview_agent_output(
            agent_key="manager",
            learner_context=learner_context,
            study_plan=deterministic_study_plan,
            readiness=deterministic_readiness,
            team=team,
            learner_request=learner_request,
        ),
        tracer=tracer,
        step_order=5,
        verbose=verbose,
    )

    # 6. Verifier Agent
    verifier_input = {
        "learner_request": learner_request,
        "curator": build_agent_output_summary(curator_result),
        "study_plan": {
            "deterministic_constraints": deterministic_study_plan,
            "foundry_agent_output": build_agent_output_summary(planner_result),
        },
        "engagement": build_agent_output_summary(engagement_result),
        "assessment": {
            "deterministic_readiness": deterministic_readiness,
            "foundry_agent_output": build_agent_output_summary(assessment_result),
        },
        "manager_insights": build_agent_output_summary(manager_result),
    }

    verifier_prompt = build_verifier_prompt(verifier_input)
    verifier_result = run_agent_or_preview(
        agent_name=agent_names["verifier"],
        prompt=verifier_prompt,
        live=live,
        preview_output_text=build_deterministic_preview_agent_output(
            agent_key="verifier",
            learner_context=learner_context,
            study_plan=deterministic_study_plan,
            readiness=deterministic_readiness,
            team=team,
            learner_request=learner_request,
        ),
        tracer=tracer,
        step_order=6,
        verbose=verbose,
    )

    verifier_decision = parse_verifier_decision(verifier_result.get("output_text"))
    total_duration_seconds = time.perf_counter() - workflow_start_time
    tracer.finalize(
        total_duration_seconds=total_duration_seconds,
        verifier_decision=verifier_decision,
    )

    trace_path = str(tracer.save()) if save_trace else None

    return {
        "workflow_name": "enterprise_learning_multi_agent_workflow",
        "mode": workflow_mode,
        "learner_id": learner_id,
        "learner_request": learner_request,
        "team": team,
        "target_certification": learner_context["certification"]["id"],
        "foundry_agents": agent_names,
        "deterministic_outputs": {
            "study_plan_constraints": deterministic_study_plan,
            "readiness": deterministic_readiness,
        },
        "agent_outputs": {
            "curator": curator_result,
            "study_plan_generator": planner_result,
            "engagement": engagement_result,
            "assessment": assessment_result,
            "manager_insights": manager_result,
            "verifier": verifier_result,
        },
        "verifier_decision": verifier_decision,
        "trace": tracer.to_dict(),
        "trace_path": trace_path,
    }
