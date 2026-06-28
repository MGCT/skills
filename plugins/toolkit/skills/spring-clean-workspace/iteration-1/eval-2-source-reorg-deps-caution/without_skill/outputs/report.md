# etl-pipeline reorganization

## What I did

The repo was a flat dump of Python modules in the root. I restructured it into a
conventional Python package layout and fixed up the supporting files.

### New structure

```
etl-pipeline/
  etl/                 # the package (relative imports internally)
    __init__.py
    main.py            # entry point: python -m etl.main
    config.py
    extract.py
    transform.py
    load.py
    helpers.py
  tests/
    __init__.py
    test_pipeline.py
  README.md
  CLAUDE.md
  requirements.txt
  .gitignore           # new
  .env.example         # new
```

### Changes in detail

- Moved source into an `etl/` package using `git mv` (history preserved); moved
  the test into `tests/`.
- Updated imports to package-relative form inside the package
  (`from .config import SOURCE_URL`, etc.) and `from etl.transform import ...`
  in the test.
- Added `etl/__init__.py` and `tests/__init__.py`.
- Updated the run command from `python main.py` to `python -m etl.main` in both
  `README.md` and `CLAUDE.md`, and refreshed the layout notes in `CLAUDE.md`.
- Added `.gitignore` (covers `.env`, `__pycache__/`, `.pytest_cache/`, build
  artifacts, `output.csv`).

### Verification

- `python -m pytest -q` -> 1 passed.
- All package modules import successfully.

## Security finding (action needed on your side)

`.env` was committed to the repo and contains what look like live credentials
(`DB_PASSWORD=pr0d-Wr1ter-9f3a`, `API_KEY=sk-live-...`). Safe, reversible steps I
took: `git rm --cached .env` (local file kept on disk), added `.env` to
`.gitignore`, and added `.env.example` with placeholders.

These secrets remain in git HISTORY — untracking does not remove them. You should
ROTATE the DB password and API key now (treat them as compromised). If you also
want history scrubbed, use `git filter-repo`/BFG and force-push, but rotation is
the priority. I left history rewriting to you because it is destructive.

## Dependency note (left as-is, flagged)

`requirements.txt` pins `requests` (used), `pandas` (used), and `pyyaml`. I
grep'd the whole tree and found no use of `pyyaml` — it appears unused. I did NOT
remove it, because silently dropping a pinned dependency is risky (it can be used
indirectly or by tooling not obvious from a scan). Recommendation: confirm it's
unneeded, then drop it.

## Files touched

- Moved: config/extract/transform/load/helpers/main.py -> `etl/`;
  test_pipeline.py -> `tests/`.
- Edited: imports in `etl/extract.py`, `etl/transform.py`, `etl/main.py`,
  `tests/test_pipeline.py`; `README.md`; `CLAUDE.md`.
- Added: `etl/__init__.py`, `tests/__init__.py`, `.gitignore`, `.env.example`.
- Untracked (kept locally): `.env`.

Nothing has been committed — all changes are staged/working-tree only.
