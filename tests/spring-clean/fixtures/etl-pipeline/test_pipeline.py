"""Tests for the transform step (no network)."""
from transform import clean_records


def test_clean_drops_nameless_and_titlecases():
    raw = [{"name": "  alice "}, {"name": None}, {"name": "bob"}]
    out = clean_records(raw)
    names = [r["name"] for r in out]
    assert names == ["Alice", "Bob"]
