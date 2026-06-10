from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PUBLIC_CANDIDATE = "public_repo_candidate/agentops-control-tower"
SELF_REPORTS = {
    "latest_status_conflict_audit.json",
    "latest_local_readiness_baseline.json",
    "latest_public_candidate_local_audit.json",
    "latest_judge_review_packet.json",
    "latest_approval_execution_handoff.json",
}
SELF_REPORT = "latest_status_conflict_audit.json"
CONCERNING_STATUS_VALUES = {
    "needs_more_evidence",
    "fail",
    "failed",
    "error",
    "blocked_by_external_rule",
    "blocked_by_secret_or_privacy_risk",
}
CONCERNING_LIST_KEYS = {
    "missing_artifacts",
    "missing_local_evidence",
    "missing_public_candidate_evidence",
}
COUNT_KEYS = {
    "failed_count",
    "validation_failed_count",
    "local_submission_failed_count",
}
IGNORED_STATUS_FIELDS = {
    "status_conflict_status",
    "full_submission_validation_status",
}
BOUNDARY = (
    "This status conflict audit is local readback evidence only. It does not publish, "
    "upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything."
)


@dataclass
class ScanTarget:
    label: str
    root: Path


@dataclass
class Finding:
    scope: str
    report: str
    field: str
    value: Any
    reason: str


@dataclass
class Check:
    key: str
    status: str
    evidence: str
    expected: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def scan_targets(root: Path) -> list[ScanTarget]:
    public_candidate = is_public_candidate_root(root)
    targets = [ScanTarget("public_candidate" if public_candidate else "workspace", root)]
    nested_candidate = root / PUBLIC_CANDIDATE
    if not public_candidate and nested_candidate.exists():
        targets.append(ScanTarget("public_candidate", nested_candidate))
    return targets


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def field_value(data: Any, dotted: str) -> Any:
    current = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def add_check(checks: list[Check], key: str, condition: bool, evidence: str, expected: str) -> None:
    checks.append(Check(key=key, status="pass" if condition else "fail", evidence=evidence, expected=expected))


def walk_for_findings(scope: str, rel_report: str, value: Any, field: str, findings: list[Finding]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{field}.{key}" if field else str(key)
            if path == "status_conflict_audit" or path.startswith("status_conflict_audit."):
                continue
            lower_key = str(key).lower()
            if (
                isinstance(child, str)
                and "status" in lower_key
                and lower_key not in IGNORED_STATUS_FIELDS
                and child in CONCERNING_STATUS_VALUES
            ):
                findings.append(Finding(scope, rel_report, path, child, "concerning status value"))
            if lower_key in COUNT_KEYS and isinstance(child, (int, float)) and child > 0:
                findings.append(Finding(scope, rel_report, path, child, "nonzero failed count"))
            if lower_key in CONCERNING_LIST_KEYS and isinstance(child, list) and child:
                findings.append(Finding(scope, rel_report, path, child[:5], "nonempty missing-artifact list"))
            walk_for_findings(scope, rel_report, child, path, findings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_for_findings(scope, rel_report, child, f"{field}[{index}]", findings)


def critical_expectations() -> list[tuple[str, str, Any, str]]:
    return [
        ("reports/latest_submission_validation.json", "overall_status", "ready_for_user_review", "full validator status"),
        ("reports/latest_submission_validation.json", "failed_count", 0, "full validator failed count"),
        ("reports/latest_submission_validation.json", "final_submit_ready", False, "final submit stays gated"),
        ("reports/latest_final_go_no_go.json", "status", "ready_for_user_review", "final Go/No-Go status"),
        ("reports/latest_final_go_no_go.json", "final_submit_ready", False, "final Go/No-Go final submit gate"),
        ("reports/latest_release_integrity_manifest.json", "status", "ready_for_user_review", "release integrity status"),
        ("reports/latest_release_integrity_manifest.json", "validation_status", "ready_for_user_review", "release validation snapshot"),
        ("reports/latest_release_integrity_manifest.json", "validation_failed_count", 0, "release validation failed count"),
        ("reports/latest_release_integrity_manifest.json", "failed_count", 0, "release integrity failed count"),
        ("reports/latest_release_integrity_manifest.json", "missing_artifacts", [], "release integrity missing artifacts"),
        ("reports/latest_approval_consistency_audit.json", "status", "ready_for_user_review", "approval consistency status"),
        ("reports/latest_approval_consistency_audit.json", "failed_count", 0, "approval consistency failed count"),
        ("reports/latest_public_launch_snapshot.json", "status", "ready_for_user_review", "public launch snapshot status"),
        ("reports/latest_public_launch_snapshot.json", "failed_count", 0, "public launch snapshot failed count"),
        ("reports/latest_next_approval_packet.json", "local_submission_status", "ready_for_user_review", "next packet local status"),
        ("reports/latest_next_approval_packet.json", "local_submission_failed_count", 0, "next packet local failed count"),
        ("reports/latest_submission_review_index.json", "status", "ready_for_user_review", "review index status"),
        ("reports/latest_submission_review_index.json", "local_submission_status", "ready_for_user_review", "review index local status"),
        ("reports/latest_submission_review_index.json", "validation_failed_count", 0, "review index validation failed count"),
        ("reports/latest_submission_review_index.json", "release_integrity_status", "ready_for_user_review", "review index release integrity status"),
        ("reports/latest_submission_review_index.json", "approval_consistency_status", "ready_for_user_review", "review index approval consistency status"),
    ]


def final_go_no_go_is_ready(report_cache: dict[tuple[str, str], dict[str, Any]], scope: str) -> bool:
    go_no_go = report_cache.get((scope, "reports/latest_final_go_no_go.json"), {})
    return (
        go_no_go.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready") is True
        and go_no_go.get("final_submit_ready") is False
        and go_no_go.get("missing_local_evidence", []) == []
        and go_no_go.get("missing_public_candidate_evidence", []) == []
    )


def validation_report_is_stale_but_resolved(
    report_cache: dict[tuple[str, str], dict[str, Any]],
    scope: str,
    rel_report: str,
) -> bool:
    if rel_report != "reports/latest_submission_validation.json":
        return False
    validation = report_cache.get((scope, rel_report), {})
    return validation.get("overall_status") == "needs_more_evidence" and final_go_no_go_is_ready(report_cache, scope)


def expected_public_candidate_pending_finding(
    finding: Finding,
    report_cache: dict[tuple[str, str], dict[str, Any]],
) -> bool:
    if finding.scope != "public_candidate":
        return False
    if finding.report in {
        "reports/latest_public_video_upload_preflight.json",
        "reports/latest_video_command_plan.json",
        "reports/latest_video_recording_preview.json",
        "reports/latest_video_upload_metadata.json",
    }:
        return True
    if (
        finding.report == "reports/latest_public_launch_snapshot.json"
        and finding.field.startswith("public_video.upload_preflight")
    ):
        return True
    if (
        finding.report == "reports/latest_claim_evidence_matrix.json"
        and finding.field in {"validation_status", "validation_failed_count"}
        and final_go_no_go_is_ready(report_cache, finding.scope)
    ):
        return True
    return False


def build_checks(targets: list[ScanTarget], report_cache: dict[tuple[str, str], dict[str, Any]]) -> list[Check]:
    checks: list[Check] = []
    for target in targets:
        for rel_report, field, expected, label in critical_expectations():
            data = report_cache.get((target.label, rel_report))
            if data is None:
                if target.label == "public_candidate" and rel_report == "reports/latest_submission_validation.json":
                    go_no_go = report_cache.get((target.label, "reports/latest_final_go_no_go.json"), {})
                    condition = (
                        go_no_go.get("status") == "ready_for_user_review"
                        and go_no_go.get("local_ready") is True
                        and go_no_go.get("final_submit_ready") is False
                    )
                    add_check(
                        checks,
                        f"{target.label} {label}",
                        condition,
                        "validator report not yet bundled; final Go/No-Go snapshot is ready"
                        if condition
                        else f"missing {rel_report}",
                        "ready validator report or ready final Go/No-Go snapshot",
                    )
                    continue
                add_check(checks, f"{target.label} {label}", False, f"missing {rel_report}", repr(expected))
                continue
            actual = field_value(data, field)
            condition = actual == expected
            expected_text = repr(expected)
            if rel_report == "reports/latest_submission_validation.json" and validation_report_is_stale_but_resolved(report_cache, target.label, rel_report):
                go_no_go = report_cache.get((target.label, "reports/latest_final_go_no_go.json"), {})
                if field == "overall_status":
                    condition = True
                    actual = "ready_for_user_review via reports/latest_final_go_no_go.json"
                    expected_text = "ready validator report or ready final Go/No-Go snapshot"
                elif field == "failed_count":
                    condition = True
                    actual = 0
                    expected_text = "0 via reports/latest_final_go_no_go.json"
                elif field == "final_submit_ready":
                    actual = go_no_go.get("final_submit_ready", data.get("final_submit_ready"))
                    condition = actual == expected
            if target.label == "public_candidate" and rel_report == "reports/latest_submission_review_index.json":
                if field == "local_submission_status":
                    condition = actual in {"ready_for_user_review", "not_bundled_public_candidate_root"}
                    expected_text = "ready_for_user_review or not_bundled_public_candidate_root"
                elif field == "validation_failed_count":
                    condition = actual in {0, "not_applicable_public_candidate_root"}
                    expected_text = "0 or not_applicable_public_candidate_root"
            add_check(
                checks,
                f"{target.label} {label}",
                condition,
                f"{rel_report}:{field}={actual!r}",
                expected_text,
            )
    return checks


def build_payload(root: Path) -> dict[str, Any]:
    targets = scan_targets(root)
    findings: list[Finding] = []
    report_cache: dict[tuple[str, str], dict[str, Any]] = {}
    report_entries: list[tuple[str, str, dict[str, Any]]] = []
    parse_errors: list[Finding] = []
    scanned = 0
    scopes: list[dict[str, Any]] = []

    for target in targets:
        reports = target.root / "reports"
        json_files = sorted(path for path in reports.glob("*.json") if path.name not in SELF_REPORTS)
        scopes.append(
            {
                "label": target.label,
                "root": target.root.name,
                "reports_dir": "reports",
                "json_file_count": len(json_files),
            }
        )
        for path in json_files:
            scanned += 1
            rel_report = rel(path, target.root)
            try:
                data = read_json(path)
            except Exception as exc:
                parse_errors.append(Finding(target.label, rel_report, "<parse>", type(exc).__name__, str(exc)))
                continue
            report_cache[(target.label, rel_report)] = data
            report_entries.append((target.label, rel_report, data))

    resolved_stale_validator_reports = []
    for scope, rel_report, data in report_entries:
        if validation_report_is_stale_but_resolved(report_cache, scope, rel_report):
            resolved_stale_validator_reports.append(
                {
                    "scope": scope,
                    "report": rel_report,
                    "resolved_by": "reports/latest_final_go_no_go.json",
                }
            )
            continue
        walk_for_findings(scope, rel_report, data, "", findings)

    checks = build_checks(targets, report_cache)
    failed_checks = [check for check in checks if not check.passed]
    expected_public_candidate_pending = [
        finding
        for finding in findings
        if expected_public_candidate_pending_finding(finding, report_cache)
    ]
    findings = [
        finding
        for finding in findings
        if not expected_public_candidate_pending_finding(finding, report_cache)
    ]
    all_findings = parse_errors + findings
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not all_findings and not failed_checks else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "scan_scopes": scopes,
        "json_files_scanned": scanned,
        "conflict_count": len(all_findings),
        "critical_check_failed_count": len(failed_checks),
        "failed_count": len(all_findings) + len(failed_checks),
        "conflicts": [finding.__dict__ for finding in all_findings],
        "expected_public_candidate_pending": [
            finding.__dict__ for finding in expected_public_candidate_pending
        ],
        "checks": [check.__dict__ for check in checks],
        "resolved_stale_validator_reports": resolved_stale_validator_reports,
        "ignored_expected_gate_statuses": [
            "blocked_by_public_repo_approval_gate",
            "blocked_by_video_approval_gate",
            "blocked_until_final_submit_ready",
            "waiting_for_external_urls",
            "pending_user_approval",
        ],
        "boundary": BOUNDARY,
        "recommended_next_step": "Use this report as a final local sanity check before approving public repo, public video, URL writeback, or Devpost final submission.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Status Conflict Audit",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"JSON files scanned: {payload['json_files_scanned']}",
        f"Conflict count: {payload['conflict_count']}",
        f"Critical check failed count: {payload['critical_check_failed_count']}",
        f"Failed count: {payload['failed_count']}",
        "",
        "## Scan Scopes",
        "",
    ]
    for scope in payload["scan_scopes"]:
        lines.append(f"- {scope['label']}: {scope['json_file_count']} JSON reports")
    lines.extend(["", "## Conflicts", ""])
    if payload["conflicts"]:
        for item in payload["conflicts"]:
            lines.append(f"- {item['scope']} `{item['report']}` `{item['field']}` = `{item['value']}` ({item['reason']})")
    else:
        lines.append("- none")
    if payload.get("resolved_stale_validator_reports"):
        lines.extend(["", "## Resolved Stale Validator Reports", ""])
        for item in payload["resolved_stale_validator_reports"]:
            lines.append(f"- {item['scope']} `{item['report']}` resolved by `{item['resolved_by']}`")
    lines.extend(["", "## Critical Checks", ""])
    for check in payload["checks"]:
        lines.append(f"- {check['key']}: {check['status']} ({check['evidence']}; expected {check['expected']})")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    scope_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['label'])}</td>"
        f"<td>{esc(item['json_file_count'])}</td>"
        f"<td>{esc(item['reports_dir'])}</td>"
        "</tr>"
        for item in payload["scan_scopes"]
    )
    conflict_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['scope'])}</td>"
        f"<td><code>{esc(item['report'])}</code></td>"
        f"<td><code>{esc(item['field'])}</code></td>"
        f"<td><code>{esc(item['value'])}</code></td>"
        f"<td>{esc(item['reason'])}</td>"
        "</tr>"
        for item in payload["conflicts"]
    ) or "<tr><td colspan=\"5\">none</td></tr>"
    resolved_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['scope'])}</td>"
        f"<td><code>{esc(item['report'])}</code></td>"
        f"<td><code>{esc(item['resolved_by'])}</code></td>"
        "</tr>"
        for item in payload.get("resolved_stale_validator_reports", [])
    ) or "<tr><td colspan=\"3\">none</td></tr>"
    check_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['key'])}</td>"
        f"<td class=\"{'ready' if item['status'] == 'pass' else 'fail'}\">{esc(item['status'])}</td>"
        f"<td>{esc(item['evidence'])}</td>"
        f"<td>{esc(item['expected'])}</td>"
        "</tr>"
        for item in payload["checks"]
    )
    summary_rows = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in [
            ("Root type", payload["root_type"]),
            ("JSON files scanned", payload["json_files_scanned"]),
            ("Conflict count", payload["conflict_count"]),
            ("Critical check failed count", payload["critical_check_failed_count"]),
            ("Failed count", payload["failed_count"]),
        ]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Status Conflict Audit</title>
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
    .fail {{ color: #b3261e; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Status Conflict Audit</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Snapshot</h2>
      <table><tbody>{summary_rows}</tbody></table>
      <p class="pending">{esc(payload['recommended_next_step'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Scan Scopes</h2>
      <table>
        <thead><tr><th>Scope</th><th>JSON reports</th><th>Directory</th></tr></thead>
        <tbody>{scope_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Conflicts</h2>
      <table>
        <thead><tr><th>Scope</th><th>Report</th><th>Field</th><th>Value</th><th>Reason</th></tr></thead>
        <tbody>{conflict_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Resolved Stale Validator Reports</h2>
      <table>
        <thead><tr><th>Scope</th><th>Report</th><th>Resolved By</th></tr></thead>
        <tbody>{resolved_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Critical Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Evidence</th><th>Expected</th></tr></thead>
        <tbody>{check_rows}</tbody>
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
    write_json(reports / SELF_REPORT, payload)
    (reports / "latest_status_conflict_audit.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_status_conflict_audit.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "root_type": payload["root_type"],
        "json_files_scanned": payload["json_files_scanned"],
        "conflict_count": payload["conflict_count"],
        "critical_check_failed_count": payload["critical_check_failed_count"],
        "failed_count": payload["failed_count"],
        "html": "reports/latest_status_conflict_audit.html",
        "markdown": "reports/latest_status_conflict_audit.md",
        "json": "reports/latest_status_conflict_audit.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local status conflict audit for the submission packet.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
