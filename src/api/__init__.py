"""FastAPI роутеры."""

from fastapi import FastAPI

from .health import router as health_router
from .checks import router as checks_router


def setup_routes(app: FastAPI) -> None:
    app.include_router(health_router, tags=["health"])
    app.include_router(checks_router, tags=["checks"])

