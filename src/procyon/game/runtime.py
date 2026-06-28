from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import LevelArtifact
from procyon.telemetry.events import TelemetryEvent
class GameRuntime(ABC):
    @abstractmethod
    def apply_level(self, level: LevelArtifact) -> None: ...
    @abstractmethod
    def collect_events(self) -> list[TelemetryEvent]: ...
