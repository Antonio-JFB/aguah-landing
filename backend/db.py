import sqlite3
from contextlib import contextmanager

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT UNIQUE NOT NULL,
  email         TEXT,
  password_hash TEXT NOT NULL,
  full_name     TEXT,
  cliente       TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'client',
  is_active     INTEGER NOT NULL DEFAULT 1,
  created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(SCHEMA)


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_user_by_username(username: str) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)
        ).fetchone()


def upsert_user(
    username: str,
    password_hash: str,
    cliente: str,
    role: str = "client",
    full_name: str | None = None,
    email: str | None = None,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name, cliente, role)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                email = excluded.email,
                password_hash = excluded.password_hash,
                full_name = excluded.full_name,
                cliente = excluded.cliente,
                role = excluded.role,
                is_active = 1
            """,
            (username, email, password_hash, full_name, cliente, role),
        )
