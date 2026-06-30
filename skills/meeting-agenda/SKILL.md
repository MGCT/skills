---
name: meeting-agenda
description: Draft a clear, client-ready agenda for an upcoming meeting, grounded in the current project. Use this whenever the user types /meeting-agenda, or says they have a meeting/call/workshop/review/kickoff coming up and wants help preparing — "draft an agenda", "what should we cover with the client", "agenda for Thursday's call", "prep for the kickoff", "put together a running order", "I'm meeting <client> about <X>, help me structure it". Reads the project (briefs, notes, open decisions, milestones, risks) to populate real topics, asks for the few essentials it can't infer (purpose, attendees, length, format), allocates time, tags each item as decision/discussion/update, and outputs a tidy agenda the user can send. Distinct from /workshop (internal idea stress-testing, not a client deliverable) and from /handover (resuming your own work, not running a meeting).
argument-hint: "[who the meeting is with / what it's about]"
allowed-tools: Read Grep Glob
---

# Meeting agenda

A good agenda does two jobs at once: it tells attendees what the meeting is *for*, and
it quietly drives the meeting toward the outcomes you need. A weak one is a list of
topics; a strong one is a sequence of **decisions and discussions with time against
each**, ordered so the meeting builds momentum and ends on clear next steps. This skill
turns what the project already knows — plus the few facts only you can supply — into the
strong kind, ready to paste into an email or a calendar invite.

The leverage is in *grounding*. You don't want a generic "Introductions / Project update
/ AOB" template; you want an agenda whose items are the real open decisions, the genuine
risks, and the actual milestones of *this* project. So the skill reads the project first
and proposes topics that matter, rather than asking you to supply them.

Know what this is *not*:

- **Not [[workshop]].** Workshop is internal: it stress-tests your own thinking with
  pushback and parallel agents. A meeting agenda is outward-facing — a deliverable you
  send to a client to structure time you'll spend together. If the user wants to *develop*
  ideas, that's workshop; if they want to *run a meeting about* them, that's this.
- **Not minutes or a follow-up.** This is prep, written before the meeting. Capturing what
  was decided afterwards is a different job.

## Steps

### 1. Establish the essentials (ask, don't assume)

An agenda built on guessed facts is worse than none — it misleads the people you send it
to. Before drafting, make sure you know:

- **Purpose** — the one outcome that makes this meeting worth holding. If the user hasn't
  said, ask. Everything else hangs off this.
- **Attendees & audience** — who's in the room (client-side and your side), and how senior.
  This sets tone and depth.
- **When & how long** — date/time and the total minutes you're allocating. Time budget
  drives everything downstream.
- **Format** — in person, video, or call; that changes what's realistic (e.g. screen-share
  walkthroughs, breakout discussion).

Pull what you can from the argument and the conversation; ask only for what's genuinely
missing, in one short batch rather than a slow interrogation. If the user gives you almost
nothing ("agenda for the client call"), it's fine to propose a draft from the project and
flag the assumptions you made for them to correct.

### 2. Mine the project for real topics

Read the project for the substance that should be on the agenda:

- **Open decisions** the client needs to make (these are the backbone — a meeting that
  produces decisions was worth holding).
- **Milestones / status** worth reporting since the last touchpoint.
- **Risks, blockers, and dependencies** that need the client's input or sign-off.
- **Questions for the client** — anything the project is waiting on.
- **Anything due to be shown** — deliverables, prototypes, findings ready to walk through.

Favour items that need *this audience* in *this meeting*. Park anything that could be
handled async — don't pad the agenda to fill time.

### 3. Build the running order

Sequence for momentum, and put time against every item so the meeting stays on track:

- Open with a one-line **objective** and a quick orientation, not a long preamble.
- Front-load the items that need the freshest attention — usually the key **decision**.
- Tag each item so the room knows the mode: **[Decision]**, **[Discussion]**, **[Update]**,
  or **[Info]**. People prepare differently for "approve this" than "FYI".
- Give each item an **owner** and a realistic minute budget. Sum them and leave slack —
  an agenda that needs 75 minutes for a 60-minute slot will overrun and frustrate.
- Close with **next steps / actions** and a short AOB. End on who-does-what-by-when.

### 4. Output

Produce a clean agenda in the format below, plus — if the user's sending it — a one or two
line covering note they can put in the email. Keep the language client-appropriate: crisp,
concrete, free of internal jargon and project shorthand the client won't know.

```markdown
# <Meeting title> — <client / project>

**Date:** <date, time, timezone>  **Duration:** <n> min  **Format:** <in person / video / call>
**Attendees:** <names / roles>

**Objective:** <the single outcome this meeting exists to produce.>

**Pre-reads:** <links / docs to review beforehand, or "none">

| # | Time | Item | Mode | Lead |
|---|------|------|------|------|
| 1 | 5m | Welcome & objectives | Info | <you> |
| 2 | 15m | <real topic from the project> | Decision | <name> |
| 3 | 15m | <real topic> | Discussion | <name> |
| 4 | 10m | <update> | Update | <name> |
| 5 | 10m | Next steps & actions | Decision | <you> |
| 6 | 5m | AOB | Discussion | all |

**Desired outcomes:** <the decisions/sign-offs you need to leave with.>
```

Then surface, briefly: the **assumptions** you made (so the user can correct them), and
any **gaps** — a decision the project implies is needed but for which you couldn't find
enough context. Don't invent detail to fill a gap; name it.

## Notes & conventions

- **Ask before you assume, but don't stall.** If one or two essentials are missing, ask.
  If you can draft a credible agenda and flag the assumptions, do that rather than blocking.
- **Decisions are the backbone.** The best agenda item is one that ends with the client
  having decided something. Lead with those; relegate pure updates.
- **Time is the honest constraint.** Always budget minutes and always leave slack. An
  agenda that can't fit its slot is a planning error you're handing to the client.
- **Client voice, not project shorthand.** Expand internal acronyms, drop the war stories,
  and write as the client will read it.
- **Propose, don't send.** Produce the draft and the covering note; the user sends it. If
  they ask, you can also produce a calendar-ready plain-text version.
