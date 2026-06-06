# Submission Deadline Burndown

Status: ready_for_user_review
Root type: public_candidate
Target submit by: 2026-06-15 20:00 JST
Official deadline: 2026-06-16 01:00 JST
Days until target submit: 8.91
Days until official deadline: 9.12
Urgency: on_track
Local validation: ready_for_user_review / failed_count 0
Local validation source: `reports/latest_final_go_no_go.json`
Local validation note: Public candidate inherits the workspace release validation through the final Go/No-Go evidence bundled in the candidate.
Final submit ready: false

## Minimum Viable Submit Path

- Approve and publish the clean public GitHub repository.
- Approve recording and public upload of the under-3-minute demo video.
- Verify both public URLs, then approve local URL writeback.
- Complete human confirmations and Devpost final review checklist.
- Rerun validation and submit on Devpost only after explicit final approval.

## Stretch Path

- Approve optional live Splunk/MCP proof only if account scope, credential handling, and time are safe.
- Use synthetic data only and upgrade claim wording only after proof cites event IDs and evidence references.

## Milestones

### Public GitHub Repository

- Key: `public_github_repository`
- Status: ready_for_user_decision
- Due: 2026-06-09 20:00 JST
- Owner: entrant
- Approval phrase: `Approve public GitHub publication for the clean agentops-control-tower candidate.`
- Blocker: Needs explicit public GitHub publication approval.
- Notes: This is the first required external artifact. Publish only from the clean staged candidate after approval.
- Evidence:
  - `reports/latest_public_repo_publish_brief.html` (present)
  - `reports/latest_release_integrity_manifest.html` (present)
  - `PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present)

### Public Demo Video

- Key: `public_demo_video`
- Status: ready_for_user_decision
- Due: 2026-06-10 20:00 JST
- Owner: entrant
- Approval phrase: `Approve recording and public upload of the Agentic Incident Command Center demo video.`
- Blocker: Needs explicit recording and public upload approval.
- Notes: Record and upload only after screen-safety review. Keep the video under 3 minutes.
- Evidence:
  - `reports/latest_demo_tour.html` (present)
  - `reports/latest_video_readiness.html` (present)
  - `reports/latest_video_command_plan.html` (present)
  - `reports/latest_public_video_upload_preflight.html` (present)
  - `submission/VIDEO_RECORDING_RUNBOOK.md` (present)
  - `submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md` (present)

### Optional Live Splunk / MCP Proof

- Key: `optional_live_splunk_mcp_proof`
- Status: optional_user_decision
- Due: 2026-06-11 20:00 JST
- Owner: entrant
- Approval phrase: `Approve optional live Splunk and Splunk MCP proof using synthetic data only.`
- Blocker: Optional. Needs explicit approval, account scope, credentials, and synthetic-data-only guardrails.
- Notes: Skip if it risks cost, credential exposure, or deadline slip. The local submission remains viable without live proof.
- Evidence:
  - `reports/latest_splunk_mcp_command_plan.html` (present)
  - `reports/latest_splunk_mcp_proof_brief.html` (present)
  - `reports/latest_splunk_mcp_prompt_pack.html` (present)
  - `reports/latest_splunk_mcp_proof_capture_manifest.html` (present)
  - `submission/SPLUNK_MCP_PROMPT_PACK.md` (present)
  - `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md` (present)

### Approved URL Writeback

- Key: `approved_url_writeback`
- Status: blocked_until_public_urls
- Due: 2026-06-13 20:00 JST
- Owner: Codex after approval
- Approval phrase: `Approve writing the verified public repository and demo video URLs into local submission artifacts.`
- Blocker: Blocked until both public repository and public demo video URLs are verified.
- Notes: Write approved URLs only after both public artifacts are public and read back.
- Evidence:
  - `reports/latest_submission_url_validation.html` (present)
  - `reports/latest_submission_url_apply_plan.html` (present)
  - `reports/latest_public_artifact_url_readback.html` (present)

### Devpost Final Submission

- Key: `devpost_final_submission`
- Status: blocked_until_public_urls
- Due: 2026-06-15 20:00 JST
- Owner: entrant
- Approval phrase: `Approve final Devpost submission for Agentic Incident Command Center.`
- Blocker: Blocked until public URLs, human confirmations, final checklist, validation, and explicit final approval are complete.
- Notes: Submit before the target time, then read back the submitted Devpost page/status into local evidence.
- Evidence:
  - `reports/latest_devpost_final_copy.md` (present)
  - `reports/latest_devpost_manual_fill_brief.html` (present)
  - `submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md` (present)
  - `submission/HUMAN_CONFIRMATION_CHECKLIST.md` (present)
  - `reports/latest_final_go_no_go.html` (present)

## Boundary

This burndown is local planning evidence only. It does not publish a repository, record or upload video, connect to Splunk, configure MCP, write approved URLs, update Devpost, save a draft, press submit, or submit anything.
