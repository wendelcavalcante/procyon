from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SQLiteConnectionFactory:
    """
    Small connection factory for SQLite persistence.

    It returns a new connection per operation. This keeps usage simple and avoids
    sharing sqlite3 connection objects across threads in web contexts.
    """

    database_path: Path | str

    def connect(self) -> sqlite3.Connection:
        database_path = Path(self.database_path)

        if database_path.parent != Path("."):
            database_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(str(database_path))
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection