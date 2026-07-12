from __future__ import annotations

from pprint import pprint

from procyon.adaptation.types import AdaptationRequest
from procyon.core.types import AdaptiveDimension, GenerationStrategyType
from procyon.generation.pipeline import GenerationPipeline
from procyon.generation.stages import (
    AssessDifficultyStage,
    GenerateCandidatesStage,
    SelectClosestDifficultyCandidateStage,
)
from procyon.plugins.puzzles.sokoban.assessors import (
    SokobanReverseDifficultyAssessor,
)
from procyon.plugins.puzzles.sokoban.generators import (
    ReverseSokobanGenerator,
)


def print_sokoban_level(content: dict) -> None:
    ascii_level = content.get("ascii")

    if ascii_level is not None:
        print(ascii_level)
        return

    grid = content.get("grid")

    if grid is not None:
        for row in grid:
            if isinstance(row, str):
                print(row)
            else:
                print("".join(str(cell) for cell in row))
        return

    pprint(content)


def main() -> None:
    request = AdaptationRequest(
        dimensions={AdaptiveDimension.DIFFICULTY},
        strategy_type=GenerationStrategyType.REVERSE_SEARCH,
        target_parameters={
            "domain": "sokoban",
            "target_difficulty": 0.50,
            "difficulty_tolerance": 0.10,
            "candidate_count": 30,
            "width": 9,
            "height": 9,
            "reverse_steps": 30,
            "wall_density": 0.12,
        },
    )

    pipeline = (
        GenerationPipeline()
        .then(
            GenerateCandidatesStage(
                ReverseSokobanGenerator(
                    width=9,
                    height=9,
                    reverse_steps=30,
                    candidate_count=30,
                    seed=42,
                    avoid_backtracking=True,
                    reposition_player_before_pull=True,
                    wall_density=0.12,
                    ensure_connected_floor=True,
                )
            )
        )
        .then(
            AssessDifficultyStage(
                SokobanReverseDifficultyAssessor()
            )
        )
        .then(
            SelectClosestDifficultyCandidateStage()
        )
    )

    result = pipeline.run(request)

    print("\n=== Sokoban Pipeline Example ===")
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

    print("\n=== Level ===")
    print_sokoban_level(selected.level.content)

    print("\n=== Level Metadata ===")
    pprint(selected.level.metadata)


if __name__ == "__main__":
    main()