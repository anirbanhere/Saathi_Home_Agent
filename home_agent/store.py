"""Short SQLite transactions serialize approvals and inventory changes."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .catalog import SEED_STOCK
from .errors import AppError


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY, kind TEXT, actor TEXT, session TEXT, status TEXT,
                args TEXT, result TEXT, created_at TEXT, updated_at TEXT)""")
            db.execute("""CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY, session TEXT, request_id TEXT, fingerprint TEXT,
                language TEXT, user_text TEXT, response TEXT, created_at TEXT,
                UNIQUE(session, request_id))""")
            db.execute("CREATE TABLE IF NOT EXISTS inventory (name TEXT PRIMARY KEY, quantity REAL, unit TEXT)")
            db.execute("""CREATE TABLE IF NOT EXISTS inventory_events (
                id TEXT PRIMARY KEY, name TEXT, delta REAL, unit TEXT, source TEXT, estimated INTEGER,
                created_at TEXT)""")
            db.execute("CREATE TABLE IF NOT EXISTS receipts (id TEXT PRIMARY KEY, fingerprint TEXT, result TEXT)")
            db.execute("""CREATE TABLE IF NOT EXISTS stock_corrections (
                id TEXT PRIMARY KEY, name TEXT, quantity REAL, unit TEXT, result TEXT)""")
            if not db.execute("SELECT 1 FROM settings WHERE key='seeded'").fetchone():
                for name, quantity, unit in SEED_STOCK:
                    db.execute("INSERT INTO inventory VALUES (?, ?, ?)", (name, quantity, unit))
                    db.execute("INSERT INTO inventory_events VALUES (?, ?, ?, ?, ?, 0, ?)",
                               ("seed:" + name, name, quantity, unit, "Demo opening stock (estimate)", now()))
                db.execute("INSERT INTO settings VALUES ('seeded', 'yes')")

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA foreign_keys = ON")
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def decode(row):
        if row is None:
            raise AppError("Task not found.", 404, "NOT_FOUND")
        result = dict(row)
        result["args"] = json.loads(result["args"])
        result["result"] = json.loads(result["result"])
        return result

    def save_task(self, db, kind, actor, args, result, status="succeeded", session="", task_id=None):
        stamp = now()
        task_id = task_id or uuid4().hex
        db.execute("""INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET status=excluded.status, args=excluded.args,
                    result=excluded.result, updated_at=excluded.updated_at""",
                   (task_id, kind, actor, session, status, json.dumps(args), json.dumps(result), stamp, stamp))
        return self.decode(db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())

    @staticmethod
    def stock_event(db, event_id, name, delta, unit, source, estimated=False):
        if db.execute("SELECT 1 FROM inventory_events WHERE id=?", (event_id,)).fetchone():
            return
        old = db.execute("SELECT * FROM inventory WHERE name=?", (name,)).fetchone()
        if old and old["unit"] != unit:
            raise AppError(f"{name} is tracked in {old['unit']}; use a compatible unit.")
        balance = round((old["quantity"] if old else 0) + delta, 4)
        if balance < 0:
            raise AppError(f"Insufficient {name}. Correct inventory or add groceries before marking cooked.", 409, "INSUFFICIENT_STOCK")
        db.execute("INSERT INTO inventory VALUES (?, ?, ?) ON CONFLICT(name) DO UPDATE SET quantity=excluded.quantity",
                   (name, balance, unit))
        db.execute("INSERT INTO inventory_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (event_id, name, delta, unit, source, int(estimated), now()))
