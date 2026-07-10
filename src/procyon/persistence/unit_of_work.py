from __future__ import annotations

from dataclasses import dataclass

from procyon.persistence.ports import (
    AdaptationDecisionRepository,
    PerformanceObservationRepository,
    PlayerStateRepository,
    TelemetryRepository,
)


@dataclass(slots=True)
class PersistenceStore:
    player_states: PlayerStateRepository
    telemetry: TelemetryRepository
    observations: PerformanceObservationRepository
    adaptation_decisions: AdaptationDecisionRepository