# Public Repo Dry Run

Status: ready_for_user_review
Candidate: `.`
Candidate files: 253
Final submit ready: false
Approved public URLs file exists: false
Git staged file count: 253
Git tracked file count after commit: 253
Git branch: main
Git commit created: true
Staging location policy: system_temp_outside_private_workspace
Staging isolated from private workspace: true

## Dry Run Actions

- copy public candidate to an isolated temporary staging folder outside the private workspace
- run git init -b main without remote
- configure a temporary local git identity
- run git add -A
- run a local git commit rehearsal
- inspect git status --short
- scan temporary copy for internal paths and secret-like strings

## Checks

- pass: candidate source exists - .
- pass: candidate required files - all required files present
- pass: candidate top-level allowlist - top-level entries expected
- pass: candidate has no git directory - .git absent
- pass: candidate has no release directory - release absent
- pass: approved URL writeback absent - approved_public_urls.json absent
- pass: approval phrase stable - Approve public GitHub publication for the clean agentops-control-tower candidate.
- pass: snapshot final gate closed - False
- pass: URL validation final gate closed - False
- pass: Go/No-Go final gate closed - False
- pass: pending repo and video URLs - repository_url, demo_video_url
- pass: staging copy outside private workspace - outside private workspace
- pass: git init main-branch rehearsal - Initialized empty Git repository in <local-path>
- pass: git branch rehearsal uses main - main
- pass: git remote list remains empty - no remotes
- pass: git dry-run user.name configured - ok
- pass: git dry-run user.email configured - ok
- pass: git add rehearsal - 168 line-ending warnings suppressed
- pass: git status rehearsal - 253 staged files
- pass: git status has no private workspace names - clean
- pass: git commit rehearsal - reate mode 100644 submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md
 create mode 100644 submission/SPLUNK_MCP_RUNBOOK.md
 create mode 100644 submission/SPL_QUERIES.md
 create mode 100644 submission/SUBMISSION_DEADLINE_BURNDOWN.md
 create mode 100644 submission/SUBMISSION_LAUNCH_RUNBOOK.md
 create mode 100644 submission/SUBMISSION_REVIEW_QA.md
 create mode 100644 submission/USER_APPROVAL_GATES.md
 create mode 100644 submission/VIDEO_RECORDING_RUNBOOK.md
 create mode 100644 submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md
 create mode 100644 submission/VIDEO_UPLOAD_METADATA.md
 create mode 100644 submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md
 create mode 100644 tests/test_agentops_control_tower.py
 create mode 100644 tests/test_submission_safety_boundaries.py
- pass: git commit hash exists - 879573302da8
- pass: git tracked files rehearsal - tracked=253 staged=253
- pass: git post-commit status clean - clean
- pass: git remote remains empty after commit - no remotes
- pass: rehearsal internal path scan - no internal patterns
- pass: rehearsal secret-like scan - no secret-like patterns

## Boundary

This dry run is local publication rehearsal only. It copies the reviewed public candidate to an isolated temporary staging folder outside the private workspace and runs git init/add/commit/status without creating a remote, pushing commits, publishing files, writing approved URLs, uploading video, updating Devpost, or submitting anything.
