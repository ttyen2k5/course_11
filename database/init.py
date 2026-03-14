from pathlib import Path
import sqlite3
from sqlite3 import Connection

from flask import Flask, current_app, g


BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "database" / "init.sql"
DEFAULT_DB_PATH = BASE_DIR / "database" / "course.db"


def connect_db(db_path: str | Path = DEFAULT_DB_PATH) -> Connection:
    resolved_path = Path(db_path)
    if not resolved_path.is_absolute():
        resolved_path = (BASE_DIR / resolved_path).resolve()

    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(resolved_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_db() -> Connection:
    if "db" not in g:
        database_path = current_app.config.get("DATABASE", str(DEFAULT_DB_PATH))
        g.db = connect_db(database_path)
    return g.db


def close_db(_error=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        db.executescript(schema_file.read())
    db.commit()


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()