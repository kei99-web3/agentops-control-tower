from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ApprovalRequest:
    key: str
    title: str
    status: str
    purpose: str
    exact_operation: str
    benefit: str
    main_risk: str
    verification: str
    evidence: list[str]


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def file_exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def official_mcp_readback_verified(root: Path) -> bool:
    readback = root / "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md"
    if not readback.exists():
        return False
    text = readback.read_text(encoding="utf-8").lower()
    return all(
        marker in text
        for marker in [
            "status: ready_for_claim_update",
            "checksum match: yes",
            "mcp connection status: connected",
            "tool used: `splunk_run_query`",
            "official splunk mcp server was installed and verified",
            "production splunk cloud deployment is not claimed",
        ]
    )


def public_repo_evidence(root: Path) -> list[str]:
    if is_public_candidate_root(root):
        return [
            "README.md",
            "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
            "reports/latest_public_repo_publication_preflight.html",
            "reports/latest_public_repo_dry_run.html",
            "reports/latest_demo_tour.html",
            "reports/latest_video_readiness.html",
            "reports/latest_devpost_submission_packet.html",
            "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
        ]
    return [
        "public_repo_candidate/agentops-control-tower/README.md",
        "public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md",
        "reports/latest_public_repo_publication_preflight.html",
        "reports/latest_public_repo_dry_run.html",
        "release/agentops-control-tower-public-candidate.zip",
        "reports/latest_release_zip_smoke_test.html",
    ]


def devpost_evidence(root: Path) -> list[str]:
    if is_public_candidate_root(root):
        return [
            "reports/latest_devpost_final_copy.md",
            "reports/latest_final_go_no_go.html",
            "submission/DEVPOST_FIELD_MAP.md",
            "submission/SUBMISSION_LAUNCH_RUNBOOK.md",
        ]
    return [
        "reports/latest_devpost_final_copy.md",
        "reports/latest_submission_validation.html",
        "submission/DEVPOST_FIELD_MAP.md",
        "submission/SUBMISSION_LAUNCH_RUNBOOK.md",
    ]


def load_state(root: Path) -> dict[str, Any]:
    return {
        "submission": read_json(root / "reports/latest_submission_validation.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "urls": read_json(root / "reports/latest_submission_url_validation.json"),
        "repo_publication_preflight": read_json(root / "reports/latest_public_repo_publication_preflight.json"),
        "video": read_json(root / "reports/latest_video_readiness.json"),
        "video_upload_preflight": read_json(root / "reports/latest_public_video_upload_preflight.json"),
        "devpost": read_json(root / "reports/latest_devpost_final_copy.json"),
        "smoke": read_json(root / "reports/latest_release_zip_smoke_test.json"),
    }


def local_submission_status(state: dict[str, Any]) -> str:
    submission = state["submission"]
    go_no_go = state["go_no_go"]
    status = submission.get("overall_status", go_no_go.get("status", "missing"))
    if (
        status == "needs_more_evidence"
        and go_no_go.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready") is True
        and go_no_go.get("missing_local_evidence", []) == []
        and go_no_go.get("missing_public_candidate_evidence", []) == []
    ):
        return "ready_for_user_review"
    return status


def build_requests(root: Path, state: dict[str, Any]) -> list[ApprovalRequest]:
    local_ready = bool(state["submission"].get("local_checks_passed")) or bool(state["go_no_go"].get("local_ready"))
    repo_pending = "repository_url" in state["urls"].get("pending_urls", [])
    video_pending = "demo_video_url" in state["urls"].get("pending_urls", [])
    repo_preflight_ready = state["repo_publication_preflight"].get("status") == "ready_for_user_review"
    video_ready = state["video"].get("status") == "ready_for_recording_review"
    video_preflight_ready = state["video_upload_preflight"].get("status") == "ready_for_user_review"
    zip_ready = state["smoke"].get("status") == "pass" or is_public_candidate_root(root)

    repo_status = "ready_for_user_decision" if local_ready and zip_ready and repo_preflight_ready and repo_pending else "not_ready"
    video_status = "ready_for_user_decision" if local_ready and video_ready and video_preflight_ready and video_pending else "not_ready"
    official_mcp_done = official_mcp_readback_verified(root)
    splunk_status = "completed" if official_mcp_done else "optional_user_decision"
    devpost_status = "blocked_until_public_urls" if repo_pending or video_pending else "ready_for_user_decision"

    return [
        ApprovalRequest(
            key="public_github_repository",
            title="Public GitHub Repository",
            status=repo_status,
            purpose="Make the clean Agentic Incident Command Center code package reviewable for Devpost judges.",
            exact_operation="Run scripts/verify_public_repo_publication_gate.py with the exact approval phrase, public git identity, and manual safety confirmations, then use scripts/publish_public_repo_after_approval.py to create and push the public repository only after explicit approval.",
            benefit="Satisfies the public open-source repository requirement and lets judges run the prototype, inspect the Splunk app candidate, and review local evidence.",
            main_risk="Accidental disclosure of local paths, credentials, or private workspace material if the wrong folder is published or Git is initialized inside the private workspace.",
            verification="Review reports/latest_public_repo_publication_preflight.html, run the guarded helper, confirm public candidate secret/internal scans and isolated staging dry run pass, open the public repository URL, then validate the URL before local URL writeback.",
            evidence=public_repo_evidence(root),
        ),
        ApprovalRequest(
            key="public_demo_video",
            title="Public Demo Video",
            status=video_status,
            purpose="Show the Agentic Incident Command Center flow in a concise Devpost-compatible demo.",
            exact_operation="Run scripts/verify_public_video_upload_gate.py with the exact approval phrase and manual safety confirmations, record the browser walkthrough using reports/latest_demo_tour.html and submission/VIDEO_RECORDING_RUNBOOK.md, then upload publicly only after explicit approval.",
            benefit="Gives judges a fast path through the problem, dashboard, local SPL proof, MCP Remediation Ledger, and Splunk MCP boundary.",
            main_risk="The recording could expose private tabs, terminals, account pages, local paths, or overclaim live Splunk MCP verification before it exists.",
            verification="Review reports/latest_public_video_upload_preflight.html and reports/latest_video_readiness.html, confirm the recording is under 3 minutes, watch the uploaded video while checking the screen safety list, then validate the public video URL.",
            evidence=[
                "reports/latest_demo_tour.html",
                "reports/latest_video_readiness.html",
                "reports/latest_public_video_upload_preflight.html",
                "submission/DEMO_VIDEO_SCRIPT.md",
                "submission/VIDEO_RECORDING_RUNBOOK.md",
            ],
        ),
        ApprovalRequest(
            key="live_splunk_bonus_proof",
            title="Optional Live Splunk / MCP Proof",
            status=splunk_status,
            purpose=(
                "Completed: strengthen the Best Use of Splunk MCP Server bonus claim with local official-MCP proof using synthetic data only."
                if official_mcp_done
                else "Strengthen the Best Use of Splunk MCP Server bonus claim if time and credentials are approved."
            ),
            exact_operation=(
                "No further external setup is needed for the local official-MCP proof; keep claims bounded to local Splunk Enterprise Docker with synthetic data."
                if official_mcp_done
                else "Set up Splunk account/license, import only synthetic data into agentops_events, configure Splunk MCP Server with approved scope, and capture proof."
            ),
            benefit=(
                "Improves technical implementation evidence and supports bounded wording: official Splunk MCP Server verified in local Splunk Enterprise Docker with synthetic data."
                if official_mcp_done
                else "Improves technical implementation evidence and allows stronger wording: verified through Splunk MCP Server."
            ),
            main_risk=(
                "Overclaiming production Splunk Cloud deployment or exposing credentials in public video/screenshots."
                if official_mcp_done
                else "Requires credentials, account setup, possible cloud cost, and careful scope control. It must not expose private data or secrets."
            ),
            verification=(
                "Review submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md and rerun claim-boundary validation."
                if official_mcp_done
                else "Follow submission/SPLUNK_MCP_RUNBOOK.md, the prompt pack, and the proof capture manifest; run the high-risk and approval queue SPL queries, capture evidence, then rerun claim-boundary and submission validation."
            ),
            evidence=[
                "submission/SPLUNK_MCP_RUNBOOK.md",
                "reports/latest_splunk_mcp_proof_brief.html",
                "reports/latest_splunk_mcp_prompt_pack.html",
                "reports/latest_splunk_mcp_proof_capture_manifest.html",
                "submission/SPLUNK_MCP_PROMPT_PACK.md",
                "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md",
                "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md",
                "data/splunk_agentops_events.csv",
                "submission/SPL_QUERIES.md",
                "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
            ],
        ),
        ApprovalRequest(
            key="devpost_final_submission",
            title="Devpost Final Submission",
            status=devpost_status,
            purpose="Submit the completed Splunk Agentic Ops Hackathon entry.",
            exact_operation="After public repo and public video URLs are inserted and validation passes, review reports/latest_devpost_final_copy.md and press the Devpost submit button only with explicit final approval.",
            benefit="Completes the hackathon submission with a locally verified code package, demo video, architecture diagram, and safe claim wording.",
            main_risk="Submitting too early with pending URLs, overclaims, wrong track selection, or missing public artifacts.",
            verification="Confirm reports/latest_submission_validation.html is ready_for_user_review, repository and video URLs are public, Devpost fields match submission/DEVPOST_FIELD_MAP.md, and final submit approval is explicit.",
            evidence=devpost_evidence(root),
        ),
    ]


def request_to_dict(request: ApprovalRequest, root: Path) -> dict[str, Any]:
    return {
        "key": request.key,
        "title": request.title,
        "status": request.status,
        "purpose": request.purpose,
        "exact_operation": request.exact_operation,
        "benefit": request.benefit,
        "main_risk": request.main_risk,
        "verification": request.verification,
        "evidence": [
            {"path": item, "exists": file_exists(root, item)}
            for item in request.evidence
        ],
    }


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    requests = [request_to_dict(item, root) for item in build_requests(root, state)]
    missing_evidence = [
        f"{request['key']}:{item['path']}"
        for request in requests
        for item in request["evidence"]
        if not item["exists"]
    ]
    ready_requests = [item["key"] for item in requests if item["status"] == "ready_for_user_decision"]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not missing_evidence else "needs_more_evidence",
        "local_submission_status": local_submission_status(state),
        "local_checks_passed": state["submission"].get("local_checks_passed", False),
        "ready_requests": ready_requests,
        "missing_evidence": missing_evidence,
        "approval_requests": requests,
        "non_action_boundary": "This packet does not publish, upload, submit, create accounts, configure credentials, or update Devpost.",
        "recommended_next_decision": "Approve or hold public GitHub publication and demo video recording/upload.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# External Approval Packet",
        "",
        f"Status: {payload['status']}",
        f"Local submission status: {payload['local_submission_status']}",
        "",
        "This packet lists the external actions that still require explicit human approval.",
        "",
        "## Approval Requests",
        "",
    ]
    for request in payload["approval_requests"]:
        lines.extend([
            f"### {request['title']}",
            "",
            f"Status: {request['status']}",
            "",
            f"Purpose: {request['purpose']}",
            "",
            f"Exact operation: {request['exact_operation']}",
            "",
            f"Benefit: {request['benefit']}",
            "",
            f"Main risk: {request['main_risk']}",
            "",
            f"Verification: {request['verification']}",
            "",
            "Evidence:",
        ])
        for item in request["evidence"]:
            marker = "present" if item["exists"] else "missing"
            lines.append(f"- {item['path']} ({marker})")
        lines.append("")
    lines.extend([
        "## Boundary",
        "",
        payload["non_action_boundary"],
        "",
    ])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    cards = []
    for request in payload["approval_requests"]:
        evidence_rows = "\n".join(
            "<tr>"
            f"<td>{esc(item['path'])}</td>"
            f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
            "</tr>"
            for item in request["evidence"]
        )
        cards.append(f"""    <section>
      <h2>{esc(request['title'])}</h2>
      <p>Status: <span class="{'ready' if request['status'] == 'ready_for_user_decision' else 'pending'}">{esc(request['status'])}</span></p>
      <table>
        <tbody>
          <tr><th>Purpose</th><td>{esc(request['purpose'])}</td></tr>
          <tr><th>Exact operation</th><td>{esc(request['exact_operation'])}</td></tr>
          <tr><th>Benefit</th><td>{esc(request['benefit'])}</td></tr>
          <tr><th>Main risk</th><td>{esc(request['main_risk'])}</td></tr>
          <tr><th>Verification</th><td>{esc(request['verification'])}</td></tr>
        </tbody>
      </table>
      <h3>Evidence</h3>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>""")
    cards_html = "\n".join(cards)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>External Approval Packet</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; width: 180px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
  </style>
</head>
<body>
  <header>
    <h1>External Approval Packet</h1>
    <p>Status: <span class="ready">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Decision Needed</h2>
      <p>{esc(payload['recommended_next_decision'])}</p>
      <p class="pending">{esc(payload['non_action_boundary'])}</p>
    </section>
{cards_html}
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
    write_json(reports / "latest_external_approval_packet.json", payload)
    (reports / "latest_external_approval_packet.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_external_approval_packet.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "ready_requests": payload["ready_requests"],
        "html": "reports/latest_external_approval_packet.html",
        "markdown": "reports/latest_external_approval_packet.md",
        "json": "reports/latest_external_approval_packet.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an external approval packet for user-reviewed submission gates.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
