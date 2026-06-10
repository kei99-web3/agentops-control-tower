from __future__ import annotations

import argparse
import hashlib
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ZIP_PATH = "release/agentops-control-tower-public-candidate.zip"
EXPECTED_ORDER = [
    "public_github_repository",
    "public_demo_video",
    "approved_url_writeback",
    "devpost_final_submission",
]
BOUNDARY = (
    "This public launch snapshot is local approval evidence only. It does not publish a repository, "
    "record or upload video, connect to Splunk, configure MCP, write approved URLs, update Devpost, "
    "save a draft, press submit, or mark the submission complete."
)


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


def official_mcp_readback_verified(root: Path) -> bool:
    readback = root / "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md"
    if not readback.exists():
        return False
    text = readback.read_text(encoding="utf-8").lower()
    return all(
        marker in text
        for marker in [
            "status: ready_for_claim_update",
            "checksum match: yes",
            "mcp connection status: connected",
            "tool used: `splunk_run_query`",
            "official splunk mcp server was installed and verified",
            "production splunk cloud deployment is not claimed",
        ]
    )


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024, ), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def action_by_key(actions: Any, key: str) -> dict[str, Any]:
    if not isinstance(actions, list):
        return {}
    for item in actions:
        if isinstance(item, dict) and item.get("key") == key:
            return item
    return {}


def zip_snapshot(root: Path, public_candidate: bool, publish: dict[str, Any], release: dict[str, Any]) -> dict[str, Any]:
    zip_path = root / ZIP_PATH
    if zip_path.exists():
        return {
            "path": ZIP_PATH,
            "exists": True,
            "size_bytes": zip_path.stat().st_size,
            "sha256": sha256_file(zip_path),
            "file_count": release.get("release_zip", {}).get("file_count")
            or publish.get("zip", {}).get("file_count"),
            "smoke_status": release.get("release_zip", {}).get("smoke_status")
            or publish.get("zip", {}).get("smoke_status"),
        }
    return {
        "path": ZIP_PATH,
        "exists": False,
        "size_bytes": 0,
        "sha256": "",
        "file_count": None,
        "smoke_status": "not_applicable_public_candidate_root" if public_candidate else "missing",
    }


def required_evidence(public_candidate: bool) -> list[dict[str, str]]:
    common = [
        {"path": "reports/latest_next_approval_packet.html", "role": "copy-paste approval phrases and human confirmations"},
        {"path": "reports/latest_public_repo_publish_brief.html", "role": "public repo approval boundary and ZIP evidence"},
        {"path": "reports/latest_public_repo_publication_preflight.html", "role": "public repo approval phrase and manual publication gate"},
        {"path": "reports/latest_video_readiness.html", "role": "screen-safe recording readiness"},
        {"path": "reports/latest_video_command_plan.html", "role": "post-approval recording/upload plan"},
        {"path": "reports/latest_public_video_upload_preflight.html", "role": "public video approval phrase and manual confirmation gate"},
        {"path": "reports/latest_video_cue_sheet.html", "role": "under-3-minute scene timing"},
        {"path": "reports/latest_approval_consistency_audit.html", "role": "approval order consistency"},
        {"path": "reports/latest_release_integrity_manifest.html", "role": "artifact hashes and no-publish boundary"},
        {"path": "reports/latest_content_rights_audit.html", "role": "license, media, and screen safety"},
        {"path": "reports/latest_submission_url_validation.html", "role": "pending public URL gates"},
        {"path": "reports/latest_post_action_evidence_brief.html", "role": "readback plan after approved external actions"},
        {"path": "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md", "role": "local evidence log template"},
    ]
    if public_candidate:
        return [
            {"path": "PUBLIC_REPO_CANDIDATE_MANIFEST.md", "role": "clean public candidate boundary"},
            *common,
        ]
    return [
        {"path": "public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md", "role": "clean public candidate folder boundary"},
        {"path": "reports/latest_release_zip_smoke_test.html", "role": "extract-and-test proof for the release ZIP"},
        {"path": "reports/latest_public_candidate_zip_manifest.html", "role": "release ZIP file list"},
        {"path": ZIP_PATH, "role": "local release ZIP for user review"},
        {"path": "reports/latest_public_repo_dry_run.html", "role": "isolated TEMP staging git-init/commit rehearsal for the clean public candidate"},
        {"path": "reports/latest_video_dry_run.html", "role": "local recording rehearsal and screen-safety scan"},
        {"path": "reports/latest_url_writeback_dry_run.html", "role": "temporary-copy rehearsal for approved URL writeback"},
        *common,
    ]


def load_state(root: Path) -> dict[str, Any]:
    return {
        "validation": read_json(root / "reports/latest_submission_validation.json"),
        "next_packet": read_json(root / "reports/latest_next_approval_packet.json"),
        "publish": read_json(root / "reports/latest_public_repo_publish_brief.json"),
        "repo_publication_preflight": read_json(root / "reports/latest_public_repo_publication_preflight.json"),
        "video": read_json(root / "reports/latest_video_readiness.json"),
        "video_upload_preflight": read_json(root / "reports/latest_public_video_upload_preflight.json"),
        "video_plan": read_json(root / "reports/latest_video_command_plan.json"),
        "video_cue": read_json(root / "reports/latest_video_cue_sheet.json"),
        "video_dry_run": read_json(root / "reports/latest_video_dry_run.json"),
        "url_writeback_dry_run": read_json(root / "reports/latest_url_writeback_dry_run.json"),
        "approval": read_json(root / "reports/latest_approval_consistency_audit.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
        "release": read_json(root / "reports/latest_release_integrity_manifest.json"),
        "content_rights": read_json(root / "reports/latest_content_rights_audit.json"),
        "post_action": read_json(root / "reports/latest_post_action_evidence_brief.json"),
    }


def build_checks(root: Path, payload: dict[str, Any], state: dict[str, Any]) -> list[Check]:
    checks: list[Check] = []
    public_candidate = payload["root_type"] == "public_candidate"
    evidence = payload["evidence"]
    missing = [item["path"] for item in evidence if not item["exists"]]
    ready_now = set(state["next_packet"].get("ready_now", []))
    add_check(checks, "required evidence present", not missing, "missing: " + ", ".join(missing) if missing else "all required evidence present")
    add_check(checks, "next approval target is public repo", state["next_packet"].get("next_approval_target") == "public_github_repository", str(state["next_packet"].get("next_approval_target")))
    repo_video_ready = {"public_github_repository", "public_demo_video"}.issubset(ready_now)
    if public_candidate:
        repo_video_ready = "public_github_repository" in ready_now
    add_check(checks, "public repo and video are ready now", repo_video_ready, ", ".join(sorted(ready_now)))
    add_check(checks, "public repo approval ready", state["publish"].get("public_repo_approval_ready") is True, str(state["publish"].get("public_repo_approval_ready")))
    add_check(
        checks,
        "public repo publication preflight ready and blocked",
        state["repo_publication_preflight"].get("status") == "ready_for_user_review"
        and state["repo_publication_preflight"].get("public_repo_publication_allowed") is False
        and state["repo_publication_preflight"].get("gate_status") == "blocked_by_public_repo_approval_gate",
        f"status={state['repo_publication_preflight'].get('status', 'missing')} allowed={state['repo_publication_preflight'].get('public_repo_publication_allowed', 'missing')} gate={state['repo_publication_preflight'].get('gate_status', 'missing')}",
    )
    add_check(checks, "video recording review ready", state["video"].get("status") == "ready_for_recording_review", str(state["video"].get("status", "missing")))
    video_upload_blocked = (
        state["video_upload_preflight"].get("status") == "ready_for_user_review"
        and state["video_upload_preflight"].get("public_video_upload_allowed") is False
        and state["video_upload_preflight"].get("gate_status") == "blocked_by_video_approval_gate"
    )
    if public_candidate:
        video_upload_blocked = (
            state["video_upload_preflight"].get("status") in {"ready_for_user_review", "needs_more_evidence"}
            and state["video_upload_preflight"].get("public_video_upload_allowed") is False
            and state["video_upload_preflight"].get("gate_status") in {"blocked_by_video_approval_gate", "needs_more_evidence"}
        )
    add_check(
        checks,
        "public video upload preflight ready and blocked",
        video_upload_blocked,
        f"status={state['video_upload_preflight'].get('status', 'missing')} allowed={state['video_upload_preflight'].get('public_video_upload_allowed', 'missing')} gate={state['video_upload_preflight'].get('gate_status', 'missing')}",
    )
    add_check(checks, "video cue under three minutes", int(state["video_cue"].get("duration_seconds", 999)) <= 180, str(state["video_cue"].get("duration_seconds", "missing")))
    if public_candidate:
        add_check(checks, "video dry run ready", True, "not_applicable_public_candidate_root")
        add_check(checks, "URL writeback dry run ready", True, "not_applicable_public_candidate_root")
    else:
        add_check(checks, "video dry run ready", state["video_dry_run"].get("status") == "ready_for_recording_review" and int(state["video_dry_run"].get("failed_count", 1)) == 0, f"status={state['video_dry_run'].get('status', 'missing')} failed={state['video_dry_run'].get('failed_count', 'missing')}")
        add_check(checks, "URL writeback dry run ready", state["url_writeback_dry_run"].get("status") == "ready_for_user_review" and int(state["url_writeback_dry_run"].get("failed_count", 1)) == 0 and state["url_writeback_dry_run"].get("approved_public_urls_written_to_working_tree") is False, f"status={state['url_writeback_dry_run'].get('status', 'missing')} failed={state['url_writeback_dry_run'].get('failed_count', 'missing')} wrote={state['url_writeback_dry_run'].get('approved_public_urls_written_to_working_tree', 'missing')}")
    add_check(checks, "approval order matches expected", state["approval"].get("expected_order") == EXPECTED_ORDER and state["approval"].get("failed_count") == 0, ", ".join(state["approval"].get("expected_order", [])))
    add_check(checks, "official Splunk MCP proof completed", official_mcp_readback_verified(root), "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md")
    if public_candidate:
        add_check(checks, "release ZIP status", True, "not_applicable_public_candidate_root")
    else:
        release_zip = payload["release_zip"]
        add_check(checks, "release ZIP exists", release_zip["exists"] is True, str(release_zip["exists"]))
        add_check(checks, "release ZIP smoke passed", release_zip["smoke_status"] == "pass", str(release_zip["smoke_status"]))
        add_check(checks, "release ZIP SHA256 present", len(str(release_zip["sha256"])) == 64, str(release_zip["sha256"]))
    add_check(checks, "approved public URLs not written", payload["approved_public_urls_exists"] is False, str(payload["approved_public_urls_exists"]))
    add_check(checks, "final submit remains false", payload["final_submit_ready"] is False, str(payload["final_submit_ready"]))
    add_check(checks, "content rights ready", state["content_rights"].get("status") == "ready_for_user_review", str(state["content_rights"].get("status", "missing")))
    add_check(checks, "post-action evidence remains incomplete before externals", state["post_action"].get("post_action_evidence_ready") is False, str(state["post_action"].get("post_action_evidence_ready")))
    add_check(checks, "no external action boundary", "does not publish" in BOUNDARY and "press submit" in BOUNDARY, BOUNDARY)
    return checks


def local_validation_snapshot(state: dict[str, Any], public_candidate: bool) -> dict[str, Any]:
    validation = state["validation"]
    go_no_go = state["go_no_go"]
    status = validation.get("overall_status", go_no_go.get("status", "missing"))
    failed_count = validation.get("failed_count", "missing")
    source = "reports/latest_submission_validation.json" if validation else "reports/latest_final_go_no_go.json"
    if public_candidate and not validation:
        return {
            "status": "not_bundled_public_candidate_root",
            "failed_count": "not_applicable_public_candidate_root",
            "source": "public_candidate_local_artifacts",
        }
    if (
        status == "needs_more_evidence"
        and go_no_go.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready") is True
        and go_no_go.get("missing_local_evidence", []) == []
        and go_no_go.get("missing_public_candidate_evidence", []) == []
    ):
        return {
            "status": "ready_for_user_review",
            "failed_count": 0,
            "source": "reports/latest_final_go_no_go.json",
        }
    return {
        "status": status,
        "failed_count": failed_count,
        "source": source,
    }


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    public_candidate = is_public_candidate_root(root)
    next_actions = state["next_packet"].get("actions", [])
    evidence = [
        {"path": item["path"], "role": item["role"], "exists": exists(root, item["path"])}
        for item in required_evidence(public_candidate)
    ]
    validation_snapshot = local_validation_snapshot(state, public_candidate)
    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "needs_more_evidence",
        "root_type": "public_candidate" if public_candidate else "workspace",
        "validation_status": validation_snapshot["status"],
        "validation_failed_count": validation_snapshot["failed_count"],
        "validation_source": validation_snapshot["source"],
        "next_approval_target": state["next_packet"].get("next_approval_target", ""),
        "ready_now": state["next_packet"].get("ready_now", []),
        "expected_order": EXPECTED_ORDER,
        "approval_phrases": {
            "public_github_repository": action_by_key(next_actions, "public_github_repository").get("approval_phrase", ""),
            "public_demo_video": action_by_key(next_actions, "public_demo_video").get("approval_phrase", ""),
            "optional_live_splunk_mcp_proof": action_by_key(next_actions, "optional_live_splunk_mcp_proof").get("approval_phrase", ""),
            "approved_url_writeback": action_by_key(next_actions, "approved_url_writeback").get("approval_phrase", ""),
            "devpost_final_submission": action_by_key(next_actions, "devpost_final_submission").get("approval_phrase", ""),
        },
        "release_zip": zip_snapshot(root, public_candidate, state["publish"], state["release"]),
        "public_repo": {
            "repo_name": state["publish"].get("repo_name", "agentops-control-tower"),
            "candidate_path": "PUBLIC_REPO_CANDIDATE_MANIFEST.md" if public_candidate else state["publish"].get("candidate_path", "public_repo_candidate/agentops-control-tower"),
            "approval_ready": state["publish"].get("public_repo_approval_ready") is True,
            "publication_preflight_status": state["repo_publication_preflight"].get("status", "missing"),
            "publication_preflight_gate_status": state["repo_publication_preflight"].get("gate_status", "missing"),
            "publication_preflight_allowed": state["repo_publication_preflight"].get("public_repo_publication_allowed", False),
            "status": action_by_key(next_actions, "public_github_repository").get("status", "missing"),
        },
        "public_video": {
            "status": state["video"].get("status", "missing"),
            "upload_preflight_status": state["video_upload_preflight"].get("status", "missing"),
            "upload_preflight_gate_status": state["video_upload_preflight"].get("gate_status", "missing"),
            "upload_preflight_allowed": state["video_upload_preflight"].get("public_video_upload_allowed", False),
            "dry_run_status": "not_applicable_public_candidate_root" if public_candidate else state["video_dry_run"].get("status", "missing"),
            "dry_run_failed_count": "not_applicable_public_candidate_root" if public_candidate else state["video_dry_run"].get("failed_count", "missing"),
            "duration_seconds": state["video"].get("duration_seconds", state["video_cue"].get("duration_seconds", "")),
            "scene_count": state["video"].get("scene_count", state["video_cue"].get("scene_count", "")),
            "final_public_video_ready": state["video"].get("final_public_video_ready", False),
        },
        "final_submit_ready": bool(state["go_no_go"].get("final_submit_ready", False)),
        "approved_public_urls_exists": (root / "submission/approved_public_urls.json").exists(),
        "url_writeback_dry_run": {
            "status": "not_applicable_public_candidate_root" if public_candidate else state["url_writeback_dry_run"].get("status", "missing"),
            "failed_count": "not_applicable_public_candidate_root" if public_candidate else state["url_writeback_dry_run"].get("failed_count", "missing"),
            "final_submit_ready_in_temp": "not_applicable_public_candidate_root" if public_candidate else state["url_writeback_dry_run"].get("final_submit_ready_in_temp", "missing"),
            "working_tree_write_guard": "not_applicable_public_candidate_root" if public_candidate else not bool(state["url_writeback_dry_run"].get("approved_public_urls_written_to_working_tree", True)),
        },
        "pending_urls": state["url_validation"].get("pending_urls", []),
        "post_action_evidence_ready": bool(state["post_action"].get("post_action_evidence_ready", False)),
        "official_splunk_mcp_proof": {
            "completed": official_mcp_readback_verified(root),
            "evidence": "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md",
            "claim_boundary": "local Splunk Enterprise Docker with synthetic data; production Splunk Cloud deployment is not claimed",
        },
        "evidence": evidence,
        "boundary": BOUNDARY,
        "recommended_next_step": "Review this snapshot, then use reports/latest_next_approval_packet.html before any public repo or demo video approval.",
    }
    checks = build_checks(root, payload, state)
    failed = [check for check in checks if not check.passed]
    payload["failed_count"] = len(failed)
    payload["checks"] = [check.__dict__ for check in checks]
    payload["missing_evidence"] = [item["path"] for item in evidence if not item["exists"]]
    payload["status"] = "ready_for_user_review" if not failed else "needs_more_evidence"
    return payload


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Public Launch Snapshot",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Next approval target: {payload['next_approval_target']}",
        f"Ready now: {', '.join(payload['ready_now']) if payload['ready_now'] else 'none'}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        f"Approved public URLs file exists: {str(payload['approved_public_urls_exists']).lower()}",
        "",
        "## Approval Phrases",
        "",
    ]
    for key in EXPECTED_ORDER:
        phrase = payload["approval_phrases"].get(key) or "not ready"
        lines.append(f"- {key}: `{phrase}`")
    lines.extend([
        "",
        "## Release ZIP",
        "",
        f"- Path: `{payload['release_zip']['path']}`",
        f"- Exists: {payload['release_zip']['exists']}",
        f"- File count: {payload['release_zip']['file_count']}",
        f"- SHA256: `{payload['release_zip']['sha256']}`",
        f"- Smoke status: {payload['release_zip']['smoke_status']}",
        "",
        "## Checks",
        "",
    ])
    for check in payload["checks"]:
        lines.append(f"- {check['name']}: {check['status']} ({check['detail']})")
    lines.extend(["", "## Evidence", ""])
    for item in payload["evidence"]:
        status = "present" if item["exists"] else "missing"
        lines.append(f"- `{item['path']}` ({status}) - {item['role']}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    summary_rows = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in [
            ("Root type", payload["root_type"]),
            ("Validation status", payload["validation_status"]),
            ("Validation failed count", payload["validation_failed_count"]),
            ("Next approval target", payload["next_approval_target"]),
            ("Ready now", ", ".join(payload["ready_now"]) if payload["ready_now"] else "none"),
            ("Final submit ready", payload["final_submit_ready"]),
            ("Approved public URLs file", payload["approved_public_urls_exists"]),
            ("Pending URLs", ", ".join(payload["pending_urls"]) if payload["pending_urls"] else "none"),
            ("Post-action evidence ready", payload["post_action_evidence_ready"]),
        ]
    )
    approval_rows = "\n".join(
        f"<tr><td>{esc(key)}</td><td><code>{esc(payload['approval_phrases'].get(key) or 'not ready')}</code></td></tr>"
        for key in EXPECTED_ORDER
    )
    zip_rows = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in [
            ("Path", payload["release_zip"]["path"]),
            ("Exists", payload["release_zip"]["exists"]),
            ("File count", payload["release_zip"]["file_count"]),
            ("Size bytes", payload["release_zip"]["size_bytes"]),
            ("SHA256", payload["release_zip"]["sha256"]),
            ("Smoke status", payload["release_zip"]["smoke_status"]),
        ]
    )
    check_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['name'])}</td>"
        f"<td class=\"{'ready' if item['status'] == 'pass' else 'fail'}\">{esc(item['status'])}</td>"
        f"<td>{esc(item['detail'])}</td>"
        "</tr>"
        for item in payload["checks"]
    )
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td class=\"{'ready' if item['exists'] else 'fail'}\">{esc('present' if item['exists'] else 'missing')}</td>"
        f"<td>{esc(item['role'])}</td>"
        "</tr>"
        for item in payload["evidence"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Launch Snapshot</title>
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
    <h1>Public Launch Snapshot</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Snapshot</h2>
      <table><tbody>{summary_rows}</tbody></table>
      <p class="pending">{esc(payload['recommended_next_step'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Approval Phrases</h2>
      <table><thead><tr><th>Gate</th><th>Phrase</th></tr></thead><tbody>{approval_rows}</tbody></table>
    </section>
    <section>
      <h2>Release ZIP</h2>
      <table><tbody>{zip_rows}</tbody></table>
    </section>
    <section>
      <h2>Checks</h2>
      <table><thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead><tbody>{check_rows}</tbody></table>
    </section>
    <section>
      <h2>Evidence</h2>
      <table><thead><tr><th>Path</th><th>Status</th><th>Role</th></tr></thead><tbody>{evidence_rows}</tbody></table>
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
    write_json(reports / "latest_public_launch_snapshot.json", payload)
    (reports / "latest_public_launch_snapshot.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_public_launch_snapshot.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "failed_count": payload["failed_count"],
        "root_type": payload["root_type"],
        "html": "reports/latest_public_launch_snapshot.html",
        "markdown": "reports/latest_public_launch_snapshot.md",
        "json": "reports/latest_public_launch_snapshot.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local public launch snapshot before external approval.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
