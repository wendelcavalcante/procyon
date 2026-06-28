from __future__ import annotations
from procyon.core.artifacts import AdaptationRequest
from procyon.core.types import AdaptiveDimension, GenerationStrategyType
from procyon.generation.pipeline import GenerationPipeline
from procyon.generation.stages import AssessDifficultyStage, GenerateCandidatesStage, SelectFirstCandidateStage, ValidateCandidatesStage, SelectClosestDifficultyCandidateStage
from procyon.plugins.puzzles.fifteen import FifteenManhattanDifficultyAssessor, FifteenSolvabilityValidator, FisherYatesFifteenGenerator, ReverseShuffleFifteenGenerator

def main() -> None:
    request = AdaptationRequest(dimensions={AdaptiveDimension.DIFFICULTY}, target_parameters={"target_difficulty": 0.5}, strategy_type=GenerationStrategyType.GENERATE_AND_TEST)
    # generate_and_test_pipeline = GenerationPipeline(stages=[GenerateCandidatesStage(FisherYatesFifteenGenerator(seed=42, candidate_count=10)), ValidateCandidatesStage(FifteenSolvabilityValidator(), keep_only_valid=True), AssessDifficultyStage(FifteenManhattanDifficultyAssessor()), SelectFirstCandidateStage()])
    generate_and_test_pipeline = (
        GenerationPipeline()
        .then(GenerateCandidatesStage(FisherYatesFifteenGenerator(seed=42, candidate_count=10)))
        .then(ValidateCandidatesStage(FifteenSolvabilityValidator(), keep_only_valid=True))
        .then(AssessDifficultyStage(FifteenManhattanDifficultyAssessor()))
        .then(SelectClosestDifficultyCandidateStage())
    )
    result = generate_and_test_pipeline.run(request)
    print("Fisher-Yates selected grid:")
    print(result.level.content["grid"])
    print(result.validation)
    print(result.difficulty)
    reverse_pipeline = GenerationPipeline(stages=[GenerateCandidatesStage(ReverseShuffleFifteenGenerator(seed=42, iterations=80, candidate_count=10)), AssessDifficultyStage(FifteenManhattanDifficultyAssessor()), SelectClosestDifficultyCandidateStage()])
    result = reverse_pipeline.run(request)
    print("Reverse Shuffle selected grid:")
    print(result.level.content["grid"])
    print(result.validation)
    print(result.difficulty)
    reverse_pipeline = GenerationPipeline(stages=[GenerateCandidatesStage(ReverseShuffleFifteenGenerator(seed=42, iterations=80, candidate_count=10)), AssessDifficultyStage(FifteenManhattanDifficultyAssessor()), SelectFirstCandidateStage()])
    result = reverse_pipeline.run(request)
    print("Reverse Shuffle selected grid:")
    print(result.level.content["grid"])
    print(result.validation)
    print(result.difficulty)
if __name__ == "__main__": main()
