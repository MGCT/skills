# Spring-clean plan: recipe-api

I surveyed the whole project (read-only) and have a concrete tidy-up plan below.
**Nothing has been changed yet** — this is a propose-first pass. Tell me which parts
to apply (all / some / none) and I'll execute exactly that, history-safely.

## Current state

- **13 tracked files**, 8 of them loose at the repo root. Five are clutter:
  `.DS_Store`, `server.log`, `debug_output.txt`, `scratch.py`, and a screenshot
  placeholder — none belong in version control.
- **One dead source file**: `src/handlers_old.py`. It's superseded by `handlers.py`
  and imports from a `core` module that no longer exists, so it would crash on import.
  Nothing references it.
- **`CLAUDE.md` is 138 lines and substantially wrong.** It describes a Flask app with
  `core.py`, `models.py`, `utils.py`, `cache.py`, a `deploy.sh`, and PUT/DELETE
  endpoints — *none of which exist*. The real app is a ~30-line stdlib `http.server`
  with three modules and three GET/POST endpoints. The doc is actively misleading.
- **No `.gitignore`**, which is why the OS/log junk got committed in the first place.
- Baseline is green: `pytest` passes 2/2. `README.md`, `requirements.txt`, and the
  `src/` layout are accurate and tidy.

## Proposed changes

### File organization / cleanup (low risk)

- [ ] **delete** `.DS_Store` — macOS Finder cruft, pure junk.
- [ ] **delete** `server.log` — runtime log (4 lines from a Jan 2025 session); regenerated at runtime, shouldn't be tracked.
- [ ] **add `.gitignore`** so this junk doesn't come back:
  ```
  __pycache__/
  *.pyc
  *.log
  .DS_Store
  recipes.db
  ```
  (`recipes.db` is the runtime SQLite file per `db.py` — gitignored preventatively.)

### Archive (plausibly dead — moved aside, not deleted, so it's reversible)

Proposing a new tracked `archive/` folder (via `git mv`, so history follows each file).
You can drop the whole folder later once you're sure none of it is wanted.

- [ ] **archive** `src/handlers_old.py` -> `archive/` — dead: superseded by `handlers.py`, imports a deleted `core` module, zero references. (Strong candidate for outright deletion if you prefer — git history keeps it either way.)
- [ ] **archive** `scratch.py` -> `archive/` — a 4-line JSON-encoder doodle; CLAUDE.md itself says "scratch.py was me testing something, can probably go."
- [ ] **archive** `debug_output.txt` -> `archive/` — one-off captured request output from a debug session.
- [ ] **archive** `Screenshot 2025-01-03 at 11.04.png.txt` -> `archive/` — a placeholder for a debug screenshot of a since-resolved CORS issue.

### CLAUDE.md — trim and refresh (highest-value item)

Rewrite from **138 lines -> ~50 lines**, keeping only what's true about the code as it
stands today. Proposed before/after shape:

**Cut entirely (stale or rederivable):**
- The entire "History (for context)" section — Flask-vs-FastAPI saga, `core.py`,
  `models.py`, ORM removal, Redis/`cache.py`, the spring rename. All historical noise.
- Every reference to files that don't exist: `core.py`, `models.py`, `utils.py`,
  `cache.py`, `deploy.sh`.
- The PUT and DELETE endpoints (not implemented — `app.py` only wires `do_GET`/`do_POST`).
- The `python -m recipe_api` / `DATABASE_URL` / Postgres speculation and the open
  "how do I run this?" TODO — the run command is simply `python src/app.py`.
- The TODO wishlist (search, pagination, auth, automate deploy, more tests), the
  "Random notes" section, the `handlers_old.py` "should delete this" note (we're
  doing it), and the Contact section.

**Fix to match reality:**
- Server is **Python stdlib `http.server`**, not Flask. Remove all Flask framing.
- Architecture = three real modules: `app.py` (entry point + routing), `handlers.py`
  (request handlers, JSON I/O), `db.py` (SQLite helpers).
- Endpoints: `GET /recipes`, `GET /recipes/<id>`, `POST /recipes` — the three that exist.
- Run: `python src/app.py`, port via `PORT` (no `pip install` needed — stdlib only).

**Keep (still true, earns its place):**
- One-line overview + "keep it simple, don't over-engineer" ethos.
- SQLite details: `recipes.db`, schema inline in `db.py:init_db()`, reset by deleting the file.
- Conventions: plain functions over classes, JSON errors use an `"error"` key.
- The two real gotchas: SQLite "database is locked" under concurrent writes, and
  converting `created_at` datetimes to strings before JSON encoding.
- Testing: `pytest`, tests in `tests/`.

### README.md

- [ ] No change needed — it's accurate and appropriately short (it already only lists
  the three real endpoints, unlike the old CLAUDE.md).

## Flagged for your call (no change proposed)

- **Dependencies:** `requirements.txt` correctly states stdlib-only; nothing unused, no
  lockfiles, no conflicts. Clean — no action.
- **`handlers_old.py` — archive vs delete:** I've put it under *archive* to stay
  reversible, but it's genuinely dead and broken. Say the word and I'll `git rm` it
  instead (history still preserves it).
- **`archive/` folder fate:** if you'd rather not carry an `archive/` folder at all, I
  can delete the four archived files outright instead of moving them — your call on how
  conservative to be.

## Already tidy (checked, no action)

- `src/` module layout (`app.py`, `handlers.py`, `db.py`) — clean and correctly imported.
- `tests/test_handlers.py` — passes (2/2).
- `README.md` and `requirements.txt` — accurate and concise.

## How I'll apply it (once you approve)

1. Create `.gitignore` and `archive/`.
2. `git mv` the four archive files; `git rm` `.DS_Store` and `server.log`.
3. Rewrite `CLAUDE.md` to the ~50-line version above.
4. Re-run `pytest` to confirm nothing broke, and report the result.
5. Leave it uncommitted (I won't commit or push unless you ask).

Reply with which sections to apply.
