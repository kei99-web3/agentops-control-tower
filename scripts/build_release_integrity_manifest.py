from __future__ import annotations

import argparse
import hashlib
import html
import json
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ZIP_PATH = "release/agentops-control-tower-public-candidate.zip"
SPLUNK_PACKAGE = "dist/agentops-control-tower-splunk-app.spl"
PUBLIC_CANDIDATE = "public_repo_candidate/agentops-control-tower"
BOUNDARY = (
    "This release integrity manifest is local readback evidence only. It does not publish, "
    "upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything."
)


@dataclass
class ArtifactSpec:
    title: str
    path: str
    role: str
    required: bool = True


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


def read_json(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def base_artifacts() -> list[ArtifactSpec]:
    return [
        ArtifactSpec("README", "README.md", "Portable project overview and local run instructions."),
        ArtifactSpec("License", "LICENSE", "Open-source license candidate for public review."),
        ArtifactSpec("Architecture diagram", "architecture_diagram.md", "Root architecture evidence required by the submission packet."),
        ArtifactSpec("Dashboard preview", "assets/dashboard_preview.png", "Visual README/Devpost preview asset."),
        ArtifactSpec("Local demo prototype", "prototype/agentops_control_tower.py", "Generator for synthetic checkout-incident events, analysis, dashboard, and SPL examples."),
        ArtifactSpec("Splunk-ready CSV", "data/splunk_agentops_events.csv", "Synthetic data export for a future agentops_events index after approval."),
        ArtifactSpec("SPL query pack", "submission/SPL_QUERIES.md", "Reviewer-facing SPL examples for the Control Tower flow."),
        ArtifactSpec("Splunk index config", "splunk_app/agentops_control_tower/default/indexes.conf", "Optional local index definition for agentops_events."),
        ArtifactSpec("Splunk sourcetype config", "splunk_app/agentops_control_tower/default/props.conf", "CSV extraction and timestamp parsing for the agentops:events sourcetype."),
        ArtifactSpec("Splunk app package", SPLUNK_PACKAGE, "Local .spl package candidate; not installed or uploaded."),
        ArtifactSpec("Splunk app package manifest", "reports/latest_splunk_app_package_manifest.html", "Members, SHA256, and package boundary evidence."),
        ArtifactSpec("Splunk app package manifest JSON", "reports/latest_splunk_app_package_manifest.json", "Machine-readable .spl integrity evidence."),
        ArtifactSpec("Splunk MCP command plan", "reports/latest_splunk_mcp_command_plan.html", "Post-approval live Splunk/MCP setup and proof command plan."),
        ArtifactSpec("Splunk MCP proof brief", "reports/latest_splunk_mcp_proof_brief.html", "Success criteria, screen safety, stop conditions, and claim-upgrade rules for optional live proof."),
        ArtifactSpec("Splunk MCP prompt pack", "reports/latest_splunk_mcp_prompt_pack.html", "Prompt-by-prompt live proof guide for evidence-backed MCP answers."),
        ArtifactSpec("Splunk MCP prompt pack JSON", "reports/latest_splunk_mcp_prompt_pack.json", "Machine-readable prompt keys, SPL, expected citations, and live-proof gates."),
        ArtifactSpec("Splunk MCP prompt pack Markdown", "reports/latest_splunk_mcp_prompt_pack.md", "Reviewable prompt pack for approved live proof capture."),
        ArtifactSpec("Splunk MCP prompt pack submission copy", "submission/SPLUNK_MCP_PROMPT_PACK.md", "Submission-side copy of the prompt pack and stop conditions."),
        ArtifactSpec("Claim evidence matrix", "reports/latest_claim_evidence_matrix.html", "Allowed wording, avoid wording, evidence, and remaining gates."),
        ArtifactSpec("Claim evidence matrix JSON", "reports/latest_claim_evidence_matrix.json", "Machine-readable claim support status."),
        ArtifactSpec("Submission gate ledger", "reports/latest_submission_gate_ledger.html", "Approval-gate ledger for public repo, video, live proof, and Devpost."),
        ArtifactSpec("Submission deadline burndown", "reports/latest_submission_deadline_burndown.html", "Deadline-aware path for public repo, video, optional live proof, URL writeback, and Devpost final submit."),
        ArtifactSpec("Submission deadline burndown JSON", "reports/latest_submission_deadline_burndown.json", "Machine-readable target date, official deadline, milestones, and blocked final submit gate."),
        ArtifactSpec("Submission deadline burndown Markdown", "reports/latest_submission_deadline_burndown.md", "Reviewable deadline burndown for local launch planning."),
        ArtifactSpec("Submission deadline burndown submission copy", "submission/SUBMISSION_DEADLINE_BURNDOWN.md", "Submission-side copy of the deadline burndown and approval timing path."),
        ArtifactSpec("Next approval packet", "reports/latest_next_approval_packet.html", "Next user approval target, approval phrases, risks, and verification steps."),
        ArtifactSpec("Next approval packet JSON", "reports/latest_next_approval_packet.json", "Machine-readable next approval status and human-confirmation gates."),
        ArtifactSpec("Next approval packet submission copy", "submission/NEXT_APPROVAL_PACKET.md", "Markdown copy of the next approval packet for final user decision support."),
        ArtifactSpec("Approval consistency audit", "reports/latest_approval_consistency_audit.html", "Checks approval order consistency across plan, approval gates, launch brief, next packet, and validator state."),
        ArtifactSpec("Approval consistency audit JSON", "reports/latest_approval_consistency_audit.json", "Machine-readable approval-order consistency status."),
        ArtifactSpec("Status conflict audit", "reports/latest_status_conflict_audit.html", "Scans root and public-candidate JSON reports for stale failed statuses or missing local artifacts.", required=False),
        ArtifactSpec("Status conflict audit JSON", "reports/latest_status_conflict_audit.json", "Machine-readable status conflict scan and critical ready-state checks.", required=False),
        ArtifactSpec("Status conflict audit Markdown", "reports/latest_status_conflict_audit.md", "Reviewable status conflict audit summary.", required=False),
        ArtifactSpec("Public launch snapshot", "reports/latest_public_launch_snapshot.html", "Frozen local snapshot for public repo and demo video approval review."),
        ArtifactSpec("Public launch snapshot JSON", "reports/latest_public_launch_snapshot.json", "Machine-readable public launch readiness, ZIP hash, approval phrases, and remaining gates."),
        ArtifactSpec("Public launch snapshot Markdown", "reports/latest_public_launch_snapshot.md", "Reviewable public launch snapshot for copy/paste and audit."),
        ArtifactSpec("Public repo metadata", "reports/latest_public_repo_metadata.html", "GitHub repository name, description, topics, expected readback, and no-publish boundary."),
        ArtifactSpec("Public repo metadata JSON", "reports/latest_public_repo_metadata.json", "Machine-readable public repository metadata and post-approval readback expectations."),
        ArtifactSpec("Public repo metadata Markdown", "reports/latest_public_repo_metadata.md", "Reviewable public repository metadata packet."),
        ArtifactSpec("Public repo metadata submission copy", "submission/PUBLIC_REPO_METADATA.md", "Submission-side copy of public repository metadata and stop conditions."),
        ArtifactSpec("User approval gates", "submission/USER_APPROVAL_GATES.md", "Human approval boundaries and current recommended approval order."),
        ArtifactSpec("Ready for review", "READY_FOR_REVIEW.md", "Shortest local review entrypoint for the current SPAK packet."),
        ArtifactSpec("SPAK judge review packet", "reports/latest_judge_review_packet.html", "Judge-facing local packet with readiness, evidence, and closed external gates."),
        ArtifactSpec("SPAK judge review packet JSON", "reports/latest_judge_review_packet.json", "Machine-readable SPAK judge packet status."),
        ArtifactSpec("SPAK judge review packet Markdown", "reports/latest_judge_review_packet.md", "Reviewable SPAK judge packet summary."),
        ArtifactSpec("SPAK judge review submission copy", "submission/JUDGE_REVIEW_PACKET.md", "Submission-side copy of the local judge review packet."),
        ArtifactSpec("Local readiness baseline", "reports/latest_local_readiness_baseline.html", "Targeted pass/fail baseline for local package/proof readiness."),
        ArtifactSpec("Local readiness baseline JSON", "reports/latest_local_readiness_baseline.json", "Machine-readable targeted local readiness baseline."),
        ArtifactSpec("Local readiness baseline Markdown", "reports/latest_local_readiness_baseline.md", "Reviewable targeted local readiness baseline."),
        ArtifactSpec("Public candidate local audit", "reports/latest_public_candidate_local_audit.html", "Secret/internal-path and completeness audit for the public repo candidate."),
        ArtifactSpec("Public candidate local audit JSON", "reports/latest_public_candidate_local_audit.json", "Machine-readable public candidate safety audit."),
        ArtifactSpec("Public candidate local audit Markdown", "reports/latest_public_candidate_local_audit.md", "Reviewable public candidate safety audit."),
        ArtifactSpec("Devpost copy audit", "reports/latest_devpost_copy_audit.html", "Local audit of Devpost copy readiness with final submission still gated."),
        ArtifactSpec("Devpost copy audit JSON", "reports/latest_devpost_copy_audit.json", "Machine-readable Devpost copy audit."),
        ArtifactSpec("Devpost copy audit Markdown", "reports/latest_devpost_copy_audit.md", "Reviewable Devpost copy audit."),
        ArtifactSpec("Judge quickstart", "reports/latest_judge_quickstart.html", "Five-minute review path for judges and final preflight."),
        ArtifactSpec("Devpost final copy", "reports/latest_devpost_final_copy.md", "Copy/paste packet with pending public URL placeholders."),
        ArtifactSpec("Post-action evidence brief", "reports/latest_post_action_evidence_brief.html", "Readback plan after approved external actions."),
        ArtifactSpec("Post-action evidence brief JSON", "reports/latest_post_action_evidence_brief.json", "Machine-readable post-action gate state."),
        ArtifactSpec("Post-action evidence log template", "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md", "Template for safe readback after approved external actions."),
        ArtifactSpec("Splunk MCP proof capture manifest", "reports/latest_splunk_mcp_proof_capture_manifest.html", "Live Splunk/MCP proof capture slots, expected readback, stop conditions, and claim-upgrade gate."),
        ArtifactSpec("Splunk MCP proof capture manifest JSON", "reports/latest_splunk_mcp_proof_capture_manifest.json", "Machine-readable live Splunk/MCP proof capture gate state."),
        ArtifactSpec("Splunk MCP proof capture manifest Markdown", "reports/latest_splunk_mcp_proof_capture_manifest.md", "Reviewable live Splunk/MCP proof capture manifest."),
        ArtifactSpec("Splunk MCP proof capture manifest submission copy", "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md", "Submission-side copy of the proof capture manifest and no-live-proof boundary."),
        ArtifactSpec("Official source freshness", "reports/latest_official_source_freshness.html", "Current official Devpost source and requirement freshness evidence."),
        ArtifactSpec("Official source freshness JSON", "reports/latest_official_source_freshness.json", "Machine-readable official source freshness and local mapping status."),
        ArtifactSpec("Content rights audit", "reports/latest_content_rights_audit.html", "License, bundled asset, audio/video, and screen-safety evidence."),
        ArtifactSpec("Content rights audit JSON", "reports/latest_content_rights_audit.json", "Machine-readable content rights and asset safety status."),
        ArtifactSpec("Eligibility compliance audit", "reports/latest_eligibility_compliance_audit.html", "Eligibility, ownership, language, uniqueness, and human-confirmation evidence."),
        ArtifactSpec("Eligibility compliance audit JSON", "reports/latest_eligibility_compliance_audit.json", "Machine-readable eligibility and compliance status."),
    ]


def workspace_artifacts() -> list[ArtifactSpec]:
    return [
        ArtifactSpec("Public candidate ZIP", ZIP_PATH, "Local ZIP for user review before public repo approval."),
        ArtifactSpec("Public candidate ZIP manifest", "reports/latest_public_candidate_zip_manifest.html", "ZIP content and publication boundary evidence."),
        ArtifactSpec("Public candidate ZIP manifest JSON", "reports/latest_public_candidate_zip_manifest.json", "Machine-readable ZIP file count and package metadata."),
        ArtifactSpec("Release ZIP smoke test", "reports/latest_release_zip_smoke_test.html", "Extract-and-test proof for the local ZIP."),
        ArtifactSpec("Release ZIP smoke test JSON", "reports/latest_release_zip_smoke_test.json", "Machine-readable smoke status and ZIP file count."),
        ArtifactSpec("Public candidate folder manifest", f"{PUBLIC_CANDIDATE}/PUBLIC_REPO_CANDIDATE_MANIFEST.md", "Clean local public-candidate staging boundary."),
        ArtifactSpec("Approval execution handoff", "reports/latest_approval_execution_handoff.html", "Private-workspace handoff for post-approval launch execution order, readbacks, and stop conditions."),
        ArtifactSpec("Approval execution handoff JSON", "reports/latest_approval_execution_handoff.json", "Machine-readable approval execution state and closed external-action boundary."),
        ArtifactSpec("Approval execution handoff Markdown", "reports/latest_approval_execution_handoff.md", "Reviewable approval execution handoff for interrupted sessions."),
        ArtifactSpec("Approval execution handoff submission copy", "submission/APPROVAL_EXECUTION_HANDOFF.md", "Submission-side copy of the local approval execution handoff."),
        ArtifactSpec("Live Splunk Docker proof", "reports/latest_live_splunk_docker_proof.html", "Private local proof that the synthetic CSV indexed and queried successfully in ephemeral Docker Splunk.", required=False),
        ArtifactSpec("Live Splunk Docker proof JSON", "reports/latest_live_splunk_docker_proof.json", "Machine-readable live Splunk query and local MCP SDK adapter readback; official Splunk MCP Server remains separate.", required=False),
        ArtifactSpec("Live Splunk Docker proof Markdown", "reports/latest_live_splunk_docker_proof.md", "Reviewable summary of the approved synthetic-only live Docker proof.", required=False),
        ArtifactSpec("Live Splunk Docker proof runner", "scripts/run_live_splunk_docker_proof.py", "Approved ephemeral Docker Splunk proof runner using synthetic data and read-only local MCP SDK adapter evidence.", required=False),
        ArtifactSpec("Public repo dry run", "reports/latest_public_repo_dry_run.html", "Isolated TEMP staging git-init/commit rehearsal for the clean public candidate before approval."),
        ArtifactSpec("Public repo dry run JSON", "reports/latest_public_repo_dry_run.json", "Machine-readable public repo rehearsal status, scans, and closed submission gates."),
        ArtifactSpec("Public repo dry run Markdown", "reports/latest_public_repo_dry_run.md", "Reviewable public repo rehearsal summary."),
        ArtifactSpec("Guarded public repo publication helper", "scripts/publish_public_repo_after_approval.py", "Default non-executing helper that can publish only after the exact approval phrase and public git identity are supplied."),
        ArtifactSpec("Demo video dry run", "reports/latest_video_dry_run.html", "Local recording rehearsal, timeline check, and screen-safety scan before approval."),
        ArtifactSpec("Demo video dry run JSON", "reports/latest_video_dry_run.json", "Machine-readable recording rehearsal status and closed video gates."),
        ArtifactSpec("Demo video dry run Markdown", "reports/latest_video_dry_run.md", "Reviewable recording rehearsal summary."),
        ArtifactSpec("Demo video recording preview", "reports/latest_video_recording_preview.html", "Local-only localhost preview preflight for recording from a public-candidate copy."),
        ArtifactSpec("Demo video recording preview JSON", "reports/latest_video_recording_preview.json", "Machine-readable recording preview status, temp-stage policy, and screen scan results."),
        ArtifactSpec("Demo video recording preview Markdown", "reports/latest_video_recording_preview.md", "Reviewable localhost recording preview summary."),
        ArtifactSpec("Video upload metadata", "reports/latest_video_upload_metadata.html", "Public demo video title, description, tags, visibility, readback expectations, and upload stop conditions."),
        ArtifactSpec("Video upload metadata JSON", "reports/latest_video_upload_metadata.json", "Machine-readable public demo video metadata and readback expectations."),
        ArtifactSpec("Video upload metadata Markdown", "reports/latest_video_upload_metadata.md", "Reviewable public demo video upload metadata packet."),
        ArtifactSpec("Video upload metadata submission copy", "submission/VIDEO_UPLOAD_METADATA.md", "Submission-side copy of public demo video metadata and stop conditions."),
        ArtifactSpec("Public video upload preflight", "reports/latest_public_video_upload_preflight.html", "Local-only preflight gate before public demo video recording/upload approval."),
        ArtifactSpec("Public video upload preflight JSON", "reports/latest_public_video_upload_preflight.json", "Machine-readable public video approval phrase, manual confirmation, and safe-readback gate."),
        ArtifactSpec("Public video upload preflight Markdown", "reports/latest_public_video_upload_preflight.md", "Reviewable public video upload preflight gate summary."),
        ArtifactSpec("Public artifact URL readback", "reports/latest_public_artifact_url_readback.html", "Post-publication repository/video URL readback gate before approved URL writeback."),
        ArtifactSpec("Public artifact URL readback JSON", "reports/latest_public_artifact_url_readback.json", "Machine-readable public URL shape/readback status and writeback readiness."),
        ArtifactSpec("Public artifact URL readback Markdown", "reports/latest_public_artifact_url_readback.md", "Reviewable public URL readback summary."),
        ArtifactSpec("URL writeback dry run", "reports/latest_url_writeback_dry_run.html", "Temporary-copy rehearsal for approved URL writeback and final-submit state changes."),
        ArtifactSpec("URL writeback dry run JSON", "reports/latest_url_writeback_dry_run.json", "Machine-readable URL writeback rehearsal status and working-tree write guard."),
        ArtifactSpec("URL writeback dry run Markdown", "reports/latest_url_writeback_dry_run.md", "Reviewable URL writeback rehearsal summary."),
    ]


def public_candidate_artifacts() -> list[ArtifactSpec]:
    return [
        ArtifactSpec("Public candidate manifest", "PUBLIC_REPO_CANDIDATE_MANIFEST.md", "Confirms this folder is the clean local public-candidate root."),
        ArtifactSpec("Candidate-local ZIP", ZIP_PATH, "Optional local ZIP generated inside the public candidate for review.", required=False),
        ArtifactSpec("Candidate-local ZIP manifest", "reports/latest_public_candidate_zip_manifest.json", "Optional machine-readable candidate ZIP manifest.", required=False),
    ]


def artifact_specs(root: Path) -> list[ArtifactSpec]:
    if is_public_candidate_root(root):
        return public_candidate_artifacts() + base_artifacts()
    return workspace_artifacts() + base_artifacts()


def artifact_to_dict(root: Path, spec: ArtifactSpec) -> dict[str, Any]:
    path = root / spec.path
    exists = path.exists()
    return {
        "title": spec.title,
        "path": spec.path,
        "role": spec.role,
        "required": spec.required,
        "exists": exists,
        "size_bytes": path.stat().st_size if exists and path.is_file() else 0,
        "sha256": sha256_file(path) if exists and path.is_file() else "",
    }


def zip_member_count(path: Path) -> int | None:
    if not path.exists():
        return None
    with zipfile.ZipFile(path) as archive:
        return len(archive.namelist())


def build_checks(root: Path, artifacts: list[dict[str, Any]], state: dict[str, Any]) -> list[Check]:
    checks: list[Check] = []
    public_candidate = is_public_candidate_root(root)
    missing_required = [item["path"] for item in artifacts if item["required"] and not item["exists"]]
    add_check(
        checks,
        "required artifacts present",
        not missing_required,
        "missing: " + ", ".join(missing_required) if missing_required else "all required artifacts present",
    )

    splunk_manifest = state["splunk_package"]
    splunk_artifact = next((item for item in artifacts if item["path"] == SPLUNK_PACKAGE), {})
    expected_sha = str(splunk_manifest.get("sha256", ""))
    actual_sha = str(splunk_artifact.get("sha256", ""))
    add_check(
        checks,
        "Splunk app package SHA256 consistency",
        bool(expected_sha) and expected_sha == actual_sha,
        f"manifest={expected_sha or 'missing'} artifact={actual_sha or 'missing'}",
    )
    add_check(
        checks,
        "Splunk app package manifest status",
        splunk_manifest.get("status") == "ready_for_user_review",
        str(splunk_manifest.get("status", "missing")),
    )
    prompt_pack = state["splunk_mcp_prompt_pack"]
    add_check(
        checks,
        "Splunk MCP prompt pack status",
        prompt_pack.get("status") == "ready_for_user_review"
        and prompt_pack.get("live_splunk_mcp_verified") is False
        and prompt_pack.get("external_actions_attempted") is False,
        f"status={prompt_pack.get('status', 'missing')} live={prompt_pack.get('live_splunk_mcp_verified', 'missing')} external={prompt_pack.get('external_actions_attempted', 'missing')}",
    )
    live_proof = state["live_splunk_docker_proof"]
    if live_proof:
        add_check(
            checks,
            "live Splunk Docker proof captured without official MCP overclaim",
            live_proof.get("live_splunk_verified") is True
            and int(live_proof.get("failed_query_count", 1)) == 0
            and live_proof.get("mcp_protocol_adapter_verified") is True
            and live_proof.get("official_splunk_mcp_server_verified") is False,
            (
                f"status={live_proof.get('status', 'missing')} "
                f"live={live_proof.get('live_splunk_verified', 'missing')} "
                f"adapter={live_proof.get('mcp_protocol_adapter_verified', 'missing')} "
                f"official={live_proof.get('official_splunk_mcp_server_verified', 'missing')} "
                f"failed_queries={live_proof.get('failed_query_count', 'missing')}"
            ),
        )

    claim_boundary = state["claim_boundary"]
    claim_boundary_ok = public_candidate or claim_boundary.get("status") == "pass"
    add_check(
        checks,
        "claim boundary status",
        claim_boundary_ok,
        "not_applicable_public_candidate_root" if public_candidate else str(claim_boundary.get("status", "missing")),
    )

    if public_candidate:
        add_check(checks, "release ZIP smoke status", True, "not_applicable_public_candidate_root")
        optional_zip = root / ZIP_PATH
        if optional_zip.exists():
            optional_manifest_count = state["zip_manifest"].get("file_count")
            actual_count = zip_member_count(optional_zip)
            count_ok = not isinstance(optional_manifest_count, int) or optional_manifest_count == actual_count
            add_check(
                checks,
                "candidate-local ZIP count consistency",
                count_ok,
                f"manifest={optional_manifest_count} actual={actual_count}",
            )
    else:
        smoke = state["release_smoke"]
        manifest = state["zip_manifest"]
        zip_file = root / ZIP_PATH
        actual_count = zip_member_count(zip_file)
        manifest_count = manifest.get("file_count")
        smoke_count = smoke.get("zip_file_count")
        add_check(checks, "release ZIP smoke status", smoke.get("status") == "pass", str(smoke.get("status", "missing")))
        count_values = [value for value in [actual_count, manifest_count, smoke_count] if isinstance(value, int)]
        add_check(
            checks,
            "release ZIP count consistency",
            len(count_values) >= 2 and len(set(count_values)) == 1,
            f"zip={actual_count} manifest={manifest_count} smoke={smoke_count}",
        )

    go_no_go = state["go_no_go"]
    url_validation = state["url_validation"]
    post_action = state["post_action"]
    final_submit_ready = bool(go_no_go.get("final_submit_ready", False)) or bool(url_validation.get("final_submit_ready", False))
    approved_urls_exists = (root / "submission/approved_public_urls.json").exists()
    pending_actions = post_action.get("incomplete_actions", [])
    add_check(checks, "final submit remains gated", not final_submit_ready, str(final_submit_ready))
    add_check(checks, "approved URLs remain gated", not approved_urls_exists, str(approved_urls_exists))
    add_check(
        checks,
        "post-action external gates tracked",
        isinstance(pending_actions, list) and len(pending_actions) >= 3,
        ", ".join(str(item) for item in pending_actions) if pending_actions else "missing",
    )
    add_check(
        checks,
        "publication boundary text",
        "does not publish" in BOUNDARY and "submit anything" in BOUNDARY,
        BOUNDARY,
    )
    if public_candidate:
        add_check(checks, "video dry run status", True, "not_applicable_public_candidate_root")
        add_check(checks, "public video upload preflight status", True, "not_applicable_public_candidate_root")
        add_check(checks, "URL writeback dry run status", True, "not_applicable_public_candidate_root")
    else:
        video_dry_run = state["video_dry_run"]
        add_check(
            checks,
            "video dry run status",
            video_dry_run.get("status") == "ready_for_recording_review" and int(video_dry_run.get("failed_count", 1)) == 0,
            f"status={video_dry_run.get('status', 'missing')} failed={video_dry_run.get('failed_count', 'missing')}",
        )
        video_upload_preflight = state["public_video_upload_preflight"]
        add_check(
            checks,
            "public video upload preflight status",
            video_upload_preflight.get("status") == "ready_for_user_review"
            and video_upload_preflight.get("public_video_upload_allowed") is False
            and video_upload_preflight.get("gate_status") == "blocked_by_video_approval_gate",
            f"status={video_upload_preflight.get('status', 'missing')} allowed={video_upload_preflight.get('public_video_upload_allowed', 'missing')} gate={video_upload_preflight.get('gate_status', 'missing')}",
        )
        url_dry_run = state["url_writeback_dry_run"]
        add_check(
            checks,
            "URL writeback dry run status",
            url_dry_run.get("status") == "ready_for_user_review"
            and int(url_dry_run.get("failed_count", 1)) == 0
            and url_dry_run.get("approved_public_urls_written_to_working_tree") is False,
            f"status={url_dry_run.get('status', 'missing')} failed={url_dry_run.get('failed_count', 'missing')} wrote={url_dry_run.get('approved_public_urls_written_to_working_tree', 'missing')}",
        )
    return checks


def load_state(root: Path) -> dict[str, Any]:
    return {
        "validation": read_json(root / "reports/latest_submission_validation.json"),
        "go_no_go": read_json(root / "reports/latest_final_go_no_go.json"),
        "url_validation": read_json(root / "reports/latest_submission_url_validation.json"),
        "zip_manifest": read_json(root / "reports/latest_public_candidate_zip_manifest.json"),
        "release_smoke": read_json(root / "reports/latest_release_zip_smoke_test.json"),
        "splunk_package": read_json(root / "reports/latest_splunk_app_package_manifest.json"),
        "splunk_mcp_prompt_pack": read_json(root / "reports/latest_splunk_mcp_prompt_pack.json"),
        "live_splunk_docker_proof": read_json(root / "reports/latest_live_splunk_docker_proof.json"),
        "claim_boundary": read_json(root / "reports/latest_claim_boundary_validation.json"),
        "post_action": read_json(root / "reports/latest_post_action_evidence_brief.json"),
        "video_dry_run": read_json(root / "reports/latest_video_dry_run.json"),
        "public_video_upload_preflight": read_json(root / "reports/latest_public_video_upload_preflight.json"),
        "url_writeback_dry_run": read_json(root / "reports/latest_url_writeback_dry_run.json"),
    }


def local_validation_snapshot(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    validation = state["validation"]
    go_no_go = state["go_no_go"]
    public_candidate = is_public_candidate_root(root)
    if validation:
        validation_status = validation.get("overall_status", "missing")
        validation_failed_count = validation.get("failed_count", "missing")
        if (
            validation_status == "needs_more_evidence"
            and go_no_go.get("status") == "ready_for_user_review"
            and go_no_go.get("local_ready") is True
            and go_no_go.get("missing_local_evidence", []) == []
            and go_no_go.get("missing_public_candidate_evidence", []) == []
        ):
            return {
                "status": "ready_for_user_review",
                "failed_count": 0,
                "source": "reports/latest_final_go_no_go.json",
                "note": "Resolved from final Go/No-Go because the full validator report is written after release-manifest refresh during validation.",
            }
        return {
            "status": validation_status,
            "failed_count": validation_failed_count,
            "source": "reports/latest_submission_validation.json",
            "note": "Full submission validator output.",
        }
    if (
        go_no_go.get("status") == "ready_for_user_review"
        and go_no_go.get("local_ready") is True
        and go_no_go.get("missing_local_evidence", []) == []
        and go_no_go.get("missing_public_candidate_evidence", []) == []
    ):
        return {
            "status": "ready_for_user_review",
            "failed_count": 0,
            "source": "reports/latest_final_go_no_go.json",
            "note": "Final Go/No-Go evidence is used because no full validator report is bundled yet.",
        }
    if public_candidate:
        return {
            "status": "not_bundled_public_candidate_root",
            "failed_count": "not_applicable_public_candidate_root",
            "source": "public_candidate_local_artifacts",
            "note": "Public candidate root can be validated from bundled local artifacts without a full workspace validator report.",
        }
    return {
        "status": "missing",
        "failed_count": "missing",
        "source": "missing",
        "note": "No validation or final Go/No-Go evidence was found.",
    }


def build_payload(root: Path) -> dict[str, Any]:
    state = load_state(root)
    artifacts = [artifact_to_dict(root, spec) for spec in artifact_specs(root)]
    checks = build_checks(root, artifacts, state)
    failed = [check for check in checks if not check.passed]
    public_candidate = is_public_candidate_root(root)
    zip_file = root / ZIP_PATH
    zip_count = zip_member_count(zip_file)
    validation = local_validation_snapshot(root, state)
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ready_for_user_review" if not failed else "needs_more_evidence",
        "root_type": "public_candidate" if public_candidate else "workspace",
        "validation_status": validation["status"],
        "validation_failed_count": validation["failed_count"],
        "validation_source": validation["source"],
        "validation_note": validation["note"],
        "final_submit_ready": bool(state["go_no_go"].get("final_submit_ready", False)),
        "approved_public_urls_exists": (root / "submission/approved_public_urls.json").exists(),
        "release_zip": {
            "path": ZIP_PATH,
            "exists": zip_file.exists(),
            "size_bytes": zip_file.stat().st_size if zip_file.exists() else 0,
            "sha256": sha256_file(zip_file) if zip_file.exists() else "",
            "file_count": zip_count,
            "smoke_status": "not_applicable_public_candidate_root" if public_candidate else state["release_smoke"].get("status", "missing"),
        },
        "splunk_app_package_status": state["splunk_package"].get("status", "missing"),
        "claim_boundary_status": "not_applicable_public_candidate_root" if public_candidate else state["claim_boundary"].get("status", "missing"),
        "artifact_count": len(artifacts),
        "missing_artifacts": [item["path"] for item in artifacts if item["required"] and not item["exists"]],
        "artifacts": artifacts,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "boundary": BOUNDARY,
        "recommended_next_step": "Review this manifest before approving public GitHub, public demo video, optional Splunk/MCP proof, URL writeback, or Devpost final submission.",
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def artifact_status_label(item: dict[str, Any]) -> str:
    if item["exists"]:
        return "present"
    if not item["required"]:
        return "not bundled"
    return "missing"


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Release Integrity Manifest",
        "",
        f"Status: {payload['status']}",
        f"Root type: {payload['root_type']}",
        f"Validation status: {payload['validation_status']}",
        f"Validation failed count: {payload['validation_failed_count']}",
        f"Validation source: {payload['validation_source']}",
        f"Artifact count: {payload['artifact_count']}",
        f"Final submit ready: {str(payload['final_submit_ready']).lower()}",
        "",
        "## Release ZIP",
        "",
        f"- Path: `{payload['release_zip']['path']}`",
        f"- Exists: {payload['release_zip']['exists']}",
        f"- File count: {payload['release_zip']['file_count']}",
        f"- Size bytes: {payload['release_zip']['size_bytes']}",
        f"- SHA256: `{payload['release_zip']['sha256']}`",
        f"- Smoke status: {payload['release_zip']['smoke_status']}",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        lines.append(f"- {check['name']}: {check['status']} ({check['detail']})")
    lines.extend(["", "## Artifact Integrity", ""])
    for item in payload["artifacts"]:
        status = artifact_status_label(item)
        required = "required" if item["required"] else "optional"
        lines.append(
            f"- `{item['path']}` ({status}, {required}) - size={item['size_bytes']} sha256=`{item['sha256']}` - {item['role']}"
        )
    lines.extend(["", "## Publication Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    summary_rows = "\n".join(
        f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>"
        for key, value in [
            ("Root type", payload["root_type"]),
            ("Validation status", payload["validation_status"]),
            ("Validation failed count", payload["validation_failed_count"]),
            ("Validation source", payload["validation_source"]),
            ("Validation note", payload["validation_note"]),
            ("Final submit ready", payload["final_submit_ready"]),
            ("Approved public URLs file", payload["approved_public_urls_exists"]),
            ("Splunk app package", payload["splunk_app_package_status"]),
            ("Claim boundary", payload["claim_boundary_status"]),
            ("Artifact count", payload["artifact_count"]),
            ("Missing artifacts", ", ".join(payload["missing_artifacts"]) if payload["missing_artifacts"] else "none"),
        ]
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
        f"<td>{esc(check['name'])}</td>"
        f"<td class=\"{'ready' if check['status'] == 'pass' else 'fail'}\">{esc(check['status'])}</td>"
        f"<td>{esc(check['detail'])}</td>"
        "</tr>"
        for check in payload["checks"]
    )
    artifact_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['title'])}</td>"
        f"<td><code>{esc(item['path'])}</code></td>"
        f"<td class=\"{'ready' if item['exists'] else ('pending' if not item['required'] else 'fail')}\">{esc(artifact_status_label(item))}</td>"
        f"<td>{esc('required' if item['required'] else 'optional')}</td>"
        f"<td>{esc(item['size_bytes'])}</td>"
        f"<td><code>{esc(item['sha256'])}</code></td>"
        f"<td>{esc(item['role'])}</td>"
        "</tr>"
        for item in payload["artifacts"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Release Integrity Manifest</title>
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
    <h1>Release Integrity Manifest</h1>
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
      <h2>Release ZIP</h2>
      <table><tbody>{zip_rows}</tbody></table>
    </section>
    <section>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{check_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Artifact Integrity</h2>
      <table>
        <thead><tr><th>Artifact</th><th>Path</th><th>Status</th><th>Required</th><th>Size</th><th>SHA256</th><th>Role</th></tr></thead>
        <tbody>{artifact_rows}</tbody>
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
    write_json(reports / "latest_release_integrity_manifest.json", payload)
    (reports / "latest_release_integrity_manifest.md").write_text(render_markdown(payload), encoding="utf-8")
    (reports / "latest_release_integrity_manifest.html").write_text(render_html(payload), encoding="utf-8")
    return {
        "status": payload["status"],
        "root_type": payload["root_type"],
        "artifact_count": payload["artifact_count"],
        "missing_artifacts": payload["missing_artifacts"],
        "failed_count": payload["failed_count"],
        "html": "reports/latest_release_integrity_manifest.html",
        "markdown": "reports/latest_release_integrity_manifest.md",
        "json": "reports/latest_release_integrity_manifest.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local release integrity manifest for the submission packet.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = run(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
