from __future__ import annotations

from pathlib import Path
from pprint import pprint

from procyon.orchestration import (
    AdaptiveGenerationRequestDTO,
    create_sqlite_orchestrator,
)


def print_sokoban_level(selected_level) -> None:
    if selected_level is None:
        print("No Sokoban level selected.")
        return

    content = selected_level.content

    ascii_level = content.get("ascii")
    if ascii_level is not None:
        print(ascii_level)
        return

    grid = content.get("grid")
    if grid is not None:
        for row in grid:
            if isinstance(row, str):
                print(row)
            else:
                print("".join(str(cell) for cell in row))
        return

    pprint(content)


def print_response(response) -> None:
    print("\n=== Updated Player State ===")
    pprint(response.updated_player_state.model_dump())

    print("\n=== Adaptation Decision ===")
    pprint(response.adaptation_decision.model_dump())

    print("\n=== Selected Sokoban Level ===")
    print_sokoban_level(response.selected_level)

    print("\n=== Selected Level Metadata ===")
    if response.selected_level is not None:
        pprint(response.selected_level.model_dump())

    print("\n=== Generation Summary ===")
    pprint(response.generation_result.model_dump())


def main() -> None:
    Path("runtime").mkdir(parents=True, exist_ok=True)

    orchestrator = create_sqlite_orchestrator(
        "runtime/sokoban_case_study.sqlite3"
    )

    request = AdaptiveGenerationRequestDTO.model_validate(
        {
            "session_id": "sokoban_session_001",
            "player_id": "player_001",
            "runtime": {
                "source": "case_study",
                "game": "sokoban",
            },
            "telemetry": {
                "level_id": "sokoban_level_001",
                "estimated_difficulty": 0.40,
                "target_difficulty": 0.40,
                "success": True,
                "solving_time": 85.0,
                "move_count": 48,
                "mistake_count": 2,
                "restart_count": 0,
                "hint_count": 0,
                "give_up": False,
                "metadata": {
                    "case_study": "sokoban",
                    "description": "Previous Sokoban attempt telemetry.",
                },
            },
            "design_goals": {
                "target_experience": "balanced_challenge",
                "allowed_dimensions": ["difficulty"],
                "constraints": {
                    "min_difficulty": 0.10,
                    "max_difficulty": 0.90,
                    "max_step_change": 0.10,
                    "difficulty_tolerance": 0.10,
                },
            },
            "generation": {
                "domain": "sokoban",
                "strategy": "reverse_search",
                "candidate_count": 30,
                "include_candidates": True,
                "parameters": {
                    "seed": 42,
                    "width": 9,
                    "height": 9,
                    "reverse_steps": 30,
                    "wall_density": 0.12,
                    "avoid_backtracking": True,
                    "reposition_player_before_pull": True,
                    "ensure_connected_floor": True,
                    "select": True,
                },
            },
        }
    )

    response = orchestrator.generate_next(request)
    print_response(response)


if __name__ == "__main__":
    main()