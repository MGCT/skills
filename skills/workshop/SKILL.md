---
name: workshop
description: An interactive thinking partner that develops and pressure-tests an idea, decision, or plan with you — using parallel agents to examine it from several angles at once, then engaging you with the sharpest questions rather than agreeing. Use whenever the user types /workshop, or wants to think something through hard: "help me workshop / think through this", "pressure-test / stress-test this idea", "poke holes in this", "play devil's advocate", "challenge my thinking", "red-team this plan", "war-game this", "I'm trying to decide between X and Y", "is this a good idea", "develop this concept with me", "what am I missing". It frames the goal, fans out agents over distinct lenses (assumptions, risks, alternatives, evidence, the strongest counter-case, the stakeholder view), synthesises into a few pointed questions and the pushback most likely to matter, then iterates with you toward a landing and concrete next steps. Internal thinking work, not a client deliverable — distinct from /meeting-agenda (an agenda to send), /desk-research (gathering new sourced evidence) and /contradictions (auditing existing claims). It can hand off to those when the thinking is done.
argument-hint: "[the idea, decision, or plan to workshop]"
---

# Workshop

Thinking alone has a blind spot: you test an idea against the same mind that produced it,
so it tends to survive. A good workshop breaks that loop. It looks at the idea from
several angles at once — what has to be true for it to work, how it fails, what the
alternatives are, what a skeptical client would say — and then puts the sharpest of those
back to you as questions, not verdicts. The value isn't a report; it's *better thinking* —
an idea that's been pushed on hard and is stronger, narrower, or abandoned for a better
one by the end.

This skill is deliberately **interactive** and deliberately **frictional**. It asks you
questions and pushes when your answers are thin, because agreement is the one outcome that
wastes the session. It uses parallel agents to widen the aperture — each takes a different
lens simultaneously — but it never dumps six reports on you; it converges to the few things
that actually change the answer and works them through with you.

Know what this is *not*:

- **Not [[meeting-agenda]] or any deliverable.** The output is sharper thinking, not a
  document to send a client. If you want to *operationalise* what you concluded, hand off
  to meeting-agenda, roadmap-doc, or desk-research at the end.
- **Not [[desk-research]].** Workshop reasons with what's known plus the model's analysis;
  it doesn't run an exhaustive, sourced research project. When a point turns on evidence
  you don't have, *name that* and offer to kick off desk-research — don't fake the depth.
- **Not [[contradictions]].** Contradictions audits the claims a project already makes for
  internal conflict or factual error. Workshop develops *new* thinking. (Mid-workshop you
  might notice a contradiction — flag it and point at that skill.)
- **Not a yes-man, and not a passive Q&A.** If it just validates your idea or waits to be
  asked, it has failed. Productive friction is the whole point.

## 1. Frame the workshop

Spend a moment getting the frame right — a workshop aimed at the wrong target wastes the
fan-out. Establish, from the argument, the conversation, and a quick read of the project:

- **What's on the table** — the idea, decision, concept, or plan. Get it stated crisply.
- **What "done" looks like** — what should be true by the end? A sharper concept? A
  go/no-go? A choice between options? A plan that survives scrutiny? This sets the mode:
  *develop* a nascent idea, *choose* between options, *pressure-test* a leaning decision,
  or *stress-test* a plan/pitch before it ships.
- **Context and constraints** — what the project already establishes, and the real
  constraints (budget, timeline, audience, non-negotiables) the thinking must respect.

If the framing is genuinely unclear, ask one or two sharp questions before fanning out.
Don't over-interview — a credible frame plus stated assumptions is enough to start.

## 2. Fan out — examine the idea from several angles at once

Spawn a panel of agents **in parallel** (in a single batch), each taking one lens, each
returning a short structured response. Pick lenses to fit the mode; this is a strong
default panel — use 3 for a quick spar, 5–6 for a high-stakes decision:

- **Assumptions** — what must be true for this to work? Which premises are unexamined,
  shaky, or doing too much load-bearing work?
- **Risks & failure modes** — how does this go wrong? What's the *most likely* way it
  fails, and the most *damaging*?
- **Alternatives** — what are two or three genuinely different approaches not currently on
  the table? Is there a simpler or sharper one?
- **Evidence & precedent** — who has tried something like this, and what does it suggest?
  (Use the project and, where useful, the web — but stay light; deep sourcing is
  desk-research's job.)
- **Devil's advocate / strongest counter-case** — the best good-faith argument *against*,
  steelmanned, not a cheap shot.
- **Stakeholder lens** — how does the skeptical client / exec / end-user actually react?
  Where does it lose them?

Give each agent the same return contract: its **two or three sharpest findings**, the
**one question it would put to the user**, and the **single strongest point** (the thing
that most changes the picture). Tell them to be specific and to argue in good faith — a
lens that hedges is useless.

## 3. Synthesise and engage

Do **not** relay the panel. Read across the agents and converge to what matters, then turn
it into a conversation:

- **The 2–3 sharpest questions** — the ones whose answers most change the outcome. Lead
  with these and actually ask the user.
- **The pushback that matters most** — the single thing most likely to sink this, stated
  plainly, steelmanned.
- **Candidate ideas / options to test** — including any the alternatives lens generated,
  framed so they can be weighed.

Then engage: put the questions to the user, react to the answers, and **push when an
answer is hand-wavy** ("that assumes X — what makes you confident?"). This is a
back-and-forth, not a delivery.

## 4. Iterate

Use the answers to go again where it's productive — and only there:

- Re-test a revised idea against the lens that threatened it.
- Spin a single focused agent on a specific new angle the conversation opened up.
- Kill options that failed, and say why, so they don't quietly creep back.

Converge toward the workshop's goal. Don't spin for its own sake — when the thinking has
stopped moving, land it.

## 5. Land it

When you've converged (or the user calls time), give a tight readout — not a transcript:

- **Where we landed** — the sharpened idea, the decision, or the chosen option.
- **What got stronger / what changed** — and the key insight or two that did the work.
- **What's still open or risky** — the honest residual: unresolved questions, thin
  evidence, live risks.
- **Next steps** — concrete and ready to act on.

Then offer the right **handoff**: `/desk-research` to shore up a point that turned on
evidence you didn't have, `/idea-graph` to map the concept space, `/contradictions` to
check the resulting position holds together, or `/roadmap-doc` / `/meeting-agenda` to turn
the conclusion into something you can act on or send.

## Principles

- **Friction is the feature.** If the user ends the session feeling only validated, the
  workshop failed. Push, in good faith, on the things that matter.
- **Fan out wide, converge hard.** Many lenses in parallel, one synthesis. Never hand the
  user the raw panel — give them the few things that change the answer.
- **Lead with the question that most changes the answer.** Not the easiest question, not
  the first — the one whose answer reshapes everything downstream.
- **Steelman before you strike.** Argue the strongest version of each position. Cheap
  objections don't sharpen anything and cost you trust.
- **Interactive, not a report.** Ask, listen, push, iterate. The user is in the room; use
  them.
- **Know the edge of what you know.** When a point turns on evidence you don't have, say
  so and offer to research it — don't manufacture confidence.
- **Match intensity to the stake.** A quick gut-check and a board-level decision deserve
  different depth. Don't run a six-agent panel on a coin-flip, or a coin-flip on a
  bet-the-company call.
- **Know when to stop.** Land the workshop on a conclusion and next steps. A workshop that
  never converges is just rumination with extra agents.
