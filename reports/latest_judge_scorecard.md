# Judge Scorecard

Status: ready_for_user_review
Root type: public_candidate
Official rules source: https://splunk.devpost.com/rules
Rules last checked by package: 2026-06-04 JST
Final submit ready: false

## Recommended Judge Path

- Open reports/latest_judge_quickstart.html.
- Review this scorecard by Stage One, Stage Two, and bonus alignment.
- Open reports/latest_control_tower.html and reports/latest_demo_tour.html.
- Review reports/latest_local_spl_query_results.html and reports/latest_splunk_app_package_manifest.html.
- Review reports/latest_submission_gate_ledger.html before any external approval.
- Keep live Splunk/MCP wording local-design-only until approved proof exists.

## Stage One Pass/Fail Baseline

Stage One is treated as a pass/fail viability gate before Stage Two scoring; these checks are the local minimum review baseline.

Stage One baseline ready: true

### Theme fit

Local status: local_ready
Ready: true
Official basis: Stage One is pass/fail; the project must clearly address the Agentic Ops challenge.

Evidence:
- `README.md` (present)
- `architecture_diagram.md` (present)
- `submission/JUDGING_ALIGNMENT.md` (present)

Remaining gate: Public demo still needs approval before final submission.

### Required Splunk capability use

Local status: local_ready_live_optional
Ready: true
Official basis: Stage One should show credible use of Splunk data, Splunk AI, or Splunk MCP-style capability.

Evidence:
- `submission/SPLUNK_MCP_RUNBOOK.md` (present)
- `reports/latest_local_spl_query_results.html` (present)
- `reports/latest_splunk_app_package_manifest.html` (present)

Remaining gate: Live Splunk/MCP proof remains optional and approval-gated.

### Required submission artifacts

Local status: local_ready_external_urls_pending
Ready: true
Official basis: Stage One requires reviewable materials including code, public demo video, architecture, and runnable instructions.

Evidence:
- `LICENSE` (present)
- `reports/latest_devpost_final_copy.html` (present)
- `reports/latest_video_cue_sheet.html` (present)
- `reports/latest_public_repo_publish_brief.html` (present)

Remaining gate: Public repository URL and public demo video URL are still pending user approval.

### Safe data and claim integrity

Local status: local_ready
Ready: true
Official basis: Stage One should be reviewable without unsafe data, hidden credentials, or overstated capability claims.

Evidence:
- `reports/latest_claim_evidence_matrix.html` (present)
- `reports/latest_claim_boundary_validation.html` (present)
- `reports/latest_status_conflict_audit.html` (present)

Remaining gate: Keep final submit blocked until public URLs and optional proof readbacks are approved.

## Stage Two Scored Criteria

- Technological Implementation
- Design
- Potential Impact
- Quality of the Idea

## MCP Bonus Claim Boundary

Bonus category: Best Use of Splunk MCP Server
Live Splunk MCP verified: true
Live Splunk verified: true
Local MCP SDK adapter verified: true
Official Splunk MCP Server verified: true
Current safe claim: Official Splunk MCP Server verified in local Splunk Enterprise Docker with synthetic data, plus local synthetic proof, SPL examples, local SPL-equivalent query evidence, and bounded claim validation.

Blocked claims until verified:
- production Splunk Cloud deployment completed
- Splunk MCP Server generated the final submitted decisions

Upgrade condition: Keep verified-through-Splunk-MCP wording bounded to the local Splunk Enterprise Docker proof with synthetic data; do not claim production Splunk Cloud deployment unless separate evidence is captured.

Evidence:
- `reports/latest_splunk_mcp_proof_brief.html` (present)
- `reports/latest_splunk_mcp_prompt_pack.html` (present)
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present)
- `reports/latest_claim_evidence_matrix.html` (present)
- `reports/latest_claim_boundary_validation.html` (present)

## Criteria

### Stage One Viability: Theme fit and required Splunk capability use

Readiness: strong_local_evidence
Ready: true

Official basis: The project should fit the Agentic Ops theme and reasonably apply Splunk AI, Splunk data, or MCP-style capabilities.

Judge message: Agentic Incident Command Center treats incident response as a Splunk-grounded evidence workflow, then uses an MCP Remediation Ledger to keep AI-proposed actions human-approved.

Evidence:
- `README.md` (present) - States the Agentic Incident Command Center thesis and Splunk-native framing.
- `architecture_diagram.md` (present) - Shows the Splunk data flow, AI/MCP investigation path, and approval boundary.
- `submission/SPLUNK_MCP_RUNBOOK.md` (present) - Explains the intended Splunk MCP Server integration path.
- `reports/latest_splunk_mcp_command_plan.html` (present) - Shows the live Splunk/MCP setup plan without executing it.
- `reports/latest_splunk_mcp_prompt_pack.html` (present) - Shows the exact evidence-backed prompts and stop conditions for optional MCP proof.
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present) - Shows the capture slots and readback gates for optional live MCP proof.

Remaining gate: Live Splunk/MCP proof still requires explicit user approval.

### Stage One Viability: Submission requirements

Readiness: local_ready_external_urls_pending
Ready: true

Official basis: The submission needs a public code URL, public demo video, description, track, architecture diagram, and runnable project materials.

Judge message: The local package contains the code, open-source license, architecture diagram, run instructions, demo script, public-candidate folder, and URL placeholders.

Evidence:
- `LICENSE` (present) - Open-source license candidate for the public repository.
- `reports/latest_devpost_final_copy.html` (present) - Copy/paste Devpost text with pending URL gates.
- `reports/latest_video_cue_sheet.html` (present) - Under-three-minute demo structure and screen-safety guardrails.
- `reports/latest_public_repo_publish_brief.html` (present) - Clean public repository publication evidence and stop conditions.
- `reports/latest_submission_url_validation.html` (present) - Shows repository/video URLs are pending until approved.

Remaining gate: Public repository URL and public demo video URL are still pending approval.

### Stage Two Judging: Technological Implementation

Readiness: strong_local_evidence
Ready: true

Official basis: Quality software development, consistent run behavior, and credible platform implementation.

Judge message: The implementation is deterministic, standard-library Python, testable locally, and produces Splunk-ready CSV, SPL-equivalent proof, a dashboard, and a packaged Splunk app candidate.

Evidence:
- `prototype/agentops_control_tower.py` (present) - Generates synthetic events, analysis, dashboard, SPL examples, and MCP preview.
- `tests/test_agentops_control_tower.py` (present) - Unit tests cover event generation and blocked/approval analysis.
- `reports/latest_local_spl_query_results.html` (present) - Shows the SPL query intent returns concrete synthetic event evidence.
- `reports/latest_splunk_app_package_manifest.html` (present) - Shows .spl package members and package integrity.
- `scripts/validate_submission_packet.py` (present) - Full local validator covering root, public candidate, scans, and smoke tests.

Remaining gate: Live Splunk import and MCP-assisted answer remain optional, post-approval proof.

### Stage Two Judging: Design

Readiness: strong_local_evidence
Ready: true

Official basis: User experience and design should be well thought out.

Judge message: The design is organized around the human reviewer workflow: identify risk, see evidence, decide approve/hold/block, and keep external actions gated.

Evidence:
- `reports/latest_control_tower.html` (present) - Main dashboard with KPIs, incident summary, approval queue, and MCP Remediation Ledger.
- `assets/dashboard_preview.png` (present) - Static preview for README and Devpost review.
- `reports/latest_demo_tour.html` (present) - Recording-friendly walkthrough showing the intended user path.
- `reports/latest_judge_quickstart.html` (present) - Five-minute review path for judges and final reviewers.

Remaining gate: Public video recording still needs approval and screen-safety readback.

### Stage Two Judging: Potential Impact

Readiness: strong_local_evidence
Ready: true

Official basis: The project should show meaningful impact for observability, security operations, or developer productivity.

Judge message: The pattern can apply to any agentic workflow where AI can notify, publish, deploy, access tools, or prepare sensitive actions faster than people can review them.

Evidence:
- `submission/DEVPOST_SUBMISSION_DRAFT.md` (present) - Frames the problem and practical value.
- `submission/REQUIREMENTS_MATRIX.md` (present) - Maps built artifacts to requirements and impact claims.
- `reports/latest_submission_gate_ledger.html` (present) - Shows how external action gates can be audited and reused.
- `reports/latest_post_action_evidence_brief.html` (present) - Defines completion evidence after public or submitted actions.

Remaining gate: Impact story is ready locally; public demo is still pending.

### Stage Two Judging: Quality of the Idea

Readiness: strong_local_evidence
Ready: true

Official basis: The project should be creative, unique, and clearly motivated.

Judge message: Most agent demos emphasize autonomy. This idea emphasizes operational control: Splunk becomes the evidence layer and MCP becomes a governed investigation interface.

Evidence:
- `submission/JUDGING_ALIGNMENT.md` (present) - Maps the idea to judging criteria and bonus alignment.
- `reports/latest_mcp_investigation.md` (present) - Shows evidence-backed investigation output with event IDs.
- `submission/SPL_QUERIES.md` (present) - Shows reusable query patterns for the AgentOps event model.
- `reports/latest_splunk_mcp_proof_brief.html` (present) - Defines how to upgrade claims after verified live proof.
- `reports/latest_splunk_mcp_prompt_pack.html` (present) - Defines the judge-visible MCP prompt/readback path with citations.
- `reports/latest_claim_evidence_matrix.html` (present) - Maps allowed public claims to evidence and avoid wording.

Remaining gate: Best-use-of-MCP claim should remain design/local-proof wording until live proof is approved.

### Bonus Alignment: Best Use of Splunk MCP Server

Readiness: local_design_ready_live_proof_pending
Ready: true

Official basis: Bonus prize fit depends on intelligent, agent-driven use of Splunk MCP Server for contextual insight and decisions.

Judge message: The package is built for Splunk MCP Server: an agent asks which operation needs human review first, and the answer cites event IDs, risk scores, policy decisions, and evidence references.

Evidence:
- `submission/SPLUNK_MCP_RUNBOOK.md` (present) - Post-approval runbook for Splunk MCP setup and proof capture.
- `reports/latest_splunk_mcp_command_plan.html` (present) - Command plan for synthetic import, app install, MCP setup, and proof.
- `reports/latest_splunk_mcp_proof_brief.html` (present) - Success criteria and stop conditions for live proof.
- `reports/latest_splunk_mcp_prompt_pack.html` (present) - Prompt pack with SPL, expected event citations, success readbacks, and safety stop conditions.
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present) - Capture manifest with approved scope, evidence slots, readback expectations, and claim-upgrade gate.
- `reports/latest_claim_evidence_matrix.html` (present) - Keeps MCP wording to designed-for/local-proof until live proof exists.
- `reports/latest_claim_boundary_validation.html` (present) - Checks that live Splunk/MCP claims are not overstated.

Remaining gate: Optional live Splunk/MCP proof requires explicit account/license/MCP approval.

## Boundary

This scorecard is local judging support only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.
