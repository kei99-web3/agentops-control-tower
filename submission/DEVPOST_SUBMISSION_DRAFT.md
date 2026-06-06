# Devpost Submission Draft

## Project Name

Agentic Incident Command Center

## Tagline

Splunk-grounded AI incident commander with human-approved remediation.

## Short Description

Agentic Incident Command Center helps platform teams move from scattered outage signals to evidence-backed action. It turns deploy, observability, security, network, and MCP/tool-call events into Splunk-ready incident data, ranks likely root causes, maps blast radius, and produces a remediation ledger where high-impact actions remain human-approved.

## Inspiration

During a serious incident, the hardest part is rarely a lack of logs. It is the time lost stitching together deployment context, application errors, traces, database pressure, edge health, security noise, and proposed remediation. AI agents can help, but only if they are grounded in trusted operational data and cannot quietly execute risky actions.

Splunk is the right evidence layer for this. Splunk MCP Server can let an AI assistant investigate operational context, but the final response should still cite events, show confidence, and preserve human approval for rollback, security rule changes, customer communications, and credential-adjacent tool calls.

## What It Does

- Generates synthetic checkout-incident events across deployment, application, APM, database, identity/security, edge network, WAF, AI correlation, remediation, communications, ticketing, and MCP runtime domains.
- Exports a Splunk-ready CSV for the `agentops_events` index.
- Ranks root-cause candidates with evidence weights and cited event references.
- Shows service blast radius and the highest-risk evidence by service.
- Builds an MCP Remediation Ledger for rollback, WAF watch, stakeholder update, ticket creation, and blocked credential-boundary attempts.
- Renders a local dashboard showing incident summary, root-cause ranking, blast radius, remediation approval queue, SPL queries, and an MCP investigation preview.
- Generates a local SPL-equivalent proof report so reviewers can see the intended Splunk query behavior before live Splunk/MCP setup is approved.
- Includes a local Splunk app candidate with Simple XML dashboard panels and saved searches for the core incident-command queries.

## How We Built It

The local prototype uses Python standard library tooling to keep the demo portable and auditable:

- JSONL synthetic incident event generation
- Splunk-ready CSV export
- deterministic risk scoring and approval-state modeling
- root-cause evidence scoring
- blast-radius grouping by service and signal domain
- remediation ledger extraction
- HTML dashboard rendering
- SPL query examples for Splunk ingestion
- local SPL-equivalent query emulation over the generated CSV
- Splunk app candidate files for dashboard and saved search setup

The architecture is designed for Splunk MCP Server: indexed incident events become the evidence source an AI incident commander can query, while the human reviewer retains final control over high-impact remediation.

## Splunk Usage

The current local package includes a Splunk-ready CSV and SPL examples. The intended Splunk flow is:

1. Index `data/splunk_agentops_events.csv` into `agentops_events`.
2. Use SPL queries to retrieve the incident timeline, root-cause evidence, remediation approval ledger, MCP investigation context, and blast radius.
3. Use Splunk MCP Server so an AI assistant can answer questions such as:

```text
What likely caused the checkout incident, which services are affected, and which remediation needs human approval first?
```

Before live Splunk setup, the repository includes a local query proof pack at `reports/latest_local_spl_query_results.html`. It emulates the incident timeline, root-cause evidence, remediation ledger, MCP investigation context, and blast-radius SPL queries over the generated CSV. This is labeled as local emulation, not live Splunk verification.

## Tracks

Primary track:

- Platform & Developer Experience

Bonus target:

- Best Use of Splunk MCP Server

Secondary relevance:

- Observability
- Security

## What Makes It Different

Most AI incident demos either summarize logs or jump straight to automation. Agentic Incident Command Center focuses on the hard middle: making the next human decision faster, safer, and backed by Splunk evidence. The AI can rank causes and propose actions, but rollback, security changes, notifications, and credential-boundary cases remain gated.

## Judging Alignment

- Technological Implementation: deterministic event generation, Splunk-ready CSV, root-cause scoring, local SPL-equivalent query proof, tests, and submission validation.
- Design: a dashboard built around incident command decisions, not raw log browsing.
- Potential Impact: a reusable pattern for teams adopting AI-assisted operations without losing approval control.
- Quality of the Idea: Splunk MCP Server becomes an evidence gateway for agentic incident investigation, while human approval remains the final gate.

## Challenges

The main challenge is balancing a compelling incident story with safe public evidence. The demo must feel operationally real without using private logs, credentials, accounts, customer data, or real external actions. The current implementation solves this with synthetic but realistic cross-domain incident events.

## Accomplishments

- A complete local event-to-dashboard incident command pipeline.
- Root-cause ranking and blast-radius outputs grounded in evidence fields.
- A reusable MCP Remediation Ledger for human-approved incident actions.
- Splunk-ready event exports and SPL examples.
- Local SPL-equivalent query results that prove the CSV supports the intended searches.
- A recording-friendly demo tour that keeps the public video focused and safe.
- A Splunk app candidate with dashboard XML and saved searches.
- Submission-ready architecture, demo script, and judge-alignment materials.

## New During Hackathon

This project was created during the Splunk Agentic Ops Hackathon submission period. The local implementation, synthetic incident event model, dashboard, query pack, public repository candidate, and submission materials were assembled for this hackathon entry.

## What Is Next

- Connect the synthetic incident event stream to an approved Splunk environment.
- Configure Splunk MCP Server after credentials and access boundaries are approved.
- Capture optional live Splunk/MCP proof using synthetic data only.
- Record and upload the public demo video after explicit approval.
- Publish the code repository and submit on Devpost after final user approval.
