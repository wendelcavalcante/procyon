from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from procyon.core.types import JsonDict


@dataclass(slots=True)
class TelemetrySummary:
    """
    Aggregated telemetry for a completed, failed or abandoned level attempt.

    This is the internal representation used by the Adaptation Core.
    """

    level_id: str
    player_id: str | None = None
    session_id: str | None = None

    success: bool | None = None
    give_up: bool = False

    estimated_difficulty: float | None = None
    target_difficulty: float | None = None

    solving_time: float | None = None
    move_count: int | None = None
    mistake_count: int | None = None
    restart_count: int | None = None
    hint_count: int | None = None
    idle_time: float | None = None

    timestamp: datetime | None = None
    metadata: JsonDict = field(default_factory=dict)