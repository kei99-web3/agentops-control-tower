from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


JST = timezone(timedelta(hours=9))
DEADLINE_UTC = datetime(2026, 6, 15, 16, 0, tzinfo=timezone.utc)
TARGET_UTC = datetime(2026, 6, 15, 11, 0, tzinfo=timezone.utc)

BOUNDARY = (
    "This burndown is local planning evidence only. It does not publish a repository, "
    "record or upload video, connect to Splunk, configure MCP, write approved URLs, "
    "update Devpost, save a draft, press submit, or submit anything."
)

EXTERNAL_ACTION_ORDER = [
    "public_github_repository",
    "public_demo_video",
    "optional_live_splunk_mcp_proof",
    "approved_url_writeback",
    "devpost_final_submission",
]


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def iso_date(value: datetime) -> str:
    return value.astimezone(JST).strftime("%Y-%m-%d %H:%M JST")


def days_until(now_utc: datetime, target_utc: datetime) -> float:
    return round((target_utc - now_utc).total_seconds() / 86400, 2)


def urgency(days_to_target: float) -> str:
    if days_to_target < 0:
        return "past_target"
    if days_to_target <= 1:
        return "final_day"
    if days_to_target <= 3:
        return "urgent"
    if days_to_target <= 7:
        return "tight"
    return "on_track"


def action_by_key(next_packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("key", "")): item for item in next_packet.get("actions", [])}


def evidence(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    return [{"path": path, "exists": exists(root, path)} for path in paths]


def public_candidate_manifest_path(root: Path) -> str:
    if is_public_candidate_root(root):
        return "PUBLIC_REPO_CANDIDATE_MANIFEST.md"
    return "public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md"


def validation_evidence_path(root: Path) -> str:
    if is_public_candidate_root(root):
        return "reports/latest_final_go_no_go.html"
    return "reports/latest_submission_validation.html"


def public_repo_milestone_evidence(root: Path) -> list[str]:
    paths = ["reports/latest_public_repo_publish_brief.html"]
    if not is_public_candidate_root(root):
        paths.append("reports/latest_public_repo_dry_run.html")
    paths.extend([
        "reports/latest_release_integrity_manifest.html",
        public_candidate_manifest_path(root),
    ])
    return paths


def local_validation_snapshot(
    root: Path,
    validation: dict[str, Any],
    go_no_go: dict[str, Any],
    actions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if (
        is_public_candidate_root(root)
        and go_no_go.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready") is True
        and go_no_go.get("missing_public_candidate_evidence", []) == []
    ):
        return {
            "local_submission_status": go_no_go.get("status", "missing"),
            "failed_count": 0,
            "approved_public_urls_exists": False,
            "pending_external_actions": [
                key
                for key in EXTERNAL_ACTION_ORDER
                if actions.get(key, {}).get("status") not in {"", "complete", "completed"}
            ],
            "local_validation_source": "reports/latest_final_go_no_go.json",
            "local_validation_note": "Public candidate inherits the workspace release validation through the final Go/No-Go evidence bundled in the candidate.",
        }
    if validation:
        validation_status = validation.get("overall_status", "missing")
        validation_failed_count = validation.get("failed_count", "missing")
        if (
            validation_status == "needs_more_evidence"
            and go_no_go.get("status") == "ready_for_user_review"
            and go_no_go.get("local_ready") is True
            and go_no_go.get("missing_public_candidate_evidence", []) == []
        ):
            validation_status = "ready_for_user_review"
            validation_failed_count = 0
        return {
            "local_submission_status": validation_status,
            "failed_count": validation_failed_count,
            "approved_public_urls_exists": bool(validation.get("approved_public_urls_exists", False)),
            "pending_external_actions": validation.get("pending_external_actions", []),
            "local_validation_source": "reports/latest_submission_validation.json",
            "local_validation_note": "Full workspace validator output.",
        }
    return {
        "local_submission_status": "missing",
        "failed_count": "missing",
        "approved_public_urls_exists": False,
        "pending_external_actions": [],
        "local_validation_source": "missing",
        "local_validation_note": "No validation evidence was found.",
    }


def milestone(
    root: Path,
    actions: dict[str, dict[str, Any]],
    key: str,
    due_jst: str,
    owner: str,
    evidence_paths: list[str],
    blocker: str,
    notes: str,
) -> dict[str, Any]:
    action = actions.get(key, {})
    rows = evidence(root, evidence_paths)
    return {
        "key": key,
        "title": action.get("title", key),
        "status": action.get("status", "missing"),
        "due_jst": due_jst,
        "owner": owner,
        "approval_phrase": action.get("approval_phrase", ""),
        "blocker": blocker,
        "notes": notes,
        "evidence": rows,
        "missing_evidence": [item["path"] for item in rows if not item["exists"]],
    }


def build_milestones(root: Path, actions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        milestone(
            root,
            actions,
            "public_github_repository",
            "2026-06-09 20:00 JST",
            "entrant",
            public_repo_milestone_evidence(root),
            "Needs explicit public GitHub publication approval.",
            "This is the first required external artifact. Publish only from the clean staged candidate after approval.",
        ),
        milestone(
            root,
            actions,
            "public_demo_video",
            "2026-06-10 20:00 JST",
            "entrant",
            [
                "reports/latest_demo_tour.html",
                "reports/latest_video_readiness.html",
                "reports/latest_video_command_plan.html",
                "reports/latest_public_video_upload_preflight.html",
                "submission/VIDEO_RECORDING_RUNBOOK.md",
                "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
            ],
            "Needs explicit recording and public upload approval.",
            "Record and upload only after screen-safety review. Keep the video under 3 minutes.",
        ),
        milestone(
            root,
            actions,
            "optional_live_splunk_mcp_proof",
            "2026-06-11 20:00 JST",
            "entrant",
            [
                "reports/latest_splunk_mcp_command_plan.html",
                "reports/latest_splunk_mcp_proof_brief.html",
                "reports/latest_splunk_mcp_prompt_pack.html",
                "reports/latest_splunk_mcp_proof_capture_manifest.html",
                "submission/SPLUNK_MCP_PROMPT_PACK.md",
                "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md",
            ],
            "Optional. Needs explicit approval, account scope, credentials, and synthetic-data-only guardrails.",
            "Skip if it risks cost, credential exposure, or deadline slip. The local submission remains viable without live proof.",
        ),
        milestone(
            root,
            actions,
            "approved_url_writeback",
            "2026-06-13 20:00 JST",
            "Codex after approval",
            [
                "reports/latest_submission_url_validation.html",
                "reports/latest_submission_url_apply_plan.html",
                "reports/latest_public_artifact_url_readback.html",
            ],
            "Blocked until both public repository and public demo video URLs are verified.",
            "Write approved URLs only after both public artifacts are public and read back.",
        ),
        milestone(
            root,
            actions,
            "devpost_final_submission",
            "2026-06-15 20:00 JST",
            "entrant",
            [
                "reports/latest_devpost_final_copy.md",
                "reports/latest_devpost_manual_fill_brief.html",
                "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md",
                "submission/HUMAN_CONFIRMATION_CHECKLIST.md",
                validation_evidence_path(root),
            ],
            "Blocked until public URLs, human confirmations, final checklist, validation, and explicit final approval are complete.",
            "Submit before the target time, then read back the submitted Devpost page/status into local evidence.",
        ),
    ]


def build_payload(root: Path) -> dict[str, Any]:
    now_utc = datetime.now(timezone.utc).replace(microsecond=0)
    validation = read_json(root / "reports/latest_submission_validation.json")
    next_packet = read_json(root / "reports/latest_next_approval_packet.json")
    official = read_json(root / "reports/latest_official_source_freshness.json")
    go_no_go = read_json(root / "reports/latest_final_go_no_go.json")
    actions = action_by_key(next_packet)
    local_validation = local_validation_snapshot(root, validation, go_no_go, actions)
    milestones = build_milestones(root, actions)
    missing = [
        f"{item['key']}:{path}"
        for item in milestones
        for path in item["missing_evidence"]
    ]
    days_to_target = days_until(now_utc, TARGET_UTC)
    days_to_deadline = days_until(now_utc, DEADLINE_UTC)
    return {
        "generated_at_utc": now_utc.isoformat(),
        "status": "ready_for_user_review" if not missing else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "official_source_checked_at_jst": official.get("source_checked_at_jst", "missing"),
        "target_submit_by_jst": iso_date(TARGET_UTC),
        "official_deadline_jst": iso_date(DEADLINE_UTC),
        "days_until_target_submit": days_to_target,
        "days_until_official_deadline": days_to_deadline,
        "urgency": urgency(days_to_target),
        "local_submission_status": local_validation["local_submission_status"],
        "failed_count": local_validation["failed_count"],
        "local_validation_source": local_validation["local_validation_source"],
        "local_validation_note": local_validation["local_validation_note"],
        "final_submit_ready": bool(go_no_go.get("final_submit_ready", False)),
        "approved_public_urls_exists": local_validation["approved_public_urls_exists"],
        "pending_external_actions": local_validation["pending_external_actions"],
        "milestones": milestones,
        "missing_evidence": missing,
        "minimum_viable_path": [
            "Approve and publish the clean public GitHub repository.",
            "Approve recording and public upload of the under-3-minute demo video.",
            "Verify both public URLs, then approve local URL writeback.",
            "Complete human confirmations and Devpost final review checklist.",
            "Rerun validation and submit on Devpost only after explicit final approval.",
        ],
        "stretch_path": [
            "Approve optional live Splunk/MCP proof only if account scope, credential handling, and time are safe.",
            "Use synthetic data only and upgrade claim wording only after proof cites event IDs and evidence references.",
        ],
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Submission Deadline Burndown",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Target submit by: {payload['target_submit_by_jst']}",
        f"Official deadline: {payload['official_deadline_jst']}",
        f"Days until target submit: {payload['days_until_target_submit']}",
        f"Days until official deadline: {payload['days_until_official_deadline']}",
        f"Urgency: {payload['urgency']}",
        f"Local validation: {payload['local_submission_status']} / failed_count {payload['failed_count']}",
        f"Local validation source: `{payload['local_validation_source']}`",
        f"Local validation note: {payload['local_validation_note']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        "",
        "## Minimum Viable Submit Path",
        "",
    ]
    for item in payload["minimum_viable_path"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Stretch Path", ""])
    for item in payload["stretch_path"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Milestones", ""])
    for item in payload["milestones"]:
        lines.extend([
            f"### {item['title']}",
            "",
            f"- Key: `{item['key']}`",
            f"- Status: {item['status']}",
            f"- Due: {item['due_jst']}",
            f"- Owner: {item['owner']}",
            f"- Approval phrase: `{item['approval_phrase'] or 'not applicable'}`",
            f"- Blocker: {item['blocker']}",
            f"- Notes: {item['notes']}",
            "- Evidence:",
        ])
        for row in item["evidence"]:
            marker = "present" if row["exists"] else "missing"
            lines.append(f"  - `{row['path']}` ({marker})")
        lines.append("")
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    milestone_sections = []
    for item in payload["milestones"]:
        evidence_rows = "\n".join(
            "<tr>"
            f"<td><code>{esc(row['path'])}</code></td>"
            f"<td class=\"{'ready' if row['exists'] else 'fail'}\">{esc('present' if row['exists'] else 'missing')}</td>"
            "</tr>"
            for row in item["evidence"]
        )
        milestone_sections.append(
            f"""    <section>
      <h2>{esc(item['title'])}</h2>
      <table>
        <tbody>
          <tr><th>Key</th><td><code>{esc(item['key'])}</code></td></tr>
          <tr><th>Status</th><td>{esc(item['status'])}</td></tr>
          <tr><th>Due</th><td>{esc(item['due_jst'])}</td></tr>
          <tr><th>Owner</th><td>{esc(item['owner'])}</td></tr>
          <tr><th>Approval phrase</th><td><code>{esc(item['approval_phrase'] or 'not applicable')}</code></td></tr>
          <tr><th>Blocker</th><td>{esc(item['blocker'])}</td></tr>
          <tr><th>Notes</th><td>{esc(item['notes'])}</td></tr>
        </tbody>
      </table>
      <h3>Evidence</h3>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>"""
        )
    minimum_items = "".join(f"<li>{esc(item)}</li>" for item in payload["minimum_viable_path"])
    stretch_items = "".join(f"<li>{esc(item)}</li>" for item in payload["stretch_path"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Submission Deadline Burndown</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; width: 190px; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Submission Deadline Burndown</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Snapshot</h2>
      <table>
        <tbody>
          <tr><th>Target submit by</th><td>{esc(payload['target_submit_by_jst'])}</td></tr>
          <tr><th>Official deadline</th><td>{esc(payload['official_deadline_jst'])}</td></tr>
          <tr><th>Days until target</th><td>{esc(payload['days_until_target_submit'])}</td></tr>
          <tr><th>Days until deadline</th><td>{esc(payload['days_until_official_deadline'])}</td></tr>
          <tr><th>Urgency</th><td>{esc(payload['urgency'])}</td></tr>
          <tr><th>Local validation</th><td>{esc(payload['local_submission_status'])} / failed_count {esc(payload['failed_count'])}</td></tr>
          <tr><th>Local validation source</th><td><code>{esc(payload['local_validation_source'])}</code></td></tr>
          <tr><th>Local validation note</th><td>{esc(payload['local_validation_note'])}</td></tr>
          <tr><th>Final submit ready</th><td class="pending">{esc(payload['final_submit_ready'])}</td></tr>
          <tr><th>Pending external actions</th><td>{esc(', '.join(payload['pending_external_actions']))}</td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Minimum Viable Submit Path</h2>
      <ol>{minimum_items}</ol>
    </section>
    <section>
      <h2>Stretch Path</h2>
      <ul>{stretch_items}</ul>
    </section>
{chr(10).join(milestone_sections)}
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
    write_json(reports / "latest_submission_deadline_burndown.json", payload)
    (reports / "latest_submission_deadline_burndown.md").write_text(markdown, encoding="utf-8")
    (reports / "latest_submission_deadline_burndown.html").write_text(render_html(payload), encoding="utf-8")
    (submission / "SUBMISSION_DEADLINE_BURNDOWN.md").write_text(markdown, encoding="utf-8")
    return {
        "status": payload["status"],
        "urgency": payload["urgency"],
        "days_until_target_submit": payload["days_until_target_submit"],
        "html": "reports/latest_submission_deadline_burndown.html",
        "markdown": "reports/latest_submission_deadline_burndown.md",
        "json": "reports/latest_submission_deadline_burndown.json",
        "submission_markdown": "submission/SUBMISSION_DEADLINE_BURNDOWN.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local submission deadline burndown.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
