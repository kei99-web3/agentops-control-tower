from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ZIP_NAME = "agentops-control-tower-public-candidate.zip"

REQUIRED_FILES = [
    ".gitattributes",
    "README.md",
    "LICENSE",
    "architecture_diagram.md",
    "prototype/agentops_control_tower.py",
    "scripts/build_approval_consistency_audit.py",
    "scripts/build_video_readiness_report.py",
    "scripts/build_video_command_plan.py",
    "scripts/build_video_cue_sheet.py",
    "scripts/build_video_dry_run.py",
    "scripts/build_video_upload_metadata.py",
    "scripts/build_claim_evidence_matrix.py",
    "scripts/build_external_approval_packet.py",
    "scripts/build_devpost_manual_fill_brief.py",
    "scripts/build_devpost_submit_command_plan.py",
    "scripts/build_publication_command_plan.py",
    "scripts/build_public_repo_metadata.py",
    "scripts/build_public_repo_publish_brief.py",
    "scripts/build_public_repo_dry_run.py",
    "scripts/verify_public_repo_publication_gate.py",
    "scripts/build_public_launch_snapshot.py",
    "scripts/build_splunk_mcp_command_plan.py",
    "scripts/build_splunk_mcp_proof_brief.py",
    "scripts/build_splunk_mcp_prompt_pack.py",
    "scripts/build_splunk_mcp_proof_capture_manifest.py",
    "scripts/build_submission_gate_ledger.py",
    "scripts/build_submission_deadline_burndown.py",
    "scripts/build_submission_review_index.py",
    "scripts/build_judge_quickstart.py",
    "scripts/build_judge_scorecard.py",
    "scripts/build_launch_decision_brief.py",
    "scripts/build_next_approval_packet.py",
    "scripts/build_content_rights_audit.py",
    "scripts/build_eligibility_compliance_audit.py",
    "scripts/build_post_action_evidence_brief.py",
    "scripts/build_official_source_freshness.py",
    "scripts/build_url_writeback_dry_run.py",
    "scripts/build_release_integrity_manifest.py",
    "scripts/build_spak_autonomous_review_packet.py",
    "scripts/package_splunk_app.py",
    "scripts/prepare_submission_urls.py",
    "scripts/run_local_spl_query_pack.py",
    "scripts/submission_urls.py",
    "scripts/validate_claim_boundaries.py",
    "scripts/validate_splunk_app.py",
    "scripts/validate_submission_urls.py",
    "tests/test_agentops_control_tower.py",
    "tests/test_submission_safety_boundaries.py",
    "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
    "dist/agentops-control-tower-splunk-app.spl",
    "reports/latest_approval_consistency_audit.html",
    "reports/latest_approval_consistency_audit.json",
    "reports/latest_approval_consistency_audit.md",
    "reports/latest_claim_evidence_matrix.html",
    "reports/latest_claim_evidence_matrix.json",
    "reports/latest_claim_evidence_matrix.md",
    "reports/latest_devpost_final_copy.md",
    "reports/latest_devpost_submit_command_plan.html",
    "reports/latest_devpost_submit_command_plan.json",
    "reports/latest_devpost_submit_command_plan.md",
    "reports/latest_devpost_manual_fill_brief.html",
    "reports/latest_devpost_manual_fill_brief.json",
    "reports/latest_devpost_manual_fill_brief.md",
    "reports/latest_video_readiness.html",
    "reports/latest_video_readiness.json",
    "reports/latest_video_command_plan.html",
    "reports/latest_video_command_plan.json",
    "reports/latest_video_command_plan.md",
    "reports/latest_video_upload_metadata.html",
    "reports/latest_video_upload_metadata.json",
    "reports/latest_video_upload_metadata.md",
    "reports/latest_video_cue_sheet.html",
    "reports/latest_video_cue_sheet.json",
    "reports/latest_video_cue_sheet.md",
    "reports/latest_external_approval_packet.html",
    "reports/latest_external_approval_packet.json",
    "reports/latest_external_approval_packet.md",
    "reports/latest_submission_url_apply_plan.html",
    "reports/latest_submission_url_apply_plan.json",
    "reports/latest_submission_url_apply_plan.md",
    "reports/latest_submission_review_index.html",
    "reports/latest_submission_review_index.json",
    "reports/latest_submission_review_index.md",
    "reports/latest_judge_quickstart.html",
    "reports/latest_judge_quickstart.json",
    "reports/latest_judge_quickstart.md",
    "reports/latest_judge_review_packet.html",
    "reports/latest_judge_review_packet.json",
    "reports/latest_judge_review_packet.md",
    "reports/latest_judge_scorecard.html",
    "reports/latest_judge_scorecard.json",
    "reports/latest_judge_scorecard.md",
    "reports/latest_local_readiness_baseline.html",
    "reports/latest_local_readiness_baseline.json",
    "reports/latest_local_readiness_baseline.md",
    "reports/latest_public_candidate_local_audit.html",
    "reports/latest_public_candidate_local_audit.json",
    "reports/latest_public_candidate_local_audit.md",
    "reports/latest_devpost_copy_audit.html",
    "reports/latest_devpost_copy_audit.json",
    "reports/latest_devpost_copy_audit.md",
    "reports/latest_launch_decision_brief.html",
    "reports/latest_launch_decision_brief.json",
    "reports/latest_launch_decision_brief.md",
    "reports/latest_next_approval_packet.html",
    "reports/latest_next_approval_packet.json",
    "reports/latest_next_approval_packet.md",
    "reports/latest_content_rights_audit.html",
    "reports/latest_content_rights_audit.json",
    "reports/latest_content_rights_audit.md",
    "reports/latest_eligibility_compliance_audit.html",
    "reports/latest_eligibility_compliance_audit.json",
    "reports/latest_eligibility_compliance_audit.md",
    "reports/latest_post_action_evidence_brief.html",
    "reports/latest_post_action_evidence_brief.json",
    "reports/latest_post_action_evidence_brief.md",
    "reports/latest_official_source_freshness.html",
    "reports/latest_official_source_freshness.json",
    "reports/latest_official_source_freshness.md",
    "reports/latest_release_integrity_manifest.html",
    "reports/latest_release_integrity_manifest.json",
    "reports/latest_release_integrity_manifest.md",
    "reports/latest_splunk_app_package_manifest.html",
    "reports/latest_splunk_app_package_manifest.json",
    "reports/latest_splunk_app_package_manifest.md",
    "reports/latest_publication_command_plan.html",
    "reports/latest_publication_command_plan.json",
    "reports/latest_publication_command_plan.md",
    "reports/latest_public_repo_metadata.html",
    "reports/latest_public_repo_metadata.json",
    "reports/latest_public_repo_metadata.md",
    "reports/latest_public_repo_publish_brief.html",
    "reports/latest_public_repo_publish_brief.json",
    "reports/latest_public_repo_publish_brief.md",
    "reports/latest_public_repo_publication_preflight.html",
    "reports/latest_public_repo_publication_preflight.json",
    "reports/latest_public_repo_publication_preflight.md",
    "reports/latest_public_launch_snapshot.html",
    "reports/latest_public_launch_snapshot.json",
    "reports/latest_public_launch_snapshot.md",
    "reports/latest_splunk_mcp_command_plan.html",
    "reports/latest_splunk_mcp_command_plan.json",
    "reports/latest_splunk_mcp_command_plan.md",
    "reports/latest_splunk_mcp_proof_brief.html",
    "reports/latest_splunk_mcp_proof_brief.json",
    "reports/latest_splunk_mcp_proof_brief.md",
    "reports/latest_splunk_mcp_prompt_pack.html",
    "reports/latest_splunk_mcp_prompt_pack.json",
    "reports/latest_splunk_mcp_prompt_pack.md",
    "reports/latest_splunk_mcp_proof_capture_manifest.html",
    "reports/latest_splunk_mcp_proof_capture_manifest.json",
    "reports/latest_splunk_mcp_proof_capture_manifest.md",
    "reports/latest_submission_gate_ledger.html",
    "reports/latest_submission_gate_ledger.json",
    "reports/latest_submission_gate_ledger.md",
    "reports/latest_submission_deadline_burndown.html",
    "reports/latest_submission_deadline_burndown.json",
    "reports/latest_submission_deadline_burndown.md",
    "reports/latest_submission_url_validation.html",
    "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md",
    "submission/FINAL_SUBMISSION_CHECKLIST.md",
    "submission/JUDGE_REVIEW_PACKET.md",
    "submission/NEXT_APPROVAL_PACKET.md",
    "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md",
    "submission/PUBLIC_REPO_METADATA.md",
    "submission/VIDEO_UPLOAD_METADATA.md",
    "submission/SPLUNK_MCP_PROMPT_PACK.md",
    "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md",
    "submission/SUBMISSION_DEADLINE_BURNDOWN.md",
    "submission/USER_APPROVAL_GATES.md",
    "READY_FOR_REVIEW.md",
]

TEXT_SUFFIXES = {
    ".conf",
    ".csv",
    ".html",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".xml",
}

INTERNAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"C:\\" + "Users",
        "PC" + "_User",
        r"Desktop\\" + "AI" + "_Workspace",
        "AI" + "_Workspace",
        r"\." + "company",
        "private " + "workspace tree",
    ]
]

SECRET_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"ghp_[A-Za-z0-9]{20,}",
        r"sk-[A-Za-z0-9]{20,}",
        r"xox[baprs]-[A-Za-z0-9-]{20,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"AKIA[0-9A-Z]{16}",
        r"token=[A-Za-z0-9._~+/=-]{12,}",
        r"api[_-]?key=[A-Za-z0-9._~+/=-]{12,}",
    ]
]

ABSOLUTE_PATH_PATTERN = re.compile(r"[A-Za-z]:\\[^\n\r\"']+")


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def sanitize(value: str) -> str:
    return ABSOLUTE_PATH_PATTERN.sub("<local-path>", value)


def run_command(name: str, args: list[str], cwd: Path, checks: list[Check]) -> None:
    completed = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    output = (completed.stdout + "\n" + completed.stderr).strip()
    detail = sanitize(output[-700:] if output else "no output")
    add_check(checks, name, completed.returncode == 0, detail)


def add_skipped_video_refresh(name: str, checks: list[Check]) -> None:
    add_check(
        checks,
        name,
        True,
        "skipped in no-video structural smoke mode; existing packaged video report files are presence/scanned only",
    )


def check_zip_names(names: list[str], checks: list[Check]) -> None:
    unsafe = [
        name
        for name in names
        if name.startswith("/") or name.startswith("\\") or ".." in Path(name).parts
    ]
    add_check(checks, "zip path traversal guard", not unsafe, "unsafe: " + ", ".join(unsafe) if unsafe else "no unsafe zip names")
    missing = [item for item in REQUIRED_FILES if item not in names]
    add_check(checks, "zip required files", not missing, "missing: " + ", ".join(missing) if missing else f"{len(REQUIRED_FILES)} files present")


def scan_text_files(root: Path, checks: list[Check]) -> None:
    internal_hits: list[str] = []
    secret_hits: list[str] = []
    for path in root.rglob("*"):
        if path.is_dir() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            add_check(checks, f"text decode {rel}", False, "non-utf8 text candidate")
            continue
        for pattern in INTERNAL_PATTERNS:
            if pattern.search(text):
                internal_hits.append(f"{rel}:{pattern.pattern}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append(f"{rel}:{pattern.pattern}")
    add_check(checks, "extracted internal path scan", not internal_hits, "\n".join(internal_hits) if internal_hits else "no internal patterns")
    add_check(checks, "extracted secret-like scan", not secret_hits, "\n".join(secret_hits) if secret_hits else "no secret-like patterns")


def build_report(root: Path, zip_path: Path, include_video_refresh: bool = False) -> dict[str, Any]:
    checks: list[Check] = []
    if not zip_path.exists():
        add_check(checks, "release zip exists", False, f"missing: {zip_path}")
        return report_payload(root, zip_path, checks, [], 0)

    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        check_zip_names(names, checks)
        with tempfile.TemporaryDirectory(prefix="agentops_zip_smoke_") as temp_dir:
            extract_root = Path(temp_dir)
            archive.extractall(extract_root)
            scan_text_files(extract_root, checks)
            run_command("zip local SPL query pack", [sys.executable, "scripts/run_local_spl_query_pack.py"], extract_root, checks)
            run_command("zip public repo publication preflight", [sys.executable, "scripts/verify_public_repo_publication_gate.py"], extract_root, checks)
            run_command("zip external approval packet before consistency", [sys.executable, "scripts/build_external_approval_packet.py"], extract_root, checks)
            run_command("zip launch decision brief before consistency", [sys.executable, "scripts/build_launch_decision_brief.py"], extract_root, checks)
            run_command("zip next approval packet before consistency", [sys.executable, "scripts/build_next_approval_packet.py"], extract_root, checks)
            run_command("zip approval consistency audit", [sys.executable, "scripts/build_approval_consistency_audit.py"], extract_root, checks)
            if include_video_refresh:
                run_command("zip video readiness report", [sys.executable, "scripts/build_video_readiness_report.py"], extract_root, checks)
            else:
                add_skipped_video_refresh("zip video readiness report", checks)
            run_command("zip claim evidence matrix", [sys.executable, "scripts/build_claim_evidence_matrix.py"], extract_root, checks)
            run_command("zip public repo dry run", [sys.executable, "scripts/build_public_repo_dry_run.py"], extract_root, checks)
            run_command("zip external approval packet", [sys.executable, "scripts/build_external_approval_packet.py"], extract_root, checks)
            run_command("zip submission URL apply plan", [sys.executable, "scripts/prepare_submission_urls.py"], extract_root, checks)
            if include_video_refresh:
                run_command("zip video command plan", [sys.executable, "scripts/build_video_command_plan.py"], extract_root, checks)
                run_command("zip video cue sheet", [sys.executable, "scripts/build_video_cue_sheet.py"], extract_root, checks)
                run_command("zip video dry run", [sys.executable, "scripts/build_video_dry_run.py"], extract_root, checks)
                run_command("zip video upload metadata", [sys.executable, "scripts/build_video_upload_metadata.py"], extract_root, checks)
            else:
                add_skipped_video_refresh("zip video command plan", checks)
                add_skipped_video_refresh("zip video cue sheet", checks)
                add_skipped_video_refresh("zip video dry run", checks)
                add_skipped_video_refresh("zip video upload metadata", checks)
            run_command("zip publication command plan", [sys.executable, "scripts/build_publication_command_plan.py"], extract_root, checks)
            run_command("zip public repo metadata", [sys.executable, "scripts/build_public_repo_metadata.py"], extract_root, checks)
            run_command("zip public repo publish brief", [sys.executable, "scripts/build_public_repo_publish_brief.py"], extract_root, checks)
            run_command("zip public launch snapshot", [sys.executable, "scripts/build_public_launch_snapshot.py"], extract_root, checks)
            run_command("zip Splunk MCP command plan", [sys.executable, "scripts/build_splunk_mcp_command_plan.py"], extract_root, checks)
            run_command("zip Splunk MCP proof brief", [sys.executable, "scripts/build_splunk_mcp_proof_brief.py"], extract_root, checks)
            run_command("zip Splunk MCP prompt pack", [sys.executable, "scripts/build_splunk_mcp_prompt_pack.py"], extract_root, checks)
            run_command("zip Splunk MCP proof capture manifest", [sys.executable, "scripts/build_splunk_mcp_proof_capture_manifest.py"], extract_root, checks)
            run_command("zip submission gate ledger", [sys.executable, "scripts/build_submission_gate_ledger.py"], extract_root, checks)
            run_command("zip submission deadline burndown", [sys.executable, "scripts/build_submission_deadline_burndown.py"], extract_root, checks)
            run_command("zip submission review index", [sys.executable, "scripts/build_submission_review_index.py"], extract_root, checks)
            run_command("zip judge quickstart", [sys.executable, "scripts/build_judge_quickstart.py"], extract_root, checks)
            run_command("zip judge scorecard", [sys.executable, "scripts/build_judge_scorecard.py"], extract_root, checks)
            run_command("zip launch decision brief", [sys.executable, "scripts/build_launch_decision_brief.py"], extract_root, checks)
            run_command("zip content rights audit", [sys.executable, "scripts/build_content_rights_audit.py"], extract_root, checks)
            run_command("zip eligibility compliance audit", [sys.executable, "scripts/build_eligibility_compliance_audit.py"], extract_root, checks)
            run_command("zip next approval packet", [sys.executable, "scripts/build_next_approval_packet.py"], extract_root, checks)
            run_command("zip unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"], extract_root, checks)
            run_command("zip post-action evidence brief", [sys.executable, "scripts/build_post_action_evidence_brief.py"], extract_root, checks)
            run_command("zip URL writeback dry run", [sys.executable, "scripts/build_url_writeback_dry_run.py"], extract_root, checks)
            run_command("zip official source freshness", [sys.executable, "scripts/build_official_source_freshness.py"], extract_root, checks)
            run_command("zip release integrity manifest", [sys.executable, "scripts/build_release_integrity_manifest.py"], extract_root, checks)
            run_command("zip Splunk app package", [sys.executable, "scripts/package_splunk_app.py"], extract_root, checks)
            run_command("zip Splunk app validation", [sys.executable, "scripts/validate_splunk_app.py"], extract_root, checks)
            run_command("zip claim boundary validation", [sys.executable, "scripts/validate_claim_boundaries.py"], extract_root, checks)
            run_command("zip submission URL validation", [sys.executable, "scripts/validate_submission_urls.py"], extract_root, checks)
            run_command("zip Devpost final copy export", [sys.executable, "scripts/export_devpost_final_copy.py"], extract_root, checks)
            run_command("zip Devpost submit command plan", [sys.executable, "scripts/build_devpost_submit_command_plan.py"], extract_root, checks)
            run_command("zip Devpost manual fill brief", [sys.executable, "scripts/build_devpost_manual_fill_brief.py"], extract_root, checks)

    return report_payload(root, zip_path, checks, names, zip_path.stat().st_size)


def report_payload(root: Path, zip_path: Path, checks: list[Check], names: list[str], size_bytes: int) -> dict[str, Any]:
    failed = [check for check in checks if not check.passed]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "pass" if not failed else "fail",
        "root": root.name,
        "zip": zip_path.relative_to(root).as_posix() if zip_path.exists() else zip_path.name,
        "zip_size_bytes": size_bytes,
        "zip_file_count": len(names),
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "publication_boundary": "This smoke test extracts the local release zip only. It does not publish, upload, or submit anything.",
        "video_refresh_mode": "included" if any(check.name.startswith("zip video") and "skipped" not in check.detail for check in checks) else "skipped",
    }


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def render_html(report: dict[str, Any]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(check['name'])}</td>"
        f"<td>{html.escape(check['status'])}</td>"
        f"<td>{html.escape(check['detail'])}</td>"
        "</tr>"
        for check in report["checks"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Release Zip Smoke Test</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; }}
    header {{ background: #17202a; color: #fff; padding: 28px 36px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 18px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; }}
    .pass {{ color: #127c76; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Release Zip Smoke Test</h1>
    <p>Status: <span class="{html.escape(report['status'])}">{html.escape(report['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <p>Zip: <code>{html.escape(report['zip'])}</code></p>
      <p>Files: {html.escape(str(report['zip_file_count']))}</p>
      <p>Size bytes: {html.escape(str(report['zip_size_bytes']))}</p>
      <p class="pending">{html.escape(report['publication_boundary'])}</p>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def run(root: Path, include_video_refresh: bool = False) -> dict[str, Any]:
    zip_path = root / "release" / ZIP_NAME
    report = build_report(root, zip_path, include_video_refresh=include_video_refresh)
    write_json(root / "reports/latest_release_zip_smoke_test.json", report)
    (root / "reports/latest_release_zip_smoke_test.html").write_text(render_html(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the packaged public candidate release zip.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument(
        "--include-video-refresh",
        action="store_true",
        help="Run video planning/report builders inside the extracted zip. Default skips them for structural-only revalidation.",
    )
    args = parser.parse_args()
    report = run(Path(args.root).resolve(), include_video_refresh=args.include_video_refresh)
    print(json.dumps({
        "status": report["status"],
        "failed_count": report["failed_count"],
        "zip_file_count": report["zip_file_count"],
        "video_refresh_mode": report["video_refresh_mode"],
    }, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
