# Post-Action Evidence Brief

Status: ready_for_user_review
Root type: public_candidate
Final submit ready: false
Post-action evidence ready: false
Approved public URLs file exists: false

## Boundary

This brief is local post-action evidence guidance only. It does not publish a repository, record or upload video, connect to Splunk, configure MCP, write approved URLs, update Devpost, save a draft, press submit, or mark the submission complete.

## Actions

### Public GitHub Repository

Status: waiting_for_user_approval
Evidence note target: `submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md`
Safe readback source: Use the public_safe_readback block from scripts/publish_public_repo_after_approval.py JSON output.

Readback command: `gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url`

Completion evidence:
- Public repository URL opens without authentication.
- Repository visibility readback is PUBLIC.
- README, LICENSE, architecture diagram, source, reports, and Splunk app candidate are present.
- Public candidate internal path and secret-like scans pass after publication.
- Repository URL is recorded only after the user approves URL writeback.

Stop condition: Stop if the URL points to a private workspace repository or the wrong folder was published.

### Public Demo Video

Status: waiting_for_user_approval
Evidence note target: `submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md`
Safe readback source: Use the public_video_upload_safe_readback block from reports/latest_public_video_upload_preflight.json, the public_video_safe_readback block from reports/latest_video_recording_preview.json, plus a short manual final-recording review summary.

Readback command: `manual: open the video URL, watch end to end, and save the verified URL in the approved URL packet only after approval`

Completion evidence:
- Public video upload preflight gate allowed manual recording/upload only after the exact approval phrase and manual safety confirmations.
- Uploaded video URL opens publicly or with the approved visibility.
- Duration is under 3 minutes.
- Recording shows only the prepared demo surfaces and no private tabs, local paths, credentials, or billing/account pages.
- Narration does not claim live Splunk/MCP proof unless that proof is separately verified.
- Demo video URL is recorded only after the user approves URL writeback.

Stop condition: Stop if the recording exposes private screens or overstates live Splunk/MCP verification.

### Optional Live Splunk / MCP Proof

Status: live_splunk_mcp_verified
Evidence note target: `submission/post_action_evidence/YYYY-MM-DD_optional_live_splunk_mcp_proof_readback.md`
Safe readback source: Use the proof capture summary from submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md with synthetic event IDs only.

Readback command: `manual: follow submission/SPLUNK_MCP_RUNBOOK.md and reports/latest_splunk_mcp_proof_capture_manifest.html before changing wording`

Completion evidence:
- Splunk account/license and MCP setup were explicitly approved before use.
- Only synthetic AgentOps data was imported.
- SPL queries return concrete synthetic event IDs.
- MCP-assisted answer cites the same synthetic event evidence.
- Proof capture manifest slots are completed and read back before any claim wording upgrade.
- Claim-boundary validation passes after any wording upgrade.

Stop condition: Stop if credentials, costs, private data, or unapproved live Splunk/MCP scope would be exposed.

### Approved URL Writeback

Status: blocked_until_public_urls
Evidence note target: `submission/post_action_evidence/YYYY-MM-DD_approved_url_writeback_readback.md`
Safe readback source: Use the public_safe_readback block from reports/latest_public_artifact_url_readback.json after live URL readback passes.

Readback command: `python scripts\verify_public_artifact_urls.py --repository-url <public_repo_url> --demo-video-url <public_video_url> --live-readback && python scripts\prepare_submission_urls.py --repository-url <public_repo_url> --demo-video-url <public_video_url> --write-approved --approval-note "user approved public URLs" && python scripts\validate_submission_packet.py`

Completion evidence:
- submission/approved_public_urls.json exists only after explicit approval.
- repository_url and demo_video_url are both approved public URLs.
- reports/latest_submission_url_validation.json returns final_submit_ready true.
- reports/latest_devpost_final_copy.json no longer contains pending URL placeholders.
- Final Go/No-Go moves to final_submit_ready true only after both URLs validate.

Stop condition: Stop if either URL is missing, private, unapproved, or still a PENDING_USER_APPROVAL placeholder.

### Devpost Final Submission

Status: blocked_until_public_urls
Evidence note target: `submission/post_action_evidence/YYYY-MM-DD_devpost_final_submission_readback.md`
Safe readback source: Use the devpost_final_submit_safe_readback block from reports/latest_devpost_final_submit_preflight.json before submit; after submit, add a short manual Devpost submitted page/status summary only.

Readback command: `manual: after explicit approval, submit Devpost, read back the submitted page/status, and store local evidence`

Completion evidence:
- Final submit approval is explicit in the current thread.
- Final submit preflight gate allows manual submit only after final_submit_ready, exact approval phrase, and manual readback confirmations.
- Devpost fields match reports/latest_devpost_final_copy.md and submission/DEVPOST_FIELD_MAP.md.
- Selected track and bonus target match the launch decision brief.
- Submitted Devpost page/status is read back after pressing submit.
- A local post-submit evidence note captures the submitted URL/status without secrets or account screenshots.
- submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md is copied or filled as the local post-action evidence note.

Stop condition: Stop if final_submit_ready is false, public URLs are pending, or claim wording has not passed validation.

## Final Readback Sequence

- Read the public GitHub repository URL and visibility.
- Watch the public demo video and confirm screen safety.
- Optionally read back live Splunk/MCP proof against reports/latest_splunk_mcp_proof_capture_manifest.html only after approved setup.
- Validate approved URL writeback and final copy placeholders.
- Fill the post-action evidence log template with approved URLs, status, and validation readback.
- Read back the submitted Devpost page/status after explicit final approval.

## Evidence Log Policy

- Recommended directory: `submission/post_action_evidence/`
- Filename pattern: `YYYY-MM-DD_<action_key>_readback.md`
- Write policy: Create a dated local evidence note only after explicit user approval, external action completion, and completion readback.
- Public candidate policy: Keep completed evidence notes private/local by default. Include them in a public candidate only after a separate review confirms they contain no credentials, tokens, account screenshots, billing or OAuth screens, local absolute paths, private workspace material, private logs, or customer data.
- Required fields: approval evidence, completion readback, verification command or check, evidence file or URL, claim wording impact, status
- Forbidden content: credentials, tokens, account screenshots, billing pages, OAuth screens, local absolute paths, private workspace material, private logs, customer data

## Local Evidence

- All required local evidence for this brief is present.
