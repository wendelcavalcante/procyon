from procyon.player_modeling.probabilistic import ProbabilisticPlayerModelUpdater
from procyon.player_modeling.types import PlayerModelState
from procyon.telemetry.types import TelemetrySummary


def test_probabilistic_updater_increases_skill_after_unexpected_success() -> None:
    updater = ProbabilisticPlayerModelUpdater()

    previous = PlayerModelState(
        skill=0.40,
        uncertainty=0.50,
        confidence=0.50,
    )

    telemetry = TelemetrySummary(
        level_id="level_001",
        estimated_difficulty=0.75,
        success=True,
        give_up=False,
    )

    updated, observation = updater.update(previous, telemetry)

    assert observation is not None
    assert updated.skill > previous.skill
    assert updated.uncertainty < previous.uncertainty
    assert updated.confidence > previous.confidence


def test_probabilistic_updater_decreases_skill_after_unexpected_failure() -> None:
    updater = ProbabilisticPlayerModelUpdater()

    previous = PlayerModelState(
        skill=0.75,
        uncertainty=0.50,
        confidence=0.50,
    )

    telemetry = TelemetrySummary(
        level_id="level_001",
        estimated_difficulty=0.35,
        success=False,
        give_up=True,
    )

    updated, observation = updater.update(previous, telemetry)

    assert observation is not None
    assert updated.skill < previous.skill
    assert updated.uncertainty < previous.uncertainty
    assert updated.frustration > previous.frustration