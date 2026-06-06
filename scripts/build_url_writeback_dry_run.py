from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SAMPLE_REPOSITORY_URL = "https://github.com/example/agentops-control-tower"
SAMPLE_DEMO_VIDEO_URL = "https://youtu.be/agentops-control-tower-demo"
SAMPLE_READBACK_REL_PATH = "reports/latest_public_artifact_url_readback.json"
BOUNDARY = (
    "This URL writeback dry run uses sample public URL shapes inside a temporary local copy only. "
    "It does not publish a repository, upload video, write approved URLs to the working tree, "
    "update Devpost, save a draft, press submit, or submit anything."
)
ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/][^\n\r\"']+")


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=sanitize(detail)))


def sanitize(value: str) -> str:
    return ABSOLUTE_PATH_PATTERN.sub("<local-path>", value)


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def run_command(name: str, args: list[str], cwd: Path, checks: list[Check], *, expected_returncode: int = 0) -> None:
    completed = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    output = (completed.stdout + "\n" + completed.stderr).strip()
    detail = sanitize(output[-900:] if output else "no output")
    add_check(checks, name, completed.returncode == expected_returncode, detail)


def copy_project_to_temp(root: Path, temp_root: Path) -> Path:
    rehearsal = temp_root / "agentops_url_writeback_dry_run"
    shutil.copytree(
        root,
        rehearsal,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "release"),
    )
    return rehearsal


def seed_verified_readback(root: Path) -> None:
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "producer": "verify_public_artifact_urls.py",
        "status": "ready_for_url_writeback_after_user_approval",
        "repository_url": SAMPLE_REPOSITORY_URL,
        "demo_video_url": SAMPLE_DEMO_VIDEO_URL,
        "pending_urls": [],
        "url_shape_final_submit_ready": True,
        "live_readback_requested": True,
        "live_readback_attempted": True,
        "ready_for_url_writeback": True,
        "approved_public_urls_exists": False,
        "failed_count": 0,
        "public_safe_readback": {
            "action_key": "approved_url_writeback",
            "status": "ready_for_url_writeback_after_user_approval",
            "repository": {
                "url": SAMPLE_REPOSITORY_URL,
                "slug": "example/agentops-control-tower",
                "visibility": "PUBLIC",
                "is_private": False,
                "name_with_owner": "example/agentops-control-tower",
            },
            "demo_video": {
                "url": SAMPLE_DEMO_VIDEO_URL,
                "final_url": SAMPLE_DEMO_VIDEO_URL,
                "host": "youtu.be",
                "http_status": 200,
                "method": "GET",
                "content_type": "text/html",
                "error_present": False,
            },
            "pending_urls": [],
            "live_readback_attempted": True,
            "ready_for_url_writeback": True,
            "approved_public_urls_exists": False,
            "failed_count": 0,
        },
        "boundary": "Synthetic verified-readback fixture for temp dry run only.",
    }
    write_json(root / SAMPLE_READBACK_REL_PATH, payload)


def inspect_rehearsal(root: Path, checks: list[Check]) -> dict[str, Any]:
    approved_path = root / "submission" / "approved_public_urls.json"
    apply_plan = read_json(root / "reports/latest_submission_url_apply_plan.json")
    validation = read_json(root / "reports/latest_submission_url_validation.json")
    final_copy = read_json(root / "reports/latest_devpost_final_copy.json")
    go_no_go = read_json(root / "reports/latest_final_go_no_go.json")
    submit_plan = read_json(root / "reports/latest_devpost_submit_command_plan.json")
    manual_fill = read_json(root / "reports/latest_devpost_manual_fill_brief.json")
    post_action = read_json(root / "reports/latest_post_action_evidence_brief.json")

    add_check(checks, "temp approved URL file exists", approved_path.exists(), "submission/approved_public_urls.json")
    approved = read_json(approved_path)
    add_check(checks, "temp repository URL matches sample", approved.get("repository_url") == SAMPLE_REPOSITORY_URL, str(approved.get("repository_url", "missing")))
    add_check(checks, "temp demo video URL matches sample", approved.get("demo_video_url") == SAMPLE_DEMO_VIDEO_URL, str(approved.get("demo_video_url", "missing")))
    add_check(checks, "URL apply plan wrote only in temp", apply_plan.get("approved_urls_file_written") is True, str(apply_plan.get("approved_urls_file_written", "missing")))
    add_check(checks, "URL apply plan required verified readback in temp", apply_plan.get("verified_readback_required") is True, str(apply_plan.get("verified_readback_required", "missing")))
    add_check(checks, "URL apply plan accepted verified readback in temp", apply_plan.get("verified_readback_passed") is True, str(apply_plan.get("verified_readback_passed", "missing")))
    add_check(checks, "URL validation ready in temp", validation.get("final_submit_ready") is True and validation.get("pending_urls") == [], str(validation.get("pending_urls", "missing")))
    add_check(checks, "Devpost final copy ready in temp", final_copy.get("final_submit_ready") is True and final_copy.get("pending_urls") == [], str(final_copy.get("pending_urls", "missing")))
    add_check(checks, "Go/No-Go final ready in temp", go_no_go.get("final_submit_ready") is True, str(go_no_go.get("final_submit_ready", "missing")))
    add_check(checks, "Devpost submit plan final ready in temp", submit_plan.get("final_submit_ready") is True, str(submit_plan.get("final_submit_ready", "missing")))
    add_check(checks, "Devpost manual fill has no pending URL fields in temp", manual_fill.get("pending_fields") == [], str(manual_fill.get("pending_fields", "missing")))
    add_check(checks, "Post-action brief sees approved URLs in temp", post_action.get("approved_public_urls_exists") is True, str(post_action.get("approved_public_urls_exists", "missing")))
    return {
        "approved_urls_file_exists": approved_path.exists(),
        "url_apply_status": apply_plan.get("status", "missing"),
        "url_apply_verified_readback_passed": apply_plan.get("verified_readback_passed", "missing"),
        "url_validation_status": validation.get("status", "missing"),
        "final_copy_submit_ready": final_copy.get("final_submit_ready", "missing"),
        "go_no_go_final_submit_ready": go_no_go.get("final_submit_ready", "missing"),
        "submit_plan_final_submit_ready": submit_plan.get("final_submit_ready", "missing"),
        "manual_fill_pending_fields": manual_fill.get("pending_fields", "missing"),
        "post_action_evidence_ready": post_action.get("post_action_evidence_ready", "missing"),
        "post_action_incomplete_actions": post_action.get("incomplete_actions", []),
    }


def build_payload(root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    project_root = root.resolve()
    original_approved_path = project_root / "submission" / "approved_public_urls.json"
    add_check(checks, "working tree approved URL file absent before dry run", not original_approved_path.exists(), "approved_public_urls.json absent" if not original_approved_path.exists() else "approved_public_urls.json exists")

    with tempfile.TemporaryDirectory(prefix="agentops_url_writeback_dry_run_") as temp_dir:
        temp_root = Path(temp_dir)
        rehearsal = copy_project_to_temp(project_root, temp_root)
        run_command(
            "temp block approved sample URLs without verified readback",
            [
                sys.executable,
                "scripts/prepare_submission_urls.py",
                "--repository-url",
                SAMPLE_REPOSITORY_URL,
                "--demo-video-url",
                SAMPLE_DEMO_VIDEO_URL,
                "--write-approved",
                "--approval-note",
                "local dry run only",
            ],
            rehearsal,
            checks,
            expected_returncode=1,
        )
        add_check(
            checks,
            "temp approved URL file absent before verified readback",
            not (rehearsal / "submission/approved_public_urls.json").exists(),
            "approved_public_urls.json absent",
        )
        seed_verified_readback(rehearsal)
        run_command(
            "temp write approved sample URLs",
            [
                sys.executable,
                "scripts/prepare_submission_urls.py",
                "--repository-url",
                SAMPLE_REPOSITORY_URL,
                "--demo-video-url",
                SAMPLE_DEMO_VIDEO_URL,
                "--write-approved",
                "--approval-note",
                "local dry run only",
            ],
            rehearsal,
            checks,
        )
        for name, script in [
            ("temp validate submission URLs", "scripts/validate_submission_urls.py"),
            ("temp rebuild Devpost submission packet", "scripts/build_devpost_submission_packet.py"),
            ("temp export Devpost final copy", "scripts/export_devpost_final_copy.py"),
            ("temp rebuild final Go/No-Go", "scripts/build_final_go_no_go_report.py"),
            ("temp rebuild Devpost submit plan", "scripts/build_devpost_submit_command_plan.py"),
            ("temp rebuild Devpost manual fill brief", "scripts/build_devpost_manual_fill_brief.py"),
            ("temp rebuild post-action evidence brief", "scripts/build_post_action_evidence_brief.py"),
        ]:
            run_command(name, [sys.executable, script], rehearsal, checks)
        rehearsal_state = inspect_rehearsal(rehearsal, checks)

    add_check(checks, "working tree approved URL file still absent after dry run", not original_approved_path.exists(), "approved_public_urls.json absent" if not original_approved_path.exists() else "approved_public_urls.json exists")
    failed = [check for check in checks if not check.passed]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not failed else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(project_root) else "workspace",
        "sample_repository_url": SAMPLE_REPOSITORY_URL,
        "sample_demo_video_url": SAMPLE_DEMO_VIDEO_URL,
        "working_tree_approved_urls_exists": original_approved_path.exists(),
        "temp_root_removed_after_run": True,
        "rehearsal_state": rehearsal_state,
        "final_submit_ready_in_temp": rehearsal_state.get("go_no_go_final_submit_ready") is True,
        "approved_public_urls_written_to_working_tree": original_approved_path.exists(),
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "next_required_external_approval": "approved_url_writeback",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# URL Writeback Dry Run",
        "",
        f"Status: {payload['status']}",
        f"Final submit ready in temp: {str(payload['final_submit_ready_in_temp']).lower()}",
        f"Approved URLs written to working tree: {str(payload['approved_public_urls_written_to_working_tree']).lower()}",
        f"Verified readback passed in temp: {str(payload['rehearsal_state'].get('url_apply_verified_readback_passed')).lower()}",
        "",
        "## Sample URLs",
        "",
        f"- Repository: {payload['sample_repository_url']}",
        f"- Demo video: {payload['sample_demo_video_url']}",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        lines.append(f"- {check['status']}: {check['name']} - {check['detail']}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
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
  <title>URL Writeback Dry Run</title>
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
    <h1>URL Writeback Dry Run</h1>
    <p>Local-only rehearsal for approved public URL writeback and final-submit state changes.</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <table>
        <tbody>
          <tr><th>Status</th><td class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</td></tr>
          <tr><th>Final submit ready in temp</th><td>{esc(payload['final_submit_ready_in_temp'])}</td></tr>
          <tr><th>Verified readback passed in temp</th><td>{esc(payload['rehearsal_state'].get('url_apply_verified_readback_passed'))}</td></tr>
          <tr><th>Approved URLs written to working tree</th><td>{esc(payload['approved_public_urls_written_to_working_tree'])}</td></tr>
          <tr><th>Sample repository URL</th><td><code>{esc(payload['sample_repository_url'])}</code></td></tr>
          <tr><th>Sample demo video URL</th><td><code>{esc(payload['sample_demo_video_url'])}</code></td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
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


def run(root: Path) -> dict[str, Any]:
    payload = build_payload(root)
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_url_writeback_dry_run.json", payload)
    (reports / "latest_url_writeback_dry_run.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_url_writeback_dry_run.html").write_text(render_html(payload), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local-only approved URL writeback dry run report.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    payload = run(Path(args.root).resolve())
    print(json.dumps({
        "status": payload["status"],
        "failed_count": payload["failed_count"],
        "final_submit_ready_in_temp": payload["final_submit_ready_in_temp"],
        "approved_public_urls_written_to_working_tree": payload["approved_public_urls_written_to_working_tree"],
        "html": "reports/latest_url_writeback_dry_run.html",
        "markdown": "reports/latest_url_writeback_dry_run.md",
        "json": "reports/latest_url_writeback_dry_run.json",
    }, ensure_ascii=False, indent=2))
    return 0 if payload["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
