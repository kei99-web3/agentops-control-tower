from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_REQUIRED = [
    ".gitattributes",
    "README.md",
    "LICENSE",
    "architecture_diagram.md",
    "assets/dashboard_preview.png",
    "prototype/agentops_control_tower.py",
    "scripts/build_approval_execution_handoff.py",
    "scripts/build_approval_consistency_audit.py",
    "scripts/build_demo_tour.py",
    "scripts/build_video_readiness_report.py",
    "scripts/build_video_command_plan.py",
    "scripts/build_video_cue_sheet.py",
    "scripts/build_video_dry_run.py",
    "scripts/build_video_recording_preview.py",
    "scripts/build_video_upload_metadata.py",
    "scripts/verify_public_video_upload_gate.py",
    "scripts/build_claim_evidence_matrix.py",
    "scripts/build_external_approval_packet.py",
    "scripts/build_devpost_submission_packet.py",
    "scripts/build_devpost_manual_fill_brief.py",
    "scripts/build_devpost_submit_command_plan.py",
    "scripts/verify_devpost_final_submit_gate.py",
    "scripts/build_final_go_no_go_report.py",
    "scripts/build_publication_command_plan.py",
    "scripts/build_public_repo_metadata.py",
    "scripts/build_public_repo_publish_brief.py",
    "scripts/build_public_repo_dry_run.py",
    "scripts/publish_public_repo_after_approval.py",
    "scripts/verify_public_repo_publication_gate.py",
    "scripts/build_public_launch_snapshot.py",
    "scripts/build_user_approval_brief_ja.py",
    "scripts/build_splunk_mcp_command_plan.py",
    "scripts/build_splunk_mcp_proof_brief.py",
    "scripts/build_splunk_mcp_prompt_pack.py",
    "scripts/build_splunk_mcp_proof_capture_manifest.py",
    "scripts/build_submission_gate_ledger.py",
    "scripts/build_submission_deadline_burndown.py",
    "scripts/build_submission_review_index.py",
    "scripts/build_judge_quickstart.py",
    "scripts/build_judge_scorecard.py",
    "scripts/build_spak_autonomous_review_packet.py",
    "scripts/build_launch_decision_brief.py",
    "scripts/build_next_approval_packet.py",
    "scripts/build_content_rights_audit.py",
    "scripts/build_eligibility_compliance_audit.py",
    "scripts/build_post_action_evidence_brief.py",
    "scripts/build_official_source_freshness.py",
    "scripts/build_url_writeback_dry_run.py",
    "scripts/build_release_integrity_manifest.py",
    "scripts/build_status_conflict_audit.py",
    "scripts/export_devpost_final_copy.py",
    "scripts/package_splunk_app.py",
    "scripts/build_public_repo_candidate.py",
    "scripts/package_public_candidate_zip.py",
    "scripts/prepare_submission_urls.py",
    "scripts/verify_public_artifact_urls.py",
    "scripts/run_local_spl_query_pack.py",
    "scripts/submission_urls.py",
    "scripts/smoke_test_release_zip.py",
    "scripts/validate_claim_boundaries.py",
    "scripts/validate_submission_urls.py",
    "scripts/validate_splunk_app.py",
    "scripts/validate_submission_packet.py",
    "tests/test_agentops_control_tower.py",
    "tests/test_submission_safety_boundaries.py",
    "data/agentops_event_schema.json",
    "data/splunk_agentops_events.csv",
    "dist/agentops-control-tower-splunk-app.spl",
    "reports/latest_control_tower.html",
    "reports/latest_approval_execution_handoff.html",
    "reports/latest_approval_execution_handoff.json",
    "reports/latest_approval_execution_handoff.md",
    "reports/latest_approval_consistency_audit.html",
    "reports/latest_approval_consistency_audit.json",
    "reports/latest_approval_consistency_audit.md",
    "reports/latest_claim_evidence_matrix.html",
    "reports/latest_claim_evidence_matrix.json",
    "reports/latest_claim_evidence_matrix.md",
    "reports/latest_claim_boundary_validation.html",
    "reports/latest_claim_boundary_validation.json",
    "reports/latest_devpost_final_copy.html",
    "reports/latest_devpost_final_copy.json",
    "reports/latest_devpost_final_copy.md",
    "reports/latest_devpost_submit_command_plan.html",
    "reports/latest_devpost_submit_command_plan.json",
    "reports/latest_devpost_submit_command_plan.md",
    "reports/latest_devpost_final_submit_preflight.html",
    "reports/latest_devpost_final_submit_preflight.json",
    "reports/latest_devpost_final_submit_preflight.md",
    "reports/latest_devpost_manual_fill_brief.html",
    "reports/latest_devpost_manual_fill_brief.json",
    "reports/latest_devpost_manual_fill_brief.md",
    "reports/latest_demo_tour.html",
    "reports/latest_video_readiness.html",
    "reports/latest_video_readiness.json",
    "reports/latest_video_command_plan.html",
    "reports/latest_video_command_plan.json",
    "reports/latest_video_command_plan.md",
    "reports/latest_video_recording_preview.html",
    "reports/latest_video_recording_preview.json",
    "reports/latest_video_recording_preview.md",
    "reports/latest_video_upload_metadata.html",
    "reports/latest_video_upload_metadata.json",
    "reports/latest_video_upload_metadata.md",
    "reports/latest_public_video_upload_preflight.html",
    "reports/latest_public_video_upload_preflight.json",
    "reports/latest_public_video_upload_preflight.md",
    "reports/latest_video_cue_sheet.html",
    "reports/latest_video_cue_sheet.json",
    "reports/latest_video_cue_sheet.md",
    "reports/latest_external_approval_packet.html",
    "reports/latest_external_approval_packet.json",
    "reports/latest_external_approval_packet.md",
    "reports/latest_submission_url_apply_plan.html",
    "reports/latest_submission_url_apply_plan.json",
    "reports/latest_submission_url_apply_plan.md",
    "reports/latest_public_artifact_url_readback.html",
    "reports/latest_public_artifact_url_readback.json",
    "reports/latest_public_artifact_url_readback.md",
    "reports/latest_publication_command_plan.html",
    "reports/latest_publication_command_plan.json",
    "reports/latest_publication_command_plan.md",
    "reports/latest_public_repo_metadata.html",
    "reports/latest_public_repo_metadata.json",
    "reports/latest_public_repo_metadata.md",
    "reports/latest_public_repo_publish_brief.html",
    "reports/latest_public_repo_publish_brief.json",
    "reports/latest_public_repo_publish_brief.md",
    "reports/latest_public_repo_publication_preflight.html",
    "reports/latest_public_repo_publication_preflight.json",
    "reports/latest_public_repo_publication_preflight.md",
    "reports/latest_public_launch_snapshot.html",
    "reports/latest_public_launch_snapshot.json",
    "reports/latest_public_launch_snapshot.md",
    "reports/latest_user_approval_brief_ja.html",
    "reports/latest_user_approval_brief_ja.json",
    "reports/latest_user_approval_brief_ja.md",
    "reports/latest_splunk_mcp_command_plan.html",
    "reports/latest_splunk_mcp_command_plan.json",
    "reports/latest_splunk_mcp_command_plan.md",
    "reports/latest_splunk_mcp_proof_brief.html",
    "reports/latest_splunk_mcp_proof_brief.json",
    "reports/latest_splunk_mcp_proof_brief.md",
    "reports/latest_splunk_mcp_prompt_pack.html",
    "reports/latest_splunk_mcp_prompt_pack.json",
    "reports/latest_splunk_mcp_prompt_pack.md",
    "reports/latest_splunk_mcp_proof_capture_manifest.html",
    "reports/latest_splunk_mcp_proof_capture_manifest.json",
    "reports/latest_splunk_mcp_proof_capture_manifest.md",
    "reports/latest_submission_gate_ledger.html",
    "reports/latest_submission_gate_ledger.json",
    "reports/latest_submission_gate_ledger.md",
    "reports/latest_submission_deadline_burndown.html",
    "reports/latest_submission_deadline_burndown.json",
    "reports/latest_submission_deadline_burndown.md",
    "reports/latest_submission_review_index.html",
    "reports/latest_submission_review_index.json",
    "reports/latest_submission_review_index.md",
    "reports/latest_judge_quickstart.html",
    "reports/latest_judge_quickstart.json",
    "reports/latest_judge_quickstart.md",
    "reports/latest_judge_review_packet.html",
    "reports/latest_judge_review_packet.json",
    "reports/latest_judge_review_packet.md",
    "reports/latest_judge_scorecard.html",
    "reports/latest_judge_scorecard.json",
    "reports/latest_judge_scorecard.md",
    "reports/latest_local_readiness_baseline.html",
    "reports/latest_local_readiness_baseline.json",
    "reports/latest_local_readiness_baseline.md",
    "reports/latest_public_candidate_local_audit.html",
    "reports/latest_public_candidate_local_audit.json",
    "reports/latest_public_candidate_local_audit.md",
    "reports/latest_devpost_copy_audit.html",
    "reports/latest_devpost_copy_audit.json",
    "reports/latest_devpost_copy_audit.md",
    "reports/latest_launch_decision_brief.html",
    "reports/latest_launch_decision_brief.json",
    "reports/latest_launch_decision_brief.md",
    "reports/latest_next_approval_packet.html",
    "reports/latest_next_approval_packet.json",
    "reports/latest_next_approval_packet.md",
    "reports/latest_content_rights_audit.html",
    "reports/latest_content_rights_audit.json",
    "reports/latest_content_rights_audit.md",
    "reports/latest_eligibility_compliance_audit.html",
    "reports/latest_eligibility_compliance_audit.json",
    "reports/latest_eligibility_compliance_audit.md",
    "reports/latest_post_action_evidence_brief.html",
    "reports/latest_post_action_evidence_brief.json",
    "reports/latest_post_action_evidence_brief.md",
    "reports/latest_official_source_freshness.html",
    "reports/latest_official_source_freshness.json",
    "reports/latest_official_source_freshness.md",
    "reports/latest_release_integrity_manifest.html",
    "reports/latest_release_integrity_manifest.json",
    "reports/latest_release_integrity_manifest.md",
    "reports/latest_status_conflict_audit.html",
    "reports/latest_status_conflict_audit.json",
    "reports/latest_status_conflict_audit.md",
    "reports/latest_devpost_submission_packet.html",
    "reports/latest_devpost_submission_packet.json",
    "reports/latest_final_go_no_go.html",
    "reports/latest_final_go_no_go.json",
    "reports/latest_local_spl_query_results.html",
    "reports/latest_local_spl_query_results.json",
    "reports/latest_mcp_investigation.md",
    "reports/latest_submission_url_validation.html",
    "reports/latest_submission_url_validation.json",
    "reports/latest_splunk_app_package_manifest.html",
    "reports/latest_splunk_app_package_manifest.json",
    "reports/latest_splunk_app_package_manifest.md",
    "submission/DEMO_VIDEO_SCRIPT.md",
    "submission/APPROVAL_EXECUTION_HANDOFF.md",
    "submission/DEVPOST_FIELD_MAP.md",
    "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md",
    "submission/DEVPOST_SUBMISSION_DRAFT.md",
    "submission/FINAL_SUBMISSION_CHECKLIST.md",
    "submission/HUMAN_CONFIRMATION_CHECKLIST.md",
    "submission/JUDGE_REVIEW_PACKET.md",
    "submission/JUDGING_ALIGNMENT.md",
    "submission/NEXT_APPROVAL_PACKET.md",
    "submission/OFFICIAL_REQUIREMENTS_AUDIT.md",
    "submission/PUBLIC_REPO_READINESS.md",
    "submission/SPL_QUERIES.md",
    "submission/SPLUNK_MCP_RUNBOOK.md",
    "submission/SPLUNK_MCP_PROMPT_PACK.md",
    "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md",
    "submission/SUBMISSION_DEADLINE_BURNDOWN.md",
    "submission/SUBMISSION_LAUNCH_RUNBOOK.md",
    "submission/SUBMISSION_REVIEW_QA.md",
    "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md",
    "submission/PUBLIC_REPO_METADATA.md",
    "submission/VIDEO_UPLOAD_METADATA.md",
    "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
    "submission/USER_APPROVAL_GATES.md",
    "submission/VIDEO_RECORDING_RUNBOOK.md",
    "READY_FOR_REVIEW.md",
    "splunk_app/agentops_control_tower/README.md",
    "splunk_app/agentops_control_tower/default/app.conf",
    "splunk_app/agentops_control_tower/default/indexes.conf",
    "splunk_app/agentops_control_tower/default/props.conf",
    "splunk_app/agentops_control_tower/default/savedsearches.conf",
    "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
    "splunk_app/agentops_control_tower/metadata/default.meta",
]

PUBLIC_REQUIRED = [
    ".gitattributes",
    "README.md",
    "LICENSE",
    "architecture_diagram.md",
    "assets/dashboard_preview.png",
    "prototype/agentops_control_tower.py",
    "scripts/build_approval_consistency_audit.py",
    "scripts/build_demo_tour.py",
    "scripts/build_video_readiness_report.py",
    "scripts/build_video_command_plan.py",
    "scripts/build_video_cue_sheet.py",
    "scripts/build_video_dry_run.py",
    "scripts/build_video_recording_preview.py",
    "scripts/build_video_upload_metadata.py",
    "scripts/verify_public_video_upload_gate.py",
    "scripts/build_claim_evidence_matrix.py",
    "scripts/build_external_approval_packet.py",
    "scripts/build_devpost_submission_packet.py",
    "scripts/build_devpost_manual_fill_brief.py",
    "scripts/build_devpost_submit_command_plan.py",
    "scripts/verify_devpost_final_submit_gate.py",
    "scripts/build_final_go_no_go_report.py",
    "scripts/build_publication_command_plan.py",
    "scripts/build_public_repo_metadata.py",
    "scripts/build_public_repo_publish_brief.py",
    "scripts/build_public_repo_dry_run.py",
    "scripts/publish_public_repo_after_approval.py",
    "scripts/verify_public_repo_publication_gate.py",
    "scripts/build_public_launch_snapshot.py",
    "scripts/build_splunk_mcp_command_plan.py",
    "scripts/build_splunk_mcp_proof_brief.py",
    "scripts/build_splunk_mcp_prompt_pack.py",
    "scripts/build_splunk_mcp_proof_capture_manifest.py",
    "scripts/build_submission_gate_ledger.py",
    "scripts/build_submission_deadline_burndown.py",
    "scripts/build_submission_review_index.py",
    "scripts/build_judge_quickstart.py",
    "scripts/build_judge_scorecard.py",
    "scripts/build_spak_autonomous_review_packet.py",
    "scripts/build_launch_decision_brief.py",
    "scripts/build_next_approval_packet.py",
    "scripts/build_content_rights_audit.py",
    "scripts/build_eligibility_compliance_audit.py",
    "scripts/build_post_action_evidence_brief.py",
    "scripts/build_official_source_freshness.py",
    "scripts/build_url_writeback_dry_run.py",
    "scripts/build_release_integrity_manifest.py",
    "scripts/build_status_conflict_audit.py",
    "scripts/export_devpost_final_copy.py",
    "scripts/package_splunk_app.py",
    "scripts/package_public_candidate_zip.py",
    "scripts/prepare_submission_urls.py",
    "scripts/verify_public_artifact_urls.py",
    "scripts/run_local_spl_query_pack.py",
    "scripts/submission_urls.py",
    "scripts/smoke_test_release_zip.py",
    "scripts/validate_claim_boundaries.py",
    "scripts/validate_submission_urls.py",
    "scripts/validate_splunk_app.py",
    "scripts/validate_submission_packet.py",
    "tests/test_agentops_control_tower.py",
    "tests/test_submission_safety_boundaries.py",
    "data/agentops_event_schema.json",
    "data/splunk_agentops_events.csv",
    "dist/agentops-control-tower-splunk-app.spl",
    "reports/latest_control_tower.html",
    "reports/latest_approval_consistency_audit.html",
    "reports/latest_approval_consistency_audit.json",
    "reports/latest_approval_consistency_audit.md",
    "reports/latest_claim_evidence_matrix.html",
    "reports/latest_claim_evidence_matrix.json",
    "reports/latest_claim_evidence_matrix.md",
    "reports/latest_claim_boundary_validation.html",
    "reports/latest_claim_boundary_validation.json",
    "reports/latest_devpost_final_copy.html",
    "reports/latest_devpost_final_copy.json",
    "reports/latest_devpost_final_copy.md",
    "reports/latest_devpost_submit_command_plan.html",
    "reports/latest_devpost_submit_command_plan.json",
    "reports/latest_devpost_submit_command_plan.md",
    "reports/latest_devpost_final_submit_preflight.html",
    "reports/latest_devpost_final_submit_preflight.json",
    "reports/latest_devpost_final_submit_preflight.md",
    "reports/latest_devpost_manual_fill_brief.html",
    "reports/latest_devpost_manual_fill_brief.json",
    "reports/latest_devpost_manual_fill_brief.md",
    "reports/latest_demo_tour.html",
    "reports/latest_video_readiness.html",
    "reports/latest_video_readiness.json",
    "reports/latest_video_command_plan.html",
    "reports/latest_video_command_plan.json",
    "reports/latest_video_command_plan.md",
    "reports/latest_video_recording_preview.html",
    "reports/latest_video_recording_preview.json",
    "reports/latest_video_recording_preview.md",
    "reports/latest_video_upload_metadata.html",
    "reports/latest_video_upload_metadata.json",
    "reports/latest_video_upload_metadata.md",
    "reports/latest_public_video_upload_preflight.html",
    "reports/latest_public_video_upload_preflight.json",
    "reports/latest_public_video_upload_preflight.md",
    "reports/latest_video_cue_sheet.html",
    "reports/latest_video_cue_sheet.json",
    "reports/latest_video_cue_sheet.md",
    "reports/latest_external_approval_packet.html",
    "reports/latest_external_approval_packet.json",
    "reports/latest_external_approval_packet.md",
    "reports/latest_submission_url_apply_plan.html",
    "reports/latest_submission_url_apply_plan.json",
    "reports/latest_submission_url_apply_plan.md",
    "reports/latest_public_artifact_url_readback.html",
    "reports/latest_public_artifact_url_readback.json",
    "reports/latest_public_artifact_url_readback.md",
    "reports/latest_publication_command_plan.html",
    "reports/latest_publication_command_plan.json",
    "reports/latest_publication_command_plan.md",
    "reports/latest_public_repo_metadata.html",
    "reports/latest_public_repo_metadata.json",
    "reports/latest_public_repo_metadata.md",
    "reports/latest_public_repo_publish_brief.html",
    "reports/latest_public_repo_publish_brief.json",
    "reports/latest_public_repo_publish_brief.md",
    "reports/latest_public_repo_publication_preflight.html",
    "reports/latest_public_repo_publication_preflight.json",
    "reports/latest_public_repo_publication_preflight.md",
    "reports/latest_public_launch_snapshot.html",
    "reports/latest_public_launch_snapshot.json",
    "reports/latest_public_launch_snapshot.md",
    "reports/latest_splunk_mcp_command_plan.html",
    "reports/latest_splunk_mcp_command_plan.json",
    "reports/latest_splunk_mcp_command_plan.md",
    "reports/latest_splunk_mcp_proof_brief.html",
    "reports/latest_splunk_mcp_proof_brief.json",
    "reports/latest_splunk_mcp_proof_brief.md",
    "reports/latest_splunk_mcp_prompt_pack.html",
    "reports/latest_splunk_mcp_prompt_pack.json",
    "reports/latest_splunk_mcp_prompt_pack.md",
    "reports/latest_splunk_mcp_proof_capture_manifest.html",
    "reports/latest_splunk_mcp_proof_capture_manifest.json",
    "reports/latest_splunk_mcp_proof_capture_manifest.md",
    "reports/latest_submission_gate_ledger.html",
    "reports/latest_submission_gate_ledger.json",
    "reports/latest_submission_gate_ledger.md",
    "reports/latest_submission_deadline_burndown.html",
    "reports/latest_submission_deadline_burndown.json",
    "reports/latest_submission_deadline_burndown.md",
    "reports/latest_submission_review_index.html",
    "reports/latest_submission_review_index.json",
    "reports/latest_submission_review_index.md",
    "reports/latest_judge_quickstart.html",
    "reports/latest_judge_quickstart.json",
    "reports/latest_judge_quickstart.md",
    "reports/latest_judge_review_packet.html",
    "reports/latest_judge_review_packet.json",
    "reports/latest_judge_review_packet.md",
    "reports/latest_judge_scorecard.html",
    "reports/latest_judge_scorecard.json",
    "reports/latest_judge_scorecard.md",
    "reports/latest_local_readiness_baseline.html",
    "reports/latest_local_readiness_baseline.json",
    "reports/latest_local_readiness_baseline.md",
    "reports/latest_public_candidate_local_audit.html",
    "reports/latest_public_candidate_local_audit.json",
    "reports/latest_public_candidate_local_audit.md",
    "reports/latest_devpost_copy_audit.html",
    "reports/latest_devpost_copy_audit.json",
    "reports/latest_devpost_copy_audit.md",
    "reports/latest_launch_decision_brief.html",
    "reports/latest_launch_decision_brief.json",
    "reports/latest_launch_decision_brief.md",
    "reports/latest_next_approval_packet.html",
    "reports/latest_next_approval_packet.json",
    "reports/latest_next_approval_packet.md",
    "reports/latest_content_rights_audit.html",
    "reports/latest_content_rights_audit.json",
    "reports/latest_content_rights_audit.md",
    "reports/latest_eligibility_compliance_audit.html",
    "reports/latest_eligibility_compliance_audit.json",
    "reports/latest_eligibility_compliance_audit.md",
    "reports/latest_post_action_evidence_brief.html",
    "reports/latest_post_action_evidence_brief.json",
    "reports/latest_post_action_evidence_brief.md",
    "reports/latest_official_source_freshness.html",
    "reports/latest_official_source_freshness.json",
    "reports/latest_official_source_freshness.md",
    "reports/latest_release_integrity_manifest.html",
    "reports/latest_release_integrity_manifest.json",
    "reports/latest_release_integrity_manifest.md",
    "reports/latest_status_conflict_audit.html",
    "reports/latest_status_conflict_audit.json",
    "reports/latest_status_conflict_audit.md",
    "reports/latest_devpost_submission_packet.html",
    "reports/latest_devpost_submission_packet.json",
    "reports/latest_final_go_no_go.html",
    "reports/latest_final_go_no_go.json",
    "reports/latest_local_spl_query_results.html",
    "reports/latest_local_spl_query_results.json",
    "reports/latest_mcp_investigation.md",
    "reports/latest_submission_url_validation.html",
    "reports/latest_submission_url_validation.json",
    "reports/latest_splunk_app_package_manifest.html",
    "reports/latest_splunk_app_package_manifest.json",
    "reports/latest_splunk_app_package_manifest.md",
    "submission/DEMO_VIDEO_SCRIPT.md",
    "submission/DEVPOST_FIELD_MAP.md",
    "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md",
    "submission/DEVPOST_SUBMISSION_DRAFT.md",
    "submission/FINAL_SUBMISSION_CHECKLIST.md",
    "submission/HUMAN_CONFIRMATION_CHECKLIST.md",
    "submission/JUDGE_REVIEW_PACKET.md",
    "submission/JUDGING_ALIGNMENT.md",
    "submission/NEXT_APPROVAL_PACKET.md",
    "submission/OFFICIAL_REQUIREMENTS_AUDIT.md",
    "submission/REQUIREMENTS_MATRIX.md",
    "submission/SPL_QUERIES.md",
    "submission/SPLUNK_MCP_RUNBOOK.md",
    "submission/SPLUNK_MCP_PROMPT_PACK.md",
    "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md",
    "submission/SUBMISSION_DEADLINE_BURNDOWN.md",
    "submission/SUBMISSION_LAUNCH_RUNBOOK.md",
    "submission/SUBMISSION_REVIEW_QA.md",
    "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md",
    "submission/PUBLIC_REPO_METADATA.md",
    "submission/VIDEO_UPLOAD_METADATA.md",
    "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
    "submission/USER_APPROVAL_GATES.md",
    "submission/VIDEO_RECORDING_RUNBOOK.md",
    "READY_FOR_REVIEW.md",
    "splunk_app/agentops_control_tower/README.md",
    "splunk_app/agentops_control_tower/default/app.conf",
    "splunk_app/agentops_control_tower/default/indexes.conf",
    "splunk_app/agentops_control_tower/default/props.conf",
    "splunk_app/agentops_control_tower/default/savedsearches.conf",
    "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
    "splunk_app/agentops_control_tower/metadata/default.meta",
    "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
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
    ]
]

CHECKLIST_SYNC_SCRIPTS = [
    "scripts/build_approval_execution_handoff.py",
    "scripts/build_public_repo_metadata.py",
    "scripts/build_public_repo_dry_run.py",
    "scripts/build_submission_deadline_burndown.py",
    "scripts/build_splunk_mcp_proof_capture_manifest.py",
    "scripts/build_status_conflict_audit.py",
    "scripts/build_url_writeback_dry_run.py",
    "scripts/build_user_approval_brief_ja.py",
    "scripts/build_video_dry_run.py",
    "scripts/build_video_recording_preview.py",
    "scripts/build_video_upload_metadata.py",
    "scripts/publish_public_repo_after_approval.py",
    "scripts/verify_public_artifact_urls.py",
]

ABSOLUTE_PATH_PATTERN = re.compile(r"[A-Za-z]:\\[^\n\r\"']+")

EXTERNAL_ACTION_ORDER = [
    "public_github_repository",
    "public_demo_video",
    "approved_url_writeback",
    "devpost_final_submission",
]


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=detail))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(name: str, args: list[str], cwd: Path, checks: list[Check]) -> None:
    completed = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    output = (completed.stdout + "\n" + completed.stderr).strip()
    detail = sanitize_detail(output[-600:] if output else "no output")
    add_check(checks, name, completed.returncode == 0, detail)


def cleanup_public_candidate_package_artifacts(candidate: Path, checks: list[Check]) -> None:
    candidate_root = candidate.resolve()
    target_rels = [
        "release",
        "reports/latest_public_candidate_zip_manifest.html",
        "reports/latest_public_candidate_zip_manifest.json",
    ]
    removed: list[str] = []
    for rel_path in target_rels:
        path = (candidate / rel_path).resolve()
        path.relative_to(candidate_root)
        if not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        removed.append(rel_path)
    detail = "removed: " + ", ".join(removed) if removed else "no generated package artifacts present"
    add_check(checks, "public candidate generated package cleanup", True, detail)


def sanitize_detail(value: str) -> str:
    return ABSOLUTE_PATH_PATTERN.sub("<local-path>", value)


def remove_pycache(root: Path) -> None:
    for path in root.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)


def read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_pending_urls(value: Any) -> list[str]:
    if isinstance(value, dict):
        return sorted(str(key) for key in value)
    if isinstance(value, list):
        return sorted(str(item) for item in value)
    return []


def order_external_actions(values: list[str]) -> list[str]:
    seen = set(values)
    ordered = [item for item in EXTERNAL_ACTION_ORDER if item in seen]
    ordered.extend(item for item in values if item not in EXTERNAL_ACTION_ORDER)
    return ordered


def build_submission_gate_summary(root: Path, local_checks_passed: bool) -> dict[str, Any]:
    go_no_go = read_optional_json(root / "reports/latest_final_go_no_go.json")
    url_validation = read_optional_json(root / "reports/latest_submission_url_validation.json")
    post_action = read_optional_json(root / "reports/latest_post_action_evidence_brief.json")
    gate_ledger = read_optional_json(root / "reports/latest_submission_gate_ledger.json")

    pending_urls = normalize_pending_urls(url_validation.get("pending_urls") or go_no_go.get("pending_urls"))
    pending_external_actions = [
        str(item)
        for item in (post_action.get("incomplete_actions") or gate_ledger.get("pending_gates") or [])
    ]
    pending_external_actions = order_external_actions(pending_external_actions)
    external_gates = [
        str(item)
        for item in (
            go_no_go.get("external_gates_pending")
            or gate_ledger.get("pending_gates")
            or pending_external_actions
        )
    ]
    approved_public_urls_exists = (root / "submission/approved_public_urls.json").exists()
    final_submit_ready = (
        local_checks_passed
        and bool(go_no_go.get("final_submit_ready", False))
        and bool(url_validation.get("final_submit_ready", False))
    )
    if not local_checks_passed:
        next_action = "Fix failed local checks before asking for external approval."
    elif final_submit_ready:
        next_action = "Ask for explicit final Devpost submit approval and use the post-action evidence brief for readback."
    elif pending_urls:
        next_action = "Ask user for public repo/video approval, then write approved URLs only after both are verified."
    else:
        next_action = "Ask user for remaining external approval before Devpost submission."

    return {
        "local_checks_passed": local_checks_passed,
        "final_submit_ready": final_submit_ready,
        "approved_public_urls_exists": approved_public_urls_exists,
        "url_validation_status": url_validation.get("status", "missing"),
        "pending_urls": pending_urls,
        "post_action_evidence_ready": bool(post_action.get("post_action_evidence_ready", False)),
        "pending_external_actions": pending_external_actions,
        "external_gates_pending": external_gates,
        "next_action": next_action,
        "evidence_sources": {
            "final_go_no_go": "reports/latest_final_go_no_go.json",
            "submission_url_validation": "reports/latest_submission_url_validation.json",
            "post_action_evidence_brief": "reports/latest_post_action_evidence_brief.json",
            "submission_gate_ledger": "reports/latest_submission_gate_ledger.json",
        },
        "boundary": (
            "Validation metadata is local readback only. It does not publish, upload, "
            "write approved URLs, connect to Splunk/MCP, update Devpost, or submit."
        ),
    }


def check_required(root: Path, files: list[str], prefix: str, checks: list[Check]) -> None:
    missing = [item for item in files if not (root / item).exists()]
    add_check(checks, f"{prefix} required files", not missing, "missing: " + ", ".join(missing) if missing else f"{len(files)} files present")


def check_final_submission_checklist(root: Path, checks: list[Check]) -> None:
    path = root / "submission/FINAL_SUBMISSION_CHECKLIST.md"
    if not path.exists():
        add_check(checks, "Final submission checklist exists", False, "missing")
        return

    text = path.read_text(encoding="utf-8")
    missing_scripts = [
        item
        for item in CHECKLIST_SYNC_SCRIPTS
        if item not in text and item.replace("/", "\\") not in text
    ]
    add_check(
        checks,
        "Final submission checklist safety script sync",
        not missing_scripts,
        "missing: " + ", ".join(missing_scripts) if missing_scripts else f"{len(CHECKLIST_SYNC_SCRIPTS)} safety scripts present",
    )

    required_phrases = [
        "Public repo dry run shows isolated TEMP staging",
        "Guarded public repo helper blocks execute mode",
        "Video screen safety checklist exists",
        "Video dry run shows a local-only recording rehearsal",
        "Video recording preview shows a TEMP-staged preview URL",
        "Video upload metadata shows title, description, tags",
        "Public artifact URL readback stays pending",
        "URL writeback dry run shows exactly what would change",
        "Public repo metadata shows repository name",
        "Submission deadline burndown shows target submit timing",
        "Splunk MCP proof capture manifest shows capture slots",
        "Status conflict audit shows no stale failed statuses",
        "Candidate includes `reports/latest_status_conflict_audit.html`",
        "Devpost final review checklist exists",
        "Approval execution handoff maps each next phase",
    ]
    missing_phrases = [item for item in required_phrases if item not in text]
    add_check(
        checks,
        "Final submission checklist safety evidence sync",
        not missing_phrases,
        "missing: " + ", ".join(missing_phrases) if missing_phrases else f"{len(required_phrases)} safety evidence checks present",
    )


def check_png(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"PNG exists {rel(path, root)}", False, "missing")
        return
    data = path.read_bytes()
    ok = len(data) > 1000 and data[:8] == b"\x89PNG\r\n\x1a\n"
    add_check(checks, f"PNG signature {rel(path, root)}", ok, f"bytes={len(data)}")


def check_html(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"HTML exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Agentic Incident Command Center",
        "MCP Remediation Ledger",
        "Splunk Queries For Demo",
        "MCP Investigation Preview",
    ]
    missing = [item for item in required if item not in text]
    add_check(checks, f"HTML sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_local_spl_html(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"Local SPL HTML exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Local SPL Query Results",
        "Incident timeline across observability, security, network, deploy, and MCP",
        "Root-cause evidence for checkout regression",
        "Human-approved remediation ledger",
        "Splunk MCP investigation context",
        "Blast radius by service",
    ]
    missing = [item for item in required if item not in text]
    add_check(checks, f"Local SPL HTML sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_demo_tour_html(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"Demo tour HTML exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Agentic Incident Command Center Demo Tour",
        "Scene 1 / Problem",
        "Scene 2 / Incident Command Summary",
        "Scene 5 / Local SPL Proof",
        "Scene 6 / Splunk MCP Boundary",
        "Still pending user approval",
    ]
    missing = [item for item in required if item not in text]
    add_check(checks, f"Demo tour HTML sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_video_readiness(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_video_readiness.html"
    json_path = root / "reports/latest_video_readiness.json"
    checklist_path = root / "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md"
    missing_files = [rel(path, root) for path in [html_path, json_path, checklist_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Video readiness report files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    checklist = checklist_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Video Readiness Report",
        "Timing",
        "Screen Safety And Claim Boundary",
        "External Gates",
        "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
        "ready_for_recording_review",
    ]
    missing = [item for item in required if item not in plain_html]
    checklist_required = [
        "Video Screen Safety Checklist",
        "Status: pending screen safety review",
        "Use synthetic data only.",
        "Do not show `.env`, config files, API keys, OAuth tokens, or private logs.",
        "Do not show real customer, cloud, incident, identity, ticketing, or Splunk account screens.",
        "designed for Splunk MCP Server",
        "does not record, upload, publish, write approved URLs, update Devpost, or submit",
        "Public video upload stays blocked",
    ]
    checklist_missing = [item for item in checklist_required if item not in checklist]
    add_check(checks, f"Video readiness sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Video readiness status {rel(json_path, root)}", payload.get("status") == "ready_for_recording_review", str(payload.get("status")))
    add_check(checks, f"Video readiness duration {rel(json_path, root)}", int(payload.get("duration_seconds", 9999)) <= 180, f"{payload.get('duration_seconds')}s")
    add_check(checks, f"Video readiness screen checklist pointer {rel(json_path, root)}", payload.get("screen_safety_checklist") == "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md", str(payload.get("screen_safety_checklist")))
    add_check(checks, f"Video screen safety checklist sections {rel(checklist_path, root)}", not checklist_missing, "missing: " + ", ".join(checklist_missing) if checklist_missing else "all key sections present")
    add_check(checks, f"Video screen safety checklist pending state {rel(checklist_path, root)}", checklist.count("- [ ]") >= 8 and "Status: pending screen safety review" in checklist, f"unchecked={checklist.count('- [ ]')}")


def check_video_command_plan(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_video_command_plan.html"
    md_path = root / "reports/latest_video_command_plan.md"
    json_path = root / "reports/latest_video_command_plan.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Video command plan files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Demo Video Recording And Upload Command Plan",
        "Commands After Approval",
        "Build screen-safe localhost recording preview",
        "build_video_recording_preview.py",
        "Review video upload metadata",
        "build_video_upload_metadata.py",
        "Public video upload preflight gate",
        "verify_public_video_upload_gate.py",
        "Approve recording and public upload of the Agentic Incident Command Center demo video.",
        "verify_public_artifact_urls.py",
        "manual: record",
        "manual: upload",
        "Explicit user approval is required",
        "does not record, upload, publish",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    commands = payload.get("commands", [])
    add_check(checks, f"Video command plan sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Video command plan status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    commands_text = "\n".join(str(item.get("command", "")) for item in commands if isinstance(item, dict))
    add_check(checks, f"Video command plan command count {rel(json_path, root)}", len(commands) >= 8, str(len(commands)))
    add_check(checks, f"Video command plan preview helper {rel(json_path, root)}", "build_video_recording_preview.py" in commands_text, "preview helper present" if "build_video_recording_preview.py" in commands_text else "missing preview helper")
    add_check(checks, f"Video command plan upload metadata {rel(json_path, root)}", "build_video_upload_metadata.py" in commands_text, "upload metadata present" if "build_video_upload_metadata.py" in commands_text else "missing upload metadata")
    add_check(checks, f"Video command plan upload preflight {rel(json_path, root)}", "verify_public_video_upload_gate.py" in commands_text and "Approve recording and public upload of the Agentic Incident Command Center demo video." in commands_text, "upload preflight present" if "verify_public_video_upload_gate.py" in commands_text else "missing upload preflight")
    add_check(checks, f"Video command plan URL readback {rel(json_path, root)}", "verify_public_artifact_urls.py" in commands_text and "--live-readback" in commands_text, "URL readback present" if "verify_public_artifact_urls.py" in commands_text else "missing URL readback")


def check_video_cue_sheet(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_video_cue_sheet.html"
    md_path = root / "reports/latest_video_cue_sheet.md"
    json_path = root / "reports/latest_video_cue_sheet.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Video cue sheet files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Demo Video Cue Sheet",
        "0:00-0:20",
        "Problem",
        "Dashboard",
        "Splunk/MCP Fit",
        "Screen Safety Guardrails",
        "does not record, upload, publish, write approved URLs, update Devpost, or submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    scenes = payload.get("scenes", [])
    add_check(checks, f"Video cue sheet sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Video cue sheet status {rel(json_path, root)}", payload.get("status") == "ready_for_recording_review", str(payload.get("status")))
    add_check(checks, f"Video cue sheet scene count {rel(json_path, root)}", len(scenes) >= 6, str(len(scenes)))
    add_check(checks, f"Video cue sheet duration {rel(json_path, root)}", int(payload.get("duration_seconds", 999)) <= 180, str(payload.get("duration_seconds")))
    add_check(checks, f"Video cue sheet missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Video cue sheet final gate {rel(json_path, root)}", payload.get("final_public_video_ready") is False, str(payload.get("final_public_video_ready")))


def check_video_dry_run(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_video_dry_run.html"
    md_path = root / "reports/latest_video_dry_run.md"
    json_path = root / "reports/latest_video_dry_run.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Video dry run files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Demo Video Dry Run",
        "Local-only recording rehearsal",
        "screen safety",
        "internal paths",
        "secret-like strings",
        "without recording video",
        "uploading video",
    ]
    combined = "\n".join([plain_html, markdown])
    missing = [item for item in required if item not in combined]
    gate_state = payload.get("external_gate_state", {})
    add_check(checks, f"Video dry run sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Video dry run status {rel(json_path, root)}", payload.get("status") == "ready_for_recording_review", str(payload.get("status")))
    add_check(checks, f"Video dry run failed count {rel(json_path, root)}", payload.get("failed_count") == 0, str(payload.get("failed_count")))
    add_check(checks, f"Video dry run scene count {rel(json_path, root)}", int(payload.get("scene_count", 0)) >= 6, str(payload.get("scene_count")))
    add_check(checks, f"Video dry run duration {rel(json_path, root)}", int(payload.get("duration_seconds", 999)) <= 180, str(payload.get("duration_seconds")))
    add_check(checks, f"Video dry run missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Video dry run final gate {rel(json_path, root)}", payload.get("final_public_video_ready") is False, str(payload.get("final_public_video_ready")))
    add_check(checks, f"Video dry run approved URL gate {rel(json_path, root)}", gate_state.get("approved_public_urls_exists") is False, str(gate_state.get("approved_public_urls_exists")))


def check_video_recording_preview(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_video_recording_preview.html"
    md_path = root / "reports/latest_video_recording_preview.md"
    json_path = root / "reports/latest_video_recording_preview.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Video recording preview files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Demo Video Recording Preview",
        "localhost preview",
        "127.0.0.1",
        "system_temp_public_candidate_copy",
        "Public Video Safe Readback",
        "YYYY-MM-DD_public_demo_video_readback.md",
        "Do not copy raw recording output",
        "without recording video",
        "uploading video",
    ]
    combined = "\n".join([plain_html, markdown])
    missing = [item for item in required if item not in combined]
    add_check(checks, f"Video recording preview sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Video recording preview status {rel(json_path, root)}", payload.get("status") == "ready_for_recording_review", str(payload.get("status")))
    add_check(checks, f"Video recording preview failed count {rel(json_path, root)}", payload.get("failed_count") == 0, str(payload.get("failed_count")))
    add_check(checks, f"Video recording preview stage policy {rel(json_path, root)}", payload.get("stage_policy") == "system_temp_public_candidate_copy", str(payload.get("stage_policy")))
    add_check(checks, f"Video recording preview stage cleanup {rel(json_path, root)}", payload.get("stage_removed_after_run") is True, str(payload.get("stage_removed_after_run")))
    add_check(checks, f"Video recording preview localhost URL {rel(json_path, root)}", str(payload.get("preview_url", "")).startswith("http://127.0.0.1:"), str(payload.get("preview_url", "missing")))
    add_check(checks, f"Video recording preview external gate {rel(json_path, root)}", payload.get("external_actions_attempted") is False and payload.get("external_actions_completed") is False, f"attempted={payload.get('external_actions_attempted')} completed={payload.get('external_actions_completed')}")
    safe = payload.get("public_video_safe_readback", {}) if isinstance(payload, dict) else {}
    safe_json = json.dumps(safe, ensure_ascii=False)
    scan = safe.get("screen_scan", {}) if isinstance(safe.get("screen_scan"), dict) else {}
    add_check(checks, f"Video recording preview safe readback action {rel(json_path, root)}", safe.get("action_key") == "public_demo_video", str(safe.get("action_key")))
    add_check(checks, f"Video recording preview safe readback target {rel(json_path, root)}", safe.get("evidence_note_target") == "submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md", str(safe.get("evidence_note_target")))
    add_check(checks, f"Video recording preview safe readback upload gate {rel(json_path, root)}", safe.get("ready_for_public_upload") is False and safe.get("external_actions_attempted") is False, f"ready={safe.get('ready_for_public_upload')} attempted={safe.get('external_actions_attempted')}")
    add_check(checks, f"Video recording preview safe readback scans {rel(json_path, root)}", int(scan.get("internal_path_hit_count", -1)) == 0 and int(scan.get("secret_like_hit_count", -1)) == 0, json.dumps(scan, ensure_ascii=False))
    add_check(checks, f"Video recording preview safe readback omits local paths {rel(json_path, root)}", ABSOLUTE_PATH_PATTERN.search(safe_json) is None, sanitize_detail(safe_json[-800:]))


def check_video_upload_metadata(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_video_upload_metadata.html"
    md_path = root / "reports/latest_video_upload_metadata.md"
    json_path = root / "reports/latest_video_upload_metadata.json"
    submission_path = root / "submission/VIDEO_UPLOAD_METADATA.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, submission_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Video upload metadata files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    submission_markdown = submission_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    combined = "\n".join([plain_html, markdown, submission_markdown])
    required = [
        "Video Upload Metadata",
        "Agentic Incident Command Center: Splunk-grounded AI incident response",
        "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL",
        "synthetic checkout-incident events",
        "MCP Remediation Ledger",
        "human approval",
        "Expected Readback",
        "Do not upload if the recording shows private paths",
        "does not record video, upload video, publish media",
    ]
    missing = [item for item in required if item not in combined]
    readback = payload.get("expected_readback", {})
    tags = set(payload.get("tags", []))
    add_check(checks, f"Video upload metadata sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Video upload metadata status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Video upload metadata duration {rel(json_path, root)}", int(payload.get("observed_duration_seconds", 999)) <= 180 and int(payload.get("duration_limit_seconds", 0)) == 180, f"observed={payload.get('observed_duration_seconds')} limit={payload.get('duration_limit_seconds')}")
    add_check(checks, f"Video upload metadata pending URL {rel(json_path, root)}", payload.get("public_video_url") == "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL", str(payload.get("public_video_url")))
    add_check(checks, f"Video upload metadata final gate {rel(json_path, root)}", payload.get("final_public_video_ready") is False and payload.get("approved_public_urls_exists") is False, f"final={payload.get('final_public_video_ready')} urls={payload.get('approved_public_urls_exists')}")
    add_check(checks, f"Video upload metadata tags {rel(json_path, root)}", {"Splunk", "AgentOps", "AI agents", "MCP"}.issubset(tags), ", ".join(sorted(tags)))
    add_check(checks, f"Video upload metadata readback {rel(json_path, root)}", readback.get("visibility") == "public" and readback.get("duration_seconds_max") == 180, str(readback))


def check_public_video_upload_preflight(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_public_video_upload_preflight.html"
    md_path = root / "reports/latest_public_video_upload_preflight.md"
    json_path = root / "reports/latest_public_video_upload_preflight.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Public video upload preflight files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Public Video Upload Preflight",
        "Gate status",
        "Public video upload allowed",
        "Approval phrase accepted",
        "Safe Readback",
        "YYYY-MM-DD_public_demo_video_readback.md",
        "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
        "does not record video, upload video, publish media",
    ]
    combined = "\n".join([plain_html, markdown])
    missing = [item for item in required if item not in combined]
    safe = payload.get("public_video_upload_safe_readback", {})
    safe_json = json.dumps(safe, ensure_ascii=False)
    add_check(checks, f"Public video upload preflight sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Public video upload preflight status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Public video upload preflight blocks upload {rel(json_path, root)}", payload.get("public_video_upload_allowed") is False and payload.get("gate_status") == "blocked_by_video_approval_gate", f"allowed={payload.get('public_video_upload_allowed')} gate={payload.get('gate_status')}")
    add_check(checks, f"Public video upload preflight approval gate {rel(json_path, root)}", payload.get("approval_phrase_accepted") is False, str(payload.get("approval_phrase_accepted")))
    add_check(checks, f"Public video upload preflight duration {rel(json_path, root)}", int(payload.get("duration_seconds", 999)) <= 180, str(payload.get("duration_seconds")))
    add_check(checks, f"Public video upload preflight missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Public video upload preflight no external action {rel(json_path, root)}", payload.get("external_actions_attempted") is False and payload.get("external_actions_completed") is False, f"attempted={payload.get('external_actions_attempted')} completed={payload.get('external_actions_completed')}")
    add_check(checks, f"Public video upload safe readback action {rel(json_path, root)}", safe.get("action_key") == "public_demo_video", str(safe.get("action_key")))
    add_check(checks, f"Public video upload safe readback target {rel(json_path, root)}", safe.get("evidence_note_target") == "submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md", str(safe.get("evidence_note_target")))
    add_check(checks, f"Public video upload safe readback upload gate {rel(json_path, root)}", safe.get("ready_for_public_upload") is False and safe.get("external_actions_attempted") is False, f"ready={safe.get('ready_for_public_upload')} attempted={safe.get('external_actions_attempted')}")
    add_check(checks, f"Public video upload safe readback omits local paths {rel(json_path, root)}", ABSOLUTE_PATH_PATTERN.search(safe_json) is None, sanitize_detail(safe_json[-800:]))


def check_public_repo_publication_preflight(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_public_repo_publication_preflight.html"
    md_path = root / "reports/latest_public_repo_publication_preflight.md"
    json_path = root / "reports/latest_public_repo_publication_preflight.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Public repo publication preflight files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Public Repo Publication Preflight",
        "Gate status",
        "Public repo publication allowed",
        "Approval phrase accepted",
        "Safe Readback",
        "YYYY-MM-DD_public_github_repository_readback.md",
        "verify_public_repo_publication_gate.py",
        "publish_public_repo_after_approval.py",
        "does not create a repository, push commits, publish files",
    ]
    combined = "\n".join([plain_html, markdown])
    missing = [item for item in required if item not in combined]
    safe = payload.get("public_repo_publication_safe_readback", {})
    safe_json = json.dumps(safe, ensure_ascii=False)
    add_check(checks, f"Public repo publication preflight sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Public repo publication preflight status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Public repo publication preflight blocks publication {rel(json_path, root)}", payload.get("public_repo_publication_allowed") is False and payload.get("gate_status") == "blocked_by_public_repo_approval_gate", f"allowed={payload.get('public_repo_publication_allowed')} gate={payload.get('gate_status')}")
    add_check(checks, f"Public repo publication preflight approval gate {rel(json_path, root)}", payload.get("approval_phrase_accepted") is False, str(payload.get("approval_phrase_accepted")))
    add_check(checks, f"Public repo publication preflight missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Public repo publication preflight no external action {rel(json_path, root)}", payload.get("external_actions_attempted") is False and payload.get("external_actions_completed") is False, f"attempted={payload.get('external_actions_attempted')} completed={payload.get('external_actions_completed')}")
    add_check(checks, f"Public repo publication safe readback action {rel(json_path, root)}", safe.get("action_key") == "public_github_repository", str(safe.get("action_key")))
    add_check(checks, f"Public repo publication safe readback target {rel(json_path, root)}", safe.get("evidence_note_target") == "submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md", str(safe.get("evidence_note_target")))
    add_check(checks, f"Public repo publication safe readback publish gate {rel(json_path, root)}", safe.get("ready_for_publication") is False and safe.get("external_actions_attempted") is False, f"ready={safe.get('ready_for_publication')} attempted={safe.get('external_actions_attempted')}")
    add_check(checks, f"Public repo publication safe readback omits local paths {rel(json_path, root)}", ABSOLUTE_PATH_PATTERN.search(safe_json) is None, sanitize_detail(safe_json[-800:]))


def check_claim_evidence_matrix(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_claim_evidence_matrix.html"
    md_path = root / "reports/latest_claim_evidence_matrix.md"
    json_path = root / "reports/latest_claim_evidence_matrix.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Claim evidence matrix files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Claim Evidence Matrix",
        "Allowed Wording",
        "Avoid Wording",
        "synthetic incident data",
        "Splunk-ready incident data",
        "MCP Remediation Ledger",
        "Splunk MCP Server",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    claims = payload.get("claims", [])
    add_check(checks, f"Claim evidence matrix sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Claim evidence matrix status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Claim evidence matrix missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Claim evidence matrix claim count {rel(json_path, root)}", len(claims) >= 7, str(len(claims)))
    add_check(checks, f"Claim evidence matrix ready count {rel(json_path, root)}", payload.get("ready_claim_count") == payload.get("total_claim_count"), f"{payload.get('ready_claim_count')}/{payload.get('total_claim_count')}")
    add_check(checks, f"Claim evidence matrix final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    splunk_claim = next((item for item in claims if item.get("key") == "splunk_mcp_design"), {})
    splunk_paths = {item.get("path") for item in splunk_claim.get("evidence", [])}
    add_check(checks, f"Claim evidence matrix Splunk MCP capture evidence {rel(json_path, root)}", "reports/latest_splunk_mcp_proof_capture_manifest.html" in splunk_paths, ", ".join(sorted(str(item) for item in splunk_paths)))


def check_external_approval_packet(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_external_approval_packet.html"
    md_path = root / "reports/latest_external_approval_packet.md"
    json_path = root / "reports/latest_external_approval_packet.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "External approval packet files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "External Approval Packet",
        "Public GitHub Repository",
        "reports/latest_public_repo_publication_preflight.html",
        "Public Demo Video",
        "reports/latest_public_video_upload_preflight.html",
        "Optional Live Splunk / MCP Proof",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "Devpost Final Submission",
        "does not publish, upload, submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    ready = set(payload.get("ready_requests", []))
    expected_ready = {"public_github_repository", "public_demo_video"}
    add_check(checks, f"External approval packet sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"External approval packet status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"External approval packet ready requests {rel(json_path, root)}", expected_ready.issubset(ready), ", ".join(sorted(ready)))
    optional_request = next((item for item in payload.get("approval_requests", []) if item.get("title") == "Optional Live Splunk / MCP Proof"), {})
    optional_paths = {item.get("path") for item in optional_request.get("evidence", [])}
    add_check(checks, f"External approval packet Splunk MCP capture evidence {rel(json_path, root)}", "reports/latest_splunk_mcp_proof_capture_manifest.html" in optional_paths and "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md" in optional_paths, ", ".join(sorted(str(item) for item in optional_paths)))
    repo_request = next((item for item in payload.get("approval_requests", []) if item.get("key") == "public_github_repository"), {})
    repo_paths = {item.get("path") for item in repo_request.get("evidence", [])}
    add_check(checks, f"External approval packet public repo preflight evidence {rel(json_path, root)}", "reports/latest_public_repo_publication_preflight.html" in repo_paths, ", ".join(sorted(str(item) for item in repo_paths)))
    video_request = next((item for item in payload.get("approval_requests", []) if item.get("key") == "public_demo_video"), {})
    video_paths = {item.get("path") for item in video_request.get("evidence", [])}
    add_check(checks, f"External approval packet public video preflight evidence {rel(json_path, root)}", "reports/latest_public_video_upload_preflight.html" in video_paths, ", ".join(sorted(str(item) for item in video_paths)))


def check_submission_url_apply_plan(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_submission_url_apply_plan.html"
    md_path = root / "reports/latest_submission_url_apply_plan.md"
    json_path = root / "reports/latest_submission_url_apply_plan.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Submission URL apply plan files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Submission URL Apply Plan",
        "Repository URL",
        "Demo video URL",
        "Approved URL file",
        "Verified live readback",
        "reports/latest_public_artifact_url_readback.json",
        "does not publish, upload, submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    allowed_statuses = {"waiting_for_external_urls", "ready_to_submit_after_user_approval"}
    add_check(checks, f"Submission URL apply plan sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Submission URL apply plan status {rel(json_path, root)}", payload.get("status") in allowed_statuses, str(payload.get("status")))
    add_check(checks, f"Submission URL apply plan write gate {rel(json_path, root)}", payload.get("approved_urls_file_written") is False, str(payload.get("approved_urls_file_written")))
    add_check(checks, f"Submission URL apply plan readback gate {rel(json_path, root)}", payload.get("verified_readback_required") is False and payload.get("verified_readback_passed") is False, f"required={payload.get('verified_readback_required')} passed={payload.get('verified_readback_passed')}")
    add_check(checks, f"Submission URL apply plan readback source {rel(json_path, root)}", payload.get("verified_readback_source") == "reports/latest_public_artifact_url_readback.json", str(payload.get("verified_readback_source")))


def check_public_artifact_url_readback(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_public_artifact_url_readback.html"
    md_path = root / "reports/latest_public_artifact_url_readback.md"
    json_path = root / "reports/latest_public_artifact_url_readback.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Public artifact URL readback files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Public Artifact URL Readback",
        "Verification gate before approved URL writeback",
        "Live readback attempted",
        "Ready for URL writeback",
        "Public-Safe Readback",
        "YYYY-MM-DD_approved_url_writeback_readback.md",
        "Do not copy raw command output",
        "does not publish, upload",
    ]
    combined = "\n".join([plain_html, markdown])
    missing = [item for item in required if item not in combined]
    add_check(checks, f"Public artifact URL readback sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Public artifact URL readback producer {rel(json_path, root)}", payload.get("producer") == "verify_public_artifact_urls.py", str(payload.get("producer")))
    add_check(checks, f"Public artifact URL readback status {rel(json_path, root)}", payload.get("status") in {"waiting_for_external_urls", "ready_for_live_readback", "ready_for_url_writeback_after_user_approval"}, str(payload.get("status")))
    add_check(checks, f"Public artifact URL readback failed count {rel(json_path, root)}", payload.get("failed_count") == 0, str(payload.get("failed_count")))
    add_check(checks, f"Public artifact URL readback pending gate {rel(json_path, root)}", set(payload.get("pending_urls", [])) == {"repository_url", "demo_video_url"}, ", ".join(payload.get("pending_urls", [])))
    add_check(checks, f"Public artifact URL readback no network while pending {rel(json_path, root)}", payload.get("live_readback_attempted") is False, str(payload.get("live_readback_attempted")))
    add_check(checks, f"Public artifact URL readback writeback closed {rel(json_path, root)}", payload.get("ready_for_url_writeback") is False and payload.get("approved_public_urls_exists") is False, f"ready={payload.get('ready_for_url_writeback')} approved={payload.get('approved_public_urls_exists')}")
    safe = payload.get("public_safe_readback", {}) if isinstance(payload, dict) else {}
    safe_json = json.dumps(safe, ensure_ascii=False)
    add_check(checks, f"Public artifact URL safe readback present {rel(json_path, root)}", safe.get("action_key") == "approved_url_writeback", str(safe.get("action_key")))
    add_check(checks, f"Public artifact URL safe readback target {rel(json_path, root)}", safe.get("evidence_note_target") == "submission/post_action_evidence/YYYY-MM-DD_approved_url_writeback_readback.md", str(safe.get("evidence_note_target")))
    add_check(checks, f"Public artifact URL safe readback writeback closed {rel(json_path, root)}", safe.get("ready_for_url_writeback") is False and safe.get("approved_public_urls_exists") is False, f"ready={safe.get('ready_for_url_writeback')} approved={safe.get('approved_public_urls_exists')}")
    add_check(checks, f"Public artifact URL safe readback omits local paths {rel(json_path, root)}", ABSOLUTE_PATH_PATTERN.search(safe_json) is None, sanitize_detail(safe_json[-800:]))


def check_publication_command_plan(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_publication_command_plan.html"
    md_path = root / "reports/latest_publication_command_plan.md"
    json_path = root / "reports/latest_publication_command_plan.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Publication command plan files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Public Repository Publication Command Plan",
        "Commands After Approval",
        "guarded publication rehearsal",
        "verify_public_repo_publication_gate.py",
        "publish_public_repo_after_approval.py",
        "verify_public_artifact_urls.py",
        "--execute",
        "Explicit user approval is required",
        "does not create a repo, push commits, publish files",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    commands = payload.get("commands", [])
    commands_text = "\n".join(str(item.get("command", "")) for item in commands if isinstance(item, dict))
    add_check(checks, f"Publication command plan sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Publication command plan status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Publication command plan command count {rel(json_path, root)}", len(commands) >= 5, str(len(commands)))
    add_check(checks, f"Publication command plan publication preflight {rel(json_path, root)}", "verify_public_repo_publication_gate.py" in commands_text and "--public-git-identity-confirmed" in commands_text, "publication preflight present" if "verify_public_repo_publication_gate.py" in commands_text else "missing publication preflight")
    add_check(checks, f"Publication command plan guarded helper {rel(json_path, root)}", "publish_public_repo_after_approval.py" in commands_text and "--execute" in commands_text, "guarded helper present" if "publish_public_repo_after_approval.py" in commands_text else "missing guarded helper")
    add_check(checks, f"Publication command plan URL readback {rel(json_path, root)}", "verify_public_artifact_urls.py" in commands_text and "--live-readback" in commands_text, "URL readback present" if "verify_public_artifact_urls.py" in commands_text else "missing URL readback")


def check_guarded_publication_helper_metadata(root: Path, checks: list[Check]) -> None:
    helper_path = root / "scripts/publish_public_repo_after_approval.py"
    if not helper_path.exists():
        add_check(checks, "Guarded publication helper metadata file", False, f"missing: {rel(helper_path, root)}")
        return
    source = helper_path.read_text(encoding="utf-8")
    required = [
        "Splunk-grounded AI incident commander with human-approved remediation.",
        "reports/latest_public_repo_metadata.json",
        "submission/PUBLIC_REPO_METADATA.md",
        "--description",
        "gh repo readback description",
        "gh repo readback default branch",
        "gh repo readback license",
        "gh repo readback topics",
        "nameWithOwner,visibility,url,description,defaultBranchRef,licenseInfo,repositoryTopics,isPrivate",
        "expected_metadata",
        "approved_public_urls.json absent",
        "public_safe_readback",
        "evidence_note_target",
        "Do not copy stage_root",
        "YYYY-MM-DD_public_github_repository_readback.md",
        "invalid_execute_inputs",
        "approved-public-git-name",
        "approved-public-git-email",
        "must be a real public git identity",
        "must include @",
    ]
    missing = [item for item in required if item not in source]
    add_check(checks, f"Guarded publication helper metadata readback {rel(helper_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "metadata expectations present")


def check_public_repo_metadata(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_public_repo_metadata.html"
    md_path = root / "reports/latest_public_repo_metadata.md"
    json_path = root / "reports/latest_public_repo_metadata.json"
    submission_path = root / "submission/PUBLIC_REPO_METADATA.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, submission_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Public repo metadata files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    submission_markdown = submission_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Public Repo Metadata",
        "agentops-control-tower",
        "Splunk-grounded AI incident commander",
        "Commands After Approval",
        "gh repo create agentops-control-tower --public",
        "gh repo edit <owner>/agentops-control-tower",
        "gh repo view <owner>/agentops-control-tower",
        "Expected Readback",
        "Stop Conditions",
        "does not create a repository, edit GitHub metadata, push commits, publish files",
    ]
    missing = [
        item
        for item in required
        if item not in plain_html and item not in markdown and item not in submission_markdown
    ]
    topics = set(payload.get("topics", []))
    expected_topics = {"splunk", "agentops", "ai-agents", "observability", "mcp", "safety"}
    commands = "\n".join(str(item.get("command", "")) for item in payload.get("commands_after_approval", []) if isinstance(item, dict))
    readback = payload.get("expected_readback", {})
    add_check(checks, f"Public repo metadata sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Public repo metadata status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Public repo metadata missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Public repo metadata topics {rel(json_path, root)}", expected_topics.issubset(topics), ", ".join(sorted(topics)))
    add_check(checks, f"Public repo metadata command guard {rel(json_path, root)}", "gh repo create" in commands and "gh repo view" in commands, commands)
    add_check(checks, f"Public repo metadata readback {rel(json_path, root)}", readback.get("visibility") == "PUBLIC" and readback.get("isPrivate") is False, str(readback))
    add_check(checks, f"Public repo metadata final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False and payload.get("approved_public_urls_exists") is False, f"final={payload.get('final_submit_ready')} urls={payload.get('approved_public_urls_exists')}")


def check_public_repo_publish_brief(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_public_repo_publish_brief.html"
    md_path = root / "reports/latest_public_repo_publish_brief.md"
    json_path = root / "reports/latest_public_repo_publish_brief.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Public repo publish brief files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Public Repo Publish Brief",
        "Approval phrase",
        "Approve public GitHub publication",
        "ZIP Evidence",
        "Publish Steps After Approval",
        "guarded publication rehearsal",
        "verify_public_repo_publication_gate.py",
        "publish_public_repo_after_approval.py",
        "verify_public_artifact_urls.py",
        "--execute",
        "Stop Conditions",
        "does not create a public repo, push commits, publish files, write approved URLs",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    steps = payload.get("publish_steps", [])
    steps_text = "\n".join(str(item.get("command", "")) for item in steps if isinstance(item, dict))
    zip_info = payload.get("zip", {})
    add_check(checks, f"Public repo publish brief sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Public repo publish brief status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Public repo publish brief missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Public repo publish brief step count {rel(json_path, root)}", len(steps) >= 5, str(len(steps)))
    add_check(checks, f"Public repo publish brief publication preflight {rel(json_path, root)}", "verify_public_repo_publication_gate.py" in steps_text and "--public-git-identity-confirmed" in steps_text, "publication preflight present" if "verify_public_repo_publication_gate.py" in steps_text else "missing publication preflight")
    add_check(checks, f"Public repo publish brief guarded helper {rel(json_path, root)}", "publish_public_repo_after_approval.py" in steps_text and "--execute" in steps_text, "guarded helper present" if "publish_public_repo_after_approval.py" in steps_text else "missing guarded helper")
    add_check(checks, f"Public repo publish brief URL readback {rel(json_path, root)}", "verify_public_artifact_urls.py" in steps_text and "--live-readback" in steps_text, "URL readback present" if "verify_public_artifact_urls.py" in steps_text else "missing URL readback")
    add_check(checks, f"Public repo publish brief approval gate {rel(json_path, root)}", payload.get("public_repo_approval_ready") is True, str(payload.get("public_repo_approval_ready")))
    add_check(checks, f"Public repo publish brief final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    file_count = zip_info.get("file_count")
    add_check(checks, f"Public repo publish brief zip count {rel(json_path, root)}", isinstance(file_count, int) and file_count > 0, str(file_count))
    expected_counts: dict[str, int] = {}
    manifest = read_optional_json(root / "reports/latest_public_candidate_zip_manifest.json")
    smoke = read_optional_json(root / "reports/latest_release_zip_smoke_test.json")
    if isinstance(manifest.get("file_count"), int):
        expected_counts["manifest"] = manifest["file_count"]
    if isinstance(smoke.get("zip_file_count"), int):
        expected_counts["smoke"] = smoke["zip_file_count"]
    if expected_counts and isinstance(file_count, int):
        mismatches = {key: value for key, value in expected_counts.items() if value != file_count}
        detail = f"publish={file_count}; " + ", ".join(f"{key}={value}" for key, value in expected_counts.items())
        add_check(checks, f"Public repo publish brief zip count consistency {rel(json_path, root)}", not mismatches, detail)


def check_public_repo_dry_run(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_public_repo_dry_run.html"
    md_path = root / "reports/latest_public_repo_dry_run.md"
    json_path = root / "reports/latest_public_repo_dry_run.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Public repo dry run files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Public Repo Dry Run",
        "git init",
        "git add",
        "git commit",
        "Git branch",
        "Staging isolated",
        "internal paths",
        "secret-like strings",
        "without creating a remote, pushing commits",
    ]
    combined = "\n".join([plain_html, markdown])
    missing = [item for item in required if item not in combined]
    rehearsal = payload.get("rehearsal", {})
    add_check(checks, f"Public repo dry run sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Public repo dry run status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Public repo dry run failed count {rel(json_path, root)}", payload.get("failed_count") == 0, str(payload.get("failed_count")))
    add_check(checks, f"Public repo dry run file count {rel(json_path, root)}", int(payload.get("candidate_file_count", 0)) >= 100, str(payload.get("candidate_file_count")))
    add_check(checks, f"Public repo dry run staged count {rel(json_path, root)}", int(rehearsal.get("git_status_line_count", 0)) >= 100, str(rehearsal.get("git_status_line_count")))
    add_check(checks, f"Public repo dry run main branch {rel(json_path, root)}", rehearsal.get("git_branch") == "main", str(rehearsal.get("git_branch")))
    add_check(checks, f"Public repo dry run commit created {rel(json_path, root)}", rehearsal.get("git_commit_created") is True, str(rehearsal.get("git_commit_created")))
    add_check(checks, f"Public repo dry run tracked count {rel(json_path, root)}", int(rehearsal.get("git_tracked_file_count", 0)) >= 100, str(rehearsal.get("git_tracked_file_count")))
    add_check(checks, f"Public repo dry run post-commit clean {rel(json_path, root)}", int(rehearsal.get("git_post_commit_status_line_count", -1)) == 0, str(rehearsal.get("git_post_commit_status_line_count")))
    add_check(checks, f"Public repo dry run isolated staging {rel(json_path, root)}", rehearsal.get("staging_isolated_from_private_workspace") is True, str(rehearsal.get("staging_isolated_from_private_workspace")))
    add_check(checks, f"Public repo dry run staging policy {rel(json_path, root)}", rehearsal.get("staging_location_policy") == "system_temp_outside_private_workspace", str(rehearsal.get("staging_location_policy")))
    add_check(checks, f"Public repo dry run no remote {rel(json_path, root)}", not str(rehearsal.get("git_remote_output", "")).strip(), str(rehearsal.get("git_remote_output", "")) or "no remotes")
    add_check(checks, f"Public repo dry run no remote after commit {rel(json_path, root)}", not str(rehearsal.get("git_post_commit_remote_output", "")).strip(), str(rehearsal.get("git_post_commit_remote_output", "")) or "no remotes")
    add_check(checks, f"Public repo dry run final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    add_check(checks, f"Public repo dry run approved URL gate {rel(json_path, root)}", payload.get("approved_public_urls_exists") is False, str(payload.get("approved_public_urls_exists")))


def check_url_writeback_dry_run(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_url_writeback_dry_run.html"
    md_path = root / "reports/latest_url_writeback_dry_run.md"
    json_path = root / "reports/latest_url_writeback_dry_run.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "URL writeback dry run files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "URL Writeback Dry Run",
        "temporary local copy",
        "Final submit ready in temp",
        "Verified readback passed in temp",
        "Approved URLs written to working tree",
        "does not publish a repository, upload video",
    ]
    combined = "\n".join([plain_html, markdown])
    missing = [item for item in required if item not in combined]
    rehearsal = payload.get("rehearsal_state", {})
    add_check(checks, f"URL writeback dry run sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"URL writeback dry run status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"URL writeback dry run failed count {rel(json_path, root)}", payload.get("failed_count") == 0, str(payload.get("failed_count")))
    add_check(checks, f"URL writeback dry run temp final gate {rel(json_path, root)}", payload.get("final_submit_ready_in_temp") is True, str(payload.get("final_submit_ready_in_temp")))
    add_check(checks, f"URL writeback dry run working tree guard {rel(json_path, root)}", payload.get("approved_public_urls_written_to_working_tree") is False, str(payload.get("approved_public_urls_written_to_working_tree")))
    add_check(checks, f"URL writeback dry run verified readback gate {rel(json_path, root)}", rehearsal.get("url_apply_verified_readback_passed") is True, str(rehearsal.get("url_apply_verified_readback_passed")))
    add_check(checks, f"URL writeback dry run temp URL validation {rel(json_path, root)}", rehearsal.get("url_validation_status") == "ready_to_submit_after_user_approval", str(rehearsal.get("url_validation_status")))
    add_check(checks, f"URL writeback dry run temp pending URL fields {rel(json_path, root)}", rehearsal.get("manual_fill_pending_fields") == [], str(rehearsal.get("manual_fill_pending_fields")))


def check_public_launch_snapshot(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_public_launch_snapshot.html"
    md_path = root / "reports/latest_public_launch_snapshot.md"
    json_path = root / "reports/latest_public_launch_snapshot.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Public launch snapshot files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Public Launch Snapshot",
        "Approval Phrases",
        "Release ZIP",
        "Approve public GitHub",
        "reports/latest_public_repo_publication_preflight.html",
        "Approve recording and public upload",
        "reports/latest_public_video_upload_preflight.html",
        "does not publish a repository, record or upload video",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    expected_order = [
        "public_github_repository",
        "public_demo_video",
        "approved_url_writeback",
        "devpost_final_submission",
    ]
    release_zip = payload.get("release_zip", {})
    root_type = payload.get("root_type")
    add_check(checks, f"Public launch snapshot sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Public launch snapshot status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Public launch snapshot failed count {rel(json_path, root)}", payload.get("failed_count") == 0, str(payload.get("failed_count")))
    add_check(checks, f"Public launch snapshot order {rel(json_path, root)}", payload.get("expected_order") == expected_order, ", ".join(payload.get("expected_order", [])))
    add_check(checks, f"Public launch snapshot ready now {rel(json_path, root)}", {"public_github_repository", "public_demo_video"}.issubset(set(payload.get("ready_now", []))), ", ".join(payload.get("ready_now", [])))
    add_check(checks, f"Public launch snapshot final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    add_check(checks, f"Public launch snapshot approved URL gate {rel(json_path, root)}", payload.get("approved_public_urls_exists") is False, str(payload.get("approved_public_urls_exists")))
    public_repo = payload.get("public_repo", {})
    add_check(
        checks,
        f"Public launch snapshot repo preflight gate {rel(json_path, root)}",
        public_repo.get("publication_preflight_status") == "ready_for_user_review"
        and public_repo.get("publication_preflight_gate_status") == "blocked_by_public_repo_approval_gate"
        and public_repo.get("publication_preflight_allowed") is False,
        f"status={public_repo.get('publication_preflight_status')} gate={public_repo.get('publication_preflight_gate_status')} allowed={public_repo.get('publication_preflight_allowed')}",
    )
    public_video = payload.get("public_video", {})
    add_check(
        checks,
        f"Public launch snapshot video preflight gate {rel(json_path, root)}",
        public_video.get("upload_preflight_status") == "ready_for_user_review"
        and public_video.get("upload_preflight_gate_status") == "blocked_by_video_approval_gate"
        and public_video.get("upload_preflight_allowed") is False,
        f"status={public_video.get('upload_preflight_status')} gate={public_video.get('upload_preflight_gate_status')} allowed={public_video.get('upload_preflight_allowed')}",
    )
    if root_type == "workspace":
        zip_path = root / str(release_zip.get("path", "release/agentops-control-tower-public-candidate.zip"))
        actual_sha = sha256_file(zip_path) if zip_path.exists() else ""
        add_check(checks, f"Public launch snapshot zip SHA {rel(json_path, root)}", len(str(release_zip.get("sha256", ""))) == 64, str(release_zip.get("sha256", "")))
        add_check(checks, f"Public launch snapshot zip SHA matches file {rel(json_path, root)}", release_zip.get("sha256") == actual_sha, f"snapshot={release_zip.get('sha256')} actual={actual_sha}")
        add_check(checks, f"Public launch snapshot zip smoke {rel(json_path, root)}", release_zip.get("smoke_status") == "pass", str(release_zip.get("smoke_status")))
    else:
        add_check(checks, f"Public launch snapshot zip boundary {rel(json_path, root)}", release_zip.get("smoke_status") == "not_applicable_public_candidate_root", str(release_zip.get("smoke_status")))


def check_user_approval_brief_ja(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_user_approval_brief_ja.html"
    md_path = root / "reports/latest_user_approval_brief_ja.md"
    json_path = root / "reports/latest_user_approval_brief_ja.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Japanese user approval brief files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Splunk次ゲート承認ブリーフ",
        "public GitHub repo",
        "公開デモ動画",
        "Approve public GitHub publication",
        "Approve recording and public upload",
        "repo公開、動画録画/アップロード",
        "承認可否マトリクス",
        "今すぐ承認可",
        "まだ承認しない",
        "状態衝突監査",
        "latest_status_conflict_audit",
        "URL反映とDevpost最終提出はまだ承認しない",
    ]
    combined = "\n".join([plain_html, markdown])
    missing = [item for item in required if item not in combined]
    ready_now = set(payload.get("ready_now", []))
    pending_actions = set(payload.get("pending_external_actions", []))
    decision_matrix_payload = payload.get("approval_decision_matrix", [])
    decision_matrix = decision_matrix_payload if isinstance(decision_matrix_payload, list) else []
    decisions = {str(item.get("key")): str(item.get("decision")) for item in decision_matrix if isinstance(item, dict)}
    release_zip = payload.get("release_zip", {})
    status_conflict = payload.get("status_conflict_audit", {})
    file_count = release_zip.get("file_count")
    artifact_count = payload.get("artifact_count")
    zip_path = root / str(release_zip.get("path", "release/agentops-control-tower-public-candidate.zip"))
    actual_sha = sha256_file(zip_path) if zip_path.exists() else ""
    add_check(checks, f"Japanese user approval brief sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Japanese user approval brief status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Japanese user approval brief failed count {rel(json_path, root)}", payload.get("failed_count") == 0, str(payload.get("failed_count")))
    add_check(checks, f"Japanese user approval brief order {rel(json_path, root)}", payload.get("expected_order") == EXTERNAL_ACTION_ORDER, ", ".join(payload.get("expected_order", [])))
    add_check(checks, f"Japanese user approval brief ready now {rel(json_path, root)}", {"public_github_repository", "public_demo_video"}.issubset(ready_now), ", ".join(sorted(ready_now)))
    add_check(checks, f"Japanese user approval brief pending actions {rel(json_path, root)}", set(EXTERNAL_ACTION_ORDER).issubset(pending_actions), ", ".join(sorted(pending_actions)))
    add_check(checks, f"Japanese user approval brief decision matrix keys {rel(json_path, root)}", set(EXTERNAL_ACTION_ORDER).issubset(set(decisions)), ", ".join(sorted(decisions)))
    add_check(
        checks,
        f"Japanese user approval brief approve-now gates {rel(json_path, root)}",
        decisions.get("public_github_repository") == "今すぐ承認可" and decisions.get("public_demo_video") == "今すぐ承認可",
        f"public_github_repository={decisions.get('public_github_repository')} public_demo_video={decisions.get('public_demo_video')}",
    )
    add_check(
        checks,
        f"Japanese user approval brief hold gates {rel(json_path, root)}",
        decisions.get("approved_url_writeback") == "まだ承認しない" and decisions.get("devpost_final_submission") == "まだ承認しない",
        f"approved_url_writeback={decisions.get('approved_url_writeback')} devpost_final_submission={decisions.get('devpost_final_submission')}",
    )
    add_check(checks, f"Japanese user approval brief final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    add_check(checks, f"Japanese user approval brief approved URL gate {rel(json_path, root)}", payload.get("approved_public_urls_exists") is False, str(payload.get("approved_public_urls_exists")))
    add_check(checks, f"Japanese user approval brief artifact count {rel(json_path, root)}", isinstance(artifact_count, int) and artifact_count >= 18, str(artifact_count))
    add_check(checks, f"Japanese user approval brief zip count {rel(json_path, root)}", isinstance(file_count, int) and file_count > 0, str(file_count))
    add_check(checks, f"Japanese user approval brief zip smoke {rel(json_path, root)}", release_zip.get("smoke_status") == "pass", str(release_zip.get("smoke_status")))
    add_check(checks, f"Japanese user approval brief zip SHA {rel(json_path, root)}", len(str(release_zip.get("sha256", ""))) == 64, str(release_zip.get("sha256", "")))
    add_check(checks, f"Japanese user approval brief zip SHA matches file {rel(json_path, root)}", release_zip.get("sha256") == actual_sha, f"brief={release_zip.get('sha256')} actual={actual_sha}")
    add_check(checks, f"Japanese user approval brief status conflict path {rel(json_path, root)}", status_conflict.get("path") == "reports/latest_status_conflict_audit.html", str(status_conflict.get("path")))
    add_check(checks, f"Japanese user approval brief status conflict status {rel(json_path, root)}", status_conflict.get("status") == "ready_for_user_review", str(status_conflict.get("status")))
    add_check(checks, f"Japanese user approval brief status conflict failed count {rel(json_path, root)}", status_conflict.get("failed_count") == 0, str(status_conflict.get("failed_count")))
    add_check(checks, f"Japanese user approval brief status conflict count {rel(json_path, root)}", status_conflict.get("conflict_count") == 0, str(status_conflict.get("conflict_count")))
    add_check(checks, f"Japanese user approval brief status conflict critical count {rel(json_path, root)}", status_conflict.get("critical_check_failed_count") == 0, str(status_conflict.get("critical_check_failed_count")))
    add_check(checks, f"Japanese user approval brief status conflict scan count {rel(json_path, root)}", isinstance(status_conflict.get("json_files_scanned"), int) and status_conflict.get("json_files_scanned") >= 20, str(status_conflict.get("json_files_scanned")))


def check_approval_execution_handoff(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_approval_execution_handoff.html"
    md_path = root / "reports/latest_approval_execution_handoff.md"
    json_path = root / "reports/latest_approval_execution_handoff.json"
    submission_path = root / "submission/APPROVAL_EXECUTION_HANDOFF.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, submission_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Approval execution handoff files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    submission_markdown = submission_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Splunk承認後実行ハンドオフ",
        "Public GitHub repo公開",
        "reports/latest_public_repo_publication_preflight.html",
        "verify_public_repo_publication_gate.py",
        "公開デモ動画",
        "reports/latest_public_video_upload_preflight.html",
        "verify_public_video_upload_gate.py",
        "任意 Splunk/MCP proof",
        "最小提出パス",
        "任意ボーナスパス",
        "公開URL読戻し",
        "承認済みURL書き戻し",
        "Devpost最終提出",
        "reports/latest_status_conflict_audit.html",
        "status conflict audit",
        "does not publish a repository",
        "press submit",
    ]
    combined = "\n".join([plain_html, markdown, submission_markdown])
    missing = [item for item in required if item not in combined]
    phases = payload.get("phases", [])
    phase_keys = {phase.get("key") for phase in phases}
    phases_by_key = {str(phase.get("key")): phase for phase in phases if isinstance(phase, dict)}
    public_repo_command = str(phases_by_key.get("public_github_repository", {}).get("command_or_action", ""))
    public_repo_phase = phases_by_key.get("public_github_repository", {})
    optional_phase = phases_by_key.get("optional_live_splunk_mcp_proof", {})
    video_phase = phases_by_key.get("public_demo_video", {})
    video_command = str(video_phase.get("command_or_action", ""))
    local_preflight_phase = phases_by_key.get("local_preflight", {})
    local_preflight_readback = " ".join(str(item) for item in local_preflight_phase.get("must_readback", []))
    status_conflict = payload.get("status_conflict_audit", {})
    minimum_path = payload.get("minimum_viable_submit_path", [])
    optional_path = payload.get("optional_bonus_path", [])
    expected = {
        "local_preflight",
        "public_github_repository",
        "public_demo_video",
        "optional_live_splunk_mcp_proof",
        "public_artifact_url_readback",
        "approved_url_writeback",
        "devpost_final_submission",
    }
    add_check(checks, f"Approval execution handoff sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Approval execution handoff status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Approval execution handoff ready {rel(json_path, root)}", payload.get("handoff_ready") is True, str(payload.get("handoff_ready")))
    add_check(checks, f"Approval execution handoff status conflict path {rel(json_path, root)}", status_conflict.get("path") == "reports/latest_status_conflict_audit.html", str(status_conflict.get("path")))
    add_check(checks, f"Approval execution handoff status conflict status {rel(json_path, root)}", status_conflict.get("status") == "ready_for_user_review", str(status_conflict.get("status")))
    add_check(checks, f"Approval execution handoff status conflict failed count {rel(json_path, root)}", status_conflict.get("failed_count") == 0, str(status_conflict.get("failed_count")))
    add_check(checks, f"Approval execution handoff status conflict count {rel(json_path, root)}", status_conflict.get("conflict_count") == 0, str(status_conflict.get("conflict_count")))
    add_check(checks, f"Approval execution handoff status conflict critical count {rel(json_path, root)}", status_conflict.get("critical_check_failed_count") == 0, str(status_conflict.get("critical_check_failed_count")))
    add_check(checks, f"Approval execution handoff status conflict readback {rel(json_path, root)}", "latest_status_conflict_audit" in local_preflight_readback and "conflict_count=0" in local_preflight_readback, local_preflight_readback)
    add_check(checks, f"Approval execution handoff phase keys {rel(json_path, root)}", expected.issubset(phase_keys), ", ".join(sorted(str(item) for item in phase_keys)))
    add_check(
        checks,
        f"Approval execution handoff minimum path {rel(json_path, root)}",
        minimum_path == [
            "local_preflight",
            "public_github_repository",
            "public_demo_video",
            "public_artifact_url_readback",
            "approved_url_writeback",
            "devpost_final_submission",
        ],
        ", ".join(str(item) for item in minimum_path),
    )
    add_check(
        checks,
        f"Approval execution handoff optional path {rel(json_path, root)}",
        optional_path == [
            "local_preflight",
            "public_github_repository",
            "public_demo_video",
            "optional_live_splunk_mcp_proof",
            "public_artifact_url_readback",
            "approved_url_writeback",
            "devpost_final_submission",
        ],
        ", ".join(str(item) for item in optional_path),
    )
    add_check(
        checks,
        f"Approval execution handoff optional Splunk phase {rel(json_path, root)}",
        optional_phase.get("status") == "optional_user_decision"
        and optional_phase.get("requires_user_approval") is True
        and "SPLUNK_MCP_RUNBOOK.md" in str(optional_phase.get("command_or_action", "")),
        json.dumps(optional_phase, ensure_ascii=False)[:800],
    )
    add_check(
        checks,
        f"Approval execution handoff public repo execute command {rel(json_path, root)}",
        public_repo_phase.get("primary_artifact") == "reports/latest_public_repo_publication_preflight.html"
        and "verify_public_repo_publication_gate.py" in public_repo_command
        and "Approve public GitHub publication for the clean agentops-control-tower candidate." in public_repo_command
        and "--git-user-name" in public_repo_command
        and "--git-user-email" in public_repo_command,
        public_repo_command,
    )
    add_check(
        checks,
        f"Approval execution handoff public video preflight command {rel(json_path, root)}",
        video_phase.get("primary_artifact") == "reports/latest_public_video_upload_preflight.html"
        and "verify_public_video_upload_gate.py" in video_command
        and "Approve recording and public upload of the Agentic Incident Command Center demo video." in video_command
        and "--screen-safety-confirmed" in video_command,
        video_command,
    )
    add_check(checks, f"Approval execution handoff missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Approval execution handoff external closed {rel(json_path, root)}", payload.get("external_actions_attempted") is False and payload.get("external_actions_completed") is False, f"attempted={payload.get('external_actions_attempted')} completed={payload.get('external_actions_completed')}")
    add_check(checks, f"Approval execution handoff final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    add_check(checks, f"Approval execution handoff URL gate {rel(json_path, root)}", payload.get("approved_public_urls_exists") is False, str(payload.get("approved_public_urls_exists")))


def check_splunk_mcp_command_plan(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_splunk_mcp_command_plan.html"
    md_path = root / "reports/latest_splunk_mcp_command_plan.md"
    json_path = root / "reports/latest_splunk_mcp_command_plan.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Splunk MCP command plan files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Live Splunk And MCP Proof Command Plan",
        "Commands After Approval",
        "manual: configure Splunk MCP Server",
        "build_splunk_mcp_proof_capture_manifest.py",
        "Explicit user approval is required",
        "does not create accounts, configure credentials, import data, install apps, connect MCP",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    commands = payload.get("commands", [])
    add_check(checks, f"Splunk MCP command plan sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Splunk MCP command plan status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Splunk MCP command plan command count {rel(json_path, root)}", len(commands) >= 10, str(len(commands)))
    add_check(checks, f"Splunk MCP command plan live proof gate {rel(json_path, root)}", payload.get("live_splunk_mcp_verified") is False, str(payload.get("live_splunk_mcp_verified")))


def check_splunk_mcp_proof_brief(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_splunk_mcp_proof_brief.html"
    md_path = root / "reports/latest_splunk_mcp_proof_brief.md"
    json_path = root / "reports/latest_splunk_mcp_proof_brief.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Splunk MCP proof brief files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Live Splunk/MCP Proof Brief",
        "Approval phrase",
        "Approve optional live Splunk and Splunk MCP proof using synthetic data only",
        "Proof Success Criteria",
        "Screen Safety Checks",
        "Stop Conditions",
        "Use verified-through-Splunk-MCP wording only after",
        "does not create accounts, configure credentials, import data, install apps, connect MCP",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    criteria = payload.get("proof_success_criteria", [])
    steps = payload.get("approval_steps", [])
    add_check(checks, f"Splunk MCP proof brief sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Splunk MCP proof brief status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Splunk MCP proof brief missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Splunk MCP proof brief success criteria {rel(json_path, root)}", len(criteria) >= 5, str(len(criteria)))
    add_check(checks, f"Splunk MCP proof brief approval steps {rel(json_path, root)}", len(steps) >= 6, str(len(steps)))
    add_check(checks, f"Splunk MCP proof brief live proof gate {rel(json_path, root)}", payload.get("live_splunk_mcp_verified") is False, str(payload.get("live_splunk_mcp_verified")))


def check_splunk_mcp_prompt_pack(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_splunk_mcp_prompt_pack.html"
    md_path = root / "reports/latest_splunk_mcp_prompt_pack.md"
    json_path = root / "reports/latest_splunk_mcp_prompt_pack.json"
    submission_path = root / "submission/SPLUNK_MCP_PROMPT_PACK.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, submission_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Splunk MCP prompt pack files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    submission_markdown = submission_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Splunk MCP Prompt Pack",
        "Root-Cause Priority Investigation",
        "Human-Approved Remediation Check",
        "Blast Radius Summary",
        "Executive Brief With Citations",
        "Safe Next Action Check",
        "evt-0006",
        "evt-0009",
        "does not create accounts, configure credentials",
    ]
    combined = "\n".join([plain_html, markdown, submission_markdown])
    missing = [item for item in required if item not in combined]
    prompts = payload.get("prompts", [])
    prompt_keys = {prompt.get("key") for prompt in prompts}
    expected = {
        "root_cause_priority",
        "remediation_approval",
        "blast_radius",
        "executive_brief",
        "safe_next_action",
    }
    all_prompts_have_spl = all(prompt.get("spl") for prompt in prompts)
    all_prompts_have_stop = all(prompt.get("stop_condition") for prompt in prompts)
    add_check(checks, f"Splunk MCP prompt pack sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Splunk MCP prompt pack status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Splunk MCP prompt pack missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Splunk MCP prompt pack prompt keys {rel(json_path, root)}", expected.issubset(prompt_keys), ", ".join(sorted(str(item) for item in prompt_keys)))
    add_check(checks, f"Splunk MCP prompt pack SPL coverage {rel(json_path, root)}", all_prompts_have_spl, "all prompts have SPL" if all_prompts_have_spl else "missing SPL")
    add_check(checks, f"Splunk MCP prompt pack stop conditions {rel(json_path, root)}", all_prompts_have_stop, "all prompts have stop conditions" if all_prompts_have_stop else "missing stop condition")
    add_check(checks, f"Splunk MCP prompt pack live proof gate {rel(json_path, root)}", payload.get("live_splunk_mcp_verified") is False and payload.get("external_actions_attempted") is False, f"live={payload.get('live_splunk_mcp_verified')} external={payload.get('external_actions_attempted')}")


def check_splunk_mcp_proof_capture_manifest(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_splunk_mcp_proof_capture_manifest.html"
    md_path = root / "reports/latest_splunk_mcp_proof_capture_manifest.md"
    json_path = root / "reports/latest_splunk_mcp_proof_capture_manifest.json"
    submission_path = root / "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, submission_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Splunk MCP proof capture manifest files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    submission_markdown = submission_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    combined = "\n".join([plain_html, markdown, submission_markdown])
    required = [
        "Splunk MCP Proof Capture Manifest",
        "Capture Slots",
        "approved_scope",
        "synthetic_import",
        "live_spl_queries",
        "mcp_assisted_answer",
        "claim_upgrade_validation",
        "Expected Final Readback",
        "Stop Conditions",
        "does not create accounts, configure credentials, import data, install apps, connect MCP",
    ]
    missing = [item for item in required if item not in combined]
    capture_slots = payload.get("capture_slots", [])
    slot_keys = {slot.get("key") for slot in capture_slots if isinstance(slot, dict)}
    expected_slots = {"approved_scope", "synthetic_import", "live_spl_queries", "splunk_app_dashboard", "mcp_assisted_answer", "claim_upgrade_validation"}
    add_check(checks, f"Splunk MCP proof capture manifest sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Splunk MCP proof capture manifest status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Splunk MCP proof capture manifest missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Splunk MCP proof capture manifest slots {rel(json_path, root)}", expected_slots.issubset(slot_keys), ", ".join(sorted(str(item) for item in slot_keys)))
    add_check(checks, f"Splunk MCP proof capture manifest live gate {rel(json_path, root)}", payload.get("live_splunk_mcp_verified") is False and payload.get("claim_upgrade_ready") is False, f"live={payload.get('live_splunk_mcp_verified')} claim={payload.get('claim_upgrade_ready')}")
    add_check(checks, f"Splunk MCP proof capture manifest pending state {rel(json_path, root)}", payload.get("captured_evidence_status") == "pending_user_approval", str(payload.get("captured_evidence_status")))


def check_submission_gate_ledger(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_submission_gate_ledger.html"
    md_path = root / "reports/latest_submission_gate_ledger.md"
    json_path = root / "reports/latest_submission_gate_ledger.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Submission gate ledger files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Submission Gate Ledger",
        "Public GitHub Repository",
        "Public Demo Video",
        "Optional Live Splunk / MCP Proof",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "Devpost Final Submission",
        "does not create a repo, upload a video, create accounts, configure credentials, write approved URLs, update Devpost, or submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    gate_keys = {item.get("key") for item in payload.get("gates", [])}
    expected = {
        "public_github_repository",
        "public_demo_video",
        "optional_live_splunk_mcp_proof",
        "devpost_final_submission",
    }
    add_check(checks, f"Submission gate ledger sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Submission gate ledger status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Submission gate ledger gate keys {rel(json_path, root)}", expected.issubset(gate_keys), ", ".join(sorted(str(item) for item in gate_keys)))
    add_check(checks, f"Submission gate ledger final submit gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    splunk_gate = next((item for item in payload.get("gates", []) if item.get("key") == "optional_live_splunk_mcp_proof"), {})
    splunk_paths = {item.get("path") for item in splunk_gate.get("evidence", [])}
    add_check(checks, f"Submission gate ledger Splunk MCP capture evidence {rel(json_path, root)}", "reports/latest_splunk_mcp_proof_capture_manifest.html" in splunk_paths and "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md" in splunk_paths, ", ".join(sorted(str(item) for item in splunk_paths)))


def check_submission_deadline_burndown(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_submission_deadline_burndown.html"
    md_path = root / "reports/latest_submission_deadline_burndown.md"
    json_path = root / "reports/latest_submission_deadline_burndown.json"
    submission_path = root / "submission/SUBMISSION_DEADLINE_BURNDOWN.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, submission_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Submission deadline burndown files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    submission_markdown = submission_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Submission Deadline Burndown",
        "Minimum Viable Submit Path",
        "Stretch Path",
        "2026-06-15 20:00 JST",
        "2026-06-16 01:00 JST",
        "public_github_repository",
        "public_demo_video",
        "reports/latest_public_video_upload_preflight.html",
        "optional_live_splunk_mcp_proof",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "approved_url_writeback",
        "devpost_final_submission",
        "Local validation source",
        "does not publish a repository, record or upload video, connect to Splunk",
    ]
    missing = [
        item
        for item in required
        if item not in plain_html and item not in markdown and item not in submission_markdown
    ]
    milestones = payload.get("milestones", [])
    milestone_keys = {item.get("key") for item in milestones}
    expected = {
        "public_github_repository",
        "public_demo_video",
        "optional_live_splunk_mcp_proof",
        "approved_url_writeback",
        "devpost_final_submission",
    }
    add_check(checks, f"Submission deadline burndown sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Submission deadline burndown status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Submission deadline burndown milestone keys {rel(json_path, root)}", expected.issubset(milestone_keys), ", ".join(sorted(str(item) for item in milestone_keys)))
    add_check(checks, f"Submission deadline burndown missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Submission deadline burndown final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    add_check(
        checks,
        f"Submission deadline burndown validation source {rel(json_path, root)}",
        payload.get("local_submission_status") != "missing"
        and payload.get("failed_count") != "missing"
        and payload.get("local_validation_source") in {"reports/latest_submission_validation.json", "reports/latest_final_go_no_go.json"},
        f"status={payload.get('local_submission_status')} failed_count={payload.get('failed_count')} source={payload.get('local_validation_source')}",
    )
    video_milestone = next((item for item in milestones if item.get("key") == "public_demo_video"), {})
    video_paths = {item.get("path") for item in video_milestone.get("evidence", [])}
    add_check(
        checks,
        f"Submission deadline burndown public video preflight evidence {rel(json_path, root)}",
        "reports/latest_public_video_upload_preflight.html" in video_paths,
        ", ".join(sorted(str(item) for item in video_paths)),
    )
    splunk_milestone = next((item for item in milestones if item.get("key") == "optional_live_splunk_mcp_proof"), {})
    splunk_paths = {item.get("path") for item in splunk_milestone.get("evidence", [])}
    add_check(checks, f"Submission deadline burndown Splunk MCP capture evidence {rel(json_path, root)}", "reports/latest_splunk_mcp_proof_capture_manifest.html" in splunk_paths and "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md" in splunk_paths, ", ".join(sorted(str(item) for item in splunk_paths)))


def check_submission_review_index(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_submission_review_index.html"
    md_path = root / "reports/latest_submission_review_index.md"
    json_path = root / "reports/latest_submission_review_index.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Submission review index files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Submission Review Index",
        "Start Here",
        "Submission deadline burndown",
        "Splunk Evidence",
        "Devpost Copy",
        "External Gates",
        "Validation",
        "does not publish a repository, record or upload video, connect to Splunk, write approved URLs, update Devpost, or submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    artifacts = payload.get("artifacts", [])
    add_check(checks, f"Submission review index sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Submission review index status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Submission review index missing artifacts {rel(json_path, root)}", payload.get("missing_artifacts") == [], str(payload.get("missing_artifacts")))
    add_check(checks, f"Submission review index artifact count {rel(json_path, root)}", len(artifacts) >= 25, str(len(artifacts)))
    add_check(checks, f"Submission review index final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))


def check_judge_quickstart(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_judge_quickstart.html"
    md_path = root / "reports/latest_judge_quickstart.md"
    json_path = root / "reports/latest_judge_quickstart.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Judge quickstart files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Judge Quickstart",
        "5-Minute Review Path",
        "Agentic Incident Command Center",
        "MCP Remediation Ledger",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "does not publish, upload, connect to Splunk, write approved URLs, update Devpost, or submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    evidence = payload.get("quick_review_items", [])
    add_check(checks, f"Judge quickstart sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Judge quickstart status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Judge quickstart missing artifacts {rel(json_path, root)}", payload.get("missing_artifacts") == [], str(payload.get("missing_artifacts")))
    add_check(checks, f"Judge quickstart evidence count {rel(json_path, root)}", len(evidence) >= 6, str(len(evidence)))
    add_check(checks, f"Judge quickstart final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    quick_paths = {item.get("path") for item in evidence}
    add_check(checks, f"Judge quickstart Splunk MCP capture evidence {rel(json_path, root)}", "reports/latest_splunk_mcp_proof_capture_manifest.html" in quick_paths, ", ".join(sorted(str(item) for item in quick_paths)))


def check_judge_scorecard(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_judge_scorecard.html"
    md_path = root / "reports/latest_judge_scorecard.md"
    json_path = root / "reports/latest_judge_scorecard.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Judge scorecard files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Judge Scorecard",
        "Stage One Pass/Fail Baseline",
        "Stage Two Scored Criteria",
        "MCP Bonus Claim Boundary",
        "Stage One Viability",
        "Stage Two Judging",
        "Bonus Alignment",
        "Technological Implementation",
        "Design",
        "Potential Impact",
        "Quality of the Idea",
        "Best Use of Splunk MCP Server",
        "Use verified-through-Splunk-MCP wording only after",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    criteria = payload.get("criteria", [])
    baseline = payload.get("stage_one_pass_fail_baseline", [])
    scored = set(payload.get("stage_two_scored_criteria", []))
    mcp_boundary = payload.get("mcp_bonus_claim_boundary", {})
    add_check(checks, f"Judge scorecard sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Judge scorecard status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Judge scorecard missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Judge scorecard criteria count {rel(json_path, root)}", len(criteria) >= 7, str(len(criteria)))
    add_check(checks, f"Judge scorecard ready count {rel(json_path, root)}", payload.get("ready_criteria_count") == payload.get("total_criteria_count"), f"{payload.get('ready_criteria_count')}/{payload.get('total_criteria_count')}")
    add_check(checks, f"Judge scorecard final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    add_check(checks, f"Judge scorecard Stage One pass/fail baseline {rel(json_path, root)}", len(baseline) >= 4 and payload.get("stage_one_pass_fail_ready") is True and all(item.get("ready") is True for item in baseline), f"items={len(baseline)} ready={payload.get('stage_one_pass_fail_ready')}")
    add_check(checks, f"Judge scorecard Stage Two scored criteria {rel(json_path, root)}", {"Technological Implementation", "Design", "Potential Impact", "Quality of the Idea"}.issubset(scored), ", ".join(sorted(scored)))
    add_check(checks, f"Judge scorecard MCP bonus claim boundary {rel(json_path, root)}", mcp_boundary.get("bonus_category") == "Best Use of Splunk MCP Server" and mcp_boundary.get("live_splunk_mcp_verified") is False and "verified through Splunk MCP Server" in mcp_boundary.get("blocked_claims_until_verified", []), json.dumps(mcp_boundary, ensure_ascii=False)[:800])
    add_check(checks, f"Judge scorecard MCP upgrade condition {rel(json_path, root)}", "Use verified-through-Splunk-MCP wording only after" in str(mcp_boundary.get("upgrade_condition", "")) and "live_splunk_mcp_verified=true" in str(mcp_boundary.get("upgrade_condition", "")), str(mcp_boundary.get("upgrade_condition", "")))
    scorecard_paths = {entry.get("path") for criterion in criteria for entry in criterion.get("evidence", [])}
    add_check(checks, f"Judge scorecard Splunk MCP capture evidence {rel(json_path, root)}", "reports/latest_splunk_mcp_proof_capture_manifest.html" in scorecard_paths, ", ".join(sorted(str(item) for item in scorecard_paths)))


def check_launch_decision_brief(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_launch_decision_brief.html"
    md_path = root / "reports/latest_launch_decision_brief.md"
    json_path = root / "reports/latest_launch_decision_brief.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Launch decision brief files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Launch Decision Brief",
        "Recommended Approval Order",
        "Public GitHub Repository",
        "reports/latest_public_repo_publication_preflight.html",
        "Public Demo Video",
        "reports/latest_public_video_upload_preflight.html",
        "Optional Live Splunk / MCP Proof",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "Approved URL Writeback",
        "Devpost Final Submission",
        "does not publish, upload, submit, create accounts, configure credentials, write approved URLs, or update Devpost",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    decisions = payload.get("decisions", [])
    ready_now = set(payload.get("ready_now", []))
    add_check(checks, f"Launch decision brief sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Launch decision brief status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Launch decision brief missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Launch decision brief decision count {rel(json_path, root)}", len(decisions) >= 5, str(len(decisions)))
    add_check(checks, f"Launch decision brief ready requests {rel(json_path, root)}", {"public_github_repository", "public_demo_video"}.issubset(ready_now), ", ".join(sorted(ready_now)))
    add_check(checks, f"Launch decision brief final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    repo_decision = next((item for item in decisions if item.get("key") == "public_github_repository"), {})
    repo_paths = {item.get("path") for item in repo_decision.get("evidence", [])}
    add_check(checks, f"Launch decision brief public repo preflight evidence {rel(json_path, root)}", "reports/latest_public_repo_publication_preflight.html" in repo_paths, ", ".join(sorted(str(item) for item in repo_paths)))
    video_decision = next((item for item in decisions if item.get("key") == "public_demo_video"), {})
    video_paths = {item.get("path") for item in video_decision.get("evidence", [])}
    add_check(checks, f"Launch decision brief public video preflight evidence {rel(json_path, root)}", "reports/latest_public_video_upload_preflight.html" in video_paths, ", ".join(sorted(str(item) for item in video_paths)))
    splunk_decision = next((item for item in decisions if item.get("key") == "optional_live_splunk_mcp_proof"), {})
    splunk_paths = {item.get("path") for item in splunk_decision.get("evidence", [])}
    add_check(checks, f"Launch decision brief Splunk MCP capture evidence {rel(json_path, root)}", "reports/latest_splunk_mcp_proof_capture_manifest.html" in splunk_paths and "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md" in splunk_paths, ", ".join(sorted(str(item) for item in splunk_paths)))


def check_next_approval_packet(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_next_approval_packet.html"
    md_path = root / "reports/latest_next_approval_packet.md"
    json_path = root / "reports/latest_next_approval_packet.json"
    submission_path = root / "submission/NEXT_APPROVAL_PACKET.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, submission_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Next approval packet files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    submission_markdown = submission_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Next Approval Packet",
        "Public GitHub Repository",
        "reports/latest_public_repo_publication_preflight.html",
        "Public Demo Video",
        "reports/latest_public_video_upload_preflight.html",
        "Optional Live Splunk / MCP Proof",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "Approved URL Writeback",
        "Devpost Final Submission",
        "Approve public GitHub publication",
        "Approve recording and public upload",
        "age_and_residence",
        "ownership_and_ip",
        "does not publish, upload, submit",
    ]
    combined = "\n".join([plain_html, markdown, submission_markdown])
    missing = [item for item in required if item not in combined]
    ready_now = set(payload.get("ready_now", []))
    add_check(checks, f"Next approval packet sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Next approval packet status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Next approval packet missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Next approval packet ready now {rel(json_path, root)}", {"public_github_repository", "public_demo_video"}.issubset(ready_now), ", ".join(sorted(ready_now)))
    add_check(checks, f"Next approval packet target {rel(json_path, root)}", payload.get("next_approval_target") == "public_github_repository", str(payload.get("next_approval_target")))
    add_check(checks, f"Next approval packet final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    add_check(checks, f"Next approval packet human confirmations {rel(json_path, root)}", int(payload.get("human_confirmation_required_count", 0)) >= 5, str(payload.get("human_confirmation_required_count")))
    repo_action = next((item for item in payload.get("actions", []) if item.get("key") == "public_github_repository"), {})
    repo_paths = {item.get("path") for item in repo_action.get("evidence", [])}
    add_check(checks, f"Next approval packet public repo preflight evidence {rel(json_path, root)}", "reports/latest_public_repo_publication_preflight.html" in repo_paths, ", ".join(sorted(str(item) for item in repo_paths)))
    video_action = next((item for item in payload.get("actions", []) if item.get("key") == "public_demo_video"), {})
    video_paths = {item.get("path") for item in video_action.get("evidence", [])}
    add_check(checks, f"Next approval packet public video preflight evidence {rel(json_path, root)}", "reports/latest_public_video_upload_preflight.html" in video_paths, ", ".join(sorted(str(item) for item in video_paths)))
    splunk_action = next((item for item in payload.get("actions", []) if item.get("key") == "optional_live_splunk_mcp_proof"), {})
    splunk_paths = {item.get("path") for item in splunk_action.get("evidence", [])}
    add_check(checks, f"Next approval packet Splunk MCP capture evidence {rel(json_path, root)}", "reports/latest_splunk_mcp_proof_capture_manifest.html" in splunk_paths and "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md" in splunk_paths, ", ".join(sorted(str(item) for item in splunk_paths)))


def check_approval_consistency_audit(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_approval_consistency_audit.html"
    md_path = root / "reports/latest_approval_consistency_audit.md"
    json_path = root / "reports/latest_approval_consistency_audit.json"
    user_gates_path = root / "submission/USER_APPROVAL_GATES.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, user_gates_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Approval consistency audit files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    user_gates = user_gates_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Approval Consistency Audit",
        "public_github_repository",
        "public_demo_video",
        "official Splunk MCP proof completed",
        "approved_url_writeback",
        "devpost_final_submission",
        "stale Splunk-first",
        "does not publish, upload, submit",
    ]
    combined = "\n".join([plain_html, markdown, user_gates])
    missing = [item for item in required if item not in combined]
    expected = payload.get("expected_order", [])
    ready_now = set(payload.get("ready_now", []))
    add_check(checks, f"Approval consistency audit sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Approval consistency audit status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Approval consistency audit failed count {rel(json_path, root)}", int(payload.get("failed_count", 1)) == 0, str(payload.get("failed_count")))
    add_check(checks, f"Approval consistency audit target {rel(json_path, root)}", payload.get("next_approval_target") == "public_github_repository", str(payload.get("next_approval_target")))
    add_check(checks, f"Approval consistency audit order {rel(json_path, root)}", expected[:4] == EXTERNAL_ACTION_ORDER, ", ".join(expected[:4]))
    add_check(checks, f"Approval consistency audit ready now {rel(json_path, root)}", {"public_github_repository", "public_demo_video"}.issubset(ready_now), ", ".join(sorted(ready_now)))


def check_content_rights_audit(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_content_rights_audit.html"
    md_path = root / "reports/latest_content_rights_audit.md"
    json_path = root / "reports/latest_content_rights_audit.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Content rights audit files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Content Rights And Asset Safety Audit",
        "Apache-2.0",
        "assets/dashboard_preview.png",
        "Bundled Audio/Video Media",
        "none",
        "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
        "Splunk and Devpost names are used only to describe the hackathon",
        "does not publish a repository, record or upload video, write approved URLs, update Devpost",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    assets = payload.get("assets", [])
    media = payload.get("bundled_audio_video_media", [])
    wording_scan = payload.get("wording_scan", {})
    screen_sources = payload.get("screen_safety_sources", [])
    add_check(checks, f"Content rights audit sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Content rights audit status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Content rights audit failed count {rel(json_path, root)}", int(payload.get("failed_count", 1)) == 0, str(payload.get("failed_count")))
    add_check(checks, f"Content rights audit license {rel(json_path, root)}", payload.get("license", {}).get("spdx") == "Apache-2.0", str(payload.get("license")))
    add_check(checks, f"Content rights audit asset count {rel(json_path, root)}", len(assets) == 1 and assets[0].get("path") == "assets/dashboard_preview.png", str(assets))
    add_check(checks, f"Content rights audit media count {rel(json_path, root)}", media == [], str(media))
    add_check(checks, f"Content rights audit wording scan {rel(json_path, root)}", wording_scan.get("clean") is True, str(wording_scan.get("hits")))
    add_check(checks, f"Content rights audit video gate {rel(json_path, root)}", payload.get("public_video_ready") is False, str(payload.get("public_video_ready")))
    add_check(checks, f"Content rights audit screen checklist source {rel(json_path, root)}", "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md" in screen_sources, ", ".join(screen_sources))


def check_eligibility_compliance_audit(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_eligibility_compliance_audit.html"
    md_path = root / "reports/latest_eligibility_compliance_audit.md"
    json_path = root / "reports/latest_eligibility_compliance_audit.json"
    checklist_path = root / "submission/HUMAN_CONFIRMATION_CHECKLIST.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, checklist_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Eligibility compliance audit files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    checklist = checklist_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Eligibility And Compliance Audit",
        "Human Confirmation Checklist",
        "Human Confirmation Required",
        "age_and_residence",
        "ownership_and_ip",
        "no_sponsor_support_conflict",
        "public_materials_in_english",
        "does not determine legal eligibility",
        "does not publish a repository, upload video, write approved URLs",
    ]
    combined = "\n".join([plain_html, markdown, checklist])
    missing = [item for item in required if item not in combined]
    automated = payload.get("automated_evidence", [])
    human_items = payload.get("human_confirmation_items", [])
    human_keys = [str(item.get("key", "")) for item in human_items]
    checklist_missing_keys = [key for key in human_keys if key and key not in checklist]
    checklist_unchecked_count = checklist.count("- [ ] `")
    add_check(checks, f"Eligibility compliance audit sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Eligibility compliance audit status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Eligibility compliance audit failed count {rel(json_path, root)}", int(payload.get("failed_count", 1)) == 0, str(payload.get("failed_count")))
    add_check(checks, f"Eligibility compliance audit automated evidence {rel(json_path, root)}", len(automated) >= 7 and all(item.get("status") == "pass" for item in automated), str([(item.get("key"), item.get("status")) for item in automated]))
    add_check(checks, f"Eligibility compliance audit human confirmations {rel(json_path, root)}", len(human_items) >= 5 and int(payload.get("human_confirmation_required_count", 0)) >= 5, str(payload.get("human_confirmation_required_count")))
    add_check(checks, f"Human confirmation checklist keys {rel(checklist_path, root)}", not checklist_missing_keys, "missing: " + ", ".join(checklist_missing_keys) if checklist_missing_keys else ", ".join(human_keys))
    add_check(checks, f"Human confirmation checklist pending state {rel(checklist_path, root)}", checklist_unchecked_count >= len(human_items) >= 5 and "Status: pending human confirmation" in checklist, f"unchecked={checklist_unchecked_count}")
    add_check(checks, f"Human confirmation checklist submit hold {rel(checklist_path, root)}", "Devpost final submission stays blocked" in checklist and "public repository and public demo video URLs are approved and verified" in checklist, "final submit hold checked")


def check_splunk_app_package(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_splunk_app_package_manifest.html"
    md_path = root / "reports/latest_splunk_app_package_manifest.md"
    json_path = root / "reports/latest_splunk_app_package_manifest.json"
    package_path = root / "dist/agentops-control-tower-splunk-app.spl"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, package_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Splunk app package files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Splunk App Package Manifest",
        "dist/agentops-control-tower-splunk-app.spl",
        "agentops_control_tower/default/app.conf",
        "agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
        "not installed, uploaded, published, connected to Splunk, or submitted",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    sha = str(payload.get("sha256", ""))
    add_check(checks, f"Splunk app package sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Splunk app package status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Splunk app package failed count {rel(json_path, root)}", int(payload.get("failed_count", 1)) == 0, str(payload.get("failed_count")))
    add_check(checks, f"Splunk app package sha256 {rel(json_path, root)}", len(sha) == 64, sha)
    add_check(checks, f"Splunk app package size {rel(package_path, root)}", package_path.stat().st_size > 1000, f"bytes={package_path.stat().st_size}")


def check_devpost_packet_html(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"Devpost packet HTML exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    plain = html.unescape(text)
    required = [
        "Devpost Submission Packet",
        "Agentic Incident Command Center",
        "Observability",
        "PENDING_USER_APPROVAL_PUBLIC_REPO_URL",
        "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL",
        "Claim Boundaries",
        "Final Gates",
    ]
    missing = [item for item in required if item not in plain]
    add_check(checks, f"Devpost packet HTML sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_devpost_final_copy(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_devpost_final_copy.html"
    md_path = root / "reports/latest_devpost_final_copy.md"
    json_path = root / "reports/latest_devpost_final_copy.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Devpost final copy files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Devpost Final Copy Packet",
        "Copy/Paste Sections",
        "PENDING_USER_APPROVAL_PUBLIC_REPO_URL",
        "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL",
        "Final Gate",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    built_with = payload.get("fields", {}).get("built_with", [])
    mcp_proof = read_optional_json(root / "reports/latest_splunk_mcp_proof_capture_manifest.json")
    live_mcp_verified = mcp_proof.get("live_splunk_mcp_verified") is True
    add_check(checks, f"Devpost final copy sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Devpost final copy status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(
        checks,
        f"Devpost built-with Splunk MCP gate {rel(json_path, root)}",
        live_mcp_verified or "Splunk MCP Server" not in built_with,
        f"live_mcp_verified={live_mcp_verified}; built_with={built_with}",
    )


def check_devpost_submit_command_plan(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_devpost_submit_command_plan.html"
    md_path = root / "reports/latest_devpost_submit_command_plan.md"
    json_path = root / "reports/latest_devpost_submit_command_plan.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Devpost submit command plan files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Devpost Final Submission Command Plan",
        "Commands After Approval",
        "Final submit preflight gate",
        "verify_devpost_final_submit_gate.py",
        "manual: press the Devpost submit button",
        "Explicit user approval is required",
        "does not log in, save a draft, press submit, update Devpost",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    commands = payload.get("commands", [])
    add_check(checks, f"Devpost submit command plan sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Devpost submit command plan status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Devpost submit command plan command count {rel(json_path, root)}", len(commands) >= 8, str(len(commands)))
    add_check(checks, f"Devpost submit command plan final gate {rel(json_path, root)}", isinstance(payload.get("final_submit_ready"), bool), str(payload.get("final_submit_ready")))


def check_devpost_final_submit_preflight(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_devpost_final_submit_preflight.html"
    md_path = root / "reports/latest_devpost_final_submit_preflight.md"
    json_path = root / "reports/latest_devpost_final_submit_preflight.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Devpost final submit preflight files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Devpost Final Submit Preflight",
        "Gate status",
        "Manual submit allowed",
        "Final submit ready",
        "Approval phrase accepted",
        "Safe Readback",
        "YYYY-MM-DD_devpost_final_submission_readback.md",
        "does not log in to Devpost, save a draft, press submit, update Devpost",
    ]
    combined = "\n".join([plain_html, markdown])
    missing = [item for item in required if item not in combined]
    safe = payload.get("devpost_final_submit_safe_readback", {})
    add_check(checks, f"Devpost final submit preflight sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Devpost final submit preflight status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Devpost final submit preflight blocks submit {rel(json_path, root)}", payload.get("manual_submit_allowed") is False and payload.get("gate_status") == "blocked_until_final_submit_ready", f"allowed={payload.get('manual_submit_allowed')} gate={payload.get('gate_status')}")
    add_check(checks, f"Devpost final submit preflight final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    add_check(checks, f"Devpost final submit preflight approval gate {rel(json_path, root)}", payload.get("approval_phrase_accepted") is False, str(payload.get("approval_phrase_accepted")))
    add_check(checks, f"Devpost final submit preflight no external action {rel(json_path, root)}", payload.get("external_actions_attempted") is False and payload.get("external_actions_completed") is False, f"attempted={payload.get('external_actions_attempted')} completed={payload.get('external_actions_completed')}")
    add_check(checks, f"Devpost final submit safe readback target {rel(json_path, root)}", safe.get("evidence_note_target") == "submission/post_action_evidence/YYYY-MM-DD_devpost_final_submission_readback.md", str(safe.get("evidence_note_target")))


def check_devpost_manual_fill_brief(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_devpost_manual_fill_brief.html"
    md_path = root / "reports/latest_devpost_manual_fill_brief.md"
    json_path = root / "reports/latest_devpost_manual_fill_brief.json"
    checklist_path = root / "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path, checklist_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Devpost manual fill brief files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    checklist = checklist_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Devpost Manual Fill And Readback Brief",
        "Core Field Fill Order",
        "Section Readback",
        "Final Readback Checks",
        "Stop Conditions",
        "PENDING_USER_APPROVAL_PUBLIC_REPO_URL",
        "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL",
        "does not log in, save a draft, press submit, update Devpost",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    checklist_required = [
        "Devpost Final Review Checklist",
        "Status: pending final Devpost review",
        "Observability",
        "PENDING_USER_APPROVAL_PUBLIC_REPO_URL",
        "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL",
        "reports/latest_devpost_final_copy.md",
        "submission/DEVPOST_FIELD_MAP.md",
        "submission/HUMAN_CONFIRMATION_CHECKLIST.md",
        "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md",
        "No live Splunk/MCP verification claim appears unless approved proof exists",
        "does not log in, save a draft, press submit, update Devpost",
        "Final Devpost submit stays blocked",
    ]
    checklist_missing = [item for item in checklist_required if item not in checklist]
    fields = payload.get("fields", [])
    sections = payload.get("sections", [])
    readback_checks = payload.get("readback_checks", [])
    stop_conditions = payload.get("stop_conditions", [])
    add_check(checks, f"Devpost manual fill brief sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Devpost manual fill brief status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Devpost manual fill brief missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Devpost manual fill brief field count {rel(json_path, root)}", len(fields) >= 9, str(len(fields)))
    add_check(checks, f"Devpost manual fill brief section count {rel(json_path, root)}", len(sections) >= 10, str(len(sections)))
    add_check(checks, f"Devpost manual fill brief readback count {rel(json_path, root)}", len(readback_checks) >= 8, str(len(readback_checks)))
    add_check(checks, f"Devpost manual fill brief stop count {rel(json_path, root)}", len(stop_conditions) >= 6, str(len(stop_conditions)))
    add_check(checks, f"Devpost manual fill brief final gate {rel(json_path, root)}", isinstance(payload.get("final_submit_ready"), bool), str(payload.get("final_submit_ready")))
    add_check(checks, f"Devpost final review checklist pointer {rel(json_path, root)}", payload.get("final_review_checklist") == "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md", str(payload.get("final_review_checklist")))
    add_check(checks, f"Devpost final review checklist sections {rel(checklist_path, root)}", not checklist_missing, "missing: " + ", ".join(checklist_missing) if checklist_missing else "all key sections present")
    add_check(checks, f"Devpost final review checklist pending state {rel(checklist_path, root)}", checklist.count("- [ ]") >= 10 and "Status: pending final Devpost review" in checklist, f"unchecked={checklist.count('- [ ]')}")


def check_post_action_evidence_brief(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_post_action_evidence_brief.html"
    md_path = root / "reports/latest_post_action_evidence_brief.md"
    json_path = root / "reports/latest_post_action_evidence_brief.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Post-action evidence brief files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Post-Action Evidence Brief",
        "Post-Action Evidence",
        "Final Readback Sequence",
        "Evidence Log Policy",
        "submission/post_action_evidence/",
        "YYYY-MM-DD_<action_key>_readback.md",
        "Evidence note target",
        "Safe readback source",
        "YYYY-MM-DD_public_github_repository_readback.md",
        "YYYY-MM-DD_public_demo_video_readback.md",
        "YYYY-MM-DD_approved_url_writeback_readback.md",
        "public_safe_readback block",
        "public_video_upload_safe_readback",
        "reports/latest_public_video_upload_preflight.json",
        "public_video_safe_readback",
        "Keep completed evidence notes private/local by default.",
        "Public GitHub Repository",
        "Public Demo Video",
        "Approved URL Writeback",
        "Optional Live Splunk / MCP Proof",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "Devpost Final Submission",
        "devpost_final_submit_safe_readback",
        "reports/latest_devpost_final_submit_preflight.json",
        "does not publish a repository, record or upload video, connect to Splunk",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    actions = payload.get("actions", [])
    actions_by_key = {str(item.get("key")): item for item in actions if isinstance(item, dict)}
    sequence = payload.get("final_readback_sequence", [])
    policy_payload = payload.get("evidence_log_policy", {})
    policy = policy_payload if isinstance(policy_payload, dict) else {}
    forbidden_content = {str(item) for item in policy.get("forbidden_content", [])}
    incomplete = set(payload.get("incomplete_actions", []))
    expected = {
        "public_github_repository",
        "public_demo_video",
        "approved_url_writeback",
        "optional_live_splunk_mcp_proof",
        "devpost_final_submission",
    }
    add_check(checks, f"Post-action evidence brief sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Post-action evidence brief status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Post-action evidence brief missing evidence {rel(json_path, root)}", payload.get("missing_evidence") == [], str(payload.get("missing_evidence")))
    add_check(checks, f"Post-action evidence brief action keys {rel(json_path, root)}", expected.issubset({item.get("key") for item in actions}), ", ".join(sorted(str(item.get("key")) for item in actions)))
    add_check(
        checks,
        f"Post-action evidence brief log directory policy {rel(json_path, root)}",
        policy.get("recommended_directory") == "submission/post_action_evidence/",
        str(policy.get("recommended_directory")),
    )
    add_check(
        checks,
        f"Post-action evidence brief log filename policy {rel(json_path, root)}",
        policy.get("filename_pattern") == "YYYY-MM-DD_<action_key>_readback.md",
        str(policy.get("filename_pattern")),
    )
    add_check(
        checks,
        f"Post-action evidence brief log forbidden content policy {rel(json_path, root)}",
        {"credentials", "local absolute paths", "private workspace material"}.issubset(forbidden_content),
        ", ".join(sorted(forbidden_content)),
    )
    approved_url_command = str(actions_by_key.get("approved_url_writeback", {}).get("readback_command", ""))
    add_check(
        checks,
        f"Post-action evidence brief URL writeback validation command {rel(json_path, root)}",
        "verify_public_artifact_urls.py" in approved_url_command
        and "prepare_submission_urls.py" in approved_url_command
        and "validate_submission_packet.py" in approved_url_command,
        approved_url_command,
    )
    expected_targets = {
        "public_github_repository": "submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md",
        "public_demo_video": "submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md",
        "optional_live_splunk_mcp_proof": "submission/post_action_evidence/YYYY-MM-DD_optional_live_splunk_mcp_proof_readback.md",
        "approved_url_writeback": "submission/post_action_evidence/YYYY-MM-DD_approved_url_writeback_readback.md",
        "devpost_final_submission": "submission/post_action_evidence/YYYY-MM-DD_devpost_final_submission_readback.md",
    }
    target_pairs = {
        key: str(actions_by_key.get(key, {}).get("evidence_note_target", ""))
        for key in expected_targets
    }
    add_check(
        checks,
        f"Post-action evidence brief note targets {rel(json_path, root)}",
        target_pairs == expected_targets,
        json.dumps(target_pairs, ensure_ascii=False),
    )
    safe_sources = "\n".join(str(item.get("safe_readback_source", "")) for item in actions if isinstance(item, dict))
    add_check(
        checks,
        f"Post-action evidence brief safe readback sources {rel(json_path, root)}",
        "public_safe_readback" in safe_sources
        and "public_video_upload_safe_readback" in safe_sources
        and "public_video_safe_readback" in safe_sources
        and "publish_public_repo_after_approval.py" in safe_sources
        and "latest_public_video_upload_preflight.json" in safe_sources
        and "latest_video_recording_preview.json" in safe_sources
        and "latest_public_artifact_url_readback.json" in safe_sources
        and "latest_devpost_final_submit_preflight.json" in safe_sources,
        safe_sources,
    )
    add_check(checks, f"Post-action evidence brief readback sequence {rel(json_path, root)}", len(sequence) >= 5, str(len(sequence)))
    add_check(checks, f"Post-action evidence brief completion gate {rel(json_path, root)}", isinstance(payload.get("post_action_evidence_ready"), bool), str(payload.get("post_action_evidence_ready")))
    splunk_action = next((item for item in actions if item.get("key") == "optional_live_splunk_mcp_proof"), {})
    capture_in_completion = any("Proof capture manifest" in str(item) for item in splunk_action.get("completion_evidence", []))
    capture_in_sequence = any("latest_splunk_mcp_proof_capture_manifest.html" in str(item) for item in sequence)
    add_check(checks, f"Post-action evidence brief Splunk MCP capture readback {rel(json_path, root)}", capture_in_completion and capture_in_sequence, f"completion={capture_in_completion} sequence={capture_in_sequence}")
    pending_ok = (
        payload.get("approved_public_urls_exists") is True
        or {"public_github_repository", "public_demo_video", "devpost_final_submission"}.issubset(incomplete)
    )
    add_check(checks, f"Post-action evidence brief pending externals {rel(json_path, root)}", pending_ok, ", ".join(sorted(incomplete)))


def check_post_action_evidence_log_template(root: Path, checks: list[Check]) -> None:
    path = root / "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md"
    if not path.exists():
        add_check(checks, f"Post-action evidence log template exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Post-Action Evidence Log Template",
        "Boundary",
        "Evidence Log Policy",
        "submission/post_action_evidence/",
        "YYYY-MM-DD_<action_key>_readback.md",
        "Preferred Evidence Note Targets",
        "Safe Readback Sources",
        "YYYY-MM-DD_public_github_repository_readback.md",
        "YYYY-MM-DD_approved_url_writeback_readback.md",
        "public_safe_readback",
        "public_video_upload_safe_readback",
        "reports/latest_public_video_upload_preflight.json",
        "public_video_safe_readback",
        "devpost_final_submit_safe_readback",
        "reports/latest_devpost_final_submit_preflight.json",
        "Keep completed evidence notes private/local by default.",
        "Evidence Log",
        "Public Repository Readback",
        "Public Video Readback",
        "URL Writeback Readback",
        "Optional Splunk / MCP Proof Readback",
        "Devpost Final Submit Readback",
        "Final Completion Criteria",
        "does not publish a repository, upload a video, connect to Splunk, configure MCP, write approved URLs, update Devpost, save a draft, press submit, or mark the submission complete",
        "PENDING_USER_APPROVAL",
        "PENDING_READBACK",
    ]
    missing = [item for item in required if item not in text]
    add_check(checks, f"Post-action evidence log template sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_official_source_freshness(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_official_source_freshness.html"
    md_path = root / "reports/latest_official_source_freshness.md"
    json_path = root / "reports/latest_official_source_freshness.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Official source freshness files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Official Source Freshness",
        "https://splunk.devpost.com/",
        "https://splunk.devpost.com/rules",
        "2026-06-04 JST",
        "Jun 15, 2026 @ 9:00am PDT",
        "Observability",
        "Demo video under 3 minutes",
        "Public open-source repository",
        "Architecture diagram",
        "Technological Implementation",
        "reports/latest_splunk_mcp_proof_capture_manifest.html",
        "does not log in to Devpost, save a draft, publish a repository, upload a video, write approved URLs, update Devpost, or submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    requirements = payload.get("requirements", [])
    source_urls = payload.get("source_urls", [])
    add_check(checks, f"Official source freshness sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Official source freshness status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Official source freshness failed count {rel(json_path, root)}", int(payload.get("failed_count", 1)) == 0, str(payload.get("failed_count")))
    add_check(checks, f"Official source freshness source count {rel(json_path, root)}", len(source_urls) >= 3, str(len(source_urls)))
    add_check(checks, f"Official source freshness requirement count {rel(json_path, root)}", len(requirements) >= 7, str(len(requirements)))
    add_check(checks, f"Official source freshness mapped terms {rel(json_path, root)}", all(item.get("ready") for item in requirements), ", ".join(item.get("key", "") for item in requirements if not item.get("ready")))
    bonus = next((item for item in requirements if item.get("key") == "bonus"), {})
    bonus_paths = {item.get("path") for item in bonus.get("local_evidence", [])}
    add_check(checks, f"Official source freshness Splunk MCP capture evidence {rel(json_path, root)}", "reports/latest_splunk_mcp_proof_capture_manifest.html" in bonus_paths, ", ".join(sorted(str(item) for item in bonus_paths)))


def check_release_integrity_manifest(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_release_integrity_manifest.html"
    md_path = root / "reports/latest_release_integrity_manifest.md"
    json_path = root / "reports/latest_release_integrity_manifest.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Release integrity manifest files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Release Integrity Manifest",
        "Artifact Integrity",
        "Release ZIP",
        "Publication Boundary",
        "does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    artifacts = payload.get("artifacts", [])
    checks_payload = payload.get("checks", [])
    release_zip = payload.get("release_zip", {})
    artifact_paths = {str(item.get("path")) for item in artifacts}
    public_candidate = (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()
    splunk_artifact = next((item for item in artifacts if item.get("path") == "dist/agentops-control-tower-splunk-app.spl"), {})
    add_check(checks, f"Release integrity manifest sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Release integrity manifest status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Release integrity manifest missing artifacts {rel(json_path, root)}", payload.get("missing_artifacts") == [], str(payload.get("missing_artifacts")))
    add_check(checks, f"Release integrity manifest failed count {rel(json_path, root)}", int(payload.get("failed_count", 1)) == 0, str(payload.get("failed_count")))
    add_check(checks, f"Release integrity manifest artifact count {rel(json_path, root)}", len(artifacts) >= 18, str(len(artifacts)))
    add_check(checks, f"Release integrity manifest check count {rel(json_path, root)}", len(checks_payload) >= 8, str(len(checks_payload)))
    add_check(checks, f"Release integrity manifest final gate {rel(json_path, root)}", payload.get("final_submit_ready") is False, str(payload.get("final_submit_ready")))
    add_check(checks, f"Release integrity manifest approved URL gate {rel(json_path, root)}", payload.get("approved_public_urls_exists") is False, str(payload.get("approved_public_urls_exists")))
    add_check(checks, f"Release integrity manifest Splunk package hash {rel(json_path, root)}", len(str(splunk_artifact.get("sha256", ""))) == 64, str(splunk_artifact.get("sha256", "")))
    add_check(checks, f"Release integrity manifest Splunk package artifact {rel(json_path, root)}", "dist/agentops-control-tower-splunk-app.spl" in artifact_paths, ", ".join(sorted(artifact_paths)))
    if public_candidate:
        add_check(checks, f"Release integrity manifest public candidate boundary {rel(json_path, root)}", payload.get("root_type") == "public_candidate", str(payload.get("root_type")))
    else:
        zip_sha = str(release_zip.get("sha256", ""))
        zip_count = release_zip.get("file_count")
        zip_path = root / str(release_zip.get("path", "release/agentops-control-tower-public-candidate.zip"))
        actual_sha = sha256_file(zip_path) if zip_path.exists() else ""
        add_check(checks, f"Release integrity manifest workspace boundary {rel(json_path, root)}", payload.get("root_type") == "workspace", str(payload.get("root_type")))
        add_check(checks, f"Release integrity manifest release zip hash {rel(json_path, root)}", release_zip.get("exists") is True and len(zip_sha) == 64, zip_sha)
        add_check(checks, f"Release integrity manifest release zip hash matches file {rel(json_path, root)}", zip_sha == actual_sha, f"manifest={zip_sha} actual={actual_sha}")
        add_check(checks, f"Release integrity manifest release zip count {rel(json_path, root)}", isinstance(zip_count, int) and zip_count > 0, str(zip_count))
        add_check(checks, f"Release integrity manifest release smoke {rel(json_path, root)}", release_zip.get("smoke_status") == "pass", str(release_zip.get("smoke_status")))


def check_status_conflict_audit(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_status_conflict_audit.html"
    md_path = root / "reports/latest_status_conflict_audit.md"
    json_path = root / "reports/latest_status_conflict_audit.json"
    missing_files = [rel(path, root) for path in [html_path, md_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Status conflict audit files", False, "missing: " + ", ".join(missing_files))
        return

    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Status Conflict Audit",
        "Critical Checks",
        "JSON files scanned",
        "Conflict count",
        "does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit",
    ]
    missing = [item for item in required if item not in plain_html and item not in markdown]
    scope_labels = {str(item.get("label", "")) for item in payload.get("scan_scopes", [])}
    public_candidate = (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()
    expected_label = "public_candidate" if public_candidate else "workspace"
    add_check(checks, f"Status conflict audit sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Status conflict audit status {rel(json_path, root)}", payload.get("status") == "ready_for_user_review", str(payload.get("status")))
    add_check(checks, f"Status conflict audit conflict count {rel(json_path, root)}", int(payload.get("conflict_count", 1)) == 0, str(payload.get("conflict_count")))
    add_check(checks, f"Status conflict audit critical failed count {rel(json_path, root)}", int(payload.get("critical_check_failed_count", 1)) == 0, str(payload.get("critical_check_failed_count")))
    add_check(checks, f"Status conflict audit failed count {rel(json_path, root)}", int(payload.get("failed_count", 1)) == 0, str(payload.get("failed_count")))
    add_check(checks, f"Status conflict audit JSON scan count {rel(json_path, root)}", int(payload.get("json_files_scanned", 0)) >= 20, str(payload.get("json_files_scanned")))
    add_check(checks, f"Status conflict audit scope label {rel(json_path, root)}", expected_label in scope_labels, ", ".join(sorted(scope_labels)))
    add_check(checks, f"Status conflict audit check count {rel(json_path, root)}", len(payload.get("checks", [])) >= 15, str(len(payload.get("checks", []))))


def check_go_no_go_html(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"Go/No-Go HTML exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    plain = html.unescape(text)
    required = [
        "Final Go/No-Go Review",
        "LOCAL GO / EXTERNAL NO-GO",
        "Pending URL Gates",
        "PENDING_USER_APPROVAL_PUBLIC_REPO_URL",
        "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL",
        "Recommended Order",
        "Public Candidate Evidence",
    ]
    missing = [item for item in required if item not in plain]
    add_check(checks, f"Go/No-Go HTML sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_zip_manifest_html(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"Zip manifest HTML exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Public Candidate Zip Manifest",
        "local_zip_ready_for_user_review",
        "release/agentops-control-tower-public-candidate.zip",
        "Publication Boundary",
        "Included Files",
    ]
    missing = [item for item in required if item not in text]
    add_check(checks, f"Zip manifest HTML sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_zip_file(root: Path, checks: list[Check]) -> None:
    path = root / "release" / "agentops-control-tower-public-candidate.zip"
    if not path.exists():
        add_check(checks, f"ZIP exists {rel(path, root)}", False, "missing")
        return
    ok = path.stat().st_size > 1000
    add_check(checks, f"ZIP size {rel(path, root)}", ok, f"bytes={path.stat().st_size}")


def check_release_zip_smoke(root: Path, checks: list[Check]) -> None:
    html_path = root / "reports/latest_release_zip_smoke_test.html"
    json_path = root / "reports/latest_release_zip_smoke_test.json"
    missing_files = [rel(path, root) for path in [html_path, json_path] if not path.exists()]
    if missing_files:
        add_check(checks, "Release zip smoke report files", False, "missing: " + ", ".join(missing_files))
        return
    plain_html = html.unescape(html_path.read_text(encoding="utf-8"))
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    required = [
        "Release Zip Smoke Test",
        "zip unit tests",
        "zip local SPL query pack",
        "zip approval consistency audit",
        "zip video readiness report",
        "zip video cue sheet",
        "zip video dry run",
        "zip video upload metadata",
        "zip external approval packet",
        "zip public repo metadata",
        "zip public repo publish brief",
        "zip public launch snapshot",
        "zip URL writeback dry run",
        "zip Splunk MCP proof brief",
        "zip Splunk MCP prompt pack",
        "zip Splunk MCP proof capture manifest",
        "zip submission URL apply plan",
        "zip submission gate ledger",
        "zip submission deadline burndown",
        "zip submission review index",
        "zip judge quickstart",
        "zip launch decision brief",
        "zip next approval packet",
        "zip content rights audit",
        "zip eligibility compliance audit",
        "zip Splunk app package",
        "zip official source freshness",
        "zip release integrity manifest",
        "zip Splunk app validation",
        "zip claim boundary validation",
        "zip submission URL validation",
        "zip Devpost manual fill brief",
        "zip post-action evidence brief",
    ]
    missing = [item for item in required if item not in plain_html]
    add_check(checks, f"Release zip smoke sections {rel(html_path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")
    add_check(checks, f"Release zip smoke status {rel(json_path, root)}", payload.get("status") == "pass", str(payload.get("status")))


def check_official_audit(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"Official audit exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Official Requirements Audit",
        "Devpost overview",
        "Demo video under 3 minutes",
        "Public open-source code repository",
        "Root architecture diagram",
        "Eligibility and compliance",
        "Splunk MCP Server bonus",
        "reports/latest_splunk_mcp_prompt_pack.html",
        "ready_for_user_review",
    ]
    missing = [item for item in required if item not in text]
    add_check(checks, f"Official audit sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_judging_alignment(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"Judging alignment exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Judging Alignment",
        "Stage One Pass/Fail Baseline",
        "pass/fail baseline",
        "Stage One Viability",
        "Technological Implementation",
        "Design",
        "Potential Impact",
        "Quality of the Idea",
        "Bonus Prize Alignment",
        "MCP Bonus Claim Boundary",
        "Use verified-through-Splunk-MCP wording only after",
        "live_splunk_mcp_verified=true",
        "reports/latest_splunk_mcp_prompt_pack.html",
    ]
    missing = [item for item in required if item not in text]
    add_check(checks, f"Judging alignment sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_launch_runbook(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"Launch runbook exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Submission Launch Runbook",
        "Preflight Commands",
        "Launch Sequence",
        "Claim Wording",
        "Decision Matrix",
        "Final Safety Gate",
        "scripts\\build_status_conflict_audit.py",
        "reports/latest_status_conflict_audit.html",
        "no stale failed statuses",
        "ready_for_user_review",
        "reports/latest_submission_deadline_burndown.html",
        "Splunk MCP Server",
    ]
    missing = [item for item in required if item not in text]
    add_check(checks, f"Launch runbook sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def check_review_qa(path: Path, root: Path, checks: list[Check]) -> None:
    if not path.exists():
        add_check(checks, f"Review Q&A exists {rel(path, root)}", False, "missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Submission Review Q&A",
        "Core Pitch",
        "Judge Questions",
        "Safe Copy",
        "Demo Answer Template",
        "Final Review Checklist",
        "designed for Splunk MCP Server",
        "live Splunk MCP integration",
    ]
    missing = [item for item in required if item not in text]
    add_check(checks, f"Review Q&A sections {rel(path, root)}", not missing, "missing: " + ", ".join(missing) if missing else "all key sections present")


def scan_files(root: Path, checks: list[Check], include_internal_scan: bool) -> None:
    internal_hits: list[str] = []
    secret_hits: list[str] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        path_rel = rel(path, root)
        if include_internal_scan:
            for pattern in INTERNAL_PATTERNS:
                if pattern.search(text):
                    internal_hits.append(f"{path_rel}:{pattern.pattern}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append(f"{path_rel}:{pattern.pattern}")
    if include_internal_scan:
        add_check(checks, "public candidate internal path scan", not internal_hits, "\n".join(internal_hits) if internal_hits else "no internal patterns")
    add_check(checks, f"secret-like pattern scan {root.name}", not secret_hits, "\n".join(secret_hits) if secret_hits else "no secret-like patterns")


def build_report(root: Path, checks: list[Check]) -> dict[str, Any]:
    failed = [check for check in checks if not check.passed]
    gate_summary = build_submission_gate_summary(root, local_checks_passed=not failed)
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "root": root.name,
        "local_checks_passed": not failed,
        "overall_status": "ready_for_user_review" if not failed else "needs_more_evidence",
        "final_submit_ready": gate_summary["final_submit_ready"],
        "approved_public_urls_exists": gate_summary["approved_public_urls_exists"],
        "url_validation_status": gate_summary["url_validation_status"],
        "pending_urls": gate_summary["pending_urls"],
        "post_action_evidence_ready": gate_summary["post_action_evidence_ready"],
        "pending_external_actions": gate_summary["pending_external_actions"],
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "external_gates_pending": gate_summary["external_gates_pending"],
        "submission_gate_summary": gate_summary,
        "next_action": gate_summary["next_action"],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_html(path: Path, report: dict[str, Any]) -> None:
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(check['name'])}</td>"
        f"<td>{html.escape(check['status'])}</td>"
        f"<td>{html.escape(check['detail'])}</td>"
        "</tr>"
        for check in report["checks"]
    )
    gates = "\n".join(f"<li>{html.escape(item)}</li>" for item in report["external_gates_pending"])
    pending_urls = ", ".join(report["pending_urls"]) if report["pending_urls"] else "none"
    pending_actions = ", ".join(report["pending_external_actions"]) if report["pending_external_actions"] else "none"
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentOps Submission Validation</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f6f8fb; color: #17202a; }}
    header {{ background: #17202a; color: #fff; padding: 28px 36px; border-bottom: 4px solid #127c76; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fff; border: 1px solid #dbe3ec; border-radius: 8px; padding: 18px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #dbe3ec; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ color: #5f6d7c; }}
    .pass {{ color: #127c76; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
    .summary td:first-child {{ width: 260px; color: #5f6d7c; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>AgentOps Submission Validation</h1>
    <p>Overall status: <span class="{html.escape('pass' if report['local_checks_passed'] else 'fail')}">{html.escape(report['overall_status'])}</span></p>
  </header>
  <main>
    <section>
      <h2>Submission Gate Summary</h2>
      <table class="summary">
        <tbody>
          <tr><td>Final submit ready</td><td>{html.escape(str(report['final_submit_ready']))}</td></tr>
          <tr><td>Approved public URLs file</td><td>{html.escape(str(report['approved_public_urls_exists']))}</td></tr>
          <tr><td>URL validation status</td><td>{html.escape(str(report['url_validation_status']))}</td></tr>
          <tr><td>Pending URLs</td><td>{html.escape(pending_urls)}</td></tr>
          <tr><td>Post-action evidence ready</td><td>{html.escape(str(report['post_action_evidence_ready']))}</td></tr>
          <tr><td>Pending external actions</td><td>{html.escape(pending_actions)}</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Local Checks</h2>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    <section>
      <h2>External Gates Still Pending</h2>
      <ul>{gates}</ul>
    </section>
    <section>
      <h2>Next Action</h2>
      <p>{html.escape(report['next_action'])}</p>
    </section>
  </main>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")


def validate(root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    public_candidate_root = (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()

    run_command("run local demo", [sys.executable, "prototype/agentops_control_tower.py", "run-demo"], root, checks)
    run_command("run local SPL query pack", [sys.executable, "scripts/run_local_spl_query_pack.py"], root, checks)
    run_command("build demo tour", [sys.executable, "scripts/build_demo_tour.py"], root, checks)
    run_command("build video readiness report", [sys.executable, "scripts/build_video_readiness_report.py"], root, checks)
    run_command("build video cue sheet", [sys.executable, "scripts/build_video_cue_sheet.py"], root, checks)
    run_command("build claim evidence matrix", [sys.executable, "scripts/build_claim_evidence_matrix.py"], root, checks)
    run_command("build Devpost submission packet", [sys.executable, "scripts/build_devpost_submission_packet.py"], root, checks)
    run_command("export Devpost final copy", [sys.executable, "scripts/export_devpost_final_copy.py"], root, checks)
    run_command("validate submission URLs", [sys.executable, "scripts/validate_submission_urls.py"], root, checks)
    run_command("build public artifact URL readback", [sys.executable, "scripts/verify_public_artifact_urls.py"], root, checks)
    run_command("prepare submission URL apply plan", [sys.executable, "scripts/prepare_submission_urls.py"], root, checks)
    run_command("build final Go/No-Go report", [sys.executable, "scripts/build_final_go_no_go_report.py"], root, checks)
    run_command("build public repo dry run", [sys.executable, "scripts/build_public_repo_dry_run.py"], root, checks)
    run_command("build publication command plan", [sys.executable, "scripts/build_publication_command_plan.py"], root, checks)
    run_command("build public repo metadata", [sys.executable, "scripts/build_public_repo_metadata.py"], root, checks)
    run_command("build public repo publish brief", [sys.executable, "scripts/build_public_repo_publish_brief.py"], root, checks)
    run_command("build public repo publication preflight", [sys.executable, "scripts/verify_public_repo_publication_gate.py"], root, checks)
    run_command("build external approval packet", [sys.executable, "scripts/build_external_approval_packet.py"], root, checks)
    run_command("build Devpost final submit preflight", [sys.executable, "scripts/verify_devpost_final_submit_gate.py"], root, checks)
    run_command("build Devpost submit command plan", [sys.executable, "scripts/build_devpost_submit_command_plan.py"], root, checks)
    run_command("build Devpost manual fill brief", [sys.executable, "scripts/build_devpost_manual_fill_brief.py"], root, checks)
    run_command("build post-action evidence brief", [sys.executable, "scripts/build_post_action_evidence_brief.py"], root, checks)
    run_command("build official source freshness", [sys.executable, "scripts/build_official_source_freshness.py"], root, checks)
    run_command("validate Splunk app candidate", [sys.executable, "scripts/validate_splunk_app.py"], root, checks)
    run_command("package Splunk app", [sys.executable, "scripts/package_splunk_app.py"], root, checks)
    run_command("validate claim boundaries", [sys.executable, "scripts/validate_claim_boundaries.py"], root, checks)
    run_command("build Splunk MCP command plan", [sys.executable, "scripts/build_splunk_mcp_command_plan.py"], root, checks)
    run_command("build Splunk MCP proof brief", [sys.executable, "scripts/build_splunk_mcp_proof_brief.py"], root, checks)
    run_command("build Splunk MCP prompt pack", [sys.executable, "scripts/build_splunk_mcp_prompt_pack.py"], root, checks)
    run_command("build Splunk MCP proof capture manifest", [sys.executable, "scripts/build_splunk_mcp_proof_capture_manifest.py"], root, checks)
    run_command("build submission gate ledger", [sys.executable, "scripts/build_submission_gate_ledger.py"], root, checks)
    run_command("build submission deadline burndown", [sys.executable, "scripts/build_submission_deadline_burndown.py"], root, checks)
    run_command("build judge quickstart", [sys.executable, "scripts/build_judge_quickstart.py"], root, checks)
    run_command("build judge scorecard", [sys.executable, "scripts/build_judge_scorecard.py"], root, checks)
    run_command("build SPAK autonomous review packet", [sys.executable, "scripts/build_spak_autonomous_review_packet.py"], root, checks)
    run_command("build launch decision brief", [sys.executable, "scripts/build_launch_decision_brief.py"], root, checks)
    run_command("build content rights audit", [sys.executable, "scripts/build_content_rights_audit.py"], root, checks)
    run_command("build video dry run", [sys.executable, "scripts/build_video_dry_run.py"], root, checks)
    run_command("build video recording preview", [sys.executable, "scripts/build_video_recording_preview.py"], root, checks)
    run_command("build video upload metadata", [sys.executable, "scripts/build_video_upload_metadata.py"], root, checks)
    run_command("build public video upload preflight", [sys.executable, "scripts/verify_public_video_upload_gate.py"], root, checks)
    run_command("build video command plan", [sys.executable, "scripts/build_video_command_plan.py"], root, checks)
    run_command("build submission review index", [sys.executable, "scripts/build_submission_review_index.py"], root, checks)
    run_command("build eligibility compliance audit", [sys.executable, "scripts/build_eligibility_compliance_audit.py"], root, checks)
    run_command("build URL writeback dry run", [sys.executable, "scripts/build_url_writeback_dry_run.py"], root, checks)
    run_command("build release integrity manifest", [sys.executable, "scripts/build_release_integrity_manifest.py"], root, checks)
    run_command("build next approval packet", [sys.executable, "scripts/build_next_approval_packet.py"], root, checks)
    run_command("build submission deadline burndown after next approval", [sys.executable, "scripts/build_submission_deadline_burndown.py"], root, checks)
    run_command("build approval consistency audit", [sys.executable, "scripts/build_approval_consistency_audit.py"], root, checks)
    if not public_candidate_root:
        run_command("build approval execution handoff", [sys.executable, "scripts/build_approval_execution_handoff.py"], root, checks)
    run_command("build status conflict audit", [sys.executable, "scripts/build_status_conflict_audit.py"], root, checks)
    run_command("build final video cue sheet", [sys.executable, "scripts/build_video_cue_sheet.py"], root, checks)
    check_required(root, PUBLIC_REQUIRED if public_candidate_root else ROOT_REQUIRED, "public candidate root" if public_candidate_root else "root", checks)
    if not public_candidate_root:
        check_final_submission_checklist(root, checks)
    py_compile_targets = ["prototype/agentops_control_tower.py", "scripts/build_demo_tour.py", "scripts/build_video_readiness_report.py", "scripts/build_video_command_plan.py", "scripts/build_video_cue_sheet.py", "scripts/build_video_dry_run.py", "scripts/build_video_recording_preview.py", "scripts/build_video_upload_metadata.py", "scripts/verify_public_video_upload_gate.py", "scripts/build_claim_evidence_matrix.py", "scripts/build_external_approval_packet.py", "scripts/build_devpost_submission_packet.py", "scripts/build_devpost_submit_command_plan.py", "scripts/verify_devpost_final_submit_gate.py", "scripts/build_devpost_manual_fill_brief.py", "scripts/build_post_action_evidence_brief.py", "scripts/build_official_source_freshness.py", "scripts/build_content_rights_audit.py", "scripts/build_eligibility_compliance_audit.py", "scripts/build_next_approval_packet.py", "scripts/build_approval_consistency_audit.py", "scripts/build_approval_execution_handoff.py", "scripts/build_public_launch_snapshot.py", "scripts/build_user_approval_brief_ja.py", "scripts/build_release_integrity_manifest.py", "scripts/build_status_conflict_audit.py", "scripts/build_final_go_no_go_report.py", "scripts/build_publication_command_plan.py", "scripts/build_public_repo_metadata.py", "scripts/build_public_repo_publish_brief.py", "scripts/build_public_repo_dry_run.py", "scripts/publish_public_repo_after_approval.py", "scripts/verify_public_repo_publication_gate.py", "scripts/build_url_writeback_dry_run.py", "scripts/build_splunk_mcp_command_plan.py", "scripts/build_splunk_mcp_proof_brief.py", "scripts/build_splunk_mcp_prompt_pack.py", "scripts/build_splunk_mcp_proof_capture_manifest.py", "scripts/build_submission_gate_ledger.py", "scripts/build_submission_deadline_burndown.py", "scripts/build_submission_review_index.py", "scripts/build_judge_quickstart.py", "scripts/build_judge_scorecard.py", "scripts/build_spak_autonomous_review_packet.py", "scripts/build_launch_decision_brief.py", "scripts/build_public_repo_candidate.py", "scripts/export_devpost_final_copy.py", "scripts/package_splunk_app.py", "scripts/package_public_candidate_zip.py", "scripts/prepare_submission_urls.py", "scripts/verify_public_artifact_urls.py", "scripts/run_local_spl_query_pack.py", "scripts/submission_urls.py", "scripts/smoke_test_release_zip.py", "scripts/validate_claim_boundaries.py", "scripts/validate_submission_urls.py", "scripts/validate_splunk_app.py", "scripts/validate_submission_packet.py"]
    if public_candidate_root:
        py_compile_targets = [
            target
            for target in py_compile_targets
            if target not in {"scripts/build_public_repo_candidate.py", "scripts/build_user_approval_brief_ja.py", "scripts/build_approval_execution_handoff.py"}
        ]
    run_command(
        "py_compile",
        [sys.executable, "-m", "py_compile", *py_compile_targets],
        root,
        checks,
    )
    remove_pycache(root)

    check_png(root / "assets/dashboard_preview.png", root, checks)
    check_html(root / "reports/latest_control_tower.html", root, checks)
    check_demo_tour_html(root / "reports/latest_demo_tour.html", root, checks)
    check_video_readiness(root, checks)
    check_video_command_plan(root, checks)
    check_video_cue_sheet(root, checks)
    check_video_dry_run(root, checks)
    check_video_recording_preview(root, checks)
    check_video_upload_metadata(root, checks)
    check_public_video_upload_preflight(root, checks)
    check_claim_evidence_matrix(root, checks)
    check_submission_url_apply_plan(root, checks)
    check_public_artifact_url_readback(root, checks)
    check_publication_command_plan(root, checks)
    check_public_repo_publication_preflight(root, checks)
    check_guarded_publication_helper_metadata(root, checks)
    check_public_repo_metadata(root, checks)
    check_public_repo_dry_run(root, checks)
    check_url_writeback_dry_run(root, checks)
    check_splunk_mcp_command_plan(root, checks)
    check_splunk_mcp_proof_brief(root, checks)
    check_splunk_mcp_prompt_pack(root, checks)
    check_splunk_mcp_proof_capture_manifest(root, checks)
    check_submission_gate_ledger(root, checks)
    check_submission_deadline_burndown(root, checks)
    check_submission_review_index(root, checks)
    check_judge_quickstart(root, checks)
    check_judge_scorecard(root, checks)
    check_launch_decision_brief(root, checks)
    check_next_approval_packet(root, checks)
    check_approval_consistency_audit(root, checks)
    check_content_rights_audit(root, checks)
    check_eligibility_compliance_audit(root, checks)
    check_splunk_app_package(root, checks)
    check_devpost_packet_html(root / "reports/latest_devpost_submission_packet.html", root, checks)
    check_devpost_final_copy(root, checks)
    check_devpost_final_submit_preflight(root, checks)
    check_devpost_submit_command_plan(root, checks)
    check_devpost_manual_fill_brief(root, checks)
    check_post_action_evidence_brief(root, checks)
    check_post_action_evidence_log_template(root, checks)
    check_local_spl_html(root / "reports/latest_local_spl_query_results.html", root, checks)
    check_official_audit(root / "submission/OFFICIAL_REQUIREMENTS_AUDIT.md", root, checks)
    check_judging_alignment(root / "submission/JUDGING_ALIGNMENT.md", root, checks)
    check_launch_runbook(root / "submission/SUBMISSION_LAUNCH_RUNBOOK.md", root, checks)
    check_review_qa(root / "submission/SUBMISSION_REVIEW_QA.md", root, checks)
    check_status_conflict_audit(root, checks)
    scan_files(root, checks, include_internal_scan=False)

    if not public_candidate_root:
        run_command("build public repo candidate", [sys.executable, "scripts/build_public_repo_candidate.py"], root, checks)
        candidate = root / "public_repo_candidate" / "agentops-control-tower"
        run_command("prime public candidate public repo dry run", [sys.executable, "scripts/build_public_repo_dry_run.py"], candidate, checks)
        run_command("prime public candidate publication command plan", [sys.executable, "scripts/build_publication_command_plan.py"], candidate, checks)
        run_command("prime public candidate public repo metadata", [sys.executable, "scripts/build_public_repo_metadata.py"], candidate, checks)
        run_command("prime public candidate public repo publish brief", [sys.executable, "scripts/build_public_repo_publish_brief.py"], candidate, checks)
        run_command("prime public candidate public repo publication preflight", [sys.executable, "scripts/verify_public_repo_publication_gate.py"], candidate, checks)
        run_command("prime public candidate external approval packet", [sys.executable, "scripts/build_external_approval_packet.py"], candidate, checks)
        run_command("prime public candidate launch decision brief", [sys.executable, "scripts/build_launch_decision_brief.py"], candidate, checks)
        run_command("prime public candidate next approval packet", [sys.executable, "scripts/build_next_approval_packet.py"], candidate, checks)
        run_command("prime public candidate approval consistency audit", [sys.executable, "scripts/build_approval_consistency_audit.py"], candidate, checks)
        run_command("prime public candidate public launch snapshot", [sys.executable, "scripts/build_public_launch_snapshot.py"], candidate, checks)
        run_command("prime public candidate submission deadline burndown", [sys.executable, "scripts/build_submission_deadline_burndown.py"], candidate, checks)
        run_command("package public candidate zip", [sys.executable, "scripts/package_public_candidate_zip.py"], root, checks)
        run_command("smoke test release zip", [sys.executable, "scripts/smoke_test_release_zip.py"], root, checks)
        check_zip_file(root, checks)
        check_release_zip_smoke(root, checks)
        check_zip_manifest_html(root / "reports/latest_public_candidate_zip_manifest.html", root, checks)
    run_command("refresh final Go/No-Go report", [sys.executable, "scripts/build_final_go_no_go_report.py"], root, checks)
    run_command("refresh external approval packet", [sys.executable, "scripts/build_external_approval_packet.py"], root, checks)
    run_command("refresh video cue sheet", [sys.executable, "scripts/build_video_cue_sheet.py"], root, checks)
    run_command("refresh video dry run", [sys.executable, "scripts/build_video_dry_run.py"], root, checks)
    run_command("refresh video recording preview", [sys.executable, "scripts/build_video_recording_preview.py"], root, checks)
    run_command("refresh video upload metadata", [sys.executable, "scripts/build_video_upload_metadata.py"], root, checks)
    run_command("refresh public video upload preflight", [sys.executable, "scripts/verify_public_video_upload_gate.py"], root, checks)
    run_command("refresh video command plan", [sys.executable, "scripts/build_video_command_plan.py"], root, checks)
    run_command("refresh claim evidence matrix", [sys.executable, "scripts/build_claim_evidence_matrix.py"], root, checks)
    run_command("refresh public repo dry run", [sys.executable, "scripts/build_public_repo_dry_run.py"], root, checks)
    run_command("refresh publication command plan", [sys.executable, "scripts/build_publication_command_plan.py"], root, checks)
    run_command("refresh public repo metadata", [sys.executable, "scripts/build_public_repo_metadata.py"], root, checks)
    run_command("refresh public repo publish brief", [sys.executable, "scripts/build_public_repo_publish_brief.py"], root, checks)
    run_command("refresh public repo publication preflight", [sys.executable, "scripts/verify_public_repo_publication_gate.py"], root, checks)
    run_command("refresh public artifact URL readback", [sys.executable, "scripts/verify_public_artifact_urls.py"], root, checks)
    run_command("refresh URL writeback dry run", [sys.executable, "scripts/build_url_writeback_dry_run.py"], root, checks)
    run_command("refresh Devpost final submit preflight", [sys.executable, "scripts/verify_devpost_final_submit_gate.py"], root, checks)
    run_command("refresh Devpost submit command plan", [sys.executable, "scripts/build_devpost_submit_command_plan.py"], root, checks)
    run_command("refresh Devpost manual fill brief", [sys.executable, "scripts/build_devpost_manual_fill_brief.py"], root, checks)
    run_command("refresh post-action evidence brief", [sys.executable, "scripts/build_post_action_evidence_brief.py"], root, checks)
    run_command("refresh Splunk MCP command plan", [sys.executable, "scripts/build_splunk_mcp_command_plan.py"], root, checks)
    run_command("refresh Splunk MCP proof brief", [sys.executable, "scripts/build_splunk_mcp_proof_brief.py"], root, checks)
    run_command("refresh Splunk MCP prompt pack", [sys.executable, "scripts/build_splunk_mcp_prompt_pack.py"], root, checks)
    run_command("refresh Splunk MCP proof capture manifest", [sys.executable, "scripts/build_splunk_mcp_proof_capture_manifest.py"], root, checks)
    run_command("refresh final external approval packet", [sys.executable, "scripts/build_external_approval_packet.py"], root, checks)
    run_command("refresh submission gate ledger", [sys.executable, "scripts/build_submission_gate_ledger.py"], root, checks)
    run_command("refresh submission deadline burndown", [sys.executable, "scripts/build_submission_deadline_burndown.py"], root, checks)
    run_command("refresh Splunk app package", [sys.executable, "scripts/package_splunk_app.py"], root, checks)
    run_command("refresh official source freshness", [sys.executable, "scripts/build_official_source_freshness.py"], root, checks)
    run_command("refresh content rights audit", [sys.executable, "scripts/build_content_rights_audit.py"], root, checks)
    run_command("refresh eligibility compliance audit", [sys.executable, "scripts/build_eligibility_compliance_audit.py"], root, checks)
    run_command("refresh launch decision brief", [sys.executable, "scripts/build_launch_decision_brief.py"], root, checks)
    run_command("refresh next approval packet", [sys.executable, "scripts/build_next_approval_packet.py"], root, checks)
    run_command("refresh submission deadline burndown after next approval", [sys.executable, "scripts/build_submission_deadline_burndown.py"], root, checks)
    run_command("refresh approval consistency audit", [sys.executable, "scripts/build_approval_consistency_audit.py"], root, checks)
    run_command("refresh public launch snapshot", [sys.executable, "scripts/build_public_launch_snapshot.py"], root, checks)
    if not public_candidate_root:
        run_command("refresh approval execution handoff", [sys.executable, "scripts/build_approval_execution_handoff.py"], root, checks)
    run_command("refresh release integrity manifest", [sys.executable, "scripts/build_release_integrity_manifest.py"], root, checks)
    run_command("refresh submission review index", [sys.executable, "scripts/build_submission_review_index.py"], root, checks)
    run_command("refresh judge quickstart", [sys.executable, "scripts/build_judge_quickstart.py"], root, checks)
    run_command("refresh judge scorecard", [sys.executable, "scripts/build_judge_scorecard.py"], root, checks)
    run_command("refresh SPAK autonomous review packet", [sys.executable, "scripts/build_spak_autonomous_review_packet.py"], root, checks)
    run_command("refresh final public repo publish brief", [sys.executable, "scripts/build_public_repo_publish_brief.py"], root, checks)
    run_command("refresh final public repo publication preflight", [sys.executable, "scripts/verify_public_repo_publication_gate.py"], root, checks)
    if not public_candidate_root:
        run_command("refresh Japanese user approval brief", [sys.executable, "scripts/build_user_approval_brief_ja.py"], root, checks)
    run_command("refresh status conflict audit", [sys.executable, "scripts/build_status_conflict_audit.py"], root, checks)
    run_command("root unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"], root, checks)
    check_go_no_go_html(root / "reports/latest_final_go_no_go.html", root, checks)
    check_external_approval_packet(root, checks)
    check_video_command_plan(root, checks)
    check_video_cue_sheet(root, checks)
    check_video_dry_run(root, checks)
    check_video_recording_preview(root, checks)
    check_video_upload_metadata(root, checks)
    check_public_video_upload_preflight(root, checks)
    check_claim_evidence_matrix(root, checks)
    check_publication_command_plan(root, checks)
    check_public_repo_publication_preflight(root, checks)
    check_guarded_publication_helper_metadata(root, checks)
    check_public_repo_metadata(root, checks)
    check_public_repo_publish_brief(root, checks)
    check_public_repo_dry_run(root, checks)
    check_public_artifact_url_readback(root, checks)
    check_url_writeback_dry_run(root, checks)
    check_splunk_mcp_command_plan(root, checks)
    check_splunk_mcp_proof_brief(root, checks)
    check_splunk_mcp_prompt_pack(root, checks)
    check_splunk_mcp_proof_capture_manifest(root, checks)
    check_submission_gate_ledger(root, checks)
    check_submission_deadline_burndown(root, checks)
    check_submission_review_index(root, checks)
    check_judge_quickstart(root, checks)
    check_judge_scorecard(root, checks)
    check_launch_decision_brief(root, checks)
    check_next_approval_packet(root, checks)
    check_approval_consistency_audit(root, checks)
    check_public_launch_snapshot(root, checks)
    if not public_candidate_root:
        check_user_approval_brief_ja(root, checks)
        check_approval_execution_handoff(root, checks)
    check_content_rights_audit(root, checks)
    check_eligibility_compliance_audit(root, checks)
    check_splunk_app_package(root, checks)
    check_devpost_final_submit_preflight(root, checks)
    check_devpost_submit_command_plan(root, checks)
    check_devpost_manual_fill_brief(root, checks)
    check_post_action_evidence_brief(root, checks)
    check_post_action_evidence_log_template(root, checks)
    check_official_source_freshness(root, checks)
    check_release_integrity_manifest(root, checks)
    check_status_conflict_audit(root, checks)
    if public_candidate_root:
        scan_files(root, checks, include_internal_scan=True)
        return build_report(root, checks)

    candidate = root / "public_repo_candidate" / "agentops-control-tower"
    check_required(candidate, PUBLIC_REQUIRED, "public candidate", checks)
    run_command("public candidate local SPL query pack", [sys.executable, "scripts/run_local_spl_query_pack.py"], candidate, checks)
    run_command("public candidate demo tour", [sys.executable, "scripts/build_demo_tour.py"], candidate, checks)
    run_command("public candidate video readiness report", [sys.executable, "scripts/build_video_readiness_report.py"], candidate, checks)
    run_command("public candidate video cue sheet", [sys.executable, "scripts/build_video_cue_sheet.py"], candidate, checks)
    run_command("public candidate claim evidence matrix", [sys.executable, "scripts/build_claim_evidence_matrix.py"], candidate, checks)
    run_command("public candidate public repo dry run", [sys.executable, "scripts/build_public_repo_dry_run.py"], candidate, checks)
    run_command("public candidate external approval packet", [sys.executable, "scripts/build_external_approval_packet.py"], candidate, checks)
    run_command("public candidate submission URL apply plan", [sys.executable, "scripts/prepare_submission_urls.py"], candidate, checks)
    run_command("public candidate public artifact URL readback", [sys.executable, "scripts/verify_public_artifact_urls.py"], candidate, checks)
    run_command("public candidate video dry run", [sys.executable, "scripts/build_video_dry_run.py"], candidate, checks)
    run_command("public candidate video recording preview", [sys.executable, "scripts/build_video_recording_preview.py"], candidate, checks)
    run_command("public candidate video upload metadata", [sys.executable, "scripts/build_video_upload_metadata.py"], candidate, checks)
    run_command("public candidate public video upload preflight", [sys.executable, "scripts/verify_public_video_upload_gate.py"], candidate, checks)
    run_command("public candidate video command plan", [sys.executable, "scripts/build_video_command_plan.py"], candidate, checks)
    run_command("public candidate publication command plan", [sys.executable, "scripts/build_publication_command_plan.py"], candidate, checks)
    run_command("public candidate public repo metadata", [sys.executable, "scripts/build_public_repo_metadata.py"], candidate, checks)
    run_command("public candidate public repo publish brief", [sys.executable, "scripts/build_public_repo_publish_brief.py"], candidate, checks)
    run_command("public candidate public repo publication preflight", [sys.executable, "scripts/verify_public_repo_publication_gate.py"], candidate, checks)
    run_command("public candidate URL writeback dry run", [sys.executable, "scripts/build_url_writeback_dry_run.py"], candidate, checks)
    run_command("public candidate Devpost submission packet", [sys.executable, "scripts/build_devpost_submission_packet.py"], candidate, checks)
    run_command("public candidate Devpost final copy", [sys.executable, "scripts/export_devpost_final_copy.py"], candidate, checks)
    run_command("public candidate submission URL validation", [sys.executable, "scripts/validate_submission_urls.py"], candidate, checks)
    run_command("public candidate final Go/No-Go report", [sys.executable, "scripts/build_final_go_no_go_report.py"], candidate, checks)
    run_command("public candidate Devpost final submit preflight", [sys.executable, "scripts/verify_devpost_final_submit_gate.py"], candidate, checks)
    run_command("public candidate Devpost submit command plan", [sys.executable, "scripts/build_devpost_submit_command_plan.py"], candidate, checks)
    run_command("public candidate Devpost manual fill brief", [sys.executable, "scripts/build_devpost_manual_fill_brief.py"], candidate, checks)
    run_command("public candidate post-action evidence brief", [sys.executable, "scripts/build_post_action_evidence_brief.py"], candidate, checks)
    run_command("public candidate Splunk app validation", [sys.executable, "scripts/validate_splunk_app.py"], candidate, checks)
    run_command("public candidate Splunk app package", [sys.executable, "scripts/package_splunk_app.py"], candidate, checks)
    run_command("public candidate claim boundary validation", [sys.executable, "scripts/validate_claim_boundaries.py"], candidate, checks)
    run_command("public candidate Splunk MCP command plan", [sys.executable, "scripts/build_splunk_mcp_command_plan.py"], candidate, checks)
    run_command("public candidate Splunk MCP proof brief", [sys.executable, "scripts/build_splunk_mcp_proof_brief.py"], candidate, checks)
    run_command("public candidate Splunk MCP prompt pack", [sys.executable, "scripts/build_splunk_mcp_prompt_pack.py"], candidate, checks)
    run_command("public candidate Splunk MCP proof capture manifest", [sys.executable, "scripts/build_splunk_mcp_proof_capture_manifest.py"], candidate, checks)
    run_command("public candidate final external approval packet", [sys.executable, "scripts/build_external_approval_packet.py"], candidate, checks)
    run_command("public candidate submission gate ledger", [sys.executable, "scripts/build_submission_gate_ledger.py"], candidate, checks)
    run_command("public candidate submission deadline burndown", [sys.executable, "scripts/build_submission_deadline_burndown.py"], candidate, checks)
    run_command("public candidate submission review index", [sys.executable, "scripts/build_submission_review_index.py"], candidate, checks)
    run_command("public candidate judge quickstart", [sys.executable, "scripts/build_judge_quickstart.py"], candidate, checks)
    run_command("public candidate judge scorecard", [sys.executable, "scripts/build_judge_scorecard.py"], candidate, checks)
    run_command("public candidate SPAK autonomous review packet", [sys.executable, "scripts/build_spak_autonomous_review_packet.py"], candidate, checks)
    run_command("public candidate launch decision brief", [sys.executable, "scripts/build_launch_decision_brief.py"], candidate, checks)
    run_command("public candidate content rights audit", [sys.executable, "scripts/build_content_rights_audit.py"], candidate, checks)
    run_command("public candidate eligibility compliance audit", [sys.executable, "scripts/build_eligibility_compliance_audit.py"], candidate, checks)
    run_command("public candidate next approval packet", [sys.executable, "scripts/build_next_approval_packet.py"], candidate, checks)
    run_command("public candidate submission deadline burndown after next approval", [sys.executable, "scripts/build_submission_deadline_burndown.py"], candidate, checks)
    run_command("public candidate approval consistency audit", [sys.executable, "scripts/build_approval_consistency_audit.py"], candidate, checks)
    run_command("public candidate public launch snapshot", [sys.executable, "scripts/build_public_launch_snapshot.py"], candidate, checks)
    run_command("public candidate unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"], candidate, checks)
    run_command("public candidate final video cue sheet", [sys.executable, "scripts/build_video_cue_sheet.py"], candidate, checks)
    run_command("public candidate final video dry run", [sys.executable, "scripts/build_video_dry_run.py"], candidate, checks)
    run_command("public candidate final video recording preview", [sys.executable, "scripts/build_video_recording_preview.py"], candidate, checks)
    run_command("public candidate final video upload metadata", [sys.executable, "scripts/build_video_upload_metadata.py"], candidate, checks)
    run_command("public candidate final public video upload preflight", [sys.executable, "scripts/verify_public_video_upload_gate.py"], candidate, checks)
    run_command("public candidate final public repo metadata", [sys.executable, "scripts/build_public_repo_metadata.py"], candidate, checks)
    run_command("public candidate final public repo publish brief", [sys.executable, "scripts/build_public_repo_publish_brief.py"], candidate, checks)
    run_command("public candidate final public repo publication preflight", [sys.executable, "scripts/verify_public_repo_publication_gate.py"], candidate, checks)
    run_command("public candidate package zip", [sys.executable, "scripts/package_public_candidate_zip.py"], candidate, checks)
    run_command("public candidate official source freshness", [sys.executable, "scripts/build_official_source_freshness.py"], candidate, checks)
    run_command("public candidate release integrity manifest", [sys.executable, "scripts/build_release_integrity_manifest.py"], candidate, checks)
    run_command("public candidate status conflict audit", [sys.executable, "scripts/build_status_conflict_audit.py"], candidate, checks)
    remove_pycache(candidate)
    check_png(candidate / "assets/dashboard_preview.png", candidate, checks)
    check_html(candidate / "reports/latest_control_tower.html", candidate, checks)
    check_demo_tour_html(candidate / "reports/latest_demo_tour.html", candidate, checks)
    check_video_readiness(candidate, checks)
    check_video_command_plan(candidate, checks)
    check_video_cue_sheet(candidate, checks)
    check_video_dry_run(candidate, checks)
    check_video_recording_preview(candidate, checks)
    check_video_upload_metadata(candidate, checks)
    check_public_video_upload_preflight(candidate, checks)
    check_claim_evidence_matrix(candidate, checks)
    check_external_approval_packet(candidate, checks)
    check_submission_url_apply_plan(candidate, checks)
    check_publication_command_plan(candidate, checks)
    check_public_repo_publication_preflight(candidate, checks)
    check_guarded_publication_helper_metadata(candidate, checks)
    check_public_repo_metadata(candidate, checks)
    check_public_repo_publish_brief(candidate, checks)
    check_public_repo_dry_run(candidate, checks)
    check_public_artifact_url_readback(candidate, checks)
    check_url_writeback_dry_run(candidate, checks)
    check_splunk_mcp_command_plan(candidate, checks)
    check_splunk_mcp_proof_brief(candidate, checks)
    check_splunk_mcp_prompt_pack(candidate, checks)
    check_splunk_mcp_proof_capture_manifest(candidate, checks)
    check_submission_gate_ledger(candidate, checks)
    check_submission_deadline_burndown(candidate, checks)
    check_submission_review_index(candidate, checks)
    check_judge_quickstart(candidate, checks)
    check_judge_scorecard(candidate, checks)
    check_launch_decision_brief(candidate, checks)
    check_next_approval_packet(candidate, checks)
    check_approval_consistency_audit(candidate, checks)
    check_public_launch_snapshot(candidate, checks)
    check_content_rights_audit(candidate, checks)
    check_eligibility_compliance_audit(candidate, checks)
    check_splunk_app_package(candidate, checks)
    check_devpost_packet_html(candidate / "reports/latest_devpost_submission_packet.html", candidate, checks)
    check_devpost_final_copy(candidate, checks)
    check_devpost_final_submit_preflight(candidate, checks)
    check_devpost_submit_command_plan(candidate, checks)
    check_devpost_manual_fill_brief(candidate, checks)
    check_post_action_evidence_brief(candidate, checks)
    check_post_action_evidence_log_template(candidate, checks)
    check_official_source_freshness(candidate, checks)
    check_release_integrity_manifest(candidate, checks)
    check_status_conflict_audit(candidate, checks)
    check_go_no_go_html(candidate / "reports/latest_final_go_no_go.html", candidate, checks)
    check_zip_file(candidate, checks)
    check_zip_manifest_html(candidate / "reports/latest_public_candidate_zip_manifest.html", candidate, checks)
    check_local_spl_html(candidate / "reports/latest_local_spl_query_results.html", candidate, checks)
    check_official_audit(candidate / "submission/OFFICIAL_REQUIREMENTS_AUDIT.md", candidate, checks)
    check_judging_alignment(candidate / "submission/JUDGING_ALIGNMENT.md", candidate, checks)
    check_launch_runbook(candidate / "submission/SUBMISSION_LAUNCH_RUNBOOK.md", candidate, checks)
    check_review_qa(candidate / "submission/SUBMISSION_REVIEW_QA.md", candidate, checks)
    cleanup_public_candidate_package_artifacts(candidate, checks)
    scan_files(candidate, checks, include_internal_scan=True)
    run_command("final root release integrity manifest readback", [sys.executable, "scripts/build_release_integrity_manifest.py"], root, checks)
    run_command("final root public launch snapshot readback", [sys.executable, "scripts/build_public_launch_snapshot.py"], root, checks)
    run_command("final root Japanese user approval brief readback", [sys.executable, "scripts/build_user_approval_brief_ja.py"], root, checks)
    run_command("final root status conflict audit readback", [sys.executable, "scripts/build_status_conflict_audit.py"], root, checks)
    check_release_integrity_manifest(root, checks)
    check_public_launch_snapshot(root, checks)
    check_user_approval_brief_ja(root, checks)
    check_status_conflict_audit(root, checks)

    return build_report(root, checks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Agentic Incident Command Center submission packet.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = validate(root)
    write_json(root / "reports" / "latest_submission_validation.json", report)
    write_html(root / "reports" / "latest_submission_validation.html", report)
    print(json.dumps({
        "overall_status": report["overall_status"],
        "failed_count": report["failed_count"],
        "final_submit_ready": report["final_submit_ready"],
        "approved_public_urls_exists": report["approved_public_urls_exists"],
        "pending_external_actions": report["pending_external_actions"],
    }, indent=2))
    return 0 if report["local_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
