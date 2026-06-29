from __future__ import annotations

from abc import ABC, abstractmethod

from procyon.core.artifacts import LevelArtifact
from procyon.telemetry.events import TelemetryEvent, TelemetrySummary


class RuntimeAdapter(ABC):
    """Adapter between Procyon and an external game runtime."""

    @abstractmethod
    def export_level(self, level: LevelArtifact) -> dict:
        """Convert a Procyon level artifact to a runtime-specific representation."""

    @abstractmethod
    def import_telemetry(self, payload: dict) -> TelemetrySummary | list[TelemetryEvent]:
        """Convert runtime telemetry payloads to Procyon telemetry objects."""