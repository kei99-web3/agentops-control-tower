import importlib.util
import csv
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "prototype" / "agentops_control_tower.py"
SPEC = importlib.util.spec_from_file_location("agentops_control_tower", MODULE_PATH)
agentops = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["agentops_control_tower"] = agentops
SPEC.loader.exec_module(agentops)


class AgentOpsControlTowerTest(unittest.TestCase):
    def test_run_demo_creates_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = agentops.run_demo(Path(temp_dir))
            for output_path in outputs.values():
                self.assertTrue(Path(output_path).exists(), output_path)
            self.assertIn("schema", outputs)
            self.assertIn("mcp_investigation", outputs)
            self.assertIn("spl_queries", outputs)
            with Path(outputs["csv"]).open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertIn("tags", rows[0])
            self.assertIn("incident_id", rows[0])
            self.assertIn("service", rows[0])
            self.assertIn("signal_domain", rows[0])
            self.assertIn("root_cause_candidate", rows[0])
            self.assertIn("requires_human_approval", rows[0])
            self.assertTrue(any("mcp" in row["tags"].split(";") for row in rows))

    def test_analysis_finds_blocked_and_approval_queue(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            events_path = Path(temp_dir) / "events.jsonl"
            events = agentops.generate_synthetic_events(events_path)
            analysis = agentops.analyze_events(events)
            self.assertEqual(analysis["event_count"], 13)
            self.assertEqual(analysis["incident_count"], 1)
            self.assertGreaterEqual(analysis["blocked_count"], 1)
            self.assertGreaterEqual(analysis["approval_queue_count"], 4)
            self.assertIn("mcp_investigation", analysis)
            self.assertIn("incident_summaries", analysis)
            self.assertIn("root_cause_candidates", analysis)
            self.assertIn("remediation_ledger", analysis)
            self.assertEqual(analysis["root_cause_candidates"][0]["candidate"], "checkout-api release regression")
            statuses = {item["status"] for item in analysis["incident_summaries"]}
            self.assertIn("needs_human_remediation_approval", statuses)

    def test_event_schema_has_required_event_fields(self) -> None:
        schema = agentops.event_schema()
        required = set(schema["required"])
        self.assertIn("event_id", required)
        self.assertIn("risk_score", required)
        self.assertIn("evidence_ref", required)

    def test_secret_boundary_is_high_risk(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            events_path = Path(temp_dir) / "events.jsonl"
            events = agentops.generate_synthetic_events(events_path)
            credential_events = [event for event in events if "credential_boundary" in event["tags"]]
            self.assertEqual(len(credential_events), 1)
            self.assertEqual(credential_events[0]["risk_score"], 100)
            self.assertEqual(credential_events[0]["policy_decision"], "deny")


if __name__ == "__main__":
    unittest.main()
