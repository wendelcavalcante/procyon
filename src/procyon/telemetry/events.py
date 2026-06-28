from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from procyon.core.types import JsonDict, LevelId, PlayerId, SessionId
class TelemetryEventType(str, Enum):
    LEVEL_STARTED = "level_started"
    MOVE = "move"
    MISTAKE = "mistake"
    HINT_USED = "hint_used"
    RESTART = "restart"
    LEVEL_COMPLETED = "level_completed"
    LEVEL_ABANDONED = "level_abandoned"
@dataclass(slots=True)
class TelemetryEvent:
    event_type: TelemetryEventType
    player_id: PlayerId
    session_id: SessionId
    level_id: LevelId
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: JsonDict = field(default_factory=dict)
@dataclass(slots=True)
class TelemetrySummary:
    player_id: PlayerId
    session_id: SessionId
    level_id: LevelId
    success: bool
    solving_time: float
    move_count: int
    mistake_count: int
    restart_count: int
    hint_count: int = 0
    give_up: bool = False
    idle_time: float | None = None
