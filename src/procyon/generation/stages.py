from __future__ import annotations

from dataclasses import dataclass

from procyon.core.artifacts import CandidateRecord
from procyon.dimensions.difficulty.assessment import DifficultyAssessor
from procyon.dimensions.difficulty.types import DifficultyTarget
from procyon.generation.context import GenerationContext
from procyon.generation.generators import ContentGenerator
from procyon.generation.pipeline import PipelineStage
from procyon.validation.validators import Validator


@dataclass(slots=True)
class GenerateCandidatesStage(PipelineStage):
    generator: ContentGenerator

    def process(self, context: GenerationContext) -> GenerationContext:
        levels = self.generator.generate(context.request)

        start_index = len(context.candidates)

        for offset, level in enumerate(levels):
            candidate_id = start_index + offset
            context.candidates.append(
                CandidateRecord(
                    candidate_id=candidate_id,
                    level=level,
                    metadata={
                        "generated_by": self.generator.__class__.__name__,
                    },
                )
            )

        context.metadata.attempts = len(context.candidates)
        return context


@dataclass(slots=True)
class ValidateCandidatesStage(PipelineStage):
    """
    Validates candidates.

    If deactivate_invalid=True, invalid candidates remain in the result but are
    marked as inactive. This preserves them for analysis while preventing later
    runtime-oriented stages from selecting them.
    """

    validator: Validator
    deactivate_invalid: bool = True
    only_active: bool = True

    def process(self, context: GenerationContext) -> GenerationContext:
        candidates = context.active_candidates if self.only_active else context.candidates

        for candidate in candidates:
            report = self.validator.validate(candidate.level)
            candidate.validation = report

            if self.deactivate_invalid and not report.is_valid:
                candidate.is_active = False

        return context


@dataclass(slots=True)
class AssessDifficultyStage(PipelineStage):
    """
    Assesses candidate difficulty.

    By default, only active candidates are assessed. Set only_active=False if
    you want difficulty estimates for invalid candidates too.
    """

    assessor: DifficultyAssessor
    only_active: bool = True

    def process(self, context: GenerationContext) -> GenerationContext:
        candidates = context.active_candidates if self.only_active else context.candidates

        for candidate in candidates:
            candidate.difficulty = self.assessor.assess(candidate.level, context)

        return context


@dataclass(slots=True)
class SelectFirstCandidateStage(PipelineStage):
    """
    Selects the first active candidate.
    """

    def process(self, context: GenerationContext) -> GenerationContext:
        active_candidates = context.active_candidates

        if not active_candidates:
            raise RuntimeError("No active candidates available for selection.")

        context.selected = active_candidates[0]
        return context


@dataclass(slots=True)
class SelectClosestDifficultyCandidateStage(PipelineStage):
    """
    Selects the active candidate whose assessed difficulty is closest to the target.
    """

    target_parameter_name: str = "difficulty_target"

    def process(self, context: GenerationContext) -> GenerationContext:
        active_candidates = context.active_candidates

        if not active_candidates:
            raise RuntimeError("No active candidates available for selection.")

        target = self._resolve_target(context)

        best_candidate: CandidateRecord | None = None
        best_distance: float | None = None

        for candidate in active_candidates:
            if candidate.difficulty is None:
                raise RuntimeError(
                    "Missing difficulty report for candidate "
                    f"{candidate.candidate_id}. Did you forget AssessDifficultyStage?"
                )

            difficulty_score = float(candidate.difficulty.score)
            distance = abs(difficulty_score - target.score)

            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_candidate = candidate

        if best_candidate is None:
            raise RuntimeError("Could not select a candidate by difficulty.")

        context.selected = best_candidate
        context.scratch["selection"] = {
            "selector": self.__class__.__name__,
            "selected_candidate_id": best_candidate.candidate_id,
            "target_difficulty": target.score,
            "selected_difficulty": best_candidate.difficulty.score,
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

        raw_score = context.request.target_parameters.get("target_difficulty")

        if isinstance(raw_score, int | float):
            return DifficultyTarget(score=float(raw_score))

        raise RuntimeError(
            "Missing difficulty target. Expected 'difficulty_target' or "
            "'target_difficulty' in AdaptationRequest.target_parameters."
        )