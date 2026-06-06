from __future__ import annotations

import argparse
import configparser
import hashlib
import html
import json
import re
import tarfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APP_DIR = "splunk_app/agentops_control_tower"
PACKAGE_PATH = "dist/agentops-control-tower-splunk-app.spl"
PACKAGE_ROOT = "agentops_control_tower"

REQUIRED_MEMBERS = [
    "agentops_control_tower/README.md",
    "agentops_control_tower/default/app.conf",
    "agentops_control_tower/default/indexes.conf",
    "agentops_control_tower/default/props.conf",
    "agentops_control_tower/default/savedsearches.conf",
    "agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
    "agentops_control_tower/metadata/default.meta",
]

INTERNAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"C:\\" + "Users",
        "PC" + "_User",
        r"Desktop\\" + "AI" + "_Workspace",
        "AI" + "_Workspace",
        r"\." + "company",
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


def iter_app_files(app_root: Path) -> list[Path]:
    return sorted(
        [path for path in app_root.rglob("*") if path.is_file()],
        key=lambda item: item.relative_to(app_root).as_posix(),
    )


def safe_member_name(path: Path, app_root: Path) -> str:
    return f"{PACKAGE_ROOT}/{path.relative_to(app_root).as_posix()}"


def add_normalized_file(archive: tarfile.TarFile, path: Path, arcname: str) -> None:
    info = archive.gettarinfo(str(path), arcname)
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    with path.open("rb") as handle:
        archive.addfile(info, handle)


def package_app(root: Path) -> tuple[Path, list[str]]:
    app_root = root / APP_DIR
    output = root / PACKAGE_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    files = iter_app_files(app_root)
    with tarfile.open(output, "w:gz") as archive:
        for path in files:
            add_normalized_file(archive, path, safe_member_name(path, app_root))
    return output, [safe_member_name(path, app_root) for path in files]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_text_files(app_root: Path, checks: list[Check]) -> None:
    internal_hits: list[str] = []
    secret_hits: list[str] = []
    for path in iter_app_files(app_root):
        rel = path.relative_to(app_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            add_check(checks, f"text decode {rel}", False, "non-utf8 text file")
            continue
        for pattern in INTERNAL_PATTERNS:
            if pattern.search(text):
                internal_hits.append(f"{rel}:{pattern.pattern}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append(f"{rel}:{pattern.pattern}")
    add_check(checks, "Splunk app internal path scan", not internal_hits, "\n".join(internal_hits) if internal_hits else "no internal patterns")
    add_check(checks, "Splunk app secret-like scan", not secret_hits, "\n".join(secret_hits) if secret_hits else "no secret-like patterns")


def validate_package(root: Path, package_path: Path, expected_members: list[str], checks: list[Check]) -> list[str]:
    if not package_path.exists():
        add_check(checks, "Splunk app package exists", False, "missing")
        return []
    add_check(checks, "Splunk app package size", package_path.stat().st_size > 1000, f"bytes={package_path.stat().st_size}")

    with tarfile.open(package_path, "r:gz") as archive:
        members = [member.name for member in archive.getmembers() if member.isfile()]

    unsafe = [
        name for name in members
        if name.startswith("/") or name.startswith("\\") or ".." in Path(name).parts
    ]
    add_check(checks, "Splunk app package path traversal guard", not unsafe, "unsafe: " + ", ".join(unsafe) if unsafe else "no unsafe member names")

    wrong_root = [name for name in members if not name.startswith(PACKAGE_ROOT + "/")]
    add_check(checks, "Splunk app package root folder", not wrong_root, "wrong root: " + ", ".join(wrong_root) if wrong_root else PACKAGE_ROOT)

    missing = [item for item in REQUIRED_MEMBERS if item not in members]
    add_check(checks, "Splunk app package required members", not missing, "missing: " + ", ".join(missing) if missing else f"{len(REQUIRED_MEMBERS)} required members present")
    add_check(checks, "Splunk app package member count", len(members) == len(expected_members), f"members={len(members)} expected={len(expected_members)}")
    return members


def validate_app_files(root: Path, checks: list[Check]) -> None:
    app_root = root / APP_DIR
    app_conf = app_root / "default/app.conf"
    dashboard = app_root / "default/data/ui/views/agentops_control_tower.xml"

    parser = configparser.ConfigParser()
    parser.read(app_conf, encoding="utf-8")
    add_check(checks, "packaged app label", parser.get("ui", "label", fallback="") == "Agentic Incident Command Center", "ui.label checked")
    add_check(checks, "packaged app id", parser.get("package", "id", fallback="") == "agentops_control_tower", "package.id checked")

    try:
        tree = ET.parse(dashboard)
        root_node = tree.getroot()
        add_check(checks, "packaged dashboard XML parses", root_node.tag == "form", f"root={root_node.tag}")
    except ET.ParseError as error:
        add_check(checks, "packaged dashboard XML parses", False, str(error))


def build_payload(root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    app_root = root / APP_DIR
    missing_source = [item for item in REQUIRED_MEMBERS if not (root / item.replace(PACKAGE_ROOT, APP_DIR, 1)).exists()]
    add_check(checks, "Splunk app source files", not missing_source, "missing: " + ", ".join(missing_source) if missing_source else f"{len(REQUIRED_MEMBERS)} source files present")
    package_path, expected_members = package_app(root)
    members = validate_package(root, package_path, expected_members, checks)
    scan_text_files(app_root, checks)
    validate_app_files(root, checks)
    failed = [check for check in checks if not check.passed]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not failed else "needs_more_evidence",
        "package": PACKAGE_PATH,
        "package_exists": package_path.exists(),
        "package_size_bytes": package_path.stat().st_size if package_path.exists() else 0,
        "sha256": sha256(package_path) if package_path.exists() else "",
        "member_count": len(members),
        "members": members,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": "This local package is not installed, uploaded, published, connected to Splunk, or submitted anywhere.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Splunk App Package Manifest",
        "",
        f"Status: {payload['status']}",
        f"Package: {payload['package']}",
        f"Size bytes: {payload['package_size_bytes']}",
        f"SHA256: {payload['sha256']}",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        lines.append(f"- {check['name']}: {check['status']} ({check['detail']})")
    lines.extend(["", "## Members", ""])
    for member in payload["members"]:
        lines.append(f"- `{member}`")
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
    member_rows = "\n".join(f"<tr><td>{esc(member)}</td></tr>" for member in payload["members"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Splunk App Package Manifest</title>
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
    <h1>Splunk App Package Manifest</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Package</h2>
      <table>
        <tbody>
          <tr><th>Path</th><td><code>{esc(payload['package'])}</code></td></tr>
          <tr><th>Size bytes</th><td>{esc(payload['package_size_bytes'])}</td></tr>
          <tr><th>SHA256</th><td><code>{esc(payload['sha256'])}</code></td></tr>
          <tr><th>Members</th><td>{esc(payload['member_count'])}</td></tr>
        </tbody>
      </table>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{check_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Members</h2>
      <table>
        <thead><tr><th>Path</th></tr></thead>
        <tbody>{member_rows}</tbody>
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
    write_json(reports / "latest_splunk_app_package_manifest.json", payload)
    (reports / "latest_splunk_app_package_manifest.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_splunk_app_package_manifest.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "package": payload["package"],
        "failed_count": payload["failed_count"],
        "html": "reports/latest_splunk_app_package_manifest.html",
        "markdown": "reports/latest_splunk_app_package_manifest.md",
        "json": "reports/latest_splunk_app_package_manifest.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Package the local Splunk app candidate into a reviewable .spl artifact.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
