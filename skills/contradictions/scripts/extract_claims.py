#!/usr/bin/env python3
"""Extract candidate factual claims from a project's text, with provenance.

A contradiction check (or a fact-check) only needs to scan the *checkable*
statements in a body of work, not every line. This script walks a project,
reads its text/doc files, and pulls out lines that look like factual claims —
ones carrying numbers, dates, money, comparatives/superlatives, certainty
words, or citations — tagging each with the signals it matched and its
file:line provenance.

The model then does the semantic work the script can't: clustering claims about
the same subject to spot internal contradictions, and picking externally
verifiable ones to fact-check. This script just finds and tags the candidates,
deterministically and at scale, so nothing relevant is missed and large
projects don't have to be read in full.

Pure stdlib; cross-platform. It reads plain-text formats natively (.md, .txt,
.rst, etc.). Binary docs (.docx/.pdf) are skipped with a note — read those
directly with the model's own tools if a project leans on them.

Usage:
  python extract_claims.py [PATHS ...] [--signals s1,s2] [--text] [--max-per-file N]

  PATHS         Files or dirs to scan (default: current directory).
  --signals     Comma-separated subset to keep: number,percent,money,date,
                comparative,certainty,citation. Default: all.
  --text        Human-readable grouped output instead of JSON.
  --max-per-file Cap candidates emitted per file (default: no cap).
"""
import argparse
import json
import re
import sys
from pathlib import Path

TEXT_EXTS = {".md", ".markdown", ".txt", ".rst", ".text", ".adoc", ".org"}
# Binary doc formats we can't read with stdlib — reported so they aren't silently missed.
DOC_EXTS = {".docx", ".pdf", ".pptx", ".doc", ".ppt"}
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", ".idea", ".vscode", ".pytest_cache",
    ".mypy_cache", "site-packages", ".tox", "coverage",
}
MAX_BYTES = 2_000_000  # skip very large files
MAX_TEXT = 320          # truncate a reported line to this many chars

MONTHS = (
    r"jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|"
    r"aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember)?"
)

SIGNAL_PATTERNS = {
    "percent": re.compile(r"\b\d+(\.\d+)?\s*%|\bper ?cent\b|\bpercent\b", re.I),
    "money": re.compile(
        r"[£$€]\s?\d|\b\d+(\.\d+)?\s?(k|m|bn|million|billion|trillion|"
        r"gbp|usd|eur)\b",
        re.I,
    ),
    "date": re.compile(
        rf"\b(19|20)\d{{2}}\b|\b\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}}\b|"
        rf"\b({MONTHS})\b",
        re.I,
    ),
    "comparative": re.compile(
        r"\b(larg|small|high|low|great|fast|slow|big|strong|weak|cheap|"
        r"expensiv)(est|er)\b|\b(most|least|best|worst|leading|top|only|"
        r"first|fewest|majority|minority)\b",
        re.I,
    ),
    "certainty": re.compile(
        r"\b(always|never|all|none|every|everyone|nobody|guarantee[d]?|"
        r"definitely|certainly|proven|must|impossible|cannot|will not|"
        r"won't|no one)\b",
        re.I,
    ),
    "citation": re.compile(
        r"\b(according to|research (shows|suggests|found)|stud(y|ies)|"
        r"survey(ed)?|report(s|ed)?|data (shows|suggest)|source[ds]?|"
        r"evidence|analys(is|ts)|forecast|estimate[ds]?)\b|https?://",
        re.I,
    ),
    # plain number last, so more specific signals win the "primary" label
    "number": re.compile(r"\b\d+(\.\d+)?\b"),
}

# A line needs some prose to be a claim, not a table rule or code.
LETTERS = re.compile(r"[A-Za-z]")
HAS_WORDS = re.compile(r"[A-Za-z]{3,}")


def signals_for(line: str):
    found = []
    for name, pat in SIGNAL_PATTERNS.items():
        if pat.search(line):
            found.append(name)
    # collapse: if a richer numeric signal fired, "number" is redundant
    if len(found) > 1 and "number" in found and (
        {"percent", "money", "date"} & set(found)
    ):
        found.remove("number")
    return found


def looks_like_claim(line: str) -> bool:
    s = line.strip()
    if len(s) < 12 or len(s) > 600:
        return False
    if not HAS_WORDS.search(s):
        return False
    # skip markdown structure / table separators / code fences
    if set(s) <= set("|-=+*_# "):
        return False
    if s.startswith("```") or s.startswith("|--") or s.startswith("---"):
        return False
    # need at least a few words, not just a heading of one token
    if len(re.findall(r"[A-Za-z]{2,}", s)) < 3:
        return False
    return True


def iter_files(paths):
    for p in paths:
        path = Path(p)
        if path.is_file():
            yield path
        elif path.is_dir():
            for f in sorted(path.rglob("*")):
                if f.is_dir():
                    if f.name in SKIP_DIRS:
                        # prune by skipping; rglob can't prune, so filter on parts
                        continue
                    continue
                if any(part in SKIP_DIRS for part in f.parts):
                    continue
                yield f


def extract(paths, wanted):
    claims = []
    scanned = 0
    skipped_docs = []
    root = Path(paths[0]).resolve()
    base = root if root.is_dir() else root.parent
    for f in iter_files(paths):
        ext = f.suffix.lower()
        if ext in DOC_EXTS:
            skipped_docs.append(str(f))
            continue
        if ext not in TEXT_EXTS:
            continue
        try:
            if f.stat().st_size > MAX_BYTES:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        scanned += 1
        try:
            rel = f.relative_to(base)
        except ValueError:
            rel = f
        for i, line in enumerate(text.splitlines(), 1):
            if not looks_like_claim(line):
                continue
            sigs = signals_for(line)
            if not sigs:
                continue
            # markdown table rows are mostly structure; keep only if a richer
            # signal than a bare number fired (a real figure, date, claim word).
            if line.lstrip().startswith("|") and set(sigs) <= {"number"}:
                continue
            if wanted and not (set(sigs) & wanted):
                continue
            txt = line.strip()
            if len(txt) > MAX_TEXT:
                txt = txt[:MAX_TEXT] + "…"
            claims.append(
                {"file": str(rel).replace("\\", "/"),
                 "line": i, "text": txt,
                 "signals": [s for s in sigs if not wanted or s in wanted]}
            )
    return claims, scanned, skipped_docs


def summarize(claims):
    by_signal, by_file = {}, {}
    for c in claims:
        by_file[c["file"]] = by_file.get(c["file"], 0) + 1
        for s in c["signals"]:
            by_signal[s] = by_signal.get(s, 0) + 1
    return {"by_signal": by_signal, "by_file": by_file}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Extract candidate factual claims.")
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--signals", default="")
    ap.add_argument("--text", action="store_true")
    ap.add_argument("--max-per-file", type=int, default=0)
    args = ap.parse_args(argv)

    paths = args.paths or ["."]
    wanted = {s.strip() for s in args.signals.split(",") if s.strip()}
    unknown = wanted - set(SIGNAL_PATTERNS)
    if unknown:
        ap.error(f"unknown signals: {', '.join(sorted(unknown))}")

    claims, scanned, skipped = extract(paths, wanted)

    if args.max_per_file > 0:
        seen = {}
        capped = []
        for c in claims:
            n = seen.get(c["file"], 0)
            if n < args.max_per_file:
                capped.append(c)
                seen[c["file"]] = n + 1
        claims = capped

    if args.text:
        out = [f"# {len(claims)} candidate claims across {scanned} files"]
        cur = None
        for c in claims:
            if c["file"] != cur:
                cur = c["file"]
                out.append(f"\n## {cur}")
            out.append(f"  L{c['line']} [{','.join(c['signals'])}] {c['text']}")
        if skipped:
            out.append(f"\n# {len(skipped)} binary doc(s) skipped (read directly):")
            out.extend(f"  - {s}" for s in skipped)
        print("\n".join(out))
    else:
        print(json.dumps({
            "files_scanned": scanned,
            "claim_count": len(claims),
            "skipped_binary_docs": skipped,
            "summary": summarize(claims),
            "claims": claims,
        }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
