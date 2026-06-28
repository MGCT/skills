#!/usr/bin/env python3
"""Survey a project for spring-cleaning: surface clutter, dead weight, doc bloat,
and likely-stale files so the skill can propose a tidy-up plan from facts instead
of guesswork.

Pure stdlib. Git-aware when possible (uses `git ls-files` to respect .gitignore),
degrades to a filesystem walk otherwise.

Usage:
    python survey.py [repo-path] [--stale-days N] [--doc-lines N]

Output is human-readable text grouped by concern. It recommends nothing on its own —
it just lays out what's there so a human (or the model running the skill) can decide.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# Files that legitimately live at the repo root — don't flag these as clutter.
ROOT_WHITELIST = {
    "readme.md", "readme.rst", "readme.txt", "readme",
    "license", "license.md", "license.txt", "copying", "notice",
    "claude.md", "agents.md", "contributing.md", "code_of_conduct.md",
    "changelog.md", "security.md", "authors", "maintainers",
    ".gitignore", ".gitattributes", ".editorconfig", ".gitmodules",
    "makefile", "dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "poetry.lock",
    "cargo.toml", "cargo.lock", "go.mod", "go.sum",
    "tsconfig.json", "jsconfig.json", ".env.example", ".env.sample",
    ".nvmrc", ".python-version", ".ruby-version", ".tool-versions",
    "vite.config.ts", "vite.config.js", "next.config.js", "tailwind.config.js",
    ".prettierrc", ".eslintrc", ".eslintrc.json", ".eslintrc.js",
}

# Directories we never descend into (caches, deps, build output, vcs).
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".venv", "venv", "env", ".env",
    "dist", "build", ".next", ".nuxt", "target", "out", ".cache",
    "coverage", ".idea", ".vscode", ".gradle", "vendor", ".tox",
}

# Extensions / names that are almost always disposable junk.
JUNK_SUFFIXES = (".log", ".tmp", ".temp", ".bak", ".orig", ".swp", ".pyc", ".pyo")
JUNK_NAMES = {".ds_store", "thumbs.db", "desktop.ini", "npm-debug.log"}

# Naming patterns that hint a file is a superseded copy worth archiving/reviewing.
ARCHIVE_HINTS = (
    "copy", "old", "backup", "deprecated", "draft",
    "final", "finalfinal", "v2", "v3", "vfinal", "todelete", "delete_me",
)

DOC_FILES = {"claude.md", "agents.md", "readme.md", "contributing.md"}


def run_git(repo: Path, *args: str) -> list[str] | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, check=True,
        )
        return [ln for ln in out.stdout.splitlines() if ln.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_git_repo(repo: Path) -> bool:
    return run_git(repo, "rev-parse", "--is-inside-work-tree") is not None


def collect_files(repo: Path) -> list[Path]:
    """Tracked + untracked-not-ignored files (git), or a filtered walk."""
    if is_git_repo(repo):
        tracked = run_git(repo, "ls-files") or []
        untracked = run_git(repo, "ls-files", "--others", "--exclude-standard") or []
        rels = set(tracked) | set(untracked)
        return [repo / r for r in sorted(rels)]
    files: list[Path] = []
    for root, dirs, names in os.walk(repo):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS]
        for n in names:
            files.append(Path(root) / n)
    return files


def days_since(path: Path) -> float:
    try:
        return (time.time() - path.stat().st_mtime) / 86400.0
    except OSError:
        return 0.0


def line_count(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def section(title: str) -> None:
    print(f"\n## {title}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Survey a project for spring-cleaning.")
    ap.add_argument("repo", nargs="?", default=".", help="path to the project (default: cwd)")
    ap.add_argument("--stale-days", type=int, default=180,
                    help="flag files untouched longer than this (default: 180)")
    ap.add_argument("--doc-lines", type=int, default=200,
                    help="flag CLAUDE.md/docs longer than this many lines (default: 200)")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"error: {repo} is not a directory", file=sys.stderr)
        return 2

    git = is_git_repo(repo)
    files = collect_files(repo)
    print(f"# Spring-clean survey: {repo}")
    print(f"{'git repo' if git else 'not a git repo (filesystem walk)'} - "
          f"{len(files)} files in scope")

    # --- Root-level clutter -------------------------------------------------
    root_clutter = []
    for f in files:
        try:
            rel = f.relative_to(repo)
        except ValueError:
            continue
        if len(rel.parts) == 1 and f.is_file():
            if rel.name.lower() not in ROOT_WHITELIST and not rel.name.lower().startswith(".env"):
                root_clutter.append(rel.name)
    section(f"Root-level files that may want filing ({len(root_clutter)})")
    if root_clutter:
        print("Non-standard files sitting at the repo root - candidates to move into a "
              "folder (docs/, scripts/, assets/...) or archive:")
        for name in sorted(root_clutter):
            print(f"  - {name}")
    else:
        print("None - the root is tidy.")

    # --- Junk ---------------------------------------------------------------
    junk = []
    for f in files:
        nm = f.name.lower()
        if nm in JUNK_NAMES or nm.endswith(JUNK_SUFFIXES):
            junk.append(str(f.relative_to(repo)))
    section(f"Likely disposable junk ({len(junk)})")
    if junk:
        print("Caches, logs, editor/OS cruft - usually safe to delete and gitignore:")
        for j in sorted(junk):
            print(f"  - {j}")
    else:
        print("None found.")

    # --- Archive-name hints -------------------------------------------------
    archivey = []
    for f in files:
        stem = f.stem.lower().replace("-", "").replace("_", "").replace(" ", "")
        if any(h in stem for h in ARCHIVE_HINTS):
            archivey.append(str(f.relative_to(repo)))
    section(f"Files whose names suggest they're superseded ({len(archivey)})")
    if archivey:
        print("Names containing copy/old/backup/final/v2... - confirm which is current, "
              "then archive or delete the rest:")
        for a in sorted(archivey):
            print(f"  - {a}")
    else:
        print("None found.")

    # --- Doc bloat ----------------------------------------------------------
    section("Documentation size")
    found_doc = False
    for f in files:
        if f.name.lower() in DOC_FILES and f.is_file():
            found_doc = True
            lc = line_count(f)
            flag = "  <-- large, consider trimming/splitting" if lc > args.doc_lines else ""
            print(f"  - {f.relative_to(repo)}: {lc} lines{flag}")
    if not found_doc:
        print("  No CLAUDE.md / README / AGENTS.md found.")

    # --- Stale --------------------------------------------------------------
    stale = []
    for f in files:
        if not f.is_file():
            continue
        d = days_since(f)
        if d > args.stale_days:
            stale.append((d, str(f.relative_to(repo))))
    stale.sort(reverse=True)
    section(f"Files untouched > {args.stale_days} days ({len(stale)})")
    if stale:
        print("By filesystem mtime (a fresh clone resets these, so treat as a hint, "
              "not proof). Oldest first:")
        for d, p in stale[:40]:
            print(f"  - {p}  ({int(d)}d)")
        if len(stale) > 40:
            print(f"  ... and {len(stale) - 40} more")
    else:
        print("None - or this is a fresh clone with reset timestamps.")

    # --- Top-level layout ---------------------------------------------------
    dir_counts: dict[str, int] = {}
    for f in files:
        rel = f.relative_to(repo)
        top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        dir_counts[top] = dir_counts.get(top, 0) + 1
    section("Top-level layout (file counts)")
    for name, count in sorted(dir_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  - {name}: {count}")

    print("\n# End of survey - nothing has been changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
