from __future__ import annotations
from dataclasses import dataclass
from procyon.core.artifacts import LevelArtifact
from procyon.dimensions.difficulty.assessment import DifficultyAssessor
from procyon.dimensions.difficulty.types import DifficultyReport
from procyon.plugins.puzzles.fifteen.utils import Board, manhattan_distance
@dataclass(slots=True)
class FifteenManhattanDifficultyAssessor(DifficultyAssessor):
    """Simple Fifteen Puzzle difficulty assessor based on Manhattan distance."""
    rough_max_divisor: float | None = None
    def assess(self, level: LevelArtifact, context: object | None = None) -> DifficultyReport:
        size = int(level.content["size"]); blank_value = int(level.content["blank_value"]); board: Board = tuple(int(v) for v in level.content["board"])
        distance = manhattan_distance(board, size, blank_value)
        divisor = self.rough_max_divisor or float(size*size*size)
        score = min(1.0, distance/divisor)
        level.estimated_difficulty = score
        return DifficultyReport(score=score, confidence=0.50, metrics={"manhattan_distance":float(distance)}, method="manhattan_distance", explanation="Normalized Manhattan distance. Proxy only; not optimal solution depth.", metadata={"assessor":self.__class__.__name__, "rough_max_divisor":divisor})
