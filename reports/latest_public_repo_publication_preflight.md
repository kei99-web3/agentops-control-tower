# Public Repo Publication Preflight

Status: needs_more_evidence
Gate status: needs_more_evidence
Public repo publication allowed: false
Approval phrase accepted: false

## Safe Readback

- Evidence note target: submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md
- Candidate path: `public_repo_candidate/agentops-control-tower`
- Expected visibility: `PUBLIC`
- Ready for publication: false
- Preflight command: `python scripts\verify_public_repo_publication_gate.py --approval-phrase "Approve public GitHub publication for the clean agentops-control-tower candidate." --source-folder-reviewed --isolated-staging-confirmed --secret-scan-confirmed --public-visibility-confirmed --public-git-identity-confirmed --git-user-name "<approved-public-git-name>" --git-user-email "<approved-public-git-email>"`
- Execute command: `python scripts\publish_public_repo_after_approval.py --execute --approval-phrase "Approve public GitHub publication for the clean agentops-control-tower candidate." --repo-name agentops-control-tower --git-user-name "<approved-public-git-name>" --git-user-email "<approved-public-git-email>"`
- Copy policy: Use this pre-publication safe readback plus the guarded helper safe_readback after publication. Do not copy stage_root, audit_stage, publish_stage, raw command output, credentials, tokens, or local absolute paths.

## Gate Issues

- public repo publish brief must be ready and approval-ready
- isolated public repo dry run must pass before publication
- repository_url must still be pending before publication
- approved URL writeback must remain absent before public repo publication
- final submit must remain blocked until public URLs are verified
- approval phrase is required before public repository publication
- manual source, staging, scan, visibility, and git identity confirmations are required

## Manual Confirmations

- source_folder_reviewed: false
- isolated_staging_confirmed: false
- secret_scan_confirmed: false
- public_visibility_confirmed: false
- public_git_identity_confirmed: false

## Evidence

- `public_repo_candidate/agentops-control-tower/.gitattributes` (present)
- `public_repo_candidate/agentops-control-tower/README.md` (present)
- `public_repo_candidate/agentops-control-tower/LICENSE` (present)
- `public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present)
- `reports/latest_publication_command_plan.html` (present)
- `reports/latest_publication_command_plan.json` (present)
- `reports/latest_public_repo_metadata.html` (present)
- `reports/latest_public_repo_metadata.json` (present)
- `reports/latest_public_repo_publish_brief.html` (present)
- `reports/latest_public_repo_publish_brief.json` (present)
- `reports/latest_public_repo_dry_run.html` (present)
- `reports/latest_public_repo_dry_run.json` (present)
- `reports/latest_submission_url_validation.html` (present)
- `reports/latest_submission_url_validation.json` (present)
- `reports/latest_public_artifact_url_readback.html` (present)
- `reports/latest_public_artifact_url_readback.json` (present)
- `scripts/publish_public_repo_after_approval.py` (present)
- `submission/PUBLIC_REPO_METADATA.md` (present)
- `submission/USER_APPROVAL_GATES.md` (present)

## Boundary

This public repository publication gate is a local preflight only. It does not create a repository, push commits, publish files, write approved URLs, upload video, update Devpost, press submit, or submit anything.
