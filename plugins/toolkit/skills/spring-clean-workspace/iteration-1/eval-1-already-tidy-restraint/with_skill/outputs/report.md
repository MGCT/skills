# Spring-clean plan: unit-convert

## Current state
I surveyed the whole project (6 tracked files, ~27 lines of docs). It is already
in good shape: a clean `src/` + `tests/` split, a `CLAUDE.md` (18 lines) and
`README.md` (9 lines) that are both lean and accurate to the current tree, and no
junk, no superseded/`_old` copies, no stale files. The only thing sitting loose is
a one-line `notes.md` at the root. There is genuinely very little to do here, and
the honest answer is mostly "this is already tidy."

## Proposed changes

### File organization (low risk)
- [ ] `notes.md` (root) — a single-line idea note: *"maybe add volume units
  (litres, gallons) later. not urgent."* This is the one loose file. There's no
  obvious home for it, and standing up a `docs/` folder for one line would be more
  ceremony than a project this size wants. Three ways to handle it, in order of my
  recommendation:
  - **(A, recommended) Fold the idea into the README as a one-line "Ideas / later"
    note, then `git rm notes.md`.** Keeps the thought, removes the loose root file,
    costs the docs one line. Net tidier.
  - (B) Leave `notes.md` as-is. It's harmless and self-explanatory; "loose" is
    arguably overstating a single intentional idea-note.
  - (C) `git mv notes.md docs/notes.md` (creates a `docs/` folder). Files it away
    literally, but introduces a folder holding one short file — heavier than this
    project needs.

### Archive / delete
- Nothing. No junk, caches, logs, build artifacts, or superseded copies exist.

### CLAUDE.md / docs
- **No change recommended.** `CLAUDE.md` (18 lines) is already lean and true: its
  Layout section matches `src/convert.py`, `src/units.py`, `tests/test_convert.py`
  exactly, and the Conventions notes (pure functions, temperature special-casing in
  `convert.py`, "add a unit by extending the tables in `units.py`") are all accurate
  against the code. `README.md` (9 lines) is correct — its examples
  (`convert(100,"cm","m") == 1.0`, `convert(32,"F","C") == 0.0`) match the code and
  the tests. There is no bloat or staleness to trim. Trimming further would remove
  useful, accurate signal, so I'm explicitly *not* proposing doc edits.
  - One optional micro-note tied to option A above: if you fold the volume-units idea
    into the README, that's the only doc touch — and it's an addition, not a trim.

### Source moves (higher risk)
- None. The `src/` / `tests/` layout fits the project's grain. `tests/` and `src/`
  both rely on importing `convert`/`units` as top-level modules (no package prefix),
  so moving source files would mean fixing imports for no real benefit. Leave as-is.

## Flagged for your call (no change proposed)
- **Dependencies/config:** none to flag. There's no `requirements.txt`,
  `pyproject.toml`, lockfile, or `.gitignore`. That's fine for a project this size;
  I'm not proposing to add scaffolding you didn't ask for. (If you ever want it,
  a `.gitignore` with `__pycache__/` and `.pytest_cache/` would be the natural first
  addition — flagging only, not doing.)
- **`notes.md` disposition:** which of A/B/C above you prefer is your call.

## Already tidy (checked, no action needed)
- Root: clean apart from `notes.md`; no scratch files, screenshots, logs, or exports.
- `src/`: two focused modules, clear responsibilities, no dead code or duplicates.
- `tests/`: one suite, references real functions, no stale fixtures.
- `CLAUDE.md` and `README.md`: lean, accurate, consistent with the code.
- No archive-named, backup, empty, or stale-by-age files anywhere.

---

**Recommendation:** This is a restraint case — the project is essentially already
spring-cleaned. The single actionable item is `notes.md`, and even that is minor.
My pick is **option A** (fold the one idea into the README, remove the loose note),
but B (leave it) is perfectly defensible. No doc trimming is warranted.

No changes have been made. Tell me which option for `notes.md` you'd like (A / B / C),
and I'll apply only that.
