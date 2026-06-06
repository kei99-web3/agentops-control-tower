# Splunk App Package Manifest

Status: ready_for_user_review
Package: dist/agentops-control-tower-splunk-app.spl
Size bytes: 2409
SHA256: 8817972eb99d06d0cbfd8dffd2de4c758a0f41cf867ed65816ddfd817f2ea2e6

## Boundary

This local package is not installed, uploaded, published, connected to Splunk, or submitted anywhere.

## Checks

- Splunk app source files: pass (7 source files present)
- Splunk app package size: pass (bytes=2409)
- Splunk app package path traversal guard: pass (no unsafe member names)
- Splunk app package root folder: pass (agentops_control_tower)
- Splunk app package required members: pass (7 required members present)
- Splunk app package member count: pass (members=7 expected=7)
- Splunk app internal path scan: pass (no internal patterns)
- Splunk app secret-like scan: pass (no secret-like patterns)
- packaged app label: pass (ui.label checked)
- packaged app id: pass (package.id checked)
- packaged dashboard XML parses: pass (root=form)

## Members

- `agentops_control_tower/README.md`
- `agentops_control_tower/default/app.conf`
- `agentops_control_tower/default/data/ui/views/agentops_control_tower.xml`
- `agentops_control_tower/default/indexes.conf`
- `agentops_control_tower/default/props.conf`
- `agentops_control_tower/default/savedsearches.conf`
- `agentops_control_tower/metadata/default.meta`