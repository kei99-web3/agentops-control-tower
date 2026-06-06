# Judging Alignment

Last verified: 2026-06-06 JST

Official source:

- https://splunk.devpost.com/rules

The official rules describe a pass/fail Stage One viability screen, followed by Stage Two judging across four equally weighted criteria: Technological Implementation, Design, Potential Impact, and Quality of the Idea.

## Stage One Pass/Fail Baseline

This section is the pass/fail baseline used by the local review packet before scored judging.

| Pass/fail baseline | Local status | Evidence | Remaining gate |
| --- | --- | --- | --- |
| Theme fit | Local ready | `README.md`, `architecture_diagram.md`, `reports/latest_judge_scorecard.html` | Public demo still needs approval before final submission. |
| Required Splunk capability use | Local ready, live proof optional | `submission/SPLUNK_MCP_RUNBOOK.md`, `reports/latest_local_spl_query_results.html`, `reports/latest_splunk_app_package_manifest.html` | Live Splunk/MCP proof remains optional and approval-gated. |
| Required submission artifacts | Local ready, external URLs pending | `LICENSE`, `reports/latest_devpost_final_copy.html`, `reports/latest_video_cue_sheet.html`, `reports/latest_public_repo_publish_brief.html` | Public repository URL and public demo video URL are still pending user approval. |
| Safe data and claim integrity | Local ready | `reports/latest_claim_evidence_matrix.html`, `reports/latest_claim_boundary_validation.html`, `reports/latest_status_conflict_audit.html` | Keep final submit blocked until public URLs and optional proof readbacks are approved. |

## Stage One Viability

| Requirement | How Agentic Incident Command Center addresses it | Evidence |
| --- | --- | --- |
| Fits the hackathon theme | Uses Splunk as the operational evidence layer for agentic incident response. | `README.md`, `architecture_diagram.md` |
| Applies Splunk AI / MCP capabilities | Designed around `agentops_events` in Splunk and Splunk MCP Server as the evidence source for AI incident investigation. | `submission/SPLUNK_MCP_RUNBOOK.md`, `submission/SPLUNK_MCP_PROMPT_PACK.md`, `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md`, `submission/SPL_QUERIES.md` |
| Runs consistently on the target platform | Standard-library Python demo generates data, dashboard, local SPL-equivalent proof, and validation reports. | `python scripts/validate_submission_packet.py` |
| Uses safe, authorized data | Public demo uses synthetic incident events only. | `data/synthetic_agentops_events.jsonl`, `submission/OFFICIAL_REQUIREMENTS_AUDIT.md` |

## Criterion 1: Technological Implementation

What to show:

- Deterministic synthetic incident event generation.
- Splunk-ready CSV export with incident, service, signal domain, root-cause, approval, MCP, and evidence fields.
- Local SPL-equivalent query proof for incident timeline, root-cause evidence, remediation ledger, Splunk MCP investigation context, and blast radius.
- Splunk app candidate with dashboard XML and saved searches for the same workflow.
- Splunk MCP prompt pack and proof capture manifest for optional live proof.
- Claim evidence matrix and validator that prevent overclaiming live Splunk/MCP, public URLs, or final submission.

Best evidence:

- `prototype/agentops_control_tower.py`
- `scripts/run_local_spl_query_pack.py`
- `reports/latest_control_tower.html`
- `reports/latest_local_spl_query_results.html`
- `reports/latest_claim_evidence_matrix.html`
- `reports/latest_judge_scorecard.html`

## Criterion 2: Design

What to show:

- Dashboard organized around incident command decisions, not generic logs.
- KPI summary, incident summary, root-cause ranking, blast radius, MCP Remediation Ledger, SPL queries, and MCP investigation preview.
- Clear evidence references so a reviewer can move from AI recommendation to source event.

Best evidence:

- `reports/latest_control_tower.html`
- `assets/dashboard_preview.png`
- `reports/latest_mcp_investigation.md`
- `submission/DEMO_VIDEO_SCRIPT.md`

## Criterion 3: Potential Impact

What to show:

- Modern incidents require evidence from deploys, application telemetry, traces, databases, networks, security systems, and AI/tool runtime logs.
- The project gives platform teams a practical way to use AI for triage without letting AI silently execute high-impact remediation.
- The same pattern can extend to SRE, SOC, developer platforms, customer support, and MCP governance.

Best evidence:

- `submission/DEVPOST_SUBMISSION_DRAFT.md`
- `architecture_diagram.md`
- `submission/REQUIREMENTS_MATRIX.md`
- `submission/OFFICIAL_REQUIREMENTS_AUDIT.md`

## Criterion 4: Quality of the Idea

What to show:

- The strongest idea is not “AI does everything.” It is “AI makes incident command decisions evidence-backed and faster.”
- Splunk MCP Server is positioned as an evidence gateway for agents, not an unchecked action channel.
- The MCP Remediation Ledger is reusable: every proposed action must cite source events, approval state, policy decision, and runbook action.
- The claim evidence matrix keeps local proof, live proof, public URL status, and submitted status separated.

Best evidence:

- `README.md`
- `reports/latest_mcp_investigation.md`
- `reports/latest_claim_evidence_matrix.html`
- `submission/SPLUNK_MCP_RUNBOOK.md`
- `reports/latest_splunk_mcp_prompt_pack.html`
- `submission/SPL_QUERIES.md`
- `reports/latest_judge_scorecard.html`

## Bonus Prize Alignment: Splunk MCP Server

The Best Use of Splunk MCP Server prize rewards intelligent, agent-driven experiences that connect AI agents to Splunk data for contextual insight and decision making. Agentic Incident Command Center is designed for that pattern:

1. Incident events are indexed in Splunk.
2. Splunk MCP Server exposes approved query tools.
3. The AI incident commander asks what likely caused the outage and which remediation needs approval first.
4. The answer cites event IDs, risk scores, root-cause evidence, policy decisions, and evidence references.

Current status: local proof exists; live MCP verification still requires approved Splunk account/license and MCP configuration.

## MCP Bonus Claim Boundary

Current safe claim: Agentic Incident Command Center is designed for Splunk MCP Server, with local synthetic proof and an explicit approval-gated live proof path.

Do not claim yet:

- verified through Splunk MCP Server
- live Splunk MCP integration completed
- Splunk MCP Server generated the final submitted decisions

Use verified-through-Splunk-MCP wording only after explicit user approval, synthetic-only live proof capture, safe readback, and `reports/latest_splunk_mcp_proof_capture_manifest.json` has `live_splunk_mcp_verified=true`.

## Demo Emphasis

In the under-3-minute video, spend the most time on:

1. The concrete problem: incident evidence is scattered across teams and tools.
2. The dashboard: root-cause ranking, blast radius, and approval queue.
3. The MCP story: AI can investigate Splunk evidence, but human approval remains the final gate.
4. The proof boundary: synthetic data and local SPL emulation now; live Splunk MCP only after approved setup.
