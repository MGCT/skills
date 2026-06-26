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

- **wrap-up** — end-of-session housekeeping. Reconstructs what the session did,
  checks the codebase is up to date and internally consistent (stale docs,
  cross-file contradictions, duplication, dead files), runs the project's read-only
  checks (tests/lint), scans for code loose ends and risky/secret-bearing changes
  before commit, and flags anything worth saving to Claude's persistent memory —
  then proposes the fixes for approval (it never edits, commits, or pushes on its own).

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
