from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APPROVAL_PHRASE = "Approve recording and public upload of the Agentic Incident Command Center demo video."
BOUNDARY = (
    "This public video upload gate is a local preflight only. It does not record video, "
    "upload video, publish media, open accounts, write approved URLs, update Devpost, "
    "connect to Splunk, configure MCP, or submit anything."
)
REPORT_STEM = "latest_public_video_upload_preflight"
EVIDENCE_NOTE_TARGET = "submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md"
SCREEN_SAFETY_CHECKLIST = "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md"


REQUIRED_EVIDENCE = [
    "reports/latest_demo_tour.html",
    "reports/latest_video_readiness.html",
    "reports/latest_video_readiness.json",
    "reports/latest_video_cue_sheet.html",
    "reports/latest_video_cue_sheet.json",
    "reports/latest_video_recording_preview.html",
    "reports/latest_video_recording_preview.json",
    "reports/latest_video_upload_metadata.html",
    "reports/latest_video_upload_metadata.json",
    "reports/latest_content_rights_audit.html",
    "reports/latest_content_rights_audit.json",
    "reports/latest_claim_boundary_validation.html",
    "reports/latest_claim_boundary_validation.json",
    "submission/DEMO_VIDEO_SCRIPT.md",
    "submission/VIDEO_RECORDING_RUNBOOK.md",
    "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
    "submission/VIDEO_UPLOAD_METADATA.md",
]


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def manual_confirmation_flags(args: argparse.Namespace) -> dict[str, bool]:
    return {
        "screen_safety_confirmed": bool(args.screen_safety_confirmed),
        "duration_confirmed": bool(args.duration_confirmed),
        "claim_boundary_confirmed": bool(args.claim_boundary_confirmed),
        "content_rights_confirmed": bool(args.content_rights_confirmed),
        "upload_visibility_confirmed": bool(args.upload_visibility_confirmed),
    }


def duration_values(*payloads: dict[str, Any]) -> list[int]:
    values: list[int] = []
    for payload in payloads:
        for key in ["duration_seconds", "observed_duration_seconds"]:
            value = payload.get(key)
            if isinstance(value, int):
                values.append(value)
            elif isinstance(value, str) and value.isdigit():
                values.append(int(value))
    return values


def build_payload(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    readiness = read_json(root / "reports/latest_video_readiness.json")
    cue = read_json(root / "reports/latest_video_cue_sheet.json")
    preview = read_json(root / "reports/latest_video_recording_preview.json")
    upload = read_json(root / "reports/latest_video_upload_metadata.json")
    claim = read_json(root / "reports/latest_claim_boundary_validation.json")
    content = read_json(root / "reports/latest_content_rights_audit.json")

    evidence = [{"path": item, "exists": (root / item).exists()} for item in REQUIRED_EVIDENCE]
    missing = [item["path"] for item in evidence if not item["exists"]]
    durations = duration_values(readiness, cue, upload)
    duration_seconds = max(durations) if durations else None
    duration_ok = duration_seconds is not None and duration_seconds <= 180

    preview_safe = preview.get("public_video_safe_readback", {})
    screen_scan = preview_safe.get("screen_scan", {}) if isinstance(preview_safe, dict) else {}
    preview_ok = bool(
        preview.get("status") == "ready_for_recording_review"
        and preview.get("failed_count") == 0
        and preview_safe.get("ready_for_recording_review") is True
        and int(screen_scan.get("internal_path_hit_count", 1)) == 0
        and int(screen_scan.get("secret_like_hit_count", 1)) == 0
    )
    readiness_ok = readiness.get("status") == "ready_for_recording_review"
    cue_ok = cue.get("status") == "ready_for_recording_review"
    upload_ok = upload.get("status") == "ready_for_user_review" and upload.get("public_video_url") == "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL"
    claim_ok = claim.get("status") == "pass"
    content_ok = content.get("status") == "ready_for_user_review"

    approval_phrase_accepted = args.approval_phrase == APPROVAL_PHRASE
    manual_flags = manual_confirmation_flags(args)
    missing_manual_confirmations = [key for key, value in manual_flags.items() if not value]

    local_ready = bool(
        not missing
        and readiness_ok
        and cue_ok
        and preview_ok
        and upload_ok
        and claim_ok
        and content_ok
        and duration_ok
    )
    public_video_upload_allowed = bool(local_ready and approval_phrase_accepted and not missing_manual_confirmations)

    gate_issues: list[str] = []
    if missing:
        gate_issues.append("required video upload preflight evidence is missing")
    if not readiness_ok:
        gate_issues.append("video readiness must be ready_for_recording_review")
    if not cue_ok:
        gate_issues.append("video cue sheet must be ready_for_recording_review")
    if not preview_ok:
        gate_issues.append("recording preview safe readback must pass without internal paths or secret-like hits")
    if not upload_ok:
        gate_issues.append("video upload metadata must be ready_for_user_review with a pending public video URL")
    if not claim_ok:
        gate_issues.append("claim boundary validation must pass before public upload")
    if not content_ok:
        gate_issues.append("content rights audit must be ready_for_user_review before public upload")
    if not duration_ok:
        gate_issues.append("video duration must be confirmed at 180 seconds or less")
    if args.approval_phrase and not approval_phrase_accepted:
        gate_issues.append("approval phrase must exactly match the public demo video approval phrase")
    elif not args.approval_phrase:
        gate_issues.append("approval phrase is required before manual recording or public upload")
    if missing_manual_confirmations:
        gate_issues.append("manual screen, duration, claim, rights, and visibility confirmations are required before upload")

    if not local_ready:
        gate_status = "needs_more_evidence"
    elif public_video_upload_allowed:
        gate_status = "ready_for_manual_public_video_upload"
    elif not approval_phrase_accepted:
        gate_status = "blocked_by_video_approval_gate"
    elif missing_manual_confirmations:
        gate_status = "blocked_by_screen_safety_gate"
    else:
        gate_status = "blocked_by_video_approval_gate"

    safe_readback = {
        "action_key": "public_demo_video",
        "gate_status": gate_status,
        "public_video_upload_allowed": public_video_upload_allowed,
        "approval_phrase_accepted": approval_phrase_accepted,
        "ready_for_public_upload": public_video_upload_allowed,
        "ready_for_recording_review": local_ready,
        "final_recording_review_required": True,
        "duration_seconds": duration_seconds,
        "screen_safety_checklist": SCREEN_SAFETY_CHECKLIST,
        "evidence_note_target": EVIDENCE_NOTE_TARGET,
        "public_video_url": "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL",
        "external_actions_attempted": False,
        "external_actions_completed": False,
        "forbidden_content": [
            "credentials",
            "tokens",
            "account screenshots",
            "browser tabs",
            "billing pages",
            "OAuth screens",
            "local absolute paths",
            "private workspace material",
            "private logs",
            "customer data",
        ],
        "copy_policy": (
            "Use this pre-upload safe readback plus the recording-preview safe readback and a short "
            "manual final-recording review summary. Do not copy screenshots, browser state, account "
            "pages, raw recording output, credentials, tokens, or local absolute paths."
        ),
    }

    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "gate_status": gate_status,
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": local_ready,
        "duration_seconds": duration_seconds,
        "public_video_upload_allowed": public_video_upload_allowed,
        "approval_phrase_accepted": approval_phrase_accepted,
        "approval_phrase_required": APPROVAL_PHRASE,
        "manual_confirmations": manual_flags,
        "missing_manual_confirmations": missing_manual_confirmations,
        "missing_evidence": missing,
        "gate_issues": gate_issues,
        "evidence": evidence,
        "external_actions_attempted": False,
        "external_actions_completed": False,
        "public_video_upload_safe_readback": safe_readback,
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    safe = payload["public_video_upload_safe_readback"]
    lines = [
        "# Public Video Upload Preflight",
        "",
        f"Status: {payload['status']}",
        f"Gate status: {payload['gate_status']}",
        f"Public video upload allowed: {str(payload['public_video_upload_allowed']).lower()}",
        f"Approval phrase accepted: {str(payload['approval_phrase_accepted']).lower()}",
        f"Duration seconds: {payload['duration_seconds']}",
        "",
        "## Safe Readback",
        "",
        f"- Evidence note target: {safe['evidence_note_target']}",
        f"- Screen safety checklist: {safe['screen_safety_checklist']}",
        f"- Ready for public upload: {str(safe['ready_for_public_upload']).lower()}",
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
    safe = payload["public_video_upload_safe_readback"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Video Upload Preflight</title>
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
    <h1>Public Video Upload Preflight</h1>
    <p>Gate status: <span class="{'ready' if payload['public_video_upload_allowed'] else 'pending'}">{esc(payload['gate_status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <table>
        <tbody>
          <tr><th>Status</th><td>{esc(payload['status'])}</td></tr>
          <tr><th>Public video upload allowed</th><td>{esc(payload['public_video_upload_allowed'])}</td></tr>
          <tr><th>Approval phrase accepted</th><td>{esc(payload['approval_phrase_accepted'])}</td></tr>
          <tr><th>Duration seconds</th><td>{esc(payload['duration_seconds'])}</td></tr>
          <tr><th>Evidence note target</th><td><code>{esc(safe['evidence_note_target'])}</code></td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Safe Readback</h2>
      <table>
        <tbody>
          <tr><th>Ready for public upload</th><td>{esc(safe['ready_for_public_upload'])}</td></tr>
          <tr><th>Screen safety checklist</th><td><code>{esc(safe['screen_safety_checklist'])}</code></td></tr>
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
    parser = argparse.ArgumentParser(description="Local-only public demo video upload preflight gate.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--approval-phrase", default="")
    parser.add_argument("--screen-safety-confirmed", action="store_true")
    parser.add_argument("--duration-confirmed", action="store_true")
    parser.add_argument("--claim-boundary-confirmed", action="store_true")
    parser.add_argument("--content-rights-confirmed", action="store_true")
    parser.add_argument("--upload-visibility-confirmed", action="store_true")
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    payload = build_payload(root, args)
    if not args.no_write_report:
        write_outputs(root, payload)
    print(json.dumps({
        "status": payload["status"],
        "gate_status": payload["gate_status"],
        "public_video_upload_allowed": payload["public_video_upload_allowed"],
        "approval_phrase_accepted": payload["approval_phrase_accepted"],
        "external_actions_attempted": payload["external_actions_attempted"],
        "html": f"reports/{REPORT_STEM}.html",
        "markdown": f"reports/{REPORT_STEM}.md",
        "json": f"reports/{REPORT_STEM}.json",
    }, ensure_ascii=False, indent=2))
    if args.approval_phrase or any(manual_confirmation_flags(args).values()):
        return 0 if payload["public_video_upload_allowed"] else 2
    return 0 if payload["status"] != "needs_more_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
