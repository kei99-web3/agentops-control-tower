from __future__ import annotations

import json
from pathlib import Path
from typing import Any


APPROVED_URLS_REL_PATH = "submission/approved_public_urls.json"

PENDING_REPO = "PENDING_USER_APPROVAL_PUBLIC_REPO_URL"
PENDING_VIDEO = "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL"

BASE_BUILT_WITH = ["Python", "Splunk", "SPL", "JSON", "CSV", "HTML"]
VERIFIED_SPLUNK_MCP_BUILT_WITH = ["Python", "Splunk", "SPL", "Splunk MCP Server", "JSON", "CSV", "HTML"]


DEFAULT_FIELD_VALUES = {
    "project_name": "Agentic Incident Command Center",
    "tagline": "Splunk-grounded AI incident commander with human-approved remediation.",
    "track": "Observability",
    "bonus_target": "Best Use of Splunk MCP Server",
    "built_with": BASE_BUILT_WITH,
    "repository_url": PENDING_REPO,
    "demo_video_url": PENDING_VIDEO,
}


def default_field_values() -> dict[str, Any]:
    fields = dict(DEFAULT_FIELD_VALUES)
    fields["built_with"] = list(BASE_BUILT_WITH)
    return fields


def approved_urls_path(root: Path) -> Path:
    return root / APPROVED_URLS_REL_PATH


def load_approved_urls(root: Path) -> dict[str, str]:
    path = approved_urls_path(root)
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    approved: dict[str, str] = {}
    for key in ["repository_url", "demo_video_url"]:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            approved[key] = value.strip()
    return approved


def live_splunk_mcp_verified(root: Path) -> bool:
    readback = root / "submission/post_action_evidence/2026-06-09_optional_live_splunk_mcp_proof_readback.md"
    if readback.exists():
        text = readback.read_text(encoding="utf-8")
        required_markers = [
            "Status: ready_for_claim_update",
            "MCP connection status: connected",
            "Tool used: `splunk_run_query`",
            "Official Splunk MCP Server was installed and verified",
        ]
        if all(marker in text for marker in required_markers):
            return True
    proof_paths = [
        root / "reports/latest_splunk_mcp_proof_capture_manifest.json",
        root / "reports/latest_splunk_mcp_prompt_pack.json",
    ]
    for path in proof_paths:
        if not path.exists():
            return False
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("live_splunk_mcp_verified") is not True:
            return False
    return True


def field_values_for(root: Path) -> dict[str, Any]:
    fields = default_field_values()
    if live_splunk_mcp_verified(root):
        fields["built_with"] = list(VERIFIED_SPLUNK_MCP_BUILT_WITH)
    fields.update(load_approved_urls(root))
    return fields


def approved_url_source(root: Path) -> str:
    return APPROVED_URLS_REL_PATH if approved_urls_path(root).exists() else "pending placeholders"
