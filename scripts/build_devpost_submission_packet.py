from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

from submission_urls import approved_url_source, default_field_values, field_values_for

FIELD_VALUES = default_field_values()


SECTION_NAMES = [
    "Short Description",
    "Inspiration",
    "What It Does",
    "How We Built It",
    "Splunk Usage",
    "What Makes It Different",
    "Judging Alignment",
    "Challenges",
    "Accomplishments",
    "New During Hackathon",
    "What Is Next",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def markdown_section(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*\n(?P<body>.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown)
    return match.group("body").strip() if match else ""


def markdown_to_html(text: str) -> str:
    blocks: list[str] = []
    lines = text.splitlines()
    bullet_items: list[str] = []
    code_lines: list[str] = []
    in_code = False
    for line in lines:
        if line.startswith("```"):
            if in_code:
                blocks.append("<pre>" + esc("\n".join(code_lines)) + "</pre>")
                code_lines = []
                in_code = False
            else:
                flush_bullets(blocks, bullet_items)
                bullet_items.clear()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if line.startswith("- "):
            bullet_items.append(line[2:].strip())
            continue
        flush_bullets(blocks, bullet_items)
        bullet_items.clear()
        if line.strip():
            blocks.append(f"<p>{esc(line.strip())}</p>")
    if in_code:
        blocks.append("<pre>" + esc("\n".join(code_lines)) + "</pre>")
    flush_bullets(blocks, bullet_items)
    return "\n".join(blocks)


def flush_bullets(blocks: list[str], bullet_items: list[str]) -> None:
    if bullet_items:
        items = "".join(f"<li>{esc(item)}</li>" for item in bullet_items)
        blocks.append(f"<ul>{items}</ul>")


def build_payload(root: Path) -> dict[str, Any]:
    draft = read_text(root / "submission" / "DEVPOST_SUBMISSION_DRAFT.md")
    field_map = read_text(root / "submission" / "DEVPOST_FIELD_MAP.md")
    sections = {name: markdown_section(draft, name) for name in SECTION_NAMES}
    fields = field_values_for(root)
    return {
        "status": "local_draft_not_submitted",
        "fields": fields,
        "sections": sections,
        "field_map_summary": {
            "has_pending_repo_url": str(fields["repository_url"]).startswith("PENDING_"),
            "has_pending_video_url": str(fields["demo_video_url"]).startswith("PENDING_"),
            "source": approved_url_source(root),
        },
        "required_local_evidence": [
            "README.md",
            "LICENSE",
            "architecture_diagram.md",
            "reports/latest_demo_tour.html",
            "reports/latest_control_tower.html",
            "reports/latest_local_spl_query_results.html",
            "submission/DEVPOST_SUBMISSION_DRAFT.md",
            "submission/FINAL_SUBMISSION_CHECKLIST.md",
            "submission/OFFICIAL_REQUIREMENTS_AUDIT.md",
        ],
        "claim_boundaries": markdown_section(field_map, "Claim Boundaries"),
    }


def render_html(payload: dict[str, Any]) -> str:
    fields = payload["fields"]
    sections = payload["sections"]
    built_with = ", ".join(fields["built_with"])
    evidence_items = "".join(f"<li><code>{esc(item)}</code></li>" for item in payload["required_local_evidence"])
    section_cards = "\n".join(
        f"<section><h2>{esc(name)}</h2>{markdown_to_html(body) if body else '<p>Missing local draft section.</p>'}</section>"
        for name, body in sections.items()
        if body
    )
    boundaries = markdown_to_html(payload.get("claim_boundaries", ""))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Devpost Submission Packet</title>
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
    code, pre {{ background: #edf3f6; border-radius: 6px; }}
    code {{ padding: 2px 5px; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; padding: 10px; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    @media (max-width: 760px) {{
      header {{ padding: 22px 18px; }}
      main {{ padding: 14px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Devpost Submission Packet</h1>
    <p>Local copy/paste packet for Agentic Incident Command Center. It is not submitted and still requires public repository, public video, and final Devpost approval.</p>
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
          <tr><th>Built with</th><td>{esc(built_with)}</td></tr>
          <tr><th>Repository URL</th><td class="pending">{esc(fields['repository_url'])}</td></tr>
          <tr><th>Demo video URL</th><td class="pending">{esc(fields['demo_video_url'])}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Local Evidence</h2>
      <ul>{evidence_items}</ul>
    </section>
    <section>
      <h2>Claim Boundaries</h2>
      {boundaries}
    </section>
    {section_cards}
    <section>
      <h2>Final Gates</h2>
      <p class="pending">Replace the pending repository and video URLs only after explicit user approval. Then re-run validation and get final submit approval.</p>
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
    html_path = root / "reports" / "latest_devpost_submission_packet.html"
    json_path = root / "reports" / "latest_devpost_submission_packet.json"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(payload), encoding="utf-8")
    write_json(json_path, payload)
    return {
        "status": payload["status"],
        "html": "reports/latest_devpost_submission_packet.html",
        "json": "reports/latest_devpost_submission_packet.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local Devpost copy/paste submission packet.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    print(json.dumps(run(Path(args.root).resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
