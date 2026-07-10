from __future__ import annotations

from procyon.persistence.sqlite.connection import SQLiteConnectionFactory


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS player_states (
    player_id TEXT PRIMARY KEY,
    skill REAL NOT NULL,
    uncertainty REAL NOT NULL DEFAULT 0.50,
    engagement REAL NOT NULL,
    frustration REAL NOT NULL,
    confidence REAL NOT NULL,
    preferred_pace REAL,
    stability REAL,
    observations_count INTEGER NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS telemetry_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT,
    session_id TEXT,
    level_id TEXT NOT NULL,
    success INTEGER,
    give_up INTEGER NOT NULL,
    estimated_difficulty REAL,
    target_difficulty REAL,
    solving_time REAL,
    move_count INTEGER,
    mistake_count INTEGER,
    restart_count INTEGER,
    hint_count INTEGER,
    idle_time REAL,
    timestamp TEXT,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_telemetry_player_id
ON telemetry_summaries(player_id);

CREATE INDEX IF NOT EXISTS idx_telemetry_session_id
ON telemetry_summaries(session_id);

CREATE TABLE IF NOT EXISTS performance_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    session_id TEXT,
    level_id TEXT NOT NULL,
    estimated_difficulty REAL,
    success INTEGER,
    performance_score REAL NOT NULL,
    skill_delta REAL NOT NULL,
    engagement_delta REAL NOT NULL,
    frustration_delta REAL NOT NULL,
    confidence_delta REAL NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_observations_player_id
ON performance_observations(player_id);

CREATE INDEX IF NOT EXISTS idx_observations_session_id
ON performance_observations(session_id);

CREATE TABLE IF NOT EXISTS adaptation_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    session_id TEXT,
    target_difficulty REAL,
    previous_difficulty REAL,
    reason TEXT,
    confidence REAL,
    applied_constraints_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_adaptation_decisions_player_id
ON adaptation_decisions(player_id);

CREATE INDEX IF NOT EXISTS idx_adaptation_decisions_session_id
ON adaptation_decisions(session_id);
"""

def _column_exists(
    factory: SQLiteConnectionFactory,
    table_name: str,
    column_name: str,
) -> bool:
    with factory.connect() as connection:
        rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()

    return any(row["name"] == column_name for row in rows)


def _add_column_if_missing(
    factory: SQLiteConnectionFactory,
    table_name: str,
    column_name: str,
    column_sql: str,
) -> None:
    if _column_exists(factory, table_name, column_name):
        return

    with factory.connect() as connection:
        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"
        )
        connection.commit()


def initialize_sqlite_database(factory: SQLiteConnectionFactory) -> None:
    """Create persistence tables and apply lightweight migrations."""
    with factory.connect() as connection:
        connection.executescript(SCHEMA_SQL)
        connection.commit()

    _add_column_if_missing(
        factory=factory,
        table_name="player_states",
        column_name="uncertainty",
        column_sql="REAL NOT NULL DEFAULT 0.50",
    )