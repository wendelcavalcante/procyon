from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import PlayerState
from procyon.telemetry.events import TelemetrySummary
class PlayerModel(ABC):
    @abstractmethod
    def update(self, telemetry: TelemetrySummary) -> PlayerState: ...
class SimulatedPlayer(ABC):
    @abstractmethod
    def play(self, level_difficulty: float) -> TelemetrySummary: ...
