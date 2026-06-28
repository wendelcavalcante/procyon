from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import AdaptationRequest, DesignGoals, PlayerState
class AdaptationEngine(ABC):
    @abstractmethod
    def create_request(self, player_state: PlayerState, design_goals: DesignGoals) -> AdaptationRequest: ...
