from __future__ import annotations

from dataclasses import dataclass

from procyon.core.artifacts import AdaptationRequest
from procyon.core.types import GenerationStrategyType
from procyon.generation.pipeline import GenerationPipeline
from procyon.generation.stages import (
    AssessDifficultyStage,
    GenerateCandidatesStage,
    SelectClosestDifficultyCandidateStage,
    ValidateCandidatesStage,
)


@dataclass(slots=True)
class DefaultPipelineBuilder:
    """
    Builds generation pipelines from an AdaptationRequest.

    This first version supports the plugins already implemented:
    - fifteen
    - sudoku
    - sokoban
    """

    def build(self, request: AdaptationRequest) -> GenerationPipeline:
        domain = str(request.target_parameters.get("domain", "")).strip().lower()

        if domain == "fifteen":
            return self._build_fifteen_pipeline(request)

        if domain == "sudoku":
            return self._build_sudoku_pipeline(request)

        if domain == "sokoban":
            return self._build_sokoban_pipeline(request)

        raise ValueError(f"Unsupported generation domain: {domain}")

    def _build_fifteen_pipeline(self, request: AdaptationRequest) -> GenerationPipeline:
        from procyon.plugins.puzzles.fifteen import (
            FifteenManhattanDifficultyAssessor,
            FifteenSolvabilityValidator,
            FisherYatesFifteenGenerator,
            ReverseShuffleFifteenGenerator,
        )

        parameters = request.target_parameters
        candidate_count = int(parameters.get("candidate_count", 50))
        seed = parameters.get("seed")
        select = bool(parameters.get("select", True))

        strategy = request.strategy_type

        if strategy == GenerationStrategyType.REVERSE_SEARCH:
            generator = ReverseShuffleFifteenGenerator(
                seed=seed,
                iterations=int(parameters.get("iterations", 80)),
                candidate_count=candidate_count,
            )

            pipeline = (
                GenerationPipeline()
                .then(GenerateCandidatesStage(generator))
                .then(AssessDifficultyStage(FifteenManhattanDifficultyAssessor()))
            )

        else:
            generator = FisherYatesFifteenGenerator(
                seed=seed,
                candidate_count=candidate_count,
            )

            pipeline = (
                GenerationPipeline()
                .then(GenerateCandidatesStage(generator))
                .then(ValidateCandidatesStage(FifteenSolvabilityValidator()))
                .then(AssessDifficultyStage(FifteenManhattanDifficultyAssessor()))
            )

        if select:
            pipeline.then(SelectClosestDifficultyCandidateStage())

        return pipeline

    def _build_sudoku_pipeline(self, request: AdaptationRequest) -> GenerationPipeline:
        from procyon.plugins.puzzles.sudoku import (
            RandomBacktrackingSudokuGenerator,
            RemoveSudokuCluesStage,
            SudokuSearchDifficultyAssessor,
            SudokuUniqueSolutionValidator,
        )

        parameters = request.target_parameters

        candidate_count = int(parameters.get("candidate_count", 200))
        seed = parameters.get("seed")
        target_clues = int(parameters.get("target_clues", 32))
        removal_strategy = str(parameters.get("clue_removal_strategy", "symmetric"))
        select = bool(parameters.get("select", False))

        pipeline = (
            GenerationPipeline()
            .then(
                GenerateCandidatesStage(
                    RandomBacktrackingSudokuGenerator(
                        seed=seed,
                        candidate_count=candidate_count,
                    )
                )
            )
            .then(
                RemoveSudokuCluesStage(
                    strategy=removal_strategy,
                    target_clues=target_clues,
                    seed=seed,
                )
            )
            .then(ValidateCandidatesStage(SudokuUniqueSolutionValidator()))
            .then(AssessDifficultyStage(SudokuSearchDifficultyAssessor()))
        )

        if select:
            pipeline.then(SelectClosestDifficultyCandidateStage())

        return pipeline

    def _build_sokoban_pipeline(self, request: AdaptationRequest) -> GenerationPipeline:
        from procyon.plugins.puzzles.sokoban import (
            ReverseSokobanGenerator,
            SokobanReverseDifficultyAssessor,
        )

        parameters = request.target_parameters

        candidate_count = int(parameters.get("candidate_count", 50))
        seed = parameters.get("seed")
        select = bool(parameters.get("select", False))

        pipeline = (
            GenerationPipeline()
            .then(
                GenerateCandidatesStage(
                    ReverseSokobanGenerator(
                        width=int(parameters.get("width", 9)),
                        height=int(parameters.get("height", 9)),
                        reverse_steps=int(parameters.get("reverse_steps", 30)),
                        candidate_count=candidate_count,
                        seed=seed,
                        avoid_backtracking=bool(parameters.get("avoid_backtracking", True)),
                        wall_density=float(parameters.get("wall_density", 0.12)),
                        ensure_connected_floor=bool(
                            parameters.get("ensure_connected_floor", True)
                        ),
                    )
                )
            )
            .then(AssessDifficultyStage(SokobanReverseDifficultyAssessor()))
        )

        if select:
            pipeline.then(SelectClosestDifficultyCandidateStage())

        return pipeline