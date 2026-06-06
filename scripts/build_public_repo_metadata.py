from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_NAME = "agentops-control-tower"
DESCRIPTION = "Splunk-ready safety and incident intelligence for autonomous AI agent operations."
LICENSE = "Apache-2.0"
DEFAULT_BRANCH = "main"
TOPICS = [
    "splunk",
    "agentops",
    "ai-agents",
    "observability",
    "mcp",
    "safety",
    "incident-response",
    "splunk-mcp",
    "autonomous-agents",
    "hackathon",
]
BOUNDARY = (
    "This metadata packet is local publication setup evidence only. It does not create a repository, "
    "edit GitHub metadata, push commits, publish files, write approved URLs, update Devpost, or submit anything."
)


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def candidate_path(root: Path) -> str:
    if is_public_candidate_root(root):
        return "."
    return "public_repo_candidate/agentops-control-tower"


def candidate_manifest(root: Path) -> str:
    if is_public_candidate_root(root):
        return "PUBLIC_REPO_CANDIDATE_MANIFEST.md"
    return "public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md"


def evidence(root: Path) -> list[dict[str, Any]]:
    paths = [
        candidate_manifest(root),
        "README.md" if is_public_candidate_root(root) else "public_repo_candidate/agentops-control-tower/README.md",
        "LICENSE" if is_public_candidate_root(root) else "public_repo_candidate/agentops-control-tower/LICENSE",
        "reports/latest_public_repo_publish_brief.html",
        "reports/latest_public_repo_dry_run.html",
        "reports/latest_public_launch_snapshot.html",
        "reports/latest_release_integrity_manifest.html",
        "reports/latest_release_zip_smoke_test.html" if not is_public_candidate_root(root) else "reports/latest_release_integrity_manifest.html",
    ]
    return [{"path": path, "exists": exists(root, path)} for path in paths]


def gh_create_command() -> str:
    return (
        "gh repo create agentops-control-tower --public --source . --remote origin "
        f"--description \"{DESCRIPTION}\""
    )


def gh_topic_command(owner: str = "<owner>") -> str:
    topics = " ".join(f"--add-topic {topic}" for topic in TOPICS)
    return f"gh repo edit {owner}/{REPO_NAME} {topics}"


def readback_command(owner: str = "<owner>") -> str:
    return (
        f"gh repo view {owner}/{REPO_NAME} "
        "--json nameWithOwner,visibility,url,description,defaultBranchRef,licenseInfo,repositoryTopics,isPrivate"
    )


def build_payload(root: Path) -> dict[str, Any]:
    publish = read_json(root / "reports/latest_public_repo_publish_brief.json")
    launch = read_json(root / "reports/latest_public_launch_snapshot.json")
    validation = read_json(root / "reports/latest_submission_validation.json")
    rows = evidence(root)
    missing = [row["path"] for row in rows if not row["exists"]]
    approval_phrase = publish.get(
        "approval_phrase",
        "Approve public GitHub publication for the clean agentops-control-tower candidate.",
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not missing else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "repo_name": REPO_NAME,
        "visibility_after_approval": "public",
        "description": DESCRIPTION,
        "license": LICENSE,
        "default_branch": DEFAULT_BRANCH,
        "topics": TOPICS,
        "candidate_path": candidate_path(root),
        "approval_phrase": approval_phrase,
        "public_repo_approval_ready": bool(publish.get("public_repo_approval_ready", False)),
        "final_submit_ready": bool(validation.get("final_submit_ready", False) or launch.get("final_submit_ready", False)),
        "approved_public_urls_exists": bool(validation.get("approved_public_urls_exists", False)),
        "commands_after_approval": [
            {
                "name": "create_public_repository",
                "command": gh_create_command(),
                "purpose": "Create a public GitHub repository from isolated TEMP staging after explicit approval.",
            },
            {
                "name": "apply_topics",
                "command": gh_topic_command(),
                "purpose": "Apply discoverability topics after the repository exists.",
            },
            {
                "name": "readback_metadata",
                "command": readback_command(),
                "purpose": "Read back visibility, URL, description, default branch, license, and topics.",
            },
        ],
        "expected_readback": {
            "visibility": "PUBLIC",
            "isPrivate": False,
            "description": DESCRIPTION,
            "defaultBranchRef": DEFAULT_BRANCH,
            "licenseInfo": LICENSE,
            "topics": TOPICS,
        },
        "evidence": rows,
        "missing_evidence": missing,
        "stop_conditions": [
            "Do not create or edit a GitHub repository without the exact public GitHub approval phrase.",
            "Do not publish from the private workspace root.",
            "Do not publish if public candidate scans, release integrity, or ZIP smoke checks fail.",
            "Do not write approved URLs until public repository and public demo video URLs are both verified.",
            "Do not update Devpost or press submit from this step.",
        ],
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Public Repo Metadata",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Repository name: `{payload['repo_name']}`",
        f"Visibility after approval: {payload['visibility_after_approval']}",
        f"Description: {payload['description']}",
        f"License: {payload['license']}",
        f"Default branch: {payload['default_branch']}",
        f"Candidate path: `{payload['candidate_path']}`",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        "",
        "## Topics",
        "",
    ]
    for topic in payload["topics"]:
        lines.append(f"- `{topic}`")
    lines.extend(["", "## Commands After Approval", ""])
    for item in payload["commands_after_approval"]:
        lines.extend([
            f"### {item['name']}",
            "",
            "```powershell",
            item["command"],
            "```",
            "",
            item["purpose"],
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
    topics = "".join(f"<li><code>{esc(topic)}</code></li>" for topic in payload["topics"])
    commands = "\n".join(
        f"""<tr>
          <td>{esc(item['name'])}</td>
          <td><pre>{esc(item['command'])}</pre></td>
          <td>{esc(item['purpose'])}</td>
        </tr>"""
        for item in payload["commands_after_approval"]
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
    stops = "".join(f"<li>{esc(item)}</li>" for item in payload["stop_conditions"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Repo Metadata</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; width: 190px; }}
    code, pre {{ background: #edf3f6; border-radius: 4px; }}
    code {{ padding: 2px 5px; }}
    pre {{ margin: 0; padding: 8px; white-space: pre-wrap; overflow-wrap: anywhere; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Public Repo Metadata</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Repository</h2>
      <table>
        <tbody>
          <tr><th>Name</th><td><code>{esc(payload['repo_name'])}</code></td></tr>
          <tr><th>Visibility</th><td>{esc(payload['visibility_after_approval'])}</td></tr>
          <tr><th>Description</th><td>{esc(payload['description'])}</td></tr>
          <tr><th>License</th><td>{esc(payload['license'])}</td></tr>
          <tr><th>Default branch</th><td>{esc(payload['default_branch'])}</td></tr>
          <tr><th>Candidate path</th><td><code>{esc(payload['candidate_path'])}</code></td></tr>
          <tr><th>Final submit ready</th><td class="pending">{esc(payload['final_submit_ready'])}</td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Topics</h2>
      <ul>{topics}</ul>
    </section>
    <section>
      <h2>Commands After Approval</h2>
      <table>
        <thead><tr><th>Name</th><th>Command</th><th>Purpose</th></tr></thead>
        <tbody>{commands}</tbody>
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
    submission = root / "submission"
    reports.mkdir(parents=True, exist_ok=True)
    submission.mkdir(parents=True, exist_ok=True)
    markdown = render_markdown(payload)
    write_json(reports / "latest_public_repo_metadata.json", payload)
    (reports / "latest_public_repo_metadata.md").write_text(markdown, encoding="utf-8")
    (reports / "latest_public_repo_metadata.html").write_text(render_html(payload), encoding="utf-8")
    (submission / "PUBLIC_REPO_METADATA.md").write_text(markdown, encoding="utf-8")
    return {
        "status": payload["status"],
        "repo_name": payload["repo_name"],
        "html": "reports/latest_public_repo_metadata.html",
        "markdown": "reports/latest_public_repo_metadata.md",
        "json": "reports/latest_public_repo_metadata.json",
        "submission_markdown": "submission/PUBLIC_REPO_METADATA.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local public GitHub repository metadata packet.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
