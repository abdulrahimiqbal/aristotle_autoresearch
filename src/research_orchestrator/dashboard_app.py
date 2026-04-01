from __future__ import annotations

from fastapi import FastAPI

from research_orchestrator.dashboard_routes import build_dashboard_router


def create_dashboard_app(
    *,
    db: str,
    project_id: str | None = None,
) -> FastAPI:
    app = FastAPI(title="Research Orchestrator Dashboard")
    config = {
        "db": db,
        "project_id": project_id,
    }
    app.include_router(build_dashboard_router(config))
    return app
