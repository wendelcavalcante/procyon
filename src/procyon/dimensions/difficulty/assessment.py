from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import LevelArtifact
from procyon.dimensions.difficulty.types import DifficultyReport
class DifficultyAssessor(ABC):
    @abstractmethod
    def assess(self, level: LevelArtifact, context: object | None = None) -> DifficultyReport: ...
