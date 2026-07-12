from __future__ import annotations

from pathlib import Path
from pprint import pprint

from procyon.orchestration import (
    AdaptiveGenerationRequestDTO,
    create_sqlite_orchestrator,
)


def print_response(response) -> None:
    print("\n=== Updated Player State ===")
    pprint(response.updated_player_state.model_dump())

    print("\n=== Adaptation Decision ===")
    pprint(response.adaptation_decision.model_dump())

    print("\n=== Selected Level ===")
    if response.selected_level is None:
        print("No level selected.")
    else:
        pprint(response.selected_level.model_dump())

    print("\n=== Generation Summary ===")
    pprint(response.generation_result.model_dump())


def main() -> None:
    Path("runtime").mkdir(parents=True, exist_ok=True)

    orchestrator = create_sqlite_orchestrator(
        "runtime/fifteen_case_study.sqlite3"
    )

    request = AdaptiveGenerationRequestDTO.model_validate(
        {
            "session_id": "fifteen_session_001",
            "player_id": "player_001",
            "runtime": {
                "source": "case_study",
                "game": "fifteen_puzzle",
            },
            "telemetry": {
                "level_id": "fifteen_level_001",
                "estimated_difficulty": 0.35,
                "target_difficulty": 0.40,
                "success": True,
                "solving_time": 95.0,
                "move_count": 80,
                "mistake_count": 4,
                "restart_count": 0,
                "hint_count": 0,
                "give_up": False,
                "metadata": {
                    "case_study": "fifteen_puzzle",
                    "description": "Previous Fifteen Puzzle attempt telemetry.",
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
                "domain": "fifteen",
                "strategy": "generate_and_test",
                "candidate_count": 100,
                "include_candidates": True,
                "parameters": {
                    "seed": 42,
                    "select": True,
                },
            },
        }
    )

    response = orchestrator.generate_next(request)
    print_response(response)


if __name__ == "__main__":
    main()