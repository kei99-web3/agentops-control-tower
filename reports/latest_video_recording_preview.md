# Demo Video Recording Preview

Status: needs_more_evidence
Candidate: `public_repo_candidate/agentops-control-tower`
Preview URL: `http://127.0.0.1:8765/reports/latest_demo_tour.html`
Server command template: `python -m http.server 8765 --bind 127.0.0.1 --directory <recording-stage>`
Stage removed after run: true

## Public Video Safe Readback

- Evidence note target: `submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md`
- Screen safety checklist: `submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md`
- Duration seconds: `180`
- Screen scan: 7 scanned, 0 missing, 0 internal-path hits, 0 secret-like hits
- Ready for public upload: false
- Copy policy: Use this public_video_safe_readback block plus a short manual final-recording review summary for post-action evidence. Do not copy raw recording output, account screenshots, browser tabs, credentials, tokens, or local absolute paths.

## Checks

- pass: candidate source exists - <local-path>
- pass: candidate source is public candidate - <local-path>
- pass: stage root under system temp - <local-path>
- pass: stage root outside private workspace - <local-path>
- pass: recording stage isolated - <local-path>
- pass: recording required files - all required files present
- pass: video readiness status - ready_for_recording_review
- pass: video cue status - ready_for_recording_review
- pass: video duration under three minutes - cue=180 readiness=180
- pass: approved URL writeback absent - approved_public_urls.json absent
- fail: submission URLs still pending - 
- pass: recording screen internal path scan - no internal paths
- pass: recording screen secret-like scan - no secret-like strings

## Boundary

This recording preview is local preparation only. It copies the reviewed public candidate to an isolated temporary folder, scans the recording files, and provides a localhost preview command template without recording video, uploading video, publishing files, writing approved URLs, updating Devpost, or submitting anything.
