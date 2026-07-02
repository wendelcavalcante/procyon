from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from procyon.core.artifacts import AdaptationRequest, LevelArtifact
from procyon.core.types import AdaptiveDimension
from procyon.generation.generators import PuzzleGenerator
from procyon.plugins.puzzles.sokoban.utils import (
    Position,
    SokobanLevel,
    add_positions,
    adjacent_positions,
    all_floor_positions,
    box_goal_distance_sum,
    create_outer_walls,
    generate_internal_walls,
    has_enough_floor,
    inside_floor_positions,
    is_floor_connected,
    is_free_floor,
    reachable_positions,
)


@dataclass(slots=True)
class ReverseSokobanGenerator(PuzzleGenerator):
    """
    Generates simple Sokoban candidates using reverse moves from a solved state.

    Initial version:
    - rectangular map;
    - external walls;
    - optional random internal walls;
    - one box;
    - one goal;
    - reverse generation by pulling the box away from the goal.
    """

    width: int = 7
    height: int = 7
    reverse_steps: int = 20
    candidate_count: int = 1
    seed: int | None = None
    avoid_backtracking: bool = True
    reposition_player_before_pull: bool = True
    max_attempts_per_candidate: int = 100

    wall_density: float = 0.10
    ensure_connected_floor: bool = True
    min_floor_count: int | None = None

    _rng: Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.width < 5 or self.height < 5:
            raise ValueError("Sokoban maps should be at least 5x5.")

        if self.reverse_steps < 0:
            raise ValueError("reverse_steps must be non-negative.")

        if self.candidate_count < 1:
            raise ValueError("candidate_count must be at least 1.")

        if not 0.0 <= self.wall_density <= 1.0:
            raise ValueError("wall_density must be between 0.0 and 1.0.")

        self._rng = Random(self.seed)

    def generate(self, request: AdaptationRequest) -> list[LevelArtifact]:
        candidates: list[LevelArtifact] = []

        for candidate_index in range(self.candidate_count):
            level, reverse_history = self._generate_candidate()

            candidates.append(
                LevelArtifact(
                    content={
                        "puzzle": "sokoban",
                        "representation": "ascii_grid",
                        "width": level.width,
                        "height": level.height,
                        "ascii": level.to_ascii(),
                        "grid": level.to_grid(),
                        "player": list(level.player),
                        "boxes": [list(pos) for pos in sorted(level.boxes)],
                        "goals": [list(pos) for pos in sorted(level.goals)],
                        "walls": [list(pos) for pos in sorted(level.walls)],
                    },
                    dimensions={AdaptiveDimension.DIFFICULTY},
                    estimated_difficulty=None,
                    metadata={
                        "generator": self.__class__.__name__,
                        "strategy": "reverse_sokoban",
                        "candidate_index": candidate_index,
                        "reverse_steps": self.reverse_steps,
                        "actual_reverse_steps": len(reverse_history),
                        "avoid_backtracking": self.avoid_backtracking,
                        "reposition_player_before_pull": self.reposition_player_before_pull,
                        "wall_density": self.wall_density,
                        "internal_wall_count": self._count_internal_walls(level.walls),
                        "floor_count": len(
                            all_floor_positions(level.width, level.height, level.walls)
                        ),
                        "box_count": len(level.boxes),
                        "goal_count": len(level.goals),
                        "box_goal_distance_sum": box_goal_distance_sum(
                            level.boxes,
                            level.goals,
                        ),
                        "construction_guarantee": (
                            "reachable_from_goal_state_by_reverse_pulls"
                        ),
                        "requires_validation": False,
                        "reverse_history": reverse_history,
                    },
                )
            )

        return candidates

    def _generate_candidate(self) -> tuple[SokobanLevel, list[dict[str, object]]]:
        last_error: Exception | None = None

        for _ in range(self.max_attempts_per_candidate):
            try:
                return self._try_generate_candidate()
            except RuntimeError as error:
                last_error = error

        raise RuntimeError(
            "Could not generate Sokoban candidate after "
            f"{self.max_attempts_per_candidate} attempts."
        ) from last_error

    def _try_generate_candidate(self) -> tuple[SokobanLevel, list[dict[str, object]]]:
        walls = self._generate_walls()

        floors = list(all_floor_positions(self.width, self.height, walls))

        if not floors:
            raise RuntimeError("Generated map has no floor positions.")

        goal = self._choose_goal_position(floors, walls)
        box = goal

        player_candidates = [
            pos
            for pos in adjacent_positions(box)
            if is_free_floor(pos, self.width, self.height, walls, boxes={box})
        ]

        if not player_candidates:
            raise RuntimeError("Could not place player near solved box.")

        player = self._rng.choice(player_candidates)

        level = SokobanLevel(
            width=self.width,
            height=self.height,
            walls=walls,
            goals={goal},
            boxes={box},
            player=player,
        )

        reverse_history: list[dict[str, object]] = []
        previous_box_position: Position | None = None

        for step in range(self.reverse_steps):
            move = self._choose_reverse_pull(level, previous_box_position)

            if move is None:
                break

            old_box = next(iter(level.boxes))
            pull_from = move["pull_from"]
            new_box = move["new_box"]
            new_player = move["new_player"]

            level.boxes = {new_box}
            level.player = new_player

            reverse_history.append(
                {
                    "step": step,
                    "old_box": list(old_box),
                    "pull_from": list(pull_from),
                    "new_box": list(new_box),
                    "new_player": list(new_player),
                }
            )

            previous_box_position = old_box

        if len(reverse_history) == 0 and self.reverse_steps > 0:
            raise RuntimeError("No reverse pulls could be applied.")

        return level, reverse_history

    def _generate_walls(self) -> set[Position]:
        outer_walls = create_outer_walls(self.width, self.height)

        min_floor_count = self.min_floor_count
        if min_floor_count is None:
            # Enough floor for player, box, goal and some movement.
            min_floor_count = max(8, int((self.width - 2) * (self.height - 2) * 0.50))

        for _ in range(self.max_attempts_per_candidate):
            internal_walls = generate_internal_walls(
                width=self.width,
                height=self.height,
                rng=self._rng,
                wall_density=self.wall_density,
            )

            walls = outer_walls | internal_walls

            if not has_enough_floor(self.width, self.height, walls, min_floor_count):
                continue

            if self.ensure_connected_floor and not is_floor_connected(
                self.width,
                self.height,
                walls,
            ):
                continue

            return walls

        raise RuntimeError("Could not generate a valid internal wall layout.")

    def _choose_goal_position(
        self,
        floors: list[Position],
        walls: set[Position],
    ) -> Position:
        """
        Prefer less constrained goal positions.

        For a first version, avoid positions with fewer than two free neighbors.
        """

        safer_floors = []

        for pos in floors:
            free_neighbors = [
                neighbor
                for neighbor in adjacent_positions(pos)
                if is_free_floor(neighbor, self.width, self.height, walls, boxes=set())
            ]

            if len(free_neighbors) >= 2:
                safer_floors.append(pos)

        if safer_floors:
            return self._rng.choice(safer_floors)

        return self._rng.choice(floors)

    def _choose_reverse_pull(
        self,
        level: SokobanLevel,
        previous_box_position: Position | None,
    ) -> dict[str, Position] | None:
        box = next(iter(level.boxes))

        reachable = reachable_positions(
            start=level.player,
            width=level.width,
            height=level.height,
            walls=level.walls,
            boxes=level.boxes,
        )

        possible_moves: list[dict[str, Position]] = []

        for direction in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            # Reverse pull model:
            #
            # Before pull:
            #   player stands at pull_from, adjacent to box.
            #
            # After pull:
            #   box moves into pull_from.
            #   player moves one cell further in the same direction.
            #
            # This corresponds to reversing a forward push.
            pull_from = add_positions(box, direction)
            new_player = add_positions(pull_from, direction)
            new_box = pull_from

            if self.reposition_player_before_pull and pull_from not in reachable:
                continue

            if not self.reposition_player_before_pull and level.player != pull_from:
                continue

            if not is_free_floor(
                new_player,
                level.width,
                level.height,
                level.walls,
                level.boxes,
            ):
                continue

            if not is_free_floor(
                new_box,
                level.width,
                level.height,
                level.walls,
                boxes=set(),
            ):
                continue

            if self.avoid_backtracking and previous_box_position is not None:
                if new_box == previous_box_position:
                    continue

            possible_moves.append(
                {
                    "pull_from": pull_from,
                    "new_box": new_box,
                    "new_player": new_player,
                }
            )

        if not possible_moves:
            return None

        return self._rng.choice(possible_moves)

    def _count_internal_walls(self, walls: set[Position]) -> int:
        return sum(
            1
            for row, col in walls
            if 0 < row < self.height - 1 and 0 < col < self.width - 1
        )