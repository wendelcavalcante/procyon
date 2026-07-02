from __future__ import annotations

from procyon.core.artifacts import LevelArtifact, ValidationReport
from procyon.plugins.puzzles.sudoku.utils import count_clues, copy_grid, solve_count
from procyon.validation.validators import Validator


class SudokuUniqueSolutionValidator(Validator):
    """
    Validates whether a Sudoku puzzle has exactly one solution.

    This validator is intended to be plugged after a generator or clue-removal stage.
    """

    def validate(self, level: LevelArtifact) -> ValidationReport:
        grid = copy_grid(level.content["grid"])
        solution_count, search_metadata = solve_count(grid, limit=2, use_mrv=True)

        is_unique = solution_count == 1

        return ValidationReport(
            is_valid=is_unique,
            score=1.0 if is_unique else 0.0,
            messages=[] if is_unique else [f"Expected unique solution, found {solution_count}."],
            metadata={
                "validator": self.__class__.__name__,
                "solution_count_limited": solution_count,
                "clue_count": count_clues(grid),
                **search_metadata,
            },
        )