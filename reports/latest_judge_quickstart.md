# Judge Quickstart

Status: ready_for_user_review
Root type: public_candidate

## One-Minute Summary

Agentic Incident Command Center demonstrates how Splunk-ready incident data can make AI-assisted response evidence-backed: root-cause candidates are ranked, blast radius is visible, and high-impact remediation stays queued for human approval through the MCP Remediation Ledger.

## 5-Minute Review Path

1. `READY_FOR_REVIEW.md` (present) - Plain-language readiness memo that keeps final submit and external gates closed.
2. `reports/latest_judge_review_packet.html` (present) - Single review path that separates local evidence from approval-only external work.
3. `reports/latest_local_readiness_baseline.html` (present) - Explains current targeted readiness and why the full submission validator may still show external-gate failures.
4. `reports/latest_public_candidate_local_audit.html` (present) - Scans the local public candidate for required artifacts, internal paths, secret-like strings, and claim boundaries.
5. `reports/latest_devpost_copy_audit.html` (present) - Verifies copy, placeholders, character limits, field map alignment, and no-overclaim boundaries.
6. `reports/latest_submission_review_index.html` (present) - One-page map of the evidence and remaining external gates.
7. `reports/latest_judge_scorecard.html` (present) - Maps Stage One, Stage Two, and bonus alignment to concrete local evidence.
8. `reports/latest_official_source_freshness.html` (present) - Shows the current official Devpost source check and local requirement mapping.
9. `reports/latest_control_tower.html` (present) - Shows incident summary, root-cause ranking, blast radius, approval queue, and MCP Remediation Ledger.
10. `reports/latest_demo_tour.html` (present) - Gives the intended under-3-minute walkthrough sequence.
11. `reports/latest_local_spl_query_results.html` (present) - Shows the Splunk query intent over the synthetic CSV before live Splunk access.
12. `reports/latest_splunk_mcp_prompt_pack.html` (present) - Shows the evidence-backed questions, SPL, expected citations, and stop conditions for optional live MCP proof.
13. `reports/latest_splunk_mcp_proof_capture_manifest.html` (present) - Freezes capture slots, readback expectations, stop conditions, and claim-upgrade gate before optional live proof.
14. `reports/latest_claim_evidence_matrix.html` (present) - Maps each public claim to evidence, allowed wording, and remaining gates.
15. `reports/latest_splunk_app_package_manifest.html` (present) - Shows the .spl package, members, SHA256, and no-install boundary.
16. `reports/latest_devpost_final_copy.html` (present) - Shows the copy/paste candidate and pending URL gates.
17. `reports/latest_submission_gate_ledger.html` (present) - Separates public repo, video, optional Splunk/MCP proof, and final Devpost approval.
18. `reports/latest_next_approval_packet.html` (present) - Shows the next user approval target, exact approval phrases, and pre-Devpost human confirmations.
19. `reports/latest_public_launch_snapshot.html` (present) - Freezes the repo/video approval packet, ZIP hash, approval phrases, and no-external-action boundary.
20. `reports/latest_approval_consistency_audit.html` (present) - Confirms public repo/video are first and live Splunk/MCP proof remains optional until explicitly approved.
21. `reports/latest_content_rights_audit.html` (present) - Shows license, bundled asset, audio/video, trademark, and screen-safety evidence.
22. `reports/latest_eligibility_compliance_audit.html` (present) - Shows automated compliance evidence and the human confirmations needed before final submission.
23. `reports/latest_release_integrity_manifest.html` (present) - Shows key artifact SHA256, sizes, ZIP count consistency, and no-publish boundary.
24. `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` (present) - Shows how approved publication, video, URL writeback, Splunk/MCP proof, and Devpost submit readback will be recorded.

## Commands

### Run local demo

Regenerate synthetic events, analysis JSON, dashboard, SPL examples, and MCP investigation preview.

```powershell
python prototype\agentops_control_tower.py run-demo
```

### Run local SPL proof

Regenerate the five SPL-equivalent proof sections over the synthetic CSV.

```powershell
python scripts\run_local_spl_query_pack.py
```

### Build targeted SPAK review packet

Regenerate local readiness, public candidate audit, Devpost copy audit, and judge review packet without publishing, recording, submitting, or starting live Splunk.

```powershell
python scripts\build_spak_autonomous_review_packet.py
```

## Boundary

This quickstart is local review guidance only. It does not publish, upload, connect to Splunk, write approved URLs, update Devpost, or submit anything.
