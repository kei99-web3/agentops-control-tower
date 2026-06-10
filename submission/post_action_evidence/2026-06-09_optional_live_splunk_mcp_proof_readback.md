# Optional Live Splunk MCP Proof Readback

Status: ready_for_claim_update
Captured at: 2026-06-09 JST
Environment: Local Splunk Enterprise Docker proof environment
Data boundary: synthetic data only

## Official App

- Splunkbase app: Splunk MCP Server
- Downloaded file: `splunk-mcp-server_120.tgz`
- SHA256 expected: `fa3c2d7ef500148d9ee2f2b92f1b2e5e3026401ca57138ffdfab20710f7d695c`
- SHA256 actual: `fa3c2d7ef500148d9ee2f2b92f1b2e5e3026401ca57138ffdfab20710f7d695c`
- Checksum match: yes
- Installed app name in Splunk: `Splunk_MCP_Server`
- App state: enabled, visible

## Official MCP Connection

- MCP token generation endpoint: passed
- Token handling: encrypted token generated for the ephemeral local proof session; token value was not saved to this evidence file.
- MCP endpoint tested: `https://localhost:18089/services/mcp`
- Client path tested: `mcp-remote@latest` using Streamable HTTP
- MCP connection status: connected
- Tool discovery: passed
- Tool count: 10
- Sample tools:
  - `splunk_get_info`
  - `splunk_get_indexes`
  - `splunk_get_index_info`
  - `splunk_get_user_list`
  - `splunk_get_user_info`
  - `splunk_run_query`
  - `splunk_get_metadata`
  - `splunk_get_kv_store_collections`
  - `splunk_get_knowledge_objects`
  - `splunk_run_saved_search`

## Synthetic Query Proof

Tool used: `splunk_run_query`

Query:

```spl
search index=agentops_events incident_id="inc-checkout-20260603-0900" | sort _time | table _time event_id service event_type risk_score evidence_ref | head 5
```

Returned rows: 5

Observed synthetic evidence:

| event_id | service | event_type | risk_score | evidence_ref |
| --- | --- | --- | --- | --- |
| `evt-0001` | `checkout-api` | `deploy_completed` | `45` | `splunk://agentops_events/inc-checkout-20260603-0900/0001` |
| `evt-0002` | `checkout-api` | `error_rate_spike` | `100` | `splunk://agentops_events/inc-checkout-20260603-0900/0002` |
| `evt-0003` | `checkout-api` | `latency_regression` | `80` | `splunk://agentops_events/inc-checkout-20260603-0900/0003` |
| `evt-0004` | `payments-db` | `connection_pool_pressure` | `70` | `splunk://agentops_events/inc-checkout-20260603-0900/0004` |
| `evt-0005` | `auth-gateway` | `auth_failure_burst` | `45` | `splunk://agentops_events/inc-checkout-20260603-0900/0005` |

## Claim Boundary

Supported claim:

> Official Splunk MCP Server was installed and verified in a reproducible local Splunk Enterprise Docker proof environment against synthetic incident data.

Do not claim:

> Production Splunk Cloud deployment verified.

Production Splunk Cloud deployment is not claimed.

Do not show:

- MCP encrypted token values
- Splunk password or login screens
- Account, billing, personal, or private workspace pages
- Non-synthetic data

## Notes

- The local endpoint used a self-signed Splunk certificate. TLS verification was relaxed only for this ephemeral local proof client path.
- This evidence upgrades the previous state from `official_splunk_mcp_server_verified=false` to a local official-MCP proof, bounded to the Docker Splunk Enterprise environment.
