# Splunk Agentic Ops Hackathon Requirement Matrix

Last checked: 2026-06-06 JST

Official sources checked:

- https://splunk.devpost.com/
- https://splunk.devpost.com/rules
- https://splunk.devpost.com/updates/43765-the-challenge-is-live-and-so-are-the-prizes

## Official Submission Requirements

| Requirement | Local status | Evidence | Approval needed |
| --- | --- | --- | --- |
| Build an AI-powered solution for Observability, Security, or Platform & Developer Experience | In progress | Agentic Incident Command Center concept and local demo script | No |
| Use Splunk AI capabilities / Splunk MCP Server story | Local proof plus live setup pending | Architecture maps Splunk index to Splunk MCP Server to AI incident commander; local SPL-equivalent results and Splunk app candidate exist | Splunk account/license and MCP setup |
| Text description explaining features and functionality | Drafted and packetized | README, Devpost draft, field map, and Devpost submission packet exist | No |
| Demo video under 3 minutes, publicly posted | Recording path prepared | Demo tour, demo script, and recording runbook exist | Yes: public upload |
| Public code repository | Local private candidate only | `public_repo_candidate/agentops-control-tower` is generated and validated | Yes: public repo |
| Open source license visible | Local candidate ready | Apache-2.0 LICENSE added | Yes: public repo |
| Clear README, setup/run instructions, dependencies | Ready for local candidate | README includes local run instructions and standard-library-only test flow | No |
| Architecture diagram at root named architecture_diagram.(md\|pdf\|png) | Ready as Markdown candidate | `architecture_diagram.md` | No |
| Project available free for judging through judging period | Not ready | Local-only for now | Yes: public repo and public demo access |
| English submission materials | Drafted | README, Devpost draft, demo script, runbook, and public readiness checklist | No |
| Judging criteria alignment | Ready | `submission/JUDGING_ALIGNMENT.md` maps the project to Stage One and the four Stage Two criteria | No |
| Official requirement audit | Ready | `submission/OFFICIAL_REQUIREMENTS_AUDIT.md` | No |

## Target Prize Fit

| Prize / track | Fit | Why |
| --- | --- | --- |
| Platform & Developer Experience | Strong | Gives platform/SRE teams a repeatable AI incident command workflow with evidence, blast radius, and approval gates. |
| Best Use of Splunk MCP Server | Strong if Splunk MCP is configured | The core story is AI assistant access to Splunk operational context through MCP, with event citations and human-approved remediation. |
| Observability | Strong | The main scenario correlates deployment, application, APM, database, and network telemetry. |
| Security | Medium to strong | Security and MCP boundary signals are included as supporting incident evidence and guardrails without turning the project into exploit hunting. |

## Current Risk

- Splunk account/license is not configured yet.
- Splunk MCP Server integration is architecture-level until user approval enables setup.
- Public repo and public video are hard submission gates.
- The demo must avoid private workspace data; current implementation uses synthetic data only.
