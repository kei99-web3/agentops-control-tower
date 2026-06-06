from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_kpis(analysis: dict[str, Any]) -> str:
    items = [
        ("Events", analysis.get("event_count", 0)),
        ("Incidents", analysis.get("incident_count", 0)),
        ("Services", analysis.get("service_count", 0)),
        ("Blocked", analysis.get("blocked_count", 0)),
        ("Approval Queue", analysis.get("approval_queue_count", 0)),
        ("Max Risk", analysis.get("max_risk", 0)),
    ]
    return "\n".join(
        f'<div class="metric"><span>{esc(label)}</span><strong>{esc(value)}</strong></div>'
        for label, value in items
    )


def render_incidents(analysis: dict[str, Any]) -> str:
    rows = []
    for incident in analysis.get("incident_summaries", [])[:5]:
        rows.append(
            "<tr>"
            f"<td>{esc(incident.get('incident_id', ''))}</td>"
            f"<td>{esc(incident.get('status', ''))}</td>"
            f"<td>{esc(incident.get('max_risk', ''))}</td>"
            f"<td>{esc(incident.get('primary_root_cause', ''))}</td>"
            f"<td>{esc(incident.get('recommended_human_action', ''))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_approval_queue(analysis: dict[str, Any]) -> str:
    rows = []
    for item in analysis.get("approval_queue", [])[:5]:
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('event_id', ''))}</td>"
            f"<td>{esc(item.get('service', ''))}</td>"
            f"<td>{esc(item.get('risk_score', ''))}</td>"
            f"<td>{esc(item.get('policy_decision', ''))}</td>"
            f"<td>{esc(item.get('recommended_human_action', ''))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_query_cards(query_pack: dict[str, Any]) -> str:
    cards: list[str] = []
    for result in query_pack.get("results", []):
        rows = result.get("rows", [])
        sample = rows[0] if rows else {}
        sample_bits = []
        for key in ["component", "event_type", "risk_score", "policy_decision", "approval_state"]:
            if key in sample:
                sample_bits.append(f"{key}: {sample[key]}")
        cards.append(
            '<div class="query">'
            f"<h3>{esc(result.get('name', 'Query'))}</h3>"
            f"<p>{esc(result.get('row_count', len(rows)))} rows returned over synthetic CSV.</p>"
            f"<pre>{esc(result.get('spl', ''))}</pre>"
            f"<small>{esc(' | '.join(sample_bits) if sample_bits else 'No sample row')}</small>"
            "</div>"
        )
    return "\n".join(cards)


def build_payload(root: Path) -> dict[str, Any]:
    analysis = read_json(root / "reports" / "latest_analysis.json")
    query_pack = read_json(root / "reports" / "latest_local_spl_query_results.json")
    return {
        "analysis": analysis,
        "query_pack": query_pack,
        "validation_status": "ready_for_user_review",
        "external_gates": [
            "Public GitHub repository",
            "Public demo video upload",
            "Devpost final submission",
            "Splunk account / license",
            "Splunk MCP Server configuration",
        ],
    }


def render_html(payload: dict[str, Any]) -> str:
    analysis = payload["analysis"]
    query_pack = payload["query_pack"]
    gates = "\n".join(f"<li>{esc(item)}</li>" for item in payload["external_gates"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agentic Incident Command Center Demo Tour</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --ink: #17202a;
      --muted: #5f6d7c;
      --line: #dbe3ec;
      --panel: #ffffff;
      --accent: #127c76;
      --danger: #b3261e;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: var(--bg); color: var(--ink); line-height: 1.55; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid var(--accent); }}
    header p {{ color: #dbe3ec; max-width: 920px; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    h1, h2, h3 {{ margin-top: 0; }}
    .scene {{ color: var(--accent); font-weight: 700; text-transform: uppercase; font-size: 12px; letter-spacing: 0; }}
    .metrics {{ display: grid; grid-template-columns: repeat(6, minmax(120px, 1fr)); gap: 12px; }}
    .metric {{ border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: #fbfcfe; }}
    .metric span {{ display: block; color: var(--muted); font-size: 13px; }}
    .metric strong {{ display: block; font-size: 28px; margin-top: 4px; }}
    .split {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; align-items: start; }}
    .queries {{ display: grid; grid-template-columns: repeat(2, minmax(240px, 1fr)); gap: 14px; }}
    .query {{ border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: #fbfcfe; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: 13px; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #edf3f6; border-radius: 6px; padding: 10px; font-size: 13px; }}
    .boundary {{ border-left: 5px solid var(--danger); }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
    @media (max-width: 820px) {{
      header {{ padding: 22px 18px; }}
      main {{ padding: 14px; }}
      .metrics, .split, .queries {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <p class="scene">Devpost video path</p>
    <h1>Agentic Incident Command Center Demo Tour</h1>
    <p>A recording-friendly walkthrough for showing a synthetic checkout incident, cross-domain Splunk evidence, root-cause ranking, human-approved remediation, and the Splunk MCP story without exposing private data or claiming live MCP verification before approval.</p>
  </header>
  <main>
    <section>
      <p class="scene">Scene 1 / Problem</p>
      <h2>Incidents move faster than manual triage</h2>
      <p>During an outage, evidence is scattered across deploy logs, APM, database telemetry, edge networking, security detections, and MCP tool calls. Agentic Incident Command Center turns those signals into one Splunk-grounded incident narrative with human-approved remediation.</p>
    </section>
    <section>
      <p class="scene">Scene 2 / Incident Command Summary</p>
      <h2>Operational snapshot</h2>
      <div class="metrics">{render_kpis(analysis)}</div>
    </section>
    <section>
      <p class="scene">Scene 3 / Incident Review</p>
      <h2>What needs attention?</h2>
      <table>
        <thead><tr><th>Incident</th><th>Status</th><th>Max Risk</th><th>Root cause</th><th>Human action</th></tr></thead>
        <tbody>{render_incidents(analysis)}</tbody>
      </table>
    </section>
    <section>
      <p class="scene">Scene 4 / Human Approval Queue</p>
      <h2>Evidence-backed remediation decisions</h2>
      <table>
        <thead><tr><th>Event</th><th>Service</th><th>Risk</th><th>Decision</th><th>Recommended action</th></tr></thead>
        <tbody>{render_approval_queue(analysis)}</tbody>
      </table>
    </section>
    <section>
      <p class="scene">Scene 5 / Local SPL Proof</p>
      <h2>Query intent before live Splunk setup</h2>
      <p>{esc(query_pack.get('note', 'Local query proof over generated CSV.'))}</p>
      <div class="queries">{render_query_cards(query_pack)}</div>
    </section>
    <section class="boundary">
      <p class="scene">Scene 6 / Splunk MCP Boundary</p>
      <h2>Designed for Splunk MCP Server</h2>
      <p>In the live version, incident events are indexed in Splunk, Splunk MCP Server exposes approved query tools, and an AI incident commander answers review questions with event IDs, risk scores, root-cause evidence, policy decisions, and evidence references.</p>
      <p>Current status: <code>{esc(payload['validation_status'])}</code>. This local demo uses synthetic data and local SPL-equivalent proof. Live Splunk MCP verification still requires approval.</p>
    </section>
    <section>
      <p class="scene">Submission Gates</p>
      <h2>Still pending user approval</h2>
      <ul>{gates}</ul>
    </section>
  </main>
</body>
</html>
"""


def run(root: Path) -> dict[str, str]:
    payload = build_payload(root)
    html_path = root / "reports" / "latest_demo_tour.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(payload), encoding="utf-8")
    return {"status": "ok", "html": "reports/latest_demo_tour.html"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a recording-friendly demo tour HTML page.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    print(json.dumps(run(Path(args.root).resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
