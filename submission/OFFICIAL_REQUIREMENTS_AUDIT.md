# Official Requirements Audit

Last verified: 2026-06-04 JST

Local freshness report: `reports/latest_official_source_freshness.html`

Sources:

- Devpost overview: https://splunk.devpost.com/
- Devpost official rules: https://splunk.devpost.com/rules
- Devpost challenge update: https://splunk.devpost.com/updates/43765-the-challenge-is-live-and-so-are-the-prizes

Re-check note: Official overview, rules, and challenge update pages were rechecked on 2026-06-04 JST. Deadline, required public repository, under-3-minute public demo video, root architecture diagram, tracks, MCP bonus category, and judging criteria still match this packet.

## Deadline

- Official deadline: 2026-06-15 09:00 PDT
- Japan time equivalent: 2026-06-16 01:00 JST
- Local target: submit before 2026-06-15 20:00 JST to leave rollback time.

## Submission Gate Audit

| Official requirement | Current local evidence | Status | Remaining gate |
| --- | --- | --- | --- |
| Build an AI-powered solution for observability, security, or developer productivity | `README.md`, `prototype/agentops_control_tower.py`, `reports/latest_control_tower.html`, `splunk_app/agentops_control_tower` | Locally ready | Live Splunk proof still improves credibility |
| Select one track | `submission/DEVPOST_SUBMISSION_DRAFT.md` selects Platform & Developer Experience | Ready | Confirm during Devpost submission |
| Explain features and functionality in text | `README.md`, `submission/DEVPOST_SUBMISSION_DRAFT.md`, `submission/DEVPOST_FIELD_MAP.md`, `reports/latest_devpost_submission_packet.html`, `reports/latest_claim_evidence_matrix.html`, `reports/latest_final_go_no_go.html`, `reports/latest_submission_gate_ledger.html`, `reports/latest_submission_review_index.html`, `reports/latest_judge_quickstart.html`, `reports/latest_judge_scorecard.html`, `reports/latest_launch_decision_brief.html`, `reports/latest_official_source_freshness.html` | Ready | Copy into Devpost after approval |
| Demo video under 3 minutes showing project function, AI usage, problem, and value | `reports/latest_demo_tour.html`, `reports/latest_video_readiness.html`, `reports/latest_video_command_plan.html`, `reports/latest_video_cue_sheet.html`, `reports/latest_content_rights_audit.html`, `submission/DEMO_VIDEO_SCRIPT.md`, `submission/VIDEO_RECORDING_RUNBOOK.md` | Prepared locally | Record and publicly upload after approval |
| Public open-source code repository | `public_repo_candidate/agentops-control-tower`, `reports/latest_publication_command_plan.html`, `reports/latest_public_repo_publish_brief.html`, `reports/latest_release_integrity_manifest.html` | Prepared locally | Publish only after user approval |
| Open-source license | `LICENSE` | Ready | Include in public repo |
| Source code, assets, instructions, dependencies, configs, or datasets | `README.md`, `prototype/`, `data/`, `assets/dashboard_preview.png`, `submission/SPL_QUERIES.md`, `dist/agentops-control-tower-splunk-app.spl`, `reports/latest_splunk_app_package_manifest.html`, `reports/latest_content_rights_audit.html`, `reports/latest_release_integrity_manifest.html` | Ready | Include in public repo |
| Root architecture diagram showing Splunk interaction, AI/agent integration, and data flow | `architecture_diagram.md` | Ready | Include in public repo root |
| Project functions as depicted in video/text | `scripts/validate_submission_packet.py` checks demo, tests, HTML, claim evidence, public candidate, local SPL proof, release ZIP smoke, and release integrity | Locally ready | Re-run immediately before recording/submission |
| Eligibility and compliance: entrant eligibility, team representation, ownership/IP, language, testing access, and conflict rules | `reports/latest_eligibility_compliance_audit.html` | Prepared locally | Human confirmation required before final Devpost submission |
| Splunk MCP Server bonus / Best Use of Splunk MCP Server | `architecture_diagram.md`, `submission/SPLUNK_MCP_RUNBOOK.md`, `submission/SPLUNK_MCP_PROMPT_PACK.md`, `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md`, `reports/latest_local_spl_query_results.html`, `reports/latest_splunk_mcp_command_plan.html`, `reports/latest_splunk_mcp_proof_brief.html`, `reports/latest_splunk_mcp_prompt_pack.html`, `reports/latest_splunk_mcp_proof_capture_manifest.html`, `reports/latest_splunk_app_package_manifest.html`, `reports/latest_judge_scorecard.html` | Partial local proof | Requires approved Splunk account and MCP configuration |
| Public video URL | Not generated | Not ready | User approval required |
| Public repo URL | Not generated | Not ready | User approval required |
| Devpost final submit | `reports/latest_judge_quickstart.html`, `reports/latest_judge_scorecard.html`, `reports/latest_launch_decision_brief.html`, `reports/latest_submission_review_index.html`, `reports/latest_submission_gate_ledger.html`, `reports/latest_devpost_submit_command_plan.html`, `reports/latest_devpost_manual_fill_brief.html`, `reports/latest_post_action_evidence_brief.html`, `reports/latest_official_source_freshness.html`, `reports/latest_release_integrity_manifest.html`, `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` | Not submitted | User approval required |

## Rule/Risk Notes

- Use synthetic data only in the public demo.
- Do not expose private workspace paths, credentials, OAuth tokens, account data, customer data, or real incident logs.
- Do not include unlicensed third-party trademarks, music, copyrighted material, stock footage, sponsor logos, account screenshots, or unrelated media in the public repo, video, screenshots, or Devpost text.
- Do not claim live Splunk MCP integration until an approved Splunk environment and MCP Server are configured and recorded.
- Before final submission, the entrant must confirm eligibility, team/representative authority if applicable, no excluded role or conflict, ownership/IP rights, and no prohibited sponsor/administrator support.
- Use `reports/latest_claim_evidence_matrix.html` before Devpost/video copy changes to keep allowed wording, avoided wording, evidence, and remaining gates aligned.
- Use `reports/latest_eligibility_compliance_audit.html` before Devpost final approval to separate automated package evidence from human confirmation items.
- Use `reports/latest_official_source_freshness.html` before final approval to confirm the latest official source check, deadline, required artifacts, and judging criteria are still aligned.
- Use `reports/latest_release_integrity_manifest.html` before publication or final submission approval to confirm key artifact hashes, ZIP counts, and no-publish/no-submit boundaries.
- The current local SPL result report is an emulation over the generated CSV. It is useful as proof that the query pack returns meaningful rows, but it is not a substitute for live Splunk verification.
- The current Splunk MCP prompt pack is a local proof-preparation artifact. It defines approved-proof prompts, SPL, expected event citations, success readbacks, and stop conditions, but it is not live MCP verification.
- The project was created locally on 2026-06-03 JST during the hackathon submission period and should be described as a new hackathon build.

## Go / No-Go Summary

Current status: `ready_for_user_review`

Submit only after all three external publication gates are approved and completed:

1. Public GitHub repository.
2. Public demo video.
3. Devpost final submission.
