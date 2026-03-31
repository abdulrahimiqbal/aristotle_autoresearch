from __future__ import annotations

from fastapi import FastAPI

from research_orchestrator.dashboard_routes import build_dashboard_router


def create_dashboard_app(
    *,
    state_dir: str | None,
    db: str | None,
    project_id: str | None = None,
) -> FastAPI:
    app = FastAPI(title="Research Orchestrator Dashboard")
    config = {
        "state_dir": state_dir,
        "db": db,
        "project_id": project_id,
    }
    app.include_router(build_dashboard_router(config))
    return app
