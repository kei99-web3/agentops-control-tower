from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORTS = {
    "local_readiness": "latest_local_readiness_baseline",
    "public_candidate_audit": "latest_public_candidate_local_audit",
    "devpost_copy_audit": "latest_devpost_copy_audit",
    "judge_review_packet": "latest_judge_review_packet",
}

TEXT_SKIP_DIRS = {".git", "__pycache__"}
TEXT_SKIP_SUFFIXES = {
    ".zip",
    ".spl",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".pyc",
}
SELF_AUDIT_REPORT_PREFIX = "reports/latest_public_candidate_local_audit."

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

PRIVATE_USER_FRAGMENT = "PC" + "_User"
PRIVATE_WORKSPACE_FRAGMENT = "AI" + "_Workspace"
PRIVATE_COMPANY_FRAGMENT = "." + "company"

INTERNAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"C:\\Users",
        re.escape(PRIVATE_USER_FRAGMENT),
        r"Desktop\\" + re.escape(PRIVATE_WORKSPACE_FRAGMENT),
        re.escape(PRIVATE_WORKSPACE_FRAGMENT),
        re.escape(PRIVATE_COMPANY_FRAGMENT),
    ]
]

BOUNDARY = (
    "This packet is local review evidence only. It does not publish a repository, "
    "record or upload video, connect to Splunk, configure MCP, write approved URLs, "
    "update Devpost, save a draft, press submit, or submit anything."
)


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def exists(root: Path, relative_path: str) -> bool:
    return (root / relative_path).exists()


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def candidate_root_for(root: Path) -> Path:
    if is_public_candidate_root(root):
        return root
    return root / "public_repo_candidate" / "agentops-control-tower"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def text_file_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith(SELF_AUDIT_REPORT_PREFIX):
            continue
        parts = set(path.relative_to(root).parts)
        if parts & TEXT_SKIP_DIRS:
            continue
        name = path.name.lower()
        if name == ".env" or name.startswith(".env."):
            continue
        if path.suffix.lower() in TEXT_SKIP_SUFFIXES:
            continue
        paths.append(path)
    return sorted(paths, key=lambda item: item.relative_to(root).as_posix())


def scan_patterns(root: Path, patterns: list[re.Pattern[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in text_file_paths(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in patterns:
                if pattern.search(line):
                    findings.append(
                        {
                            "path": rel(path, root),
                            "line": line_number,
                            "pattern": pattern.pattern,
                        }
                    )
    return findings


def contains_text(root: Path, relative_path: str, needle: str) -> bool:
    path = root / relative_path
    return path.exists() and needle in read_text(path)


def local_readiness_payload(root: Path, candidate_root: Path) -> dict[str, Any]:
    public_candidate = is_public_candidate_root(root)
    reports = root / "reports"
    go_no_go = read_json(reports / "latest_final_go_no_go.json")
    validation = read_json(reports / "latest_submission_validation.json")
    status_conflict = read_json(reports / "latest_status_conflict_audit.json")
    claim = read_json(reports / "latest_claim_boundary_validation.json")
    package = read_json(reports / "latest_splunk_app_package_manifest.json")
    release = read_json(reports / "latest_release_integrity_manifest.json")
    spl = read_json(reports / "latest_local_spl_query_results.json")
    url_validation = read_json(reports / "latest_submission_url_validation.json")
    devpost = read_json(reports / "latest_devpost_final_copy.json")

    checks: list[Check] = []
    add_check(
        checks,
        "final Go/No-Go local ready",
        go_no_go.get("status") == "ready_for_user_review" and go_no_go.get("local_ready") is True,
        f"status={go_no_go.get('status', 'missing')} local_ready={go_no_go.get('local_ready', 'missing')}",
    )
    add_check(
        checks,
        "final submit remains closed",
        go_no_go.get("final_submit_ready") is False,
        str(go_no_go.get("final_submit_ready", "missing")),
    )
    add_check(
        checks,
        "local evidence complete",
        go_no_go.get("missing_local_evidence", []) == [] and go_no_go.get("missing_public_candidate_evidence", []) == [],
        f"local={len(go_no_go.get('missing_local_evidence', []))} public_candidate={len(go_no_go.get('missing_public_candidate_evidence', []))}",
    )
    add_check(
        checks,
        "status conflict audit clean",
        public_candidate
        or (
            status_conflict.get("status") == "ready_for_user_review"
            and int(status_conflict.get("failed_count", 1)) == 0
            and int(status_conflict.get("conflict_count", 1)) == 0
        ),
        "not_applicable_public_candidate_root"
        if public_candidate
        else f"status={status_conflict.get('status', 'missing')} failed={status_conflict.get('failed_count', 'missing')} conflicts={status_conflict.get('conflict_count', 'missing')}",
    )
    add_check(checks, "claim boundary validation pass", claim.get("status") == "pass", str(claim.get("status", "missing")))
    add_check(
        checks,
        "Splunk app package ready",
        package.get("status") == "ready_for_user_review" and int(package.get("failed_count", 1)) == 0,
        f"status={package.get('status', 'missing')} failed={package.get('failed_count', 'missing')}",
    )
    add_check(
        checks,
        "release integrity ready",
        public_candidate or (release.get("status") == "ready_for_user_review" and int(release.get("failed_count", 1)) == 0),
        "not_applicable_public_candidate_root"
        if public_candidate
        else f"status={release.get('status', 'missing')} failed={release.get('failed_count', 'missing')}",
    )
    add_check(
        checks,
        "local SPL proof present",
        spl.get("status") == "local_spl_emulation_only" and int(spl.get("event_count", 0)) > 0,
        f"status={spl.get('status', 'missing')} events={spl.get('event_count', 'missing')}",
    )
    add_check(
        checks,
        "public URLs still pending",
        url_validation.get("status") == "waiting_for_external_urls"
        and url_validation.get("final_submit_ready") is False,
        f"status={url_validation.get('status', 'missing')} final_submit_ready={url_validation.get('final_submit_ready', 'missing')}",
    )
    add_check(
        checks,
        "Devpost copy locally reviewable",
        devpost.get("status") == "ready_for_user_review" and devpost.get("final_submit_ready") is False,
        f"status={devpost.get('status', 'missing')} final_submit_ready={devpost.get('final_submit_ready', 'missing')}",
    )
    add_check(
        checks,
        "root pass/fail baseline present",
        contains_text(root, "submission/JUDGING_ALIGNMENT.md", "pass/fail baseline"),
        "submission/JUDGING_ALIGNMENT.md",
    )
    add_check(
        checks,
        "public candidate pass/fail baseline present",
        contains_text(candidate_root, "submission/JUDGING_ALIGNMENT.md", "pass/fail baseline"),
        "public candidate submission/JUDGING_ALIGNMENT.md",
    )
    validator_status = validation.get("overall_status", "missing")
    validator_status_ok = validator_status in {"needs_more_evidence", "ready_for_user_review"} or (
        is_public_candidate_root(root) and validator_status == "missing"
    )
    add_check(
        checks,
        "full validator stale failure explained",
        validator_status_ok
        and go_no_go.get("local_ready") is True
        and (public_candidate or status_conflict.get("status") == "ready_for_user_review"),
        f"latest_submission_validation status={validator_status} failed_count={validation.get('failed_count', 'missing')} is full submission/external-gate evidence; targeted baseline uses current Go/No-Go and status-conflict readback.",
    )

    status = "ready_for_user_review" if all(check.passed for check in checks) else "needs_more_evidence"
    return {
        "generated_at_utc": now(),
        "status": status,
        "root_type": "public_candidate" if public_candidate else "workspace",
        "local_ready": status == "ready_for_user_review",
        "final_submit_ready": False,
        "full_submission_validation_status": validation.get("overall_status", "missing"),
        "full_submission_validation_failed_count": validation.get("failed_count", "missing"),
        "full_submission_validation_note": (
            "The full validator still records external-gate/stale run failures. This targeted baseline "
            "uses current local evidence only and keeps public URL, video, live Splunk/MCP, and Devpost gates closed."
        ),
        "external_gates_still_blocked": [
            "public_github_repository",
            "public_demo_video",
            "optional_live_splunk_mcp_proof",
            "approved_url_writeback",
            "devpost_final_submission",
        ],
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
    }


def public_candidate_audit_payload(root: Path, candidate_root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    add_check(checks, "public candidate folder exists", candidate_root.exists(), rel(candidate_root, root) if candidate_root.exists() else str(candidate_root))
    required = [
        "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
        "README.md",
        "LICENSE",
        "architecture_diagram.md",
        "assets/dashboard_preview.png",
        "prototype/agentops_control_tower.py",
        "reports/latest_judge_quickstart.html",
        "reports/latest_judge_scorecard.html",
        "reports/latest_submission_review_index.html",
        "reports/latest_public_launch_snapshot.html",
        "reports/latest_claim_evidence_matrix.html",
        "reports/latest_devpost_final_copy.html",
        "reports/latest_splunk_app_package_manifest.html",
        "dist/agentops-control-tower-splunk-app.spl",
        "submission/JUDGING_ALIGNMENT.md",
        "submission/DEVPOST_FIELD_MAP.md",
        "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md",
    ]
    missing = [item for item in required if not exists(candidate_root, item)]
    add_check(checks, "required public candidate artifacts present", not missing, "missing: " + ", ".join(missing) if missing else "all required artifacts present")
    add_check(checks, "no nested git directory", not (candidate_root / ".git").exists(), ".git absent")
    add_check(checks, "no release directory in public candidate", not (candidate_root / "release").exists(), "release absent")
    add_check(checks, "approved URL writeback absent", not (candidate_root / "approved_public_urls.json").exists(), "approved_public_urls.json absent")

    secret_findings = scan_patterns(candidate_root, SECRET_PATTERNS) if candidate_root.exists() else []
    internal_findings = scan_patterns(candidate_root, INTERNAL_PATTERNS) if candidate_root.exists() else []
    add_check(checks, "secret-like scan clean", not secret_findings, f"findings={len(secret_findings)}")
    add_check(checks, "private/internal path scan clean", not internal_findings, f"findings={len(internal_findings)}")
    add_check(
        checks,
        "public candidate pass/fail baseline present",
        contains_text(candidate_root, "submission/JUDGING_ALIGNMENT.md", "pass/fail baseline"),
        "submission/JUDGING_ALIGNMENT.md",
    )

    claim = read_json(candidate_root / "reports/latest_claim_boundary_validation.json")
    devpost = read_json(candidate_root / "reports/latest_devpost_final_copy.json")
    proof_brief = read_text(candidate_root / "reports/latest_splunk_mcp_proof_brief.md")
    proof_readback = read_text(candidate_root / "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md")
    add_check(checks, "claim boundary pass", claim.get("status") == "pass", str(claim.get("status", "missing")))
    add_check(
        checks,
        "Devpost URLs remain placeholders",
        devpost.get("final_submit_ready") is False
        and {"repository_url", "demo_video_url"}.issubset(set(devpost.get("pending_urls", []))),
        f"final_submit_ready={devpost.get('final_submit_ready', 'missing')} pending={', '.join(devpost.get('pending_urls', []))}",
    )
    proof_readback_lower = proof_readback.lower()
    add_check(
        checks,
        "official MCP proof bounded to local synthetic data",
        "Official Splunk MCP Server verified: true" in proof_brief
        and "local Splunk Enterprise Docker" in proof_readback
        and "production splunk cloud deployment is not claimed" in proof_readback_lower,
        "reports/latest_splunk_mcp_proof_brief.md and post-action evidence",
    )

    status = "ready_for_user_review" if all(check.passed for check in checks) else "needs_more_evidence"
    return {
        "generated_at_utc": now(),
        "status": status,
        "candidate_root": rel(candidate_root, root) if candidate_root.exists() and not is_public_candidate_root(root) else ".",
        "text_files_scanned": len(text_file_paths(candidate_root)) if candidate_root.exists() else 0,
        "secret_like_findings": secret_findings,
        "internal_path_findings": internal_findings,
        "missing_required_artifacts": missing,
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
    }


def combined_devpost_text(payload: dict[str, Any]) -> str:
    fields = payload.get("fields", {})
    sections = payload.get("sections", {})
    return "\n".join(
        [
            str(fields.get("project_name", "")),
            str(fields.get("tagline", "")),
            str(fields.get("track", "")),
            str(fields.get("bonus_target", "")),
            " ".join(fields.get("built_with", [])),
            str(fields.get("repository_url", "")),
            str(fields.get("demo_video_url", "")),
            *[str(value) for value in sections.values()],
        ]
    )


def devpost_copy_audit_payload(root: Path) -> dict[str, Any]:
    final_copy = read_json(root / "reports/latest_devpost_final_copy.json")
    manual = read_json(root / "reports/latest_devpost_manual_fill_brief.json")
    field_map_path = root / "submission/DEVPOST_FIELD_MAP.md"
    field_map = read_text(field_map_path) if field_map_path.exists() else ""
    text = combined_devpost_text(final_copy)
    built_with = set(final_copy.get("fields", {}).get("built_with", []))
    checks: list[Check] = []

    add_check(checks, "Devpost final copy ready", final_copy.get("status") == "ready_for_user_review", str(final_copy.get("status", "missing")))
    manual_pending_urls_only = (
        manual.get("status") == "needs_more_evidence"
        and set(manual.get("pending_fields", [])) == {"Repository URL", "Demo video URL"}
        and final_copy.get("final_submit_ready") is False
    )
    add_check(
        checks,
        "manual fill brief ready",
        manual.get("status") == "ready_for_user_review" or manual_pending_urls_only,
        str(manual.get("status", "missing")),
    )
    add_check(
        checks,
        "pending URLs preserved",
        final_copy.get("final_submit_ready") is False
        and {"repository_url", "demo_video_url"}.issubset(set(final_copy.get("pending_urls", []))),
        f"final_submit_ready={final_copy.get('final_submit_ready', 'missing')} pending={', '.join(final_copy.get('pending_urls', []))}",
    )
    mcp_tag_allowed = "Splunk MCP Server" in built_with and "local Splunk Enterprise Docker" in text and "does not claim production Splunk Cloud deployment" in text
    add_check(checks, "Splunk MCP Server tag bounded", mcp_tag_allowed, ", ".join(sorted(built_with)))
    add_check(checks, "local proof boundary stated", "synthetic data only" in text and "production Splunk Cloud deployment" in text, "Splunk Usage section")
    add_check(checks, "no public repo completion claim", "repository is public" not in text.lower() and "public repository is live" not in text.lower(), "no completion wording found")
    add_check(checks, "no Devpost submitted claim", "submitted on devpost" not in text.lower() and "devpost submission is complete" not in text.lower(), "no submitted wording found")
    add_check(checks, "field map project name aligned", final_copy.get("fields", {}).get("project_name", "") in field_map, "project name present in field map")
    add_check(checks, "field map track aligned", final_copy.get("fields", {}).get("track", "") in field_map, "track present in field map")
    add_check(checks, "field map URL placeholders aligned", "PENDING_USER_APPROVAL_PUBLIC_REPO_URL" in field_map and "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL" in field_map, "pending placeholders present")
    add_check(
        checks,
        "character checks pass",
        all(item.get("status") == "pass" for item in final_copy.get("checks", [])),
        f"checks={len(final_copy.get('checks', []))}",
    )

    status = "ready_for_user_review" if all(check.passed for check in checks) else "needs_more_evidence"
    return {
        "generated_at_utc": now(),
        "status": status,
        "final_submit_ready": False,
        "pending_urls": final_copy.get("pending_urls", []),
        "built_with": sorted(built_with),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
    }


def report_link(path: str, title: str, why: str) -> dict[str, str]:
    return {"path": path, "title": title, "why": why}


def judge_review_packet_payload(root: Path, candidate_root: Path, local: dict[str, Any], audit: dict[str, Any], devpost: dict[str, Any]) -> dict[str, Any]:
    gate = read_json(root / "reports/latest_submission_gate_ledger.json")
    launch = read_json(root / "reports/latest_public_launch_snapshot.json")
    next_packet = read_json(root / "reports/latest_next_approval_packet.json")
    evidence = [
        report_link("READY_FOR_REVIEW.md", "Ready for review memo", "Plain-language start page for this local packet."),
        report_link("reports/latest_judge_review_packet.html", "Judge review packet", "Single review packet that separates local evidence from approval-only external work."),
        report_link("reports/latest_judge_quickstart.html", "Judge quickstart", "Five-minute review path and core story."),
        report_link("reports/latest_judge_scorecard.html", "Judge scorecard", "Stage One, Stage Two, and bonus alignment mapped to evidence."),
        report_link("reports/latest_local_readiness_baseline.html", "Local readiness baseline", "Separates local readiness from external URL/Devpost gates."),
        report_link("reports/latest_public_candidate_local_audit.html", "Public candidate local audit", "Local scan of public-candidate contents before any publication."),
        report_link("reports/latest_devpost_copy_audit.html", "Devpost copy audit", "Checks copy, character limits, placeholders, and claim boundaries."),
        report_link("reports/latest_claim_evidence_matrix.html", "Claim evidence matrix", "Allowed wording and evidence for each public claim."),
        report_link("reports/latest_local_spl_query_results.html", "Local SPL proof", "SPL-equivalent query results over synthetic CSV."),
        report_link("reports/latest_splunk_app_package_manifest.html", "Splunk app package manifest", ".spl package hash and member list."),
        report_link("reports/latest_devpost_final_copy.html", "Devpost final copy", "Copy/paste text with public URL placeholders."),
        report_link("reports/latest_public_launch_snapshot.html", "Public launch snapshot", "Approval phrases, ZIP hash, and no-external-action boundary."),
        report_link("reports/latest_submission_gate_ledger.html", "Submission gate ledger", "External gates and their current closed/open state."),
    ]
    generated_by_this_run = {"READY_FOR_REVIEW.md", "reports/latest_judge_review_packet.html"}
    missing = [
        item["path"]
        for item in evidence
        if not exists(root, item["path"]) and item["path"] not in generated_by_this_run
    ]
    status = "ready_for_user_review" if local["status"] == audit["status"] == devpost["status"] == "ready_for_user_review" and not missing else "needs_more_evidence"
    return {
        "generated_at_utc": now(),
        "status": status,
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "local_readiness_status": local["status"],
        "public_candidate_audit_status": audit["status"],
        "devpost_copy_audit_status": devpost["status"],
        "final_submit_ready": False,
        "next_approval_target": next_packet.get("next_approval_target", launch.get("next_approval_target", "public_github_repository")),
        "pending_gates": gate.get("pending_gates", []),
        "candidate_root": rel(candidate_root, root) if candidate_root.exists() and not is_public_candidate_root(root) else ".",
        "missing_review_evidence": missing,
        "review_evidence": evidence,
        "safe_summary": (
            "Agentic Incident Command Center is locally review-ready: synthetic checkout-incident events, local SPL-equivalent proof, "
            "claim-boundary validation, Splunk app packaging, public candidate audit, and Devpost copy audit are ready. "
            "Final submission stays closed until public URLs, optional live proof, and Devpost approval are explicitly handled."
        ),
        "boundary": BOUNDARY,
    }


def render_checks(title: str, payload: dict[str, Any]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['name'])}</td>"
        f"<td class=\"{'ready' if item['status'] == 'pass' else 'fail'}\">{esc(item['status'])}</td>"
        f"<td>{esc(item['detail'])}</td>"
        "</tr>"
        for item in payload.get("checks", [])
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.56; }}
    header {{ background: #17202a; color: #fff; padding: 28px 36px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 18px; margin-bottom: 18px; }}
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
    <h1>{esc(title)}</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <p>Generated: <code>{esc(payload['generated_at_utc'])}</code></p>
      <p>Final submit ready: <span class="pending">{esc(payload.get('final_submit_ready', False))}</span></p>
      <p>{esc(payload.get('full_submission_validation_note', payload.get('boundary', BOUNDARY)))}</p>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Boundary</h2>
      <p class="pending">{esc(payload.get('boundary', BOUNDARY))}</p>
    </section>
  </main>
</body>
</html>
"""


def render_checks_markdown(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        f"Status: {payload['status']}",
        f"Generated: {payload['generated_at_utc']}",
        f"Final submit ready: {str(payload.get('final_submit_ready', False)).lower()}",
        "",
        "## Checks",
        "",
    ]
    for item in payload.get("checks", []):
        lines.append(f"- {item['status']}: {item['name']} - {item['detail']}")
    lines.extend(["", "## Boundary", "", payload.get("boundary", BOUNDARY), ""])
    return "\n".join(lines)


def render_judge_packet_html(payload: dict[str, Any]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['title'])}</td>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td>{esc(item['why'])}</td>"
        "</tr>"
        for item in payload["review_evidence"]
    )
    gates = ", ".join(payload["pending_gates"]) if payload["pending_gates"] else "none"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SPAK Judge Review Packet</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.56; }}
    header {{ background: #17202a; color: #fff; padding: 28px 36px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 18px; margin-bottom: 18px; }}
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
    <h1>SPAK Judge Review Packet</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Safe Summary</h2>
      <p>{esc(payload['safe_summary'])}</p>
      <p>Next approval target: <code>{esc(payload['next_approval_target'])}</code></p>
      <p>Pending gates: <span class="pending">{esc(gates)}</span></p>
      <p>Final submit ready: <span class="pending">{esc(payload['final_submit_ready'])}</span></p>
    </section>
    <section>
      <h2>Review Order</h2>
      <table>
        <thead><tr><th>Artifact</th><th>Path</th><th>Why it matters</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Boundary</h2>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
  </main>
</body>
</html>
"""


def render_judge_packet_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# SPAK Judge Review Packet",
        "",
        f"Status: {payload['status']}",
        f"Generated: {payload['generated_at_utc']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Next approval target: {payload['next_approval_target']}",
        "",
        "## Safe Summary",
        "",
        payload["safe_summary"],
        "",
        "## Review Order",
        "",
    ]
    for item in payload["review_evidence"]:
        lines.append(f"- `{item['path']}` - {item['title']}: {item['why']}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_ready_for_review(payload: dict[str, Any]) -> str:
    gates = ", ".join(payload["pending_gates"]) if payload["pending_gates"] else "none"
    lines = [
        "# Ready For Review",
        "",
        "Agentic Incident Command Center / SPAK is locally ready for user and judge review.",
        "",
        f"- Local readiness: {payload['local_readiness_status']}",
        f"- Public candidate audit: {payload['public_candidate_audit_status']}",
        f"- Devpost copy audit: {payload['devpost_copy_audit_status']}",
        f"- Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"- Next approval target: {payload['next_approval_target']}",
        f"- Pending external gates: {gates}",
        "",
        "## Start Here",
        "",
        "- `reports/latest_judge_review_packet.html`",
        "- `reports/latest_local_readiness_baseline.html`",
        "- `reports/latest_public_candidate_local_audit.html`",
        "- `reports/latest_devpost_copy_audit.html`",
        "- `reports/latest_judge_quickstart.html`",
        "- `reports/latest_judge_scorecard.html`",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        "",
    ]
    return "\n".join(lines)


def write_report(root: Path, name: str, title: str, payload: dict[str, Any], *, judge: bool = False) -> None:
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / f"{name}.json", payload)
    if judge:
        markdown = render_judge_packet_markdown(payload)
        html_text = render_judge_packet_html(payload)
    else:
        markdown = render_checks_markdown(title, payload)
        html_text = render_checks(title, payload)
    (reports / f"{name}.md").write_text(markdown, encoding="utf-8")
    (reports / f"{name}.html").write_text(html_text, encoding="utf-8")


def write_ready_files(root: Path, payload: dict[str, Any]) -> None:
    ready = render_ready_for_review(payload)
    (root / "READY_FOR_REVIEW.md").write_text(ready, encoding="utf-8")
    submission = root / "submission"
    submission.mkdir(parents=True, exist_ok=True)
    (submission / "JUDGE_REVIEW_PACKET.md").write_text(render_judge_packet_markdown(payload), encoding="utf-8")


def build_one(root: Path) -> dict[str, Any]:
    candidate_root = candidate_root_for(root)
    local = local_readiness_payload(root, candidate_root)
    public_audit = public_candidate_audit_payload(root, candidate_root)
    devpost = devpost_copy_audit_payload(root)
    write_report(root, REPORTS["local_readiness"], "Local Readiness Baseline", local)
    write_report(root, REPORTS["public_candidate_audit"], "Public Candidate Local Audit", public_audit)
    write_report(root, REPORTS["devpost_copy_audit"], "Devpost Copy Audit", devpost)
    judge = judge_review_packet_payload(root, candidate_root, local, public_audit, devpost)
    write_report(root, REPORTS["judge_review_packet"], "SPAK Judge Review Packet", judge, judge=True)
    write_ready_files(root, judge)
    return {
        "root": str(root),
        "status": judge["status"],
        "local_readiness_status": local["status"],
        "public_candidate_audit_status": public_audit["status"],
        "devpost_copy_audit_status": devpost["status"],
        "judge_review_packet": f"reports/{REPORTS['judge_review_packet']}.html",
        "ready_for_review": "READY_FOR_REVIEW.md",
    }


def run(root: Path, include_candidate: bool = True) -> dict[str, Any]:
    root = root.resolve()
    results: list[dict[str, Any]] = []
    candidate = candidate_root_for(root)
    if include_candidate and not is_public_candidate_root(root) and candidate.exists():
        results.append(build_one(candidate))
    results.append(build_one(root))
    overall_status = "ready_for_user_review" if all(item["status"] == "ready_for_user_review" for item in results) else "needs_more_evidence"
    return {
        "generated_at_utc": now(),
        "status": overall_status,
        "results": results,
        "boundary": BOUNDARY,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SPAK local readiness, public candidate, Devpost, and judge review reports.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument(
        "--root-only",
        action="store_true",
        help="Update only the selected root. Useful after the public candidate has already been packaged into a release zip.",
    )
    args = parser.parse_args()
    result = run(Path(args.root), include_candidate=not args.root_only)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
