from __future__ import annotations

from abc import ABC, abstractmethod

from procyon.adaptation.types import AdaptationDecision
from procyon.player_modeling.types import PlayerModelState, PerformanceObservation
from procyon.telemetry.types import TelemetrySummary


class PlayerStateRepository(ABC):
    """Persistence port for player model states."""

    @abstractmethod
    def get(self, player_id: str) -> PlayerModelState | None:
        """Return the latest persisted player state for a player."""

    @abstractmethod
    def save(self, player_id: str, state: PlayerModelState) -> None:
        """Persist the latest player state for a player."""


class TelemetryRepository(ABC):
    """Persistence port for telemetry summaries."""

    @abstractmethod
    def save(self, telemetry: TelemetrySummary) -> None:
        """Persist a telemetry summary."""


class PerformanceObservationRepository(ABC):
    """Persistence port for player-model observations."""

    @abstractmethod
    def save(
        self,
        player_id: str,
        session_id: str | None,
        observation: PerformanceObservation,
    ) -> None:
        """Persist a performance observation."""


class AdaptationDecisionRepository(ABC):
    """Persistence port for adaptation decisions."""

    @abstractmethod
    def save(
        self,
        player_id: str,
        session_id: str | None,
        decision: AdaptationDecision,
    ) -> None:
        """Persist an adaptation decision."""