# unit-convert

A small library for converting between units (length, mass, temperature).

## Layout
- `src/convert.py` — the public `convert(value, from_unit, to_unit)` entry point.
- `src/units.py` — the unit tables and conversion factors.
- `tests/test_convert.py` — pytest suite.

## Run tests
```
pytest
```

## Conventions
- Pure functions, no global state.
- Temperatures are special-cased (offset, not just a factor) in `convert.py`.
- Add a new unit by extending the tables in `units.py`; no other file needs touching.
