from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from procyon.core.artifacts import AdaptationRequest, LevelArtifact
from procyon.core.types import AdaptiveDimension
from procyon.generation.generators import PuzzleGenerator
from procyon.plugins.puzzles.sudoku.utils import (
    copy_grid,
    empty_grid,
    fill_grid_backtracking,
    grid_to_flat,
)


@dataclass(slots=True)
class RandomBacktrackingSudokuGenerator(PuzzleGenerator):
    """
    Generates complete valid Sudoku solution grids using randomized backtracking.

    This generator produces complete solution candidates. A later pipeline stage
    may remove clues to produce playable puzzle instances.
    """

    seed: int | None = None
    candidate_count: int = 1
    _rng: Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = Random(self.seed)

    def generate(self, request: AdaptationRequest) -> list[LevelArtifact]:
        candidates: list[LevelArtifact] = []

        for candidate_index in range(self.candidate_count):
            grid = empty_grid()
            success = fill_grid_backtracking(grid, self._rng)

            if not success:
                raise RuntimeError("Could not generate a complete Sudoku solution.")

            candidates.append(
                LevelArtifact(
                    content={
                        "puzzle": "sudoku",
                        "representation": "grid",
                        "size": 9,
                        "grid": copy_grid(grid),
                        "flat": grid_to_flat(grid),
                        "solution": copy_grid(grid),
                    },
                    dimensions={AdaptiveDimension.DIFFICULTY},
                    estimated_difficulty=None,
                    metadata={
                        "generator": self.__class__.__name__,
                        "candidate_index": candidate_index,
                        "is_complete_solution": True,
                        "requires_clue_removal": True,
                    },
                )
            )

        return candidates