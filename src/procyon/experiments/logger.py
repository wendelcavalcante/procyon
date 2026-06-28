from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import GenerationResult
from procyon.telemetry.events import TelemetrySummary
class ExperimentLogger(ABC):
    @abstractmethod
    def log_telemetry(self, telemetry: TelemetrySummary) -> None: ...
    @abstractmethod
    def log_generation(self, result: GenerationResult) -> None: ...
