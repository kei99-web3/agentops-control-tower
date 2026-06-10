from __future__ import annotations

import argparse
import configparser
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "splunk_app/agentops_control_tower/README.md",
    "splunk_app/agentops_control_tower/default/app.conf",
    "splunk_app/agentops_control_tower/default/indexes.conf",
    "splunk_app/agentops_control_tower/default/props.conf",
    "splunk_app/agentops_control_tower/default/savedsearches.conf",
    "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml",
    "splunk_app/agentops_control_tower/metadata/default.meta",
]

REQUIRED_SEARCH_NAMES = [
    "Incident Command - Timeline",
    "Incident Command - Root Cause Evidence",
    "Incident Command - Human Approved Remediation Ledger",
    "Incident Command - Splunk MCP Investigation Context",
    "Incident Command - Blast Radius By Service",
]

REQUIRED_DASHBOARD_TERMS = [
    "Agentic Incident Command Center",
    "agentops_events",
    "Incident Timeline",
    "Root-Cause Evidence Ranking",
    "MCP Remediation Ledger",
    "Splunk MCP Investigation Context",
    "Blast Radius By Service",
]


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "status": "pass" if passed else "fail", "detail": detail})


def validate(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    missing = [item for item in REQUIRED_FILES if not (root / item).exists()]
    add_check(checks, "required Splunk app files", not missing, "missing: " + ", ".join(missing) if missing else f"{len(REQUIRED_FILES)} files present")

    app_conf = root / "splunk_app/agentops_control_tower/default/app.conf"
    if app_conf.exists():
        parser = configparser.ConfigParser()
        parser.read(app_conf, encoding="utf-8")
        add_check(checks, "app.conf ui label", parser.get("ui", "label", fallback="") == "Agentic Incident Command Center", "ui.label checked")
        add_check(checks, "app.conf package id", parser.get("package", "id", fallback="") == "agentops_control_tower", "package.id checked")

    saved_searches = root / "splunk_app/agentops_control_tower/default/savedsearches.conf"
    if saved_searches.exists():
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(saved_searches, encoding="utf-8")
        missing_searches = [name for name in REQUIRED_SEARCH_NAMES if name not in parser.sections()]
        add_check(checks, "saved searches present", not missing_searches, "missing: " + ", ".join(missing_searches) if missing_searches else f"{len(REQUIRED_SEARCH_NAMES)} searches present")
        missing_index = [
            name for name in REQUIRED_SEARCH_NAMES
            if name in parser and "index=agentops_events" not in parser[name].get("search", "")
        ]
        add_check(checks, "saved searches use agentops_events", not missing_index, "missing index in: " + ", ".join(missing_index) if missing_index else "all required searches use agentops_events")

    indexes_conf = root / "splunk_app/agentops_control_tower/default/indexes.conf"
    if indexes_conf.exists():
        parser = configparser.ConfigParser()
        parser.read(indexes_conf, encoding="utf-8")
        add_check(checks, "indexes.conf agentops_events", "agentops_events" in parser.sections(), "agentops_events present")
        add_check(checks, "indexes.conf safe storage paths", parser.get("agentops_events", "homePath", fallback="").startswith("$SPLUNK_DB/"), "uses $SPLUNK_DB")

    props_conf = root / "splunk_app/agentops_control_tower/default/props.conf"
    if props_conf.exists():
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        parser.read(props_conf, encoding="utf-8")
        add_check(checks, "props.conf sourcetype", "agentops:events" in parser.sections(), "agentops:events present")
        add_check(checks, "props.conf csv extraction", parser.get("agentops:events", "INDEXED_EXTRACTIONS", fallback="") == "csv", "INDEXED_EXTRACTIONS checked")
        add_check(checks, "props.conf timestamp field", parser.get("agentops:events", "TIMESTAMP_FIELDS", fallback="") == "timestamp", "TIMESTAMP_FIELDS checked")

    dashboard = root / "splunk_app/agentops_control_tower/default/data/ui/views/agentops_control_tower.xml"
    if dashboard.exists():
        try:
            tree = ET.parse(dashboard)
            root_node = tree.getroot()
            add_check(checks, "dashboard XML parses", root_node.tag == "form", f"root={root_node.tag}")
        except ET.ParseError as error:
            add_check(checks, "dashboard XML parses", False, str(error))
            root_node = None
        text = dashboard.read_text(encoding="utf-8")
        missing_terms = [term for term in REQUIRED_DASHBOARD_TERMS if term not in text]
        add_check(checks, "dashboard required terms", not missing_terms, "missing: " + ", ".join(missing_terms) if missing_terms else "all key terms present")
        if root_node is not None:
            query_count = len(root_node.findall(".//query"))
            add_check(checks, "dashboard query count", query_count >= 6, f"queries={query_count}")

    failed = [check for check in checks if check["status"] != "pass"]
    return {
        "status": "pass" if not failed else "fail",
        "failed_count": len(failed),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the local Splunk app candidate.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    report = validate(Path(args.root).resolve())
    print(json.dumps({"status": report["status"], "failed_count": report["failed_count"]}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
