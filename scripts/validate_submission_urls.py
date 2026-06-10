from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from submission_urls import PENDING_REPO, PENDING_VIDEO, field_values_for


ALLOWED_REPO_HOSTS = {"github.com"}
ALLOWED_VIDEO_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "vimeo.com",
    "www.vimeo.com",
}

SECRET_LIKE_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"ghp_[A-Za-z0-9]{20,}",
        r"sk-[A-Za-z0-9]{20,}",
        r"xox[baprs]-[A-Za-z0-9-]{20,}",
        r"AKIA[0-9A-Z]{16}",
        r"token=[A-Za-z0-9._~+/=-]{12,}",
        r"api[_-]?key=[A-Za-z0-9._~+/=-]{12,}",
    ]
]


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


def normalize_host(hostname: str | None) -> str:
    return (hostname or "").lower()


def is_pending(value: str, expected: str) -> bool:
    return value == expected


def has_secret_like(value: str) -> bool:
    return any(pattern.search(value) for pattern in SECRET_LIKE_PATTERNS)


def validate_url(value: str, *, label: str, pending_value: str, allowed_hosts: set[str]) -> tuple[bool, str, bool]:
    if is_pending(value, pending_value):
        return True, "pending user-approved URL", True
    parsed = urlparse(value)
    host = normalize_host(parsed.hostname)
    if parsed.scheme != "https":
        return False, "must use https or pending placeholder", False
    if not host:
        return False, "missing hostname", False
    if host not in allowed_hosts:
        return False, f"{label} host must be one of: {', '.join(sorted(allowed_hosts))}", False
    if has_secret_like(value):
        return False, "URL contains secret-like query or token pattern", False
    local_markers = ["localhost", "127.0.0.1", "file://", "desktop", "ai" + "_workspace"]
    if any(part in value.lower() for part in local_markers):
        return False, "URL appears local or workspace-specific", False
    return True, f"valid public {label} URL shape", False


def build_report(root: Path, repository_url: str, demo_video_url: str) -> dict[str, Any]:
    checks: list[Check] = []
    repo_ok, repo_detail, repo_pending = validate_url(
        repository_url,
        label="repository",
        pending_value=PENDING_REPO,
        allowed_hosts=ALLOWED_REPO_HOSTS,
    )
    video_ok, video_detail, video_pending = validate_url(
        demo_video_url,
        label="video",
        pending_value=PENDING_VIDEO,
        allowed_hosts=ALLOWED_VIDEO_HOSTS,
    )
    add_check(checks, "repository URL", repo_ok, repo_detail)
    add_check(checks, "demo video URL", video_ok, video_detail)
    add_check(checks, "repository approval gate", repo_pending or repository_url.startswith("https://"), "pending or approved URL supplied")
    add_check(checks, "video approval gate", video_pending or demo_video_url.startswith("https://"), "pending or approved URL supplied")

    pending = []
    if repo_pending:
        pending.append("repository_url")
    if video_pending:
        pending.append("demo_video_url")

    failed = [check for check in checks if not check.passed]
    final_submit_ready = not failed and not pending
    if failed:
        status = "needs_more_evidence"
    elif final_submit_ready:
        status = "ready_to_submit_after_user_approval"
    else:
        status = "waiting_for_external_urls"

    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "final_submit_ready": final_submit_ready,
        "pending_urls": pending,
        "repository_url": repository_url,
        "demo_video_url": demo_video_url,
        "checks": [check.__dict__ for check in checks],
        "boundary": "This script validates URL shape only. It does not publish, upload, submit, or update Devpost.",
        "root": root.name,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def render_html(report: dict[str, Any]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(check['name'])}</td>"
        f"<td>{html.escape(check['status'])}</td>"
        f"<td>{html.escape(check['detail'])}</td>"
        "</tr>"
        for check in report["checks"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Submission URL Validation</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; }}
    header {{ background: #17202a; color: #fff; padding: 28px 36px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1040px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 18px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; }}
    .pass {{ color: #127c76; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Submission URL Validation</h1>
    <p>Status: <span class="{html.escape('pass' if report['status'] != 'needs_more_evidence' else 'fail')}">{html.escape(report['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>URLs</h2>
      <table>
        <tbody>
          <tr><th>Repository URL</th><td>{html.escape(report['repository_url'])}</td></tr>
          <tr><th>Demo video URL</th><td>{html.escape(report['demo_video_url'])}</td></tr>
          <tr><th>Final submit ready</th><td class="{'pass' if report['final_submit_ready'] else 'pending'}">{html.escape(str(report['final_submit_ready']))}</td></tr>
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
      <p>{html.escape(report['boundary'])}</p>
    </section>
  </main>
</body>
</html>
"""


def run(root: Path, repository_url: str, demo_video_url: str) -> dict[str, Any]:
    report = build_report(root, repository_url, demo_video_url)
    write_json(root / "reports/latest_submission_url_validation.json", report)
    (root / "reports/latest_submission_url_validation.html").write_text(render_html(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public repo and demo video URL shape before Devpost submission.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--repository-url", default=None)
    parser.add_argument("--demo-video-url", default=None)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    fields = field_values_for(root)
    repository_url = args.repository_url or str(fields["repository_url"])
    demo_video_url = args.demo_video_url or str(fields["demo_video_url"])
    report = run(root, repository_url, demo_video_url)
    print(json.dumps({
        "status": report["status"],
        "final_submit_ready": report["final_submit_ready"],
        "pending_urls": report["pending_urls"],
    }, ensure_ascii=False, indent=2))
    return 0 if report["status"] != "needs_more_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
