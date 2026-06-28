# Spring-clean plan: etl-pipeline

I surveyed the repo and built the plan below. **Nothing has been changed yet** — this
is a survey -> plan -> approve -> apply workflow, and the source reorg plus the secret
issue both need your sign-off before I touch anything.

## Current state

- 11 tracked files, all sitting flat in the repo root. No `.gitignore`.
- Six Python modules form a clean extract -> transform -> load pipeline wired by
  `main.py`; one test file (`test_pipeline.py`) also lives in the root.
- No junk, no superseded/`_old` copies, no stale files. Docs are small and healthy
  (`CLAUDE.md` 10 lines, `README.md` 8 lines) — they just describe the flat layout, so
  they'll need reconciling with any reorg.
- **Two real problems beyond layout:** `.env` is committed to git with what look like
  **live production secrets**, and `pyyaml` is declared in `requirements.txt` but never
  imported.

## Proposed changes

### Source reorganization (higher risk — review carefully)

The root is flat but the code is already well-factored, so the tidy is mostly about
giving it a home. I traced every import (all are flat top-level imports) and I'm
confident the full reference set is below — this is a small, fully-traceable graph.

Proposed layout:

```
etl/
  __init__.py        (new, empty — makes it a package)
  main.py
  extract.py
  transform.py
  load.py
  config.py
  helpers.py
tests/
  test_pipeline.py
README.md
CLAUDE.md
requirements.txt
.gitignore           (new)
```

- [ ] `git mv` `main.py extract.py transform.py load.py config.py helpers.py` -> `etl/`
- [ ] `git mv test_pipeline.py` -> `tests/test_pipeline.py`
- [ ] create `etl/__init__.py` (empty)

**Follow-on reference edits (must land in the same step as the moves):**

- [ ] `etl/main.py`: `from extract import ...` / `from transform ...` / `from load ...` /
      `from config ...`  ->  `from .extract import fetch_records`,
      `from .transform import clean_records`, `from .load import write_csv`,
      `from .config import OUTPUT_PATH`
- [ ] `etl/extract.py`: `from config import SOURCE_URL` -> `from .config import SOURCE_URL`
- [ ] `etl/transform.py`: `from helpers import normalise_name` -> `from .helpers import normalise_name`
- [ ] `tests/test_pipeline.py`: `from transform import clean_records` -> `from etl.transform import clean_records`

**Run-command changes (the package can no longer be run as a loose script):**

- [ ] `python main.py` -> `python -m etl.main` (update both `README.md` and `CLAUDE.md`)
- [ ] tests: run with `python -m pytest` from the repo root (so `etl` is importable)

**Verification:** after applying, I'd run `python -m pytest` and a smoke import of
`etl.main` to prove nothing dangles. The test only exercises `transform` (no network),
so it's a clean signal.

If you'd rather keep things runnable as plain scripts, the lighter alternative is to
move the modules under `src/` without converting to a package — but that leaves the
imports flat and doesn't really improve how the code is run, so I'd recommend the
package layout above.

### CLAUDE.md / docs (low risk, but tied to the moves)

Neither doc is bloated, so this is reconciliation, not trimming:

- [ ] `CLAUDE.md`: update the per-file bullets to the new `etl/` paths and change the
      run/test commands to `python -m etl.main` / `python -m pytest`.
- [ ] `README.md`: change `python main.py` -> `python -m etl.main`.

### .gitignore (new, low risk)

- [ ] add `.gitignore` covering `.env`, `__pycache__/`, `*.pyc`, and `output.csv`
      (the default `OUTPUT_PATH` the pipeline writes to the working dir).

## Flagged for your call (no change made — these need your decision)

- **`.env` is committed with live-looking secrets — treat as the top priority.**
  It contains `DB_PASSWORD=pr0d-Wr1ter-9f3a` and `API_KEY=sk-live-9aQ2xR7tLm04vB`, and
  it's been in git since the initial commit. Recommended remediation (I did not run any
  of this — it changes tracking and the secrets should be rotated by a human):
    1. **Rotate those credentials now** — assume they're compromised the moment they
       hit the repo. The DB password and the `sk-live-` API key both look real.
    2. `git rm --cached .env` to stop tracking it, and add it to `.gitignore`.
    3. Commit a `.env.example` with the keys but no values, so the required vars are
       documented.
    4. Note that `git rm --cached` only stops *future* tracking — the secrets remain in
       history. Purging them needs `git filter-repo` / BFG and a force-push, which is
       disruptive on a shared repo; flagging it as a separate decision.
- **`pyyaml==6.0.1` looks unused.** No `import yaml` / `yaml` reference anywhere in the
  tree (only `requests` and `pandas` are imported). Likely safe to drop from
  `requirements.txt`, but confirm nothing external (a deploy step, a sibling repo) relies
  on it being installed before removing.

## Already tidy (checked, no action needed)

- No disposable junk (caches, `.DS_Store`, logs, build artifacts) in the tree.
- No superseded / `_old` / `_v2` / backup copies; no empty or near-empty files.
- No stale-by-mtime files.
- The module code itself is clean and well-factored — the only source issue is *where*
  it lives, not how it's written.
- `requests` and `pandas` are both genuinely used; only `pyyaml` is in question.

## How I'd like to proceed

Tell me which sections to apply — you can approve all, some, or none. My suggested order
once you sign off: (1) add `.gitignore`, (2) the `.env` untracking (you handle rotation),
(3) the source reorg + reference edits together, (4) doc updates, then (5) run
`python -m pytest` to verify. I won't move anything until you say go.
