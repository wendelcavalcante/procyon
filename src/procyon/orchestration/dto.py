from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


JsonDict = dict[str, Any]


class RuntimeContextDTO(BaseModel):
    source: str = "unknown"
    game: str | None = None
    engine: str | None = None
    version: str | None = None
    metadata: JsonDict = Field(default_factory=dict)


class TelemetrySummaryDTO(BaseModel):
    level_id: str
    player_id: str | None = None
    session_id: str | None = None

    success: bool | None = None
    give_up: bool = False

    estimated_difficulty: float | None = None
    target_difficulty: float | None = None

    solving_time: float | None = None
    move_count: int | None = None
    mistake_count: int | None = None
    restart_count: int | None = None
    hint_count: int | None = None
    idle_time: float | None = None

    timestamp: datetime | None = None
    metadata: JsonDict = Field(default_factory=dict)


class PlayerModelStateDTO(BaseModel):
    skill: float = 0.50
    engagement: float = 0.50
    frustration: float = 0.00
    confidence: float = 0.10

    preferred_pace: float | None = None
    stability: float | None = None

    observations_count: int = 0
    metadata: JsonDict = Field(default_factory=dict)


class DesignGoalsDTO(BaseModel):
    target_experience: str | None = "balanced_challenge"
    allowed_dimensions: list[str] = Field(default_factory=lambda: ["difficulty"])
    constraints: JsonDict = Field(default_factory=dict)


class GenerationConfigDTO(BaseModel):
    """
    External generation configuration requested by a runtime or simulation.

    domain examples:
    - fifteen
    - sudoku
    - sokoban

    strategy examples:
    - generate_and_test
    - reverse_search
    - constructive
    """

    domain: str
    strategy: str | None = None
    candidate_count: int | None = None
    include_candidates: bool = False
    parameters: JsonDict = Field(default_factory=dict)


class AdaptiveGenerationRequestDTO(BaseModel):
    """
    DTO received by the Orchestration Layer.

    This object is transport-friendly and can be created from:
    - FastAPI request body;
    - file-based JSON exchange;
    - simulation code;
    - CLI input.
    """

    session_id: str | None = None
    player_id: str | None = None

    runtime: RuntimeContextDTO = Field(default_factory=RuntimeContextDTO)

    telemetry: TelemetrySummaryDTO | None = None
    last_player_state: PlayerModelStateDTO = Field(default_factory=PlayerModelStateDTO)
    design_goals: DesignGoalsDTO = Field(default_factory=DesignGoalsDTO)
    generation: GenerationConfigDTO


class AdaptationDecisionDTO(BaseModel):
    target_difficulty: float | None = None
    previous_difficulty: float | None = None
    reason: str | None = None
    confidence: float | None = None
    applied_constraints: list[str] = Field(default_factory=list)
    metadata: JsonDict = Field(default_factory=dict)


class CandidateSummaryDTO(BaseModel):
    candidate_id: int
    is_active: bool = True
    estimated_difficulty: float | None = None
    validation_score: float | None = None
    is_valid: bool | None = None
    metadata: JsonDict = Field(default_factory=dict)


class LevelArtifactDTO(BaseModel):
    content: JsonDict
    dimensions: list[str] = Field(default_factory=list)
    estimated_difficulty: float | None = None
    metadata: JsonDict = Field(default_factory=dict)


class GenerationResultSummaryDTO(BaseModel):
    candidate_count: int = 0
    active_candidate_count: int = 0
    selected_candidate_id: int | None = None
    candidates: list[CandidateSummaryDTO] | None = None
    metadata: JsonDict = Field(default_factory=dict)


class AdaptiveGenerationResponseDTO(BaseModel):
    session_id: str | None = None
    player_id: str | None = None

    updated_player_state: PlayerModelStateDTO
    adaptation_decision: AdaptationDecisionDTO | None = None

    selected_level: LevelArtifactDTO | None = None
    generation_result: GenerationResultSummaryDTO