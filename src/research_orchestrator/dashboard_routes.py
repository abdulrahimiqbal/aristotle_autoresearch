from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from jinja2 import DictLoader, Environment, select_autoescape

from research_orchestrator.dashboard_live_loader import LiveDashboardLoader
from research_orchestrator.db import Database


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
.error-banner { border:1px solid #ef4444; background:#fef2f2; padding:8px; margin:8px 0; font-size:12px; color:#991b1b; }
.block { border:1px solid #e5e7eb; padding:8px; margin-bottom:8px; }
.nav a,a { color:#1d4ed8; text-decoration:none; }
.nav a { margin-right:10px; font-size:12px; }
a:hover { text-decoration:underline; }
pre { white-space:pre-wrap; word-break:break-word; font-size:12px; }
.badge { display:inline-block; padding:2px 6px; border-radius:4px; font-size:11px; background:#e5e7eb; }
.actions { display:flex; gap:6px; flex-wrap:wrap; }
button { font-size:12px; padding:6px 10px; border:1px solid #cbd5f5; background:#eef2ff; cursor:pointer; }
.outlook-card { border-left:4px solid #8b5cf6; background:#f5f3ff; }
.route-badge { text-transform:uppercase; font-weight:bold; }
.route-breakthrough { color:#7c3aed; }
.route-active { color:#2563eb; }
.route-stalled { color:#d97706; }
/* Event type colors for timeline */
.evt-heartbeat { border-left:3px solid #9ca3af; }
.evt-decision { border-left:3px solid #3b82f6; }
.evt-submitted { border-left:3px solid #22c55e; }
.evt-result-ok { border-left:3px solid #22c55e; }
.evt-result-stalled { border-left:3px solid #f59e0b; }
.evt-result-fail { border-left:3px solid #ef4444; }
.evt-stalled { border-left:3px solid #f59e0b; }
.evt-incident { border-left:3px solid #ef4444; }
.evt-operator { border-left:3px solid #8b5cf6; }
.evt-policy { border-left:3px solid #6366f1; }
.evt-default { border-left:3px solid #d1d5db; }
"""


TEMPLATES = {
    "base.html": """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Aristotle Research Control Plane</title>
    <style>{{ inline_css }}</style>
  </head>
  <body>
    <main class="container">
      <header class="panel">
        <h1>Aristotle Research Control Plane</h1>
        <p class="muted">
          Source: <strong>{{ state.health.source_mode }}</strong> |
          Project: <strong>{{ state.project_id or "unknown" }}</strong> |
          Last event: <strong>{{ state.health.last_event_at or "n/a" }}</strong> |
          Last projection: <strong>{{ state.health.last_projection_at or "n/a" }}</strong>
        </p>
        <nav class="nav">
          <a href="/">Dashboard</a>
          <a href="/project">Experiments</a>
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
{% if state.health.get('projection_stale', false) %}
<div class="error-banner">&#9888; Projections may be stale &mdash; {{ state.health.get('projection_gap', 0) }} events behind the event log. Run <code>db-refresh-projections</code> to catch up.</div>
{% endif %}

<section class="panel outlook-card">
  <h2>Strategic Outlook</h2>
  {% if state.outlook %}
    <p><strong>Manager Summary:</strong> {{ state.outlook.summary }}</p>
    <div class="grid grid-3">
      {% for route, status in state.outlook.get('route_health', {}).items() %}
        <div class="block">
          <div class="muted">Route: {{ route }}</div>
          <div class="route-badge route-{{ status }}">{{ status }}</div>
        </div>
      {% endfor %}
    </div>
    <p class="muted"><strong>Critical Path:</strong> {{ state.outlook.critical_path }}</p>
  {% else %}
    <p class="muted">No strategic interpretation available for this project yet.</p>
  {% endif %}
</section>

<section class="panel">
  <h2>Live Manager Timeline</h2>
  <div class="actions" style="margin-bottom:8px;">
    <button data-command="pause-manager">Pause manager</button>
    <button data-command="resume-manager">Resume manager</button>
  </div>
  <div id="timeline">
    {% for event in state.timeline %}
      <div class="block {{ event._css_class }}">
        <div><strong>{{ event.event_type }}</strong> <span class="muted">{{ event.occurred_at }}</span></div>
        <div class="muted">Route: {{ event.route_id or "" }} Experiment: {{ event.experiment_id or "" }}</div>
        {% if event.payload %}<pre>{{ event.payload | tojson(indent=2) }}</pre>{% endif %}
      </div>
    {% endfor %}
  </div>
</section>

<section class="grid grid-3">
  <article class="panel">
    <h2>Operations</h2>
    <table>
      <tr><th>Manager status</th><td>{{ state.health.manager_status }}</td></tr>
      <tr><th>Active experiments</th><td>{{ state.operations.active_experiments }}</td></tr>
      <tr><th>Recent results</th><td>{{ state.operations.recent_results }}</td></tr>
      <tr><th>Open incidents</th><td>{{ state.operations.open_incidents }}</td></tr>
    </table>
  </article>
  <article class="panel">
    <h2>Decision Inspector</h2>
    {% if state.decision %}
      <div class="block">
        <div><strong>Selected route:</strong> {{ state.decision.payload.selected_route.route_key if state.decision.payload and state.decision.payload.selected_route else state.decision.payload.route_key }}</div>
        <div class="muted">Score: {{ state.decision.payload.total_score if state.decision.payload else "" }}</div>
        <details>
          <summary>Alternatives</summary>
          <pre>{{ state.decision.payload.alternatives | tojson(indent=2) if state.decision.payload else "" }}</pre>
        </details>
      </div>
    {% else %}
      <div class="muted">No route decision recorded yet.</div>
    {% endif %}
  </article>
  <article class="panel">
    <h2>Timeline Health</h2>
    <table>
      <tr><th>Event log entries</th><td>{{ state.health.get('event_count', 'n/a') }}</td></tr>
      <tr><th>Projection gap</th><td>{{ state.health.get('projection_gap', 0) }}</td></tr>
      <tr><th>Sequence gaps</th><td>{{ state.health.get('sequence_gaps', 0) }}</td></tr>
    </table>
  </article>
</section>

<section class="panel">
  <h2>Theorem Routes Board</h2>
  <table>
    <thead><tr><th>Route</th><th>Status</th><th>Strength</th><th>Signal Velocity</th><th>Reuse</th><th>Blockers</th><th>Next Move</th></tr></thead>
    <tbody>
      {% for route in state.routes %}
      <tr>
        <td>{{ route.route_key }}</td>
        <td><span class="badge">{{ route.route_status }}</span></td>
        <td>{{ route.current_strength }}</td>
        <td>{{ route.recent_signal_velocity }}</td>
        <td>{{ route.reuse_score }}</td>
        <td>{{ route.blocker_pressure }}</td>
        <td>{{ route.summary.top_move_family if route.summary else "" }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>

<section class="panel">
  <h2>Frontier Rankings</h2>
  <table>
    <thead><tr><th>Rank</th><th>Experiment</th><th>Route</th><th>Score</th><th>Move</th><th>Reason</th></tr></thead>
    <tbody>
      {% for row in state.frontier %}
      <tr>
        <td>{{ row.rank_position }}</td>
        <td>{{ row.experiment_id }}</td>
        <td>{{ row.route_id }}</td>
        <td>{{ row.score }}</td>
        <td>{{ row.candidate.move_family or row.candidate.move }}</td>
        <td>{{ row.score_breakdown.baseline_score if row.score_breakdown else "" }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>

<script>
const EVENT_CSS = {
  'manager.tick': 'evt-heartbeat',
  'route.selected': 'evt-decision',
  'candidate.selected': 'evt-submitted',
  'job.submitted': 'evt-submitted',
  'candidate.submitted': 'evt-submitted',
  'cycle.started': 'evt-heartbeat',
  'cycle.completed': 'evt-result-ok',
  'cycle.submit.started': 'evt-heartbeat',
  'result.ingested': 'evt-result-ok',
  'route.strengthened': 'evt-result-ok',
  'route.stalled': 'evt-stalled',
  'route.updated': 'evt-default',
  'frontier.generated': 'evt-default',
  'candidate.scored': 'evt-default',
  'candidate.rejected': 'evt-stalled',
  'policy.prompt.created': 'evt-policy',
  'policy.response.received': 'evt-policy',
  'policy.response.parsed': 'evt-policy',
  'policy.fallback.used': 'evt-stalled',
  'operator.command.received': 'evt-operator',
  'operator.command.applied': 'evt-operator',
};
function evtClass(eventType) {
  for (const [prefix, cls] of Object.entries(EVENT_CSS)) {
    if (eventType.startsWith(prefix)) return cls;
  }
  if (eventType.includes('incident')) return 'evt-incident';
  return 'evt-default';
}
const source = new EventSource("/api/stream");
source.onmessage = (event) => {
  const data = JSON.parse(event.data);
  const container = document.getElementById("timeline");
  if (!container) return;
  const block = document.createElement("div");
  block.className = "block " + evtClass(data.event_type);
  block.innerHTML = `<div><strong>${data.event_type}</strong> <span class="muted">${data.occurred_at}</span></div>`
    + `<div class="muted">Route: ${data.route_id || ""} Experiment: ${data.experiment_id || ""}</div>`
    + `<pre>${JSON.stringify(data.payload, null, 2)}</pre>`;
  container.prepend(block);
};

document.querySelectorAll("button[data-command]").forEach((button) => {
  button.addEventListener("click", async () => {
    const command = button.dataset.command;
    await fetch(`/api/commands/${command}`, { method: "POST", headers: {"Content-Type": "application/json"}, body: "{}" });
  });
});
</script>
{% endblock %}
""",
    "health.html": """
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h2>System Health</h2>
  <pre>{{ state.health | tojson(indent=2) }}</pre>
</section>
{% endblock %}
""",
}


def _event_css_class(event_type: str) -> str:
    """Map event_type to a CSS class for color-coded timeline rendering."""
    _MAP = {
        "manager.tick": "evt-heartbeat",
        "route.selected": "evt-decision",
        "candidate.selected": "evt-submitted",
        "job.submitted": "evt-submitted",
        "candidate.submitted": "evt-submitted",
        "cycle.started": "evt-heartbeat",
        "cycle.completed": "evt-result-ok",
        "cycle.submit.started": "evt-heartbeat",
        "result.ingested": "evt-result-ok",
        "route.strengthened": "evt-result-ok",
        "route.stalled": "evt-stalled",
        "route.updated": "evt-default",
        "frontier.generated": "evt-default",
        "candidate.scored": "evt-default",
        "candidate.rejected": "evt-stalled",
        "policy.prompt.created": "evt-policy",
        "policy.response.received": "evt-policy",
        "policy.response.parsed": "evt-policy",
        "policy.fallback.used": "evt-stalled",
        "operator.command.received": "evt-operator",
        "operator.command.applied": "evt-operator",
    }
    for prefix, cls in _MAP.items():
        if event_type.startswith(prefix):
            return cls
    if "incident" in event_type:
        return "evt-incident"
    return "evt-default"


def _render(name: str, **context: Any) -> HTMLResponse:
    env = Environment(
        loader=DictLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(name)
    html = template.render(**context, inline_css=INLINE_CSS)
    return HTMLResponse(html)


def _load_live_state(config: dict[str, Any]) -> dict[str, Any]:
    db_path = config.get("db")
    if not db_path:
        return {
            "project_id": "",
            "health": {"source_mode": "none", "manager_status": "unknown"},
            "timeline": [],
            "routes": [],
            "decision": {},
            "frontier": [],
            "operations": {"active_experiments": 0, "recent_results": 0, "open_incidents": 0},
            "outlook": {},
            "active_experiments": [],
            "recent_results": [],
            "incidents": [],
        }
    loader = LiveDashboardLoader(db_path=db_path, project_id=config.get("project_id"))
    state = loader.load()
    # Annotate timeline events with CSS class for color coding
    for event in state.get("timeline", []):
        event["_css_class"] = _event_css_class(event.get("event_type", ""))
    # Compute timeline health metrics
    health = state.get("health", {})
    try:
        db = Database(db_path)
        db.initialize()
        event_count_row = db.conn.execute("SELECT COUNT(*) FROM manager_events").fetchone()
        health["event_count"] = int(event_count_row[0]) if event_count_row else 0
        projection_count_row = db.conn.execute("SELECT COUNT(*) FROM live_manager_timeline").fetchone()
        projection_count = int(projection_count_row[0]) if projection_count_row else 0
        health["projection_gap"] = max(0, health["event_count"] - projection_count)
        health["projection_stale"] = health["projection_gap"] > 50
        gap_row = db.conn.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT sequence_no, LAG(sequence_no) OVER (ORDER BY sequence_no) AS prev
                FROM manager_events
            ) WHERE prev IS NOT NULL AND sequence_no != prev + 1
            """
        ).fetchone()
        health["sequence_gaps"] = int(gap_row[0]) if gap_row else 0
        db.close()
    except Exception:
        health.setdefault("event_count", 0)
        health.setdefault("projection_gap", 0)
        health.setdefault("projection_stale", False)
        health.setdefault("sequence_gaps", 0)
    state["health"] = health
    return state


def _db(config: dict[str, Any]) -> Database:
    db_path = config.get("db")
    if not db_path:
        raise HTTPException(status_code=500, detail="DB path not configured")
    db = Database(db_path)
    db.initialize()
    return db


def _resolve_project_id(db: Database, config: dict[str, Any]) -> str:
    if config.get("project_id"):
        return config["project_id"]
    row = db.conn.execute("SELECT project_id FROM projects ORDER BY created_at DESC LIMIT 1").fetchone()
    return row[0] if row else ""


def build_dashboard_router(config: dict[str, Any]) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    def overview() -> HTMLResponse:
        state = _load_live_state(config)
        return _render("overview.html", state=state)

    @router.get("/health", response_class=HTMLResponse)
    def health_page() -> HTMLResponse:
        state = _load_live_state(config)
        return _render("health.html", state=state)

    @router.get("/api/health")
    def api_health() -> JSONResponse:
        state = _load_live_state(config)
        return JSONResponse(state.get("health", {}))

    @router.get("/api/dashboard")
    def api_dashboard() -> JSONResponse:
        return JSONResponse(_load_live_state(config))

    @router.get("/api/routes")
    def api_routes() -> JSONResponse:
        db = _db(config)
        project_id = _resolve_project_id(db, config)
        if not project_id:
            db.close()
            raise HTTPException(status_code=400, detail="project_id not found")
        routes = db.list_theorem_routes(project_id)
        db.close()
        return JSONResponse(routes)

    @router.get("/api/routes/{route_id}")
    def api_route(route_id: str) -> JSONResponse:
        db = _db(config)
        route = db.get_theorem_route(route_id)
        if route is None:
            db.close()
            raise HTTPException(status_code=404, detail="route not found")
        evidence = db.list_route_evidence(route_id)
        db.close()
        return JSONResponse({"route": route, "evidence": evidence})

    @router.get("/api/manager-timeline")
    def api_timeline() -> JSONResponse:
        state = _load_live_state(config)
        return JSONResponse(state.get("timeline", []))

    @router.get("/api/frontier")
    def api_frontier() -> JSONResponse:
        state = _load_live_state(config)
        return JSONResponse(state.get("frontier", []))

    @router.get("/api/incidents")
    def api_incidents() -> JSONResponse:
        state = _load_live_state(config)
        return JSONResponse(state.get("incidents", []))

    @router.get("/api/stream")
    async def api_stream(request: Request) -> StreamingResponse:
        db = _db(config)
        project_id = _resolve_project_id(db, config)
        if not project_id:
            db.close()
            raise HTTPException(status_code=400, detail="project_id not found")
        last_event = db.last_manager_event(project_id)
        last_sequence = last_event["sequence_no"] if last_event else 0

        async def event_generator() -> AsyncGenerator[str, None]:
            nonlocal last_sequence
            while True:
                if await request.is_disconnected():
                    break
                events = db.list_manager_events(project_id, since_sequence=last_sequence, limit=50)
                for event in events:
                    last_sequence = event["sequence_no"]
                    payload = {
                        "event_id": event["event_id"],
                        "sequence_no": event["sequence_no"],
                        "occurred_at": event["occurred_at"],
                        "event_type": event["event_type"],
                        "route_id": event.get("route_id"),
                        "experiment_id": event.get("experiment_id"),
                        "payload": event.get("payload", {}),
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(1.2)

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @router.post("/api/commands/{command_type}")
    async def api_command(command_type: str, request: Request) -> JSONResponse:
        payload = await request.json() if request.headers.get("content-type") == "application/json" else {}
        db = _db(config)
        project_id = _resolve_project_id(db, config)
        if not project_id:
            db.close()
            raise HTTPException(status_code=400, detail="project_id not found")
        command_id = db.create_operator_command(
            project_id=project_id,
            command_type=command_type,
            target_type=payload.get("target_type", "manager"),
            target_id=payload.get("target_id"),
            route_id=payload.get("route_id"),
            payload=payload,
        )
        db.emit_manager_event(
            project_id=project_id,
            run_id=f"operator:{command_id}",
            event_type="operator.command.received",
            source_component="operator",
            experiment_id=payload.get("target_id"),
            route_id=payload.get("route_id"),
            payload={
                "command_id": command_id,
                "command_type": command_type,
                "payload": payload,
            },
        )
        db.close()
        return JSONResponse({"command_id": command_id, "status": "queued"})

    return router
