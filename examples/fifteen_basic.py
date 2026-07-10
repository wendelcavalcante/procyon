from __future__ import annotations
from procyon.core.artifacts import AdaptationRequest
from procyon.core.types import AdaptiveDimension, GenerationStrategyType
from procyon.generation.pipeline import GenerationPipeline
from procyon.generation.stages import AssessDifficultyStage, GenerateCandidatesStage, SelectFirstCandidateStage, ValidateCandidatesStage, SelectClosestDifficultyCandidateStage
from procyon.plugins.puzzles.fifteen import FifteenManhattanDifficultyAssessor, FifteenSolvabilityValidator, FisherYatesFifteenGenerator, ReverseShuffleFifteenGenerator

import matplotlib.pyplot as plt


def plot_difficulty_histogram(result, bins: int = 10) -> None:
    difficulties = [
        candidate.difficulty.score
        for candidate in result.candidates
        if candidate.difficulty is not None
    ]

    if not difficulties:
        raise ValueError(
            "No difficulty reports found. "
            "Did you run AssessDifficultyStage before plotting?"
        )

    plt.figure(figsize=(8, 5))
    plt.hist(difficulties, bins=bins, edgecolor="black")

    plt.title("Difficulty Distribution of Generated Candidates")
    plt.xlabel("Difficulty score")
    plt.ylabel("Number of candidates")

    plt.xlim(0.0, 1.0)
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt


def plot_active_difficulty_histogram(result, bins: int = 10) -> None:
    difficulties = [
        candidate.difficulty.score
        for candidate in result.active_candidates
        if candidate.difficulty is not None
    ]

    if not difficulties:
        raise ValueError(
            "No difficulty reports found for active candidates. "
            "Did you run validation and difficulty assessment?"
        )

    plt.figure(figsize=(8, 5))
    plt.hist(difficulties, bins=bins, edgecolor="black")

    plt.title("Difficulty Distribution of Valid Generated Candidates")
    plt.xlabel("Difficulty score")
    plt.ylabel("Number of candidates")

    plt.xlim(0.0, 1.0)
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()

def main() -> None:
    request = AdaptationRequest(dimensions={AdaptiveDimension.DIFFICULTY}, target_parameters={"target_difficulty": 0.5}, strategy_type=GenerationStrategyType.GENERATE_AND_TEST)

    pipeline = GenerationPipeline().then(
        GenerateCandidatesStage(
            FisherYatesFifteenGenerator(seed=42, candidate_count=100)
        )
    )

    result = pipeline.run(request)

    print(len(result.candidates))
    print(result.selected)
    # None
    pipeline = (
        GenerationPipeline()
        .then(GenerateCandidatesStage(FisherYatesFifteenGenerator(seed=42, candidate_count=100)))
        .then(ValidateCandidatesStage(FifteenSolvabilityValidator()))
    )

    result = pipeline.run(request)

    total = len(result.candidates)
    valid = sum(
        1
        for candidate in result.candidates
        if candidate.validation is not None and candidate.validation.is_valid
    )

    print(f"Solvable: {valid}/{total}")

    pipeline = (
        GenerationPipeline()
        .then(GenerateCandidatesStage(FisherYatesFifteenGenerator(seed=42, candidate_count=10000)))
        .then(ValidateCandidatesStage(FifteenSolvabilityValidator()))
        .then(AssessDifficultyStage(FifteenManhattanDifficultyAssessor()))
    )

    result = pipeline.run(request)

    difficulties = [
        candidate.difficulty.score
        for candidate in result.active_candidates
        if candidate.difficulty is not None
    ]

    print(difficulties)

    plot_active_difficulty_histogram(result, bins=100)

    # pipeline = (
    #     GenerationPipeline()
    #     .then(GenerateCandidatesStage(FisherYatesFifteenGenerator(seed=42, candidate_count=10000)))
    #     .then(GenerateCandidatesStage(ReverseShuffleFifteenGenerator(seed=42, candidate_count=10000,iterations=100)))
    #     .then(ValidateCandidatesStage(FifteenSolvabilityValidator()))
    #     .then(AssessDifficultyStage(FifteenManhattanDifficultyAssessor()))
    # )

    pipeline = GenerationPipeline()
    for i in range(10,1000):
        pipeline.add_stage(GenerateCandidatesStage(ReverseShuffleFifteenGenerator(seed=42, candidate_count=10,iterations=i)))
    pipeline.add_stage(ValidateCandidatesStage(FifteenSolvabilityValidator()))
    pipeline.add_stage(AssessDifficultyStage(FifteenManhattanDifficultyAssessor()))

    result = pipeline.run(request)

    difficulties = [
        candidate.difficulty.score
        for candidate in result.active_candidates
        if candidate.difficulty is not None
    ]

    # print(difficulties)

    plot_active_difficulty_histogram(result, bins=100)
if __name__ == "__main__": main()
