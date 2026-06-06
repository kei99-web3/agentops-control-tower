# Demo Video Dry Run

Status: ready_for_recording_review
Duration: 180 seconds
Scene count: 6
Final public video ready: false

## Dry Run Actions

- read video readiness report
- read video cue sheet and validate timeline
- read recording runbook and screen-safety guardrails
- scan planned recording files for internal paths and secret-like strings
- verify public URL and final submit gates remain closed

## Checks

- pass: video readiness status - ready_for_recording_review
- pass: video readiness failed count - 0
- pass: video readiness duration - 180
- pass: video readiness final gate - False
- pass: video cue status - ready_for_recording_review
- pass: video cue missing evidence - []
- pass: video cue duration - 180
- pass: video cue final gate - False
- pass: video command plan status - ready_for_user_review
- pass: content rights status - ready_for_user_review
- pass: recording evidence files - all required evidence present
- pass: video dry run scene count - 6
- pass: video dry run duration - end=180s
- pass: video dry run positive scene durations - all scenes positive
- pass: video dry run timeline continuity - continuous from 0:00
- pass: video dry run required beats - all required beats present
- pass: video dry run scene fields - screen, narration, and guardrail present for each scene
- pass: video dry run screen safety terms - screen safety terms present
- pass: video dry run boundary - This video dry run is local recording rehearsal only. It checks the prepared demo script, cue sheet, evidence files, screen-safety guardrails, and text scans without recording video, uploading video, publishing files, writing approved URLs, updating Devpost, or submitting anything.
- pass: video dry run live-claim boundary - no unsafe live-claim narration
- pass: video dry run Splunk MCP positioning - designed-for wording present
- pass: video dry run internal path scan - no internal paths
- pass: video dry run secret-like scan - no secret-like strings
- pass: video dry run approved URLs absent - approved_public_urls.json absent
- pass: video dry run URL gate closed - False
- pass: video dry run repo and video URLs pending - demo_video_url, repository_url
- pass: video dry run Go/No-Go final gate - False

## Boundary

This video dry run is local recording rehearsal only. It checks the prepared demo script, cue sheet, evidence files, screen-safety guardrails, and text scans without recording video, uploading video, publishing files, writing approved URLs, updating Devpost, or submitting anything.
