# Release Integrity Manifest

Status: ready_for_user_review
Root type: public_candidate
Validation status: ready_for_user_review
Validation failed count: 0
Validation source: reports/latest_final_go_no_go.json
Artifact count: 73
Final submit ready: false

## Release ZIP

- Path: `release/agentops-control-tower-public-candidate.zip`
- Exists: True
- File count: 253
- Size bytes: 795464
- SHA256: `5418ee50e8daeb9f1ccf2d0147bd5eec9d7acd016799a52ae4183b0222682f81`
- Smoke status: not_applicable_public_candidate_root

## Checks

- required artifacts present: pass (all required artifacts present)
- Splunk app package SHA256 consistency: pass (manifest=360a8057c192a84a6d3a63b8da946a74fdfd43bf10bf8b84646629b1a9ca357f artifact=360a8057c192a84a6d3a63b8da946a74fdfd43bf10bf8b84646629b1a9ca357f)
- Splunk app package manifest status: pass (ready_for_user_review)
- Splunk MCP prompt pack status: pass (status=ready_for_user_review live=True external=False)
- live Splunk Docker and official MCP proof captured with bounded claim: pass (status=live_splunk_verified_official_mcp_verified live=True adapter=True official=True failed_queries=0)
- claim boundary status: pass (not_applicable_public_candidate_root)
- release ZIP smoke status: pass (not_applicable_public_candidate_root)
- candidate-local ZIP count consistency: pass (manifest=253 actual=253)
- final submit remains gated: pass (False)
- approved URLs remain gated: pass (False)
- post-action external gates tracked: pass (public_github_repository, public_demo_video, approved_url_writeback, devpost_final_submission)
- publication boundary text: pass (This release integrity manifest is local readback evidence only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.)
- video dry run status: pass (not_applicable_public_candidate_root)
- public video upload preflight status: pass (not_applicable_public_candidate_root)
- URL writeback dry run status: pass (not_applicable_public_candidate_root)

## Artifact Integrity

- `PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present, required) - size=11663 sha256=`39410cd90dc860ad013bd79da19f17f917617b33081008df71dfca1276da93d6` - Confirms this folder is the clean local public-candidate root.
- `release/agentops-control-tower-public-candidate.zip` (present, optional) - size=795464 sha256=`5418ee50e8daeb9f1ccf2d0147bd5eec9d7acd016799a52ae4183b0222682f81` - Optional local ZIP generated inside the public candidate for review.
- `reports/latest_public_candidate_zip_manifest.json` (present, optional) - size=12976 sha256=`b626dd42c6be89bed4fa6336e1f8e449936f90541f04ecf2fd0727d5649666fc` - Optional machine-readable candidate ZIP manifest.
- `README.md` (present, required) - size=23457 sha256=`ead36dee9b5a820b70875ece7b483caefd658ba510a3ebe3d7fb599cba90d3f7` - Portable project overview and local run instructions.
- `LICENSE` (present, required) - size=11358 sha256=`c95bae1d1ce0235ecccd3560b772ec1efb97f348a79f0fbe0a634f0c2ccefe2c` - Open-source license candidate for public review.
- `architecture_diagram.md` (present, required) - size=1912 sha256=`b3b0f36a0d1e0a3bdd8d45c926e0d5fb6fff5ca9791c95d8fd90a6d9a3fd454b` - Root architecture evidence required by the submission packet.
- `assets/dashboard_preview.png` (present, required) - size=75210 sha256=`a172e0fa0fcaa2b4bb0a96b7b02c5bd326b37dbf26d5c4130010f54579df6142` - Visual README/Devpost preview asset.
- `prototype/agentops_control_tower.py` (present, required) - size=36533 sha256=`fce2f1c75eb25f4dfab60c57bfbbcbc9b0e126840b5672d9bfecbf070f5b871b` - Generator for synthetic checkout-incident events, analysis, dashboard, and SPL examples.
- `data/splunk_agentops_events.csv` (present, required) - size=8368 sha256=`3bb781d0e8859b52b5dd6676b35b8d051b9d2c355cec05bcb5ae2f85b5aa5a6e` - Synthetic data export for a future agentops_events index after approval.
- `submission/SPL_QUERIES.md` (present, required) - size=1783 sha256=`feb15f47a2498d4f54a2cc0ae0e41767c0c6100ebdcb6dcc2f4989651920e02a` - Reviewer-facing SPL examples for the Control Tower flow.
- `splunk_app/agentops_control_tower/default/indexes.conf` (present, required) - size=212 sha256=`4e966767e2b53e1c45102702824549f04d785e32052d0692c0f1f3410c2e9ffd` - Optional local index definition for agentops_events.
- `splunk_app/agentops_control_tower/default/props.conf` (present, required) - size=217 sha256=`6c6e3704dbd785b9fc52526b3c5fe429ac5648982d5347fce226d087fc6b024d` - CSV extraction and timestamp parsing for the agentops:events sourcetype.
- `dist/agentops-control-tower-splunk-app.spl` (present, required) - size=2409 sha256=`360a8057c192a84a6d3a63b8da946a74fdfd43bf10bf8b84646629b1a9ca357f` - Local .spl package candidate; not installed or uploaded.
- `reports/latest_splunk_app_package_manifest.html` (present, required) - size=3767 sha256=`e77ef086ca7079c757452a1518eef313f4f76de56e1c017e23edaa6cb1fc85c3` - Members, SHA256, and package boundary evidence.
- `reports/latest_splunk_app_package_manifest.json` (present, required) - size=2255 sha256=`48117267011f708ca1d32ff5d9ea6df8f177ae558efb8a5eee798543205d986c` - Machine-readable .spl integrity evidence.
- `reports/latest_splunk_mcp_command_plan.html` (present, required) - size=7990 sha256=`5b7a5ab9a96b76ec531a24fe7658c54b1237b11529dd184acb502fbc70825d17` - Post-approval live Splunk/MCP setup and proof command plan.
- `reports/latest_splunk_mcp_proof_brief.html` (present, required) - size=9389 sha256=`0c3eba6257d8df6f8c583d015810641195866b2b33b81ebab82981f40e72fe60` - Success criteria, screen safety, stop conditions, and claim-upgrade rules for optional live proof.
- `reports/latest_splunk_mcp_prompt_pack.html` (present, required) - size=8562 sha256=`0d5e125c91a8fdc41a376dd60065cf077bf14b84a3c4ee3c1c393e34d4165273` - Prompt-by-prompt live proof guide for evidence-backed MCP answers.
- `reports/latest_splunk_mcp_prompt_pack.json` (present, required) - size=8628 sha256=`0799252ab690dafafc29128c45b032130c216df877f3865ed11317a5a3485bce` - Machine-readable prompt keys, SPL, expected citations, and live-proof gates.
- `reports/latest_splunk_mcp_prompt_pack.md` (present, required) - size=6691 sha256=`515b112f9400503b67397d84684a306bcd1f6d784af45e0b1935517526308f43` - Reviewable prompt pack for approved live proof capture.
- `submission/SPLUNK_MCP_PROMPT_PACK.md` (present, required) - size=6691 sha256=`515b112f9400503b67397d84684a306bcd1f6d784af45e0b1935517526308f43` - Submission-side copy of the prompt pack and stop conditions.
- `reports/latest_claim_evidence_matrix.html` (present, required) - size=11006 sha256=`2f03b115b3d85f307c65e8788f20261033ade4b3254561317ca18f867f082c80` - Allowed wording, avoid wording, evidence, and remaining gates.
- `reports/latest_claim_evidence_matrix.json` (present, required) - size=11992 sha256=`68e244823680bf25c547ea0795e5c5d7ace420351df9d8cd6e2c0b846977157a` - Machine-readable claim support status.
- `reports/latest_submission_gate_ledger.html` (present, required) - size=9098 sha256=`5c66c8a7090f481f8c28b80820c0878de0b8865fcd07ee536ac0f5679b7514de` - Approval-gate ledger for public repo, video, live proof, and Devpost.
- `reports/latest_submission_deadline_burndown.html` (present, required) - size=10535 sha256=`30ca0adc49209e7b0acdcc8e56df328fc67c5ad29a5477b1bed932ee0df84f50` - Deadline-aware path for public repo, video, optional live proof, URL writeback, and Devpost final submit.
- `reports/latest_submission_deadline_burndown.json` (present, required) - size=7493 sha256=`a3398d7bc4a73193f12ffb6b0c9a205e4f54e53d48f01cfbe8812e96603366f7` - Machine-readable target date, official deadline, milestones, and blocked final submit gate.
- `reports/latest_submission_deadline_burndown.md` (present, required) - size=5137 sha256=`0085ee60a16fd4f451b2b1ffa9529130a69bf0e4b3249555dc35a32a4df9074e` - Reviewable deadline burndown for local launch planning.
- `submission/SUBMISSION_DEADLINE_BURNDOWN.md` (present, required) - size=5137 sha256=`0085ee60a16fd4f451b2b1ffa9529130a69bf0e4b3249555dc35a32a4df9074e` - Submission-side copy of the deadline burndown and approval timing path.
- `reports/latest_next_approval_packet.html` (present, required) - size=15234 sha256=`48022ab37a396c7a525507fa78a6c5c48f0d047803b6ce76245506c06128db6d` - Next user approval target, approval phrases, risks, and verification steps.
- `reports/latest_next_approval_packet.json` (present, required) - size=13303 sha256=`4b8cfbe55f18a3de386178a6ae92e7e67dd83cdfecc137be461c41707fc875d5` - Machine-readable next approval status and human-confirmation gates.
- `submission/NEXT_APPROVAL_PACKET.md` (present, required) - size=9685 sha256=`41adf400a019fd558ec01546a4a3e5d2b349fa988d1db0febd4315df837fd64a` - Markdown copy of the next approval packet for final user decision support.
- `reports/latest_approval_consistency_audit.html` (present, required) - size=6332 sha256=`4211f66af6c9d146d3f6bc5af703c283d760456d7e00d408374ec877cb6cb432` - Checks approval order consistency across plan, approval gates, launch brief, next packet, and validator state.
- `reports/latest_approval_consistency_audit.json` (present, required) - size=5538 sha256=`6e61487dd3c3fd1b976ba7c9b9115c33361d0f91287dc6d11462fdf12a007112` - Machine-readable approval-order consistency status.
- `reports/latest_status_conflict_audit.html` (present, optional) - size=7550 sha256=`c8599a372f1ff3d43c38f3f9a4cee9ca655907407791d0a12940e6217ef7a023` - Scans root and public-candidate JSON reports for stale failed statuses or missing local artifacts.
- `reports/latest_status_conflict_audit.json` (present, optional) - size=6338 sha256=`25c8ea73b081140fcdf48473ea4932b144d16119b9e61fe1e0bc8a3f681c92ff` - Machine-readable status conflict scan and critical ready-state checks.
- `reports/latest_status_conflict_audit.md` (present, optional) - size=4020 sha256=`d3b68e6389f61d670d5836e49fefffbcf7e1b6c837a577ef643f68298a22f2dd` - Reviewable status conflict audit summary.
- `reports/latest_public_launch_snapshot.html` (present, required) - size=8441 sha256=`47cd351a13b5f23b39d07fa3d32b591dca943c090c88475d511a62332dece3a8` - Frozen local snapshot for public repo and demo video approval review.
- `reports/latest_public_launch_snapshot.json` (present, required) - size=8644 sha256=`2be9fe96bb66f22f4186512f408e052f954cfcdbeb90b4971ec4723290b800a8` - Machine-readable public launch readiness, ZIP hash, approval phrases, and remaining gates.
- `reports/latest_public_launch_snapshot.md` (present, required) - size=4283 sha256=`e53e48cb2bd9744c05a12bd360205d7b01c18e8b24770b8e6c8635d7f873aaa3` - Reviewable public launch snapshot for copy/paste and audit.
- `reports/latest_public_repo_metadata.html` (present, required) - size=6104 sha256=`21c346bc21b00914423a19d99556fef951d1571a1ef3b3b907530d981947b93f` - GitHub repository name, description, topics, expected readback, and no-publish boundary.
- `reports/latest_public_repo_metadata.json` (present, required) - size=3844 sha256=`85578f758400e360f6446b159c875d2aadaa477fa2fbf8fdd137a0eaa11c19bf` - Machine-readable public repository metadata and post-approval readback expectations.
- `reports/latest_public_repo_metadata.md` (present, required) - size=2920 sha256=`b5a935204c7a3e8f3bf6b0c4fc8f52a9a9cb21a5568726ff270283b2949bc0c4` - Reviewable public repository metadata packet.
- `submission/PUBLIC_REPO_METADATA.md` (present, required) - size=2920 sha256=`b5a935204c7a3e8f3bf6b0c4fc8f52a9a9cb21a5568726ff270283b2949bc0c4` - Submission-side copy of public repository metadata and stop conditions.
- `submission/USER_APPROVAL_GATES.md` (present, required) - size=1637 sha256=`38bbcc3aac49b272690152682046ebe590121d842b3c91f60dfe7eaba41524f6` - Human approval boundaries and current recommended approval order.
- `READY_FOR_REVIEW.md` (present, required) - size=977 sha256=`35cf68ec7e79e0316247c98a81ccc27de542657d95e4349fc4282028c5c34601` - Shortest local review entrypoint for the current SPAK packet.
- `reports/latest_judge_review_packet.html` (present, required) - size=4627 sha256=`d1fe56a47a38f14879c28764c08659e996b8f198e55eed83a2fb05aa955bbe64` - Judge-facing local packet with readiness, evidence, and closed external gates.
- `reports/latest_judge_review_packet.json` (present, required) - size=3639 sha256=`27187538bfb6d41138508e79b1ad350e4ceabc1adb9ca80d2762ce274d42ed6d` - Machine-readable SPAK judge packet status.
- `reports/latest_judge_review_packet.md` (present, required) - size=2427 sha256=`59ee66e033193aa5af471cea97357ffda787e3be60afaa1ae4740072e4f182e0` - Reviewable SPAK judge packet summary.
- `submission/JUDGE_REVIEW_PACKET.md` (present, required) - size=2427 sha256=`59ee66e033193aa5af471cea97357ffda787e3be60afaa1ae4740072e4f182e0` - Submission-side copy of the local judge review packet.
- `reports/latest_local_readiness_baseline.html` (present, required) - size=3843 sha256=`5720ee77556d4c97d3818b7beca09f5468132c68d19b497e3a78b0f46caa27d6` - Targeted pass/fail baseline for local package/proof readiness.
- `reports/latest_local_readiness_baseline.json` (present, required) - size=2985 sha256=`8752d05f99178b3cd9f89e1c0bf8516ed0529a1cb18e2877d725e7585b9d451b` - Machine-readable targeted local readiness baseline.
- `reports/latest_local_readiness_baseline.md` (present, required) - size=1515 sha256=`46f0575426b4994e0f1e2355a1e86b169a26c6acb5d6f6ca73318b52e96ea566` - Reviewable targeted local readiness baseline.
- `reports/latest_public_candidate_local_audit.html` (present, required) - size=3431 sha256=`043630c700a3367591f65e0253a244a7359d178ab16c5e47f23dc8c97715c61a` - Secret/internal-path and completeness audit for the public repo candidate.
- `reports/latest_public_candidate_local_audit.json` (present, required) - size=2011 sha256=`ccfca6afef49a921bdec5c5b186608bd1f5c475e0026aa12c17d377d85007e56` - Machine-readable public candidate safety audit.
- `reports/latest_public_candidate_local_audit.md` (present, required) - size=1160 sha256=`1cb477a8bc96af1a53b2b21ab105570c637aafe8a5a6548b484829aa625b57e6` - Reviewable public candidate safety audit.
- `reports/latest_devpost_copy_audit.html` (present, required) - size=3396 sha256=`16099c9c08c00d0d686341d5c8cee29cdcb817b5fd22e4b3424bdb03eba25d40` - Local audit of Devpost copy readiness with final submission still gated.
- `reports/latest_devpost_copy_audit.json` (present, required) - size=2073 sha256=`43fe1bbff24d9c06c5cce5c19c09ac04d9b22ace65e715166872ab26be6bfe8e` - Machine-readable Devpost copy audit.
- `reports/latest_devpost_copy_audit.md` (present, required) - size=1135 sha256=`eddb2cf442b38f13a07d9bd0ce71d9271ca2f56e44355ae389b09bece2863c3b` - Reviewable Devpost copy audit.
- `reports/latest_judge_quickstart.html` (present, required) - size=9768 sha256=`c48de3972790049e34a092e2a0dceada3428edd6e68387baf1a4fb612fe943c4` - Five-minute review path for judges and final preflight.
- `reports/latest_devpost_final_copy.md` (present, required) - size=9121 sha256=`ee53060b0dde21ffebc28ac773d3fe5512da90ec417a07aa240fee1c9a9cd334` - Copy/paste packet with pending public URL placeholders.
- `reports/latest_post_action_evidence_brief.html` (present, required) - size=10298 sha256=`c6defd3b8657ce97ce79a9718f469590753792d456757b83712bc2c6418ed25a` - Readback plan after approved external actions.
- `reports/latest_post_action_evidence_brief.json` (present, required) - size=9018 sha256=`d372696f34cdd214be2eae8aaf1dc314a7936b275706926d28f3cdde4cd93390` - Machine-readable post-action gate state.
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` (present, required) - size=7393 sha256=`f35de1a10121305df6bc05c184d5855101beaeb186f62a2ceb48bf8e103a248c` - Template for safe readback after approved external actions.
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present, required) - size=9935 sha256=`a4574eb4f21302104d61235c741b7b95438fdbe042e8313c4586619602513764` - Live Splunk/MCP proof capture slots, expected readback, stop conditions, and claim-upgrade gate.
- `reports/latest_splunk_mcp_proof_capture_manifest.json` (present, required) - size=8272 sha256=`0552a1305727500e30cd6ecabf863e4a879c55cd1cc14b2bbb0d587250a3ac55` - Machine-readable live Splunk/MCP proof capture gate state.
- `reports/latest_splunk_mcp_proof_capture_manifest.md` (present, required) - size=6360 sha256=`24a67683578d57a122efe481b67d90e8c151093ba5533f7e0cbbb73d423a1b0f` - Reviewable live Splunk/MCP proof capture manifest.
- `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md` (present, required) - size=6360 sha256=`24a67683578d57a122efe481b67d90e8c151093ba5533f7e0cbbb73d423a1b0f` - Submission-side copy of the proof capture manifest and no-live-proof boundary.
- `reports/latest_official_source_freshness.html` (present, required) - size=6399 sha256=`c8b9c27dac1a204aa0a7c58fcd8be5b26ffc60c28d13dbc526c4a6404885b894` - Current official Devpost source and requirement freshness evidence.
- `reports/latest_official_source_freshness.json` (present, required) - size=7726 sha256=`d5a704134bd5e149212863198f41f943f76c79b7ca65c9801bb62397cb0865a6` - Machine-readable official source freshness and local mapping status.
- `reports/latest_content_rights_audit.html` (present, required) - size=4886 sha256=`9d23cbe82972acd73d2f7788b72c3254f3692b95cd98f534504b15a032aaa001` - License, bundled asset, audio/video, and screen-safety evidence.
- `reports/latest_content_rights_audit.json` (present, required) - size=3632 sha256=`43eae64f9ee81f1a41f588300ba6717528fefbcaa5020d69f62f8d4ca7fadc21` - Machine-readable content rights and asset safety status.
- `reports/latest_eligibility_compliance_audit.html` (present, required) - size=7810 sha256=`fd0302542ef8e148d3edf5e4fded7804741c9689b931eda7c1f338289cc5d1ea` - Eligibility, ownership, language, uniqueness, and human-confirmation evidence.
- `reports/latest_eligibility_compliance_audit.json` (present, required) - size=6314 sha256=`b0dac56db0d64f42664c6abc5857b730f046446d533d075589d4762f20003f7f` - Machine-readable eligibility and compliance status.

## Publication Boundary

This release integrity manifest is local readback evidence only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.
