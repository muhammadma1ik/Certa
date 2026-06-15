import json
import sys
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APPROVED_DOCS_DIR = PROJECT_ROOT / "data" / "approved_docs"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.agents.manager_insights import build_team_aggregate_context
from app.orchestration import build_default_learner_request, run_enterprise_learning_workflow
from app.tools.data_loader import (
    build_learner_context,
    list_available_learners,
    list_available_teams,
)


LIVE_MODE_LABEL = "Live Microsoft Foundry agents"
PREVIEW_MODE_LABEL = "Deterministic preview fallback"


st.set_page_config(
    page_title="Certa - Enterprise Learning Agent",
    page_icon="C",
    layout="wide",
)


def apply_theme() -> None:
    """Apply a stable light presentation even when the browser uses dark mode."""
    st.markdown(
        """
        <style>
        :root {
            --certa-ink: #172033;
            --certa-muted: #5d6978;
            --certa-line: #d9e2ec;
            --certa-surface: #ffffff;
            --certa-soft: #f5f8fb;
            --certa-blue: #2357c6;
            --certa-teal: #007c89;
            --certa-green: #1f7a4d;
            --certa-amber: #a15c00;
            --certa-red: #a63a3a;
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: #f3f6fb;
            color: var(--certa-ink);
        }

        [data-testid="stHeader"] {
            background: rgba(243, 246, 251, 0.92);
        }

        .block-container {
            padding-top: 1.35rem;
            padding-bottom: 2.25rem;
            max-width: 1420px;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--certa-line);
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {
            color: var(--certa-ink) !important;
        }

        h1, h2, h3, h4 {
            color: var(--certa-ink);
            letter-spacing: 0;
        }

        [data-testid="stMarkdownContainer"] a[href^="#"] {
            display: none;
        }

        .certa-hero {
            border: 1px solid var(--certa-line);
            border-radius: 8px;
            background: #ffffff;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(23, 32, 51, 0.04);
        }

        .certa-eyebrow {
            color: var(--certa-teal);
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }

        .certa-title {
            color: var(--certa-ink);
            font-size: 2rem;
            font-weight: 780;
            line-height: 1.15;
            margin-bottom: 0.3rem;
        }

        .certa-subtitle {
            color: var(--certa-muted);
            font-size: 1rem;
            max-width: 1040px;
        }

        .certa-card {
            border: 1px solid var(--certa-line);
            border-radius: 8px;
            background: var(--certa-surface);
            padding: 0.9rem 1rem;
            min-height: 100%;
            box-shadow: 0 1px 2px rgba(23, 32, 51, 0.04);
        }

        .certa-card-title {
            color: var(--certa-muted);
            font-size: 0.76rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.32rem;
        }

        .certa-card-value {
            color: var(--certa-ink);
            font-size: 1.25rem;
            font-weight: 760;
            line-height: 1.2;
            overflow-wrap: anywhere;
        }

        .certa-card-caption {
            color: var(--certa-muted);
            font-size: 0.85rem;
            line-height: 1.35;
            margin-top: 0.32rem;
        }

        .certa-pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.18rem 0.55rem;
            font-size: 0.77rem;
            font-weight: 760;
            border: 1px solid var(--certa-line);
            background: var(--certa-soft);
            color: var(--certa-ink);
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            white-space: nowrap;
        }

        .certa-pill.green {
            color: var(--certa-green);
            border-color: rgba(31, 122, 77, 0.24);
            background: rgba(31, 122, 77, 0.08);
        }

        .certa-pill.amber {
            color: var(--certa-amber);
            border-color: rgba(161, 92, 0, 0.24);
            background: rgba(161, 92, 0, 0.08);
        }

        .certa-pill.red {
            color: var(--certa-red);
            border-color: rgba(166, 58, 58, 0.24);
            background: rgba(166, 58, 58, 0.08);
        }

        .certa-small {
            color: var(--certa-muted);
            font-size: 0.88rem;
            line-height: 1.5;
        }

        .certa-bar-row {
            display: grid;
            grid-template-columns: minmax(140px, 1fr) 54px;
            gap: 0.8rem;
            align-items: center;
            margin: 0.42rem 0;
        }

        .certa-bar-label {
            color: var(--certa-ink);
            font-size: 0.86rem;
            font-weight: 680;
            overflow-wrap: anywhere;
        }

        .certa-bar-value {
            color: var(--certa-muted);
            font-size: 0.84rem;
            text-align: right;
        }

        .certa-bar-track {
            grid-column: 1 / 3;
            height: 8px;
            border-radius: 99px;
            background: #e7edf5;
            overflow: hidden;
        }

        .certa-bar-fill {
            height: 8px;
            border-radius: 99px;
            background: linear-gradient(90deg, var(--certa-blue), var(--certa-teal));
        }

        div[data-testid="stMetric"] {
            border: 1px solid var(--certa-line);
            border-radius: 8px;
            padding: 0.7rem 0.85rem;
            background: #ffffff;
            color: var(--certa-ink);
        }

        div[data-testid="stMetric"] * {
            color: var(--certa-ink) !important;
        }

        div[data-testid="stButton"] button[kind="primary"] {
            background: var(--certa-blue);
            border: 1px solid var(--certa-blue);
            color: #ffffff;
            border-radius: 8px;
            font-weight: 760;
        }

        div[data-testid="stButton"] button[kind="primary"] p,
        div[data-testid="stButton"] button[kind="primary"] span {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def risk_tone(value: str | None) -> str:
    if value in {"Ready", "Low", "publish", "low", "success", "Live"}:
        return "green"
    if value in {"Almost Ready", "Medium", "revise", "medium", "Fallback"}:
        return "amber"
    if value in {"Needs More Preparation", "High", "send_back_to_agent", "high", "failed"}:
        return "red"
    return ""


def mode_label(mode: str) -> str:
    if mode == "live_foundry":
        return "Live Microsoft Foundry"
    if mode == "deterministic_preview":
        return "Deterministic Preview"
    return mode.replace("_", " ").title()


def render_pill(label: str, tone: str = "") -> None:
    st.markdown(
        f'<span class="certa-pill {tone}">{escape(str(label))}</span>',
        unsafe_allow_html=True,
    )


def render_card(title: str, value: Any, caption: str | None = None) -> None:
    caption_markup = ""

    if caption:
        caption_markup = f'<div class="certa-card-caption">{escape(str(caption))}</div>'

    st.markdown(
        f"""
        <div class="certa-card">
            <div class="certa-card-title">{escape(str(title))}</div>
            <div class="certa-card-value">{escape(str(value))}</div>
            {caption_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bar_list(rows: list[dict[str, Any]], label_key: str, value_key: str) -> None:
    max_value = max([float(row[value_key]) for row in rows] or [1.0])

    if max_value <= 0:
        max_value = 1.0

    html_rows = []

    for row in rows:
        value = float(row[value_key])
        width = round((value / max_value) * 100, 1)
        html_rows.append(
            f"""
            <div class="certa-bar-row">
                <div class="certa-bar-label">{escape(str(row[label_key]))}</div>
                <div class="certa-bar-value">{escape(str(row[value_key]))}</div>
                <div class="certa-bar-track">
                    <div class="certa-bar-fill" style="width:{width}%"></div>
                </div>
            </div>
            """
        )

    st.markdown("".join(html_rows), unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        """
        <div class="certa-hero">
            <div class="certa-eyebrow">Microsoft Agents League Challenge A - Reasoning Agents</div>
            <div class="certa-title">Certa Enterprise Learning Agent</div>
            <div class="certa-subtitle">
                Live Microsoft Foundry multi-agent workflow for certification planning, grounded practice,
                workload-aware engagement, deterministic readiness scoring, and privacy-safe manager insight.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_selected_context(learner_context: dict[str, Any]) -> None:
    employee = learner_context["employee"]
    work_signal = learner_context["work_signal"]
    certification = learner_context["certification"]
    practice_history = learner_context["practice_history"]

    st.markdown("#### Selected learner")
    render_pill(employee["role"])
    render_pill(certification["id"])
    render_pill(f"{work_signal['workload_level']} workload", risk_tone(work_signal["workload_level"]))
    st.markdown(
        f"""
        <div class="certa-small">
        Team: <b>{escape(employee["team"])}</b><br>
        Experience: <b>{escape(employee["experience_level"])}</b><br>
        Focus hours/week: <b>{escape(str(work_signal["focus_hours_per_week"]))}</b><br>
        Meeting hours/week: <b>{escape(str(work_signal["meeting_hours_per_week"]))}</b><br>
        Weakest skill: <b>{escape(practice_history["weakest_skill"])}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rubric_evidence() -> None:
    st.markdown("### What this shows")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        render_card("Accuracy", "Foundry IQ", "Approved synthetic docs and citations")
    with col2:
        render_card("Reasoning", "6 agents", "Specialized workflow with verifier")
    with col3:
        render_card("Reliability", "Rules + evals", "Deterministic scoring and tests")
    with col4:
        render_card("Safety", "Privacy-safe", "Aggregate manager view only")
    with col5:
        render_card("UX", "Polished UI", "Live workflow with trace evidence")


def render_architecture_summary() -> None:
    st.markdown("### Architecture at a glance")
    rows = [
        ("1", "Curator", "Foundry IQ retrieves approved certification guidance"),
        ("2", "Planner", "Python scheduling rules constrain the study plan"),
        ("3", "Engagement", "Synthetic work signals shape reminders and pacing"),
        ("4", "Assessment", "Foundry IQ grounds questions; Python scores readiness"),
        ("5", "Manager Insights", "Aggregate analytics avoid exposing learner-level detail"),
        ("6", "Verifier", "Final grounding, privacy, and human-review gate"),
    ]
    st.dataframe(
        pd.DataFrame(rows, columns=["Step", "Agent", "What this step does"]),
        width="stretch",
        hide_index=True,
    )


def render_workflow_overview(result: dict[str, Any]) -> None:
    readiness = result["deterministic_outputs"]["readiness"]
    study_plan = result["deterministic_outputs"]["study_plan_constraints"]
    verifier_decision = result["verifier_decision"]
    failed_agents = [
        name
        for name, output in result["agent_outputs"].items()
        if output.get("error")
    ]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_card("Execution", mode_label(result["mode"]), "Six-agent Foundry path" if result["mode"] == "live_foundry" else "Offline fallback path")
    with col2:
        render_card("Readiness", readiness["readiness_status"], f"Score {readiness['readiness_score']} / 100")
    with col3:
        render_card("Capacity Risk", study_plan["capacity_risk"], f"{study_plan['weekly_study_capacity']} study hrs/week")
    with col4:
        render_card("Verifier", verifier_decision.get("recommended_action", "unknown"), verifier_decision.get("risk_level", "unknown"))

    if failed_agents:
        st.error(f"Live agent errors detected: {', '.join(failed_agents)}")
    elif result["mode"] == "live_foundry":
        st.success("Live Microsoft Foundry workflow completed successfully across all six agents.")
    else:
        st.warning("Deterministic preview was used. Switch to live mode for the submitted run.")

    if result.get("learner_request"):
        st.info(f"Learner request: {result['learner_request']}")

    render_architecture_summary()


def render_study_plan(study_plan: dict[str, Any]) -> None:
    st.markdown("### Learner journey")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_card("Weekly Capacity", f"{study_plan['weekly_study_capacity']} hrs", "Calculated from synthetic work signals")
    with col2:
        render_card("Duration", f"{study_plan['estimated_weeks']} weeks", "Total hours split by capacity")
    with col3:
        render_card("Cadence", study_plan["recommended_session_frequency"], "Reminder rhythm")
    with col4:
        render_card("Weakest Skill", study_plan["current_weakest_skill"], "Prioritized first")

    st.info(study_plan["planning_reason"])
    st.markdown(f"**Recommended study slot:** {study_plan['recommended_study_slot']}")

    weekly_plan = pd.DataFrame(study_plan["weekly_plan"]).rename(
        columns={
            "week": "Week",
            "planned_hours": "Planned hours",
            "focus_skill": "Focus skill",
            "checkpoint": "Checkpoint",
        }
    )
    st.dataframe(weekly_plan, width="stretch", hide_index=True)


def render_readiness(readiness: dict[str, Any]) -> None:
    st.markdown("### Readiness decision")
    score = float(readiness["readiness_score"])
    st.progress(min(max(score / 100, 0), 1), text=f"Readiness score: {score} / 100")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_card("Threshold", readiness["readiness_threshold"])
    with col2:
        render_card("Gap", readiness["readiness_gap"])
    with col3:
        render_card("Risk", readiness["readiness_risk"])
    with col4:
        render_card("Loop-back", "Yes" if readiness["loop_back_required"] else "No")

    st.info(readiness["explanation"])
    st.warning(readiness["recommended_next_action"])

    details = {
        "Practice score average": readiness["practice_score_avg"],
        "Hours studied": readiness["hours_studied"],
        "Recommended hours": readiness["recommended_hours"],
        "Hours completion ratio": readiness["hours_completion_ratio"],
        "Weakest skill": readiness["weakest_skill"],
        "Next step": readiness["next_step"],
    }
    st.dataframe(
        pd.DataFrame(
            [{"Metric": key, "Value": "" if value is None else str(value)} for key, value in details.items()]
        ),
        width="stretch",
        hide_index=True,
    )


def render_agent_output(title: str, agent_result: dict[str, Any], expanded: bool = False) -> None:
    mode = agent_result.get("mode", "unknown")
    error = agent_result.get("error")
    output_text = agent_result.get("output_text")
    prompt = agent_result.get("prompt")

    with st.expander(title, expanded=expanded):
        render_pill(mode_label(mode), risk_tone("Live" if mode == "live_foundry" else "Fallback"))

        if error:
            st.error(error)
        elif output_text:
            st.markdown(output_text)
        else:
            st.info("No output was returned. Check Foundry configuration or use deterministic preview fallback.")

        if prompt:
            with st.expander("Prompt sent to this agent"):
                st.code(prompt, language="text")


def render_manager_view(team: str) -> None:
    aggregate_context = build_team_aggregate_context(team)
    readiness_counts = aggregate_context["readiness_counts"]
    readiness_order = ["Ready", "Almost Ready", "Not Ready", "Unknown"]
    readiness_rows = [
        {"Band": band, "Learners": int(readiness_counts.get(band, 0))}
        for band in readiness_order
        if int(readiness_counts.get(band, 0)) > 0
    ]
    skill_rows = [
        {"Skill": skill, "Count": int(count)}
        for skill, count in aggregate_context["top_weak_skills"].items()
    ]

    top_left, top_right = st.columns(2)
    with top_left:
        render_card("Team", team)
    with top_right:
        render_card("Learners", aggregate_context["total_learners"])

    bottom_left, bottom_right = st.columns(2)
    with bottom_left:
        render_card("Average Practice", f"{aggregate_context['average_practice_score']}%")
    with bottom_right:
        render_card("Capacity Risk", aggregate_context["capacity_risk"])

    left, right = st.columns(2)

    with left:
        st.markdown("#### Readiness bands")
        render_bar_list(readiness_rows, "Band", "Learners")

    with right:
        st.markdown("#### Weak skill trends")
        if skill_rows:
            render_bar_list(skill_rows, "Skill", "Count")
        else:
            st.info("No weak skill trend data is available for this team.")

    breakdown = pd.DataFrame(aggregate_context["certification_breakdown"]).rename(
        columns={
            "certification": "Certification",
            "total_learners": "Learners",
            "ready_count": "Ready",
            "almost_ready_count": "Almost Ready",
            "not_ready_count": "Not Ready",
            "average_practice_score": "Avg Practice",
            "average_hours_studied": "Avg Hours",
            "capacity_risk": "Capacity Risk",
        }
    )
    st.markdown("#### Certification breakdown")
    st.dataframe(breakdown, width="stretch", hide_index=True)
    st.caption(aggregate_context["privacy_note"])


def render_verifier_and_trace(result: dict[str, Any]) -> None:
    verifier_decision = result["verifier_decision"]
    trace = result["trace"]
    trace_file = Path(result["trace_path"]).name if result.get("trace_path") else "not saved"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_card("Approved", verifier_decision.get("approved"))
    with col2:
        render_card("Risk", verifier_decision.get("risk_level", "unknown"))
    with col3:
        render_card("Human Review", verifier_decision.get("human_review_required"))
    with col4:
        render_card("Trace Events", trace["agent_event_count"], trace_file)

    st.markdown("#### Verifier decision")
    st.code(json.dumps(verifier_decision, indent=2), language="json")

    trace_events = pd.DataFrame(trace["events"])
    st.markdown("#### Workflow trace")
    st.dataframe(trace_events, width="stretch", hide_index=True)


def render_sources() -> None:
    st.markdown("### Synthetic data and approved sources")
    st.info(
        "All learner, work-signal, practice, team, and approved-source data is synthetic. "
        "The demo excludes real employee data, customer data, credentials, and PII."
    )

    docs = sorted(path.name for path in APPROVED_DOCS_DIR.glob("*.md"))
    col1, col2 = st.columns([0.55, 0.45])

    with col1:
        st.dataframe(
            pd.DataFrame({"Approved Foundry IQ source document": docs}),
            width="stretch",
            hide_index=True,
        )

    with col2:
        rows = [
            {"Layer": "Foundry IQ", "Evidence": "Approved markdown corpus and source references"},
            {"Layer": "Work context", "Evidence": "Synthetic meeting/focus/workload signals"},
            {"Layer": "Fabric-style semantics", "Evidence": "Certification, role, skill, threshold, next-step model"},
            {"Layer": "Evaluation", "Evidence": "Local eval JSONL and pytest suite"},
        ]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_initial_overview(selected_team: str) -> None:
    render_rubric_evidence()

    left, right = st.columns([0.52, 0.48])

    with left:
        st.markdown("### Learning workflow")
        st.write(
            "Start with the live Foundry run. The workflow calls six prompt agents, uses "
            "Foundry IQ-grounded instructions for approved documents, applies deterministic "
            "business rules for scheduling and scoring, and finishes with verifier review."
        )
        render_architecture_summary()

    with right:
        st.markdown("### Manager impact preview")
        render_manager_view(selected_team)


def main() -> None:
    apply_theme()
    render_header()

    learners = list_available_learners()
    teams = list_available_teams()

    with st.sidebar:
        st.header("Run Certa")

        selected_learner = st.selectbox("Learner", options=learners, index=0)
        learner_context = build_learner_context(selected_learner)
        default_team = learner_context["employee"]["team"]
        default_team_index = teams.index(default_team) if default_team in teams else 0

        selected_team = st.selectbox(
            "Manager team view",
            options=teams,
            index=default_team_index,
        )

        default_learner_request = build_default_learner_request(learner_context)
        learner_request = st.text_area(
            "Learner request",
            value=default_learner_request,
            height=110,
            key=f"learner_request_{selected_learner}",
            help="Topic or goal the learner wants the agents to plan around.",
        )

        run_mode = st.radio(
            "Execution mode",
            options=[LIVE_MODE_LABEL, PREVIEW_MODE_LABEL],
            index=0,
            help="Live mode calls your Microsoft Foundry agents. Preview is only for offline fallback.",
        )
        live_mode = run_mode == LIVE_MODE_LABEL

        if live_mode:
            st.success("Default path: calls all six Microsoft Foundry prompt agents.")
            button_label = "Run live workflow"
        else:
            st.warning("Fallback path: skips Azure calls but keeps the same data, prompts, rules, and workflow.")
            button_label = "Run deterministic preview"

        run_button = st.button(button_label, type="primary", width="stretch")

        st.divider()
        render_selected_context(learner_context)

    if run_button:
        spinner_text = "Calling six live Microsoft Foundry agents..." if live_mode else "Running deterministic preview..."

        with st.spinner(spinner_text):
            st.session_state["workflow_result"] = run_enterprise_learning_workflow(
                learner_id=selected_learner,
                team=selected_team,
                learner_request=learner_request,
                live=live_mode,
            )

    result = st.session_state.get("workflow_result")

    if result is None:
        render_initial_overview(selected_team)
        return

    tabs = st.tabs(
        [
            "Overview",
            "Learner Journey",
            "Agent Outputs",
            "Manager Insight",
            "Safety & Trace",
            "Data & Sources",
            "Raw JSON",
        ]
    )

    with tabs[0]:
        render_workflow_overview(result)

    with tabs[1]:
        render_study_plan(result["deterministic_outputs"]["study_plan_constraints"])
        render_readiness(result["deterministic_outputs"]["readiness"])

    with tabs[2]:
        render_agent_output("1. Learning Path Curator - Foundry IQ grounding", result["agent_outputs"]["curator"], expanded=True)
        render_agent_output("2. Study Plan Generator - capacity-aware planning", result["agent_outputs"]["study_plan_generator"])
        render_agent_output("3. Engagement Agent - work-context reminders", result["agent_outputs"]["engagement"])
        render_agent_output("4. Assessment Agent - grounded practice and readiness", result["agent_outputs"]["assessment"])
        render_agent_output("5. Manager Insights Agent - aggregate team view", result["agent_outputs"]["manager_insights"])
        render_agent_output("6. Verifier Agent - safety and grounding gate", result["agent_outputs"]["verifier"])

    with tabs[3]:
        render_manager_view(result["team"])
        st.divider()
        st.markdown("### Manager agent output")
        st.markdown(result["agent_outputs"]["manager_insights"].get("output_text") or "")

    with tabs[4]:
        render_verifier_and_trace(result)

    with tabs[5]:
        render_sources()

    with tabs[6]:
        st.json(result)


if __name__ == "__main__":
    main()
