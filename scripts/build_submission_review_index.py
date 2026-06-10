from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This review index is local evidence only. It does not publish a repository, "
    "record or upload video, connect to Splunk, write approved URLs, update Devpost, or submit anything."
)


@dataclass
class Artifact:
    section: str
    title: str
    path: str
    purpose: str
    required: bool = True


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def artifact_sections(root: Path) -> list[Artifact]:
    public_candidate = is_public_candidate_root(root)
    validation_paths = [
        Artifact("Validation", "Final Go/No-Go", "reports/latest_final_go_no_go.html", "Separates local readiness from pending external gates."),
        Artifact("Validation", "Local readiness baseline", "reports/latest_local_readiness_baseline.html", "Targeted local baseline that explains stale/full validator failures without moving external gates."),
        Artifact("Validation", "Public candidate local audit", "reports/latest_public_candidate_local_audit.html", "Scans the local public candidate for required artifacts, internal paths, secret-like strings, and claim boundaries."),
        Artifact("Validation", "Devpost copy audit", "reports/latest_devpost_copy_audit.html", "Checks final Devpost copy, placeholders, character limits, field-map alignment, and overclaim boundaries."),
        Artifact("Validation", "Claim evidence matrix", "reports/latest_claim_evidence_matrix.html", "Maps public claims to evidence, allowed wording, avoid wording, and remaining gates."),
        Artifact("Validation", "Claim boundary validation", "reports/latest_claim_boundary_validation.html", "Checks that live Splunk/MCP claims are not overstated before proof exists."),
        Artifact("Validation", "Submission URL validation", "reports/latest_submission_url_validation.html", "Shows repository/video URLs are still pending or approved-public."),
        Artifact("Validation", "Content rights audit", "reports/latest_content_rights_audit.html", "Shows license, bundled asset, audio/video, trademark, and screen-safety evidence."),
        Artifact("Validation", "Eligibility and compliance audit", "reports/latest_eligibility_compliance_audit.html", "Separates automated compliance evidence from user-confirmed eligibility, team, ownership, and conflict items."),
        Artifact("Validation", "Approval consistency audit", "reports/latest_approval_consistency_audit.html", "Checks that approval order stays public repo, public video, optional Splunk/MCP proof, URL writeback, then Devpost."),
        Artifact("Validation", "Status conflict audit", "reports/latest_status_conflict_audit.html", "Scans JSON reports for stale failed statuses, failed counts, and missing local artifacts.", False),
        Artifact("Validation", "Public launch snapshot", "reports/latest_public_launch_snapshot.html", "Freezes the public repo/video approval evidence, ZIP hash, approval phrases, and no-external-action boundary."),
        Artifact("Validation", "Release integrity manifest", "reports/latest_release_integrity_manifest.html", "Summarizes key artifact SHA256, size, ZIP count consistency, and no-publish boundary."),
        Artifact("Validation", "Official source freshness", "reports/latest_official_source_freshness.html", "Shows the latest official Devpost source check and local requirement mapping."),
    ]
    public_package_paths = [
        Artifact("Release Package", "Public candidate manifest", "PUBLIC_REPO_CANDIDATE_MANIFEST.md", "Shows this folder is a clean local public-candidate staging area."),
    ] if public_candidate else [
            Artifact("Release Package", "Public candidate zip manifest", "reports/latest_public_candidate_zip_manifest.html", "Shows the local public-candidate ZIP contents and publication boundary."),
            Artifact("Release Package", "Public candidate folder", "public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md", "Shows the clean local folder intended for public GitHub review after approval."),
            Artifact("Release Package", "Public candidate ZIP", "release/agentops-control-tower-public-candidate.zip", "Local ZIP package for user review. It is not published."),
        ]
    approval_execution_paths = [] if public_candidate else [
        Artifact("External Gates", "Approval execution handoff", "reports/latest_approval_execution_handoff.html", "Japanese local handoff for the exact post-approval execution order, readbacks, and stop conditions."),
        Artifact("External Gates", "Approval execution handoff submission copy", "submission/APPROVAL_EXECUTION_HANDOFF.md", "Markdown copy of the local approval execution handoff for interrupted sessions."),
    ]
    if not public_candidate:
        validation_paths.extend([
            Artifact("Validation", "Submission validation", "reports/latest_submission_validation.html", "Full local validation report for root, public candidate, and safety scans."),
            Artifact("Validation", "Release ZIP smoke test", "reports/latest_release_zip_smoke_test.html", "Extracts and rechecks the local public-candidate ZIP."),
        ])

    return [
        Artifact("Start Here", "Ready for review memo", "READY_FOR_REVIEW.md", "Plain-language local readiness and review start page."),
        Artifact("Start Here", "Judge review packet", "reports/latest_judge_review_packet.html", "Single review packet that separates local readiness from external approval gates."),
        Artifact("Start Here", "README", "README.md", "Portable project overview and local run instructions."),
        Artifact("Start Here", "Control Tower dashboard", "reports/latest_control_tower.html", "Main local dashboard showing incidents, approval queue, and MCP Remediation Ledger."),
        Artifact("Start Here", "Demo tour", "reports/latest_demo_tour.html", "Recording-friendly walkthrough for the public demo video."),
        Artifact("Start Here", "Submission gate ledger", "reports/latest_submission_gate_ledger.html", "Single ledger for public repo, video, optional Splunk/MCP proof, and Devpost gates."),
        Artifact("Start Here", "Submission deadline burndown", "reports/latest_submission_deadline_burndown.html", "Deadline-aware sequence for public repo, video, optional live proof, URL writeback, and Devpost final submit."),
        Artifact("Splunk Evidence", "Splunk-ready CSV", "data/splunk_agentops_events.csv", "Synthetic checkout-incident events ready for an agentops_events index after approval."),
        Artifact("Splunk Evidence", "SPL query pack", "submission/SPL_QUERIES.md", "Queries for high-risk events, approval queue, MCP remediation ledger, and external guardrails."),
        Artifact("Splunk Evidence", "Local SPL-equivalent proof", "reports/latest_local_spl_query_results.html", "Local proof that the query intent returns concrete rows before live Splunk setup."),
        Artifact("Splunk Evidence", "Splunk index config", "splunk_app/agentops_control_tower/default/indexes.conf", "Optional app-local index definition for agentops_events."),
        Artifact("Splunk Evidence", "Splunk sourcetype config", "splunk_app/agentops_control_tower/default/props.conf", "CSV extraction and timestamp parsing for agentops:events."),
        Artifact("Splunk Evidence", "Splunk app package manifest", "reports/latest_splunk_app_package_manifest.html", "Local .spl package members, SHA256, and no-install/no-upload boundary."),
        Artifact("Splunk Evidence", "Splunk app package", "dist/agentops-control-tower-splunk-app.spl", "Local reviewable .spl artifact. It is not installed or uploaded."),
        Artifact("Splunk Evidence", "Splunk MCP command plan", "reports/latest_splunk_mcp_command_plan.html", "Post-approval plan for account/license, synthetic import, app install, MCP setup, and proof capture."),
        Artifact("Splunk Evidence", "Splunk MCP proof brief", "reports/latest_splunk_mcp_proof_brief.html", "Decision brief for live proof success criteria, screen safety, stop conditions, and claim upgrade rules."),
        Artifact("Splunk Evidence", "Splunk MCP prompt pack", "reports/latest_splunk_mcp_prompt_pack.html", "Five approved-proof prompts with SPL, expected citations, success readbacks, and stop conditions."),
        Artifact("Splunk Evidence", "Splunk MCP prompt pack submission copy", "submission/SPLUNK_MCP_PROMPT_PACK.md", "Markdown copy of the Splunk MCP prompt pack for public review and live proof preparation."),
        Artifact("Splunk Evidence", "Splunk MCP proof capture manifest", "reports/latest_splunk_mcp_proof_capture_manifest.html", "Capture slots, expected readback, stop conditions, and claim-upgrade gate for optional live proof."),
        Artifact("Splunk Evidence", "Splunk MCP proof capture manifest submission copy", "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md", "Markdown copy of the optional live proof capture manifest."),
        Artifact("Devpost Copy", "Devpost submission packet", "reports/latest_devpost_submission_packet.html", "Local Devpost field packet with pending URL placeholders and claim boundaries."),
        Artifact("Devpost Copy", "Devpost final copy", "reports/latest_devpost_final_copy.html", "Copy/paste text and character checks for the final Devpost form."),
        Artifact("Devpost Copy", "Devpost submit command plan", "reports/latest_devpost_submit_command_plan.html", "Post-approval Devpost form-fill, final review, submit, and readback plan."),
        Artifact("Devpost Copy", "Devpost manual fill brief", "reports/latest_devpost_manual_fill_brief.html", "Field-by-field form fill order, readback checks, and stop conditions before final submit."),
        Artifact("Devpost Copy", "Devpost final review checklist", "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md", "Unchecked final-screen checklist for track, public URLs, claim boundaries, human confirmations, video safety, validation, and explicit final approval."),
        Artifact("External Gates", "External approval packet", "reports/latest_external_approval_packet.html", "Purpose, operation, benefit, risk, and verification for each external action."),
        Artifact("External Gates", "Next approval packet", "reports/latest_next_approval_packet.html", "Shows the next approval target, copy-paste approval phrases, and human confirmations before Devpost."),
        Artifact("External Gates", "Publication command plan", "reports/latest_publication_command_plan.html", "Post-approval public GitHub command plan using isolated TEMP staging. It does not create or push a repo."),
        Artifact("External Gates", "Public repo metadata", "reports/latest_public_repo_metadata.html", "GitHub repository name, description, topics, expected readback, and no-publish boundary."),
        Artifact("External Gates", "Video command plan", "reports/latest_video_command_plan.html", "Post-approval recording/upload plan. It does not record or upload."),
        Artifact("External Gates", "Video recording preview", "reports/latest_video_recording_preview.html", "Local-only localhost preview preflight for the public demo recording path."),
        Artifact("External Gates", "Video upload metadata", "reports/latest_video_upload_metadata.html", "Public demo video title, description, tags, visibility, expected readback, and no-upload boundary."),
        Artifact("External Gates", "Public artifact URL readback", "reports/latest_public_artifact_url_readback.html", "Post-publication URL readback gate before approved URL writeback."),
        Artifact("External Gates", "Submission URL apply plan", "reports/latest_submission_url_apply_plan.html", "Dry-run or approved local URL write plan. It does not write without explicit approval."),
        Artifact("External Gates", "Post-action evidence brief", "reports/latest_post_action_evidence_brief.html", "Readback checklist for proving public repo, video, URL writeback, optional Splunk/MCP proof, and Devpost submit after approval."),
        Artifact("External Gates", "Post-action evidence log template", "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md", "Template to copy/fill after approved external actions are completed."),
        *approval_execution_paths,
        *validation_paths,
        *public_package_paths,
        Artifact("Requirements", "Official requirements audit", "submission/OFFICIAL_REQUIREMENTS_AUDIT.md", "Maps current artifacts to the official Devpost requirements."),
        Artifact("Requirements", "Judge review packet markdown", "submission/JUDGE_REVIEW_PACKET.md", "Markdown copy of the review packet for local and public-candidate review."),
        Artifact("Requirements", "Judging alignment", "submission/JUDGING_ALIGNMENT.md", "Maps the project to judging criteria and bonus alignment."),
        Artifact("Requirements", "Judge scorecard", "reports/latest_judge_scorecard.html", "Maps Stage One, Stage Two, and bonus judging points to concrete evidence and remaining gates."),
        Artifact("Requirements", "Launch runbook", "submission/SUBMISSION_LAUNCH_RUNBOOK.md", "Preflight, launch sequence, claim wording, and final safety gate."),
        Artifact("Requirements", "Review Q&A", "submission/SUBMISSION_REVIEW_QA.md", "Judge-facing answers and safe copy guardrails."),
    ]


def load_state(root: Path) -> dict[str, Any]:
    return {
        "validation": read_json(root / "reports/latest_submission_validation.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "gate_ledger": read_json(root / "reports/latest_submission_gate_ledger.json"),
        "splunk_package": read_json(root / "reports/latest_splunk_app_package_manifest.json"),
        "release_smoke": read_json(root / "reports/latest_release_zip_smoke_test.json"),
        "release_integrity": read_json(root / "reports/latest_release_integrity_manifest.json"),
        "official_source_freshness": read_json(root / "reports/latest_official_source_freshness.json"),
        "content_rights": read_json(root / "reports/latest_content_rights_audit.json"),
        "eligibility_compliance": read_json(root / "reports/latest_eligibility_compliance_audit.json"),
        "approval_consistency": read_json(root / "reports/latest_approval_consistency_audit.json"),
        "status_conflict": read_json(root / "reports/latest_status_conflict_audit.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
    }


def local_submission_snapshot(state: dict[str, Any], public_candidate: bool) -> dict[str, Any]:
    validation = state["validation"]
    go_no_go = state["go_no_go"]
    status = validation.get("overall_status", go_no_go.get("status", "missing"))
    failed_count = validation.get("failed_count", "missing")
    source = "reports/latest_submission_validation.json" if validation else "reports/latest_final_go_no_go.json"
    if public_candidate and not validation:
        return {
            "status": "not_bundled_public_candidate_root",
            "failed_count": "not_applicable_public_candidate_root",
            "source": "public_candidate_local_artifacts",
        }
    if (
        status == "needs_more_evidence"
        and go_no_go.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready") is True
        and go_no_go.get("missing_local_evidence", []) == []
        and go_no_go.get("missing_public_candidate_evidence", []) == []
    ):
        return {
            "status": "ready_for_user_review",
            "failed_count": 0,
            "source": "reports/latest_final_go_no_go.json",
        }
    return {
        "status": status,
        "failed_count": failed_count,
        "source": source,
    }


def build_payload(root: Path) -> dict[str, Any]:
    artifacts = [
        {
            "section": item.section,
            "title": item.title,
            "path": item.path,
            "purpose": item.purpose,
            "exists": exists(root, item.path),
            "required": item.required,
        }
        for item in artifact_sections(root)
    ]
    missing = [f"{item['section']}:{item['path']}" for item in artifacts if item["required"] and not item["exists"]]
    state = load_state(root)
    public_candidate = is_public_candidate_root(root)
    validation_snapshot = local_submission_snapshot(state, public_candidate)
    validation_status = validation_snapshot["status"]
    validation_failed_count = validation_snapshot["failed_count"]
    release_zip_status = state["release_smoke"].get("status", "missing")
    if public_candidate:
        release_zip_status = state["release_integrity"].get("release_zip", {}).get(
            "smoke_status",
            "not_applicable_public_candidate_root",
        )
    recommended_review_order = [
        "Open READY_FOR_REVIEW.md and reports/latest_judge_review_packet.html first.",
        "Review reports/latest_local_readiness_baseline.html to separate local readiness from external gates.",
        "Review reports/latest_public_candidate_local_audit.html and reports/latest_devpost_copy_audit.html.",
        "Open reports/latest_judge_quickstart.html for the 5-minute review path.",
        "Open reports/latest_submission_review_index.html.",
        "Review reports/latest_submission_gate_ledger.html and reports/latest_external_approval_packet.html.",
        "Review reports/latest_submission_deadline_burndown.html for target submit timing and milestone order.",
        "Open reports/latest_next_approval_packet.html to decide the next explicit approval phrase.",
        "Open reports/latest_public_launch_snapshot.html to confirm the exact repo/video launch packet before approval.",
        "Open reports/latest_approval_consistency_audit.html to confirm stale Splunk-first guidance is not present.",
        "Open reports/latest_status_conflict_audit.html to confirm no stale failed status remains in JSON reports.",
    ]
    if not public_candidate:
        recommended_review_order.append(
            "Open reports/latest_approval_execution_handoff.html before performing any approved external action."
        )
    recommended_review_order.extend([
        "Review reports/latest_control_tower.html and reports/latest_demo_tour.html for the story.",
        "Review Splunk evidence: local SPL proof, .spl package manifest, Splunk MCP command plan, proof brief, and prompt pack.",
        "Review Devpost final copy and URL validation.",
        "Only after explicit approval, proceed to public repo, video, optional live Splunk/MCP proof, and final Devpost submit gates.",
    ])
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not missing else "needs_more_evidence",
        "root_type": "public_candidate" if public_candidate else "workspace",
        "local_submission_status": validation_status,
        "validation_failed_count": validation_failed_count,
        "local_submission_source": validation_snapshot["source"],
        "final_submit_ready": state["go_no_go"].get("final_submit_ready", False),
        "pending_gates": state["gate_ledger"].get("pending_gates", []),
        "splunk_app_package_status": state["splunk_package"].get("status", "missing"),
        "release_zip_status": release_zip_status,
        "release_integrity_status": state["release_integrity"].get("status", "missing"),
        "official_source_freshness_status": state["official_source_freshness"].get("status", "missing"),
        "content_rights_status": state["content_rights"].get("status", "missing"),
        "eligibility_compliance_status": state["eligibility_compliance"].get("status", "missing"),
        "approval_consistency_status": state["approval_consistency"].get("status", "missing"),
        "status_conflict_status": state["status_conflict"].get("status", "missing"),
        "status_conflict_failed_count": state["status_conflict"].get("failed_count", "missing"),
        "url_status": state["url_validation"].get("status", "missing"),
        "missing_artifacts": missing,
        "artifacts": artifacts,
        "recommended_review_order": recommended_review_order,
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Submission Review Index",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Local submission status: {payload['local_submission_status']}",
        f"Local submission source: {payload['local_submission_source']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        "",
        "## Recommended Review Order",
        "",
    ]
    for item in payload["recommended_review_order"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Artifacts", ""])
    for section in sorted({item["section"] for item in payload["artifacts"]}):
        lines.extend([f"### {section}", ""])
        for item in [row for row in payload["artifacts"] if row["section"] == section]:
            status = "present" if item["exists"] else "missing"
            lines.append(f"- `{item['path']}` ({status}) - {item['title']}: {item['purpose']}")
        lines.append("")
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    summary_rows = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in [
            ("Local submission status", payload["local_submission_status"]),
            ("Local submission source", payload["local_submission_source"]),
            ("Validation failed count", payload["validation_failed_count"]),
            ("Final submit ready", payload["final_submit_ready"]),
            ("Pending gates", ", ".join(payload["pending_gates"]) if payload["pending_gates"] else "none"),
            ("Splunk app package", payload["splunk_app_package_status"]),
            ("Release ZIP", payload["release_zip_status"]),
            ("Release integrity", payload["release_integrity_status"]),
            ("Official source freshness", payload["official_source_freshness_status"]),
            ("Content rights", payload["content_rights_status"]),
            ("Eligibility compliance", payload["eligibility_compliance_status"]),
            ("Approval consistency", payload["approval_consistency_status"]),
            ("Status conflict audit", payload["status_conflict_status"]),
            ("Status conflict failed count", payload["status_conflict_failed_count"]),
            ("URL status", payload["url_status"]),
        ]
    )
    order_items = "".join(f"<li>{esc(item)}</li>" for item in payload["recommended_review_order"])
    sections = []
    for section in sorted({item["section"] for item in payload["artifacts"]}):
        rows = "\n".join(
            "<tr>"
            f"<td>{esc(item['title'])}</td>"
            f"<td><code>{esc(item['path'])}</code></td>"
            f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
            f"<td>{esc(item['purpose'])}</td>"
            "</tr>"
            for item in payload["artifacts"]
            if item["section"] == section
        )
        sections.append(f"""    <section>
      <h2>{esc(section)}</h2>
      <table>
        <thead><tr><th>Artifact</th><th>Path</th><th>Status</th><th>Purpose</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>""")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Submission Review Index</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
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
    <h1>Submission Review Index</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Snapshot</h2>
      <table><tbody>{summary_rows}</tbody></table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Recommended Review Order</h2>
      <ol>{order_items}</ol>
    </section>
{chr(10).join(sections)}
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
    write_json(reports / "latest_submission_review_index.json", payload)
    (reports / "latest_submission_review_index.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_submission_review_index.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "root_type": payload["root_type"],
        "missing_artifacts": payload["missing_artifacts"],
        "html": "reports/latest_submission_review_index.html",
        "markdown": "reports/latest_submission_review_index.md",
        "json": "reports/latest_submission_review_index.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local submission review index.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
