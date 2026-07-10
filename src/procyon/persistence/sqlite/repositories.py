from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any

from procyon.adaptation.types import AdaptationDecision
from procyon.persistence.ports import (
    AdaptationDecisionRepository,
    PerformanceObservationRepository,
    PlayerStateRepository,
    TelemetryRepository,
)
from procyon.persistence.sqlite.connection import SQLiteConnectionFactory
from procyon.player_modeling.types import PerformanceObservation, PlayerModelState
from procyon.telemetry.types import TelemetrySummary


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_json(value: Any) -> str:
    if value is None:
        return "{}"

    if is_dataclass(value):
        value = asdict(value)

    return json.dumps(value, ensure_ascii=False, default=str)


def _from_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}

    loaded = json.loads(value)

    if isinstance(loaded, dict):
        return loaded

    return {"value": loaded}


def _bool_to_int(value: bool | None) -> int | None:
    if value is None:
        return None

    return 1 if value else 0


def _int_to_bool(value: int | None) -> bool | None:
    if value is None:
        return None

    return bool(value)


class SQLitePlayerStateRepository(PlayerStateRepository):
    def __init__(self, factory: SQLiteConnectionFactory) -> None:
        self.factory = factory

    def get(self, player_id: str) -> PlayerModelState | None:
        with self.factory.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    skill,
                    uncertainty,
                    engagement,
                    frustration,
                    confidence,
                    preferred_pace,
                    stability,
                    observations_count,
                    metadata_json
                FROM player_states
                WHERE player_id = ?
                """,
                (player_id,),
            ).fetchone()

        if row is None:
            return None

        return PlayerModelState(
            skill=float(row["skill"]),
            uncertainty=float(row["uncertainty"]),
            engagement=float(row["engagement"]),
            frustration=float(row["frustration"]),
            confidence=float(row["confidence"]),
            preferred_pace=row["preferred_pace"],
            stability=row["stability"],
            observations_count=int(row["observations_count"]),
            metadata=_from_json(row["metadata_json"]),
        )

    def save(self, player_id: str, state: PlayerModelState) -> None:
        with self.factory.connect() as connection:
            connection.execute(
                """
                INSERT INTO player_states (
                    player_id,
                    skill,
                    uncertainty,
                    engagement,
                    frustration,
                    confidence,
                    preferred_pace,
                    stability,
                    observations_count,
                    updated_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_id) DO UPDATE SET
                    skill = excluded.skill,
                    uncertainty = excluded.uncertainty,
                    engagement = excluded.engagement,
                    frustration = excluded.frustration,
                    confidence = excluded.confidence,
                    preferred_pace = excluded.preferred_pace,
                    stability = excluded.stability,
                    observations_count = excluded.observations_count,
                    updated_at = excluded.updated_at,
                    metadata_json = excluded.metadata_json
                """,
                (
                    player_id,
                    state.skill,
                    state.uncertainty,
                    state.engagement,
                    state.frustration,
                    state.confidence,
                    state.preferred_pace,
                    state.stability,
                    state.observations_count,
                    _utc_now_iso(),
                    _to_json(state.metadata),
                ),
            )
            connection.commit()


class SQLiteTelemetryRepository(TelemetryRepository):
    def __init__(self, factory: SQLiteConnectionFactory) -> None:
        self.factory = factory

    def save(self, telemetry: TelemetrySummary) -> None:
        with self.factory.connect() as connection:
            connection.execute(
                """
                INSERT INTO telemetry_summaries (
                    player_id,
                    session_id,
                    level_id,
                    success,
                    give_up,
                    estimated_difficulty,
                    target_difficulty,
                    solving_time,
                    move_count,
                    mistake_count,
                    restart_count,
                    hint_count,
                    idle_time,
                    timestamp,
                    created_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    telemetry.player_id,
                    telemetry.session_id,
                    telemetry.level_id,
                    _bool_to_int(telemetry.success),
                    _bool_to_int(telemetry.give_up),
                    telemetry.estimated_difficulty,
                    telemetry.target_difficulty,
                    telemetry.solving_time,
                    telemetry.move_count,
                    telemetry.mistake_count,
                    telemetry.restart_count,
                    telemetry.hint_count,
                    telemetry.idle_time,
                    telemetry.timestamp.isoformat() if telemetry.timestamp else None,
                    _utc_now_iso(),
                    _to_json(telemetry.metadata),
                ),
            )
            connection.commit()


class SQLitePerformanceObservationRepository(PerformanceObservationRepository):
    def __init__(self, factory: SQLiteConnectionFactory) -> None:
        self.factory = factory

    def save(
        self,
        player_id: str,
        session_id: str | None,
        observation: PerformanceObservation,
    ) -> None:
        with self.factory.connect() as connection:
            connection.execute(
                """
                INSERT INTO performance_observations (
                    player_id,
                    session_id,
                    level_id,
                    estimated_difficulty,
                    success,
                    performance_score,
                    skill_delta,
                    engagement_delta,
                    frustration_delta,
                    confidence_delta,
                    reason,
                    created_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    player_id,
                    session_id,
                    observation.level_id,
                    observation.estimated_difficulty,
                    _bool_to_int(observation.success),
                    observation.performance_score,
                    observation.skill_delta,
                    observation.engagement_delta,
                    observation.frustration_delta,
                    observation.confidence_delta,
                    observation.reason,
                    _utc_now_iso(),
                    _to_json(observation.metadata),
                ),
            )
            connection.commit()


class SQLiteAdaptationDecisionRepository(AdaptationDecisionRepository):
    def __init__(self, factory: SQLiteConnectionFactory) -> None:
        self.factory = factory

    def save(
        self,
        player_id: str,
        session_id: str | None,
        decision: AdaptationDecision,
    ) -> None:
        with self.factory.connect() as connection:
            connection.execute(
                """
                INSERT INTO adaptation_decisions (
                    player_id,
                    session_id,
                    target_difficulty,
                    previous_difficulty,
                    reason,
                    confidence,
                    applied_constraints_json,
                    created_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    player_id,
                    session_id,
                    decision.target_difficulty,
                    decision.previous_difficulty,
                    decision.reason,
                    decision.confidence,
                    _to_json(decision.applied_constraints),
                    _utc_now_iso(),
                    _to_json(decision.metadata),
                ),
            )
            connection.commit()