from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DATABASE_PATH = Path(__file__).parent / "database" / "sentinelscan.db"


def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(database_path)) as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 100),
                hostname TEXT NOT NULL,
                scope_description TEXT NOT NULL CHECK(length(scope_description) BETWEEN 1 AND 1000),
                exclusions_json TEXT NOT NULL DEFAULT '[]',
                authorization_reference TEXT,
                authorization_confirmed INTEGER NOT NULL CHECK(authorization_confirmed = 1),
                is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
                created_at TEXT NOT NULL,
                deactivated_at TEXT
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_targets_active_hostname
                ON targets(hostname) WHERE is_active = 1;

            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                actor TEXT NOT NULL,
                details_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record_audit_event(
    connection: sqlite3.Connection,
    event_type: str,
    details: dict[str, Any],
) -> None:
    connection.execute(
        """
        INSERT INTO audit_events (event_type, actor, details_json, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            event_type,
            "local-operator",
            json.dumps(details, ensure_ascii=False, sort_keys=True),
            utc_now(),
        ),
    )
