# Live Splunk And MCP Proof Command Plan

Status: ready_for_user_review
Root type: public_candidate
Live Splunk MCP verified: true
Live Splunk verified: true
Local MCP SDK adapter verified: true
Official Splunk MCP Server verified: true
Live proof status: live_splunk_verified_official_mcp_verified

## Boundary

This command plan is advisory/readback only. The plan builder does not create accounts, configure credentials, import data, install apps, connect MCP, capture screenshots, update claims, publish, upload, or submit anything.
Explicit user approval is required before credential handling, official Splunk MCP Server configuration, dashboard/screenshot capture, or live-MCP claim wording changes.

## Evidence

- submission/SPLUNK_MCP_RUNBOOK.md (present, required)
- data/splunk_agentops_events.csv (present, required)
- submission/SPL_QUERIES.md (present, required)
- reports/latest_live_splunk_docker_proof.html (present, optional)
- reports/latest_live_splunk_docker_proof.json (present, optional)
- reports/latest_live_splunk_docker_proof.md (present, optional)
- reports/latest_local_spl_query_results.html (present, required)
- reports/latest_local_spl_query_results.json (present, required)
- reports/latest_mcp_investigation.md (present, required)
- reports/latest_claim_boundary_validation.html (present, required)
- reports/latest_claim_boundary_validation.json (present, required)
- reports/latest_external_approval_packet.html (present, required)
- splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml (present, required)
- splunk_app/agentops_control_tower/default/savedsearches.conf (present, required)
- splunk_app/agentops_control_tower/default/app.conf (present, required)

## Commands After Approval

### Refresh local synthetic event proof

Regenerate synthetic checkout-incident events and the local dashboard before any live setup.

```powershell
python prototype\agentops_control_tower.py run-demo
```

### Refresh local SPL-equivalent proof

Confirm incident timeline, root-cause evidence, remediation ledger, MCP investigation context, and blast-radius rows exist before import.

```powershell
python scripts\run_local_spl_query_pack.py
```

### Validate Splunk app candidate

Confirm the Simple XML dashboard and saved searches are locally valid before installing or copying them.

```powershell
python scripts\validate_splunk_app.py
```

### Review live setup boundary

Confirm scope, cost, credential, and data boundaries before any Splunk account or MCP action.

```powershell
manual: review submission\SPLUNK_MCP_RUNBOOK.md and reports\latest_external_approval_packet.html
```

### Approve Splunk account and license use

Start live proof only after explicit account/license approval.

```powershell
manual: create or use an approved Splunk account, trial, Cloud access, or Developer License
```

### Run approved ephemeral Docker Splunk proof

After the user approves Splunk General Terms for this proof only, index the synthetic CSV in temporary Docker Splunk and capture live SPL plus local MCP SDK adapter readback.

```powershell
python scripts\run_live_splunk_docker_proof.py
```

### Create approved synthetic-data index

Keep live proof isolated from private workspace logs or customer data.

```powershell
manual: create index agentops_events for synthetic checkout-incident events only
```

### Import synthetic CSV

Load only the generated synthetic dataset used by the local proof.

```powershell
manual: import data\splunk_agentops_events.csv into agentops_events
```

### Install or copy Splunk app candidate

Expose the Control Tower dashboard without adding unreviewed apps or private data sources.

```powershell
manual: install or copy splunk_app\agentops_control_tower after reviewing app.conf, savedsearches.conf, and dashboard XML
```

### Run live SPL evidence checks

Verify live Splunk results match the local query proof before strengthening claims.

```powershell
manual: run the incident timeline, root-cause evidence, remediation ledger, MCP investigation context, and blast-radius queries from submission\SPL_QUERIES.md
```

### Configure Splunk MCP Server after approval

Allow MCP-assisted investigation only inside the approved synthetic-data scope.

```powershell
manual: configure Splunk MCP Server with read-only approved scope for agentops_events
```

### Run MCP-assisted investigation

Capture the bonus-proof story without allowing external actions or secret access.

```powershell
manual: ask what caused the checkout incident, which services are affected, and which remediation needs human approval first; require cited event IDs plus evidence refs
```

### Build proof capture manifest

Freeze the required live proof capture slots, readback evidence, stop conditions, and claim-upgrade gate before any proof capture.

```powershell
python scripts\build_splunk_mcp_proof_capture_manifest.py
```

### Capture live proof safely

Create evidence for the final demo only after the screen-safety review passes.

```powershell
manual: capture screenshots or recording of indexed CSV, live SPL results, and MCP answer with no tokens, account pages, or private paths visible
```

### Upgrade claim wording only after proof

Re-check public copy before saying the project is verified through Splunk MCP Server.

```powershell
python scripts\validate_claim_boundaries.py && python scripts\validate_submission_packet.py
```
