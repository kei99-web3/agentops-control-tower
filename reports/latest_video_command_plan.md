# Demo Video Recording And Upload Command Plan

Status: ready_for_user_review
Root type: workspace

## Boundary

This command plan is advisory only. It does not record, upload, publish, write URLs, update Devpost, or submit anything.
Explicit user approval is required before recording capture, public video upload, or writing approved public URLs.

## Evidence

- reports/latest_demo_tour.html (present)
- reports/latest_video_readiness.html (present)
- reports/latest_video_readiness.json (present)
- reports/latest_video_recording_preview.html (present)
- reports/latest_video_recording_preview.json (present)
- reports/latest_video_upload_metadata.html (present)
- reports/latest_video_upload_metadata.json (present)
- reports/latest_public_video_upload_preflight.html (present)
- reports/latest_public_video_upload_preflight.json (present)
- submission/VIDEO_UPLOAD_METADATA.md (present)
- submission/DEMO_VIDEO_SCRIPT.md (present)
- submission/VIDEO_RECORDING_RUNBOOK.md (present)
- reports/latest_external_approval_packet.html (present)
- reports/latest_submission_url_apply_plan.html (present)
- reports/latest_public_artifact_url_readback.html (present)
- reports/latest_public_artifact_url_readback.json (present)
- reports/latest_devpost_final_copy.md (present)
- reports/latest_submission_validation.html (present)
- reports/latest_release_zip_smoke_test.html (present)

## Commands After Approval

### Refresh safe demo tour

Regenerate the browser walkthrough used for the recording path.

```powershell
python scripts\build_demo_tour.py
```

### Refresh video readiness

Confirm timing, screen safety, claim wording, and upload approval gate.

```powershell
python scripts\build_video_readiness_report.py
```

### Build screen-safe localhost recording preview

Copy the public candidate to an isolated temporary preview stage, scan recording files, and produce a localhost preview command template.

```powershell
python scripts\build_video_recording_preview.py
```

### Review video upload metadata

Confirm the upload title, description, tags, visibility, expected readback, and public video stop conditions before any upload.

```powershell
python scripts\build_video_upload_metadata.py
```

### Public video upload preflight gate

Require the exact public demo video approval phrase plus screen, duration, claim, rights, and visibility confirmations before manual capture or upload.

```powershell
python scripts\verify_public_video_upload_gate.py --approval-phrase "Approve recording and public upload of the Agentic Incident Command Center demo video." --screen-safety-confirmed --duration-confirmed --claim-boundary-confirmed --content-rights-confirmed --upload-visibility-confirmed
```

### Open recording review artifacts

Review the demo path, readiness report, localhost preview preflight, upload metadata, and public video upload gate before any capture.

```powershell
start reports\latest_demo_tour.html && start reports\latest_video_readiness.html && start reports\latest_video_recording_preview.html && start reports\latest_video_upload_metadata.html && start reports\latest_public_video_upload_preflight.html
```

### Capture local recording after approval

Record only the approved browser path with synthetic data and no private screens.

```powershell
manual: record reports\latest_demo_tour.html using submission\VIDEO_RECORDING_RUNBOOK.md
```

### Review recording before upload

Hold upload if private paths, credentials, account pages, or live Splunk/MCP overclaims appear.

```powershell
manual: watch the recording and check duration, screen safety, and claim wording
```

### Upload public video after approval

Create the public Devpost video URL only after explicit approval.

```powershell
manual: upload the reviewed video to an approved public video host and capture the URL
```

### Verify public artifact URLs before writeback

Confirm the public GitHub repository and public demo video URL are reachable before writing them into local submission artifacts.

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
