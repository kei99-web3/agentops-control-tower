# Release Integrity Manifest

Status: needs_more_evidence
Root type: workspace
Validation status: needs_more_evidence
Validation failed count: 29
Validation source: reports/latest_submission_validation.json
Artifact count: 107
Final submit ready: true

## Release ZIP

- Path: `release/agentops-control-tower-public-candidate.zip`
- Exists: True
- File count: 250
- Size bytes: 803352
- SHA256: `769db8778a993757aed1600062dde25a9daff8280ede4097aaf8554c5cea0ea9`
- Smoke status: fail

## Checks

- required artifacts present: pass (all required artifacts present)
- Splunk app package SHA256 consistency: pass (manifest=fdad475534452d6175dcb69d77e4a5ef9effb5c8aac94d0dbfcf864387db9e4f artifact=fdad475534452d6175dcb69d77e4a5ef9effb5c8aac94d0dbfcf864387db9e4f)
- Splunk app package manifest status: pass (ready_for_user_review)
- Splunk MCP prompt pack status: pass (status=ready_for_user_review live=True external=False)
- live Splunk Docker and official MCP proof captured with bounded claim: pass (status=live_splunk_verified_official_mcp_verified live=True adapter=True official=True failed_queries=0)
- claim boundary status: pass (pass)
- release ZIP smoke status: fail (fail)
- release ZIP count consistency: pass (zip=250 manifest=250 smoke=250)
- final submit remains gated: fail (True)
- approved URLs remain gated: fail (True)
- post-action external gates tracked: fail (missing)
- publication boundary text: pass (This release integrity manifest is local readback evidence only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.)
- video dry run status: fail (status=needs_more_evidence failed=4)
- public video upload preflight status: fail (status=needs_more_evidence allowed=False gate=needs_more_evidence)
- URL writeback dry run status: fail (status=needs_more_evidence failed=3 wrote=True)

## Artifact Integrity

- `release/agentops-control-tower-public-candidate.zip` (present, required) - size=803352 sha256=`769db8778a993757aed1600062dde25a9daff8280ede4097aaf8554c5cea0ea9` - Local ZIP for user review before public repo approval.
- `reports/latest_public_candidate_zip_manifest.html` (present, required) - size=17024 sha256=`725063ea7759bfb4c094341480e97bcb124f178f866a4d32d369f1ed9a1a9cb8` - ZIP content and publication boundary evidence.
- `reports/latest_public_candidate_zip_manifest.json` (present, required) - size=12828 sha256=`996492f8851b2ba559515fa8227113c734e844d65789fbe2f6a4f30f9b22aff2` - Machine-readable ZIP file count and package metadata.
- `reports/latest_release_zip_smoke_test.html` (present, required) - size=21934 sha256=`ed2ad2397d735fdb9788df1ef652e5d54a9af1b338435c0d5b49876922ae3071` - Extract-and-test proof for the local ZIP.
- `reports/latest_release_zip_smoke_test.json` (present, required) - size=19114 sha256=`3b366caeca27aad69cc49aba4c3fcfeb0f237da7c11bc2c10cc98505f4fafbe9` - Machine-readable smoke status and ZIP file count.
- `public_repo_candidate/agentops-control-tower/PUBLIC_REPO_CANDIDATE_MANIFEST.md` (present, required) - size=11663 sha256=`39410cd90dc860ad013bd79da19f17f917617b33081008df71dfca1276da93d6` - Clean local public-candidate staging boundary.
- `reports/latest_approval_execution_handoff.html` (present, required) - size=14081 sha256=`f5c59238611dfba798e25790572a5f090b98358e7857ce992a0a621fa9793bbd` - Private-workspace handoff for post-approval launch execution order, readbacks, and stop conditions.
- `reports/latest_approval_execution_handoff.json` (present, required) - size=10386 sha256=`7ade50f5e1f93dc8141b91a98d48da61b1b5098e566c0536175ca971497e07ef` - Machine-readable approval execution state and closed external-action boundary.
- `reports/latest_approval_execution_handoff.md` (present, required) - size=8401 sha256=`741444e9fa5571c4c9102e596e864fe99597a89e37ee53edc9ed01c75ec5435c` - Reviewable approval execution handoff for interrupted sessions.
- `submission/APPROVAL_EXECUTION_HANDOFF.md` (present, required) - size=8401 sha256=`741444e9fa5571c4c9102e596e864fe99597a89e37ee53edc9ed01c75ec5435c` - Submission-side copy of the local approval execution handoff.
- `reports/latest_live_splunk_docker_proof.html` (present, optional) - size=4563 sha256=`e1ee81f552c21bdc6e798355136434f67ebfd0300d1acc3205d20b0b7a726b5a` - Private local proof that the synthetic CSV indexed and queried successfully in ephemeral Docker Splunk.
- `reports/latest_live_splunk_docker_proof.json` (present, optional) - size=22554 sha256=`a2a91b670c7d42d25bca84a9081618a2778dd2876b496025813899ad36ed687d` - Machine-readable live Splunk query and local MCP SDK adapter readback; official Splunk MCP Server remains separate.
- `reports/latest_live_splunk_docker_proof.md` (present, optional) - size=3134 sha256=`f672f85a251d6e77226d22382bb0d66b4785c60a55454c3d45ac1a232e909986` - Reviewable summary of the approved synthetic-only live Docker proof.
- `scripts/run_live_splunk_docker_proof.py` (present, optional) - size=28285 sha256=`eb1ab035a6895ef92d3b59302096e24e931cfd624e42a89922bea9e221eea527` - Approved ephemeral Docker Splunk proof runner using synthetic data and read-only local MCP SDK adapter evidence.
- `reports/latest_public_repo_dry_run.html` (present, required) - size=6824 sha256=`96ed315af8f495af3ff2c54fd0ed113e1fd911355a745a7e0f7c71ca83ad8b18` - Isolated TEMP staging git-init/commit rehearsal for the clean public candidate before approval.
- `reports/latest_public_repo_dry_run.json` (present, required) - size=5965 sha256=`b01787b7034bdd8086f8ef953aa568955ee8b3387e7e2727d5cecd5d7685d07d` - Machine-readable public repo rehearsal status, scans, and closed submission gates.
- `reports/latest_public_repo_dry_run.md` (present, required) - size=3561 sha256=`f9bf109077f247c1b11ba87899b3d9c24a6b1d7bd0488571ab5b448546ca1f74` - Reviewable public repo rehearsal summary.
- `scripts/publish_public_repo_after_approval.py` (present, required) - size=28792 sha256=`0b5d58bc5afeada50be4214f19bdccdecaea2908c1271842e54c02884f8cb751` - Default non-executing helper that can publish only after the exact approval phrase and public git identity are supplied.
- `reports/latest_video_dry_run.html` (present, required) - size=6892 sha256=`186c89733c9ce8fdcbac7e8e87e334c0c8e547659d278bb54b3ec232c0ed616e` - Local recording rehearsal, timeline check, and screen-safety scan before approval.
- `reports/latest_video_dry_run.json` (present, required) - size=6832 sha256=`5438dd7445eaadbf97005c87bce9366849016990ee4e88d403b1d10b0e16a8e7` - Machine-readable recording rehearsal status and closed video gates.
- `reports/latest_video_dry_run.md` (present, required) - size=2545 sha256=`85865d0ea95b1ff261a0bb9de45d6f355a4f245cb3bec1add715724267c8c652` - Reviewable recording rehearsal summary.
- `reports/latest_video_recording_preview.html` (present, required) - size=5665 sha256=`ddcfc4ef94fd419ad6fb7c373205dfc9a66e12b5146bf49dd09e0a48b2a14434` - Local-only localhost preview preflight for recording from a public-candidate copy.
- `reports/latest_video_recording_preview.json` (present, required) - size=5050 sha256=`19b7a0f893e01f0453aa141080232d40d6648023816874d2144ea5764ee5fef7` - Machine-readable recording preview status, temp-stage policy, and screen scan results.
- `reports/latest_video_recording_preview.md` (present, required) - size=2048 sha256=`95e8f1296e5113674c3c664b19706cc72663683bb6a548f7eabb6bc9503cdc60` - Reviewable localhost recording preview summary.
- `reports/latest_video_upload_metadata.html` (present, required) - size=8076 sha256=`3c25e2ed117f7d3b06af98f4f216358dd4197c05ce1ccccb0cd0efcc6c0fe043` - Public demo video title, description, tags, visibility, readback expectations, and upload stop conditions.
- `reports/latest_video_upload_metadata.json` (present, required) - size=5685 sha256=`a976ee492168213b7fd79e5d5733dd5285c22fcc32f5f867f0c6db7ec4ee2412` - Machine-readable public demo video metadata and readback expectations.
- `reports/latest_video_upload_metadata.md` (present, required) - size=4656 sha256=`8fc948b047ea568e59268f2588c9ab0c9120394aed0b6c54b568b7d3db64075a` - Reviewable public demo video upload metadata packet.
- `submission/VIDEO_UPLOAD_METADATA.md` (present, required) - size=4656 sha256=`8fc948b047ea568e59268f2588c9ab0c9120394aed0b6c54b568b7d3db64075a` - Submission-side copy of public demo video metadata and stop conditions.
- `reports/latest_public_video_upload_preflight.html` (present, required) - size=5162 sha256=`0edb4474b9552eb79d548ac4c84f89a19aa6ba85f3ec78be6c77ed0d185c3ae1` - Local-only preflight gate before public demo video recording/upload approval.
- `reports/latest_public_video_upload_preflight.json` (present, required) - size=4385 sha256=`4017674b7c517e0adefdfbb5b3e52d79943bbc7ab23dc7b62410352cdd9aef4d` - Machine-readable public video approval phrase, manual confirmation, and safe-readback gate.
- `reports/latest_public_video_upload_preflight.md` (present, required) - size=1396 sha256=`234603c22d7b26c84b78925e9a24c8a279c9d2fb81fdc89ddc963ce73674df0b` - Reviewable public video upload preflight gate summary.
- `reports/latest_public_artifact_url_readback.html` (present, required) - size=3865 sha256=`8a114fb32881551703d909a66ad868741b1c8410928f83b1bb08ef1515cb66bd` - Post-publication repository/video URL readback gate before approved URL writeback.
- `reports/latest_public_artifact_url_readback.json` (present, required) - size=3104 sha256=`87bc61f92d5b2160df209e824659c4a72d236cb1c71a781f87d13de53325dcc4` - Machine-readable public URL shape/readback status and writeback readiness.
- `reports/latest_public_artifact_url_readback.md` (present, required) - size=1351 sha256=`6bb5fd11799b2384afe67bb60c33a0901f9c3d34fcb80cbd85dcdbb0a29b802a` - Reviewable public URL readback summary.
- `reports/latest_url_writeback_dry_run.html` (present, required) - size=7905 sha256=`79e9bbca8815c6b6d430d87c806e04fd18422c1887785df4ed2021a2a934f0ce` - Temporary-copy rehearsal for approved URL writeback and final-submit state changes.
- `reports/latest_url_writeback_dry_run.json` (present, required) - size=6763 sha256=`acbba19ddbb87da9371d2478b2beba2fcd9e92ef5682e58735bc82cde0935de0` - Machine-readable URL writeback rehearsal status and working-tree write guard.
- `reports/latest_url_writeback_dry_run.md` (present, required) - size=4294 sha256=`9e19a814984f7a4f085b8e69760c0548393c3c0d34e638db3058b57489f429db` - Reviewable URL writeback rehearsal summary.
- `README.md` (present, required) - size=23654 sha256=`e48c7427f33c5f013ddbc9e8409d50577b98a4b1cb5590b6235e3f316bd11f86` - Portable project overview and local run instructions.
- `LICENSE` (present, required) - size=11358 sha256=`c95bae1d1ce0235ecccd3560b772ec1efb97f348a79f0fbe0a634f0c2ccefe2c` - Open-source license candidate for public review.
- `architecture_diagram.md` (present, required) - size=1912 sha256=`b3b0f36a0d1e0a3bdd8d45c926e0d5fb6fff5ca9791c95d8fd90a6d9a3fd454b` - Root architecture evidence required by the submission packet.
- `assets/dashboard_preview.png` (present, required) - size=75210 sha256=`a172e0fa0fcaa2b4bb0a96b7b02c5bd326b37dbf26d5c4130010f54579df6142` - Visual README/Devpost preview asset.
- `prototype/agentops_control_tower.py` (present, required) - size=36533 sha256=`fce2f1c75eb25f4dfab60c57bfbbcbc9b0e126840b5672d9bfecbf070f5b871b` - Generator for synthetic checkout-incident events, analysis, dashboard, and SPL examples.
- `data/splunk_agentops_events.csv` (present, required) - size=8368 sha256=`3bb781d0e8859b52b5dd6676b35b8d051b9d2c355cec05bcb5ae2f85b5aa5a6e` - Synthetic data export for a future agentops_events index after approval.
- `submission/SPL_QUERIES.md` (present, required) - size=1783 sha256=`feb15f47a2498d4f54a2cc0ae0e41767c0c6100ebdcb6dcc2f4989651920e02a` - Reviewer-facing SPL examples for the Control Tower flow.
- `splunk_app/agentops_control_tower/default/indexes.conf` (present, required) - size=212 sha256=`4e966767e2b53e1c45102702824549f04d785e32052d0692c0f1f3410c2e9ffd` - Optional local index definition for agentops_events.
- `splunk_app/agentops_control_tower/default/props.conf` (present, required) - size=217 sha256=`6c6e3704dbd785b9fc52526b3c5fe429ac5648982d5347fce226d087fc6b024d` - CSV extraction and timestamp parsing for the agentops:events sourcetype.
- `dist/agentops-control-tower-splunk-app.spl` (present, required) - size=2409 sha256=`fdad475534452d6175dcb69d77e4a5ef9effb5c8aac94d0dbfcf864387db9e4f` - Local .spl package candidate; not installed or uploaded.
- `reports/latest_splunk_app_package_manifest.html` (present, required) - size=3767 sha256=`f4170fac331594750797aa5f3d45d539ea7fdf5efc275349a969d402fcc9fbf1` - Members, SHA256, and package boundary evidence.
- `reports/latest_splunk_app_package_manifest.json` (present, required) - size=2255 sha256=`76ce27eda837e3b98e7a1189414203d3a0c4270ad5850ee8daae3bda11bd563f` - Machine-readable .spl integrity evidence.
- `reports/latest_splunk_mcp_command_plan.html` (present, required) - size=7990 sha256=`5b7a5ab9a96b76ec531a24fe7658c54b1237b11529dd184acb502fbc70825d17` - Post-approval live Splunk/MCP setup and proof command plan.
- `reports/latest_splunk_mcp_proof_brief.html` (present, required) - size=9389 sha256=`0c3eba6257d8df6f8c583d015810641195866b2b33b81ebab82981f40e72fe60` - Success criteria, screen safety, stop conditions, and claim-upgrade rules for optional live proof.
- `reports/latest_splunk_mcp_prompt_pack.html` (present, required) - size=8562 sha256=`0d5e125c91a8fdc41a376dd60065cf077bf14b84a3c4ee3c1c393e34d4165273` - Prompt-by-prompt live proof guide for evidence-backed MCP answers.
- `reports/latest_splunk_mcp_prompt_pack.json` (present, required) - size=8621 sha256=`24966ce93abe417a574b8e49165a71da9a364c9008903d3152b5e33f0787b396` - Machine-readable prompt keys, SPL, expected citations, and live-proof gates.
- `reports/latest_splunk_mcp_prompt_pack.md` (present, required) - size=6684 sha256=`670623f0393c5738863703a7d0129879ff9145ce97c911d42e7d38b2c06579e4` - Reviewable prompt pack for approved live proof capture.
- `submission/SPLUNK_MCP_PROMPT_PACK.md` (present, required) - size=6684 sha256=`670623f0393c5738863703a7d0129879ff9145ce97c911d42e7d38b2c06579e4` - Submission-side copy of the prompt pack and stop conditions.
- `reports/latest_claim_evidence_matrix.html` (present, required) - size=11003 sha256=`382ef96a03e5dd123df08fe7243e733101e04a368f9f97f036db5b2c41e41c1e` - Allowed wording, avoid wording, evidence, and remaining gates.
- `reports/latest_claim_evidence_matrix.json` (present, required) - size=11982 sha256=`8de8d093d63effb959db077b8a2f6f2cd3ed2aac97884a21e97f53de5aaeb0a1` - Machine-readable claim support status.
- `reports/latest_submission_gate_ledger.html` (present, required) - size=9113 sha256=`ed0c4fc28c3a3f9cacb0e7369ba13bf07aaaf2a889ec4d5dc422532a5a224041` - Approval-gate ledger for public repo, video, live proof, and Devpost.
- `reports/latest_submission_deadline_burndown.html` (present, required) - size=10564 sha256=`05ad198b89e2f14d60ab0f25748a10f2788271443cb821c30a433e3b870b15bc` - Deadline-aware path for public repo, video, optional live proof, URL writeback, and Devpost final submit.
- `reports/latest_submission_deadline_burndown.json` (present, required) - size=7524 sha256=`7e68e00cd939e8f2cbd800e2f52b40e1050fbbdc374b7633c3313c79e79674cf` - Machine-readable target date, official deadline, milestones, and blocked final submit gate.
- `reports/latest_submission_deadline_burndown.md` (present, required) - size=5114 sha256=`c9d819f0a6b879a49304c3f9718bc7c4c08bfb4d928c852771aa684e206a0680` - Reviewable deadline burndown for local launch planning.
- `submission/SUBMISSION_DEADLINE_BURNDOWN.md` (present, required) - size=5114 sha256=`c9d819f0a6b879a49304c3f9718bc7c4c08bfb4d928c852771aa684e206a0680` - Submission-side copy of the deadline burndown and approval timing path.
- `reports/latest_next_approval_packet.html` (present, required) - size=15312 sha256=`02b30d4584a9360bb6010c8f2336f63d7f758093d7b2ea4d2b276eff9959b535` - Next user approval target, approval phrases, risks, and verification steps.
- `reports/latest_next_approval_packet.json` (present, required) - size=13399 sha256=`16f5198cbdf8d4e997af80fd9b52396ae61a1318ae37ae40e34fc42ac281e471` - Machine-readable next approval status and human-confirmation gates.
- `submission/NEXT_APPROVAL_PACKET.md` (present, required) - size=9704 sha256=`ea6731ecafb3a456582b5eeed4ecf2aaa30821c5ce3519e6921e563774ecf85d` - Markdown copy of the next approval packet for final user decision support.
- `reports/latest_approval_consistency_audit.html` (present, required) - size=6218 sha256=`45b5e60f441a1c9073947680c33ee1509db27e1931e961965f2abbcb06f69473` - Checks approval order consistency across plan, approval gates, launch brief, next packet, and validator state.
- `reports/latest_approval_consistency_audit.json` (present, required) - size=5424 sha256=`ab03f93fc5f633d30bb1ef663bae279d63d7639f53611950e4ed48500fbcaa4b` - Machine-readable approval-order consistency status.
- `reports/latest_status_conflict_audit.html` (present, optional) - size=51684 sha256=`e7286789ef547fb84c09de79e6f151fc9a78ba499b213fac7e2534e4edf09404` - Scans root and public-candidate JSON reports for stale failed statuses or missing local artifacts.
- `reports/latest_status_conflict_audit.json` (present, optional) - size=55419 sha256=`c2fe68e68cb38c54c1e8ccad7fbb663e050a0340ebb8880778aab0b9203563fb` - Machine-readable status conflict scan and critical ready-state checks.
- `reports/latest_status_conflict_audit.md` (present, optional) - size=31480 sha256=`d1a424078f014843234ba3846d7670860dd1a02018b2cd0f88ca8ca2dee83621` - Reviewable status conflict audit summary.
- `reports/latest_public_launch_snapshot.html` (present, required) - size=9569 sha256=`19b1c0028983cbe434c2ec7e694ec16836cc3deb71fa1ed5223c52d94dc1cdc3` - Frozen local snapshot for public repo and demo video approval review.
- `reports/latest_public_launch_snapshot.json` (present, required) - size=9619 sha256=`015a809f9719555e63442f6cdf4be87e90cddebeb4356af1a424d5e0b1dfdaa7` - Machine-readable public launch readiness, ZIP hash, approval phrases, and remaining gates.
- `reports/latest_public_launch_snapshot.md` (present, required) - size=5089 sha256=`7ea0b478fc5a4439ee330e50c3aecac35864a1e04bf16db71696f6602d9ff97f` - Reviewable public launch snapshot for copy/paste and audit.
- `reports/latest_public_repo_metadata.html` (present, required) - size=6278 sha256=`de897447d6b3749f7f552a30bd33aacf3e552e7f1a048b5e11aa9f16e357b316` - GitHub repository name, description, topics, expected readback, and no-publish boundary.
- `reports/latest_public_repo_metadata.json` (present, required) - size=4012 sha256=`43fa24797aa22c9146f09e7a821e98dea1748b45826f9245086230026a55fa8f` - Machine-readable public repository metadata and post-approval readback expectations.
- `reports/latest_public_repo_metadata.md` (present, required) - size=3087 sha256=`edcdea3c4b35bcfd9356ea80fd508e7ab102af0fc515beb02068c09614e40b48` - Reviewable public repository metadata packet.
- `submission/PUBLIC_REPO_METADATA.md` (present, required) - size=3087 sha256=`edcdea3c4b35bcfd9356ea80fd508e7ab102af0fc515beb02068c09614e40b48` - Submission-side copy of public repository metadata and stop conditions.
- `submission/USER_APPROVAL_GATES.md` (present, required) - size=1637 sha256=`38bbcc3aac49b272690152682046ebe590121d842b3c91f60dfe7eaba41524f6` - Human approval boundaries and current recommended approval order.
- `READY_FOR_REVIEW.md` (present, required) - size=926 sha256=`c59ec778e432c805f62e6df69b2da5c296da0d8fd38582cf87cffdd026820a93` - Shortest local review entrypoint for the current SPAK packet.
- `reports/latest_judge_review_packet.html` (present, required) - size=4577 sha256=`52ffd6e9f056c972dda8887fe5678ddc01219f355d8d914ed0694ee96d8776a6` - Judge-facing local packet with readiness, evidence, and closed external gates.
- `reports/latest_judge_review_packet.json` (present, required) - size=3608 sha256=`8c6c5e8641f86f5e99ab7ebbc079c88308f77cf5deb342e7b588531c97fab880` - Machine-readable SPAK judge packet status.
- `reports/latest_judge_review_packet.md` (present, required) - size=2423 sha256=`e744d4c141a4f0043564ca368c85e55afe3f03831df574e264070db020548c4c` - Reviewable SPAK judge packet summary.
- `submission/JUDGE_REVIEW_PACKET.md` (present, required) - size=2423 sha256=`e744d4c141a4f0043564ca368c85e55afe3f03831df574e264070db020548c4c` - Submission-side copy of the local judge review packet.
- `reports/latest_local_readiness_baseline.html` (present, required) - size=3874 sha256=`a909593f8549cfbcd66e8df5673e9a72fd21076438f74881cc1cf64c654efe18` - Targeted pass/fail baseline for local package/proof readiness.
- `reports/latest_local_readiness_baseline.json` (present, required) - size=3023 sha256=`3cedeb9578ab493b49b315f0209fbbc99fdc5d10fc56c45dc69a8c3454cfa44f` - Machine-readable targeted local readiness baseline.
- `reports/latest_local_readiness_baseline.md` (present, required) - size=1554 sha256=`823cedb98c5e78260a8f4a76cb8bca37c4c0c33965f553ae94aa19039e86eb14` - Reviewable targeted local readiness baseline.
- `reports/latest_public_candidate_local_audit.html` (present, required) - size=3474 sha256=`05addf6bbad2f28c2087435e4d78c538de076c4559ab15c4d6e82b88a29012de` - Secret/internal-path and completeness audit for the public repo candidate.
- `reports/latest_public_candidate_local_audit.json` (present, required) - size=2097 sha256=`9fc286fd1367ca129986f137257c66a471e7c2d466dd04d1bb19074f04675383` - Machine-readable public candidate safety audit.
- `reports/latest_public_candidate_local_audit.md` (present, required) - size=1203 sha256=`f7c056bcdb544c1d4711b59a8502ccc8b5537396abce089291c12c8b0a04387c` - Reviewable public candidate safety audit.
- `reports/latest_devpost_copy_audit.html` (present, required) - size=3361 sha256=`841ead8acb9c78696e196cf67ce57cf94a4a63b4cada8e3ea2ae224df910aa27` - Local audit of Devpost copy readiness with final submission still gated.
- `reports/latest_devpost_copy_audit.json` (present, required) - size=1991 sha256=`8a72bc9d0c7837e5494effd4254667e1f26759a78359f24ab83799498153a397` - Machine-readable Devpost copy audit.
- `reports/latest_devpost_copy_audit.md` (present, required) - size=1102 sha256=`c4afcad0d6ab236c9ad25baa214cfa8aa29f0c1e716a5c3cddb8f79ca40b46bd` - Reviewable Devpost copy audit.
- `reports/latest_judge_quickstart.html` (present, required) - size=9733 sha256=`87dfd46d941df1726c7ebb2b4191fe0f03c1e2b9d3ded2759379dbeec3dfc12f` - Five-minute review path for judges and final preflight.
- `reports/latest_devpost_final_copy.md` (present, required) - size=9125 sha256=`704b1a700f730c6d8cb8ff8726b9a86e5f968be27e2791668752f1224203cdc7` - Copy/paste packet with pending public URL placeholders.
- `reports/latest_post_action_evidence_brief.html` (present, required) - size=10260 sha256=`882f46867914bcbb3b0ed25764bda94bb85f7ac89a867fda94a7641e8b8a806f` - Readback plan after approved external actions.
- `reports/latest_post_action_evidence_brief.json` (present, required) - size=8853 sha256=`b025b35db519df3ff7bb9636f2ff24a792327fefd49bf04574ece14d68fe0808` - Machine-readable post-action gate state.
- `submission/POST_ACTION_EVIDENCE_LOG_TEMPLATE.md` (present, required) - size=7393 sha256=`f35de1a10121305df6bc05c184d5855101beaeb186f62a2ceb48bf8e103a248c` - Template for safe readback after approved external actions.
- `reports/latest_splunk_mcp_proof_capture_manifest.html` (present, required) - size=10144 sha256=`f3adcdb168c03a1149c37bec13c6b88e9adb63e44fcaffc142306387f8a12379` - Live Splunk/MCP proof capture slots, expected readback, stop conditions, and claim-upgrade gate.
- `reports/latest_splunk_mcp_proof_capture_manifest.json` (present, required) - size=8510 sha256=`2058268ab75c5023ea252a557757d1ee5b072041ce98c3eee3e623603c493b71` - Machine-readable live Splunk/MCP proof capture gate state.
- `reports/latest_splunk_mcp_proof_capture_manifest.md` (present, required) - size=6488 sha256=`14fb6c97a587edf8758e9fb3c4bc169801e620cfdc6ae61aff4e2243c1bcdccf` - Reviewable live Splunk/MCP proof capture manifest.
- `submission/SPLUNK_MCP_PROOF_CAPTURE_MANIFEST.md` (present, required) - size=6488 sha256=`14fb6c97a587edf8758e9fb3c4bc169801e620cfdc6ae61aff4e2243c1bcdccf` - Submission-side copy of the proof capture manifest and no-live-proof boundary.
- `reports/latest_official_source_freshness.html` (present, required) - size=6399 sha256=`c8b9c27dac1a204aa0a7c58fcd8be5b26ffc60c28d13dbc526c4a6404885b894` - Current official Devpost source and requirement freshness evidence.
- `reports/latest_official_source_freshness.json` (present, required) - size=7719 sha256=`02bd4314ac8a80ce56d03378ccd281522b83c503b9ad4a825ab5ce0772c49136` - Machine-readable official source freshness and local mapping status.
- `reports/latest_content_rights_audit.html` (present, required) - size=4886 sha256=`9d23cbe82972acd73d2f7788b72c3254f3692b95cd98f534504b15a032aaa001` - License, bundled asset, audio/video, and screen-safety evidence.
- `reports/latest_content_rights_audit.json` (present, required) - size=3625 sha256=`85e4a998eb553a02c1aa6b07190ef226a71ec7c7b11ac47e32c0815688d9f017` - Machine-readable content rights and asset safety status.
- `reports/latest_eligibility_compliance_audit.html` (present, required) - size=7816 sha256=`31a902f83f5962ade79ab94f2525a80985a37d3a634f6eec78bb26b1bedbbcf5` - Eligibility, ownership, language, uniqueness, and human-confirmation evidence.
- `reports/latest_eligibility_compliance_audit.json` (present, required) - size=6320 sha256=`1a5ff8b5a9765f010349636de65057f34d56ac50f104c1713e1f487a232ae705` - Machine-readable eligibility and compliance status.

## Publication Boundary

This release integrity manifest is local readback evidence only. It does not publish, upload, connect to Splunk, configure MCP, write approved URLs, update Devpost, or submit anything.
