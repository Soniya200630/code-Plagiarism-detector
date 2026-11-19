"""Tiny SQLite storage (swap for MySQL/PostgreSQL later if your guide insists)."""
import json
import sqlite3
import time
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "plagiarism.db"


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with closing(_conn()) as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS submissions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, code TEXT NOT NULL, created REAL);
            CREATE TABLE IF NOT EXISTS reports(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                a_id INTEGER, b_id INTEGER, data TEXT, created REAL);
        """)
        c.commit()


def add_submission(name: str, code: str) -> int:
    with closing(_conn()) as c:
        cur = c.execute("INSERT INTO submissions(name, code, created) VALUES(?,?,?)",
                        (name, code, time.time()))
        c.commit()
        return cur.lastrowid


def get_submission(sid: int):
    with closing(_conn()) as c:
        row = c.execute("SELECT * FROM submissions WHERE id=?", (sid,)).fetchone()
        return dict(row) if row else None


def list_submissions(ids=None, with_code=False):
    cols = "id, name, code" if with_code else "id, name"
    with closing(_conn()) as c:
        rows = [dict(r) for r in c.execute(f"SELECT {cols} FROM submissions ORDER BY id")]
    if ids is not None:
        keep = set(ids)
        rows = [r for r in rows if r["id"] in keep]
    return rows


def clear_all():
    with closing(_conn()) as c:
        c.executescript("DELETE FROM submissions; DELETE FROM reports;")
        c.commit()


def save_report(a_id: int, b_id: int, report: dict) -> int:
    with closing(_conn()) as c:
        cur = c.execute("INSERT INTO reports(a_id, b_id, data, created) VALUES(?,?,?,?)",
                        (a_id, b_id, json.dumps(report), time.time()))
        c.commit()
        return cur.lastrowid


def get_report(rid: int):
    with closing(_conn()) as c:
        row = c.execute("SELECT * FROM reports WHERE id=?", (rid,)).fetchone()
        return json.loads(row["data"]) if row else None
