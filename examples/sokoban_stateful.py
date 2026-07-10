from procyon.orchestration import (
    AdaptiveGenerationRequestDTO,
    create_sqlite_orchestrator,
)

orchestrator = create_sqlite_orchestrator("runtime/procyon.sqlite3")

request = AdaptiveGenerationRequestDTO.model_validate(
    {
        "session_id": "session_001",
        "player_id": "player_001::sokoban",
        "runtime": {
            "source": "simulation",
            "game": "sokoban_prototype",
        },
        "telemetry": {
            "level_id": "level_001",
            "estimated_difficulty": 0.40,
            "success": True,
            "solving_time": 65.0,
            "move_count": 42,
            "mistake_count": 2,
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
            "candidate_count": 20,
            "include_candidates": False,
            "parameters": {
                "width": 9,
                "height": 9,
                "reverse_steps": 30,
                "wall_density": 0.12,
                "seed": 42,
                "select": True,
            },
        },
    }
)

response = orchestrator.generate_next(request)

print(response.updated_player_state)
print(response.adaptation_decision)
print(response.selected_level.content["ascii"])