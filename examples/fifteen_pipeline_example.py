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
from procyon.plugins.puzzles.fifteen.assessors import (
    FifteenManhattanDifficultyAssessor,
)
from procyon.plugins.puzzles.fifteen.generators import (
    FisherYatesFifteenGenerator,
)
from procyon.plugins.puzzles.fifteen.validators import (
    FifteenSolvabilityValidator,
)


def print_fifteen_board(board: list[int], size: int = 4) -> None:
    for row_index in range(size):
        row = board[row_index * size : (row_index + 1) * size]
        print(
            " ".join(
                "__" if value == 0 else f"{value:02d}"
                for value in row
            )
        )


def main() -> None:
    request = AdaptationRequest(
        dimensions={AdaptiveDimension.DIFFICULTY},
        strategy_type=GenerationStrategyType.GENERATE_AND_TEST,
        target_parameters={
            "domain": "fifteen",
            "target_difficulty": 0.50,
            "difficulty_tolerance": 0.10,
            "candidate_count": 100,
        },
    )

    pipeline = (
        GenerationPipeline()
        .then(
            GenerateCandidatesStage(
                FisherYatesFifteenGenerator(
                    seed=42,
                    candidate_count=100,
                )
            )
        )
        .then(
            ValidateCandidatesStage(
                FifteenSolvabilityValidator(),
                deactivate_invalid=True,
            )
        )
        .then(
            AssessDifficultyStage(
                FifteenManhattanDifficultyAssessor()
            )
        )
        .then(
            SelectClosestDifficultyCandidateStage()
        )
    )

    result = pipeline.run(request)

    print("\n=== Fifteen Puzzle Pipeline Example ===")
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

    print("\n=== Board ===")
    board = selected.level.content.get("board")
    if board is None:
        pprint(selected.level.content)
    else:
        print_fifteen_board(board)


if __name__ == "__main__":
    main()