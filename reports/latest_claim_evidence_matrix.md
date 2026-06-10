# Claim Evidence Matrix

Status: ready_for_user_review
Root type: workspace
Claim boundary status: pass
Final submit ready: true
Ready claims: 7/7

## Safe Copy Rule

Use local-proof and designed-for wording until public URL, live Splunk/MCP, or Devpost submit evidence has been explicitly approved and read back.

## Claims

### The demo uses synthetic incident data only.

Support status: locally_supported
Ready: true

Allowed wording: The current demo uses synthetic checkout-incident events only; no real secrets, accounts, customer data, cloud accounts, or private logs are used.
Avoid wording: Avoid implying the demo uses real customer logs, production secrets, or live private operations.

Evidence:
- `data/synthetic_agentops_events.jsonl` (present) - Synthetic source events used by the local demo.
- `data/agentops_event_schema.json` (present) - Schema describing the synthetic event model.
- `data/splunk_agentops_events.csv` (present) - Splunk-ready export generated from synthetic events.
- `submission/OFFICIAL_REQUIREMENTS_AUDIT.md` (present) - Records the synthetic-data-only public demo boundary.

Remaining gate: None for local demo evidence; keep the same boundary in public video and Devpost text.

### Agentic Incident Command Center produces Splunk-ready incident data and SPL query examples.

Support status: locally_supported
Ready: true

Allowed wording: The package exports Splunk-ready CSV and includes SPL examples plus a local SPL-equivalent proof report.
Avoid wording: Avoid saying the data has already been imported into live Splunk unless approved live proof exists.

Evidence:
- `data/splunk_agentops_events.csv` (present) - CSV intended for an agentops_events index after approval.
- `submission/SPL_QUERIES.md` (present) - SPL examples for incident timeline, root-cause evidence, remediation ledger, MCP investigation context, and blast radius.
- `reports/latest_local_spl_query_results.html` (present) - Local SPL-equivalent proof over the generated CSV.
- `architecture_diagram.md` (present) - Shows the Splunk data-flow architecture.

Remaining gate: Live Splunk import requires explicit account/license approval.

### The MCP Remediation Ledger ranks proposed incident actions and cites evidence for human review.

Support status: locally_supported
Ready: true

Allowed wording: The local dashboard and analysis show rollback, WAF watch, stakeholder update, ticketing, and blocked credential-boundary items with evidence references.
Avoid wording: Avoid claiming fully autonomous remediation, production enforcement, or real incident execution.

Evidence:
- `reports/latest_analysis.json` (present) - Analysis output containing incident summary, root-cause candidates, remediation ledger, approval queue, and MCP preview.
- `reports/latest_control_tower.html` (present) - Dashboard surface for root-cause ranking, blast radius, remediation ledger, and approval queue.
- `reports/latest_mcp_investigation.md` (present) - Evidence-backed MCP investigation preview with event IDs.
- `prototype/agentops_control_tower.py` (present) - Generates the ledger, recommendations, SPL examples, and dashboard.

Remaining gate: No external gate for local proof; keep real external actions human-approved.

### High-impact remediation remains behind explicit human approval gates.

Support status: locally_supported
Ready: true

Allowed wording: Rollback, WAF changes, stakeholder updates, public repo publication, video upload, URL writeback, live Splunk/MCP proof, and Devpost submission are modeled as explicit approval gates.
Avoid wording: Avoid saying remediation, publication, upload, URL writeback, live proof, or final submission has happened before readback evidence exists.

Evidence:
- `reports/latest_submission_gate_ledger.html` (present) - Gate ledger for public repo, video, optional live proof, and Devpost final submission.
- `reports/latest_external_approval_packet.html` (present) - Explains purpose, benefits, risks, and verification for each external action.
- `reports/latest_post_action_evidence_brief.html` (present) - Defines completion/readback evidence after each external action.
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` (present) - Template for recording approved external-action readback without secrets.
- `reports/latest_submission_url_validation.html` (present) - Shows public repo and video URLs are pending until approved.

Remaining gate: All external actions require explicit user approval before execution.

### The package includes a local Splunk app candidate.

Support status: locally_supported
Ready: true

Allowed wording: The package includes a local .spl app candidate with dashboard XML and saved searches for review.
Avoid wording: Avoid saying the app has been installed, uploaded, or accepted by Splunk unless that proof is captured.

Evidence:
- `dist/agentops-control-tower-splunk-app.spl` (present) - Local .spl package artifact.
- `reports/latest_splunk_app_package_manifest.html` (present) - Package member list, SHA256, and no-install/no-upload boundary.
- `splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml` (present) - Simple XML dashboard candidate.
- `splunk_app/agentops_control_tower/default/savedsearches.conf` (present) - Saved search candidates for AgentOps queries.

Remaining gate: Install/upload/use in Splunk requires explicit approval.

### The project is designed for Splunk MCP Server investigation.

Support status: designed_pending_live_proof
Ready: true

Allowed wording: Agentic Incident Command Center is designed for Splunk MCP Server, with synthetic incident data, SPL examples, local SPL proof, and a live proof runbook.
Avoid wording: Avoid saying verified through Splunk MCP Server until approved live setup and proof capture are complete.

Evidence:
- `submission/SPLUNK_MCP_RUNBOOK.md` (present) - Post-approval runbook for live Splunk MCP setup and proof capture.
- `reports/latest_splunk_mcp_command_plan.html` (present) - Command plan for account/license, synthetic import, app install, MCP setup, and proof.
- `reports/latest_splunk_mcp_proof_brief.html` (present) - Success criteria and claim-upgrade rules for live proof.
- `reports/latest_splunk_mcp_prompt_pack.html` (present) - Prompt pack with SPL, expected event citations, success readbacks, and stop conditions.
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present) - Capture slots, expected readback, stop conditions, and claim-upgrade gate for optional live proof.
- `reports/latest_claim_boundary_validation.html` (present) - Checks that public copy does not overclaim live Splunk/MCP proof.

Remaining gate: Optional live Splunk/MCP proof requires approved Splunk account/license and MCP configuration.

### The local package is ready for user review, but final submission is not complete.

Support status: ready_for_user_review_external_gates_pending
Ready: true

Allowed wording: The local package is ready for user review; final submission is pending public repo URL, public video URL, approved URL writeback, and final Devpost approval.
Avoid wording: Avoid saying submitted, public, final, or approved until post-action evidence confirms it.

Evidence:
- `reports/latest_final_go_no_go.html` (present) - Separates local readiness from pending external gates.
- `scripts/validate_submission_packet.py` (present) - Validator that reports final_submit_ready false and pending actions.
- `reports/latest_launch_decision_brief.html` (present) - Approval order, approval phrases, and blocked final gates.
- `reports/latest_devpost_manual_fill_brief.html` (present) - Devpost field fill and readback brief with pending URL fields.

Remaining gate: Public repo, public video, URL writeback, and Devpost final submission remain pending.

## Boundary

This matrix is local claim-support evidence only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.
