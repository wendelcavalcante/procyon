from __future__ import annotations

from random import Random

Grid = list[list[int]]


def empty_grid() -> Grid:
    return [[0 for _ in range(9)] for _ in range(9)]


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def grid_to_flat(grid: Grid) -> list[int]:
    return [value for row in grid for value in row]


def flat_to_grid(values: list[int]) -> Grid:
    if len(values) != 81:
        raise ValueError(f"Expected 81 values, got {len(values)}.")

    return [values[i : i + 9] for i in range(0, 81, 9)]


def count_clues(grid: Grid) -> int:
    return sum(1 for row in grid for value in row if value != 0)


def is_complete(grid: Grid) -> bool:
    return all(value != 0 for row in grid for value in row)


def box_start(index: int) -> int:
    return (index // 3) * 3


def is_valid_placement(grid: Grid, row: int, col: int, value: int) -> bool:
    for c in range(9):
        if grid[row][c] == value:
            return False

    for r in range(9):
        if grid[r][col] == value:
            return False

    box_row = box_start(row)
    box_col = box_start(col)

    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if grid[r][c] == value:
                return False

    return True


def find_empty_cell(grid: Grid) -> tuple[int, int] | None:
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                return row, col

    return None


def find_empty_cell_mrv(grid: Grid) -> tuple[int, int] | None:
    best_cell: tuple[int, int] | None = None
    best_candidate_count: int | None = None

    for row in range(9):
        for col in range(9):
            if grid[row][col] != 0:
                continue

            candidates = get_candidates(grid, row, col)

            if best_candidate_count is None or len(candidates) < best_candidate_count:
                best_candidate_count = len(candidates)
                best_cell = (row, col)

            if best_candidate_count == 1:
                return best_cell

    return best_cell


def get_candidates(grid: Grid, row: int, col: int) -> list[int]:
    if grid[row][col] != 0:
        return []

    return [
        value
        for value in range(1, 10)
        if is_valid_placement(grid, row, col, value)
    ]


def fill_grid_backtracking(grid: Grid, rng: Random) -> bool:
    empty_cell = find_empty_cell(grid)

    if empty_cell is None:
        return True

    row, col = empty_cell
    values = list(range(1, 10))
    rng.shuffle(values)

    for value in values:
        if not is_valid_placement(grid, row, col, value):
            continue

        grid[row][col] = value

        if fill_grid_backtracking(grid, rng):
            return True

        grid[row][col] = 0

    return False


def solve_count(
    grid: Grid,
    limit: int = 2,
    use_mrv: bool = True,
) -> tuple[int, dict[str, int]]:
    """
    Count Sudoku solutions up to a given limit.

    Returns:
        solution_count, search_metadata
    """

    working = copy_grid(grid)

    metadata = {
        "recursive_calls": 0,
        "assignments": 0,
        "backtracks": 0,
        "dead_ends": 0,
        "max_depth": 0,
    }

    def backtrack(depth: int = 0) -> int:
        metadata["recursive_calls"] += 1
        metadata["max_depth"] = max(metadata["max_depth"], depth)

        empty_cell = find_empty_cell_mrv(working) if use_mrv else find_empty_cell(working)

        if empty_cell is None:
            return 1

        row, col = empty_cell
        candidates = get_candidates(working, row, col)

        if not candidates:
            metadata["dead_ends"] += 1
            return 0

        solutions = 0

        for value in candidates:
            working[row][col] = value
            metadata["assignments"] += 1

            solutions += backtrack(depth + 1)

            if solutions >= limit:
                working[row][col] = 0
                return solutions

            working[row][col] = 0
            metadata["backtracks"] += 1

        return solutions

    solution_count = backtrack()
    return solution_count, metadata


def symmetric_cell(row: int, col: int) -> tuple[int, int]:
    return 8 - row, 8 - col


def shuffled_cells(rng: Random) -> list[tuple[int, int]]:
    cells = [(row, col) for row in range(9) for col in range(9)]
    rng.shuffle(cells)
    return cells