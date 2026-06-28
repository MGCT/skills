#!/usr/bin/env python3
"""Scan a git repo's pending changes for things that should not be committed.

Looks at staged changes, unstaged-but-tracked changes, and untracked files, and
flags likely secrets, oversized files, and Jupyter notebooks committed with their
output cells intact. Pure standard library; works anywhere git and Python 3.8+ run.

Usage:
    python scan_staged.py [repo-path]      # defaults to the current directory

Exit code is 0 when nothing notable is found, 1 when there are findings (so a
caller can use it as a pre-commit gate).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# Files larger than this (bytes) are flagged as probably-not-meant-for-git.
LARGE_FILE_BYTES = 1_000_000

# Filenames / suffixes that should almost never be committed.
RISKY_NAMES = re.compile(
    r"(^|/)(\.env(\.[\w.-]+)?|\.npmrc|\.pypirc|id_rsa|id_ed25519|"
    r".*\.(pem|key|pfx|p12|keystore|jks))$",
    re.IGNORECASE,
)

# Secret patterns matched against added lines. Each is (label, compiled regex).
SECRET_PATTERNS = [
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("AWS secret access key", re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+]{40}")),
    ("OpenAI/Stripe-style key", re.compile(r"\bsk-(?:live-|test-)?[A-Za-z0-9]{16,}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("DB URL with credentials", re.compile(r"\b\w+://[^:\s/]+:[^@\s/]+@[^\s/]+")),
    ("Hardcoded secret assignment", re.compile(
        r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|auth[_-]?token|token)\b"
        r"\s*[:=]\s*['\"][^'\"]{6,}['\"]")),
]

# Lines that look like placeholders rather than real secrets — don't flag these.
PLACEHOLDER = re.compile(
    r"(?i)(your[_-]?|example|placeholder|changeme|change_me|xxxx|<[^>]+>|\bdummy\b|\bfake\b|\bredacted\b|\*{4,})"
)


def git(repo: Path, *args: str) -> str:
    """Run a git command in repo and return stdout (empty string on failure)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, check=False,
        )
        return out.stdout
    except FileNotFoundError:
        print("error: git is not installed or not on PATH", file=sys.stderr)
        sys.exit(2)


def added_lines(repo: Path) -> list[tuple[str, str]]:
    """Return (file, line) for every added line across staged + unstaged diffs."""
    results: list[tuple[str, str]] = []
    for diff_args in (["diff", "--cached"], ["diff"]):
        current = None
        for line in git(repo, *diff_args, "--unified=0").splitlines():
            if line.startswith("+++ b/"):
                current = line[6:]
            elif line.startswith("+") and not line.startswith("+++") and current:
                results.append((current, line[1:]))
    return results


def changed_and_untracked(repo: Path) -> list[str]:
    """Paths that are staged, modified, or untracked (not ignored)."""
    paths: set[str] = set()
    for line in git(repo, "status", "--porcelain").splitlines():
        if not line:
            continue
        # Format: "XY <path>" or "XY <old> -> <new>"
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.strip().strip('"'))
    return sorted(paths)


def file_size(repo: Path, rel: str) -> int:
    p = repo / rel
    try:
        return p.stat().st_size
    except OSError:
        return 0


def notebook_has_output(repo: Path, rel: str) -> bool:
    p = repo / rel
    try:
        nb = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, json.JSONDecodeError):
        return False
    for cell in nb.get("cells", []):
        if cell.get("outputs") or cell.get("execution_count") is not None:
            return True
    return False


def main() -> int:
    repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    if not (repo / ".git").exists():
        print(f"note: {repo} is not a git repository — nothing to scan.")
        return 0

    secret_hits: list[str] = []
    for rel, line in added_lines(repo):
        if PLACEHOLDER.search(line):
            continue
        for label, pat in SECRET_PATTERNS:
            if pat.search(line):
                snippet = line.strip()
                if len(snippet) > 120:
                    snippet = snippet[:117] + "..."
                secret_hits.append(f"  {rel}: {label}\n      {snippet}")
                break

    risky_files: list[str] = []
    large_files: list[str] = []
    nb_with_output: list[str] = []
    for rel in changed_and_untracked(repo):
        if RISKY_NAMES.search(rel):
            risky_files.append(f"  {rel}")
        size = file_size(repo, rel)
        if size >= LARGE_FILE_BYTES:
            large_files.append(f"  {rel} ({size/1_000_000:.1f} MB)")
        if rel.endswith(".ipynb") and notebook_has_output(repo, rel):
            nb_with_output.append(f"  {rel}")

    findings = bool(secret_hits or risky_files or large_files or nb_with_output)

    print(f"Scan of pending changes in {repo}\n" + "=" * 48)
    if secret_hits:
        print("\n[!] POSSIBLE SECRETS in added lines - do NOT commit, and rotate if real:")
        print("\n".join(secret_hits))
    if risky_files:
        print("\n[!] SENSITIVE FILES staged/changed/untracked - should usually be git-ignored:")
        print("\n".join(risky_files))
    if large_files:
        print(f"\n[!] LARGE FILES (>= {LARGE_FILE_BYTES/1_000_000:.0f} MB) — likely not meant for git:")
        print("\n".join(large_files))
    if nb_with_output:
        print("\n[!] NOTEBOOKS WITH OUTPUT retained — clear outputs before committing:")
        print("\n".join(nb_with_output))
    if not findings:
        print("\nNo secrets, sensitive files, oversized files, or notebook outputs detected.")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
