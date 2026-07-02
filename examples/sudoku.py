from procyon.core.artifacts import AdaptationRequest
from procyon.core.types import AdaptiveDimension, GenerationStrategyType
from procyon.generation.pipeline import GenerationPipeline
import utils
from procyon.generation.stages import (
    AssessDifficultyStage,
    GenerateCandidatesStage,
    ValidateCandidatesStage,
)
from procyon.plugins.puzzles.sudoku import (
    RandomBacktrackingSudokuGenerator,
    RemoveSudokuCluesStage,
    SudokuSearchDifficultyAssessor,
    SudokuUniqueSolutionValidator,
)



request = AdaptationRequest(
    dimensions={AdaptiveDimension.DIFFICULTY},
    target_parameters={"target_difficulty": 0.5},
    strategy_type=GenerationStrategyType.GENERATE_AND_TEST,
)

result = (
    GenerationPipeline()
    .then(GenerateCandidatesStage(RandomBacktrackingSudokuGenerator(seed=42, candidate_count=2000)))
    .then(RemoveSudokuCluesStage(strategy="symmetric", target_clues=32, seed=42))
    .then(ValidateCandidatesStage(SudokuUniqueSolutionValidator(), deactivate_invalid=True))
    .then(AssessDifficultyStage(SudokuSearchDifficultyAssessor()))
    .run(request)
)

print(f"Generated candidates: {len(result.candidates)}")
print(f"Valid candidates: {len(result.active_candidates)}")

difficulties = [
    candidate.difficulty.score
    for candidate in result.active_candidates
    if candidate.difficulty is not None
]



print(f"Assessed valid candidates: {len(difficulties)}")
print(difficulties[:10])

utils.plot_active_difficulty_histogram(result,20)