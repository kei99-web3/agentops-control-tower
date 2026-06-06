from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_NAME = "agentops-control-tower"
PUBLIC_CANDIDATE = "public_repo_candidate/agentops-control-tower"
APPROVAL_PHRASE = "Approve public GitHub publication for the clean agentops-control-tower candidate."
COMMIT_MESSAGE = "Initial Agentic Incident Command Center submission"
DESCRIPTION = "Splunk-ready safety and incident intelligence for autonomous AI agent operations."
LICENSE = "Apache-2.0"
DEFAULT_BRANCH = "main"
TOPICS = [
    "splunk",
    "agentops",
    "ai-agents",
    "observability",
    "mcp",
    "safety",
    "incident-response",
    "splunk-mcp",
    "autonomous-agents",
    "hackathon",
]
BOUNDARY = (
    "Default mode is a local rehearsal only. Public GitHub creation and push require --execute, "
    "the exact approval phrase, and explicit public git identity arguments."
)
PLACEHOLDER_GIT_IDENTITY_TOKENS = {
    "<approved-public-git-name>",
    "<approved-public-git-email>",
    "approved-public-git-name",
    "approved-public-git-email",
}

TEXT_SUFFIXES = {
    ".conf",
    ".csv",
    ".html",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".xml",
}

INTERNAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"C:\\" + "Users",
        "PC" + "_User",
        r"Desktop\\" + "AI" + "_" + "Workspace",
        "AI" + "_" + "Workspace",
        r"\." + "com" + "pany",
        "private " + "workspace tree",
    ]
]

SECRET_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"ghp_[A-Za-z0-9]{20,}",
        r"sk-[A-Za-z0-9]{20,}",
        r"xox[baprs]-[A-Za-z0-9-]{20,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"AKIA[0-9A-Z]{16}",
        r"token=[A-Za-z0-9._~+/=-]{12,}",
        r"api[_-]?key=[A-Za-z0-9._~+/=-]{12,}",
    ]
]

ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/][^\n\r\"']+")

REQUIRED_FILES = [
    ".gitattributes",
    "README.md",
    "LICENSE",
    "PUBLIC_REPO_CANDIDATE_MANIFEST.md",
    "architecture_diagram.md",
    "prototype/agentops_control_tower.py",
    "scripts/validate_submission_packet.py",
    "scripts/publish_public_repo_after_approval.py",
    "scripts/build_public_repo_metadata.py",
    "reports/latest_public_repo_metadata.json",
    "reports/latest_public_repo_publish_brief.json",
    "reports/latest_public_launch_snapshot.json",
    "reports/latest_submission_url_validation.json",
    "submission/PUBLIC_REPO_METADATA.md",
    "submission/USER_APPROVAL_GATES.md",
]

LOCAL_ONLY_GENERATED = [
    "release",
    "reports/latest_public_candidate_zip_manifest.html",
    "reports/latest_public_candidate_zip_manifest.json",
    "reports/latest_public_repo_dry_run.html",
    "reports/latest_public_repo_dry_run.json",
    "reports/latest_public_repo_dry_run.md",
    "reports/latest_video_dry_run.html",
    "reports/latest_video_dry_run.json",
    "reports/latest_video_dry_run.md",
    "reports/latest_url_writeback_dry_run.html",
    "reports/latest_url_writeback_dry_run.json",
    "reports/latest_url_writeback_dry_run.md",
]


@dataclass
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def sanitize(value: str) -> str:
    return ABSOLUTE_PATH_PATTERN.sub("<local-path>", value)


def compact(value: str, limit: int = 1200) -> str:
    return value[-limit:] if value else "no output"


def add_check(checks: list[Check], name: str, condition: bool, detail: str) -> None:
    checks.append(Check(name=name, status="pass" if condition else "fail", detail=sanitize(detail)))


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def is_public_candidate_root(root: Path) -> bool:
    return (root / "PUBLIC_REPO_CANDIDATE_MANIFEST.md").exists()


def candidate_source(root: Path) -> Path:
    return root if is_public_candidate_root(root) else root / PUBLIC_CANDIDATE


def private_workspace_root(root: Path) -> Path:
    workspace_name = "AI" + "_Workspace"
    for candidate in [root, *root.parents]:
        if candidate.name == workspace_name:
            return candidate
    return root


def safe_stage_root(value: str | None) -> Path:
    temp_root = Path(tempfile.gettempdir()).resolve()
    stage_root = (Path(value) if value else Path(tempfile.mkdtemp(prefix="agentops-control-tower-public-stage-"))).resolve()
    stage_root.relative_to(temp_root)
    if stage_root == temp_root:
        raise ValueError("stage root must be a child of the system temp directory")
    return stage_root


def remove_readonly(func: Any, path: str, _exc_info: Any) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


def reset_stage_root(stage_root: Path) -> None:
    temp_root = Path(tempfile.gettempdir()).resolve()
    stage_root = stage_root.resolve()
    stage_root.relative_to(temp_root)
    if stage_root.exists() and any(stage_root.iterdir()):
        shutil.rmtree(stage_root, onerror=remove_readonly)
    stage_root.mkdir(parents=True, exist_ok=True)


def copy_candidate(source: Path, target: Path) -> None:
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )


def cleanup_local_only_generated(root: Path) -> list[str]:
    removed: list[str] = []
    resolved_root = root.resolve()
    for rel_path in LOCAL_ONLY_GENERATED:
        path = (root / rel_path).resolve()
        path.relative_to(resolved_root)
        if not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        removed.append(rel_path)
    return removed


def scan_text(root: Path) -> tuple[list[str], list[str]]:
    internal_hits: list[str] = []
    secret_hits: list[str] = []
    for path in root.rglob("*"):
        if path.is_dir() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel_path = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            secret_hits.append(f"non_utf8:{rel_path}")
            continue
        for pattern in INTERNAL_PATTERNS:
            if pattern.search(text):
                internal_hits.append(f"{rel_path}:{pattern.pattern}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append(f"{rel_path}:{pattern.pattern}")
    return internal_hits, secret_hits


def run_command(args: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    output = (completed.stdout + "\n" + completed.stderr).strip()
    return completed.returncode, sanitize(output)


def run_git(args: list[str], cwd: Path) -> tuple[int, str]:
    return run_command(["git", *args], cwd)


def parse_json_output(output: str) -> dict[str, Any]:
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {}


def default_branch_name(readback: dict[str, Any]) -> str:
    value = readback.get("defaultBranchRef")
    if isinstance(value, dict):
        return str(value.get("name", ""))
    return str(value or "")


def license_spdx(readback: dict[str, Any]) -> str:
    value = readback.get("licenseInfo")
    if isinstance(value, dict):
        return str(value.get("spdxId") or value.get("key") or value.get("name") or "")
    return str(value or "")


def topic_names(readback: dict[str, Any]) -> set[str]:
    value = readback.get("repositoryTopics")
    names: set[str] = set()
    if isinstance(value, dict):
        nodes = value.get("nodes", [])
        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node, dict):
                    topic = node.get("topic")
                    if isinstance(topic, dict) and topic.get("name"):
                        names.add(str(topic["name"]))
                    elif node.get("name"):
                        names.add(str(node["name"]))
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                names.add(item)
            elif isinstance(item, dict):
                if item.get("name"):
                    names.add(str(item["name"]))
                elif isinstance(item.get("topic"), dict) and item["topic"].get("name"):
                    names.add(str(item["topic"]["name"]))
    return names


def public_safe_readback(
    args: argparse.Namespace,
    *,
    status: str,
    failed_count: int,
    external_attempted: bool,
    external_completed: bool,
    commit: dict[str, Any] | None = None,
    publication: dict[str, Any] | None = None,
    missing_execute_inputs: list[str] | None = None,
    invalid_execute_inputs: list[str] | None = None,
) -> dict[str, Any]:
    publication = publication or {}
    readback = parse_json_output(str(publication.get("readback", "")))
    return {
        "action_key": "public_github_repository",
        "status": status,
        "mode": "execute" if args.execute else "rehearsal",
        "repo_name": args.repo_name,
        "approval_phrase_accepted": args.approval_phrase == APPROVAL_PHRASE,
        "external_actions_attempted": external_attempted,
        "external_actions_completed": external_completed,
        "missing_execute_inputs": missing_execute_inputs or [],
        "invalid_execute_inputs": invalid_execute_inputs or [],
        "failed_count": failed_count,
        "git_commit_sha": str((commit or {}).get("git_commit_sha", "")),
        "repository_readback": {
            "url": str(readback.get("url", "")),
            "visibility": str(readback.get("visibility", "")),
            "is_private": readback.get("isPrivate", None),
            "default_branch": default_branch_name(readback),
            "license": license_spdx(readback),
            "topics": sorted(topic_names(readback)),
        },
        "evidence_note_target": "submission/post_action_evidence/YYYY-MM-DD_public_github_repository_readback.md",
        "copy_policy": (
            "Use this public_safe_readback block for post-action evidence. Do not copy stage_root, "
            "audit_stage, publish_stage, raw command output, credentials, tokens, or local absolute paths."
        ),
    }


def is_placeholder_git_identity(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        normalized in PLACEHOLDER_GIT_IDENTITY_TOKENS
        or normalized.startswith("<")
        or normalized.endswith(">")
        or "approved-public-git-" in normalized
    )


def validate_public_git_identity(name: str, email: str) -> list[str]:
    issues: list[str] = []
    if name and is_placeholder_git_identity(name):
        issues.append("--git-user-name must be a real public git identity, not <approved-public-git-name>")
    if email and is_placeholder_git_identity(email):
        issues.append("--git-user-email must be a real public git email, not <approved-public-git-email>")
    elif email and "@" not in email:
        issues.append("--git-user-email must include @")
    return issues


def init_main_branch(root: Path) -> tuple[int, str]:
    init_code, init_output = run_git(["init", "-b", "main"], root)
    if init_code == 0:
        return init_code, init_output
    fallback_code, fallback_output = run_git(["init"], root)
    checkout_code, checkout_output = run_git(["checkout", "-b", "main"], root)
    combined = "\n".join(part for part in [init_output, fallback_output, checkout_output] if part)
    return (0 if fallback_code == 0 and checkout_code == 0 else 1), combined


def validate_execute_args(args: argparse.Namespace) -> dict[str, Any] | None:
    if not args.execute:
        return None
    missing = []
    if args.approval_phrase != APPROVAL_PHRASE:
        missing.append("exact approval phrase")
    if not args.git_user_name:
        missing.append("--git-user-name")
    if not args.git_user_email:
        missing.append("--git-user-email")
    invalid = validate_public_git_identity(args.git_user_name, args.git_user_email)
    if missing or invalid:
        status = "blocked_by_approval_gate"
        return {
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "status": status,
            "mode": "execute",
            "failed_count": 1,
            "external_actions_attempted": False,
            "external_actions_completed": False,
            "approval_phrase_accepted": args.approval_phrase == APPROVAL_PHRASE,
            "missing_execute_inputs": missing,
            "invalid_execute_inputs": invalid,
            "public_safe_readback": public_safe_readback(
                args,
                status=status,
                failed_count=1,
                external_attempted=False,
                external_completed=False,
                missing_execute_inputs=missing,
                invalid_execute_inputs=invalid,
            ),
            "boundary": BOUNDARY,
        }
    return None


def audit_stage(stage: Path, checks: list[Check]) -> None:
    dry_run_code, dry_run_output = run_command([sys.executable, "scripts/build_public_repo_dry_run.py", "--root", str(stage)], stage)
    add_check(checks, "audit-stage public repo dry run", dry_run_code == 0, compact(dry_run_output))
    code, output = run_command([sys.executable, "scripts/validate_submission_packet.py", "--root", str(stage)], stage)
    add_check(checks, "audit-stage validation", code == 0, compact(output))


def prepare_publish_commit(
    stage: Path,
    checks: list[Check],
    *,
    git_user_name: str,
    git_user_email: str,
) -> dict[str, Any]:
    init_code, init_output = init_main_branch(stage)
    add_check(checks, "git init publish stage", init_code == 0, compact(init_output))
    name_code, name_output = run_git(["config", "user.name", git_user_name], stage)
    add_check(checks, "git user.name configured", name_code == 0, compact(name_output))
    email_code, email_output = run_git(["config", "user.email", git_user_email], stage)
    add_check(checks, "git user.email configured", email_code == 0, compact(email_output))
    add_code, add_output = run_git(["add", "-A"], stage)
    add_check(checks, "git add publish stage", add_code == 0, compact(add_output))
    status_code, status_output = run_git(["status", "--short"], stage)
    status_lines = [line for line in status_output.splitlines() if line.strip()]
    add_check(checks, "git status publish stage has files", status_code == 0 and len(status_lines) >= 100, f"{len(status_lines)} staged files")
    commit_code, commit_output = run_git(["commit", "-m", COMMIT_MESSAGE], stage)
    add_check(checks, "git commit publish stage", commit_code == 0, compact(commit_output))
    rev_code, rev_output = run_git(["rev-parse", "--short=12", "HEAD"], stage)
    commit_sha = rev_output.strip()
    add_check(checks, "git commit hash exists", rev_code == 0 and bool(commit_sha), commit_sha or "missing")
    post_status_code, post_status_output = run_git(["status", "--short"], stage)
    post_status_lines = [line for line in post_status_output.splitlines() if line.strip()]
    add_check(checks, "git post-commit status clean", post_status_code == 0 and not post_status_lines, compact(post_status_output) if post_status_lines else "clean")
    remote_code, remote_output = run_git(["remote"], stage)
    add_check(checks, "no remote before execute", remote_code == 0 and not remote_output.strip(), compact(remote_output) if remote_output.strip() else "no remotes")
    return {
        "git_status_line_count": len(status_lines),
        "git_post_commit_status_line_count": len(post_status_lines),
        "git_commit_sha": commit_sha,
        "git_commit_created": commit_code == 0 and rev_code == 0,
    }


def execute_publication(stage: Path, checks: list[Check], repo_name: str) -> dict[str, Any]:
    namespace_code, namespace_output = run_command(
        [
            "gh",
            "repo",
            "view",
            repo_name,
            "--json",
            "nameWithOwner,visibility,url,isPrivate",
        ],
        stage,
    )
    namespace_exists = namespace_code == 0 and '"nameWithOwner"' in namespace_output
    add_check(
        checks,
        "gh repo namespace precheck",
        not namespace_exists,
        compact(namespace_output) if namespace_exists else "no readable existing repository; gh repo create remains authoritative",
    )
    if namespace_exists:
        add_check(checks, "gh public repo create", False, "skipped because target repository namespace already resolves")
        add_check(checks, "git push public repo", False, "skipped because target repository namespace already resolves")
        add_check(checks, "gh repo topics applied", False, "skipped because target repository namespace already resolves")
        add_check(checks, "gh repo readback", False, compact(namespace_output))
        add_check(checks, "gh repo readback visibility public", False, compact(namespace_output))
        add_check(checks, "gh repo readback description", False, "skipped because target repository namespace already resolves")
        add_check(checks, "gh repo readback default branch", False, "skipped because target repository namespace already resolves")
        add_check(checks, "gh repo readback license", False, "skipped because target repository namespace already resolves")
        add_check(checks, "gh repo readback topics", False, "skipped because target repository namespace already resolves")
        return {
            "namespace_precheck_returncode": namespace_code,
            "namespace_precheck": namespace_output,
            "repo_create_returncode": None,
            "push_returncode": None,
            "topics_returncodes": {},
            "readback_returncode": namespace_code,
            "readback": namespace_output,
            "expected_metadata": {
                "description": DESCRIPTION,
                "default_branch": DEFAULT_BRANCH,
                "license": LICENSE,
                "topics": TOPICS,
            },
        }
    repo_code, repo_output = run_command(
        [
            "gh",
            "repo",
            "create",
            repo_name,
            "--public",
            "--source",
            ".",
            "--remote",
            "origin",
            "--description",
            DESCRIPTION,
        ],
        stage,
    )
    add_check(checks, "gh public repo create", repo_code == 0, compact(repo_output))
    push_code, push_output = run_git(["push", "-u", "origin", "main"], stage) if repo_code == 0 else (1, "repo create failed")
    add_check(checks, "git push public repo", push_code == 0, compact(push_output))

    topic_results: list[dict[str, Any]] = []
    if push_code == 0:
        for topic in TOPICS:
            topic_code, topic_output = run_command(["gh", "repo", "edit", repo_name, "--add-topic", topic], stage)
            topic_results.append({"topic": topic, "returncode": topic_code, "output": compact(topic_output)})
        failed_topics = [item for item in topic_results if item["returncode"] != 0]
        add_check(checks, "gh repo topics applied", not failed_topics, "; ".join(f"{item['topic']}:{item['output']}" for item in failed_topics) if failed_topics else ", ".join(TOPICS))
    else:
        add_check(checks, "gh repo topics applied", False, "push failed")

    view_code, view_output = run_command(
        [
            "gh",
            "repo",
            "view",
            repo_name,
            "--json",
            "nameWithOwner,visibility,url,description,defaultBranchRef,licenseInfo,repositoryTopics,isPrivate",
        ],
        stage,
    ) if push_code == 0 else (1, "push failed")
    add_check(checks, "gh repo readback", view_code == 0 and '"visibility"' in view_output, compact(view_output))
    readback = parse_json_output(view_output) if view_code == 0 else {}
    readback_topics = topic_names(readback)
    add_check(checks, "gh repo readback visibility public", readback.get("visibility") == "PUBLIC" and readback.get("isPrivate") is False, json.dumps(readback, ensure_ascii=False))
    add_check(checks, "gh repo readback description", readback.get("description") == DESCRIPTION, str(readback.get("description", "")))
    add_check(checks, "gh repo readback default branch", default_branch_name(readback) == DEFAULT_BRANCH, default_branch_name(readback) or "missing")
    add_check(checks, "gh repo readback license", license_spdx(readback) == LICENSE, license_spdx(readback) or "missing")
    add_check(checks, "gh repo readback topics", set(TOPICS).issubset(readback_topics), ", ".join(sorted(readback_topics)) if readback_topics else "missing")
    return {
        "namespace_precheck_returncode": namespace_code,
        "namespace_precheck": namespace_output,
        "repo_create_returncode": repo_code,
        "push_returncode": push_code,
        "topics_returncodes": {item["topic"]: item["returncode"] for item in topic_results},
        "readback_returncode": view_code,
        "readback": view_output,
        "expected_metadata": {
            "description": DESCRIPTION,
            "default_branch": DEFAULT_BRANCH,
            "license": LICENSE,
            "topics": TOPICS,
        },
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    blocked = validate_execute_args(args)
    if blocked is not None:
        return blocked

    root = Path(args.root).resolve()
    source = candidate_source(root).resolve()
    stage_root = safe_stage_root(args.stage_root)
    workspace_root = private_workspace_root(root)
    checks: list[Check] = []

    add_check(checks, "candidate source exists", source.exists(), str(source))
    add_check(checks, "candidate source is public candidate", is_public_candidate_root(source), str(source))
    add_check(checks, "stage root outside private workspace", not is_relative_to(stage_root, workspace_root), str(stage_root))
    add_check(checks, "stage root under system temp", is_relative_to(stage_root, Path(tempfile.gettempdir()).resolve()), str(stage_root))
    if any(not check.passed for check in checks):
        failed = [check for check in checks if not check.passed]
        return {
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "status": "needs_more_evidence",
            "mode": "execute" if args.execute else "rehearsal",
            "failed_count": len(failed),
            "checks": [check.__dict__ for check in checks],
            "external_actions_attempted": False,
            "external_actions_completed": False,
            "boundary": BOUNDARY,
        }

    reset_stage_root(stage_root)
    audit = stage_root / "audit" / REPO_NAME
    publish = stage_root / "publish" / REPO_NAME
    audit.parent.mkdir(parents=True, exist_ok=True)
    publish.parent.mkdir(parents=True, exist_ok=True)
    copy_candidate(source, audit)
    copy_candidate(source, publish)

    add_check(checks, "audit stage isolated", not is_relative_to(audit, workspace_root), str(audit))
    add_check(checks, "publish stage isolated", not is_relative_to(publish, workspace_root), str(publish))
    audit_stage(audit, checks)
    removed = cleanup_local_only_generated(publish)
    add_check(checks, "publish stage local-only generated cleanup", True, ", ".join(removed) if removed else "no cleanup needed")
    missing_required = [rel_path for rel_path in REQUIRED_FILES if not (publish / rel_path).exists()]
    add_check(checks, "publish stage required files", not missing_required, ", ".join(missing_required) if missing_required else "all required files present")
    add_check(checks, "publish stage has no .git before init", not (publish / ".git").exists(), ".git absent")
    add_check(checks, "approved URL writeback absent", not (publish / "submission/approved_public_urls.json").exists(), "approved_public_urls.json absent")
    internal_hits, secret_hits = scan_text(publish)
    add_check(checks, "publish stage internal path scan", not internal_hits, "\n".join(internal_hits) if internal_hits else "no internal patterns")
    add_check(checks, "publish stage secret-like scan", not secret_hits, "\n".join(secret_hits) if secret_hits else "no secret-like patterns")

    git_identity = {
        "git_user_name": args.git_user_name or "Agentic Incident Command Center Dry Run",
        "git_user_email": args.git_user_email or "agentops-control-tower@example.invalid",
    }
    commit = prepare_publish_commit(publish, checks, **git_identity)

    failed_before_external = [check for check in checks if not check.passed]
    publication: dict[str, Any] = {
        "repo_create_returncode": None,
        "push_returncode": None,
        "readback_returncode": None,
        "readback": "",
    }
    external_attempted = False
    if args.execute and not failed_before_external:
        external_attempted = True
        publication = execute_publication(publish, checks, args.repo_name)

    failed = [check for check in checks if not check.passed]
    status = "published_pending_readback_use" if args.execute and not failed else "ready_for_user_review"
    if failed:
        status = "needs_more_evidence"
    external_completed = args.execute and external_attempted and not failed
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "mode": "execute" if args.execute else "rehearsal",
        "repo_name": args.repo_name,
        "candidate_source": "." if is_public_candidate_root(root) else PUBLIC_CANDIDATE,
        "stage_root": str(stage_root),
        "audit_stage": str(audit),
        "publish_stage": str(publish),
        "approval_phrase_accepted": args.approval_phrase == APPROVAL_PHRASE,
        "external_actions_attempted": external_attempted,
        "external_actions_completed": external_completed,
        "failed_count": len(failed),
        "checks": [check.__dict__ for check in checks],
        "commit": commit,
        "publication": publication,
        "public_safe_readback": public_safe_readback(
            args,
            status=status,
            failed_count=len(failed),
            external_attempted=external_attempted,
            external_completed=external_completed,
            commit=commit,
            publication=publication,
        ),
        "boundary": BOUNDARY,
        "next_step": "Capture the public repository URL only after execute mode succeeds and GitHub readback shows PUBLIC visibility.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded public GitHub publication helper for Agentic Incident Command Center.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--stage-root", default=None)
    parser.add_argument("--repo-name", default=REPO_NAME)
    parser.add_argument("--execute", action="store_true", help="Actually create and push the public GitHub repository after all guards pass.")
    parser.add_argument("--approval-phrase", default="", help="Must exactly match the public repo approval phrase when --execute is used.")
    parser.add_argument("--git-user-name", default="", help="Public git author name to set in the isolated staging repository.")
    parser.add_argument("--git-user-email", default="", help="Public git author email to set in the isolated staging repository.")
    args = parser.parse_args()

    try:
        payload = build_payload(args)
    except Exception as exc:
        payload = {
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "status": "needs_more_evidence",
            "mode": "execute" if args.execute else "rehearsal",
            "failed_count": 1,
            "external_actions_attempted": False,
            "external_actions_completed": False,
            "error": sanitize(str(exc)),
            "boundary": BOUNDARY,
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if payload["status"] == "blocked_by_approval_gate":
        return 2
    return 0 if payload.get("failed_count") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
