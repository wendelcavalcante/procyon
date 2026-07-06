from __future__ import annotations

from dataclasses import dataclass, field

from procyon.core.artifacts import AdaptationRequest
from procyon.core.types import JsonDict


@dataclass(slots=True)
class AdaptationDecision:
    """
    Explanation and output of an adaptation step.

    The AdaptationRequest is the concrete object that will be sent to the
    Pipeline Builder / Generation Pipeline.
    """

    request: AdaptationRequest

    target_difficulty: float | None = None
    previous_difficulty: float | None = None

    reason: str | None = None
    confidence: float | None = None

    applied_constraints: list[str] = field(default_factory=list)
    metadata: JsonDict = field(default_factory=dict)