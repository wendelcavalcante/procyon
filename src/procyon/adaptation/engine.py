from __future__ import annotations

from abc import ABC, abstractmethod

from dataclasses import dataclass

from procyon.adaptation.types import AdaptationDecision
from procyon.core.artifacts import AdaptationRequest, DesignGoals
from procyon.core.types import AdaptiveDimension, GenerationStrategyType
from procyon.dimensions.difficulty.types import DifficultyTarget
from procyon.player_modeling.types import PlayerModelState


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


@dataclass
class AdaptationEngine(ABC):
    @abstractmethod
    def decide(
            self,
            player_state: PlayerModelState,
            design_goals: DesignGoals,
            domain: str,
            strategy_type: GenerationStrategyType | None,
            generation_parameters: dict,
        ) -> AdaptationDecision: ...

@dataclass(slots=True)
class SimpleAdaptationEngine(AdaptationEngine):
    """
    Initial adaptation engine.

    Converts player state + design goals + generation config into an
    AdaptationRequest for the Generation Core.
    """

    default_challenge_offset: float = 0.05

    def decide(
        self,
        player_state: PlayerModelState,
        design_goals: DesignGoals,
        domain: str,
        strategy_type: GenerationStrategyType | None,
        generation_parameters: dict,
    ) -> AdaptationDecision:
        constraints = design_goals.constraints

        min_difficulty = float(constraints.get("min_difficulty", 0.05))
        max_difficulty = float(constraints.get("max_difficulty", 0.95))
        max_step_change = constraints.get("max_step_change")

        previous_target = generation_parameters.get("previous_target_difficulty")
        previous_target = (
            float(previous_target)
            if previous_target is not None
            else None
        )

        challenge_offset = self._challenge_offset_for_experience(
            design_goals.target_experience
        )

        confidence = player_state.confidence

        # When confidence is low, the challenge offset is reduced.
        # This makes early adaptation more conservative.
        effective_offset = challenge_offset * confidence

        raw_target = player_state.skill + effective_offset

        applied_constraints: list[str] = []

        target = _clamp(raw_target, min_difficulty, max_difficulty)

        if target != raw_target:
            applied_constraints.append("min_max_difficulty")

        if previous_target is not None and max_step_change is not None:
            max_step_change = float(max_step_change)

            lower = previous_target - max_step_change
            upper = previous_target + max_step_change

            constrained = _clamp(target, lower, upper)

            if constrained != target:
                applied_constraints.append("max_step_change")

            target = constrained

        difficulty_target = DifficultyTarget(
            score=target,
            tolerance=float(constraints.get("difficulty_tolerance", 0.08)),
            label=None,
            metadata={
                "source": self.__class__.__name__,
                "player_skill": player_state.skill,
                "player_confidence": player_state.confidence,
                "player_uncertainty": player_state.uncertainty,
                "challenge_offset": challenge_offset,
                "effective_challenge_offset": effective_offset,
            },
        )

        target_parameters = dict(generation_parameters)
        target_parameters.update(
            {
                "domain": domain,
                "difficulty_target": difficulty_target,
                "target_difficulty": target,
            }
        )

        request = AdaptationRequest(
            dimensions=design_goals.allowed_dimensions or {AdaptiveDimension.DIFFICULTY},
            target_parameters=target_parameters,
            strategy_type=strategy_type,
            constraints=dict(constraints),
            design_goals=design_goals,
        )

        return AdaptationDecision(
            request=request,
            target_difficulty=target,
            previous_difficulty=previous_target,
            reason=self._reason(player_state, target),
            confidence=player_state.confidence,
            applied_constraints=applied_constraints,
            metadata={
                "engine": self.__class__.__name__,
                "target_experience": design_goals.target_experience,
                "domain": domain,
            },
        )

    def _challenge_offset_for_experience(self, target_experience: str | None) -> float:
        if target_experience is None:
            return self.default_challenge_offset

        normalized = target_experience.strip().lower()

        offsets = {
            "relaxed": -0.05,
            "casual": -0.03,
            "balanced": 0.05,
            "balanced_challenge": 0.05,
            "challenging": 0.12,
            "hardcore": 0.18,
        }

        return offsets.get(normalized, self.default_challenge_offset)

    def _reason(self, player_state: PlayerModelState, target: float) -> str:
        if target > player_state.skill:
            return "target_set_above_estimated_skill_for_challenge"

        if target < player_state.skill:
            return "target_set_below_estimated_skill_for_relief"

        return "target_matches_estimated_skill"