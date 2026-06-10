# Submission Review Index

Status: ready_for_user_review
Root type: public_candidate
Local submission status: not_bundled_public_candidate_root
Local submission source: public_candidate_local_artifacts
Final submit ready: false

## Recommended Review Order

- Open READY_FOR_REVIEW.md and reports/latest_judge_review_packet.html first.
- Review reports/latest_local_readiness_baseline.html to separate local readiness from external gates.
- Review reports/latest_public_candidate_local_audit.html and reports/latest_devpost_copy_audit.html.
- Open reports/latest_judge_quickstart.html for the 5-minute review path.
- Open reports/latest_submission_review_index.html.
- Review reports/latest_submission_gate_ledger.html and reports/latest_external_approval_packet.html.
- Review reports/latest_submission_deadline_burndown.html for target submit timing and milestone order.
- Open reports/latest_next_approval_packet.html to decide the next explicit approval phrase.
- Open reports/latest_public_launch_snapshot.html to confirm the exact repo/video launch packet before approval.
- Open reports/latest_approval_consistency_audit.html to confirm stale Splunk-first guidance is not present.
- Open reports/latest_status_conflict_audit.html to confirm no stale failed status remains in JSON reports.
- Review reports/latest_control_tower.html and reports/latest_demo_tour.html for the story.
- Review Splunk evidence: local SPL proof, .spl package manifest, Splunk MCP command plan, proof brief, and prompt pack.
- Review Devpost final copy and URL validation.
- Only after explicit approval, proceed to public repo, video, optional live Splunk/MCP proof, and final Devpost submit gates.

## Artifacts

### Devpost Copy

- `reports/latest_devpost_submission_packet.html` (present) - Devpost submission packet: Local Devpost field packet with pending URL placeholders and claim boundaries.
- `reports/latest_devpost_final_copy.html` (present) - Devpost final copy: Copy/paste text and character checks for the final Devpost form.
- `reports/latest_devpost_submit_command_plan.html` (present) - Devpost submit command plan: Post-approval Devpost form-fill, final review, submit, and readback plan.
- `reports/latest_devpost_manual_fill_brief.html` (present) - Devpost manual fill brief: Field-by-field form fill order, readback checks, and stop conditions before final submit.
- `submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md` (present) - Devpost final review checklist: Unchecked final-screen checklist for track, public URLs, claim boundaries, human confirmations, video safety, validation, and explicit final approval.

### External Gates

- `reports/latest_external_approval_packet.html` (present) - External approval packet: Purpose, operation, benefit, risk, and verification for each external action.
- `reports/latest_next_approval_packet.html` (present) - Next approval packet: Shows the next approval target, copy-paste approval phrases, and human confirmations before Devpost.
- `reports/latest_publication_command_plan.html` (present) - Publication command plan: Post-approval public GitHub command plan using isolated TEMP staging. It does not create or push a repo.
- `reports/latest_public_repo_metadata.html` (present) - Public repo metadata: GitHub repository name, description, topics, expected readback, and no-publish boundary.
- `reports/latest_video_command_plan.html` (present) - Video command plan: Post-approval recording/upload plan. It does not record or upload.
- `reports/latest_video_recording_preview.html` (present) - Video recording preview: Local-only localhost preview preflight for the public demo recording path.
- `reports/latest_video_upload_metadata.html` (present) - Video upload metadata: Public demo video title, description, tags, visibility, expected readback, and no-upload boundary.
- `reports/latest_public_artifact_url_readback.html` (present) - Public artifact URL readback: Post-publication URL readback gate before approved URL writeback.
- `reports/latest_submission_url_apply_plan.html` (present) - Submission URL apply plan: Dry-run or approved local URL write plan. It does not write without explicit approval.
- `reports/latest_post_action_evidence_brief.html` (present) - Post-action evidence brief: Readback checklist for proving public repo, video, URL writeback, optional Splunk/MCP proof, and Devpost submit after approval.
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` (present) - Post-action evidence log template: Template to copy/fill after approved external actions are completed.

### Release Package

- `PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present) - Public candidate manifest: Shows this folder is a clean local public-candidate staging area.

### Requirements

- `submission/OFFICIAL_REQUIREMENTS_AUDIT.md` (present) - Official requirements audit: Maps current artifacts to the official Devpost requirements.
- `submission/JUDGE_REVIEW_PACKET.md` (present) - Judge review packet markdown: Markdown copy of the review packet for local and public-candidate review.
- `submission/JUDGING_ALIGNMENT.md` (present) - Judging alignment: Maps the project to judging criteria and bonus alignment.
- `reports/latest_judge_scorecard.html` (present) - Judge scorecard: Maps Stage One, Stage Two, and bonus judging points to concrete evidence and remaining gates.
- `submission/SUBMISSION_LAUNCH_RUNBOOK.md` (present) - Launch runbook: Preflight, launch sequence, claim wording, and final safety gate.
- `submission/SUBMISSION_REVIEW_QA.md` (present) - Review Q&A: Judge-facing answers and safe copy guardrails.

### Splunk Evidence

- `data/splunk_agentops_events.csv` (present) - Splunk-ready CSV: Synthetic checkout-incident events ready for an agentops_events index after approval.
- `submission/SPL_QUERIES.md` (present) - SPL query pack: Queries for high-risk events, approval queue, MCP remediation ledger, and external guardrails.
- `reports/latest_local_spl_query_results.html` (present) - Local SPL-equivalent proof: Local proof that the query intent returns concrete rows before live Splunk setup.
- `splunk_app/agentops_control_tower/default/indexes.conf` (present) - Splunk index config: Optional app-local index definition for agentops_events.
- `splunk_app/agentops_control_tower/default/props.conf` (present) - Splunk sourcetype config: CSV extraction and timestamp parsing for agentops:events.
- `reports/latest_splunk_app_package_manifest.html` (present) - Splunk app package manifest: Local .spl package members, SHA256, and no-install/no-upload boundary.
- `dist/agentops-control-tower-splunk-app.spl` (present) - Splunk app package: Local reviewable .spl artifact. It is not installed or uploaded.
- `reports/latest_splunk_mcp_command_plan.html` (present) - Splunk MCP command plan: Post-approval plan for account/license, synthetic import, app install, MCP setup, and proof capture.
- `reports/latest_splunk_mcp_proof_brief.html` (present) - Splunk MCP proof brief: Decision brief for live proof success criteria, screen safety, stop conditions, and claim upgrade rules.
- `reports/latest_splunk_mcp_prompt_pack.html` (present) - Splunk MCP prompt pack: Five approved-proof prompts with SPL, expected citations, success readbacks, and stop conditions.
- `submission/SPLUNK_MCP_PROMPT_PACK.md` (present) - Splunk MCP prompt pack submission copy: Markdown copy of the Splunk MCP prompt pack for public review and live proof preparation.
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present) - Splunk MCP proof capture manifest: Capture slots, expected readback, stop conditions, and claim-upgrade gate for optional live proof.
- `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md` (present) - Splunk MCP proof capture manifest submission copy: Markdown copy of the optional live proof capture manifest.

### Start Here

- `READY_FOR_REVIEW.md` (present) - Ready for review memo: Plain-language local readiness and review start page.
- `reports/latest_judge_review_packet.html` (present) - Judge review packet: Single review packet that separates local readiness from external approval gates.
- `README.md` (present) - README: Portable project overview and local run instructions.
- `reports/latest_control_tower.html` (present) - Control Tower dashboard: Main local dashboard showing incidents, approval queue, and MCP Remediation Ledger.
- `reports/latest_demo_tour.html` (present) - Demo tour: Recording-friendly walkthrough for the public demo video.
- `reports/latest_submission_gate_ledger.html` (present) - Submission gate ledger: Single ledger for public repo, video, optional Splunk/MCP proof, and Devpost gates.
- `reports/latest_submission_deadline_burndown.html` (present) - Submission deadline burndown: Deadline-aware sequence for public repo, video, optional live proof, URL writeback, and Devpost final submit.

### Validation

- `reports/latest_final_go_no_go.html` (present) - Final Go/No-Go: Separates local readiness from pending external gates.
- `reports/latest_local_readiness_baseline.html` (present) - Local readiness baseline: Targeted local baseline that explains stale/full validator failures without moving external gates.
- `reports/latest_public_candidate_local_audit.html` (present) - Public candidate local audit: Scans the local public candidate for required artifacts, internal paths, secret-like strings, and claim boundaries.
- `reports/latest_devpost_copy_audit.html` (present) - Devpost copy audit: Checks final Devpost copy, placeholders, character limits, field-map alignment, and overclaim boundaries.
- `reports/latest_claim_evidence_matrix.html` (present) - Claim evidence matrix: Maps public claims to evidence, allowed wording, avoid wording, and remaining gates.
- `reports/latest_claim_boundary_validation.html` (present) - Claim boundary validation: Checks that live Splunk/MCP claims are not overstated before proof exists.
- `reports/latest_submission_url_validation.html` (present) - Submission URL validation: Shows repository/video URLs are still pending or approved-public.
- `reports/latest_content_rights_audit.html` (present) - Content rights audit: Shows license, bundled asset, audio/video, trademark, and screen-safety evidence.
- `reports/latest_eligibility_compliance_audit.html` (present) - Eligibility and compliance audit: Separates automated compliance evidence from user-confirmed eligibility, team, ownership, and conflict items.
- `reports/latest_approval_consistency_audit.html` (present) - Approval consistency audit: Checks that approval order stays public repo, public video, optional Splunk/MCP proof, URL writeback, then Devpost.
- `reports/latest_status_conflict_audit.html` (present) - Status conflict audit: Scans JSON reports for stale failed statuses, failed counts, and missing local artifacts.
- `reports/latest_public_launch_snapshot.html` (present) - Public launch snapshot: Freezes the public repo/video approval evidence, ZIP hash, approval phrases, and no-external-action boundary.
- `reports/latest_release_integrity_manifest.html` (present) - Release integrity manifest: Summarizes key artifact SHA256, size, ZIP count consistency, and no-publish boundary.
- `reports/latest_official_source_freshness.html` (present) - Official source freshness: Shows the latest official Devpost source check and local requirement mapping.

## Boundary

This review index is local evidence only. It does not publish a repository, record or upload video, connect to Splunk, write approved URLs, update Devpost, or submit anything.
