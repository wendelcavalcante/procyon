from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from procyon.orchestration import (
    AdaptiveGenerationOrchestrator,
    AdaptiveGenerationRequestDTO,
    AdaptiveGenerationResponseDTO,
)

from examples.fastapi.dependencies import get_orchestrator

router = APIRouter(prefix="/v1", tags=["adaptive-generation"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "procyon",
    }


@router.post(
    "/generate-next",
    response_model=AdaptiveGenerationResponseDTO,
)
def generate_next(
    request: AdaptiveGenerationRequestDTO,
    orchestrator: AdaptiveGenerationOrchestrator = Depends(get_orchestrator),
) -> AdaptiveGenerationResponseDTO:
    """
    Generate the next adaptive level from runtime telemetry and player state.

    This endpoint is intentionally thin. It delegates the complete use case to
    the orchestration layer.
    """

    try:
        print("teste")
        return orchestrator.generate_next(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error