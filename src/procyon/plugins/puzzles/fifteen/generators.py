from __future__ import annotations
from dataclasses import dataclass, field
from random import Random
from typing import Iterable
from procyon.core.artifacts import AdaptationRequest, LevelArtifact
from procyon.core.types import AdaptiveDimension
from procyon.generation.generators import PuzzleGenerator
from procyon.plugins.puzzles.fifteen.utils import Board, FifteenPuzzleConfig, board_to_grid, manhattan_distance, swap_positions, valid_blank_neighbors
@dataclass(slots=True)
class FisherYatesFifteenGenerator(PuzzleGenerator):
    """Generates candidate Fifteen Puzzle boards using Fisher-Yates shuffle.
    This generator does not check solvability; validation is a pluggable pipeline stage.
    """
    size: int = 4
    seed: int | None = None
    blank_value: int = 0
    candidate_count: int = 1
    _rng: Random = field(init=False, repr=False)
    def __post_init__(self) -> None: self._rng = Random(self.seed)
    def generate(self, request: AdaptationRequest) -> list[LevelArtifact]:
        candidates=[]
        for candidate_index in range(self.candidate_count):
            board = self._generate_board()
            candidates.append(LevelArtifact(content={"puzzle":"fifteen", "representation":"flat_board", "size":self.size, "blank_value":self.blank_value, "board":list(board), "grid":board_to_grid(board,self.size)}, dimensions={AdaptiveDimension.DIFFICULTY}, estimated_difficulty=None, metadata={"generator":self.__class__.__name__, "strategy":"fisher_yates", "candidate_index":candidate_index, "requires_validation":True, "manhattan_distance":manhattan_distance(board,self.size,self.blank_value)}))
        return candidates
    def _generate_board(self) -> Board:
        values = list(range(1, self.size*self.size)) + [self.blank_value]
        self._fisher_yates_shuffle(values)
        return tuple(values)
    def _fisher_yates_shuffle(self, values: list[int]) -> None:
        for i in range(len(values)-1, 0, -1):
            j = self._rng.randint(0, i); values[i], values[j] = values[j], values[i]
@dataclass(slots=True)
class ReverseShuffleFifteenGenerator(PuzzleGenerator):
    """Generates candidate Fifteen Puzzle boards by legal moves from the goal state."""
    size: int = 4
    iterations: int = 50
    seed: int | None = None
    blank_value: int = 0
    avoid_backtracking: bool = True
    start_state: Iterable[int] | None = None
    candidate_count: int = 1
    _rng: Random = field(init=False, repr=False)
    def __post_init__(self) -> None: self._rng = Random(self.seed)
    def generate(self, request: AdaptationRequest) -> list[LevelArtifact]:
        candidates=[]
        for candidate_index in range(self.candidate_count):
            board, move_history = self._generate_board()
            candidates.append(LevelArtifact(content={"puzzle":"fifteen", "representation":"flat_board", "size":self.size, "blank_value":self.blank_value, "board":list(board), "grid":board_to_grid(board,self.size)}, dimensions={AdaptiveDimension.DIFFICULTY}, estimated_difficulty=None, metadata={"generator":self.__class__.__name__, "strategy":"reverse_shuffle", "candidate_index":candidate_index, "iterations":self.iterations, "avoid_backtracking":self.avoid_backtracking, "construction_guarantee":"reachable_from_goal_state", "requires_validation":False, "move_history":move_history, "manhattan_distance":manhattan_distance(board,self.size,self.blank_value)}))
        return candidates
    def _generate_board(self) -> tuple[Board, list[int]]:
        if self.start_state is None:
            board = FifteenPuzzleConfig(size=self.size, blank_value=self.blank_value).solved_board()
        else:
            board = tuple(self.start_state); self._validate_start_state_shape(board)
        blank_index = board.index(self.blank_value); previous_blank_index=None; move_history=[]
        for _ in range(self.iterations):
            neighbors = valid_blank_neighbors(blank_index, self.size)
            if self.avoid_backtracking and previous_blank_index is not None:
                non_backtracking = [n for n in neighbors if n != previous_blank_index]
                if non_backtracking: neighbors = non_backtracking
            next_blank_index = self._rng.choice(neighbors)
            board = swap_positions(board, blank_index, next_blank_index)
            previous_blank_index = blank_index; blank_index = next_blank_index; move_history.append(next_blank_index)
        return board, move_history
    def _validate_start_state_shape(self, board: Board) -> None:
        expected_length = self.size*self.size
        if len(board) != expected_length: raise ValueError(f"Expected board with {expected_length} positions, got {len(board)}.")
        expected_values = set(range(1, expected_length)) | {self.blank_value}
        if set(board) != expected_values: raise ValueError("Invalid start_state values.")
