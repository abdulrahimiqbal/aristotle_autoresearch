"""Multi-tenant dashboard for aggregating data from multiple problem databases.

This module provides a unified dashboard that connects to multiple SQLite
databases (one per Erdős problem) and aggregates them for a global view.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Import the Database class for direct connections
from research_orchestrator.db import Database


@dataclass
class ProblemConfig:
    """Configuration for a single problem database."""
    problem_number: str  # e.g., "273"
    problem_name: str  # e.g., "Erdős covering systems"
    database_path: str
    project_id: Optional[str] = None
    is_active: bool = True
    convergence_target: float = 0.95


class MultiTenantDashboard:
    """Aggregates data from multiple problem databases."""

    def __init__(self, config_json: str):
        """Initialize with database configuration JSON.

        Args:
            config_json: JSON string mapping problem numbers to database paths
                e.g., '{"273": "/data/erdos273.sqlite", "123": "/data/erdos123.sqlite"}'
        """
        self.problems: Dict[str, ProblemConfig] = {}
        self._db_cache: Dict[str, Database] = {}

        config = json.loads(config_json)
        for problem_num, db_path in config.items():
            self.problems[problem_num] = ProblemConfig(
                problem_number=problem_num,
                problem_name=self._get_problem_name(problem_num),
                database_path=db_path,
            )

    def _get_problem_name(self, problem_num: str) -> str:
        """Get display name for a problem number."""
        names = {
            "44": "Sidon Sets",
            "123": "Complete Sequences",
            "181": "Hypercube Ramsey",
            "273": "Covering Systems",
        }
        return names.get(problem_num, f"Erdős {problem_num}")

    def _get_db(self, problem_num: str) -> Optional[Database]:
        """Get or create database connection for a problem."""
        if problem_num not in self._db_cache:
            config = self.problems.get(problem_num)
            if not config:
                return None
            path = Path(config.database_path)
            if not path.exists():
                return None
            try:
                self._db_cache[problem_num] = Database(str(path))
            except Exception:
                return None
        return self._db_cache.get(problem_num)

    def list_problems(self) -> List[Dict[str, Any]]:
        """List all configured problems with their status."""
        results = []
        for problem_num, config in self.problems.items():
            db = self._get_db(problem_num)
            if not db:
                results.append({
                    "id": problem_num,
                    "name": config.problem_name,
                    "status": "inactive",
                    "convergence": 0.0,
                    "experiments": 0,
                    "active_experiments": 0,
                    "error": "Database not found",
                })
                continue

            try:
                # Get project info
                projects = db.list_projects()
                if projects:
                    project_id = projects[0]["project_id"]
                    config.project_id = project_id

                    # Get metrics
                    metrics = db.convergence_metrics(project_id)
                    conv_score = metrics.get("convergence_score", 0)
                    trend = metrics.get("trend", "unknown")

                    # Get experiment counts
                    all_exps = db.list_experiments(project_id)
                    active_exps = db.list_active_experiments(project_id)

                    results.append({
                        "id": problem_num,
                        "name": config.problem_name,
                        "project_id": project_id,
                        "status": "active" if active_exps else "idle",
                        "convergence": conv_score,
                        "trend": trend,
                        "experiments": len(all_exps),
                        "active_experiments": len(active_exps),
                        "convergence_target": config.convergence_target,
                    })
                else:
                    results.append({
                        "id": problem_num,
                        "name": config.problem_name,
                        "status": "no_project",
                        "convergence": 0.0,
                        "experiments": 0,
                        "active_experiments": 0,
                    })
            except Exception as e:
                results.append({
                    "id": problem_num,
                    "name": config.problem_name,
                    "status": "error",
                    "convergence": 0.0,
                    "experiments": 0,
                    "active_experiments": 0,
                    "error": str(e),
                })

        return sorted(results, key=lambda x: x["id"])

    def get_global_summary(self) -> Dict[str, Any]:
        """Get aggregated summary across all problems."""
        problems = self.list_problems()

        total_experiments = sum(p["experiments"] for p in problems)
        total_active = sum(p["active_experiments"] for p in problems)
        active_problems = sum(1 for p in problems if p["status"] == "active")

        # Calculate average convergence
        conv_values = [p["convergence"] for p in problems if p["convergence"] > 0]
        avg_convergence = sum(conv_values) / len(conv_values) if conv_values else 0

        return {
            "total_problems": len(problems),
            "active_problems": active_problems,
            "total_experiments": total_experiments,
            "total_active_experiments": total_active,
            "average_convergence": avg_convergence,
            "problems": problems,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_problem_dashboard(self, problem_num: str) -> Optional[Dict[str, Any]]:
        """Get detailed dashboard data for a specific problem."""
        db = self._get_db(problem_num)
        if not db:
            return None

        config = self.problems.get(problem_num)
        if not config or not config.project_id:
            # Try to find project
            projects = db.list_projects()
            if not projects:
                return None
            config.project_id = projects[0]["project_id"]

        project_id = config.project_id

        try:
            # Get convergence metrics
            metrics = db.convergence_metrics(project_id)

            # Get experiment summary
            experiments = db.list_experiments(project_id)
            active = db.list_active_experiments(project_id)

            # Get recent events
            events = db.list_manager_events(project_id, limit=20)

            # Get health status
            health = db.campaign_health(project_id)

            # Get conjectures
            conjectures = db.list_conjectures(project_id)

            return {
                "problem_number": problem_num,
                "problem_name": config.problem_name,
                "project_id": project_id,
                "metrics": metrics,
                "experiments": {
                    "total": len(experiments),
                    "active": len(active),
                    "by_status": self._count_by_status(experiments),
                },
                "conjectures": [
                    {
                        "id": c.conjecture_id,
                        "name": c.name or c.conjecture_id,
                        "domain": c.domain,
                        "status": c.status,
                    }
                    for c in conjectures
                ],
                "recent_events": events,
                "health": health,
            }
        except Exception as e:
            return {"error": str(e)}

    def _count_by_status(self, experiments: List[Dict]) -> Dict[str, int]:
        """Count experiments by status."""
        counts = {}
        for exp in experiments:
            status = exp.get("status", "unknown")
            counts[status] = counts.get(status, 0) + 1
        return counts

    def get_experiments(self, problem_num: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get experiments for a specific problem."""
        db = self._get_db(problem_num)
        if not db:
            return []

        config = self.problems.get(problem_num)
        if not config or not config.project_id:
            projects = db.list_projects()
            if not projects:
                return []
            config.project_id = projects[0]["project_id"]

        try:
            exps = db.list_experiments(config.project_id)
            # Sort by created_at descending
            exps.sort(key=lambda e: e.get("created_at", ""), reverse=True)
            return exps[:limit]
        except Exception:
            return []

    def get_health_status(self, problem_num: Optional[str] = None) -> Dict[str, Any]:
        """Get health status for a specific or all problems."""
        if problem_num:
            db = self._get_db(problem_num)
            if not db:
                return {"status": "unhealthy", "error": "Database not found"}

            config = self.problems.get(problem_num)
            if not config or not config.project_id:
                return {"status": "unhealthy", "error": "No project found"}

            try:
                # Check if manager is making progress
                events = db.list_manager_events(config.project_id, limit=5)
                if not events:
                    return {"status": "idle", "message": "No recent events"}

                latest = events[0]
                return {
                    "status": "healthy",
                    "last_event": latest.get("event_type"),
                    "last_event_at": latest.get("occurred_at"),
                    "active_experiments": len(db.list_active_experiments(config.project_id)),
                }
            except Exception as e:
                return {"status": "error", "error": str(e)}
        else:
            # Global health check
            results = {}
            for pnum in self.problems.keys():
                results[pnum] = self.get_health_status(pnum)
            return results


# Create FastAPI app for the multi-tenant dashboard
def create_multi_tenant_app() -> FastAPI:
    """Create FastAPI application for multi-tenant dashboard."""
    app = FastAPI(title="Aristotle Multi-Tenant Dashboard")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize dashboard from environment variable
    dashboard: Optional[MultiTenantDashboard] = None

    @app.on_event("startup")
    async def startup():
        nonlocal dashboard
        config = os.getenv("DATABASE_CONFIG", "{}")
        if config:
            dashboard = MultiTenantDashboard(config)

    @app.get("/")
    async def root():
        """Redirect to global dashboard."""
        return await global_dashboard()

    @app.get("/global")
    async def global_dashboard():
        """Global view showing all problems."""
        if not dashboard:
            return HTMLResponse("<h1>Dashboard not configured</h1><p>Set DATABASE_CONFIG env var</p>")

        summary = dashboard.get_global_summary()
        html = render_global_dashboard(summary)
        return HTMLResponse(content=html)

    @app.get("/problem/{problem_num}")
    async def problem_dashboard(problem_num: str):
        """Individual problem dashboard."""
        if not dashboard:
            return HTMLResponse("<h1>Dashboard not configured</h1>")

        data = dashboard.get_problem_dashboard(problem_num)
        if not data:
            raise HTTPException(status_code=404, detail=f"Problem {problem_num} not found")

        html = render_problem_dashboard(data, dashboard.list_problems())
        return HTMLResponse(content=html)

    @app.get("/api/problems")
    async def api_list_problems():
        """List all problems."""
        if not dashboard:
            return JSONResponse({"error": "Not configured"}, status_code=503)
        return JSONResponse(dashboard.list_problems())

    @app.get("/api/global/summary")
    async def api_global_summary():
        """Get global summary."""
        if not dashboard:
            return JSONResponse({"error": "Not configured"}, status_code=503)
        return JSONResponse(dashboard.get_global_summary())

    @app.get("/api/problems/{problem_num}/dashboard")
    async def api_problem_dashboard(problem_num: str):
        """Get problem dashboard data."""
        if not dashboard:
            return JSONResponse({"error": "Not configured"}, status_code=503)
        data = dashboard.get_problem_dashboard(problem_num)
        if not data:
            raise HTTPException(status_code=404, detail="Problem not found")
        return JSONResponse(data)

    @app.get("/api/problems/{problem_num}/experiments")
    async def api_problem_experiments(problem_num: str, limit: int = 100):
        """Get experiments for a problem."""
        if not dashboard:
            return JSONResponse({"error": "Not configured"}, status_code=503)
        exps = dashboard.get_experiments(problem_num, limit)
        return JSONResponse({
            "problem": problem_num,
            "count": len(exps),
            "experiments": exps,
        })

    @app.get("/api/health")
    async def api_health():
        """Health check."""
        if not dashboard:
            return JSONResponse({"status": "unconfigured"})
        return JSONResponse(dashboard.get_health_status())

    @app.get("/api/problems/{problem_num}/health")
    async def api_problem_health(problem_num: str):
        """Health check for specific problem."""
        if not dashboard:
            return JSONResponse({"error": "Not configured"}, status_code=503)
        return JSONResponse(dashboard.get_health_status(problem_num))

    return app


# HTML Rendering functions
def render_global_dashboard(summary: Dict[str, Any]) -> str:
    """Render the global dashboard HTML."""
    problems = summary.get("problems", [])

    # Build problem cards
    cards_html = ""
    for p in problems:
        status_color = {
            "active": "#22c55e",
            "idle": "#f59e0b",
            "error": "#ef4444",
        }.get(p["status"], "#6b7280")

        conv_pct = p.get("convergence", 0) * 100

        cards_html += f"""
        <div class="problem-card" style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; background: #fff;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 18px;"><a href="/problem/{p['id']}" style="color: #111827; text-decoration: none;">{p['name']}</a></h3>
                <span style="background: {status_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; text-transform: uppercase;">{p['status']}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 600; color: #111827;">{p['experiments']}</div>
                    <div style="font-size: 12px; color: #6b7280;">Experiments</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 600; color: #111827;">{p.get('active_experiments', 0)}</div>
                    <div style="font-size: 12px; color: #6b7280;">Active</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 600; color: #111827;">{conv_pct:.1f}%</div>
                    <div style="font-size: 12px; color: #6b7280;">Converged</div>
                </div>
            </div>
            <div style="font-size: 12px; color: #6b7280;">
                Trend: <strong>{p.get('trend', 'unknown')}</strong>
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Aristotle Research - Global Dashboard</title>
    <style>
        body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; color: #111827; line-height: 1.5; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
        header {{ background: #fff; border-bottom: 1px solid #e5e7eb; padding: 24px; margin-bottom: 24px; }}
        h1 {{ margin: 0 0 8px 0; font-size: 28px; }}
        .subtitle {{ color: #6b7280; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .metric-card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; }}
        .metric-value {{ font-size: 36px; font-weight: 700; color: #111827; }}
        .metric-label {{ font-size: 14px; color: #6b7280; margin-top: 4px; }}
        .problems-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .nav {{ background: #fff; padding: 12px 24px; border-bottom: 1px solid #e5e7eb; }}
        .nav a {{ color: #4b5563; text-decoration: none; margin-right: 20px; font-weight: 500; }}
        .nav a:hover {{ color: #111827; }}
        .refresh {{ float: right; color: #6b7280; font-size: 14px; }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="/global" style="color: #111827;">Global</a>
        <a href="/api/global/summary">API</a>
        <span class="refresh">Last updated: {summary.get('timestamp', 'now')}</span>
    </nav>
    <header>
        <div class="container">
            <h1>Aristotle Research Orchestrator</h1>
            <div class="subtitle">Global view across {summary['total_problems']} Erdős problems</div>
        </div>
    </header>
    <div class="container">
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{summary['total_problems']}</div>
                <div class="metric-label">Total Problems</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary['active_problems']}</div>
                <div class="metric-label">Active</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary['total_experiments']}</div>
                <div class="metric-label">Total Experiments</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary['total_active_experiments']}</div>
                <div class="metric-label">Running Now</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary['average_convergence']*100:.1f}%</div>
                <div class="metric-label">Avg Convergence</div>
            </div>
        </div>
        <h2 style="margin-bottom: 16px;">Problems</h2>
        <div class="problems-grid">
            {cards_html}
        </div>
    </div>
</body>
</html>"""


def render_problem_dashboard(data: Dict[str, Any], all_problems: List[Dict]) -> str:
    """Render individual problem dashboard."""
    problem_num = data["problem_number"]
    problem_name = data["problem_name"]
    metrics = data.get("metrics", {})
    experiments = data.get("experiments", {})
    conjectures = data.get("conjectures", [])
    recent_events = data.get("recent_events", [])

    conv_score = metrics.get("convergence_score", 0) * 100
    trend = metrics.get("trend", "unknown")

    # Build problem tabs
    tabs_html = ""
    for p in all_problems:
        active = "background: #111827; color: #fff;" if p["id"] == problem_num else ""
        tabs_html += f"""
        <a href="/problem/{p['id']}" style="display: inline-block; padding: 8px 16px; text-decoration: none; color: {'#fff' if p['id'] == problem_num else '#4b5563'}; {active} border-radius: 4px; margin-right: 8px;">
            {p['name']}
            <span style="font-size: 11px; opacity: 0.8;">({p.get('experiments', 0)})</span>
        </a>
        """

    # Build conjecture list
    conj_html = ""
    for c in conjectures:
        conj_html += f"""
        <div style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
            <strong>{c['name']}</strong>
            <span style="color: #6b7280; font-size: 12px; margin-left: 8px;">{c['domain']}</span>
            <span style="float: right; font-size: 12px; color: {'#22c55e' if c['status'] == 'active' else '#6b7280'};">{c['status']}</span>
        </div>
        """

    # Build recent events
    events_html = ""
    for e in recent_events[:10]:
        events_html += f"""
        <div style="padding: 8px; border-bottom: 1px solid #e5e7eb; font-size: 13px;">
            <span style="color: #6b7280;">{e.get('occurred_at', 'unknown')}</span>
            <span style="margin-left: 12px;">{e.get('event_type', 'unknown')}</span>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{problem_name} - Aristotle Dashboard</title>
    <style>
        body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; color: #111827; line-height: 1.5; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
        header {{ background: #fff; border-bottom: 1px solid #e5e7eb; padding: 24px; margin-bottom: 24px; }}
        h1 {{ margin: 0 0 8px 0; font-size: 24px; }}
        .nav {{ background: #fff; padding: 12px 24px; border-bottom: 1px solid #e5e7eb; }}
        .nav a {{ color: #4b5563; text-decoration: none; margin-right: 20px; font-weight: 500; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; }}
        .metric {{ font-size: 32px; font-weight: 700; color: #111827; }}
        .metric-label {{ font-size: 14px; color: #6b7280; margin-top: 4px; }}
        .progress-bar {{ width: 100%; height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; margin-top: 12px; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #22c55e, #16a34a); border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #e5e7eb; }}
        th {{ font-weight: 600; color: #6b7280; font-size: 12px; text-transform: uppercase; }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="/global">← Global</a>
        <span style="float: right; color: #6b7280; font-size: 14px;">Project: {data.get('project_id', 'unknown')[:30]}...</span>
    </nav>
    <nav class="nav" style="background: #f9fafb; padding: 12px 24px;">
        {tabs_html}
    </nav>
    <header>
        <div class="container">
            <h1>{problem_name} (Erdős {problem_num})</h1>
            <div style="color: #6b7280;">Convergence: {conv_score:.1f}% | Trend: {trend}</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {conv_score}%"></div>
            </div>
        </div>
    </header>
    <div class="container">
        <div class="grid">
            <div class="card">
                <div class="metric">{experiments.get('total', 0)}</div>
                <div class="metric-label">Total Experiments</div>
            </div>
            <div class="card">
                <div class="metric">{experiments.get('active', 0)}</div>
                <div class="metric-label">Active</div>
            </div>
            <div class="card">
                <div class="metric">{len(conjectures)}</div>
                <div class="metric-label">Conjectures</div>
            </div>
            <div class="card">
                <div class="metric">{conv_score:.1f}%</div>
                <div class="metric-label">Converged</div>
            </div>
        </div>
        <div class="grid" style="margin-top: 20px;">
            <div class="card">
                <h3 style="margin-top: 0;">Conjectures</h3>
                {conj_html if conj_html else '<p style="color: #6b7280;">No conjectures</p>'}
            </div>
            <div class="card">
                <h3 style="margin-top: 0;">Recent Events</h3>
                {events_html if events_html else '<p style="color: #6b7280;">No recent events</p>'}
            </div>
        </div>
        <div style="margin-top: 20px; text-align: center;">
            <a href="/api/problems/{problem_num}/experiments" style="color: #4b5563;">View API →</a>
        </div>
    </div>
</body>
</html>"""


# Create the application instance
app = create_multi_tenant_app()

# For Railway/uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
