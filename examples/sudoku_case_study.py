from __future__ import annotations

from pathlib import Path
from pprint import pprint

from procyon.orchestration import (
    AdaptiveGenerationRequestDTO,
    create_sqlite_orchestrator,
)


def print_sudoku_grid(selected_level) -> None:
    if selected_level is None:
        print("No Sudoku selected.")
        return

    content = selected_level.content

    grid = content.get("grid")
    if grid is None:
        pprint(content)
        return

    for row in grid:
        print(" ".join(str(value) if value != 0 else "." for value in row))


def print_response(response) -> None:
    print("\n=== Updated Player State ===")
    pprint(response.updated_player_state.model_dump())

    print("\n=== Adaptation Decision ===")
    pprint(response.adaptation_decision.model_dump())

    print("\n=== Selected Sudoku Grid ===")
    print_sudoku_grid(response.selected_level)

    print("\n=== Selected Level Metadata ===")
    if response.selected_level is not None:
        pprint(response.selected_level.model_dump())

    print("\n=== Generation Summary ===")
    pprint(response.generation_result.model_dump())


def main() -> None:
    Path("runtime").mkdir(parents=True, exist_ok=True)

    orchestrator = create_sqlite_orchestrator(
        "runtime/sudoku_case_study.sqlite3"
    )

    request = AdaptiveGenerationRequestDTO.model_validate(
        {
            "session_id": "sudoku_session_001",
            "player_id": "player_001",
            "runtime": {
                "source": "case_study",
                "game": "sudoku",
            },
            "telemetry": {
                "level_id": "sudoku_level_001",
                "estimated_difficulty": 0.45,
                "target_difficulty": 0.45,
                "success": True,
                "solving_time": 210.0,
                "move_count": 55,
                "mistake_count": 3,
                "restart_count": 0,
                "hint_count": 1,
                "give_up": False,
                "metadata": {
                    "case_study": "sudoku",
                    "description": "Previous Sudoku attempt telemetry.",
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
                "domain": "sudoku",
                "strategy": "generate_and_test",
                "candidate_count": 50,
                "include_candidates": True,
                "parameters": {
                    "seed": 42,
                    "target_clues": 32,
                    "clue_removal_strategy": "symmetric",
                    "select": True,
                },
            },
        }
    )

    response = orchestrator.generate_next(request)
    print_response(response)


if __name__ == "__main__":
    main()