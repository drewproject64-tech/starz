from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class Storage:
    def __init__(self, path: str = "data/starz_promosyon.db") -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def add_submission(self, user_id: int, username: str | None, text: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO submissions (user_id, username, text, created_at) VALUES (?, ?, ?, ?)",
                (user_id, username, text, datetime.now(timezone.utc).isoformat()),
            )
            connection.commit()
            return int(cursor.lastrowid)
