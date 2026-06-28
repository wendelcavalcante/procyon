from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import DesignGoals
class DesignGoalsManager(ABC):
    @abstractmethod
    def current_goals(self) -> DesignGoals: ...
