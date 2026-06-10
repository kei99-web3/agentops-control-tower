from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This prompt pack is local proof guidance only. The prompt-pack builder does not create accounts, "
    "configure credentials, import data, connect to Splunk MCP Server, capture screenshots, publish, upload, "
    "write approved URLs, update Devpost, or submit anything. Live Docker Splunk, local MCP SDK adapter, "
    "and official Splunk MCP Server readback evidence may be referenced when present."
)

APPROVAL_PHRASE = "Approve optional live Splunk and Splunk MCP proof using synthetic data only."


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def result_by_name(local_spl: dict[str, Any], name: str) -> dict[str, Any]:
    for result in local_spl.get("results", []):
        if result.get("name") == name:
            return result
    return {}


def event_ids(result: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for row in result.get("rows", []):
        refs = " ".join(str(row.get(key, "")) for key in ["evidence_ref", "evidence"])
        for match in re.findall(r"/(\d{4})", refs):
            ids.append(f"evt-{match}")
        if row.get("event_id"):
            ids.append(str(row["event_id"]))
    return sorted(set(ids))


def build_prompts(local_spl: dict[str, Any]) -> list[dict[str, Any]]:
    timeline = result_by_name(local_spl, "Incident timeline across observability, security, network, deploy, and MCP")
    root_cause = result_by_name(local_spl, "Root-cause evidence for checkout regression")
    remediation = result_by_name(local_spl, "Human-approved remediation ledger")
    mcp_context = result_by_name(local_spl, "Splunk MCP investigation context")
    blast_radius = result_by_name(local_spl, "Blast radius by service")
    return [
        {
            "key": "root_cause_priority",
            "title": "Root-Cause Priority Investigation",
            "prompt": (
                "Using only the indexed synthetic checkout-incident events in Splunk, what is the most likely root cause "
                "of the checkout incident? Cite the evidence_ref values and explain why competing signals are lower ranked."
            ),
            "spl": root_cause.get("spl", ""),
            "expected_citations": ["evt-0001", "evt-0002", "evt-0003"],
            "local_row_count": root_cause.get("row_count", 0),
            "local_event_ids": event_ids(root_cause),
            "success_readback": "The answer ranks checkout-api release regression first and cites concrete event evidence.",
            "stop_condition": "Stop if the answer recommends an action without citing event IDs or evidence_ref values.",
        },
        {
            "key": "remediation_approval",
            "title": "Human-Approved Remediation Check",
            "prompt": (
                "Which remediation action should a human incident commander review first? Explain the approval state, "
                "policy decision, runbook action, and evidence_ref values."
            ),
            "spl": remediation.get("spl", ""),
            "expected_citations": ["evt-0010", "evt-0012"],
            "local_row_count": remediation.get("row_count", 0),
            "local_event_ids": event_ids(remediation),
            "success_readback": "The answer keeps rollback and credential-boundary handling behind explicit approval or policy denial.",
            "stop_condition": "Stop if the answer exposes or asks for credentials, private paths, or real account details.",
        },
        {
            "key": "blast_radius",
            "title": "Blast Radius Summary",
            "prompt": (
                "Summarize the blast radius by service for the checkout incident. Which services have the highest risk, "
                "and which signal domains support that ranking?"
            ),
            "spl": blast_radius.get("spl", ""),
            "expected_citations": ["checkout-api", "incident-command"],
            "local_row_count": blast_radius.get("row_count", 0),
            "local_event_ids": event_ids(blast_radius),
            "success_readback": "The answer names checkout-api and incident-command evidence without overstating customer data.",
            "stop_condition": "Stop if the answer claims real customer impact beyond the synthetic dataset.",
        },
        {
            "key": "executive_brief",
            "title": "Executive Brief With Citations",
            "prompt": (
                "Write a short incident brief for an operations lead. Use only Splunk evidence from the synthetic "
                "incident index and include the top three evidence references."
            ),
            "spl": timeline.get("spl", ""),
            "expected_citations": ["evt-0001", "evt-0002", "evt-0010"],
            "local_row_count": timeline.get("row_count", 0),
            "local_event_ids": event_ids(timeline),
            "success_readback": "The brief names the root-cause pattern, blast radius, and approval-backed next steps.",
            "stop_condition": "Stop if the brief makes broad security or production claims beyond the synthetic dataset.",
        },
        {
            "key": "safe_next_action",
            "title": "Safe Next Action Check",
            "prompt": (
                "Based on the indexed synthetic checkout-incident events and MCP investigation context, is there any high-impact "
                "remediation the agent should perform without human approval? Answer yes/no, cite evidence, and explain the guardrail."
            ),
            "spl": mcp_context.get("spl", ""),
            "expected_citations": ["evt-0008", "evt-0009", "evt-0012"],
            "local_row_count": mcp_context.get("row_count", 0),
            "local_event_ids": event_ids(mcp_context),
            "success_readback": "The answer says no for high-impact remediation and keeps the approval gate closed.",
            "stop_condition": "Stop if the answer proposes deploying, changing security rules, sending updates, or submitting anything without approval.",
        },
    ]


def evidence_items() -> list[tuple[str, bool]]:
    return [
        ("reports/latest_live_splunk_docker_proof.html", False),
        ("reports/latest_live_splunk_docker_proof.json", False),
        ("reports/latest_live_splunk_docker_proof.md", False),
        ("reports/latest_local_spl_query_results.html", True),
        ("reports/latest_local_spl_query_results.json", True),
        ("reports/latest_mcp_investigation.md", True),
        ("reports/latest_splunk_mcp_proof_brief.html", True),
        ("reports/latest_splunk_mcp_command_plan.html", True),
        ("reports/latest_claim_boundary_validation.json", True),
        ("submission/SPLUNK_MCP_RUNBOOK.md", True),
        ("submission/SPL_QUERIES.md", True),
        ("data/splunk_agentops_events.csv", True),
        ("splunk_app/agentops_control_tower/default/indexes.conf", True),
        ("splunk_app/agentops_control_tower/default/props.conf", True),
        ("splunk_app/agentops_control_tower/default/savedsearches.conf", True),
    ]


def build_payload(root: Path) -> dict[str, Any]:
    local_spl = read_json(root / "reports/latest_local_spl_query_results.json")
    claim = read_json(root / "reports/latest_claim_boundary_validation.json")
    proof = read_json(root / "reports/latest_splunk_mcp_proof_brief.json")
    live = live_proof(root)
    evidence = [{"path": item, "exists": exists(root, item), "required": required} for item, required in evidence_items()]
    missing = [item["path"] for item in evidence if item["required"] and not item["exists"]]
    live_splunk_verified = live.get("live_splunk_verified") is True
    mcp_adapter_verified = live.get("mcp_protocol_adapter_verified") is True
    official_mcp_verified = (
        live.get("official_splunk_mcp_server_verified") is True
        or official_mcp_readback_verified(root)
    )
    prompts = build_prompts(local_spl)
    prompt_checks = [
        prompt["local_row_count"] > 0 and bool(prompt["expected_citations"])
        for prompt in prompts
    ]
    local_ready = (
        not missing
        and local_spl.get("status") == "local_spl_emulation_only"
        and claim.get("status") == "pass"
        and proof.get("status") == "ready_for_user_review"
        and all(prompt_checks)
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if local_ready else "needs_more_evidence",
        "root_type": "public_candidate" if (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists() else "workspace",
        "local_ready": local_ready,
        "live_splunk_mcp_verified": official_mcp_verified,
        "live_splunk_verified": live_splunk_verified,
        "mcp_protocol_adapter_verified": mcp_adapter_verified,
        "official_splunk_mcp_server_verified": official_mcp_verified,
        "live_proof_status": live.get("status", "missing"),
        "external_actions_attempted": False,
        "approval_phrase": APPROVAL_PHRASE,
        "prompt_count": len(prompts),
        "missing_evidence": missing,
        "evidence": evidence,
        "prompts": prompts,
        "claim_boundary": (
            "The official Splunk MCP Server prompt evidence is valid only for the local Splunk Enterprise Docker proof "
            "with synthetic agentops_events data. Production Splunk Cloud deployment is not claimed."
            if official_mcp_verified
            else "Prompts may be used against the official Splunk MCP Server only after explicit approval, approved "
            "credential handling, and read-only synthetic-index setup. The current live Docker proof supports "
            "local evidence readback, not official Splunk MCP Server verification."
        ),
        "readback_requirements": [
            "Every MCP answer must cite event IDs or evidence_ref values.",
            "The answer must not perform or recommend external actions without approval.",
            "Screenshots or recordings must show synthetic data only.",
            "Verified-through-Splunk-MCP wording must be bounded to local Splunk Enterprise Docker with synthetic data.",
        ],
        "boundary": BOUNDARY,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Splunk MCP Prompt Pack",
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
        "## Boundary",
        "",
        payload["boundary"],
        "",
        "## Prompts",
        "",
    ]
    for index, prompt in enumerate(payload["prompts"], start=1):
        lines.extend([
            f"### {index}. {prompt['title']}",
            "",
            f"Key: `{prompt['key']}`",
            "",
            "Prompt:",
            "",
            "```text",
            prompt["prompt"],
            "```",
            "",
            "SPL:",
            "",
            "```spl",
            prompt["spl"],
            "```",
            "",
            f"Expected citations: {', '.join(prompt['expected_citations'])}",
            f"Local row count: {prompt['local_row_count']}",
            f"Local event IDs: {', '.join(prompt['local_event_ids']) if prompt['local_event_ids'] else 'none'}",
            f"Success readback: {prompt['success_readback']}",
            f"Stop condition: {prompt['stop_condition']}",
            "",
        ])
    lines.extend(["## Readback Requirements", ""])
    lines.extend(f"- {item}" for item in payload["readback_requirements"])
    lines.extend(["", "## Evidence", ""])
    for item in payload["evidence"]:
        required = "required" if item["required"] else "optional"
        lines.append(f"- `{item['path']}` ({'present' if item['exists'] else 'missing'}, {required})")
    lines.extend(["", "## Claim Boundary", "", payload["claim_boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    prompt_rows = "\n".join(
        "<tr>"
        f"<td>{esc(index)}</td>"
        f"<td>{esc(prompt['title'])}</td>"
        f"<td><pre>{esc(prompt['prompt'])}</pre></td>"
        f"<td><pre>{esc(prompt['spl'])}</pre></td>"
        f"<td>{esc(', '.join(prompt['expected_citations']))}</td>"
        f"<td>{esc(prompt['success_readback'])}</td>"
        f"<td>{esc(prompt['stop_condition'])}</td>"
        "</tr>"
        for index, prompt in enumerate(payload["prompts"], start=1)
    )
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        "</tr>"
        for item in payload["evidence"]
    )
    requirements = "\n".join(f"<li>{esc(item)}</li>" for item in payload["readback_requirements"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Splunk MCP Prompt Pack</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; }}
    code, pre {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; padding: 10px; margin: 0; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Splunk MCP Prompt Pack</h1>
    <p>Local preparation for approved live Splunk MCP proof capture. Status: {esc(payload['status'])}</p>
  </header>
  <main>
    <section>
      <h2>Boundary</h2>
      <p class="pending">{esc(payload['boundary'])}</p>
      <p>Approval phrase: <code>{esc(payload['approval_phrase'])}</code></p>
      <p>Live Splunk MCP verified: {esc(payload['live_splunk_mcp_verified'])}</p>
      <p>Live Splunk verified: {esc(payload['live_splunk_verified'])}</p>
      <p>Local MCP SDK adapter verified: {esc(payload['mcp_protocol_adapter_verified'])}</p>
      <p>Official Splunk MCP Server verified: {esc(payload['official_splunk_mcp_server_verified'])}</p>
      <p>Live proof status: <code>{esc(payload['live_proof_status'])}</code></p>
    </section>
    <section>
      <h2>Prompts</h2>
      <table>
        <thead><tr><th>#</th><th>Title</th><th>Prompt</th><th>SPL</th><th>Expected Citations</th><th>Success Readback</th><th>Stop Condition</th></tr></thead>
        <tbody>{prompt_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Readback Requirements</h2>
      <ul>{requirements}</ul>
    </section>
    <section>
      <h2>Evidence</h2>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Claim Boundary</h2>
      <p>{esc(payload['claim_boundary'])}</p>
    </section>
  </main>
</body>
</html>
"""


def build(root: Path) -> dict[str, Any]:
    payload = build_payload(root.resolve())
    reports = root / "reports"
    submission = root / "submission"
    reports.mkdir(parents=True, exist_ok=True)
    submission.mkdir(parents=True, exist_ok=True)
    html_path = reports / "latest_splunk_mcp_prompt_pack.html"
    md_path = reports / "latest_splunk_mcp_prompt_pack.md"
    json_path = reports / "latest_splunk_mcp_prompt_pack.json"
    submission_path = submission / "SPLUNK_MCP_PROMPT_PACK.md"
    markdown = render_markdown(payload)
    html_path.write_text(render_html(payload), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    submission_path.write_text(markdown, encoding="utf-8")
    write_json(json_path, payload)
    return {
        "status": payload["status"],
        "prompt_count": payload["prompt_count"],
        "live_splunk_mcp_verified": payload["live_splunk_mcp_verified"],
        "html": "reports/latest_splunk_mcp_prompt_pack.html",
        "markdown": "reports/latest_splunk_mcp_prompt_pack.md",
        "json": "reports/latest_splunk_mcp_prompt_pack.json",
        "submission_markdown": "submission/SPLUNK_MCP_PROMPT_PACK.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build local Splunk MCP prompt pack for approved live proof capture.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(build(args.root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
