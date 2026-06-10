# Live Splunk Incident Command Proof

Status: `live_splunk_verified_official_mcp_verified`
Live Splunk verified: `True`
Official Splunk MCP Server verified: `True`
Local MCP SDK adapter verified: `True`
Synthetic rows: `13`
Indexed rows: `13`

## Query Results

### incident_timeline

- Status: `pass`
- Row count: `13`
- SPL: `search index=agentops_events incident_id="inc-checkout-20260603-0900" | sort _time | table _time event_id signal_domain service event_type risk_score evidence_ref message`
- Missing event IDs: `none`

### root_cause_ranking

- Status: `pass`
- Row count: `4`
- SPL: `search index=agentops_events incident_id="inc-checkout-20260603-0900" root_cause_candidate!="incident_response_coordination" root_cause_candidate!="governance_control" root_cause_candidate!="investigation_context" | stats sum(root_cause_weight) as evidence_score values(signal_domain) as domains values(service) as services values(evidence_ref) as evidence by root_cause_candidate | sort -evidence_score`
- Missing event IDs: `none`

### approval_queue

- Status: `pass`
- Row count: `4`
- SPL: `search index=agentops_events requires_human_approval="True" OR policy_decision="deny" | sort -risk_score | table _time event_id service external_action risk_score approval_state policy_decision runbook_action evidence_ref recommended_human_action`
- Missing event IDs: `none`

### mcp_investigation_context

- Status: `pass`
- Row count: `3`
- SPL: `search index=agentops_events mcp_tool!="none" OR signal_domain="ai_correlation" | table _time event_id component mcp_tool event_type evidence_ref recommended_human_action`
- Missing event IDs: `none`

### blast_radius_by_service

- Status: `pass`
- Row count: `6`
- SPL: `search index=agentops_events incident_id="inc-checkout-20260603-0900" | stats count max(risk_score) as max_risk values(signal_domain) as domains by service | sort -max_risk`
- Missing event IDs: `none`

## Official Splunk MCP Server Proof

Status: `official_splunk_mcp_server_captured`
Evidence: `submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md`

Supported claim:

> Official Splunk MCP Server was installed and verified in a reproducible local Splunk Enterprise Docker proof environment against synthetic incident data.

Boundary:

- Production Splunk Cloud deployment is not claimed.
- Token values, Splunk password, login screens, account pages, and non-synthetic data are not included.
- The proof is bounded to local Splunk Enterprise Docker with synthetic `agentops_events` data.

## MCP Boundary

Official Splunk MCP Server proof is bounded to local Splunk Enterprise Docker, synthetic agentops_events data, Streamable HTTP via mcp-remote, and read-only query evidence.

## Safety Boundary

Approved proof used an ephemeral local Docker Splunk runtime and only generated synthetic CSV data. Production Splunk Cloud deployment is not claimed. No tokens, passwords, private workspace logs, public repo publication, video upload, URL writeback, Devpost update, or Devpost submission is included in this report.
