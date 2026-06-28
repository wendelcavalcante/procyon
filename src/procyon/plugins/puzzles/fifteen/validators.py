from __future__ import annotations
from procyon.core.artifacts import LevelArtifact, ValidationReport
from procyon.plugins.puzzles.fifteen.utils import Board, blank_row_from_bottom, count_inversions, is_fifteen_solvable
from procyon.validation.validators import Validator
class FifteenSolvabilityValidator(Validator):
    """Pluggable validator for Fifteen Puzzle solvability."""
    def validate(self, level: LevelArtifact) -> ValidationReport:
        size = int(level.content["size"]); blank_value = int(level.content["blank_value"]); board: Board = tuple(int(v) for v in level.content["board"])
        solvable = is_fifteen_solvable(board, size, blank_value)
        return ValidationReport(is_valid=solvable, score=1.0 if solvable else 0.0, messages=[] if solvable else ["Fifteen Puzzle board is not solvable."], metadata={"validator":self.__class__.__name__, "inversions":count_inversions(board, blank_value), "blank_row_from_bottom":blank_row_from_bottom(board, size, blank_value)})
