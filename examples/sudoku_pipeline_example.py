from __future__ import annotations

from pprint import pprint

from procyon.adaptation.types import AdaptationRequest
from procyon.core.types import AdaptiveDimension, GenerationStrategyType
from procyon.generation.pipeline import GenerationPipeline
from procyon.generation.stages import (
    AssessDifficultyStage,
    GenerateCandidatesStage,
    SelectClosestDifficultyCandidateStage,
    ValidateCandidatesStage,
)
from procyon.plugins.puzzles.sudoku.assessors import (
    SudokuSearchDifficultyAssessor,
)
from procyon.plugins.puzzles.sudoku.generators import (
    RandomBacktrackingSudokuGenerator,
)
from procyon.plugins.puzzles.sudoku.stages import (
    RemoveSudokuCluesStage,
)
from procyon.plugins.puzzles.sudoku.validators import (
    SudokuUniqueSolutionValidator,
)


def print_sudoku_grid(grid: list[list[int]]) -> None:
    for row_index, row in enumerate(grid):
        if row_index > 0 and row_index % 3 == 0:
            print("------+-------+------")

        rendered_row = []
        for column_index, value in enumerate(row):
            if column_index > 0 and column_index % 3 == 0:
                rendered_row.append("|")

            rendered_row.append("." if value == 0 else str(value))

        print(" ".join(rendered_row))


def main() -> None:
    request = AdaptationRequest(
        dimensions={AdaptiveDimension.DIFFICULTY},
        strategy_type=GenerationStrategyType.GENERATE_AND_TEST,
        target_parameters={
            "domain": "sudoku",
            "target_difficulty": 0.50,
            "difficulty_tolerance": 0.10,
            "candidate_count": 50,
            "target_clues": 32,
            "clue_removal_strategy": "symmetric",
        },
    )

    pipeline = (
        GenerationPipeline()
        .then(
            GenerateCandidatesStage(
                RandomBacktrackingSudokuGenerator(
                    seed=42,
                    candidate_count=50,
                )
            )
        )
        .then(
            RemoveSudokuCluesStage(
                strategy="symmetric",
                target_clues=32,
                seed=42,
            )
        )
        .then(
            ValidateCandidatesStage(
                SudokuUniqueSolutionValidator(),
                deactivate_invalid=True,
            )
        )
        .then(
            AssessDifficultyStage(
                SudokuSearchDifficultyAssessor()
            )
        )
        .then(
            SelectClosestDifficultyCandidateStage()
        )
    )

    result = pipeline.run(request)

    print("\n=== Sudoku Pipeline Example ===")
    print(f"Generated candidates: {len(result.candidates)}")
    print(f"Active candidates: {len(result.active_candidates)}")

    if result.selected is None:
        print("No candidate selected.")
        return

    selected = result.selected

    print("\n=== Selected Candidate ===")
    print(f"Candidate ID: {selected.candidate_id}")
    print(f"Score: {selected.score}")

    print("\n=== Difficulty Report ===")
    pprint(selected.difficulty)

    print("\n=== Validation Report ===")
    pprint(selected.validation)

    print("\n=== Puzzle Grid ===")
    grid = selected.level.content.get("grid")
    if grid is None:
        pprint(selected.level.content)
    else:
        print_sudoku_grid(grid)

    solution = selected.level.content.get("solution")
    if solution is not None:
        print("\n=== Solution Grid ===")
        print_sudoku_grid(solution)


if __name__ == "__main__":
    main()