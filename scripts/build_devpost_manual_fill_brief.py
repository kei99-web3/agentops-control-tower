from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_devpost_submission_packet import SECTION_NAMES


BOUNDARY = (
    "This brief is local Devpost form-fill decision support only. It does not log in, "
    "save a draft, press submit, update Devpost, publish, upload, write approved URLs, "
    "or submit anything."
)


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def evidence_items() -> list[str]:
    return [
        "reports/latest_devpost_submission_packet.html",
        "reports/latest_devpost_submission_packet.json",
        "reports/latest_devpost_final_copy.html",
        "reports/latest_devpost_final_copy.md",
        "reports/latest_devpost_final_copy.json",
        "reports/latest_devpost_submit_command_plan.html",
        "reports/latest_submission_url_validation.html",
        "reports/latest_submission_url_validation.json",
        "reports/latest_submission_url_apply_plan.html",
        "reports/latest_final_go_no_go.html",
        "reports/latest_claim_boundary_validation.html",
        "reports/latest_external_approval_packet.html",
        "submission/DEVPOST_FIELD_MAP.md",
        "submission/FINAL_SUBMISSION_CHECKLIST.md",
        "submission/SUBMISSION_LAUNCH_RUNBOOK.md",
        "architecture_diagram.md",
        "LICENSE",
    ]


def field_rows(final_copy: dict[str, Any]) -> list[dict[str, Any]]:
    fields = final_copy.get("fields", {})
    built_with = ", ".join(fields.get("built_with", []))
    mcp_tag_included = "Splunk MCP Server" in fields.get("built_with", [])
    built_with_readback = (
        "Official Splunk MCP Server is verified in the local Splunk Enterprise Docker proof with synthetic data; Splunk MCP Server may be included as a built-with tag. Do not claim production Splunk Cloud deployment."
        if mcp_tag_included
        else (
            "Use Python, Splunk, SPL, JSON, CSV, HTML now; keep Splunk MCP Server out of built-with "
            "tags until approved live proof is captured and claim validation passes."
        )
    )
    rows = [
        ("Project name", fields.get("project_name", ""), "Exact text matches final copy."),
        ("Tagline", fields.get("tagline", ""), "Exact text matches final copy and stays within the soft limit."),
        ("Track", fields.get("track", ""), "Observability is selected as the primary track."),
        ("Bonus target", fields.get("bonus_target", ""), "Best Use of Splunk MCP Server is selected or described where Devpost allows."),
        ("Built with", built_with, built_with_readback),
        ("Repository URL", fields.get("repository_url", ""), "Must be a user-approved public repository URL, not a pending placeholder."),
        ("Demo video URL", fields.get("demo_video_url", ""), "Must be a user-approved public video URL, not a pending placeholder."),
        ("Architecture diagram", "architecture_diagram.md", "Attach or reference the root architecture diagram evidence."),
        ("License", "LICENSE", "Open-source license remains present in the public repository candidate."),
    ]
    return [
        {
            "field": field,
            "value": value,
            "readback": readback,
            "pending": str(value).startswith("PENDING_USER_APPROVAL_"),
        }
        for field, value, readback in rows
    ]


def section_rows(final_copy: dict[str, Any]) -> list[dict[str, Any]]:
    sections = final_copy.get("sections", {})
    counts = final_copy.get("char_counts", {})
    return [
        {
            "section": name,
            "source": "reports/latest_devpost_final_copy.md",
            "chars": counts.get(name, len(sections.get(name, ""))),
            "present": bool(str(sections.get(name, "")).strip()),
            "readback": "Text matches the final copy and keeps the official MCP claim bounded to local Splunk Enterprise Docker with synthetic data.",
        }
        for name in SECTION_NAMES
    ]


def readback_checks() -> list[str]:
    return [
        "Project name, tagline, track, bonus target, and built-with tags match the final copy packet.",
        "Repository URL and demo video URL are real public URLs and no pending placeholder remains.",
        "Architecture diagram evidence is attached or visible according to the Devpost form requirement.",
        "The Splunk usage text says official Splunk MCP Server proof is local Splunk Enterprise Docker with synthetic data and does not claim production Splunk Cloud deployment.",
        "No text claims the repository is public, video is uploaded, or submission is complete before those gates are true.",
        "No credentials, account pages, local absolute paths, private workspace material, or non-public data are visible.",
        "Final local validation is ready_for_user_review with failed_count 0 immediately before pressing submit.",
        "The final Devpost submit action has explicit user approval in this thread before the button is pressed.",
    ]


def stop_conditions() -> list[str]:
    return [
        "Stop if repository_url or demo_video_url still starts with PENDING_USER_APPROVAL.",
        "Stop if URL validation is not final-submit ready after approved URLs are written.",
        "Stop if claim-boundary validation finds an unqualified live Splunk/MCP claim.",
        "Stop if Devpost shows the wrong track, missing architecture evidence, or missing public repository/video links.",
        "Stop if a browser screen exposes account settings, billing, credentials, local paths, or private data.",
        "Stop if the user has not explicitly approved the final Devpost submit action.",
    ]


def final_review_checklist_items() -> list[tuple[str, str]]:
    return [
        ("track_selected", "Primary track selected: Observability."),
        ("public_repo_url_approved", "Repository URL is approved, public, and not PENDING_USER_APPROVAL_PUBLIC_REPO_URL."),
        ("public_video_url_approved", "Demo video URL is approved, public, and not PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL."),
        ("final_copy_matches", "Devpost text matches reports/latest_devpost_final_copy.md without ad hoc edits."),
        ("field_map_matches", "Visible Devpost fields match submission/DEVPOST_FIELD_MAP.md."),
        ("claim_boundary_reviewed", "No live Splunk/MCP verification claim appears unless approved proof exists."),
        ("human_confirmations_done", "submission/HUMAN_CONFIRMATION_CHECKLIST.md is completed by the entrant."),
        ("video_screen_safety_done", "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md is completed against the final recording."),
        ("local_validation_clean", "reports/latest_submission_validation.html shows ready_for_user_review with failed_count 0."),
        ("public_urls_verified", "reports/latest_submission_url_validation.html shows approved public URLs are valid."),
        ("post_action_evidence_reviewed", "reports/latest_post_action_evidence_brief.html has been reviewed for required readback evidence."),
        ("final_approval_explicit", "The final approval phrase for Devpost final submission is explicit before pressing submit."),
    ]


def build_payload(root: Path) -> dict[str, Any]:
    final_copy = read_json(root / "reports/latest_devpost_final_copy.json")
    submit_plan = read_json(root / "reports/latest_devpost_submit_command_plan.json")
    url_validation = read_json(root / "reports/latest_submission_url_validation.json")
    go_no_go = read_json(root / "reports/latest_final_go_no_go.json")
    claim = read_json(root / "reports/latest_claim_boundary_validation.json")
    evidence = [{"path": item, "exists": exists(root, item)} for item in evidence_items()]
    missing = [item["path"] for item in evidence if not item["exists"]]
    fields = field_rows(final_copy)
    pending_fields = [item["field"] for item in fields if item["pending"]]
    submit_plan_status = submit_plan.get("status")
    submit_plan_reviewable = submit_plan_status == "ready_for_user_review" or (
        submit_plan_status == "needs_more_evidence"
        and set(pending_fields).issubset({"Repository URL", "Demo video URL"})
    )
    local_ready = (
        not missing
        and final_copy.get("status") == "ready_for_user_review"
        and submit_plan_reviewable
        and go_no_go.get("local_ready") is True
        and claim.get("status") == "pass"
    )
    final_submit_ready = bool(
        final_copy.get("final_submit_ready") is True
        and submit_plan.get("final_submit_ready") is True
        and url_validation.get("final_submit_ready") is True
        and go_no_go.get("final_submit_ready") is True
        and not pending_fields
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": local_ready,
        "final_submit_ready": final_submit_ready,
        "pending_fields": pending_fields,
        "submission_url_validation_status": url_validation.get("status", "missing"),
        "claim_boundary_status": claim.get("status", "missing"),
        "missing_evidence": missing,
        "fields": fields,
        "sections": section_rows(final_copy),
        "readback_checks": readback_checks(),
        "stop_conditions": stop_conditions(),
        "final_review_checklist": "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md",
        "final_review_checklist_items": [
            {"id": item_id, "text": text}
            for item_id, text in final_review_checklist_items()
        ],
        "boundary": BOUNDARY,
        "approval_required": "Explicit user approval is required before using a Devpost account/session, saving a draft, or pressing submit.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Devpost Manual Fill And Readback Brief",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Pending fields: {', '.join(payload['pending_fields']) if payload['pending_fields'] else 'none'}",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        payload["approval_required"],
        "",
        "## Core Field Fill Order",
        "",
    ]
    for item in payload["fields"]:
        lines.extend([
            f"### {item['field']}",
            "",
            "```text",
            str(item["value"]),
            "```",
            "",
            f"Readback: {item['readback']}",
            "",
        ])
    lines.extend(["## Section Readback", ""])
    for item in payload["sections"]:
        lines.append(f"- {item['section']}: {item['chars']} chars, source `{item['source']}`. {item['readback']}")
    lines.extend(["", "## Final Readback Checks", ""])
    for item in payload["readback_checks"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Stop Conditions", ""])
    for item in payload["stop_conditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Evidence", ""])
    for item in payload["missing_evidence"]:
        lines.append(f"- Missing: `{item}`")
    if not payload["missing_evidence"]:
        lines.append("- All required local evidence is present.")
    lines.append("")
    return "\n".join(lines)


def render_final_review_checklist(payload: dict[str, Any]) -> str:
    lines = [
        "# Devpost Final Review Checklist",
        "",
        "Status: pending final Devpost review",
        "",
        "Use this checklist immediately before saving a Devpost draft or pressing submit. Leave every item unchecked until the visible Devpost screen, public repository, public demo video, and local evidence have been reviewed.",
        "",
        "## Source Evidence",
        "",
        "- `reports/latest_devpost_manual_fill_brief.html`",
        "- `reports/latest_devpost_final_copy.md`",
        "- `submission/DEVPOST_FIELD_MAP.md`",
        "- `submission/HUMAN_CONFIRMATION_CHECKLIST.md`",
        "- `submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md`",
        "- `reports/latest_submission_validation.html`",
        "- `reports/latest_submission_url_validation.html`",
        "- `reports/latest_post_action_evidence_brief.html`",
        "",
        "## Checklist",
        "",
    ]
    for item in payload["final_review_checklist_items"]:
        lines.append(f"- [ ] `{item['id']}` - {item['text']}")
    lines.extend([
        "",
        "## Boundary",
        "",
        (
            "This checklist does not log in, save a draft, press submit, update Devpost, "
            "publish a repository, upload video, write approved URLs, connect to Splunk, "
            "configure MCP, or submit anything."
        ),
        "",
        "## Final Submit Hold",
        "",
        (
            "Final Devpost submit stays blocked until public repo/video URLs are verified, "
            "human and video screen-safety checklists are completed, validation is rerun, "
            "and explicit final approval exists."
        ),
        "",
    ])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    field_rows_html = "\n".join(
        "<tr>"
        f"<td>{esc(item['field'])}</td>"
        f"<td><pre>{esc(item['value'])}</pre></td>"
        f"<td class=\"{'pending' if item['pending'] else 'ready'}\">{esc('pending' if item['pending'] else 'ready')}</td>"
        f"<td>{esc(item['readback'])}</td>"
        "</tr>"
        for item in payload["fields"]
    )
    section_rows_html = "\n".join(
        "<tr>"
        f"<td>{esc(item['section'])}</td>"
        f"<td>{esc(item['chars'])}</td>"
        f"<td>{esc('present' if item['present'] else 'missing')}</td>"
        f"<td>{esc(item['readback'])}</td>"
        "</tr>"
        for item in payload["sections"]
    )
    readback_items = "\n".join(f"<li>{esc(item)}</li>" for item in payload["readback_checks"])
    stops = "\n".join(f"<li>{esc(item)}</li>" for item in payload["stop_conditions"])
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item)}</code></td>"
        f"<td class=\"fail\">missing</td>"
        "</tr>"
        for item in payload["missing_evidence"]
    ) or "<tr><td>All required local evidence</td><td class=\"ready\">present</td></tr>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Devpost Manual Fill And Readback Brief</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; }}
    code, pre {{ background: #edf3f6; border-radius: 4px; }}
    code {{ padding: 2px 5px; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; padding: 8px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Devpost Manual Fill And Readback Brief</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Boundary</h2>
      <p class="pending">{esc(payload['boundary'])}</p>
      <p>{esc(payload['approval_required'])}</p>
      <table>
        <tbody>
          <tr><th>Final submit ready</th><td class="{'ready' if payload['final_submit_ready'] else 'pending'}">{esc(payload['final_submit_ready'])}</td></tr>
          <tr><th>Pending fields</th><td>{esc(', '.join(payload['pending_fields']) if payload['pending_fields'] else 'none')}</td></tr>
          <tr><th>URL validation</th><td>{esc(payload['submission_url_validation_status'])}</td></tr>
          <tr><th>Claim boundary</th><td>{esc(payload['claim_boundary_status'])}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Core Field Fill Order</h2>
      <table>
        <thead><tr><th>Field</th><th>Value</th><th>Status</th><th>Readback</th></tr></thead>
        <tbody>{field_rows_html}</tbody>
      </table>
    </section>
    <section>
      <h2>Section Readback</h2>
      <table>
        <thead><tr><th>Section</th><th>Chars</th><th>Status</th><th>Readback</th></tr></thead>
        <tbody>{section_rows_html}</tbody>
      </table>
    </section>
    <section>
      <h2>Final Readback Checks</h2>
      <ul>{readback_items}</ul>
    </section>
    <section>
      <h2>Stop Conditions</h2>
      <ul>{stops}</ul>
    </section>
    <section>
      <h2>Evidence</h2>
      <table>
        <thead><tr><th>Item</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
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
    submission = root / "submission"
    reports.mkdir(parents=True, exist_ok=True)
    submission.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_devpost_manual_fill_brief.json", payload)
    (reports / "latest_devpost_manual_fill_brief.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_devpost_manual_fill_brief.html").write_text(render_html(payload), encoding="utf-8")
    (submission / "DEVPOST_FINAL_REVIEW_CHECKLIST.md").write_text(render_final_review_checklist(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "final_submit_ready": payload["final_submit_ready"],
        "pending_fields": payload["pending_fields"],
        "html": "reports/latest_devpost_manual_fill_brief.html",
        "markdown": "reports/latest_devpost_manual_fill_brief.md",
        "json": "reports/latest_devpost_manual_fill_brief.json",
        "final_review_checklist": payload["final_review_checklist"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Devpost manual fill and pre-submit readback brief.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
