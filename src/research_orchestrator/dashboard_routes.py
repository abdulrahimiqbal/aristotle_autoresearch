from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import DictLoader, Environment, select_autoescape

from research_orchestrator.dashboard_loader import DashboardLoader, dashboard_state_to_dict


INLINE_CSS = """
body { margin:0; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background:#f6f8fa; color:#111827; }
.container { max-width:1500px; margin:0 auto; padding:12px; }
.panel { border:1px solid #d1d5db; background:#fff; padding:12px; margin-bottom:12px; }
.grid { display:grid; gap:12px; }
.grid-2,.grid-3 { grid-template-columns:1fr; }
@media (min-width:980px) { .grid-2 { grid-template-columns:1fr 1fr; } .grid-3 { grid-template-columns:1fr 1fr 1fr; } }
h1,h2 { margin:0 0 8px 0; }
table { width:100%; border-collapse:collapse; }
th,td { border:1px solid #e5e7eb; padding:6px; text-align:left; vertical-align:top; font-size:12px; }
th { background:#f3f4f6; }
.muted { color:#4b5563; font-size:12px; }
.warning { border:1px solid #f59e0b; background:#fffbeb; padding:8px; margin:8px 0; font-size:12px; }
.block { border:1px solid #e5e7eb; padding:8px; margin-bottom:8px; }
.nav a,a { color:#1d4ed8; text-decoration:none; }
.nav a { margin-right:10px; font-size:12px; }
a:hover { text-decoration:underline; }
pre { white-space:pre-wrap; word-break:break-word; font-size:12px; }
"""


TEMPLATES = {
    "base.html": """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Aristotle Research Dashboard</title>
    <style>{{ inline_css }}</style>
  </head>
  <body>
    <main class="container">
      <header class="panel">
        <h1>Aristotle Research Dashboard</h1>
        <p class="muted">
          Source mode: <strong>{{ state.source_mode }}</strong> |
          Project: <strong>{{ state.project_id }}</strong> |
          Last update: <strong>{{ state.campaign_snapshot.last_db_update or state.campaign_snapshot.last_export_time or "unknown" }}</strong>
        </p>
        {% if state.health.warnings %}
          <div class="warning">
            {% for warning in state.health.warnings %}
              <div>{{ warning }}</div>
            {% endfor %}
          </div>
        {% endif %}
        <nav class="nav">
          <a href="/">Overview</a>
          <a href="/health">Health</a>
          <a href="/api/dashboard">/api/dashboard</a>
        </nav>
      </header>
      {% block content %}{% endblock %}
    </main>
  </body>
</html>
""",
    "overview.html": """
{% extends "base.html" %}
{% block content %}
<section class="grid grid-3">
  <article class="panel">
    <h2>Campaign snapshot</h2>
    <table>
      <tr><th>Campaign</th><td>{{ state.campaign_name }}</td></tr>
      <tr><th>Manager status</th><td>{{ state.campaign_snapshot.manager_status }}</td></tr>
      <tr><th>Total experiments</th><td>{{ state.campaign_snapshot.total_experiments }}</td></tr>
      <tr><th>Active / Failed / Stalled</th><td>{{ state.campaign_snapshot.active }} / {{ state.campaign_snapshot.failed }} / {{ state.campaign_snapshot.stalled }}</td></tr>
      <tr><th>Graph nodes / edges</th><td>{{ state.campaign_snapshot.graph_nodes }} / {{ state.campaign_snapshot.graph_edges }}</td></tr>
      <tr><th>Recurring clusters</th><td>{{ state.campaign_snapshot.recurring_cluster_count }}</td></tr>
      <tr><th>Open incidents</th><td>{{ state.campaign_snapshot.open_incidents }}</td></tr>
      <tr><th>DB health</th><td>{{ state.campaign_snapshot.db_health }} ({{ state.campaign_snapshot.integrity_status }})</td></tr>
      <tr><th>Last export</th><td>{{ state.campaign_snapshot.last_export_time or "n/a" }}</td></tr>
    </table>
  </article>
  <article class="panel">
    <h2>Knowledge pipeline</h2>
    <table>
      {% for item in state.knowledge_pipeline %}
      <tr><th>{{ item.label }}</th><td>{{ item.value }}</td></tr>
      {% endfor %}
    </table>
  </article>
  <article class="panel">
    <h2>Falsehood boundary map</h2>
    {% for item in state.falsehood_boundaries %}
      <div class="block">
        <div><a href="/problem/{{ item.conjecture_id }}">{{ item.conjecture_id }}</a></div>
        <div class="muted">{{ item.falsified_weakened_variants }}</div>
        <div class="muted">Witness regions: {{ item.witness_backed_false_regions }}</div>
      </div>
    {% endfor %}
  </article>
</section>
<section class="panel">
  <h2>Knowledge structure</h2>
  <table>
    <thead><tr><th>Name</th><th>Type</th><th>Reuse</th><th>Role</th><th>Status</th><th>Touched conjectures</th></tr></thead>
    <tbody>
      {% for row in state.knowledge_structures %}
      <tr><td>{{ row.name }}</td><td>{{ row.type }}</td><td>{{ row.reuse_count }}</td><td>{{ row.role }}</td><td>{{ row.status }}</td><td>{{ row.touches|join(", ") if row.touches else "n/a" }}</td></tr>
      {% endfor %}
    </tbody>
  </table>
</section>
<section class="panel">
  <h2>Problem progress</h2>
  <table>
    <thead><tr><th>Conjecture</th><th>Experiments</th><th>New signals</th><th>Strongest motif</th><th>Strongest obstruction</th><th>Proof traction</th><th>Current best route</th><th>Still missing</th></tr></thead>
    <tbody>
      {% for row in state.problem_progress %}
      <tr><td><a href="/problem/{{ row.conjecture_id }}">{{ row.conjecture_id }}</a></td><td>{{ row.experiments_count }}</td><td>{{ row.total_new_signals }}</td><td>{{ row.strongest_motif }}</td><td>{{ row.strongest_obstruction }}</td><td>{{ row.proof_traction_state }}</td><td>{{ row.current_best_route }}</td><td>{{ row.what_is_still_missing }}</td></tr>
      {% endfor %}
    </tbody>
  </table>
</section>
<section class="grid grid-2">
  <article class="panel">
    <h2>Recent results and what they mean</h2>
    <table>
      <thead><tr><th>Experiment</th><th>Conjecture</th><th>Move / family</th><th>Status</th><th>Proof outcome</th><th>New signals</th><th>Interpretation</th></tr></thead>
      <tbody>
        {% for row in state.recent_results[:20] %}
        <tr><td><a href="/experiment/{{ row.experiment_id }}">{{ row.experiment_id }}</a></td><td>{{ row.conjecture_id }}</td><td>{{ row.move }} / {{ row.move_family }}</td><td>{{ row.status }}</td><td>{{ row.proof_outcome }}</td><td>{{ row.new_signal_count }}</td><td>{{ row.interpretation }}</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </article>
  <article class="panel">
    <h2>Manager next actions</h2>
    <table>
      <thead><tr><th>Priority</th><th>Problem</th><th>Move / family</th><th>Rationale</th><th>Motif</th><th>Expected signal</th><th>Reuse</th><th>Blocker support</th><th>Witness support</th><th>Velocity</th></tr></thead>
      <tbody>
        {% for row in state.manager_actions %}
        <tr><td>{{ row.priority }}</td><td><a href="/problem/{{ row.problem }}">{{ row.problem }}</a></td><td>{{ row.move }}</td><td>{{ row.rationale }}</td><td>{{ row.motif_signature or row.motif_id or "n/a" }}</td><td>{{ row.expected_signal or "n/a" }}</td><td>{{ row.reuse_potential }}</td><td>{{ row.blocker_support }}</td><td>{{ row.witness_support }}</td><td>{{ row.recent_signal_velocity }}</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </article>
</section>
<section class="panel">
  <h2>Manager stream of thought</h2>
  {% if state.manager_reasoning %}
    {% for row in state.manager_reasoning %}
      <div class="block">
        <div><strong>{{ row.title }}</strong> <span class="muted">({{ row.kind }})</span></div>
        {% if row.created_at %}<div class="muted">{{ row.created_at }}</div>{% endif %}
        {% if row.summary %}<div>{{ row.summary }}</div>{% endif %}
        {% if row.reasoning %}<pre>{{ row.reasoning }}</pre>{% endif %}
        {% if row.prompt %}<details><summary>Prompt</summary><pre>{{ row.prompt }}</pre></details>{% endif %}
        {% if row.raw_response %}<details><summary>Stored raw output</summary><pre>{{ row.raw_response }}</pre></details>{% endif %}
      </div>
    {% endfor %}
  {% else %}
    <div class="muted">No stored manager reasoning artifacts yet.</div>
  {% endif %}
</section>
{% endblock %}
""",
    "problem.html": """
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h2>Problem dossier: {{ conjecture_id }}</h2>
  <table>
    <tr><th>Experiments</th><td>{{ problem.experiments_count }}</td></tr>
    <tr><th>Total new signals</th><td>{{ problem.total_new_signals }}</td></tr>
    <tr><th>Strongest motif</th><td>{{ problem.strongest_motif }}</td></tr>
    <tr><th>Strongest obstruction</th><td>{{ problem.strongest_obstruction }}</td></tr>
    <tr><th>Proof traction</th><td>{{ problem.proof_traction_state }}</td></tr>
    <tr><th>Current best route</th><td>{{ problem.current_best_route }}</td></tr>
    <tr><th>Still missing</th><td>{{ problem.what_is_still_missing }}</td></tr>
    <tr><th>Falsehood boundary status</th><td>{{ problem.falsehood_boundary_status }}</td></tr>
  </table>
</section>
<section class="panel">
  <h2>Falsehood boundary summary</h2>
  <table>
    <tr><th>Falsified weakened variants</th><td>{{ problem.falsehood_boundary.falsified_weakened_variants }}</td></tr>
    <tr><th>Witness-backed false regions</th><td>{{ problem.falsehood_boundary.witness_backed_false_regions }}</td></tr>
    <tr><th>Recurring missing assumptions</th><td>{{ problem.falsehood_boundary.recurring_missing_assumptions }}</td></tr>
    <tr><th>Likely salvageable repairs</th><td>{{ problem.falsehood_boundary.likely_salvageable_repairs }}</td></tr>
  </table>
</section>
<section class="grid grid-2">
  <article class="panel">
    <h2>Recurring structures touching this problem</h2>
    <table>
      <thead><tr><th>Name</th><th>Type</th><th>Reuse</th><th>Status</th></tr></thead>
      <tbody>
        {% for row in problem.structures %}
        <tr><td>{{ row.name }}</td><td>{{ row.type }}</td><td>{{ row.reuse_count }}</td><td>{{ row.status }}</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </article>
  <article class="panel">
    <h2>Recent results</h2>
    <table>
      <thead><tr><th>Experiment</th><th>Move</th><th>Status</th><th>Outcome</th><th>Signals</th><th>Interpretation</th></tr></thead>
      <tbody>
        {% for row in problem.recent_results %}
        <tr><td><a href="/experiment/{{ row.experiment_id }}">{{ row.experiment_id }}</a></td><td>{{ row.move_family }}</td><td>{{ row.status }}</td><td>{{ row.proof_outcome }}</td><td>{{ row.new_signal_count }}</td><td>{{ row.interpretation }}</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </article>
</section>
{% endblock %}
""",
    "experiment.html": """
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h2>Experiment: {{ experiment_id }}</h2>
  <table>
    <tr><th>Conjecture</th><td><a href="/problem/{{ experiment.conjecture_id }}">{{ experiment.conjecture_id }}</a></td></tr>
    <tr><th>Move</th><td>{{ experiment.move }}</td></tr>
    <tr><th>Move family</th><td>{{ experiment.move_family }}</td></tr>
    <tr><th>Status</th><td>{{ experiment.status }}</td></tr>
    <tr><th>Proof outcome</th><td>{{ experiment.proof_outcome }}</td></tr>
    <tr><th>Blocker</th><td>{{ experiment.blocker_type }}</td></tr>
    <tr><th>New signals</th><td>{{ experiment.new_signal_count }}</td></tr>
    <tr><th>Reused signals</th><td>{{ experiment.reused_signal_count }}</td></tr>
    <tr><th>Objective</th><td>{{ experiment.objective }}</td></tr>
    <tr><th>Expected signal</th><td>{{ experiment.expected_signal }}</td></tr>
    <tr><th>Boundary summary</th><td>{{ experiment.boundary_summary or "n/a" }}</td></tr>
    <tr><th>Motif</th><td>{{ experiment.motif_signature or experiment.motif_id or "n/a" }}</td></tr>
    <tr><th>Created</th><td>{{ experiment.created_at }}</td></tr>
    <tr><th>Completed</th><td>{{ experiment.completed_at or "n/a" }}</td></tr>
  </table>
</section>
{% endblock %}
""",
    "health.html": """
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h2>Health and source integrity</h2>
  <table>
    <tr><th>Source mode</th><td>{{ state.health.source_mode }}</td></tr>
    <tr><th>State directory</th><td>{{ state.health.state_dir or "n/a" }}</td></tr>
    <tr><th>DB path</th><td>{{ state.health.db_path or "n/a" }}</td></tr>
    <tr><th>SQLite readable</th><td>{{ state.health.db_readable }}</td></tr>
    <tr><th>SQLite corrupt</th><td>{{ state.health.db_corrupt }}</td></tr>
    <tr><th>SQLite integrity</th><td>{{ state.health.db_integrity }}</td></tr>
    <tr><th>Last bundle export</th><td>{{ state.health.last_bundle_export or "n/a" }}</td></tr>
    <tr><th>Last DB update</th><td>{{ state.health.last_db_update or "n/a" }}</td></tr>
    <tr><th>Stale-data warning</th><td>{{ state.health.stale_bundle_warning or "none" }}</td></tr>
    <tr><th>Missing bundle files</th><td>{{ state.health.missing_files|join(", ") if state.health.missing_files else "none" }}</td></tr>
  </table>
</section>
{% endblock %}
""",
}


def _env() -> Environment:
    return Environment(
        loader=DictLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"]),
    )


def _render(template_name: str, **context: Any) -> HTMLResponse:
    html = _env().get_template(template_name).render(inline_css=INLINE_CSS, **context)
    return HTMLResponse(html)


def _load_state(config: dict[str, Any]) -> dict[str, Any]:
    try:
        loader = DashboardLoader(
            state_dir=config.get("state_dir"),
            db_path=config.get("db"),
            project_id=config.get("project_id"),
        )
        state = loader.load()
        return dashboard_state_to_dict(state)
    except Exception as exc:
        return {
            "project_id": config.get("project_id") or "unknown-project",
            "campaign_name": "Dashboard source unavailable",
            "source_mode": "none",
            "campaign_snapshot": {
                "project_id": config.get("project_id") or "unknown-project",
                "campaign_name": "Dashboard source unavailable",
                "manager_status": "unavailable",
                "total_experiments": 0,
                "failed": 0,
                "stalled": 0,
                "active": 0,
                "graph_nodes": 0,
                "graph_edges": 0,
                "recurring_cluster_count": 0,
                "open_incidents": 0,
                "db_health": "unknown",
                "integrity_status": "unknown",
                "last_export_time": "",
                "last_db_update": "",
                "source_mode": "none",
            },
            "knowledge_structures": [],
            "problem_progress": [],
            "falsehood_boundaries": [],
            "knowledge_pipeline": [],
            "recent_results": [],
            "manager_actions": [],
            "manager_reasoning": [],
            "problems": {},
            "experiments": {},
            "provenance": {},
            "health": {
                "source_mode": "none",
                "db_path": config.get("db") or "",
                "state_dir": config.get("state_dir") or "",
                "db_readable": False,
                "db_corrupt": False,
                "db_integrity": "unknown",
                "last_bundle_export": "",
                "last_db_update": "",
                "missing_files": [],
                "stale_bundle_warning": "",
                "warnings": [f"Dashboard source initialization failed: {exc}"],
            },
        }


def build_dashboard_router(config: dict[str, Any]) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    def overview() -> HTMLResponse:
        state = _load_state(config)
        return _render("overview.html", state=state)

    @router.get("/problem/{conjecture_id}", response_class=HTMLResponse)
    def problem_page(conjecture_id: str) -> HTMLResponse:
        state = _load_state(config)
        problem = state["problems"].get(conjecture_id)
        if problem is None:
            raise HTTPException(status_code=404, detail=f"Unknown conjecture_id '{conjecture_id}'")
        return _render("problem.html", state=state, problem=problem, conjecture_id=conjecture_id)

    @router.get("/experiment/{experiment_id}", response_class=HTMLResponse)
    def experiment_page(experiment_id: str) -> HTMLResponse:
        state = _load_state(config)
        experiment = state["experiments"].get(experiment_id)
        if experiment is None:
            raise HTTPException(status_code=404, detail=f"Unknown experiment_id '{experiment_id}'")
        return _render("experiment.html", state=state, experiment=experiment, experiment_id=experiment_id)

    @router.get("/health", response_class=HTMLResponse)
    def health_page() -> HTMLResponse:
        state = _load_state(config)
        return _render("health.html", state=state)

    @router.get("/api/dashboard")
    def api_dashboard() -> JSONResponse:
        return JSONResponse(_load_state(config))

    @router.get("/api/problems")
    def api_problems() -> JSONResponse:
        state = _load_state(config)
        return JSONResponse(state["problem_progress"])

    @router.get("/api/problem/{conjecture_id}")
    def api_problem(conjecture_id: str) -> JSONResponse:
        state = _load_state(config)
        problem = state["problems"].get(conjecture_id)
        if problem is None:
            raise HTTPException(status_code=404, detail=f"Unknown conjecture_id '{conjecture_id}'")
        return JSONResponse(problem)

    @router.get("/api/recent-results")
    def api_recent_results() -> JSONResponse:
        state = _load_state(config)
        return JSONResponse(state["recent_results"])

    @router.get("/api/manager-actions")
    def api_manager_actions() -> JSONResponse:
        state = _load_state(config)
        return JSONResponse(state["manager_actions"])

    @router.get("/api/manager-reasoning")
    def api_manager_reasoning() -> JSONResponse:
        state = _load_state(config)
        return JSONResponse(state["manager_reasoning"])

    @router.get("/debug/state", response_class=HTMLResponse)
    def debug_state() -> HTMLResponse:
        state = _load_state(config)
        return HTMLResponse(f"<pre>{json.dumps(state, indent=2)}</pre>")

    return router
