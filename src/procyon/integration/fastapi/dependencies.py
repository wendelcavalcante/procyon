from __future__ import annotations

from functools import lru_cache

from procyon.orchestration import (
    AdaptiveGenerationOrchestrator,
    create_default_orchestrator,
)


@lru_cache(maxsize=1)
def get_orchestrator() -> AdaptiveGenerationOrchestrator:
    """
    Provides the default orchestrator instance for the FastAPI adapter.

    The orchestrator itself should not store player/session state. Player state
    is expected to be received in the request and returned in the response.
    """
    return create_default_orchestrator()