from procyon.orchestration import (
    AdaptiveGenerationRequestDTO,
    create_sqlite_orchestrator,
)


def test_stateful_orchestrator_reuses_persisted_player_state(tmp_path) -> None:
    database_path = tmp_path / "procyon_test.sqlite3"
    orchestrator = create_sqlite_orchestrator(database_path)

    base_request = {
        "session_id": "session_001",
        "player_id": "player_001",
        "runtime": {
            "source": "test",
            "game": "sokoban_prototype",
        },
        "telemetry": {
            "level_id": "level_001",
            "estimated_difficulty": 0.40,
            "success": True,
            "solving_time": 60.0,
            "move_count": 40,
            "mistake_count": 1,
            "restart_count": 0,
            "hint_count": 0,
            "give_up": False,
        },
        "design_goals": {
            "target_experience": "balanced_challenge",
            "allowed_dimensions": ["difficulty"],
            "constraints": {
                "min_difficulty": 0.10,
                "max_difficulty": 0.90,
                "max_step_change": 0.10,
            },
        },
        "generation": {
            "domain": "sokoban",
            "strategy": "reverse_search",
            "candidate_count": 3,
            "include_candidates": False,
            "parameters": {
                "width": 7,
                "height": 7,
                "reverse_steps": 10,
                "wall_density": 0.05,
                "seed": 42,
                "select": True,
            },
        },
    }

    first_response = orchestrator.generate_next(
        AdaptiveGenerationRequestDTO.model_validate(base_request)
    )

    second_request = dict(base_request)
    second_request["telemetry"] = {
        **base_request["telemetry"],
        "level_id": "level_002",
        "estimated_difficulty": first_response.selected_level.estimated_difficulty,
        "success": True,
    }

    second_response = orchestrator.generate_next(
        AdaptiveGenerationRequestDTO.model_validate(second_request)
    )

    assert first_response.updated_player_state.observations_count == 1
    assert second_response.updated_player_state.observations_count == 2