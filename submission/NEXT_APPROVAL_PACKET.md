# Next Approval Packet

Status: ready_for_user_review
Root type: workspace
Next approval target: approved_url_writeback
Local submission status: needs_more_evidence / failed_count 29 (reports/latest_submission_validation.json)
Final submit ready: true
Pending URLs: none

## Recommended Approval Order

1. Public GitHub Repository - hold
2. Public Demo Video - hold
3. Optional Live Splunk / MCP Proof - completed
4. Approved URL Writeback - ready_for_user_decision
5. Devpost Final Submission - ready_for_user_decision

## Copy-Paste Approval Phrases

### Public GitHub Repository

Status: hold
Approval phrase: `Approve public GitHub publication for the clean agentops-control-tower candidate.`

Purpose: Satisfy the public open-source repository requirement and give judges a runnable code package.
Exact operation: Run scripts/verify_public_repo_publication_gate.py with the exact approval phrase, public git identity, and manual safety confirmations, then use scripts/publish_public_repo_after_approval.py to create and push the public repository only after explicit approval.
After approval: Run the public repository publication preflight gate with the exact approval phrase, public git identity, and manual safety confirmations, then create and push the public repository through the guarded helper and record the public repository URL.
Main risk: Publishing the wrong folder or initializing Git inside the private workspace could expose private workspace material, local paths, or non-public artifacts.
Verification: Review reports/latest_public_repo_publication_preflight.html, open the public repository URL, rerun the public candidate scans and isolated staging dry run, then validate the URL before writing it locally.

Evidence:
- `reports/latest_judge_quickstart.html` (present)
- `reports/latest_publication_command_plan.html` (present)
- `reports/latest_public_repo_publish_brief.html` (present)
- `reports/latest_public_repo_publication_preflight.html` (present)
- `reports/latest_public_repo_dry_run.html` (present)
- `reports/latest_release_integrity_manifest.html` (present)
- `reports/latest_release_zip_smoke_test.html` (present)
- `public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present)

### Public Demo Video

Status: hold
Approval phrase: `Approve recording and public upload of the Agentic Incident Command Center demo video.`

Purpose: Give judges a fast walkthrough of the dashboard, local SPL proof, approval queue, and MCP Remediation Ledger.
Exact operation: Run scripts/verify_public_video_upload_gate.py with the exact approval phrase and manual safety confirmations, record the browser walkthrough using reports/latest_demo_tour.html and submission/VIDEO_RECORDING_RUNBOOK.md, then upload publicly only after explicit approval.
After approval: Run the public video upload preflight gate with the exact approval phrase and manual safety confirmations, record, review, and upload the public demo video, then record the public video URL.
Main risk: A recording could expose private tabs, local paths, accounts, credentials, or overstate live Splunk MCP proof.
Verification: Review reports/latest_public_video_upload_preflight.html, watch the uploaded public video end to end, confirm it is under 3 minutes and screen-safe, then validate the URL.

Evidence:
- `reports/latest_demo_tour.html` (present)
- `reports/latest_video_readiness.html` (present)
- `reports/latest_video_command_plan.html` (present)
- `reports/latest_public_video_upload_preflight.html` (present)
- `reports/latest_video_cue_sheet.html` (present)
- `reports/latest_content_rights_audit.html` (present)
- `submission/VIDEO_RECORDING_RUNBOOK.md` (present)

### Optional Live Splunk / MCP Proof

Status: completed
Approval phrase: `Approve optional live Splunk and Splunk MCP proof using synthetic data only.`

Purpose: Completed: strengthen the Best Use of Splunk MCP Server bonus claim with a local official-MCP proof using synthetic data only.
Exact operation: No further external setup is needed for the local official-MCP proof; keep claims bounded to local Splunk Enterprise Docker with synthetic data.
After approval: No further action required for the local official-MCP proof. Keep the claim bounded to local Splunk Enterprise Docker with synthetic data.
Main risk: Overclaiming production Splunk Cloud deployment or exposing credentials in video/screenshots.
Verification: Read submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md and rerun claim validation.

Evidence:
- `reports/latest_splunk_mcp_command_plan.html` (present)
- `reports/latest_splunk_mcp_proof_brief.html` (present)
- `reports/latest_splunk_mcp_prompt_pack.html` (present)
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present)
- `reports/latest_splunk_app_package_manifest.html` (present)
- `submission/SPLUNK_MCP_RUNBOOK.md` (present)
- `submission/SPLUNK_MCP_PROMPT_PACK.md` (present)
- `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md` (present)
- `submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md` (present)
- `data/splunk_agentops_events.csv` (present)

### Approved URL Writeback

Status: ready_for_user_decision
Approval phrase: `Approve writing the verified public repository and demo video URLs into local submission artifacts.`

Purpose: Replace pending URL placeholders only after both public URLs are real and approved.
Exact operation: Run prepare_submission_urls.py with both approved URLs and --write-approved, then rebuild final copy.
After approval: Run prepare_submission_urls.py with both approved URLs and --write-approved, then rebuild final copy.
Main risk: Writing unverified or private URLs could make the Devpost packet look ready when it is not.
Verification: Rerun URL validation and confirm final_submit_ready changes only when both public URLs pass.

Evidence:
- `reports/latest_submission_url_validation.html` (present)
- `reports/latest_submission_url_apply_plan.html` (present)
- `reports/latest_devpost_final_copy.html` (present)

### Devpost Final Submission

Status: ready_for_user_decision
Approval phrase: `Approve final Devpost submission for Agentic Incident Command Center.`

Purpose: Complete the hackathon submission after all required public artifacts and claim boundaries are verified.
Exact operation: After public repo and public video URLs are inserted and validation passes, review reports/latest_devpost_final_copy.md and press the Devpost submit button only with explicit final approval.
After approval: Use the Devpost command plan, fill fields, perform human readback, then press submit only after final approval.
Main risk: Submitting with pending URLs, wrong track, missing architecture evidence, or unverified live Splunk claims.
Verification: Read back the submitted Devpost page/status and save local post-submit evidence.

Evidence:
- `reports/latest_devpost_submit_command_plan.html` (present)
- `reports/latest_devpost_manual_fill_brief.html` (present)
- `reports/latest_post_action_evidence_brief.html` (present)
- `reports/latest_official_source_freshness.html` (present)
- `reports/latest_content_rights_audit.html` (present)
- `reports/latest_eligibility_compliance_audit.html` (present)
- `reports/latest_release_integrity_manifest.html` (present)
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` (present)
- `reports/latest_devpost_final_copy.html` (present)
- `reports/latest_final_go_no_go.html` (present)
- `submission/DEVPOST_FIELD_MAP.md` (present)

## Human Confirmations Before Devpost

### age_and_residence

Rule area: Eligibility
Confirm: Entrant is at least the age of majority where they reside and is not resident/domiciled in an excluded jurisdiction.
Why Codex cannot confirm: This depends on personal/legal facts and should be confirmed by the user before Devpost submission.

### no_excluded_role_or_conflict

Rule area: Eligibility and conflict of interest
Confirm: Entrant is not a judge, promotion entity, government/state-owned entity, excluded affiliate, household member, or otherwise conflicted participant.
Why Codex cannot confirm: This depends on employment, affiliation, household, and conflict facts outside the local packet.

### team_or_representative_authority

Rule area: Team representation
Confirm: If submitted as a team or organization, the submitter is authorized to act as the representative and the team size is within the rules.
Why Codex cannot confirm: The local packet does not know whether the Devpost entry will be individual, team, or organization.

### ownership_and_ip

Rule area: Submission ownership and IP
Confirm: The entrant owns the submitted work or has permission for every included component, and no third-party rights are violated.
Why Codex cannot confirm: The package can audit files and licenses, but final ownership representation belongs to the entrant.

### no_sponsor_support_conflict

Rule area: Financial or preferential support
Confirm: The project was not developed with prohibited financial or preferential support from Sponsor or Administrator.
Why Codex cannot confirm: This depends on external business, employment, funding, and contract facts.

## Boundary

This packet is local approval guidance only. It does not publish, upload, submit, create accounts, configure credentials, write approved URLs, or update Devpost.

## Recommended Next Step

Ask for public GitHub and public demo video approval first. Keep URL writeback and Devpost final submission blocked until both public URLs are verified.
