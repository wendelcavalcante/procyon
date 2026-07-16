from __future__ import annotations

from fastapi import FastAPI

from examples.fastapi.routes import router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Procyon Adaptive Generation API",
        version="0.1.0",
        description=(
            "HTTP adapter for Procyon adaptive game level generation. "
            "This API delegates adaptive generation requests to the "
            "orchestration layer."
        ),
    )

    app.include_router(router)

    return app


app = create_app()