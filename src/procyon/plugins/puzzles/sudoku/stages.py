from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Literal

from procyon.generation.context import GenerationContext
from procyon.generation.pipeline import PipelineStage
from procyon.plugins.puzzles.sudoku.utils import (
    copy_grid,
    count_clues,
    grid_to_flat,
    shuffled_cells,
    symmetric_cell,
)

RemovalStrategy = Literal["random", "symmetric"]


@dataclass(slots=True)
class RemoveSudokuCluesStage(PipelineStage):
    """
    Removes clues from complete Sudoku solution grids.

    This stage transforms complete solved Sudoku grids into puzzle candidates.
    It does not guarantee uniqueness. Unique-solution checking is expected to be
    performed later by a pluggable validator.
    """

    strategy: RemovalStrategy = "symmetric"
    target_clues: int = 32
    seed: int | None = None
    only_active: bool = True
    _rng: Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not 17 <= self.target_clues <= 81:
            raise ValueError("target_clues should be between 17 and 81 for a 9x9 Sudoku.")

        self._rng = Random(self.seed)

    def process(self, context: GenerationContext) -> GenerationContext:
        candidates = context.active_candidates if self.only_active else context.candidates

        for candidate in candidates:
            solution = candidate.level.content.get("solution")

            if solution is None:
                raise RuntimeError(
                    "RemoveSudokuCluesStage expects candidates with a complete "
                    "solution stored in level.content['solution']."
                )

            puzzle = copy_grid(solution)

            if self.strategy == "random":
                self._remove_random(puzzle)
            elif self.strategy == "symmetric":
                self._remove_symmetric(puzzle)
            else:
                raise ValueError(f"Unknown clue removal strategy: {self.strategy}")

            candidate.level.content["grid"] = puzzle
            candidate.level.content["flat"] = grid_to_flat(puzzle)
            candidate.level.content["clue_count"] = count_clues(puzzle)
            candidate.level.content["empty_count"] = 81 - count_clues(puzzle)

            candidate.level.metadata.update(
                {
                    "clue_removal_stage": self.__class__.__name__,
                    "clue_removal_strategy": self.strategy,
                    "target_clues": self.target_clues,
                    "actual_clues": count_clues(puzzle),
                    "is_complete_solution": False,
                    "requires_validation": True,
                }
            )

        return context

    def _remove_random(self, puzzle: list[list[int]]) -> None:
        cells = shuffled_cells(self._rng)

        for row, col in cells:
            if count_clues(puzzle) <= self.target_clues:
                break

            puzzle[row][col] = 0

    def _remove_symmetric(self, puzzle: list[list[int]]) -> None:
        cells = shuffled_cells(self._rng)

        for row, col in cells:
            if count_clues(puzzle) <= self.target_clues:
                break

            sym_row, sym_col = symmetric_cell(row, col)

            if puzzle[row][col] == 0:
                continue

            removed_positions = [(row, col)]

            if (sym_row, sym_col) != (row, col) and puzzle[sym_row][sym_col] != 0:
                removed_positions.append((sym_row, sym_col))

            current_clues = count_clues(puzzle)

            if current_clues - len(removed_positions) < self.target_clues:
                continue

            for r, c in removed_positions:
                puzzle[r][c] = 0