import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import AsyncGenerator

app = FastAPI(title="Aristotle Research Control Plane")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get state directory from environment or use default
STATE_DIR = Path(os.getenv("STATE_DIR", "outputs/dashboard_bundle_live"))
PROJECT_ID = os.getenv("PROJECT_ID", "erdos-combo-001")

# EST is UTC-5 (or UTC-4 during DST - we'll use standard offset)
EST_OFFSET = timedelta(hours=-5)

def to_est(timestamp_str: str) -> str:
    """Convert ISO timestamp to EST format."""
    if not timestamp_str:
        return ""
    try:
        # Parse ISO timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        # Convert to EST
        est_dt = dt + EST_OFFSET
        return est_dt.strftime("%Y-%m-%d %I:%M:%S %p EST")
    except:
        return timestamp_str

def load_json(filename: str) -> list:
    """Load JSON lines or JSON array from file."""
    path = STATE_DIR / filename
    if not path.exists():
        return []
    content = path.read_text()
    if not content.strip():
        return []
    # Try parsing as JSON array first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    # Parse as JSON lines
    results = []
    for line in content.strip().split('\n'):
        if line.strip():
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return results

def load_state() -> dict:
    """Load full dashboard state from JSON files."""
    events = load_json("manager_events.json")
    routes = load_json("route_strength.json")
    health_list = load_json("system_health.json")
    health = health_list[0] if health_list else {
        "project_id": PROJECT_ID,
        "manager_status": "unknown",
        "source_mode": "json_bundle"
    }

    # Get all decisions with scoring details
    decisions = [e for e in events if e.get("event_type") == "route.selected"]
    latest_decision = decisions[-1] if decisions else {}

    # Build timeline with CSS classes and EST times
    timeline = []
    for event in reversed(events[-200:]):
        event_type = event.get("event_type", "")
        css_class = _event_css_class(event_type)
        est_time = to_est(event.get("occurred_at", ""))
        timeline.append({
            **event,
            "_css_class": css_class,
            "payload": event.get("payload", {}),
            "est_time": est_time
        })

    # Count operations by status
    active_experiments = len([e for e in events if e.get("event_type") == "job.submitted"])
    completed = len([e for e in events if e.get("event_type") == "result.ingested"])
    open_incidents = len([e for e in events if "incident" in e.get("event_type", "")])
    
    # Get frontier/candidate scoring events
    scored_candidates = [e for e in events if e.get("event_type") == "candidate.scored"]
    rejected = [e for e in events if e.get("event_type") == "candidate.rejected"]

    # Build frontier from scored candidates
    frontier = []
    for i, e in enumerate(scored_candidates[-20:]):
        payload = e.get("payload", {})
        components = payload.get("components", {})
        frontier.append({
            "rank": i + 1,
            "experiment_id": payload.get("experiment_id", "unknown"),
            "route_id": payload.get("route_id", ""),
            "total_score": payload.get("total_score", 0),
            "components": components,
            "move_family": payload.get("move_family", "unknown"),
            "reasoning": _build_reasoning(components)
        })

    return {
        "project_id": PROJECT_ID,
        "health": {
            **health,
            "source_mode": "json_bundle",
            "event_count": len(events),
            "latest_event_est": timeline[0].get("est_time") if timeline else "",
        },
        "timeline": timeline,
        "routes": routes,
        "decisions": decisions[-10:],  # Last 10 decisions
        "latest_decision": latest_decision,
        "frontier": frontier,
        "operations": {
            "active_experiments": active_experiments,
            "recent_results": completed,
            "open_incidents": open_incidents,
            "scored_candidates": len(scored_candidates),
            "rejected_candidates": len(rejected),
        },
        "outlook": {},
    }

def _build_reasoning(components: dict) -> str:
    """Build human-readable reasoning from score components."""
    reasons = []
    if components.get("reuse_score", 0) > 2:
        reasons.append("high reuse potential")
    if components.get("transfer_score", 0) > 1.5:
        reasons.append("transferable across domains")
    if components.get("novelty_score", 0) > 2:
        reasons.append("novel approach")
    if components.get("signal_support", 0) > 0:
        reasons.append("signal supported")
    if components.get("blocker_pressure", 0) > 1:
        reasons.append("blocker pressure")
    if not reasons:
        reasons.append("standard candidate")
    return ", ".join(reasons)

def _event_css_class(event_type: str) -> str:
    """Map event_type to CSS class for color coding."""
    mapping = {
        "manager.tick": "evt-heartbeat",
        "manager.tick.started": "evt-heartbeat",
        "route.selected": "evt-decision",
        "candidate.selected": "evt-submitted",
        "candidate.submitted": "evt-submitted",
        "candidate.scored": "evt-scored",
        "job.submitted": "evt-submitted",
        "cycle.started": "evt-heartbeat",
        "cycle.completed": "evt-result-ok",
        "result.ingested": "evt-result-ok",
        "route.strengthened": "evt-result-ok",
        "route.stalled": "evt-stalled",
        "candidate.rejected": "evt-stalled",
        "policy.fallback.used": "evt-stalled",
        "policy.prompt.created": "evt-policy",
    }
    for prefix, cls in mapping.items():
        if event_type.startswith(prefix):
            return cls
    if "incident" in event_type:
        return "evt-incident"
    return "evt-default"

INLINE_CSS = """
body { margin:0; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background:#0f172a; color:#e2e8f0; }
.container { max-width:1600px; margin:0 auto; padding:12px; }
.panel { border:1px solid #334155; background:#1e293b; padding:12px; margin-bottom:12px; border-radius:8px; }
.grid { display:grid; gap:12px; }
.grid-2,.grid-3,.grid-4 { grid-template-columns:1fr; }
@media (min-width:980px) { .grid-2 { grid-template-columns:1fr 1fr; } .grid-3 { grid-template-columns:1fr 1fr 1fr; } .grid-4 { grid-template-columns:1fr 1fr 1fr 1fr; } }
h1,h2,h3 { margin:0 0 8px 0; color:#f8fafc; }
h3 { font-size:14px; color:#94a3b8; }
table { width:100%; border-collapse:collapse; font-size:11px; }
th,td { border:1px solid #334155; padding:6px; text-align:left; vertical-align:top; }
th { background:#334155; color:#f8fafc; font-weight:600; }
.muted { color:#94a3b8; font-size:12px; }
.warning { border:1px solid #f59e0b; background:#451a03; padding:8px; margin:8px 0; font-size:12px; color:#fbbf24; }
.error-banner { border:1px solid #ef4444; background:#450a0a; padding:8px; margin:8px 0; font-size:12px; color:#fca5a5; }
.block { border:1px solid #334155; padding:10px; margin-bottom:8px; background:#0f172a; border-radius:4px; }
.nav a,a { color:#60a5fa; text-decoration:none; }
.nav a { margin-right:10px; font-size:12px; }
a:hover { text-decoration:underline; }
pre { white-space:pre-wrap; word-break:break-word; font-size:11px; background:#020617; padding:10px; border-radius:4px; border:1px solid #1e293b; }
.badge { display:inline-block; padding:2px 6px; border-radius:4px; font-size:10px; background:#334155; color:#e2e8f0; }
.badge-selected { background:#166534; color:#86efac; }
.badge-rejected { background:#7f1d1d; color:#fca5a5; }
.badge-scored { background:#1e3a8a; color:#93c5fd; }
.actions { display:flex; gap:6px; flex-wrap:wrap; }
button { font-size:12px; padding:6px 10px; border:1px solid #475569; background:#334155; color:#e2e8f0; cursor:pointer; border-radius:4px; }
button:hover { background:#475569; }
.outlook-card { border-left:4px solid #8b5cf6; background:#1e1b4b; }
.route-badge { text-transform:uppercase; font-weight:bold; font-size:11px; }
.route-breakthrough { color:#a78bfa; }
.route-active { color:#60a5fa; }
.route-stalled { color:#fbbf24; }
/* Event type colors for timeline - dark theme */
.evt-heartbeat { border-left:3px solid #6b7280; }
.evt-decision { border-left:3px solid #3b82f6; background:#172554; }
.evt-submitted { border-left:3px solid #22c55e; }
.evt-scored { border-left:3px solid #6366f1; }
.evt-result-ok { border-left:3px solid #22c55e; }
.evt-result-stalled { border-left:3px solid #f59e0b; }
.evt-stalled { border-left:3px solid #f59e0b; background:#451a03; }
.evt-incident { border-left:3px solid #ef4444; }
.evt-operator { border-left:3px solid #8b5cf6; }
.evt-policy { border-left:3px solid #06b6d4; }
.evt-default { border-left:3px solid #4b5563; }
.live-indicator { display:inline-block; width:8px; height:8px; background:#22c55e; border-radius:50%; animation:pulse 2s infinite; margin-right:6px; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }
.timestamp { font-family: monospace; color:#64748b; font-size:11px; }
.timestamp-est { font-family: monospace; color:#fbbf24; font-size:12px; font-weight:600; }
.metric-card { text-align:center; padding:16px; }
.metric-value { font-size:24px; font-weight:bold; color:#60a5fa; }
.metric-label { font-size:11px; color:#94a3b8; text-transform:uppercase; }
.score-breakdown { display:grid; grid-template-columns: repeat(4, 1fr); gap:8px; font-size:10px; margin-top:6px; }
.score-item { background:#0f172a; padding:4px 6px; border-radius:3px; text-align:center; }
.score-label { color:#64748b; font-size:9px; }
.score-value { color:#e2e8f0; font-weight:600; }
.decision-card { background:#172554; border:1px solid #1e40af; padding:12px; margin-bottom:10px; border-radius:6px; }
.decision-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
.decision-selected { font-size:14px; color:#93c5fd; font-weight:600; }
.decision-score { font-size:18px; color:#22c55e; font-weight:bold; }
.reasoning { color:#94a3b8; font-size:11px; font-style:italic; margin-top:4px; }
.component-bar { display:flex; height:4px; background:#1e293b; border-radius:2px; margin-top:4px; overflow:hidden; }
.component-segment { height:100%; }
.component-reuse { background:#22c55e; }
.component-transfer { background:#3b82f6; }
.component-novelty { background:#a855f7; }
.component-signal { background:#f59e0b; }
.alt-routes { margin-top:10px; padding-top:10px; border-top:1px solid #1e40af; }
.alt-route { display:flex; justify-content:space-between; padding:4px 0; font-size:11px; color:#94a3b8; }
.alt-route-name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.alt-route-score { color:#64748b; margin-left:10px; }
"""

def render_dashboard(state: dict) -> str:
    """Render the main dashboard HTML."""
    health = state.get("health", {})
    timeline = state.get("timeline", [])
    routes = state.get("routes", [])
    latest_decision = state.get("latest_decision", {})
    decisions = state.get("decisions", [])
    operations = state.get("operations", {})
    frontier = state.get("frontier", [])

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Aristotle Research Control Plane</title>
    <style>{INLINE_CSS}</style>
</head>
<body>
    <div class="container">
        <header class="panel">
            <h1><span class="live-indicator"></span>Aristotle Research Control Plane</h1>
            <p class="muted">
                Project: <strong>{state.get("project_id", "unknown")}</strong> |
                Manager: <strong class="route-{'active' if health.get('manager_status') == 'running' else 'stalled'}">{health.get("manager_status", "unknown")}</strong> |
                Total Events: <strong>{health.get("event_count", 0)}</strong> |
                Last Update: <span class="timestamp-est">{health.get("latest_event_est", "")}</span>
            </p>
            <nav class="nav">
                <a href="/">Dashboard</a>
                <a href="#decisions">Decisions</a>
                <a href="#frontier">Frontier</a>
                <a href="#timeline">Timeline</a>
                <a href="/api/dashboard">API</a>
            </nav>
        </header>

        <section class="grid grid-4">
            <article class="panel metric-card">
                <div class="metric-value">{operations.get("active_experiments", 0)}</div>
                <div class="metric-label">Jobs Submitted</div>
            </article>
            <article class="panel metric-card">
                <div class="metric-value">{operations.get("recent_results", 0)}</div>
                <div class="metric-label">Results Ingested</div>
            </article>
            <article class="panel metric-card">
                <div class="metric-value">{operations.get("scored_candidates", 0)}</div>
                <div class="metric-label">Candidates Scored</div>
            </article>
            <article class="panel metric-card">
                <div class="metric-value">{operations.get("rejected_candidates", 0)}</div>
                <div class="metric-label">Rejected</div>
            </article>
        </section>

        <section id="decisions" class="panel">
            <h2>Manager Decision History (Last 5)</h2>
            <p class="muted">How the manager chooses which route to pursue - shows selected route vs alternatives</p>
            {render_decisions(decisions)}
        </section>

        <section id="frontier" class="panel">
            <h2>Candidate Scoring Frontier (Last 20)</h2>
            <p class="muted">How each candidate is scored - components determine selection priority</p>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Experiment</th>
                        <th>Route</th>
                        <th>Move</th>
                        <th>Total Score</th>
                        <th>Score Components</th>
                        <th>Reasoning</th>
                    </tr>
                </thead>
                <tbody>
                    {render_frontier(frontier)}
                </tbody>
            </table>
        </section>

        <section id="routes" class="panel">
            <h2>Theorem Routes ({len(routes)} active)</h2>
            <table>
                <thead>
                    <tr><th>Route</th><th>Status</th><th>Strength</th><th>Velocity</th><th>Reuse</th><th>Transfer</th><th>Novelty</th><th>Blockers</th></tr>
                </thead>
                <tbody>
                    {render_routes(routes[:15])}
                </tbody>
            </table>
        </section>

        <section id="timeline" class="panel">
            <h2>Live Manager Timeline (EST)</h2>
            <div id="timeline-container">
                {render_timeline(timeline[:30])}
            </div>
        </section>
    </div>

    <script>
        const evtSource = new EventSource("/api/stream");
        const timeline = document.getElementById("timeline-container");

        evtSource.onmessage = function(event) {{
            const data = JSON.parse(event.data);
            const block = document.createElement("div");
            block.className = "block evt-" + (data.css_class || "default");
            block.innerHTML = `
                <div><strong>${{data.event_type}}</strong> <span class="timestamp-est">${{data.est_time || data.occurred_at}}</span></div>
                <div class="muted">${{data.route_id ? "Route: " + data.route_id : ""}} ${{data.experiment_id ? "Exp: " + data.experiment_id : ""}}</div>
                <pre>${{JSON.stringify(data.payload, null, 2)}}</pre>
            `;
            timeline.insertBefore(block, timeline.firstChild);
            while (timeline.children.length > 30) {{
                timeline.removeChild(timeline.lastChild);
            }}
        }};

        evtSource.onerror = function(err) {{
            console.error("EventSource error:", err);
        }};
    </script>
</body>
</html>
"""
    return html

def render_timeline(events: list) -> str:
    """Render timeline events with EST times."""
    html = []
    for event in events:
        css = event.get("_css_class", "evt-default")
        est_time = event.get("est_time", "")
        payload = event.get("payload", {})
        event_type = event.get("event_type", "")
        
        # Show different details based on event type
        detail = ""
        if event_type == "candidate.scored":
            components = payload.get("components", {})
            detail = f"Score: {payload.get('total_score', 0):.2f} | Reuse: {components.get('reuse_score', 0):.1f} | Transfer: {components.get('transfer_score', 0):.1f}"
        elif event_type == "route.selected":
            detail = f"Selected: {payload.get('route_key', 'unknown')} | Score: {payload.get('total_score', 0):.2f}"
        elif event_type == "job.submitted":
            detail = f"Exp: {payload.get('experiment_id', 'unknown')}"
        
        html.append(f"""
        <div class="block {css}">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong>{event_type}</strong>
                <span class="timestamp-est">{est_time}</span>
            </div>
            {f'<div class="muted">{detail}</div>' if detail else ''}
            <details>
                <summary style="color:#64748b; font-size:11px; cursor:pointer;">Details</summary>
                <pre>{json.dumps(payload, indent=2)}</pre>
            </details>
        </div>
        """)
    return "\n".join(html)

def render_decisions(decisions: list) -> str:
    """Render detailed decision history showing how manager selects routes."""
    if not decisions:
        return '<div class="muted">No route decisions recorded yet.</div>'
    
    html = []
    # Show last 5 decisions, newest first
    for decision in reversed(decisions[-5:]):
        payload = decision.get("payload", {})
        selected_key = payload.get("route_key", "unknown")
        total_score = payload.get("total_score", 0)
        components = payload.get("components", {})
        alternatives = payload.get("alternatives", [])[:4]  # Top 4 alternatives
        est_time = to_est(decision.get("occurred_at", ""))
        
        # Build component breakdown
        comp_html = ""
        if components:
            comp_parts = []
            for key, val in components.items():
                if val > 0:
                    comp_parts.append(f"{key.replace('_', ' ')}: {val:.2f}")
            comp_html = " | ".join(comp_parts)
        
        # Build alternatives list
        alt_html = ""
        if alternatives:
            alt_rows = []
            for alt in alternatives:
                alt_key = alt.get("route_key", "")[:50]
                alt_score = alt.get("total_score", 0)
                alt_rows.append(f'<div class="alt-route"><span class="alt-route-name">{alt_key}</span><span class="alt-route-score">{alt_score:.2f}</span></div>')
            alt_html = f'<div class="alt-routes"><div class="muted" style="margin-bottom:6px;">Alternatives considered:</div>{"".join(alt_rows)}</div>'
        
        html.append(f"""
        <div class="decision-card">
            <div class="decision-header">
                <div>
                    <div class="timestamp-est">{est_time}</div>
                    <div class="decision-selected">{selected_key[:60]}</div>
                </div>
                <div class="decision-score">{total_score:.2f}</div>
            </div>
            <div class="score-breakdown">
                <div class="score-item"><div class="score-label">reuse</div><div class="score-value">{components.get('reuse_score', 0):.2f}</div></div>
                <div class="score-item"><div class="score-label">transfer</div><div class="score-value">{components.get('transfer_score', 0):.2f}</div></div>
                <div class="score-item"><div class="score-label">novelty</div><div class="score-value">{components.get('novelty_score', 0):.2f}</div></div>
                <div class="score-item"><div class="score-label">signal</div><div class="score-value">{components.get('signal_support', 0):.2f}</div></div>
            </div>
            {alt_html}
        </div>
        """)
    
    return "\n".join(html)

def render_frontier(frontier: list) -> str:
    """Render candidate frontier with scoring breakdown."""
    html = []
    for item in frontier:
        components = item.get("components", {})
        html.append(f"""
        <tr>
            <td>#{item.get('rank', 0)}</td>
            <td>{item.get('experiment_id', '')[:20]}...</td>
            <td>{item.get('route_id', '')[:35]}...</td>
            <td><span class="badge badge-scored">{item.get('move_family', 'unknown')}</span></td>
            <td style="font-weight:bold; color:#60a5fa;">{item.get('total_score', 0):.2f}</td>
            <td>
                <div style="font-size:10px;">
                    <span style="color:#22c55e;">R:{components.get('reuse_score', 0):.1f}</span>
                    <span style="color:#3b82f6;">T:{components.get('transfer_score', 0):.1f}</span>
                    <span style="color:#a855f7;">N:{components.get('novelty_score', 0):.1f}</span>
                    <span style="color:#f59e0b;">S:{components.get('signal_support', 0):.1f}</span>
                </div>
                <div class="component-bar">
                    <div class="component-segment component-reuse" style="width:{components.get('reuse_score', 0)*10}%"></div>
                    <div class="component-segment component-transfer" style="width:{components.get('transfer_score', 0)*10}%"></div>
                    <div class="component-segment component-novelty" style="width:{components.get('novelty_score', 0)*10}%"></div>
                    <div class="component-segment component-signal" style="width:{components.get('signal_support', 0)*10}%"></div>
                </div>
            </td>
            <td class="reasoning">{item.get('reasoning', '')}</td>
        </tr>
        """)
    return "\n".join(html)

def render_routes(routes: list) -> str:
    """Render route rows with detailed metrics."""
    html = []
    for route in routes:
        status = route.get("route_status", "unknown")
        status_class = "route-active" if status == "active" else "route-stalled" if status == "stalled" else ""
        html.append(f"""
        <tr>
            <td title="{route.get('route_key', '')}">{route.get("route_key", "")[:50]}{'...' if len(route.get('route_key', '')) > 50 else ''}</td>
            <td><span class="route-badge {status_class}">{status}</span></td>
            <td>{route.get("current_strength", 0):.2f}</td>
            <td>{route.get("recent_signal_velocity", 0):.2f}</td>
            <td>{route.get("reuse_score", 0):.2f}</td>
            <td>{route.get("transfer_score", 0):.2f}</td>
            <td>{route.get("novelty_score", 0):.2f}</td>
            <td>{route.get("blocker_pressure", 0):.2f}</td>
        </tr>
        """)
    return "\n".join(html)

@app.get("/", response_class=HTMLResponse)
def dashboard():
    """Main dashboard page."""
    state = load_state()
    html = render_dashboard(state)
    return HTMLResponse(content=html)

@app.get("/api/health")
def api_health():
    """Health check endpoint."""
    state = load_state()
    return JSONResponse(state.get("health", {}))

@app.get("/api/dashboard")
def api_dashboard():
    """Full state API."""
    return JSONResponse(load_state())

@app.get("/api/events")
def api_events():
    """Get all events with EST times."""
    events = load_json("manager_events.json")
    for e in events:
        e["est_time"] = to_est(e.get("occurred_at", ""))
        e["css_class"] = _event_css_class(e.get("event_type", ""))
    return JSONResponse(events[-200:])

@app.get("/api/decisions")
def api_decisions():
    """Get detailed decision history."""
    events = load_json("manager_events.json")
    decisions = [e for e in events if e.get("event_type") == "route.selected"]
    for d in decisions:
        d["est_time"] = to_est(d.get("occurred_at", ""))
    return JSONResponse(decisions[-20:])

@app.get("/api/stream")
async def api_stream(request: Request):
    """Server-sent events endpoint for live updates."""
    async def event_generator() -> AsyncGenerator[str, None]:
        events = load_json("manager_events.json")
        for event in events:
            event["css_class"] = _event_css_class(event.get("event_type", ""))
            event["est_time"] = to_est(event.get("occurred_at", ""))
            yield f"data: {json.dumps(event)}\n\n"

        last_count = len(events)
        while True:
            if await request.is_disconnected():
                break
            current = load_json("manager_events.json")
            if len(current) > last_count:
                for event in current[last_count:]:
                    event["css_class"] = _event_css_class(event.get("event_type", ""))
                    event["est_time"] = to_est(event.get("occurred_at", ""))
                    yield f"data: {json.dumps(event)}\n\n"
                last_count = len(current)
            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Vercel handler
handler = app
