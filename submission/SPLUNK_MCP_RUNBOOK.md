# Splunk MCP Runbook

This runbook is a preparation document only. Do not execute account, license, credential, or cloud setup steps without explicit user approval.

For the non-executing approval sequence, regenerate and review:

```powershell
python scripts\build_splunk_mcp_command_plan.py
python scripts\build_splunk_mcp_proof_brief.py
python scripts\build_splunk_mcp_prompt_pack.py
python scripts\build_splunk_mcp_proof_capture_manifest.py
```

Open `reports/latest_splunk_mcp_command_plan.html`, `reports/latest_splunk_mcp_proof_brief.html`, `reports/latest_splunk_mcp_prompt_pack.html`, and `reports/latest_splunk_mcp_proof_capture_manifest.html` before any Splunk account, license, credential, import, app install, MCP Server configuration, proof capture, or live-claim wording change.

## Goal

Connect the local AgentOps event stream to Splunk, then expose that indexed operational data through Splunk MCP Server so an AI assistant can investigate agent operations with evidence-backed queries.

## Local-Only Step Already Available

Run:

```powershell
python prototype\agentops_control_tower.py run-demo
python scripts\run_local_spl_query_pack.py
python scripts\validate_splunk_app.py
```

This creates:

- `data/synthetic_agentops_events.jsonl`
- `data/splunk_agentops_events.csv`
- `reports/latest_analysis.json`
- `reports/latest_control_tower.html`
- `reports/latest_local_spl_query_results.html`
- `reports/latest_local_spl_query_results.json`
- `reports/latest_splunk_mcp_prompt_pack.html`
- `reports/latest_splunk_mcp_proof_capture_manifest.html`
- `reports/latest_splunk_mcp_proof_capture_manifest.json`
- `reports/latest_splunk_mcp_proof_capture_manifest.md`
- `submission/SPLUNK_MCP_PROMPT_PACK.md`
- `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md`
- `splunk_app/agentops_control_tower/default/indexes.conf`
- `splunk_app/agentops_control_tower/default/props.conf`
- `splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml`
- `splunk_app/agentops_control_tower/default/savedsearches.conf`

The local query result report emulates the demo SPL query intent before live Splunk access is approved. It should not be presented as live Splunk proof, but it confirms that the generated CSV contains the rows needed for the demo searches.

## Splunk Setup After Approval

1. Create or use an approved Splunk account.
2. Install Splunk Enterprise trial or use approved Splunk Cloud access.
3. Request or apply the Developer License if needed.
4. Create an index such as `agentops_events` or review the packaged `default/indexes.conf`.
5. Import `data/splunk_agentops_events.csv` with sourcetype `agentops:events`; review `default/props.conf` for CSV extraction and timestamp handling.
6. Optionally install or copy the local Splunk app candidate from `splunk_app/agentops_control_tower`.
7. Open the `Agentic Incident Command Center` dashboard or verify basic searches:

```spl
index=agentops_events | stats count by component
```

```spl
index=agentops_events risk_score>=70 | table _time component run_id event_type risk_score policy_decision evidence_ref message
```

8. Configure Splunk MCP Server only after credentials and access scopes are approved.
9. Verify that MCP queries can retrieve:

- high-risk events
- blocked policy events
- approval queue
- MCP remediation ledger entries
- Root-cause ranking and blast-radius rows

## Demo Proof To Capture

- Screenshot or recording of CSV indexed in Splunk.
- Screenshot or recording of high-risk event SPL query.
- Screenshot or recording of MCP-assisted question:

```text
Which autonomous AI operation needs human approval first, and what evidence supports that recommendation?
```

Expected answer should cite the blocked X publishing event or secret-boundary MCP event with event IDs and evidence references.

Review `reports/latest_splunk_mcp_proof_brief.html` before recording. It defines the proof success criteria, screen safety checks, stop conditions, and claim-upgrade rule.

Use `submission/SPLUNK_MCP_PROMPT_PACK.md` as the approved-proof prompt list. It defines the exact questions, SPL, expected event citations, success readbacks, and stop conditions for the optional live MCP demonstration.

Use `reports/latest_splunk_mcp_proof_capture_manifest.html` as the capture checklist. It freezes the approved scope, synthetic import, live SPL checks, dashboard view, MCP-assisted answer, claim-upgrade validation, expected readback, and stop conditions before any optional live proof is attempted.

## Safety Notes

- Use synthetic data only for the public demo.
- Do not import real private workspace logs, private paths, or customer data.
- Do not expose `.env`, tokens, API keys, private keys, OAuth refresh tokens, account pages, customer data, or personal data.
- Do not enable any real rollback, security-rule change, customer notification, ticket write, deployment, or production action from the demo.
