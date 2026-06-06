# Video Upload Metadata

Status: ready_for_user_review
Root type: public_candidate
Title: Agentic Incident Command Center: Splunk-grounded AI incident response
Platform: approved public video host
Visibility after approval: public
Duration limit: 180 seconds
Observed local plan duration: 180 seconds
Public video URL: PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL
Final public video ready: false

## Description

Agentic Incident Command Center is a Splunk-grounded AI incident commander for modern operations teams.

This demo uses synthetic checkout-incident events to show how deploy, APM, database, network, security, and MCP-adjacent signals can be correlated into one incident timeline.

The MCP Remediation Ledger keeps evidence references attached to each proposed action so operators can see the ranked root cause, blast radius, blocked credential-boundary attempt, and the remediation steps that still require human approval. The project is designed for Splunk MCP Server workflows; live Splunk/MCP verification should only be claimed after explicit approval and captured proof.

Repository and Devpost links should be added only after public URL readback has passed.

## Tags

- `Splunk`
- `AgentOps`
- `AI agents`
- `MCP`
- `observability`
- `incident response`
- `human approval`
- `hackathon`

## Safe Claim Boundary

Say designed for Splunk MCP Server unless approved live Splunk/MCP proof has been captured and validated.

## Upload Steps After Approval

### review_recording_path

Confirm the capture path is synthetic-data-only and screen safe before recording.

```text
Open reports/latest_demo_tour.html, reports/latest_video_cue_sheet.html, and reports/latest_video_recording_preview.html.
```

### record_after_approval

Capture the demo only after explicit recording approval.

```text
Record the approved browser path using submission/VIDEO_RECORDING_RUNBOOK.md.
```

### screen_safety_review

Block upload if private screens, account pages, local paths, credentials, or overclaims appear.

```text
Watch the final recording end to end and check submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md.
```

### upload_after_approval

Create the public demo video URL only after explicit public upload approval.

```text
Upload to an approved public video host using the title, description, tags, and visibility in this packet.
```

### public_url_readback

Confirm the public repo and demo video are both reachable before approved URL writeback.

```text
Run python scripts\verify_public_artifact_urls.py --repository-url <public-repo-url> --demo-video-url <public-video-url> --live-readback.
```

## Expected Readback

- video_url: `openable public video URL`
- visibility: `public`
- title: `Agentic Incident Command Center: Splunk-grounded AI incident response`
- duration_seconds_max: `180`
- screen_safety_checklist: `completed before upload approval`
- description_contains: `['synthetic checkout-incident events', 'MCP Remediation Ledger', 'human approval']`

## Evidence

- `reports/latest_video_readiness.html` (present)
- `reports/latest_video_readiness.json` (present)
- `reports/latest_video_command_plan.html` (present)
- `reports/latest_video_cue_sheet.html` (present)
- `reports/latest_video_recording_preview.html` (present)
- `reports/latest_content_rights_audit.html` (present)
- `reports/latest_public_artifact_url_readback.html` (present)
- `reports/latest_post_action_evidence_brief.html` (present)
- `submission/DEMO_VIDEO_SCRIPT.md` (present)
- `submission/VIDEO_RECORDING_RUNBOOK.md` (present)
- `submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md` (present)

## Stop Conditions

- Do not record until the recording path and script are reviewed.
- Do not upload if the recording shows private paths, credentials, account pages, private logs, or unrelated workspace content.
- Do not claim live Splunk MCP verification unless the optional live proof gate is approved and captured.
- Do not write approved URLs until the public repo and demo video URLs both pass readback.
- Do not update Devpost or press submit from this step.

## Boundary

This video upload metadata packet is local review evidence only. It does not record video, upload video, publish media, write approved URLs, update Devpost, connect to Splunk, configure MCP, or submit anything.
