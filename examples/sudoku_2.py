from procyon.orchestration import (
    AdaptiveGenerationRequestDTO,
    create_default_orchestrator,
)

orchestrator = create_default_orchestrator()

request = AdaptiveGenerationRequestDTO.model_validate(
    {
        "session_id": "session_001",
        "player_id": "player_001",
        "runtime": {
            "source": "simulation",
            "game": "sudoku_prototype",
        },
        "last_player_state": {
            "skill": 0.52,
            "engagement": 0.60,
            "frustration": 0.15,
            "confidence": 0.40,
            "observations_count": 8,
        },
        "telemetry": {
            "level_id": "level_008",
            "estimated_difficulty": 0.48,
            "success": True,
            "solving_time": 72.5,
            "move_count": 48,
            "mistake_count": 4,
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
                "difficulty_tolerance": 0.08,
            },
        },
        "generation": {
            "domain": "sudoku",
            "strategy": "generate_and_test",
            "candidate_count": 200,
            "include_candidates": True,
            "parameters": {
                "target_clues": 32,
                "clue_removal_strategy": "symmetric",
                "seed": 42,
                "select": True,
            },
        },
    }
)

response = orchestrator.generate_next(request)

print(response.updated_player_state)
print(response.adaptation_decision)
print(response.selected_level)
print(response.generation_result)