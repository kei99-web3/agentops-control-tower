# Public Launch Snapshot

Status: ready_for_user_review
Root type: public_candidate
Next approval target: public_github_repository
Ready now: public_github_repository, public_demo_video
Final submit ready: false
Approved public URLs file exists: false

## Approval Phrases

- public_github_repository: `Approve public GitHub publication for the clean agentops-control-tower candidate.`
- public_demo_video: `Approve recording and public upload of the Agentic Incident Command Center demo video.`
- optional_live_splunk_mcp_proof: `Approve optional live Splunk and Splunk MCP proof using synthetic data only.`
- approved_url_writeback: `Approve writing the verified public repository and demo video URLs into local submission artifacts.`
- devpost_final_submission: `Approve final Devpost submission for Agentic Incident Command Center.`

## Release ZIP

- Path: `release/agentops-control-tower-public-candidate.zip`
- Exists: False
- File count: None
- SHA256: ``
- Smoke status: not_applicable_public_candidate_root

## Checks

- required evidence present: pass (all required evidence present)
- next approval target is public repo: pass (public_github_repository)
- public repo and video are ready now: pass (public_demo_video, public_github_repository)
- public repo approval ready: pass (True)
- public repo publication preflight ready and blocked: pass (status=ready_for_user_review allowed=False gate=blocked_by_public_repo_approval_gate)
- video recording review ready: pass (ready_for_recording_review)
- public video upload preflight ready and blocked: pass (status=ready_for_user_review allowed=False gate=blocked_by_video_approval_gate)
- video cue under three minutes: pass (180)
- video dry run ready: pass (not_applicable_public_candidate_root)
- URL writeback dry run ready: pass (not_applicable_public_candidate_root)
- approval order matches expected: pass (public_github_repository, public_demo_video, optional_live_splunk_mcp_proof, approved_url_writeback, devpost_final_submission)
- release ZIP status: pass (not_applicable_public_candidate_root)
- approved public URLs not written: pass (False)
- final submit remains false: pass (False)
- content rights ready: pass (ready_for_user_review)
- post-action evidence remains incomplete before externals: pass (False)
- no external action boundary: pass (This public launch snapshot is local approval evidence only. It does not publish a repository, record or upload video, connect to Splunk, configure MCP, write approved URLs, update Devpost, save a draft, press submit, or mark the submission complete.)

## Evidence

- `PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present) - clean public candidate boundary
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
