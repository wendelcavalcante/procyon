from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Self

from procyon.core.artifacts import AdaptationRequest, GenerationResult
from procyon.generation.context import GenerationContext


class PipelineStage(ABC):
    """A single stage in a composable generation pipeline."""

    @abstractmethod
    def process(self, context: GenerationContext) -> GenerationContext:
        """Process and return the generation context."""


@dataclass(slots=True)
class GenerationPipeline:
    """
    Sequence of stages assembled according to the selected strategy.

    A pipeline may or may not select a final candidate. This supports both
    runtime usage and experimental analysis.
    """

    stages: list[PipelineStage] = field(default_factory=list)

    def then(self, stage: PipelineStage) -> Self:
        self.stages.append(stage)
        return self

    def add_stage(self, stage: PipelineStage) -> Self:
        return self.then(stage)

    def add_stages(self, stages: list[PipelineStage]) -> Self:
        self.stages.extend(stages)
        return self

    def run(self, request: AdaptationRequest) -> GenerationResult:
        context = GenerationContext(request=request)

        for stage in self.stages:
            context = stage.process(context)

        return GenerationResult(
            candidates=context.candidates,
            selected=context.selected,
            metadata=context.metadata,
        )