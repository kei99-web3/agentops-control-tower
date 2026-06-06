# Splunk MCP Proof Capture Manifest

Status: ready_for_user_review
Root type: public_candidate
Approval phrase: `Approve optional live Splunk and Splunk MCP proof using synthetic data only.`
Live Splunk MCP verified: false
Live Splunk verified: false
Local MCP SDK adapter verified: false
Official Splunk MCP Server verified: false
Captured evidence status: pending_user_approval
Claim upgrade ready: false

## Live Proof Summary

- status: `missing`
- synthetic_row_count: `missing`
- indexed_row_count: `missing`
- failed_query_count: `missing`
- official_mcp_blocker: `not_recorded`

## Capture Slots

### approved_scope

Status: pending_user_approval

Required readback:

- Explicit approval phrase is present.
- Splunk General Terms flag is used only for the temporary Docker proof.
- Data source is limited to data/splunk_agentops_events.csv.
- MCP scope is read-only for the synthetic agentops_events index.

Safe artifact: Local note in post-action evidence log; no credential or account screenshots.

### synthetic_import

Status: pending_live_capture

Required readback:

- agentops_events index exists.
- Imported rows match the generated synthetic CSV row count.
- Sourcetype is agentops:events or equivalent documented mapping.

Safe artifact: reports/latest_live_splunk_docker_proof.*

### live_spl_queries

Status: pending_live_capture

Required readback:

- Incident timeline query returns signal domains, services, risk scores, and evidence refs.
- Root-cause evidence query ranks checkout-api release regression first.
- MCP Remediation Ledger query returns pending/blocked human-review items.
- Blast-radius query returns affected services and max risk.

Safe artifact: reports/latest_live_splunk_docker_proof.json query_results.

### splunk_app_dashboard

Status: pending_dashboard_ui_capture

Required readback:

- Agentic Incident Command Center dashboard opens against the synthetic index.
- KPI, incident summary, root-cause ranking, blast radius, and remediation ledger sections render.
- No private workspace paths, real accounts, or credentials are visible.

Safe artifact: Dashboard screenshot or recording segment after screen-safety review.

### mcp_assisted_answer

Status: pending_live_capture

Required readback:

- MCP answer cites event IDs and evidence refs.
- MCP answer does not perform external actions.
- MCP answer stays within read-only synthetic data scope.
- Official Splunk MCP Server app remains pending until approved credential handling and install are completed.

Safe artifact: reports/latest_live_splunk_docker_proof.json mcp_adapter_proof.

### claim_upgrade_validation

Status: blocked_until_official_splunk_mcp_server_proof

Required readback:

- Claim wording is updated only after live SPL and official Splunk MCP Server evidence are reviewed.
- validate_claim_boundaries.py passes.
- validate_submission_packet.py passes.

Safe artifact: Validation JSON/HTML after approved proof capture and wording update.

## Expected Final Readback

- synthetic_index: `agentops_events contains only generated synthetic rows`
- live_spl_queries: `required SPL result tables cite event IDs and evidence refs`
- mcp_answer: `local read-only MCP SDK adapter cites event IDs and evidence refs without external action`
- official_mcp: `official Splunk MCP Server remains pending until Splunkbase install and approved credential handling`
- screen_safety: `no credentials, account pages, private paths, or secrets are visible`
- claim_validation: `claim and submission validators pass after any wording change`

## Evidence

- `reports/latest_splunk_mcp_command_plan.html` (present, required)
- `reports/latest_splunk_mcp_proof_brief.html` (present, required)
- `reports/latest_splunk_mcp_prompt_pack.html` (present, required)
- `reports/latest_live_splunk_docker_proof.html` (missing, optional)
- `reports/latest_live_splunk_docker_proof.json` (missing, optional)
- `reports/latest_live_splunk_docker_proof.md` (missing, optional)
- `reports/latest_local_spl_query_results.html` (present, required)
- `reports/latest_local_spl_query_results.json` (present, required)
- `reports/latest_splunk_app_package_manifest.html` (present, required)
- `reports/latest_claim_boundary_validation.html` (present, required)
- `reports/latest_claim_boundary_validation.json` (present, required)
- `reports/latest_public_artifact_url_readback.html` (present, required)
- `reports/latest_post_action_evidence_brief.html` (present, required)
- `submission/SPLUNK_MCP_RUNBOOK.md` (present, required)
- `submission/SPLUNK_MCP_PROMPT_PACK.md` (present, required)
- `submission/SPL_QUERIES.md` (present, required)
- `data/splunk_agentops_events.csv` (present, required)
- `splunk_app/agentops_control_tower/default/indexes.conf` (present, required)
- `splunk_app/agentops_control_tower/default/props.conf` (present, required)
- `splunk_app/agentops_control_tower/default/savedsearches.conf` (present, required)
- `splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml` (present, required)

## Stop Conditions

- Stop if Splunk account, license, cost, credential, or MCP scope is not explicitly approved.
- Stop if any data source is real private workspace data, customer data, local paths, or credentials.
- Stop if screenshots or recordings show account settings, billing pages, tokens, hostnames, terminals with secrets, or unrelated private files.
- Stop if MCP can mutate data, send notifications, publish, trade, deploy, or access outside the approved synthetic index.
- Stop if event IDs and evidence refs cannot be cited from the live proof.
- Stop if claim-boundary validation fails after any wording change.

## Boundary

This proof capture manifest is local evidence aggregation only. The manifest builder does not create accounts, configure credentials, import data, install apps, connect MCP, capture screenshots, record video, update claims, publish, upload, write approved URLs, update Devpost, or submit anything. When a live proof artifact is present, it is limited to the approved ephemeral Docker Splunk runtime, synthetic data, and read-only local MCP SDK adapter evidence.
