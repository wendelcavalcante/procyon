from __future__ import annotations
from dataclasses import dataclass
Board = tuple[int, ...]
@dataclass(slots=True)
class FifteenPuzzleConfig:
    size: int = 4
    blank_value: int = 0
    @property
    def tile_count(self) -> int: return self.size * self.size
    def solved_board(self) -> Board: return tuple(range(1, self.tile_count)) + (self.blank_value,)
def board_to_grid(board: Board, size: int) -> list[list[int]]:
    return [list(board[row*size:(row+1)*size]) for row in range(size)]
def count_inversions(board: Board, blank_value: int = 0) -> int:
    values = [value for value in board if value != blank_value]
    return sum(1 for i in range(len(values)) for j in range(i+1, len(values)) if values[i] > values[j])
def blank_row_from_bottom(board: Board, size: int, blank_value: int = 0) -> int:
    blank_index = board.index(blank_value)
    return size - (blank_index // size)
def is_fifteen_solvable(board: Board, size: int, blank_value: int = 0) -> bool:
    inversions = count_inversions(board, blank_value)
    if size % 2 == 1: return inversions % 2 == 0
    blank_row = blank_row_from_bottom(board, size, blank_value)
    return inversions % 2 == 1 if blank_row % 2 == 0 else inversions % 2 == 0
def manhattan_distance(board: Board, size: int, blank_value: int = 0) -> int:
    distance = 0
    for index, value in enumerate(board):
        if value == blank_value: continue
        current_row, current_col = divmod(index, size)
        goal_row, goal_col = divmod(value - 1, size)
        distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance
def valid_blank_neighbors(blank_index: int, size: int) -> list[int]:
    row, col = divmod(blank_index, size); neighbors=[]
    if row > 0: neighbors.append(blank_index-size)
    if row < size-1: neighbors.append(blank_index+size)
    if col > 0: neighbors.append(blank_index-1)
    if col < size-1: neighbors.append(blank_index+1)
    return neighbors
def swap_positions(board: Board, i: int, j: int) -> Board:
    values = list(board); values[i], values[j] = values[j], values[i]; return tuple(values)
