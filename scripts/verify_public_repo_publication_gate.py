from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APPROVAL_PHRASE = "Approve public GitHub publication for the clean agentops-control-tower candidate."
BOUNDARY = (
    "This public repository publication gate is a local preflight only. It does not "
    "create a repository, push commits, publish files, write approved URLs, upload "
    "video, update Devpost, press submit, or submit anything."
)
REPORT_STEM = "latest_public_repo_publication_preflight"
EVIDENCE_NOTE_TARGET = "submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md"
PUBLIC_CANDIDATE = "public_repo_candidate/agentops-control-tower"
REPO_NAME = "agentops-control-tower"
PLACEHOLDER_GIT_IDENTITY_TOKENS = {
    "<approved-public-git-name>",
    "<approved-public-git-email>",
    "approved-public-git-name",
    "approved-public-git-email",
}


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def required_evidence(root: Path) -> list[str]:
    if is_public_candidate_root(root):
        return [
            ".gitattributes",
            "README.md",
            "LICENSE",
            "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
            "reports/latest_publication_command_plan.html",
            "reports/latest_publication_command_plan.json",
            "reports/latest_public_repo_metadata.html",
            "reports/latest_public_repo_metadata.json",
            "reports/latest_public_repo_publish_brief.html",
            "reports/latest_public_repo_publish_brief.json",
            "reports/latest_submission_url_validation.html",
            "reports/latest_submission_url_validation.json",
            "reports/latest_public_artifact_url_readback.html",
            "reports/latest_public_artifact_url_readback.json",
            "reports/latest_final_go_no_go.html",
            "reports/latest_final_go_no_go.json",
            "scripts/publish_public_repo_after_approval.py",
            "submission/PUBLIC_REPO_METADATA.md",
            "submission/USER_APPROVAL_GATES.md",
        ]
    return [
        f"{PUBLIC_CANDIDATE}/.gitattributes",
        f"{PUBLIC_CANDIDATE}/README.md",
        f"{PUBLIC_CANDIDATE}/LICENSE",
        f"{PUBLIC_CANDIDATE}/PUBLIC_REPO_CANDIDATE_MANIFEST.md",
        "reports/latest_publication_command_plan.html",
        "reports/latest_publication_command_plan.json",
        "reports/latest_public_repo_metadata.html",
        "reports/latest_public_repo_metadata.json",
        "reports/latest_public_repo_publish_brief.html",
        "reports/latest_public_repo_publish_brief.json",
        "reports/latest_public_repo_dry_run.html",
        "reports/latest_public_repo_dry_run.json",
        "reports/latest_submission_url_validation.html",
        "reports/latest_submission_url_validation.json",
        "reports/latest_public_artifact_url_readback.html",
        "reports/latest_public_artifact_url_readback.json",
        "scripts/publish_public_repo_after_approval.py",
        "submission/PUBLIC_REPO_METADATA.md",
        "submission/USER_APPROVAL_GATES.md",
    ]


def manual_confirmation_flags(args: argparse.Namespace) -> dict[str, bool]:
    return {
        "source_folder_reviewed": bool(args.source_folder_reviewed),
        "isolated_staging_confirmed": bool(args.isolated_staging_confirmed),
        "secret_scan_confirmed": bool(args.secret_scan_confirmed),
        "public_visibility_confirmed": bool(args.public_visibility_confirmed),
        "public_git_identity_confirmed": bool(args.public_git_identity_confirmed),
    }


def is_placeholder_git_identity(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        not normalized
        or normalized in PLACEHOLDER_GIT_IDENTITY_TOKENS
        or normalized.startswith("<")
        or normalized.endswith(">")
        or "approved-public-git-" in normalized
    )


def validate_public_git_identity(name: str, email: str) -> list[str]:
    issues: list[str] = []
    if is_placeholder_git_identity(name):
        issues.append("--git-user-name must be a real public git identity, not a placeholder")
    if is_placeholder_git_identity(email):
        issues.append("--git-user-email must be a real public git email, not a placeholder")
    elif "@" not in email:
        issues.append("--git-user-email must include @")
    return issues


def execute_command(name: str, email: str) -> str:
    safe_name = name or "<approved-public-git-name>"
    safe_email = email or "<approved-public-git-email>"
    return (
        "python scripts\\publish_public_repo_after_approval.py "
        "--execute "
        f"--approval-phrase \"{APPROVAL_PHRASE}\" "
        f"--repo-name {REPO_NAME} "
        f"--git-user-name \"{safe_name}\" "
        f"--git-user-email \"{safe_email}\""
    )


def build_payload(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    publication = read_json(root / "reports/latest_publication_command_plan.json")
    metadata = read_json(root / "reports/latest_public_repo_metadata.json")
    publish = read_json(root / "reports/latest_public_repo_publish_brief.json")
    dry_run = read_json(root / "reports/latest_public_repo_dry_run.json")
    url_validation = read_json(root / "reports/latest_submission_url_validation.json")
    go_no_go = read_json(root / "reports/latest_final_go_no_go.json")

    evidence = [{"path": item, "exists": (root / item).exists()} for item in required_evidence(root)]
    missing = [item["path"] for item in evidence if not item["exists"]]
    public_candidate = is_public_candidate_root(root)
    repo_pending = "repository_url" in set(url_validation.get("pending_urls", []))
    dry_run_ready = (
        public_candidate
        or (
            dry_run.get("status") == "ready_for_user_review"
            and int(dry_run.get("failed_count", 1)) == 0
            and dry_run.get("rehearsal", {}).get("staging_isolated_from_private_workspace") is True
        )
    )
    local_ready = bool(
        not missing
        and publication.get("status") == "ready_for_user_review"
        and metadata.get("status") == "ready_for_user_review"
        and publish.get("status") == "ready_for_user_review"
        and publish.get("public_repo_approval_ready") is True
        and dry_run_ready
        and repo_pending
        and not (root / "submission/approved_public_urls.json").exists()
        and not bool(go_no_go.get("final_submit_ready", False))
    )

    approval_phrase_accepted = args.approval_phrase == APPROVAL_PHRASE
    manual_flags = manual_confirmation_flags(args)
    missing_manual_confirmations = [key for key, value in manual_flags.items() if not value]
    identity_validation_requested = bool(
        args.public_git_identity_confirmed or args.git_user_name or args.git_user_email
    )
    invalid_git_identity = (
        validate_public_git_identity(args.git_user_name, args.git_user_email)
        if identity_validation_requested
        else []
    )
    public_repo_publication_allowed = bool(
        local_ready
        and approval_phrase_accepted
        and not missing_manual_confirmations
        and not invalid_git_identity
    )

    gate_issues: list[str] = []
    if missing:
        gate_issues.append("required public repo publication preflight evidence is missing")
    if publication.get("status") != "ready_for_user_review":
        gate_issues.append("publication command plan must be ready_for_user_review")
    if metadata.get("status") != "ready_for_user_review":
        gate_issues.append("public repo metadata must be ready_for_user_review")
    if publish.get("status") != "ready_for_user_review" or publish.get("public_repo_approval_ready") is not True:
        gate_issues.append("public repo publish brief must be ready and approval-ready")
    if not dry_run_ready:
        gate_issues.append("isolated public repo dry run must pass before publication")
    if not repo_pending:
        gate_issues.append("repository_url must still be pending before publication")
    if (root / "submission/approved_public_urls.json").exists():
        gate_issues.append("approved URL writeback must remain absent before public repo publication")
    if bool(go_no_go.get("final_submit_ready", False)):
        gate_issues.append("final submit must remain blocked until public URLs are verified")
    if args.approval_phrase and not approval_phrase_accepted:
        gate_issues.append("approval phrase must exactly match the public GitHub approval phrase")
    elif not args.approval_phrase:
        gate_issues.append("approval phrase is required before public repository publication")
    if missing_manual_confirmations:
        gate_issues.append("manual source, staging, scan, visibility, and git identity confirmations are required")
    gate_issues.extend(invalid_git_identity)

    if not local_ready:
        gate_status = "needs_more_evidence"
    elif public_repo_publication_allowed:
        gate_status = "ready_for_manual_public_repo_publication"
    elif invalid_git_identity:
        gate_status = "blocked_by_public_git_identity_gate"
    elif not approval_phrase_accepted:
        gate_status = "blocked_by_public_repo_approval_gate"
    elif missing_manual_confirmations:
        gate_status = "blocked_by_publication_safety_gate"
    else:
        gate_status = "blocked_by_public_repo_approval_gate"

    safe_readback = {
        "action_key": "public_github_repository",
        "gate_status": gate_status,
        "public_repo_publication_allowed": public_repo_publication_allowed,
        "approval_phrase_accepted": approval_phrase_accepted,
        "ready_for_publication": public_repo_publication_allowed,
        "repo_name": REPO_NAME,
        "expected_visibility": "PUBLIC",
        "candidate_path": "." if public_candidate else PUBLIC_CANDIDATE,
        "preflight_command": (
            f'python scripts\\verify_public_repo_publication_gate.py --approval-phrase "{APPROVAL_PHRASE}" '
            "--source-folder-reviewed --isolated-staging-confirmed --secret-scan-confirmed "
            "--public-visibility-confirmed --public-git-identity-confirmed "
            "--git-user-name \"<approved-public-git-name>\" --git-user-email \"<approved-public-git-email>\""
        ),
        "execute_command": execute_command(args.git_user_name, args.git_user_email),
        "evidence_note_target": EVIDENCE_NOTE_TARGET,
        "repository_url": "PENDING_USER_APPROVAL_PUBLIC_REPO_URL",
        "external_actions_attempted": False,
        "external_actions_completed": False,
        "forbidden_content": [
            "credentials",
            "tokens",
            "local absolute paths",
            "private workspace material",
            "private logs",
            "customer data",
            "private Devpost/account pages",
        ],
        "copy_policy": (
            "Use this pre-publication safe readback plus the guarded helper safe_readback "
            "after publication. Do not copy stage_root, audit_stage, publish_stage, raw "
            "command output, credentials, tokens, or local absolute paths."
        ),
    }

    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "gate_status": gate_status,
        "root_type": "public_candidate" if public_candidate else "workspace",
        "local_ready": local_ready,
        "public_repo_publication_allowed": public_repo_publication_allowed,
        "approval_phrase_accepted": approval_phrase_accepted,
        "approval_phrase_required": APPROVAL_PHRASE,
        "manual_confirmations": manual_flags,
        "missing_manual_confirmations": missing_manual_confirmations,
        "invalid_git_identity": invalid_git_identity,
        "missing_evidence": missing,
        "gate_issues": gate_issues,
        "evidence": evidence,
        "external_actions_attempted": False,
        "external_actions_completed": False,
        "public_repo_publication_safe_readback": safe_readback,
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    safe = payload["public_repo_publication_safe_readback"]
    lines = [
        "# Public Repo Publication Preflight",
        "",
        f"Status: {payload['status']}",
        f"Gate status: {payload['gate_status']}",
        f"Public repo publication allowed: {str(payload['public_repo_publication_allowed']).lower()}",
        f"Approval phrase accepted: {str(payload['approval_phrase_accepted']).lower()}",
        "",
        "## Safe Readback",
        "",
        f"- Evidence note target: {safe['evidence_note_target']}",
        f"- Candidate path: `{safe['candidate_path']}`",
        f"- Expected visibility: `{safe['expected_visibility']}`",
        f"- Ready for publication: {str(safe['ready_for_publication']).lower()}",
        f"- Preflight command: `{safe['preflight_command']}`",
        f"- Execute command: `{safe['execute_command']}`",
        f"- Copy policy: {safe['copy_policy']}",
        "",
        "## Gate Issues",
        "",
    ]
    if payload["gate_issues"]:
        lines.extend(f"- {item}" for item in payload["gate_issues"])
    else:
        lines.append("- none")
    lines.extend(["", "## Manual Confirmations", ""])
    for key, value in payload["manual_confirmations"].items():
        lines.append(f"- {key}: {str(value).lower()}")
    lines.extend(["", "## Evidence", ""])
    for item in payload["evidence"]:
        lines.append(f"- `{item['path']}` ({'present' if item['exists'] else 'missing'})")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    evidence_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['path'])}</td>"
        f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        "</tr>"
        for item in payload["evidence"]
    )
    issue_rows = "\n".join(f"<li>{esc(item)}</li>" for item in payload["gate_issues"]) or "<li>none</li>"
    confirmations = "\n".join(
        "<tr>"
        f"<td>{esc(key)}</td>"
        f"<td class=\"{'ready' if value else 'pending'}\">{esc(value)}</td>"
        "</tr>"
        for key, value in payload["manual_confirmations"].items()
    )
    safe = payload["public_repo_publication_safe_readback"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Repo Publication Preflight</title>
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
    <h1>Public Repo Publication Preflight</h1>
    <p>Gate status: <span class="{'ready' if payload['public_repo_publication_allowed'] else 'pending'}">{esc(payload['gate_status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <table>
        <tbody>
          <tr><th>Status</th><td>{esc(payload['status'])}</td></tr>
          <tr><th>Public repo publication allowed</th><td>{esc(payload['public_repo_publication_allowed'])}</td></tr>
          <tr><th>Approval phrase accepted</th><td>{esc(payload['approval_phrase_accepted'])}</td></tr>
          <tr><th>Candidate path</th><td><code>{esc(safe['candidate_path'])}</code></td></tr>
          <tr><th>Evidence note target</th><td><code>{esc(safe['evidence_note_target'])}</code></td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Safe Readback</h2>
      <table>
        <tbody>
          <tr><th>Ready for publication</th><td>{esc(safe['ready_for_publication'])}</td></tr>
          <tr><th>Expected visibility</th><td><code>{esc(safe['expected_visibility'])}</code></td></tr>
          <tr><th>Preflight command</th><td><code>{esc(safe['preflight_command'])}</code></td></tr>
          <tr><th>Execute command</th><td><code>{esc(safe['execute_command'])}</code></td></tr>
          <tr><th>Copy policy</th><td>{esc(safe['copy_policy'])}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Gate Issues</h2>
      <ul>{issue_rows}</ul>
    </section>
    <section>
      <h2>Manual Confirmations</h2>
      <table><tbody>{confirmations}</tbody></table>
    </section>
    <section>
      <h2>Evidence</h2>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def write_outputs(root: Path, payload: dict[str, Any]) -> None:
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / f"{REPORT_STEM}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (reports / f"{REPORT_STEM}.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / f"{REPORT_STEM}.html").write_text(render_html(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Local-only public GitHub publication preflight gate.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--approval-phrase", default="")
    parser.add_argument("--source-folder-reviewed", action="store_true")
    parser.add_argument("--isolated-staging-confirmed", action="store_true")
    parser.add_argument("--secret-scan-confirmed", action="store_true")
    parser.add_argument("--public-visibility-confirmed", action="store_true")
    parser.add_argument("--public-git-identity-confirmed", action="store_true")
    parser.add_argument("--git-user-name", default="")
    parser.add_argument("--git-user-email", default="")
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    payload = build_payload(root, args)
    if not args.no_write_report:
        write_outputs(root, payload)
    print(json.dumps({
        "status": payload["status"],
        "gate_status": payload["gate_status"],
        "public_repo_publication_allowed": payload["public_repo_publication_allowed"],
        "approval_phrase_accepted": payload["approval_phrase_accepted"],
        "external_actions_attempted": payload["external_actions_attempted"],
        "html": f"reports/{REPORT_STEM}.html",
        "markdown": f"reports/{REPORT_STEM}.md",
        "json": f"reports/{REPORT_STEM}.json",
    }, ensure_ascii=False, indent=2))
    if args.approval_phrase or any(manual_confirmation_flags(args).values()) or args.git_user_name or args.git_user_email:
        return 0 if payload["public_repo_publication_allowed"] else 2
    return 0 if payload["status"] != "needs_more_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
