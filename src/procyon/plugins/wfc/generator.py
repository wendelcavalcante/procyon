from __future__ import annotations
from procyon.core.artifacts import AdaptationRequest, LevelArtifact
from procyon.generation.generators import ContentGenerator
class WFCGenerator(ContentGenerator):
    def generate(self, request: AdaptationRequest) -> list[LevelArtifact]: raise NotImplementedError
