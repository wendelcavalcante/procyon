from __future__ import annotations

from dataclasses import dataclass

from procyon.core.artifacts import LevelArtifact
from procyon.dimensions.difficulty.assessment import DifficultyAssessor
from procyon.dimensions.difficulty.types import DifficultyReport
from procyon.generation.context import GenerationContext


@dataclass(slots=True)
class SokobanReverseDifficultyAssessor(DifficultyAssessor):
    """
    Simple Sokoban difficulty proxy for reverse-generated levels.

    This is not a solver-based difficulty measure. It combines:
    - number of reverse steps actually applied;
    - box-goal distance after reverse generation;
    - map size;
    - box count.

    Later, this can be replaced or complemented by a solver-based assessor.
    """

    reverse_step_normalizer: float = 100.0
    distance_normalizer: float = 20.0
    map_size_normalizer: float = 100.0

    def assess(
        self,
        level: LevelArtifact,
        context: GenerationContext | None = None,
    ) -> DifficultyReport:
        metadata = level.metadata

        reverse_steps = float(metadata.get("actual_reverse_steps", 0))
        box_goal_distance = float(metadata.get("box_goal_distance_sum", 0))
        box_count = float(metadata.get("box_count", 1))

        width = float(level.content["width"])
        height = float(level.content["height"])
        map_area = width * height

        reverse_step_score = min(1.0, reverse_steps / self.reverse_step_normalizer)
        distance_score = min(1.0, box_goal_distance / self.distance_normalizer)
        map_size_score = min(1.0, map_area / self.map_size_normalizer)
        box_count_score = min(1.0, box_count / 5.0)

        score = (
            0.50 * reverse_step_score
            + 0.25 * distance_score
            + 0.15 * map_size_score
            + 0.10 * box_count_score
        )

        level.estimated_difficulty = score

        return DifficultyReport(
            score=score,
            confidence=0.40,
            metrics={
                "actual_reverse_steps": reverse_steps,
                "box_goal_distance_sum": box_goal_distance,
                "box_count": box_count,
                "map_area": map_area,
                "reverse_step_score": reverse_step_score,
                "distance_score": distance_score,
                "map_size_score": map_size_score,
                "box_count_score": box_count_score,
            },
            method="reverse_generation_proxy",
            explanation=(
                "Difficulty estimated from reverse generation metadata. "
                "This is a lightweight proxy and does not represent minimal "
                "solution length or human-perceived Sokoban difficulty."
            ),
            metadata={
                "assessor": self.__class__.__name__,
                "reverse_step_normalizer": self.reverse_step_normalizer,
                "distance_normalizer": self.distance_normalizer,
                "map_size_normalizer": self.map_size_normalizer,
            },
        )