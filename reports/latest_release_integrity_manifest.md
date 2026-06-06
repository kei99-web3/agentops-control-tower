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
- File count: 248
- Size bytes: 773263
- SHA256: `b0fe4414c923c47260213bae03dd9fb38ad3de91296b97fe7682b8ba6bbe652a`
- Smoke status: not_applicable_public_candidate_root

## Checks

- required artifacts present: pass (all required artifacts present)
- Splunk app package SHA256 consistency: pass (manifest=061d79ceec155e7b9681bc5fcf671aa5685680f1ed274d404a0947817998e23e artifact=061d79ceec155e7b9681bc5fcf671aa5685680f1ed274d404a0947817998e23e)
- Splunk app package manifest status: pass (ready_for_user_review)
- Splunk MCP prompt pack status: pass (status=ready_for_user_review live=False external=False)
- claim boundary status: pass (not_applicable_public_candidate_root)
- release ZIP smoke status: pass (not_applicable_public_candidate_root)
- candidate-local ZIP count consistency: pass (manifest=248 actual=248)
- final submit remains gated: pass (False)
- approved URLs remain gated: pass (False)
- post-action external gates tracked: pass (public_github_repository, public_demo_video, optional_live_splunk_mcp_proof, approved_url_writeback, devpost_final_submission)
- publication boundary text: pass (This release integrity manifest is local readback evidence only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.)
- video dry run status: pass (not_applicable_public_candidate_root)
- public video upload preflight status: pass (not_applicable_public_candidate_root)
- URL writeback dry run status: pass (not_applicable_public_candidate_root)

## Artifact Integrity

- `PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present, required) - size=11379 sha256=`d4565fdea014528ae731984c653d582e6cd674007b06ae4816978332afa41a27` - Confirms this folder is the clean local public-candidate root.
- `release/agentops-control-tower-public-candidate.zip` (present, optional) - size=773263 sha256=`b0fe4414c923c47260213bae03dd9fb38ad3de91296b97fe7682b8ba6bbe652a` - Optional local ZIP generated inside the public candidate for review.
- `reports/latest_public_candidate_zip_manifest.json` (present, optional) - size=12677 sha256=`08b532d955587f5fd5e2021075fa186f56ce2cc5829f4e87e2504d2bfa59e0fd` - Optional machine-readable candidate ZIP manifest.
- `README.md` (present, required) - size=20826 sha256=`5bd90033a12afba0192d9eeb7f96298b103a18768d9100476a712b8409760505` - Portable project overview and local run instructions.
- `LICENSE` (present, required) - size=11358 sha256=`c95bae1d1ce0235ecccd3560b772ec1efb97f348a79f0fbe0a634f0c2ccefe2c` - Open-source license candidate for public review.
- `architecture_diagram.md` (present, required) - size=1912 sha256=`b3b0f36a0d1e0a3bdd8d45c926e0d5fb6fff5ca9791c95d8fd90a6d9a3fd454b` - Root architecture evidence required by the submission packet.
- `assets/dashboard_preview.png` (present, required) - size=75210 sha256=`a172e0fa0fcaa2b4bb0a96b7b02c5bd326b37dbf26d5c4130010f54579df6142` - Visual README/Devpost preview asset.
- `prototype/agentops_control_tower.py` (present, required) - size=36533 sha256=`fce2f1c75eb25f4dfab60c57bfbbcbc9b0e126840b5672d9bfecbf070f5b871b` - Generator for synthetic checkout-incident events, analysis, dashboard, and SPL examples.
- `data/splunk_agentops_events.csv` (present, required) - size=8368 sha256=`3bb781d0e8859b52b5dd6676b35b8d051b9d2c355cec05bcb5ae2f85b5aa5a6e` - Synthetic data export for a future agentops_events index after approval.
- `submission/SPL_QUERIES.md` (present, required) - size=1783 sha256=`feb15f47a2498d4f54a2cc0ae0e41767c0c6100ebdcb6dcc2f4989651920e02a` - Reviewer-facing SPL examples for the Control Tower flow.
- `splunk_app/agentops_control_tower/default/indexes.conf` (present, required) - size=212 sha256=`4e966767e2b53e1c45102702824549f04d785e32052d0692c0f1f3410c2e9ffd` - Optional local index definition for agentops_events.
- `splunk_app/agentops_control_tower/default/props.conf` (present, required) - size=217 sha256=`6c6e3704dbd785b9fc52526b3c5fe429ac5648982d5347fce226d087fc6b024d` - CSV extraction and timestamp parsing for the agentops:events sourcetype.
- `dist/agentops-control-tower-splunk-app.spl` (present, required) - size=2409 sha256=`061d79ceec155e7b9681bc5fcf671aa5685680f1ed274d404a0947817998e23e` - Local .spl package candidate; not installed or uploaded.
- `reports/latest_splunk_app_package_manifest.html` (present, required) - size=3767 sha256=`8bd3e3535b604785a3ead259c231be69401d4906b2533f9543a7fc3d691d47f1` - Members, SHA256, and package boundary evidence.
- `reports/latest_splunk_app_package_manifest.json` (present, required) - size=2255 sha256=`31c961482a64df27e972c7ff5c4553eaac2e16fa2408e0a5708a2cff7f99213a` - Machine-readable .spl integrity evidence.
- `reports/latest_splunk_mcp_command_plan.html` (present, required) - size=7956 sha256=`f18c8514781183a40e114ba65820383cde5fd401d85a856cbc24257505139e2c` - Post-approval live Splunk/MCP setup and proof command plan.
- `reports/latest_splunk_mcp_proof_brief.html` (present, required) - size=9457 sha256=`30086309e0f80c75965b272f1f608435942e527fa4321c2a189f0512d061a0e4` - Success criteria, screen safety, stop conditions, and claim-upgrade rules for optional live proof.
- `reports/latest_splunk_mcp_prompt_pack.html` (present, required) - size=8643 sha256=`d9fda2d8db8ebecb0048b97768cb6948faaaaf3f7f5306a4c4c081e5ee70b3ad` - Prompt-by-prompt live proof guide for evidence-backed MCP answers.
- `reports/latest_splunk_mcp_prompt_pack.json` (present, required) - size=8715 sha256=`a2843e522b735e5512dc50cf086410d8ec1de6e32c552ac3110634c38f385d9f` - Machine-readable prompt keys, SPL, expected citations, and live-proof gates.
- `reports/latest_splunk_mcp_prompt_pack.md` (present, required) - size=6775 sha256=`b84338006dcf4c7c3b9a8e565a4fcb7e1e175a7f6518c9a803b0b1bdfd90fa4d` - Reviewable prompt pack for approved live proof capture.
- `submission/SPLUNK_MCP_PROMPT_PACK.md` (present, required) - size=6775 sha256=`b84338006dcf4c7c3b9a8e565a4fcb7e1e175a7f6518c9a803b0b1bdfd90fa4d` - Submission-side copy of the prompt pack and stop conditions.
- `reports/latest_claim_evidence_matrix.html` (present, required) - size=11006 sha256=`2f03b115b3d85f307c65e8788f20261033ade4b3254561317ca18f867f082c80` - Allowed wording, avoid wording, evidence, and remaining gates.
- `reports/latest_claim_evidence_matrix.json` (present, required) - size=11992 sha256=`7988029f56834ae73d0f8f1fd4e65027afc3d35da0a4556fad32e8b84f925f4c` - Machine-readable claim support status.
- `reports/latest_submission_gate_ledger.html` (present, required) - size=9016 sha256=`b8bd1ef7a5746e931f684cb4baa6b46483982941f34a07ca5c23a8af4db235e4` - Approval-gate ledger for public repo, video, live proof, and Devpost.
- `reports/latest_submission_deadline_burndown.html` (present, required) - size=10583 sha256=`acb43ec2ed009238e244c074edf732d81fb5480dd95b5d722199f2d856ba3bb1` - Deadline-aware path for public repo, video, optional live proof, URL writeback, and Devpost final submit.
- `reports/latest_submission_deadline_burndown.json` (present, required) - size=7548 sha256=`ad555b48106fdbf6a7a2544cbb996dd7a6c8a4af64b7d0eea76d92856d817af8` - Machine-readable target date, official deadline, milestones, and blocked final submit gate.
- `reports/latest_submission_deadline_burndown.md` (present, required) - size=5153 sha256=`859f5500e0db4631cd1eaa1ed1b065cc0f5acb47d70763876f0be6a850266ec6` - Reviewable deadline burndown for local launch planning.
- `submission/SUBMISSION_DEADLINE_BURNDOWN.md` (present, required) - size=5153 sha256=`859f5500e0db4631cd1eaa1ed1b065cc0f5acb47d70763876f0be6a850266ec6` - Submission-side copy of the deadline burndown and approval timing path.
- `reports/latest_next_approval_packet.html` (present, required) - size=15096 sha256=`d591b6a74232d56ae4714f104d018d873daa69a3174922985ef06ee694c3087b` - Next user approval target, approval phrases, risks, and verification steps.
- `reports/latest_next_approval_packet.json` (present, required) - size=13143 sha256=`6e5ca2be9792bd551d242ab21069a7c0731452d9842c186d25ce3fcaf34bc4ed` - Machine-readable next approval status and human-confirmation gates.
- `submission/NEXT_APPROVAL_PACKET.md` (present, required) - size=9594 sha256=`7e2723a48164945bbdea413a524f55145ebec2dfb34338198fae7b4db815ebad` - Markdown copy of the next approval packet for final user decision support.
- `reports/latest_approval_consistency_audit.html` (present, required) - size=6609 sha256=`047d7be233be735a6d560817c23bfa818db3fc686f4882f916e1acb037a622e7` - Checks approval order consistency across plan, approval gates, launch brief, next packet, and validator state.
- `reports/latest_approval_consistency_audit.json` (present, required) - size=5756 sha256=`e2f80d5943f00052dfd866ea3638e1738cac84f50420001501a842a2d3a6ee3b` - Machine-readable approval-order consistency status.
- `reports/latest_status_conflict_audit.html` (present, optional) - size=7550 sha256=`ff188298cdbb139b647182501e9cced5ecc966b0d83e31d61e3dc77c2fcd6198` - Scans root and public-candidate JSON reports for stale failed statuses or missing local artifacts.
- `reports/latest_status_conflict_audit.json` (present, optional) - size=6294 sha256=`f21592b7f2136cb5f802590159df0e9ac8549d29d05f7c6e8e9eb13945e7ff06` - Machine-readable status conflict scan and critical ready-state checks.
- `reports/latest_status_conflict_audit.md` (present, optional) - size=4020 sha256=`9446d5bfcf64a263f9e4f3ed6d0edacf59727e6ec4768844fd7dcf3681c9b06f` - Reviewable status conflict audit summary.
- `reports/latest_public_launch_snapshot.html` (present, required) - size=8445 sha256=`55068bd9b5de2a7ba0cbc27adb0cc1b76ebe8bb5aaf3adb73f47e37be04d4fb8` - Frozen local snapshot for public repo and demo video approval review.
- `reports/latest_public_launch_snapshot.json` (present, required) - size=8219 sha256=`f087dadb18db600fc7741ce35340224587022d016ef336f44dd20b2d95e5f79f` - Machine-readable public launch readiness, ZIP hash, approval phrases, and remaining gates.
- `reports/latest_public_launch_snapshot.md` (present, required) - size=4296 sha256=`40c4771b22535b60bef87a6e1072c61c5d18d5cc821f5f79f3c4371491e997c9` - Reviewable public launch snapshot for copy/paste and audit.
- `reports/latest_public_repo_metadata.html` (present, required) - size=6104 sha256=`21c346bc21b00914423a19d99556fef951d1571a1ef3b3b907530d981947b93f` - GitHub repository name, description, topics, expected readback, and no-publish boundary.
- `reports/latest_public_repo_metadata.json` (present, required) - size=3844 sha256=`ad5b7fdaecad7926f7f38db8496fe686e4723b51bad896a0dd1e977c44dc80f6` - Machine-readable public repository metadata and post-approval readback expectations.
- `reports/latest_public_repo_metadata.md` (present, required) - size=2920 sha256=`b5a935204c7a3e8f3bf6b0c4fc8f52a9a9cb21a5568726ff270283b2949bc0c4` - Reviewable public repository metadata packet.
- `submission/PUBLIC_REPO_METADATA.md` (present, required) - size=2920 sha256=`b5a935204c7a3e8f3bf6b0c4fc8f52a9a9cb21a5568726ff270283b2949bc0c4` - Submission-side copy of public repository metadata and stop conditions.
- `submission/USER_APPROVAL_GATES.md` (present, required) - size=1451 sha256=`00e00ba2b137bea9a14b2e4cd6904163a87d57847f094ad5772dd97ac1b2009a` - Human approval boundaries and current recommended approval order.
- `READY_FOR_REVIEW.md` (present, required) - size=1009 sha256=`ff1b2788abb21f856dea23e2123da80068a75ba06e1f0c48f0a39b98d36ddbc8` - Shortest local review entrypoint for the current SPAK packet.
- `reports/latest_judge_review_packet.html` (present, required) - size=4659 sha256=`cd9a4fc0fdfc60b6e84a5ee93ab20e13c921ddde2a08f52d34f899e244d04f6a` - Judge-facing local packet with readiness, evidence, and closed external gates.
- `reports/latest_judge_review_packet.json` (present, required) - size=3678 sha256=`b5d0990d377502a9d6a1668eee0d7f49602dd286cb9418658ee625d5c577caa2` - Machine-readable SPAK judge packet status.
- `reports/latest_judge_review_packet.md` (present, required) - size=2427 sha256=`2144e7e0b0c6daeffdfd5efe5558a5bd7fd6b70e0670a9f0c78b887fbe0160ac` - Reviewable SPAK judge packet summary.
- `submission/JUDGE_REVIEW_PACKET.md` (present, required) - size=2427 sha256=`2144e7e0b0c6daeffdfd5efe5558a5bd7fd6b70e0670a9f0c78b887fbe0160ac` - Submission-side copy of the local judge review packet.
- `reports/latest_local_readiness_baseline.html` (present, required) - size=3843 sha256=`63d11110eadf88b743574f8f8b3ddfec5980eac8210b5e5401018f3f4252e14c` - Targeted pass/fail baseline for local package/proof readiness.
- `reports/latest_local_readiness_baseline.json` (present, required) - size=2985 sha256=`056e84ef57452cefe6f0602d07cfcb9e4a40ac41b5022bc109abc7eb8dc98aa6` - Machine-readable targeted local readiness baseline.
- `reports/latest_local_readiness_baseline.md` (present, required) - size=1515 sha256=`7465ddf21facc57cc927adf6bd341e231be779f1c6dea52653f5dbbf0f8f7a7a` - Reviewable targeted local readiness baseline.
- `reports/latest_public_candidate_local_audit.html` (present, required) - size=3395 sha256=`ccedb28b76d95d5f7736a8afdc0a49225111f401d83e2e17c0c087eff0c13c6b` - Secret/internal-path and completeness audit for the public repo candidate.
- `reports/latest_public_candidate_local_audit.json` (present, required) - size=1975 sha256=`a3717fe818b1816a8d7de7d09a966d00a8cb0ac65e61cc69fb24a2c04efda8bb` - Machine-readable public candidate safety audit.
- `reports/latest_public_candidate_local_audit.md` (present, required) - size=1124 sha256=`02c148111253c14636f0aee7a3d0e185bcd923e0b86080638429773918a56902` - Reviewable public candidate safety audit.
- `reports/latest_devpost_copy_audit.html` (present, required) - size=3382 sha256=`37b62d3af36576082434a90c5bf919c71a4fe0b108cd5bdbc83b6066a695ca07` - Local audit of Devpost copy readiness with final submission still gated.
- `reports/latest_devpost_copy_audit.json` (present, required) - size=2033 sha256=`0cf6073c9a5e7348b64fe6c5ce2f87b55c9dc5ec5adc817696acda73e644bab2` - Machine-readable Devpost copy audit.
- `reports/latest_devpost_copy_audit.md` (present, required) - size=1121 sha256=`3226ec2ab990ea757de9aafff4bdac7706a37112f050aa5f55beec251e55dce5` - Reviewable Devpost copy audit.
- `reports/latest_judge_quickstart.html` (present, required) - size=9800 sha256=`8af1a5780240d7a7512cd20d60e1cb113ed03306696bf3f2cd9b5dc37a5bd163` - Five-minute review path for judges and final preflight.
- `reports/latest_devpost_final_copy.md` (present, required) - size=7027 sha256=`e8df366b808c9794fb40fbf5f00762ebfaa40e0f4413db36bf68fba25f79d39d` - Copy/paste packet with pending public URL placeholders.
- `reports/latest_post_action_evidence_brief.html` (present, required) - size=10308 sha256=`f3633bba8732bdfb711b975aebfd1e1bbf3c63483042c9c27020042cc34cd42a` - Readback plan after approved external actions.
- `reports/latest_post_action_evidence_brief.json` (present, required) - size=9067 sha256=`03cf2583d8a27be638181619302539f56f5cd30bf444c192f561c509cdad6497` - Machine-readable post-action gate state.
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` (present, required) - size=7393 sha256=`f35de1a10121305df6bc05c184d5855101beaeb186f62a2ceb48bf8e103a248c` - Template for safe readback after approved external actions.
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present, required) - size=9872 sha256=`fb74a1ff294c98503e3670bc993f9b5258acd471f4d838b592024d7155a01137` - Live Splunk/MCP proof capture slots, expected readback, stop conditions, and claim-upgrade gate.
- `reports/latest_splunk_mcp_proof_capture_manifest.json` (present, required) - size=8201 sha256=`b008e3f8f212a1725764efadb82d6e55d91626f024d9e68db0fc5af4116da95c` - Machine-readable live Splunk/MCP proof capture gate state.
- `reports/latest_splunk_mcp_proof_capture_manifest.md` (present, required) - size=6280 sha256=`574fc46a3560362a475c5d2f0170aab09e06a2fd7e50bd261c63cda5157e360a` - Reviewable live Splunk/MCP proof capture manifest.
- `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md` (present, required) - size=6280 sha256=`574fc46a3560362a475c5d2f0170aab09e06a2fd7e50bd261c63cda5157e360a` - Submission-side copy of the proof capture manifest and no-live-proof boundary.
- `reports/latest_official_source_freshness.html` (present, required) - size=6399 sha256=`c8b9c27dac1a204aa0a7c58fcd8be5b26ffc60c28d13dbc526c4a6404885b894` - Current official Devpost source and requirement freshness evidence.
- `reports/latest_official_source_freshness.json` (present, required) - size=7744 sha256=`d3f47dca236b8f9facbbd2f01bf55fe7436739632ac99a3bedb40fd92acb749a` - Machine-readable official source freshness and local mapping status.
- `reports/latest_content_rights_audit.html` (present, required) - size=4886 sha256=`9d23cbe82972acd73d2f7788b72c3254f3692b95cd98f534504b15a032aaa001` - License, bundled asset, audio/video, and screen-safety evidence.
- `reports/latest_content_rights_audit.json` (present, required) - size=3632 sha256=`1847111ec2b84a80e93fa7c14e1ec7422253adf0d2d073d68513057695f1ca9a` - Machine-readable content rights and asset safety status.
- `reports/latest_eligibility_compliance_audit.html` (present, required) - size=7810 sha256=`fd0302542ef8e148d3edf5e4fded7804741c9689b931eda7c1f338289cc5d1ea` - Eligibility, ownership, language, uniqueness, and human-confirmation evidence.
- `reports/latest_eligibility_compliance_audit.json` (present, required) - size=6314 sha256=`2bc4d15a70320a5174ac8e4e59ce63a9733130d163eb4ecda6f9ee3534c1f953` - Machine-readable eligibility and compliance status.

## Publication Boundary

This release integrity manifest is local readback evidence only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.
