from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def evidence(root: Path) -> list[dict[str, Any]]:
    items: list[tuple[str, bool]] = [
        ("submission/SPLUNK_MCP_RUNBOOK.md", True),
        ("data/splunk_agentops_events.csv", True),
        ("submission/SPL_QUERIES.md", True),
        ("reports/latest_live_splunk_docker_proof.html", False),
        ("reports/latest_live_splunk_docker_proof.json", False),
        ("reports/latest_live_splunk_docker_proof.md", False),
        ("reports/latest_local_spl_query_results.html", True),
        ("reports/latest_local_spl_query_results.json", True),
        ("reports/latest_mcp_investigation.md", True),
        ("reports/latest_claim_boundary_validation.html", True),
        ("reports/latest_claim_boundary_validation.json", True),
        ("reports/latest_external_approval_packet.html", True),
        ("splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml", True),
        ("splunk_app/agentops_control_tower/default/savedsearches.conf", True),
        ("splunk_app/agentops_control_tower/default/app.conf", True),
    ]
    return [{"path": item, "exists": exists(root, item), "required": required} for item, required in items]


def command_steps() -> list[dict[str, str]]:
    return [
        {
            "name": "Refresh local synthetic event proof",
            "command": "python prototype\\agentops_control_tower.py run-demo",
            "purpose": "Regenerate synthetic checkout-incident events and the local dashboard before any live setup.",
        },
        {
            "name": "Refresh local SPL-equivalent proof",
            "command": "python scripts\\run_local_spl_query_pack.py",
            "purpose": "Confirm incident timeline, root-cause evidence, remediation ledger, MCP investigation context, and blast-radius rows exist before import.",
        },
        {
            "name": "Validate Splunk app candidate",
            "command": "python scripts\\validate_splunk_app.py",
            "purpose": "Confirm the Simple XML dashboard and saved searches are locally valid before installing or copying them.",
        },
        {
            "name": "Review live setup boundary",
            "command": "manual: review submission\\SPLUNK_MCP_RUNBOOK.md and reports\\latest_external_approval_packet.html",
            "purpose": "Confirm scope, cost, credential, and data boundaries before any Splunk account or MCP action.",
        },
        {
            "name": "Approve Splunk account and license use",
            "command": "manual: create or use an approved Splunk account, trial, Cloud access, or Developer License",
            "purpose": "Start live proof only after explicit account/license approval.",
        },
        {
            "name": "Run approved ephemeral Docker Splunk proof",
            "command": "python scripts\\run_live_splunk_docker_proof.py",
            "purpose": "After the user approves Splunk General Terms for this proof only, index the synthetic CSV in temporary Docker Splunk and capture live SPL plus local MCP SDK adapter readback.",
        },
        {
            "name": "Create approved synthetic-data index",
            "command": "manual: create index agentops_events for synthetic checkout-incident events only",
            "purpose": "Keep live proof isolated from private workspace logs or customer data.",
        },
        {
            "name": "Import synthetic CSV",
            "command": "manual: import data\\splunk_agentops_events.csv into agentops_events",
            "purpose": "Load only the generated synthetic dataset used by the local proof.",
        },
        {
            "name": "Install or copy Splunk app candidate",
            "command": "manual: install or copy splunk_app\\agentops_control_tower after reviewing app.conf, savedsearches.conf, and dashboard XML",
            "purpose": "Expose the Control Tower dashboard without adding unreviewed apps or private data sources.",
        },
        {
            "name": "Run live SPL evidence checks",
            "command": "manual: run the incident timeline, root-cause evidence, remediation ledger, MCP investigation context, and blast-radius queries from submission\\SPL_QUERIES.md",
            "purpose": "Verify live Splunk results match the local query proof before strengthening claims.",
        },
        {
            "name": "Configure Splunk MCP Server after approval",
            "command": "manual: configure Splunk MCP Server with read-only approved scope for agentops_events",
            "purpose": "Allow MCP-assisted investigation only inside the approved synthetic-data scope.",
        },
        {
            "name": "Run MCP-assisted investigation",
            "command": "manual: ask what caused the checkout incident, which services are affected, and which remediation needs human approval first; require cited event IDs plus evidence refs",
            "purpose": "Capture the bonus-proof story without allowing external actions or secret access.",
        },
        {
            "name": "Build proof capture manifest",
            "command": "python scripts\\build_splunk_mcp_proof_capture_manifest.py",
            "purpose": "Freeze the required live proof capture slots, readback evidence, stop conditions, and claim-upgrade gate before any proof capture.",
        },
        {
            "name": "Capture live proof safely",
            "command": "manual: capture screenshots or recording of indexed CSV, live SPL results, and MCP answer with no tokens, account pages, or private paths visible",
            "purpose": "Create evidence for the final demo only after the screen-safety review passes.",
        },
        {
            "name": "Upgrade claim wording only after proof",
            "command": "python scripts\\validate_claim_boundaries.py && python scripts\\validate_submission_packet.py",
            "purpose": "Re-check public copy before saying the project is verified through Splunk MCP Server.",
        },
    ]


def build_payload(root: Path) -> dict[str, Any]:
    approval = read_json(root / "reports/latest_external_approval_packet.json")
    local_spl = read_json(root / "reports/latest_local_spl_query_results.json")
    claim = read_json(root / "reports/latest_claim_boundary_validation.json")
    live = live_proof(root)
    rows = evidence(root)
    missing = [item["path"] for item in rows if item["required"] and not item["exists"]]
    approval_requests = {
        item.get("key"): item
        for item in approval.get("approval_requests", [])
        if isinstance(item, dict)
    }
    splunk_request = approval_requests.get("live_splunk_bonus_proof", {})
    local_ready = (
        not missing
        and local_spl.get("status") == "local_spl_emulation_only"
        and len(local_spl.get("results", [])) >= 4
        and claim.get("status") == "pass"
        and splunk_request.get("status") in {"optional_user_decision", "completed"}
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": local_ready,
        "live_splunk_mcp_verified": live.get("official_splunk_mcp_server_verified") is True,
        "live_splunk_verified": live.get("live_splunk_verified") is True,
        "mcp_protocol_adapter_verified": live.get("mcp_protocol_adapter_verified") is True,
        "official_splunk_mcp_server_verified": live.get("official_splunk_mcp_server_verified") is True,
        "live_proof_status": live.get("status", "missing"),
        "splunk_request_status": splunk_request.get("status", "missing"),
        "missing_evidence": missing,
        "evidence": rows,
        "commands": command_steps(),
        "boundary": "This command plan is advisory/readback only. The plan builder does not create accounts, configure credentials, import data, install apps, connect MCP, capture screenshots, update claims, publish, upload, or submit anything.",
        "approval_required": "Explicit user approval is required before credential handling, official Splunk MCP Server configuration, dashboard/screenshot capture, or live-MCP claim wording changes.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Live Splunk And MCP Proof Command Plan",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Live Splunk MCP verified: {str(payload['live_splunk_mcp_verified']).lower()}",
        f"Live Splunk verified: {str(payload['live_splunk_verified']).lower()}",
        f"Local MCP SDK adapter verified: {str(payload['mcp_protocol_adapter_verified']).lower()}",
        f"Official Splunk MCP Server verified: {str(payload['official_splunk_mcp_server_verified']).lower()}",
        f"Live proof status: {payload['live_proof_status']}",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        payload["approval_required"],
        "",
        "## Evidence",
        "",
    ]
    for item in payload["evidence"]:
        required = "required" if item["required"] else "optional"
        lines.append(f"- {item['path']} ({'present' if item['exists'] else 'missing'}, {required})")
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
  <title>Live Splunk And MCP Proof Command Plan</title>
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
    <h1>Live Splunk And MCP Proof Command Plan</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Boundary</h2>
      <p class="pending">{esc(payload['boundary'])}</p>
      <p>{esc(payload['approval_required'])}</p>
      <p>Live Splunk MCP verified: <span class="pending">{esc(payload['live_splunk_mcp_verified'])}</span></p>
      <p>Live Splunk verified: <span class="ready">{esc(payload['live_splunk_verified'])}</span></p>
      <p>Local MCP SDK adapter verified: <span class="ready">{esc(payload['mcp_protocol_adapter_verified'])}</span></p>
      <p>Official Splunk MCP Server verified: <span class="pending">{esc(payload['official_splunk_mcp_server_verified'])}</span></p>
      <p>Live proof status: <code>{esc(payload['live_proof_status'])}</code></p>
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
    write_json(reports / "latest_splunk_mcp_command_plan.json", payload)
    (reports / "latest_splunk_mcp_command_plan.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_splunk_mcp_command_plan.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "live_splunk_mcp_verified": payload["live_splunk_mcp_verified"],
        "html": "reports/latest_splunk_mcp_command_plan.html",
        "markdown": "reports/latest_splunk_mcp_command_plan.md",
        "json": "reports/latest_splunk_mcp_command_plan.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a non-executing live Splunk and MCP proof command plan.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
