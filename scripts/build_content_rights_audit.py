from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY = (
    "This content rights audit is local review evidence only. It does not publish a repository, "
    "record or upload video, write approved URLs, update Devpost, request trademark permission, "
    "or submit anything."
)

MEDIA_SUFFIXES = {".mp3", ".wav", ".m4a", ".aac", ".mp4", ".mov", ".webm", ".avi"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
TEXT_SUFFIXES = {".md", ".txt", ".py", ".json", ".html", ".xml", ".csv", ".conf"}


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


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def list_files(root: Path) -> list[Path]:
    skip_dirs = {".git", "__pycache__", "release", "video_drafts"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        parts = set(path.relative_to(root).parts)
        if parts.intersection(skip_dirs):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def asset_inventory(root: Path) -> list[dict[str, Any]]:
    assets_dir = root / "assets"
    if not assets_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(assets_dir.rglob("*")):
        if path.is_dir():
            continue
        rows.append({
            "path": rel(root, path),
            "suffix": path.suffix.lower(),
            "size_bytes": path.stat().st_size,
            "role": "Dashboard screenshot generated from the local synthetic-data demo." if path.name == "dashboard_preview.png" else "Review manually before publication.",
        })
    return rows


def media_inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": rel(root, path),
            "suffix": path.suffix.lower(),
            "size_bytes": path.stat().st_size,
        }
        for path in list_files(root)
        if path.suffix.lower() in MEDIA_SUFFIXES
    ]


def png_signature(path: Path) -> bool:
    if not path.exists():
        return False
    data = path.read_bytes()
    return len(data) > 1000 and data[:8] == b"\x89PNG\r\n\x1a\n"


def text_contains_any(root: Path, rel_paths: list[str], terms: list[str]) -> bool:
    text = "\n".join(read_text(root / path) for path in rel_paths)
    return all(term in text for term in terms)


def public_wording_scan(root: Path) -> dict[str, Any]:
    suspicious_terms = [
        "uses royalty-free music",
        "includes background music",
        "contains stock footage",
        "uses stock footage",
        "copyrighted song included",
        "licensed track included",
        "Getty Images asset",
        "Shutterstock asset",
    ]
    hits: list[str] = []
    for path in list_files(root):
        if path.name == "build_content_rights_audit.py":
            continue
        if path.name.startswith("latest_content_rights_audit."):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = read_text(path)
        for term in suspicious_terms:
            if term.lower() in text.lower():
                hits.append(f"{rel(root, path)}:{term}")
    return {
        "suspicious_terms": suspicious_terms,
        "hits": hits,
        "clean": not hits,
    }


def build_payload(root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    license_text = read_text(root / "LICENSE")
    video_runbook = read_text(root / "submission/VIDEO_RECORDING_RUNBOOK.md")
    video_screen_checklist = read_text(root / "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md")
    official_audit = read_text(root / "submission/OFFICIAL_REQUIREMENTS_AUDIT.md")
    video_readiness = read_text(root / "reports/latest_video_readiness.json")
    assets = asset_inventory(root)
    media = media_inventory(root)
    wording_scan = public_wording_scan(root)

    add_check(checks, "Apache-2.0 license present", "Apache License" in license_text and "Version 2.0" in license_text, "LICENSE")
    add_check(checks, "dashboard preview PNG present", png_signature(root / "assets/dashboard_preview.png"), "assets/dashboard_preview.png")
    add_check(checks, "asset inventory limited", len(assets) == 1 and assets[0]["path"] == "assets/dashboard_preview.png", ", ".join(item["path"] for item in assets))
    add_check(checks, "no bundled audio or video media", len(media) == 0, ", ".join(item["path"] for item in media) if media else "no audio/video files bundled")
    add_check(checks, "video runbook synthetic-data boundary", "Use synthetic data only." in video_runbook, "synthetic-data screen safety")
    add_check(checks, "video runbook account/privacy boundary", "Do not show real customer, cloud, incident, identity, ticketing, or Splunk account screens." in video_runbook, "account screen safety")
    add_check(checks, "video screen checklist pending review", "Status: pending screen safety review" in video_screen_checklist and "Public video upload stays blocked" in video_screen_checklist, "screen safety checklist stays gated")
    add_check(checks, "video screen checklist privacy boundary", "Do not show `.env`, config files, API keys, OAuth tokens, or private logs." in video_screen_checklist, "secret screen safety")
    add_check(checks, "video readiness not final public video", '"final_public_video_ready": false' in video_readiness, "public video still requires approval/upload")
    add_check(
        checks,
        "official audit content rights note",
        "unlicensed third-party trademarks, music, copyrighted material" in official_audit,
        "official requirements audit rights note",
    )
    add_check(checks, "public wording rights scan", wording_scan["clean"], ", ".join(wording_scan["hits"]) if wording_scan["hits"] else "no suspicious media-license terms")
    add_check(checks, "boundary text", "does not publish" in BOUNDARY and "submit anything" in BOUNDARY, BOUNDARY)

    failed = [check for check in checks if not check.passed]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not failed else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "license": {
            "path": "LICENSE",
            "spdx": "Apache-2.0",
            "present": bool(license_text),
        },
        "assets": assets,
        "bundled_audio_video_media": media,
        "public_video_ready": False,
        "screen_safety_sources": [
            "submission/VIDEO_RECORDING_RUNBOOK.md",
            "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
            "reports/latest_video_readiness.html",
            "reports/latest_video_cue_sheet.html",
        ],
        "trademark_note": (
            "Splunk and Devpost names are used only to describe the hackathon, platform fit, "
            "and interoperability target. No sponsor logo, third-party music, stock footage, "
            "or account screenshots are bundled in the local package."
        ),
        "wording_scan": wording_scan,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "recommended_next_step": (
            "Before public video upload, watch the final recording end to end and confirm no private "
            "tabs, accounts, copyrighted music, unlicensed third-party marks, or unrelated media appear."
        ),
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Content Rights And Asset Safety Audit",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"License: {payload['license']['spdx']}",
        f"Public video ready: {str(payload['public_video_ready']).lower()}",
        "",
        "## Assets",
        "",
    ]
    for item in payload["assets"]:
        lines.append(f"- `{item['path']}` - {item['size_bytes']} bytes - {item['role']}")
    if not payload["assets"]:
        lines.append("- none")
    lines.extend(["", "## Bundled Audio/Video Media", ""])
    if payload["bundled_audio_video_media"]:
        for item in payload["bundled_audio_video_media"]:
            lines.append(f"- `{item['path']}` - {item['size_bytes']} bytes")
    else:
        lines.append("- none")
    lines.extend(["", "## Screen Safety Sources", ""])
    for source in payload["screen_safety_sources"]:
        lines.append(f"- `{source}`")
    lines.extend(["", "## Trademark Note", "", payload["trademark_note"], "", "## Checks", ""])
    for check in payload["checks"]:
        lines.append(f"- {check['name']}: {check['status']} ({check['detail']})")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    asset_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td>{esc(item['size_bytes'])}</td>"
        f"<td>{esc(item['role'])}</td>"
        "</tr>"
        for item in payload["assets"]
    ) or "<tr><td colspan=\"3\">none</td></tr>"
    media_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td>{esc(item['suffix'])}</td>"
        f"<td>{esc(item['size_bytes'])}</td>"
        "</tr>"
        for item in payload["bundled_audio_video_media"]
    ) or "<tr><td colspan=\"3\">none</td></tr>"
    check_rows = "\n".join(
        "<tr>"
        f"<td>{esc(check['name'])}</td>"
        f"<td class=\"{'ready' if check['status'] == 'pass' else 'fail'}\">{esc(check['status'])}</td>"
        f"<td>{esc(check['detail'])}</td>"
        "</tr>"
        for check in payload["checks"]
    )
    screen_source_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(source)}</code></td>"
        "</tr>"
        for source in payload["screen_safety_sources"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Content Rights And Asset Safety Audit</title>
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
    .pending {{ color: #a35b00; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Content Rights And Asset Safety Audit</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Snapshot</h2>
      <p>License: <strong>{esc(payload['license']['spdx'])}</strong></p>
      <p>Public video ready: <strong>{esc(payload['public_video_ready'])}</strong></p>
      <p>{esc(payload['trademark_note'])}</p>
      <p class="pending">{esc(payload['recommended_next_step'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Assets</h2>
      <table>
        <thead><tr><th>Path</th><th>Size</th><th>Role</th></tr></thead>
        <tbody>{asset_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Bundled Audio/Video Media</h2>
      <table>
        <thead><tr><th>Path</th><th>Type</th><th>Size</th></tr></thead>
        <tbody>{media_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Screen Safety Sources</h2>
      <table>
        <thead><tr><th>Path</th></tr></thead>
        <tbody>{screen_source_rows}</tbody>
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
    write_json(reports / "latest_content_rights_audit.json", payload)
    (reports / "latest_content_rights_audit.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_content_rights_audit.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "root_type": payload["root_type"],
        "failed_count": payload["failed_count"],
        "html": "reports/latest_content_rights_audit.html",
        "markdown": "reports/latest_content_rights_audit.md",
        "json": "reports/latest_content_rights_audit.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local content rights and asset safety audit.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
