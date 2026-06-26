# claude-skills

A Claude Code **plugin marketplace** holding a collection of custom skills. Install
it once and the skills are available in any project, on any machine.

## Repository layout

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json          # declares the marketplace + which plugins it offers
├── plugins/
│   └── toolkit/                  # the plugin (a bundle of skills)
│       ├── .claude-plugin/
│       │   └── plugin.json        # plugin manifest
│       └── skills/
│           └── <skill-name>/
│               ├── SKILL.md       # one folder per skill
│               └── scripts/       # optional bundled helper scripts
├── SKILL_TEMPLATE.md             # copy this to start a new skill
└── README.md
```

## Installing the skills

From inside Claude Code:

```
/plugin marketplace add markthompson/claude-skills      # or the git URL
/plugin install toolkit@claude-skills
```

Then invoke a skill with `/toolkit:<skill-name>` (e.g. `/toolkit:wrap-up`), or let
Claude trigger it automatically based on the skill's `description`.

After editing skills locally, pick up changes without restarting:

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

## Adding a new skill

1. Copy `SKILL_TEMPLATE.md` into a new folder:
   `plugins/toolkit/skills/<your-skill-name>/SKILL.md`
2. Fill in the `name`, `description`, and instructions.
3. Keep any helper scripts or reference files in that same folder.
4. Commit and push. Bump the `version` in `plugins/toolkit/.claude-plugin/plugin.json`
   when you want to cut a release others pull.

The fastest way to author one is the built-in **skill-creator** skill — run
`/skill-creator` and it will scaffold and refine the `SKILL.md` interactively.

## Conventions

- `name` is kebab-case and becomes the invocation name (`/toolkit:name`).
- The `description` is the *only* text Claude uses to decide when to auto-trigger
  a skill — make it specific about both **what** it does and **when** to use it.
