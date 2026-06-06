# Demo Video Script

Target length: under 3 minutes

## 0:00-0:20 Problem

Show `reports/latest_demo_tour.html`.

When a checkout incident starts, the evidence is scattered: deploy logs, application errors, APM latency, database pressure, edge networking, WAF/security signals, and tool-call audit events. The team needs a commander that can connect the dots without hiding the evidence.

## 0:20-0:45 Solution

Agentic Incident Command Center uses Splunk as the evidence layer for an AI incident commander. It turns every signal into structured incident data, ranks likely root causes, maps blast radius, and keeps remediation behind human approval.

## 0:45-1:20 Synthetic Event Flow

Show synthetic events:

- Checkout API release completes shortly before the error spike.
- Application 5xx and APM latency jump at the same time.
- Database pressure, auth anomalies, WAF probes, and edge packet loss are captured as competing signals.
- Splunk MCP investigation context is requested, and a credential-boundary tool call is blocked by policy.

## 1:20-2:10 Dashboard

Show the dashboard:

- Event count, incident count, service count, max risk, blocked actions, and approval queue.
- Root-cause ranking with `checkout-api release regression` as the leading candidate.
- Blast radius by service.
- MCP Remediation Ledger with rollback, WAF watch, stakeholder update, ticketing, and blocked credential-boundary evidence.

## 2:10-2:40 Splunk/MCP Fit

Show Splunk-ready CSV and sample SPL queries. Explain that in a full Splunk environment, these events are indexed in `agentops_events`, then exposed to AI assistants through Splunk MCP Server so analysts can ask natural-language incident questions without losing auditability.

## 2:40-3:00 Close

This project does not remove humans from the loop. It makes the human incident commander faster by giving them ranked causes, blast radius, and approval-ready remediation backed by Splunk evidence.
