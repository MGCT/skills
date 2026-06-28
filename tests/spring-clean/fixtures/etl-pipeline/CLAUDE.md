# etl-pipeline

Extract -> transform -> load. Everything currently sits flat in the repo root.

- `main.py` wires the three stages together.
- `extract.py` / `transform.py` / `load.py` are the stages.
- `config.py` reads settings from the environment.
- `helpers.py` holds shared utilities.

Run with `python main.py`. Tests: `pytest`.
