from __future__ import annotations
from procyon.core.artifacts import AdaptationRequest, LevelArtifact, ValidationReport
from procyon.generation.generators import PuzzleGenerator
from procyon.validation.validators import PuzzleSolver, Validator
class SudokuGenerator(PuzzleGenerator):
    def generate(self, request: AdaptationRequest) -> list[LevelArtifact]: raise NotImplementedError
class SudokuSolver(PuzzleSolver):
    def solve(self, level: LevelArtifact) -> ValidationReport: raise NotImplementedError
class SudokuValidator(Validator):
    def validate(self, level: LevelArtifact) -> ValidationReport: raise NotImplementedError
