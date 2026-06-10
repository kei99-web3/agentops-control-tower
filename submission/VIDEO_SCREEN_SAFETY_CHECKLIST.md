# Video Screen Safety Checklist

Status: pending screen safety review
Source report: `reports/latest_video_readiness.html`
Source runbook: `submission/VIDEO_RECORDING_RUNBOOK.md`

Use this file before screen recording and again before public upload approval.
Leave items unchecked until the final recording screen has been reviewed end to end.

## Screen Review Items

- [ ] Use synthetic data only.
- [ ] Close terminals that show private paths, tokens, account names, or unrelated files.
- [ ] Do not show `.env`, config files, API keys, OAuth tokens, or private logs.
- [ ] Do not show real customer, cloud, incident, identity, ticketing, or Splunk account screens.
- [ ] Keep the browser on the dashboard, SPL query examples, and public candidate files.
- [ ] The recording shows only the demo tour, dashboard, SPL examples, public candidate files, or the local Splunk Enterprise Docker official MCP proof screens.
- [ ] The voiceover uses `designed for Splunk MCP Server` for architecture and limits `verified through Splunk MCP Server` to the local synthetic-data proof.
- [ ] The final video duration is 180 seconds or less.

## Current Readiness

- Readiness status: `ready_for_recording_review`
- Scripted duration: `180s`
- Final public video ready: `false`

## Boundary

This checklist is local review evidence only. It does not record, upload, publish, write approved URLs, update Devpost, or submit anything.

## Final Upload Hold

Public video upload stays blocked until the user explicitly approves upload and this checklist has been completed against the final recording.
