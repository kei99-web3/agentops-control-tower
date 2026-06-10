# Submission Review Q&A

Status: local review aid, not submitted
Last updated: 2026-06-06 JST

Use this sheet while reviewing the Devpost copy, recording the demo, or answering judge-style questions. It keeps the project story crisp and separates public submission status from bounded local Splunk/MCP proof.

## Core Pitch

Agentic Incident Command Center turns scattered incident signals into Splunk-ready evidence for an AI incident commander. It ranks root causes, maps blast radius, and builds an MCP Remediation Ledger so rollback, security rules, stakeholder updates, ticketing, and credential-boundary cases remain evidence-backed and human-approved.

## Judge Questions

| Question | Short answer |
| --- | --- |
| What problem does this solve? | Incident evidence is scattered across deploy logs, observability, security, network, and tool-call audit trails. The project gives teams a single AI-assisted incident command flow grounded in Splunk evidence. |
| Why Splunk? | Splunk is the operational evidence layer that can unify those signals, query them with SPL, dashboard them, and expose approved context to AI through Splunk MCP Server. |
| What is the MCP Remediation Ledger? | It is a structured view of proposed incident actions: what action is suggested, what policy applies, whether approval is pending or denied, and which evidence a human should review. |
| Where is AI used? | The AI incident commander ranks root causes, summarizes blast radius, and recommends the first human decision. It does not execute high-impact remediation by itself. |
| What is working locally? | Synthetic incident generation, Splunk-ready CSV export, deterministic risk scoring, root-cause ranking, blast-radius grouping, remediation ledger, dashboard rendering, local SPL-equivalent query results, Splunk app candidate, official Splunk MCP Server proof in local Docker with synthetic data, Devpost packet, and validators. |
| What is not claimed yet? | Public repository publication, public video upload, approved URL writeback, Devpost final submission, production Splunk Cloud deployment, and any real customer-log validation are not claimed. |
| How can judges run it? | Run the Python demo commands in `README.md`, inspect `reports/latest_control_tower.html`, review `submission/SPL_QUERIES.md`, and optionally install the Splunk app candidate after importing the CSV into Splunk. |
| Why is the data synthetic? | The public demo should prove the workflow without exposing private logs, credentials, accounts, customer data, or real incident systems. |
| What makes it different? | It does not ask AI to bypass people. It uses AI to make the human incident command decision faster, better structured, and easier to audit. |
| How does it fit the Platform track? | It gives platform/SRE teams a repeatable AI incident command workflow: event schema, pipeline, dashboard, query pack, app candidate, approval ledger, and review runbooks. |
| How does it fit Security? | It includes auth/WAF signals and blocks credential-boundary tool calls while keeping security-rule changes approval-gated. |
| How does it fit Observability? | It correlates deployment, application, APM, database, and network telemetry into a ranked incident narrative. |
| How does it fit the Splunk MCP Server bonus? | The project installed and verified the official Splunk MCP Server in a local Splunk Enterprise Docker proof environment with synthetic `agentops_events`, then used `splunk_run_query` to retrieve event IDs and evidence references. |

## Safe Copy

Use these phrases for the core architecture:

- "designed for Splunk MCP Server"
- "Splunk-ready CSV"
- "SPL examples"
- "local SPL-equivalent proof"
- "Splunk app candidate"
- "synthetic checkout-incident events"

Use these phrases only with the local-Docker/synthetic-data boundary:

- "indexed in Splunk"
- "official Splunk MCP Server verified in local Splunk Enterprise Docker with synthetic data"
- "MCP-assisted investigation over synthetic Splunk search results"
- "captured in the final demo video with no tokens or account screens"

Avoid these phrases:

- "production deployment"
- "real customer logs"
- "autonomous remediation"
- "automatically approved"
- "live Splunk MCP integration"

## Demo Answer Template

```text
The leading root-cause candidate is checkout-api release regression. Agentic Incident Command Center shows the deploy proximity, application error spike, APM latency evidence, blast radius, approval state, and recommended human action. The point is not to let the agent roll back automatically; it is to give the human incident commander the right Splunk evidence faster.
```

## Final Review Checklist

- Confirm the Devpost copy matches the actual proof level.
- Confirm the demo video bounds the MCP proof to local Splunk Enterprise Docker with synthetic data.
- Confirm all public artifacts use synthetic data only.
- Confirm repository and video URLs are replaced only after approval.
- Confirm `reports/latest_submission_validation.html` still reports `ready_for_user_review`.
