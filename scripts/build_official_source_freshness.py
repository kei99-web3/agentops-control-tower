from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This source freshness report is local review evidence only. It records the latest manual "
    "official-source check used by the packet. It does not log in to Devpost, save a draft, "
    "publish a repository, upload a video, write approved URLs, update Devpost, or submit anything."
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


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def expected_sources() -> list[dict[str, str]]:
    return [
        {
            "name": "Devpost overview",
            "url": "https://splunk.devpost.com/",
            "local_relevance": "Deadline, challenge scope, tracks, requirements, prizes, judges, and judging criteria.",
        },
        {
            "name": "Devpost official rules",
            "url": "https://splunk.devpost.com/rules",
            "local_relevance": "Registration/submission periods, modification rules, eligibility, and staged judging process.",
        },
        {
            "name": "Devpost challenge update",
            "url": "https://splunk.devpost.com/updates/43765-the-challenge-is-live-and-so-are-the-prizes",
            "local_relevance": "Challenge launch and prize context.",
        },
    ]


def expected_requirements() -> list[dict[str, Any]]:
    return [
        {
            "key": "deadline",
            "official_value": "Jun 15, 2026 @ 9:00am PDT / 2026-06-16 01:00 JST",
            "local_evidence": ["submission/OFFICIAL_REQUIREMENTS_AUDIT.md"],
            "required_terms": ["2026-06-15 09:00 PDT", "2026-06-16 01:00 JST"],
        },
        {
            "key": "track",
            "official_value": "Observability, Security, or Platform & Developer Experience",
            "local_evidence": ["submission/DEVPOST_SUBMISSION_DRAFT.md", "submission/OFFICIAL_REQUIREMENTS_AUDIT.md"],
            "required_terms": ["Observability"],
        },
        {
            "key": "demo_video",
            "official_value": "Demo video under 3 minutes showing the project, AI usage, problem, and value.",
            "local_evidence": ["reports/latest_video_readiness.html", "submission/OFFICIAL_REQUIREMENTS_AUDIT.md"],
            "required_terms": ["Demo video under 3 minutes", "publicly upload"],
        },
        {
            "key": "public_repo",
            "official_value": "Public open-source repository with license, code, assets, setup/run instructions, dependencies/configs/datasets.",
            "local_evidence": ["reports/latest_public_repo_publish_brief.html", "submission/OFFICIAL_REQUIREMENTS_AUDIT.md"],
            "required_terms": ["Public open-source code repository", "Open-source license"],
        },
        {
            "key": "architecture_diagram",
            "official_value": "Architecture diagram in the repo root showing Splunk interaction, AI/agent integration, and data flow.",
            "local_evidence": ["architecture_diagram.md", "submission/OFFICIAL_REQUIREMENTS_AUDIT.md"],
            "required_terms": ["Root architecture diagram", "Splunk interaction"],
        },
        {
            "key": "judging",
            "official_value": "Technological Implementation, Design, Potential Impact, and Quality of the Idea.",
            "local_evidence": ["reports/latest_judge_scorecard.html", "submission/JUDGING_ALIGNMENT.md"],
            "required_terms": ["Technological Implementation", "Design", "Potential Impact", "Quality of the Idea"],
        },
        {
            "key": "bonus",
            "official_value": "Best Use of Splunk MCP Server is a bonus prize category.",
            "local_evidence": ["reports/latest_splunk_mcp_proof_brief.html", "reports/latest_splunk_mcp_prompt_pack.html", "reports/latest_splunk_mcp_proof_capture_manifest.html", "submission/OFFICIAL_REQUIREMENTS_AUDIT.md"],
            "required_terms": ["Best Use of Splunk MCP Server", "Splunk MCP Server bonus"],
        },
        {
            "key": "eligibility_compliance",
            "official_value": "Eligibility, team representation, ownership/IP, language, testing access, and conflict rules require entrant confirmation and local evidence.",
            "local_evidence": ["reports/latest_eligibility_compliance_audit.html", "submission/OFFICIAL_REQUIREMENTS_AUDIT.md"],
            "required_terms": ["Eligibility and compliance", "Human confirmation"],
        },
    ]


def evidence_exists(root: Path, paths: list[str]) -> bool:
    return all((root / path).exists() for path in paths)


def requirement_to_dict(root: Path, item: dict[str, Any]) -> dict[str, Any]:
    texts = "\n".join(read_text(root / path) for path in item["local_evidence"])
    missing_terms = [term for term in item["required_terms"] if term not in texts]
    missing_evidence = [path for path in item["local_evidence"] if not (root / path).exists()]
    return {
        "key": item["key"],
        "official_value": item["official_value"],
        "local_evidence": [{"path": path, "exists": (root / path).exists()} for path in item["local_evidence"]],
        "required_terms": item["required_terms"],
        "missing_terms": missing_terms,
        "missing_evidence": missing_evidence,
        "ready": not missing_terms and not missing_evidence,
    }


def build_payload(root: Path) -> dict[str, Any]:
    requirements = [requirement_to_dict(root, item) for item in expected_requirements()]
    checks: list[Check] = []
    audit_text = read_text(root / "submission/OFFICIAL_REQUIREMENTS_AUDIT.md")
    review_files = [
        "submission/OFFICIAL_REQUIREMENTS_AUDIT.md",
        "submission/JUDGING_ALIGNMENT.md",
        "reports/latest_judge_scorecard.html",
        "reports/latest_launch_decision_brief.html",
        "reports/latest_release_integrity_manifest.html",
    ]
    add_check(checks, "official audit file present", bool(audit_text), "submission/OFFICIAL_REQUIREMENTS_AUDIT.md")
    add_check(checks, "official source URLs present", all(source["url"] in audit_text for source in expected_sources()), "overview/rules/update URLs")
    add_check(checks, "official source freshness date present", SOURCE_CHECKED_AT_JST in audit_text, SOURCE_CHECKED_AT_JST)
    add_check(checks, "review evidence files present", evidence_exists(root, review_files), ", ".join(review_files))
    missing_requirement_keys = [item["key"] for item in requirements if not item["ready"]]
    add_check(checks, "official requirement terms mapped", not missing_requirement_keys, ", ".join(missing_requirement_keys) if missing_requirement_keys else "all mapped")
    add_check(checks, "external gates remain explicit", "User approval required" in audit_text and "Not submitted" in audit_text, "user approval and not-submitted wording checked")
    add_check(checks, "boundary text", "does not log in to Devpost" in BOUNDARY and "submit anything" in BOUNDARY, BOUNDARY)
    failed = [check for check in checks if not check.passed]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not failed else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "source_checked_at_jst": SOURCE_CHECKED_AT_JST,
        "source_urls": expected_sources(),
        "requirements": requirements,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "recommended_next_step": "Before final approval, reopen the Devpost overview and official rules pages and confirm the same deadline, required artifacts, and judging criteria still apply.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Official Source Freshness",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Source checked at: {payload['source_checked_at_jst']}",
        "",
        "## Official Sources",
        "",
    ]
    for source in payload["source_urls"]:
        lines.append(f"- [{source['name']}]({source['url']}) - {source['local_relevance']}")
    lines.extend(["", "## Requirement Snapshot", ""])
    for item in payload["requirements"]:
        lines.extend([
            f"### {item['key']}",
            "",
            f"Official value: {item['official_value']}",
            f"Ready: {str(item['ready']).lower()}",
            "",
            "Local evidence:",
        ])
        for evidence in item["local_evidence"]:
            lines.append(f"- `{evidence['path']}` ({'present' if evidence['exists'] else 'missing'})")
        if item["missing_terms"]:
            lines.append("Missing terms: " + ", ".join(item["missing_terms"]))
        lines.append("")
    lines.extend(["## Checks", ""])
    for check in payload["checks"]:
        lines.append(f"- {check['name']}: {check['status']} ({check['detail']})")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
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
    requirement_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['key'])}</td>"
        f"<td>{esc(item['official_value'])}</td>"
        f"<td class=\"{'ready' if item['ready'] else 'fail'}\">{esc('ready' if item['ready'] else 'missing')}</td>"
        f"<td>{esc(', '.join(path['path'] for path in item['local_evidence']))}</td>"
        f"<td>{esc(', '.join(item['missing_terms']) if item['missing_terms'] else 'none')}</td>"
        "</tr>"
        for item in payload["requirements"]
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
  <title>Official Source Freshness</title>
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
    <h1>Official Source Freshness</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Snapshot</h2>
      <p>Official sources last checked: <strong>{esc(payload['source_checked_at_jst'])}</strong></p>
      <p class="pending">{esc(payload['recommended_next_step'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Official Sources</h2>
      <table>
        <thead><tr><th>Source</th><th>URL</th><th>Local Relevance</th></tr></thead>
        <tbody>{source_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Requirement Snapshot</h2>
      <table>
        <thead><tr><th>Key</th><th>Official Value</th><th>Status</th><th>Local Evidence</th><th>Missing Terms</th></tr></thead>
        <tbody>{requirement_rows}</tbody>
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
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_official_source_freshness.json", payload)
    (reports / "latest_official_source_freshness.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_official_source_freshness.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "root_type": payload["root_type"],
        "failed_count": payload["failed_count"],
        "html": "reports/latest_official_source_freshness.html",
        "markdown": "reports/latest_official_source_freshness.md",
        "json": "reports/latest_official_source_freshness.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local official-source freshness report.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
