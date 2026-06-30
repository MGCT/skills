---
name: contradictions
description: Run a deliberate integrity pass over a body of work to surface where it argues against itself or states something false. Two modes. INTERNAL (default) — a semantic scan for self-contradiction: figures that don't reconcile, dates or statuses that disagree across documents, a recommendation that reverses an earlier finding, a term defined two ways, a claim flatly contradicted elsewhere. EXTERNAL / verify — extract the project's checkable factual claims and web-search them, flagging any that are false, unsupported, or out of date, with sources. Use whenever the user types /contradictions, or asks to "check for contradictions / inconsistencies", "does anything here conflict", "are these docs consistent", "sanity-check the numbers", "fact-check this", "verify these claims", "is this still true". Reads the project's notes, briefs and docs; reports findings ranked by severity with the conflicting passages cited by file:line, and proposes resolutions — it never edits on its own. Distinct from /wrap-up (a light end-of-session check that docs match the code that just changed) and from /desk-research (which gathers NEW supporting evidence rather than auditing existing claims).
argument-hint: "[internal | verify | paths or topic to focus on]"
allowed-tools: Read Grep Glob Bash WebSearch WebFetch
---

# Contradictions

A body of work drifts out of agreement with itself as it grows. A number quoted in the
brief stops matching the number in the deck; a recommendation written in week six quietly
reverses a finding from week two; "the launch is Q3" in one doc and "Q4" in another; a
term used loosely in one place and precisely in another. Each is small on its own and
invisible in a linear read — you only catch them by holding two passages side by side.
Worse are the claims that are simply *wrong*: a market size, a statistic, an attribution
that was never checked and is now load-bearing in a client deliverable. This skill is the
deliberate pass that finds both — the project contradicting *itself*, and the project
contradicting *the world*.

It is an audit, not an edit. The output is a ranked list of findings, each showing the
conflicting passages so you can judge them, with a proposed resolution. It proposes;
**you** decide which side is right, because often only you know.

Know what this is *not*:

- **Not [[wrap-up]].** Wrap-up is a light end-of-session pass that reconciles docs with the
  code that *just changed* and gets the repo safe to leave — it catches stale references in
  passing. Contradictions is a deep, on-demand, semantic pass over the *meaning* of the
  content, run whenever you want to trust the whole corpus, not just the latest diff.
- **Not [[desk-research]].** Desk-research goes out and gathers *new* evidence to support
  the project's thesis. The verify mode here does the opposite-facing job: it takes the
  claims the project *already makes* and checks whether they hold up. One builds the
  evidence base; the other audits it.

## Two modes

Read intent and pick; when unclear, default to **internal** and offer verify as a follow-up.

- **Internal** — "check for contradictions", "is anything here inconsistent", "do these
  docs agree". Scans the project against itself.
- **External / verify** — "fact-check this", "verify these claims", "are these numbers
  right", "is this still true". Checks the project's claims against outside sources.

They compose: a thorough audit runs internal first (cheap, no network), then verify on the
externally-checkable claims that survived.

## Gather the candidates

Both modes start from the same place — the checkable statements in the project, with
provenance. Let the bundled script find them so nothing is missed and a large project
doesn't have to be read in full:

```
python <skill-dir>/scripts/extract_claims.py [PATHS] [--text] [--signals ...]
```

It walks the project's text/doc files and pulls lines carrying numbers, percentages,
money, dates, comparatives/superlatives, certainty words, or citations — tagging each with
`file:line` and the signals it matched. It reads plain-text formats natively; it **reports
binary docs (`.docx`/`.pdf`) it skipped** so you can open those directly with your own
tools rather than missing them. For a small project, reading the files yourself is fine;
the script earns its keep on large or sprawling ones.

## Internal mode: find self-contradiction

The script gives you candidates; the contradiction-spotting is yours. Work by *subject*,
not by file — a contradiction is two statements about the same thing that can't both be
true, and they usually live in different documents.

1. **Cluster** the candidate claims by what they're about: the same metric, date,
   entity, status, definition, or recommendation.
2. **Compare within each cluster** for genuine conflict:
   - **Figures that don't reconcile** — the same quantity given two values (revenue,
     sample size, market share, budget, headcount).
   - **Dates / timelines that disagree** — a milestone, deadline, or sequence stated
     differently across docs.
   - **Status mismatches** — "done" here, "in progress" there; "approved" vs "pending".
   - **Reversed positions** — a later recommendation that contradicts an earlier finding
     without acknowledging the change.
   - **Inconsistent definitions** — a key term, segment, or metric used to mean different
     things in different places.
   - **Flat contradictions** — one passage asserting X, another asserting not-X.
3. **Distinguish genuine from apparent.** Before flagging, ask whether scope or time
   explains the gap — "£4m" (UK) vs "£7m" (global), or a figure that changed because the
   project moved on. A false alarm erodes trust in the whole report. If it's plausibly
   reconcilable, say so and note what would confirm it, rather than crying contradiction.

## External / verify mode: check claims against the world

1. **Triage** the candidates into *externally verifiable* (a public statistic, a market
   size, a date, an attribution, "studies show…") versus *internal/subjective* (the
   project's own opinions, plans, or framing — not fact-checkable, skip them).
2. **Verify** each checkable claim with `WebSearch` / `WebFetch`. Prefer primary or
   authoritative sources; corroborate a surprising claim with more than one.
3. **Verdict** per claim: **Supported**, **Contradicted**, **Unsupported** (no source
   found), or **Outdated** (was true, newer data supersedes it) — each with the source
   (URL/title/date) and a confidence level. Be honest about uncertainty; "couldn't verify"
   is a finding, not a failure.

## Report

One scannable report, findings ranked by **severity** — does this change a decision or
mislead a client? A reversed recommendation in a final deck outranks a typo'd date in an
internal note. For each finding:

```markdown
## <short title of the conflict / claim>   — <severity: high | medium | low>

- **Type:** internal contradiction | external: contradicted/unsupported/outdated
- **What conflicts:**
  - `path/a.md:42` — "<the passage, quoted>"
  - `path/b.md:17` — "<the conflicting passage>"        # internal
  - or — source: <title, URL, date>                      # external
- **Why it matters:** <the decision or deliverable it affects>
- **Proposed resolution:** <which looks right and why, or "needs your call: …">
```

Close with a one-line summary (N findings: X high / Y medium / Z low), the list of binary
docs the script couldn't read (so coverage is honest), and — for verify mode — anything you
couldn't confirm either way. Then **stop and let the user decide.** Apply corrections only
on an explicit go-ahead, one at a time or as an approved batch; never rewrite the project's
claims on your own judgement.

## Principles

- **Evidence, not assertion.** Every finding shows both passages (or the source). A claim
  that something contradicts, without the two quotes side by side, is unfalsifiable noise.
- **Severity first.** Lead with the contradictions that change a decision or reach a
  client. Don't bury a load-bearing conflict under a list of trivial date typos.
- **Don't cry wolf.** Different scope, timeframe, or rounding often explains an apparent
  gap. Rule that out before flagging; a report full of false positives gets ignored.
- **You decide which side is right.** The skill surfaces and proposes; resolving a
  contradiction is a judgement about the project that belongs to the user. Propose, never
  silently edit.
- **Honest coverage.** Say what wasn't checked — binary docs not read, claims not
  verifiable, sources not found. A pass that hides its blind spots is worse than one that
  names them.
- **Cite and date external checks.** A fact-check without a source and a date is just a
  second opinion. Link it, and flag when "true" really means "was true as of <date>".
