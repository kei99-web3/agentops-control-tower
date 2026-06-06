# Devpost Field Map

Status: local draft, not submitted
Last updated: 2026-06-06 JST

Use this as the copy/paste map for the Devpost submission form after the public repository and public video gates are approved.

## Core Fields

| Devpost field | Value |
| --- | --- |
| Project name | Agentic Incident Command Center |
| Tagline | Splunk-grounded AI incident commander with human-approved remediation. |
| Track | Platform & Developer Experience |
| Bonus target | Best Use of Splunk MCP Server |
| Built with | Python, Splunk, SPL, JSON, CSV, HTML |
| Conditional MCP tag | Add Splunk MCP Server only after approved live Splunk/MCP proof capture and claim validation. |
| Repository URL | PENDING_USER_APPROVAL_PUBLIC_REPO_URL |
| Demo video URL | PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL |

## Short Description

Agentic Incident Command Center turns deploy, observability, security, network, and MCP/tool-call signals into Splunk-ready incident evidence. It ranks root-cause candidates, maps blast radius, and keeps high-impact remediation actions human-approved.

## Suggested Devpost Sections

| Devpost section | Local source |
| --- | --- |
| Inspiration | `submission/DEVPOST_SUBMISSION_DRAFT.md#inspiration` |
| What it does | `submission/DEVPOST_SUBMISSION_DRAFT.md#what-it-does` |
| How we built it | `submission/DEVPOST_SUBMISSION_DRAFT.md#how-we-built-it` |
| Challenges | `submission/DEVPOST_SUBMISSION_DRAFT.md#challenges` |
| Accomplishments | `submission/DEVPOST_SUBMISSION_DRAFT.md#accomplishments` |
| What is next | `submission/DEVPOST_SUBMISSION_DRAFT.md#what-is-next` |

## Required Attachments / Links

| Requirement | Local evidence | External status |
| --- | --- | --- |
| Public open-source repo | `public_repo_candidate/agentops-control-tower` | PENDING_USER_APPROVAL |
| Open-source license | `LICENSE` | Ready locally |
| Architecture diagram | `architecture_diagram.md` | Ready locally |
| Demo video under 3 minutes | `reports/latest_demo_tour.html`, `submission/DEMO_VIDEO_SCRIPT.md`, `submission/VIDEO_RECORDING_RUNBOOK.md` | PENDING_USER_APPROVAL |
| Working project for judging | `README.md`, `prototype/`, `data/`, `reports/` | Public repo pending |

## Claim Boundaries

- Safe to claim: synthetic incident data demo, local dashboard, local SPL-equivalent proof, public repo candidate, recording-ready demo tour, and Splunk MCP design.
- Do not claim yet: live Splunk MCP verification, public repo publication, public video upload, approved URL writeback, or Devpost submission.
- Keep `Splunk MCP Server` out of the Built with/tag field until approved live proof exists; use the bonus target and narrative copy for the designed-for MCP story.
- Use the phrase "designed for Splunk MCP Server" until live MCP setup is approved and verified.
- Use the phrase "verified through Splunk MCP Server" only after approved live setup and recording.

## Final Copy Gate

Before submitting:

1. Replace `PENDING_USER_APPROVAL_PUBLIC_REPO_URL`.
2. Replace `PENDING_USER_APPROVAL_PUBLIC_VIDEO_URL`.
3. Re-run `python scripts\validate_submission_packet.py`.
4. Confirm `reports/latest_submission_validation.html` says `ready_for_user_review`.
5. Review `reports/latest_devpost_manual_fill_brief.html` against the visible Devpost form.
6. Get explicit final submit approval.
