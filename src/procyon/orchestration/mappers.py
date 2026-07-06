from __future__ import annotations

from procyon.core.artifacts import DesignGoals, LevelArtifact
from procyon.core.types import AdaptiveDimension, GenerationStrategyType
from procyon.generation.context import GenerationContext
from procyon.player_modeling.types import PlayerModelState
from procyon.telemetry.types import TelemetrySummary
from dataclasses import asdict, is_dataclass
from procyon.orchestration.dto import (
    AdaptationDecisionDTO,
    AdaptiveGenerationResponseDTO,
    CandidateSummaryDTO,
    DesignGoalsDTO,
    GenerationResultSummaryDTO,
    LevelArtifactDTO,
    PlayerModelStateDTO,
    TelemetrySummaryDTO,
)

def _json_safe_metadata(value) -> dict:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if is_dataclass(value):
        return asdict(value)

    return {"value": str(value)}

def telemetry_from_dto(dto: TelemetrySummaryDTO | None) -> TelemetrySummary | None:
    if dto is None:
        return None

    return TelemetrySummary(
        level_id=dto.level_id,
        player_id=dto.player_id,
        session_id=dto.session_id,
        success=dto.success,
        give_up=dto.give_up,
        estimated_difficulty=dto.estimated_difficulty,
        target_difficulty=dto.target_difficulty,
        solving_time=dto.solving_time,
        move_count=dto.move_count,
        mistake_count=dto.mistake_count,
        restart_count=dto.restart_count,
        hint_count=dto.hint_count,
        idle_time=dto.idle_time,
        timestamp=dto.timestamp,
        metadata=dto.metadata,
    )


def player_state_from_dto(dto: PlayerModelStateDTO) -> PlayerModelState:
    return PlayerModelState(
        skill=dto.skill,
        engagement=dto.engagement,
        frustration=dto.frustration,
        confidence=dto.confidence,
        preferred_pace=dto.preferred_pace,
        stability=dto.stability,
        observations_count=dto.observations_count,
        metadata=dto.metadata,
    )


def player_state_to_dto(state: PlayerModelState) -> PlayerModelStateDTO:
    return PlayerModelStateDTO(
        skill=state.skill,
        engagement=state.engagement,
        frustration=state.frustration,
        confidence=state.confidence,
        preferred_pace=state.preferred_pace,
        stability=state.stability,
        observations_count=state.observations_count,
        metadata=state.metadata,
    )


def design_goals_from_dto(dto: DesignGoalsDTO) -> DesignGoals:
    return DesignGoals(
        target_experience=dto.target_experience,
        allowed_dimensions={
            _adaptive_dimension_from_string(value)
            for value in dto.allowed_dimensions
        },
        constraints=dto.constraints,
    )


def strategy_from_string(value: str | None) -> GenerationStrategyType | None:
    if value is None:
        return None

    normalized = value.strip().lower()

    aliases = {
        "generate_and_test": GenerationStrategyType.GENERATE_AND_TEST,
        "generate-and-test": GenerationStrategyType.GENERATE_AND_TEST,
        "constructive": GenerationStrategyType.CONSTRUCTIVE,
        "reverse_search": GenerationStrategyType.REVERSE_SEARCH,
        "reverse-search": GenerationStrategyType.REVERSE_SEARCH,
        "reverse": GenerationStrategyType.REVERSE_SEARCH,
        "wfc": GenerationStrategyType.WFC,
        "ml": GenerationStrategyType.ML_MODEL,
        "ml_model": GenerationStrategyType.ML_MODEL,
        "llm": GenerationStrategyType.LLM_LOCAL,
        "llm_local": GenerationStrategyType.LLM_LOCAL,
        "custom": GenerationStrategyType.CUSTOM,
    }

    if normalized not in aliases:
        raise ValueError(f"Unknown generation strategy: {value}")

    return aliases[normalized]


def level_to_dto(level: LevelArtifact) -> LevelArtifactDTO:
    return LevelArtifactDTO(
        content=level.content,
        dimensions=[dimension.value for dimension in level.dimensions],
        estimated_difficulty=level.estimated_difficulty,
        metadata=level.metadata,
    )


def generation_result_summary_to_dto(
    context_or_result,
    include_candidates: bool = False,
) -> GenerationResultSummaryDTO:
    candidates = context_or_result.candidates
    selected = context_or_result.selected

    candidate_summaries: list[CandidateSummaryDTO] | None = None

    if include_candidates:
        candidate_summaries = [
            CandidateSummaryDTO(
                candidate_id=candidate.candidate_id,
                is_active=candidate.is_active,
                estimated_difficulty=(
                    candidate.difficulty.score
                    if candidate.difficulty is not None
                    else candidate.level.estimated_difficulty
                ),
                validation_score=(
                    candidate.validation.score
                    if candidate.validation is not None
                    else None
                ),
                is_valid=(
                    candidate.validation.is_valid
                    if candidate.validation is not None
                    else None
                ),
                metadata=candidate.metadata,
            )
            for candidate in candidates
        ]

    return GenerationResultSummaryDTO(
        candidate_count=len(candidates),
        active_candidate_count=sum(1 for candidate in candidates if candidate.is_active),
        selected_candidate_id=selected.candidate_id if selected is not None else None,
        candidates=candidate_summaries,
        metadata=_json_safe_metadata(getattr(context_or_result, "metadata", {})),
    )


def _adaptive_dimension_from_string(value: str) -> AdaptiveDimension:
    normalized = value.strip().lower()

    aliases = {
        "difficulty": AdaptiveDimension.DIFFICULTY,
        "gameplay": AdaptiveDimension.GAMEPLAY,
        "layout": AdaptiveDimension.LAYOUT,
        "spatial": AdaptiveDimension.LAYOUT,
        "assets": AdaptiveDimension.ASSETS,
        "soundtrack": AdaptiveDimension.SOUNDTRACK,
        "music": AdaptiveDimension.SOUNDTRACK,
        "narrative": AdaptiveDimension.NARRATIVE,
    }

    if normalized not in aliases:
        raise ValueError(f"Unknown adaptive dimension: {value}")

    return aliases[normalized]