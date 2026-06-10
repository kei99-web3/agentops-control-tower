from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This brief is local proof-decision support only. The brief builder does not create accounts, "
    "configure credentials, import data, install apps, connect MCP, capture screenshots, publish, "
    "upload, update claims, write approved URLs, update Devpost, or submit anything. When live proof "
    "evidence exists, it is limited to approved ephemeral Docker Splunk, synthetic data, and a local "
    "read-only MCP SDK adapter unless the official Splunk MCP Server field says otherwise."
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
            "checksum match: yes",
            "mcp connection status: connected",
            "tool used: `splunk_run_query`",
            "official splunk mcp server was installed and verified",
            "production splunk cloud deployment is not claimed",
        ]
    )


def evidence_items() -> list[tuple[str, bool]]:
    return [
        ("reports/latest_splunk_mcp_command_plan.html", True),
        ("reports/latest_splunk_app_package_manifest.html", True),
        ("reports/latest_live_splunk_docker_proof.html", False),
        ("reports/latest_live_splunk_docker_proof.json", False),
        ("reports/latest_live_splunk_docker_proof.md", False),
        ("reports/latest_local_spl_query_results.html", True),
        ("reports/latest_local_spl_query_results.json", True),
        ("reports/latest_claim_boundary_validation.html", True),
        ("reports/latest_claim_boundary_validation.json", True),
        ("reports/latest_mcp_investigation.md", True),
        ("submission/SPLUNK_MCP_RUNBOOK.md", True),
        ("submission/SPL_QUERIES.md", True),
        ("data/splunk_agentops_events.csv", True),
        ("splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml", True),
        ("splunk_app/agentops_control_tower/default/savedsearches.conf", True),
    ]


def proof_success_criteria() -> list[dict[str, str]]:
    return [
        {
            "criterion": "Synthetic data isolation",
            "evidence": "Only data/splunk_agentops_events.csv is imported into the approved agentops_events index.",
            "acceptance": "No real workspace logs, customer data, local paths, credentials, or account pages are shown.",
        },
        {
            "criterion": "Live SPL query proof",
            "evidence": "Incident timeline, root-cause evidence, MCP Remediation Ledger, Splunk MCP investigation context, and blast-radius SPL queries return rows.",
            "acceptance": "Returned rows include incident IDs, services, risk scores, root-cause candidates, policy decisions, approval states, and evidence refs.",
        },
        {
            "criterion": "Splunk app proof",
            "evidence": "The local Splunk app candidate or copied dashboard shows the Agentic Incident Command Center view.",
            "acceptance": "The dashboard points only at the approved synthetic index and mirrors the local proof story.",
        },
        {
            "criterion": "MCP-assisted investigation proof",
            "evidence": "Splunk MCP Server answers the approval-priority question from indexed synthetic events.",
            "acceptance": "The answer cites event IDs and evidence refs instead of making unsupported recommendations.",
        },
        {
            "criterion": "Claim boundary upgrade",
            "evidence": "Claim validation and submission validation pass after any wording changes.",
            "acceptance": "Live Splunk/MCP wording is used only after the live evidence above is captured and reviewed.",
        },
    ]


def approval_steps() -> list[dict[str, str]]:
    return [
        {
            "step": "Approve live proof scope",
            "owner": "User",
            "action": "Approve optional live Splunk and Splunk MCP proof using synthetic data only.",
            "verification": "Approval explicitly covers account/license use, synthetic import, read-only MCP scope, and proof capture.",
        },
        {
            "step": "Prepare local proof inputs",
            "owner": "Codex/local",
            "action": "Run the local demo, SPL-equivalent query pack, Splunk app validation, and package manifest.",
            "verification": "latest_local_spl_query_results and latest_splunk_app_package_manifest are ready_for_user_review.",
        },
        {
            "step": "Create approved Splunk scope",
            "owner": "User/manual",
            "action": "Use approved Splunk access and create/import only the synthetic agentops_events dataset.",
            "verification": "The index contains the expected synthetic rows and no private or account data.",
        },
        {
            "step": "Capture SPL proof",
            "owner": "User/manual",
            "action": "Run the SPL queries from submission/SPL_QUERIES.md.",
            "verification": "Screenshots or recording show incident timeline, root-cause evidence, remediation ledger, MCP investigation context, and blast-radius rows.",
        },
        {
            "step": "Configure Splunk MCP read-only proof",
            "owner": "User/manual",
            "action": "Configure Splunk MCP Server with approved read-only scope for the synthetic index.",
            "verification": "The MCP answer cites event IDs and evidence refs and does not perform external actions.",
        },
        {
            "step": "Upgrade public claims only after proof",
            "owner": "Codex/local",
            "action": "Update Devpost/video wording only if proof evidence is reviewed, then rerun validators.",
            "verification": "validate_claim_boundaries.py and validate_submission_packet.py pass.",
        },
    ]


def screen_safety_checks() -> list[str]:
    return [
        "Show only the Splunk search/dashboard, local demo pages, and synthetic event evidence needed for the proof.",
        "Hide browser tabs, account settings, billing, tokens, hostnames, private paths, terminals with secrets, and personal data.",
        "Use synthetic event IDs and evidence refs as the narration anchor.",
        "Do not show credential setup screens or MCP configuration secrets in the video.",
        "Do not imply live Splunk/MCP verification unless the proof has actually been captured.",
    ]


def stop_conditions() -> list[str]:
    return [
        "Stop if Splunk access, cost, license, or credential scope is not explicitly approved.",
        "Stop if the data source is anything other than the generated synthetic CSV.",
        "Stop if any screenshot or recording exposes credentials, account pages, local paths, or private data.",
        "Stop if MCP can access more than the approved read-only synthetic-data scope.",
        "Stop if claim-boundary validation fails after wording changes.",
        "Stop before public repo publication, video upload, URL writeback, or Devpost submit unless those separate gates are approved.",
    ]


def build_payload(root: Path) -> dict[str, Any]:
    command_plan = read_json(root / "reports/latest_splunk_mcp_command_plan.json")
    app_manifest = read_json(root / "reports/latest_splunk_app_package_manifest.json")
    local_spl = read_json(root / "reports/latest_local_spl_query_results.json")
    claim = read_json(root / "reports/latest_claim_boundary_validation.json")
    live = live_proof(root)
    evidence = [{"path": item, "exists": exists(root, item), "required": required} for item, required in evidence_items()]
    missing = [item["path"] for item in evidence if item["required"] and not item["exists"]]
    live_splunk_verified = live.get("live_splunk_verified") is True
    mcp_adapter_verified = live.get("mcp_protocol_adapter_verified") is True
    official_mcp_verified = (
        live.get("official_splunk_mcp_server_verified") is True
        or official_mcp_readback_verified(root)
    )
    local_ready = (
        not missing
        and command_plan.get("status") == "ready_for_user_review"
        and app_manifest.get("status") in {"ready_for_user_review", "local_package_ready_for_review"}
        and local_spl.get("status") == "local_spl_emulation_only"
        and len(local_spl.get("results", [])) >= 4
        and claim.get("status") == "pass"
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_ready": local_ready,
        "live_splunk_mcp_verified": official_mcp_verified,
        "live_splunk_verified": live_splunk_verified,
        "mcp_protocol_adapter_verified": mcp_adapter_verified,
        "official_splunk_mcp_server_verified": official_mcp_verified,
        "live_proof_status": live.get("status", "missing"),
        "live_proof_rows": {
            "synthetic_row_count": live.get("synthetic_row_count", "missing"),
            "indexed_row_count": live.get("indexed_row_count", "missing"),
            "failed_query_count": live.get("failed_query_count", "missing"),
        },
        "approval_phrase": "Approve optional live Splunk and Splunk MCP proof using synthetic data only.",
        "grant_fit": (
            "The live Docker proof strengthens the Splunk data story, the local MCP SDK adapter demonstrates "
            "read-only cited investigation behavior, and the official Splunk MCP Server readback confirms the "
            "bonus proof in a reproducible local Splunk Enterprise Docker environment using synthetic data only. "
            "Production Splunk Cloud deployment is not claimed."
            if official_mcp_verified
            else "The live Docker proof strengthens the Splunk data story, and the local MCP SDK adapter demonstrates "
            "read-only cited investigation behavior. The official Splunk MCP Server bonus claim remains pending until "
            "the Splunkbase app is installed and verified with approved credential handling."
        ),
        "missing_evidence": missing,
        "evidence": evidence,
        "proof_success_criteria": proof_success_criteria(),
        "approval_steps": approval_steps(),
        "screen_safety_checks": screen_safety_checks(),
        "stop_conditions": stop_conditions(),
        "claim_upgrade_rule": (
            "Use verified-through-Splunk-MCP wording only when it is explicitly bounded to the local Splunk Enterprise "
            "Docker proof with synthetic data. Do not claim production Splunk Cloud deployment."
            if official_mcp_verified
            else "Use verified-through-Splunk-MCP wording only after the official Splunk MCP Server app is installed, "
            "read-only synthetic-index answers are captured, reviewed, and claim-boundary validation passes. The "
            "current approved evidence supports only 'live Splunk Docker proof captured' and 'local MCP SDK adapter verified'."
        ),
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Live Splunk/MCP Proof Brief",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Live Splunk MCP verified: {str(payload['live_splunk_mcp_verified']).lower()}",
        f"Live Splunk verified: {str(payload['live_splunk_verified']).lower()}",
        f"Local MCP SDK adapter verified: {str(payload['mcp_protocol_adapter_verified']).lower()}",
        f"Official Splunk MCP Server verified: {str(payload['official_splunk_mcp_server_verified']).lower()}",
        f"Live proof status: {payload['live_proof_status']}",
        f"Approval phrase: {payload['approval_phrase']}",
        "",
        "## Live Proof Rows",
        "",
        f"- Synthetic rows: `{payload['live_proof_rows']['synthetic_row_count']}`",
        f"- Indexed rows: `{payload['live_proof_rows']['indexed_row_count']}`",
        f"- Failed live SPL queries: `{payload['live_proof_rows']['failed_query_count']}`",
        "",
        "## Why This Matters",
        "",
        payload["grant_fit"],
        "",
        "## Evidence",
        "",
    ]
    for item in payload["evidence"]:
        required = "required" if item["required"] else "optional"
        lines.append(f"- `{item['path']}` ({'present' if item['exists'] else 'missing'}, {required})")
    lines.extend(["", "## Proof Success Criteria", ""])
    for item in payload["proof_success_criteria"]:
        lines.extend([
            f"### {item['criterion']}",
            "",
            f"Evidence: {item['evidence']}",
            "",
            f"Acceptance: {item['acceptance']}",
            "",
        ])
    lines.extend(["## Approval Steps", ""])
    for index, item in enumerate(payload["approval_steps"], start=1):
        lines.extend([
            f"{index}. {item['step']} ({item['owner']})",
            "",
            f"Action: {item['action']}",
            "",
            f"Verification: {item['verification']}",
            "",
        ])
    lines.extend(["## Screen Safety Checks", ""])
    for item in payload["screen_safety_checks"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Stop Conditions", ""])
    for item in payload["stop_conditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Claim Upgrade Rule", "", payload["claim_upgrade_rule"], "", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        "</tr>"
        for item in payload["evidence"]
    )
    criteria_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['criterion'])}</td>"
        f"<td>{esc(item['evidence'])}</td>"
        f"<td>{esc(item['acceptance'])}</td>"
        "</tr>"
        for item in payload["proof_success_criteria"]
    )
    step_rows = "\n".join(
        "<tr>"
        f"<td>{esc(index)}</td>"
        f"<td>{esc(item['step'])}</td>"
        f"<td>{esc(item['owner'])}</td>"
        f"<td>{esc(item['action'])}</td>"
        f"<td>{esc(item['verification'])}</td>"
        "</tr>"
        for index, item in enumerate(payload["approval_steps"], start=1)
    )
    safety_items = "\n".join(f"<li>{esc(item)}</li>" for item in payload["screen_safety_checks"])
    stops = "\n".join(f"<li>{esc(item)}</li>" for item in payload["stop_conditions"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Live Splunk/MCP Proof Brief</title>
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
    <h1>Live Splunk/MCP Proof Brief</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Decision</h2>
      <p>Approval phrase: <strong>{esc(payload['approval_phrase'])}</strong></p>
      <p>Live Splunk MCP verified: <span class="pending">{esc(payload['live_splunk_mcp_verified'])}</span></p>
      <p>Live Splunk verified: <span class="ready">{esc(payload['live_splunk_verified'])}</span></p>
      <p>Local MCP SDK adapter verified: <span class="ready">{esc(payload['mcp_protocol_adapter_verified'])}</span></p>
      <p>Official Splunk MCP Server verified: <span class="pending">{esc(payload['official_splunk_mcp_server_verified'])}</span></p>
      <p>Live proof status: <code>{esc(payload['live_proof_status'])}</code>; rows: {esc(payload['live_proof_rows']['indexed_row_count'])}/{esc(payload['live_proof_rows']['synthetic_row_count'])}; failed queries: {esc(payload['live_proof_rows']['failed_query_count'])}</p>
      <p>{esc(payload['grant_fit'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Evidence</h2>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Proof Success Criteria</h2>
      <table>
        <thead><tr><th>Criterion</th><th>Evidence</th><th>Acceptance</th></tr></thead>
        <tbody>{criteria_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Approval Steps</h2>
      <table>
        <thead><tr><th>#</th><th>Step</th><th>Owner</th><th>Action</th><th>Verification</th></tr></thead>
        <tbody>{step_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Screen Safety Checks</h2>
      <ul>{safety_items}</ul>
    </section>
    <section>
      <h2>Stop Conditions</h2>
      <ul>{stops}</ul>
    </section>
    <section>
      <h2>Claim Upgrade Rule</h2>
      <p>{esc(payload['claim_upgrade_rule'])}</p>
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
    write_json(reports / "latest_splunk_mcp_proof_brief.json", payload)
    (reports / "latest_splunk_mcp_proof_brief.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_splunk_mcp_proof_brief.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "live_splunk_mcp_verified": payload["live_splunk_mcp_verified"],
        "missing_evidence": payload["missing_evidence"],
        "html": "reports/latest_splunk_mcp_proof_brief.html",
        "markdown": "reports/latest_splunk_mcp_proof_brief.md",
        "json": "reports/latest_splunk_mcp_proof_brief.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a live Splunk/MCP proof decision brief.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
