from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APPROVAL_PHRASE = "Approve final Devpost submission for Agentic Incident Command Center."
BOUNDARY = (
    "This final submit gate is a local preflight only. It does not log in to Devpost, "
    "save a draft, press submit, update Devpost, publish, upload, write approved URLs, "
    "or mark the submission complete."
)
REPORT_STEM = "latest_devpost_final_submit_preflight"
EVIDENCE_NOTE_TARGET = "submission/post_action_evidence/YYYY-MM-DD_devpost_final_submission_readback.md"


REQUIRED_EVIDENCE = [
    "reports/latest_devpost_final_copy.json",
    "reports/latest_devpost_manual_fill_brief.json",
    "reports/latest_devpost_submit_command_plan.json",
    "reports/latest_submission_url_validation.json",
    "reports/latest_final_go_no_go.json",
    "reports/latest_claim_boundary_validation.json",
    "reports/latest_post_action_evidence_brief.json",
    "submission/DEVPOST_FIELD_MAP.md",
    "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md",
    "submission/HUMAN_CONFIRMATION_CHECKLIST.md",
    "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
    "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md",
]


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def pending_url_fields(final_copy: dict[str, Any], url_validation: dict[str, Any]) -> list[str]:
    fields = final_copy.get("fields", {})
    pending = set(str(item) for item in url_validation.get("pending_urls", []))
    for key in ["repository_url", "demo_video_url"]:
        if str(fields.get(key, "")).startswith("PENDING_USER_APPROVAL_"):
            pending.add(key)
    return sorted(pending)


def manual_confirmation_flags(args: argparse.Namespace) -> dict[str, bool]:
    return {
        "field_map_readback_confirmed": bool(args.field_map_readback_confirmed),
        "human_confirmations_completed": bool(args.human_confirmations_completed),
        "video_screen_safety_confirmed": bool(args.video_screen_safety_confirmed),
        "post_action_evidence_plan_reviewed": bool(args.post_action_evidence_plan_reviewed),
    }


def build_payload(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    submission_validation = read_json(root / "reports/latest_submission_validation.json")
    final_copy = read_json(root / "reports/latest_devpost_final_copy.json")
    manual_fill = read_json(root / "reports/latest_devpost_manual_fill_brief.json")
    submit_plan = read_json(root / "reports/latest_devpost_submit_command_plan.json")
    url_validation = read_json(root / "reports/latest_submission_url_validation.json")
    go_no_go = read_json(root / "reports/latest_final_go_no_go.json")
    claim = read_json(root / "reports/latest_claim_boundary_validation.json")
    post_action = read_json(root / "reports/latest_post_action_evidence_brief.json")
    approved_urls = read_json(root / "submission/approved_public_urls.json")

    evidence = [{"path": item, "exists": (root / item).exists()} for item in REQUIRED_EVIDENCE]
    missing = [item["path"] for item in evidence if not item["exists"]]
    pending_urls = pending_url_fields(final_copy, url_validation)
    approval_phrase_accepted = args.final_approval_phrase == APPROVAL_PHRASE
    manual_flags = manual_confirmation_flags(args)
    missing_manual_confirmations = [key for key, value in manual_flags.items() if not value]

    final_submit_ready = bool(
        submission_validation.get("overall_status") == "ready_for_user_review"
        and submission_validation.get("failed_count") == 0
        and submission_validation.get("final_submit_ready") is True
        and final_copy.get("final_submit_ready") is True
        and manual_fill.get("final_submit_ready") is True
        and submit_plan.get("final_submit_ready") is True
        and url_validation.get("final_submit_ready") is True
        and go_no_go.get("final_submit_ready") is True
        and claim.get("status") == "pass"
        and not pending_urls
        and approved_urls.get("repository_url")
        and approved_urls.get("demo_video_url")
    )
    local_ready = bool(
        not missing
        and submission_validation.get("overall_status")
        in {"ready_for_user_review", "ready_to_submit_after_user_approval", "needs_more_evidence", None}
        and final_copy.get("status") == "ready_for_user_review"
        and manual_fill.get("status") == "ready_for_user_review"
        and submit_plan.get("status") == "ready_for_user_review"
        and claim.get("status") == "pass"
    )

    gate_issues: list[str] = []
    if missing:
        gate_issues.append("required evidence is missing")
    if not final_submit_ready:
        gate_issues.append("final_submit_ready must be true across validation, final copy, URL validation, and Go/No-Go")
    if args.final_approval_phrase and not approval_phrase_accepted:
        gate_issues.append("final approval phrase must exactly match the Devpost final submission approval phrase")
    elif not args.final_approval_phrase:
        gate_issues.append("final approval phrase is required before manual submit")
    if pending_urls:
        gate_issues.append("repository_url and demo_video_url must not be pending placeholders")
    if missing_manual_confirmations:
        gate_issues.append("manual confirmations are required before manual submit")

    manual_submit_allowed = bool(final_submit_ready and approval_phrase_accepted and not missing_manual_confirmations and not missing)
    if not local_ready:
        gate_status = "needs_more_evidence"
    elif manual_submit_allowed:
        gate_status = "ready_for_manual_devpost_submit"
    elif args.final_approval_phrase and not approval_phrase_accepted:
        gate_status = "blocked_by_final_approval_gate"
    elif not final_submit_ready:
        gate_status = "blocked_until_final_submit_ready"
    elif missing_manual_confirmations:
        gate_status = "blocked_by_manual_readback_gate"
    else:
        gate_status = "blocked_by_final_approval_gate"

    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "gate_status": gate_status,
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": local_ready,
        "final_submit_ready": final_submit_ready,
        "manual_submit_allowed": manual_submit_allowed,
        "approval_phrase_accepted": approval_phrase_accepted,
        "approval_phrase_required": APPROVAL_PHRASE,
        "pending_urls": pending_urls,
        "approved_public_urls_exists": bool((root / "submission/approved_public_urls.json").exists()),
        "manual_confirmations": manual_flags,
        "missing_manual_confirmations": missing_manual_confirmations,
        "missing_evidence": missing,
        "gate_issues": gate_issues,
        "evidence": evidence,
        "post_action_evidence_ready": bool(post_action.get("post_action_evidence_ready", False)),
        "external_actions_attempted": False,
        "external_actions_completed": False,
        "devpost_final_submit_safe_readback": {
            "action_key": "devpost_final_submission",
            "gate_status": gate_status,
            "manual_submit_allowed": manual_submit_allowed,
            "approval_phrase_accepted": approval_phrase_accepted,
            "final_submit_ready": final_submit_ready,
            "pending_urls": pending_urls,
            "evidence_note_target": EVIDENCE_NOTE_TARGET,
            "copy_policy": (
                "Use this block for pre-submit evidence only. After pressing submit, write a short manual "
                "readback note. Do not copy account screenshots, browser state, credentials, tokens, or local paths."
            ),
        },
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    safe = payload["devpost_final_submit_safe_readback"]
    lines = [
        "# Devpost Final Submit Preflight",
        "",
        f"Status: {payload['status']}",
        f"Gate status: {payload['gate_status']}",
        f"Manual submit allowed: {str(payload['manual_submit_allowed']).lower()}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Approval phrase accepted: {str(payload['approval_phrase_accepted']).lower()}",
        "",
        "## Safe Readback",
        "",
        f"- Evidence note target: {safe['evidence_note_target']}",
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
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Devpost Final Submit Preflight</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Devpost Final Submit Preflight</h1>
    <p>Gate status: <span class="{'ready' if payload['manual_submit_allowed'] else 'pending'}">{esc(payload['gate_status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <table>
        <tbody>
          <tr><th>Status</th><td>{esc(payload['status'])}</td></tr>
          <tr><th>Manual submit allowed</th><td>{esc(payload['manual_submit_allowed'])}</td></tr>
          <tr><th>Final submit ready</th><td>{esc(payload['final_submit_ready'])}</td></tr>
          <tr><th>Approval phrase accepted</th><td>{esc(payload['approval_phrase_accepted'])}</td></tr>
          <tr><th>Evidence note target</th><td>{esc(payload['devpost_final_submit_safe_readback']['evidence_note_target'])}</td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
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
    parser = argparse.ArgumentParser(description="Local-only final Devpost submit preflight gate.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--final-approval-phrase", default="")
    parser.add_argument("--field-map-readback-confirmed", action="store_true")
    parser.add_argument("--human-confirmations-completed", action="store_true")
    parser.add_argument("--video-screen-safety-confirmed", action="store_true")
    parser.add_argument("--post-action-evidence-plan-reviewed", action="store_true")
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    payload = build_payload(root, args)
    if not args.no_write_report:
        write_outputs(root, payload)
    print(json.dumps({
        "status": payload["status"],
        "gate_status": payload["gate_status"],
        "final_submit_ready": payload["final_submit_ready"],
        "manual_submit_allowed": payload["manual_submit_allowed"],
        "approval_phrase_accepted": payload["approval_phrase_accepted"],
        "external_actions_attempted": payload["external_actions_attempted"],
        "html": f"reports/{REPORT_STEM}.html",
        "markdown": f"reports/{REPORT_STEM}.md",
        "json": f"reports/{REPORT_STEM}.json",
    }, ensure_ascii=False, indent=2))
    if args.final_approval_phrase or any(manual_confirmation_flags(args).values()):
        return 0 if payload["manual_submit_allowed"] else 2
    return 0 if payload["status"] != "needs_more_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
