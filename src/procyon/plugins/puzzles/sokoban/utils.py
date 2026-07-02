from __future__ import annotations

from dataclasses import dataclass

Position = tuple[int, int]


@dataclass(slots=True)
class SokobanLevel:
    width: int
    height: int
    walls: set[Position]
    goals: set[Position]
    boxes: set[Position]
    player: Position

    def to_ascii(self) -> str:
        lines: list[str] = []

        for row in range(self.height):
            chars: list[str] = []

            for col in range(self.width):
                pos = (row, col)

                if pos in self.walls:
                    chars.append("#")
                elif pos == self.player and pos in self.goals:
                    chars.append("+")
                elif pos == self.player:
                    chars.append("@")
                elif pos in self.boxes and pos in self.goals:
                    chars.append("*")
                elif pos in self.boxes:
                    chars.append("$")
                elif pos in self.goals:
                    chars.append(".")
                else:
                    chars.append(" ")

            lines.append("".join(chars))

        return "\n".join(lines)

    def to_grid(self) -> list[list[str]]:
        return [list(line) for line in self.to_ascii().splitlines()]


def create_outer_walls(width: int, height: int) -> set[Position]:
    walls: set[Position] = set()

    for row in range(height):
        for col in range(width):
            if row == 0 or row == height - 1 or col == 0 or col == width - 1:
                walls.add((row, col))

    return walls


def inside_floor_positions(width: int, height: int) -> list[Position]:
    return [
        (row, col)
        for row in range(1, height - 1)
        for col in range(1, width - 1)
    ]


def add_positions(a: Position, b: Position) -> Position:
    return a[0] + b[0], a[1] + b[1]


def subtract_positions(a: Position, b: Position) -> Position:
    return a[0] - b[0], a[1] - b[1]


def manhattan(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def directions() -> list[Position]:
    return [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]


def adjacent_positions(pos: Position) -> list[Position]:
    return [add_positions(pos, direction) for direction in directions()]


def is_floor(pos: Position, width: int, height: int, walls: set[Position]) -> bool:
    row, col = pos

    if row < 0 or row >= height:
        return False

    if col < 0 or col >= width:
        return False

    return pos not in walls


def is_free_floor(
    pos: Position,
    width: int,
    height: int,
    walls: set[Position],
    boxes: set[Position],
) -> bool:
    return is_floor(pos, width, height, walls) and pos not in boxes


def reachable_positions(
    start: Position,
    width: int,
    height: int,
    walls: set[Position],
    boxes: set[Position],
) -> set[Position]:
    visited: set[Position] = set()
    frontier: list[Position] = [start]

    while frontier:
        current = frontier.pop()

        if current in visited:
            continue

        visited.add(current)

        for neighbor in adjacent_positions(current):
            if neighbor in visited:
                continue

            if is_free_floor(neighbor, width, height, walls, boxes):
                frontier.append(neighbor)

    return visited


def box_goal_distance_sum(boxes: set[Position], goals: set[Position]) -> int:
    if not boxes or not goals:
        return 0

    total = 0

    for box in boxes:
        total += min(manhattan(box, goal) for goal in goals)

    return total

def generate_internal_walls(
    width: int,
    height: int,
    rng: Random,
    wall_density: float,
    protected_positions: set[Position] | None = None,
) -> set[Position]:
    """
    Generate random internal walls.

    protected_positions are never turned into walls.
    """

    if not 0.0 <= wall_density <= 1.0:
        raise ValueError("wall_density must be between 0.0 and 1.0.")

    protected_positions = protected_positions or set()

    internal_positions = [
        (row, col)
        for row in range(1, height - 1)
        for col in range(1, width - 1)
        if (row, col) not in protected_positions
    ]

    rng.shuffle(internal_positions)

    wall_count = int(len(internal_positions) * wall_density)
    return set(internal_positions[:wall_count])


def connected_floor_component(
    start: Position,
    width: int,
    height: int,
    walls: set[Position],
) -> set[Position]:
    """
    Return all floor positions reachable from start, ignoring boxes.
    """

    if not is_floor(start, width, height, walls):
        return set()

    visited: set[Position] = set()
    frontier: list[Position] = [start]

    while frontier:
        current = frontier.pop()

        if current in visited:
            continue

        visited.add(current)

        for neighbor in adjacent_positions(current):
            if neighbor in visited:
                continue

            if is_floor(neighbor, width, height, walls):
                frontier.append(neighbor)

    return visited


def all_floor_positions(
    width: int,
    height: int,
    walls: set[Position],
) -> set[Position]:
    return {
        (row, col)
        for row in range(height)
        for col in range(width)
        if is_floor((row, col), width, height, walls)
    }


def is_floor_connected(
    width: int,
    height: int,
    walls: set[Position],
) -> bool:
    floors = all_floor_positions(width, height, walls)

    if not floors:
        return False

    start = next(iter(floors))
    component = connected_floor_component(start, width, height, walls)

    return component == floors


def has_enough_floor(
    width: int,
    height: int,
    walls: set[Position],
    min_floor_count: int,
) -> bool:
    return len(all_floor_positions(width, height, walls)) >= min_floor_count