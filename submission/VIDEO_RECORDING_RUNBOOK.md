# Video Recording Runbook

Status: local draft
Target: under 3 minutes

## Goal

Record a concise Devpost demo that proves the Agentic Incident Command Center flow:

synthetic incident events -> Splunk-ready data -> incident command dashboard -> root-cause ranking -> MCP Remediation Ledger -> human approval decision.

## Recording Flow

1. Run `python scripts\build_demo_tour.py`.
2. Open `reports/latest_demo_tour.html`.
3. Use the demo tour as the safe recording path:
   - Scene 1 / Problem
   - Scene 2 / Incident Command Summary
   - Scene 3 / Incident Review
   - Scene 4 / Human Approval Queue
   - Scene 5 / Local SPL Proof
   - Scene 6 / Splunk MCP Boundary
4. If more detail is needed, open `reports/latest_control_tower.html`.
5. Show the KPI strip:
   - Events
   - Incidents
   - Services
   - Max Risk
   - Blocked
   - Approval Queue
6. Scroll to Incident Command Summary.
7. Show the Root-Cause Ranking and explain why the checkout release regression leads.
8. Show Blast Radius By Service.
9. Show the MCP Remediation Ledger and explain that rollback, WAF watch, stakeholder update, and credential-boundary cases are evidence-backed and approval-gated.
10. Show Splunk Queries For Demo and MCP Investigation Preview.
11. If a real Splunk environment is approved later, cut only to synthetic indexed data and run the incident timeline/root-cause query.
12. Close with the human-in-the-loop message:

```text
The agent does not bypass approval. It gives the human incident commander the right evidence faster.
```

## Screen Safety Checklist

Before recording:

- Use synthetic data only.
- Close terminals that show private paths, tokens, account names, or unrelated files.
- Do not show `.env`, config files, API keys, OAuth tokens, or private logs.
- Do not show real customer, cloud, incident, identity, ticketing, or Splunk account screens.
- Keep the browser on the dashboard, SPL query examples, and public candidate files.

## Voiceover Notes

- Keep the explanation concrete.
- Avoid saying the project already has live Splunk MCP integration until that is actually verified.
- Say "designed for Splunk MCP Server" for the local-only version.
- Say "verified through Splunk MCP Server" only after the external setup is completed and recorded.
