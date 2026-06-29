---
name: desk-research
description: Gather external supporting evidence for a project's thesis and write it up as a cited, client-ready deliverable (markdown + designed PDF). Use whenever the user types /desk-research, or asks to "do some desk research", "find supporting evidence / sources / data for this", "what backs up our recommendation", "is there research / data to support X", "build the evidence base", "find papers / articles / stats on …". It reads the project first to ground the search in the actual thesis and its gaps, runs deep multi-source research via the deep-research harness (it does not re-implement search/verify), then produces a write-up with an evidence table (claim → sources → strength) — honestly flagging where evidence is thin, mixed, or contradicts the thesis. Distinct from /deep-research (open-ended research on any question — desk-research is anchored to *this* project and outputs a designed deliverable) and from /contradictions (which audits the claims the project already makes; desk-research goes out and finds new evidence for or against them).
argument-hint: "[the claim/thesis to support, or leave blank to use the project]"
---

# Desk research

Most desk research has a job narrower than "go learn about a topic": it's *find the
evidence that stands behind what we're already saying* — the stats, studies, precedents,
and data points that turn a recommendation from an assertion into a supported case a
client will trust. That means it starts from the project's thesis, not a blank page, and
it has a duty the open-ended kind doesn't: to report honestly when the evidence is thin or
points the other way, because a deliverable that only confirms is worthless the moment a
client checks it.

This skill is a **specialisation, not a reimplementation**. The hard part — fanning out
searches, fetching sources, verifying claims adversarially, synthesising with citations —
is exactly what the **`deep-research`** harness already does well. Desk-research wraps it
with three things deep-research doesn't do on its own: it **grounds** the questions in the
project, it frames the goal as **supporting (or testing) a specific thesis**, and it turns
the result into a **designed, client-ready deliverable** with an evidence table.

Know what this is *not*:

- **Not plain [[deep-research]].** Deep-research answers an open question you bring it.
  Desk-research derives the questions *from the project*, aims them at the project's
  thesis, and packages the output as a deliverable. When the user's question has nothing to
  do with the current project, that's a deep-research job — route there.
- **Not [[contradictions]].** Contradictions audits the claims the project *already makes*
  for internal conflict or factual error, using what's in front of it. Desk-research goes
  *outward* to find new evidence for or against the thesis. They're complementary: verify
  what you said with contradictions; find what backs it up with desk-research.

## 1. Ground in the project

Read the project before searching, so the research is aimed, not generic:

- **The thesis / claims that need support** — the recommendations or assertions a client
  would challenge ("younger professionals are the core subscription segment", "the market
  is growing at X"). These become the research targets.
- **What's already cited vs bare** — find the load-bearing claims with no source behind
  them; those are the priority.
- **The gaps** — what the project assumes but hasn't established.

If the project is broad or the user hasn't said which claims to back, confirm scope in a
short batch: *which* claims to support, and how deep to go (a quick evidence scan vs a
thorough sourced review). Use the argument as the thesis if one's given.

## 2. Frame the research questions

Turn the thesis into specific, researchable questions — the sharper the question, the
better the evidence. "Do younger urban professionals adopt subscription products at higher
rates than older consumers, and in what categories?" beats "subscription trends". Note for
each whether you're seeking *support*, *magnitude* (a number to cite), or a *test* of a
shaky assumption.

## 3. Run the research via deep-research

Hand the framed questions to the **`deep-research`** skill rather than rolling your own
search loop — it already does the multi-source fan-out, source-fetching, adversarial
verification, and cited synthesis. Pass the project-grounded questions as its input,
weaving in the relevant context from step 1.

> If `deep-research` isn't available in the environment, fall back to `WebSearch` /
> `WebFetch` directly — but keep its discipline: corroborate surprising claims across more
> than one source, prefer primary/authoritative sources, and capture every citation.

## 4. Build the evidence base — honestly

Organise the findings against the project's claims, and rate each. The evidence table is
the spine of the deliverable:

| Project claim | Evidence found | Source(s) | Strength |
|---------------|----------------|-----------|----------|
| <the claim> | <what the evidence says> | <title, date, link> | strong / moderate / weak / **contested** |

- **Rate strength honestly** — strong (multiple authoritative, primary, current),
  moderate, weak (single/secondary/old), or **contested** (good evidence points the other
  way). Date every source; flag anything stale.
- **Surface the exposed claims.** Where the evidence is thin or contradicts the thesis, say
  so plainly and up front — this is the most valuable part of the report, not a footnote to
  bury. A claim you couldn't support is a finding.

## 5. Produce the deliverable

Write a cited markdown report first (fast to review), then render the designed PDF. Inline
the shared `scripts/house-style.css` into the HTML and **swap the palette for the client's
or Mesh's brand**, then:

```
python <skill-dir>/scripts/render_pdf.py research.html research.pdf
```

Structure both outputs as:

- **Executive summary** — what the evidence does and doesn't support, in a few lines.
- **Evidence by theme** — the findings, each claim with its supporting (or contradicting)
  sources cited inline.
- **Evidence table** — the claim → source → strength matrix above.
- **Gaps & caveats** — what couldn't be substantiated, and what's contested or stale.
- **Sources** — the full reference list with dates and links.

Save the `.md`, `.html`, and `.pdf` where the user keeps deliverables and tell them where.

## 6. Close

Lead the wrap-up with the honest verdict: where the thesis is **well-supported** and where
it's **exposed**. Offer handoffs — `/contradictions` to check the project's own claims hold
together now, or `/workshop` to rethink a claim the evidence undercut.

## Bundled files

- `scripts/render_pdf.py` — HTML → PDF via headless Chrome/Edge (no install).
- `scripts/house-style.css` — shared deliverable print style; inline it, swap the palette
  for brand.
- The research engine is the separate **`deep-research`** skill — invoke it; don't
  duplicate it here.

## Principles

- **Anchored, not open-ended.** The project's thesis sets the questions. Generic research
  on the topic isn't the job; evidence for *these* claims is.
- **Honesty over confirmation.** Report thin and contradicting evidence prominently. A
  desk-research deliverable that only confirms collapses the first time a client checks a
  source — and misleads the team in the meantime.
- **Reuse the engine.** deep-research already does search/fetch/verify/cite. Wrap it; don't
  reinvent it.
- **Cite and date everything.** Every claim in the deliverable traces to a dated source.
  "A study showed" without a link is not evidence.
- **Strength, not just presence.** One blog post and five peer-reviewed studies are not the
  same support. Rate it so the reader knows how hard they can lean on each claim.
- **A deliverable, not a dump.** The output is client-ready: an executive summary, an
  evidence table, clean citations — proposed for the user to review and send, not pasted raw.
