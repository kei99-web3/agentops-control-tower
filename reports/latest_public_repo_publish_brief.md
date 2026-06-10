# Public Repo Publish Brief

Status: ready_for_user_review
Candidate: .
Approval phrase: Approve public GitHub publication for the clean agentops-control-tower candidate.
Final submit ready: false

## ZIP Evidence

- Path: `release/agentops-control-tower-public-candidate.zip`
- Exists: False
- File count: 253
- Smoke status: not_applicable_public_candidate_root
- SHA256: ``

## Publish Steps After Approval

1. Review source folder

```powershell
manual: review current folder
```

Verification: Confirm this is the clean public candidate, not the private workspace root.

2. Run guarded publication rehearsal

```powershell
python scripts\publish_public_repo_after_approval.py
```

Verification: The helper validates an isolated audit copy, scans a clean publish copy, creates a local commit, and leaves no remote configured.

3. Run public repository publication preflight

```powershell
python scripts\verify_public_repo_publication_gate.py --approval-phrase "Approve public GitHub publication for the clean agentops-control-tower candidate." --source-folder-reviewed --isolated-staging-confirmed --secret-scan-confirmed --public-visibility-confirmed --public-git-identity-confirmed --git-user-name "<approved-public-git-name>" --git-user-email "<approved-public-git-email>"
```

Verification: Preflight must show ready_for_manual_public_repo_publication before any public repository creation.

4. Check public repository namespace

```powershell
gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url,isPrivate
```

Verification: If this resolves to an existing repository, stop and choose a new approved repo name or remove the stale repository before running the guarded helper.

5. Execute guarded public GitHub publication after explicit approval

```powershell
python scripts\publish_public_repo_after_approval.py --execute --approval-phrase "Approve public GitHub publication for the clean agentops-control-tower candidate." --repo-name agentops-control-tower --git-user-name "<approved-public-git-name>" --git-user-email "<approved-public-git-email>"
```

Verification: The helper accepts the exact approval phrase, creates the public repository, pushes main, and prints GitHub readback.

6. Read back public repository URL

```powershell
gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url
```

Verification: Visibility is PUBLIC and the URL opens without authentication.

7. Verify public artifact URLs after repo and video are public

```powershell
python scripts\verify_public_artifact_urls.py --repository-url <public-repo-url> --demo-video-url <public-video-url> --live-readback
```

Verification: URL readback confirms the GitHub repository is PUBLIC and the public video URL is reachable.

8. Hold URL writeback until video URL also exists

```powershell
manual: do not run prepare_submission_urls.py until both public repo and public video URLs are approved
```

Verification: submission/approved_public_urls.json remains absent until both URLs are approved.

## Stop Conditions

- Do not publish if the source path is not the clean public candidate.
- Do not publish from a git repository initialized inside the private workspace.
- Do not publish if internal path or secret-like scans fail.
- Do not write approved URLs until both public repository and public demo video URLs are verified.
- Do not press Devpost submit from this step.

## Boundary

This brief is local publication decision support only. It does not create a public repo, push commits, publish files, write approved URLs, upload video, update Devpost, or submit anything.
