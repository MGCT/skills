# claude-skills

A Claude Code **plugin marketplace** holding MESH's custom skills for marketing
analytics and data science work. Install it once and the skills are available in
any project, on any machine.

## Repository layout

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json          # declares the marketplace + which plugins it offers
├── plugins/
│   └── mesh-skills/              # the plugin (a bundle of skills)
│       ├── .claude-plugin/
│       │   └── plugin.json        # plugin manifest
│       └── skills/
│           └── <skill-name>/
│               └── SKILL.md       # one folder per skill
├── SKILL_TEMPLATE.md             # copy this to start a new skill
└── README.md
```

## Installing the skills

From inside Claude Code:

```
/plugin marketplace add markthompson/claude-skills      # or the git URL
/plugin install mesh-skills@claude-skills
```

Then invoke a skill with `/mesh-skills:<skill-name>`, or let Claude trigger it
automatically based on the skill's `description`.

After editing skills locally, pick up changes without restarting:

```
/plugin reload-plugins
```

## Adding a new skill

1. Copy `SKILL_TEMPLATE.md` into a new folder:
   `plugins/mesh-skills/skills/<your-skill-name>/SKILL.md`
2. Fill in the `name`, `description`, and instructions.
3. Keep any helper scripts or reference files in that same folder.
4. Commit and push. Bump the `version` in `plugins/mesh-skills/.claude-plugin/plugin.json`
   when you want to cut a release teammates pull.

The fastest way to author one is the built-in **skill-creator** skill — run
`/skill-creator` and it will scaffold and refine the `SKILL.md` interactively.

## Conventions

- `name` is kebab-case and becomes the invocation name (`/mesh-skills:name`).
- The `description` is the *only* text Claude uses to decide when to auto-trigger
  a skill — make it specific about both **what** it does and **when** to use it.
- Follow MESH output conventions in skill instructions (e.g. report
  percentage-point lift rather than odds ratios; single numbers with plausible ranges).
