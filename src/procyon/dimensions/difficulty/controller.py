from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import AdaptationRequest
from procyon.dimensions.base import DimensionController as BaseDimensionController
from procyon.dimensions.difficulty.types import DifficultyTarget
class DifficultyController(BaseDimensionController, ABC):
    @abstractmethod
    def configure_target(self, request: AdaptationRequest) -> DifficultyTarget: ...
    def configure(self, request: AdaptationRequest) -> AdaptationRequest:
        target = self.configure_target(request)
        request.target_parameters["difficulty_target"] = target
        return request
