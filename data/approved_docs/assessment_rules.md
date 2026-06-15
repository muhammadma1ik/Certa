# Assessment Rules — Synthetic

> Synthetic content notice: This document is fictional demo content created for the Microsoft Agents League Hackathon 2026. It does not contain real employee data, customer data, credentials, confidential information, or PII.

## Assessment Purpose

The Assessment Agent evaluates whether a learner appears ready for a certification based on practice performance, hours studied, skill coverage, and grounded practice questions.

## Question Generation Rules

Assessment questions should:
- Be based on approved learning documents
- Include the source used to create the question
- Focus on the learner's target certification
- Include scenario-style reasoning where possible
- Avoid unsupported facts
- Avoid copied real exam questions or exam dump-style content

## Readiness Thresholds

Recommended readiness thresholds:
- AZ-204: 75%
- AZ-400: 78%
- SC-900: 72%
- DP-203: 76%

## Readiness Labels

Ready:
- Learner meets or exceeds the threshold
- Learner has covered all core skills
- Learner has enough study hours compared to recommendation

Almost Ready:
- Learner is within 10 points of the threshold
- Learner has some weak areas but is progressing

Needs More Preparation:
- Learner is more than 10 points below threshold
- Learner has significant skill gaps
- Learner has insufficient study hours

## Loop-Back Rule

If a learner is not ready, the system should return them to the study planning workflow with extra focus on weak skill areas.