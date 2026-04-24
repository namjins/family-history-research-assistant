"""SQLite connection + migration helper."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def open_db(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Open a connection, commit/rollback the transaction, and *close* the
    connection on exit.

    Prefer this over ``with connect(...) as conn`` — ``sqlite3.Connection``'s
    own context manager commits/rolls back but does not close the connection,
    leaking file descriptors. This helper adds the close and also commits on
    non-exception exit so callers don't need a trailing ``conn.commit()``.
    """
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Path) -> None:
    """Create the database and apply schema. Idempotent."""
    schema_sql = SCHEMA_PATH.read_text()
    with open_db(db_path) as conn:
        conn.executescript(schema_sql)
        conn.execute(
            "INSERT OR REPLACE INTO schema_meta(key, value) VALUES ('version', '1')"
        )
        conn.commit()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
