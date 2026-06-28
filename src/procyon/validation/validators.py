from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import LevelArtifact, ValidationReport
class Validator(ABC):
    @abstractmethod
    def validate(self, level: LevelArtifact) -> ValidationReport: ...
class PuzzleSolver(ABC):
    @abstractmethod
    def solve(self, level: LevelArtifact) -> ValidationReport: ...
