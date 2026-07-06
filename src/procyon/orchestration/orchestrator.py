from __future__ import annotations

from dataclasses import dataclass

from procyon.adaptation.engine import SimpleAdaptationEngine
from procyon.orchestration.dto import (
    AdaptationDecisionDTO,
    AdaptiveGenerationRequestDTO,
    AdaptiveGenerationResponseDTO,
)
from procyon.orchestration.mappers import (
    design_goals_from_dto,
    generation_result_summary_to_dto,
    level_to_dto,
    player_state_from_dto,
    player_state_to_dto,
    strategy_from_string,
    telemetry_from_dto,
)
from procyon.orchestration.pipeline_builder import DefaultPipelineBuilder
from procyon.player_modeling.updater import SimplePlayerModelUpdater


@dataclass(slots=True)
class AdaptiveGenerationOrchestrator:
    """
    Coordinates the adaptive generation use case.

    This class is intentionally independent from FastAPI, Unity, files or any
    specific runtime integration.
    """

    player_model_updater: SimplePlayerModelUpdater
    adaptation_engine: SimpleAdaptationEngine
    pipeline_builder: DefaultPipelineBuilder

    def generate_next(
        self,
        request_dto: AdaptiveGenerationRequestDTO,
    ) -> AdaptiveGenerationResponseDTO:
        telemetry = telemetry_from_dto(request_dto.telemetry)
        previous_player_state = player_state_from_dto(request_dto.last_player_state)
        design_goals = design_goals_from_dto(request_dto.design_goals)

        updated_player_state, performance_observation = self.player_model_updater.update(
            previous_state=previous_player_state,
            telemetry=telemetry,
        )

        strategy_type = strategy_from_string(request_dto.generation.strategy)

        generation_parameters = dict(request_dto.generation.parameters)

        if request_dto.generation.candidate_count is not None:
            generation_parameters["candidate_count"] = request_dto.generation.candidate_count

        # By default, runtime-style requests select one candidate.
        # Experimental requests can set parameters.select = False.
        generation_parameters.setdefault("select", True)

        if performance_observation is not None:
            generation_parameters["last_performance_score"] = (
                performance_observation.performance_score
            )

        adaptation_decision = self.adaptation_engine.decide(
            player_state=updated_player_state,
            design_goals=design_goals,
            domain=request_dto.generation.domain,
            strategy_type=strategy_type,
            generation_parameters=generation_parameters,
        )

        pipeline = self.pipeline_builder.build(adaptation_decision.request)
        generation_result = pipeline.run(adaptation_decision.request)

        selected_level = (
            level_to_dto(generation_result.selected.level)
            if generation_result.selected is not None
            else None
        )

        return AdaptiveGenerationResponseDTO(
            session_id=request_dto.session_id,
            player_id=request_dto.player_id,
            updated_player_state=player_state_to_dto(updated_player_state),
            adaptation_decision=AdaptationDecisionDTO(
                target_difficulty=adaptation_decision.target_difficulty,
                previous_difficulty=adaptation_decision.previous_difficulty,
                reason=adaptation_decision.reason,
                confidence=adaptation_decision.confidence,
                applied_constraints=adaptation_decision.applied_constraints,
                metadata=adaptation_decision.metadata,
            ),
            selected_level=selected_level,
            generation_result=generation_result_summary_to_dto(
                generation_result,
                include_candidates=request_dto.generation.include_candidates,
            ),
        )


def create_default_orchestrator() -> AdaptiveGenerationOrchestrator:
    return AdaptiveGenerationOrchestrator(
        player_model_updater=SimplePlayerModelUpdater(),
        adaptation_engine=SimpleAdaptationEngine(),
        pipeline_builder=DefaultPipelineBuilder(),
    )