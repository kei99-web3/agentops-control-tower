# Public Video Upload Preflight

Status: needs_more_evidence
Gate status: needs_more_evidence
Public video upload allowed: false
Approval phrase accepted: false
Duration seconds: 180

## Safe Readback

- Evidence note target: submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md
- Screen safety checklist: submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md
- Ready for public upload: false
- Copy policy: Use this pre-upload safe readback plus the recording-preview safe readback and a short manual final-recording review summary. Do not copy screenshots, browser state, account pages, raw recording output, credentials, tokens, or local absolute paths.

## Gate Issues

- recording preview safe readback must pass without internal paths or secret-like hits
- approval phrase is required before manual recording or public upload
- manual screen, duration, claim, rights, and visibility confirmations are required before upload

## Manual Confirmations

- screen_safety_confirmed: false
- duration_confirmed: false
- claim_boundary_confirmed: false
- content_rights_confirmed: false
- upload_visibility_confirmed: false

## Boundary

This public video upload gate is a local preflight only. It does not record video, upload video, publish media, open accounts, write approved URLs, update Devpost, connect to Splunk, configure MCP, or submit anything.
