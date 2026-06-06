from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This matrix is local claim-support evidence only. It does not publish, upload, "
    "connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything."
)


@dataclass
class Evidence:
    path: str
    reason: str


@dataclass
class Claim:
    key: str
    public_claim: str
    support_status: str
    allowed_wording: str
    avoid_wording: str
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


def evidence(path: str, reason: str) -> Evidence:
    return Evidence(path=path, reason=reason)


def build_claims() -> list[Claim]:
    return [
        Claim(
            key="synthetic_data_boundary",
            public_claim="The demo uses synthetic incident data only.",
            support_status="locally_supported",
            allowed_wording="The current demo uses synthetic checkout-incident events only; no real secrets, accounts, customer data, cloud accounts, or private logs are used.",
            avoid_wording="Avoid implying the demo uses real customer logs, production secrets, or live private operations.",
            evidence=[
                evidence("data/synthetic_agentops_events.jsonl", "Synthetic source events used by the local demo."),
                evidence("data/agentops_event_schema.json", "Schema describing the synthetic event model."),
                evidence("data/splunk_agentops_events.csv", "Splunk-ready export generated from synthetic events."),
                evidence("submission/OFFICIAL_REQUIREMENTS_AUDIT.md", "Records the synthetic-data-only public demo boundary."),
            ],
            remaining_gate="None for local demo evidence; keep the same boundary in public video and Devpost text.",
        ),
        Claim(
            key="splunk_ready_event_model",
            public_claim="Agentic Incident Command Center produces Splunk-ready incident data and SPL query examples.",
            support_status="locally_supported",
            allowed_wording="The package exports Splunk-ready CSV and includes SPL examples plus a local SPL-equivalent proof report.",
            avoid_wording="Avoid saying the data has already been imported into live Splunk unless approved live proof exists.",
            evidence=[
                evidence("data/splunk_agentops_events.csv", "CSV intended for an agentops_events index after approval."),
                evidence("submission/SPL_QUERIES.md", "SPL examples for incident timeline, root-cause evidence, remediation ledger, MCP investigation context, and blast radius."),
                evidence("reports/latest_local_spl_query_results.html", "Local SPL-equivalent proof over the generated CSV."),
                evidence("architecture_diagram.md", "Shows the Splunk data-flow architecture."),
            ],
            remaining_gate="Live Splunk import requires explicit account/license approval.",
        ),
        Claim(
            key="mcp_remediation_ledger",
            public_claim="The MCP Remediation Ledger ranks proposed incident actions and cites evidence for human review.",
            support_status="locally_supported",
            allowed_wording="The local dashboard and analysis show rollback, WAF watch, stakeholder update, ticketing, and blocked credential-boundary items with evidence references.",
            avoid_wording="Avoid claiming fully autonomous remediation, production enforcement, or real incident execution.",
            evidence=[
                evidence("reports/latest_analysis.json", "Analysis output containing incident summary, root-cause candidates, remediation ledger, approval queue, and MCP preview."),
                evidence("reports/latest_control_tower.html", "Dashboard surface for root-cause ranking, blast radius, remediation ledger, and approval queue."),
                evidence("reports/latest_mcp_investigation.md", "Evidence-backed MCP investigation preview with event IDs."),
                evidence("prototype/agentops_control_tower.py", "Generates the ledger, recommendations, SPL examples, and dashboard."),
            ],
            remaining_gate="No external gate for local proof; keep real external actions human-approved.",
        ),
        Claim(
            key="human_approval_gates",
            public_claim="High-impact remediation remains behind explicit human approval gates.",
            support_status="locally_supported",
            allowed_wording="Rollback, WAF changes, stakeholder updates, public repo publication, video upload, URL writeback, live Splunk/MCP proof, and Devpost submission are modeled as explicit approval gates.",
            avoid_wording="Avoid saying remediation, publication, upload, URL writeback, live proof, or final submission has happened before readback evidence exists.",
            evidence=[
                evidence("reports/latest_submission_gate_ledger.html", "Gate ledger for public repo, video, optional live proof, and Devpost final submission."),
                evidence("reports/latest_external_approval_packet.html", "Explains purpose, benefits, risks, and verification for each external action."),
                evidence("reports/latest_post_action_evidence_brief.html", "Defines completion/readback evidence after each external action."),
                evidence("submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md", "Template for recording approved external-action readback without secrets."),
                evidence("reports/latest_submission_url_validation.html", "Shows public repo and video URLs are pending until approved."),
            ],
            remaining_gate="All external actions require explicit user approval before execution.",
        ),
        Claim(
            key="splunk_app_candidate",
            public_claim="The package includes a local Splunk app candidate.",
            support_status="locally_supported",
            allowed_wording="The package includes a local .spl app candidate with dashboard XML and saved searches for review.",
            avoid_wording="Avoid saying the app has been installed, uploaded, or accepted by Splunk unless that proof is captured.",
            evidence=[
                evidence("dist/agentops-control-tower-splunk-app.spl", "Local .spl package artifact."),
                evidence("reports/latest_splunk_app_package_manifest.html", "Package member list, SHA256, and no-install/no-upload boundary."),
                evidence("splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml", "Simple XML dashboard candidate."),
                evidence("splunk_app/agentops_control_tower/default/savedsearches.conf", "Saved search candidates for AgentOps queries."),
            ],
            remaining_gate="Install/upload/use in Splunk requires explicit approval.",
        ),
        Claim(
            key="splunk_mcp_design",
            public_claim="The project is designed for Splunk MCP Server investigation.",
            support_status="designed_pending_live_proof",
            allowed_wording="Agentic Incident Command Center is designed for Splunk MCP Server, with synthetic incident data, SPL examples, local SPL proof, and a live proof runbook.",
            avoid_wording="Avoid saying verified through Splunk MCP Server until approved live setup and proof capture are complete.",
            evidence=[
              evidence("submission/SPLUNK_MCP_RUNBOOK.md", "Post-approval runbook for live Splunk MCP setup and proof capture."),
              evidence("reports/latest_splunk_mcp_command_plan.html", "Command plan for account/license, synthetic import, app install, MCP setup, and proof."),
              evidence("reports/latest_splunk_mcp_proof_brief.html", "Success criteria and claim-upgrade rules for live proof."),
              evidence("reports/latest_splunk_mcp_prompt_pack.html", "Prompt pack with SPL, expected event citations, success readbacks, and stop conditions."),
              evidence("reports/latest_splunk_mcp_proof_capture_manifest.html", "Capture slots, expected readback, stop conditions, and claim-upgrade gate for optional live proof."),
              evidence("reports/latest_claim_boundary_validation.html", "Checks that public copy does not overclaim live Splunk/MCP proof."),
          ],
            remaining_gate="Optional live Splunk/MCP proof requires approved Splunk account/license and MCP configuration.",
        ),
        Claim(
            key="submission_state",
            public_claim="The local package is ready for user review, but final submission is not complete.",
            support_status="ready_for_user_review_external_gates_pending",
            allowed_wording="The local package is ready for user review; final submission is pending public repo URL, public video URL, approved URL writeback, and final Devpost approval.",
            avoid_wording="Avoid saying submitted, public, final, or approved until post-action evidence confirms it.",
            evidence=[
                evidence("reports/latest_final_go_no_go.html", "Separates local readiness from pending external gates."),
                evidence("scripts/validate_submission_packet.py", "Validator that reports final_submit_ready false and pending actions."),
                evidence("reports/latest_launch_decision_brief.html", "Approval order, approval phrases, and blocked final gates."),
                evidence("reports/latest_devpost_manual_fill_brief.html", "Devpost field fill and readback brief with pending URL fields."),
            ],
            remaining_gate="Public repo, public video, URL writeback, and Devpost final submission remain pending.",
        ),
    ]


def claim_to_dict(root: Path, claim: Claim) -> dict[str, Any]:
    evidence_items = [
        {
            "path": item.path,
            "exists": exists(root, item.path),
            "reason": item.reason,
        }
        for item in claim.evidence
    ]
    missing = [item["path"] for item in evidence_items if not item["exists"]]
    return {
        "key": claim.key,
        "public_claim": claim.public_claim,
        "support_status": claim.support_status,
        "allowed_wording": claim.allowed_wording,
        "avoid_wording": claim.avoid_wording,
        "evidence": evidence_items,
        "missing_evidence": missing,
        "remaining_gate": claim.remaining_gate,
        "ready": not missing,
    }


def build_payload(root: Path) -> dict[str, Any]:
    claim_boundary = read_json(root / "reports/latest_claim_boundary_validation.json")
    validation = read_json(root / "reports/latest_submission_validation.json")
    go_no_go = read_json(root / "reports/latest_final_go_no_go.json")
    claims = [claim_to_dict(root, item) for item in build_claims()]
    missing = [
        f"{claim['key']}:{path}"
        for claim in claims
        for path in claim["missing_evidence"]
    ]
    public_candidate = is_public_candidate_root(root)
    claim_boundary_clean = claim_boundary.get("status") == "pass" or public_candidate
    validation_status = validation.get("overall_status", go_no_go.get("status", "missing"))
    validation_source = "reports/latest_submission_validation.json" if validation else "reports/latest_final_go_no_go.json"
    validation_failed_count = validation.get("failed_count", "missing")
    if (
        validation_status == "needs_more_evidence"
        and go_no_go.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready") is True
        and go_no_go.get("missing_local_evidence", []) == []
        and go_no_go.get("missing_public_candidate_evidence", []) == []
    ):
        validation_status = "ready_for_user_review"
        validation_source = "reports/latest_final_go_no_go.json"
        validation_failed_count = 0
    ready = not missing and claim_boundary_clean
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if ready else "needs_more_evidence",
        "root_type": "public_candidate" if public_candidate else "workspace",
        "claim_boundary_status": claim_boundary.get("status", "missing"),
        "validation_status": validation_status,
        "validation_failed_count": validation_failed_count,
        "validation_source": validation_source,
        "final_submit_ready": bool(go_no_go.get("final_submit_ready", validation.get("final_submit_ready", False))),
        "approved_public_urls_exists": bool(validation.get("approved_public_urls_exists", False)),
        "claims": claims,
        "missing_evidence": missing,
        "ready_claim_count": sum(1 for item in claims if item["ready"]),
        "total_claim_count": len(claims),
        "safe_copy_rule": (
            "Use local-proof and designed-for wording until public URL, live Splunk/MCP, "
            "or Devpost submit evidence has been explicitly approved and read back."
        ),
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Claim Evidence Matrix",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Claim boundary status: {payload['claim_boundary_status']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Ready claims: {payload['ready_claim_count']}/{payload['total_claim_count']}",
        "",
        "## Safe Copy Rule",
        "",
        payload["safe_copy_rule"],
        "",
        "## Claims",
        "",
    ]
    for claim in payload["claims"]:
        lines.extend([
            f"### {claim['public_claim']}",
            "",
            f"Support status: {claim['support_status']}",
            f"Ready: {str(claim['ready']).lower()}",
            "",
            f"Allowed wording: {claim['allowed_wording']}",
            f"Avoid wording: {claim['avoid_wording']}",
            "",
            "Evidence:",
        ])
        for item in claim["evidence"]:
            status = "present" if item["exists"] else "missing"
            lines.append(f"- `{item['path']}` ({status}) - {item['reason']}")
        lines.extend([
            "",
            f"Remaining gate: {claim['remaining_gate']}",
            "",
        ])
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    snapshot_rows = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in [
            ("Claim boundary status", payload["claim_boundary_status"]),
            ("Validation status", payload["validation_status"]),
            ("Final submit ready", payload["final_submit_ready"]),
            ("Approved public URLs file", payload["approved_public_urls_exists"]),
            ("Ready claims", f"{payload['ready_claim_count']}/{payload['total_claim_count']}"),
        ]
    )
    claim_rows = []
    for claim in payload["claims"]:
        evidence_rows = "<ul>" + "".join(
            f"<li><code>{esc(item['path'])}</code> "
            f"<span class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</span>"
            f" - {esc(item['reason'])}</li>"
            for item in claim["evidence"]
        ) + "</ul>"
        claim_rows.append(
            "<tr>"
            f"<td>{esc(claim['public_claim'])}</td>"
            f"<td class=\"{'ready' if claim['ready'] else 'fail'}\">{esc(claim['support_status'])}</td>"
            f"<td>{esc(claim['allowed_wording'])}</td>"
            f"<td>{esc(claim['avoid_wording'])}</td>"
            f"<td>{evidence_rows}<p class=\"pending\">{esc(claim['remaining_gate'])}</p></td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Claim Evidence Matrix</title>
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
    <h1>Claim Evidence Matrix</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Snapshot</h2>
      <table><tbody>{snapshot_rows}</tbody></table>
      <p class="pending">{esc(payload['safe_copy_rule'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Claims</h2>
      <table>
        <thead><tr><th>Claim</th><th>Support</th><th>Allowed Wording</th><th>Avoid Wording</th><th>Evidence and Remaining Gate</th></tr></thead>
        <tbody>{''.join(claim_rows)}</tbody>
      </table>
    </section>
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
    write_json(reports / "latest_claim_evidence_matrix.json", payload)
    (reports / "latest_claim_evidence_matrix.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_claim_evidence_matrix.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "root_type": payload["root_type"],
        "ready_claim_count": payload["ready_claim_count"],
        "total_claim_count": payload["total_claim_count"],
        "missing_evidence": payload["missing_evidence"],
        "html": "reports/latest_claim_evidence_matrix.html",
        "markdown": "reports/latest_claim_evidence_matrix.md",
        "json": "reports/latest_claim_evidence_matrix.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local claim evidence matrix.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
