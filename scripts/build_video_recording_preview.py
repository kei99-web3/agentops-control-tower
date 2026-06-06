from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PUBLIC_CANDIDATE = "public_repo_candidate/agentops-control-tower"
DEFAULT_PORT = 8765
BOUNDARY = (
    "This recording preview is local preparation only. It copies the reviewed public candidate "
    "to an isolated temporary folder, scans the recording files, and provides a localhost preview "
    "command template without recording video, uploading video, publishing files, writing approved "
    "URLs, updating Devpost, or submitting anything."
)

REQUIRED_FILES = [
    "reports/latest_demo_tour.html",
    "reports/latest_control_tower.html",
    "reports/latest_local_spl_query_results.html",
    "reports/latest_video_readiness.html",
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

ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/][^\n\r\"']+")


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def sanitize(value: str) -> str:
    return ABSOLUTE_PATH_PATTERN.sub("<local-path>", value)


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=sanitize(detail)))


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def candidate_source(root: Path) -> Path:
    return root if is_public_candidate_root(root) else root / PUBLIC_CANDIDATE


def private_workspace_root(root: Path) -> Path:
    workspace_name = "AI" + "_Workspace"
    for candidate in [root, *root.parents]:
        if candidate.name == workspace_name:
            return candidate
    return root


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def copy_candidate(source: Path, target: Path) -> None:
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "release"),
    )


def scan_text_files(root: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
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
    return scanned, internal_hits, secret_hits


def public_video_safe_readback(
    *,
    status: str,
    preview_url: str,
    stage_policy: str,
    stage_removed_after_run: bool,
    duration_seconds: int | None,
    scanned: list[dict[str, Any]],
    internal_hit_count: int,
    secret_hit_count: int,
    failed_count: int,
) -> dict[str, Any]:
    missing_count = sum(1 for item in scanned if item.get("status") == "missing")
    return {
        "action_key": "public_demo_video",
        "status": status,
        "evidence_note_target": "submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md",
        "screen_safety_checklist": "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
        "preview_url": preview_url,
        "stage_policy": stage_policy,
        "stage_removed_after_run": stage_removed_after_run,
        "duration_seconds": duration_seconds,
        "screen_scan": {
            "scanned_count": len([item for item in scanned if item.get("status") == "scanned"]),
            "missing_count": missing_count,
            "internal_path_hit_count": internal_hit_count,
            "secret_like_hit_count": secret_hit_count,
        },
        "ready_for_recording_review": status == "ready_for_recording_review" and failed_count == 0,
        "final_recording_review_required": True,
        "ready_for_public_upload": False,
        "external_actions_attempted": False,
        "external_actions_completed": False,
        "forbidden_content": [
            "credentials",
            "tokens",
            "account screenshots",
            "browser tabs",
            "billing pages",
            "OAuth screens",
            "local absolute paths",
            "private workspace material",
            "private logs",
            "customer data",
        ],
        "copy_policy": (
            "Use this public_video_safe_readback block plus a short manual final-recording "
            "review summary for post-action evidence. Do not copy raw recording output, "
            "account screenshots, browser tabs, credentials, tokens, or local absolute paths."
        ),
        "next_required_external_approval": "public_demo_video",
    }


def build_payload(root: Path, *, port: int, keep_stage: bool) -> dict[str, Any]:
    project_root = root.resolve()
    source = candidate_source(project_root).resolve()
    workspace_root = private_workspace_root(project_root)
    checks: list[Check] = []
    temp_context: tempfile.TemporaryDirectory[str] | None = None
    readiness: dict[str, Any] = {}
    cue: dict[str, Any] = {}
    scanned: list[dict[str, Any]] = []
    internal_hit_count = 0
    secret_hit_count = 0

    add_check(checks, "candidate source exists", source.exists(), str(source))
    add_check(checks, "candidate source is public candidate", is_public_candidate_root(source), str(source))

    if keep_stage:
        stage_root = Path(tempfile.mkdtemp(prefix="agentops-video-preview-")).resolve()
    else:
        temp_context = tempfile.TemporaryDirectory(prefix="agentops-video-preview-")
        stage_root = Path(temp_context.name).resolve()
    stage = stage_root / "agentops-control-tower"
    add_check(checks, "stage root under system temp", is_relative_to(stage_root, Path(tempfile.gettempdir()).resolve()), str(stage_root))
    add_check(checks, "stage root outside private workspace", not is_relative_to(stage_root, workspace_root), str(stage_root))

    stage_created = False
    if source.exists() and not any(not check.passed for check in checks):
        copy_candidate(source, stage)
        stage_created = True
        add_check(checks, "recording stage isolated", not is_relative_to(stage, workspace_root), str(stage))
        missing = [item for item in REQUIRED_FILES if not (stage / item).exists()]
        add_check(checks, "recording required files", not missing, "missing: " + ", ".join(missing) if missing else "all required files present")
        readiness = read_json(stage / "reports/latest_video_readiness.json")
        cue = read_json(stage / "reports/latest_video_cue_sheet.json")
        url_validation = read_json(stage / "reports/latest_submission_url_validation.json")
        add_check(checks, "video readiness status", readiness.get("status") == "ready_for_recording_review", str(readiness.get("status", "missing")))
        add_check(checks, "video cue status", cue.get("status") == "ready_for_recording_review", str(cue.get("status", "missing")))
        add_check(checks, "video duration under three minutes", int(cue.get("duration_seconds", 999)) <= 180 and int(readiness.get("duration_seconds", 999)) <= 180, f"cue={cue.get('duration_seconds', 'missing')} readiness={readiness.get('duration_seconds', 'missing')}")
        add_check(checks, "approved URL writeback absent", not (stage / "submission/approved_public_urls.json").exists(), "approved_public_urls.json absent")
        add_check(checks, "submission URLs still pending", set(url_validation.get("pending_urls", [])) == {"repository_url", "demo_video_url"}, ", ".join(url_validation.get("pending_urls", [])))
        scanned, internal_hits, secret_hits = scan_text_files(stage)
        internal_hit_count = len(internal_hits)
        secret_hit_count = len(secret_hits)
        add_check(checks, "recording screen internal path scan", not internal_hits, "\n".join(internal_hits) if internal_hits else "no internal paths")
        add_check(checks, "recording screen secret-like scan", not secret_hits, "\n".join(secret_hits) if secret_hits else "no secret-like strings")

    failed = [check for check in checks if not check.passed]
    status = "ready_for_recording_review" if not failed else "needs_more_evidence"
    duration_values = [
        int(value)
        for value in [cue.get("duration_seconds"), readiness.get("duration_seconds")]
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit())
    ]
    duration_seconds = max(duration_values) if duration_values else None
    preview_url = f"http://127.0.0.1:{port}/reports/latest_demo_tour.html"
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "root_type": "public_candidate" if is_public_candidate_root(project_root) else "workspace",
        "candidate_source": "." if is_public_candidate_root(project_root) else PUBLIC_CANDIDATE,
        "stage_policy": "system_temp_public_candidate_copy",
        "stage_created": stage_created,
        "stage_removed_after_run": not keep_stage,
        "stage_path": "<system-temp>/agentops-video-preview-*/agentops-control-tower",
        "preview_url": preview_url,
        "server_command_template": f"python -m http.server {port} --bind 127.0.0.1 --directory <recording-stage>",
        "screen_scan_files": scanned,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "external_actions_attempted": False,
        "external_actions_completed": False,
        "next_required_external_approval": "public_demo_video",
    }
    payload["public_video_safe_readback"] = public_video_safe_readback(
        status=status,
        preview_url=preview_url,
        stage_policy="system_temp_public_candidate_copy",
        stage_removed_after_run=not keep_stage,
        duration_seconds=duration_seconds,
        scanned=scanned,
        internal_hit_count=internal_hit_count,
        secret_hit_count=secret_hit_count,
        failed_count=len(failed),
    )
    if temp_context is not None:
        temp_context.cleanup()
    return payload


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    safe = payload["public_video_safe_readback"]
    scan = safe["screen_scan"]
    lines = [
        "# Demo Video Recording Preview",
        "",
        f"Status: {payload['status']}",
        f"Candidate: `{payload['candidate_source']}`",
        f"Preview URL: `{payload['preview_url']}`",
        f"Server command template: `{payload['server_command_template']}`",
        f"Stage removed after run: {str(payload['stage_removed_after_run']).lower()}",
        "",
        "## Public Video Safe Readback",
        "",
        f"- Evidence note target: `{safe['evidence_note_target']}`",
        f"- Screen safety checklist: `{safe['screen_safety_checklist']}`",
        f"- Duration seconds: `{safe['duration_seconds']}`",
        f"- Screen scan: {scan['scanned_count']} scanned, {scan['missing_count']} missing, {scan['internal_path_hit_count']} internal-path hits, {scan['secret_like_hit_count']} secret-like hits",
        f"- Ready for public upload: {str(safe['ready_for_public_upload']).lower()}",
        f"- Copy policy: {safe['copy_policy']}",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        lines.append(f"- {check['status']}: {check['name']} - {check['detail']}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    safe = payload["public_video_safe_readback"]
    scan = safe["screen_scan"]
    check_rows = "\n".join(
        "<tr>"
        f"<td>{esc(check['name'])}</td>"
        f"<td class=\"{'ready' if check['status'] == 'pass' else 'fail'}\">{esc(check['status'])}</td>"
        f"<td>{esc(check['detail'])}</td>"
        "</tr>"
        for check in payload["checks"]
    )
    scan_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td>{esc(item['status'])}</td>"
        "</tr>"
        for item in payload["screen_scan_files"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Demo Video Recording Preview</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ width: 240px; color: #5f6d7c; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Demo Video Recording Preview</h1>
    <p>Local-only localhost preview rehearsal for the public demo video path.</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <table>
        <tbody>
          <tr><th>Status</th><td class="{'ready' if payload['status'] == 'ready_for_recording_review' else 'fail'}">{esc(payload['status'])}</td></tr>
          <tr><th>Candidate</th><td><code>{esc(payload['candidate_source'])}</code></td></tr>
          <tr><th>Preview URL</th><td><code>{esc(payload['preview_url'])}</code></td></tr>
          <tr><th>Server command template</th><td><code>{esc(payload['server_command_template'])}</code></td></tr>
          <tr><th>Stage policy</th><td>{esc(payload['stage_policy'])}</td></tr>
          <tr><th>Stage removed after run</th><td>{esc(payload['stage_removed_after_run'])}</td></tr>
          <tr><th>External actions attempted</th><td>{esc(payload['external_actions_attempted'])}</td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Public Video Safe Readback</h2>
      <table>
        <tbody>
          <tr><th>Evidence note target</th><td><code>{esc(safe['evidence_note_target'])}</code></td></tr>
          <tr><th>Screen safety checklist</th><td><code>{esc(safe['screen_safety_checklist'])}</code></td></tr>
          <tr><th>Duration seconds</th><td>{esc(safe['duration_seconds'])}</td></tr>
          <tr><th>Screen scan</th><td>{esc(scan['scanned_count'])} scanned, {esc(scan['missing_count'])} missing, {esc(scan['internal_path_hit_count'])} internal-path hits, {esc(scan['secret_like_hit_count'])} secret-like hits</td></tr>
          <tr><th>Ready for public upload</th><td>{esc(safe['ready_for_public_upload'])}</td></tr>
          <tr><th>Copy policy</th><td>{esc(safe['copy_policy'])}</td></tr>
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
    <section>
      <h2>Screen Scan Files</h2>
      <table>
        <thead><tr><th>Path</th><th>Status</th></tr></thead>
        <tbody>{scan_rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(root: Path, *, port: int, keep_stage: bool) -> dict[str, Any]:
    payload = build_payload(root, port=port, keep_stage=keep_stage)
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "latest_video_recording_preview.json", payload)
    (reports / "latest_video_recording_preview.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_video_recording_preview.html").write_text(render_html(payload), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local-only demo video recording preview report.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--keep-stage", action="store_true", help="Leave the temporary recording stage in place for a local preview server.")
    args = parser.parse_args()
    payload = run(Path(args.root).resolve(), port=args.port, keep_stage=args.keep_stage)
    print(json.dumps({
        "status": payload["status"],
        "failed_count": payload["failed_count"],
        "preview_url": payload["preview_url"],
        "stage_policy": payload["stage_policy"],
        "stage_removed_after_run": payload["stage_removed_after_run"],
        "external_actions_attempted": payload["external_actions_attempted"],
        "html": "reports/latest_video_recording_preview.html",
        "markdown": "reports/latest_video_recording_preview.md",
        "json": "reports/latest_video_recording_preview.json",
    }, ensure_ascii=False, indent=2))
    return 0 if payload["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
