# SPL Queries

Use these after importing `data/splunk_agentops_events.csv` into the `agentops_events` index.
The query pack demonstrates a cross-domain incident command workflow over synthetic data.

For local proof before live Splunk access is approved, run:

```powershell
python scripts\run_local_spl_query_pack.py
```

This writes `reports/latest_local_spl_query_results.html` and `.json` with equivalent table results over the generated CSV. It is a local emulation, not live Splunk verification.

## Incident timeline across observability, security, network, deploy, and MCP

```spl
index=agentops_events incident_id="inc-checkout-20260603-0900" | sort _time | table _time signal_domain service event_type risk_score evidence_ref message
```

## Root-cause evidence for checkout regression

```spl
index=agentops_events incident_id="inc-checkout-20260603-0900" root_cause_candidate!="incident_response_coordination" | stats sum(root_cause_weight) as evidence_score values(signal_domain) as domains values(evidence_ref) as evidence by root_cause_candidate | sort -evidence_score
```

## Human-approved remediation ledger

```spl
index=agentops_events requires_human_approval=true OR policy_decision="deny" | sort -risk_score | table _time service external_action approval_state policy_decision runbook_action evidence_ref
```

## Splunk MCP investigation context

```spl
index=agentops_events mcp_tool!="none" OR signal_domain="ai_correlation" | table _time component mcp_tool event_type evidence_ref recommended_human_action
```

## Blast radius by service

```spl
index=agentops_events incident_id="inc-checkout-20260603-0900" | stats count max(risk_score) as max_risk values(signal_domain) as domains by service | sort -max_risk
```
