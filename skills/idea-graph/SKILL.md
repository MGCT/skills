---
name: idea-graph
description: Turn a project's knowledge into a navigable idea graph — a standalone, self-contained interactive HTML deliverable that lives in the project and is meant to be shared to explain the thinking to others. Use whenever the user types /idea-graph, or asks to "map the ideas / concepts", "build an idea graph / concept map / knowledge map", "show how these ideas connect", "visualise the thinking", "make something to explain this to the team / client". It reads the project to identify the concepts (nodes) and their relationships (edges), groups them into themes, and produces an interactive HTML map (pan / zoom / click) plus a Mermaid source — then reports what the structure reveals: the central ideas (hubs), the themes (clusters), and the gaps (orphan ideas with no links, or a graph that splits into disconnected pieces). Distinct from /workshop (which develops and pressure-tests thinking interactively — idea-graph maps thinking that already exists into a shareable artifact) and from /roadmap-doc & /timeline (time-structured; an idea graph is concept-structured, with no time axis).
argument-hint: "[project, or the theme to map]"
allowed-tools: Read Grep Glob Bash
---

# Idea graph

A body of project thinking is a web, but it's written down as a line — pages of notes and
docs read top to bottom. The connections that make it make sense (this segment is why we
chose that tier; this risk threatens that recommendation) are real but invisible, scattered
across documents. An idea graph makes the web visible: it lays the concepts out as nodes,
draws the relationships as labelled edges, and turns "you'd have to read everything and hold
it in your head" into something a person can see at a glance and explore. That's why it's
built as a **standalone deliverable that lives in the project** — a self-contained HTML file
that opens in any browser, offline, and can be handed to a teammate or client to explain the
thinking without a walkthrough.

The value isn't the picture; it's the **structure the picture reveals**. Laying the ideas
out exposes the central ones everything hangs off (hubs), the natural themes (clusters), and
— most usefully — the gaps: an idea that connects to nothing, or a set of ideas that floats
apart from the rest. So this skill always pairs the artifact with a short read-out of what
the graph shows, rather than leaving you to interpret a hairball.

Know what this is *not*:

- **Not [[workshop]].** Workshop *develops and pressure-tests* thinking interactively, with
  pushback and parallel agents. Idea-graph *maps thinking that already exists* into a
  shareable artifact. They compose: map the concept space, then workshop an idea the map
  shows is isolated or load-bearing.
- **Not [[contradictions]].** Contradictions audits claims for conflict and error. An idea
  graph just shows structure — though if you draw a "contradicts" edge between two ideas,
  that's a cue to run contradictions on them.
- **Not [[roadmap-doc]] or [[timeline]].** Those are time-structured — what happens when. An
  idea graph has no time axis; it's about how concepts relate, not their schedule.

## 1. Read the project and identify the ideas

Read the project and pull out its substance as a graph:

- **Nodes — the ideas.** The concepts that matter: goals, segments, options, decisions,
  recommendations, evidence, risks, assumptions, products, themes. Give each a short,
  human label and (where it helps a reader) a one-line `summary`.
- **Edges — the relationships.** How the ideas actually relate, *labelled* so the link
  means something: `supports`, `targets`, `depends on`, `contradicts`, `part of`,
  `leads to`, `evidence for`. An unlabelled web explains nothing.
- **Clusters — the themes.** Tag each node with the theme it belongs to (e.g. Segment,
  Product, Market, Decision, Risk). These become the colour groups and the legend.

Be **faithful to the source** — nodes and edges come from what the project actually says.
Don't invent relationships to make a tidier graph; a missing connection is a finding, not a
defect to paper over. If the project is large, agree a focus with the user (the whole thing,
or one theme) rather than mapping everything thinly.

## 2. Assemble the spec

Put the graph into a JSON spec for the builder:

```json
{
  "title": "<Project> — Idea Map",
  "nodes": [
    {"id": "subs", "label": "Subscription product", "cluster": "Product",
     "summary": "The recurring-revenue offer at the centre of the strategy."}
  ],
  "edges": [
    {"source": "subs", "target": "younger", "label": "targets"}
  ]
}
```

`id`s are short keys you reference in edges; `label` is what the reader sees.

## 3. Build the deliverable

```
python <skill-dir>/scripts/build_graph.py spec.json idea-map.html
```

It computes a stable, seeded layout (the same spec always lays out the same way), writes a
**self-contained interactive HTML** (inline SVG + JS: pan, zoom, click an idea to see its
connections and summary, search, cluster legend — no external dependencies), and a
`idea-map.mmd` **Mermaid source** for pasting into docs or GitHub. It then prints
**analytics** you use in the read-out: the clusters, the most-connected ideas (hubs), the
orphans (no links), and how many disconnected components the graph has.

Save the deliverable **into the project** where the user keeps shared artifacts (it's
meant to sit there), with a clear name; if you're unsure where, ask rather than guessing.
Don't overwrite an existing file. For a static version to drop in a deck, optionally render
a snapshot with the bundled `scripts/render_pdf.py idea-map.html idea-map.pdf`.

## 4. Read out what the graph reveals

Don't just hand over a file. Using the analytics, tell the user what the structure shows:

- **Hubs** — the central ideas everything hangs off. If the hub isn't what you'd expect,
  that's interesting.
- **Clusters** — the themes, and whether they're balanced or one dominates.
- **Orphans & splits** — ideas with no connections, or a graph that breaks into separate
  components. Each is a question: is this a *missing link* (the thinking is connected but
  undocumented) or a *disconnected idea* (something raised but never tied into the thesis)?
  This is the most valuable output — surface it plainly.

Offer handoffs: `/workshop` to develop an idea the map shows is isolated or pivotal,
`/contradictions` if two connected ideas look like they conflict.

## Bundled files

- `scripts/build_graph.py` — JSON spec → self-contained interactive HTML + Mermaid source,
  with a seeded layout and printed cluster/hub/orphan analytics. Pure stdlib.
  `python scripts/build_graph.py spec.json out.html`.
- `scripts/render_pdf.py` — optional static PDF snapshot of the HTML via headless
  Chrome/Edge (no install).

## Principles

- **A map, not decoration.** The point is the structure it reveals — hubs, clusters, gaps.
  Always write the read-out; a graph handed over without interpretation is a puzzle, not a
  deliverable.
- **Orphans and splits are findings.** An idea connected to nothing is the most informative
  thing on the page — a missing link or a disconnected thought. Surface it, don't tidy it
  away.
- **Edges must mean something.** Label every relationship. An unlabelled hairball looks
  busy and says nothing.
- **Faithful to the source.** Nodes and edges come from what the project says. Inventing
  links to make the graph look complete defeats its purpose.
- **A standalone artifact.** Self-contained HTML that opens offline and is built to be
  shared. It lives in the project; name it clearly and don't clobber existing files.
- **Focus beats completeness.** A readable map of one theme beats an unreadable map of
  everything. Scope it with the user when the project is large.
