from __future__ import annotations

from dataclasses import dataclass, field

from procyon.core.types import JsonDict


@dataclass(slots=True)
class PlayerModelState:
    """
    Current estimated state of a player.

    This object is intentionally serializable, so it can be sent back to a
    stateless API client and provided again in a future request.
    """

    skill: float = 0.50
    engagement: float = 0.50
    frustration: float = 0.00
    confidence: float = 0.10

    preferred_pace: float | None = None
    stability: float | None = None

    observations_count: int = 0
    metadata: JsonDict = field(default_factory=dict)


@dataclass(slots=True)
class PerformanceObservation:
    """
    Interpretation of a telemetry summary produced by the player model.

    This is useful for logging and later experimental analysis.
    """

    level_id: str
    estimated_difficulty: float | None
    success: bool | None

    performance_score: float
    skill_delta: float = 0.0
    engagement_delta: float = 0.0
    frustration_delta: float = 0.0
    confidence_delta: float = 0.0

    reason: str | None = None
    metadata: JsonDict = field(default_factory=dict)