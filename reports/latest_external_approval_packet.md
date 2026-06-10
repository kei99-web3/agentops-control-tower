# External Approval Packet

Status: ready_for_user_review
Local submission status: ready_for_user_review

This packet lists the external actions that still require explicit human approval.

## Approval Requests

### Public GitHub Repository

Status: ready_for_user_decision

Purpose: Make the clean Agentic Incident Command Center code package reviewable for Devpost judges.

Exact operation: Run scripts/verify_public_repo_publication_gate.py with the exact approval phrase, public git identity, and manual safety confirmations, then use scripts/publish_public_repo_after_approval.py to create and push the public repository only after explicit approval.

Benefit: Satisfies the public open-source repository requirement and lets judges run the prototype, inspect the Splunk app candidate, and review local evidence.

Main risk: Accidental disclosure of local paths, credentials, or private workspace material if the wrong folder is published or Git is initialized inside the private workspace.

Verification: Review reports/latest_public_repo_publication_preflight.html, run the guarded helper, confirm public candidate secret/internal scans and isolated staging dry run pass, open the public repository URL, then validate the URL before local URL writeback.

Evidence:
- README.md (present)
- PUBLIC_REPO_CANDIDATE_MANIFEST.md (present)
- reports/latest_public_repo_publication_preflight.html (present)
- reports/latest_public_repo_dry_run.html (present)
- reports/latest_demo_tour.html (present)
- reports/latest_video_readiness.html (present)
- reports/latest_devpost_submission_packet.html (present)
- splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml (present)

### Public Demo Video

Status: ready_for_user_decision

Purpose: Show the Agentic Incident Command Center flow in a concise Devpost-compatible demo.

Exact operation: Run scripts/verify_public_video_upload_gate.py with the exact approval phrase and manual safety confirmations, record the browser walkthrough using reports/latest_demo_tour.html and submission/VIDEO_RECORDING_RUNBOOK.md, then upload publicly only after explicit approval.

Benefit: Gives judges a fast path through the problem, dashboard, local SPL proof, MCP Remediation Ledger, and Splunk MCP boundary.

Main risk: The recording could expose private tabs, terminals, account pages, local paths, or overclaim live Splunk MCP verification before it exists.

Verification: Review reports/latest_public_video_upload_preflight.html and reports/latest_video_readiness.html, confirm the recording is under 3 minutes, watch the uploaded video while checking the screen safety list, then validate the public video URL.

Evidence:
- reports/latest_demo_tour.html (present)
- reports/latest_video_readiness.html (present)
- reports/latest_public_video_upload_preflight.html (present)
- submission/DEMO_VIDEO_SCRIPT.md (present)
- submission/VIDEO_RECORDING_RUNBOOK.md (present)

### Optional Live Splunk / MCP Proof

Status: completed

Purpose: Completed: strengthen the Best Use of Splunk MCP Server bonus claim with local official-MCP proof using synthetic data only.

Exact operation: No further external setup is needed for the local official-MCP proof; keep claims bounded to local Splunk Enterprise Docker with synthetic data.

Benefit: Improves technical implementation evidence and supports bounded wording: official Splunk MCP Server verified in local Splunk Enterprise Docker with synthetic data.

Main risk: Overclaiming production Splunk Cloud deployment or exposing credentials in public video/screenshots.

Verification: Review submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md and rerun claim-boundary validation.

Evidence:
- submission/SPLUNK_MCP_RUNBOOK.md (present)
- reports/latest_splunk_mcp_proof_brief.html (present)
- reports/latest_splunk_mcp_prompt_pack.html (present)
- reports/latest_splunk_mcp_proof_capture_manifest.html (present)
- submission/SPLUNK_MCP_PROMPT_PACK.md (present)
- submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md (present)
- submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md (present)
- data/splunk_agentops_events.csv (present)
- submission/SPL_QUERIES.md (present)
- splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml (present)

### Devpost Final Submission

Status: blocked_until_public_urls

Purpose: Submit the completed Splunk Agentic Ops Hackathon entry.

Exact operation: After public repo and public video URLs are inserted and validation passes, review reports/latest_devpost_final_copy.md and press the Devpost submit button only with explicit final approval.

Benefit: Completes the hackathon submission with a locally verified code package, demo video, architecture diagram, and safe claim wording.

Main risk: Submitting too early with pending URLs, overclaims, wrong track selection, or missing public artifacts.

Verification: Confirm reports/latest_submission_validation.html is ready_for_user_review, repository and video URLs are public, Devpost fields match submission/DEVPOST_FIELD_MAP.md, and final submit approval is explicit.

Evidence:
- reports/latest_devpost_final_copy.md (present)
- reports/latest_final_go_no_go.html (present)
- submission/DEVPOST_FIELD_MAP.md (present)
- submission/SUBMISSION_LAUNCH_RUNBOOK.md (present)

## Boundary

This packet does not publish, upload, submit, create accounts, configure credentials, or update Devpost.
