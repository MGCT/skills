---
name: roadmap-doc
description: Build a clear, client-ready roadmap from a project's goals, workstreams, and milestones — a strategic view of direction and priorities over time, not a date-precise schedule. Use whenever the user types /roadmap-doc, or asks to "create / draft / put together a roadmap", "lay out the phases", "show the plan over the next few quarters", "what's the roadmap for this", "map out the milestones for the client". It reads the project for goals, workstreams, milestones, dependencies and status, asks you to confirm anything it can't infer (it never invents dates or commitments), then organises it into time horizons and workstreams with honest status and a short narrative of the journey. Outputs a polished markdown roadmap now; a designed PDF export follows once the document toolchain is in place. Distinct from /timeline (the date-precise schedule — when each thing happens, with dependencies, as Excel + a visual) and /meeting-agenda; it composes with both.
argument-hint: "[project or the horizon to cover, e.g. 'next 3 quarters']"
allowed-tools: Read Grep Glob
---

# Roadmap doc

A roadmap answers a different question from a schedule. A schedule says *when each task
happens*; a roadmap says *where we're going, in what order, and why* — the handful of
themes and milestones that show a client the journey from here to the goal. The skill of
it is altitude: enough structure to be credible and committed-to, not so much false
precision that it becomes a brittle list of dates you'll be held to. This builds the
roadmap from what the project already knows, confirms the gaps with you rather than
guessing, and lays it out so a client can see the shape of the plan at a glance.

The danger with roadmaps is invented certainty. A date you put on a slide becomes a
promise the moment the client reads it. So this skill is deliberate about the line between
what the project *states*, what it *implies*, and what nobody has decided yet — and it asks
you about the third rather than filling it in.

Know what this is *not*:

- **Not [[timeline]].** A timeline is the date-precise schedule: when each piece of work
  happens, who owns it, what depends on what — rendered as Excel plus a visual. A roadmap
  is the altitude above that: themes, horizons, and the strategic milestones that show
  direction. They share the same source material and compose well — roadmap for the
  "where are we going" conversation, timeline for the "are we on track" one. If the user
  wants exact dates and dependencies, route to timeline.
- **Not [[meeting-agenda]].** That structures a single meeting; this is a standing artifact
  about the whole engagement.

## 1. Gather the raw material

Read the project for everything a roadmap is built from:

- **Goal / vision** — the one outcome the roadmap drives toward. Lead the doc with it.
- **Workstreams / themes** — the parallel tracks of work (these become the swimlanes).
- **Milestones** — the meaningful waypoints, with any stated target dates and current
  **status** (done / in progress / planned / at risk).
- **Dependencies & sequencing** — what must happen before what. These shape the order and
  are often where the real risk lives.
- **Constraints & scope** — budget gates, fixed deadlines, and anything explicitly out of
  scope or parked.

## 2. Confirm the gaps — never invent commitments

Roadmaps are full of *implied* timing the project never actually pinned down. Before
drafting, separate the three kinds of information and **ask the user about the unknowns**
in one short batch rather than filling them in:

- **Stated** — the project says it plainly. Use as-is.
- **Implied** — you can infer it from sequencing or dependencies. Use it, but mark it as
  an assumption.
- **Undecided** — nobody has committed. *Ask*, or place it on a coarse horizon ("Later")
  and flag it — do not fabricate a date, an owner, or a commitment.

A roadmap that confidently shows a date nobody agreed to is worse than one with an honest
"TBC", because the client will hold you to it.

## 3. Structure it

Choose the shape that fits the engagement and the audience:

- **Horizons** — *Now / Next / Later*, or by quarter (Q3 / Q4 / H1 next year). Best when
  exact dates aren't fixed; communicates direction without over-promising.
- **Swimlanes** — workstream × horizon grid. Best when several tracks run in parallel and
  the client needs to see them side by side.
- **Maturity / phases** — Crawl → Walk → Run, or named phases. Best for a capability being
  built up over time.

Place milestones into the structure with their status, show the key dependencies (so the
sequencing logic is visible), and call out what's **parked / out of scope** — a roadmap
that hides its cuts misleads. Add a one or two line narrative of the journey so the doc
reads as a story, not just a grid.

## 4. Output

Produce a polished markdown roadmap in roughly this shape, adapting structure to the
project:

```markdown
# <Project> — Roadmap

**Goal:** <the single outcome this drives toward.>
**Horizon covered:** <e.g. now → end of next year>   **Status as of:** <date>

> <1–2 line narrative: the journey from where we are to the goal.>

## Now  (<period>)
- **<Workstream>** — <milestone> · _<status>_  <(assumption) if inferred>

## Next  (<period>)
- **<Workstream>** — <milestone> · _planned_   <depends on: …>

## Later  (<period / TBC>)
- **<Workstream>** — <milestone> · _planned_

## Dependencies & sequencing
- <X must complete before Y> …

## Parked / out of scope
- <what was deliberately excluded, so it's explicit>

## Assumptions & open questions
- <every inferred date/commitment, and everything still TBC with the client>
```

Close by surfacing the **assumptions and open questions** prominently (so the user can
correct them before this reaches a client), and offer the **`/timeline`** handoff if they
want the date-precise schedule underneath this roadmap.

> **Designed PDF — pending the document toolchain.** For now the output is polished
> markdown. Once the Phase 0 render approach is in place (HTML+CSS → PDF), this same
> structure renders to a designed, client-ready PDF; the content logic here doesn't change.

## Principles

- **Direction over dates.** Lead with the goal and the why. A roadmap's job is to show
  where the work is heading and in what order — not to be a calendar.
- **Never invent a commitment.** Stated, implied, and undecided are three different things.
  Ask about the undecided; mark the implied as an assumption; only the stated stands
  unqualified. A fabricated date becomes a promise.
- **Coarse beats falsely precise.** "Next quarter" you can stand behind beats a specific
  date you can't. Use horizons when the schedule genuinely isn't fixed.
- **Show dependencies and what's parked.** The sequencing logic and the scope cuts are
  where a roadmap earns trust. Hiding them flatters the plan and misleads the reader.
- **Status honestly.** done / in progress / planned / at risk — not everything-green. A
  roadmap that can't show a slip can't be trusted when it shows progress.
- **Propose, don't commit.** It's a draft the user owns and sends. Surface the assumptions
  so they can be corrected before anyone external sees it.
