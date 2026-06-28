from __future__ import annotations
from dataclasses import dataclass, field
from procyon.core.artifacts import AdaptationRequest, GenerationMetadata, LevelArtifact, ValidationReport
from procyon.core.types import JsonDict
from procyon.dimensions.difficulty.types import DifficultyReport
@dataclass(slots=True)
class GenerationContext:
    request: AdaptationRequest
    candidates: list[LevelArtifact] = field(default_factory=list)
    selected: LevelArtifact | None = None
    validation_reports: dict[int, ValidationReport] = field(default_factory=dict)
    difficulty_reports: dict[int, DifficultyReport] = field(default_factory=dict)
    metadata: GenerationMetadata = field(default_factory=GenerationMetadata)
    scratch: JsonDict = field(default_factory=dict)
