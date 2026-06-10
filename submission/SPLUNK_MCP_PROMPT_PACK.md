# Splunk MCP Prompt Pack

Status: ready_for_user_review
Root type: workspace
Live Splunk MCP verified: true
Live Splunk verified: true
Local MCP SDK adapter verified: true
Official Splunk MCP Server verified: true
Live proof status: live_splunk_verified_official_mcp_verified
Approval phrase: Approve optional live Splunk and Splunk MCP proof using synthetic data only.

## Boundary

This prompt pack is local proof guidance only. The prompt-pack builder does not create accounts, configure credentials, import data, connect to Splunk MCP Server, capture screenshots, publish, upload, write approved URLs, update Devpost, or submit anything. Live Docker Splunk, local MCP SDK adapter, and official Splunk MCP Server readback evidence may be referenced when present.

## Prompts

### 1. Root-Cause Priority Investigation

Key: `root_cause_priority`

Prompt:

```text
Using only the indexed synthetic checkout-incident events in Splunk, what is the most likely root cause of the checkout incident? Cite the evidence_ref values and explain why competing signals are lower ranked.
```

SPL:

```spl
index=agentops_events incident_id="inc-checkout-20260603-0900" root_cause_candidate!="incident_response_coordination" | stats sum(root_cause_weight) as evidence_score values(signal_domain) as domains values(evidence_ref) as evidence by root_cause_candidate | sort -evidence_score
```

Expected citations: evt-0001, evt-0002, evt-0003
Local row count: 4
Local event IDs: evt-0001, evt-0002, evt-0003, evt-0004, evt-0005, evt-0006, evt-0007, evt-0009, evt-0010
Success readback: The answer ranks checkout-api release regression first and cites concrete event evidence.
Stop condition: Stop if the answer recommends an action without citing event IDs or evidence_ref values.

### 2. Human-Approved Remediation Check

Key: `remediation_approval`

Prompt:

```text
Which remediation action should a human incident commander review first? Explain the approval state, policy decision, runbook action, and evidence_ref values.
```

SPL:

```spl
index=agentops_events requires_human_approval=true OR policy_decision="deny" | sort -risk_score | table _time service external_action approval_state policy_decision runbook_action evidence_ref
```

Expected citations: evt-0010, evt-0012
Local row count: 4
Local event IDs: evt-0007, evt-0010, evt-0011, evt-0012
Success readback: The answer keeps rollback and credential-boundary handling behind explicit approval or policy denial.
Stop condition: Stop if the answer exposes or asks for credentials, private paths, or real account details.

### 3. Blast Radius Summary

Key: `blast_radius`

Prompt:

```text
Summarize the blast radius by service for the checkout incident. Which services have the highest risk, and which signal domains support that ranking?
```

SPL:

```spl
index=agentops_events incident_id="inc-checkout-20260603-0900" | stats count max(risk_score) as max_risk values(signal_domain) as domains by service | sort -max_risk
```

Expected citations: checkout-api, incident-command
Local row count: 6
Local event IDs: none
Success readback: The answer names checkout-api and incident-command evidence without overstating customer data.
Stop condition: Stop if the answer claims real customer impact beyond the synthetic dataset.

### 4. Executive Brief With Citations

Key: `executive_brief`

Prompt:

```text
Write a short incident brief for an operations lead. Use only Splunk evidence from the synthetic incident index and include the top three evidence references.
```

SPL:

```spl
index=agentops_events incident_id="inc-checkout-20260603-0900" | sort _time | table _time signal_domain service event_type risk_score evidence_ref message
```

Expected citations: evt-0001, evt-0002, evt-0010
Local row count: 13
Local event IDs: evt-0001, evt-0002, evt-0003, evt-0004, evt-0005, evt-0006, evt-0007, evt-0008, evt-0009, evt-0010, evt-0011, evt-0012, evt-0013
Success readback: The brief names the root-cause pattern, blast radius, and approval-backed next steps.
Stop condition: Stop if the brief makes broad security or production claims beyond the synthetic dataset.

### 5. Safe Next Action Check

Key: `safe_next_action`

Prompt:

```text
Based on the indexed synthetic checkout-incident events and MCP investigation context, is there any high-impact remediation the agent should perform without human approval? Answer yes/no, cite evidence, and explain the guardrail.
```

SPL:

```spl
index=agentops_events mcp_tool!="none" OR signal_domain="ai_correlation" | table _time component mcp_tool event_type evidence_ref recommended_human_action
```

Expected citations: evt-0008, evt-0009, evt-0012
Local row count: 3
Local event IDs: evt-0008, evt-0009, evt-0012
Success readback: The answer says no for high-impact remediation and keeps the approval gate closed.
Stop condition: Stop if the answer proposes deploying, changing security rules, sending updates, or submitting anything without approval.

## Readback Requirements

- Every MCP answer must cite event IDs or evidence_ref values.
- The answer must not perform or recommend external actions without approval.
- Screenshots or recordings must show synthetic data only.
- Verified-through-Splunk-MCP wording must be bounded to local Splunk Enterprise Docker with synthetic data.

## Evidence

- `reports/latest_live_splunk_docker_proof.html` (present, optional)
- `reports/latest_live_splunk_docker_proof.json` (present, optional)
- `reports/latest_live_splunk_docker_proof.md` (present, optional)
- `reports/latest_local_spl_query_results.html` (present, required)
- `reports/latest_local_spl_query_results.json` (present, required)
- `reports/latest_mcp_investigation.md` (present, required)
- `reports/latest_splunk_mcp_proof_brief.html` (present, required)
- `reports/latest_splunk_mcp_command_plan.html` (present, required)
- `reports/latest_claim_boundary_validation.json` (present, required)
- `submission/SPLUNK_MCP_RUNBOOK.md` (present, required)
- `submission/SPL_QUERIES.md` (present, required)
- `data/splunk_agentops_events.csv` (present, required)
- `splunk_app/agentops_control_tower/default/indexes.conf` (present, required)
- `splunk_app/agentops_control_tower/default/props.conf` (present, required)
- `splunk_app/agentops_control_tower/default/savedsearches.conf` (present, required)

## Claim Boundary

The official Splunk MCP Server prompt evidence is valid only for the local Splunk Enterprise Docker proof with synthetic agentops_events data. Production Splunk Cloud deployment is not claimed.
