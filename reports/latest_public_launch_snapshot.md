# Public Launch Snapshot

Status: needs_more_evidence
Root type: workspace
Next approval target: approved_url_writeback
Ready now: approved_url_writeback, devpost_final_submission
Final submit ready: true
Approved public URLs file exists: true

## Approval Phrases

- public_github_repository: `Approve public GitHub publication for the clean agentops-control-tower candidate.`
- public_demo_video: `Approve recording and public upload of the Agentic Incident Command Center demo video.`
- approved_url_writeback: `Approve writing the verified public repository and demo video URLs into local submission artifacts.`
- devpost_final_submission: `Approve final Devpost submission for Agentic Incident Command Center.`

## Release ZIP

- Path: `release/agentops-control-tower-public-candidate.zip`
- Exists: True
- File count: 250
- SHA256: `769db8778a993757aed1600062dde25a9daff8280ede4097aaf8554c5cea0ea9`
- Smoke status: fail

## Checks

- required evidence present: pass (all required evidence present)
- next approval target is public repo: fail (approved_url_writeback)
- public repo and video are ready now: fail (approved_url_writeback, devpost_final_submission)
- public repo approval ready: fail (False)
- public repo publication preflight ready and blocked: fail (status=needs_more_evidence allowed=False gate=needs_more_evidence)
- video recording review ready: pass (ready_for_recording_review)
- public video upload preflight ready and blocked: fail (status=needs_more_evidence allowed=False gate=needs_more_evidence)
- video cue under three minutes: pass (180)
- video dry run ready: fail (status=needs_more_evidence failed=4)
- URL writeback dry run ready: fail (status=needs_more_evidence failed=3 wrote=True)
- approval order matches expected: fail (public_github_repository, public_demo_video, approved_url_writeback, devpost_final_submission)
- official Splunk MCP proof completed: pass (submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md)
- release ZIP exists: pass (True)
- release ZIP smoke passed: fail (fail)
- release ZIP SHA256 present: pass (769db8778a993757aed1600062dde25a9daff8280ede4097aaf8554c5cea0ea9)
- approved public URLs not written: fail (True)
- final submit remains false: fail (True)
- content rights ready: pass (ready_for_user_review)
- post-action evidence remains incomplete before externals: fail (True)
- no external action boundary: pass (This public launch snapshot is local approval evidence only. It does not publish a repository, record or upload video, connect to Splunk, configure MCP, write approved URLs, update Devpost, save a draft, press submit, or mark the submission complete.)

## Evidence

- `public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present) - clean public candidate folder boundary
- `reports/latest_release_zip_smoke_test.html` (present) - extract-and-test proof for the release ZIP
- `reports/latest_public_candidate_zip_manifest.html` (present) - release ZIP file list
- `release/agentops-control-tower-public-candidate.zip` (present) - local release ZIP for user review
- `reports/latest_public_repo_dry_run.html` (present) - isolated TEMP staging git-init/commit rehearsal for the clean public candidate
- `reports/latest_video_dry_run.html` (present) - local recording rehearsal and screen-safety scan
- `reports/latest_url_writeback_dry_run.html` (present) - temporary-copy rehearsal for approved URL writeback
- `reports/latest_next_approval_packet.html` (present) - copy-paste approval phrases and human confirmations
- `reports/latest_public_repo_publish_brief.html` (present) - public repo approval boundary and ZIP evidence
- `reports/latest_public_repo_publication_preflight.html` (present) - public repo approval phrase and manual publication gate
- `reports/latest_video_readiness.html` (present) - screen-safe recording readiness
- `reports/latest_video_command_plan.html` (present) - post-approval recording/upload plan
- `reports/latest_public_video_upload_preflight.html` (present) - public video approval phrase and manual confirmation gate
- `reports/latest_video_cue_sheet.html` (present) - under-3-minute scene timing
- `reports/latest_approval_consistency_audit.html` (present) - approval order consistency
- `reports/latest_release_integrity_manifest.html` (present) - artifact hashes and no-publish boundary
- `reports/latest_content_rights_audit.html` (present) - license, media, and screen safety
- `reports/latest_submission_url_validation.html` (present) - pending public URL gates
- `reports/latest_post_action_evidence_brief.html` (present) - readback plan after approved external actions
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` (present) - local evidence log template

## Boundary

This public launch snapshot is local approval evidence only. It does not publish a repository, record or upload video, connect to Splunk, configure MCP, write approved URLs, update Devpost, save a draft, press submit, or mark the submission complete.
