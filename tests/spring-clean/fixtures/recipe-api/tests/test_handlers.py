"""Smoke tests for the db layer behind the handlers."""
import os
import tempfile

import db


def setup_module(_):
    db.DB_PATH = os.path.join(tempfile.mkdtemp(), "test.db")
    db.init_db()


def test_create_and_get():
    rid = db.create_recipe("Toast", "bread", "toast it")
    row = db.get_recipe(rid)
    assert row[1] == "Toast"


def test_list():
    db.create_recipe("Soup", "water", "boil")
    assert len(db.list_recipes()) >= 1
