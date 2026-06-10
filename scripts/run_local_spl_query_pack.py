from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


TIMELINE_FIELDS = [
    "timestamp",
    "signal_domain",
    "service",
    "event_type",
    "risk_score",
    "evidence_ref",
    "message",
]


def load_events(csv_path: Path) -> list[dict[str, Any]]:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["risk_score"] = int(row.get("risk_score") or 0)
        row["root_cause_weight"] = int(row.get("root_cause_weight") or 0)
        row["requires_human_approval_bool"] = str(row.get("requires_human_approval", "")).lower() == "true"
        row["tags_list"] = [tag for tag in row.get("tags", "").split(";") if tag]
    return rows


def table_rows(events: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
    return [{field: event.get(field, "") for field in fields} for event in events]


def incident_timeline(events: list[dict[str, Any]]) -> dict[str, Any]:
    filtered = sorted(
        [event for event in events if event.get("incident_id") == "inc-checkout-20260603-0900"],
        key=lambda event: event["timestamp"],
    )
    return {
        "name": "Incident timeline across observability, security, network, deploy, and MCP",
        "spl": 'index=agentops_events incident_id="inc-checkout-20260603-0900" | sort _time | table _time signal_domain service event_type risk_score evidence_ref message',
        "rows": table_rows(filtered, TIMELINE_FIELDS),
    }


def root_cause_evidence(events: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}
    for event in events:
        candidate = event.get("root_cause_candidate", "")
        if candidate in {"", "incident_response_coordination", "governance_control", "investigation_context"}:
            continue
        item = groups.setdefault(candidate, {
            "root_cause_candidate": candidate,
            "evidence_score": 0,
            "domains": set(),
            "services": set(),
            "evidence": [],
        })
        item["evidence_score"] += event["root_cause_weight"]
        item["domains"].add(event.get("signal_domain", ""))
        item["services"].add(event.get("service", ""))
        item["evidence"].append(event.get("evidence_ref", ""))
    rows = []
    for item in groups.values():
        rows.append({
            "root_cause_candidate": item["root_cause_candidate"],
            "evidence_score": item["evidence_score"],
            "domains": ", ".join(sorted(item["domains"])),
            "services": ", ".join(sorted(item["services"])),
            "evidence": ", ".join(item["evidence"]),
        })
    rows.sort(key=lambda row: row["evidence_score"], reverse=True)
    return {
        "name": "Root-cause evidence for checkout regression",
        "spl": 'index=agentops_events incident_id="inc-checkout-20260603-0900" root_cause_candidate!="incident_response_coordination" | stats sum(root_cause_weight) as evidence_score values(signal_domain) as domains values(evidence_ref) as evidence by root_cause_candidate | sort -evidence_score',
        "rows": rows,
    }


def remediation_ledger(events: list[dict[str, Any]]) -> dict[str, Any]:
    filtered = [
        event for event in events
        if event.get("requires_human_approval_bool") or event.get("policy_decision") == "deny"
    ]
    filtered.sort(key=lambda event: event["risk_score"], reverse=True)
    fields = [
        "timestamp",
        "service",
        "external_action",
        "approval_state",
        "policy_decision",
        "runbook_action",
        "evidence_ref",
    ]
    return {
        "name": "Human-approved remediation ledger",
        "spl": 'index=agentops_events requires_human_approval=true OR policy_decision="deny" | sort -risk_score | table _time service external_action approval_state policy_decision runbook_action evidence_ref',
        "rows": table_rows(filtered, fields),
    }


def mcp_investigation_context(events: list[dict[str, Any]]) -> dict[str, Any]:
    filtered = [
        event for event in events
        if event.get("mcp_tool") != "none" or event.get("signal_domain") == "ai_correlation"
    ]
    fields = ["timestamp", "component", "mcp_tool", "event_type", "evidence_ref", "recommended_human_action"]
    return {
        "name": "Splunk MCP investigation context",
        "spl": 'index=agentops_events mcp_tool!="none" OR signal_domain="ai_correlation" | table _time component mcp_tool event_type evidence_ref recommended_human_action',
        "rows": table_rows(filtered, fields),
    }


def blast_radius_by_service(events: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "max_risk": 0, "domains": set()})
    for event in events:
        service = event.get("service", "")
        item = groups[service]
        item["count"] += 1
        item["max_risk"] = max(item["max_risk"], event["risk_score"])
        item["domains"].add(event.get("signal_domain", ""))
    rows = [
        {
            "service": service,
            "count": item["count"],
            "max_risk": item["max_risk"],
            "domains": ", ".join(sorted(item["domains"])),
        }
        for service, item in groups.items()
    ]
    rows.sort(key=lambda row: row["max_risk"], reverse=True)
    return {
        "name": "Blast radius by service",
        "spl": 'index=agentops_events incident_id="inc-checkout-20260603-0900" | stats count max(risk_score) as max_risk values(signal_domain) as domains by service | sort -max_risk',
        "rows": rows,
    }


def build_query_pack(events: list[dict[str, Any]]) -> dict[str, Any]:
    results = [
        incident_timeline(events),
        root_cause_evidence(events),
        remediation_ledger(events),
        mcp_investigation_context(events),
        blast_radius_by_service(events),
    ]
    return {
        "status": "local_spl_emulation_only",
        "note": "These tables emulate the demo SPL queries over the generated CSV. They are not a substitute for live Splunk verification.",
        "source": "data/splunk_agentops_events.csv",
        "event_count": len(events),
        "results": [{**result, "row_count": len(result["rows"])} for result in results],
    }


def render_html(path: Path, payload: dict[str, Any]) -> None:
    sections: list[str] = []
    for result in payload["results"]:
        rows = result["rows"]
        if rows:
            fields = list(rows[0].keys())
            head = "".join(f"<th>{esc(field)}</th>" for field in fields)
            body = "\n".join(
                "<tr>" + "".join(f"<td>{esc(row.get(field, ''))}</td>" for field in fields) + "</tr>"
                for row in rows
            )
            table = f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
        else:
            table = "<p>No rows.</p>"
        sections.append(
            f"<section><h2>{esc(result['name'])}</h2>"
            f"<p>Rows: {result['row_count']}</p>"
            f"<pre>{esc(result['spl'])}</pre>{table}</section>"
        )

    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Local SPL Query Results</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; }}
    header {{ background: #14212b; color: #fff; padding: 28px 36px; border-bottom: 4px solid #087568; }}
    main {{ max-width: 1160px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 18px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ color: #5f6d7c; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #edf3f6; border-radius: 6px; padding: 12px; }}
  </style>
</head>
<body>
  <header>
    <h1>Local SPL Query Results</h1>
    <p>{esc(payload['note'])}</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <p>Status: {esc(payload['status'])}</p>
      <p>Source: {esc(payload['source'])}</p>
      <p>Events: {payload['event_count']}</p>
    </section>
    {''.join(sections)}
  </main>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run(root: Path) -> dict[str, Any]:
    events = load_events(root / "data" / "splunk_agentops_events.csv")
    payload = build_query_pack(events)
    json_path = root / "reports" / "latest_local_spl_query_results.json"
    html_path = root / "reports" / "latest_local_spl_query_results.html"
    write_json(json_path, payload)
    render_html(html_path, payload)
    return {
        "status": payload["status"],
        "event_count": payload["event_count"],
        "query_count": len(payload["results"]),
        "json": "reports/latest_local_spl_query_results.json",
        "html": "reports/latest_local_spl_query_results.html",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local SPL-equivalent incident command demo queries over generated CSV.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
