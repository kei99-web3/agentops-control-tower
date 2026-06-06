from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_ORDER = [
    "public_github_repository",
    "public_demo_video",
    "optional_live_splunk_mcp_proof",
    "approved_url_writeback",
    "devpost_final_submission",
]

BOUNDARY = (
    "This audit checks local approval guidance only. It does not publish, upload, submit, "
    "create accounts, configure credentials, write approved URLs, or update Devpost."
)


@dataclass
class Check:
    key: str
    status: str
    evidence: str
    expected: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def add_check(checks: list[Check], key: str, condition: bool, evidence: str, expected: str) -> None:
    checks.append(Check(key=key, status="pass" if condition else "fail", evidence=evidence, expected=expected))


def load_state(root: Path) -> dict[str, Any]:
    return {
        "next_packet": read_json(root / "reports/latest_next_approval_packet.json"),
        "launch": read_json(root / "reports/latest_launch_decision_brief.json"),
        "external": read_json(root / "reports/latest_external_approval_packet.json"),
        "gate_ledger": read_json(root / "reports/latest_submission_gate_ledger.json"),
        "post_action": read_json(root / "reports/latest_post_action_evidence_brief.json"),
        "validation": read_json(root / "reports/latest_submission_validation.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
        "project_plan": read_text(root / "PROJECT_PLAN.md"),
        "user_approval_gates": read_text(root / "submission/USER_APPROVAL_GATES.md"),
        "next_packet_md": read_text(root / "submission/NEXT_APPROVAL_PACKET.md"),
    }


def approval_order_from_text(text: str) -> list[str]:
    lowered = text.lower()
    order = []
    phrases = {
        "public_github_repository": ["public github", "github repository"],
        "public_demo_video": ["public demo video", "demo video"],
        "optional_live_splunk_mcp_proof": ["optional live splunk", "optional splunk", "splunk/mcp", "splunk mcp", "splunk account"],
        "approved_url_writeback": ["approved url writeback", "url writeback", "replace pending url", "approved urls"],
        "devpost_final_submission": ["devpost final", "final devpost", "devpost submission"],
    }
    for key, candidates in phrases.items():
        indexes = [lowered.find(phrase) for phrase in candidates if lowered.find(phrase) >= 0]
        if indexes:
            order.append((min(indexes), key))
    return [key for _, key in sorted(order)]


def order_from_keys(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item) for item in values if str(item) in EXPECTED_ORDER]


def order_from_action_rows(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    order: list[str] = []
    for item in values:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key", ""))
        if key in EXPECTED_ORDER:
            order.append(key)
    return order


def section_after(text: str, heading: str) -> str:
    marker = heading.lower()
    lowered = text.lower()
    index = lowered.find(marker)
    if index < 0:
        return text
    section = text[index:]
    next_heading = section.find("\n## ", 1)
    return section if next_heading < 0 else section[:next_heading]


def build_checks(root: Path, state: dict[str, Any]) -> list[Check]:
    checks: list[Check] = []
    next_packet = state["next_packet"]
    launch = state["launch"]
    external = state["external"]
    gate_ledger = state["gate_ledger"]
    post_action = state["post_action"]
    validation = state["validation"]
    go_no_go = state["go_no_go"]
    url_validation = state["url_validation"]
    project_plan = state["project_plan"]
    user_gates = state["user_approval_gates"]
    next_packet_md = state["next_packet_md"]

    launch_order = launch.get("recommended_approval_order", [])
    next_order = next_packet.get("recommended_approval_order", [])
    gate_order = order_from_keys(gate_ledger.get("pending_gates", []))
    post_action_order = order_from_action_rows(post_action.get("actions", []))
    go_no_go_order = approval_order_from_text(" ".join(str(item) for item in go_no_go.get("recommended_order", [])))
    ready_now = set(next_packet.get("ready_now", []))
    ready_requests = set(external.get("ready_requests", []))
    external_request_keys = {str(item.get("key", "")) for item in external.get("approval_requests", [])}
    pending_external = set(validation.get("pending_external_actions", []))
    if not pending_external:
        pending_external = set(gate_ledger.get("pending_gates", []))
        if url_validation.get("pending_urls", []):
            pending_external.add("approved_url_writeback")
    pending_gates = set(gate_ledger.get("pending_gates", []))
    user_order = approval_order_from_text(section_after(user_gates, "## Recommended Approval Order"))
    public_candidate = is_public_candidate_root(root)

    add_check(
        checks,
        "next target is public repo",
        next_packet.get("next_approval_target") == "public_github_repository",
        str(next_packet.get("next_approval_target")),
        "public_github_repository",
    )
    add_check(
        checks,
        "ready now starts with repo and video",
        {"public_github_repository", "public_demo_video"}.issubset(ready_now),
        ", ".join(sorted(ready_now)),
        "public_github_repository and public_demo_video ready",
    )
    add_check(
        checks,
        "launch order matches expected order",
        launch_order[:5] == EXPECTED_ORDER,
        ", ".join(launch_order[:5]),
        ", ".join(EXPECTED_ORDER),
    )
    add_check(
        checks,
        "next packet order matches expected order",
        next_order[:5] == EXPECTED_ORDER,
        ", ".join(next_order[:5]),
        ", ".join(EXPECTED_ORDER),
    )
    add_check(
        checks,
        "gate ledger pending order matches expected order",
        gate_order[:5] == EXPECTED_ORDER,
        ", ".join(gate_order[:5]),
        ", ".join(EXPECTED_ORDER),
    )
    add_check(
        checks,
        "post-action evidence order matches expected order",
        post_action_order[:5] == EXPECTED_ORDER,
        ", ".join(post_action_order[:5]),
        ", ".join(EXPECTED_ORDER),
    )
    add_check(
        checks,
        "go/no-go order matches expected order",
        go_no_go_order[:5] == EXPECTED_ORDER,
        ", ".join(go_no_go_order[:5]),
        ", ".join(EXPECTED_ORDER),
    )
    add_check(
        checks,
        "external approval packet includes first gates",
        {"public_github_repository", "public_demo_video"}.issubset(external_request_keys),
        "requests=" + ", ".join(sorted(external_request_keys)) + " ready=" + ", ".join(sorted(ready_requests)),
        "public_github_repository and public_demo_video requests present",
    )
    add_check(
        checks,
        "pending actions remain external only",
        {"public_github_repository", "public_demo_video", "approved_url_writeback", "optional_live_splunk_mcp_proof", "devpost_final_submission"}.issubset(pending_external),
        ", ".join(sorted(pending_external)),
        "public repo, video, URL writeback, optional Splunk/MCP proof, Devpost",
    )
    add_check(
        checks,
        "gate ledger keeps external gates pending",
        {"public_github_repository", "public_demo_video", "optional_live_splunk_mcp_proof", "devpost_final_submission"}.issubset(pending_gates),
        ", ".join(sorted(pending_gates)),
        "public repo, video, optional Splunk/MCP proof, Devpost",
    )
    add_check(
        checks,
        "project plan current next gate",
        (public_candidate and not project_plan)
        or (
            "public GitHub publication and public demo video" in project_plan
            and "Approved URL writeback and Devpost final submission stay blocked" in project_plan
        ),
        "PROJECT_PLAN.md Next Gate" if project_plan else "not_applicable_public_candidate_root",
        "public repo/video first; URL writeback and Devpost blocked until public URLs",
    )
    add_check(
        checks,
        "project plan does not name Splunk setup as next material gate",
        (public_candidate and not project_plan)
        or "The next material gate is user approval for Splunk account/license" not in project_plan,
        "PROJECT_PLAN.md stale Splunk-first phrase scan" if project_plan else "not_applicable_public_candidate_root",
        "no stale Splunk-first next gate wording",
    )
    add_check(
        checks,
        "user approval gates order starts repo then video",
        user_order[:2] == ["public_github_repository", "public_demo_video"],
        ", ".join(user_order[:5]),
        "public_github_repository, public_demo_video",
    )
    add_check(
        checks,
        "user approval gates includes optional live proof after video",
        "Optionally approve live Splunk/MCP proof" in user_gates,
        "submission/USER_APPROVAL_GATES.md optional proof wording",
        "optional Splunk/MCP proof remains optional and post-video",
    )
    add_check(
        checks,
        "next approval markdown mirrors target and confirmations",
        "Next approval target: public_github_repository" in next_packet_md
        and "Human Confirmations Before Devpost" in next_packet_md
        and "age_and_residence" in next_packet_md,
        "submission/NEXT_APPROVAL_PACKET.md",
        "target plus human confirmations present",
    )
    add_check(
        checks,
        "final submit remains false",
        next_packet.get("final_submit_ready") is False
        and (validation.get("final_submit_ready") is False or (not validation and go_no_go.get("final_submit_ready") is False)),
        f"next={next_packet.get('final_submit_ready')} validation={validation.get('final_submit_ready')} go_no_go={go_no_go.get('final_submit_ready')}",
        "final_submit_ready false until public URLs and final approval",
    )
    return checks


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    checks = build_checks(root, state)
    failed = [check for check in checks if not check.passed]
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not failed else "needs_more_evidence",
        "root_type": "public_candidate" if is_public_candidate_root(root) else "workspace",
        "expected_order": EXPECTED_ORDER,
        "next_approval_target": state["next_packet"].get("next_approval_target", ""),
        "ready_now": state["next_packet"].get("ready_now", []),
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "recommended_next_step": "Use reports/latest_next_approval_packet.html before asking for or acting on any external approval.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Approval Consistency Audit",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Next approval target: {payload['next_approval_target']}",
        f"Ready now: {', '.join(payload['ready_now']) if payload['ready_now'] else 'none'}",
        f"Failed count: {payload['failed_count']}",
        "",
        "## Expected Approval Order",
        "",
    ]
    for index, item in enumerate(payload["expected_order"], start=1):
        lines.append(f"{index}. {item}")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        lines.extend(
            [
                f"### {check['key']}",
                "",
                f"Status: {check['status']}",
                f"Evidence: {check['evidence']}",
                f"Expected: {check['expected']}",
                "",
            ]
        )
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    order_rows = "\n".join(
        f"<tr><td>{esc(index)}</td><td>{esc(item)}</td></tr>"
        for index, item in enumerate(payload["expected_order"], start=1)
    )
    check_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['key'])}</td>"
        f"<td class=\"{'ready' if item['status'] == 'pass' else 'fail'}\">{esc(item['status'])}</td>"
        f"<td>{esc(item['evidence'])}</td>"
        f"<td>{esc(item['expected'])}</td>"
        "</tr>"
        for item in payload["checks"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Approval Consistency Audit</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; line-height: 1.58; }}
    header {{ background: #17202a; color: #fff; padding: 30px 38px 24px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: #5f6d7c; }}
    .ready {{ color: #127c76; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
    .pending {{ color: #a35b00; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Approval Consistency Audit</h1>
    <p>Status: <span class="{'ready' if payload['status'] == 'ready_for_user_review' else 'fail'}">{esc(payload['status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <p>Next approval target: <code>{esc(payload['next_approval_target'])}</code></p>
      <p>Ready now: {esc(', '.join(payload['ready_now']) if payload['ready_now'] else 'none')}</p>
      <p>Failed count: {esc(payload['failed_count'])}</p>
      <p class="pending">{esc(payload['boundary'])}</p>
    </section>
    <section>
      <h2>Expected Approval Order</h2>
      <table>
        <thead><tr><th>#</th><th>Gate</th></tr></thead>
        <tbody>{order_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Evidence</th><th>Expected</th></tr></thead>
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
    write_json(reports / "latest_approval_consistency_audit.json", payload)
    (reports / "latest_approval_consistency_audit.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_approval_consistency_audit.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "failed_count": payload["failed_count"],
        "next_approval_target": payload["next_approval_target"],
        "html": "reports/latest_approval_consistency_audit.html",
        "markdown": "reports/latest_approval_consistency_audit.md",
        "json": "reports/latest_approval_consistency_audit.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an approval consistency audit for the Splunk submission packet.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready_for_user_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
