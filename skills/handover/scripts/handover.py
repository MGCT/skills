#!/usr/bin/env python3
"""Resolve and manage handover notes stored outside the repo.

Handovers are session baton-passes: a future session reads the latest one to
pick up working state. They live under ~/.claude/handovers/<project>/ so they
persist across session windows without ever touching the repo or git.

This script owns the path/filesystem mechanics (resolving the store, minting
timestamped filenames, finding the latest, listing, pruning) so the model can
focus on writing good handover *content*. Pure stdlib; cross-platform.

Subcommands:
  path              Print (and create) the handover dir for this project.
  new               Print a fresh timestamped target path to write into.
  latest            Print the newest handover's path (exit 1 if none exist).
  list              List handovers newest-first, with age.
  prune --keep N    Delete handovers beyond the N most recent.

Project keying: the store is named after the project's folder (git top-level if
in a repo, else the current directory). Override with --name. The absolute
project path is meant to be recorded inside each handover so a resuming session
can confirm it's reading notes for the right project.
"""
import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path


def project_root(start: Path) -> Path:
    """Git top-level if available, else the starting directory."""
    try:
        out = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return start


def slugify(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    return slug or "project"


def store_dir(name: str | None, start: Path) -> Path:
    root = project_root(start)
    project = name or root.name
    d = Path.home() / ".claude" / "handovers" / slugify(project)
    d.mkdir(parents=True, exist_ok=True)
    return d


def handovers(d: Path) -> list[Path]:
    # Filenames are timestamped, so lexical sort == chronological. Newest last.
    return sorted(d.glob("*.md"))


def human_age(path: Path) -> str:
    delta = dt.datetime.now() - dt.datetime.fromtimestamp(path.stat().st_mtime)
    secs = int(delta.total_seconds())
    if secs < 3600:
        return f"{secs // 60}m ago"
    if secs < 86400:
        return f"{secs // 3600}h ago"
    return f"{secs // 86400}d ago"


def main() -> int:
    p = argparse.ArgumentParser(description="Manage handover notes outside the repo.")
    p.add_argument("command", choices=["path", "new", "latest", "list", "prune"])
    p.add_argument("--name", help="Override the project name used to key the store.")
    p.add_argument("--root", default=".", help="Where to detect the project from (default: cwd).")
    p.add_argument("--keep", type=int, default=10, help="For prune: how many recent handovers to keep.")
    args = p.parse_args()

    start = Path(args.root).resolve()
    d = store_dir(args.name, start)

    if args.command == "path":
        print(d)
        return 0

    if args.command == "new":
        stamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        print(d / f"{stamp}.md")
        return 0

    if args.command == "latest":
        items = handovers(d)
        if not items:
            print(f"No handovers found in {d}", file=sys.stderr)
            return 1
        print(items[-1])
        return 0

    if args.command == "list":
        items = handovers(d)
        if not items:
            print(f"No handovers found in {d}")
            return 0
        print(f"{len(items)} handover(s) in {d}:")
        for path in reversed(items):  # newest first
            print(f"  {path.name}  ({human_age(path)})")
        return 0

    if args.command == "prune":
        items = handovers(d)
        excess = items[: max(0, len(items) - args.keep)]
        for path in excess:
            path.unlink()
        print(f"Pruned {len(excess)} handover(s); kept {len(items) - len(excess)} in {d}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
