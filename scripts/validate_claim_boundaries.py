from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PUBLIC_COPY_FILES = [
    "README.md",
    "submission/DEVPOST_SUBMISSION_DRAFT.md",
    "submission/DEMO_VIDEO_SCRIPT.md",
    "submission/DEVPOST_FIELD_MAP.md",
]

BOUNDARY_DOCS = [
    "submission/DEVPOST_FIELD_MAP.md",
    "submission/VIDEO_RECORDING_RUNBOOK.md",
    "submission/SUBMISSION_LAUNCH_RUNBOOK.md",
    "submission/SUBMISSION_REVIEW_QA.md",
]

OVERCLAIM_PHRASES = [
    "verified through Splunk MCP Server",
    "live Splunk MCP integration",
    "live Splunk MCP verification",
    "live Splunk verification",
    "MCP-assisted investigation over live Splunk search results",
    "production deployment",
    "real customer logs",
    "autonomous remediation",
    "automatically approved",
]

CONTEXT_QUALIFIERS = [
    "avoid",
    "before",
    "after",
    "approved",
    "configured",
    "designed",
    "do not claim",
    "full splunk environment",
    "if live",
    "intended",
    "local proof boundary",
    "local splunk enterprise",
    "not ",
    "only after",
    "pending",
    "recorded",
    "requires",
    "until",
    "when live",
]

REQUIRED_BOUNDARY_TEXT = {
    "submission/DEVPOST_FIELD_MAP.md": [
        "Do not claim yet",
        "designed for Splunk MCP Server",
        "local Splunk Enterprise Docker proof with synthetic data",
    ],
    "submission/VIDEO_RECORDING_RUNBOOK.md": [
        "Avoid saying",
        "designed for Splunk MCP Server",
        "verified through Splunk MCP Server",
    ],
    "submission/SUBMISSION_LAUNCH_RUNBOOK.md": [
        "Claim Wording",
        "Final Safety Gate",
        "ready_for_user_review",
    ],
    "submission/SUBMISSION_REVIEW_QA.md": [
        "Safe Copy",
        "Avoid these phrases",
        "Final Review Checklist",
    ],
}


@dataclass
class Finding:
    path: str
    line: int
    phrase: str
    text: str


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def line_is_qualified(line: str) -> bool:
    lower = line.lower()
    return any(qualifier in lower for qualifier in CONTEXT_QUALIFIERS)


def collect_overclaims(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel in PUBLIC_COPY_FILES:
        path = root / rel
        if not path.exists():
            findings.append(Finding(rel, 0, "missing-file", "missing file"))
            continue
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            lower = line.lower()
            for phrase in OVERCLAIM_PHRASES:
                if phrase.lower() in lower and not line_is_qualified(line):
                    findings.append(Finding(rel, index, phrase, line.strip()))
    return findings


def check_required_boundary_text(root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for rel, required_items in REQUIRED_BOUNDARY_TEXT.items():
        path = root / rel
        if not path.exists():
            checks.append({"path": rel, "status": "fail", "detail": "missing file"})
            continue
        text = path.read_text(encoding="utf-8")
        missing = [item for item in required_items if item not in text]
        checks.append({
            "path": rel,
            "status": "pass" if not missing else "fail",
            "detail": "all boundary text present" if not missing else "missing: " + ", ".join(missing),
        })
    return checks


def build_report(root: Path) -> dict[str, Any]:
    findings = collect_overclaims(root)
    boundary_checks = check_required_boundary_text(root)
    failed_boundary_checks = [check for check in boundary_checks if check["status"] != "pass"]
    status = "pass" if not findings and not failed_boundary_checks else "fail"
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "root": root.name,
        "public_copy_files": PUBLIC_COPY_FILES,
        "boundary_docs": BOUNDARY_DOCS,
        "overclaim_findings": [finding.__dict__ for finding in findings],
        "boundary_checks": boundary_checks,
        "summary": "claim boundaries clean" if status == "pass" else "claim boundary issues found",
    }


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def write_html(path: Path, report: dict[str, Any]) -> None:
    finding_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(item['path'])}</td>"
        f"<td>{item['line']}</td>"
        f"<td>{html.escape(item['phrase'])}</td>"
        f"<td>{html.escape(item['text'])}</td>"
        "</tr>"
        for item in report["overclaim_findings"]
    ) or '<tr><td colspan="4">No unqualified overclaim phrases found.</td></tr>'

    check_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(item['path'])}</td>"
        f"<td>{html.escape(item['status'])}</td>"
        f"<td>{html.escape(item['detail'])}</td>"
        "</tr>"
        for item in report["boundary_checks"]
    )

    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentOps Claim Boundary Validation</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; }}
    header {{ background: #17202a; color: #fff; padding: 28px 36px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 18px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ color: #5f6d7c; }}
    .pass {{ color: #127c76; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>AgentOps Claim Boundary Validation</h1>
    <p>Status: <span class="{html.escape(report['status'])}">{html.escape(report['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Scope</h2>
      <p>Checks public-facing submission copy for unqualified live Splunk or live MCP claims before external proof is approved.</p>
    </section>
    <section>
      <h2>Overclaim Findings</h2>
      <table>
        <thead><tr><th>File</th><th>Line</th><th>Phrase</th><th>Text</th></tr></thead>
        <tbody>{finding_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Boundary Text Checks</h2>
      <table>
        <thead><tr><th>File</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{check_rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public submission claim boundaries.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_report(root)
    write_json(root / "reports" / "latest_claim_boundary_validation.json", report)
    write_html(root / "reports" / "latest_claim_boundary_validation.html", report)
    print(json.dumps({"status": report["status"], "finding_count": len(report["overclaim_findings"])}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
