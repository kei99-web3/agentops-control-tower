# Status Conflict Audit

Status: ready_for_user_review
Root type: public_candidate
JSON files scanned: 49
Conflict count: 0
Critical check failed count: 0
Failed count: 0

## Scan Scopes

- public_candidate: 49 JSON reports

## Conflicts

- none

## Critical Checks

- public_candidate full validator status: pass (validator report not yet bundled; final Go/No-Go snapshot is ready; expected ready validator report or ready final Go/No-Go snapshot)
- public_candidate full validator failed count: pass (validator report not yet bundled; final Go/No-Go snapshot is ready; expected ready validator report or ready final Go/No-Go snapshot)
- public_candidate final submit stays gated: pass (validator report not yet bundled; final Go/No-Go snapshot is ready; expected ready validator report or ready final Go/No-Go snapshot)
- public_candidate final Go/No-Go status: pass (reports/latest_final_go_no_go.json:status='ready_for_user_review'; expected 'ready_for_user_review')
- public_candidate final Go/No-Go final submit gate: pass (reports/latest_final_go_no_go.json:final_submit_ready=False; expected False)
- public_candidate release integrity status: pass (reports/latest_release_integrity_manifest.json:status='ready_for_user_review'; expected 'ready_for_user_review')
- public_candidate release validation snapshot: pass (reports/latest_release_integrity_manifest.json:validation_status='ready_for_user_review'; expected 'ready_for_user_review')
- public_candidate release validation failed count: pass (reports/latest_release_integrity_manifest.json:validation_failed_count=0; expected 0)
- public_candidate release integrity failed count: pass (reports/latest_release_integrity_manifest.json:failed_count=0; expected 0)
- public_candidate release integrity missing artifacts: pass (reports/latest_release_integrity_manifest.json:missing_artifacts=[]; expected [])
- public_candidate approval consistency status: pass (reports/latest_approval_consistency_audit.json:status='ready_for_user_review'; expected 'ready_for_user_review')
- public_candidate approval consistency failed count: pass (reports/latest_approval_consistency_audit.json:failed_count=0; expected 0)
- public_candidate public launch snapshot status: pass (reports/latest_public_launch_snapshot.json:status='ready_for_user_review'; expected 'ready_for_user_review')
- public_candidate public launch snapshot failed count: pass (reports/latest_public_launch_snapshot.json:failed_count=0; expected 0)
- public_candidate next packet local status: pass (reports/latest_next_approval_packet.json:local_submission_status='ready_for_user_review'; expected 'ready_for_user_review')
- public_candidate next packet local failed count: pass (reports/latest_next_approval_packet.json:local_submission_failed_count=0; expected 0)
- public_candidate review index status: pass (reports/latest_submission_review_index.json:status='ready_for_user_review'; expected 'ready_for_user_review')
- public_candidate review index local status: pass (reports/latest_submission_review_index.json:local_submission_status='not_bundled_public_candidate_root'; expected ready_for_user_review or not_bundled_public_candidate_root)
- public_candidate review index validation failed count: pass (reports/latest_submission_review_index.json:validation_failed_count='not_applicable_public_candidate_root'; expected 0 or not_applicable_public_candidate_root)
- public_candidate review index release integrity status: pass (reports/latest_submission_review_index.json:release_integrity_status='ready_for_user_review'; expected 'ready_for_user_review')
- public_candidate review index approval consistency status: pass (reports/latest_submission_review_index.json:approval_consistency_status='ready_for_user_review'; expected 'ready_for_user_review')

## Boundary

This status conflict audit is local readback evidence only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.
