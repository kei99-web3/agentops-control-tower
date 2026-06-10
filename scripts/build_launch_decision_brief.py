from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This brief is local decision support only. It does not publish, upload, submit, "
    "create accounts, configure credentials, write approved URLs, or update Devpost."
)


@dataclass
class Decision:
    key: str
    title: str
    status: str
    approval_phrase: str
    purpose: str
    evidence: list[str]
    after_approval: str
    main_risk: str
    verification: str


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
        "review_index": read_json(root / "reports/latest_submission_review_index.json"),
        "gate_ledger": read_json(root / "reports/latest_submission_gate_ledger.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "external_approval": read_json(root / "reports/latest_external_approval_packet.json"),
        "repo_publication_preflight": read_json(root / "reports/latest_public_repo_publication_preflight.json"),
        "video": read_json(root / "reports/latest_video_readiness.json"),
        "video_upload_preflight": read_json(root / "reports/latest_public_video_upload_preflight.json"),
        "zip_smoke": read_json(root / "reports/latest_release_zip_smoke_test.json"),
        "release_integrity": read_json(root / "reports/latest_release_integrity_manifest.json"),
        "official_source_freshness": read_json(root / "reports/latest_official_source_freshness.json"),
        "content_rights": read_json(root / "reports/latest_content_rights_audit.json"),
        "eligibility_compliance": read_json(root / "reports/latest_eligibility_compliance_audit.json"),
    }


def local_ready(root: Path, state: dict[str, Any]) -> bool:
    if is_public_candidate_root(root):
        return (
            state["review_index"].get("status") == "ready_for_user_review"
            and state["gate_ledger"].get("status") == "ready_for_user_review"
        )
    return (
        (
            state["validation"].get("overall_status") == "ready_for_user_review"
            and int(state["validation"].get("failed_count", 1)) == 0
        )
        or state["go_no_go"].get("local_ready") is True
    )


def pending_urls(state: dict[str, Any]) -> list[str]:
    return list(state["url_validation"].get("pending_urls", []))


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


def build_decisions(root: Path, state: dict[str, Any]) -> list[Decision]:
    ready = local_ready(root, state)
    pending = set(pending_urls(state))
    official_mcp_done = official_mcp_readback_verified(root)
    repo_ready = (
        ready
        and state["repo_publication_preflight"].get("status") == "ready_for_user_review"
        and ("repository_url" in pending)
    )
    video_ready = (
        ready
        and state["video"].get("status") == "ready_for_recording_review"
        and state["video_upload_preflight"].get("status") == "ready_for_user_review"
        and ("demo_video_url" in pending)
    )
    urls_ready = "repository_url" not in pending and "demo_video_url" not in pending
    return [
        Decision(
            key="public_github_repository",
            title="Public GitHub Repository",
            status="ready_for_user_decision" if repo_ready else "hold",
            approval_phrase="Approve public GitHub publication for the clean agentops-control-tower candidate.",
            purpose="Satisfy the public open-source repository requirement and give judges a runnable code package.",
            evidence=[
                "reports/latest_judge_quickstart.html",
                "reports/latest_publication_command_plan.html",
                "reports/latest_public_repo_publish_brief.html",
                "reports/latest_public_repo_publication_preflight.html",
                "reports/latest_public_repo_dry_run.html",
                "reports/latest_release_integrity_manifest.html",
                "reports/latest_release_zip_smoke_test.html" if not is_public_candidate_root(root) else "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
                "public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md" if not is_public_candidate_root(root) else "README.md",
            ],
            after_approval="Run the public repository publication preflight gate with the exact approval phrase, public git identity, and manual safety confirmations, then create and push the public repository through the guarded helper and record the public repository URL.",
            main_risk="Publishing the wrong folder or initializing Git inside the private workspace could expose private workspace material, local paths, or non-public artifacts.",
            verification="Review reports/latest_public_repo_publication_preflight.html, open the public repository URL, rerun the public candidate scans and isolated staging dry run, then validate the URL before writing it locally.",
        ),
        Decision(
            key="public_demo_video",
            title="Public Demo Video",
            status="ready_for_user_decision" if video_ready else "hold",
            approval_phrase="Approve recording and public upload of the Agentic Incident Command Center demo video.",
            purpose="Give judges a fast walkthrough of the dashboard, local SPL proof, approval queue, and MCP Remediation Ledger.",
            evidence=[
                "reports/latest_demo_tour.html",
                "reports/latest_video_readiness.html",
                "reports/latest_video_command_plan.html",
                "reports/latest_public_video_upload_preflight.html",
                "reports/latest_video_cue_sheet.html",
                "reports/latest_content_rights_audit.html",
                "submission/VIDEO_RECORDING_RUNBOOK.md",
            ],
            after_approval="Run the public video upload preflight gate with the exact approval phrase and manual safety confirmations, record, review, and upload the public demo video, then record the public video URL.",
            main_risk="A recording could expose private tabs, local paths, accounts, credentials, or overstate live Splunk MCP proof.",
            verification="Review reports/latest_public_video_upload_preflight.html, watch the uploaded public video end to end, confirm it is under 3 minutes and screen-safe, then validate the URL.",
        ),
        Decision(
            key="optional_live_splunk_mcp_proof",
            title="Optional Live Splunk / MCP Proof",
            status="completed" if official_mcp_done else "optional_user_decision" if ready else "hold",
            approval_phrase="Approve optional live Splunk and Splunk MCP proof using synthetic data only.",
            purpose=(
                "Completed: strengthen the Best Use of Splunk MCP Server bonus claim with a local official-MCP proof using synthetic data only."
                if official_mcp_done
                else "Strengthen the Best Use of Splunk MCP Server bonus claim if credentials, time, and scope are acceptable."
            ),
            evidence=[
                "reports/latest_splunk_mcp_command_plan.html",
                "reports/latest_splunk_mcp_proof_brief.html",
                "reports/latest_splunk_mcp_prompt_pack.html",
                "reports/latest_splunk_mcp_proof_capture_manifest.html",
                "reports/latest_splunk_app_package_manifest.html",
                "submission/SPLUNK_MCP_RUNBOOK.md",
                "submission/SPLUNK_MCP_PROMPT_PACK.md",
                "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md",
                "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md",
                "data/splunk_agentops_events.csv",
            ],
            after_approval=(
                "No further action required for the local official-MCP proof. Keep the claim bounded to local Splunk Enterprise Docker with synthetic data."
                if official_mcp_done
                else "Configure Splunk/MCP with approved scope, import only synthetic data, capture proof, and rerun claim validation."
            ),
            main_risk=(
                "Overclaiming production Splunk Cloud deployment or exposing credentials in video/screenshots."
                if official_mcp_done
                else "Requires account setup, credentials, possible cost, and careful scope control."
            ),
            verification=(
                "Read submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md and rerun claim validation."
                if official_mcp_done
                else "Use the prompt pack and proof capture manifest, confirm SPL queries and MCP-assisted answer cite synthetic event IDs, then update wording only after proof exists."
            ),
        ),
        Decision(
            key="approved_url_writeback",
            title="Approved URL Writeback",
            status="blocked_until_public_urls" if not urls_ready else "ready_for_user_decision",
            approval_phrase="Approve writing the verified public repository and demo video URLs into local submission artifacts.",
            purpose="Replace pending URL placeholders only after both public URLs are real and approved.",
            evidence=[
                "reports/latest_submission_url_validation.html",
                "reports/latest_submission_url_apply_plan.html",
                "reports/latest_devpost_final_copy.html",
            ],
            after_approval="Run prepare_submission_urls.py with both approved URLs and --write-approved, then rebuild final copy.",
            main_risk="Writing unverified or private URLs could make the Devpost packet look ready when it is not.",
            verification="Rerun URL validation and confirm final_submit_ready changes only when both public URLs pass.",
        ),
        Decision(
            key="devpost_final_submission",
            title="Devpost Final Submission",
            status="blocked_until_public_urls" if not urls_ready else "ready_for_user_decision",
            approval_phrase="Approve final Devpost submission for Agentic Incident Command Center.",
            purpose="Complete the hackathon submission after all required public artifacts and claim boundaries are verified.",
            evidence=[
                "reports/latest_devpost_submit_command_plan.html",
                "reports/latest_devpost_manual_fill_brief.html",
                "reports/latest_post_action_evidence_brief.html",
                "reports/latest_official_source_freshness.html",
                "reports/latest_content_rights_audit.html",
                "reports/latest_eligibility_compliance_audit.html",
                "reports/latest_release_integrity_manifest.html",
                "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md",
                "reports/latest_devpost_final_copy.html",
                "reports/latest_final_go_no_go.html",
                "submission/DEVPOST_FIELD_MAP.md",
            ],
            after_approval="Use the Devpost command plan, fill fields, perform human readback, then press submit only after final approval.",
            main_risk="Submitting with pending URLs, wrong track, missing architecture evidence, or unverified live Splunk claims.",
            verification="Read back the submitted Devpost page/status and save local post-submit evidence.",
        ),
    ]


def decision_to_dict(root: Path, decision: Decision) -> dict[str, Any]:
    return {
        "key": decision.key,
        "title": decision.title,
        "status": decision.status,
        "approval_phrase": decision.approval_phrase,
        "purpose": decision.purpose,
        "after_approval": decision.after_approval,
        "main_risk": decision.main_risk,
        "verification": decision.verification,
        "evidence": [{"path": item, "exists": exists(root, item)} for item in decision.evidence],
    }


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    decisions = [decision_to_dict(root, item) for item in build_decisions(root, state)]
    missing = [
        f"{decision['key']}:{item['path']}"
        for decision in decisions
        for item in decision["evidence"]
        if not item["exists"]
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not missing and local_ready(root, state) else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": local_ready(root, state),
        "final_submit_ready": bool(state["go_no_go"].get("final_submit_ready", False)),
        "pending_urls": pending_urls(state),
        "ready_now": [item["key"] for item in decisions if item["status"] == "ready_for_user_decision"],
        "recommended_approval_order": [item["key"] for item in decisions],
        "missing_evidence": missing,
        "decisions": decisions,
        "boundary": BOUNDARY,
        "recommended_next_step": "Review public GitHub and public demo video approvals first; hold Devpost final submission until both public URLs are verified.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Launch Decision Brief",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Pending URLs: {', '.join(payload['pending_urls']) if payload['pending_urls'] else 'none'}",
        "",
        "## Recommended Approval Order",
        "",
    ]
    for key in payload["recommended_approval_order"]:
        decision = next(item for item in payload["decisions"] if item["key"] == key)
        lines.append(f"- {decision['title']} ({decision['status']})")
    lines.extend(["", "## Decisions", ""])
    for decision in payload["decisions"]:
        lines.extend([
            f"### {decision['title']}",
            "",
            f"Status: {decision['status']}",
            f"Approval phrase: {decision['approval_phrase']}",
            "",
            f"Purpose: {decision['purpose']}",
            f"After approval: {decision['after_approval']}",
            f"Main risk: {decision['main_risk']}",
            f"Verification: {decision['verification']}",
            "",
            "Evidence:",
        ])
        for item in decision["evidence"]:
            lines.append(f"- `{item['path']}` ({'present' if item['exists'] else 'missing'})")
        lines.append("")
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    order_rows = "\n".join(
        "<tr>"
        f"<td>{esc(index)}</td>"
        f"<td>{esc(next(item['title'] for item in payload['decisions'] if item['key'] == key))}</td>"
        f"<td>{esc(key)}</td>"
        "</tr>"
        for index, key in enumerate(payload["recommended_approval_order"], start=1)
    )
    sections = []
    for decision in payload["decisions"]:
        evidence_rows = "\n".join(
            "<tr>"
            f"<td><code>{esc(item['path'])}</code></td>"
            f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
            "</tr>"
            for item in decision["evidence"]
        )
        sections.append(f"""    <section>
      <h2>{esc(decision['title'])}</h2>
      <p>Status: <span class="{'ready' if decision['status'] == 'ready_for_user_decision' else 'pending'}">{esc(decision['status'])}</span></p>
      <table>
        <tbody>
          <tr><th>Approval phrase</th><td>{esc(decision['approval_phrase'])}</td></tr>
          <tr><th>Purpose</th><td>{esc(decision['purpose'])}</td></tr>
          <tr><th>After approval</th><td>{esc(decision['after_approval'])}</td></tr>
          <tr><th>Main risk</th><td>{esc(decision['main_risk'])}</td></tr>
          <tr><th>Verification</th><td>{esc(decision['verification'])}</td></tr>
        </tbody>
      </table>
      <h3>Evidence</h3>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>""")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Launch Decision Brief</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
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
    <h1>Launch Decision Brief</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Recommended Next Step</h2>
      <p>{esc(payload['recommended_next_step'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Recommended Approval Order</h2>
      <table>
        <thead><tr><th>#</th><th>Decision</th><th>Key</th></tr></thead>
        <tbody>{order_rows}</tbody>
      </table>
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
    write_json(reports / "latest_launch_decision_brief.json", payload)
    (reports / "latest_launch_decision_brief.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_launch_decision_brief.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "ready_now": payload["ready_now"],
        "missing_evidence": payload["missing_evidence"],
        "html": "reports/latest_launch_decision_brief.html",
        "markdown": "reports/latest_launch_decision_brief.md",
        "json": "reports/latest_launch_decision_brief.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local launch decision brief for external approval gates.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
