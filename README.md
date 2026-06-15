# Certa - Enterprise Learning Agent

Certa is a multi-agent enterprise learning demo for the Microsoft Agents League Reasoning Agents track, Challenge A. It helps a fictional organization plan internal certification readiness across learners and teams using Microsoft Foundry prompt agents, Foundry IQ grounding, deterministic scheduling rules, deterministic readiness scoring, synthetic work signals, and privacy-safe manager insight.

## What It Demonstrates

- Role-to-certification mapping for synthetic enterprise learners.
- Capacity-aware study planning using meeting load, focus hours, workload level, and missed learning sessions.
- Foundry IQ-grounded learning path and assessment prompts for approved synthetic documents.
- Deterministic readiness scoring so pass, loop-back, and next-step decisions are explainable.
- Privacy-safe manager insight using aggregate team metrics only.
- Verifier agent review for grounding, citation, safety, privacy, and human-review decisions.
- Local trace JSON for observability and a lightweight evaluation harness for reliability.

## Agent Workflow

1. `learning-path-curator-agent` recommends role-aligned learning paths from the approved Foundry IQ knowledge base.
2. `study-plan-generator-agent` turns deterministic scheduling constraints into a practical weekly study plan.
3. `engagement-agent` creates supportive reminders using synthetic Work IQ-style work-context signals.
4. `assessment-agent` generates grounded practice-question guidance and uses deterministic readiness results.
5. `manager-insights-agent` summarizes aggregate team readiness, risk, and skill trends without exposing individual records.
6. `verifier-agent` checks grounding, citations, privacy, safety, and whether human review is required.

The Python orchestrator owns the workflow. Deterministic code handles data loading, study-hour allocation, readiness scoring, aggregate analytics, privacy checks, tracing, and the fallback preview path. Foundry agents handle grounded reasoning, natural-language explanation, and review in the default live mode.

## Learner Access

Learners access the agents through the Streamlit app. The `Learner request` field captures the topics or goals they want to study, then the app runs the live multi-agent workflow and shows the resulting plan, engagement strategy, assessment guidance, and readiness decision. The baseline flow asks for learner-provided topics, but it does not require a separate multi-turn chat interface for each agent.

## Microsoft Foundry And IQ Layer

The demo uses Microsoft Foundry and Foundry IQ as the enterprise grounding layer.

Configured Foundry setup notes are in `docs/foundry_setup_notes.md`:

- Foundry project: `Certa`
- Model deployment: `gpt-4.1-mini`
- Foundry IQ connection/resource: `certa-srch`
- Knowledge source: `approved-learning-docs`
- Knowledge base: `enterprise-learning-kb`
- Uploaded source folder: `data/approved_docs/`

The Streamlit app has two execution modes:

- Live Microsoft Foundry agents: the default path. It calls the six Foundry prompt agents using `AZURE_AI_PROJECT_ENDPOINT` and default Azure credentials.
- Deterministic preview fallback: no Azure call. It uses the same synthetic data, prompts, rules, workflow shape, and approved-source references for offline verification only.

## Synthetic Data

All data is synthetic and for demonstration only. The project does not include real employee data, customer data, credentials, confidential records, or PII.

Synthetic structured data:

- `data/synthetic/employees.csv`
- `data/synthetic/work_signals.csv`
- `data/synthetic/practice_history.csv`
- `data/synthetic/team_progress.csv`
- `data/synthetic/certifications.json`

Approved synthetic knowledge documents:

- `data/approved_docs/engineering_certification_guide.md`
- `data/approved_docs/cloud_engineer_az204_guide.md`
- `data/approved_docs/devops_az400_guide.md`
- `data/approved_docs/security_sc900_guide.md`
- `data/approved_docs/data_engineer_dp203_guide.md`
- `data/approved_docs/internal_learning_policy.md`
- `data/approved_docs/assessment_rules.md`
- `data/approved_docs/workload_learning_report.md`

## Project Structure

```text
app/
  agents/                  Prompt builders for the six specialist agents
  tools/                   Data, scoring, scheduling, tracing, privacy, eval helpers
  ui/streamlit_app.py       Streamlit demo interface
  orchestration.py          End-to-end workflow coordinator
data/
  approved_docs/            Synthetic Foundry IQ source documents
  synthetic/                Synthetic CSV and JSON business data
docs/
  foundry_setup_notes.md    Foundry IQ and agent setup notes
evals/
  eval_config.json          Local eval definition
  test_cases.jsonl          Local workflow smoke eval cases
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Required for live Foundry mode:

```text
AZURE_AI_PROJECT_ENDPOINT=<your-foundry-project-endpoint>
AZURE_AI_MODEL_DEPLOYMENT=gpt-4.1-mini
```

Optional agent-name overrides:

```text
FOUNDRY_AGENT_CURATOR=learning-path-curator-agent
FOUNDRY_AGENT_PLANNER=study-plan-generator-agent
FOUNDRY_AGENT_ENGAGEMENT=engagement-agent
FOUNDRY_AGENT_ASSESSMENT=assessment-agent
FOUNDRY_AGENT_MANAGER=manager-insights-agent
FOUNDRY_AGENT_VERIFIER=verifier-agent
```

Authenticate for live mode with an Azure identity that can access the Foundry project. The deterministic preview fallback does not require Azure authentication.

## Run The App

```bash
streamlit run app/ui/streamlit_app.py
```

Recommended flow:

1. Keep `Execution mode` set to `Live Microsoft Foundry agents`.
2. Select learner `L-1001` and team `TEAM-A`.
3. Enter or adjust the learner request to reflect the topics or goals the learner wants to study.
4. Run the live workflow and review the overview, learner journey, agent outputs, manager insight, safety trace, and data/source tabs.
5. Switch to another learner such as `L-1004` or `L-1005` to show the ready and next-step paths.
6. Use deterministic preview fallback only if Azure authentication, quota, or network conditions prevent live execution during recording.

## Validate And Test

Validate synthetic files and document notices:

```bash
python -m app.tools.validate_data
```

Run unit and workflow tests:

```bash
python -m pytest -q
```

Run the local evaluation harness:

```bash
python -m app.tools.evaluation_harness
```

Check Foundry configuration without printing full endpoint values:

```bash
python -m app.tools.check_foundry_config
```

## Observability

Every workflow run creates a local trace object with:

- workflow run ID
- learner ID and team
- mode
- per-agent status
- prompt and output lengths
- duration
- verifier decision

When `save_trace=True`, traces are written under `data/traces/`. That directory is ignored by Git to avoid committing generated run logs.
