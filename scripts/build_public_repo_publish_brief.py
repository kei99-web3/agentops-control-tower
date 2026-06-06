from __future__ import annotations

import argparse
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_NAME = "agentops-control-tower"
PUBLIC_CANDIDATE = "public_repo_candidate/agentops-control-tower"
ZIP_PATH = "release/agentops-control-tower-public-candidate.zip"
NAMESPACE_CHECK_COMMAND = "gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url,isPrivate"
BOUNDARY = (
    "This brief is local publication decision support only. It does not create a public repo, "
    "push commits, publish files, write approved URLs, upload video, update Devpost, or submit anything."
)


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_file_count(root: Path) -> int:
    skip_dirs = {".git", "__pycache__", "release", "public_repo_candidate"}
    skip_suffixes = {".pyc", ".zip"}
    count = 0
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        parts = set(path.relative_to(root).parts)
        if parts.intersection(skip_dirs) or path.suffix.lower() in skip_suffixes:
            continue
        count += 1
    return count


def evidence_items(root: Path) -> list[str]:
    if is_public_candidate_root(root):
        return [
            "README.md",
            "LICENSE",
            "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
            "reports/latest_judge_quickstart.html",
            "reports/latest_launch_decision_brief.html",
            "reports/latest_publication_command_plan.html",
            "reports/latest_video_cue_sheet.html",
            "reports/latest_submission_url_validation.html",
            "reports/latest_public_artifact_url_readback.html",
        ]
    return [
        f"{PUBLIC_CANDIDATE}/README.md",
        f"{PUBLIC_CANDIDATE}/LICENSE",
        f"{PUBLIC_CANDIDATE}/PUBLIC_REPO_CANDIDATE_MANIFEST.md",
        f"{PUBLIC_CANDIDATE}/reports/latest_judge_quickstart.html",
        f"{PUBLIC_CANDIDATE}/reports/latest_launch_decision_brief.html",
        "reports/latest_public_artifact_url_readback.html",
        "reports/latest_publication_command_plan.html",
        "reports/latest_public_repo_dry_run.html",
        "reports/latest_release_zip_smoke_test.html",
        "reports/latest_public_candidate_zip_manifest.html",
        ZIP_PATH,
    ]


def publish_steps(root: Path) -> list[dict[str, str]]:
    candidate_root = is_public_candidate_root(root)
    helper_command = "python scripts\\publish_public_repo_after_approval.py"
    execute_command = (
        "python scripts\\publish_public_repo_after_approval.py "
        "--execute "
        "--approval-phrase \"Approve public GitHub publication for the clean agentops-control-tower candidate.\" "
        "--repo-name agentops-control-tower "
        "--git-user-name \"<approved-public-git-name>\" "
        "--git-user-email \"<approved-public-git-email>\""
    )
    source_label = "current folder" if candidate_root else PUBLIC_CANDIDATE
    return [
        {
            "step": "Review source folder",
            "command": f"manual: review {source_label}",
            "verification": "Confirm this is the clean public candidate, not the private workspace root.",
        },
        {
            "step": "Run guarded publication rehearsal",
            "command": helper_command,
            "verification": "The helper validates an isolated audit copy, scans a clean publish copy, creates a local commit, and leaves no remote configured.",
        },
        {
            "step": "Run public repository publication preflight",
            "command": (
                "python scripts\\verify_public_repo_publication_gate.py "
                "--approval-phrase \"Approve public GitHub publication for the clean agentops-control-tower candidate.\" "
                "--source-folder-reviewed --isolated-staging-confirmed --secret-scan-confirmed "
                "--public-visibility-confirmed --public-git-identity-confirmed "
                "--git-user-name \"<approved-public-git-name>\" "
                "--git-user-email \"<approved-public-git-email>\""
            ),
            "verification": "Preflight must show ready_for_manual_public_repo_publication before any public repository creation.",
        },
        {
            "step": "Check public repository namespace",
            "command": NAMESPACE_CHECK_COMMAND,
            "verification": "If this resolves to an existing repository, stop and choose a new approved repo name or remove the stale repository before running the guarded helper.",
        },
        {
            "step": "Execute guarded public GitHub publication after explicit approval",
            "command": execute_command,
            "verification": "The helper accepts the exact approval phrase, creates the public repository, pushes main, and prints GitHub readback.",
        },
        {
            "step": "Read back public repository URL",
            "command": "gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url",
            "verification": "Visibility is PUBLIC and the URL opens without authentication.",
        },
        {
            "step": "Verify public artifact URLs after repo and video are public",
            "command": "python scripts\\verify_public_artifact_urls.py --repository-url <public-repo-url> --demo-video-url <public-video-url> --live-readback",
            "verification": "URL readback confirms the GitHub repository is PUBLIC and the public video URL is reachable.",
        },
        {
            "step": "Hold URL writeback until video URL also exists",
            "command": "manual: do not run prepare_submission_urls.py until both public repo and public video URLs are approved",
            "verification": "submission/approved_public_urls.json remains absent until both URLs are approved.",
        },
    ]


def build_payload(root: Path) -> dict[str, Any]:
    publication = read_json(root / "reports/latest_publication_command_plan.json")
    url_validation = read_json(root / "reports/latest_submission_url_validation.json")
    zip_manifest = read_json(root / "reports/latest_public_candidate_zip_manifest.json")
    smoke = read_json(root / "reports/latest_release_zip_smoke_test.json")
    approved_urls = root / "submission/approved_public_urls.json"
    evidence = [{"path": item, "exists": exists(root, item)} for item in evidence_items(root)]
    missing = [item["path"] for item in evidence if not item["exists"]]
    zip_file = root / ZIP_PATH
    zip_sha = sha256_file(zip_file) if zip_file.exists() else ""
    candidate_root = is_public_candidate_root(root)
    file_count = zip_manifest.get("file_count", smoke.get("zip_file_count", "missing"))
    if file_count == "missing" and candidate_root:
        file_count = candidate_file_count(root)
    pending_urls = set(url_validation.get("pending_urls", []))
    zip_ready = candidate_root or smoke.get("status") == "pass" or isinstance(zip_manifest.get("file_count"), int)
    publication_ready = publication.get("status") == "ready_for_user_review"
    ready = (
        not missing
        and publication_ready
        and zip_ready
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if ready else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "repo_name": REPO_NAME,
        "candidate_path": "." if is_public_candidate_root(root) else PUBLIC_CANDIDATE,
        "approval_phrase": "Approve public GitHub publication for the clean agentops-control-tower candidate.",
        "public_repo_approval_ready": ready and "repository_url" in pending_urls,
        "final_submit_ready": False,
        "approved_urls_written": approved_urls.exists(),
        "zip": {
            "path": ZIP_PATH,
            "exists": zip_file.exists(),
            "sha256": zip_sha,
            "file_count": file_count,
            "smoke_status": "not_applicable_public_candidate_root" if candidate_root else smoke.get("status", "missing"),
        },
        "missing_evidence": missing,
        "evidence": evidence,
        "publish_steps": publish_steps(root),
        "stop_conditions": [
            "Do not publish if the source path is not the clean public candidate.",
            "Do not publish from a git repository initialized inside the private workspace.",
            "Do not publish if internal path or secret-like scans fail.",
            "Do not write approved URLs until both public repository and public demo video URLs are verified.",
            "Do not press Devpost submit from this step.",
        ],
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Public Repo Publish Brief",
        "",
        f"Status: {payload['status']}",
        f"Candidate: {payload['candidate_path']}",
        f"Approval phrase: {payload['approval_phrase']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        "",
        "## ZIP Evidence",
        "",
        f"- Path: `{payload['zip']['path']}`",
        f"- Exists: {payload['zip']['exists']}",
        f"- File count: {payload['zip']['file_count']}",
        f"- Smoke status: {payload['zip']['smoke_status']}",
        f"- SHA256: `{payload['zip']['sha256']}`",
        "",
        "## Publish Steps After Approval",
        "",
    ]
    for index, step in enumerate(payload["publish_steps"], start=1):
        lines.extend([
            f"{index}. {step['step']}",
            "",
            "```powershell",
            step["command"],
            "```",
            "",
            f"Verification: {step['verification']}",
            "",
        ])
    lines.extend(["## Stop Conditions", ""])
    for item in payload["stop_conditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        "</tr>"
        for item in payload["evidence"]
    )
    step_rows = "\n".join(
        "<tr>"
        f"<td>{esc(index)}</td>"
        f"<td>{esc(step['step'])}</td>"
        f"<td><code>{esc(step['command'])}</code></td>"
        f"<td>{esc(step['verification'])}</td>"
        "</tr>"
        for index, step in enumerate(payload["publish_steps"], start=1)
    )
    stops = "\n".join(f"<li>{esc(item)}</li>" for item in payload["stop_conditions"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Repo Publish Brief</title>
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
    <h1>Public Repo Publish Brief</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Decision</h2>
      <p>Approval phrase: <strong>{esc(payload['approval_phrase'])}</strong></p>
      <p>Candidate: <code>{esc(payload['candidate_path'])}</code></p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>ZIP Evidence</h2>
      <table>
        <tbody>
          <tr><th>Path</th><td><code>{esc(payload['zip']['path'])}</code></td></tr>
          <tr><th>File count</th><td>{esc(payload['zip']['file_count'])}</td></tr>
          <tr><th>Smoke status</th><td>{esc(payload['zip']['smoke_status'])}</td></tr>
          <tr><th>SHA256</th><td><code>{esc(payload['zip']['sha256'])}</code></td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Evidence</h2>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Publish Steps After Approval</h2>
      <table>
        <thead><tr><th>#</th><th>Step</th><th>Command</th><th>Verification</th></tr></thead>
        <tbody>{step_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Stop Conditions</h2>
      <ul>{stops}</ul>
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
    write_json(reports / "latest_public_repo_publish_brief.json", payload)
    (reports / "latest_public_repo_publish_brief.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_public_repo_publish_brief.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "repo_name": payload["repo_name"],
        "missing_evidence": payload["missing_evidence"],
        "html": "reports/latest_public_repo_publish_brief.html",
        "markdown": "reports/latest_public_repo_publish_brief.md",
        "json": "reports/latest_public_repo_publish_brief.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local public repository publish decision brief.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
