from __future__ import annotations
from enum import Enum
from typing import Any, NewType
LevelId = NewType("LevelId", str)
PlayerId = NewType("PlayerId", str)
SessionId = NewType("SessionId", str)
JsonDict = dict[str, Any]
class AdaptiveDimension(str, Enum):
    DIFFICULTY = "difficulty"
    GAMEPLAY = "gameplay"
    LAYOUT = "layout"
    ASSETS = "assets"
    SOUNDTRACK = "soundtrack"
    NARRATIVE = "narrative"
class GenerationStrategyType(str, Enum):
    GENERATE_AND_TEST = "generate_and_test"
    CONSTRUCTIVE = "constructive"
    REVERSE_SEARCH = "reverse_search"
    WFC = "wave_function_collapse"
    ML_MODEL = "ml_model"
    LLM_LOCAL = "llm_local"
    CUSTOM = "custom"
