---
# Copy this whole folder to: plugins/toolkit/skills/<your-skill-name>/SKILL.md
# Required:
name: my-skill-name            # kebab-case; becomes /toolkit:my-skill-name
description: One or two sentences describing WHAT this does and WHEN to use it. This is the only text Claude reads to decide whether to auto-trigger the skill, so be specific about the trigger conditions and the kind of request it matches.

# --- Optional fields (delete the ones you don't need) ---
# when_to_use: Extra triggering hints, appended to description. Combined cap ~1,536 chars.
# argument-hint: "[project-name]"        # autocomplete hint shown after the slash command
# disable-model-invocation: false         # true = only the user can invoke it (no auto-trigger)
# user-invocable: true                     # false = hidden from the / menu, Claude-only
# allowed-tools: Read Grep Glob Bash       # pre-approved tools while the skill runs
# model: claude-opus-4-8                   # override the model for this skill
# effort: high                             # low | medium | high | xhigh | max
# context: fork                            # run in an isolated subagent context
# agent: Explore                           # subagent type when context: fork
# paths: "**/*.csv"                        # only activate when these files are in play
---

# My Skill Name

Write the instructions Claude should follow when this skill runs. Be direct and
imperative — this is a prompt, not documentation.

## When to use this
- Bullet the concrete situations that should trigger it.

## Steps
1. First do this.
2. Then do that.
3. Output the result in <this format>.

## Notes / conventions
- Reference any house style, e.g. "report percentage-point lift, not odds ratios."
- Keep supporting files (scripts, reference data) alongside this SKILL.md in the
  same folder and refer to them by relative path.
