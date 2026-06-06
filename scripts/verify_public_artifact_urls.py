from __future__ import annotations

import argparse
import html
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from submission_urls import PENDING_REPO, PENDING_VIDEO, field_values_for
from validate_submission_urls import build_report


BOUNDARY = (
    "This public artifact URL readback is a verification aid only. Default mode does not "
    "perform network readback when URLs are still pending. It does not publish, upload, "
    "write approved URLs, update Devpost, or submit anything."
)


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def is_pending(repository_url: str, demo_video_url: str) -> bool:
    return repository_url == PENDING_REPO or demo_video_url == PENDING_VIDEO


def gh_repo_slug(repository_url: str) -> str:
    parsed = urlparse(repository_url)
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return ""
    return f"{parts[0]}/{parts[1]}"


def verify_github_repo(repository_url: str, checks: list[Check]) -> dict[str, Any]:
    slug = gh_repo_slug(repository_url)
    add_check(checks, "GitHub repository URL path", bool(slug), slug or "missing owner/repo")
    if not slug:
        return {"slug": "", "readback": {}, "returncode": 1}

    completed = subprocess.run(
        ["gh", "repo", "view", slug, "--json", "isPrivate,nameWithOwner,url,visibility"],
        capture_output=True,
        text=True,
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()
    try:
        payload = json.loads(completed.stdout) if completed.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    add_check(checks, "GitHub repository readback", completed.returncode == 0, output[-800:] if output else "no output")
    add_check(checks, "GitHub repository visibility public", payload.get("visibility") == "PUBLIC" and payload.get("isPrivate") is False, json.dumps(payload, ensure_ascii=False) if payload else "missing readback")
    return {"slug": slug, "readback": payload, "returncode": completed.returncode}


def http_probe(url: str, *, timeout_seconds: int) -> dict[str, Any]:
    for method in ["HEAD", "GET"]:
        request = Request(url, method=method, headers={"User-Agent": "AgentOps-Control-Tower-URL-Readback/1.0"})
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                return {
                    "method": method,
                    "status_code": int(response.status),
                    "final_url": response.geturl(),
                    "content_type": response.headers.get("content-type", ""),
                    "error": "",
                }
        except HTTPError as exc:
            if method == "HEAD" and exc.code in {403, 405}:
                continue
            return {
                "method": method,
                "status_code": int(exc.code),
                "final_url": url,
                "content_type": exc.headers.get("content-type", "") if exc.headers else "",
                "error": str(exc),
            }
        except URLError as exc:
            return {
                "method": method,
                "status_code": 0,
                "final_url": url,
                "content_type": "",
                "error": str(exc.reason),
            }
    return {"method": "none", "status_code": 0, "final_url": url, "content_type": "", "error": "unreachable"}


def verify_video_url(demo_video_url: str, checks: list[Check], *, timeout_seconds: int) -> dict[str, Any]:
    probe = http_probe(demo_video_url, timeout_seconds=timeout_seconds)
    status_code = int(probe.get("status_code", 0))
    add_check(checks, "Demo video URL HTTP readback", 200 <= status_code < 400, json.dumps(probe, ensure_ascii=False))
    final_host = (urlparse(str(probe.get("final_url", demo_video_url))).hostname or "").lower()
    allowed_hosts = {"youtube.com", "www.youtube.com", "youtu.be", "vimeo.com", "www.vimeo.com"}
    add_check(checks, "Demo video URL remains on allowed host", final_host in allowed_hosts, final_host or "missing host")
    return probe


def public_safe_readback(
    *,
    status: str,
    repository_url: str,
    demo_video_url: str,
    pending_urls: list[str],
    live_readback_attempted: bool,
    ready_for_url_writeback: bool,
    approved_public_urls_exists: bool,
    repo_readback: dict[str, Any],
    video_readback: dict[str, Any],
    failed_count: int,
) -> dict[str, Any]:
    repo_metadata = repo_readback.get("readback", {}) if isinstance(repo_readback.get("readback"), dict) else {}
    raw_video_final_url = str(video_readback.get("final_url") or "")
    video_final_url = "" if raw_video_final_url == PENDING_VIDEO else raw_video_final_url
    video_public_url = "" if demo_video_url == PENDING_VIDEO else demo_video_url
    video_host = (urlparse(video_final_url or video_public_url).hostname or "").lower()
    repo_public_url = "" if repository_url == PENDING_REPO else str(repo_metadata.get("url") or repository_url)

    return {
        "action_key": "approved_url_writeback",
        "status": status,
        "repository": {
            "url": repo_public_url,
            "slug": str(repo_readback.get("slug") or ""),
            "visibility": str(repo_metadata.get("visibility") or ""),
            "is_private": repo_metadata.get("isPrivate", None),
            "name_with_owner": str(repo_metadata.get("nameWithOwner") or ""),
        },
        "demo_video": {
            "url": video_public_url,
            "final_url": video_final_url,
            "host": video_host,
            "http_status": video_readback.get("status_code", None),
            "method": str(video_readback.get("method") or ""),
            "content_type": str(video_readback.get("content_type") or ""),
            "error_present": bool(video_readback.get("error")),
        },
        "pending_urls": pending_urls,
        "live_readback_attempted": live_readback_attempted,
        "ready_for_url_writeback": ready_for_url_writeback,
        "approved_public_urls_exists": approved_public_urls_exists,
        "failed_count": failed_count,
        "evidence_note_target": "submission/post_action_evidence/YYYY-MM-DD_approved_url_writeback_readback.md",
        "copy_policy": (
            "Use this public_safe_readback block for post-action evidence. Do not copy raw "
            "command output, credentials, tokens, account screenshots, browser tabs, or local absolute paths."
        ),
        "next_required_external_approval": "approved_url_writeback",
    }


def build_payload(
    root: Path,
    repository_url: str,
    demo_video_url: str,
    *,
    live_readback: bool,
    timeout_seconds: int,
) -> dict[str, Any]:
    checks: list[Check] = []
    shape = build_report(root, repository_url, demo_video_url)
    for item in shape["checks"]:
        checks.append(Check(name=f"shape: {item['name']}", status=item["status"], detail=item["detail"]))

    pending = is_pending(repository_url, demo_video_url)
    add_check(checks, "approved URL file remains absent", not (root / "submission/approved_public_urls.json").exists(), "approved_public_urls.json absent" if not (root / "submission/approved_public_urls.json").exists() else "approved_public_urls.json exists")
    if pending:
        add_check(checks, "public URLs pending", True, ", ".join(shape.get("pending_urls", [])))
        repo_readback = {"slug": "", "readback": {}, "returncode": None}
        video_readback = {"method": "not_run", "status_code": None, "final_url": "", "content_type": "", "error": "pending URLs"}
        live_attempted = False
    elif live_readback:
        repo_readback = verify_github_repo(repository_url, checks)
        video_readback = verify_video_url(demo_video_url, checks, timeout_seconds=timeout_seconds)
        live_attempted = True
    else:
        add_check(checks, "live readback explicitly skipped", True, "pass --live-readback after public URLs exist")
        repo_readback = {"slug": gh_repo_slug(repository_url), "readback": {}, "returncode": None}
        video_readback = {"method": "not_run", "status_code": None, "final_url": "", "content_type": "", "error": "live readback skipped"}
        live_attempted = False

    failed = [check for check in checks if not check.passed]
    ready_for_writeback = bool(shape["final_submit_ready"] and live_readback and live_attempted and not failed)
    if failed:
        status = "needs_more_evidence"
    elif pending:
        status = "waiting_for_external_urls"
    elif ready_for_writeback:
        status = "ready_for_url_writeback_after_user_approval"
    else:
        status = "ready_for_live_readback"
    approved_public_urls_exists = (root / "submission/approved_public_urls.json").exists()
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "producer": "verify_public_artifact_urls.py",
        "status": status,
        "repository_url": repository_url,
        "demo_video_url": demo_video_url,
        "pending_urls": shape["pending_urls"],
        "url_shape_final_submit_ready": shape["final_submit_ready"],
        "live_readback_requested": live_readback,
        "live_readback_attempted": live_attempted,
        "ready_for_url_writeback": ready_for_writeback,
        "approved_public_urls_exists": approved_public_urls_exists,
        "github_repo_readback": repo_readback,
        "demo_video_readback": video_readback,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "next_required_external_approval": "approved_url_writeback",
    }
    payload["public_safe_readback"] = public_safe_readback(
        status=status,
        repository_url=repository_url,
        demo_video_url=demo_video_url,
        pending_urls=shape["pending_urls"],
        live_readback_attempted=live_attempted,
        ready_for_url_writeback=ready_for_writeback,
        approved_public_urls_exists=approved_public_urls_exists,
        repo_readback=repo_readback,
        video_readback=video_readback,
        failed_count=len(failed),
    )
    return payload


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    safe = payload["public_safe_readback"]
    repo = safe["repository"]
    video = safe["demo_video"]
    lines = [
        "# Public Artifact URL Readback",
        "",
        f"Status: {payload['status']}",
        f"Live readback attempted: {str(payload['live_readback_attempted']).lower()}",
        f"Ready for URL writeback: {str(payload['ready_for_url_writeback']).lower()}",
        "",
        "## URLs",
        "",
        f"- Repository: {payload['repository_url']}",
        f"- Demo video: {payload['demo_video_url']}",
        "",
        "## Public-Safe Readback",
        "",
        f"- Evidence note target: {safe['evidence_note_target']}",
        f"- Copy policy: {safe['copy_policy']}",
        f"- Repository visibility: {repo['visibility'] or 'pending'}",
        f"- Demo video host/status: {video['host'] or 'pending'} / {video['http_status']}",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        lines.append(f"- {check['status']}: {check['name']} - {check['detail']}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    safe = payload["public_safe_readback"]
    repo = safe["repository"]
    video = safe["demo_video"]
    rows = "\n".join(
        "<tr>"
        f"<td>{esc(check['name'])}</td>"
        f"<td class=\"{'ready' if check['status'] == 'pass' else 'fail'}\">{esc(check['status'])}</td>"
        f"<td>{esc(check['detail'])}</td>"
        "</tr>"
        for check in payload["checks"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Artifact URL Readback</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ width: 240px; color: #5f6d7c; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Public Artifact URL Readback</h1>
    <p>Verification gate before approved URL writeback.</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <table>
        <tbody>
          <tr><th>Status</th><td class="{'ready' if payload['status'] != 'needs_more_evidence' else 'fail'}">{esc(payload['status'])}</td></tr>
          <tr><th>Repository URL</th><td><code>{esc(payload['repository_url'])}</code></td></tr>
          <tr><th>Demo video URL</th><td><code>{esc(payload['demo_video_url'])}</code></td></tr>
          <tr><th>Live readback attempted</th><td>{esc(payload['live_readback_attempted'])}</td></tr>
          <tr><th>Ready for URL writeback</th><td>{esc(payload['ready_for_url_writeback'])}</td></tr>
          <tr><th>Approved public URLs file exists</th><td>{esc(payload['approved_public_urls_exists'])}</td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Public-Safe Readback</h2>
      <table>
        <tbody>
          <tr><th>Evidence note target</th><td><code>{esc(safe['evidence_note_target'])}</code></td></tr>
          <tr><th>Copy policy</th><td>{esc(safe['copy_policy'])}</td></tr>
          <tr><th>Repository visibility</th><td>{esc(repo['visibility'] or 'pending')}</td></tr>
          <tr><th>Repository name</th><td>{esc(repo['name_with_owner'] or 'pending')}</td></tr>
          <tr><th>Demo video host</th><td>{esc(video['host'] or 'pending')}</td></tr>
          <tr><th>Demo video HTTP status</th><td>{esc(video['http_status'])}</td></tr>
          <tr><th>Ready for URL writeback</th><td>{esc(safe['ready_for_url_writeback'])}</td></tr>
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
  </main>
</body>
</html>
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(
    root: Path,
    repository_url: str | None,
    demo_video_url: str | None,
    *,
    live_readback: bool,
    timeout_seconds: int,
) -> dict[str, Any]:
    fields = field_values_for(root)
    repo = repository_url or str(fields["repository_url"])
    video = demo_video_url or str(fields["demo_video_url"])
    payload = build_payload(root, repo, video, live_readback=live_readback, timeout_seconds=timeout_seconds)
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_public_artifact_url_readback.json", payload)
    (reports / "latest_public_artifact_url_readback.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_public_artifact_url_readback.html").write_text(render_html(payload), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify public repository and demo video URLs before local approved URL writeback.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--repository-url", "--repo-url", dest="repository_url", default=None)
    parser.add_argument("--demo-video-url", "--video-url", dest="demo_video_url", default=None)
    parser.add_argument("--live-readback", action="store_true", help="Perform GitHub/video URL readback after public URLs exist.")
    parser.add_argument("--timeout-seconds", type=int, default=12)
    args = parser.parse_args()
    payload = run(
        Path(args.root).resolve(),
        args.repository_url,
        args.demo_video_url,
        live_readback=args.live_readback,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps({
        "status": payload["status"],
        "failed_count": payload["failed_count"],
        "pending_urls": payload["pending_urls"],
        "live_readback_attempted": payload["live_readback_attempted"],
        "ready_for_url_writeback": payload["ready_for_url_writeback"],
        "html": "reports/latest_public_artifact_url_readback.html",
        "markdown": "reports/latest_public_artifact_url_readback.md",
        "json": "reports/latest_public_artifact_url_readback.json",
    }, ensure_ascii=False, indent=2))
    return 0 if payload["status"] != "needs_more_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
