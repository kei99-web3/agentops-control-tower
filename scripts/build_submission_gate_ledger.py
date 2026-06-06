from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NON_ACTION_BOUNDARY = (
    "This ledger is advisory only. It does not create a repo, upload a video, "
    "create accounts, configure credentials, write approved URLs, update Devpost, or submit anything."
)


@dataclass
class Gate:
    key: str
    title: str
    status: str
    approval_required: str
    next_safe_action: str
    verification: str
    evidence: list[str]


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def is_pending(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("PENDING_")


def public_repo_evidence(root: Path) -> list[str]:
    if is_public_candidate_root(root):
        return [
            "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
            "reports/latest_external_approval_packet.html",
            "reports/latest_publication_command_plan.html",
            "reports/latest_submission_url_apply_plan.html",
        ]
    return [
        "public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md",
        "reports/latest_external_approval_packet.html",
        "reports/latest_publication_command_plan.html",
        "reports/latest_release_zip_smoke_test.html",
    ]


def video_evidence() -> list[str]:
    return [
        "reports/latest_demo_tour.html",
        "reports/latest_video_readiness.html",
        "reports/latest_video_command_plan.html",
        "submission/VIDEO_RECORDING_RUNBOOK.md",
    ]


def splunk_evidence() -> list[str]:
    return [
        "reports/latest_splunk_mcp_command_plan.html",
        "reports/latest_splunk_mcp_proof_brief.html",
        "reports/latest_splunk_mcp_prompt_pack.html",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "submission/SPLUNK_MCP_RUNBOOK.md",
        "submission/SPLUNK_MCP_PROMPT_PACK.md",
        "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md",
        "submission/SPL_QUERIES.md",
        "data/splunk_agentops_events.csv",
        "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
    ]


def devpost_evidence() -> list[str]:
    return [
        "reports/latest_devpost_final_copy.html",
        "reports/latest_devpost_submit_command_plan.html",
        "reports/latest_devpost_manual_fill_brief.html",
        "reports/latest_post_action_evidence_brief.html",
        "reports/latest_submission_url_validation.html",
        "reports/latest_final_go_no_go.html",
        "submission/DEVPOST_FIELD_MAP.md",
        "submission/SUBMISSION_LAUNCH_RUNBOOK.md",
    ]


def url_writeback_evidence() -> list[str]:
    return [
        "reports/latest_submission_url_validation.html",
        "reports/latest_submission_url_apply_plan.html",
        "reports/latest_devpost_final_copy.html",
        "reports/latest_final_go_no_go.html",
    ]


def gate_to_dict(root: Path, gate: Gate) -> dict[str, Any]:
    return {
        "key": gate.key,
        "title": gate.title,
        "status": gate.status,
        "approval_required": gate.approval_required,
        "next_safe_action": gate.next_safe_action,
        "verification": gate.verification,
        "evidence": [
            {"path": item, "exists": exists(root, item)}
            for item in gate.evidence
        ],
    }


def build_gates(root: Path, state: dict[str, Any]) -> list[Gate]:
    go_no_go = state["go_no_go"]
    approval = state["approval"]
    video = state["video"]
    mcp_plan = state["mcp_plan"]
    url_validation = state["url_validation"]
    submit_plan = state["submit_plan"]
    url_apply = state["url_apply"]

    ready_requests = set(approval.get("ready_requests", []))
    pending_urls = go_no_go.get("pending_urls", {})
    repo_url = pending_urls.get("repository_url", "PENDING_USER_APPROVAL_PUBLIC_REPO_URL")
    video_url = pending_urls.get("demo_video_url", "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL")

    repo_status = "approved_url_recorded" if not is_pending(repo_url) else (
        "ready_for_user_decision" if "public_github_repository" in ready_requests else "not_ready"
    )
    video_status = "approved_url_recorded" if not is_pending(video_url) else (
        "ready_for_user_decision"
        if "public_demo_video" in ready_requests and video.get("status") == "ready_for_recording_review"
        else "not_ready"
    )
    splunk_status = (
        "live_splunk_mcp_verified"
        if mcp_plan.get("live_splunk_mcp_verified") is True
        else "optional_user_decision"
        if mcp_plan.get("status") == "ready_for_user_review"
        else "not_ready"
    )
    final_submit_ready = bool(
        go_no_go.get("final_submit_ready") is True
        and url_validation.get("final_submit_ready") is True
        and submit_plan.get("final_submit_ready") is True
    )
    approved_urls_written = url_apply.get("approved_urls_file_written") is True
    url_writeback_status = (
        "approved_urls_written"
        if approved_urls_written and final_submit_ready
        else "blocked_until_public_urls"
        if is_pending(repo_url) or is_pending(video_url)
        else "ready_for_user_decision"
    )
    devpost_status = (
        "ready_for_final_approval"
        if final_submit_ready and approved_urls_written
        else "blocked_until_public_urls"
        if is_pending(repo_url) or is_pending(video_url)
        else "not_ready"
    )

    return [
        Gate(
            key="public_github_repository",
            title="Public GitHub Repository",
            status=repo_status,
            approval_required="Explicit approval is required before creating a public repository or pushing files.",
            next_safe_action="Review the publication command plan and hold until the public repository decision is explicit.",
            verification="After approval, confirm the public URL opens, then rerun URL validation and the submission packet validator.",
            evidence=public_repo_evidence(root),
        ),
        Gate(
            key="public_demo_video",
            title="Public Demo Video",
            status=video_status,
            approval_required="Explicit approval is required before recording, uploading, or making the video public.",
            next_safe_action="Review the video readiness report and command plan, then record only after the screen safety check is complete.",
            verification="Confirm the uploaded video is public, under 3 minutes, and does not expose private screens or overclaim live Splunk MCP proof.",
            evidence=video_evidence(),
        ),
        Gate(
            key="optional_live_splunk_mcp_proof",
            title="Optional Live Splunk / MCP Proof",
            status=splunk_status,
            approval_required="Explicit approval is required before Splunk account/license use, credential setup, data import, app install, MCP setup, or proof capture.",
            next_safe_action="Use the Splunk MCP command plan, prompt pack, and proof capture manifest if the optional bonus proof is approved.",
            verification="Capture live SPL and MCP evidence, then rerun claim-boundary validation before strengthening any bonus wording.",
            evidence=splunk_evidence(),
        ),
        Gate(
            key="approved_url_writeback",
            title="Approved URL Writeback",
            status=url_writeback_status,
            approval_required="Explicit approval is required before writing verified public URLs into local submission artifacts.",
            next_safe_action="Wait until the public repository and demo video URLs are real, public, and read back.",
            verification="Run prepare_submission_urls.py with both approved URLs, then rerun URL validation and final copy export.",
            evidence=url_writeback_evidence(),
        ),
        Gate(
            key="devpost_final_submission",
            title="Devpost Final Submission",
            status=devpost_status,
            approval_required="Explicit final approval is required before using a Devpost session, saving a draft, or pressing submit.",
            next_safe_action="Wait for public repo and video URLs, write approved URL evidence only after approval, then review final copy.",
            verification="Confirm approved public URLs, safe claim wording, selected track, architecture evidence, and final submit readback.",
            evidence=devpost_evidence(),
        ),
    ]


def load_state(root: Path) -> dict[str, Any]:
    return {
        "approval": read_json(root / "reports/latest_external_approval_packet.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
        "url_apply": read_json(root / "reports/latest_submission_url_apply_plan.json"),
        "video": read_json(root / "reports/latest_video_readiness.json"),
        "mcp_plan": read_json(root / "reports/latest_splunk_mcp_command_plan.json"),
        "submit_plan": read_json(root / "reports/latest_devpost_submit_command_plan.json"),
    }


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    gates = [gate_to_dict(root, gate) for gate in build_gates(root, state)]
    missing_evidence = [
        f"{gate['key']}:{item['path']}"
        for gate in gates
        for item in gate["evidence"]
        if not item["exists"]
    ]
    pending_gates = [
        gate["key"]
        for gate in gates
        if gate["status"] not in {"approved_url_recorded", "approved_urls_written", "live_splunk_mcp_verified", "ready_for_final_approval"}
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not missing_evidence else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": state["go_no_go"].get("local_ready", False),
        "final_submit_ready": state["go_no_go"].get("final_submit_ready", False),
        "pending_gates": pending_gates,
        "missing_evidence": missing_evidence,
        "gates": gates,
        "recommended_order": [
            "Review this Submission Gate Ledger and the External Approval Packet.",
            "Approve or hold public GitHub publication.",
            "Approve or hold public demo video recording/upload.",
            "Optionally approve live Splunk/MCP proof if the bonus path is worth the account and credential work.",
            "After public URLs are approved, write approved URL evidence locally and rerun validation.",
            "Only then request final Devpost submit approval.",
        ],
        "non_action_boundary": NON_ACTION_BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Submission Gate Ledger",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Local ready: {str(payload['local_ready']).lower()}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        "",
        "This ledger records the external gates that still need human approval before submission.",
        "",
        "## Gates",
        "",
    ]
    for gate in payload["gates"]:
        lines.extend([
            f"### {gate['title']}",
            "",
            f"Status: {gate['status']}",
            "",
            f"Approval required: {gate['approval_required']}",
            "",
            f"Next safe action: {gate['next_safe_action']}",
            "",
            f"Verification: {gate['verification']}",
            "",
            "Evidence:",
        ])
        for item in gate["evidence"]:
            lines.append(f"- {item['path']} ({'present' if item['exists'] else 'missing'})")
        lines.append("")
    lines.extend([
        "## Recommended Order",
        "",
    ])
    for item in payload["recommended_order"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Boundary",
        "",
        payload["non_action_boundary"],
        "",
    ])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    gate_sections = []
    for gate in payload["gates"]:
        evidence_rows = "\n".join(
            "<tr>"
            f"<td>{esc(item['path'])}</td>"
            f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
            "</tr>"
            for item in gate["evidence"]
        )
        gate_sections.append(f"""    <section>
      <h2>{esc(gate['title'])}</h2>
      <p>Status: <span class="{'ready' if gate['status'] in {'approved_url_recorded', 'ready_for_user_decision', 'ready_for_final_approval'} else 'pending'}">{esc(gate['status'])}</span></p>
      <table>
        <tbody>
          <tr><th>Approval required</th><td>{esc(gate['approval_required'])}</td></tr>
          <tr><th>Next safe action</th><td>{esc(gate['next_safe_action'])}</td></tr>
          <tr><th>Verification</th><td>{esc(gate['verification'])}</td></tr>
        </tbody>
      </table>
      <h3>Evidence</h3>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>""")
    order = "".join(f"<li>{esc(item)}</li>" for item in payload["recommended_order"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Submission Gate Ledger</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; width: 190px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Submission Gate Ledger</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Submission Boundary</h2>
      <p>Local ready: <span class="{'ready' if payload['local_ready'] else 'pending'}">{esc(payload['local_ready'])}</span></p>
      <p>Final submit ready: <span class="{'ready' if payload['final_submit_ready'] else 'pending'}">{esc(payload['final_submit_ready'])}</span></p>
      <p class="pending">{esc(payload['non_action_boundary'])}</p>
    </section>
{chr(10).join(gate_sections)}
    <section>
      <h2>Recommended Order</h2>
      <ol>{order}</ol>
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
    write_json(reports / "latest_submission_gate_ledger.json", payload)
    (reports / "latest_submission_gate_ledger.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_submission_gate_ledger.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "pending_gates": payload["pending_gates"],
        "html": "reports/latest_submission_gate_ledger.html",
        "markdown": "reports/latest_submission_gate_ledger.md",
        "json": "reports/latest_submission_gate_ledger.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a non-executing submission gate ledger.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
