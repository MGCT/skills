---
name: timeline
description: Build a date-precise project timeline as a styled Excel schedule (with a month-by-month Gantt) plus a designed PDF visual, from the project's milestones and dates. Use whenever the user types /timeline, or asks to "build / create a timeline", "lay out the schedule", "put the milestones on a Gantt", "when does each phase land", "give me a delivery schedule I can track against", "timeline for the client / for the plan". It reads the project for workstreams, milestones, dates, dependencies and status, then — crucially — prompts you to confirm any date, duration, or dependency it can't infer rather than inventing one; anything still undecided is shown as "Unscheduled / TBC", not given a made-up date. Outputs an .xlsx schedule and a PDF visual. Distinct from /roadmap-doc (the higher-altitude strategic view — direction and priorities by horizon, not exact dates), which it composes with; and from /meeting-agenda.
argument-hint: "[project, or the window to schedule]"
allowed-tools: Read Grep Glob Bash
---

# Timeline

A timeline answers the operational question a roadmap doesn't: *when does each thing
happen, in what order, and what is it waiting on?* It's the artifact you track delivery
against. Its value is precision — but precision is also its danger, because a Gantt bar
drawn on a guessed date looks exactly as authoritative as one drawn on an agreed one. So
this skill is built around a single discipline: schedule only what's known or confirmed,
and surface everything else as explicitly unscheduled rather than quietly inventing dates.

The model does the judgement — reading the project, working out what the milestones are,
and *confirming the gaps with you*. A bundled script does the deterministic rendering: a
formatted Excel schedule with a month-grid Gantt coloured by status, and a separate block
for anything still TBC.

Know what this is *not*:

- **Not [[roadmap-doc]].** A roadmap is the altitude above this: themes, horizons (Now /
  Next / Later), and the strategic story — deliberately coarse on dates. A timeline is the
  schedule underneath it: specific months, dependencies, owners, something you track
  against. Same source material, different question. If the user wants direction and
  priorities, route to roadmap-doc; if they want dates and a Gantt, stay here. They pair
  well — roadmap for the "where are we going" conversation, timeline for "are we on track".
- **Not [[meeting-agenda]].** That structures one meeting; this schedules the whole plan.

## 1. Gather and confirm

Read the project for the schedule's raw material — workstreams, milestones, any stated
start/end dates or durations, dependencies, owners, and status. Then separate what you
*know* from what you're *guessing*, and **ask the user about the guesses in one batch**:

- **Stated** — a date or duration the project gives plainly. Use it.
- **Inferable** — derivable from a dependency ("tooling starts when the data foundation is
  stable"). You may schedule it, but **mark it as an assumption** so it's visibly not a
  commitment.
- **Undecided** — nobody has set it. Do **not** invent a date. Confirm it with the user if
  they know, otherwise leave it **Unscheduled / TBC**.

A Gantt bar on a fabricated date is worse than an honest "TBC", because the client reads
the bar as a promise. When in doubt, ask or leave it unscheduled.

## 2. Assemble the spec

Put the confirmed schedule into a JSON spec for the builder. Dates are month-granular
(`YYYY-MM` or `YYYY-MM-DD`); items with a valid `start` **and** `end` land on the Gantt,
anything else falls to the TBC block automatically.

```json
{
  "title": "<Project> — Delivery Timeline",
  "status_as_of": "<YYYY-MM-DD>",
  "items": [
    {"workstream": "Data foundation", "milestone": "Single searchable store",
     "owner": "Acme", "start": "2026-04", "end": "2026-09",
     "status": "in progress", "depends_on": ""},
    {"workstream": "Adoption", "milestone": "UK pilot", "status": "planned",
     "assumption": "date TBC — not agreed with client"}
  ]
}
```

Status values render with their own colour: `done`, `in progress`, `planned`, `at risk`.
Use `assumption` for an inferred date (it shows a ⚠ note) and for the reason a TBC item
isn't scheduled.

## 3. Build the Excel schedule

```
python <skill-dir>/scripts/build_xlsx.py spec.json timeline.xlsx
```

It writes a titled schedule table (workstream, milestone, owner, start, end, status), a
month-by-month Gantt grid with status-coloured bars, an **Unscheduled / TBC** block, and a
legend — frozen panes so the task columns stay visible while scrolling the months.

## 4. Build the PDF visual

For a client-facing one-pager, author an HTML visual and render it. Inline the shared
`scripts/house-style.css`, then add a small `<style>` block for the timeline bars on top
of it (a horizontal track per workstream, or a clean milestone list with dates and status
pills). Then:

```
python <skill-dir>/scripts/render_pdf.py timeline.html timeline.pdf
```

It uses a headless Chrome/Edge already on the machine (no install). **Swap the
house-style palette for the client's or Mesh's brand** before sending.

Save the `.xlsx`, `.html`, and `.pdf` where the user keeps deliverables, and tell them
where they are.

## 5. Close

Surface the **assumptions and TBC items** prominently — the inferred dates and everything
left unscheduled — so the user can confirm or correct them before this is tracked against
or sent. Offer the **`/roadmap-doc`** handoff if they want the strategic view above this
schedule.

## Bundled files

- `scripts/build_xlsx.py` — JSON spec → styled `.xlsx` with a month-grid Gantt and a TBC
  block. Needs `openpyxl`. `python scripts/build_xlsx.py spec.json out.xlsx`.
- `scripts/render_pdf.py` — HTML → PDF via headless Chrome/Edge (no install), for the
  visual one-pager.
- `scripts/house-style.css` — shared deliverable print style; inline it, then add
  timeline-bar styles on top. Swap the palette for brand.

## Principles

- **Never draw a bar on a guessed date.** Stated, inferable, undecided are three different
  things. Schedule the first, flag the second as an assumption, and leave the third
  visibly TBC. A fabricated bar is read as a commitment.
- **Precision where you have it, honesty where you don't.** The TBC block is a feature, not
  a gap — it's how the timeline stays trustworthy.
- **Dependencies are where the risk lives.** Show what waits on what; a schedule that hides
  sequencing flatters the plan.
- **Status honestly.** done / in progress / planned / at risk — colour-coded, not all
  green. A timeline that can't show a slip can't be trusted on progress.
- **Two outputs, one truth.** The Excel is for tracking, the PDF for showing — both built
  from the same confirmed spec, so they never disagree.
- **Propose, don't commit.** The user owns the dates and sends the deliverable; surface the
  assumptions so they're corrected first.
