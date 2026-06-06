# Agentic Incident Command Center Splunk App Candidate

This folder is a local Splunk app candidate for the hackathon demo. It is not installed, published, or connected to any Splunk environment by default.

## Contents

- `default/app.conf`: minimal app metadata.
- `default/indexes.conf`: optional local index definition for `agentops_events`.
- `default/props.conf`: CSV parsing and timestamp settings for the `agentops:events` sourcetype.
- `default/savedsearches.conf`: reusable searches for incident timeline, root-cause evidence, human-approved remediation ledger, Splunk MCP investigation context, and blast radius.
- `default/data/ui/views/agentops_control_tower.xml`: Simple XML dashboard candidate.
- `metadata/default.meta`: read permissions for app objects.

## Local Package

From the repository root, run:

```powershell
python scripts\package_splunk_app.py
```

This writes `dist/agentops-control-tower-splunk-app.spl` and a local package manifest. It does not install the app, upload it, publish it, connect to Splunk, or submit anything.

## Intended Setup After Approval

1. Import `data/splunk_agentops_events.csv` into a Splunk index named `agentops_events` with sourcetype `agentops:events`.
2. Copy or install this app folder into an approved Splunk environment.
3. Open the `Agentic Incident Command Center` dashboard.
4. Verify the incident timeline, root-cause evidence, MCP Remediation Ledger, Splunk MCP investigation context, and blast-radius panels.
5. Configure Splunk MCP Server only after credentials and scope are approved.

## Safety Boundary

Use synthetic data only. Do not import private logs, credentials, account data, customer data, or personal data into the public demo.
