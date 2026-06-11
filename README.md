# Enterprise Learning Agent

A synthetic multi-agent enterprise learning system built for the Microsoft Agents League Hackathon 2026 — Reasoning Agents Track, Challenge A: Enterprise Learning System.

## Problem

Organizations need a better way to manage internal certification programs across teams. Learners need role-based study plans, grounded learning resources, adaptive study schedules, readiness assessments, and manager-level insights.

## Solution

This project uses a multi-agent architecture to help learners and managers plan, track, assess, and improve certification readiness.

## Agents

- Learning Path Curator Agent
- Study Plan Generator Agent
- Engagement Agent
- Assessment Agent
- Manager Insights Agent
- Critic / Verifier Agent

## Microsoft Foundry Usage

The project uses Microsoft Foundry and Foundry IQ for grounded learning content and cited assessment generation.

## Synthetic Data Notice

All data and documents in this project are synthetic and created only for demonstration. No real employee data, customer data, confidential data, credentials, or PII are included.

## How to Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/ui/streamlit_app.py