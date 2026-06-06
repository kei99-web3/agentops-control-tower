from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_devpost_submission_packet import SECTION_NAMES, markdown_section
from submission_urls import field_values_for


SOFT_LIMITS = {
    "tagline": 120,
    "Short Description": 500,
    "Inspiration": 5000,
    "What It Does": 5000,
    "How We Built It": 5000,
    "Splunk Usage": 5000,
    "What Makes It Different": 3000,
    "Judging Alignment": 3000,
    "Challenges": 3000,
    "Accomplishments": 3000,
    "New During Hackathon": 1500,
    "What Is Next": 3000,
}


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def is_pending_or_url(value: str) -> bool:
    return value.startswith("PENDING_USER_APPROVAL_") or bool(re.match(r"^https?://", value))


def build_payload(root: Path) -> dict[str, Any]:
    draft = read_text(root / "submission" / "DEVPOST_SUBMISSION_DRAFT.md")
    sections = {name: markdown_section(draft, name) for name in SECTION_NAMES}
    fields = field_values_for(root)
    char_counts = {
        "project_name": len(fields["project_name"]),
        "tagline": len(fields["tagline"]),
        **{name: len(body) for name, body in sections.items()},
    }

    checks: list[Check] = []
    add_check(checks, "project name present", bool(fields["project_name"].strip()), fields["project_name"])
    add_check(checks, "tagline present", bool(fields["tagline"].strip()), fields["tagline"])
    add_check(checks, "tagline soft limit", char_counts["tagline"] <= SOFT_LIMITS["tagline"], f"{char_counts['tagline']}/{SOFT_LIMITS['tagline']}")
    add_check(checks, "repository URL placeholder or URL", is_pending_or_url(fields["repository_url"]), fields["repository_url"])
    add_check(checks, "demo video URL placeholder or URL", is_pending_or_url(fields["demo_video_url"]), fields["demo_video_url"])

    for section in SECTION_NAMES:
        body = sections.get(section, "")
        add_check(checks, f"section present: {section}", bool(body.strip()), f"chars={len(body)}")
        if section in SOFT_LIMITS:
            add_check(checks, f"section soft limit: {section}", len(body) <= SOFT_LIMITS[section], f"{len(body)}/{SOFT_LIMITS[section]}")

    pending_urls = [
        name
        for name in ["repository_url", "demo_video_url"]
        if str(fields[name]).startswith("PENDING_USER_APPROVAL_")
    ]
    final_submit_ready = not pending_urls
    status = "ready_for_user_review" if all(check.passed for check in checks) else "needs_more_evidence"

    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "final_submit_ready": final_submit_ready,
        "pending_urls": pending_urls,
        "fields": fields,
        "sections": sections,
        "char_counts": char_counts,
        "checks": [check.__dict__ for check in checks],
        "copy_boundary": "Do not submit or replace pending URLs without explicit user approval.",
    }


def render_markdown(payload: dict[str, Any]) -> str:
    fields = payload["fields"]
    sections = payload["sections"]
    built_with = ", ".join(fields["built_with"])
    lines = [
        "# Devpost Final Copy Packet",
        "",
        f"Status: {payload['status']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        "",
        "## Core Fields",
        "",
        f"Project name: {fields['project_name']}",
        f"Tagline: {fields['tagline']}",
        f"Track: {fields['track']}",
        f"Bonus target: {fields['bonus_target']}",
        f"Built with: {built_with}",
        f"Repository URL: {fields['repository_url']}",
        f"Demo video URL: {fields['demo_video_url']}",
        "",
        "## Copy/Paste Sections",
        "",
    ]
    for name in SECTION_NAMES:
        lines.extend([f"### {name}", "", sections.get(name, "").strip(), ""])
    lines.extend([
        "## Final Gate",
        "",
        "Do not submit this packet until the public repository URL, public video URL, and final Devpost action are explicitly approved.",
        "",
    ])
    return "\n".join(lines)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_html(payload: dict[str, Any]) -> str:
    fields = payload["fields"]
    sections = payload["sections"]
    check_rows = "\n".join(
        "<tr>"
        f"<td>{esc(check['name'])}</td>"
        f"<td>{esc(check['status'])}</td>"
        f"<td>{esc(check['detail'])}</td>"
        "</tr>"
        for check in payload["checks"]
    )
    section_cards = "\n".join(
        f"<section><h2>{esc(name)}</h2><pre>{esc(sections.get(name, '').strip())}</pre></section>"
        for name in SECTION_NAMES
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Devpost Final Copy Packet</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.56; }}
    header {{ background: #17202a; color: #fff; padding: 28px 36px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 18px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ color: #5f6d7c; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #edf3f6; border-radius: 6px; padding: 12px; }}
    .pass {{ color: #127c76; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Devpost Final Copy Packet</h1>
    <p>Status: <span class="{esc('pass' if payload['status'] == 'ready_for_user_review' else 'fail')}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Core Fields</h2>
      <table>
        <tbody>
          <tr><th>Project name</th><td>{esc(fields['project_name'])}</td></tr>
          <tr><th>Tagline</th><td>{esc(fields['tagline'])}</td></tr>
          <tr><th>Track</th><td>{esc(fields['track'])}</td></tr>
          <tr><th>Bonus target</th><td>{esc(fields['bonus_target'])}</td></tr>
          <tr><th>Built with</th><td>{esc(', '.join(fields['built_with']))}</td></tr>
          <tr><th>Repository URL</th><td class="pending">{esc(fields['repository_url'])}</td></tr>
          <tr><th>Demo video URL</th><td class="pending">{esc(fields['demo_video_url'])}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{check_rows}</tbody>
      </table>
    </section>
    {section_cards}
    <section>
      <h2>Final Gate</h2>
      <p class="pending">Do not submit this packet until the public repository URL, public video URL, and final Devpost action are explicitly approved.</p>
    </section>
  </main>
</body>
</html>
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run(root: Path) -> dict[str, Any]:
    payload = build_payload(root)
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "latest_devpost_final_copy.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_devpost_final_copy.html").write_text(render_html(payload), encoding="utf-8")
    write_json(reports / "latest_devpost_final_copy.json", payload)
    return {
        "status": payload["status"],
        "final_submit_ready": payload["final_submit_ready"],
        "pending_urls": payload["pending_urls"],
        "markdown": "reports/latest_devpost_final_copy.md",
        "html": "reports/latest_devpost_final_copy.html",
        "json": "reports/latest_devpost_final_copy.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Devpost final copy packet with copy/paste checks.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
