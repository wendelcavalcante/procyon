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
class GenerationResult:
    level: LevelArtifact
    validation: ValidationReport | None = None
    difficulty: object | None = None
    metadata: GenerationMetadata = field(default_factory=GenerationMetadata)
