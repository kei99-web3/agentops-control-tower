# Live Splunk/MCP Proof Brief

Status: ready_for_user_review
Root type: workspace
Live Splunk MCP verified: true
Live Splunk verified: true
Local MCP SDK adapter verified: true
Official Splunk MCP Server verified: true
Live proof status: live_splunk_verified_official_mcp_verified
Approval phrase: Approve optional live Splunk and Splunk MCP proof using synthetic data only.

## Live Proof Rows

- Synthetic rows: `13`
- Indexed rows: `13`
- Failed live SPL queries: `0`

## Why This Matters

The live Docker proof strengthens the Splunk data story, the local MCP SDK adapter demonstrates read-only cited investigation behavior, and the official Splunk MCP Server readback confirms the bonus proof in a reproducible local Splunk Enterprise Docker environment using synthetic data only. Production Splunk Cloud deployment is not claimed.

## Evidence

- `reports/latest_splunk_mcp_command_plan.html` (present, required)
- `reports/latest_splunk_app_package_manifest.html` (present, required)
- `reports/latest_live_splunk_docker_proof.html` (present, optional)
- `reports/latest_live_splunk_docker_proof.json` (present, optional)
- `reports/latest_live_splunk_docker_proof.md` (present, optional)
- `reports/latest_local_spl_query_results.html` (present, required)
- `reports/latest_local_spl_query_results.json` (present, required)
- `reports/latest_claim_boundary_validation.html` (present, required)
- `reports/latest_claim_boundary_validation.json` (present, required)
- `reports/latest_mcp_investigation.md` (present, required)
- `submission/SPLUNK_MCP_RUNBOOK.md` (present, required)
- `submission/SPL_QUERIES.md` (present, required)
- `data/splunk_agentops_events.csv` (present, required)
- `splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml` (present, required)
- `splunk_app/agentops_control_tower/default/savedsearches.conf` (present, required)

## Proof Success Criteria

### Synthetic data isolation

Evidence: Only data/splunk_agentops_events.csv is imported into the approved agentops_events index.

Acceptance: No real workspace logs, customer data, local paths, credentials, or account pages are shown.

### Live SPL query proof

Evidence: Incident timeline, root-cause evidence, MCP Remediation Ledger, Splunk MCP investigation context, and blast-radius SPL queries return rows.

Acceptance: Returned rows include incident IDs, services, risk scores, root-cause candidates, policy decisions, approval states, and evidence refs.

### Splunk app proof

Evidence: The local Splunk app candidate or copied dashboard shows the Agentic Incident Command Center view.

Acceptance: The dashboard points only at the approved synthetic index and mirrors the local proof story.

### MCP-assisted investigation proof

Evidence: Splunk MCP Server answers the approval-priority question from indexed synthetic events.

Acceptance: The answer cites event IDs and evidence refs instead of making unsupported recommendations.

### Claim boundary upgrade

Evidence: Claim validation and submission validation pass after any wording changes.

Acceptance: Live Splunk/MCP wording is used only after the live evidence above is captured and reviewed.

## Approval Steps

1. Approve live proof scope (User)

Action: Approve optional live Splunk and Splunk MCP proof using synthetic data only.

Verification: Approval explicitly covers account/license use, synthetic import, read-only MCP scope, and proof capture.

2. Prepare local proof inputs (Codex/local)

Action: Run the local demo, SPL-equivalent query pack, Splunk app validation, and package manifest.

Verification: latest_local_spl_query_results and latest_splunk_app_package_manifest are ready_for_user_review.

3. Create approved Splunk scope (User/manual)

Action: Use approved Splunk access and create/import only the synthetic agentops_events dataset.

Verification: The index contains the expected synthetic rows and no private or account data.

4. Capture SPL proof (User/manual)

Action: Run the SPL queries from submission/SPL_QUERIES.md.

Verification: Screenshots or recording show incident timeline, root-cause evidence, remediation ledger, MCP investigation context, and blast-radius rows.

5. Configure Splunk MCP read-only proof (User/manual)

Action: Configure Splunk MCP Server with approved read-only scope for the synthetic index.

Verification: The MCP answer cites event IDs and evidence refs and does not perform external actions.

6. Upgrade public claims only after proof (Codex/local)

Action: Update Devpost/video wording only if proof evidence is reviewed, then rerun validators.

Verification: validate_claim_boundaries.py and validate_submission_packet.py pass.

## Screen Safety Checks

- Show only the Splunk search/dashboard, local demo pages, and synthetic event evidence needed for the proof.
- Hide browser tabs, account settings, billing, tokens, hostnames, private paths, terminals with secrets, and personal data.
- Use synthetic event IDs and evidence refs as the narration anchor.
- Do not show credential setup screens or MCP configuration secrets in the video.
- Do not imply live Splunk/MCP verification unless the proof has actually been captured.

## Stop Conditions

- Stop if Splunk access, cost, license, or credential scope is not explicitly approved.
- Stop if the data source is anything other than the generated synthetic CSV.
- Stop if any screenshot or recording exposes credentials, account pages, local paths, or private data.
- Stop if MCP can access more than the approved read-only synthetic-data scope.
- Stop if claim-boundary validation fails after wording changes.
- Stop before public repo publication, video upload, URL writeback, or Devpost submit unless those separate gates are approved.

## Claim Upgrade Rule

Use verified-through-Splunk-MCP wording only when it is explicitly bounded to the local Splunk Enterprise Docker proof with synthetic data. Do not claim production Splunk Cloud deployment.

## Boundary

This brief is local proof-decision support only. The brief builder does not create accounts, configure credentials, import data, install apps, connect MCP, capture screenshots, publish, upload, update claims, write approved URLs, update Devpost, or submit anything. When live proof evidence exists, it is limited to approved ephemeral Docker Splunk, synthetic data, and a local read-only MCP SDK adapter unless the official Splunk MCP Server field says otherwise.
