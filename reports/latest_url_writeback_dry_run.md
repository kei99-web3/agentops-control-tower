# URL Writeback Dry Run

Status: ready_for_user_review
Final submit ready in temp: true
Approved URLs written to working tree: false
Verified readback passed in temp: true

## Sample URLs

- Repository: https://github.com/example/agentops-control-tower
- Demo video: https://youtu.be/agentops-control-tower-demo

## Checks

- pass: working tree approved URL file absent before dry run - approved_public_urls.json absent
- pass: temp block approved sample URLs without verified readback - {
  "status": "needs_more_evidence",
  "final_submit_ready": true,
  "approved_urls_file_written": false,
  "html": "reports/latest_submission_url_apply_plan.html",
  "markdown": "reports/latest_submission_url_apply_plan.md",
  "json": "reports/latest_submission_url_apply_plan.json"
}
- pass: temp approved URL file absent before verified readback - approved_public_urls.json absent
- pass: temp write approved sample URLs - {
  "status": "ready_to_submit_after_user_approval",
  "final_submit_ready": true,
  "approved_urls_file_written": true,
  "html": "reports/latest_submission_url_apply_plan.html",
  "markdown": "reports/latest_submission_url_apply_plan.md",
  "json": "reports/latest_submission_url_apply_plan.json"
}
- pass: temp validate submission URLs - {
  "status": "ready_to_submit_after_user_approval",
  "final_submit_ready": true,
  "pending_urls": []
}
- pass: temp rebuild Devpost submission packet - {
  "status": "local_draft_not_submitted",
  "html": "reports/latest_devpost_submission_packet.html",
  "json": "reports/latest_devpost_submission_packet.json"
}
- pass: temp export Devpost final copy - {
  "status": "ready_for_user_review",
  "final_submit_ready": true,
  "pending_urls": [],
  "markdown": "reports/latest_devpost_final_copy.md",
  "html": "reports/latest_devpost_final_copy.html",
  "json": "reports/latest_devpost_final_copy.json"
}
- pass: temp rebuild final Go/No-Go - {
  "status": "ready_to_submit_after_user_approval",
  "html": "reports/latest_final_go_no_go.html",
  "json": "reports/latest_final_go_no_go.json"
}
- pass: temp rebuild Devpost submit plan - {
  "status": "ready_for_user_review",
  "final_submit_ready": true,
  "html": "reports/latest_devpost_submit_command_plan.html",
  "markdown": "reports/latest_devpost_submit_command_plan.md",
  "json": "reports/latest_devpost_submit_command_plan.json"
}
- pass: temp rebuild Devpost manual fill brief - {
  "status": "ready_for_user_review",
  "final_submit_ready": true,
  "pending_fields": [],
  "html": "reports/latest_devpost_manual_fill_brief.html",
  "markdown": "reports/latest_devpost_manual_fill_brief.md",
  "json": "reports/latest_devpost_manual_fill_brief.json",
  "final_review_checklist": "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md"
}
- pass: temp rebuild post-action evidence brief - {
  "status": "ready_for_user_review",
  "post_action_evidence_ready": true,
  "incomplete_actions": [],
  "html": "reports/latest_post_action_evidence_brief.html",
  "markdown": "reports/latest_post_action_evidence_brief.md",
  "json": "reports/latest_post_action_evidence_brief.json"
}
- pass: temp approved URL file exists - submission/approved_public_urls.json
- pass: temp repository URL matches sample - https://github.com/example/agentops-control-tower
- pass: temp demo video URL matches sample - https://youtu.be/agentops-control-tower-demo
- pass: URL apply plan wrote only in temp - True
- pass: URL apply plan required verified readback in temp - True
- pass: URL apply plan accepted verified readback in temp - True
- pass: URL validation ready in temp - []
- pass: Devpost final copy ready in temp - []
- pass: Go/No-Go final ready in temp - True
- pass: Devpost submit plan final ready in temp - True
- pass: Devpost manual fill has no pending URL fields in temp - []
- pass: Post-action brief sees approved URLs in temp - True
- pass: working tree approved URL file still absent after dry run - approved_public_urls.json absent

## Boundary

This URL writeback dry run uses sample public URL shapes inside a temporary local copy only. It does not publish a repository, upload video, write approved URLs to the working tree, update Devpost, save a draft, press submit, or submit anything.
