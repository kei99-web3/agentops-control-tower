from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


JST = timezone(timedelta(hours=9))


SEVERITY_SCORE = {
    "info": 5,
    "low": 20,
    "medium": 45,
    "high": 70,
    "critical": 90,
}

EXTERNAL_ACTION_BONUS = {
    "none": 0,
    "incident_ticket": 10,
    "stakeholder_notify": 20,
    "cloud_rollback": 35,
    "security_rule_change": 40,
}

APPROVAL_BONUS = {
    "not_required": 0,
    "approved": 0,
    "pending_user": 20,
    "missing": 35,
    "expired": 30,
    "revoked": 45,
    "blocked_by_policy": 50,
}


@dataclass(frozen=True)
class Paths:
    root: Path
    data_dir: Path
    reports_dir: Path
    submission_dir: Path

    @classmethod
    def from_root(cls, root: Path) -> "Paths":
        return cls(
            root=root,
            data_dir=root / "data",
            reports_dir=root / "reports",
            submission_dir=root / "submission",
        )


def now_iso() -> str:
    return datetime.now(JST).replace(microsecond=0).isoformat()


def ensure_dirs(paths: Paths) -> None:
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    paths.reports_dir.mkdir(parents=True, exist_ok=True)
    paths.submission_dir.mkdir(parents=True, exist_ok=True)


def risk_score(event: dict[str, Any]) -> int:
    score = SEVERITY_SCORE.get(event.get("severity", "info"), 5)
    score += EXTERNAL_ACTION_BONUS.get(event.get("external_action", "none"), 0)
    score += APPROVAL_BONUS.get(event.get("approval_state", "not_required"), 0)
    if event.get("policy_decision") == "deny":
        score += 15
    if event.get("requires_human_approval"):
        score += 10
    if "credential_boundary" in event.get("tags", []):
        score += 35
    if "customer_impact" in event.get("tags", []):
        score += 10
    return min(score, 100)


def generate_synthetic_events(path: Path) -> list[dict[str, Any]]:
    base = datetime(2026, 6, 3, 9, 0, tzinfo=JST)
    incident_id = "inc-checkout-20260603-0900"
    seeds = [
        seed(0, "change_intelligence", "checkout-api", "deployment", "deploy_completed", "medium", "Checkout API release 2026.06.03.1 completed 11 minutes before the error spike.", "deploy.version", "2026.06.03.1", "2026.06.02.4", "checkout-api release regression", 34, "none", "not_required", "allow", "Compare the release window with error and latency spikes before approving rollback.", "Inspect deploy diff and recent config changes.", False, "none", ["deploy", "change", "checkout"]),
        seed(8, "service_observability", "checkout-api", "application", "error_rate_spike", "critical", "Checkout API 5xx rate jumped from 0.2% to 14.8% after the release.", "http.5xx_rate", "14.8%", "0.2%", "checkout-api release regression", 30, "none", "not_required", "review", "Prioritize checkout outage investigation and collect the affected endpoint list.", "Open checkout service incident runbook.", False, "none", ["observability", "customer_impact", "checkout"]),
        seed(10, "apm_latency_monitor", "checkout-api", "apm", "latency_regression", "high", "p95 latency increased from 240ms to 2.8s for POST /checkout.", "checkout.p95_latency_ms", "2800", "240", "checkout-api release regression", 22, "none", "not_required", "review", "Correlate slow traces with the deploy and database connection pool telemetry.", "Open APM trace comparison for POST /checkout.", False, "none", ["observability", "apm", "customer_impact"]),
        seed(11, "database_monitor", "payments-db", "database", "connection_pool_pressure", "high", "Payments DB connection pool saturation rose to 92% during the checkout error spike.", "db.connection_pool_utilization", "92%", "38%", "database pool saturation", 18, "none", "not_required", "review", "Treat DB pressure as a contributing factor until trace evidence proves it is primary.", "Check connection pool settings and slow query sample.", False, "none", ["database", "observability"]),
        seed(12, "identity_security", "auth-gateway", "security", "auth_failure_burst", "medium", "Auth failures increased from a single ASN but did not align with checkout error start.", "auth.failed_login_count", "480", "45", "credential attack distraction", 9, "none", "not_required", "review", "Keep security watch active but do not make it the primary outage cause yet.", "Attach auth anomaly context to the incident.", False, "none", ["security", "identity"]),
        seed(13, "edge_network", "edge-us-west", "network", "packet_loss_warning", "medium", "Edge packet loss reached 2.2% in one region after the checkout regression was already visible.", "edge.packet_loss_percent", "2.2%", "0.1%", "regional network degradation", 6, "none", "not_required", "review", "Route network signal to supporting evidence, not primary rollback justification.", "Check regional edge health and route impact.", False, "none", ["network", "observability"]),
        seed(14, "waf_security", "edge-waf", "security", "waf_probe_detected", "medium", "WAF detected probing against checkout paths without a matching exploit signature.", "waf.probe_count", "173", "12", "credential attack distraction", 7, "security_rule_change", "pending_user", "review", "Approve a temporary WAF watch rule only after confirming it will not block valid checkout traffic.", "Prepare temporary WAF watch rule, not a hard block.", True, "none", ["security", "approval_required"]),
        seed(15, "splunk_mcp_investigator", "incident-command", "mcp", "spl_query_requested", "low", "AI incident commander requested Splunk context for timeline, blast radius, and root-cause ranking.", "mcp.query_count", "4", "0", "investigation_context", 0, "none", "not_required", "allow", "Use Splunk evidence citations before taking remediation action.", "Run incident timeline, root-cause ranking, approval ledger, and blast radius SPL.", False, "splunk_search", ["mcp", "splunk", "investigation"]),
        seed(16, "ai_incident_commander", "incident-command", "ai_correlation", "root_cause_ranked", "high", "AI ranked checkout-api release regression as the most likely cause using deploy proximity, error spike, and APM evidence.", "root_cause.confidence", "86", "0", "checkout-api release regression", 26, "none", "not_required", "review", "Review the rollback recommendation and confirm a human owner before action.", "Promote checkout rollback to first human decision.", False, "none", ["ai", "root_cause", "incident_command"]),
        seed(17, "remediation_orchestrator", "checkout-api", "remediation", "rollback_proposed", "high", "Rollback to release 2026.06.02.4 is proposed but blocked until human approval.", "runbook.rollback_candidate", "2026.06.02.4", "none", "checkout-api release regression", 20, "cloud_rollback", "pending_user", "review", "Approve or reject rollback after checking deploy owner, current traffic, and DB pool status.", "Rollback checkout-api to 2026.06.02.4.", True, "none", ["remediation", "approval_required", "customer_impact"]),
        seed(18, "communications_orchestrator", "incident-command", "communications", "stakeholder_update_prepared", "medium", "Customer-support and internal stakeholder update is drafted but not sent.", "comm.update_ready", "true", "false", "incident_response_coordination", 0, "stakeholder_notify", "pending_user", "review", "Review wording and send only after incident commander confirms customer impact.", "Send concise incident update to support and engineering leads.", True, "none", ["communications", "approval_required"]),
        seed(19, "mcp_runtime_guard", "incident-command", "mcp_security", "credential_boundary_blocked", "critical", "A proposed tool call attempted to inspect a credential-like path during incident response and was blocked.", "mcp.blocked_tool_calls", "1", "0", "governance_control", 0, "none", "blocked_by_policy", "deny", "Keep the tool call blocked and cite redacted evidence only.", "Preserve redacted audit event; do not expose credentials.", False, "filesystem_read", ["mcp", "credential_boundary", "policy"]),
        seed(20, "ticketing_orchestrator", "incident-command", "platform", "incident_ticket_ready", "low", "Incident ticket payload is ready with timeline, root-cause candidates, and approval ledger links.", "ticket.ready", "true", "false", "incident_response_coordination", 0, "incident_ticket", "approved", "allow", "Create ticket only in approved internal project space.", "Create incident ticket with Splunk evidence references.", False, "none", ["platform", "ticketing"]),
    ]

    events: list[dict[str, Any]] = []
    for counter, item in enumerate(seeds, start=1):
        ts = base + timedelta(minutes=int(item["minute"]))
        event = {
            "event_id": f"evt-{counter:04d}",
            "timestamp": ts.isoformat(),
            "workspace": "synthetic_retail_saas",
            "incident_id": incident_id,
            "component": item["component"],
            "service": item["service"],
            "run_id": f"run-{incident_id}",
            "event_type": item["event_type"],
            "severity": item["severity"],
            "risk_domain": classify_risk_domain(item["tags"], item["signal_domain"], item["external_action"]),
            "signal_domain": item["signal_domain"],
            "external_action": item["external_action"],
            "approval_state": item["approval_state"],
            "policy_decision": item["policy_decision"],
            "requires_human_approval": item["requires_human_approval"],
            "mcp_tool": item["mcp_tool"],
            "evidence_ref": f"splunk://agentops_events/{incident_id}/{counter:04d}",
            "message": item["message"],
            "metric_name": item["metric_name"],
            "observed_value": item["observed_value"],
            "baseline_value": item["baseline_value"],
            "root_cause_candidate": item["root_cause_candidate"],
            "root_cause_weight": item["root_cause_weight"],
            "recommended_human_action": item["recommended_human_action"],
            "runbook_action": item["runbook_action"],
            "tags": item["tags"],
        }
        event["risk_score"] = risk_score(event)
        events.append(event)

    with path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return events


def seed(
    minute: int,
    component: str,
    service: str,
    signal_domain: str,
    event_type: str,
    severity: str,
    message: str,
    metric_name: str,
    observed_value: str,
    baseline_value: str,
    root_cause_candidate: str,
    root_cause_weight: int,
    external_action: str,
    approval_state: str,
    policy_decision: str,
    recommended_human_action: str,
    runbook_action: str,
    requires_human_approval: bool,
    mcp_tool: str,
    tags: list[str],
) -> dict[str, Any]:
    return locals()


def classify_risk_domain(tags: list[str], signal_domain: str, external_action: str) -> str:
    if "credential_boundary" in tags:
        return "credential_boundary"
    if "approval_required" in tags or external_action != "none":
        return "remediation_approval"
    if signal_domain in {"security", "mcp_security"}:
        return "security_signal"
    if signal_domain in {"application", "apm", "database", "network"}:
        return "observability_signal"
    if signal_domain == "deployment":
        return "change_signal"
    if signal_domain == "mcp":
        return "mcp_runtime"
    return "incident_command"


def load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def analyze_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    by_incident: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_service: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_incident[event["incident_id"]].append(event)
        by_service[event["service"]].append(event)

    candidates = root_cause_candidates(events)
    approval_queue = approval_queue_items(events)
    incident_summaries = []
    for incident_id, incident_events in sorted(by_incident.items()):
        primary = candidates[0]
        incident_summaries.append({
            "incident_id": incident_id,
            "status": "needs_human_remediation_approval" if approval_queue else "investigating",
            "max_risk": max(event["risk_score"] for event in incident_events),
            "event_count": len(incident_events),
            "impacted_services": sorted({event["service"] for event in incident_events}),
            "primary_root_cause": primary["candidate"],
            "primary_confidence": primary["confidence"],
            "recommended_human_action": primary["recommended_human_action"],
        })

    service_impact = []
    for service, service_events in sorted(by_service.items()):
        service_impact.append({
            "service": service,
            "event_count": len(service_events),
            "max_risk": max(event["risk_score"] for event in service_events),
            "domains": sorted({event["signal_domain"] for event in service_events}),
            "top_message": max(service_events, key=lambda item: item["risk_score"])["message"],
        })

    ledger = remediation_ledger(events)
    return {
        "generated_at": now_iso(),
        "project_name": "Agentic Incident Command Center",
        "tagline": "Splunk-grounded AI incident commander with human-approved remediation.",
        "event_count": len(events),
        "incident_count": len(by_incident),
        "service_count": len(by_service),
        "max_risk": max((event["risk_score"] for event in events), default=0),
        "blocked_count": sum(1 for event in events if event["policy_decision"] == "deny"),
        "approval_queue_count": len(approval_queue),
        "mcp_event_count": sum(1 for event in events if event["mcp_tool"] != "none"),
        "incident_summaries": incident_summaries,
        "service_impact": sorted(service_impact, key=lambda item: item["max_risk"], reverse=True),
        "root_cause_candidates": candidates,
        "approval_queue": approval_queue,
        "remediation_ledger": ledger,
        "safety_ledger": ledger,
        "spl_queries": spl_queries(),
        "mcp_investigation": mock_mcp_investigation(approval_queue, candidates),
    }


def root_cause_candidates(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    excluded = {"investigation_context", "governance_control", "incident_response_coordination"}
    for event in events:
        candidate = event["root_cause_candidate"]
        if candidate in excluded:
            continue
        item = buckets.setdefault(candidate, {"candidate": candidate, "score": 0, "evidence": [], "domains": set(), "services": set()})
        item["score"] += int(event["root_cause_weight"])
        if event["risk_score"] >= 70:
            item["score"] += 8
        if "customer_impact" in event["tags"]:
            item["score"] += 6
        item["evidence"].append({
            "event_id": event["event_id"],
            "signal_domain": event["signal_domain"],
            "service": event["service"],
            "risk_score": event["risk_score"],
            "evidence_ref": event["evidence_ref"],
            "message": event["message"],
        })
        item["domains"].add(event["signal_domain"])
        item["services"].add(event["service"])

    max_score = max((item["score"] for item in buckets.values()), default=1)
    candidates = []
    for item in buckets.values():
        candidates.append({
            "candidate": item["candidate"],
            "score": item["score"],
            "confidence": round((item["score"] / max_score) * 100),
            "domains": sorted(item["domains"]),
            "services": sorted(item["services"]),
            "evidence": sorted(item["evidence"], key=lambda row: row["risk_score"], reverse=True),
            "recommended_human_action": candidate_recommendation(item["candidate"]),
        })
    return sorted(candidates, key=lambda item: item["score"], reverse=True)


def candidate_recommendation(candidate: str) -> str:
    recommendations = {
        "checkout-api release regression": "Approve or reject rollback after checking deploy owner, current traffic, and database pressure.",
        "database pool saturation": "Keep DB mitigation ready, but do not treat it as primary until trace evidence beats deploy proximity.",
        "credential attack distraction": "Keep security monitoring active and avoid blocking checkout traffic without proof.",
        "regional network degradation": "Treat network degradation as supporting evidence unless blast-radius expands.",
    }
    return recommendations.get(candidate, "Review candidate evidence before taking action.")


def approval_queue_items(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = [
        event for event in events
        if event["requires_human_approval"]
        or event["approval_state"] in {"pending_user", "missing", "expired", "revoked", "blocked_by_policy"}
        or event["policy_decision"] == "deny"
    ]
    return sorted([ledger_row(event) for event in items], key=lambda item: item["risk_score"], reverse=True)


def remediation_ledger(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        ledger_row(event)
        for event in events
        if event["risk_score"] >= 45
        or event["external_action"] != "none"
        or event["approval_state"] != "not_required"
        or event["mcp_tool"] != "none"
    ]
    return sorted(rows, key=lambda item: (item["requires_human_approval"], item["risk_score"]), reverse=True)


def ledger_row(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event["event_id"],
        "timestamp": event["timestamp"],
        "incident_id": event["incident_id"],
        "component": event["component"],
        "service": event["service"],
        "risk_domain": event["risk_domain"],
        "signal_domain": event["signal_domain"],
        "risk_score": event["risk_score"],
        "external_action": event["external_action"],
        "approval_state": event["approval_state"],
        "policy_decision": event["policy_decision"],
        "requires_human_approval": event["requires_human_approval"],
        "mcp_tool": event["mcp_tool"],
        "evidence_ref": event["evidence_ref"],
        "message": event["message"],
        "recommended_human_action": event["recommended_human_action"],
        "runbook_action": event["runbook_action"],
    }


def spl_queries() -> list[dict[str, str]]:
    return [
        {
            "name": "Incident timeline across observability, security, network, deploy, and MCP",
            "query": 'index=agentops_events incident_id="inc-checkout-20260603-0900" | sort _time | table _time signal_domain service event_type risk_score evidence_ref message',
        },
        {
            "name": "Root-cause evidence for checkout regression",
            "query": 'index=agentops_events incident_id="inc-checkout-20260603-0900" root_cause_candidate!="incident_response_coordination" | stats sum(root_cause_weight) as evidence_score values(signal_domain) as domains values(evidence_ref) as evidence by root_cause_candidate | sort -evidence_score',
        },
        {
            "name": "Human-approved remediation ledger",
            "query": 'index=agentops_events requires_human_approval=true OR policy_decision="deny" | sort -risk_score | table _time service external_action approval_state policy_decision runbook_action evidence_ref',
        },
        {
            "name": "Splunk MCP investigation context",
            "query": 'index=agentops_events mcp_tool!="none" OR signal_domain="ai_correlation" | table _time component mcp_tool event_type evidence_ref recommended_human_action',
        },
        {
            "name": "Blast radius by service",
            "query": 'index=agentops_events incident_id="inc-checkout-20260603-0900" | stats count max(risk_score) as max_risk values(signal_domain) as domains by service | sort -max_risk',
        },
    ]


def event_schema() -> dict[str, Any]:
    required = [
        "event_id", "timestamp", "workspace", "incident_id", "component", "service",
        "run_id", "event_type", "severity", "risk_score", "risk_domain", "signal_domain",
        "external_action", "approval_state", "policy_decision", "requires_human_approval",
        "mcp_tool", "evidence_ref", "message", "metric_name", "observed_value",
        "baseline_value", "root_cause_candidate", "root_cause_weight",
        "recommended_human_action", "runbook_action", "tags",
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Agentic incident command event",
        "type": "object",
        "required": required,
        "properties": {
            "event_id": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"},
            "workspace": {"type": "string"},
            "incident_id": {"type": "string"},
            "component": {"type": "string"},
            "service": {"type": "string"},
            "run_id": {"type": "string"},
            "event_type": {"type": "string"},
            "severity": {"enum": ["info", "low", "medium", "high", "critical"]},
            "risk_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "risk_domain": {"type": "string"},
            "signal_domain": {"type": "string"},
            "external_action": {"type": "string"},
            "approval_state": {"type": "string"},
            "policy_decision": {"enum": ["allow", "review", "deny"]},
            "requires_human_approval": {"type": "boolean"},
            "mcp_tool": {"type": "string"},
            "evidence_ref": {"type": "string"},
            "message": {"type": "string"},
            "metric_name": {"type": "string"},
            "observed_value": {"type": "string"},
            "baseline_value": {"type": "string"},
            "root_cause_candidate": {"type": "string"},
            "root_cause_weight": {"type": "integer"},
            "recommended_human_action": {"type": "string"},
            "runbook_action": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
        },
    }


def mock_mcp_investigation(approval_queue: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    primary = candidates[0] if candidates else None
    top_approvals = approval_queue[:3]
    if primary is None:
        return {
            "question": "What caused the checkout incident and what action needs approval first?",
            "answer": "No root-cause candidate is available.",
            "evidence": [],
            "spl": 'index=agentops_events incident_id="inc-checkout-20260603-0900"',
        }
    lines = [
        f"The most likely cause is {primary['candidate']} with confidence {primary['confidence']}%.",
        "The ranking is grounded in deploy proximity, application error spike, APM latency, and supporting database context.",
        "The first human decision should be the rollback approval because it is high impact and blocked by the remediation approval ledger.",
    ]
    for index, item in enumerate(top_approvals, start=1):
        lines.append(f"{index}. {item['service']} / {item['event_id']} requires review: {item['runbook_action']} ({item['evidence_ref']})")
    evidence = primary["evidence"][:3] + [
        {
            "event_id": item["event_id"],
            "service": item["service"],
            "risk_score": item["risk_score"],
            "evidence_ref": item["evidence_ref"],
            "message": item["message"],
        }
        for item in top_approvals
    ]
    return {
        "question": "What likely caused the checkout incident, and which remediation needs human approval first?",
        "answer": "\n".join(lines),
        "evidence": evidence,
        "spl": 'index=agentops_events incident_id="inc-checkout-20260603-0900" | sort _time | table _time signal_domain service event_type risk_score evidence_ref message',
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, events: list[dict[str, Any]]) -> None:
    fieldnames = [
        "timestamp", "event_id", "workspace", "incident_id", "component", "service",
        "run_id", "event_type", "severity", "risk_score", "risk_domain", "signal_domain",
        "external_action", "approval_state", "policy_decision", "requires_human_approval",
        "mcp_tool", "evidence_ref", "message", "metric_name", "observed_value",
        "baseline_value", "root_cause_candidate", "root_cause_weight",
        "recommended_human_action", "runbook_action", "tags",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            row = {key: event.get(key, "") for key in fieldnames}
            row["tags"] = ";".join(event.get("tags", []))
            writer.writerow(row)


def write_spl_queries(path: Path, queries: list[dict[str, str]]) -> None:
    body = [
        "# SPL Queries",
        "",
        "Use these after importing `data/splunk_agentops_events.csv` into the `agentops_events` index.",
        "The query pack demonstrates a cross-domain incident command workflow over synthetic data.",
        "",
        "For local proof before live Splunk access is approved, run:",
        "",
        "```powershell",
        "python scripts\\run_local_spl_query_pack.py",
        "```",
        "",
        "This writes `reports/latest_local_spl_query_results.html` and `.json` with equivalent table results over the generated CSV. It is a local emulation, not live Splunk verification.",
        "",
    ]
    for query in queries:
        body.extend([f"## {query['name']}", "", "```spl", query["query"], "```", ""])
    path.write_text("\n".join(body), encoding="utf-8")


def write_mcp_investigation(path: Path, investigation: dict[str, Any]) -> None:
    body = [
        "# Splunk MCP Investigation Preview",
        "",
        "This deterministic preview shows the answer an AI incident commander should produce after querying Splunk evidence through Splunk MCP Server.",
        "",
        "## Question",
        "",
        investigation["question"],
        "",
        "## Answer",
        "",
        investigation["answer"],
        "",
        "## Evidence",
        "",
    ]
    for item in investigation["evidence"]:
        body.append(f"- `{item['event_id']}` / `{item.get('service', '')}` / risk `{item['risk_score']}` / {item['evidence_ref']} / {item['message']}")
    body.extend(["", "## SPL", "", "```spl", investigation["spl"], "```", ""])
    path.write_text("\n".join(body), encoding="utf-8")


def render_html(path: Path, analysis: dict[str, Any]) -> None:
    incident_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['incident_id'])}</td>"
        f"<td>{esc(item['status'])}</td>"
        f"<td>{item['max_risk']}</td>"
        f"<td>{esc(', '.join(item['impacted_services']))}</td>"
        f"<td>{esc(item['primary_root_cause'])}</td>"
        f"<td>{item['primary_confidence']}%</td>"
        f"<td>{esc(item['recommended_human_action'])}</td>"
        "</tr>"
        for item in analysis["incident_summaries"]
    )
    candidate_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['candidate'])}</td>"
        f"<td>{item['confidence']}%</td>"
        f"<td>{esc(', '.join(item['domains']))}</td>"
        f"<td>{esc(', '.join(item['services']))}</td>"
        f"<td>{esc(item['recommended_human_action'])}</td>"
        "</tr>"
        for item in analysis["root_cause_candidates"]
    )
    service_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['service'])}</td>"
        f"<td>{item['max_risk']}</td>"
        f"<td>{esc(', '.join(item['domains']))}</td>"
        f"<td>{esc(item['top_message'])}</td>"
        "</tr>"
        for item in analysis["service_impact"]
    )
    ledger_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['event_id'])}</td>"
        f"<td>{esc(item['service'])}</td>"
        f"<td>{esc(item['signal_domain'])}</td>"
        f"<td>{item['risk_score']}</td>"
        f"<td>{esc(item['external_action'])}</td>"
        f"<td>{esc(item['approval_state'])}</td>"
        f"<td>{esc(item['policy_decision'])}</td>"
        f"<td>{esc(item['runbook_action'])}</td>"
        "</tr>"
        for item in analysis["remediation_ledger"]
    )
    query_cards = "\n".join(f"<article><h3>{esc(query['name'])}</h3><pre>{esc(query['query'])}</pre></article>" for query in analysis["spl_queries"])
    investigation = analysis["mcp_investigation"]
    evidence_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['event_id'])}</td>"
        f"<td>{esc(item.get('service', ''))}</td>"
        f"<td>{item['risk_score']}</td>"
        f"<td>{esc(item['evidence_ref'])}</td>"
        f"<td>{esc(item['message'])}</td>"
        "</tr>"
        for item in investigation["evidence"]
    )
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agentic Incident Command Center</title>
  <style>
    :root {{ color-scheme: light; --bg:#f5f7fa; --ink:#14212b; --muted:#5e6b77; --line:#d8e1ea; --panel:#fff; --accent:#087568; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Arial, Helvetica, sans-serif; background:var(--bg); color:var(--ink); line-height:1.45; }}
    header {{ padding:28px 36px 18px; background:#14212b; color:#fff; border-bottom:4px solid var(--accent); }}
    header p {{ max-width:960px; color:#d9e1ea; }}
    main {{ max-width:1200px; margin:0 auto; padding:24px; }}
    .kpis {{ display:grid; grid-template-columns:repeat(6, minmax(120px, 1fr)); gap:12px; margin-bottom:20px; }}
    .kpi, article, section {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:0 1px 2px rgba(20,33,43,.06); }}
    .kpi {{ padding:16px; }}
    .kpi strong {{ display:block; font-size:28px; margin-top:6px; }}
    .kpi span {{ color:var(--muted); font-size:13px; }}
    section {{ padding:18px; margin-bottom:20px; }}
    h1, h2, h3 {{ margin-top:0; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th, td {{ border-bottom:1px solid var(--line); padding:10px; text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:0; }}
    pre {{ white-space:pre-wrap; overflow-wrap:anywhere; background:#eef3f7; padding:12px; border-radius:6px; }}
    .queries {{ display:grid; grid-template-columns:repeat(2, minmax(260px, 1fr)); gap:12px; }}
    .note {{ color:var(--muted); }}
    @media (max-width:900px) {{ header {{ padding:22px 18px 14px; }} main {{ padding:14px; }} .kpis,.queries {{ grid-template-columns:1fr; }} table {{ font-size:12px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Agentic Incident Command Center</h1>
    <p>Splunk-grounded AI incident commander with human-approved remediation. This local demo uses synthetic observability, security, network, deploy, and MCP events only.</p>
  </header>
  <main>
    <div class="kpis">
      <div class="kpi"><span>Events</span><strong>{analysis['event_count']}</strong></div>
      <div class="kpi"><span>Incidents</span><strong>{analysis['incident_count']}</strong></div>
      <div class="kpi"><span>Services</span><strong>{analysis['service_count']}</strong></div>
      <div class="kpi"><span>Max Risk</span><strong>{analysis['max_risk']}</strong></div>
      <div class="kpi"><span>Blocked</span><strong>{analysis['blocked_count']}</strong></div>
      <div class="kpi"><span>Approval Queue</span><strong>{analysis['approval_queue_count']}</strong></div>
    </div>
    <section><h2>Incident Command Summary</h2><table><thead><tr><th>Incident</th><th>Status</th><th>Max Risk</th><th>Impacted Services</th><th>Primary Cause</th><th>Confidence</th><th>Recommended Action</th></tr></thead><tbody>{incident_rows}</tbody></table></section>
    <section><h2>Root-Cause Ranking</h2><table><thead><tr><th>Candidate</th><th>Confidence</th><th>Domains</th><th>Services</th><th>Human Decision</th></tr></thead><tbody>{candidate_rows}</tbody></table></section>
    <section><h2>Blast Radius By Service</h2><table><thead><tr><th>Service</th><th>Max Risk</th><th>Domains</th><th>Top Evidence</th></tr></thead><tbody>{service_rows}</tbody></table></section>
    <section><h2>MCP Remediation Ledger</h2><p class="note">High-impact remediation stays human-approved and evidence-backed. The AI can recommend rollback, WAF watch, ticketing, and stakeholder updates, but risky actions remain gated.</p><table><thead><tr><th>Event</th><th>Service</th><th>Domain</th><th>Risk</th><th>Action</th><th>Approval</th><th>Decision</th><th>Runbook</th></tr></thead><tbody>{ledger_rows}</tbody></table></section>
    <section><h2>Splunk Queries For Demo</h2><div class="queries">{query_cards}</div></section>
    <section><h2>Splunk MCP Investigation Preview</h2><p class="note">{esc(investigation['question'])}</p><pre>{esc(investigation['answer'])}</pre><table><thead><tr><th>Event</th><th>Service</th><th>Risk</th><th>Evidence</th><th>Message</th></tr></thead><tbody>{evidence_rows}</tbody></table></section>
  </main>
</body>
</html>
"""
    path.write_text(html_doc, encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def run_demo(root: Path) -> dict[str, Any]:
    paths = Paths.from_root(root)
    ensure_dirs(paths)
    events_path = paths.data_dir / "synthetic_agentops_events.jsonl"
    schema_path = paths.data_dir / "agentops_event_schema.json"
    csv_path = paths.data_dir / "splunk_agentops_events.csv"
    analysis_path = paths.reports_dir / "latest_analysis.json"
    html_path = paths.reports_dir / "latest_control_tower.html"
    investigation_path = paths.reports_dir / "latest_mcp_investigation.md"
    spl_queries_path = paths.submission_dir / "SPL_QUERIES.md"

    events = generate_synthetic_events(events_path)
    analysis = analyze_events(events)
    write_csv(csv_path, events)
    write_json(schema_path, event_schema())
    write_json(analysis_path, analysis)
    write_mcp_investigation(investigation_path, analysis["mcp_investigation"])
    write_spl_queries(spl_queries_path, analysis["spl_queries"])
    render_html(html_path, analysis)
    return {
        "events": str(events_path),
        "schema": str(schema_path),
        "csv": str(csv_path),
        "analysis": str(analysis_path),
        "mcp_investigation": str(investigation_path),
        "spl_queries": str(spl_queries_path),
        "html": str(html_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Agentic Incident Command Center local demo.")
    parser.add_argument("command", choices=["run-demo", "generate", "analyze"], help="Command to run.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="Project root.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    paths = Paths.from_root(root)
    ensure_dirs(paths)

    if args.command == "run-demo":
        outputs = run_demo(root)
        print(json.dumps(outputs, indent=2, ensure_ascii=False))
        return 0

    events_path = paths.data_dir / "synthetic_agentops_events.jsonl"
    if args.command == "generate":
        events = generate_synthetic_events(events_path)
        print(f"generated {len(events)} events at {events_path}")
        return 0

    if args.command == "analyze":
        events = load_events(events_path)
        analysis = analyze_events(events)
        write_json(paths.reports_dir / "latest_analysis.json", analysis)
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
