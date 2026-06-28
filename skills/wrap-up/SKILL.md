---
name: wrap-up
description: End-of-session housekeeping pass that leaves the project up to date, internally consistent, and safe to resume. Use this whenever the user types /wrap-up, or signals they're finishing — "let's wrap up", "I'm done for the day", "wrapping up here", "before we finish", "end of session", "let's call it" — or asks to make sure everything is tidy, current, consistent, documented, or safe to commit before stopping. Reconstructs what the session did, then checks that documentation is current, that files don't contradict or duplicate each other or sit stale, that no code loose ends or risky/secret-bearing changes are about to be committed, and that anything worth remembering is captured — proposing the fixes and applying them only once the user approves.
---

# Wrap-up

The end of a session is when context is richest and most perishable. You know what
changed, what was half-finished, what was decided, and which docs you didn't get back
to. The next session — you or someone else — starts cold and has to reconstruct all of
it from the repo alone. This skill spends that fading context now: it makes the
project's written record agree with what actually happened, removes contradictions and
dead weight that quietly accumulate, catches anything risky before it's committed, and
leaves a clean, resumable state.

A bare "wrap up the session" prompt already does the obvious tidying. The point of
this skill is the work a model *won't* reliably do on its own: hunt for cross-file
contradictions, notice what's gone stale, scan for secrets deterministically, and
capture decisions and memory. Lean into those.

This is a **propose-then-apply** workflow. Do the full review, present findings as a
report, and wait for the user's go-ahead before changing any file. Editing files,
committing, and pushing all change state, so propose those and act only on approval —
never as a reflex of wrapping up. Read-only checks are different: running the test
suite, a linter, or a type-checker changes nothing and never touches git, so **run
those freely** to ground the report in fact instead of guesswork. The user came here to
close out a session cleanly, not to be surprised.

## How to run it

### 1. Reconstruct what this session actually did

Build a clear picture of the session's work before auditing. Corroborate the
conversation against the repo rather than trusting memory:

- Read the conversation so far for what was built, changed, decided, or deferred.
- Run `git status`, `git diff`, and `git diff --staged` for concrete changes.
- Run `git log` for commits made this session, if any.
- If it isn't a git repo, fall back to recently modified files.

You're looking for the gap between *what happened* and *what the project's written
record now says*. That gap is most of the work.

### 2. Audit

Work through each area and collect specific, actionable items — point at the exact
file, line, or change. "`CLAUDE.md` still says `analyze.py` is the only module" beats
"docs may need review."

**Documentation currency.** Check the docs that track state against what changed:
`CLAUDE.md`, `README`, and any roadmap / plan / actions / TODO / changelog files
(`ROADMAP.md`, `TODO.md`, `ACTIONS.md`, `CHANGELOG.md`, `docs/`, plan files). New
commands, dependencies, file-structure changes, or conventions introduced this session
often belong in `CLAUDE.md`. Completed work should be checked off or moved out of the
roadmap; newly discovered work should be added.

**Cross-file consistency and staleness.** This is the part a quick once-over misses,
so spend real effort here. Look across the whole set of project documents and config,
not just the files touched this session:

- *Contradictions.* The same fact stated two different ways in two places — a version
  number, a command, a config value, a date, a status. An action item dated one way in
  the roadmap and another in a notes file. A feature described as "planned" in one doc
  and "done" in another. A path or filename referenced that doesn't match the actual
  tree. When you find a contradiction, work out which side is now true (the code and
  git history usually settle it) and propose reconciling the rest to match.
- *Duplication.* The same content copied across files that will drift apart — two docs
  both trying to be the source of truth for the same thing, a setup step pasted into
  three places, near-duplicate notes. Propose a single home and a pointer from the
  others.
- *Staleness / rot.* Sections that refer to things that no longer exist (a removed
  module, a renamed file, a dead link, an old dependency), dated items whose date has
  passed, plans or notes superseded by later work, and scratch/temp/backup files left
  lying around. For each, recommend the honest action: update it, or delete it. Stale
  docs are worse than missing ones because they're believed.

**Code loose ends.** Scan for things left mid-flight, prioritizing what this session
introduced: `TODO`/`FIXME`/`XXX` markers, debug or print statements, commented-out
blocks, obviously half-finished functions, and tests that are failing, skipped, or
were never written for new code. Don't try to clear the project's whole backlog — flag
older issues briefly rather than folding them into the proposed edits.

**Verification gates — run the read-only ones.** If the project has a way to check
itself — a test suite, linter, type-checker — the honest way to know it's "tidy" is to
run it, not infer from reading. These are read-only: they change no files and never
touch git, so just run them and report the real result. Don't claim tests pass without
having run them; if you choose not to run something, say so plainly rather than
implying it's green. The one exception is a check that genuinely has side effects — a
"build" that writes artifacts, a step that hits a paid or external service — name that
and get a yes first. Either way, running a check never implies committing or pushing;
those stay separate and separately approved.

**Git status and risky-commit scan.** Surface uncommitted changes, untracked files,
and unpushed commits. Before proposing any commit, run the bundled scanner over what's
staged/changed to catch things that must not be committed:

```
python <skill-dir>/scripts/scan_staged.py <repo-path>
```

It flags likely secrets (API keys, passwords, private keys, DB URLs with credentials),
`.env`-style files, oversized files, and notebooks committed with their output cells
intact — failure modes a visual skim misses. Treat any hit as a stop-and-flag, loudly
and early. Then group the legitimate changes into sensible commits and propose
messages. **Never commit, and never push, without explicit approval** — and if the
scanner finds a secret, recommend rotating it, since writing a secret to disk in a repo
should be treated as exposure.

**Memory.** Consider whether anything from this session is worth persisting to memory
for future sessions — a durable project fact, a decision and its rationale, a user
preference, or a correction. Only flag things that are *non-obvious and not already
recoverable from the repo or git history*; the code documents itself, so don't propose
saving what a future session could just read. If a memory index or directory is in
use, check it for entries this session has made stale or wrong.

### 3. Present the wrap-up report

Summarize in the chat in this shape. Keep it scannable — the user is closing out.

```
# Session wrap-up

## What got done
- <concise bullets of the session's actual accomplishments>

## Still open
- <unfinished work, deferred items, known issues — enough detail to resume cold>

## Proposed updates
### Docs
- [ ] <file>: <specific change>
### Consistency & stale files
- [ ] <file(s)>: <the contradiction / duplication / stale item, and how to resolve it>
### Code loose ends
- [ ] <file:line>: <what's dangling and the suggested resolution>
### Checks
- <test / lint / type-check you ran and the actual result; or a side-effecting one you'd run with the user's OK>
### Git
- [ ] <proposed commit(s) + message(s); note untracked/unpushed work; SCANNER HITS first>
### Memory
- [ ] <fact to save, and why it's worth persisting>

## Nothing-needed
- <areas you checked that are already clean — so the user knows they were covered>
```

Then ask how they want to proceed — apply everything, a subset, or nothing. Don't
start editing.

### 4. Apply approved changes

Make exactly what the user approved, and nothing with side effects they didn't:

- Edit the docs and code as proposed; resolve contradictions to the side you confirmed
  is true; remove or update stale files.
- Run any checks the user approved, and report real results.
- Save approved memory entries using whatever memory convention the project uses.
- If the session involved non-trivial decisions worth preserving, offer to append a
  short dated entry to a decision log capturing *what was decided and why* — the
  rationale that commit messages lose. Match an existing changelog/log format if one
  exists; create a new file only with the user's OK.
- Stage and commit only if approved, with the agreed messages. Push only on an explicit
  request.

Close with a one-line summary of what changed and what was deliberately left for next
time. That line is the resume point for the next session — make it useful.

## Bundled script

- `scripts/scan_staged.py` — scans staged + changed + untracked files for secrets,
  oversized files, and notebooks with retained output. Pure stdlib; run it with
  `python scripts/scan_staged.py [repo-path]` (defaults to the current directory).
  Exit code is non-zero when it finds something worth blocking a commit.

## Principles

- **Specific beats thorough-looking.** Every item should be actionable without the
  user asking what you meant. Name the file, the line, the exact change.
- **Stale and contradictory is worse than missing.** A doc that confidently states
  something untrue costs more than a gap, because it's trusted. Hunt these down — it's
  the main thing this skill adds over an ad-hoc tidy.
- **Know which actions mutate.** Reading files and running tests/linters/type-checkers
  change nothing — do them freely and report real results. Editing files, committing,
  and pushing change state — propose those and get a yes each time. Don't conflate the
  two: being timid about a read-only test run is as unhelpful as committing without asking.
- **Surface risk early.** A secret about to be committed, a deleted file that wasn't
  meant to go, tests that started failing — say so plainly and at the top, not buried.
- **Adapt to the project.** A solo script, a shared codebase with a formal roadmap, and
  a scratch folder want different levels of ceremony. Match what the project actually
  uses; don't impose process it doesn't have.
