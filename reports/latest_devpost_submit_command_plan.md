# Devpost Final Submission Command Plan

Status: ready_for_user_review
Root type: public_candidate
Final submit ready: false
Pending URLs: repository_url, demo_video_url

## Boundary

This command plan is advisory only. It does not log in, save a draft, press submit, update Devpost, publish, upload, write URLs, or submit anything.
Explicit user approval is required before using a Devpost account/session, saving a Devpost draft, or pressing the final submit button.

## Evidence

- reports/latest_devpost_submission_packet.html (present)
- reports/latest_devpost_submission_packet.json (present)
- reports/latest_devpost_final_copy.html (present)
- reports/latest_devpost_final_copy.md (present)
- reports/latest_devpost_final_copy.json (present)
- reports/latest_devpost_final_submit_preflight.html (present)
- reports/latest_devpost_final_submit_preflight.json (present)
- reports/latest_submission_url_validation.html (present)
- reports/latest_submission_url_validation.json (present)
- reports/latest_submission_url_apply_plan.html (present)
- reports/latest_final_go_no_go.html (present)
- reports/latest_final_go_no_go.json (present)
- reports/latest_external_approval_packet.html (present)
- reports/latest_video_command_plan.html (present)
- reports/latest_publication_command_plan.html (present)
- submission/DEVPOST_FIELD_MAP.md (present)
- submission/FINAL_SUBMISSION_CHECKLIST.md (present)
- submission/OFFICIAL_REQUIREMENTS_AUDIT.md (present)
- submission/SUBMISSION_LAUNCH_RUNBOOK.md (present)

## Commands After Approval

### Refresh Devpost packet

Regenerate local Devpost field evidence before copying anything into Devpost.

```powershell
python scripts\build_devpost_submission_packet.py
```

### Refresh final copy

Regenerate copy/paste text and character checks.

```powershell
python scripts\export_devpost_final_copy.py
```

### Validate public URLs

Confirm repository and video URLs are either still pending or valid approved public URLs.

```powershell
python scripts\validate_submission_urls.py
```

### Refresh Go/No-Go

Confirm whether the package is local-ready and whether final submit is still blocked by external gates.

```powershell
python scripts\build_final_go_no_go_report.py
```

### Final local validation

Re-run the full local submission validator before touching the Devpost form.

```powershell
python scripts\validate_submission_packet.py
```

### Open final review artifacts

Review fields, URL state, claim boundaries, and final gate before any Devpost session.

```powershell
start reports\latest_devpost_final_copy.html && start reports\latest_final_go_no_go.html && start reports\latest_submission_url_validation.html
```

### Fill Devpost form after approval

Populate the form only after account/session use is approved.

```powershell
manual: copy fields from reports\latest_devpost_final_copy.md into Devpost; select Platform & Developer Experience; attach architecture_diagram.md; use only approved public repo/video URLs
```

### Pre-submit human review

Hold submission if pending URLs, unsafe Splunk MCP claims, wrong track, or missing architecture evidence remain.

```powershell
manual: compare Devpost screen against submission\DEVPOST_FIELD_MAP.md and reports\latest_devpost_final_copy.md
```

### Final submit preflight gate

Require final_submit_ready, exact final approval phrase, and manual readback confirmations before the submit button is pressed.

```powershell
python scripts\verify_devpost_final_submit_gate.py --final-approval-phrase "Approve final Devpost submission for Agentic Incident Command Center." --field-map-readback-confirmed --human-confirmations-completed --video-screen-safety-confirmed --post-action-evidence-plan-reviewed
```

### Submit after explicit final approval

Complete the external submission only when the final approval gate is satisfied.

```powershell
manual: press the Devpost submit button only after explicit final user approval
```

### Post-submit readback

Create a local audit trail after the external submit action has actually completed.

```powershell
manual: capture the Devpost submitted URL/status and save local evidence after submission
```
