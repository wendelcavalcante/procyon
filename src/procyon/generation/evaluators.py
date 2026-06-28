from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import LevelArtifact
from procyon.generation.context import GenerationContext
class CandidateEvaluator(ABC):
    @abstractmethod
    def score(self, candidate: LevelArtifact, context: GenerationContext) -> float: ...
class ContentSelector(ABC):
    @abstractmethod
    def select(self, candidates: list[LevelArtifact], context: GenerationContext) -> LevelArtifact: ...
