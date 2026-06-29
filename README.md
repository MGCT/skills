# claude-skills

A Claude Code **plugin marketplace** holding a collection of custom skills. Install
it once and the skills are available in any project, on any machine.

## Repository layout

```
skills (MGCT/skills)/
├── .claude-plugin/
│   ├── marketplace.json          # declares the marketplace + the plugin it offers
│   └── plugin.json               # plugin manifest (the repo root is the plugin)
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md              # one folder per skill (the only required file)
│       └── scripts/              # optional bundled helper scripts
├── tests/                        # optional eval cases, kept out of the shipped skills
│   └── <skill-name>/             # so `npx skills` installs stay lean
├── SKILL_TEMPLATE.md             # copy this to start a new skill
└── README.md
```

The top-level `skills/` directory is the convention both installers below understand.
Eval/test cases live in `tests/<skill-name>/` rather than inside the skill folders, so
they aren't copied into users' projects on install.

## Installing the skills

There are two ways to install, depending on your setup.

### A. `npx skills` — into a single project (any agent)

Uses [Vercel Labs' `skills` CLI](https://github.com/vercel-labs/skills); GitHub is the
registry, so no npm publish is involved. Run from your project root:

```bash
npx skills@latest add MGCT/skills            # interactive: pick skills + agent
npx skills add MGCT/skills --list            # list what's available
npx skills add MGCT/skills -s handover       # one skill (repeat -s for more)
npx skills add MGCT/skills -s '*' -y         # all skills, no prompts
npx skills add MGCT/skills -g                # install globally (~/.claude/skills)
```

Skills land in `.claude/skills/` (project) or `~/.claude/skills/` (with `-g`), and are
invoked as `/<skill-name>` (e.g. `/handover`). The whole skill folder is copied, so
bundled scripts come along.

### B. Claude Code plugin marketplace — install once, use everywhere

From inside Claude Code:

```
/plugin marketplace add MGCT/skills          # or the git URL
/plugin install toolkit@claude-skills
```

Installed this way the skills are invoked as `/toolkit:<skill-name>` (e.g.
`/toolkit:wrap-up`), or trigger automatically from their `description`. After editing
skills locally, pick up changes without restarting:

```
/plugin reload-plugins
```

## Skills

### `wrap-up` — end-of-session housekeeping + memory check

A pass to run when you're finishing a work session: it leaves the project up to
date, internally consistent, and safe to resume — and captures anything worth
remembering for next time.

**Trigger it** by typing `/toolkit:wrap-up`, or just by saying you're done —
"let's wrap up", "I'm done for the day", "before we finish". It first reconstructs
what the session actually did (from `git` plus the conversation), then checks:

- **Documentation currency** — reconciles `CLAUDE.md`, `README`, roadmaps, and
  action/TODO lists against what really changed this session.
- **Cross-file consistency & staleness** — hunts for contradictions across files
  (mismatched versions, dates, statuses, references to files that no longer exist),
  duplicated content that has drifted, and stale/dead files that should be updated
  or removed.
- **Code loose ends** — stray `TODO`/`FIXME`s, debug prints, commented-out blocks,
  half-finished functions, and skipped or failing tests left from the session.
- **Verification** — runs the project's read-only checks (tests, linters) and
  reports the real result, rather than guessing that things pass.
- **Risky commits** — runs a bundled scanner (`scripts/scan_staged.py`) over pending
  changes to catch secrets, `.env`-style files, oversized files, and notebooks
  committed with their output intact, before any of it reaches a commit.
- **Memory** — flags anything durable worth saving to Claude's persistent,
  cross-session memory (a decision and its rationale, a new convention, a
  preference) so the next session starts informed.

It then presents one scannable report — *What got done / Still open / Proposed
updates / Nothing-needed* — and **proposes** the fixes. It never edits files on its
own, and committing or pushing always require your explicit go-ahead.

### `spring-clean` — deliberate tidy-up of a cluttered project

A deeper, deliberate spring-cleaning of how a project is physically organized — for
when scratch files have piled up at the root, `utils_old.py` sits next to `utils.py`,
three folders each hold "the" config, and the `CLAUDE.md` that was tight at 40 lines
is now 300 lines of half-true history.

**Trigger it** by typing `/toolkit:spring-clean`, or by asking to tidy up / clean up
/ declutter / reorganize / "sort out" a project, file loose files into folders,
archive dead files, restructure a messy repo, or trim a bloated `CLAUDE.md`/`README`.
It runs a strict **survey → plan → approve → apply** workflow and changes nothing
until you sign off:

- **Survey** — a bundled scanner (`scripts/survey.py`) does the deterministic legwork
  (root clutter, junk, doc bloat, files stale by mtime, top-level layout; git-aware,
  pure stdlib), then Claude reads the flagged files with judgment the script can't apply.
- **File organization** — finds loose scratch files, logs, one-off scripts, exports,
  and assets that drifted to the wrong place, and proposes a home for each, tidying
  *toward the project's existing grain* rather than imposing a generic structure.
- **Redundant & dead files** — superseded copies, backups, spent one-shot scripts, and
  junk; it **archives by default and deletes only the obvious**, working out which of
  two look-alike files is current before retiring the other.
- **Source moves (higher risk)** — only when the layout is genuinely messy, and only
  after tracing every reference (imports, config, build, CI) so the follow-on edits
  ship in the same step and nothing breaks.
- **Docs — trim and refresh** — makes `CLAUDE.md`/`README` *lean and true*: cuts
  rederivable content, fixes stale paths/commands/versions, and splits rarely-needed
  detail into linked reference files, shown as a before/after shape.
- **Dependencies & config** — *flags* likely-unused deps, duplicate lockfiles, and
  stray `.env`-style files for you to act on, rather than removing them itself.

Moves use `git mv` so history follows the file; if the project has tests/lint/build it
runs them after applying to prove the reorg didn't break anything. As with `wrap-up`,
it proposes first and never commits or pushes without your go-ahead.

> Distinct from `wrap-up`: wrap-up is a light end-of-session pass focused on git
> safety and matching docs to what just changed; spring-clean ignores "this session"
> and reorganizes the project as a standing artifact.

### `handover` — baton-pass between session windows

A structured way to capture the *live working state* of a session so a fresh window
can pick it up cold — and to read the last one back to resume. For when you have to
stop mid-task, run out of context, or switch windows and want to carry on later
without re-deriving everything you already worked out.

**Trigger it** by typing `/toolkit:handover`, or by saying you want to "create a
handover", "hand this off", "save where we are before I stop" — or, to resume, "pick
up where I left off", "continue from yesterday", "what were we doing". It runs in two
modes:

- **Save** — reconstructs the session from `git` plus the conversation, then writes a
  cold-reader summary: what you were doing, progress so far, problems hit and how they
  were resolved, what was implemented, key knowledge/gotchas, current state, and the
  concrete **next steps** (the first item is the literal next action).
- **Resume** — finds the latest handover, reconciles it against the current `git`
  state so a stale snapshot can't mislead, and briefs you to continue from the next step.

Notes live in **temp memory outside the repo** (`~/.claude/handovers/<project>/`),
kept as timestamped history, so the codebase and git stay clean and handovers can be
pruned freely once consumed. A bundled script (`scripts/handover.py`) owns all the
path/file mechanics.

> Distinct from `wrap-up` and permanent memory: wrap-up makes the *repo* safe to leave;
> permanent memory holds *durable* facts for every future session; a handover is
> *disposable working state* for resuming one in-flight task.

### `meeting-agenda` — client-ready agenda for an upcoming meeting

Turns what the project already knows — plus the few facts only you can supply — into a
tidy, decision-led agenda you can send. Instead of a generic "intro / update / AOB"
template, it reads the project for the *real* open decisions, risks, and milestones and
builds the running order from those.

**Trigger it** by typing `/toolkit:meeting-agenda`, or by saying you've got a meeting
coming up — "draft an agenda", "what should we cover with the client", "agenda for
Thursday's call", "prep for the kickoff". It asks for the few essentials it can't infer
(purpose, attendees, length, format) in one short batch, mines the project for topics
that need *this* audience, then builds a timed running order — each item tagged
**[Decision] / [Discussion] / [Update] / [Info]** with an owner and a minute budget that
fits the slot — opening on the objective and closing on next steps. It outputs the agenda
plus a short covering note, surfaces the assumptions it made and any gaps, and leaves the
sending to you.

> Distinct from `workshop` (internal idea stress-testing, not a client deliverable) and
> `handover` (resuming your own work, not running a meeting).

### `contradictions` — find where the work disagrees with itself, or with the world

A deliberate integrity pass over a body of work. It catches the conflicts a linear read
misses — a figure in the brief that stops matching the deck, a launch date given two ways,
a recommendation that quietly reverses an earlier finding — and, in verify mode, claims
that are simply *wrong*: an unchecked statistic or market size now load-bearing in a
client deliverable.

**Trigger it** by typing `/toolkit:contradictions`, or by asking to "check for
contradictions / inconsistencies", "does anything here conflict", "sanity-check the
numbers", "fact-check this", "verify these claims". It runs in two modes:

- **Internal** (default) — a semantic scan for self-contradiction: figures that don't
  reconcile, dates or statuses that disagree across docs, reversed positions, terms
  defined two ways. It clusters claims by subject and rules out apparent gaps that scope
  or timing explains, so it doesn't cry wolf.
- **External / verify** — extracts the project's checkable claims and web-searches them,
  returning a verdict per claim (Supported / Contradicted / Unsupported / Outdated) with
  the source and date.

A bundled scanner (`scripts/extract_claims.py`) finds the candidate claims with `file:line`
provenance so nothing is missed on a large project. It reports findings ranked by
severity, with the conflicting passages cited side by side and a proposed resolution — and
never edits the project's claims on its own judgement.

> Distinct from `wrap-up` (a light end-of-session check that docs match the code that just
> changed) and `desk-research` (which gathers *new* supporting evidence rather than
> auditing the claims already made).

## Adding a new skill

1. Copy `SKILL_TEMPLATE.md` into a new folder:
   `skills/<your-skill-name>/SKILL.md`
2. Fill in the `name`, `description`, and instructions.
3. Keep any helper scripts or reference files in that same folder.
4. Commit and push. Bump the `version` in `.claude-plugin/plugin.json`
   when you want to cut a release others pull.

The fastest way to author one is the built-in **skill-creator** skill — run
`/skill-creator` and it will scaffold and refine the `SKILL.md` interactively.

## Conventions

- `name` is kebab-case and becomes the invocation name (`/toolkit:name`).
- The `description` is the *only* text Claude uses to decide when to auto-trigger
  a skill — make it specific about both **what** it does and **when** to use it.
