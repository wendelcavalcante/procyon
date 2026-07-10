from __future__ import annotations

from dataclasses import dataclass
from math import exp

from procyon.player_modeling.types import PerformanceObservation, PlayerModelState
from procyon.player_modeling.updaters import PlayerModelUpdater
from procyon.telemetry.types import TelemetrySummary


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = exp(-value)
        return 1.0 / (1.0 + z)

    z = exp(value)
    return z / (1.0 + z)


@dataclass(slots=True)
class ProbabilisticPlayerModelUpdater(PlayerModelUpdater):
    """
    Lightweight probabilistic player model updater.

    The updater estimates the expected probability of success from the current
    skill estimate and the difficulty of the previous level. It then updates
    skill according to the prediction error between expected and observed
    success.

    This is intentionally simple, but it is more structured than a purely
    heuristic rule because the update is driven by prediction error.
    """

    learning_rate: float = 0.30
    temperature: float = 0.18

    uncertainty_decay: float = 0.92
    min_uncertainty: float = 0.05
    max_uncertainty: float = 0.70

    frustration_learning_rate: float = 0.10
    engagement_learning_rate: float = 0.06

    def update(
        self,
        previous_state: PlayerModelState,
        telemetry: TelemetrySummary | None,
    ) -> tuple[PlayerModelState, PerformanceObservation | None]:
        if telemetry is None:
            return previous_state, None

        difficulty = self._resolve_difficulty(telemetry)
        observed_success = self._observed_success(telemetry)

        expected_success = self._expected_success(
            skill=previous_state.skill,
            difficulty=difficulty,
        )

        prediction_error = observed_success - expected_success

        uncertainty = _clamp(
            previous_state.uncertainty,
            self.min_uncertainty,
            self.max_uncertainty,
        )

        skill_delta = self.learning_rate * prediction_error * uncertainty
        new_skill = _clamp(previous_state.skill + skill_delta)

        new_uncertainty = max(
            self.min_uncertainty,
            uncertainty * self.uncertainty_decay,
        )

        new_confidence = _clamp(1.0 - new_uncertainty)

        performance_score = self._compute_performance_score(
            observed_success=observed_success,
            expected_success=expected_success,
            telemetry=telemetry,
        )

        frustration_delta = self._compute_frustration_delta(
            previous_state=previous_state,
            telemetry=telemetry,
            prediction_error=prediction_error,
            performance_score=performance_score,
        )

        engagement_delta = self._compute_engagement_delta(
            telemetry=telemetry,
            performance_score=performance_score,
        )

        updated_state = PlayerModelState(
            skill=new_skill,
            uncertainty=new_uncertainty,
            engagement=_clamp(previous_state.engagement + engagement_delta),
            frustration=_clamp(previous_state.frustration + frustration_delta),
            confidence=new_confidence,
            preferred_pace=previous_state.preferred_pace,
            stability=previous_state.stability,
            observations_count=previous_state.observations_count + 1,
            metadata={
                **previous_state.metadata,
                "player_model_updater": self.__class__.__name__,
                "last_expected_success": expected_success,
                "last_observed_success": observed_success,
                "last_prediction_error": prediction_error,
            },
        )

        observation = PerformanceObservation(
            level_id=telemetry.level_id,
            estimated_difficulty=difficulty,
            success=telemetry.success,
            performance_score=performance_score,
            skill_delta=skill_delta,
            engagement_delta=engagement_delta,
            frustration_delta=frustration_delta,
            confidence_delta=new_confidence - previous_state.confidence,
            reason=self._reason_from_error(prediction_error, observed_success),
            metadata={
                "updater": self.__class__.__name__,
                "difficulty": difficulty,
                "expected_success": expected_success,
                "observed_success": observed_success,
                "prediction_error": prediction_error,
                "previous_uncertainty": previous_state.uncertainty,
                "new_uncertainty": new_uncertainty,
                "temperature": self.temperature,
                "learning_rate": self.learning_rate,
            },
        )

        return updated_state, observation

    def _resolve_difficulty(self, telemetry: TelemetrySummary) -> float:
        if telemetry.estimated_difficulty is not None:
            return _clamp(telemetry.estimated_difficulty)

        if telemetry.target_difficulty is not None:
            return _clamp(telemetry.target_difficulty)

        return 0.50

    def _observed_success(self, telemetry: TelemetrySummary) -> float:
        if telemetry.give_up:
            return 0.0

        if telemetry.success is None:
            return 0.5

        return 1.0 if telemetry.success else 0.0

    def _expected_success(self, skill: float, difficulty: float) -> float:
        scaled_gap = (skill - difficulty) / self.temperature
        return _sigmoid(scaled_gap)

    def _compute_performance_score(
        self,
        observed_success: float,
        expected_success: float,
        telemetry: TelemetrySummary,
    ) -> float:
        """
        Produces a compact performance score for logging and downstream analysis.

        The probabilistic update itself is based on prediction error. This score
        additionally accounts for telemetry quality signals such as time,
        mistakes, restarts, hints, and give-up.
        """

        time_quality = 1.0
        if telemetry.solving_time is not None:
            time_quality = 1.0 - min(1.0, telemetry.solving_time / 180.0)

        mistake_quality = 1.0
        if telemetry.mistake_count is not None:
            mistake_quality = 1.0 - min(1.0, telemetry.mistake_count / 20.0)

        restart_quality = 1.0
        if telemetry.restart_count is not None:
            restart_quality = 1.0 - min(1.0, telemetry.restart_count / 5.0)

        hint_quality = 1.0
        if telemetry.hint_count is not None:
            hint_quality = 1.0 - min(1.0, telemetry.hint_count / 5.0)

        give_up_penalty = 1.0 if telemetry.give_up else 0.0

        surprise_bonus = max(0.0, observed_success - expected_success)

        score = (
            0.50 * observed_success
            + 0.15 * time_quality
            + 0.15 * mistake_quality
            + 0.10 * restart_quality
            + 0.05 * hint_quality
            + 0.05 * surprise_bonus
            - 0.30 * give_up_penalty
        )

        return _clamp(score)

    def _compute_frustration_delta(
        self,
        previous_state: PlayerModelState,
        telemetry: TelemetrySummary,
        prediction_error: float,
        performance_score: float,
    ) -> float:
        delta = 0.0

        if telemetry.give_up:
            delta += 0.12

        if telemetry.success:
            delta -= 0.03

        if prediction_error < -0.35:
            delta += 0.06

        if performance_score < 0.35:
            delta += 0.04

        if performance_score > 0.75:
            delta -= 0.03

        # High uncertainty should make frustration changes slightly more conservative.
        uncertainty_factor = 1.0 - 0.30 * previous_state.uncertainty

        return delta * self.frustration_learning_rate / 0.10 * uncertainty_factor

    def _compute_engagement_delta(
        self,
        telemetry: TelemetrySummary,
        performance_score: float,
    ) -> float:
        if telemetry.give_up:
            return -self.engagement_learning_rate

        if performance_score > 0.75:
            return self.engagement_learning_rate * 0.75

        if performance_score < 0.35:
            return -self.engagement_learning_rate * 0.50

        return self.engagement_learning_rate * 0.20

    def _reason_from_error(
        self,
        prediction_error: float,
        observed_success: float,
    ) -> str:
        if observed_success >= 1.0 and prediction_error > 0.25:
            return "player_exceeded_probabilistic_expectation"

        if observed_success <= 0.0 and prediction_error < -0.25:
            return "player_underperformed_probabilistic_expectation"

        return "player_performed_near_probabilistic_expectation"