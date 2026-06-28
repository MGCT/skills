# Spring-clean: recipe-api

Done. I tidied the loose files, removed dead code, and rewrote the bloated `CLAUDE.md`
to match what the project actually is. Tests still pass (`2 passed`) and `src/app.py`
still imports cleanly.

## What I removed (dead weight / cruft)

| File | Why |
|------|-----|
| `src/handlers_old.py` | Dead code. Imports from `core`, which no longer exists — it would crash if loaded. `handlers.py` superseded it. Nothing references it. |
| `scratch.py` | One-off json-encoder doodle. CLAUDE.md itself said "can probably go." |
| `debug_output.txt` | Stray debug capture from a manual session. |
| `server.log` | Runtime log artifact — shouldn't be in version control. |
| `Screenshot 2025-01-03 at 11.04.png.txt` | Leftover screenshot placeholder from an old CORS debugging session. |
| `.DS_Store` | macOS Finder cruft. |

Before deleting anything I confirmed the source still imports and the test suite
passes, so the removals are safe.

## What I added

- **`.gitignore`** — so the cruft doesn't creep back: `__pycache__/`, `*.pyc`,
  `.pytest_cache/`, `*.db` (the local SQLite file), `*.log`, and `.DS_Store`.

## What I left alone

- **`requirements.txt`** — it's a single comment documenting that the project is
  stdlib-only. Harmless and mildly useful, so I kept it.
- **`README.md`** — short and accurate already.
- **`src/app.py`, `src/db.py`, `src/handlers.py`, `tests/test_handlers.py`** — the
  real, working code. Untouched.

## CLAUDE.md — the big one

The old file was 139 lines / ~5.6 KB of running brain-dump, and most of it was
actively misleading. I rewrote it down to ~2.1 KB of accurate, current facts.

Key corrections (the old file would have sent you down the wrong path):

- **Said it was Flask.** It is not — the server is pure `http.server` from the stdlib.
- **Said `core.py` was "THE most important file."** `core.py` does not exist. Neither
  do `models.py`, `utils.py`, or `cache.py` — all listed in the architecture section.
- **Claimed `app.py` lived in the repo root.** It's `src/app.py`.
- **Listed PUT and DELETE endpoints as if they worked.** Only `GET /recipes`,
  `GET /recipes/<id>`, and `POST /recipes` are implemented. The unbuilt ideas moved
  into a "not yet implemented" note.
- **Was unsure how to run the app.** The answer is `python src/app.py`.
- **Referenced a `deploy.sh`** that isn't in the repo, and a `handlers_old.py` it
  admitted should be deleted (now done).

I kept the genuinely useful institutional knowledge — the SQLite "database is locked"
and transaction-commit gotchas, the datetime-serialization workaround, conventions, and
the manual deploy steps — just trimmed and reorganized.

## Verification

- `python -m pytest tests` → `2 passed`
- `python -c "import app"` (from `src/`) → clean import, no errors

## Note

I did **not** commit anything — changes are staged/working-tree only, so you can review
the diff first. `git status --short`:

```
D  .DS_Store
 M CLAUDE.md
D  "Screenshot 2025-01-03 at 11.04.png.txt"
D  debug_output.txt
D  scratch.py
D  server.log
D  src/handlers_old.py
?? .gitignore
```
