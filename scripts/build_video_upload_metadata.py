from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TITLE = "Agentic Incident Command Center: Splunk-grounded AI incident response"
VISIBILITY_AFTER_APPROVAL = "public"
PLATFORM = "approved public video host"
TAGS = [
    "Splunk",
    "AgentOps",
    "AI agents",
    "MCP",
    "observability",
    "incident response",
    "human approval",
    "hackathon",
]
DESCRIPTION = """Agentic Incident Command Center is a Splunk-grounded AI incident commander for modern operations teams.

This demo uses synthetic checkout-incident events to show how deploy, APM, database, network, security, and MCP-adjacent signals can be correlated into one incident timeline.

The MCP Remediation Ledger keeps evidence references attached to each proposed action so operators can see the ranked root cause, blast radius, blocked credential-boundary attempt, and the remediation steps that still require human approval. The project includes an official Splunk MCP Server proof in a reproducible local Splunk Enterprise Docker environment using synthetic data only; it does not claim production Splunk Cloud deployment.

Repository and Devpost links should be added only after public URL readback has passed."""
BOUNDARY = (
    "This video upload metadata packet is local review evidence only. It does not record video, "
    "upload video, publish media, write approved URLs, update Devpost, connect to Splunk, configure MCP, "
    "or submit anything."
)


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def evidence(root: Path) -> list[dict[str, Any]]:
    paths = [
        "reports/latest_video_readiness.html",
        "reports/latest_video_readiness.json",
        "reports/latest_video_command_plan.html",
        "reports/latest_video_cue_sheet.html",
        "reports/latest_video_recording_preview.html",
        "reports/latest_content_rights_audit.html",
        "reports/latest_public_artifact_url_readback.html",
        "reports/latest_post_action_evidence_brief.html",
        "submission/DEMO_VIDEO_SCRIPT.md",
        "submission/VIDEO_RECORDING_RUNBOOK.md",
        "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
    ]
    if not is_public_candidate_root(root):
        paths.extend([
            "reports/latest_submission_validation.html",
            "reports/latest_release_zip_smoke_test.html",
        ])
    return [{"path": path, "exists": exists(root, path)} for path in paths]


def upload_steps() -> list[dict[str, str]]:
    return [
        {
            "name": "review_recording_path",
            "action": "Open reports/latest_demo_tour.html, reports/latest_video_cue_sheet.html, and reports/latest_video_recording_preview.html.",
            "purpose": "Confirm the capture path is synthetic-data-only and screen safe before recording.",
        },
        {
            "name": "record_after_approval",
            "action": "Record the approved browser path using submission/VIDEO_RECORDING_RUNBOOK.md.",
            "purpose": "Capture the demo only after explicit recording approval.",
        },
        {
            "name": "screen_safety_review",
            "action": "Watch the final recording end to end and check submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md.",
            "purpose": "Block upload if private screens, account pages, local paths, credentials, or overclaims appear.",
        },
        {
            "name": "upload_after_approval",
            "action": "Upload to an approved public video host using the title, description, tags, and visibility in this packet.",
            "purpose": "Create the public demo video URL only after explicit public upload approval.",
        },
        {
            "name": "public_url_readback",
            "action": "Run python scripts\\verify_public_artifact_urls.py --repository-url <public-repo-url> --demo-video-url <public-video-url> --live-readback.",
            "purpose": "Confirm the public repo and demo video are both reachable before approved URL writeback.",
        },
    ]


def build_payload(root: Path) -> dict[str, Any]:
    readiness = read_json(root / "reports/latest_video_readiness.json")
    cue = read_json(root / "reports/latest_video_cue_sheet.json")
    url_readback = read_json(root / "reports/latest_public_artifact_url_readback.json")
    rows = evidence(root)
    missing = [item["path"] for item in rows if not item["exists"]]
    duration_seconds = int(cue.get("duration_seconds") or readiness.get("duration_seconds") or 999)
    readiness_ok = readiness.get("status") == "ready_for_recording_review"
    cue_ok = cue.get("status") == "ready_for_recording_review"
    local_ready = not missing and readiness_ok and cue_ok and duration_seconds <= 180
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "title": TITLE,
        "platform": PLATFORM,
        "visibility_after_approval": VISIBILITY_AFTER_APPROVAL,
        "duration_limit_seconds": 180,
        "observed_duration_seconds": duration_seconds,
        "tags": TAGS,
        "description": DESCRIPTION,
        "safe_claim_boundary": "Say official Splunk MCP Server verified only for the local Splunk Enterprise Docker proof with synthetic data; do not claim production Splunk Cloud deployment.",
        "public_video_url": "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL",
        "approved_public_urls_exists": bool(readiness.get("approved_public_urls_exists", False) or url_readback.get("approved_public_urls_exists", False)),
        "final_public_video_ready": False,
        "upload_steps_after_approval": upload_steps(),
        "expected_readback": {
            "video_url": "openable public video URL",
            "visibility": VISIBILITY_AFTER_APPROVAL,
            "title": TITLE,
            "duration_seconds_max": 180,
            "screen_safety_checklist": "completed before upload approval",
            "description_contains": ["synthetic checkout-incident events", "MCP Remediation Ledger", "official Splunk MCP Server proof", "human approval"],
        },
        "evidence": rows,
        "missing_evidence": missing,
        "stop_conditions": [
            "Do not record until the recording path and script are reviewed.",
            "Do not upload if the recording shows private paths, credentials, account pages, private logs, or unrelated workspace content.",
            "Do not claim production Splunk Cloud deployment; the verified MCP proof is local Splunk Enterprise Docker with synthetic data.",
            "Do not write approved URLs until the public repo and demo video URLs both pass readback.",
            "Do not update Devpost or press submit from this step.",
        ],
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Video Upload Metadata",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Title: {payload['title']}",
        f"Platform: {payload['platform']}",
        f"Visibility after approval: {payload['visibility_after_approval']}",
        f"Duration limit: {payload['duration_limit_seconds']} seconds",
        f"Observed local plan duration: {payload['observed_duration_seconds']} seconds",
        f"Public video URL: {payload['public_video_url']}",
        f"Final public video ready: {str(payload['final_public_video_ready']).lower()}",
        "",
        "## Description",
        "",
        payload["description"],
        "",
        "## Tags",
        "",
    ]
    for tag in payload["tags"]:
        lines.append(f"- `{tag}`")
    lines.extend(["", "## Safe Claim Boundary", "", payload["safe_claim_boundary"], "", "## Upload Steps After Approval", ""])
    for item in payload["upload_steps_after_approval"]:
        lines.extend([
            f"### {item['name']}",
            "",
            item["purpose"],
            "",
            "```text",
            item["action"],
            "```",
            "",
        ])
    lines.extend(["## Expected Readback", ""])
    for key, value in payload["expected_readback"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Evidence", ""])
    for row in payload["evidence"]:
        status = "present" if row["exists"] else "missing"
        lines.append(f"- `{row['path']}` ({status})")
    lines.extend(["", "## Stop Conditions", ""])
    for item in payload["stop_conditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    tags = "".join(f"<li><code>{esc(tag)}</code></li>" for tag in payload["tags"])
    steps = "\n".join(
        f"""<tr>
          <td>{esc(item['name'])}</td>
          <td>{esc(item['purpose'])}</td>
          <td><pre>{esc(item['action'])}</pre></td>
        </tr>"""
        for item in payload["upload_steps_after_approval"]
    )
    readback = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in payload["expected_readback"].items()
    )
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(row['path'])}</code></td>"
        f"<td class=\"{'ready' if row['exists'] else 'fail'}\">{esc('present' if row['exists'] else 'missing')}</td>"
        "</tr>"
        for row in payload["evidence"]
    )
    stop_items = "".join(f"<li>{esc(item)}</li>" for item in payload["stop_conditions"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Video Upload Metadata</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; width: 220px; }}
    code, pre {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; white-space: pre-wrap; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Video Upload Metadata</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Metadata</h2>
      <table>
        <tbody>
          <tr><th>Title</th><td>{esc(payload['title'])}</td></tr>
          <tr><th>Platform</th><td>{esc(payload['platform'])}</td></tr>
          <tr><th>Visibility after approval</th><td>{esc(payload['visibility_after_approval'])}</td></tr>
          <tr><th>Duration</th><td>{esc(payload['observed_duration_seconds'])} / {esc(payload['duration_limit_seconds'])} seconds</td></tr>
          <tr><th>Public video URL</th><td class="pending">{esc(payload['public_video_url'])}</td></tr>
          <tr><th>Final public video ready</th><td class="pending">{esc(payload['final_public_video_ready'])}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Description</h2>
      <p>{esc(payload['description']).replace(chr(10), '<br>')}</p>
      <h3>Tags</h3>
      <ul>{tags}</ul>
    </section>
    <section>
      <h2>Safe Claim Boundary</h2>
      <p>{esc(payload['safe_claim_boundary'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Upload Steps After Approval</h2>
      <table>
        <thead><tr><th>Step</th><th>Purpose</th><th>Action</th></tr></thead>
        <tbody>{steps}</tbody>
      </table>
    </section>
    <section>
      <h2>Expected Readback</h2>
      <table><tbody>{readback}</tbody></table>
    </section>
    <section>
      <h2>Evidence</h2>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Stop Conditions</h2>
      <ul>{stop_items}</ul>
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
    submission = root / "submission"
    reports.mkdir(parents=True, exist_ok=True)
    submission.mkdir(parents=True, exist_ok=True)
    markdown = render_markdown(payload)
    write_json(reports / "latest_video_upload_metadata.json", payload)
    (reports / "latest_video_upload_metadata.md").write_text(markdown, encoding="utf-8")
    (reports / "latest_video_upload_metadata.html").write_text(render_html(payload), encoding="utf-8")
    (submission / "VIDEO_UPLOAD_METADATA.md").write_text(markdown, encoding="utf-8")
    return {
        "status": payload["status"],
        "html": "reports/latest_video_upload_metadata.html",
        "markdown": "reports/latest_video_upload_metadata.md",
        "json": "reports/latest_video_upload_metadata.json",
        "submission_markdown": "submission/VIDEO_UPLOAD_METADATA.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local metadata and readback expectations for the public demo video upload gate.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
