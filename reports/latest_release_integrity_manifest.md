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
- Size bytes: 771004
- SHA256: `38f0d88dd0896740e3712877cc8d0a7c9fe9c33c07cf7bbb96235bc7f3934b6e`
- Smoke status: not_applicable_public_candidate_root

## Checks

- required artifacts present: pass (all required artifacts present)
- Splunk app package SHA256 consistency: pass (manifest=8817972eb99d06d0cbfd8dffd2de4c758a0f41cf867ed65816ddfd817f2ea2e6 artifact=8817972eb99d06d0cbfd8dffd2de4c758a0f41cf867ed65816ddfd817f2ea2e6)
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
- `release/agentops-control-tower-public-candidate.zip` (present, optional) - size=771004 sha256=`38f0d88dd0896740e3712877cc8d0a7c9fe9c33c07cf7bbb96235bc7f3934b6e` - Optional local ZIP generated inside the public candidate for review.
- `reports/latest_public_candidate_zip_manifest.json` (present, optional) - size=12677 sha256=`1d9916f6eea0834d3bc2f80d8983537952f399f3f788b7f2b733833a60b97b39` - Optional machine-readable candidate ZIP manifest.
- `README.md` (present, required) - size=20826 sha256=`5bd90033a12afba0192d9eeb7f96298b103a18768d9100476a712b8409760505` - Portable project overview and local run instructions.
- `LICENSE` (present, required) - size=4881 sha256=`8bcd9791ac7d1ab77082c66a607f0eec083192599b0266d17a8ae55b1517acde` - Open-source license candidate for public review.
- `architecture_diagram.md` (present, required) - size=1912 sha256=`b3b0f36a0d1e0a3bdd8d45c926e0d5fb6fff5ca9791c95d8fd90a6d9a3fd454b` - Root architecture evidence required by the submission packet.
- `assets/dashboard_preview.png` (present, required) - size=75210 sha256=`a172e0fa0fcaa2b4bb0a96b7b02c5bd326b37dbf26d5c4130010f54579df6142` - Visual README/Devpost preview asset.
- `prototype/agentops_control_tower.py` (present, required) - size=36533 sha256=`fce2f1c75eb25f4dfab60c57bfbbcbc9b0e126840b5672d9bfecbf070f5b871b` - Generator for synthetic checkout-incident events, analysis, dashboard, and SPL examples.
- `data/splunk_agentops_events.csv` (present, required) - size=8368 sha256=`3bb781d0e8859b52b5dd6676b35b8d051b9d2c355cec05bcb5ae2f85b5aa5a6e` - Synthetic data export for a future agentops_events index after approval.
- `submission/SPL_QUERIES.md` (present, required) - size=1783 sha256=`feb15f47a2498d4f54a2cc0ae0e41767c0c6100ebdcb6dcc2f4989651920e02a` - Reviewer-facing SPL examples for the Control Tower flow.
- `splunk_app/agentops_control_tower/default/indexes.conf` (present, required) - size=212 sha256=`4e966767e2b53e1c45102702824549f04d785e32052d0692c0f1f3410c2e9ffd` - Optional local index definition for agentops_events.
- `splunk_app/agentops_control_tower/default/props.conf` (present, required) - size=217 sha256=`6c6e3704dbd785b9fc52526b3c5fe429ac5648982d5347fce226d087fc6b024d` - CSV extraction and timestamp parsing for the agentops:events sourcetype.
- `dist/agentops-control-tower-splunk-app.spl` (present, required) - size=2409 sha256=`8817972eb99d06d0cbfd8dffd2de4c758a0f41cf867ed65816ddfd817f2ea2e6` - Local .spl package candidate; not installed or uploaded.
- `reports/latest_splunk_app_package_manifest.html` (present, required) - size=3767 sha256=`410fc57edf471bf4bf86ded687ec2279700d54857d89bcbe9f67472b30b92c61` - Members, SHA256, and package boundary evidence.
- `reports/latest_splunk_app_package_manifest.json` (present, required) - size=2255 sha256=`dd48e5d10a0e149e8556edb421c02013f25982bcb992268a0d92ae5bd570419e` - Machine-readable .spl integrity evidence.
- `reports/latest_splunk_mcp_command_plan.html` (present, required) - size=7956 sha256=`f18c8514781183a40e114ba65820383cde5fd401d85a856cbc24257505139e2c` - Post-approval live Splunk/MCP setup and proof command plan.
- `reports/latest_splunk_mcp_proof_brief.html` (present, required) - size=9457 sha256=`30086309e0f80c75965b272f1f608435942e527fa4321c2a189f0512d061a0e4` - Success criteria, screen safety, stop conditions, and claim-upgrade rules for optional live proof.
- `reports/latest_splunk_mcp_prompt_pack.html` (present, required) - size=8643 sha256=`d9fda2d8db8ebecb0048b97768cb6948faaaaf3f7f5306a4c4c081e5ee70b3ad` - Prompt-by-prompt live proof guide for evidence-backed MCP answers.
- `reports/latest_splunk_mcp_prompt_pack.json` (present, required) - size=8715 sha256=`df96df62ccf90153ddaad34c5146f1cb0ce5af4efe8559acb5a904ed54bc108b` - Machine-readable prompt keys, SPL, expected citations, and live-proof gates.
- `reports/latest_splunk_mcp_prompt_pack.md` (present, required) - size=6775 sha256=`b84338006dcf4c7c3b9a8e565a4fcb7e1e175a7f6518c9a803b0b1bdfd90fa4d` - Reviewable prompt pack for approved live proof capture.
- `submission/SPLUNK_MCP_PROMPT_PACK.md` (present, required) - size=6775 sha256=`b84338006dcf4c7c3b9a8e565a4fcb7e1e175a7f6518c9a803b0b1bdfd90fa4d` - Submission-side copy of the prompt pack and stop conditions.
- `reports/latest_claim_evidence_matrix.html` (present, required) - size=11006 sha256=`2f03b115b3d85f307c65e8788f20261033ade4b3254561317ca18f867f082c80` - Allowed wording, avoid wording, evidence, and remaining gates.
- `reports/latest_claim_evidence_matrix.json` (present, required) - size=11992 sha256=`0279a0471a4b4564b78225b7611102288d28b18ac173ccbec79b05703fb4a44b` - Machine-readable claim support status.
- `reports/latest_submission_gate_ledger.html` (present, required) - size=9016 sha256=`b8bd1ef7a5746e931f684cb4baa6b46483982941f34a07ca5c23a8af4db235e4` - Approval-gate ledger for public repo, video, live proof, and Devpost.
- `reports/latest_submission_deadline_burndown.html` (present, required) - size=10583 sha256=`7ef9bf2a6840792173644fa5ab76df00807536c32c94e170648bdd26fb0cddc2` - Deadline-aware path for public repo, video, optional live proof, URL writeback, and Devpost final submit.
- `reports/latest_submission_deadline_burndown.json` (present, required) - size=7548 sha256=`89c2fe41e518ef1a6afbc38050d69d7359a21fec6712f2824806b808ff23b969` - Machine-readable target date, official deadline, milestones, and blocked final submit gate.
- `reports/latest_submission_deadline_burndown.md` (present, required) - size=5153 sha256=`c2a988acf44a5ec4ca17524e7ccc94ae094b56752705675d75214cd4d5a546eb` - Reviewable deadline burndown for local launch planning.
- `submission/SUBMISSION_DEADLINE_BURNDOWN.md` (present, required) - size=5153 sha256=`c2a988acf44a5ec4ca17524e7ccc94ae094b56752705675d75214cd4d5a546eb` - Submission-side copy of the deadline burndown and approval timing path.
- `reports/latest_next_approval_packet.html` (present, required) - size=15096 sha256=`d591b6a74232d56ae4714f104d018d873daa69a3174922985ef06ee694c3087b` - Next user approval target, approval phrases, risks, and verification steps.
- `reports/latest_next_approval_packet.json` (present, required) - size=13143 sha256=`6dd11a105ff9fc847407fc43d0b53d3d0206731defa2fea38b30ce33a29deb85` - Machine-readable next approval status and human-confirmation gates.
- `submission/NEXT_APPROVAL_PACKET.md` (present, required) - size=9594 sha256=`7e2723a48164945bbdea413a524f55145ebec2dfb34338198fae7b4db815ebad` - Markdown copy of the next approval packet for final user decision support.
- `reports/latest_approval_consistency_audit.html` (present, required) - size=6609 sha256=`047d7be233be735a6d560817c23bfa818db3fc686f4882f916e1acb037a622e7` - Checks approval order consistency across plan, approval gates, launch brief, next packet, and validator state.
- `reports/latest_approval_consistency_audit.json` (present, required) - size=5756 sha256=`17133639b98aa3d627c2d8a6f3cc7530ad24170090f8da981ffb4a95357b3f92` - Machine-readable approval-order consistency status.
- `reports/latest_status_conflict_audit.html` (present, optional) - size=7550 sha256=`ff188298cdbb139b647182501e9cced5ecc966b0d83e31d61e3dc77c2fcd6198` - Scans root and public-candidate JSON reports for stale failed statuses or missing local artifacts.
- `reports/latest_status_conflict_audit.json` (present, optional) - size=6294 sha256=`6a2b7d03de24411abc0e2735b8cd932c94db156f870a0a129583246a4fb5f398` - Machine-readable status conflict scan and critical ready-state checks.
- `reports/latest_status_conflict_audit.md` (present, optional) - size=4020 sha256=`9446d5bfcf64a263f9e4f3ed6d0edacf59727e6ec4768844fd7dcf3681c9b06f` - Reviewable status conflict audit summary.
- `reports/latest_public_launch_snapshot.html` (present, required) - size=8445 sha256=`55068bd9b5de2a7ba0cbc27adb0cc1b76ebe8bb5aaf3adb73f47e37be04d4fb8` - Frozen local snapshot for public repo and demo video approval review.
- `reports/latest_public_launch_snapshot.json` (present, required) - size=8219 sha256=`e7c42b4dd4cba05073259567564d1ba238113eb177d79f7fb7712147cb15cced` - Machine-readable public launch readiness, ZIP hash, approval phrases, and remaining gates.
- `reports/latest_public_launch_snapshot.md` (present, required) - size=4296 sha256=`40c4771b22535b60bef87a6e1072c61c5d18d5cc821f5f79f3c4371491e997c9` - Reviewable public launch snapshot for copy/paste and audit.
- `reports/latest_public_repo_metadata.html` (present, required) - size=6137 sha256=`cc7030e24bd286ffb12c7363fad388898e2b508990fd212dfb55f3bfe8225a32` - GitHub repository name, description, topics, expected readback, and no-publish boundary.
- `reports/latest_public_repo_metadata.json` (present, required) - size=3877 sha256=`7909f5e7a8048530ca76bf56840e9587d331be7ed109f26e68fc4f6f195ffdc9` - Machine-readable public repository metadata and post-approval readback expectations.
- `reports/latest_public_repo_metadata.md` (present, required) - size=2953 sha256=`7004301efc77638842134e45804bc0c72bc28fb80569a2a39eda0cd1655f79a5` - Reviewable public repository metadata packet.
- `submission/PUBLIC_REPO_METADATA.md` (present, required) - size=2953 sha256=`7004301efc77638842134e45804bc0c72bc28fb80569a2a39eda0cd1655f79a5` - Submission-side copy of public repository metadata and stop conditions.
- `submission/USER_APPROVAL_GATES.md` (present, required) - size=1451 sha256=`00e00ba2b137bea9a14b2e4cd6904163a87d57847f094ad5772dd97ac1b2009a` - Human approval boundaries and current recommended approval order.
- `READY_FOR_REVIEW.md` (present, required) - size=1009 sha256=`ff1b2788abb21f856dea23e2123da80068a75ba06e1f0c48f0a39b98d36ddbc8` - Shortest local review entrypoint for the current SPAK packet.
- `reports/latest_judge_review_packet.html` (present, required) - size=4659 sha256=`cd9a4fc0fdfc60b6e84a5ee93ab20e13c921ddde2a08f52d34f899e244d04f6a` - Judge-facing local packet with readiness, evidence, and closed external gates.
- `reports/latest_judge_review_packet.json` (present, required) - size=3678 sha256=`73b06be1060b1f3feb0f51a24fc58981a55441a075213077c21a0ff10651beed` - Machine-readable SPAK judge packet status.
- `reports/latest_judge_review_packet.md` (present, required) - size=2427 sha256=`357a9c96bcc8687f4dd9b01c7d9e7dee7a1e8e1793028da95ad44dae792b3b2f` - Reviewable SPAK judge packet summary.
- `submission/JUDGE_REVIEW_PACKET.md` (present, required) - size=2427 sha256=`357a9c96bcc8687f4dd9b01c7d9e7dee7a1e8e1793028da95ad44dae792b3b2f` - Submission-side copy of the local judge review packet.
- `reports/latest_local_readiness_baseline.html` (present, required) - size=3857 sha256=`4f6966cb0866f33ff2ef079d912d5bd60058ebd995e36f37bafded8a7f03e272` - Targeted pass/fail baseline for local package/proof readiness.
- `reports/latest_local_readiness_baseline.json` (present, required) - size=2999 sha256=`86b3fe3df5d730ef37bf75e8dbfbb70927d96d27b4d037f58f0de8dad2920ea1` - Machine-readable targeted local readiness baseline.
- `reports/latest_local_readiness_baseline.md` (present, required) - size=1529 sha256=`92114852b0939c39388208450f217ea4182b0589792de8edd4352017c9ad9885` - Reviewable targeted local readiness baseline.
- `reports/latest_public_candidate_local_audit.html` (present, required) - size=3395 sha256=`9d95edfed8404802adf6ac82921cba9d52d36906d37e5a07da86610e44823466` - Secret/internal-path and completeness audit for the public repo candidate.
- `reports/latest_public_candidate_local_audit.json` (present, required) - size=1975 sha256=`aa8c0bd1f39f6c676650f29522874c0215fabf79ad6310efd4edcb03ba9076a3` - Machine-readable public candidate safety audit.
- `reports/latest_public_candidate_local_audit.md` (present, required) - size=1124 sha256=`74c63dbd920d60aae11114552390dac0d6bd80be72698108d2484651de34c459` - Reviewable public candidate safety audit.
- `reports/latest_devpost_copy_audit.html` (present, required) - size=3382 sha256=`985ef604b4efa19650bfae397a8b2d3fa94bf1704c75b7e7979148fcdf36ac15` - Local audit of Devpost copy readiness with final submission still gated.
- `reports/latest_devpost_copy_audit.json` (present, required) - size=2033 sha256=`1d8bda3c708a322b8d108e7101d4fa7f27049e293a134fd566597874b0992eb4` - Machine-readable Devpost copy audit.
- `reports/latest_devpost_copy_audit.md` (present, required) - size=1121 sha256=`ebf70a22791d0b11d531878a3f991b407f74708ba428fd401ac8886f5d781cb7` - Reviewable Devpost copy audit.
- `reports/latest_judge_quickstart.html` (present, required) - size=9800 sha256=`8af1a5780240d7a7512cd20d60e1cb113ed03306696bf3f2cd9b5dc37a5bd163` - Five-minute review path for judges and final preflight.
- `reports/latest_devpost_final_copy.md` (present, required) - size=7027 sha256=`e8df366b808c9794fb40fbf5f00762ebfaa40e0f4413db36bf68fba25f79d39d` - Copy/paste packet with pending public URL placeholders.
- `reports/latest_post_action_evidence_brief.html` (present, required) - size=10308 sha256=`f3633bba8732bdfb711b975aebfd1e1bbf3c63483042c9c27020042cc34cd42a` - Readback plan after approved external actions.
- `reports/latest_post_action_evidence_brief.json` (present, required) - size=9067 sha256=`569dcf9ca12226ef680fdbdbf40b844f9dd2e91599561f39661d271cffc3c579` - Machine-readable post-action gate state.
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` (present, required) - size=7393 sha256=`f35de1a10121305df6bc05c184d5855101beaeb186f62a2ceb48bf8e103a248c` - Template for safe readback after approved external actions.
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present, required) - size=9872 sha256=`fb74a1ff294c98503e3670bc993f9b5258acd471f4d838b592024d7155a01137` - Live Splunk/MCP proof capture slots, expected readback, stop conditions, and claim-upgrade gate.
- `reports/latest_splunk_mcp_proof_capture_manifest.json` (present, required) - size=8201 sha256=`3592e16298561a4a62234be14d8ba7d3b5c444ab01c2070ce5e5ca6a6dd570dc` - Machine-readable live Splunk/MCP proof capture gate state.
- `reports/latest_splunk_mcp_proof_capture_manifest.md` (present, required) - size=6280 sha256=`574fc46a3560362a475c5d2f0170aab09e06a2fd7e50bd261c63cda5157e360a` - Reviewable live Splunk/MCP proof capture manifest.
- `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md` (present, required) - size=6280 sha256=`574fc46a3560362a475c5d2f0170aab09e06a2fd7e50bd261c63cda5157e360a` - Submission-side copy of the proof capture manifest and no-live-proof boundary.
- `reports/latest_official_source_freshness.html` (present, required) - size=6399 sha256=`c8b9c27dac1a204aa0a7c58fcd8be5b26ffc60c28d13dbc526c4a6404885b894` - Current official Devpost source and requirement freshness evidence.
- `reports/latest_official_source_freshness.json` (present, required) - size=7744 sha256=`cd4baf4d308a7e1c937fb39fc0e9ff7184d3373e17bafcf677ed48c828016202` - Machine-readable official source freshness and local mapping status.
- `reports/latest_content_rights_audit.html` (present, required) - size=4886 sha256=`9d23cbe82972acd73d2f7788b72c3254f3692b95cd98f534504b15a032aaa001` - License, bundled asset, audio/video, and screen-safety evidence.
- `reports/latest_content_rights_audit.json` (present, required) - size=3632 sha256=`8c32a6adaeca63eecadc3cd007d3ab12c1b518147293198bc01d78c7f3f927c1` - Machine-readable content rights and asset safety status.
- `reports/latest_eligibility_compliance_audit.html` (present, required) - size=7810 sha256=`fd0302542ef8e148d3edf5e4fded7804741c9689b931eda7c1f338289cc5d1ea` - Eligibility, ownership, language, uniqueness, and human-confirmation evidence.
- `reports/latest_eligibility_compliance_audit.json` (present, required) - size=6314 sha256=`77125c5476db8d3b53780f9b2b642a99fb47a2d281b1ebaec1e6c75c161cb5b3` - Machine-readable eligibility and compliance status.

## Publication Boundary

This release integrity manifest is local readback evidence only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.
