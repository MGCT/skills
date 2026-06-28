---
name: spring-clean
description: Deliberate tidy-up pass for a project or codebase that has accumulated clutter. Use this whenever the user types /spring-clean, or asks to tidy up / clean up / declutter / reorganize / "sort out" a project, file loose files into folders, archive redundant or dead files, restructure a messy repo, or trim and refresh a CLAUDE.md (or README) that has grown bloated or stale. Surveys the whole project, proposes a concrete reorganization plan — what moves where, what gets archived, which docs get trimmed, what dependencies/config look unused — and applies it only once the user approves, moving files history-safely and without breaking imports or the build. Distinct from /wrap-up: wrap-up is a light end-of-session pass focused on git safety and matching docs to what just changed; spring-clean is a deeper, deliberate spring-cleaning of how the project is physically organized.
argument-hint: "[path or area to focus on]"
---

# Spring-clean

Projects rot in slow motion. Scratch files pile up at the root, a `utils_old.py`
sits next to `utils.py`, the `CLAUDE.md` that was tight at 40 lines is now 300 lines
of half-true history, three folders each hold "the" config, and nobody remembers if
`scripts/migrate_v2_FINAL.py` still matters. None of this breaks anything — it just
quietly raises the cost of every future change and every new person (or model) who
has to find their way around. Spring-clean is the deliberate pass that pays that debt
down: it reorganizes how the project is laid out, retires dead weight, and makes the
docs lean and true again.

This is bigger and more physical than [[wrap-up]]. Wrap-up is a light end-of-session
check that the written record matches what just happened, with a careful eye on git
and secrets. Spring-clean doesn't care about "this session" at all — it looks at the
project as a standing artifact and asks "is this well-organized for the next year of
work?" Moving and archiving files is the main event, not an afterthought. If the user
is finishing a session and wants a quick safety sweep, that's wrap-up; if they want to
*reorganize*, that's this.

## The cardinal rule: propose first, then act

Reorganizing a project is hard to reverse and easy to get wrong — a moved file can
break an import three directories away, an "obviously dead" file can be the one thing
a deploy script reads. So this is strictly a **survey -> plan -> approve -> apply**
workflow. Do the whole survey, present a concrete plan, and **change nothing until the
user signs off**. Then apply exactly what they approved.

Reading, listing, grepping, and running the bundled survey script are all read-only —
do them freely; they're how the plan earns its keep. Moving, archiving, deleting, and
editing all mutate the project — those wait for a yes.

Two non-negotiables when you do apply, because they're the ways a tidy-up does real
damage:

- **Move history-safely.** For tracked files in a git repo, use `git mv` so history
  follows the file. Never move a tracked file with a plain `mv`/copy that orphans its
  past.
- **Archive by default, delete only the obvious.** "Redundant" is a guess until
  proven. Move suspected-dead files into an archive location rather than deleting them,
  so the action is reversible. Reserve outright deletion for unambiguous junk (caches,
  `.DS_Store`, `*.log`, build artifacts) — and even then, list it first.

## How to run it

### 1. Survey the project

Build a factual map before proposing anything. Start with the bundled scanner, which
does the deterministic legwork (root clutter, junk, doc bloat, stale files, layout):

```
python <skill-dir>/scripts/survey.py <repo-path>
```

Then read with judgment the script can't apply:

- Skim the actual top-level layout and the `CLAUDE.md` / `README`. Get a feel for the
  project's *existing* conventions — where do source, tests, docs, scripts, and assets
  already live? You're tidying *toward the project's own grain*, not imposing a
  structure it doesn't use.
- Open the files the survey flagged as clutter, archive-named, or stale and judge them
  for real. A file called `notes_final.md` might be load-bearing; a blandly-named one
  might be dead. The name is a hint, not a verdict.
- Note honest uncertainty. Anything you can't confidently classify goes to the user as
  a question, not into the silent-changes pile.

### 2. Audit each area

Collect specific, actionable items — name the exact file and the exact move. "Move
`debug_output.txt`, `scratch.py`, `Screenshot 2025-01-03.png` from the root into a
gitignored `scratch/`" beats "tidy up loose files."

**File organization.** Loose files that have drifted to the wrong place — scratch
files, logs, one-off scripts, exports, screenshots, and assets sitting at the repo
root or scattered across folders. Propose a home for each, following existing folders
where they exist (`scripts/`, `docs/`, `assets/`, `data/`) and proposing new ones only
when a real cluster justifies it. Group the moves so the user sees the shape of the new
layout, not just a flat list.

**Redundant and dead files.** Superseded copies (`x_old`, `x_v2`, `x copy`), backups,
one-shot scripts whose job is done, empty or near-empty files, and genuine junk
(caches, `.DS_Store`, stray logs, build artifacts). For each, decide between *archive*
(plausibly-dead but unproven — move it aside) and *delete* (unambiguous junk). When two
files look like versions of the same thing, work out which is current — git history,
imports, and references usually settle it — and propose retiring the other.

**Source code organization (higher risk — tread carefully).** Only when the source
layout is genuinely messy and reorganizing clearly helps. Before proposing any source
move, find who references the file: imports, requires, relative paths, config, build
manifests, CI. A move is only safe if every reference moves with it, so the proposal
must include those follow-on edits, not just the `git mv`. If you can't trace all the
references confidently, say so and propose the smaller, safe subset rather than a
risky sweeping reshuffle. The build/tests passing afterward is the proof — plan to run
them.

**CLAUDE.md and docs — trim and refresh.** This is often the highest-value part. A
`CLAUDE.md` earns its place by being read every session, so length is a real cost:
bloat buries the signal. Aim to make it *lean and true*, not just shorter.

- Cut what no longer pays rent: descriptions of files/modules that moved or were
  deleted, completed TODOs, obsolete instructions, war stories, and anything a model
  could trivially rederive from the code itself.
- Reconcile what's stale: commands, paths, versions, and conventions that have drifted
  from reality. Fix them to match the current tree (and any moves you're proposing).
- Restructure when it's grown shapeless: group related guidance, lead with what's used
  most, and push rarely-needed detail into a linked reference file rather than carrying
  it inline. A 300-line `CLAUDE.md` is usually a 90-line core plus a couple of pointers.
- Apply the same eye to `README` and other docs: are they describing the project as it
  is now, or as it was?

Show proposed doc trims as a before/after shape (sections kept, cut, moved) so the
user can approve the *editorial judgment*, not just rubber-stamp a diff.

**Dependencies and config (flag, don't remove).** Removing a dependency or deleting a
config file is high-risk and easy to get wrong from the outside, so here you *report*
rather than act. Note likely-unused dependencies (declared but not imported anywhere),
duplicate or conflicting lockfiles, dead or duplicated config, and `.env`-style files
that look committed by accident. Present these as findings for the user to act on,
with your reasoning, not as changes you'll make.

### 3. Present the tidy-up plan

Lay it out so the user can approve some, all, or none. Keep it concrete and grouped by
risk — cheap-and-safe moves first, the things that need a careful look last.

```
# Spring-clean plan: <project>

## Current state
- <2-4 lines on what the survey found: root clutter count, doc sizes, obvious dead weight>

## Proposed changes

### File organization (low risk)
- [ ] move <file> -> <dir>/   (git mv)
- [ ] new folder <dir>/ for <the cluster it holds>

### Archive / delete
- [ ] archive <file> -> <archive-loc>/   (plausibly dead: <why>)
- [ ] delete <file>   (junk: <why>)

### CLAUDE.md / docs
- [ ] CLAUDE.md: <before>->after line count; cut <sections>, fix <stale items>, move <X> to references/
- [ ] README: <specific fix>

### Source moves (higher risk — review carefully)
- [ ] move <file> -> <dir>/ plus update refs in <files>   (or: "not confident all refs traced — see note")

## Flagged for your call (no change proposed)
- Dependencies: <likely-unused X, duplicate lockfile Y>
- <anything you couldn't classify — ask>

## Already tidy
- <areas you checked that are fine, so the user knows they were covered>
```

Then ask how to proceed. Don't start moving things.

### 4. Apply approved changes

Execute exactly what was approved, in safe order, and verify:

- Make moves with `git mv` for tracked files; create the destination folders first.
  Apply the follow-on reference edits for any source move *in the same step* as the
  move, so the tree is never left broken.
- Archive to the agreed location; delete only the items explicitly approved.
- Apply the `CLAUDE.md`/doc trims, creating any `references/` files the plan splits out
  and leaving a one-line pointer to them.
- Add gitignore entries for any junk classes you cleaned (so they don't come back).
- If the project has tests/lint/build, **run them after the moves** and report the real
  result — this is how you prove the reorganization didn't break anything. These are
  read-only; run them freely. (A build that writes artifacts or hits a paid service is
  the exception — name it and get a yes.)
- Don't commit or push unless the user asks; if they do, group the moves and the edits
  into sensible commits. A pure-rename commit kept separate from content edits keeps
  the history readable.

Close with a short summary: what moved, what was archived vs deleted, how much the
`CLAUDE.md` shrank, what you flagged for them to handle, and the verification result.

## Bundled script

- `scripts/survey.py` — read-only project scanner. Surfaces root-level clutter,
  disposable junk, archive-named files, oversized docs, files stale by mtime, and the
  top-level layout. Git-aware (respects `.gitignore` via `git ls-files`), pure stdlib.
  Run `python scripts/survey.py [repo-path] [--stale-days N] [--doc-lines N]`. It
  changes nothing — it just gives the plan a factual starting point.

## Principles

- **Tidy toward the project's grain.** The goal is a layout that fits how this project
  already works, not a generic ideal. Reuse existing folders and conventions before
  inventing new ones; a reorg the team has to relearn is its own kind of mess.
- **Reversible by default.** Archive over delete, `git mv` over `mv`, propose over act.
  Anyone should be able to undo a spring-clean if it went somewhere they didn't want.
- **A move isn't done until its references move too.** The damage from tidying is
  almost always a dangling reference. Trace them before proposing a source move, edit
  them in the same step, and let the tests confirm it.
- **Leaner docs beat longer ones.** For a `CLAUDE.md` especially, every stale or
  redundant line taxes every future session. Cutting true-but-rederivable content is a
  feature, not data loss.
- **Match the project's ceremony.** A personal scratch repo, a script folder, and a
  shared production codebase want very different levels of restructuring. Don't impose
  process — or folders — a small project doesn't need.
```
