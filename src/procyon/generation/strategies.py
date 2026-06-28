from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import AdaptationRequest
from procyon.generation.pipeline import GenerationPipeline
class GenerationStrategy(ABC):
    @abstractmethod
    def build_pipeline(self, request: AdaptationRequest) -> GenerationPipeline: ...
class GenerateAndTestStrategy(GenerationStrategy):
    def build_pipeline(self, request: AdaptationRequest) -> GenerationPipeline: raise NotImplementedError
class ConstructiveStrategy(GenerationStrategy):
    def build_pipeline(self, request: AdaptationRequest) -> GenerationPipeline: raise NotImplementedError
class ReverseSearchStrategy(GenerationStrategy):
    def build_pipeline(self, request: AdaptationRequest) -> GenerationPipeline: raise NotImplementedError
