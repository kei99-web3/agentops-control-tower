# Public Repository Publication Command Plan

Status: ready_for_user_review
Candidate: .

## Boundary

This command plan is advisory only. It does not create a repo, push commits, publish files, write URLs, upload videos, or submit Devpost.

## Evidence

- README.md (present)
- LICENSE (present)
- PUBLIC_REPO_CANDIDATE_MANIFEST.md (present)
- reports/latest_external_approval_packet.html (present)
- reports/latest_submission_url_apply_plan.html (present)
- reports/latest_public_artifact_url_readback.html (present)
- reports/latest_video_readiness.html (present)
- reports/latest_devpost_final_copy.md (present)
- reports/latest_final_go_no_go.html (present)
- splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml (present)

## Commands After Approval

### Run guarded publication rehearsal

Copy the clean candidate into isolated TEMP audit/publish stages, run local validation, scan the publish stage, and create a local commit with no remote.

```powershell
python scripts\publish_public_repo_after_approval.py
```

### Run public repository publication preflight

Confirm the exact approval phrase, source-folder review, staging policy, scan status, public visibility, and public git identity before any public repository creation.

```powershell
python scripts\verify_public_repo_publication_gate.py --approval-phrase "Approve public GitHub publication for the clean agentops-control-tower candidate." --source-folder-reviewed --isolated-staging-confirmed --secret-scan-confirmed --public-visibility-confirmed --public-git-identity-confirmed --git-user-name "<approved-public-git-name>" --git-user-email "<approved-public-git-email>"
```

### Check public repository namespace

Read the target GitHub namespace immediately before execution; stop if the repo name already resolves to an existing public or private repository.

```powershell
gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url,isPrivate
```

### Execute guarded public repo publication after approval

Create and push the public GitHub repository only after the exact approval phrase and public git identity are supplied.

```powershell
python scripts\publish_public_repo_after_approval.py --execute --approval-phrase "Approve public GitHub publication for the clean agentops-control-tower candidate." --repo-name agentops-control-tower --git-user-name "<approved-public-git-name>" --git-user-email "<approved-public-git-email>"
```

### Read back public repo

Verify the repo is public and capture the URL for Devpost.

```powershell
gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url
```

### Verify public artifact URLs after repo and video are public

Confirm the public GitHub repository and public demo video URL are reachable before local approved URL writeback.

```powershell
python scripts\verify_public_artifact_urls.py --repository-url <public-repo-url> --demo-video-url <public-video-url> --live-readback
```

### Apply approved URLs locally

Update the local Devpost URL source only after both public URLs are approved.

```powershell
python scripts\prepare_submission_urls.py --repository-url <public-repo-url> --demo-video-url <public-video-url> --write-approved --approval-note "user approved public URLs"
```

### Final local validation

Confirm the submission packet is ready for final Devpost review.

```powershell
python scripts\validate_submission_packet.py
```
