from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This brief is local post-action evidence guidance only. It does not publish a repository, "
    "record or upload video, connect to Splunk, configure MCP, write approved URLs, update Devpost, "
    "save a draft, press submit, or mark the submission complete."
)


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def local_evidence_items(root: Path) -> list[str]:
    if is_public_candidate_root(root):
        return [
            "reports/latest_submission_gate_ledger.html",
            "reports/latest_external_approval_packet.html",
            "reports/latest_public_repo_publish_brief.html",
            "reports/latest_video_command_plan.html",
            "reports/latest_public_video_upload_preflight.html",
            "reports/latest_splunk_mcp_proof_brief.html",
            "reports/latest_splunk_mcp_prompt_pack.html",
            "reports/latest_splunk_mcp_proof_capture_manifest.html",
            "reports/latest_submission_url_apply_plan.html",
            "reports/latest_devpost_submit_command_plan.html",
            "reports/latest_devpost_final_submit_preflight.html",
            "reports/latest_devpost_manual_fill_brief.html",
            "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md",
            "reports/latest_claim_boundary_validation.html",
            "reports/latest_judge_quickstart.html",
        ]
    return [
        "reports/latest_submission_validation.html",
        "reports/latest_submission_gate_ledger.html",
        "reports/latest_launch_decision_brief.html",
        "reports/latest_external_approval_packet.html",
        "reports/latest_public_repo_publish_brief.html",
        "reports/latest_release_zip_smoke_test.html",
        "reports/latest_video_command_plan.html",
        "reports/latest_public_video_upload_preflight.html",
        "reports/latest_splunk_mcp_proof_brief.html",
        "reports/latest_splunk_mcp_prompt_pack.html",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "reports/latest_submission_url_apply_plan.html",
        "reports/latest_devpost_submit_command_plan.html",
        "reports/latest_devpost_final_submit_preflight.html",
        "reports/latest_devpost_manual_fill_brief.html",
        "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md",
        "reports/latest_claim_boundary_validation.html",
        "reports/latest_judge_quickstart.html",
    ]


def evidence_log_policy() -> dict[str, Any]:
    return {
        "recommended_directory": "submission/post_action_evidence/",
        "filename_pattern": "YYYY-MM-DD_<action_key>_readback.md",
        "write_policy": (
            "Create a dated local evidence note only after explicit user approval, "
            "external action completion, and completion readback."
        ),
        "public_candidate_policy": (
            "Keep completed evidence notes private/local by default. Include them in a public candidate only after "
            "a separate review confirms they contain no credentials, tokens, account screenshots, billing or OAuth "
            "screens, local absolute paths, private workspace material, private logs, or customer data."
        ),
        "required_fields": [
            "approval evidence",
            "completion readback",
            "verification command or check",
            "evidence file or URL",
            "claim wording impact",
            "status",
        ],
        "forbidden_content": [
            "credentials",
            "tokens",
            "account screenshots",
            "billing pages",
            "OAuth screens",
            "local absolute paths",
            "private workspace material",
            "private logs",
            "customer data",
        ],
    }


def load_state(root: Path) -> dict[str, Any]:
    approved_urls_path = root / "submission" / "approved_public_urls.json"
    return {
        "validation": read_json(root / "reports/latest_submission_validation.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
        "url_apply": read_json(root / "reports/latest_submission_url_apply_plan.json"),
        "final_copy": read_json(root / "reports/latest_devpost_final_copy.json"),
        "submit_plan": read_json(root / "reports/latest_devpost_submit_command_plan.json"),
        "mcp_plan": read_json(root / "reports/latest_splunk_mcp_command_plan.json"),
        "mcp_proof": read_json(root / "reports/latest_splunk_mcp_proof_brief.json"),
        "mcp_capture": read_json(root / "reports/latest_splunk_mcp_proof_capture_manifest.json"),
        "claim": read_json(root / "reports/latest_claim_boundary_validation.json"),
        "video": read_json(root / "reports/latest_video_readiness.json"),
        "approved_urls": read_json(approved_urls_path),
        "approved_urls_exists": approved_urls_path.exists(),
    }


def approved_url(state: dict[str, Any], key: str) -> str:
    value = state["approved_urls"].get(key, "")
    return value if isinstance(value, str) else ""


def action_statuses(state: dict[str, Any]) -> dict[str, str]:
    repo_url = approved_url(state, "repository_url")
    video_url = approved_url(state, "demo_video_url")
    urls_ready = state["url_validation"].get("final_submit_ready") is True
    final_ready = state["go_no_go"].get("final_submit_ready") is True and state["submit_plan"].get("final_submit_ready") is True
    return {
        "public_github_repository": "approved_url_recorded" if repo_url else "waiting_for_user_approval",
        "public_demo_video": "approved_url_recorded" if video_url else "waiting_for_user_approval",
        "approved_url_writeback": "ready" if urls_ready else "blocked_until_public_urls",
        "optional_live_splunk_mcp_proof": (
            "live_splunk_mcp_verified"
            if state["mcp_proof"].get("live_splunk_mcp_verified") is True
            and state["mcp_capture"].get("live_splunk_mcp_verified") is True
            else "optional_waiting_for_user_approval"
        ),
        "devpost_final_submission": "ready_for_final_approval" if final_ready else "blocked_until_public_urls",
    }


def evidence_note_target(action_key: str) -> str:
    return f"submission/post_action_evidence/YYYY-MM-DD_{action_key}_readback.md"


def post_action_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    statuses = action_statuses(state)
    return [
        {
            "key": "public_github_repository",
            "title": "Public GitHub Repository",
            "status": statuses["public_github_repository"],
            "evidence_note_target": evidence_note_target("public_github_repository"),
            "safe_readback_source": "Use the public_safe_readback block from scripts/publish_public_repo_after_approval.py JSON output.",
            "completion_evidence": [
                "Public repository URL opens without authentication.",
                "Repository visibility readback is PUBLIC.",
                "README, LICENSE, architecture diagram, source, reports, and Splunk app candidate are present.",
                "Public candidate internal path and secret-like scans pass after publication.",
                "Repository URL is recorded only after the user approves URL writeback.",
            ],
            "readback_command": "gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url",
            "stop_condition": "Stop if the URL points to a private workspace repository or the wrong folder was published.",
        },
        {
            "key": "public_demo_video",
            "title": "Public Demo Video",
            "status": statuses["public_demo_video"],
            "evidence_note_target": evidence_note_target("public_demo_video"),
            "safe_readback_source": "Use the public_video_upload_safe_readback block from reports/latest_public_video_upload_preflight.json, the public_video_safe_readback block from reports/latest_video_recording_preview.json, plus a short manual final-recording review summary.",
            "completion_evidence": [
                "Public video upload preflight gate allowed manual recording/upload only after the exact approval phrase and manual safety confirmations.",
                "Uploaded video URL opens publicly or with the approved visibility.",
                "Duration is under 3 minutes.",
                "Recording shows only the prepared demo surfaces and no private tabs, local paths, credentials, or billing/account pages.",
                "Narration does not claim live Splunk/MCP proof unless that proof is separately verified.",
                "Demo video URL is recorded only after the user approves URL writeback.",
            ],
            "readback_command": "manual: open the video URL, watch end to end, and save the verified URL in the approved URL packet only after approval",
            "stop_condition": "Stop if the recording exposes private screens or overstates live Splunk/MCP verification.",
        },
        {
            "key": "optional_live_splunk_mcp_proof",
            "title": "Optional Live Splunk / MCP Proof",
            "status": statuses["optional_live_splunk_mcp_proof"],
            "evidence_note_target": evidence_note_target("optional_live_splunk_mcp_proof"),
            "safe_readback_source": "Use the proof capture summary from submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md with synthetic event IDs only.",
            "completion_evidence": [
                "Splunk account/license and MCP setup were explicitly approved before use.",
                "Only synthetic AgentOps data was imported.",
                "SPL queries return concrete synthetic event IDs.",
                "MCP-assisted answer cites the same synthetic event evidence.",
                "Proof capture manifest slots are completed and read back before any claim wording upgrade.",
                "Claim-boundary validation passes after any wording upgrade.",
            ],
            "readback_command": "manual: follow submission/SPLUNK_MCP_RUNBOOK.md and reports/latest_splunk_mcp_proof_capture_manifest.html before changing wording",
            "stop_condition": "Stop if credentials, costs, private data, or unapproved live Splunk/MCP scope would be exposed.",
        },
        {
            "key": "approved_url_writeback",
            "title": "Approved URL Writeback",
            "status": statuses["approved_url_writeback"],
            "evidence_note_target": evidence_note_target("approved_url_writeback"),
            "safe_readback_source": "Use the public_safe_readback block from reports/latest_public_artifact_url_readback.json after live URL readback passes.",
            "completion_evidence": [
                "submission/approved_public_urls.json exists only after explicit approval.",
                "repository_url and demo_video_url are both approved public URLs.",
                "reports/latest_submission_url_validation.json returns final_submit_ready true.",
                "reports/latest_devpost_final_copy.json no longer contains pending URL placeholders.",
                "Final Go/No-Go moves to final_submit_ready true only after both URLs validate.",
            ],
            "readback_command": "python scripts\\verify_public_artifact_urls.py --repository-url <public_repo_url> --demo-video-url <public_video_url> --live-readback && python scripts\\prepare_submission_urls.py --repository-url <public_repo_url> --demo-video-url <public_video_url> --write-approved --approval-note \"user approved public URLs\" && python scripts\\validate_submission_packet.py",
            "stop_condition": "Stop if either URL is missing, private, unapproved, or still a PENDING_USER_APPROVAL placeholder.",
        },
        {
            "key": "devpost_final_submission",
            "title": "Devpost Final Submission",
            "status": statuses["devpost_final_submission"],
            "evidence_note_target": evidence_note_target("devpost_final_submission"),
            "safe_readback_source": "Use the devpost_final_submit_safe_readback block from reports/latest_devpost_final_submit_preflight.json before submit; after submit, add a short manual Devpost submitted page/status summary only.",
            "completion_evidence": [
                "Final submit approval is explicit in the current thread.",
                "Final submit preflight gate allows manual submit only after final_submit_ready, exact approval phrase, and manual readback confirmations.",
                "Devpost fields match reports/latest_devpost_final_copy.md and submission/DEVPOST_FIELD_MAP.md.",
                "Selected track and bonus target match the launch decision brief.",
                "Submitted Devpost page/status is read back after pressing submit.",
                "A local post-submit evidence note captures the submitted URL/status without secrets or account screenshots.",
                "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md is copied or filled as the local post-action evidence note.",
            ],
            "readback_command": "manual: after explicit approval, submit Devpost, read back the submitted page/status, and store local evidence",
            "stop_condition": "Stop if final_submit_ready is false, public URLs are pending, or claim wording has not passed validation.",
        },
    ]


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    evidence = [{"path": item, "exists": exists(root, item)} for item in local_evidence_items(root)]
    missing = [item["path"] for item in evidence if not item["exists"]]
    actions = post_action_rows(state)
    incomplete = [item["key"] for item in actions if item["status"] not in {"approved_url_recorded", "ready", "live_splunk_mcp_verified", "ready_for_final_approval"}]
    local_ready = (
        not missing
        and (
            is_public_candidate_root(root)
            or state["validation"].get("overall_status") == "ready_for_user_review"
            or state["go_no_go"].get("local_ready") is True
        )
        and state["claim"].get("status") == "pass"
        and state["submit_plan"].get("status") == "ready_for_user_review"
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": local_ready,
        "final_submit_ready": bool(state["go_no_go"].get("final_submit_ready", False)),
        "post_action_evidence_ready": not incomplete,
        "approved_public_urls_exists": state["approved_urls_exists"],
        "missing_evidence": missing,
        "incomplete_actions": incomplete,
        "actions": actions,
        "evidence_log_policy": evidence_log_policy(),
        "final_readback_sequence": [
            "Read the public GitHub repository URL and visibility.",
            "Watch the public demo video and confirm screen safety.",
            "Optionally read back live Splunk/MCP proof against reports/latest_splunk_mcp_proof_capture_manifest.html only after approved setup.",
            "Validate approved URL writeback and final copy placeholders.",
            "Fill the post-action evidence log template with approved URLs, status, and validation readback.",
            "Read back the submitted Devpost page/status after explicit final approval.",
        ],
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    policy = payload["evidence_log_policy"]
    lines = [
        "# Post-Action Evidence Brief",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Post-action evidence ready: {str(payload['post_action_evidence_ready']).lower()}",
        f"Approved public URLs file exists: {str(payload['approved_public_urls_exists']).lower()}",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        "",
        "## Actions",
        "",
    ]
    for action in payload["actions"]:
        lines.extend([
            f"### {action['title']}",
            "",
            f"Status: {action['status']}",
            f"Evidence note target: `{action['evidence_note_target']}`",
            f"Safe readback source: {action['safe_readback_source']}",
            "",
            f"Readback command: `{action['readback_command']}`",
            "",
            "Completion evidence:",
        ])
        lines.extend(f"- {item}" for item in action["completion_evidence"])
        lines.extend(["", f"Stop condition: {action['stop_condition']}", ""])
    lines.extend(["## Final Readback Sequence", ""])
    lines.extend(f"- {item}" for item in payload["final_readback_sequence"])
    lines.extend([
        "",
        "## Evidence Log Policy",
        "",
        f"- Recommended directory: `{policy['recommended_directory']}`",
        f"- Filename pattern: `{policy['filename_pattern']}`",
        f"- Write policy: {policy['write_policy']}",
        f"- Public candidate policy: {policy['public_candidate_policy']}",
        "- Required fields: " + ", ".join(policy["required_fields"]),
        "- Forbidden content: " + ", ".join(policy["forbidden_content"]),
        "",
        "## Local Evidence",
        "",
    ])
    if payload["missing_evidence"]:
        lines.extend(f"- Missing: `{item}`" for item in payload["missing_evidence"])
    else:
        lines.append("- All required local evidence for this brief is present.")
    lines.append("")
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    policy = payload["evidence_log_policy"]
    action_rows = "\n".join(
        "<tr>"
        f"<td>{esc(action['title'])}</td>"
        f"<td>{esc(action['status'])}</td>"
        f"<td><code>{esc(action['evidence_note_target'])}</code><br>{esc(action['safe_readback_source'])}</td>"
        f"<td><code>{esc(action['readback_command'])}</code></td>"
        f"<td><ul>{''.join(f'<li>{esc(item)}</li>' for item in action['completion_evidence'])}</ul></td>"
        f"<td>{esc(action['stop_condition'])}</td>"
        "</tr>"
        for action in payload["actions"]
    )
    sequence = "\n".join(f"<li>{esc(item)}</li>" for item in payload["final_readback_sequence"])
    required_fields = "\n".join(f"<li>{esc(item)}</li>" for item in policy["required_fields"])
    forbidden_content = "\n".join(f"<li>{esc(item)}</li>" for item in policy["forbidden_content"])
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item)}</code></td>"
        f"<td class=\"fail\">missing</td>"
        "</tr>"
        for item in payload["missing_evidence"]
    ) or "<tr><td>All required local evidence</td><td class=\"ready\">present</td></tr>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Post-Action Evidence Brief</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1160px; margin: 0 auto; padding: 24px; }}
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
    <h1>Post-Action Evidence Brief</h1>
    <p>Readback evidence required after approved external actions. This page does not perform those actions.</p>
  </header>
  <main>
    <section>
      <h2>Status</h2>
      <table>
        <tbody>
          <tr><th>Local status</th><td class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</td></tr>
          <tr><th>Final submit ready</th><td class="{'ready' if payload['final_submit_ready'] else 'pending'}">{esc(payload['final_submit_ready'])}</td></tr>
          <tr><th>Post-action evidence ready</th><td class="{'ready' if payload['post_action_evidence_ready'] else 'pending'}">{esc(payload['post_action_evidence_ready'])}</td></tr>
          <tr><th>Approved public URLs file exists</th><td class="{'ready' if payload['approved_public_urls_exists'] else 'pending'}">{esc(payload['approved_public_urls_exists'])}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Boundary</h2>
      <p>{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Post-Action Evidence</h2>
      <table>
        <thead><tr><th>Action</th><th>Status</th><th>Evidence Note</th><th>Readback</th><th>Completion Evidence</th><th>Stop Condition</th></tr></thead>
        <tbody>{action_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Final Readback Sequence</h2>
      <ol>{sequence}</ol>
    </section>
    <section>
      <h2>Evidence Log Policy</h2>
      <table>
        <tbody>
          <tr><th>Recommended directory</th><td><code>{esc(policy['recommended_directory'])}</code></td></tr>
          <tr><th>Filename pattern</th><td><code>{esc(policy['filename_pattern'])}</code></td></tr>
          <tr><th>Write policy</th><td>{esc(policy['write_policy'])}</td></tr>
          <tr><th>Public candidate policy</th><td>{esc(policy['public_candidate_policy'])}</td></tr>
          <tr><th>Required fields</th><td><ul>{required_fields}</ul></td></tr>
          <tr><th>Forbidden content</th><td><ul>{forbidden_content}</ul></td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Local Evidence</h2>
      <table><tbody>{evidence_rows}</tbody></table>
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
    write_json(root / "reports/latest_post_action_evidence_brief.json", payload)
    (root / "reports/latest_post_action_evidence_brief.md").write_text(render_markdown(payload), encoding="utf-8")
    (root / "reports/latest_post_action_evidence_brief.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "post_action_evidence_ready": payload["post_action_evidence_ready"],
        "incomplete_actions": payload["incomplete_actions"],
        "html": "reports/latest_post_action_evidence_brief.html",
        "markdown": "reports/latest_post_action_evidence_brief.md",
        "json": "reports/latest_post_action_evidence_brief.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the post-action evidence brief.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
