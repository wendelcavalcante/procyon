from __future__ import annotations
from procyon.core.artifacts import AdaptationRequest
from procyon.dimensions.base import DimensionController
class SoundtrackController(DimensionController):
    def configure(self, request: AdaptationRequest) -> AdaptationRequest:
        return request
