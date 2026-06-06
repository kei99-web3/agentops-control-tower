# Demo Video Cue Sheet

Status: ready_for_recording_review
Duration: 180 seconds
Final public video ready: false

## Timeline

### 0:00-0:20 Problem

Screen: `reports/latest_demo_tour.html - Scene 1 / Problem`

Narration cue: Show `reports/latest_demo_tour.html`. When a checkout incident starts, the evidence is scattered: deploy logs, application errors, APM latency, database pressure, edge networking, WAF/security signals, and tool-call audit events. The team needs a commander that can connect the dots without hiding the evidence.

Guardrail: Keep this conceptual. Do not show real private operations or accounts.

### 0:20-0:45 Solution

Screen: `reports/latest_demo_tour.html - Scene 2 / Incident Command Summary`

Narration cue: Agentic Incident Command Center uses Splunk as the evidence layer for an AI incident commander. It turns every signal into structured incident data, ranks likely root causes, maps blast radius, and keeps remediation behind human approval.

Guardrail: Say MCP Remediation Ledger as evidence-backed review, not autonomous approval bypass.

### 0:45-1:20 Synthetic Event Flow

Screen: `reports/latest_demo_tour.html - Scene 3 / Incident Review`

Narration cue: Show synthetic events: - Checkout API release completes shortly before the error spike. - Application 5xx and APM latency jump at the same time. - Database pressure, auth anomalies, WAF probes, and edge packet loss are captured as competing signals. - Splunk MCP investigation context is requested, and a credential-boundary tool call is blocked by policy.

Guardrail: Point out synthetic events only. Do not mention private workspace logs.

### 1:20-2:10 Dashboard

Screen: `reports/latest_control_tower.html - KPI strip, root-cause ranking, MCP Remediation Ledger`

Narration cue: Show the dashboard: - Event count, incident count, service count, max risk, blocked actions, and approval queue. - Root-cause ranking with `checkout-api release regression` as the leading candidate. - Blast radius by service. - MCP Remediation Ledger with rollback, WAF watch, stakeholder update, ticketing, and blocked credential-boundary evidence.

Guardrail: Show only dashboard/demo artifacts. Avoid terminals with local paths or tokens.

### 2:10-2:40 Splunk/MCP Fit

Screen: `reports/latest_local_spl_query_results.html and submission/SPL_QUERIES.md`

Narration cue: Show Splunk-ready CSV and sample SPL queries. Explain that in a full Splunk environment, these events are indexed in `agentops_events`, then exposed to AI assistants through Splunk MCP Server so analysts can ask natural-language incident questions without losing auditability.

Guardrail: Say designed for Splunk MCP Server unless live proof is approved and captured.

### 2:40-3:00 Close

Screen: `reports/latest_demo_tour.html - final human-in-the-loop message`

Narration cue: This project does not remove humans from the loop. It makes the human incident commander faster by giving them ranked causes, blast radius, and approval-ready remediation backed by Splunk evidence.

Guardrail: Repeat that humans stay in the approval loop.

## Screen Safety Guardrails

- Use synthetic data only.
- Close terminals that show private paths, tokens, account names, or unrelated files.
- Do not show .env, config files, API keys, OAuth tokens, private logs, customer systems, or real accounts.
- Keep the browser on demo tour, dashboard, local SPL proof, and public candidate files.
- Do not say verified through Splunk MCP Server unless approved live proof exists.

## Boundary

This cue sheet is local recording guidance only. It does not record, upload, publish, write approved URLs, update Devpost, or submit anything.
