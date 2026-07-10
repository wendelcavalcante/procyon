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
from procyon.player_modeling.probabilistic import ProbabilisticPlayerModelUpdater
from procyon.player_modeling.updaters import PlayerModelUpdater
from procyon.persistence.unit_of_work import PersistenceStore

from pathlib import Path

from procyon.persistence.sqlite import (
    SQLiteAdaptationDecisionRepository,
    SQLiteConnectionFactory,
    SQLitePerformanceObservationRepository,
    SQLitePlayerStateRepository,
    SQLiteTelemetryRepository,
    initialize_sqlite_database,
)
from procyon.persistence.unit_of_work import PersistenceStore
from procyon.player_modeling.types import PlayerModelState

@dataclass(slots=True)
class AdaptiveGenerationOrchestrator:
    player_model_updater: PlayerModelUpdater
    adaptation_engine: SimpleAdaptationEngine
    pipeline_builder: DefaultPipelineBuilder
    persistence_store: PersistenceStore | None = None

    def _resolve_previous_player_state(
        self,
        player_id: str | None,
        request_dto: AdaptiveGenerationRequestDTO,
    ) -> PlayerModelState:
        if (
            player_id is not None
            and self.persistence_store is not None
        ):
            persisted_state = self.persistence_store.player_states.get(player_id)

            if persisted_state is not None:
                return persisted_state

        if request_dto.last_player_state is not None:
            return player_state_from_dto(request_dto.last_player_state)

        return PlayerModelState()    

    def _resolve_persistence_player_id(
        self,
        player_id: str | None,
        domain: str,
    ) -> str | None:
        if player_id is None:
            return None

        normalized_domain = domain.strip().lower()
        return f"{player_id}::{normalized_domain}"    
    
    def generate_next(
        self,
        request_dto: AdaptiveGenerationRequestDTO,
    ) -> AdaptiveGenerationResponseDTO:
        telemetry = telemetry_from_dto(request_dto.telemetry)
        external_player_id = request_dto.player_id
        session_id = request_dto.session_id
        domain = request_dto.generation.domain

        persistence_player_id = self._resolve_persistence_player_id(
            player_id=external_player_id,
            domain=domain,
        )
        session_id = request_dto.session_id

        previous_player_state = self._resolve_previous_player_state(
            player_id=persistence_player_id,
            request_dto=request_dto,
        )

        design_goals = design_goals_from_dto(request_dto.design_goals)

        if telemetry is not None:
            if telemetry.player_id is None:
                telemetry.player_id = persistence_player_id

            if telemetry.session_id is None:
                telemetry.session_id = session_id

        updated_player_state, performance_observation = self.player_model_updater.update(
            previous_state=previous_player_state,
            telemetry=telemetry,
        )

        if persistence_player_id is not None and self.persistence_store is not None:
            self.persistence_store.player_states.save(
                persistence_player_id,
                updated_player_state,
            )

            if performance_observation is not None:
                self.persistence_store.observations.save(
                    player_id=persistence_player_id,
                    session_id=session_id,
                    observation=performance_observation,
                )

        strategy_type = strategy_from_string(request_dto.generation.strategy)

        generation_parameters = dict(request_dto.generation.parameters)

        if request_dto.generation.candidate_count is not None:
            generation_parameters["candidate_count"] = request_dto.generation.candidate_count

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

        if persistence_player_id is not None and self.persistence_store is not None:
            self.persistence_store.adaptation_decisions.save(
                player_id=persistence_player_id,
                session_id=session_id,
                decision=adaptation_decision,
            )

        pipeline = self.pipeline_builder.build(adaptation_decision.request)
        generation_result = pipeline.run(adaptation_decision.request)

        selected_level = (
            level_to_dto(generation_result.selected.level)
            if generation_result.selected is not None
            else None
        )

        updated_player_state.metadata["external_player_id"] = external_player_id
        updated_player_state.metadata["domain"] = domain
        updated_player_state.metadata["persistence_player_id"] = persistence_player_id

        return AdaptiveGenerationResponseDTO(
            session_id=session_id,
            player_id=external_player_id,
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
        player_model_updater=ProbabilisticPlayerModelUpdater(),
        adaptation_engine=SimpleAdaptationEngine(),
        pipeline_builder=DefaultPipelineBuilder(),
    )

def create_sqlite_orchestrator(
    database_path: str | Path = "procyon.sqlite3",
) -> AdaptiveGenerationOrchestrator:
    factory = SQLiteConnectionFactory(database_path)
    initialize_sqlite_database(factory)

    store = PersistenceStore(
        player_states=SQLitePlayerStateRepository(factory),
        telemetry=SQLiteTelemetryRepository(factory),
        observations=SQLitePerformanceObservationRepository(factory),
        adaptation_decisions=SQLiteAdaptationDecisionRepository(factory),
    )

    return AdaptiveGenerationOrchestrator(
        player_model_updater=ProbabilisticPlayerModelUpdater(),
        adaptation_engine=SimpleAdaptationEngine(),
        pipeline_builder=DefaultPipelineBuilder(),
        persistence_store=store,
    )
