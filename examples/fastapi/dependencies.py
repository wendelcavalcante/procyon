from __future__ import annotations

import os
from functools import lru_cache

from procyon.orchestration import (
    AdaptiveGenerationOrchestrator,
    create_sqlite_orchestrator,
)

from examples.fastapi.pipeline import ExampleGenerationPipelineBuilder


@lru_cache(maxsize=1)
def get_orchestrator() -> AdaptiveGenerationOrchestrator:
    print("teste")
    database_path = os.getenv("PROCYON_SQLITE_PATH", "runtime/procyon.sqlite3")
    return create_sqlite_orchestrator(database_path=database_path, pipeline_builder=ExampleGenerationPipelineBuilder())
