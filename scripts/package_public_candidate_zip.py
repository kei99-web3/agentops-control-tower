from __future__ import annotations

import argparse
import hashlib
import html
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ZIP_NAME = "agentops-control-tower-public-candidate.zip"
SKIP_DIRS = {".git", "__pycache__", "release", "public_repo_candidate"}
SKIP_SUFFIXES = {".pyc", ".zip"}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def source_root_for(root: Path) -> Path:
    candidate = root / "public_repo_candidate" / "agentops-control-tower"
    if candidate.exists():
        return candidate
    return root


def should_skip(path: Path, source_root: Path) -> bool:
    rel_parts = path.relative_to(source_root).parts
    if any(part in SKIP_DIRS for part in rel_parts):
        return True
    return path.suffix.lower() in SKIP_SUFFIXES


def iter_files(source_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in source_root.rglob("*"):
        if path.is_dir() or should_skip(path, source_root):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(source_root).as_posix())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_zip(root: Path) -> dict[str, Any]:
    source_root = source_root_for(root)
    output_dir = root / "release"
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / ZIP_NAME
    files = iter_files(source_root)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(source_root).as_posix())
    size_bytes = zip_path.stat().st_size
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "local_zip_ready_for_user_review",
        "zip": "release/" + ZIP_NAME,
        "source_root": source_root.name,
        "file_count": len(files),
        "size_bytes": size_bytes,
        "sha256": sha256_file(zip_path),
        "files": [path.relative_to(source_root).as_posix() for path in files],
        "publication_boundary": "This zip has not been published. Public GitHub or Devpost upload requires explicit user approval.",
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def render_html(payload: dict[str, Any]) -> str:
    rows = "\n".join(
        f"<tr><td>{esc(item)}</td></tr>"
        for item in payload["files"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Candidate Zip Manifest</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 9px; text-align: left; vertical-align: top; }}
    th {{ color: #5f6d7c; }}
    code {{ background: #edf3f6; border-radius: 4px; padding: 2px 5px; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Public Candidate Zip Manifest</h1>
    <p>Local packaging proof for Agentic Incident Command Center. The zip is not published.</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <p>Status: <span class="ready">{esc(payload['status'])}</span></p>
      <p>Zip: <code>{esc(payload['zip'])}</code></p>
      <p>Files: {esc(payload['file_count'])}</p>
      <p>Size bytes: {esc(payload['size_bytes'])}</p>
      <p>SHA256: <code>{esc(payload['sha256'])}</code></p>
      <h3>Publication Boundary</h3>
      <p class="pending">{esc(payload['publication_boundary'])}</p>
    </section>
    <section>
      <h2>Included Files</h2>
      <table>
        <thead><tr><th>Path</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def run(root: Path) -> dict[str, Any]:
    payload = build_zip(root)
    write_json(root / "reports" / "latest_public_candidate_zip_manifest.json", payload)
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "reports" / "latest_public_candidate_zip_manifest.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "zip": payload["zip"],
        "file_count": payload["file_count"],
        "sha256": payload["sha256"],
        "manifest": "reports/latest_public_candidate_zip_manifest.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Package the public repo candidate into a local zip.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    print(json.dumps(run(Path(args.root).resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
