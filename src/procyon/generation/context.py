from __future__ import annotations

from dataclasses import dataclass, field

from procyon.core.artifacts import (
    AdaptationRequest,
    CandidateRecord,
    GenerationMetadata,
)
from procyon.core.types import JsonDict


@dataclass(slots=True)
class GenerationContext:
    """
    Mutable context passed through pipeline stages.

    The context preserves every generated candidate. Stages may mark candidates
    as inactive instead of removing them, which enables later experimental analysis.
    """

    request: AdaptationRequest
    candidates: list[CandidateRecord] = field(default_factory=list)
    selected: CandidateRecord | None = None
    metadata: GenerationMetadata = field(default_factory=GenerationMetadata)
    scratch: JsonDict = field(default_factory=dict)

    @property
    def active_candidates(self) -> list[CandidateRecord]:
        return [candidate for candidate in self.candidates if candidate.is_active]