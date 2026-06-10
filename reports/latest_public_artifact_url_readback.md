# Public Artifact URL Readback

Status: ready_for_url_writeback_after_user_approval
Live readback attempted: true
Ready for URL writeback: true

## URLs

- Repository: https://github.com/kei99-web3/agentops-control-tower
- Demo video: https://youtu.be/6hed52sP_XU

## Public-Safe Readback

- Evidence note target: submission/post_action_evidence/YYYY-MM-DD_approved_url_writeback_readback.md
- Copy policy: Use this public_safe_readback block for post-action evidence. Do not copy raw command output, credentials, tokens, account screenshots, browser tabs, or local absolute paths.
- Repository visibility: PUBLIC
- Demo video host/status: www.youtube.com / 200

## Checks

- pass: shape: repository URL - valid public repository URL shape
- pass: shape: demo video URL - valid public video URL shape
- pass: shape: repository approval gate - pending or approved URL supplied
- pass: shape: video approval gate - pending or approved URL supplied
- pass: approved URL file remains absent - approved_public_urls.json absent
- pass: GitHub repository URL path - kei99-web3/agentops-control-tower
- pass: GitHub repository readback - {"isPrivate":false,"nameWithOwner":"kei99-web3/agentops-control-tower","url":"https://github.com/kei99-web3/agentops-control-tower","visibility":"PUBLIC"}
- pass: GitHub repository visibility public - {"isPrivate": false, "nameWithOwner": "kei99-web3/agentops-control-tower", "url": "https://github.com/kei99-web3/agentops-control-tower", "visibility": "PUBLIC"}
- pass: Demo video URL HTTP readback - {"method": "HEAD", "status_code": 200, "final_url": "https://www.youtube.com/watch?v=6hed52sP_XU&feature=youtu.be", "content_type": "text/html; charset=utf-8", "error": ""}
- pass: Demo video URL remains on allowed host - www.youtube.com

## Boundary

This public artifact URL readback is a verification aid only. Default mode does not perform network readback when URLs are still pending. It does not publish, upload, write approved URLs, update Devpost, or submit anything.
