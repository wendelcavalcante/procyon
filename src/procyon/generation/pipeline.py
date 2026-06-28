from __future__ import annotations

from dataclasses import dataclass, field

from procyon.core.artifacts import AdaptationRequest, GenerationResult
from procyon.generation.context import GenerationContext


class PipelineStage:
    def process(self, context: GenerationContext) -> GenerationContext:
        raise NotImplementedError


@dataclass(slots=True)
class GenerationPipeline:
    stages: list[PipelineStage] = field(default_factory=list)

    def add_stage(self, stage: PipelineStage) -> GenerationPipeline:
        self.stages.append(stage)
        return self

    def add_stages(self, stages: list[PipelineStage]) -> GenerationPipeline:
        self.stages.extend(stages)
        return self

    def then(self, stage: PipelineStage) -> GenerationPipeline:
        return self.add_stage(stage)

    def run(self, request: AdaptationRequest) -> GenerationResult:
        context = GenerationContext(request=request)

        for stage in self.stages:
            context = stage.process(context)

        if context.selected is None:
            raise RuntimeError("Pipeline finished without selecting a level artifact.")

        selected_index = context.candidates.index(context.selected)
        validation = context.validation_reports.get(selected_index)
        difficulty = context.difficulty_reports.get(selected_index)

        return GenerationResult(
            level=context.selected,
            validation=validation,
            difficulty=difficulty,
            metadata=context.metadata,
        )