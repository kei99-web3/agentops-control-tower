import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CANDIDATE_ROOT = (ROOT / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()

EXPECTED_ORDER = [
    "public_github_repository",
    "public_demo_video",
    "optional_live_splunk_mcp_proof",
    "approved_url_writeback",
    "devpost_final_submission",
]

PUBLIC_README_GENERATED_PATHS = {
    "release/agentops-control-tower-public-candidate.zip",
    "reports/latest_public_candidate_zip_manifest.html",
    "reports/latest_public_candidate_zip_manifest.json",
    "reports/latest_public_repo_dry_run.html",
    "reports/latest_public_repo_dry_run.json",
    "reports/latest_public_repo_dry_run.md",
    "reports/latest_release_zip_smoke_test.html",
    "reports/latest_release_zip_smoke_test.json",
    "reports/latest_submission_validation.html",
    "reports/latest_submission_validation.json",
    "reports/latest_status_conflict_audit.html",
    "reports/latest_status_conflict_audit.json",
    "reports/latest_status_conflict_audit.md",
    "reports/latest_url_writeback_dry_run.html",
    "reports/latest_url_writeback_dry_run.json",
    "reports/latest_url_writeback_dry_run.md",
    "reports/latest_video_dry_run.html",
    "reports/latest_video_dry_run.json",
    "reports/latest_video_dry_run.md",
}

PUBLIC_REPO_APPROVAL = "Approve public GitHub publication for the clean agentops-control-tower candidate."
PUBLIC_VIDEO_APPROVAL = "Approve recording and public upload of the Agentic Incident Command Center demo video."
OPTIONAL_SPLUNK_MCP_APPROVAL = "Approve optional live Splunk and Splunk MCP proof using synthetic data only."
DEVPOST_FINAL_APPROVAL = "Approve final Devpost submission for Agentic Incident Command Center."


def read_json(rel_path: str) -> dict:
    path = ROOT / rel_path
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class SubmissionSafetyBoundaryTest(unittest.TestCase):
    def test_public_launch_snapshot_keeps_external_gates_closed(self) -> None:
        payload = read_json("reports/latest_public_launch_snapshot.json")
        evidence_paths = {item["path"] for item in payload["evidence"]}

        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["failed_count"], 0)
        self.assertEqual(payload["expected_order"], EXPECTED_ORDER)
        self.assertEqual(payload["next_approval_target"], "public_github_repository")
        self.assertEqual(payload["ready_now"], ["public_github_repository", "public_demo_video"])
        self.assertFalse(payload["final_submit_ready"])
        self.assertFalse(payload["approved_public_urls_exists"])
        self.assertIn("reports/latest_public_repo_publication_preflight.html", evidence_paths)
        self.assertEqual(payload["public_repo"]["publication_preflight_status"], "ready_for_user_review")
        self.assertEqual(payload["public_repo"]["publication_preflight_gate_status"], "blocked_by_public_repo_approval_gate")
        self.assertFalse(payload["public_repo"]["publication_preflight_allowed"])
        self.assertIn("reports/latest_public_video_upload_preflight.html", evidence_paths)
        self.assertEqual(payload["public_video"]["upload_preflight_status"], "ready_for_user_review")
        self.assertEqual(payload["public_video"]["upload_preflight_gate_status"], "blocked_by_video_approval_gate")
        self.assertFalse(payload["public_video"]["upload_preflight_allowed"])

        boundary = payload["boundary"]
        for text in [
            "does not publish",
            "record or upload video",
            "connect to Splunk",
            "configure MCP",
            "write approved URLs",
            "update Devpost",
            "press submit",
        ]:
            self.assertIn(text, boundary)

    def test_approval_phrases_are_explicit_and_stable(self) -> None:
        snapshot = read_json("reports/latest_public_launch_snapshot.json")
        next_packet = read_json("reports/latest_next_approval_packet.json")
        actions = {action["key"]: action for action in next_packet["actions"]}

        self.assertEqual(snapshot["approval_phrases"]["public_github_repository"], PUBLIC_REPO_APPROVAL)
        self.assertEqual(snapshot["approval_phrases"]["public_demo_video"], PUBLIC_VIDEO_APPROVAL)
        self.assertEqual(snapshot["approval_phrases"]["optional_live_splunk_mcp_proof"], OPTIONAL_SPLUNK_MCP_APPROVAL)
        self.assertEqual(actions["public_github_repository"]["approval_phrase"], PUBLIC_REPO_APPROVAL)
        self.assertEqual(actions["public_demo_video"]["approval_phrase"], PUBLIC_VIDEO_APPROVAL)
        self.assertEqual(actions["optional_live_splunk_mcp_proof"]["approval_phrase"], OPTIONAL_SPLUNK_MCP_APPROVAL)

    def test_next_approval_packet_uses_ready_local_submission_snapshot(self) -> None:
        next_packet = read_json("reports/latest_next_approval_packet.json")
        markdown = (ROOT / "reports/latest_next_approval_packet.md").read_text(encoding="utf-8")

        self.assertEqual(next_packet["local_submission_status"], "ready_for_user_review")
        self.assertEqual(next_packet["local_submission_failed_count"], 0)
        self.assertIn(
            next_packet["local_submission_source"],
            {"reports/latest_submission_validation.json", "reports/latest_final_go_no_go.json"},
        )
        self.assertIn("Local submission status: ready_for_user_review / failed_count 0", markdown)

    def test_release_integrity_uses_ready_local_submission_snapshot(self) -> None:
        if PUBLIC_CANDIDATE_ROOT:
            self.skipTest("workspace-level validation source is private-workspace-only")

        release = read_json("reports/latest_release_integrity_manifest.json")
        markdown = (ROOT / "reports/latest_release_integrity_manifest.md").read_text(encoding="utf-8")

        self.assertEqual(release["validation_status"], "ready_for_user_review")
        self.assertEqual(release["validation_failed_count"], 0)
        self.assertIn(
            release["validation_source"],
            {"reports/latest_submission_validation.json", "reports/latest_final_go_no_go.json"},
        )
        self.assertIn("Validation source:", markdown)

    def test_status_conflict_audit_has_no_stale_failure_states(self) -> None:
        payload = read_json("reports/latest_status_conflict_audit.json")
        markdown = (ROOT / "reports/latest_status_conflict_audit.md").read_text(encoding="utf-8")
        labels = {item["label"] for item in payload["scan_scopes"]}

        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["conflict_count"], 0)
        self.assertEqual(payload["critical_check_failed_count"], 0)
        self.assertEqual(payload["failed_count"], 0)
        self.assertGreaterEqual(payload["json_files_scanned"], 20)
        self.assertIn("Status Conflict Audit", markdown)
        self.assertIn("does not publish, upload, connect to Splunk", payload["boundary"])
        self.assertIn("public_candidate" if PUBLIC_CANDIDATE_ROOT else "workspace", labels)
        if not PUBLIC_CANDIDATE_ROOT:
            self.assertIn("public_candidate", labels)

    def test_japanese_approval_brief_has_decision_matrix(self) -> None:
        if PUBLIC_CANDIDATE_ROOT:
            self.skipTest("Japanese user approval brief is private-workspace-only")

        brief = read_json("reports/latest_user_approval_brief_ja.json")
        release = read_json("reports/latest_release_integrity_manifest.json")
        status_conflict = read_json("reports/latest_status_conflict_audit.json")
        markdown = (ROOT / "reports/latest_user_approval_brief_ja.md").read_text(encoding="utf-8")
        decisions = {item["key"]: item for item in brief["approval_decision_matrix"]}

        self.assertEqual(set(decisions), set(EXPECTED_ORDER))
        self.assertEqual(decisions["public_github_repository"]["decision"], "今すぐ承認可")
        self.assertEqual(decisions["public_demo_video"]["decision"], "今すぐ承認可")
        self.assertEqual(decisions["optional_live_splunk_mcp_proof"]["decision"], "任意・後段判断")
        self.assertEqual(decisions["approved_url_writeback"]["decision"], "まだ承認しない")
        self.assertEqual(decisions["devpost_final_submission"]["decision"], "まだ承認しない")
        self.assertIn(PUBLIC_REPO_APPROVAL, decisions["public_github_repository"]["approval_phrase"])
        self.assertIn(PUBLIC_VIDEO_APPROVAL, decisions["public_demo_video"]["approval_phrase"])
        self.assertIn("URL反映とDevpost最終提出はまだ承認しない", brief["recommended_next_reply_ja"])
        self.assertIn("## 承認可否マトリクス", markdown)
        self.assertIn("承認後にCodexが行うこと", markdown)
        self.assertIn("公開用git identity", markdown)
        self.assertIn("## このChatでの返答例", markdown)
        self.assertEqual(brief["reply_examples"][0]["text"], PUBLIC_REPO_APPROVAL)
        self.assertIn(PUBLIC_REPO_APPROVAL, brief["reply_examples"][1]["text"])
        self.assertIn(PUBLIC_VIDEO_APPROVAL, brief["reply_examples"][1]["text"])
        self.assertEqual(brief["release_zip"]["sha256"], release["release_zip"]["sha256"])
        self.assertEqual(brief["release_zip"]["file_count"], release["release_zip"]["file_count"])
        self.assertEqual(brief["status_conflict_audit"]["path"], "reports/latest_status_conflict_audit.html")
        self.assertEqual(brief["status_conflict_audit"]["status"], status_conflict["status"])
        self.assertEqual(brief["status_conflict_audit"]["failed_count"], 0)
        self.assertEqual(brief["status_conflict_audit"]["conflict_count"], 0)
        self.assertEqual(brief["status_conflict_audit"]["critical_check_failed_count"], 0)
        self.assertEqual(brief["status_conflict_audit"]["json_files_scanned"], status_conflict["json_files_scanned"])
        self.assertIn("状態衝突監査", markdown)
        self.assertIn("latest_status_conflict_audit", markdown)
        self.assertIn("まだ承認しない", markdown)

    def test_splunk_mcp_capture_manifest_is_in_approval_path(self) -> None:
        expected = {
            "reports/latest_splunk_mcp_proof_capture_manifest.html",
            "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md",
        }
        public_video_expected = "reports/latest_public_video_upload_preflight.html"
        next_packet = read_json("reports/latest_next_approval_packet.json")
        launch = read_json("reports/latest_launch_decision_brief.json")
        external = read_json("reports/latest_external_approval_packet.json")
        gate_ledger = read_json("reports/latest_submission_gate_ledger.json")
        burndown = read_json("reports/latest_submission_deadline_burndown.json")
        scorecard = read_json("reports/latest_judge_scorecard.json")
        quickstart = read_json("reports/latest_judge_quickstart.json")
        post_action = read_json("reports/latest_post_action_evidence_brief.json")

        next_action = {item["key"]: item for item in next_packet["actions"]}["optional_live_splunk_mcp_proof"]
        next_video = {item["key"]: item for item in next_packet["actions"]}["public_demo_video"]
        launch_action = {item["key"]: item for item in launch["decisions"]}["optional_live_splunk_mcp_proof"]
        launch_video = {item["key"]: item for item in launch["decisions"]}["public_demo_video"]
        external_action = next(item for item in external["approval_requests"] if item["title"] == "Optional Live Splunk / MCP Proof")
        external_video = next(item for item in external["approval_requests"] if item["key"] == "public_demo_video")
        gate = {item["key"]: item for item in gate_ledger["gates"]}["optional_live_splunk_mcp_proof"]
        milestone = {item["key"]: item for item in burndown["milestones"]}["optional_live_splunk_mcp_proof"]
        post_action_item = {item["key"]: item for item in post_action["actions"]}["optional_live_splunk_mcp_proof"]

        evidence_sets = [
            {item["path"] for item in next_action["evidence"]},
            {item["path"] for item in launch_action["evidence"]},
            {item["path"] for item in external_action["evidence"]},
            {item["path"] for item in gate["evidence"]},
            {item["path"] for item in milestone["evidence"]},
        ]
        for evidence_paths in evidence_sets:
            self.assertTrue(expected.issubset(evidence_paths))
        self.assertIn(public_video_expected, {item["path"] for item in next_video["evidence"]})
        self.assertIn(public_video_expected, {item["path"] for item in launch_video["evidence"]})
        self.assertIn(public_video_expected, {item["path"] for item in external_video["evidence"]})

        scorecard_paths = {item["path"] for criterion in scorecard["criteria"] for item in criterion["evidence"]}
        quickstart_paths = {item["path"] for item in quickstart["quick_review_items"]}
        self.assertIn("reports/latest_splunk_mcp_proof_capture_manifest.html", scorecard_paths)
        self.assertIn("reports/latest_splunk_mcp_proof_capture_manifest.html", quickstart_paths)
        self.assertEqual(post_action_item["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_optional_live_splunk_mcp_proof_readback.md")
        self.assertIn("SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md", post_action_item["safe_readback_source"])
        self.assertTrue(any("Proof capture manifest" in item for item in post_action_item["completion_evidence"]))
        self.assertTrue(any("latest_splunk_mcp_proof_capture_manifest.html" in item for item in post_action["final_readback_sequence"]))

    def test_judge_scorecard_tracks_stage_one_and_mcp_bonus_boundaries(self) -> None:
        scorecard = read_json("reports/latest_judge_scorecard.json")
        markdown = (ROOT / "reports/latest_judge_scorecard.md").read_text(encoding="utf-8")
        alignment = (ROOT / "submission/JUDGING_ALIGNMENT.md").read_text(encoding="utf-8")
        mcp_boundary = scorecard["mcp_bonus_claim_boundary"]
        scored = set(scorecard["stage_two_scored_criteria"])

        self.assertTrue(scorecard["stage_one_pass_fail_ready"])
        self.assertGreaterEqual(len(scorecard["stage_one_pass_fail_baseline"]), 4)
        self.assertTrue(all(item["ready"] for item in scorecard["stage_one_pass_fail_baseline"]))
        self.assertEqual(
            scored,
            {"Technological Implementation", "Design", "Potential Impact", "Quality of the Idea"},
        )
        self.assertEqual(mcp_boundary["bonus_category"], "Best Use of Splunk MCP Server")
        self.assertFalse(mcp_boundary["live_splunk_mcp_verified"])
        self.assertIn("verified through Splunk MCP Server", mcp_boundary["blocked_claims_until_verified"])
        self.assertIn("live_splunk_mcp_verified=true", mcp_boundary["upgrade_condition"])
        self.assertIn("Stage One Pass/Fail Baseline", markdown)
        self.assertIn("MCP Bonus Claim Boundary", markdown)
        self.assertIn("Use verified-through-Splunk-MCP wording only after", alignment)
        self.assertIn("live_splunk_mcp_verified=true", alignment)

    def test_devpost_urls_remain_pending_until_public_urls_are_approved(self) -> None:
        final_copy = read_json("reports/latest_devpost_final_copy.json")
        url_validation = read_json("reports/latest_submission_url_validation.json")
        go_no_go = read_json("reports/latest_final_go_no_go.json")

        self.assertFalse(final_copy["final_submit_ready"])
        self.assertFalse(url_validation["final_submit_ready"])
        self.assertFalse(go_no_go["final_submit_ready"])
        self.assertEqual(final_copy["pending_urls"], ["repository_url", "demo_video_url"])
        self.assertEqual(url_validation["pending_urls"], ["repository_url", "demo_video_url"])
        self.assertEqual(final_copy["fields"]["repository_url"], "PENDING_USER_APPROVAL_PUBLIC_REPO_URL")
        self.assertEqual(final_copy["fields"]["demo_video_url"], "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL")
        self.assertEqual(url_validation["repository_url"], "PENDING_USER_APPROVAL_PUBLIC_REPO_URL")
        self.assertEqual(url_validation["demo_video_url"], "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL")

    def test_approved_url_writeback_requires_verified_live_readback(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agentops_url_writeback_gate_") as tmp:
            tmp_root = Path(tmp)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prepare_submission_urls.py",
                    "--root",
                    str(tmp_root),
                    "--repository-url",
                    "https://github.com/example/agentops-control-tower",
                    "--demo-video-url",
                    "https://youtu.be/agentops-control-tower-demo",
                    "--write-approved",
                    "--approval-note",
                    "test approval",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 1)
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "needs_more_evidence")
            self.assertFalse(result["approved_urls_file_written"])
            self.assertFalse((tmp_root / "submission/approved_public_urls.json").exists())

            payload = json.loads((tmp_root / "reports/latest_submission_url_apply_plan.json").read_text(encoding="utf-8"))
            self.assertTrue(payload["final_submit_ready"])
            self.assertTrue(payload["verified_readback_required"])
            self.assertFalse(payload["verified_readback_passed"])
            self.assertIn("reports/latest_public_artifact_url_readback.json", "\n".join(payload["verified_readback_issues"]))

    def test_devpost_built_with_holds_splunk_mcp_tag_until_live_proof(self) -> None:
        final_copy = read_json("reports/latest_devpost_final_copy.json")
        proof = read_json("reports/latest_splunk_mcp_proof_capture_manifest.json")
        field_map = (ROOT / "submission/DEVPOST_FIELD_MAP.md").read_text(encoding="utf-8")
        manual_fill = read_json("reports/latest_devpost_manual_fill_brief.json")
        built_with_row = next(item for item in manual_fill["fields"] if item["field"] == "Built with")

        self.assertFalse(proof["live_splunk_mcp_verified"])
        self.assertNotIn("Splunk MCP Server", final_copy["fields"]["built_with"])
        self.assertEqual(final_copy["fields"]["built_with"], ["Python", "Splunk", "SPL", "JSON", "CSV", "HTML"])
        self.assertIn("| Built with | Python, Splunk, SPL, JSON, CSV, HTML |", field_map)
        self.assertIn("Add Splunk MCP Server only after approved live Splunk/MCP proof", field_map)
        self.assertIn("keep Splunk MCP Server out of built-with tags until approved live proof", built_with_row["readback"])

    def test_publication_plans_use_guarded_helper(self) -> None:
        command_plan = read_json("reports/latest_publication_command_plan.json")
        publish_brief = read_json("reports/latest_public_repo_publish_brief.json")
        commands = [item["command"] for item in command_plan["commands"]]
        publish_commands = [item["command"] for item in publish_brief["publish_steps"]]

        self.assertTrue(any("publish_public_repo_after_approval.py" in command for command in commands))
        self.assertTrue(any("--execute" in command for command in commands))
        self.assertTrue(any("verify_public_repo_publication_gate.py" in command for command in commands))
        self.assertTrue(any("--public-git-identity-confirmed" in command for command in commands))
        self.assertTrue(any(item["name"] == "Check public repository namespace" for item in command_plan["commands"]))
        self.assertTrue(any("gh repo view <owner>/agentops-control-tower" in command for command in commands))
        self.assertTrue(any("publish_public_repo_after_approval.py" in command for command in publish_commands))
        self.assertTrue(any("--execute" in command for command in publish_commands))
        self.assertTrue(any("verify_public_repo_publication_gate.py" in command for command in publish_commands))
        self.assertTrue(any("--public-git-identity-confirmed" in command for command in publish_commands))
        self.assertTrue(any(item["step"] == "Check public repository namespace" for item in publish_brief["publish_steps"]))
        self.assertTrue(any("gh repo view <owner>/agentops-control-tower" in command for command in publish_commands))
        self.assertFalse(any("gh repo create" in command for command in commands))
        self.assertFalse(any("git push -u origin main" in command for command in commands))

    def test_public_repo_publication_preflight_blocks_until_approval(self) -> None:
        payload = read_json("reports/latest_public_repo_publication_preflight.json")
        safe = payload["public_repo_publication_safe_readback"]

        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["gate_status"], "blocked_by_public_repo_approval_gate")
        self.assertFalse(payload["public_repo_publication_allowed"])
        self.assertFalse(payload["approval_phrase_accepted"])
        self.assertEqual(payload["missing_evidence"], [])
        self.assertFalse(payload["external_actions_attempted"])
        self.assertFalse(payload["external_actions_completed"])
        self.assertEqual(safe["action_key"], "public_github_repository")
        self.assertEqual(safe["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md")
        self.assertIn("verify_public_repo_publication_gate.py", safe["preflight_command"])
        self.assertIn("publish_public_repo_after_approval.py", safe["execute_command"])
        self.assertNotIn("stage_root", safe)
        self.assertNotIn("audit_stage", safe)
        self.assertNotIn("publish_stage", safe)

    def test_public_repo_publication_preflight_rejects_wrong_approval_phrase(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/verify_public_repo_publication_gate.py",
                "--approval-phrase",
                "wrong approval",
                "--source-folder-reviewed",
                "--isolated-staging-confirmed",
                "--secret-scan-confirmed",
                "--public-visibility-confirmed",
                "--public-git-identity-confirmed",
                "--git-user-name",
                "Agentic Incident Command Center",
                "--git-user-email",
                "agentops-control-tower@example.invalid",
                "--no-write-report",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["gate_status"], "blocked_by_public_repo_approval_gate")
        self.assertFalse(payload["public_repo_publication_allowed"])
        self.assertFalse(payload["approval_phrase_accepted"])
        self.assertFalse(payload["external_actions_attempted"])

    def test_guarded_publication_helper_blocks_bad_execute_approval(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/publish_public_repo_after_approval.py",
                "--execute",
                "--approval-phrase",
                "wrong approval",
                "--git-user-name",
                "Agentic Incident Command Center",
                "--git-user-email",
                "agentops-control-tower@example.invalid",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "blocked_by_approval_gate")
        self.assertFalse(payload["external_actions_attempted"])
        self.assertFalse(payload["external_actions_completed"])
        self.assertFalse(payload["approval_phrase_accepted"])
        safe = payload["public_safe_readback"]
        safe_json = json.dumps(safe, ensure_ascii=False)
        self.assertEqual(safe["action_key"], "public_github_repository")
        self.assertEqual(safe["status"], "blocked_by_approval_gate")
        self.assertEqual(safe["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md")
        self.assertNotIn("stage_root", safe)
        self.assertNotIn("audit_stage", safe)
        self.assertNotIn("publish_stage", safe)
        self.assertIsNone(re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/](?!/)", safe_json))

    def test_guarded_publication_helper_requires_public_git_identity(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/publish_public_repo_after_approval.py",
                "--execute",
                "--approval-phrase",
                PUBLIC_REPO_APPROVAL,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "blocked_by_approval_gate")
        self.assertTrue(payload["approval_phrase_accepted"])
        self.assertEqual(set(payload["missing_execute_inputs"]), {"--git-user-name", "--git-user-email"})
        self.assertFalse(payload["external_actions_attempted"])
        self.assertFalse(payload["external_actions_completed"])
        safe = payload["public_safe_readback"]
        self.assertTrue(safe["approval_phrase_accepted"])
        self.assertFalse(safe["external_actions_attempted"])
        self.assertFalse(safe["external_actions_completed"])
        self.assertIn("Do not copy stage_root", safe["copy_policy"])

    def test_guarded_publication_helper_rejects_placeholder_public_git_identity(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/publish_public_repo_after_approval.py",
                "--execute",
                "--approval-phrase",
                PUBLIC_REPO_APPROVAL,
                "--git-user-name",
                "<approved-public-git-name>",
                "--git-user-email",
                "<approved-public-git-email>",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "blocked_by_approval_gate")
        self.assertTrue(payload["approval_phrase_accepted"])
        self.assertEqual(payload["missing_execute_inputs"], [])
        self.assertFalse(payload["external_actions_attempted"])
        self.assertFalse(payload["external_actions_completed"])
        invalid = "\n".join(payload["invalid_execute_inputs"])
        self.assertIn("--git-user-name", invalid)
        self.assertIn("--git-user-email", invalid)
        safe = payload["public_safe_readback"]
        self.assertFalse(safe["external_actions_attempted"])
        self.assertFalse(safe["external_actions_completed"])
        self.assertEqual(safe["missing_execute_inputs"], [])
        self.assertIn("invalid_execute_inputs", safe)

    def test_guarded_publication_helper_rejects_malformed_public_git_email(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/publish_public_repo_after_approval.py",
                "--execute",
                "--approval-phrase",
                PUBLIC_REPO_APPROVAL,
                "--git-user-name",
                "Agentic Incident Command Center",
                "--git-user-email",
                "agentops-control-tower",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "blocked_by_approval_gate")
        self.assertTrue(payload["approval_phrase_accepted"])
        self.assertEqual(payload["missing_execute_inputs"], [])
        self.assertFalse(payload["external_actions_attempted"])
        self.assertFalse(payload["external_actions_completed"])
        self.assertIn("--git-user-email must include @", payload["invalid_execute_inputs"])

    def test_guarded_publication_helper_reads_back_metadata(self) -> None:
        source = (ROOT / "scripts/publish_public_repo_after_approval.py").read_text(encoding="utf-8")
        required = [
            "Splunk-ready safety and incident intelligence for autonomous AI agent operations.",
            "reports/latest_public_repo_metadata.json",
            "submission/PUBLIC_REPO_METADATA.md",
            "--description",
            "gh repo readback description",
            "gh repo readback default branch",
            "gh repo readback license",
            "gh repo readback topics",
            "nameWithOwner,visibility,url,description,defaultBranchRef,licenseInfo,repositoryTopics,isPrivate",
            "expected_metadata",
            "public_safe_readback",
            "evidence_note_target",
            "Do not copy stage_root",
            "invalid_execute_inputs",
            "approved-public-git-name",
            "approved-public-git-email",
            "must be a real public git identity",
            "must include @",
            "gh repo namespace precheck",
            "namespace_precheck",
        ]

        for text in required:
            self.assertIn(text, source)

    def test_guarded_publication_helper_rejects_workspace_stage_root(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/publish_public_repo_after_approval.py",
                "--stage-root",
                str(ROOT),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "needs_more_evidence")
        self.assertEqual(payload["mode"], "rehearsal")
        self.assertEqual(payload["failed_count"], 1)
        if "checks" in payload:
            checks = {item["name"]: item for item in payload["checks"]}
            self.assertEqual(checks["stage root outside private workspace"]["status"], "fail")
        else:
            self.assertIn("error", payload)
        self.assertFalse(payload["external_actions_attempted"])
        self.assertFalse(payload["external_actions_completed"])

    def test_final_submission_checklist_mentions_safety_gate_scripts(self) -> None:
        checklist = (ROOT / "submission/FINAL_SUBMISSION_CHECKLIST.md").read_text(encoding="utf-8")
        required_scripts = [
            "scripts/build_approval_execution_handoff.py",
            "scripts/build_public_repo_dry_run.py",
            "scripts/build_status_conflict_audit.py",
            "scripts/build_url_writeback_dry_run.py",
            "scripts/build_user_approval_brief_ja.py",
            "scripts/build_video_dry_run.py",
            "scripts/build_video_recording_preview.py",
            "scripts/publish_public_repo_after_approval.py",
            "scripts/verify_public_repo_publication_gate.py",
            "scripts/verify_public_artifact_urls.py",
        ]
        for script in required_scripts:
            self.assertIn(script, checklist)
        self.assertIn("Status conflict audit shows no stale failed statuses", checklist)
        self.assertIn("Candidate includes `reports/latest_status_conflict_audit.html`", checklist)

    def test_launch_runbook_includes_status_conflict_preflight(self) -> None:
        runbook = (ROOT / "submission/SUBMISSION_LAUNCH_RUNBOOK.md").read_text(encoding="utf-8")
        required_text = [
            "python scripts\\build_status_conflict_audit.py",
            "scripts\\build_status_conflict_audit.py",
            "reports/latest_status_conflict_audit.html",
            "no stale failed statuses",
            "Review `reports/latest_status_conflict_audit.html`",
        ]
        for text in required_text:
            self.assertIn(text, runbook)

    def test_public_repo_dry_run_summarizes_git_warning_noise(self) -> None:
        payload = read_json("reports/latest_public_repo_dry_run.json")
        checks = {item["name"]: item for item in payload["checks"]}
        detail = checks["git add rehearsal"]["detail"]

        self.assertNotIn("warning: in the working copy", detail)
        self.assertNotIn("LF will be replaced by CRLF", detail)
        self.assertTrue(
            detail == "no output"
            or detail == "ok"
            or "line-ending warnings suppressed" in detail
            or detail.startswith("other output: ")
        )

    def test_public_candidate_has_line_ending_policy(self) -> None:
        gitattributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", gitattributes)
        self.assertIn("*.spl binary", gitattributes)
        self.assertIn("*.zip binary", gitattributes)

    def test_public_candidate_builder_refreshes_candidate_local_reports(self) -> None:
        if PUBLIC_CANDIDATE_ROOT:
            self.skipTest("public candidate folder does not contain a nested public candidate")

        source = (ROOT / "scripts/build_public_repo_candidate.py").read_text(encoding="utf-8")
        required_refresh_scripts = [
            "scripts/build_public_repo_dry_run.py",
            "scripts/build_final_go_no_go_report.py",
            "scripts/build_video_readiness_report.py",
            "scripts/build_video_cue_sheet.py",
            "scripts/build_video_dry_run.py",
            "scripts/build_video_recording_preview.py",
            "scripts/build_video_upload_metadata.py",
            "scripts/verify_public_video_upload_gate.py",
            "scripts/build_external_approval_packet.py",
            "scripts/build_launch_decision_brief.py",
            "scripts/build_public_repo_metadata.py",
            "scripts/verify_public_repo_publication_gate.py",
            "scripts/build_public_launch_snapshot.py",
            "scripts/build_submission_gate_ledger.py",
            "scripts/build_submission_review_index.py",
            "scripts/build_next_approval_packet.py",
            "scripts/build_devpost_submit_command_plan.py",
            "scripts/build_devpost_manual_fill_brief.py",
            "scripts/build_post_action_evidence_brief.py",
            "scripts/verify_devpost_final_submit_gate.py",
            "scripts/build_url_writeback_dry_run.py",
            "scripts/validate_submission_packet.py",
            "scripts/build_approval_consistency_audit.py",
            "scripts/build_release_integrity_manifest.py",
            "scripts/build_status_conflict_audit.py",
        ]
        for script in required_refresh_scripts:
            self.assertIn(script, source)
        refresh_start = source.index("CANDIDATE_REFRESH_SCRIPTS")
        refresh_order = {script: source.index(f'"{script}"', refresh_start) for script in required_refresh_scripts}
        self.assertLess(refresh_order["scripts/build_public_repo_dry_run.py"], refresh_order["scripts/build_final_go_no_go_report.py"])
        self.assertLess(refresh_order["scripts/build_final_go_no_go_report.py"], refresh_order["scripts/build_video_readiness_report.py"])
        self.assertLess(refresh_order["scripts/build_video_cue_sheet.py"], refresh_order["scripts/build_video_dry_run.py"])
        self.assertLess(refresh_order["scripts/build_video_dry_run.py"], refresh_order["scripts/build_video_recording_preview.py"])
        self.assertLess(refresh_order["scripts/build_video_upload_metadata.py"], refresh_order["scripts/verify_public_video_upload_gate.py"])
        self.assertLess(refresh_order["scripts/build_final_go_no_go_report.py"], refresh_order["scripts/build_external_approval_packet.py"])
        publication_index = source.index('"scripts/build_publication_command_plan.py"', refresh_start)
        self.assertLess(refresh_order["scripts/build_external_approval_packet.py"], publication_index)
        self.assertLess(publication_index, refresh_order["scripts/build_public_repo_metadata.py"])
        self.assertLess(refresh_order["scripts/build_public_repo_metadata.py"], refresh_order["scripts/verify_public_repo_publication_gate.py"])
        second_external_index = source.index(
            '"scripts/build_external_approval_packet.py"',
            refresh_order["scripts/verify_public_repo_publication_gate.py"],
        )
        self.assertLess(refresh_order["scripts/verify_public_repo_publication_gate.py"], second_external_index)
        self.assertLess(second_external_index, refresh_order["scripts/build_submission_gate_ledger.py"])
        self.assertLess(refresh_order["scripts/build_submission_review_index.py"], refresh_order["scripts/build_launch_decision_brief.py"])
        self.assertLess(refresh_order["scripts/build_launch_decision_brief.py"], refresh_order["scripts/build_next_approval_packet.py"])
        self.assertLess(refresh_order["scripts/build_approval_consistency_audit.py"], refresh_order["scripts/build_public_launch_snapshot.py"])
        self.assertLess(refresh_order["scripts/build_devpost_manual_fill_brief.py"], refresh_order["scripts/build_post_action_evidence_brief.py"])
        self.assertLess(refresh_order["scripts/build_post_action_evidence_brief.py"], refresh_order["scripts/verify_devpost_final_submit_gate.py"])
        final_gate_index = refresh_order["scripts/verify_devpost_final_submit_gate.py"]
        second_post_action_index = source.index('"scripts/build_post_action_evidence_brief.py"', final_gate_index)
        self.assertLess(final_gate_index, second_post_action_index)
        self.assertLess(refresh_order["scripts/build_url_writeback_dry_run.py"], refresh_order["scripts/validate_submission_packet.py"])
        self.assertLess(refresh_order["scripts/validate_submission_packet.py"], refresh_order["scripts/build_release_integrity_manifest.py"])
        self.assertLess(refresh_order["scripts/build_release_integrity_manifest.py"], refresh_order["scripts/build_status_conflict_audit.py"])

        candidate_root = ROOT / "public_repo_candidate/agentops-control-tower"
        required_candidate_reports = [
            "reports/latest_public_repo_dry_run.html",
            "reports/latest_public_repo_dry_run.json",
            "reports/latest_public_repo_dry_run.md",
            "reports/latest_video_dry_run.html",
            "reports/latest_video_dry_run.json",
            "reports/latest_video_dry_run.md",
            "reports/latest_url_writeback_dry_run.html",
            "reports/latest_url_writeback_dry_run.json",
            "reports/latest_url_writeback_dry_run.md",
            "reports/latest_release_integrity_manifest.json",
            "reports/latest_status_conflict_audit.html",
            "reports/latest_status_conflict_audit.json",
            "reports/latest_status_conflict_audit.md",
        ]
        for rel_path in required_candidate_reports:
            self.assertTrue((candidate_root / rel_path).exists(), rel_path)

        release = json.loads((candidate_root / "reports/latest_release_integrity_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(release["root_type"], "public_candidate")

        validator_source = (ROOT / "scripts/validate_submission_packet.py").read_text(encoding="utf-8")
        cleanup_section = validator_source.split("def cleanup_public_candidate_package_artifacts", 1)[1].split("def sanitize_detail", 1)[0]
        for rel_path in [
            "reports/latest_public_repo_dry_run.html",
            "reports/latest_video_dry_run.html",
            "reports/latest_url_writeback_dry_run.html",
            "reports/latest_status_conflict_audit.html",
        ]:
            self.assertNotIn(rel_path, cleanup_section)

    def test_readme_mentions_safety_gate_entrypoints(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8").replace("\\", "/")
        required_text = [
            "scripts/build_video_recording_preview.py",
            "scripts/publish_public_repo_after_approval.py",
            "scripts/verify_public_repo_publication_gate.py",
            "scripts/build_status_conflict_audit.py",
            "reports/latest_video_recording_preview.html",
            "reports/latest_status_conflict_audit.html",
            "Approved public URL writeback",
            "exact public GitHub approval phrase",
            "explicit public git identity",
        ]
        for text in required_text:
            self.assertIn(text, readme)

        private_review_text = [
            "scripts/build_user_approval_brief_ja.py",
            "reports/latest_user_approval_brief_ja.html",
            "scripts/build_approval_execution_handoff.py",
            "reports/latest_approval_execution_handoff.html",
        ]
        if PUBLIC_CANDIDATE_ROOT:
            for text in private_review_text:
                self.assertNotIn(text, readme)
        else:
            for text in private_review_text:
                self.assertIn(text, readme)

    def test_public_candidate_readme_only_references_included_scripts(self) -> None:
        def assert_public_readme(candidate: Path) -> None:
            readme = (candidate / "README.md").read_text(encoding="utf-8")
            for private_marker in [
                "scripts\\build_user_approval_brief_ja.py",
                "scripts/build_user_approval_brief_ja.py",
                "scripts\\build_approval_execution_handoff.py",
                "scripts/build_approval_execution_handoff.py",
                "latest_user_approval_brief_ja",
                "latest_approval_execution_handoff",
                "APPROVAL_EXECUTION_HANDOFF.md",
                "PUBLIC_REPO_READINESS.md",
            ]:
                self.assertNotIn(private_marker, readme)

            referenced_scripts = set(re.findall(r"python\s+(scripts[\\/][^\s]+\.py)", readme))
            self.assertTrue(referenced_scripts)
            missing = [
                script
                for script in sorted(referenced_scripts)
                if not (candidate / script.replace("\\", "/")).exists()
            ]
            self.assertEqual(missing, [])

            referenced_paths = set()
            for line in readme.splitlines():
                bullet = re.match(r"^- `([^`]+)`", line)
                if bullet:
                    referenced_paths.add(bullet.group(1).replace("\\", "/"))
                    continue
                path_line = re.match(r"^((reports|submission|release|dist|assets|data|splunk_app)[\\/][^\s`]+|architecture_diagram\.md)", line)
                if path_line:
                    referenced_paths.add(path_line.group(0).replace("\\", "/"))
            missing_paths = [
                path
                for path in sorted(referenced_paths)
                if path not in PUBLIC_README_GENERATED_PATHS and not (candidate / path).exists()
            ]
            self.assertEqual(missing_paths, [])

        if PUBLIC_CANDIDATE_ROOT:
            assert_public_readme(ROOT)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                completed = subprocess.run(
                    [
                        sys.executable,
                        "scripts/build_public_repo_candidate.py",
                        "--output-root",
                        tmp,
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
                assert_public_readme(Path(tmp) / "agentops-control-tower")

    def test_human_confirmation_checklist_stays_pending_and_gated(self) -> None:
        checklist = (ROOT / "submission/HUMAN_CONFIRMATION_CHECKLIST.md").read_text(encoding="utf-8")
        required_items = [
            "age_and_residence",
            "no_excluded_role_or_conflict",
            "team_or_representative_authority",
            "ownership_and_ip",
            "no_sponsor_support_conflict",
        ]

        self.assertIn("Status: pending human confirmation", checklist)
        self.assertGreaterEqual(checklist.count("- [ ] `"), len(required_items))
        for item in required_items:
            self.assertIn(item, checklist)
        self.assertIn("It is not a legal determination", checklist)
        self.assertIn("does not publish a repository, upload video, write approved URLs", checklist)
        self.assertIn("Devpost final submission stays blocked", checklist)

    def test_devpost_final_review_checklist_stays_pending_and_gated(self) -> None:
        manual_fill = read_json("reports/latest_devpost_manual_fill_brief.json")
        command_plan = read_json("reports/latest_devpost_submit_command_plan.json")
        checklist = (ROOT / "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md").read_text(encoding="utf-8")
        commands = "\n".join(item["command"] for item in command_plan["commands"])
        required_text = [
            "Status: pending final Devpost review",
            "Platform & Developer Experience",
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

        self.assertEqual(manual_fill["final_review_checklist"], "submission/DEVPOST_FINAL_REVIEW_CHECKLIST.md")
        self.assertIn("verify_devpost_final_submit_gate.py", commands)
        self.assertIn(DEVPOST_FINAL_APPROVAL, commands)
        self.assertGreaterEqual(checklist.count("- [ ]"), 10)
        for text in required_text:
            self.assertIn(text, checklist)

    def test_devpost_final_submit_preflight_blocks_until_final_ready(self) -> None:
        payload = read_json("reports/latest_devpost_final_submit_preflight.json")
        safe = payload["devpost_final_submit_safe_readback"]

        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["gate_status"], "blocked_until_final_submit_ready")
        self.assertFalse(payload["manual_submit_allowed"])
        self.assertFalse(payload["final_submit_ready"])
        self.assertFalse(payload["approval_phrase_accepted"])
        self.assertFalse(payload["external_actions_attempted"])
        self.assertFalse(payload["external_actions_completed"])
        self.assertIn("final_submit_ready must be true", "\n".join(payload["gate_issues"]))
        self.assertEqual(safe["action_key"], "devpost_final_submission")
        self.assertFalse(safe["manual_submit_allowed"])
        self.assertEqual(safe["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_devpost_final_submission_readback.md")
        self.assertIn("Do not copy account screenshots", safe["copy_policy"])

    def test_devpost_final_submit_preflight_rejects_wrong_approval_phrase(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/verify_devpost_final_submit_gate.py",
                "--final-approval-phrase",
                "wrong approval",
                "--no-write-report",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["gate_status"], "blocked_by_final_approval_gate")
        self.assertFalse(payload["manual_submit_allowed"])
        self.assertFalse(payload["approval_phrase_accepted"])
        self.assertFalse(payload["external_actions_attempted"])

    def test_submission_deadline_burndown_keeps_external_gates_closed(self) -> None:
        payload = read_json("reports/latest_submission_deadline_burndown.json")
        checklist = (ROOT / "submission/SUBMISSION_DEADLINE_BURNDOWN.md").read_text(encoding="utf-8")
        keys = {item["key"] for item in payload["milestones"]}
        required_keys = {
            "public_github_repository",
            "public_demo_video",
            "optional_live_splunk_mcp_proof",
            "approved_url_writeback",
            "devpost_final_submission",
        }
        required_text = [
            "2026-06-15 20:00 JST",
            "2026-06-16 01:00 JST",
            "Minimum Viable Submit Path",
            "Stretch Path",
            "reports/latest_public_video_upload_preflight.html",
            "reports/latest_splunk_mcp_proof_capture_manifest.html",
            "Local validation source:",
            "does not publish a repository, record or upload video, connect to Splunk",
            "Final submit ready: false",
        ]

        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["local_submission_status"], "ready_for_user_review")
        self.assertEqual(payload["failed_count"], 0)
        expected_validation_source = (
            "reports/latest_final_go_no_go.json"
            if PUBLIC_CANDIDATE_ROOT
            else "reports/latest_submission_validation.json"
        )
        self.assertEqual(payload["local_validation_source"], expected_validation_source)
        self.assertFalse(payload["final_submit_ready"])
        self.assertEqual(payload["missing_evidence"], [])
        self.assertTrue(required_keys.issubset(keys))
        for text in required_text:
            self.assertIn(text, checklist)

    def test_public_candidate_deadline_burndown_inherits_release_validation(self) -> None:
        if PUBLIC_CANDIDATE_ROOT:
            self.skipTest("workspace-only public candidate inspection")
        from scripts.build_submission_deadline_burndown import build_payload

        candidate = ROOT / "public_repo_candidate/agentops-control-tower"
        persisted = json.loads((candidate / "reports/latest_submission_deadline_burndown.json").read_text(encoding="utf-8"))
        payload = build_payload(candidate)
        video_milestone = next(item for item in payload["milestones"] if item["key"] == "public_demo_video")
        video_paths = {item["path"] for item in video_milestone["evidence"]}

        self.assertEqual(persisted["local_validation_source"], "reports/latest_final_go_no_go.json")
        self.assertEqual(payload["root_type"], "public_candidate")
        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["local_submission_status"], "ready_for_user_review")
        self.assertEqual(payload["failed_count"], 0)
        self.assertEqual(payload["local_validation_source"], "reports/latest_final_go_no_go.json")
        self.assertIn("public_github_repository", payload["pending_external_actions"])
        self.assertIn("public_demo_video", payload["pending_external_actions"])
        self.assertIn("reports/latest_public_video_upload_preflight.html", video_paths)

    def test_public_repo_metadata_keeps_publication_gated(self) -> None:
        payload = read_json("reports/latest_public_repo_metadata.json")
        metadata = (ROOT / "submission/PUBLIC_REPO_METADATA.md").read_text(encoding="utf-8")
        required_topics = {"splunk", "agentops", "ai-agents", "observability", "mcp", "safety"}
        required_text = [
            "Repository name: `agentops-control-tower`",
            "Splunk-ready safety and incident intelligence",
            "gh repo create agentops-control-tower --public",
            "gh repo view <owner>/agentops-control-tower",
            "Expected Readback",
            "Do not create or edit a GitHub repository without the exact public GitHub approval phrase.",
            "does not create a repository, edit GitHub metadata, push commits, publish files",
        ]

        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["repo_name"], "agentops-control-tower")
        self.assertFalse(payload["final_submit_ready"])
        self.assertFalse(payload["approved_public_urls_exists"])
        self.assertEqual(payload["missing_evidence"], [])
        self.assertTrue(required_topics.issubset(set(payload["topics"])))
        self.assertEqual(payload["expected_readback"]["visibility"], "PUBLIC")
        self.assertFalse(payload["expected_readback"]["isPrivate"])
        for text in required_text:
            self.assertIn(text, metadata)

    def test_video_screen_safety_checklist_stays_pending_and_gated(self) -> None:
        readiness = read_json("reports/latest_video_readiness.json")
        checklist = (ROOT / "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md").read_text(encoding="utf-8")
        required_text = [
            "Status: pending screen safety review",
            "Use synthetic data only.",
            "Do not show `.env`, config files, API keys, OAuth tokens, or private logs.",
            "Do not show real customer, cloud, incident, identity, ticketing, or Splunk account screens.",
            "designed for Splunk MCP Server",
            "does not record, upload, publish, write approved URLs, update Devpost, or submit",
            "Public video upload stays blocked",
        ]

        self.assertEqual(readiness["screen_safety_checklist"], "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md")
        self.assertFalse(readiness["final_public_video_ready"])
        self.assertGreaterEqual(checklist.count("- [ ]"), 8)
        for text in required_text:
            self.assertIn(text, checklist)

    def test_video_recording_preview_keeps_capture_and_upload_external(self) -> None:
        command_plan = read_json("reports/latest_video_command_plan.json")
        preview = read_json("reports/latest_video_recording_preview.json")
        commands = [item["command"] for item in command_plan["commands"]]

        self.assertTrue(any("build_video_recording_preview.py" in command for command in commands))
        self.assertEqual(preview["status"], "ready_for_recording_review")
        self.assertEqual(preview["failed_count"], 0)
        self.assertEqual(preview["stage_policy"], "system_temp_public_candidate_copy")
        self.assertTrue(preview["stage_removed_after_run"])
        self.assertTrue(preview["preview_url"].startswith("http://127.0.0.1:"))
        self.assertFalse(preview["external_actions_attempted"])
        self.assertFalse(preview["external_actions_completed"])
        safe = preview["public_video_safe_readback"]
        safe_json = json.dumps(safe, ensure_ascii=False)
        self.assertEqual(safe["action_key"], "public_demo_video")
        self.assertEqual(safe["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md")
        self.assertEqual(safe["screen_safety_checklist"], "submission/VIDEO_SCREEN_SAFETY_CHECKLIST.md")
        self.assertFalse(safe["ready_for_public_upload"])
        self.assertFalse(safe["external_actions_attempted"])
        self.assertEqual(safe["screen_scan"]["internal_path_hit_count"], 0)
        self.assertEqual(safe["screen_scan"]["secret_like_hit_count"], 0)
        self.assertIn("Do not copy raw recording output", safe["copy_policy"])
        self.assertIsNone(re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/](?!/)", safe_json))

    def test_video_upload_metadata_stays_pending_and_gated(self) -> None:
        metadata = read_json("reports/latest_video_upload_metadata.json")
        submission_copy = (ROOT / "submission/VIDEO_UPLOAD_METADATA.md").read_text(encoding="utf-8")
        commands = [item["command"] for item in read_json("reports/latest_video_command_plan.json")["commands"]]
        required_text = [
            "Agentic Incident Command Center: Splunk-grounded AI incident response",
            "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL",
            "synthetic checkout-incident events",
            "MCP Remediation Ledger",
            "Expected Readback",
            "Do not upload if the recording shows private paths",
            "does not record video, upload video, publish media",
        ]

        self.assertTrue(any("build_video_upload_metadata.py" in command for command in commands))
        self.assertTrue(any("verify_public_video_upload_gate.py" in command for command in commands))
        self.assertTrue(any(PUBLIC_VIDEO_APPROVAL in command for command in commands))
        self.assertEqual(metadata["status"], "ready_for_user_review")
        self.assertFalse(metadata["final_public_video_ready"])
        self.assertFalse(metadata["approved_public_urls_exists"])
        self.assertEqual(metadata["public_video_url"], "PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL")
        self.assertLessEqual(metadata["observed_duration_seconds"], 180)
        self.assertEqual(metadata["expected_readback"]["visibility"], "public")
        for text in required_text:
            self.assertIn(text, submission_copy)

    def test_public_video_upload_preflight_blocks_until_approval(self) -> None:
        payload = read_json("reports/latest_public_video_upload_preflight.json")
        safe = payload["public_video_upload_safe_readback"]

        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["gate_status"], "blocked_by_video_approval_gate")
        self.assertFalse(payload["public_video_upload_allowed"])
        self.assertFalse(payload["approval_phrase_accepted"])
        self.assertFalse(payload["external_actions_attempted"])
        self.assertFalse(payload["external_actions_completed"])
        self.assertLessEqual(payload["duration_seconds"], 180)
        self.assertEqual(payload["missing_evidence"], [])
        self.assertIn("approval phrase is required", "\n".join(payload["gate_issues"]))
        self.assertEqual(safe["action_key"], "public_demo_video")
        self.assertFalse(safe["ready_for_public_upload"])
        self.assertEqual(safe["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md")
        self.assertIn("Do not copy screenshots", safe["copy_policy"])

    def test_public_video_upload_preflight_rejects_wrong_approval_phrase(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/verify_public_video_upload_gate.py",
                "--approval-phrase",
                "wrong approval",
                "--no-write-report",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["gate_status"], "blocked_by_video_approval_gate")
        self.assertFalse(payload["public_video_upload_allowed"])
        self.assertFalse(payload["approval_phrase_accepted"])
        self.assertFalse(payload["external_actions_attempted"])

    def test_public_artifact_url_readback_stays_pending_without_urls(self) -> None:
        readback = read_json("reports/latest_public_artifact_url_readback.json")
        apply_plan = read_json("reports/latest_submission_url_apply_plan.json")
        command_plan = read_json("reports/latest_video_command_plan.json")
        post_action = read_json("reports/latest_post_action_evidence_brief.json")
        commands = [item["command"] for item in command_plan["commands"]]
        actions = {item["key"]: item for item in post_action["actions"]}
        policy = post_action["evidence_log_policy"]
        template = (ROOT / "submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md").read_text(encoding="utf-8")
        forbidden_content = set(policy["forbidden_content"])

        self.assertEqual(readback["status"], "waiting_for_external_urls")
        self.assertEqual(set(readback["pending_urls"]), {"repository_url", "demo_video_url"})
        self.assertFalse(readback["live_readback_attempted"])
        self.assertFalse(readback["ready_for_url_writeback"])
        self.assertFalse(readback["approved_public_urls_exists"])
        self.assertFalse(apply_plan["write_requested"])
        self.assertFalse(apply_plan["approved_urls_file_written"])
        self.assertFalse(apply_plan["verified_readback_required"])
        self.assertFalse(apply_plan["verified_readback_passed"])
        self.assertEqual(apply_plan["verified_readback_source"], "reports/latest_public_artifact_url_readback.json")
        safe = readback["public_safe_readback"]
        safe_json = json.dumps(safe, ensure_ascii=False)
        self.assertEqual(safe["action_key"], "approved_url_writeback")
        self.assertEqual(safe["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_approved_url_writeback_readback.md")
        self.assertEqual(set(safe["pending_urls"]), {"repository_url", "demo_video_url"})
        self.assertFalse(safe["live_readback_attempted"])
        self.assertFalse(safe["ready_for_url_writeback"])
        self.assertFalse(safe["approved_public_urls_exists"])
        self.assertIn("Do not copy raw command output", safe["copy_policy"])
        self.assertIsNone(re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/](?!/)", safe_json))
        self.assertEqual(actions["public_github_repository"]["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md")
        self.assertIn("public_safe_readback", actions["public_github_repository"]["safe_readback_source"])
        self.assertEqual(actions["public_demo_video"]["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_public_demo_video_readback.md")
        self.assertIn("public_video_upload_safe_readback", actions["public_demo_video"]["safe_readback_source"])
        self.assertIn("latest_public_video_upload_preflight.json", actions["public_demo_video"]["safe_readback_source"])
        self.assertIn("public_video_safe_readback", actions["public_demo_video"]["safe_readback_source"])
        self.assertIn("latest_video_recording_preview.json", actions["public_demo_video"]["safe_readback_source"])
        self.assertEqual(actions["approved_url_writeback"]["evidence_note_target"], "submission/post_action_evidence/YYYY-MM-DD_approved_url_writeback_readback.md")
        self.assertIn("latest_public_artifact_url_readback.json", actions["approved_url_writeback"]["safe_readback_source"])
        self.assertTrue(any("verify_public_artifact_urls.py" in command for command in commands))
        self.assertIn("verify_public_artifact_urls.py", actions["approved_url_writeback"]["readback_command"])
        self.assertIn("prepare_submission_urls.py", actions["approved_url_writeback"]["readback_command"])
        self.assertIn("validate_submission_packet.py", actions["approved_url_writeback"]["readback_command"])
        self.assertEqual(policy["recommended_directory"], "submission/post_action_evidence/")
        self.assertEqual(policy["filename_pattern"], "YYYY-MM-DD_<action_key>_readback.md")
        self.assertIn("credentials", forbidden_content)
        self.assertIn("local absolute paths", forbidden_content)
        self.assertIn("private workspace material", forbidden_content)
        self.assertIn("submission/post_action_evidence/", template)
        self.assertIn("Keep completed evidence notes private/local by default.", template)
        self.assertIn("## Preferred Evidence Note Targets", template)
        self.assertIn("## Safe Readback Sources", template)
        self.assertIn("public_video_upload_safe_readback", template)
        self.assertIn("latest_public_video_upload_preflight.json", template)

    def test_approval_execution_handoff_keeps_launch_actions_gated(self) -> None:
        if not (ROOT / "reports/latest_approval_execution_handoff.json").exists():
            self.skipTest("approval execution handoff is private-workspace-only")

        handoff = read_json("reports/latest_approval_execution_handoff.json")
        status_conflict = read_json("reports/latest_status_conflict_audit.json")
        phases = {item["key"]: item for item in handoff["phases"]}

        self.assertEqual(handoff["status"], "ready_for_user_review")
        self.assertTrue(handoff["handoff_ready"])
        self.assertFalse(handoff["external_actions_attempted"])
        self.assertFalse(handoff["external_actions_completed"])
        self.assertFalse(handoff["final_submit_ready"])
        self.assertFalse(handoff["approved_public_urls_exists"])
        self.assertEqual(handoff["status_conflict_audit"]["path"], "reports/latest_status_conflict_audit.html")
        self.assertEqual(handoff["status_conflict_audit"]["status"], status_conflict["status"])
        self.assertEqual(handoff["status_conflict_audit"]["failed_count"], 0)
        self.assertEqual(handoff["status_conflict_audit"]["conflict_count"], 0)
        self.assertEqual(handoff["status_conflict_audit"]["critical_check_failed_count"], 0)
        self.assertEqual(handoff["status_conflict_audit"]["json_files_scanned"], status_conflict["json_files_scanned"])
        self.assertEqual(handoff["next_user_decision"], ["public_github_repository", "public_demo_video"])
        self.assertEqual(handoff["minimum_viable_submit_path"], [
            "local_preflight",
            "public_github_repository",
            "public_demo_video",
            "public_artifact_url_readback",
            "approved_url_writeback",
            "devpost_final_submission",
        ])
        self.assertEqual(handoff["optional_bonus_path"], [
            "local_preflight",
            "public_github_repository",
            "public_demo_video",
            "optional_live_splunk_mcp_proof",
            "public_artifact_url_readback",
            "approved_url_writeback",
            "devpost_final_submission",
        ])
        self.assertEqual(phases["public_github_repository"]["approval_phrase"], PUBLIC_REPO_APPROVAL)
        self.assertEqual(phases["public_demo_video"]["approval_phrase"], PUBLIC_VIDEO_APPROVAL)
        self.assertEqual(phases["optional_live_splunk_mcp_proof"]["approval_phrase"], OPTIONAL_SPLUNK_MCP_APPROVAL)
        self.assertEqual(phases["optional_live_splunk_mcp_proof"]["status"], "optional_user_decision")
        self.assertTrue(phases["optional_live_splunk_mcp_proof"]["requires_user_approval"])
        self.assertTrue(any("latest_status_conflict_audit" in item for item in phases["local_preflight"]["must_readback"]))
        self.assertTrue(any("conflict_count=0" in item for item in phases["local_preflight"]["must_readback"]))
        self.assertIn("SPLUNK_MCP_RUNBOOK.md", phases["optional_live_splunk_mcp_proof"]["command_or_action"])
        self.assertIn("任意proof", phases["optional_live_splunk_mcp_proof"]["stop_condition"])
        self.assertEqual(phases["public_github_repository"]["primary_artifact"], "reports/latest_public_repo_publication_preflight.html")
        self.assertIn("verify_public_repo_publication_gate.py", phases["public_github_repository"]["command_or_action"])
        self.assertIn(PUBLIC_REPO_APPROVAL, phases["public_github_repository"]["command_or_action"])
        self.assertIn("--public-git-identity-confirmed", phases["public_github_repository"]["command_or_action"])
        self.assertTrue(any("namespace確認" in item for item in phases["public_github_repository"]["must_readback"]))
        self.assertTrue(any("preflight gate" in item for item in phases["public_github_repository"]["must_readback"]))
        self.assertEqual(phases["public_demo_video"]["primary_artifact"], "reports/latest_public_video_upload_preflight.html")
        self.assertIn("verify_public_video_upload_gate.py", phases["public_demo_video"]["command_or_action"])
        self.assertIn(PUBLIC_VIDEO_APPROVAL, phases["public_demo_video"]["command_or_action"])
        self.assertIn("--screen-safety-confirmed", phases["public_demo_video"]["command_or_action"])
        self.assertTrue(any("preflight gate" in item for item in phases["public_demo_video"]["must_readback"]))
        self.assertIn("--git-user-name", phases["public_github_repository"]["command_or_action"])
        self.assertIn("--git-user-email", phases["public_github_repository"]["command_or_action"])
        self.assertIn(PUBLIC_REPO_APPROVAL, phases["public_github_repository"]["command_or_action"])
        self.assertTrue(any("public git identity" in item for item in phases["public_github_repository"]["must_readback"]))
        self.assertIn("verify_public_artifact_urls.py", phases["public_artifact_url_readback"]["command_or_action"])
        self.assertIn("prepare_submission_urls.py", phases["approved_url_writeback"]["command_or_action"])
        self.assertIn("validate_submission_packet.py", phases["approved_url_writeback"]["command_or_action"])
        self.assertIn("does not publish a repository", handoff["boundary"])
        self.assertIn("press submit", handoff["boundary"])

    def test_splunk_mcp_prompt_pack_is_evidence_backed_and_gated(self) -> None:
        payload = read_json("reports/latest_splunk_mcp_prompt_pack.json")
        prompts = {item["key"]: item for item in payload["prompts"]}

        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertEqual(payload["prompt_count"], 5)
        self.assertFalse(payload["live_splunk_mcp_verified"])
        self.assertFalse(payload["external_actions_attempted"])
        self.assertIn("does not create accounts, configure credentials", payload["boundary"])
        self.assertIn("evt-0001", prompts["root_cause_priority"]["expected_citations"])
        self.assertIn("evt-0010", prompts["remediation_approval"]["expected_citations"])
        self.assertIn("evt-0008", prompts["safe_next_action"]["expected_citations"])

        for prompt in prompts.values():
            self.assertTrue(prompt["spl"])
            self.assertTrue(prompt["stop_condition"])
            self.assertGreater(prompt["local_row_count"], 0)

    def test_splunk_mcp_proof_capture_manifest_stays_pending(self) -> None:
        payload = read_json("reports/latest_splunk_mcp_proof_capture_manifest.json")
        manifest = (ROOT / "submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md").read_text(encoding="utf-8")
        slot_keys = {item["key"] for item in payload["capture_slots"]}
        required_slots = {
            "approved_scope",
            "synthetic_import",
            "live_spl_queries",
            "splunk_app_dashboard",
            "mcp_assisted_answer",
            "claim_upgrade_validation",
        }
        required_text = [
            "Splunk MCP Proof Capture Manifest",
            "Captured evidence status: pending_user_approval",
            "Live Splunk MCP verified: false",
            "Expected Final Readback",
            "Stop if Splunk account, license, cost, credential, or MCP scope is not explicitly approved.",
            "does not create accounts, configure credentials, import data, install apps, connect MCP",
        ]

        self.assertEqual(payload["status"], "ready_for_user_review")
        self.assertFalse(payload["live_splunk_mcp_verified"])
        self.assertFalse(payload["claim_upgrade_ready"])
        self.assertEqual(payload["captured_evidence_status"], "pending_user_approval")
        self.assertTrue(required_slots.issubset(slot_keys))
        self.assertEqual(payload["missing_evidence"], [])
        for text in required_text:
            self.assertIn(text, manifest)


if __name__ == "__main__":
    unittest.main()
