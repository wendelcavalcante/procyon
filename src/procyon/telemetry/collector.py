from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.telemetry.events import TelemetryEvent, TelemetrySummary
class TelemetryCollector(ABC):
    @abstractmethod
    def record(self, event: TelemetryEvent) -> None: ...
    @abstractmethod
    def summarize(self) -> TelemetrySummary: ...
