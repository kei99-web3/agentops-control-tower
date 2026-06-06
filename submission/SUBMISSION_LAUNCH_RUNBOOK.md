# Submission Launch Runbook

Status: local launch plan, not submitted
Last updated: 2026-06-03 JST

Use this runbook when moving Agentic Incident Command Center from local evidence to the final Devpost submission. It keeps the external steps explicit so the project does not accidentally claim live Splunk, public repository, public video, or submitted status before those gates are approved and verified.

## Current State

- Local prototype, dashboard, query proof, Splunk app candidate, Devpost draft, public repo candidate, and validation reports are prepared.
- Official deadline: 2026-06-15 09:00 PDT / 2026-06-16 01:00 JST.
- Recommended submit target: before 2026-06-15 20:00 JST.
- Public repository URL, public video URL, live Splunk proof, Splunk MCP Server proof, and Devpost final submission are still pending user approval.

## Preflight Commands

Run from the project root:

```powershell
python prototype\agentops_control_tower.py run-demo
python scripts\run_local_spl_query_pack.py
python scripts\build_demo_tour.py
python scripts\build_video_readiness_report.py
python scripts\build_video_cue_sheet.py
python scripts\build_video_upload_metadata.py
python scripts\build_video_command_plan.py
python scripts\build_claim_evidence_matrix.py
python scripts\build_external_approval_packet.py
python scripts\build_publication_command_plan.py
python scripts\build_public_repo_metadata.py
python scripts\build_public_repo_publish_brief.py
python scripts\build_public_launch_snapshot.py
python scripts\build_devpost_submission_packet.py
python scripts\export_devpost_final_copy.py
python scripts\build_final_go_no_go_report.py
python scripts\build_devpost_submit_command_plan.py
python scripts\build_devpost_manual_fill_brief.py
python scripts\build_post_action_evidence_brief.py
python scripts\build_official_source_freshness.py
python scripts\build_release_integrity_manifest.py
python scripts\package_public_candidate_zip.py
python scripts\smoke_test_release_zip.py
python scripts\prepare_submission_urls.py
python scripts\validate_claim_boundaries.py
python scripts\validate_submission_urls.py
python scripts\validate_splunk_app.py
python scripts\package_splunk_app.py
python scripts\build_splunk_mcp_command_plan.py
python scripts\build_splunk_mcp_proof_brief.py
python scripts\build_splunk_mcp_prompt_pack.py
python scripts\build_splunk_mcp_proof_capture_manifest.py
python scripts\build_submission_gate_ledger.py
python scripts\build_submission_deadline_burndown.py
python scripts\build_submission_review_index.py
python scripts\build_judge_quickstart.py
python scripts\build_judge_scorecard.py
python scripts\build_launch_decision_brief.py
python scripts\build_content_rights_audit.py
python scripts\build_eligibility_compliance_audit.py
python scripts\build_next_approval_packet.py
python scripts\build_approval_consistency_audit.py
python scripts\build_status_conflict_audit.py
python -m unittest discover -s tests
python -m py_compile prototype\agentops_control_tower.py scripts\build_demo_tour.py scripts\build_video_readiness_report.py scripts\build_video_command_plan.py scripts\build_video_cue_sheet.py scripts\build_video_upload_metadata.py scripts\build_external_approval_packet.py scripts\build_publication_command_plan.py scripts\build_public_repo_metadata.py scripts\build_public_repo_publish_brief.py scripts\build_public_launch_snapshot.py scripts\build_splunk_mcp_command_plan.py scripts\build_splunk_mcp_proof_brief.py scripts\build_splunk_mcp_prompt_pack.py scripts\build_splunk_mcp_proof_capture_manifest.py scripts\build_submission_gate_ledger.py scripts\build_submission_deadline_burndown.py scripts\build_submission_review_index.py scripts\build_judge_quickstart.py scripts\build_judge_scorecard.py scripts\build_launch_decision_brief.py scripts\build_content_rights_audit.py scripts\build_eligibility_compliance_audit.py scripts\build_next_approval_packet.py scripts\build_approval_consistency_audit.py scripts\build_status_conflict_audit.py scripts\build_devpost_submission_packet.py scripts\build_devpost_submit_command_plan.py scripts\build_devpost_manual_fill_brief.py scripts\build_post_action_evidence_brief.py scripts\build_official_source_freshness.py scripts\build_release_integrity_manifest.py scripts\build_final_go_no_go_report.py scripts\build_public_repo_candidate.py scripts\export_devpost_final_copy.py scripts\package_splunk_app.py scripts\package_public_candidate_zip.py scripts\prepare_submission_urls.py scripts\run_local_spl_query_pack.py scripts\submission_urls.py scripts\smoke_test_release_zip.py scripts\validate_claim_boundaries.py scripts\validate_submission_urls.py scripts\validate_splunk_app.py scripts\validate_submission_packet.py
python scripts\validate_submission_packet.py
```

Expected result:

- `reports/latest_submission_validation.html` shows `ready_for_user_review`.
- `reports/latest_devpost_final_copy.html` and `.md` show copy/paste-ready Devpost text with pending URL gates.
- `reports/latest_submission_url_validation.html` shows pending URL gates or validates approved public URLs.
- `reports/latest_video_readiness.html` shows under-3-minute timing, screen safety, safe claim wording, and the upload approval gate.
- `submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md` keeps recording screen-safety checks pending until final recording review and public upload approval.
- `reports/latest_video_command_plan.html` shows post-approval recording, review, upload, and URL update steps without executing them.
- `reports/latest_video_cue_sheet.html` shows the exact 3-minute timeline, screen focus, narration cue, and screen-safety guardrail for each scene.
- `reports/latest_video_upload_metadata.html` shows the public demo video title, description, tags, visibility, readback expectations, and no-upload boundary.
- `reports/latest_claim_evidence_matrix.html` maps public claims to evidence, allowed wording, avoid wording, and remaining approval gates.
- `reports/latest_external_approval_packet.html` shows the exact external operations, benefits, risks, and verification steps before any publication, upload, or submit action.
- `reports/latest_publication_command_plan.html` shows post-approval public repo commands and their verification steps without executing them.
- `reports/latest_public_repo_metadata.html` shows the public repo name, description, topics, expected GitHub readback, and no-publish boundary.
- `reports/latest_public_repo_publish_brief.html` shows the clean candidate path, approval phrase, ZIP evidence, SHA256, stop conditions, and URL writeback hold.
- `reports/latest_public_launch_snapshot.html` freezes the repo/video approval phrases, ZIP hash, expected approval order, final-submit false gate, and no-external-action boundary.
- `reports/latest_splunk_mcp_command_plan.html` shows post-approval Splunk account/license, synthetic import, app install, MCP setup, live SPL checks, proof capture, and claim-upgrade steps without executing them.
- `reports/latest_splunk_mcp_proof_brief.html` shows live proof success criteria, screen safety checks, stop conditions, the approval phrase, and the claim-upgrade rule.
- `reports/latest_splunk_mcp_prompt_pack.html` shows exact proof prompts, SPL, expected event citations, success readbacks, and stop conditions.
- `reports/latest_splunk_mcp_proof_capture_manifest.html` shows capture slots, expected readback, stop conditions, pending live proof state, and claim-upgrade gate.
- `reports/latest_splunk_app_package_manifest.html` shows the local `.spl` package, package members, sha256, and the no-install/no-upload boundary.
- `reports/latest_submission_gate_ledger.html` shows public repo, video, optional Splunk/MCP proof, and Devpost final submission approval gates in one ledger.
- `reports/latest_submission_deadline_burndown.html` shows target submit timing, official deadline, minimum viable submit path, optional live proof stretch path, and blocked final submit gate.
- `reports/latest_submission_review_index.html` shows the recommended review order and links the key local evidence artifacts.
- `reports/latest_judge_quickstart.html` shows the 5-minute review path, local commands, key evidence, and no-publish/no-upload/no-submit boundary.
- `reports/latest_judge_scorecard.html` maps Stage One, Stage Two, and bonus alignment to concrete evidence and remaining external gates.
- `reports/latest_launch_decision_brief.html` shows the recommended approval order, approval phrases, ready public repo/video decisions, blocked URL/Devpost gates, and no-external-action boundary.
- `reports/latest_content_rights_audit.html` shows Apache-2.0 license, bundled asset inventory, no bundled audio/video media, screen-safety evidence, and public video still gated.
- `reports/latest_eligibility_compliance_audit.html` shows automated package evidence and the human confirmations required before final submission.
- `submission/HUMAN_CONFIRMATION_CHECKLIST.md` lists the entrant-only personal/legal confirmations and keeps Devpost final submission blocked until they are checked.
- `reports/latest_next_approval_packet.html` shows the next approval target, copy-paste approval phrases, and pre-Devpost human confirmations.
- `reports/latest_approval_consistency_audit.html` confirms public repo/video are first, optional Splunk/MCP proof is not first, and stale Splunk-first guidance is absent.
- `reports/latest_status_conflict_audit.html` confirms no stale failed statuses, nonzero failed counts, or missing local artifacts remain in JSON reports.
- `reports/latest_devpost_submit_command_plan.html` shows post-approval Devpost form fill, final review, submit, and readback steps without executing them.
- `reports/latest_devpost_manual_fill_brief.html` shows field-by-field fill order, section readback, pending URL fields, final readback checks, and stop conditions.
- `submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md` keeps the final visible Devpost screen review pending until track, public URLs, claim boundaries, human confirmations, video safety, validation, and explicit final approval are checked.
- `reports/latest_post_action_evidence_brief.html` shows completion/readback evidence required after public repo, video, URL writeback, optional Splunk/MCP proof, and Devpost final submission.
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` is ready to copy or fill after approved external actions are completed.
- `reports/latest_official_source_freshness.html` shows the latest official Devpost source check, expected deadline, required artifacts, judging criteria, and local evidence mapping.
- `reports/latest_release_integrity_manifest.html` shows key artifact SHA256, sizes, ZIP count consistency, `.spl` hash consistency, and the no-publish/no-submit boundary.
- `reports/latest_submission_url_apply_plan.html` shows pending URLs or validates approved public URLs without writing unless explicitly requested.
- `reports/latest_claim_boundary_validation.html` shows no unqualified live Splunk/MCP overclaims.
- `reports/latest_final_go_no_go.html` shows local readiness and the remaining external gates.
- `release/agentops-control-tower-public-candidate.zip` exists.
- `reports/latest_release_zip_smoke_test.html` shows the zip can be extracted and its core checks pass.
- `public_repo_candidate/agentops-control-tower` contains only reviewable public-candidate files.

## Launch Sequence

1. Review `reports/latest_judge_quickstart.html`.
2. Review `reports/latest_judge_scorecard.html`.
3. Review `reports/latest_claim_evidence_matrix.html`.
4. Review `reports/latest_launch_decision_brief.html`.
5. Review `reports/latest_submission_review_index.html`.
6. Review `reports/latest_submission_gate_ledger.html`.
7. Review `reports/latest_submission_deadline_burndown.html`.
8. Review `reports/latest_final_go_no_go.html`.
9. Review `reports/latest_external_approval_packet.html`.
10. Review `reports/latest_video_command_plan.html`.
11. Review `reports/latest_video_upload_metadata.html`.
12. Review `reports/latest_publication_command_plan.html`.
13. Review `reports/latest_public_repo_metadata.html`.
14. Review `reports/latest_public_repo_publish_brief.html`.
15. Review `reports/latest_public_launch_snapshot.html`.
16. Review `reports/latest_splunk_mcp_command_plan.html`.
17. Review `reports/latest_splunk_mcp_proof_brief.html`.
18. Review `reports/latest_splunk_mcp_prompt_pack.html`.
19. Review `reports/latest_splunk_mcp_proof_capture_manifest.html`.
20. Review `reports/latest_content_rights_audit.html`.
21. Review `reports/latest_eligibility_compliance_audit.html`.
22. Review `submission/HUMAN_CONFIRMATION_CHECKLIST.md`.
23. Review `reports/latest_next_approval_packet.html`.
24. Review `reports/latest_approval_consistency_audit.html`.
25. Review `reports/latest_status_conflict_audit.html`.
26. Review `reports/latest_devpost_submit_command_plan.html`.
27. Review `reports/latest_devpost_manual_fill_brief.html`.
28. Review `submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md`.
29. Review `reports/latest_post_action_evidence_brief.html`.
30. Review `reports/latest_official_source_freshness.html`.
31. Review `reports/latest_release_integrity_manifest.html`.
32. Decide whether to pursue live Splunk and MCP proof before submission.
33. If live proof is approved, follow `reports/latest_splunk_mcp_command_plan.html`, `reports/latest_splunk_mcp_proof_brief.html`, `reports/latest_splunk_mcp_prompt_pack.html`, and `reports/latest_splunk_mcp_proof_capture_manifest.html`, import only synthetic data, capture screenshots or video, and update the claim wording only after proof.
34. Publish the clean public repository only after explicit approval.
35. Read back the public repo URL, visibility, and public-candidate scan result using `reports/latest_post_action_evidence_brief.html`.
36. Review `reports/latest_video_readiness.html`.
37. Review `submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md`.
38. Review `reports/latest_video_cue_sheet.html`.
39. Record the demo using `reports/latest_demo_tour.html` and `submission/VIDEO_RECORDING_RUNBOOK.md`.
40. Check `submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md` against the final recording before upload approval.
41. Upload the video publicly only after explicit approval using `reports/latest_video_upload_metadata.html`.
42. Read back the video URL, duration, and screen-safety result using `reports/latest_post_action_evidence_brief.html`.
43. After both public URLs are approved, run `python scripts\prepare_submission_urls.py --repository-url <url> --demo-video-url <url> --write-approved --approval-note "<approval>"`.
44. Copy or fill `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` with approved URL readback and validation summaries.
45. Rebuild the Devpost packet and final copy.
46. Replace the pending repository and video URL placeholders in the Devpost form.
47. Confirm entrant eligibility, team/representative authority if applicable, ownership/IP rights, no excluded role/conflict, English materials, and no prohibited sponsor/administrator support.
48. Check `submission/HUMAN_CONFIRMATION_CHECKLIST.md` only after the entrant has confirmed each item.
49. Check `submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md` against the visible Devpost screen immediately before final approval.
50. Re-run `python scripts\validate_submission_packet.py`.
51. Get explicit final approval before pressing the Devpost submit button.
52. After final submit, read back the submitted Devpost page/status and preserve local evidence without account screenshots or secrets.

## Claim Wording

Use this wording when live Splunk setup has not been completed:

```text
Agentic Incident Command Center is designed for Splunk MCP Server. The current package includes synthetic checkout-incident events, Splunk-ready CSV, SPL examples, a local SPL-equivalent proof report, and a Splunk app candidate.
```

Use this wording only after approved live setup is verified:

```text
Agentic Incident Command Center is verified through Splunk MCP Server with synthetic checkout-incident events indexed in Splunk and MCP-assisted investigation citing event IDs and evidence references.
```

## Decision Matrix

| Path | When to use | Submission effect |
| --- | --- | --- |
| Local-only submission | Splunk account or MCP setup is not approved in time | Eligible core project with clear Splunk-ready design, weaker MCP bonus claim |
| Live Splunk proof | Splunk account and data import are approved | Stronger technical implementation and clearer Splunk usage proof |
| Live Splunk plus MCP proof | Splunk MCP Server credentials and scope are approved | Strongest fit for Best Use of Splunk MCP Server |

## Evidence To Keep Open During Review

- `reports/latest_control_tower.html`
- `reports/latest_demo_tour.html`
- `reports/latest_video_readiness.html`
- `submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md`
- `reports/latest_video_command_plan.html`
- `reports/latest_video_cue_sheet.html`
- `reports/latest_video_upload_metadata.html`
- `submission/VIDEO_UPLOAD_METADATA.md`
- `reports/latest_claim_evidence_matrix.html`
- `reports/latest_external_approval_packet.html`
- `reports/latest_publication_command_plan.html`
- `reports/latest_public_repo_metadata.html`
- `reports/latest_public_repo_publish_brief.html`
- `reports/latest_public_launch_snapshot.html`
- `reports/latest_splunk_mcp_command_plan.html`
- `reports/latest_splunk_mcp_proof_brief.html`
- `reports/latest_splunk_mcp_prompt_pack.html`
- `reports/latest_splunk_mcp_proof_capture_manifest.html`
- `submission/SPLUNK_MCP_PROMPT_PACK.md`
- `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md`
- `reports/latest_splunk_app_package_manifest.html`
- `reports/latest_submission_gate_ledger.html`
- `reports/latest_submission_deadline_burndown.html`
- `reports/latest_submission_review_index.html`
- `reports/latest_judge_quickstart.html`
- `reports/latest_judge_scorecard.html`
- `reports/latest_launch_decision_brief.html`
- `reports/latest_next_approval_packet.html`
- `reports/latest_approval_consistency_audit.html`
- `reports/latest_status_conflict_audit.html`
- `reports/latest_content_rights_audit.html`
- `reports/latest_devpost_submit_command_plan.html`
- `reports/latest_devpost_manual_fill_brief.html`
- `submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md`
- `reports/latest_post_action_evidence_brief.html`
- `reports/latest_official_source_freshness.html`
- `reports/latest_release_integrity_manifest.html`
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md`
- `submission/PUBLIC_REPO_METADATA.md`
- `submission/HUMAN_CONFIRMATION_CHECKLIST.md`
- `submission/SUBMISSION_DEADLINE_BURNDOWN.md`
- `submission/NEXT_APPROVAL_PACKET.md`
- `submission/USER_APPROVAL_GATES.md`
- `reports/latest_submission_url_apply_plan.html`
- `reports/latest_local_spl_query_results.html`
- `reports/latest_devpost_submission_packet.html`
- `reports/latest_final_go_no_go.html`
- `submission/DEVPOST_FIELD_MAP.md`
- `submission/OFFICIAL_REQUIREMENTS_AUDIT.md`
- `submission/JUDGING_ALIGNMENT.md`
- `submission/SUBMISSION_REVIEW_QA.md`
- `splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml`

## Final Safety Gate

Before final submit, confirm:

- The demo uses synthetic data only.
- No credentials, tokens, account pages, private logs, or local absolute paths appear in the public repo, screenshots, video, or Devpost text.
- The public repository URL and video URL are real and openable.
- The Devpost text does not claim live Splunk MCP verification unless that proof was approved, captured, and checked.
- The post-action evidence log has no credentials, account screenshots, private paths, or secrets.
- The user has explicitly approved the final Devpost submit action.
