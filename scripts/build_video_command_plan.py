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
        "reports/latest_demo_tour.html",
        "reports/latest_video_readiness.html",
        "reports/latest_video_readiness.json",
        "reports/latest_video_recording_preview.html",
        "reports/latest_video_recording_preview.json",
        "reports/latest_video_upload_metadata.html",
        "reports/latest_video_upload_metadata.json",
        "reports/latest_public_video_upload_preflight.html",
        "reports/latest_public_video_upload_preflight.json",
        "submission/VIDEO_UPLOAD_METADATA.md",
        "submission/DEMO_VIDEO_SCRIPT.md",
        "submission/VIDEO_RECORDING_RUNBOOK.md",
        "reports/latest_external_approval_packet.html",
        "reports/latest_submission_url_apply_plan.html",
        "reports/latest_public_artifact_url_readback.html",
        "reports/latest_public_artifact_url_readback.json",
        "reports/latest_devpost_final_copy.md",
    ]
    if not is_public_candidate_root(root):
        items.extend([
            "reports/latest_submission_validation.html",
            "reports/latest_release_zip_smoke_test.html",
        ])
    return [{"path": item, "exists": exists(root, item)} for item in items]


def command_steps() -> list[dict[str, str]]:
    return [
        {
            "name": "Refresh safe demo tour",
            "command": "python scripts\\build_demo_tour.py",
            "purpose": "Regenerate the browser walkthrough used for the recording path.",
        },
        {
            "name": "Refresh video readiness",
            "command": "python scripts\\build_video_readiness_report.py",
            "purpose": "Confirm timing, screen safety, claim wording, and upload approval gate.",
        },
        {
            "name": "Build screen-safe localhost recording preview",
            "command": "python scripts\\build_video_recording_preview.py",
            "purpose": "Copy the public candidate to an isolated temporary preview stage, scan recording files, and produce a localhost preview command template.",
        },
        {
            "name": "Review video upload metadata",
            "command": "python scripts\\build_video_upload_metadata.py",
            "purpose": "Confirm the upload title, description, tags, visibility, expected readback, and public video stop conditions before any upload.",
        },
        {
            "name": "Public video upload preflight gate",
            "command": "python scripts\\verify_public_video_upload_gate.py --approval-phrase \"Approve recording and public upload of the Agentic Incident Command Center demo video.\" --screen-safety-confirmed --duration-confirmed --claim-boundary-confirmed --content-rights-confirmed --upload-visibility-confirmed",
            "purpose": "Require the exact public demo video approval phrase plus screen, duration, claim, rights, and visibility confirmations before manual capture or upload.",
        },
        {
            "name": "Open recording review artifacts",
            "command": "start reports\\latest_demo_tour.html && start reports\\latest_video_readiness.html && start reports\\latest_video_recording_preview.html && start reports\\latest_video_upload_metadata.html && start reports\\latest_public_video_upload_preflight.html",
            "purpose": "Review the demo path, readiness report, localhost preview preflight, upload metadata, and public video upload gate before any capture.",
        },
        {
            "name": "Capture local recording after approval",
            "command": "manual: record reports\\latest_demo_tour.html using submission\\VIDEO_RECORDING_RUNBOOK.md",
            "purpose": "Record only the approved browser path with synthetic data and no private screens.",
        },
        {
            "name": "Review recording before upload",
            "command": "manual: watch the recording and check duration, screen safety, and claim wording",
            "purpose": "Hold upload if private paths, credentials, account pages, or live Splunk/MCP overclaims appear.",
        },
        {
            "name": "Upload public video after approval",
            "command": "manual: upload the reviewed video to an approved public video host and capture the URL",
            "purpose": "Create the public Devpost video URL only after explicit approval.",
        },
        {
            "name": "Verify public artifact URLs before writeback",
            "command": "python scripts\\verify_public_artifact_urls.py --repository-url <public-repo-url> --demo-video-url <public-video-url> --live-readback",
            "purpose": "Confirm the public GitHub repository and public demo video URL are reachable before writing them into local submission artifacts.",
        },
        {
            "name": "Apply approved URLs locally",
            "command": "python scripts\\prepare_submission_urls.py --repository-url <public-repo-url> --demo-video-url <public-video-url> --write-approved --approval-note \"user approved public URLs\"",
            "purpose": "Update the local Devpost URL source only after both public URLs are approved.",
        },
        {
            "name": "Final local validation",
            "command": "python scripts\\validate_submission_packet.py",
            "purpose": "Confirm the submission packet is ready for final Devpost review.",
        },
    ]


def build_payload(root: Path) -> dict[str, Any]:
    video = read_json(root / "reports/latest_video_readiness.json")
    approval = read_json(root / "reports/latest_external_approval_packet.json")
    url_plan = read_json(root / "reports/latest_submission_url_apply_plan.json")
    rows = evidence(root)
    missing = [item["path"] for item in rows if not item["exists"]]
    ready_requests = set(approval.get("ready_requests", []))
    video_approval_ready = "public_demo_video" in ready_requests
    readiness_ok = video.get("status") == "ready_for_recording_review"
    url_gate_ok = url_plan.get("status") in {"waiting_for_external_urls", "ready_to_submit_after_user_approval"}
    local_ready = not missing and readiness_ok and video_approval_ready and url_gate_ok
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": local_ready,
        "video_readiness_status": video.get("status", "missing"),
        "public_video_approval_ready": video_approval_ready,
        "submission_url_apply_plan_status": url_plan.get("status", "missing"),
        "missing_evidence": missing,
        "evidence": rows,
        "commands": command_steps(),
        "boundary": "This command plan is advisory only. It does not record, upload, publish, write URLs, update Devpost, or submit anything.",
        "approval_required": "Explicit user approval is required before recording capture, public video upload, or writing approved public URLs.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Demo Video Recording And Upload Command Plan",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
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
  <title>Demo Video Recording And Upload Command Plan</title>
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
    <h1>Demo Video Recording And Upload Command Plan</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Boundary</h2>
      <p class="pending">{esc(payload['boundary'])}</p>
      <p>{esc(payload['approval_required'])}</p>
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
    write_json(reports / "latest_video_command_plan.json", payload)
    (reports / "latest_video_command_plan.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_video_command_plan.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "html": "reports/latest_video_command_plan.html",
        "markdown": "reports/latest_video_command_plan.md",
        "json": "reports/latest_video_command_plan.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a non-executing recording and upload command plan for the demo video gate.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
