from __future__ import annotations

from dataclasses import dataclass, field

from procyon.core.types import AdaptiveDimension, GenerationStrategyType, JsonDict


@dataclass(slots=True)
class DesignGoals:
    target_experience: str | None = None
    allowed_dimensions: set[AdaptiveDimension] = field(default_factory=set)
    constraints: JsonDict = field(default_factory=dict)


@dataclass(slots=True)
class PlayerState:
    skill: float
    engagement: float | None = None
    frustration: float | None = None
    confidence: float | None = None
    metadata: JsonDict = field(default_factory=dict)


@dataclass(slots=True)
class AdaptationRequest:
    dimensions: set[AdaptiveDimension]
    target_parameters: JsonDict
    strategy_type: GenerationStrategyType | None = None
    constraints: JsonDict = field(default_factory=dict)
    player_state: PlayerState | None = None
    design_goals: DesignGoals | None = None


@dataclass(slots=True)
class LevelArtifact:
    content: JsonDict
    dimensions: set[AdaptiveDimension]
    estimated_difficulty: float | None = None
    metadata: JsonDict = field(default_factory=dict)


@dataclass(slots=True)
class ValidationReport:
    is_valid: bool
    score: float | None = None
    messages: list[str] = field(default_factory=list)
    metadata: JsonDict = field(default_factory=dict)


@dataclass(slots=True)
class GenerationMetadata:
    strategy_type: GenerationStrategyType | None = None
    elapsed_ms: float | None = None
    attempts: int = 0
    metadata: JsonDict = field(default_factory=dict)


@dataclass(slots=True)
class CandidateRecord:
    """
    Stores all information produced for a generated candidate.

    A candidate may be inactive, for example, if it failed validation,
    but it remains available for experimental analysis.
    """

    candidate_id: int
    level: LevelArtifact
    validation: ValidationReport | None = None
    difficulty: object | None = None
    score: float | None = None
    is_active: bool = True
    metadata: JsonDict = field(default_factory=dict)


@dataclass(slots=True)
class GenerationResult:
    """
    Result returned by a generation pipeline.

    It may contain one selected candidate, many generated candidates,
    or only raw generated candidates depending on which stages were used.
    """

    candidates: list[CandidateRecord] = field(default_factory=list)
    selected: CandidateRecord | None = None
    metadata: GenerationMetadata = field(default_factory=GenerationMetadata)

    @property
    def levels(self) -> list[LevelArtifact]:
        return [candidate.level for candidate in self.candidates]

    @property
    def active_candidates(self) -> list[CandidateRecord]:
        return [candidate for candidate in self.candidates if candidate.is_active]

    @property
    def selected_level(self) -> LevelArtifact | None:
        return self.selected.level if self.selected is not None else None

    @property
    def selected_validation(self) -> ValidationReport | None:
        return self.selected.validation if self.selected is not None else None

    @property
    def selected_difficulty(self) -> object | None:
        return self.selected.difficulty if self.selected is not None else None

    def require_selected(self) -> CandidateRecord:
        if self.selected is None:
            raise RuntimeError("This generation result has no selected candidate.")
        return self.selected