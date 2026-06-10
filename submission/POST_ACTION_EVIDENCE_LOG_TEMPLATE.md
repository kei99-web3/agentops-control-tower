# Post-Action Evidence Log Template

Status: template only, no external action completed

Use this template only after the relevant action has explicit user approval and has actually been performed. Keep it as local readback evidence; do not include credentials, account screenshots, private browser tabs, local absolute paths, private logs, billing pages, OAuth screens, tokens, or customer data.

## Boundary

This template does not publish a repository, upload a video, connect to Splunk, configure MCP, write approved URLs, update Devpost, save a draft, press submit, or mark the submission complete.

## How To Fill

1. Copy this file to `submission/post_action_evidence/YYYY-MM-DD_<action_key>_readback.md` after the approved action is complete.
2. Fill only the action sections that were actually completed.
3. Keep every URL, visibility state, status, and command output as a short readback summary.
4. Run `python scripts\validate_submission_packet.py` after URL writeback or claim wording changes.
5. Do not mark final submission complete until the Devpost submitted page/status has been read back.

## Evidence Log Policy

- Recommended directory: `submission/post_action_evidence/`
- Filename pattern: `YYYY-MM-DD_<action_key>_readback.md`
- Write policy: create a dated local evidence note only after explicit user approval, external action completion, and completion readback.
- Public candidate policy: Keep completed evidence notes private/local by default. Include them in a public candidate only after a separate review confirms they contain no credentials, tokens, account screenshots, billing or OAuth screens, local absolute paths, private workspace material, private logs, or customer data.
- Required fields: approval evidence, completion readback, verification command or check, evidence file or URL, claim wording impact, status.
- Forbidden content: credentials, tokens, account screenshots, billing pages, OAuth screens, local absolute paths, private workspace material, private logs, customer data.

## Evidence Log

| Action | Approval evidence | Completion readback | Verification command or check | Evidence file or URL | Claim wording impact | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Public GitHub Repository | PENDING_USER_APPROVAL | PENDING_READBACK | `gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url` | PENDING_PUBLIC_REPO_URL | Repo is public only after visibility readback is PUBLIC. | pending |
| Public Demo Video | PENDING_USER_APPROVAL | PENDING_READBACK | Open the video URL, watch end to end, confirm duration under 3 minutes and screen safety. | PENDING_PUBLIC_VIDEO_URL | Video is public only after URL and screen-safety readback. | pending |
| Optional Live Splunk / MCP Proof | PENDING_USER_APPROVAL | PENDING_READBACK | Follow `submission/SPLUNK_MCP_RUNBOOK.md`; cite synthetic event IDs and evidence refs. | PENDING_LIVE_PROOF_NOTE | Use "verified through Splunk MCP Server" only after approved proof capture and claim validation. | optional |
| Approved URL Writeback | PENDING_USER_APPROVAL | PENDING_READBACK | `python scripts\verify_public_artifact_urls.py --repository-url <public_repo_url> --demo-video-url <public_video_url> --live-readback` then `python scripts\prepare_submission_urls.py --repository-url <public_repo_url> --demo-video-url <public_video_url> --write-approved --approval-note "user approved public URLs"` then `python scripts\validate_submission_packet.py` | `submission/approved_public_urls.json` | Devpost copy can replace pending URL placeholders only after public URL readback and validation. | pending |
| Devpost Final Submission | PENDING_USER_APPROVAL | PENDING_READBACK | Manual Devpost readback after pressing submit with explicit approval. | PENDING_DEVPOST_SUBMITTED_URL_OR_STATUS | Submission is complete only after submitted page/status readback. | pending |

## Preferred Evidence Note Targets

- Public GitHub Repository: `submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md`
- Public Demo Video: `submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md`
- Optional Live Splunk / MCP Proof: `submission/post_action_evidence/YYYY-MM-DD_optional_live_splunk_mcp_proof_readback.md`
- Approved URL Writeback: `submission/post_action_evidence/YYYY-MM-DD_approved_url_writeback_readback.md`
- Devpost Final Submission: `submission/post_action_evidence/YYYY-MM-DD_devpost_final_submission_readback.md`

## Safe Readback Sources

- Public GitHub Repository: use the `public_safe_readback` block from `scripts/publish_public_repo_after_approval.py` JSON output.
- Public Demo Video: use the `public_video_upload_safe_readback` block from `reports/latest_public_video_upload_preflight.json`, the `public_video_safe_readback` block from `reports/latest_video_recording_preview.json`, plus a short manual final-recording review summary.
- Approved URL Writeback: use the `public_safe_readback` block from `reports/latest_public_artifact_url_readback.json`.
- Optional Live Splunk / MCP Proof: use short manual readback summaries only; do not copy screenshots, raw account output, private browser state, credentials, tokens, or local absolute paths.
- Devpost Final Submission: use the `devpost_final_submit_safe_readback` block from `reports/latest_devpost_final_submit_preflight.json` before submit, then add a short manual submitted page/status summary after submit; do not copy account screenshots, private browser state, credentials, tokens, or local absolute paths.

## Public Repository Readback

- Approved by:
- Approval timestamp:
- Repository URL:
- Repository visibility readback:
- Public candidate scan result:
- README/LICENSE/architecture/source present:
- Notes:

## Public Video Readback

- Approved by:
- Approval timestamp:
- Video URL:
- Visibility readback:
- Duration:
- Screen safety result:
- Claim wording result:
- Notes:

## Optional Splunk / MCP Proof Readback

- Approved by:
- Approval timestamp:
- Splunk environment type:
- Synthetic data import evidence:
- SPL query evidence:
- MCP answer evidence:
- Claim-boundary validation result:
- Notes:

## URL Writeback Readback

- Approved by:
- Approval timestamp:
- Repository URL written:
- Demo video URL written:
- `submission/approved_public_urls.json` exists:
- `reports/latest_submission_url_validation.json` status:
- `reports/latest_devpost_final_copy.json` pending URL placeholders:
- `reports/latest_final_go_no_go.json` final_submit_ready:
- Notes:

## Devpost Final Submit Readback

- Approved by:
- Approval timestamp:
- Submitted Devpost URL or status:
- Pre-submit gate readback:
- Track selected:
- Bonus selected or omitted:
- Repository URL field:
- Demo video URL field:
- Final copy matched local packet:
- Submitted page/status read back:
- Notes:

## Final Completion Criteria

Before anyone says the submission is complete, all required items below must be true:

- Public GitHub repository URL is approved, public, and read back.
- Public demo video URL is approved, openable, under 3 minutes, and screen-safe.
- Approved URL writeback validation returns `final_submit_ready: true`.
- Claim boundary validation passes after any wording changes.
- Devpost fields match the local final copy packet.
- Final Devpost submit action was explicitly approved.
- Submitted Devpost page/status was read back and recorded locally.
