from __future__ import annotations
from abc import ABC, abstractmethod
from procyon.core.artifacts import AdaptationRequest
class DimensionController(ABC):
    @abstractmethod
    def configure(self, request: AdaptationRequest) -> AdaptationRequest: ...
