# Submission Gate Ledger

Status: ready_for_user_review
Root type: public_candidate
Local ready: true
Final submit ready: false

This ledger records the external gates that still need human approval before submission.

## Gates

### Public GitHub Repository

Status: ready_for_user_decision

Approval required: Explicit approval is required before creating a public repository or pushing files.

Next safe action: Review the publication command plan and hold until the public repository decision is explicit.

Verification: After approval, confirm the public URL opens, then rerun URL validation and the submission packet validator.

Evidence:
- PUBLIC_REPO_CANDIDATE_MANIFEST.md (present)
- reports/latest_external_approval_packet.html (present)
- reports/latest_publication_command_plan.html (present)
- reports/latest_submission_url_apply_plan.html (present)

### Public Demo Video

Status: ready_for_user_decision

Approval required: Explicit approval is required before recording, uploading, or making the video public.

Next safe action: Review the video readiness report and command plan, then record only after the screen safety check is complete.

Verification: Confirm the uploaded video is public, under 3 minutes, and does not expose private screens or overclaim live Splunk MCP proof.

Evidence:
- reports/latest_demo_tour.html (present)
- reports/latest_video_readiness.html (present)
- reports/latest_video_command_plan.html (present)
- submission/VIDEO_RECORDING_RUNBOOK.md (present)

### Optional Live Splunk / MCP Proof

Status: optional_user_decision

Approval required: Explicit approval is required before Splunk account/license use, credential setup, data import, app install, MCP setup, or proof capture.

Next safe action: Use the Splunk MCP command plan, prompt pack, and proof capture manifest if the optional bonus proof is approved.

Verification: Capture live SPL and MCP evidence, then rerun claim-boundary validation before strengthening any bonus wording.

Evidence:
- reports/latest_splunk_mcp_command_plan.html (present)
- reports/latest_splunk_mcp_proof_brief.html (present)
- reports/latest_splunk_mcp_prompt_pack.html (present)
- reports/latest_splunk_mcp_proof_capture_manifest.html (present)
- submission/SPLUNK_MCP_RUNBOOK.md (present)
- submission/SPLUNK_MCP_PROMPT_PACK.md (present)
- submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md (present)
- submission/SPL_QUERIES.md (present)
- data/splunk_agentops_events.csv (present)
- splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml (present)

### Approved URL Writeback

Status: blocked_until_public_urls

Approval required: Explicit approval is required before writing verified public URLs into local submission artifacts.

Next safe action: Wait until the public repository and demo video URLs are real, public, and read back.

Verification: Run prepare_submission_urls.py with both approved URLs, then rerun URL validation and final copy export.

Evidence:
- reports/latest_submission_url_validation.html (present)
- reports/latest_submission_url_apply_plan.html (present)
- reports/latest_devpost_final_copy.html (present)
- reports/latest_final_go_no_go.html (present)

### Devpost Final Submission

Status: blocked_until_public_urls

Approval required: Explicit final approval is required before using a Devpost session, saving a draft, or pressing submit.

Next safe action: Wait for public repo and video URLs, write approved URL evidence only after approval, then review final copy.

Verification: Confirm approved public URLs, safe claim wording, selected track, architecture evidence, and final submit readback.

Evidence:
- reports/latest_devpost_final_copy.html (present)
- reports/latest_devpost_submit_command_plan.html (present)
- reports/latest_devpost_manual_fill_brief.html (present)
- reports/latest_post_action_evidence_brief.html (present)
- reports/latest_submission_url_validation.html (present)
- reports/latest_final_go_no_go.html (present)
- submission/DEVPOST_FIELD_MAP.md (present)
- submission/SUBMISSION_LAUNCH_RUNBOOK.md (present)

## Recommended Order

- Review this Submission Gate Ledger and the External Approval Packet.
- Approve or hold public GitHub publication.
- Approve or hold public demo video recording/upload.
- Optionally approve live Splunk/MCP proof if the bonus path is worth the account and credential work.
- After public URLs are approved, write approved URL evidence locally and rerun validation.
- Only then request final Devpost submit approval.

## Boundary

This ledger is advisory only. It does not create a repo, upload a video, create accounts, configure credentials, write approved URLs, update Devpost, or submit anything.
