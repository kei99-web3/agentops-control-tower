# User Approval Gates

This lane is local-only until the user approves each external step.

## Needs User Approval

- Any further Splunk Cloud, production Splunk, account, license, credential, or MCP setup beyond the completed local official-MCP proof.
- Public GitHub repository creation or publication.
- Public demo video upload to YouTube, Vimeo, or Youku.
- Devpost registration, draft save, or final submission.
- Any use of real private workspace logs.

## Does Not Need Approval

- Local synthetic data generation.
- Local dashboard build.
- Local README, architecture, demo script, and requirement matrix.
- Use of the completed official Splunk MCP Server proof as bounded evidence: local Splunk Enterprise Docker with synthetic data only.
- Private workspace commit/push for local artifacts.

## Recommended Approval Order

1. Approve public GitHub repository publication after the clean candidate, ZIP smoke test, isolated TEMP staging rehearsal, and secret/internal-path scans are reviewed.
2. Approve public demo video recording/upload after the demo tour, video readiness report, cue sheet, and screen-safety checklist are reviewed.
3. Approve local URL writeback only after both public URLs are real, public, and read back.
4. Approve Devpost final submission only after public URLs, final copy, eligibility confirmations, and post-action evidence steps are verified.

## Completed Proof To Reference

Official Splunk MCP proof is completed for local Splunk Enterprise Docker with synthetic `agentops_events` data. Use it in video and Devpost copy only with that boundary. Do not claim production Splunk Cloud deployment.
