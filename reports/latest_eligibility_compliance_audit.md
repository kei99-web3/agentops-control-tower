# Eligibility And Compliance Audit

Status: ready_for_user_review
Root type: public_candidate
Source checked at: 2026-06-04 JST
Human confirmation checklist: `submission/HUMAN_CONFIRMATION_CHECKLIST.md`

## Official Sources

- [Devpost official rules](https://splunk.devpost.com/rules) - Eligibility, project ownership, team representative, language, IP, testing, and submission rules.
- [Devpost overview](https://splunk.devpost.com/) - Challenge scope, deadline, tracks, and public submission entrypoint.

## Automated Evidence

- new_or_significantly_updated_project: pass - Local audit states the project was created locally on 2026-06-03 JST during the submission period. Evidence: `submission/OFFICIAL_REQUIREMENTS_AUDIT.md`
- public_materials_in_english: pass - No Japanese characters found in key public submission materials. Evidence: `README.md, architecture_diagram.md, submission/DEVPOST_SUBMISSION_DRAFT.md, submission/DEVPOST_FIELD_MAP.md, submission/DEMO_VIDEO_SCRIPT.md, submission/VIDEO_RECORDING_RUNBOOK.md, submission/SUBMISSION_REVIEW_QA.md, submission/SUBMISSION_LAUNCH_RUNBOOK.md, submission/JUDGING_ALIGNMENT.md, submission/OFFICIAL_REQUIREMENTS_AUDIT.md`
- open_source_license_present: pass - Apache-2.0 license is present and included in the content rights audit. Evidence: `LICENSE, reports/latest_content_rights_audit.html`
- third_party_media_not_bundled: pass - No bundled audio/video media files are present in the local package. Evidence: `reports/latest_content_rights_audit.html`
- synthetic_data_boundary: pass - The package describes demo data as synthetic and avoids private logs/customer data. Evidence: `README.md, submission/OFFICIAL_REQUIREMENTS_AUDIT.md`
- unique_project_narrative: pass - The Devpost draft frames a distinct AI incident command and remediation-ledger story. Evidence: `submission/DEVPOST_SUBMISSION_DRAFT.md`
- testing_access_gated_by_public_urls: pass - Final submission remains blocked until public repo and public video URLs are approved and validated. Evidence: `reports/latest_submission_url_validation.html`

## Human Confirmation Required

### age_and_residence

Rule area: Eligibility
Confirm: Entrant is at least the age of majority where they reside and is not resident/domiciled in an excluded jurisdiction.
Why Codex cannot confirm: This depends on personal/legal facts and should be confirmed by the user before Devpost submission.

### no_excluded_role_or_conflict

Rule area: Eligibility and conflict of interest
Confirm: Entrant is not a judge, promotion entity, government/state-owned entity, excluded affiliate, household member, or otherwise conflicted participant.
Why Codex cannot confirm: This depends on employment, affiliation, household, and conflict facts outside the local packet.

### team_or_representative_authority

Rule area: Team representation
Confirm: If submitted as a team or organization, the submitter is authorized to act as the representative and the team size is within the rules.
Why Codex cannot confirm: The local packet does not know whether the Devpost entry will be individual, team, or organization.

### ownership_and_ip

Rule area: Submission ownership and IP
Confirm: The entrant owns the submitted work or has permission for every included component, and no third-party rights are violated.
Why Codex cannot confirm: The package can audit files and licenses, but final ownership representation belongs to the entrant.

### no_sponsor_support_conflict

Rule area: Financial or preferential support
Confirm: The project was not developed with prohibited financial or preferential support from Sponsor or Administrator.
Why Codex cannot confirm: This depends on external business, employment, funding, and contract facts.

## Checks

- official rules source linked: pass (submission/OFFICIAL_REQUIREMENTS_AUDIT.md)
- automated compliance evidence ready: pass (all automated evidence ready)
- human confirmations enumerated: pass (age_and_residence, no_excluded_role_or_conflict, team_or_representative_authority, ownership_and_ip, no_sponsor_support_conflict)
- external submit remains gated: pass (user approval and not-submitted wording checked)
- boundary text: pass (This eligibility and compliance audit is local review evidence only. It does not determine legal eligibility, submit Devpost forms, create accounts, publish a repository, upload video, write approved URLs, configure Splunk, or submit anything.)

## Boundary

This eligibility and compliance audit is local review evidence only. It does not determine legal eligibility, submit Devpost forms, create accounts, publish a repository, upload video, write approved URLs, configure Splunk, or submit anything.
