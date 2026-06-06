from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This packet is local approval guidance only. It does not publish, upload, submit, "
    "create accounts, configure credentials, write approved URLs, or update Devpost."
)


ACTION_LABELS = {
    "public_github_repository": "Public GitHub Repository",
    "public_demo_video": "Public Demo Video",
    "optional_live_splunk_mcp_proof": "Optional Live Splunk / MCP Proof",
    "live_splunk_bonus_proof": "Optional Live Splunk / MCP Proof",
    "approved_url_writeback": "Approved URL Writeback",
    "devpost_final_submission": "Devpost Final Submission",
}
PUBLIC_CANDIDATE_PREFIX = "public_repo_candidate/agentops-control-tower/"
PUBLIC_CANDIDATE_ROOT_ONLY_EVIDENCE = {
    "reports/latest_release_zip_smoke_test.html",
    "reports/latest_release_zip_smoke_test.json",
    "reports/latest_public_candidate_zip_manifest.html",
    "reports/latest_public_candidate_zip_manifest.json",
    "reports/latest_public_repo_dry_run.html",
    "reports/latest_public_repo_dry_run.json",
    "reports/latest_public_repo_dry_run.md",
    "release/agentops-control-tower-public-candidate.zip",
}


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def normalize_evidence_path(root: Path, path: str) -> str:
    if not is_public_candidate_root(root):
        return path
    if path.startswith(PUBLIC_CANDIDATE_PREFIX):
        return path[len(PUBLIC_CANDIDATE_PREFIX):]
    return path


def normalize_action_key(key: str) -> str:
    if key == "live_splunk_bonus_proof":
        return "optional_live_splunk_mcp_proof"
    return key


def load_state(root: Path) -> dict[str, Any]:
    return {
        "launch": read_json(root / "reports/latest_launch_decision_brief.json"),
        "external": read_json(root / "reports/latest_external_approval_packet.json"),
        "eligibility": read_json(root / "reports/latest_eligibility_compliance_audit.json"),
        "validation": read_json(root / "reports/latest_submission_validation.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
        "release_integrity": read_json(root / "reports/latest_release_integrity_manifest.json"),
    }


def external_by_key(external: dict[str, Any]) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for item in external.get("approval_requests", []):
        key = normalize_action_key(str(item.get("key", "")))
        mapped[key] = item
    return mapped


def decision_cards(root: Path, state: dict[str, Any]) -> list[dict[str, Any]]:
    external = external_by_key(state["external"])
    cards: list[dict[str, Any]] = []
    for decision in state["launch"].get("decisions", []):
        key = normalize_action_key(str(decision.get("key", "")))
        ext = external.get(key, {})
        evidence = decision.get("evidence", [])
        normalized_evidence = []
        for item in evidence:
            path = str(item.get("path", ""))
            if not path:
                continue
            if is_public_candidate_root(root) and path in PUBLIC_CANDIDATE_ROOT_ONLY_EVIDENCE:
                continue
            path = normalize_evidence_path(root, path)
            normalized_evidence.append({"path": path, "exists": exists(root, path)})
        cards.append(
            {
                "key": key,
                "title": decision.get("title") or ACTION_LABELS.get(key, key),
                "status": decision.get("status", "hold"),
                "approval_phrase": decision.get("approval_phrase", ""),
                "purpose": decision.get("purpose") or ext.get("purpose", ""),
                "exact_operation": ext.get("exact_operation", decision.get("after_approval", "")),
                "after_approval": decision.get("after_approval", ext.get("exact_operation", "")),
                "main_risk": decision.get("main_risk") or ext.get("main_risk", ""),
                "verification": decision.get("verification") or ext.get("verification", ""),
                "evidence": normalized_evidence,
            }
        )
    if cards:
        return cards

    for item in state["external"].get("approval_requests", []):
        key = normalize_action_key(str(item.get("key", "")))
        cards.append(
            {
                "key": key,
                "title": item.get("title") or ACTION_LABELS.get(key, key),
                "status": item.get("status", "hold"),
                "approval_phrase": "",
                "purpose": item.get("purpose", ""),
                "exact_operation": item.get("exact_operation", ""),
                "after_approval": item.get("exact_operation", ""),
                "main_risk": item.get("main_risk", ""),
                "verification": item.get("verification", ""),
                "evidence": [{"path": path, "exists": exists(root, path)} for path in item.get("evidence", [])],
            }
        )
    return cards


def human_confirmations(state: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    for item in state["eligibility"].get("human_confirmation_items", []):
        items.append(
            {
                "key": item.get("key", ""),
                "rule_area": item.get("rule_area", ""),
                "confirmation_needed": item.get("confirmation_needed", ""),
                "why_codex_cannot_confirm": item.get("why_codex_cannot_confirm", ""),
            }
        )
    return items


def local_submission_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    validation = state["validation"]
    go_no_go = state["go_no_go"]
    status = validation.get("overall_status", go_no_go.get("status", "missing"))
    failed_count = validation.get("failed_count", "missing")
    source = "reports/latest_submission_validation.json" if validation else "reports/latest_final_go_no_go.json"
    if not validation and go_no_go.get("status") == "ready_for_user_review":
        failed_count = 0
    if (
        status == "needs_more_evidence"
        and go_no_go.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready") is True
        and go_no_go.get("missing_public_candidate_evidence", []) == []
    ):
        status = "ready_for_user_review"
        failed_count = 0
    return {
        "status": status,
        "failed_count": failed_count,
        "source": source,
    }


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    cards = decision_cards(root, state)
    ready_now = [item["key"] for item in cards if item["status"] == "ready_for_user_decision"]
    missing_evidence = [
        f"{item['key']}:{evidence['path']}"
        for item in cards
        for evidence in item["evidence"]
        if not evidence["exists"]
    ]
    confirmations = human_confirmations(state)
    launch_status = state["launch"].get("status", "missing")
    external_status = state["external"].get("status", "missing")
    eligibility_status = state["eligibility"].get("status", "missing")
    status = "ready_for_user_review"
    if missing_evidence or launch_status == "missing" or external_status == "missing" or eligibility_status == "missing":
        status = "needs_more_evidence"
    order = [normalize_action_key(str(key)) for key in state["launch"].get("recommended_approval_order", [])]
    if not order:
        order = [item["key"] for item in cards]
    next_target = next((item for item in cards if item["status"] == "ready_for_user_decision"), None)
    local_submission = local_submission_snapshot(state)
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "launch_status": launch_status,
        "external_approval_status": external_status,
        "eligibility_compliance_status": eligibility_status,
        "local_submission_status": local_submission["status"],
        "local_submission_failed_count": local_submission["failed_count"],
        "local_submission_source": local_submission["source"],
        "final_submit_ready": bool(state["go_no_go"].get("final_submit_ready", False)),
        "approved_public_urls_exists": bool(state["release_integrity"].get("approved_public_urls_exists", False)),
        "pending_urls": state["url_validation"].get("pending_urls", []),
        "ready_now": ready_now,
        "next_approval_target": next_target["key"] if next_target else "",
        "recommended_approval_order": order,
        "actions": cards,
        "human_confirmation_required_count": len(confirmations),
        "human_confirmations": confirmations,
        "missing_evidence": missing_evidence,
        "boundary": BOUNDARY,
        "recommended_next_step": (
            "Ask for public GitHub and public demo video approval first. Keep URL writeback and "
            "Devpost final submission blocked until both public URLs are verified."
        ),
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Next Approval Packet",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Next approval target: {payload['next_approval_target'] or 'none'}",
        f"Local submission status: {payload['local_submission_status']} / failed_count {payload['local_submission_failed_count']} ({payload['local_submission_source']})",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Pending URLs: {', '.join(payload['pending_urls']) if payload['pending_urls'] else 'none'}",
        "",
        "## Recommended Approval Order",
        "",
    ]
    actions_by_key = {item["key"]: item for item in payload["actions"]}
    for index, key in enumerate(payload["recommended_approval_order"], start=1):
        action = actions_by_key.get(key, {"title": ACTION_LABELS.get(key, key), "status": "missing"})
        lines.append(f"{index}. {action['title']} - {action['status']}")
    lines.extend(["", "## Copy-Paste Approval Phrases", ""])
    for action in payload["actions"]:
        phrase = action["approval_phrase"] or "No standalone approval phrase; use the exact operation text."
        lines.extend(
            [
                f"### {action['title']}",
                "",
                f"Status: {action['status']}",
                f"Approval phrase: `{phrase}`",
                "",
                f"Purpose: {action['purpose']}",
                f"Exact operation: {action['exact_operation']}",
                f"After approval: {action['after_approval']}",
                f"Main risk: {action['main_risk']}",
                f"Verification: {action['verification']}",
                "",
                "Evidence:",
            ]
        )
        for evidence in action["evidence"]:
            marker = "present" if evidence["exists"] else "missing"
            lines.append(f"- `{evidence['path']}` ({marker})")
        lines.append("")
    lines.extend(["## Human Confirmations Before Devpost", ""])
    for item in payload["human_confirmations"]:
        lines.extend(
            [
                f"### {item['key']}",
                "",
                f"Rule area: {item['rule_area']}",
                f"Confirm: {item['confirmation_needed']}",
                f"Why Codex cannot confirm: {item['why_codex_cannot_confirm']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary",
            "",
            payload["boundary"],
            "",
            "## Recommended Next Step",
            "",
            payload["recommended_next_step"],
            "",
        ]
    )
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    order_rows = "\n".join(
        "<tr>"
        f"<td>{esc(index)}</td>"
        f"<td>{esc(next((item['title'] for item in payload['actions'] if item['key'] == key), ACTION_LABELS.get(key, key)))}</td>"
        f"<td>{esc(next((item['status'] for item in payload['actions'] if item['key'] == key), 'missing'))}</td>"
        "</tr>"
        for index, key in enumerate(payload["recommended_approval_order"], start=1)
    )
    action_sections = []
    for action in payload["actions"]:
        evidence_rows = "\n".join(
            "<tr>"
            f"<td><code>{esc(item['path'])}</code></td>"
            f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
            "</tr>"
            for item in action["evidence"]
        )
        action_sections.append(
            f"""    <section>
      <h2>{esc(action['title'])}</h2>
      <p>Status: <span class="{'ready' if action['status'] == 'ready_for_user_decision' else 'pending'}">{esc(action['status'])}</span></p>
      <table>
        <tbody>
          <tr><th>Approval phrase</th><td><code>{esc(action['approval_phrase'] or 'No standalone approval phrase')}</code></td></tr>
          <tr><th>Purpose</th><td>{esc(action['purpose'])}</td></tr>
          <tr><th>Exact operation</th><td>{esc(action['exact_operation'])}</td></tr>
          <tr><th>After approval</th><td>{esc(action['after_approval'])}</td></tr>
          <tr><th>Main risk</th><td>{esc(action['main_risk'])}</td></tr>
          <tr><th>Verification</th><td>{esc(action['verification'])}</td></tr>
        </tbody>
      </table>
      <h3>Evidence</h3>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>"""
        )
    confirmation_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['key'])}</td>"
        f"<td>{esc(item['rule_area'])}</td>"
        f"<td>{esc(item['confirmation_needed'])}</td>"
        "</tr>"
        for item in payload["human_confirmations"]
    )
    action_html = "\n".join(action_sections)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Next Approval Packet</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; width: 190px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
  </style>
</head>
<body>
  <header>
    <h1>Next Approval Packet</h1>
    <p>Status: <span class="ready">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <table>
        <tbody>
          <tr><th>Next approval target</th><td>{esc(payload['next_approval_target'] or 'none')}</td></tr>
          <tr><th>Ready now</th><td>{esc(', '.join(payload['ready_now']) if payload['ready_now'] else 'none')}</td></tr>
          <tr><th>Local submission</th><td>{esc(payload['local_submission_status'])} / failed_count {esc(payload['local_submission_failed_count'])} ({esc(payload['local_submission_source'])})</td></tr>
          <tr><th>Pending URLs</th><td>{esc(', '.join(payload['pending_urls']) if payload['pending_urls'] else 'none')}</td></tr>
          <tr><th>Final submit ready</th><td>{esc(payload['final_submit_ready'])}</td></tr>
          <tr><th>Human confirmations</th><td>{esc(payload['human_confirmation_required_count'])}</td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Recommended Approval Order</h2>
      <table>
        <thead><tr><th>#</th><th>Action</th><th>Status</th></tr></thead>
        <tbody>{order_rows}</tbody>
      </table>
    </section>
{action_html}
    <section>
      <h2>Human Confirmations Before Devpost</h2>
      <table>
        <thead><tr><th>Key</th><th>Rule area</th><th>Confirmation needed</th></tr></thead>
        <tbody>{confirmation_rows}</tbody>
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
    markdown = render_markdown(payload)
    write_json(reports / "latest_next_approval_packet.json", payload)
    (reports / "latest_next_approval_packet.md").write_text(markdown, encoding="utf-8")
    (reports / "latest_next_approval_packet.html").write_text(render_html(payload), encoding="utf-8")
    (submission / "NEXT_APPROVAL_PACKET.md").write_text(markdown, encoding="utf-8")
    return {
        "status": payload["status"],
        "next_approval_target": payload["next_approval_target"],
        "ready_now": payload["ready_now"],
        "human_confirmation_required_count": payload["human_confirmation_required_count"],
        "html": "reports/latest_next_approval_packet.html",
        "markdown": "reports/latest_next_approval_packet.md",
        "json": "reports/latest_next_approval_packet.json",
        "submission_markdown": "submission/NEXT_APPROVAL_PACKET.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the next approval packet for safe external submission gates.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
