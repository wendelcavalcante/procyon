from __future__ import annotations
from dataclasses import dataclass, field
from procyon.core.types import JsonDict
@dataclass(slots=True)
class DifficultyTarget:
    score: float
    tolerance: float = 0.10
    label: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    metadata: JsonDict = field(default_factory=dict)
    def contains(self, difficulty_score: float) -> bool:
        return abs(difficulty_score - self.score) <= self.tolerance
@dataclass(slots=True)
class DifficultyReport:
    score: float
    label: str | None = None
    confidence: float | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    method: str | None = None
    explanation: str | None = None
    metadata: JsonDict = field(default_factory=dict)
