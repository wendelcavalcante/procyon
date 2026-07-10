from __future__ import annotations

from dataclasses import dataclass

from procyon.player_modeling.types import PerformanceObservation, PlayerModelState
from procyon.telemetry.types import TelemetrySummary
from procyon.player_modeling.updaters import PlayerModelUpdater


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


@dataclass(slots=True)
class SimplePlayerModelUpdater(PlayerModelUpdater):
    """
    Initial player model updater.

    This is intentionally simple. It updates the player state from one telemetry
    summary and produces a performance observation for logging/explanation.
    """

    learning_rate: float = 0.08
    confidence_step: float = 0.04

    def update(
        self,
        previous_state: PlayerModelState,
        telemetry: TelemetrySummary | None,
    ) -> tuple[PlayerModelState, PerformanceObservation | None]:
        if telemetry is None:
            return previous_state, None

        performance_score = self._compute_performance_score(telemetry)
        estimated_difficulty = telemetry.estimated_difficulty

        skill_delta = self._compute_skill_delta(
            previous_skill=previous_state.skill,
            estimated_difficulty=estimated_difficulty,
            performance_score=performance_score,
        )

        frustration_delta = self._compute_frustration_delta(
            telemetry=telemetry,
            performance_score=performance_score,
        )

        engagement_delta = self._compute_engagement_delta(
            telemetry=telemetry,
            performance_score=performance_score,
        )

        confidence_delta = self.confidence_step * (1.0 - previous_state.confidence)

        updated_state = PlayerModelState(
            skill=_clamp(previous_state.skill + skill_delta),
            engagement=_clamp(previous_state.engagement + engagement_delta),
            frustration=_clamp(previous_state.frustration + frustration_delta),
            confidence=_clamp(previous_state.confidence + confidence_delta),
            preferred_pace=previous_state.preferred_pace,
            stability=previous_state.stability,
            observations_count=previous_state.observations_count + 1,
            metadata=dict(previous_state.metadata),
        )

        observation = PerformanceObservation(
            level_id=telemetry.level_id,
            estimated_difficulty=estimated_difficulty,
            success=telemetry.success,
            performance_score=performance_score,
            skill_delta=skill_delta,
            engagement_delta=engagement_delta,
            frustration_delta=frustration_delta,
            confidence_delta=confidence_delta,
            reason=self._reason_from_performance(performance_score),
            metadata={
                "updater": self.__class__.__name__,
                "learning_rate": self.learning_rate,
            },
        )

        return updated_state, observation

    def _compute_performance_score(self, telemetry: TelemetrySummary) -> float:
        success_score = 1.0 if telemetry.success else 0.0

        if telemetry.give_up:
            success_score = 0.0

        time_penalty = 0.0
        if telemetry.solving_time is not None:
            # Proxy simples: acima de 120s começa a penalizar mais.
            time_penalty = min(1.0, telemetry.solving_time / 120.0)

        mistake_penalty = 0.0
        if telemetry.mistake_count is not None:
            mistake_penalty = min(1.0, telemetry.mistake_count / 20.0)

        restart_penalty = 0.0
        if telemetry.restart_count is not None:
            restart_penalty = min(1.0, telemetry.restart_count / 5.0)

        hint_penalty = 0.0
        if telemetry.hint_count is not None:
            hint_penalty = min(1.0, telemetry.hint_count / 5.0)

        give_up_penalty = 1.0 if telemetry.give_up else 0.0

        score = (
            0.55 * success_score
            + 0.15 * (1.0 - time_penalty)
            + 0.15 * (1.0 - mistake_penalty)
            + 0.10 * (1.0 - restart_penalty)
            + 0.05 * (1.0 - hint_penalty)
            - 0.35 * give_up_penalty
        )

        return _clamp(score)

    def _compute_skill_delta(
        self,
        previous_skill: float,
        estimated_difficulty: float | None,
        performance_score: float,
    ) -> float:
        if estimated_difficulty is None:
            expected_performance = 0.50
        else:
            # Se dificuldade está abaixo da skill, espera-se performance maior.
            expected_performance = _clamp(0.50 + (previous_skill - estimated_difficulty))

        return self.learning_rate * (performance_score - expected_performance)

    def _compute_frustration_delta(
        self,
        telemetry: TelemetrySummary,
        performance_score: float,
    ) -> float:
        delta = 0.0

        if telemetry.give_up:
            delta += 0.12

        if telemetry.success:
            delta -= 0.04

        if performance_score < 0.35:
            delta += 0.06
        elif performance_score > 0.70:
            delta -= 0.03

        return delta

    def _compute_engagement_delta(
        self,
        telemetry: TelemetrySummary,
        performance_score: float,
    ) -> float:
        if telemetry.give_up:
            return -0.06

        if performance_score > 0.70:
            return 0.03

        if performance_score < 0.35:
            return -0.03

        return 0.01

    def _reason_from_performance(self, performance_score: float) -> str:
        if performance_score >= 0.70:
            return "player_performed_above_expected"

        if performance_score <= 0.35:
            return "player_performed_below_expected"

        return "player_performed_near_expected"