from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import AdaptationRequest, LevelArtifact
class ContentGenerator(ABC):
    @abstractmethod
    def generate(self, request: AdaptationRequest) -> list[LevelArtifact]: ...
class PuzzleGenerator(ContentGenerator):
    pass
