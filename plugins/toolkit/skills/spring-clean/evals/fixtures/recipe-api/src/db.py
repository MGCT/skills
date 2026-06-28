"""SQLite helpers for recipe-api."""
import sqlite3
from datetime import datetime

DB_PATH = "recipes.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, ingredients TEXT, instructions TEXT,
                created_at TEXT
            )"""
        )


def list_recipes():
    with _conn() as c:
        return c.execute("SELECT * FROM recipes").fetchall()


def get_recipe(rid):
    with _conn() as c:
        return c.execute("SELECT * FROM recipes WHERE id = ?", (rid,)).fetchone()


def create_recipe(title, ingredients, instructions):
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO recipes (title, ingredients, instructions, created_at) "
            "VALUES (?, ?, ?, ?)",
            (title, ingredients, instructions, datetime.utcnow().isoformat()),
        )
        return cur.lastrowid
