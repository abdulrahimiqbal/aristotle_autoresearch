"""Health check server for Railway deployment.

Provides a FastAPI endpoint for health monitoring that runs
in a separate thread alongside the main manager loop.
"""

from __future__ import annotations

import threading
import time
from typing import Optional

try:
    from fastapi import FastAPI
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


class HealthServer:
    """Lightweight health check server for container orchestration."""

    def __init__(
        self,
        port: int = 8080,
        project_id: Optional[str] = None,
        db=None,
        llm_client=None,
    ):
        self.port = port
        self.project_id = project_id
        self.db = db
        self.llm_client = llm_client
        self._last_tick_timestamp: Optional[float] = None
        self._start_time = time.time()
        self._is_healthy = True
        self._server_thread: Optional[threading.Thread] = None
        self._app: Optional[FastAPI] = None

    def set_tick_timestamp(self):
        """Update the last tick timestamp (call from manager)."""
        self._last_tick_timestamp = time.time()

    def set_healthy(self, healthy: bool):
        """Set the overall health status."""
        self._is_healthy = healthy

    def _build_app(self) -> FastAPI:
        """Build the FastAPI application."""
        if not HAS_FASTAPI:
            raise RuntimeError("FastAPI not installed")

        app = FastAPI(title="Research Orchestrator Health")

        @app.get("/health")
        def health_check():
            """Return health status for Railway/容器 orchestration."""
            now = time.time()

            # Calculate tick staleness
            tick_stale = False
            seconds_since_tick: Optional[float] = None
            if self._last_tick_timestamp:
                seconds_since_tick = now - self._last_tick_timestamp
                # Consider stale if no tick in 5 minutes
                tick_stale = seconds_since_tick > 300

            # Check LLM availability
            llm_available = False
            if self.llm_client:
                try:
                    llm_available = getattr(self.llm_client, 'is_available', lambda: True)()
                except Exception:
                    pass

            # Check queue depth
            queue_depth = 0
            active_experiments = 0
            if self.db and self.project_id:
                try:
                    active_experiments = len(self.db.list_active_experiments(self.project_id))
                    # Try to get queue depth if method exists
                    if hasattr(self.db, 'get_queue_depth'):
                        queue_depth = self.db.get_queue_depth()
                except Exception:
                    pass

            # Determine overall status
            status = "healthy"
            if not self._is_healthy:
                status = "unhealthy"
            elif tick_stale:
                status = "degraded"

            return {
                "status": status,
                "project_id": self.project_id,
                "uptime_seconds": int(now - self._start_time),
                "active_experiments": active_experiments,
                "queue_depth": queue_depth,
                "last_tick_seconds_ago": int(seconds_since_tick) if seconds_since_tick else None,
                "llm_available": llm_available,
                "tick_stale": tick_stale,
            }

        @app.get("/")
        def root():
            """Root endpoint with basic info."""
            return {
                "service": "research-orchestrator-manager",
                "project_id": self.project_id,
                "status": "running",
            }

        return app

    def start(self) -> None:
        """Start the health server in a background thread."""
        if not HAS_FASTAPI:
            print("[HEALTH] FastAPI not available, skipping health server")
            return

        if self._server_thread and self._server_thread.is_alive():
            print("[HEALTH] Server already running")
            return

        self._app = self._build_app()

        def run_server():
            uvicorn.run(
                self._app,
                host="0.0.0.0",
                port=self.port,
                log_level="warning",
                access_log=False,
            )

        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()
        print(f"[HEALTH] Server started on port {self.port}")

    def stop(self) -> None:
        """Signal the health server to stop (thread will terminate with main)."""
        # Since it's a daemon thread, it will stop when main exits
        self._is_healthy = False


def start_health_server(
    port: int = 8080,
    project_id: Optional[str] = None,
    db=None,
    llm_client=None,
) -> HealthServer:
    """Convenience function to create and start a health server.

    Usage:
        health = start_health_server(port=8080, project_id="proj-123", db=db)
        # In manager loop:
        health.set_tick_timestamp()
    """
    server = HealthServer(port=port, project_id=project_id, db=db, llm_client=llm_client)
    server.start()
    return server
