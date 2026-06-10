from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PUBLIC_CANDIDATE = "public_repo_candidate/agentops-control-tower"
APPROVAL_PHRASE = "Approve public GitHub publication for the clean agentops-control-tower candidate."
BOUNDARY = (
    "This dry run is local publication rehearsal only. It copies the reviewed public candidate "
    "to an isolated temporary staging folder outside the private workspace and runs git init/add/commit/status "
    "without creating a remote, pushing commits, "
    "publishing files, writing approved URLs, uploading video, updating Devpost, or submitting anything."
)
EXPECTED_TOP_LEVEL = {
    ".gitattributes",
    ".gitignore",
    "LICENSE",
    "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
    "README.md",
    "READY_FOR_REVIEW.md",
    "architecture_diagram.md",
    "assets",
    "data",
    "dist",
    "prototype",
    "reports",
    "scripts",
    "splunk_app",
    "submission",
    "tests",
}
TEXT_SUFFIXES = {
    ".conf",
    ".csv",
    ".html",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".xml",
}
INTERNAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"C:\\" + "Users",
        "PC" + "_User",
        r"Desktop\\" + "AI" + "_" + "Workspace",
        "AI" + "_" + "Workspace",
        r"\." + "com" + "pany",
        "private " + "workspace tree",
    ]
]
ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/][^\n\r\"']+")
SECRET_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"ghp_[A-Za-z0-9]{20,}",
        r"sk-[A-Za-z0-9]{20,}",
        r"xox[baprs]-[A-Za-z0-9-]{20,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
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


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def sanitize(value: str) -> str:
    return ABSOLUTE_PATH_PATTERN.sub("<local-path>", value)


def summarize_git_add_output(output: str) -> str:
    if not output:
        return "no output"

    sanitized = sanitize(output)
    lines = [line.strip() for line in sanitized.splitlines() if line.strip()]
    line_ending_warnings = [
        line
        for line in lines
        if line.startswith("warning: in the working copy of ")
        and " will be replaced by " in line
        and " the next time Git touches it" in line
    ]
    other_lines = [line for line in lines if line not in line_ending_warnings]

    summary: list[str] = []
    if line_ending_warnings:
        summary.append(f"{len(line_ending_warnings)} line-ending warnings suppressed")
    if other_lines:
        summary.append("other output: " + "\n".join(other_lines[-5:]))

    return "\n".join(summary) if summary else "ok"


def private_workspace_root(root: Path) -> Path:
    workspace_name = "AI" + "_Workspace"
    for candidate in [root, *root.parents]:
        if candidate.name == workspace_name:
            return candidate
    return root


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def candidate_source(root: Path) -> Path:
    return root if is_public_candidate_root(root) else root / PUBLIC_CANDIDATE


def file_count(root: Path) -> int:
    return sum(1 for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)


def scan_text(root: Path) -> tuple[list[str], list[str]]:
    internal_hits: list[str] = []
    secret_hits: list[str] = []
    for path in root.rglob("*"):
        if path.is_dir() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            secret_hits.append(f"non_utf8:{rel}")
            continue
        for pattern in INTERNAL_PATTERNS:
            if pattern.search(text):
                internal_hits.append(f"{rel}:{pattern.pattern}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append(f"{rel}:{pattern.pattern}")
    return internal_hits, secret_hits


def run_git(args: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    output = (completed.stdout + "\n" + completed.stderr).strip()
    return completed.returncode, output


def init_main_branch(rehearsal: Path) -> tuple[int, str]:
    init_code, init_output = run_git(["init", "-b", "main"], rehearsal)
    if init_code == 0:
        return init_code, init_output

    fallback_code, fallback_output = run_git(["init"], rehearsal)
    checkout_code, checkout_output = run_git(["checkout", "-b", "main"], rehearsal)
    combined = "\n".join(part for part in [init_output, fallback_output, checkout_output] if part)
    return (0 if fallback_code == 0 and checkout_code == 0 else 1), combined


def git_rehearsal(source: Path, project_root: Path, checks: list[Check]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="agentops_public_repo_dry_run_") as temp_dir:
        temp_root = Path(temp_dir)
        rehearsal = temp_root / "agentops-control-tower"
        workspace_root = private_workspace_root(project_root)
        staging_isolated = not is_relative_to(rehearsal, workspace_root)
        shutil.copytree(
            source,
            rehearsal,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        add_check(checks, "staging copy outside private workspace", staging_isolated, "outside private workspace" if staging_isolated else sanitize(str(rehearsal)))
        init_code, init_output = init_main_branch(rehearsal)
        add_check(checks, "git init main-branch rehearsal", init_code == 0, sanitize(init_output[-800:]) if init_output else "no output")
        branch_code, branch_output = run_git(["branch", "--show-current"], rehearsal)
        branch_name = branch_output.strip()
        add_check(checks, "git branch rehearsal uses main", branch_code == 0 and branch_name == "main", branch_name or "missing")
        remote_code, remote_output = run_git(["remote"], rehearsal)
        add_check(checks, "git remote list remains empty", remote_code == 0 and not remote_output.strip(), remote_output or "no remotes")
        name_code, name_output = run_git(["config", "user.name", "Agentic Incident Command Center Dry Run"], rehearsal)
        add_check(checks, "git dry-run user.name configured", name_code == 0, sanitize(name_output[-800:]) if name_output else "ok")
        email_code, email_output = run_git(["config", "user.email", "agentops-control-tower@example.invalid"], rehearsal)
        add_check(checks, "git dry-run user.email configured", email_code == 0, sanitize(email_output[-800:]) if email_output else "ok")
        add_code, add_output = run_git(["add", "-A"], rehearsal)
        add_check(checks, "git add rehearsal", add_code == 0, summarize_git_add_output(add_output))
        status_code, status_output = run_git(["status", "--short"], rehearsal)
        status_lines = [line for line in status_output.splitlines() if line.strip()]
        add_check(checks, "git status rehearsal", status_code == 0 and len(status_lines) >= 100, f"{len(status_lines)} staged files")
        private_company = "." + "com" + "pany"
        private_workspace = "AI" + "_" + "Workspace"
        unexpected = [line for line in status_lines if private_company in line or private_workspace in line or "public_repo_candidate" in line]
        add_check(checks, "git status has no private workspace names", not unexpected, "\n".join(unexpected) if unexpected else "clean")
        commit_code, commit_output = run_git(["commit", "-m", "Initial Agentic Incident Command Center submission"], rehearsal)
        add_check(checks, "git commit rehearsal", commit_code == 0, sanitize(commit_output[-800:]) if commit_output else "no output")
        rev_code, rev_output = run_git(["rev-parse", "--short=12", "HEAD"], rehearsal)
        commit_sha = rev_output.strip()
        add_check(checks, "git commit hash exists", rev_code == 0 and bool(commit_sha), commit_sha or "missing")
        files_code, files_output = run_git(["ls-files"], rehearsal)
        tracked_files = [line for line in files_output.splitlines() if line.strip()]
        add_check(checks, "git tracked files rehearsal", files_code == 0 and len(tracked_files) == len(status_lines), f"tracked={len(tracked_files)} staged={len(status_lines)}")
        post_status_code, post_status_output = run_git(["status", "--short"], rehearsal)
        post_status_lines = [line for line in post_status_output.splitlines() if line.strip()]
        add_check(checks, "git post-commit status clean", post_status_code == 0 and not post_status_lines, "\n".join(post_status_lines) if post_status_lines else "clean")
        post_remote_code, post_remote_output = run_git(["remote"], rehearsal)
        add_check(checks, "git remote remains empty after commit", post_remote_code == 0 and not post_remote_output.strip(), post_remote_output or "no remotes")
        internal_hits, secret_hits = scan_text(rehearsal)
        add_check(checks, "rehearsal internal path scan", not internal_hits, "\n".join(internal_hits) if internal_hits else "no internal patterns")
        add_check(checks, "rehearsal secret-like scan", not secret_hits, "\n".join(secret_hits) if secret_hits else "no secret-like patterns")
        return {
            "temp_root_removed_after_run": True,
            "git_status_line_count": len(status_lines),
            "git_staged_file_count": len(status_lines),
            "git_tracked_file_count": len(tracked_files),
            "git_post_commit_status_line_count": len(post_status_lines),
            "git_branch": branch_name,
            "git_commit_created": commit_code == 0 and rev_code == 0,
            "git_commit_sha": commit_sha,
            "git_remote_output": remote_output,
            "git_post_commit_remote_output": post_remote_output,
            "staging_location_policy": "system_temp_outside_private_workspace",
            "staging_isolated_from_private_workspace": staging_isolated,
        }


def build_payload(root: Path) -> dict[str, Any]:
    project_root = root.resolve()
    source = candidate_source(project_root)
    checks: list[Check] = []
    root_type = "public_candidate" if is_public_candidate_root(project_root) else "workspace"
    rel_source = "." if root_type == "public_candidate" else PUBLIC_CANDIDATE
    required = [
        ".gitattributes",
        "README.md",
        "LICENSE",
        "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
        "architecture_diagram.md",
        "prototype/agentops_control_tower.py",
        "scripts/validate_submission_packet.py",
        "scripts/build_video_dry_run.py",
        "reports/latest_public_repo_publish_brief.json",
        "reports/latest_public_launch_snapshot.json",
        "reports/latest_submission_url_validation.json",
        "submission/USER_APPROVAL_GATES.md",
    ]
    add_check(checks, "candidate source exists", source.exists(), rel_source)
    missing_required: list[str] = []
    if source.exists():
        missing_required = [item for item in required if not (source / item).exists()]
        add_check(checks, "candidate required files", not missing_required, "missing: " + ", ".join(missing_required) if missing_required else "all required files present")
        top_level = {item.name for item in source.iterdir()}
        unexpected_top_level = sorted(top_level - EXPECTED_TOP_LEVEL)
        add_check(checks, "candidate top-level allowlist", not unexpected_top_level, ", ".join(unexpected_top_level) if unexpected_top_level else "top-level entries expected")
        add_check(checks, "candidate has no git directory", not (source / ".git").exists(), ".git absent")
        add_check(checks, "candidate has no release directory", not (source / "release").exists(), "release absent")
        add_check(checks, "approved URL writeback absent", not (source / "submission/approved_public_urls.json").exists(), "approved_public_urls.json absent")

        publish = read_json(source / "reports/latest_public_repo_publish_brief.json")
        snapshot = read_json(source / "reports/latest_public_launch_snapshot.json")
        urls = read_json(source / "reports/latest_submission_url_validation.json")
        go_no_go = read_json(source / "reports/latest_final_go_no_go.json")
        add_check(checks, "approval phrase stable", publish.get("approval_phrase") == APPROVAL_PHRASE, str(publish.get("approval_phrase", "missing")))
        add_check(checks, "snapshot final gate closed", snapshot.get("final_submit_ready") is False, str(snapshot.get("final_submit_ready")))
        add_check(checks, "URL validation final gate closed", urls.get("final_submit_ready") is False, str(urls.get("final_submit_ready")))
        add_check(checks, "Go/No-Go final gate closed", go_no_go.get("final_submit_ready") is False, str(go_no_go.get("final_submit_ready")))
        add_check(checks, "pending repo and video URLs", set(urls.get("pending_urls", [])) == {"repository_url", "demo_video_url"}, ", ".join(urls.get("pending_urls", [])))
        rehearsal = git_rehearsal(source, project_root, checks)
    else:
        rehearsal = {
            "temp_root_removed_after_run": True,
            "git_status_line_count": 0,
            "git_staged_file_count": 0,
            "git_tracked_file_count": 0,
            "git_post_commit_status_line_count": 0,
            "git_branch": "not_run",
            "git_commit_created": False,
            "git_commit_sha": "",
            "git_remote_output": "not_run",
            "git_post_commit_remote_output": "not_run",
            "staging_location_policy": "not_run",
            "staging_isolated_from_private_workspace": False,
        }

    failed = [check for check in checks if not check.passed]
    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not failed else "needs_more_evidence",
        "root_type": root_type,
        "candidate_path": rel_source,
        "candidate_file_count": file_count(source) if source.exists() else 0,
        "approval_phrase": APPROVAL_PHRASE,
        "final_submit_ready": False,
        "approved_public_urls_exists": (source / "submission/approved_public_urls.json").exists() if source.exists() else False,
        "dry_run_actions": [
            "copy public candidate to an isolated temporary staging folder outside the private workspace",
            "run git init -b main without remote",
            "configure a temporary local git identity",
            "run git add -A",
            "run a local git commit rehearsal",
            "inspect git status --short",
            "scan temporary copy for internal paths and secret-like strings",
        ],
        "rehearsal": rehearsal,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "next_required_external_approval": "public_github_repository",
    }
    return payload


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Public Repo Dry Run",
        "",
        f"Status: {payload['status']}",
        f"Candidate: `{payload['candidate_path']}`",
        f"Candidate files: {payload['candidate_file_count']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Approved public URLs file exists: {str(payload['approved_public_urls_exists']).lower()}",
        f"Git staged file count: {payload['rehearsal']['git_status_line_count']}",
        f"Git tracked file count after commit: {payload['rehearsal']['git_tracked_file_count']}",
        f"Git branch: {payload['rehearsal']['git_branch']}",
        f"Git commit created: {str(payload['rehearsal']['git_commit_created']).lower()}",
        f"Staging location policy: {payload['rehearsal']['staging_location_policy']}",
        f"Staging isolated from private workspace: {str(payload['rehearsal']['staging_isolated_from_private_workspace']).lower()}",
        "",
        "## Dry Run Actions",
        "",
    ]
    for item in payload["dry_run_actions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        lines.append(f"- {check['status']}: {check['name']} - {check['detail']}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    check_rows = "\n".join(
        "<tr>"
        f"<td>{esc(check['name'])}</td>"
        f"<td class=\"{'ready' if check['status'] == 'pass' else 'fail'}\">{esc(check['status'])}</td>"
        f"<td>{esc(check['detail'])}</td>"
        "</tr>"
        for check in payload["checks"]
    )
    actions = "\n".join(f"<li>{esc(item)}</li>" for item in payload["dry_run_actions"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Repo Dry Run</title>
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
    .fail {{ color: #a33a00; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Public Repo Dry Run</h1>
    <p>Local-only rehearsal for publishing the clean Agentic Incident Command Center candidate.</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <table>
        <tbody>
          <tr><th>Status</th><td class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</td></tr>
          <tr><th>Candidate</th><td><code>{esc(payload['candidate_path'])}</code></td></tr>
          <tr><th>Candidate file count</th><td>{esc(payload['candidate_file_count'])}</td></tr>
          <tr><th>Git branch</th><td>{esc(payload['rehearsal']['git_branch'])}</td></tr>
          <tr><th>Git staged file count</th><td>{esc(payload['rehearsal']['git_status_line_count'])}</td></tr>
          <tr><th>Git tracked file count</th><td>{esc(payload['rehearsal']['git_tracked_file_count'])}</td></tr>
          <tr><th>Git commit created</th><td>{esc(payload['rehearsal']['git_commit_created'])}</td></tr>
          <tr><th>Post-commit status lines</th><td>{esc(payload['rehearsal']['git_post_commit_status_line_count'])}</td></tr>
          <tr><th>Staging location policy</th><td>{esc(payload['rehearsal']['staging_location_policy'])}</td></tr>
          <tr><th>Staging isolated</th><td>{esc(payload['rehearsal']['staging_isolated_from_private_workspace'])}</td></tr>
          <tr><th>Final submit ready</th><td>{esc(payload['final_submit_ready'])}</td></tr>
          <tr><th>Approved public URLs</th><td>{esc(payload['approved_public_urls_exists'])}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Dry Run Actions</h2>
      <ul>{actions}</ul>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{check_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Boundary</h2>
      <p>{esc(payload['boundary'])}</p>
    </section>
  </main>
</body>
</html>
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(root: Path) -> dict[str, Any]:
    payload = build_payload(root.resolve())
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_public_repo_dry_run.json", payload)
    (reports / "latest_public_repo_dry_run.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_public_repo_dry_run.html").write_text(render_html(payload), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local-only public repository dry run report.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    payload = build(Path(args.root))
    print(json.dumps({
        "status": payload["status"],
        "failed_count": payload["failed_count"],
        "candidate_file_count": payload["candidate_file_count"],
        "git_status_line_count": payload["rehearsal"]["git_status_line_count"],
        "git_branch": payload["rehearsal"]["git_branch"],
        "git_commit_created": payload["rehearsal"]["git_commit_created"],
        "git_tracked_file_count": payload["rehearsal"]["git_tracked_file_count"],
        "staging_location_policy": payload["rehearsal"]["staging_location_policy"],
        "staging_isolated_from_private_workspace": payload["rehearsal"]["staging_isolated_from_private_workspace"],
        "html": "reports/latest_public_repo_dry_run.html",
        "markdown": "reports/latest_public_repo_dry_run.md",
        "json": "reports/latest_public_repo_dry_run.json",
    }, ensure_ascii=False, indent=2))
    return 0 if payload["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
