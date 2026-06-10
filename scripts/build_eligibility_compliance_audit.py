from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This eligibility and compliance audit is local review evidence only. It does not determine legal eligibility, "
    "submit Devpost forms, create accounts, publish a repository, upload video, write approved URLs, configure Splunk, "
    "or submit anything."
)

SOURCE_CHECKED_AT_JST = "2026-06-04 JST"


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def source_urls() -> list[dict[str, str]]:
    return [
        {
            "name": "Devpost official rules",
            "url": "https://splunk.devpost.com/rules",
            "local_relevance": "Eligibility, project ownership, team representative, language, IP, testing, and submission rules.",
        },
        {
            "name": "Devpost overview",
            "url": "https://splunk.devpost.com/",
            "local_relevance": "Challenge scope, deadline, tracks, and public submission entrypoint.",
        },
    ]


def key_english_materials() -> list[str]:
    return [
        "README.md",
        "architecture_diagram.md",
        "submission/DEVPOST_SUBMISSION_DRAFT.md",
        "submission/DEVPOST_FIELD_MAP.md",
        "submission/DEMO_VIDEO_SCRIPT.md",
        "submission/VIDEO_RECORDING_RUNBOOK.md",
        "submission/SUBMISSION_REVIEW_QA.md",
        "submission/SUBMISSION_LAUNCH_RUNBOOK.md",
        "submission/JUDGING_ALIGNMENT.md",
        "submission/OFFICIAL_REQUIREMENTS_AUDIT.md",
    ]


def japanese_char_hits(root: Path, paths: list[str]) -> list[str]:
    pattern = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
    hits: list[str] = []
    for rel_path in paths:
        path = root / rel_path
        if not path.exists():
            hits.append(f"missing:{rel_path}")
            continue
        text = read_text(path)
        if pattern.search(text):
            hits.append(rel_path)
    return hits


def human_confirmation_items() -> list[dict[str, str]]:
    return [
        {
            "key": "age_and_residence",
            "rule_area": "Eligibility",
            "confirmation_needed": "Entrant is at least the age of majority where they reside and is not resident/domiciled in an excluded jurisdiction.",
            "why_codex_cannot_confirm": "This depends on personal/legal facts and should be confirmed by the user before Devpost submission.",
        },
        {
            "key": "no_excluded_role_or_conflict",
            "rule_area": "Eligibility and conflict of interest",
            "confirmation_needed": "Entrant is not a judge, promotion entity, government/state-owned entity, excluded affiliate, household member, or otherwise conflicted participant.",
            "why_codex_cannot_confirm": "This depends on employment, affiliation, household, and conflict facts outside the local packet.",
        },
        {
            "key": "team_or_representative_authority",
            "rule_area": "Team representation",
            "confirmation_needed": "If submitted as a team or organization, the submitter is authorized to act as the representative and the team size is within the rules.",
            "why_codex_cannot_confirm": "The local packet does not know whether the Devpost entry will be individual, team, or organization.",
        },
        {
            "key": "ownership_and_ip",
            "rule_area": "Submission ownership and IP",
            "confirmation_needed": "The entrant owns the submitted work or has permission for every included component, and no third-party rights are violated.",
            "why_codex_cannot_confirm": "The package can audit files and licenses, but final ownership representation belongs to the entrant.",
        },
        {
            "key": "no_sponsor_support_conflict",
            "rule_area": "Financial or preferential support",
            "confirmation_needed": "The project was not developed with prohibited financial or preferential support from Sponsor or Administrator.",
            "why_codex_cannot_confirm": "This depends on external business, employment, funding, and contract facts.",
        },
    ]


def automated_evidence(root: Path) -> list[dict[str, Any]]:
    content_rights = read_json(root / "reports/latest_content_rights_audit.json")
    url_validation = read_json(root / "reports/latest_submission_url_validation.json")
    official_audit = read_text(root / "submission/OFFICIAL_REQUIREMENTS_AUDIT.md")
    devpost_draft = read_text(root / "submission/DEVPOST_SUBMISSION_DRAFT.md")
    readme = read_text(root / "README.md")
    language_hits = japanese_char_hits(root, key_english_materials())
    return [
        {
            "key": "new_or_significantly_updated_project",
            "status": "pass" if "created locally on 2026-06-03 JST" in official_audit else "needs_review",
            "evidence": "submission/OFFICIAL_REQUIREMENTS_AUDIT.md",
            "detail": "Local audit states the project was created locally on 2026-06-03 JST during the submission period.",
        },
        {
            "key": "public_materials_in_english",
            "status": "pass" if not language_hits else "needs_review",
            "evidence": ", ".join(key_english_materials()),
            "detail": "No Japanese characters found in key public submission materials." if not language_hits else "Review language hits: " + ", ".join(language_hits),
        },
        {
            "key": "open_source_license_present",
            "status": "pass" if content_rights.get("license", {}).get("spdx") == "Apache-2.0" else "needs_review",
            "evidence": "LICENSE, reports/latest_content_rights_audit.html",
            "detail": "Apache-2.0 license is present and included in the content rights audit.",
        },
        {
            "key": "third_party_media_not_bundled",
            "status": "pass" if content_rights.get("bundled_audio_video_media") == [] else "needs_review",
            "evidence": "reports/latest_content_rights_audit.html",
            "detail": "No bundled audio/video media files are present in the local package.",
        },
        {
            "key": "synthetic_data_boundary",
            "status": "pass" if "synthetic" in readme.lower() and "synthetic data only" in official_audit.lower() else "needs_review",
            "evidence": "README.md, submission/OFFICIAL_REQUIREMENTS_AUDIT.md",
            "detail": "The package describes demo data as synthetic and avoids private logs/customer data.",
        },
        {
            "key": "unique_project_narrative",
            "status": "pass" if "Agentic Incident Command Center" in devpost_draft and "hard middle" in devpost_draft else "needs_review",
            "evidence": "submission/DEVPOST_SUBMISSION_DRAFT.md",
            "detail": "The Devpost draft frames a distinct AI incident command and remediation-ledger story.",
        },
        {
            "key": "testing_access_gated_by_public_urls",
            "status": "pass" if url_validation.get("final_submit_ready") is False else "needs_review",
            "evidence": "reports/latest_submission_url_validation.html",
            "detail": "Final submission remains blocked until public repo and public video URLs are approved and validated.",
        },
    ]


def build_payload(root: Path) -> dict[str, Any]:
    evidence = automated_evidence(root)
    checks: list[Check] = []
    human_items = human_confirmation_items()
    failed_evidence = [item["key"] for item in evidence if item["status"] != "pass"]
    official_audit = read_text(root / "submission/OFFICIAL_REQUIREMENTS_AUDIT.md")
    add_check(checks, "official rules source linked", "https://splunk.devpost.com/rules" in official_audit, "submission/OFFICIAL_REQUIREMENTS_AUDIT.md")
    add_check(checks, "automated compliance evidence ready", not failed_evidence, ", ".join(failed_evidence) if failed_evidence else "all automated evidence ready")
    add_check(checks, "human confirmations enumerated", len(human_items) >= 5, ", ".join(item["key"] for item in human_items))
    add_check(checks, "external submit remains gated", "User approval required" in official_audit and "Not submitted" in official_audit, "user approval and not-submitted wording checked")
    add_check(checks, "boundary text", "does not determine legal eligibility" in BOUNDARY and "submit anything" in BOUNDARY, BOUNDARY)
    failed = [check for check in checks if not check.passed]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not failed else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "source_checked_at_jst": SOURCE_CHECKED_AT_JST,
        "source_urls": source_urls(),
        "automated_evidence": evidence,
        "human_confirmation_required_count": len(human_items),
        "human_confirmation_items": human_items,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "recommended_next_step": "Before Devpost final submission, the entrant should confirm each human-confirmation item and record approval in the launch runbook or post-action evidence log.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Eligibility And Compliance Audit",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Source checked at: {payload['source_checked_at_jst']}",
        "Human confirmation checklist: `submission/HUMAN_CONFIRMATION_CHECKLIST.md`",
        "",
        "## Official Sources",
        "",
    ]
    for source in payload["source_urls"]:
        lines.append(f"- [{source['name']}]({source['url']}) - {source['local_relevance']}")
    lines.extend(["", "## Automated Evidence", ""])
    for item in payload["automated_evidence"]:
        lines.append(f"- {item['key']}: {item['status']} - {item['detail']} Evidence: `{item['evidence']}`")
    lines.extend(["", "## Human Confirmation Required", ""])
    for item in payload["human_confirmation_items"]:
        lines.extend([
            f"### {item['key']}",
            "",
            f"Rule area: {item['rule_area']}",
            f"Confirm: {item['confirmation_needed']}",
            f"Why Codex cannot confirm: {item['why_codex_cannot_confirm']}",
            "",
        ])
    lines.extend(["## Checks", ""])
    for check in payload["checks"]:
        lines.append(f"- {check['name']}: {check['status']} ({check['detail']})")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_human_confirmation_checklist(payload: dict[str, Any]) -> str:
    lines = [
        "# Human Confirmation Checklist",
        "",
        "Status: pending human confirmation",
        f"Source checked at: {payload['source_checked_at_jst']}",
        "Source report: `reports/latest_eligibility_compliance_audit.html`",
        "",
        "Use this file before Devpost final submission. It records the facts Codex cannot verify from local files.",
        "Leave items unchecked until the entrant has personally confirmed them.",
        "",
        "## Confirmation Items",
        "",
    ]
    for item in payload["human_confirmation_items"]:
        lines.extend(
            [
                f"- [ ] `{item['key']}`",
                f"  - Rule area: {item['rule_area']}",
                f"  - Confirm: {item['confirmation_needed']}",
                f"  - Why Codex cannot confirm: {item['why_codex_cannot_confirm']}",
                "  - Record confirmation in `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` or the final Devpost review notes.",
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary",
            "",
            "This checklist is a local review aid only. It is not a legal determination and does not confirm eligibility by itself.",
            "It does not publish a repository, upload video, write approved URLs, configure Splunk or MCP, update Devpost, save a Devpost draft, or submit anything.",
            "",
            "## Final Submit Hold",
            "",
            "Devpost final submission stays blocked until every confirmation item above is checked by the entrant and the public repository and public demo video URLs are approved and verified.",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    source_rows = "\n".join(
        "<tr>"
        f"<td>{esc(source['name'])}</td>"
        f"<td><code>{esc(source['url'])}</code></td>"
        f"<td>{esc(source['local_relevance'])}</td>"
        "</tr>"
        for source in payload["source_urls"]
    )
    evidence_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['key'])}</td>"
        f"<td class=\"{'ready' if item['status'] == 'pass' else 'pending'}\">{esc(item['status'])}</td>"
        f"<td><code>{esc(item['evidence'])}</code></td>"
        f"<td>{esc(item['detail'])}</td>"
        "</tr>"
        for item in payload["automated_evidence"]
    )
    human_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['key'])}</td>"
        f"<td>{esc(item['rule_area'])}</td>"
        f"<td>{esc(item['confirmation_needed'])}</td>"
        f"<td>{esc(item['why_codex_cannot_confirm'])}</td>"
        "</tr>"
        for item in payload["human_confirmation_items"]
    )
    check_rows = "\n".join(
        "<tr>"
        f"<td>{esc(check['name'])}</td>"
        f"<td class=\"{'ready' if check['status'] == 'pass' else 'fail'}\">{esc(check['status'])}</td>"
        f"<td>{esc(check['detail'])}</td>"
        "</tr>"
        for check in payload["checks"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Eligibility And Compliance Audit</title>
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
    <h1>Eligibility And Compliance Audit</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Snapshot</h2>
      <table><tbody>
        <tr><th>Root type</th><td>{esc(payload['root_type'])}</td></tr>
        <tr><th>Source checked at</th><td>{esc(payload['source_checked_at_jst'])}</td></tr>
        <tr><th>Human confirmations</th><td>{esc(payload['human_confirmation_required_count'])}</td></tr>
        <tr><th>Human confirmation checklist</th><td><code>submission/HUMAN_CONFIRMATION_CHECKLIST.md</code></td></tr>
        <tr><th>Failed checks</th><td>{esc(payload['failed_count'])}</td></tr>
      </tbody></table>
      <p class="pending">{esc(payload['recommended_next_step'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Official Sources</h2>
      <table>
        <thead><tr><th>Source</th><th>URL</th><th>Local relevance</th></tr></thead>
        <tbody>{source_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Automated Evidence</h2>
      <table>
        <thead><tr><th>Item</th><th>Status</th><th>Evidence</th><th>Detail</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Human Confirmation Required</h2>
      <table>
        <thead><tr><th>Item</th><th>Rule area</th><th>Confirm</th><th>Why Codex cannot confirm</th></tr></thead>
        <tbody>{human_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
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
    submission = root / "submission"
    reports.mkdir(parents=True, exist_ok=True)
    submission.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_eligibility_compliance_audit.json", payload)
    (reports / "latest_eligibility_compliance_audit.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_eligibility_compliance_audit.html").write_text(render_html(payload), encoding="utf-8")
    (submission / "HUMAN_CONFIRMATION_CHECKLIST.md").write_text(render_human_confirmation_checklist(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "root_type": payload["root_type"],
        "failed_count": payload["failed_count"],
        "human_confirmation_required_count": payload["human_confirmation_required_count"],
        "html": "reports/latest_eligibility_compliance_audit.html",
        "markdown": "reports/latest_eligibility_compliance_audit.md",
        "json": "reports/latest_eligibility_compliance_audit.json",
        "human_confirmation_checklist": "submission/HUMAN_CONFIRMATION_CHECKLIST.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local eligibility and compliance audit for the submission packet.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
