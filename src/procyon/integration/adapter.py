from __future__ import annotations

from procyon.core.artifacts import LevelArtifact
from procyon.integration.ports import RuntimeAdapter
from procyon.telemetry.events import TelemetryEvent, TelemetrySummary


class UnityRuntimeAdapter(RuntimeAdapter):
    """Converts Procyon artifacts to and from Unity-compatible JSON payloads."""

    def export_level(self, level: LevelArtifact) -> dict:
        return {
            "levelId": level.metadata.get("level_id"),
            "dimensions": [dimension.value for dimension in level.dimensions],
            "content": level.content,
            "estimatedDifficulty": level.estimated_difficulty,
            "metadata": level.metadata,
        }

    def import_telemetry(self, payload: dict) -> TelemetrySummary | list[TelemetryEvent]:
        raise NotImplementedError