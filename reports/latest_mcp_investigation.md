# Splunk MCP Investigation Preview

This deterministic preview shows the answer an AI incident commander should produce after querying Splunk evidence through Splunk MCP Server.

## Question

What likely caused the checkout incident, and which remediation needs human approval first?

## Answer

The most likely cause is checkout-api release regression with confidence 100%.
The ranking is grounded in deploy proximity, application error spike, APM latency, and supporting database context.
The first human decision should be the rollback approval because it is high impact and blocked by the remediation approval ledger.
1. edge-waf / evt-0007 requires review: Prepare temporary WAF watch rule, not a hard block. (splunk://agentops_events/inc-checkout-20260603-0900/0007)
2. checkout-api / evt-0010 requires review: Rollback checkout-api to 2026.06.02.4. (splunk://agentops_events/inc-checkout-20260603-0900/0010)
3. incident-command / evt-0012 requires review: Preserve redacted audit event; do not expose credentials. (splunk://agentops_events/inc-checkout-20260603-0900/0012)

## Evidence

- `evt-0002` / `checkout-api` / risk `100` / splunk://agentops_events/inc-checkout-20260603-0900/0002 / Checkout API 5xx rate jumped from 0.2% to 14.8% after the release.
- `evt-0010` / `checkout-api` / risk `100` / splunk://agentops_events/inc-checkout-20260603-0900/0010 / Rollback to release 2026.06.02.4 is proposed but blocked until human approval.
- `evt-0003` / `checkout-api` / risk `80` / splunk://agentops_events/inc-checkout-20260603-0900/0003 / p95 latency increased from 240ms to 2.8s for POST /checkout.
- `evt-0007` / `edge-waf` / risk `100` / splunk://agentops_events/inc-checkout-20260603-0900/0007 / WAF detected probing against checkout paths without a matching exploit signature.
- `evt-0010` / `checkout-api` / risk `100` / splunk://agentops_events/inc-checkout-20260603-0900/0010 / Rollback to release 2026.06.02.4 is proposed but blocked until human approval.
- `evt-0012` / `incident-command` / risk `100` / splunk://agentops_events/inc-checkout-20260603-0900/0012 / A proposed tool call attempted to inspect a credential-like path during incident response and was blocked.

## SPL

```spl
index=agentops_events incident_id="inc-checkout-20260603-0900" | sort _time | table _time signal_domain service event_type risk_score evidence_ref message
```
