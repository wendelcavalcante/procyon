from __future__ import annotations

from dataclasses import dataclass
from math import log1p

from procyon.core.artifacts import LevelArtifact
from procyon.dimensions.difficulty.assessment import DifficultyAssessor
from procyon.dimensions.difficulty.types import DifficultyReport
from procyon.generation.context import GenerationContext
from procyon.plugins.puzzles.sudoku.utils import count_clues, copy_grid, solve_count


@dataclass(slots=True)
class SudokuSearchDifficultyAssessor(DifficultyAssessor):
    """
    Estimates Sudoku difficulty using solver search effort.

    This is a simple search-based proxy. It does not represent human-style
    Sudoku difficulty, but it is useful for a first pluggable difficulty assessor.
    """

    recursive_call_normalizer: float = 10_000.0
    backtrack_normalizer: float = 5_000.0

    def assess(
        self,
        level: LevelArtifact,
        context: GenerationContext | None = None,
    ) -> DifficultyReport:
        grid = copy_grid(level.content["grid"])

        solution_count, search_metadata = solve_count(grid, limit=2, use_mrv=True)

        recursive_calls = search_metadata["recursive_calls"]
        backtracks = search_metadata["backtracks"]
        dead_ends = search_metadata["dead_ends"]
        max_depth = search_metadata["max_depth"]
        clues = count_clues(grid)
        empty_cells = 81 - clues

        recursive_score = min(
            1.0,
            log1p(recursive_calls) / log1p(self.recursive_call_normalizer),
        )

        backtrack_score = min(
            1.0,
            log1p(backtracks) / log1p(self.backtrack_normalizer),
        )

        emptiness_score = empty_cells / 64.0
        emptiness_score = max(0.0, min(1.0, emptiness_score))

        score = (
            0.45 * recursive_score
            + 0.35 * backtrack_score
            + 0.20 * emptiness_score
        )

        level.estimated_difficulty = score

        return DifficultyReport(
            score=score,
            confidence=0.55,
            metrics={
                "solution_count_limited": float(solution_count),
                "recursive_calls": float(recursive_calls),
                "assignments": float(search_metadata["assignments"]),
                "backtracks": float(backtracks),
                "dead_ends": float(dead_ends),
                "max_depth": float(max_depth),
                "clue_count": float(clues),
                "empty_cells": float(empty_cells),
                "recursive_score": recursive_score,
                "backtrack_score": backtrack_score,
                "emptiness_score": emptiness_score,
            },
            method="search_effort",
            explanation=(
                "Difficulty estimated from backtracking search effort, combining "
                "recursive calls, backtracks and number of empty cells. This is a "
                "computational proxy, not a human-style Sudoku rating."
            ),
            metadata={
                "assessor": self.__class__.__name__,
                "recursive_call_normalizer": self.recursive_call_normalizer,
                "backtrack_normalizer": self.backtrack_normalizer,
            },
        )