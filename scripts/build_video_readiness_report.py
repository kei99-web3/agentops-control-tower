from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MAX_DURATION_SECONDS = 180
VIDEO_SCREEN_SAFETY_CHECKLIST = "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md"


SCREEN_SAFETY_ITEMS = [
    "Use synthetic data only.",
    "Close terminals that show private paths, tokens, account names, or unrelated files.",
    "Do not show `.env`, config files, API keys, OAuth tokens, or private logs.",
    "Do not show real customer, cloud, incident, identity, ticketing, or Splunk account screens.",
    "Keep the browser on the dashboard, SPL query examples, and public candidate files.",
]


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_time(value: str) -> int:
    minutes, seconds = value.split(":")
    return int(minutes) * 60 + int(seconds)


def parse_timeline(script: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"^##\s+(\d+:\d{2})-(\d+:\d{2})\s+(.+)$", re.MULTILINE)
    scenes: list[dict[str, Any]] = []
    for match in pattern.finditer(script):
        start = parse_time(match.group(1))
        end = parse_time(match.group(2))
        scenes.append({
            "start": match.group(1),
            "end": match.group(2),
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": end - start,
            "label": match.group(3).strip(),
        })
    return scenes


def check_timeline(script: str, checks: list[Check]) -> list[dict[str, Any]]:
    scenes = parse_timeline(script)
    add_check(checks, "video timeline ranges", len(scenes) >= 5, f"{len(scenes)} ranges parsed")
    if not scenes:
        return scenes

    max_end = max(scene["end_seconds"] for scene in scenes)
    add_check(checks, "under 3 minute target", max_end <= MAX_DURATION_SECONDS, f"end={max_end}s target<={MAX_DURATION_SECONDS}s")

    continuity_ok = scenes[0]["start_seconds"] == 0
    for previous, current in zip(scenes, scenes[1:]):
        if previous["end_seconds"] != current["start_seconds"]:
            continuity_ok = False
            break
    add_check(checks, "continuous recording timeline", continuity_ok, "no gaps or overlaps" if continuity_ok else "timeline has a gap or overlap")

    labels = {scene["label"].lower() for scene in scenes}
    required = {
        "problem",
        "solution",
        "synthetic event flow",
        "dashboard",
        "splunk/mcp fit",
        "close",
    }
    missing = [item for item in sorted(required) if item not in labels]
    add_check(checks, "required video beats", not missing, "missing: " + ", ".join(missing) if missing else "all required beats present")
    return scenes


def check_screen_safety(runbook: str, checks: list[Check]) -> None:
    required = SCREEN_SAFETY_ITEMS
    missing = [item for item in required if item not in runbook]
    add_check(checks, "screen safety checklist", not missing, "missing: " + "; ".join(missing) if missing else "all screen safety items present")


def check_claim_boundaries(script: str, runbook: str, checks: list[Check]) -> None:
    lower_script = script.lower()
    forbidden = [
        "verified through splunk mcp server",
        "live splunk mcp integration is complete",
        "already connected to splunk mcp",
        "production splunk deployment",
    ]
    hits = [item for item in forbidden if item in lower_script]
    add_check(checks, "video claim boundary", not hits, "unsafe live-claim phrases: " + ", ".join(hits) if hits else "no unsafe live-claim phrases in script")

    required_guidance = [
        "designed for Splunk MCP Server",
        "verified through Splunk MCP Server",
        "only for the local Splunk Enterprise Docker proof with synthetic data",
    ]
    missing = [item for item in required_guidance if item not in runbook]
    add_check(checks, "voiceover claim guidance", not missing, "missing: " + "; ".join(missing) if missing else "safe wording guidance present")


def check_artifacts(root: Path, checks: list[Check]) -> None:
    demo = root / "reports/latest_demo_tour.html"
    if not demo.exists():
        add_check(checks, "demo tour artifact", False, "missing reports/latest_demo_tour.html")
    else:
        text = html.unescape(read_text(demo))
        required = [
            "Agentic Incident Command Center Demo Tour",
            "Scene 1 / Problem",
            "Scene 2 / Incident Command Summary",
            "Scene 5 / Local SPL Proof",
            "Scene 6 / Splunk MCP Boundary",
            "Still pending user approval",
        ]
        missing = [item for item in required if item not in text]
        add_check(checks, "demo tour artifact", not missing, "missing: " + ", ".join(missing) if missing else "safe demo tour sections present")

    png = root / "assets/dashboard_preview.png"
    if not png.exists():
        add_check(checks, "dashboard preview image", False, "missing assets/dashboard_preview.png")
        return
    data = png.read_bytes()
    ok = len(data) > 1000 and data[:8] == b"\x89PNG\r\n\x1a\n"
    add_check(checks, "dashboard preview image", ok, f"bytes={len(data)}")


def build_report(root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    script_path = root / "submission/DEMO_VIDEO_SCRIPT.md"
    runbook_path = root / "submission/VIDEO_RECORDING_RUNBOOK.md"

    if not script_path.exists():
        add_check(checks, "demo video script exists", False, "missing submission/DEMO_VIDEO_SCRIPT.md")
        script = ""
    else:
        script = read_text(script_path)
        add_check(checks, "demo video script exists", True, "submission/DEMO_VIDEO_SCRIPT.md")

    if not runbook_path.exists():
        add_check(checks, "video recording runbook exists", False, "missing submission/VIDEO_RECORDING_RUNBOOK.md")
        runbook = ""
    else:
        runbook = read_text(runbook_path)
        add_check(checks, "video recording runbook exists", True, "submission/VIDEO_RECORDING_RUNBOOK.md")

    scenes = check_timeline(script, checks) if script else []
    if runbook:
        check_screen_safety(runbook, checks)
        check_claim_boundaries(script, runbook, checks)
    check_artifacts(root, checks)

    failed = [check for check in checks if not check.passed]
    max_end = max((scene["end_seconds"] for scene in scenes), default=0)
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_recording_review" if not failed else "needs_more_evidence",
        "final_public_video_ready": False,
        "duration_seconds": max_end,
        "scene_count": len(scenes),
        "scenes": scenes,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "external_gates_pending": [
            "user review of video script",
            "screen safety checklist completion",
            "screen recording capture",
            "public video upload approval",
            "public video URL insertion",
        ],
        "screen_safety_checklist": VIDEO_SCREEN_SAFETY_CHECKLIST,
        "publication_boundary": "This report prepares local recording review only. It does not record, upload, publish, or submit a video.",
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def render_html(report: dict[str, Any]) -> str:
    checks = "\n".join(
        "<tr>"
        f"<td>{html.escape(check['name'])}</td>"
        f"<td>{html.escape(check['status'])}</td>"
        f"<td>{html.escape(check['detail'])}</td>"
        "</tr>"
        for check in report["checks"]
    )
    scenes = "\n".join(
        "<tr>"
        f"<td>{html.escape(scene['start'])}-{html.escape(scene['end'])}</td>"
        f"<td>{html.escape(scene['label'])}</td>"
        f"<td>{html.escape(str(scene['duration_seconds']))}s</td>"
        "</tr>"
        for scene in report["scenes"]
    )
    gates = "\n".join(f"<li>{html.escape(item)}</li>" for item in report["external_gates_pending"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Video Readiness Report</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; }}
    .pass, .ready {{ color: #127c76; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
  </style>
</head>
<body>
  <header>
    <h1>Video Readiness Report</h1>
    <p>Status: <span class="ready">{html.escape(report['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Timing</h2>
      <p>Target: under 3 minutes. Current scripted end: <strong>{html.escape(str(report['duration_seconds']))}s</strong>.</p>
      <p>Screen safety checklist: <code>{html.escape(report['screen_safety_checklist'])}</code></p>
      <table>
        <thead><tr><th>Time</th><th>Beat</th><th>Duration</th></tr></thead>
        <tbody>{scenes}</tbody>
      </table>
    </section>
    <section>
      <h2>Screen Safety And Claim Boundary</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{checks}</tbody>
      </table>
    </section>
    <section>
      <h2>External Gates</h2>
      <ul>{gates}</ul>
      <p class="pending">{html.escape(report['publication_boundary'])}</p>
    </section>
  </main>
</body>
</html>
"""


def render_screen_safety_checklist(report: dict[str, Any]) -> str:
    lines = [
        "# Video Screen Safety Checklist",
        "",
        "Status: pending screen safety review",
        "Source report: `reports/latest_video_readiness.html`",
        "Source runbook: `submission/VIDEO_RECORDING_RUNBOOK.md`",
        "",
        "Use this file before screen recording and again before public upload approval.",
        "Leave items unchecked until the final recording screen has been reviewed end to end.",
        "",
        "## Screen Review Items",
        "",
    ]
    for item in SCREEN_SAFETY_ITEMS:
        lines.append(f"- [ ] {item}")
    lines.extend(
        [
            "- [ ] The recording shows only the demo tour, dashboard, SPL examples, public candidate files, or the local Splunk Enterprise Docker official MCP proof screens.",
            "- [ ] The voiceover uses `designed for Splunk MCP Server` for architecture and limits `verified through Splunk MCP Server` to the local synthetic-data proof.",
            "- [ ] The final video duration is 180 seconds or less.",
            "",
            "## Current Readiness",
            "",
            f"- Readiness status: `{report['status']}`",
            f"- Scripted duration: `{report['duration_seconds']}s`",
            f"- Final public video ready: `{str(report['final_public_video_ready']).lower()}`",
            "",
            "## Boundary",
            "",
            "This checklist is local review evidence only. It does not record, upload, publish, write approved URLs, update Devpost, or submit anything.",
            "",
            "## Final Upload Hold",
            "",
            "Public video upload stays blocked until the user explicitly approves upload and this checklist has been completed against the final recording.",
            "",
        ]
    )
    return "\n".join(lines)


def run(root: Path) -> dict[str, Any]:
    report = build_report(root)
    write_json(root / "reports/latest_video_readiness.json", report)
    (root / "reports/latest_video_readiness.html").write_text(render_html(report), encoding="utf-8")
    checklist_path = root / VIDEO_SCREEN_SAFETY_CHECKLIST
    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    checklist_path.write_text(render_screen_safety_checklist(report), encoding="utf-8")
    return {
        "status": report["status"],
        "failed_count": report["failed_count"],
        "duration_seconds": report["duration_seconds"],
        "html": "reports/latest_video_readiness.html",
        "json": "reports/latest_video_readiness.json",
        "screen_safety_checklist": VIDEO_SCREEN_SAFETY_CHECKLIST,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local video readiness report before recording or upload.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_recording_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
