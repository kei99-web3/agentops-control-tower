from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from submission_urls import approved_urls_path, field_values_for
from validate_submission_urls import build_report


READBACK_REL_PATH = "reports/latest_public_artifact_url_readback.json"


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def verified_readback_issues(root: Path, repository_url: str, demo_video_url: str) -> list[str]:
    path = root / READBACK_REL_PATH
    payload = read_json(path)
    if not payload:
        return [f"{READBACK_REL_PATH} must exist from verify_public_artifact_urls.py --live-readback before --write-approved"]

    issues: list[str] = []
    safe = payload.get("public_safe_readback", {})
    repo_safe = safe.get("repository", {}) if isinstance(safe, dict) else {}
    video_safe = safe.get("demo_video", {}) if isinstance(safe, dict) else {}

    if payload.get("producer") != "verify_public_artifact_urls.py":
        issues.append("verified readback must be produced by verify_public_artifact_urls.py")
    if payload.get("ready_for_url_writeback") is not True:
        issues.append("verified readback ready_for_url_writeback must be true")
    if payload.get("live_readback_attempted") is not True:
        issues.append("verified readback must have live_readback_attempted true")
    if payload.get("failed_count") != 0:
        issues.append("verified readback failed_count must be 0")
    if payload.get("pending_urls") != []:
        issues.append("verified readback pending_urls must be empty")
    if payload.get("repository_url") != repository_url:
        issues.append("verified readback repository_url must match --repository-url")
    if payload.get("demo_video_url") != demo_video_url:
        issues.append("verified readback demo_video_url must match --demo-video-url")
    if not isinstance(safe, dict) or safe.get("ready_for_url_writeback") is not True:
        issues.append("public_safe_readback.ready_for_url_writeback must be true")
    if repo_safe.get("url") != repository_url:
        issues.append("public_safe_readback repository.url must match --repository-url")
    if repo_safe.get("visibility") != "PUBLIC" or repo_safe.get("is_private") is not False:
        issues.append("public_safe_readback repository visibility must be PUBLIC")
    if video_safe.get("url") != demo_video_url:
        issues.append("public_safe_readback demo_video.url must match --demo-video-url")
    status = video_safe.get("http_status")
    if not isinstance(status, int) or not (200 <= status < 400):
        issues.append("public_safe_readback demo_video.http_status must be 2xx/3xx")
    return issues


def build_payload(root: Path, repository_url: str, demo_video_url: str, *, write_approved: bool, approval_note: str) -> dict[str, Any]:
    validation = build_report(root, repository_url, demo_video_url)
    readback_issues = verified_readback_issues(root, repository_url, demo_video_url) if write_approved else []
    can_write = bool(write_approved and validation["final_submit_ready"] and approval_note.strip() and not readback_issues)
    target_path = approved_urls_path(root)
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": validation["status"],
        "final_submit_ready": validation["final_submit_ready"],
        "write_requested": write_approved,
        "approved_urls_file_written": can_write,
        "approved_urls_path": target_path.relative_to(root).as_posix(),
        "repository_url": repository_url,
        "demo_video_url": demo_video_url,
        "pending_urls": validation["pending_urls"],
        "checks": validation["checks"],
        "approval_note_present": bool(approval_note.strip()),
        "verified_readback_required": bool(write_approved),
        "verified_readback_passed": bool(write_approved and not readback_issues),
        "verified_readback_source": READBACK_REL_PATH,
        "verified_readback_issues": readback_issues,
        "boundary": "This plan only validates and optionally writes a local approved URL file. It does not publish, upload, submit, or update Devpost.",
    }


def write_approved_urls(root: Path, payload: dict[str, Any], approval_note: str) -> None:
    path = approved_urls_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "generated_at_utc": payload["generated_at_utc"],
        "repository_url": payload["repository_url"],
        "demo_video_url": payload["demo_video_url"],
        "approval_note": approval_note.strip(),
        "boundary": "Public URLs only. Do not store credentials, tokens, account pages, or private workspace paths here.",
    }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Submission URL Apply Plan",
        "",
        f"Status: {payload['status']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Write requested: {str(payload['write_requested']).lower()}",
        f"Approved URL file written: {str(payload['approved_urls_file_written']).lower()}",
        f"Verified live readback required: {str(payload['verified_readback_required']).lower()}",
        f"Verified live readback passed: {str(payload['verified_readback_passed']).lower()}",
        "",
        "## URLs",
        "",
        f"Repository URL: {payload['repository_url']}",
        f"Demo video URL: {payload['demo_video_url']}",
        "",
        "## Verified Live Readback",
        "",
        f"Source: {payload['verified_readback_source']}",
        f"Issues: {', '.join(payload['verified_readback_issues']) if payload['verified_readback_issues'] else 'none'}",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        "",
    ]
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{esc(check['name'])}</td>"
        f"<td>{esc(check['status'])}</td>"
        f"<td>{esc(check['detail'])}</td>"
        "</tr>"
        for check in payload["checks"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Submission URL Apply Plan</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1040px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Submission URL Apply Plan</h1>
    <p>Status: <span class="{'ready' if payload['final_submit_ready'] else 'pending'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>URLs</h2>
      <table>
        <tbody>
          <tr><th>Repository URL</th><td>{esc(payload['repository_url'])}</td></tr>
          <tr><th>Demo video URL</th><td>{esc(payload['demo_video_url'])}</td></tr>
          <tr><th>Approved URL file</th><td>{esc(payload['approved_urls_path'])}</td></tr>
          <tr><th>File written</th><td>{esc(payload['approved_urls_file_written'])}</td></tr>
          <tr><th>Verified live readback required</th><td>{esc(payload['verified_readback_required'])}</td></tr>
          <tr><th>Verified live readback passed</th><td>{esc(payload['verified_readback_passed'])}</td></tr>
          <tr><th>Verified live readback source</th><td>{esc(payload['verified_readback_source'])}</td></tr>
          <tr><th>Verified live readback issues</th><td>{esc(', '.join(payload['verified_readback_issues']) if payload['verified_readback_issues'] else 'none')}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Boundary</h2>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
  </main>
</body>
</html>
"""


def run(root: Path, repository_url: str | None, demo_video_url: str | None, *, write_approved: bool, approval_note: str) -> dict[str, Any]:
    fields = field_values_for(root)
    repo = repository_url or str(fields["repository_url"])
    video = demo_video_url or str(fields["demo_video_url"])
    payload = build_payload(root, repo, video, write_approved=write_approved, approval_note=approval_note)
    if write_approved and not payload["approved_urls_file_written"]:
        payload["status"] = "needs_more_evidence"
    if payload["approved_urls_file_written"]:
        write_approved_urls(root, payload, approval_note)
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_submission_url_apply_plan.json", payload)
    (reports / "latest_submission_url_apply_plan.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_submission_url_apply_plan.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "final_submit_ready": payload["final_submit_ready"],
        "approved_urls_file_written": payload["approved_urls_file_written"],
        "html": "reports/latest_submission_url_apply_plan.html",
        "markdown": "reports/latest_submission_url_apply_plan.md",
        "json": "reports/latest_submission_url_apply_plan.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare or apply approved public Devpost URLs locally.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--repository-url", "--repo-url", dest="repository_url", default=None)
    parser.add_argument("--demo-video-url", "--video-url", dest="demo_video_url", default=None)
    parser.add_argument("--write-approved", action="store_true")
    parser.add_argument("--approval-note", default="")
    args = parser.parse_args()

    result = run(
        Path(args.root).resolve(),
        args.repository_url,
        args.demo_video_url,
        write_approved=args.write_approved,
        approval_note=args.approval_note,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] != "needs_more_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
