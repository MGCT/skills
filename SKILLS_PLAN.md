# Skills build plan — review draft

Planning doc for nine proposed skills. Not committed; edit freely or delete once
decisions are made. Companion to `README.md` and `SKILL_TEMPLATE.md`.

## Decisions locked (from review)

- **Target = a client/agency project folder** opened in Claude Code: notes, briefs,
  docs, some data and code. Heterogeneous and prose-heavy. Skills read whatever is in
  the folder; several will need to read `.docx`/`.pdf`/`.xlsx` inputs, not just markdown.
- **Deliverables = PDF + Excel files** (client-ready, email-attachable), not just
  on-screen Artifacts.
- **`/evals` = AI/LLM product evals** (engineering), kept on a separate track.

## Verdict summary

| # | Skill | Verdict | Phase |
|---|-------|---------|-------|
| 1 | `/contradictions` (+ folded fact-check) | ✅ Built (Phase 1) | 1 |
| 2 | `/fact-checker` | Don't build standalone — mode of #1 | — |
| 3 | `/desk-research` | Build (specialise existing `deep-research`) | 3 |
| 4 | `/idea-graph` | Build later | 4 |
| 5 | `/workshop` | Build — flagship | 2 |
| 6 | `/timeline` | Build | 3 |
| 7 | `/roadmap-doc` | Build | 2→3 |
| 8 | `/meeting-agenda` | ✅ Built (Phase 1) | 1 |
| 9 | `/evals` | Build — separate track | 4 |

> **Phase 1 status (built):** `/meeting-agenda` (`skills/meeting-agenda/`, no script) and
> `/contradictions` (`skills/contradictions/` + `scripts/extract_claims.py`), each with
> `tests/<name>/evals.json`; `contradictions` ships a planted-contradiction fixture
> (`tests/contradictions/fixtures/acme-insight/`). Plugin version bumped to `0.2.0`.
> Next up: Phase 2 (`/workshop`, then `/roadmap-doc` content logic).

## Build order

- **Phase 0 — Output toolchain.** Pick the render approach and prove it on Windows
  (one designed PDF + one styled Excel). Decide vendor-vs-shared (see Open decisions).
  Blocks Phase 3.
- **Phase 1 — Foundations + quick win.** `/meeting-agenda` (warm-up, no infra), then
  `/contradictions` (internal + external/verify modes).
- **Phase 2 — Flagship, no infra.** `/workshop`, then draft `/roadmap-doc` content
  logic (defer its rendering to Phase 3).
- **Phase 3 — Designed deliverables (need Phase 0).** `/timeline`, `/roadmap-doc`
  rendering, `/desk-research`.
- **Phase 4 — Higher-uncertainty.** `/idea-graph`, then `/evals`.

## Phase 0 — output toolchain (the unblocker)

**Recommended stack**
- Author every designed document as **HTML + print CSS** (`@page`, page-break control).
  Reuse `frontend-design` / `artifact-design` for the look.
- **HTML → PDF: Playwright Chromium** (`pip install playwright && playwright install
  chromium`), via a small `render_pdf.py`. Bundles its own browser → no system-lib hunt.
  Fallback: headless Edge/Chrome `--print-to-pdf` (Edge ships on Windows).
- **Excel: openpyxl** (styling, number formats, native charts) via `xlsx.py` helpers.
- **Reading inputs:** `python-docx` for `.docx`, `pdfplumber` for `.pdf`, `openpyxl`/
  `pandas` for spreadsheets. Add only as a skill needs them.

**Deliverable house style** (define once, reuse): cover block (project, date, author),
consistent type scale, Mesh palette, page headers/footers, source/assumptions footnotes.

**Decision needed:** vendor the render scripts into each deliverable skill (install-safe
under `npx skills -s <one>`) **or** create one `document-production` skill the deliverable
skills call (DRY, but breaks single-skill install). See Open decisions.

## Per-skill specifications

### 1. `/contradictions`  *(Phase 1)*
- **Purpose:** on-demand integrity pass over a body of work — surfaces where the
  project argues against itself or states something false.
- **Modes:** `internal` (semantic conflict scan: claims that conflict, numbers that
  don't reconcile, a recommendation contradicting an earlier finding, stale-vs-current
  statements) and `external`/`verify` (extract checkable claims → web-search → flag
  false/unsupported, with sources).
- **Inputs:** project docs (md/docx/pdf), optionally a scoped subset via args.
- **Output:** ranked report — each item with severity, the conflicting passages
  (`file:line`), and a proposed resolution. Proposes only; never edits.
- **Scripts:** `extract_claims.py` (gather candidate factual statements).
- **NOT:** `wrap-up` checks doc-vs-code currency in passing at session end on file
  metadata; `/contradictions` is a deep, on-demand semantic pass over content meaning.
- **Eval cases:** a doc set with a planted numeric contradiction, a reversed
  recommendation, and one externally-false claim.

### 2. `/fact-checker` — folded into #1
Standalone it's too thin and overlaps both `/contradictions` and `/desk-research`.
Ship as the `external`/`verify` mode of `/contradictions`.

### 3. `/desk-research`  *(Phase 3)*
- **Purpose:** build supporting evidence for the project's thesis and produce a
  client-ready research write-up.
- **Approach:** thin specialisation of the existing `deep-research` skill — do not
  rebuild the search/verify engine. Add: (a) project-grounding (read the project first
  to know the thesis and the gaps), (b) a "supporting evidence" framing, (c) designed
  PDF + markdown output (Phase 0).
- **Inputs:** project knowledge + an optional research question/thesis via args.
- **Output:** cited markdown + designed PDF; an evidence table (claim → source →
  strength). Flags where evidence is thin or contradicts the thesis.
- **NOT:** open-ended `deep-research`; this is anchored to an existing project's claims.

### 4. `/idea-graph`  *(Phase 4)*
- **Purpose:** turn project knowledge into a concept graph and use it to surface
  non-obvious connections, clusters, and **gaps/orphans** — analysis, not just a picture.
- **Output:** interactive HTML (self-contained) + a Mermaid/JSON file; a short written
  read-out of clusters and gaps. (PDF export optional via Phase 0.)
- **Open question:** what consumes the graph downstream — `/workshop`? a deliverable?
  Decide before building so the output format is fit-for-purpose.

### 5. `/workshop`  *(Phase 2 — flagship)*
- **Purpose:** interactively stress-test and develop ideas, using parallel agents.
- **Flow:** scope the topic with the user → fan out agents over distinct facets
  (assumptions, risks, alternatives, evidence, second-order effects) in parallel →
  synthesise into pointed questions, devil's-advocate pushback, and candidate ideas →
  iterate. Can hand off to `/idea-graph` or `/desk-research`.
- **Infra:** none (orchestration + dialogue). Plays to multi-agent strengths.
- **NOT:** a passive Q&A; it pushes back and tests, and it's interactive (asks the user).
- **Eval note:** hard to eval mechanically; test on scenario quality + that it actually
  challenges rather than agrees.

### 6. `/timeline`  *(Phase 3)*
- **Purpose:** build a project timeline as Excel + a designed visual (PDF).
- **Flow:** extract milestones/dates/dependencies from the project → **prompt to
  confirm anything it can't infer** (the quality differentiator) → render.
- **Output:** `.xlsx` (openpyxl: dated rows, optional Gantt-style chart) + designed PDF.
- **Shares:** milestone-extraction logic with `/roadmap-doc`.

### 7. `/roadmap-doc`  *(Phase 2 content → Phase 3 render)*
- **Purpose:** a designed roadmap from project phases/milestones.
- **Flow:** extract phases/themes/milestones/owners → confirm gaps/assumptions →
  render designed PDF.
- **Relationship to `/timeline`:** near-identical extraction; a roadmap is a themed
  timeline. Build the two together; keep as separate skills for clean triggering.

### 8. `/meeting-agenda`  *(Phase 1 — quick win)*
- **Purpose:** draft a client-ready agenda for an upcoming meeting.
- **Inputs:** meeting purpose / attendees / duration (args + conversation) + project
  context. Asks before assuming attendees or objectives.
- **Output:** objectives → timed agenda items → owners → pre-reads, as clean markdown
  (PDF optional). Lowest infra — good first build.

### 9. `/evals`  *(Phase 4 — separate track)*
- **Purpose:** scaffold AI/LLM product evals — define what's measured, build a dataset,
  pick metrics/scorers, wire it up.
- **Leans on:** the repo's `tests/` convention and `skill-creator`'s benchmarking.
- **Flow:** scope the capability under test → design cases (`tests/<project>/`) →
  choose scoring (exact/judge/rubric) → run + report variance.
- **NOT:** research/strategy validation (a different skill if you ever want that).

## Open decisions before I write SKILL.md files

1. **Vendor vs shared render scripts** (Phase 0) — self-contained per skill, or one
   `document-production` skill? Affects how `npx skills -s <one>` behaves.
2. **Confirm Playwright** as the PDF engine, or prefer Edge-headless / another tool.
3. **`/idea-graph` downstream consumer** — what uses the graph?
4. **Build `/timeline` + `/roadmap-doc` as a pair?** (shared extraction) — recommended.
