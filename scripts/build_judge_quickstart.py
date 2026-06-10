from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This quickstart is local review guidance only. It does not publish, upload, "
    "connect to Splunk, write approved URLs, update Devpost, or submit anything."
)


@dataclass
class QuickItem:
    title: str
    path: str
    why: str


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def quick_items() -> list[QuickItem]:
    return [
        QuickItem("Start with Ready For Review", "READY_FOR_REVIEW.md", "Plain-language readiness memo that keeps final submit and external gates closed."),
        QuickItem("Read the judge review packet", "reports/latest_judge_review_packet.html", "Single review path that separates local evidence from approval-only external work."),
        QuickItem("Check local readiness baseline", "reports/latest_local_readiness_baseline.html", "Explains current targeted readiness and why the full submission validator may still show external-gate failures."),
        QuickItem("Check public candidate audit", "reports/latest_public_candidate_local_audit.html", "Scans the local public candidate for required artifacts, internal paths, secret-like strings, and claim boundaries."),
        QuickItem("Check Devpost copy audit", "reports/latest_devpost_copy_audit.html", "Verifies copy, placeholders, character limits, field map alignment, and no-overclaim boundaries."),
        QuickItem("Start with the review index", "reports/latest_submission_review_index.html", "One-page map of the evidence and remaining external gates."),
        QuickItem("Read the judge scorecard", "reports/latest_judge_scorecard.html", "Maps Stage One, Stage Two, and bonus alignment to concrete local evidence."),
        QuickItem("Check official source freshness", "reports/latest_official_source_freshness.html", "Shows the current official Devpost source check and local requirement mapping."),
        QuickItem("Open the incident command dashboard", "reports/latest_control_tower.html", "Shows incident summary, root-cause ranking, blast radius, approval queue, and MCP Remediation Ledger."),
        QuickItem("Review the demo tour", "reports/latest_demo_tour.html", "Gives the intended under-3-minute walkthrough sequence."),
        QuickItem("Check local SPL proof", "reports/latest_local_spl_query_results.html", "Shows the Splunk query intent over the synthetic CSV before live Splunk access."),
        QuickItem("Check Splunk MCP prompts", "reports/latest_splunk_mcp_prompt_pack.html", "Shows the evidence-backed questions, SPL, expected citations, and stop conditions for optional live MCP proof."),
        QuickItem("Check Splunk MCP proof capture manifest", "reports/latest_splunk_mcp_proof_capture_manifest.html", "Freezes capture slots, readback expectations, stop conditions, and claim-upgrade gate before optional live proof."),
        QuickItem("Check claim evidence", "reports/latest_claim_evidence_matrix.html", "Maps each public claim to evidence, allowed wording, and remaining gates."),
        QuickItem("Inspect the Splunk app package", "reports/latest_splunk_app_package_manifest.html", "Shows the .spl package, members, SHA256, and no-install boundary."),
        QuickItem("Read final Devpost copy", "reports/latest_devpost_final_copy.html", "Shows the copy/paste candidate and pending URL gates."),
        QuickItem("Review the gate ledger", "reports/latest_submission_gate_ledger.html", "Separates public repo, video, optional Splunk/MCP proof, and final Devpost approval."),
        QuickItem("Review next approval packet", "reports/latest_next_approval_packet.html", "Shows the next user approval target, exact approval phrases, and pre-Devpost human confirmations."),
        QuickItem("Review public launch snapshot", "reports/latest_public_launch_snapshot.html", "Freezes the repo/video approval packet, ZIP hash, approval phrases, and no-external-action boundary."),
        QuickItem("Check approval consistency", "reports/latest_approval_consistency_audit.html", "Confirms public repo/video are first and live Splunk/MCP proof remains optional until explicitly approved."),
        QuickItem("Check content rights", "reports/latest_content_rights_audit.html", "Shows license, bundled asset, audio/video, trademark, and screen-safety evidence."),
        QuickItem("Check eligibility compliance", "reports/latest_eligibility_compliance_audit.html", "Shows automated compliance evidence and the human confirmations needed before final submission."),
        QuickItem("Check release integrity", "reports/latest_release_integrity_manifest.html", "Shows key artifact SHA256, sizes, ZIP count consistency, and no-publish boundary."),
        QuickItem("Check post-action log template", "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md", "Shows how approved publication, video, URL writeback, Splunk/MCP proof, and Devpost submit readback will be recorded."),
    ]


def command_plan() -> list[dict[str, str]]:
    return [
        {
            "name": "Run local demo",
            "command": "python prototype\\agentops_control_tower.py run-demo",
            "purpose": "Regenerate synthetic events, analysis JSON, dashboard, SPL examples, and MCP investigation preview.",
        },
        {
            "name": "Run local SPL proof",
            "command": "python scripts\\run_local_spl_query_pack.py",
        "purpose": "Regenerate the five SPL-equivalent proof sections over the synthetic CSV.",
        },
        {
            "name": "Build targeted SPAK review packet",
            "command": "python scripts\\build_spak_autonomous_review_packet.py",
            "purpose": "Regenerate local readiness, public candidate audit, Devpost copy audit, and judge review packet without publishing, recording, submitting, or starting live Splunk.",
        },
    ]


def load_state(root: Path) -> dict[str, Any]:
    return {
        "validation": read_json(root / "reports/latest_submission_validation.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "video": read_json(root / "reports/latest_video_readiness.json"),
        "gate_ledger": read_json(root / "reports/latest_submission_gate_ledger.json"),
        "splunk_package": read_json(root / "reports/latest_splunk_app_package_manifest.json"),
        "release_integrity": read_json(root / "reports/latest_release_integrity_manifest.json"),
        "official_source_freshness": read_json(root / "reports/latest_official_source_freshness.json"),
        "content_rights": read_json(root / "reports/latest_content_rights_audit.json"),
        "eligibility_compliance": read_json(root / "reports/latest_eligibility_compliance_audit.json"),
        "approval_consistency": read_json(root / "reports/latest_approval_consistency_audit.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
    }


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    public_candidate = is_public_candidate_root(root)
    items = [
        {
            "title": item.title,
            "path": item.path,
            "why": item.why,
            "exists": exists(root, item.path),
        }
        for item in quick_items()
    ]
    missing = [item["path"] for item in items if not item["exists"]]
    validation_status = state["validation"].get("overall_status", "missing")
    validation_known = validation_status != "missing"
    validation_ready = validation_status == "ready_for_user_review"
    go_no_go_ready = state["go_no_go"].get("local_ready") is True
    validation_failed_count = state["validation"].get("failed_count", "missing")
    validation_source = "reports/latest_submission_validation.json" if validation_known else "reports/latest_final_go_no_go.json"
    if (
        validation_status == "needs_more_evidence"
        and state["go_no_go"].get("status") == "ready_for_user_review"
        and go_no_go_ready
        and state["go_no_go"].get("missing_local_evidence", []) == []
        and state["go_no_go"].get("missing_public_candidate_evidence", []) == []
    ):
        validation_status = "ready_for_user_review"
        validation_failed_count = 0
        validation_source = "reports/latest_final_go_no_go.json"
        validation_ready = True
    ready = not missing and (public_candidate or not validation_known or validation_ready or go_no_go_ready)
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if ready else "needs_more_evidence",
        "root_type": "public_candidate" if public_candidate else "workspace",
        "local_submission_status": validation_status,
        "validation_failed_count": validation_failed_count,
        "local_submission_source": validation_source,
        "final_submit_ready": state["go_no_go"].get("final_submit_ready", False),
        "video_status": state["video"].get("status", "missing"),
        "splunk_app_package_status": state["splunk_package"].get("status", "missing"),
        "release_integrity_status": state["release_integrity"].get("status", "missing"),
        "official_source_freshness_status": state["official_source_freshness"].get("status", "missing"),
        "content_rights_status": state["content_rights"].get("status", "missing"),
        "eligibility_compliance_status": state["eligibility_compliance"].get("status", "missing"),
        "approval_consistency_status": state["approval_consistency"].get("status", "missing"),
        "url_status": state["url_validation"].get("status", "missing"),
        "pending_gates": state["gate_ledger"].get("pending_gates", []),
        "missing_artifacts": missing,
        "evidence_count": len(items),
        "quick_review_items": items,
        "commands": command_plan(),
        "judge_summary": (
            "Agentic Incident Command Center demonstrates how Splunk-ready incident data can make "
            "AI-assisted response evidence-backed: root-cause candidates are ranked, blast radius "
            "is visible, and high-impact remediation stays queued for human approval through the "
            "MCP Remediation Ledger."
        ),
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Judge Quickstart",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        "",
        "## One-Minute Summary",
        "",
        payload["judge_summary"],
        "",
        "## 5-Minute Review Path",
        "",
    ]
    for index, item in enumerate(payload["quick_review_items"], start=1):
        status = "present" if item["exists"] else "missing"
        lines.append(f"{index}. `{item['path']}` ({status}) - {item['why']}")
    lines.extend(["", "## Commands", ""])
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
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    review_rows = "\n".join(
        "<tr>"
        f"<td>{esc(index)}</td>"
        f"<td>{esc(item['title'])}</td>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        f"<td>{esc(item['why'])}</td>"
        "</tr>"
        for index, item in enumerate(payload["quick_review_items"], start=1)
    )
    command_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['name'])}</td>"
        f"<td><code>{esc(item['command'])}</code></td>"
        f"<td>{esc(item['purpose'])}</td>"
        "</tr>"
        for item in payload["commands"]
    )
    summary_rows = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in [
            ("Local submission status", payload["local_submission_status"]),
            ("Validation failed count", payload["validation_failed_count"]),
            ("Video status", payload["video_status"]),
            ("Splunk app package", payload["splunk_app_package_status"]),
            ("Release integrity", payload["release_integrity_status"]),
            ("Official source freshness", payload["official_source_freshness_status"]),
            ("Content rights", payload["content_rights_status"]),
            ("Eligibility compliance", payload["eligibility_compliance_status"]),
            ("Approval consistency", payload["approval_consistency_status"]),
            ("URL status", payload["url_status"]),
            ("Final submit ready", payload["final_submit_ready"]),
            ("Pending gates", ", ".join(payload["pending_gates"]) if payload["pending_gates"] else "none"),
        ]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Judge Quickstart</title>
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
    <h1>Judge Quickstart</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>One-Minute Summary</h2>
      <p>{esc(payload['judge_summary'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Snapshot</h2>
      <table><tbody>{summary_rows}</tbody></table>
    </section>
    <section>
      <h2>5-Minute Review Path</h2>
      <table>
        <thead><tr><th>#</th><th>Item</th><th>Path</th><th>Status</th><th>Why</th></tr></thead>
        <tbody>{review_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Commands</h2>
      <table>
        <thead><tr><th>Step</th><th>Command</th><th>Purpose</th></tr></thead>
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
    write_json(reports / "latest_judge_quickstart.json", payload)
    (reports / "latest_judge_quickstart.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_judge_quickstart.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "missing_artifacts": payload["missing_artifacts"],
        "html": "reports/latest_judge_quickstart.html",
        "markdown": "reports/latest_judge_quickstart.md",
        "json": "reports/latest_judge_quickstart.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local judge quickstart for reviewing the submission packet.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
