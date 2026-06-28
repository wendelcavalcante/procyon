from __future__ import annotations
from dataclasses import dataclass
from procyon.dimensions.difficulty.assessment import DifficultyAssessor
from procyon.generation.generators import ContentGenerator
from procyon.generation.pipeline import PipelineStage
from procyon.generation.context import GenerationContext
from procyon.validation.validators import Validator
from procyon.dimensions.difficulty.types import DifficultyTarget
@dataclass(slots=True)
class GenerateCandidatesStage(PipelineStage):
    generator: ContentGenerator
    def process(self, context: GenerationContext) -> GenerationContext:
        context.candidates = self.generator.generate(context.request)
        context.metadata.attempts = len(context.candidates)
        return context
@dataclass(slots=True)
class ValidateCandidatesStage(PipelineStage):
    validator: Validator
    keep_only_valid: bool = True
    def process(self, context: GenerationContext) -> GenerationContext:
        original_candidates = list(context.candidates)
        valid_candidates = []
        for original_index, candidate in enumerate(original_candidates):
            report = self.validator.validate(candidate)
            context.validation_reports[original_index] = report
            if report.is_valid or not self.keep_only_valid:
                valid_candidates.append(candidate)
        context.candidates = valid_candidates
        return context
@dataclass(slots=True)
class AssessDifficultyStage(PipelineStage):
    assessor: DifficultyAssessor
    def process(self, context: GenerationContext) -> GenerationContext:
        for index, candidate in enumerate(context.candidates):
            context.difficulty_reports[index] = self.assessor.assess(candidate, context)
        return context
@dataclass(slots=True)
class SelectFirstCandidateStage(PipelineStage):
    def process(self, context: GenerationContext) -> GenerationContext:
        if not context.candidates:
            raise RuntimeError("No candidates available for selection.")
        context.selected = context.candidates[0]
        return context
@dataclass(slots=True)
class SelectClosestDifficultyCandidateStage(PipelineStage):
    """
    Selects the candidate whose assessed difficulty is closest to the target difficulty.

    This stage expects that an AssessDifficultyStage has already populated
    context.difficulty_reports.
    """

    target_parameter_name: str = "difficulty_target"

    def process(self, context: GenerationContext) -> GenerationContext:
        if not context.candidates:
            raise RuntimeError("No candidates available for selection.")

        target = self._resolve_target(context)

        best_candidate_index: int | None = None
        best_distance: float | None = None

        for index, candidate in enumerate(context.candidates):
            report = context.difficulty_reports.get(index)

            if report is None:
                raise RuntimeError(
                    "Missing difficulty report for candidate index "
                    f"{index}. Did you forget to add AssessDifficultyStage?"
                )

            distance = abs(report.score - target.score)

            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_candidate_index = index

        if best_candidate_index is None:
            raise RuntimeError("Could not select a candidate by difficulty.")

        context.selected = context.candidates[best_candidate_index]
        context.scratch["selection"] = {
            "selector": self.__class__.__name__,
            "selected_candidate_index": best_candidate_index,
            "target_difficulty": target.score,
            "selected_difficulty": context.difficulty_reports[best_candidate_index].score,
            "distance_to_target": best_distance,
        }

        return context

    def _resolve_target(self, context: GenerationContext) -> DifficultyTarget:
        raw_target = context.request.target_parameters.get(self.target_parameter_name)

        if isinstance(raw_target, DifficultyTarget):
            return raw_target

        if isinstance(raw_target, int | float):
            return DifficultyTarget(score=float(raw_target))

        if isinstance(raw_target, dict):
            return DifficultyTarget(
                score=float(raw_target["score"]),
                tolerance=float(raw_target.get("tolerance", 0.10)),
                label=raw_target.get("label"),
                metrics=raw_target.get("metrics", {}),
                metadata=raw_target.get("metadata", {}),
            )

        # Fallback for the simpler parameter name used in early examples.
        raw_score = context.request.target_parameters.get("target_difficulty")

        if isinstance(raw_score, int | float):
            return DifficultyTarget(score=float(raw_score))

        raise RuntimeError(
            "Missing difficulty target. Expected one of: "
            f"'{self.target_parameter_name}' as DifficultyTarget/dict/number, "
            "or 'target_difficulty' as number."
        )
