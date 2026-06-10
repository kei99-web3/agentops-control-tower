from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OFFICIAL_RULES_SOURCE = "https://splunk.devpost.com/rules"
BOUNDARY = (
    "This scorecard is local judging support only. It does not publish, upload, "
    "connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything."
)


@dataclass
class Evidence:
    path: str
    reason: str


@dataclass
class Criterion:
    section: str
    title: str
    official_basis: str
    readiness: str
    judge_message: str
    evidence: list[Evidence]
    remaining_gate: str


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def load_state(root: Path) -> dict[str, Any]:
    return {
        "validation": read_json(root / "reports/latest_submission_validation.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "gate_ledger": read_json(root / "reports/latest_submission_gate_ledger.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
        "release_smoke": read_json(root / "reports/latest_release_zip_smoke_test.json"),
        "splunk_app": read_json(root / "reports/latest_splunk_app_package_manifest.json"),
        "claim_evidence": read_json(root / "reports/latest_claim_evidence_matrix.json"),
        "claim_boundary": read_json(root / "reports/latest_claim_boundary_validation.json"),
        "post_action": read_json(root / "reports/latest_post_action_evidence_brief.json"),
        "splunk_mcp_proof": read_json(root / "reports/latest_splunk_mcp_proof_capture_manifest.json"),
        "live_splunk_docker_proof": read_json(root / "reports/latest_live_splunk_docker_proof.json"),
    }


def local_submission_snapshot(state: dict[str, Any], public_candidate: bool) -> dict[str, Any]:
    validation = state["validation"]
    go_no_go = state["go_no_go"]
    status = validation.get("overall_status", go_no_go.get("status", "missing"))
    failed_count = validation.get("failed_count", "missing")
    source = "reports/latest_submission_validation.json" if validation else "reports/latest_final_go_no_go.json"
    if public_candidate and not validation:
        return {
            "status": "not_bundled_public_candidate_root",
            "failed_count": "not_applicable_public_candidate_root",
            "source": "public_candidate_local_artifacts",
        }
    if (
        status == "needs_more_evidence"
        and go_no_go.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready") is True
        and go_no_go.get("missing_local_evidence", []) == []
        and go_no_go.get("missing_public_candidate_evidence", []) == []
    ):
        return {
            "status": "ready_for_user_review",
            "failed_count": 0,
            "source": "reports/latest_final_go_no_go.json",
        }
    return {
        "status": status,
        "failed_count": failed_count,
        "source": source,
    }


def evidence(path: str, reason: str) -> Evidence:
    return Evidence(path=path, reason=reason)


def evidence_paths(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    return [{"path": path, "exists": exists(root, path)} for path in paths]


def baseline_item(
    root: Path,
    requirement: str,
    official_basis: str,
    local_status: str,
    paths: list[str],
    remaining_gate: str,
) -> dict[str, Any]:
    items = evidence_paths(root, paths)
    return {
        "requirement": requirement,
        "official_basis": official_basis,
        "local_status": local_status,
        "evidence": items,
        "missing_evidence": [item["path"] for item in items if not item["exists"]],
        "remaining_gate": remaining_gate,
        "ready": all(item["exists"] for item in items),
    }


def build_stage_one_pass_fail_baseline(root: Path) -> list[dict[str, Any]]:
    return [
        baseline_item(
            root,
            "Theme fit",
            "Stage One is pass/fail; the project must clearly address the Agentic Ops challenge.",
            "local_ready",
            ["README.md", "architecture_diagram.md", "submission/JUDGING_ALIGNMENT.md"],
            "Public demo still needs approval before final submission.",
        ),
        baseline_item(
            root,
            "Required Splunk capability use",
            "Stage One should show credible use of Splunk data, Splunk AI, or Splunk MCP-style capability.",
            "local_ready_live_optional",
            ["submission/SPLUNK_MCP_RUNBOOK.md", "reports/latest_local_spl_query_results.html", "reports/latest_splunk_app_package_manifest.html"],
            "Live Splunk/MCP proof remains optional and approval-gated.",
        ),
        baseline_item(
            root,
            "Required submission artifacts",
            "Stage One requires reviewable materials including code, public demo video, architecture, and runnable instructions.",
            "local_ready_external_urls_pending",
            ["LICENSE", "reports/latest_devpost_final_copy.html", "reports/latest_video_cue_sheet.html", "reports/latest_public_repo_publish_brief.html"],
            "Public repository URL and public demo video URL are still pending user approval.",
        ),
        baseline_item(
            root,
            "Safe data and claim integrity",
            "Stage One should be reviewable without unsafe data, hidden credentials, or overstated capability claims.",
            "local_ready",
            ["reports/latest_claim_evidence_matrix.html", "reports/latest_claim_boundary_validation.html", "reports/latest_status_conflict_audit.html"],
            "Keep final submit blocked until public URLs and optional proof readbacks are approved.",
        ),
    ]


def build_mcp_bonus_claim_boundary(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    live_verified = state["splunk_mcp_proof"].get("live_splunk_mcp_verified") is True
    live_splunk_verified = (
        state["splunk_mcp_proof"].get("live_splunk_verified") is True
        or state["live_splunk_docker_proof"].get("live_splunk_verified") is True
    )
    mcp_adapter_verified = (
        state["splunk_mcp_proof"].get("mcp_protocol_adapter_verified") is True
        or state["live_splunk_docker_proof"].get("mcp_protocol_adapter_verified") is True
    )
    official_mcp_verified = (
        state["splunk_mcp_proof"].get("official_splunk_mcp_server_verified") is True
        or state["live_splunk_docker_proof"].get("official_splunk_mcp_server_verified") is True
    )
    evidence = evidence_paths(
        root,
        [
            "reports/latest_splunk_mcp_proof_brief.html",
            "reports/latest_splunk_mcp_prompt_pack.html",
            "reports/latest_splunk_mcp_proof_capture_manifest.html",
            "reports/latest_claim_evidence_matrix.html",
            "reports/latest_claim_boundary_validation.html",
        ],
    )
    optional_evidence = evidence_paths(root, ["reports/latest_live_splunk_docker_proof.html"])
    current_safe_claim = (
        "Official Splunk MCP Server verified in local Splunk Enterprise Docker with synthetic data, plus "
        "local synthetic proof, SPL examples, local SPL-equivalent query evidence, and bounded claim validation."
        if live_verified and official_mcp_verified
        else (
            "Designed for Splunk MCP Server, with local synthetic proof, SPL examples, local SPL-equivalent query "
            "evidence, and an approval-gated live proof path. Official Splunk MCP Server proof remains pending."
        )
    )
    blocked_claims = [
        "production Splunk Cloud deployment completed",
        "Splunk MCP Server generated the final submitted decisions",
    ] if live_verified and official_mcp_verified else [
        "verified through Splunk MCP Server",
        "live Splunk MCP integration completed",
        "Splunk MCP Server generated the final submitted decisions",
    ]
    upgrade_condition = (
        "Keep verified-through-Splunk-MCP wording bounded to the local Splunk Enterprise Docker proof with synthetic data; "
        "do not claim production Splunk Cloud deployment unless separate evidence is captured."
        if live_verified and official_mcp_verified
        else (
            "Use verified-through-Splunk-MCP wording only after official Splunk MCP Server install/configuration, "
            "synthetic-only read-only MCP answer capture, safe readback, and "
            "reports/latest_splunk_mcp_proof_capture_manifest.json live_splunk_mcp_verified=true and official_splunk_mcp_server_verified=true."
        )
    )
    return {
        "bonus_category": "Best Use of Splunk MCP Server",
        "live_splunk_mcp_verified": live_verified,
        "live_splunk_verified": live_splunk_verified,
        "mcp_protocol_adapter_verified": mcp_adapter_verified,
        "official_splunk_mcp_server_verified": official_mcp_verified,
        "current_safe_claim": current_safe_claim,
        "blocked_claims_until_verified": blocked_claims,
        "upgrade_condition": upgrade_condition,
        "evidence": evidence,
        "optional_evidence": optional_evidence,
        "missing_evidence": [item["path"] for item in evidence if not item["exists"]],
        "ready": all(item["exists"] for item in evidence),
    }


def build_criteria() -> list[Criterion]:
    return [
        Criterion(
            section="Stage One Viability",
            title="Theme fit and required Splunk capability use",
            official_basis="The project should fit the Agentic Ops theme and reasonably apply Splunk AI, Splunk data, or MCP-style capabilities.",
            readiness="strong_local_evidence",
            judge_message=(
                "Agentic Incident Command Center treats incident response as a Splunk-grounded evidence workflow, "
                "then uses an MCP Remediation Ledger to keep AI-proposed actions human-approved."
            ),
            evidence=[
                evidence("README.md", "States the Agentic Incident Command Center thesis and Splunk-native framing."),
                evidence("architecture_diagram.md", "Shows the Splunk data flow, AI/MCP investigation path, and approval boundary."),
                evidence("submission/SPLUNK_MCP_RUNBOOK.md", "Explains the intended Splunk MCP Server integration path."),
                evidence("reports/latest_splunk_mcp_command_plan.html", "Shows the live Splunk/MCP setup plan without executing it."),
                evidence("reports/latest_splunk_mcp_prompt_pack.html", "Shows the exact evidence-backed prompts and stop conditions for optional MCP proof."),
                evidence("reports/latest_splunk_mcp_proof_capture_manifest.html", "Shows the capture slots and readback gates for optional live MCP proof."),
            ],
            remaining_gate="Live Splunk/MCP proof still requires explicit user approval.",
        ),
        Criterion(
            section="Stage One Viability",
            title="Submission requirements",
            official_basis="The submission needs a public code URL, public demo video, description, track, architecture diagram, and runnable project materials.",
            readiness="local_ready_external_urls_pending",
            judge_message=(
                "The local package contains the code, open-source license, architecture diagram, "
                "run instructions, demo script, public-candidate folder, and URL placeholders."
            ),
            evidence=[
                evidence("LICENSE", "Open-source license candidate for the public repository."),
                evidence("reports/latest_devpost_final_copy.html", "Copy/paste Devpost text with pending URL gates."),
                evidence("reports/latest_video_cue_sheet.html", "Under-three-minute demo structure and screen-safety guardrails."),
                evidence("reports/latest_public_repo_publish_brief.html", "Clean public repository publication evidence and stop conditions."),
                evidence("reports/latest_submission_url_validation.html", "Shows repository/video URLs are pending until approved."),
            ],
            remaining_gate="Public repository URL and public demo video URL are still pending approval.",
        ),
        Criterion(
            section="Stage Two Judging",
            title="Technological Implementation",
            official_basis="Quality software development, consistent run behavior, and credible platform implementation.",
            readiness="strong_local_evidence",
            judge_message=(
                "The implementation is deterministic, standard-library Python, testable locally, "
                "and produces Splunk-ready CSV, SPL-equivalent proof, a dashboard, and a packaged Splunk app candidate."
            ),
            evidence=[
                evidence("prototype/agentops_control_tower.py", "Generates synthetic events, analysis, dashboard, SPL examples, and MCP preview."),
                evidence("tests/test_agentops_control_tower.py", "Unit tests cover event generation and blocked/approval analysis."),
                evidence("reports/latest_local_spl_query_results.html", "Shows the SPL query intent returns concrete synthetic event evidence."),
                evidence("reports/latest_splunk_app_package_manifest.html", "Shows .spl package members and package integrity."),
                evidence("scripts/validate_submission_packet.py", "Full local validator covering root, public candidate, scans, and smoke tests."),
            ],
            remaining_gate="Live Splunk import and MCP-assisted answer remain optional, post-approval proof.",
        ),
        Criterion(
            section="Stage Two Judging",
            title="Design",
            official_basis="User experience and design should be well thought out.",
            readiness="strong_local_evidence",
            judge_message=(
                "The design is organized around the human reviewer workflow: identify risk, "
                "see evidence, decide approve/hold/block, and keep external actions gated."
            ),
            evidence=[
                evidence("reports/latest_control_tower.html", "Main dashboard with KPIs, incident summary, approval queue, and MCP Remediation Ledger."),
                evidence("assets/dashboard_preview.png", "Static preview for README and Devpost review."),
                evidence("reports/latest_demo_tour.html", "Recording-friendly walkthrough showing the intended user path."),
                evidence("reports/latest_judge_quickstart.html", "Five-minute review path for judges and final reviewers."),
            ],
            remaining_gate="Public video recording still needs approval and screen-safety readback.",
        ),
        Criterion(
            section="Stage Two Judging",
            title="Potential Impact",
            official_basis="The project should show meaningful impact for observability, security operations, or developer productivity.",
            readiness="strong_local_evidence",
            judge_message=(
                "The pattern can apply to any agentic workflow where AI can notify, publish, "
                "deploy, access tools, or prepare sensitive actions faster than people can review them."
            ),
            evidence=[
                evidence("submission/DEVPOST_SUBMISSION_DRAFT.md", "Frames the problem and practical value."),
                evidence("submission/REQUIREMENTS_MATRIX.md", "Maps built artifacts to requirements and impact claims."),
                evidence("reports/latest_submission_gate_ledger.html", "Shows how external action gates can be audited and reused."),
                evidence("reports/latest_post_action_evidence_brief.html", "Defines completion evidence after public or submitted actions."),
            ],
            remaining_gate="Impact story is ready locally; public demo is still pending.",
        ),
        Criterion(
            section="Stage Two Judging",
            title="Quality of the Idea",
            official_basis="The project should be creative, unique, and clearly motivated.",
            readiness="strong_local_evidence",
            judge_message=(
                "Most agent demos emphasize autonomy. This idea emphasizes operational control: "
                "Splunk becomes the evidence layer and MCP becomes a governed investigation interface."
            ),
            evidence=[
                evidence("submission/JUDGING_ALIGNMENT.md", "Maps the idea to judging criteria and bonus alignment."),
                evidence("reports/latest_mcp_investigation.md", "Shows evidence-backed investigation output with event IDs."),
                evidence("submission/SPL_QUERIES.md", "Shows reusable query patterns for the AgentOps event model."),
                evidence("reports/latest_splunk_mcp_proof_brief.html", "Defines how to upgrade claims after verified live proof."),
                evidence("reports/latest_splunk_mcp_prompt_pack.html", "Defines the judge-visible MCP prompt/readback path with citations."),
                evidence("reports/latest_claim_evidence_matrix.html", "Maps allowed public claims to evidence and avoid wording."),
            ],
            remaining_gate="Best-use-of-MCP claim should remain design/local-proof wording until live proof is approved.",
        ),
        Criterion(
            section="Bonus Alignment",
            title="Best Use of Splunk MCP Server",
            official_basis="Bonus prize fit depends on intelligent, agent-driven use of Splunk MCP Server for contextual insight and decisions.",
            readiness="local_design_ready_live_proof_pending",
            judge_message=(
                "The package is built for Splunk MCP Server: an agent asks which operation needs human review first, "
                "and the answer cites event IDs, risk scores, policy decisions, and evidence references."
            ),
            evidence=[
                evidence("submission/SPLUNK_MCP_RUNBOOK.md", "Post-approval runbook for Splunk MCP setup and proof capture."),
                evidence("reports/latest_splunk_mcp_command_plan.html", "Command plan for synthetic import, app install, MCP setup, and proof."),
                evidence("reports/latest_splunk_mcp_proof_brief.html", "Success criteria and stop conditions for live proof."),
                evidence("reports/latest_splunk_mcp_prompt_pack.html", "Prompt pack with SPL, expected event citations, success readbacks, and safety stop conditions."),
                evidence("reports/latest_splunk_mcp_proof_capture_manifest.html", "Capture manifest with approved scope, evidence slots, readback expectations, and claim-upgrade gate."),
                evidence("reports/latest_claim_evidence_matrix.html", "Keeps MCP wording to designed-for/local-proof until live proof exists."),
                evidence("reports/latest_claim_boundary_validation.html", "Checks that live Splunk/MCP claims are not overstated."),
            ],
            remaining_gate="Optional live Splunk/MCP proof requires explicit account/license/MCP approval.",
        ),
    ]


def criterion_to_dict(root: Path, item: Criterion) -> dict[str, Any]:
    evidence_items = [
        {
            "path": entry.path,
            "exists": exists(root, entry.path),
            "reason": entry.reason,
        }
        for entry in item.evidence
    ]
    missing = [entry["path"] for entry in evidence_items if not entry["exists"]]
    return {
        "section": item.section,
        "title": item.title,
        "official_basis": item.official_basis,
        "readiness": item.readiness,
        "judge_message": item.judge_message,
        "evidence": evidence_items,
        "missing_evidence": missing,
        "remaining_gate": item.remaining_gate,
        "ready": not missing,
    }


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    criteria = [criterion_to_dict(root, item) for item in build_criteria()]
    stage_one_pass_fail_baseline = build_stage_one_pass_fail_baseline(root)
    mcp_bonus_claim_boundary = build_mcp_bonus_claim_boundary(root, state)
    missing = [
        f"{item['title']}:{path}"
        for item in criteria
        for path in item["missing_evidence"]
    ]
    missing.extend(
        f"stage_one_pass_fail:{item['requirement']}:{path}"
        for item in stage_one_pass_fail_baseline
        for path in item["missing_evidence"]
    )
    missing.extend(
        f"mcp_bonus_claim_boundary:{path}"
        for path in mcp_bonus_claim_boundary["missing_evidence"]
    )
    public_candidate = is_public_candidate_root(root)
    validation_snapshot = local_submission_snapshot(state, public_candidate)
    validation_ready = (
        validation_snapshot["status"] == "ready_for_user_review"
        and validation_snapshot["failed_count"] == 0
    )
    status_ready = not missing and (public_candidate or validation_ready or state["go_no_go"].get("local_ready") is True)
    release_zip_status = state["release_smoke"].get("status", "missing")
    if release_zip_status == "fail":
        release_zip_status = "pending_zip_smoke_refresh"
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if status_ready else "needs_more_evidence",
        "root_type": "public_candidate" if public_candidate else "workspace",
        "official_rules_source": OFFICIAL_RULES_SOURCE,
        "rules_last_checked_by_package": "2026-06-04 JST",
        "local_submission_status": validation_snapshot["status"],
        "validation_failed_count": validation_snapshot["failed_count"],
        "local_submission_source": validation_snapshot["source"],
        "final_submit_ready": bool(
            state["go_no_go"].get("final_submit_ready", state["validation"].get("final_submit_ready", False))
        ),
        "url_validation_status": state["url_validation"].get("status", "missing"),
        "approved_public_urls_exists": bool(state["validation"].get("approved_public_urls_exists", False)),
        "post_action_evidence_ready": bool(state["post_action"].get("post_action_evidence_ready", False)),
        "release_zip_status": release_zip_status,
        "splunk_app_package_status": state["splunk_app"].get("status", "missing"),
        "claim_boundary_status": state["claim_boundary"].get("status", "missing"),
        "pending_gates": state["gate_ledger"].get("pending_gates", []),
        "stage_one_pass_fail_basis": (
            "Stage One is treated as a pass/fail viability gate before Stage Two scoring; "
            "these checks are the local minimum review baseline."
        ),
        "stage_one_pass_fail_baseline": stage_one_pass_fail_baseline,
        "stage_one_pass_fail_ready": all(item["ready"] for item in stage_one_pass_fail_baseline),
        "stage_two_scored_criteria": [
            "Technological Implementation",
            "Design",
            "Potential Impact",
            "Quality of the Idea",
        ],
        "mcp_bonus_claim_boundary": mcp_bonus_claim_boundary,
        "criteria": criteria,
        "missing_evidence": missing,
        "ready_criteria_count": sum(1 for item in criteria if item["ready"]),
        "total_criteria_count": len(criteria),
        "recommended_judge_path": [
            "Open reports/latest_judge_quickstart.html.",
            "Review this scorecard by Stage One, Stage Two, and bonus alignment.",
            "Open reports/latest_control_tower.html and reports/latest_demo_tour.html.",
            "Review reports/latest_local_spl_query_results.html and reports/latest_splunk_app_package_manifest.html.",
            "Review reports/latest_submission_gate_ledger.html before any external approval.",
            "Keep live Splunk/MCP wording local-design-only until approved proof exists.",
        ],
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Judge Scorecard",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Official rules source: {payload['official_rules_source']}",
        f"Rules last checked by package: {payload['rules_last_checked_by_package']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        "",
        "## Recommended Judge Path",
        "",
    ]
    for item in payload["recommended_judge_path"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Stage One Pass/Fail Baseline",
        "",
        payload["stage_one_pass_fail_basis"],
        "",
        f"Stage One baseline ready: {str(payload['stage_one_pass_fail_ready']).lower()}",
        "",
    ])
    for item in payload["stage_one_pass_fail_baseline"]:
        lines.extend([
            f"### {item['requirement']}",
            "",
            f"Local status: {item['local_status']}",
            f"Ready: {str(item['ready']).lower()}",
            f"Official basis: {item['official_basis']}",
            "",
            "Evidence:",
        ])
        for evidence_item in item["evidence"]:
            status = "present" if evidence_item["exists"] else "missing"
            lines.append(f"- `{evidence_item['path']}` ({status})")
        lines.extend(["", f"Remaining gate: {item['remaining_gate']}", ""])
    lines.extend([
        "## Stage Two Scored Criteria",
        "",
    ])
    for item in payload["stage_two_scored_criteria"]:
        lines.append(f"- {item}")
    boundary = payload["mcp_bonus_claim_boundary"]
    lines.extend([
        "",
        "## MCP Bonus Claim Boundary",
        "",
        f"Bonus category: {boundary['bonus_category']}",
        f"Live Splunk MCP verified: {str(boundary['live_splunk_mcp_verified']).lower()}",
        f"Live Splunk verified: {str(boundary['live_splunk_verified']).lower()}",
        f"Local MCP SDK adapter verified: {str(boundary['mcp_protocol_adapter_verified']).lower()}",
        f"Official Splunk MCP Server verified: {str(boundary['official_splunk_mcp_server_verified']).lower()}",
        f"Current safe claim: {boundary['current_safe_claim']}",
        "",
        "Blocked claims until verified:",
    ])
    for item in boundary["blocked_claims_until_verified"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        f"Upgrade condition: {boundary['upgrade_condition']}",
        "",
        "Evidence:",
    ])
    for evidence_item in boundary["evidence"]:
        status = "present" if evidence_item["exists"] else "missing"
        lines.append(f"- `{evidence_item['path']}` ({status})")
    lines.extend(["", "## Criteria", ""])
    for criterion in payload["criteria"]:
        lines.extend([
            f"### {criterion['section']}: {criterion['title']}",
            "",
            f"Readiness: {criterion['readiness']}",
            f"Ready: {str(criterion['ready']).lower()}",
            "",
            f"Official basis: {criterion['official_basis']}",
            "",
            f"Judge message: {criterion['judge_message']}",
            "",
            "Evidence:",
        ])
        for item in criterion["evidence"]:
            status = "present" if item["exists"] else "missing"
            lines.append(f"- `{item['path']}` ({status}) - {item['reason']}")
        lines.extend([
            "",
            f"Remaining gate: {criterion['remaining_gate']}",
            "",
        ])
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    snapshot_rows = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in [
            ("Local submission status", payload["local_submission_status"]),
            ("Validation failed count", payload["validation_failed_count"]),
            ("Final submit ready", payload["final_submit_ready"]),
            ("Approved public URLs file", payload["approved_public_urls_exists"]),
            ("URL validation", payload["url_validation_status"]),
            ("Release ZIP", payload["release_zip_status"]),
            ("Splunk app package", payload["splunk_app_package_status"]),
            ("Claim boundary", payload["claim_boundary_status"]),
            ("Stage One pass/fail baseline", payload["stage_one_pass_fail_ready"]),
            ("Live Splunk MCP verified", payload["mcp_bonus_claim_boundary"]["live_splunk_mcp_verified"]),
            ("Live Splunk verified", payload["mcp_bonus_claim_boundary"]["live_splunk_verified"]),
            ("Local MCP SDK adapter verified", payload["mcp_bonus_claim_boundary"]["mcp_protocol_adapter_verified"]),
            ("Official Splunk MCP Server verified", payload["mcp_bonus_claim_boundary"]["official_splunk_mcp_server_verified"]),
            ("Ready criteria", f"{payload['ready_criteria_count']}/{payload['total_criteria_count']}"),
            ("Pending gates", ", ".join(payload["pending_gates"]) if payload["pending_gates"] else "none"),
        ]
    )
    path_items = "".join(f"<li>{esc(item)}</li>" for item in payload["recommended_judge_path"])
    baseline_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['requirement'])}</td>"
        f"<td class=\"{'ready' if item['ready'] else 'fail'}\">{esc(item['local_status'])}</td>"
        f"<td>{esc(item['official_basis'])}</td>"
        f"<td>{esc(', '.join(entry['path'] for entry in item['evidence']))}<p class=\"pending\">{esc(item['remaining_gate'])}</p></td>"
        "</tr>"
        for item in payload["stage_one_pass_fail_baseline"]
    )
    scored_items = "".join(f"<li>{esc(item)}</li>" for item in payload["stage_two_scored_criteria"])
    mcp_boundary = payload["mcp_bonus_claim_boundary"]
    blocked_claims = "".join(f"<li>{esc(item)}</li>" for item in mcp_boundary["blocked_claims_until_verified"])
    mcp_evidence = "".join(
        f"<li><code>{esc(item['path'])}</code> "
        f"<span class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</span></li>"
        for item in mcp_boundary["evidence"]
    )
    sections = []
    for section in ["Stage One Viability", "Stage Two Judging", "Bonus Alignment"]:
        rows = []
        for criterion in [item for item in payload["criteria"] if item["section"] == section]:
            evidence_rows = "<ul>" + "".join(
                f"<li><code>{esc(item['path'])}</code> "
                f"<span class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</span>"
                f" - {esc(item['reason'])}</li>"
                for item in criterion["evidence"]
            ) + "</ul>"
            rows.append(
                "<tr>"
                f"<td>{esc(criterion['title'])}</td>"
                f"<td class=\"{'ready' if criterion['ready'] else 'fail'}\">{esc(criterion['readiness'])}</td>"
                f"<td>{esc(criterion['official_basis'])}</td>"
                f"<td>{esc(criterion['judge_message'])}{evidence_rows}<p class=\"pending\">{esc(criterion['remaining_gate'])}</p></td>"
                "</tr>"
            )
        sections.append(f"""    <section>
      <h2>{esc(section)}</h2>
      <table>
        <thead><tr><th>Criterion</th><th>Readiness</th><th>Official Basis</th><th>Judge Message and Evidence</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>""")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Judge Scorecard</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Judge Scorecard</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
    <p>Official rules source: {esc(payload['official_rules_source'])}</p>
  </header>
  <main>
    <section>
      <h2>Snapshot</h2>
      <table><tbody>{snapshot_rows}</tbody></table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Recommended Judge Path</h2>
      <ol>{path_items}</ol>
    </section>
    <section>
      <h2>Stage One Pass/Fail Baseline</h2>
      <p>{esc(payload['stage_one_pass_fail_basis'])}</p>
      <table>
        <thead><tr><th>Requirement</th><th>Local Status</th><th>Official Basis</th><th>Evidence and Gate</th></tr></thead>
        <tbody>{baseline_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Stage Two Scored Criteria</h2>
      <ul>{scored_items}</ul>
    </section>
    <section>
      <h2>MCP Bonus Claim Boundary</h2>
      <p><strong>{esc(mcp_boundary['bonus_category'])}</strong></p>
      <p>Live Splunk MCP verified: <span class="{'ready' if mcp_boundary['live_splunk_mcp_verified'] else 'pending'}">{esc(mcp_boundary['live_splunk_mcp_verified'])}</span></p>
      <p>Current safe claim: {esc(mcp_boundary['current_safe_claim'])}</p>
      <p>Blocked claims until verified:</p>
      <ul>{blocked_claims}</ul>
      <p class="pending">{esc(mcp_boundary['upgrade_condition'])}</p>
      <ul>{mcp_evidence}</ul>
    </section>
{chr(10).join(sections)}
  </main>
</body>
</html>
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run(root: Path) -> dict[str, Any]:
    payload = build_payload(root)
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_judge_scorecard.json", payload)
    (reports / "latest_judge_scorecard.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_judge_scorecard.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "root_type": payload["root_type"],
        "ready_criteria_count": payload["ready_criteria_count"],
        "total_criteria_count": payload["total_criteria_count"],
        "missing_evidence": payload["missing_evidence"],
        "html": "reports/latest_judge_scorecard.html",
        "markdown": "reports/latest_judge_scorecard.md",
        "json": "reports/latest_judge_scorecard.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local judge scorecard for Agentic Incident Command Center.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
