from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APPROVAL_PHRASE = "Approve optional live Splunk and Splunk MCP proof using synthetic data only."
BOUNDARY = (
    "This proof capture manifest is local evidence aggregation only. The manifest builder does not create "
    "accounts, configure credentials, import data, install apps, connect MCP, capture screenshots, record "
    "video, update claims, publish, upload, write approved URLs, update Devpost, or submit anything. "
    "When a live proof artifact is present, it is limited to the approved ephemeral Docker Splunk runtime, "
    "synthetic data, and read-only local MCP SDK adapter evidence."
)


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def live_proof(root: Path) -> dict[str, Any]:
    return read_json(root / "reports/latest_live_splunk_docker_proof.json")


def official_mcp_readback_verified(root: Path) -> bool:
    readback = root / "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md"
    if not readback.exists():
        return False
    text = readback.read_text(encoding="utf-8").lower()
    return all(
        marker in text
        for marker in [
            "status: ready_for_claim_update",
            "mcp connection status: connected",
            "tool used: `splunk_run_query`",
            "official splunk mcp server was installed and verified",
            "production splunk cloud deployment is not claimed",
        ]
    )


def evidence(root: Path) -> list[dict[str, Any]]:
    items: list[tuple[str, bool]] = [
        ("reports/latest_splunk_mcp_command_plan.html", True),
        ("reports/latest_splunk_mcp_proof_brief.html", True),
        ("reports/latest_splunk_mcp_prompt_pack.html", True),
        ("reports/latest_live_splunk_docker_proof.html", False),
        ("reports/latest_live_splunk_docker_proof.json", False),
        ("reports/latest_live_splunk_docker_proof.md", False),
        ("reports/latest_local_spl_query_results.html", True),
        ("reports/latest_local_spl_query_results.json", True),
        ("reports/latest_splunk_app_package_manifest.html", True),
        ("reports/latest_claim_boundary_validation.html", True),
        ("reports/latest_claim_boundary_validation.json", True),
        ("reports/latest_public_artifact_url_readback.html", True),
        ("reports/latest_post_action_evidence_brief.html", True),
        ("submission/SPLUNK_MCP_RUNBOOK.md", True),
        ("submission/SPLUNK_MCP_PROMPT_PACK.md", True),
        ("submission/SPL_QUERIES.md", True),
        ("data/splunk_agentops_events.csv", True),
        ("splunk_app/agentops_control_tower/default/indexes.conf", True),
        ("splunk_app/agentops_control_tower/default/props.conf", True),
        ("splunk_app/agentops_control_tower/default/savedsearches.conf", True),
        ("splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml", True),
    ]
    if not is_public_candidate_root(root):
        items.extend([
            ("reports/latest_submission_validation.html", True),
            ("reports/latest_release_zip_smoke_test.html", True),
        ])
    return [{"path": path, "exists": exists(root, path), "required": required} for path, required in items]


def capture_slots(live: dict[str, Any], official_mcp_verified: bool) -> list[dict[str, Any]]:
    live_splunk_verified = live.get("live_splunk_verified") is True
    live_queries_verified = live_splunk_verified and int(live.get("failed_query_count", 1)) == 0
    adapter_verified = live.get("mcp_protocol_adapter_verified") is True
    return [
        {
            "key": "approved_scope",
            "status": "captured_ephemeral_docker_terms_scope" if live_splunk_verified else "pending_user_approval",
            "required_readback": [
                "Explicit approval phrase is present.",
                "Splunk General Terms flag is used only for the temporary Docker proof.",
                "Data source is limited to data/splunk_agentops_events.csv.",
                "MCP scope is read-only for the synthetic agentops_events index.",
            ],
            "safe_artifact": "Local note in post-action evidence log; no credential or account screenshots.",
        },
        {
            "key": "synthetic_import",
            "status": "captured_live_splunk_docker" if live_splunk_verified else "pending_live_capture",
            "required_readback": [
                "agentops_events index exists.",
                "Imported rows match the generated synthetic CSV row count.",
                "Sourcetype is agentops:events or equivalent documented mapping.",
            ],
            "safe_artifact": "reports/latest_live_splunk_docker_proof.*",
        },
        {
            "key": "live_spl_queries",
            "status": "captured_live_splunk_docker" if live_queries_verified else "pending_live_capture",
            "required_readback": [
                "Incident timeline query returns signal domains, services, risk scores, and evidence refs.",
                "Root-cause evidence query ranks checkout-api release regression first.",
                "MCP Remediation Ledger query returns pending/blocked human-review items.",
                "Blast-radius query returns affected services and max risk.",
            ],
            "safe_artifact": "reports/latest_live_splunk_docker_proof.json query_results.",
        },
        {
            "key": "splunk_app_dashboard",
            "status": "pending_dashboard_ui_capture",
            "required_readback": [
                "Agentic Incident Command Center dashboard opens against the synthetic index.",
                "KPI, incident summary, root-cause ranking, blast radius, and remediation ledger sections render.",
                "No private workspace paths, real accounts, or credentials are visible.",
            ],
            "safe_artifact": "Dashboard screenshot or recording segment after screen-safety review.",
        },
        {
            "key": "mcp_assisted_answer",
            "status": (
                "captured_official_splunk_mcp_server"
                if official_mcp_verified
                else "captured_local_mcp_sdk_adapter_official_pending" if adapter_verified else "pending_live_capture"
            ),
            "required_readback": [
                "MCP answer cites event IDs and evidence refs.",
                "MCP answer does not perform external actions.",
                "MCP answer stays within read-only synthetic data scope.",
                "Official Splunk MCP Server app is verified only in local Splunk Enterprise Docker with synthetic data.",
            ],
            "safe_artifact": "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md.",
        },
        {
            "key": "claim_upgrade_validation",
            "status": "blocked_until_official_splunk_mcp_server_proof" if not official_mcp_verified else "ready_for_claim_review",
            "required_readback": [
                "Claim wording is updated only after live SPL and official Splunk MCP Server evidence are reviewed.",
                "validate_claim_boundaries.py passes.",
                "validate_submission_packet.py passes.",
            ],
            "safe_artifact": "Validation JSON/HTML after approved proof capture and wording update.",
        },
    ]


def stop_conditions() -> list[str]:
    return [
        "Stop if Splunk account, license, cost, credential, or MCP scope is not explicitly approved.",
        "Stop if any data source is real private workspace data, customer data, local paths, or credentials.",
        "Stop if screenshots or recordings show account settings, billing pages, tokens, hostnames, terminals with secrets, or unrelated private files.",
        "Stop if MCP can mutate data, send notifications, publish, trade, deploy, or access outside the approved synthetic index.",
        "Stop if event IDs and evidence refs cannot be cited from the live proof.",
        "Stop if claim-boundary validation fails after any wording change.",
    ]


def build_payload(root: Path) -> dict[str, Any]:
    command_plan = read_json(root / "reports/latest_splunk_mcp_command_plan.json")
    proof_brief = read_json(root / "reports/latest_splunk_mcp_proof_brief.json")
    prompt_pack = read_json(root / "reports/latest_splunk_mcp_prompt_pack.json")
    local_spl = read_json(root / "reports/latest_local_spl_query_results.json")
    claim = read_json(root / "reports/latest_claim_boundary_validation.json")
    live = live_proof(root)
    rows = evidence(root)
    missing = [row["path"] for row in rows if row["required"] and not row["exists"]]
    live_splunk_verified = live.get("live_splunk_verified") is True
    mcp_adapter_verified = live.get("mcp_protocol_adapter_verified") is True
    official_mcp_verified = (
        live.get("official_splunk_mcp_server_verified") is True
        or official_mcp_readback_verified(root)
    )
    local_ready = (
        not missing
        and command_plan.get("status") == "ready_for_user_review"
        and proof_brief.get("status") == "ready_for_user_review"
        and prompt_pack.get("status") == "ready_for_user_review"
        and local_spl.get("status") == "local_spl_emulation_only"
        and claim.get("status") == "pass"
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "approval_phrase": APPROVAL_PHRASE,
        "live_splunk_mcp_verified": official_mcp_verified,
        "live_splunk_verified": live_splunk_verified,
        "mcp_protocol_adapter_verified": mcp_adapter_verified,
        "official_splunk_mcp_server_verified": official_mcp_verified,
        "captured_evidence_status": (
            "official_splunk_mcp_server_captured"
            if official_mcp_verified
            else "pending_user_approval"
        ),
        "claim_upgrade_ready": official_mcp_verified and claim.get("status") == "pass",
        "local_ready": local_ready,
        "capture_slots": capture_slots(live, official_mcp_verified),
        "expected_final_readback": {
            "synthetic_index": "agentops_events contains only generated synthetic rows",
            "live_spl_queries": "required SPL result tables cite event IDs and evidence refs",
            "mcp_answer": "local read-only MCP SDK adapter cites event IDs and evidence refs without external action",
            "official_mcp": "official Splunk MCP Server verified only in local Splunk Enterprise Docker with synthetic data",
            "screen_safety": "no credentials, account pages, private paths, or secrets are visible",
            "claim_validation": "claim and submission validators pass after any wording change",
        },
        "live_proof_summary": {
            "status": live.get("status", "missing"),
            "synthetic_row_count": live.get("synthetic_row_count", "missing"),
            "indexed_row_count": live.get("indexed_row_count", "missing"),
            "failed_query_count": live.get("failed_query_count", "missing"),
            "official_mcp_blocker": "none_local_official_mcp_verified" if official_mcp_verified else live.get("official_mcp_blocker", "not_recorded"),
        },
        "evidence": rows,
        "missing_evidence": missing,
        "stop_conditions": stop_conditions(),
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Splunk MCP Proof Capture Manifest",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Approval phrase: `{payload['approval_phrase']}`",
        f"Live Splunk MCP verified: {str(payload['live_splunk_mcp_verified']).lower()}",
        f"Live Splunk verified: {str(payload['live_splunk_verified']).lower()}",
        f"Local MCP SDK adapter verified: {str(payload['mcp_protocol_adapter_verified']).lower()}",
        f"Official Splunk MCP Server verified: {str(payload['official_splunk_mcp_server_verified']).lower()}",
        f"Captured evidence status: {payload['captured_evidence_status']}",
        f"Claim upgrade ready: {str(payload['claim_upgrade_ready']).lower()}",
        "",
        "## Live Proof Summary",
        "",
    ]
    for key, value in payload["live_proof_summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend([
        "",
        "## Capture Slots",
        "",
    ])
    for slot in payload["capture_slots"]:
        lines.extend([
            f"### {slot['key']}",
            "",
            f"Status: {slot['status']}",
            "",
            "Required readback:",
            "",
        ])
        for item in slot["required_readback"]:
            lines.append(f"- {item}")
        lines.extend(["", f"Safe artifact: {slot['safe_artifact']}", ""])
    lines.extend(["## Expected Final Readback", ""])
    for key, value in payload["expected_final_readback"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Evidence", ""])
    for row in payload["evidence"]:
        status = "present" if row["exists"] else "missing"
        required = "required" if row["required"] else "optional"
        lines.append(f"- `{row['path']}` ({status}, {required})")
    lines.extend(["", "## Stop Conditions", ""])
    for item in payload["stop_conditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    capture_rows = "\n".join(
        f"""<tr>
          <td>{esc(slot['key'])}</td>
          <td class="pending">{esc(slot['status'])}</td>
          <td><ul>{''.join(f'<li>{esc(item)}</li>' for item in slot['required_readback'])}</ul></td>
          <td>{esc(slot['safe_artifact'])}</td>
        </tr>"""
        for slot in payload["capture_slots"]
    )
    readback_rows = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in payload["expected_final_readback"].items()
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
  <title>Splunk MCP Proof Capture Manifest</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; width: 220px; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Splunk MCP Proof Capture Manifest</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Gate State</h2>
      <table><tbody>
        <tr><th>Approval phrase</th><td><code>{esc(payload['approval_phrase'])}</code></td></tr>
        <tr><th>Live Splunk MCP verified</th><td class="pending">{esc(payload['live_splunk_mcp_verified'])}</td></tr>
        <tr><th>Live Splunk verified</th><td class="ready">{esc(payload['live_splunk_verified'])}</td></tr>
        <tr><th>Local MCP SDK adapter verified</th><td class="ready">{esc(payload['mcp_protocol_adapter_verified'])}</td></tr>
        <tr><th>Official Splunk MCP Server verified</th><td class="pending">{esc(payload['official_splunk_mcp_server_verified'])}</td></tr>
        <tr><th>Captured evidence status</th><td class="pending">{esc(payload['captured_evidence_status'])}</td></tr>
        <tr><th>Claim upgrade ready</th><td class="pending">{esc(payload['claim_upgrade_ready'])}</td></tr>
        <tr><th>Live proof status</th><td>{esc(payload['live_proof_summary']['status'])}</td></tr>
        <tr><th>Rows</th><td>{esc(payload['live_proof_summary']['indexed_row_count'])} indexed / {esc(payload['live_proof_summary']['synthetic_row_count'])} synthetic</td></tr>
        <tr><th>Failed live SPL queries</th><td>{esc(payload['live_proof_summary']['failed_query_count'])}</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>Capture Slots</h2>
      <table>
        <thead><tr><th>Slot</th><th>Status</th><th>Required Readback</th><th>Safe Artifact</th></tr></thead>
        <tbody>{capture_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Expected Final Readback</h2>
      <table><tbody>{readback_rows}</tbody></table>
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
      <p class="pending">{esc(payload['boundary'])}</p>
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
    write_json(reports / "latest_splunk_mcp_proof_capture_manifest.json", payload)
    (reports / "latest_splunk_mcp_proof_capture_manifest.md").write_text(markdown, encoding="utf-8")
    (reports / "latest_splunk_mcp_proof_capture_manifest.html").write_text(render_html(payload), encoding="utf-8")
    (submission / "SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md").write_text(markdown, encoding="utf-8")
    return {
        "status": payload["status"],
        "html": "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "markdown": "reports/latest_splunk_mcp_proof_capture_manifest.md",
        "json": "reports/latest_splunk_mcp_proof_capture_manifest.json",
        "submission_markdown": "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local Splunk/MCP proof capture manifest without executing live proof.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
