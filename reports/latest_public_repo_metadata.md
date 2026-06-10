# Public Repo Metadata

Status: ready_for_user_review
Root type: workspace
Repository name: `agentops-control-tower`
Visibility after approval: public
Description: Splunk-grounded AI incident commander with human-approved remediation.
License: Apache-2.0
Default branch: main
Candidate path: `public_repo_candidate/agentops-control-tower`
Final submit ready: false

## Topics

- `splunk`
- `agentops`
- `ai-agents`
- `observability`
- `mcp`
- `safety`
- `incident-response`
- `splunk-mcp`
- `autonomous-agents`
- `hackathon`

## Commands After Approval

### create_public_repository

```powershell
gh repo create agentops-control-tower --public --source . --remote origin --description "Splunk-grounded AI incident commander with human-approved remediation."
```

Create a public GitHub repository from isolated TEMP staging after explicit approval.

### apply_topics

```powershell
gh repo edit <owner>/agentops-control-tower --add-topic splunk --add-topic agentops --add-topic ai-agents --add-topic observability --add-topic mcp --add-topic safety --add-topic incident-response --add-topic splunk-mcp --add-topic autonomous-agents --add-topic hackathon
```

Apply discoverability topics after the repository exists.

### readback_metadata

```powershell
gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url,description,defaultBranchRef,licenseInfo,repositoryTopics,isPrivate
```

Read back visibility, URL, description, default branch, license, and topics.

## Expected Readback

- visibility: `PUBLIC`
- isPrivate: `False`
- description: `Splunk-grounded AI incident commander with human-approved remediation.`
- defaultBranchRef: `main`
- licenseInfo: `Apache-2.0`
- topics: `['splunk', 'agentops', 'ai-agents', 'observability', 'mcp', 'safety', 'incident-response', 'splunk-mcp', 'autonomous-agents', 'hackathon']`

## Evidence

- `public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present)
- `public_repo_candidate/agentops-control-tower/README.md` (present)
- `public_repo_candidate/agentops-control-tower/LICENSE` (present)
- `reports/latest_public_repo_publish_brief.html` (present)
- `reports/latest_public_repo_dry_run.html` (present)
- `reports/latest_public_launch_snapshot.html` (present)
- `reports/latest_release_integrity_manifest.html` (present)
- `reports/latest_release_zip_smoke_test.html` (present)

## Stop Conditions

- Do not create or edit a GitHub repository without the exact public GitHub approval phrase.
- Do not publish from the private workspace root.
- Do not publish if public candidate scans, release integrity, or ZIP smoke checks fail.
- Do not write approved URLs until public repository and public demo video URLs are both verified.
- Do not update Devpost or press submit from this step.

## Boundary

This metadata packet is local publication setup evidence only. It does not create a repository, edit GitHub metadata, push commits, publish files, write approved URLs, update Devpost, or submit anything.
