from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


LOCAL_EVIDENCE = [
    "README.md",
    "LICENSE",
    "architecture_diagram.md",
    "assets/dashboard_preview.png",
    "prototype/agentops_control_tower.py",
    "reports/latest_control_tower.html",
    "reports/latest_demo_tour.html",
    "reports/latest_video_readiness.html",
    "reports/latest_devpost_submission_packet.html",
    "reports/latest_local_spl_query_results.html",
    "submission/DEVPOST_FIELD_MAP.md",
    "submission/DEVPOST_SUBMISSION_DRAFT.md",
    "submission/FINAL_SUBMISSION_CHECKLIST.md",
    "submission/JUDGING_ALIGNMENT.md",
    "submission/OFFICIAL_REQUIREMENTS_AUDIT.md",
    "submission/SPL_QUERIES.md",
    "submission/VIDEO_RECORDING_RUNBOOK.md",
    "splunk_app/agentops_control_tower/default/app.conf",
    "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
    "splunk_app/agentops_control_tower/default/savedsearches.conf",
]

PUBLIC_CANDIDATE_EVIDENCE = [
    "public_repo_candidate/agentops-control-tower/README.md",
    "public_repo_candidate/agentops-control-tower/LICENSE",
    "public_repo_candidate/agentops-control-tower/architecture_diagram.md",
    "public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md",
    "public_repo_candidate/agentops-control-tower/reports/latest_demo_tour.html",
    "public_repo_candidate/agentops-control-tower/reports/latest_video_readiness.html",
    "public_repo_candidate/agentops-control-tower/reports/latest_devpost_submission_packet.html",
    "public_repo_candidate/agentops-control-tower/splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
]

CANDIDATE_SELF_EVIDENCE = [
    "README.md",
    "LICENSE",
    "architecture_diagram.md",
    "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
    "reports/latest_demo_tour.html",
    "reports/latest_video_readiness.html",
    "reports/latest_devpost_submission_packet.html",
    "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
]

EXTERNAL_GATES = [
    "Public GitHub repository URL",
    "Public demo video URL",
    "Optional Splunk account/license and MCP Server setup for live proof",
    "Approved URL writeback after verified public URLs",
    "Devpost account/session and final submit approval",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def exists_report(root: Path, rel_paths: list[str]) -> list[dict[str, Any]]:
    return [
        {"path": item, "exists": (root / item).exists()}
        for item in rel_paths
    ]


def load_devpost_fields(root: Path) -> dict[str, Any]:
    packet_path = root / "reports" / "latest_devpost_submission_packet.json"
    if not packet_path.exists():
        return {}
    return read_json(packet_path).get("fields", {})


def is_pending(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("PENDING_")


def build_payload(root: Path) -> dict[str, Any]:
    fields = load_devpost_fields(root)
    local_evidence = exists_report(root, LOCAL_EVIDENCE)
    public_paths = CANDIDATE_SELF_EVIDENCE if (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists() else PUBLIC_CANDIDATE_EVIDENCE
    public_evidence = exists_report(root, public_paths)
    missing_local = [item["path"] for item in local_evidence if not item["exists"]]
    missing_public = [item["path"] for item in public_evidence if not item["exists"]]
    pending_urls = {
        "repository_url": fields.get("repository_url", "PENDING_USER_APPROVAL_PUBLIC_REPO_URL"),
        "demo_video_url": fields.get("demo_video_url", "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL"),
    }
    pending_url_count = sum(1 for value in pending_urls.values() if is_pending(value))
    local_ready = not missing_local and not missing_public
    final_submit_ready = local_ready and pending_url_count == 0
    return {
        "status": "ready_to_submit_after_user_approval" if final_submit_ready else "ready_for_user_review",
        "local_ready": local_ready,
        "final_submit_ready": final_submit_ready,
        "missing_local_evidence": missing_local,
        "missing_public_candidate_evidence": missing_public,
        "pending_urls": pending_urls,
        "external_gates_pending": EXTERNAL_GATES,
        "recommended_order": [
            "Approve or hold public GitHub repository publication.",
            "Record and approve public demo video upload.",
            "Optionally approve Splunk account/license and MCP setup for live bonus proof.",
            "Replace pending URL placeholders in the Devpost field map only after both public URLs are verified and approved.",
            "Re-run python scripts\\validate_submission_packet.py.",
            "Get explicit final Devpost submit approval.",
        ],
        "public_candidate_evidence_paths": public_paths,
    }


def status_label(payload: dict[str, Any]) -> str:
    if payload["final_submit_ready"]:
        return "GO after explicit final submit approval"
    if payload["local_ready"]:
        return "LOCAL GO / EXTERNAL NO-GO"
    return "LOCAL NO-GO"


def render_list(items: list[str]) -> str:
    return "".join(f"<li>{esc(item)}</li>" for item in items)


def render_evidence(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(item['path'])}</td>"
        f"<td class=\"{'ready' if item['exists'] else 'pending'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        "</tr>"
        for item in rows
    )


def render_html(payload: dict[str, Any]) -> str:
    # Rebuild evidence row data from payload paths to keep the JSON compact.
    root_local_rows = [
        {"path": item, "exists": item not in payload["missing_local_evidence"]}
        for item in LOCAL_EVIDENCE
    ]
    root_public_rows = [
        {"path": item, "exists": item not in payload["missing_public_candidate_evidence"]}
        for item in payload["public_candidate_evidence_paths"]
    ]
    pending_urls = payload["pending_urls"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Final Go/No-Go Review</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    header p {{ color: #dbe3ec; max-width: 940px; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    h1, h2 {{ margin-top: 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ color: #5f6d7c; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .no-go {{ color: #b3261e; font-weight: 700; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
    @media (max-width: 760px) {{
      header {{ padding: 22px 18px; }}
      main {{ padding: 14px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Final Go/No-Go Review</h1>
    <p>Submission readiness snapshot for Agentic Incident Command Center. This report separates local readiness from external publication and final submit gates.</p>
  </header>
  <main>
    <section>
      <h2>Decision</h2>
      <p>Status: <span class="{'ready' if payload['local_ready'] else 'no-go'}">{esc(status_label(payload))}</span></p>
      <p>Local evidence ready: <span class="{'ready' if payload['local_ready'] else 'no-go'}">{esc(payload['local_ready'])}</span></p>
      <p>Final submit ready: <span class="{'ready' if payload['final_submit_ready'] else 'pending'}">{esc(payload['final_submit_ready'])}</span></p>
    </section>
    <section>
      <h2>Pending URL Gates</h2>
      <table>
        <tbody>
          <tr><th>Repository URL</th><td class="pending">{esc(pending_urls['repository_url'])}</td></tr>
          <tr><th>Demo video URL</th><td class="pending">{esc(pending_urls['demo_video_url'])}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>External Gates</h2>
      <ul>{render_list(payload['external_gates_pending'])}</ul>
    </section>
    <section>
      <h2>Recommended Order</h2>
      <ol>{render_list(payload['recommended_order'])}</ol>
    </section>
    <section>
      <h2>Local Evidence</h2>
      <table><thead><tr><th>Path</th><th>Status</th></tr></thead><tbody>{render_evidence(root_local_rows)}</tbody></table>
    </section>
    <section>
      <h2>Public Candidate Evidence</h2>
      <table><thead><tr><th>Path</th><th>Status</th></tr></thead><tbody>{render_evidence(root_public_rows)}</tbody></table>
    </section>
  </main>
</body>
</html>
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run(root: Path) -> dict[str, str]:
    payload = build_payload(root)
    html_path = root / "reports" / "latest_final_go_no_go.html"
    json_path = root / "reports" / "latest_final_go_no_go.json"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(payload), encoding="utf-8")
    write_json(json_path, payload)
    return {
        "status": payload["status"],
        "html": "reports/latest_final_go_no_go.html",
        "json": "reports/latest_final_go_no_go.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final Go/No-Go submission readiness report.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    print(json.dumps(run(Path(args.root).resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
