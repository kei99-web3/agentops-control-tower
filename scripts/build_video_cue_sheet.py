from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This cue sheet is local recording guidance only. It does not record, upload, "
    "publish, write approved URLs, update Devpost, or submit anything."
)


SCREEN_FOCUS = {
    "Problem": "reports/latest_demo_tour.html - Scene 1 / Problem",
    "Solution": "reports/latest_demo_tour.html - Scene 2 / Incident Command Summary",
    "Synthetic Event Flow": "reports/latest_demo_tour.html - Scene 3 / Incident Review",
    "Dashboard": "reports/latest_control_tower.html - KPI strip, root-cause ranking, MCP Remediation Ledger",
    "Splunk/MCP Fit": "reports/latest_live_splunk_docker_proof.html, submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md, and submission/SPL_QUERIES.md",
    "Close": "reports/latest_demo_tour.html - final human-in-the-loop message",
}


GUARDRAILS = {
    "Problem": "Keep this conceptual. Do not show real private operations or accounts.",
    "Solution": "Say MCP Remediation Ledger as evidence-backed review, not autonomous approval bypass.",
    "Synthetic Event Flow": "Point out synthetic events only. Do not mention private workspace logs.",
    "Dashboard": "Show only dashboard/demo artifacts. Avoid terminals with local paths or tokens.",
    "Splunk/MCP Fit": "Say verified in local Splunk Enterprise Docker with synthetic data. Do not claim production Splunk Cloud deployment.",
    "Close": "Repeat that humans stay in the approval loop.",
}


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def parse_time(value: str) -> int:
    minutes, seconds = value.split(":")
    return int(minutes) * 60 + int(seconds)


def parse_script(script: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"^##\s+(\d+:\d{2})-(\d+:\d{2})\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(script))
    scenes: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        body_start = match.end()
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(script)
        label = match.group(3).strip()
        narration = " ".join(line.strip() for line in script[body_start:body_end].strip().splitlines() if line.strip())
        scenes.append({
            "start": match.group(1),
            "end": match.group(2),
            "start_seconds": parse_time(match.group(1)),
            "end_seconds": parse_time(match.group(2)),
            "duration_seconds": parse_time(match.group(2)) - parse_time(match.group(1)),
            "label": label,
            "screen_focus": SCREEN_FOCUS.get(label, "reports/latest_demo_tour.html"),
            "narration_cue": narration,
            "guardrail": GUARDRAILS.get(label, "Keep the recording screen-safe and claim-safe."),
        })
    return scenes


def evidence_items() -> list[str]:
    return [
        "reports/latest_demo_tour.html",
        "reports/latest_control_tower.html",
        "reports/latest_local_spl_query_results.html",
        "reports/latest_live_splunk_docker_proof.html",
        "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md",
        "reports/latest_video_readiness.html",
        "reports/latest_video_command_plan.html",
        "reports/latest_launch_decision_brief.html",
        "submission/DEMO_VIDEO_SCRIPT.md",
        "submission/VIDEO_RECORDING_RUNBOOK.md",
        "submission/SPL_QUERIES.md",
    ]


def build_payload(root: Path) -> dict[str, Any]:
    script_path = root / "submission/DEMO_VIDEO_SCRIPT.md"
    script = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
    scenes = parse_script(script)
    video = read_json(root / "reports/latest_video_readiness.json")
    command_plan = read_json(root / "reports/latest_video_command_plan.json")
    evidence = [{"path": item, "exists": exists(root, item)} for item in evidence_items()]
    missing = [item["path"] for item in evidence if not item["exists"]]
    max_end = max((scene["end_seconds"] for scene in scenes), default=0)
    timeline_ok = len(scenes) >= 6 and max_end <= 180
    ready = (
        not missing
        and timeline_ok
        and video.get("status") == "ready_for_recording_review"
        and exists(root, "reports/latest_video_command_plan.html")
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_recording_review" if ready else "needs_more_evidence",
        "scene_count": len(scenes),
        "duration_seconds": max_end,
        "video_readiness_status": video.get("status", "missing"),
        "video_command_plan_status": command_plan.get("status", "missing"),
        "final_public_video_ready": False,
        "missing_evidence": missing,
        "scenes": scenes,
        "evidence": evidence,
        "screen_safety_guardrails": [
            "Use synthetic data only.",
            "Close terminals that show private paths, tokens, account names, or unrelated files.",
            "Do not show .env, config files, API keys, OAuth tokens, private logs, customer systems, or real accounts.",
            "Keep the browser on demo tour, dashboard, local SPL proof, and public candidate files.",
            "Say official Splunk MCP Server verified only for the local Splunk Enterprise Docker proof with synthetic data.",
        ],
        "boundary": BOUNDARY,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Demo Video Cue Sheet",
        "",
        f"Status: {payload['status']}",
        f"Duration: {payload['duration_seconds']} seconds",
        f"Final public video ready: {str(payload['final_public_video_ready']).lower()}",
        "",
        "## Timeline",
        "",
    ]
    for scene in payload["scenes"]:
        lines.extend([
            f"### {scene['start']}-{scene['end']} {scene['label']}",
            "",
            f"Screen: `{scene['screen_focus']}`",
            "",
            f"Narration cue: {scene['narration_cue']}",
            "",
            f"Guardrail: {scene['guardrail']}",
            "",
        ])
    lines.extend(["## Screen Safety Guardrails", ""])
    for item in payload["screen_safety_guardrails"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    scene_rows = "\n".join(
        "<tr>"
        f"<td>{esc(scene['start'])}-{esc(scene['end'])}</td>"
        f"<td>{esc(scene['label'])}</td>"
        f"<td><code>{esc(scene['screen_focus'])}</code></td>"
        f"<td>{esc(scene['narration_cue'])}</td>"
        f"<td>{esc(scene['guardrail'])}</td>"
        "</tr>"
        for scene in payload["scenes"]
    )
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        "</tr>"
        for item in payload["evidence"]
    )
    guardrails = "\n".join(f"<li>{esc(item)}</li>" for item in payload["screen_safety_guardrails"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Demo Video Cue Sheet</title>
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
    <h1>Demo Video Cue Sheet</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_recording_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Recording Boundary</h2>
      <p class="pending">{esc(payload['boundary'])}</p>
      <p>Duration target: {esc(payload['duration_seconds'])} seconds. Final public video ready: {esc(payload['final_public_video_ready'])}.</p>
    </section>
    <section>
      <h2>Timeline</h2>
      <table>
        <thead><tr><th>Time</th><th>Beat</th><th>Screen</th><th>Narration Cue</th><th>Guardrail</th></tr></thead>
        <tbody>{scene_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Screen Safety Guardrails</h2>
      <ul>{guardrails}</ul>
    </section>
    <section>
      <h2>Evidence</h2>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
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
    write_json(reports / "latest_video_cue_sheet.json", payload)
    (reports / "latest_video_cue_sheet.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_video_cue_sheet.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "duration_seconds": payload["duration_seconds"],
        "missing_evidence": payload["missing_evidence"],
        "html": "reports/latest_video_cue_sheet.html",
        "markdown": "reports/latest_video_cue_sheet.md",
        "json": "reports/latest_video_cue_sheet.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a recording cue sheet for the Agentic Incident Command Center demo video.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_recording_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
