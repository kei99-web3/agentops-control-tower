# User Approval Gates

This lane is local-only until the user approves each external step.

## Needs User Approval

- Splunk account creation.
- Splunk Enterprise trial or Splunk Cloud access.
- Splunk Developer License request.
- Any Splunk MCP Server credential, token, app install, or cloud configuration.
- Public GitHub repository creation or publication.
- Public demo video upload to YouTube, Vimeo, or Youku.
- Devpost registration, draft save, or final submission.
- Any use of real private workspace logs.

## Does Not Need Approval

- Local synthetic data generation.
- Local dashboard build.
- Local README, architecture, demo script, and requirement matrix.
- Private workspace commit/push for local artifacts.

## Recommended Approval Order

1. Approve public GitHub repository publication after the clean candidate, ZIP smoke test, isolated TEMP staging rehearsal, and secret/internal-path scans are reviewed.
2. Approve public demo video recording/upload after the demo tour, video readiness report, cue sheet, and screen-safety checklist are reviewed.
3. Optionally approve live Splunk/MCP proof using synthetic data only, after account/license, credential scope, and cost boundaries are accepted.
4. Approve local URL writeback only after both public URLs are real, public, and read back.
5. Approve Devpost final submission only after public URLs, final copy, eligibility confirmations, and post-action evidence steps are verified.
