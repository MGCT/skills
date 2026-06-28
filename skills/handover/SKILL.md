---
name: handover
description: Capture the working state of the current session as a structured baton-pass so a fresh session window can pick the work up cold — and read the last one back to resume. Use this whenever the user types /handover, or asks to "create/write a handover", "hand this off", "save where we are", "capture the session before I stop", "I need to switch windows / run out of context", "make a note so I can carry on later" — or, on the resume side, "pick up where I left off", "resume the last session", "continue from yesterday", "load the handover", "what were we doing". Writes a session summary — the workflow, problems hit and how they were fixed, what was implemented, key knowledge/gotchas, current state, and the next concrete actions — to temp memory outside the repo (~/.claude/handovers/<project>/) so it persists across session windows without cluttering the project or git. Distinct from /wrap-up (repo-facing end-of-session tidy) and from permanent memory (durable facts): a handover is disposable working state for resuming this thread of work.
argument-hint: "[resume | new]"
---

# Handover

Context at the end of a working session is rich and perishable. You know the goal, the
dead ends you already ruled out, the half-applied fix, the one config value that took an
hour to find, and the exact next thing you were about to do. A new session window starts
cold: it has the repo and nothing else, and burns time re-deriving what you already knew.
A handover spends that fading context now — it writes a structured baton-pass so the next
session (you, tomorrow, in a fresh window) resumes the *thread of work* in a minute
instead of reconstructing it from scratch.

The notes live in **temp memory outside the repo** — `~/.claude/handovers/<project>/` —
on purpose. Working state ("we're mid-refactor, the auth test is still red, try X next")
is exactly what you don't want littering the codebase or the permanent record: it's true
for a day and then it's noise. Keeping it out of the tree means the repo stays clean,
nothing risks being committed, and handovers can be pruned freely once they're consumed.

Know what this is *not*, so you route correctly:

- **Not [[wrap-up]].** Wrap-up is repo-facing: it reconciles docs with what changed, scans
  for secrets, and gets the project safe to commit and leave. Handover is forward-facing:
  it captures the *live working state* so a future session can keep going. Someone finishing
  cleanly wants wrap-up; someone who has to stop mid-task and resume later wants handover.
  They compose — wrap-up to leave the repo tidy, handover to carry the thread.
- **Not permanent memory.** A durable fact ("this project deploys via Cloud Run", "the
  user prefers tabs") belongs in the memory system, where it informs every future session.
  A handover is the opposite: disposable, specific to one in-flight task, expected to be
  thrown away after it's read. If while writing a handover you notice a genuinely durable
  fact, suggest saving *that* to memory separately — don't bury it in a handover that gets
  pruned.

## Two modes

Read the user's intent and pick the mode; when ambiguous, ask.

- **Save** — "create a handover", "/handover", "hand off", "save where we are before I
  stop". Summarize the session and write a new handover file.
- **Resume** — "pick up where I left off", "/handover resume", "what were we doing",
  "continue from yesterday". Read the latest handover and brief the user to continue.

All filesystem mechanics (resolving the store, timestamped filenames, finding the latest,
listing, pruning) go through the bundled script so paths are never guessed:

```
python <skill-dir>/scripts/handover.py <command>
```

Commands: `path`, `new`, `latest`, `list`, `prune --keep N`. It keys the store by the
project's git top-level (or the current directory) and creates the directory as needed.

## Save: write a handover

Writing to a temp dir outside the repo mutates nothing the user cares about and never
touches git, so this is low-stakes — **just do it**, then show what you saved. The value
is in the *quality* of the reconstruction, so spend the effort there, not on ceremony.

### 1. Reconstruct the session

Build an accurate picture before writing. Corroborate the conversation against the repo
rather than trusting recall:

- Read the conversation for the goal, the path taken, decisions made, and what's still open.
- Run `git status`, `git diff`, and `git diff --staged` for the concrete changes in flight.
- Run `git log` (this session's commits) and note the current branch.
- Note anything environment-specific that a fresh window won't infer: a server left
  running, a command that must be run first, an env var that was set by hand.

### 2. Write the handover

Get a fresh target path, then write the structure below into it:

```
python <skill-dir>/scripts/handover.py new
```

Aim it at a cold reader who knows the project but not this session. Be concrete — name
files, lines, commands, error messages. Omit a section if it genuinely has nothing; don't
pad. The next-steps section is the most valuable part, so make the first item the literal
next action, specific enough to start on without re-thinking.

```markdown
# Handover — <project> — <YYYY-MM-DD HH:MM>

> Project: <absolute project path>   Branch: <branch>   Base: <base branch>

## What we were doing
<2-4 lines: the goal and the thread of work, enough to orient a cold reader.>

## Progress so far
- <key steps taken, in order — what's actually been done>

## Problems hit & how they were resolved
- <problem> → <fix, or current status if still open>

## Implementations & changes
- <file:area> — <what changed and why>

## Key knowledge & gotchas
- <non-obvious things learned this session: a config quirk, an API shape, a dead end
  to avoid re-exploring, a constraint discovered the hard way>

## Current state
- <what works, what's half-done, what's untested; a one-line git status summary>

## Next steps
1. <the literal next action — specific enough to start immediately>
2. <then this>
3. <…>

## How to resume
- <commands to run / tests to check, files to open first, env/server notes>
```

### 3. Confirm

Tell the user it's saved, give the path, and echo the next-step line so the baton is
visible. Mention they can resume with `/handover resume` (or just "pick up where I left
off") in a new window. If durable facts surfaced, note them as candidates for permanent
memory rather than folding them in here. If handovers have piled up, offer to
`prune --keep N`.

## Resume: read the last handover

Reading is read-only — locate and read the latest, brief the user, then **confirm before
diving into the work itself**, since resuming means re-entering an in-flight task.

### 1. Locate and read

```
python <skill-dir>/scripts/handover.py latest
```

Read that file. If the command reports none, say so and offer `list` to check, or to
start fresh. Check the `Project:` line matches the current project path — folder-name
collisions are possible, so if it points somewhere else, flag it instead of assuming.

### 2. Brief and confirm

Give the user a tight orientation, not a wall of text:

- **Where we left off** — the goal and current state in a couple of lines.
- **Next step** — the first action from the handover, verbatim.
- Surface anything time-sensitive or stale: the handover is a snapshot, so reconcile it
  against reality before acting — re-run `git status`, and if something it claims (a red
  test, a running server, an uncommitted change) no longer holds, say so. A handover that
  has gone stale is worse than none, because it's trusted.

Then ask whether to pick up from that next step or adjust. Once you're actually
continuing, the consumed handover is a candidate for pruning — mention it, but don't
delete without a nod.

## Bundled script

- `scripts/handover.py` — resolves the per-project handover store under
  `~/.claude/handovers/<project>/`, mints timestamped filenames, finds the latest, lists,
  and prunes. Pure stdlib, cross-platform. Run
  `python scripts/handover.py {path|new|latest|list|prune --keep N} [--name X] [--root DIR]`.
  It only manages paths and files — the handover *content* is yours to write.

## Principles

- **Write for a cold reader.** The audience is a session with the repo and nothing else.
  Every line should reduce the time-to-resume. Name files, commands, and errors; vague
  notes ("fixed the bug", "continue the work") defeat the purpose.
- **The next step is the point.** A handover that captures everything except what to do
  next has buried the lede. Lead the resume with one concrete, ready-to-start action.
- **Disposable on purpose.** This is working state, not a record. It lives outside the
  repo, it's fine to prune, and durable facts belong in permanent memory instead — keep
  the two from blurring.
- **Resume against reality, not the snapshot.** A handover describes a moment that may
  have passed. On resume, reconcile it with `git status` and the actual tree before
  trusting it, and flag anything that no longer holds.
- **Match the work's weight.** A five-minute task needs a three-line handover; a deep
  multi-day refactor earns the full structure. Don't impose ceremony a quick stop doesn't
  warrant.
