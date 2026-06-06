from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def evidence(root: Path) -> list[dict[str, Any]]:
    items = [
        "reports/latest_devpost_submission_packet.html",
        "reports/latest_devpost_submission_packet.json",
        "reports/latest_devpost_final_copy.html",
        "reports/latest_devpost_final_copy.md",
        "reports/latest_devpost_final_copy.json",
        "reports/latest_devpost_final_submit_preflight.html",
        "reports/latest_devpost_final_submit_preflight.json",
        "reports/latest_submission_url_validation.html",
        "reports/latest_submission_url_validation.json",
        "reports/latest_submission_url_apply_plan.html",
        "reports/latest_final_go_no_go.html",
        "reports/latest_final_go_no_go.json",
        "reports/latest_external_approval_packet.html",
        "reports/latest_video_command_plan.html",
        "reports/latest_publication_command_plan.html",
        "submission/DEVPOST_FIELD_MAP.md",
        "submission/FINAL_SUBMISSION_CHECKLIST.md",
        "submission/OFFICIAL_REQUIREMENTS_AUDIT.md",
        "submission/SUBMISSION_LAUNCH_RUNBOOK.md",
    ]
    return [{"path": item, "exists": exists(root, item)} for item in items]


def command_steps() -> list[dict[str, str]]:
    return [
        {
            "name": "Refresh Devpost packet",
            "command": "python scripts\\build_devpost_submission_packet.py",
            "purpose": "Regenerate local Devpost field evidence before copying anything into Devpost.",
        },
        {
            "name": "Refresh final copy",
            "command": "python scripts\\export_devpost_final_copy.py",
            "purpose": "Regenerate copy/paste text and character checks.",
        },
        {
            "name": "Validate public URLs",
            "command": "python scripts\\validate_submission_urls.py",
            "purpose": "Confirm repository and video URLs are either still pending or valid approved public URLs.",
        },
        {
            "name": "Refresh Go/No-Go",
            "command": "python scripts\\build_final_go_no_go_report.py",
            "purpose": "Confirm whether the package is local-ready and whether final submit is still blocked by external gates.",
        },
        {
            "name": "Final local validation",
            "command": "python scripts\\validate_submission_packet.py",
            "purpose": "Re-run the full local submission validator before touching the Devpost form.",
        },
        {
            "name": "Open final review artifacts",
            "command": "start reports\\latest_devpost_final_copy.html && start reports\\latest_final_go_no_go.html && start reports\\latest_submission_url_validation.html",
            "purpose": "Review fields, URL state, claim boundaries, and final gate before any Devpost session.",
        },
        {
            "name": "Fill Devpost form after approval",
            "command": "manual: copy fields from reports\\latest_devpost_final_copy.md into Devpost; select Platform & Developer Experience; attach architecture_diagram.md; use only approved public repo/video URLs",
            "purpose": "Populate the form only after account/session use is approved.",
        },
        {
            "name": "Pre-submit human review",
            "command": "manual: compare Devpost screen against submission\\DEVPOST_FIELD_MAP.md and reports\\latest_devpost_final_copy.md",
            "purpose": "Hold submission if pending URLs, unsafe Splunk MCP claims, wrong track, or missing architecture evidence remain.",
        },
        {
            "name": "Final submit preflight gate",
            "command": "python scripts\\verify_devpost_final_submit_gate.py --final-approval-phrase \"Approve final Devpost submission for Agentic Incident Command Center.\" --field-map-readback-confirmed --human-confirmations-completed --video-screen-safety-confirmed --post-action-evidence-plan-reviewed",
            "purpose": "Require final_submit_ready, exact final approval phrase, and manual readback confirmations before the submit button is pressed.",
        },
        {
            "name": "Submit after explicit final approval",
            "command": "manual: press the Devpost submit button only after explicit final user approval",
            "purpose": "Complete the external submission only when the final approval gate is satisfied.",
        },
        {
            "name": "Post-submit readback",
            "command": "manual: capture the Devpost submitted URL/status and save local evidence after submission",
            "purpose": "Create a local audit trail after the external submit action has actually completed.",
        },
    ]


def pending_urls(fields: dict[str, Any]) -> list[str]:
    return [
        key
        for key in ["repository_url", "demo_video_url"]
        if str(fields.get(key, "")).startswith("PENDING_USER_APPROVAL_")
    ]


def build_payload(root: Path) -> dict[str, Any]:
    final_copy = read_json(root / "reports/latest_devpost_final_copy.json")
    go_no_go = read_json(root / "reports/latest_final_go_no_go.json")
    url_validation = read_json(root / "reports/latest_submission_url_validation.json")
    approval = read_json(root / "reports/latest_external_approval_packet.json")
    rows = evidence(root)
    missing = [item["path"] for item in rows if not item["exists"]]
    fields = final_copy.get("fields", {})
    pending = pending_urls(fields)
    urls_final_ready = url_validation.get("final_submit_ready") is True and not pending
    final_submit_ready = bool(
        final_copy.get("final_submit_ready") is True
        and go_no_go.get("final_submit_ready") is True
        and urls_final_ready
        and not pending
    )
    ready_requests = set(approval.get("ready_requests", []))
    local_ready = (
        not missing
        and final_copy.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready", False) is True
        and (
            {"public_github_repository", "public_demo_video"}.issubset(ready_requests)
            or urls_final_ready
            or pending
        )
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": local_ready,
        "final_submit_ready": final_submit_ready,
        "pending_urls": pending,
        "submission_url_validation_status": url_validation.get("status", "missing"),
        "go_no_go_status": go_no_go.get("status", "missing"),
        "missing_evidence": missing,
        "evidence": rows,
        "commands": command_steps(),
        "boundary": "This command plan is advisory only. It does not log in, save a draft, press submit, update Devpost, publish, upload, write URLs, or submit anything.",
        "approval_required": "Explicit user approval is required before using a Devpost account/session, saving a Devpost draft, or pressing the final submit button.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Devpost Final Submission Command Plan",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Pending URLs: {', '.join(payload['pending_urls']) if payload['pending_urls'] else 'none'}",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        payload["approval_required"],
        "",
        "## Evidence",
        "",
    ]
    for item in payload["evidence"]:
        lines.append(f"- {item['path']} ({'present' if item['exists'] else 'missing'})")
    lines.extend(["", "## Commands After Approval", ""])
    for item in payload["commands"]:
        lines.extend([
            f"### {item['name']}",
            "",
            item["purpose"],
            "",
            "```powershell",
            item["command"],
            "```",
            "",
        ])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    evidence_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['path'])}</td>"
        f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        "</tr>"
        for item in payload["evidence"]
    )
    command_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['name'])}</td>"
        f"<td>{esc(item['purpose'])}</td>"
        f"<td><code>{esc(item['command'])}</code></td>"
        "</tr>"
        for item in payload["commands"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Devpost Final Submission Command Plan</title>
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
    <h1>Devpost Final Submission Command Plan</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Boundary</h2>
      <p class="pending">{esc(payload['boundary'])}</p>
      <p>{esc(payload['approval_required'])}</p>
      <p>Final submit ready: <span class="{'ready' if payload['final_submit_ready'] else 'pending'}">{esc(payload['final_submit_ready'])}</span></p>
      <p>Pending URLs: {esc(', '.join(payload['pending_urls']) if payload['pending_urls'] else 'none')}</p>
    </section>
    <section>
      <h2>Evidence</h2>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Commands After Approval</h2>
      <table>
        <thead><tr><th>Step</th><th>Purpose</th><th>Command</th></tr></thead>
        <tbody>{command_rows}</tbody>
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
    write_json(reports / "latest_devpost_submit_command_plan.json", payload)
    (reports / "latest_devpost_submit_command_plan.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_devpost_submit_command_plan.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "final_submit_ready": payload["final_submit_ready"],
        "html": "reports/latest_devpost_submit_command_plan.html",
        "markdown": "reports/latest_devpost_submit_command_plan.md",
        "json": "reports/latest_devpost_submit_command_plan.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a non-executing Devpost final submission command plan.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
