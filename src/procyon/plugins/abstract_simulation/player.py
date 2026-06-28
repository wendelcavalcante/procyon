from __future__ import annotations
from procyon.player_modeling.models import SimulatedPlayer
from procyon.telemetry.events import TelemetrySummary
class AbstractSimulatedPlayer(SimulatedPlayer):
    def play(self, level_difficulty: float) -> TelemetrySummary:
        raise NotImplementedError
