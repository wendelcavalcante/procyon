from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import AdaptationRequest
from procyon.generation.pipeline import GenerationPipeline
class PipelineBuilder(ABC):
    @abstractmethod
    def build(self, request: AdaptationRequest) -> GenerationPipeline: ...
