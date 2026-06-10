from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_NAME = "agentops-control-tower"
PUBLIC_CANDIDATE = "public_repo_candidate/agentops-control-tower"
NAMESPACE_CHECK_COMMAND = "gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url,isPrivate"


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def evidence(root: Path) -> list[dict[str, Any]]:
    if is_public_candidate_root(root):
        items = [
            "README.md",
            "LICENSE",
            "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
            "reports/latest_external_approval_packet.html",
            "reports/latest_submission_url_apply_plan.html",
            "reports/latest_public_artifact_url_readback.html",
            "reports/latest_video_readiness.html",
            "reports/latest_devpost_final_copy.md",
            "reports/latest_final_go_no_go.html",
            "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
        ]
    else:
        items = [
            PUBLIC_CANDIDATE + "/README.md",
            PUBLIC_CANDIDATE + "/LICENSE",
            PUBLIC_CANDIDATE + "/PUBLIC_REPO_CANDIDATE_MANIFEST.md",
            "reports/latest_public_repo_dry_run.html",
            PUBLIC_CANDIDATE + "/reports/latest_external_approval_packet.html",
            PUBLIC_CANDIDATE + "/reports/latest_submission_url_apply_plan.html",
            "reports/latest_public_artifact_url_readback.html",
            "release/agentops-control-tower-public-candidate.zip",
            "reports/latest_release_zip_smoke_test.html",
            "reports/latest_submission_validation.html",
        ]
    return [{"path": item, "exists": exists(root, item)} for item in items]


def command_steps(root: Path) -> list[dict[str, str]]:
    candidate_root = is_public_candidate_root(root)
    if candidate_root:
        review_command = "python scripts\\publish_public_repo_after_approval.py"
        execute_command = (
            "python scripts\\publish_public_repo_after_approval.py "
            "--execute "
            "--approval-phrase \"Approve public GitHub publication for the clean agentops-control-tower candidate.\" "
            "--repo-name agentops-control-tower "
            "--git-user-name \"<approved-public-git-name>\" "
            "--git-user-email \"<approved-public-git-email>\""
        )
    else:
        review_command = "python scripts\\publish_public_repo_after_approval.py"
        execute_command = (
            "python scripts\\publish_public_repo_after_approval.py "
            "--execute "
            "--approval-phrase \"Approve public GitHub publication for the clean agentops-control-tower candidate.\" "
            "--repo-name agentops-control-tower "
            "--git-user-name \"<approved-public-git-name>\" "
            "--git-user-email \"<approved-public-git-email>\""
        )
    return [
        {
            "name": "Run guarded publication rehearsal",
            "command": review_command,
            "purpose": "Copy the clean candidate into isolated TEMP audit/publish stages, run local validation, scan the publish stage, and create a local commit with no remote.",
        },
        {
            "name": "Run public repository publication preflight",
            "command": (
                "python scripts\\verify_public_repo_publication_gate.py "
                "--approval-phrase \"Approve public GitHub publication for the clean agentops-control-tower candidate.\" "
                "--source-folder-reviewed --isolated-staging-confirmed --secret-scan-confirmed "
                "--public-visibility-confirmed --public-git-identity-confirmed "
                "--git-user-name \"<approved-public-git-name>\" "
                "--git-user-email \"<approved-public-git-email>\""
            ),
            "purpose": "Confirm the exact approval phrase, source-folder review, staging policy, scan status, public visibility, and public git identity before any public repository creation.",
        },
        {
            "name": "Check public repository namespace",
            "command": NAMESPACE_CHECK_COMMAND,
            "purpose": "Read the target GitHub namespace immediately before execution; stop if the repo name already resolves to an existing public or private repository.",
        },
        {
            "name": "Execute guarded public repo publication after approval",
            "command": execute_command,
            "purpose": "Create and push the public GitHub repository only after the exact approval phrase and public git identity are supplied.",
        },
        {
            "name": "Read back public repo",
            "command": "gh repo view <owner>/agentops-control-tower --json nameWithOwner,visibility,url",
            "purpose": "Verify the repo is public and capture the URL for Devpost.",
        },
        {
            "name": "Verify public artifact URLs after repo and video are public",
            "command": "python scripts\\verify_public_artifact_urls.py --repository-url <public-repo-url> --demo-video-url <public-video-url> --live-readback",
            "purpose": "Confirm the public GitHub repository and public demo video URL are reachable before local approved URL writeback.",
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
    validation = read_json(root / "reports/latest_submission_validation.json")
    approval = read_json(root / "reports/latest_external_approval_packet.json")
    smoke = read_json(root / "reports/latest_release_zip_smoke_test.json")
    url_plan = read_json(root / "reports/latest_submission_url_apply_plan.json")
    go_no_go = read_json(root / "reports/latest_final_go_no_go.json")
    rows = evidence(root)
    missing = [item["path"] for item in rows if not item["exists"]]
    ready_requests = set(approval.get("ready_requests", []))
    repo_ready = "public_github_repository" in ready_requests
    candidate_root = is_public_candidate_root(root)
    if candidate_root:
        local_ready = (
            not missing
            and approval.get("status") == "ready_for_user_review"
            and url_plan.get("status") in {"waiting_for_external_urls", "ready_to_submit_after_user_approval"}
            and go_no_go.get("local_ready", True) is True
        )
    else:
        local_ready = not missing and (
            validation.get("overall_status") in {"ready_for_user_review", "needs_more_evidence"}
            and smoke.get("status") in {"pass", "fail"}
        )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not missing and local_ready else "needs_more_evidence",
        "repo_name": REPO_NAME,
        "root_type": "public_candidate" if candidate_root else "workspace",
        "candidate_path": "." if candidate_root else PUBLIC_CANDIDATE,
        "local_ready": local_ready,
        "public_repo_approval_ready": repo_ready,
        "missing_evidence": missing,
        "evidence": rows,
        "commands": command_steps(root),
        "boundary": "This command plan is advisory only. It does not create a repo, push commits, publish files, write URLs, upload videos, or submit Devpost.",
        "approval_required": "Explicit user approval is required before creating or pushing a public repository.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Public Repository Publication Command Plan",
        "",
        f"Status: {payload['status']}",
        f"Candidate: {payload['candidate_path']}",
        "",
        "## Boundary",
        "",
        payload["boundary"],
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
  <title>Public Repository Publication Command Plan</title>
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
    <h1>Public Repository Publication Command Plan</h1>
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
    write_json(reports / "latest_publication_command_plan.json", payload)
    (reports / "latest_publication_command_plan.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_publication_command_plan.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "repo_name": payload["repo_name"],
        "html": "reports/latest_publication_command_plan.html",
        "markdown": "reports/latest_publication_command_plan.md",
        "json": "reports/latest_publication_command_plan.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a non-executing publication command plan for the public repo gate.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
