from procyon.core.artifacts import AdaptationRequest
from procyon.core.types import AdaptiveDimension, GenerationStrategyType
from procyon.generation.pipeline import GenerationPipeline
from procyon.generation.stages import AssessDifficultyStage, GenerateCandidatesStage
from procyon.plugins.puzzles.sokoban import (
    ReverseSokobanGenerator,
    SokobanReverseDifficultyAssessor,
)

request = AdaptationRequest(
    dimensions={AdaptiveDimension.DIFFICULTY},
    target_parameters={"target_difficulty": 0.5},
    strategy_type=GenerationStrategyType.REVERSE_SEARCH,
)

result = (
    GenerationPipeline()
    .then(
        GenerateCandidatesStage(
            ReverseSokobanGenerator(
                width=9,
                height=9,
                reverse_steps=30,
                candidate_count=1,
                seed=42,
                wall_density=0.12,
                ensure_connected_floor=True,
                avoid_backtracking=True,
            )
        )
    )
    .then(AssessDifficultyStage(SokobanReverseDifficultyAssessor()))
    .run(request)
)

for candidate in result.candidates[:3]:
    print()
    print(candidate.level.content["ascii"])
    print(candidate.difficulty)
