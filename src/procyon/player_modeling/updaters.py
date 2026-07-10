from __future__ import annotations

from abc import ABC, abstractmethod

from procyon.player_modeling.types import PerformanceObservation, PlayerModelState
from procyon.telemetry.types import TelemetrySummary


class PlayerModelUpdater(ABC):
    """
    Port for dynamic difficulty adjustment / player model update strategies.

    Different DDA approaches can implement this interface, such as:
    - heuristic rules;
    - probabilistic methods;
    - dynamic scripting;
    - reinforcement learning;
    - bandit-based approaches;
    - neural models.
    """

    @abstractmethod
    def update(
        self,
        previous_state: PlayerModelState,
        telemetry: TelemetrySummary | None,
    ) -> tuple[PlayerModelState, PerformanceObservation | None]:
        """Update the player state from telemetry."""