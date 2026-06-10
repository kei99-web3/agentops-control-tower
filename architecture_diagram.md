# Architecture Diagram

```mermaid
flowchart LR
    A["Deploy and change events"] --> B["Incident command event schema"]
    C["Application, APM, database, and network telemetry"] --> B
    D["Security signals<br/>auth anomaly, WAF probe"] --> B
    E["MCP/tool-call audit events"] --> B
    F["Human approval records"] --> B
    B --> G["Splunk index<br/>agentops_events"]
    G --> H["SPL incident queries"]
    G --> I["Splunk MCP Server<br/>approved query tools"]
    H --> J["AI incident commander"]
    I --> J
    J --> K["Root-cause ranking<br/>evidence, confidence, citations"]
    J --> L["Blast radius by service"]
    J --> M["MCP Remediation Ledger<br/>policy, approval, runbook action"]
    K --> N["Human incident commander"]
    L --> N
    M --> N
    N --> O["Approve rollback, WAF watch, update, ticket<br/>or hold action"]
```

## Data Flow

1. Synthetic incident sources emit structured events for a checkout outage.
2. Events are indexed into Splunk as operational data.
3. SPL queries and Splunk MCP Server provide approved evidence access.
4. The AI incident commander ranks root causes and recommends next actions with citations.
5. Human reviewers approve, reject, or hold remediation. Risky actions never bypass approval.

## Safety Principle

The agent does not execute high-impact remediation on its own. It makes the human decision faster and more reliable by packaging evidence.

```mermaid
stateDiagram-v2
    [*] --> Observed
    Observed --> Correlated: cross-domain Splunk evidence
    Correlated --> Ranked: root-cause candidates
    Ranked --> NeedsApproval: rollback, WAF watch, stakeholder update
    Ranked --> Blocked: credential boundary or unsafe tool call
    NeedsApproval --> ApprovedExecutable: explicit human approval
    NeedsApproval --> Held: no valid approval
    Blocked --> AuditOnly
    ApprovedExecutable --> [*]
    Held --> [*]
    AuditOnly --> [*]
```
