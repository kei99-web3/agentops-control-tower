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
BOUNDARY = (
    "This video dry run is local recording rehearsal only. It checks the prepared demo "
    "script, cue sheet, evidence files, screen-safety guardrails, and text scans without "
    "recording video, uploading video, publishing files, writing approved URLs, updating "
    "Devpost, or submitting anything."
)

EVIDENCE_ITEMS = [
    "reports/latest_demo_tour.html",
    "reports/latest_control_tower.html",
    "reports/latest_local_spl_query_results.html",
    "reports/latest_video_readiness.html",
    "reports/latest_video_command_plan.html",
    "reports/latest_video_cue_sheet.html",
    "reports/latest_content_rights_audit.html",
    "submission/DEMO_VIDEO_SCRIPT.md",
    "submission/VIDEO_RECORDING_RUNBOOK.md",
    "submission/SPL_QUERIES.md",
]

SCREEN_SCAN_FILES = [
    "reports/latest_demo_tour.html",
    "reports/latest_control_tower.html",
    "reports/latest_local_spl_query_results.html",
    "reports/latest_video_cue_sheet.md",
    "submission/DEMO_VIDEO_SCRIPT.md",
    "submission/VIDEO_RECORDING_RUNBOOK.md",
    "submission/SPL_QUERIES.md",
]

REQUIRED_BEATS = {
    "problem",
    "solution",
    "synthetic event flow",
    "dashboard",
    "splunk/mcp fit",
    "close",
}

SCREEN_SAFETY_TERMS = [
    "synthetic data only",
    "private paths",
    ".env",
    "api keys",
    "oauth tokens",
    "real accounts",
    "splunk mcp server",
    "local splunk enterprise docker",
    "production splunk cloud",
]

FORBIDDEN_NARRATION_PHRASES = [
    "verified through splunk mcp server",
    "live splunk mcp integration is complete",
    "already connected to splunk mcp",
    "production splunk deployment",
]

TEXT_SUFFIXES = {".conf", ".csv", ".html", ".json", ".md", ".py", ".txt", ".xml"}

INTERNAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"C:\\" + "Users",
        "PC" + "_User",
        r"Desktop[\\/]" + "AI" + "_" + "Workspace",
        "AI" + "_" + "Workspace",
        r"\." + "com" + "pany",
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

ABSOLUTE_PATH_PATTERN = re.compile(r"[A-Za-z]:[\\/][^\n\r\"']+")


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=sanitize(detail)))


def sanitize(value: str) -> str:
    return ABSOLUTE_PATH_PATTERN.sub("<local-path>", value)


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def parse_seconds(value: Any) -> int:
    if isinstance(value, int):
        return value
    text = str(value)
    if ":" not in text:
        return int(text)
    minutes, seconds = text.split(":", 1)
    return int(minutes) * 60 + int(seconds)


def normalized_scenes(cue: dict[str, Any]) -> list[dict[str, Any]]:
    scenes: list[dict[str, Any]] = []
    for item in cue.get("scenes", []):
        if not isinstance(item, dict):
            continue
        start_seconds = parse_seconds(item.get("start_seconds", item.get("start", 0)))
        end_seconds = parse_seconds(item.get("end_seconds", item.get("end", start_seconds)))
        scenes.append({
            "start": str(item.get("start", "")),
            "end": str(item.get("end", "")),
            "start_seconds": start_seconds,
            "end_seconds": end_seconds,
            "duration_seconds": end_seconds - start_seconds,
            "label": str(item.get("label", "")),
            "screen_focus": str(item.get("screen_focus", "")),
            "narration_cue": str(item.get("narration_cue", "")),
            "guardrail": str(item.get("guardrail", "")),
        })
    return scenes


def check_evidence(root: Path, checks: list[Check]) -> list[dict[str, Any]]:
    evidence = [{"path": item, "exists": exists(root, item)} for item in EVIDENCE_ITEMS]
    missing = [item["path"] for item in evidence if not item["exists"]]
    add_check(checks, "recording evidence files", not missing, "missing: " + ", ".join(missing) if missing else "all required evidence present")
    return evidence


def check_video_state(root: Path, checks: list[Check]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    readiness = read_json(root / "reports/latest_video_readiness.json")
    cue = read_json(root / "reports/latest_video_cue_sheet.json")
    command = read_json(root / "reports/latest_video_command_plan.json")
    content = read_json(root / "reports/latest_content_rights_audit.json")

    add_check(checks, "video readiness status", readiness.get("status") == "ready_for_recording_review", str(readiness.get("status", "missing")))
    add_check(checks, "video readiness failed count", int(readiness.get("failed_count", 1)) == 0, str(readiness.get("failed_count", "missing")))
    add_check(checks, "video readiness duration", int(readiness.get("duration_seconds", 999)) <= MAX_DURATION_SECONDS, str(readiness.get("duration_seconds", "missing")))
    add_check(checks, "video readiness final gate", readiness.get("final_public_video_ready") is False, str(readiness.get("final_public_video_ready", "missing")))

    add_check(checks, "video cue status", cue.get("status") == "ready_for_recording_review", str(cue.get("status", "missing")))
    add_check(checks, "video cue missing evidence", cue.get("missing_evidence") == [], str(cue.get("missing_evidence", "missing")))
    add_check(checks, "video cue duration", int(cue.get("duration_seconds", 999)) <= MAX_DURATION_SECONDS, str(cue.get("duration_seconds", "missing")))
    add_check(checks, "video cue final gate", cue.get("final_public_video_ready") is False, str(cue.get("final_public_video_ready", "missing")))

    add_check(
        checks,
        "video command plan artifact",
        exists(root, "reports/latest_video_command_plan.html"),
        str(command.get("status", "missing")),
    )
    add_check(checks, "content rights status", content.get("status") == "ready_for_user_review", str(content.get("status", "missing")))
    return readiness, cue, command, content


def check_timeline(scenes: list[dict[str, Any]], checks: list[Check]) -> None:
    add_check(checks, "video dry run scene count", len(scenes) >= 6, str(len(scenes)))
    if not scenes:
        add_check(checks, "video dry run timeline continuity", False, "no scenes")
        add_check(checks, "video dry run required beats", False, "no scenes")
        return

    continuity_ok = scenes[0]["start_seconds"] == 0
    positive_durations = True
    for previous, current in zip(scenes, scenes[1:]):
        if previous["end_seconds"] != current["start_seconds"]:
            continuity_ok = False
        if previous["duration_seconds"] <= 0:
            positive_durations = False
    if scenes[-1]["duration_seconds"] <= 0:
        positive_durations = False

    max_end = max(scene["end_seconds"] for scene in scenes)
    labels = {scene["label"].lower() for scene in scenes}
    missing_beats = sorted(REQUIRED_BEATS - labels)
    missing_fields = [
        scene["label"]
        for scene in scenes
        if not scene["screen_focus"] or not scene["narration_cue"] or not scene["guardrail"]
    ]
    add_check(checks, "video dry run duration", max_end <= MAX_DURATION_SECONDS, f"end={max_end}s")
    add_check(checks, "video dry run positive scene durations", positive_durations, "all scenes positive" if positive_durations else "one or more scenes have non-positive duration")
    add_check(checks, "video dry run timeline continuity", continuity_ok, "continuous from 0:00" if continuity_ok else "timeline has a gap or overlap")
    add_check(checks, "video dry run required beats", not missing_beats, "missing: " + ", ".join(missing_beats) if missing_beats else "all required beats present")
    add_check(checks, "video dry run scene fields", not missing_fields, "missing fields: " + ", ".join(missing_fields) if missing_fields else "screen, narration, and guardrail present for each scene")


def check_screen_safety(cue: dict[str, Any], runbook: str, checks: list[Check]) -> None:
    guardrail_text = " ".join(str(item) for item in cue.get("screen_safety_guardrails", []))
    combined = (guardrail_text + " " + runbook).lower()
    missing = [term for term in SCREEN_SAFETY_TERMS if term not in combined]
    add_check(checks, "video dry run screen safety terms", not missing, "missing: " + ", ".join(missing) if missing else "screen safety terms present")
    add_check(checks, "video dry run boundary", "without recording video" in BOUNDARY and "uploading video" in BOUNDARY, BOUNDARY)


def check_claims(script: str, scenes: list[dict[str, Any]], runbook: str, cue: dict[str, Any], checks: list[Check]) -> None:
    narration = " ".join(scene["narration_cue"] for scene in scenes)
    lower = (script + " " + narration).lower()
    hits = [phrase for phrase in FORBIDDEN_NARRATION_PHRASES if phrase in lower]
    add_check(checks, "video dry run live-claim boundary", not hits, "unsafe phrases: " + ", ".join(hits) if hits else "no unsafe live-claim narration")
    guardrail_text = " ".join(str(item) for item in cue.get("screen_safety_guardrails", []))
    safe_guidance = (lower + " " + runbook + " " + guardrail_text).lower()
    has_designed_wording = "designed for splunk mcp server" in safe_guidance
    add_check(checks, "video dry run Splunk MCP positioning", has_designed_wording, "designed-for wording present" if has_designed_wording else "missing designed-for wording")


def scan_text_files(root: Path, checks: list[Check]) -> list[dict[str, Any]]:
    scanned: list[dict[str, Any]] = []
    internal_hits: list[str] = []
    secret_hits: list[str] = []
    for rel_path in SCREEN_SCAN_FILES:
        path = root / rel_path
        if not path.exists():
            scanned.append({"path": rel_path, "exists": False, "status": "missing"})
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            scanned.append({"path": rel_path, "exists": True, "status": "skipped_non_text"})
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            secret_hits.append(f"non_utf8:{rel_path}")
            scanned.append({"path": rel_path, "exists": True, "status": "non_utf8"})
            continue
        for pattern in INTERNAL_PATTERNS:
            if pattern.search(text):
                internal_hits.append(f"{rel_path}:{pattern.pattern}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append(f"{rel_path}:{pattern.pattern}")
        scanned.append({"path": rel_path, "exists": True, "status": "scanned"})
    add_check(checks, "video dry run internal path scan", not internal_hits, "\n".join(internal_hits) if internal_hits else "no internal paths")
    add_check(checks, "video dry run secret-like scan", not secret_hits, "\n".join(secret_hits) if secret_hits else "no secret-like strings")
    return scanned


def check_external_gates(root: Path, checks: list[Check]) -> dict[str, Any]:
    url_validation = read_json(root / "reports/latest_submission_url_validation.json")
    go_no_go = read_json(root / "reports/latest_final_go_no_go.json")
    approved_urls_exists = (root / "submission/approved_public_urls.json").exists()
    pending_urls = set(url_validation.get("pending_urls", []))
    add_check(checks, "video dry run approved URLs absent", not approved_urls_exists, "approved_public_urls.json absent" if not approved_urls_exists else "approved_public_urls.json exists")
    add_check(checks, "video dry run URL gate closed", url_validation.get("final_submit_ready") is False, str(url_validation.get("final_submit_ready", "missing")))
    add_check(checks, "video dry run repo and video URLs pending", {"repository_url", "demo_video_url"}.issubset(pending_urls), ", ".join(sorted(pending_urls)))
    add_check(checks, "video dry run Go/No-Go final gate", go_no_go.get("final_submit_ready") is False, str(go_no_go.get("final_submit_ready", "missing")))
    return {
        "approved_public_urls_exists": approved_urls_exists,
        "url_validation_final_submit_ready": url_validation.get("final_submit_ready", "missing"),
        "go_no_go_final_submit_ready": go_no_go.get("final_submit_ready", "missing"),
        "pending_urls": sorted(pending_urls),
    }


def build_payload(root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    project_root = root.resolve()
    readiness, cue, command, content = check_video_state(project_root, checks)
    scenes = normalized_scenes(cue)
    evidence = check_evidence(project_root, checks)
    check_timeline(scenes, checks)
    runbook = read_text(project_root / "submission/VIDEO_RECORDING_RUNBOOK.md")
    script = read_text(project_root / "submission/DEMO_VIDEO_SCRIPT.md")
    check_screen_safety(cue, runbook, checks)
    check_claims(script, scenes, runbook, cue, checks)
    scanned = scan_text_files(project_root, checks)
    gate_state = check_external_gates(project_root, checks)

    failed = [check for check in checks if not check.passed]
    duration_seconds = max(
        [int(cue.get("duration_seconds", 0)), int(readiness.get("duration_seconds", 0))]
        + [scene["end_seconds"] for scene in scenes]
        + [0]
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_recording_review" if not failed else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(project_root) else "workspace",
        "duration_seconds": duration_seconds,
        "scene_count": len(scenes),
        "final_public_video_ready": False,
        "video_readiness_status": readiness.get("status", "missing"),
        "video_command_plan_status": command.get("status", "missing"),
        "content_rights_status": content.get("status", "missing"),
        "missing_evidence": [item["path"] for item in evidence if not item["exists"]],
        "evidence": evidence,
        "screen_scan_files": scanned,
        "external_gate_state": gate_state,
        "dry_run_actions": [
            "read video readiness report",
            "read video cue sheet and validate timeline",
            "read recording runbook and screen-safety guardrails",
            "scan planned recording files for internal paths and secret-like strings",
            "verify public URL and final submit gates remain closed",
        ],
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "external_gates_pending": [
            "screen recording capture",
            "public video upload approval",
            "public video URL insertion",
        ],
        "next_required_external_approval": "public_demo_video",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Demo Video Dry Run",
        "",
        f"Status: {payload['status']}",
        f"Duration: {payload['duration_seconds']} seconds",
        f"Scene count: {payload['scene_count']}",
        f"Final public video ready: {str(payload['final_public_video_ready']).lower()}",
        "",
        "## Dry Run Actions",
        "",
    ]
    for item in payload["dry_run_actions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        lines.append(f"- {check['status']}: {check['name']} - {check['detail']}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    check_rows = "\n".join(
        "<tr>"
        f"<td>{esc(check['name'])}</td>"
        f"<td class=\"{'ready' if check['status'] == 'pass' else 'fail'}\">{esc(check['status'])}</td>"
        f"<td>{esc(check['detail'])}</td>"
        "</tr>"
        for check in payload["checks"]
    )
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        "</tr>"
        for item in payload["evidence"]
    )
    actions = "\n".join(f"<li>{esc(item)}</li>" for item in payload["dry_run_actions"])
    gates = "\n".join(f"<li>{esc(item)}</li>" for item in payload["external_gates_pending"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Demo Video Dry Run</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
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
    <h1>Demo Video Dry Run</h1>
    <p>Local-only recording rehearsal and screen safety scan.</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <table>
        <tbody>
          <tr><th>Status</th><td class="{'ready' if payload['status'] == 'ready_for_recording_review' else 'fail'}">{esc(payload['status'])}</td></tr>
          <tr><th>Duration</th><td>{esc(payload['duration_seconds'])} seconds</td></tr>
          <tr><th>Scenes</th><td>{esc(payload['scene_count'])}</td></tr>
          <tr><th>Final public video ready</th><td>{esc(payload['final_public_video_ready'])}</td></tr>
          <tr><th>Approved public URLs</th><td>{esc(payload['external_gate_state']['approved_public_urls_exists'])}</td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Dry Run Actions</h2>
      <ul>{actions}</ul>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{check_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Recording Evidence</h2>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{evidence_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>External Gates Still Pending</h2>
      <ul>{gates}</ul>
    </section>
  </main>
</body>
</html>
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(root: Path) -> dict[str, Any]:
    payload = build_payload(root)
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_video_dry_run.json", payload)
    (reports / "latest_video_dry_run.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_video_dry_run.html").write_text(render_html(payload), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local-only demo video dry run report.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    payload = run(Path(args.root).resolve())
    print(json.dumps({
        "status": payload["status"],
        "failed_count": payload["failed_count"],
        "duration_seconds": payload["duration_seconds"],
        "scene_count": payload["scene_count"],
        "html": "reports/latest_video_dry_run.html",
        "markdown": "reports/latest_video_dry_run.md",
        "json": "reports/latest_video_dry_run.json",
    }, ensure_ascii=False, indent=2))
    return 0 if payload["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
