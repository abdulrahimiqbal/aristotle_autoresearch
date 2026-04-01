import json
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional

app = FastAPI(title="Aristotle Research Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE_DIR = Path(os.getenv("STATE_DIR", "outputs/dashboard_bundle_live"))
PROJECT_ID = os.getenv("PROJECT_ID", "erdos-combo-001")


def load_json(filename: str) -> list:
    """Load JSON lines or JSON array from file."""
    path = STATE_DIR / filename
    if not path.exists():
        return []
    content = path.read_text()
    if not content.strip():
        return []
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    results = []
    for line in content.strip().split('\n'):
        if line.strip():
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return results


def load_project_info() -> Dict[str, Any]:
    """Load project info from campaign_spec.json or infer from data."""
    spec_path = STATE_DIR / "campaign_spec.json"
    if spec_path.exists():
        try:
            spec = json.loads(spec_path.read_text())
            return {
                "id": PROJECT_ID,
                "title": spec.get("title", "Research Project"),
                "description": spec.get("description", ""),
            }
        except:
            pass
    return {"id": PROJECT_ID, "title": PROJECT_ID, "description": ""}


def load_experiments() -> List[Dict[str, Any]]:
    """Load experiments from CSV bundle file and merge with event data."""
    experiments = []
    
    # Load experiments from CSV
    csv_path = STATE_DIR / "experiments.csv"
    if csv_path.exists():
        import csv
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                exp_id = row.get("experiment_id", "unknown")
                mod_json = row.get("modification_json", "{}")
                try:
                    modification = json.loads(mod_json) if mod_json else {}
                except:
                    modification = {}
                
                exp = {
                    "experiment_id": exp_id,
                    "conjecture_id": row.get("conjecture_id", ""),
                    "move": row.get("move", "unknown"),
                    "move_family": row.get("move_family", "unknown"),
                    "status": row.get("status", "planned"),
                    "proof_outcome": row.get("proof_outcome") or None,
                    "blocker_type": row.get("blocker_type") or None,
                    "objective": row.get("objective", ""),
                    "expected_signal": row.get("expected_signal", ""),
                    "rationale": "",  # Will try to get from events
                    "created_at": row.get("created_at", ""),
                    "completed_at": row.get("completed_at") or None,
                    "conjecture_name": "",
                    "conjecture_domain": "",
                    "modification": modification,
                    "candidate_metadata": {k: v for k, v in row.items() if k not in ["modification_json"]},
                    "ingestion": {},
                    "outcome": {},
                    "manager_reason": "",
                    "kg_nodes": [],
                    "kg_edges": [],
                    "verification": {},
                }
                experiments.append(exp)
    
    # Load manager candidate audits for selection rationale
    audits = load_json("manager_candidate_audits.json")
    exp_manager_reason = {}
    exp_score_breakdown = {}

    for audit in audits:
        exp_id = audit.get("experiment_id")
        if exp_id:
            # Use selection_reason if available, fall back to candidate rationale
            reason = audit.get("selection_reason", "")
            if not reason and audit.get("candidate"):
                reason = audit["candidate"].get("rationale", "")
            if reason:
                exp_manager_reason[exp_id] = reason

            # Use score_breakdown from audit
            if audit.get("score_breakdown"):
                exp_score_breakdown[exp_id] = audit["score_breakdown"]

    # Try to enrich with rationale from manager events
    events = load_json("manager_events.json")
    exp_rationale = {}

    for event in events:
        if event.get("event_type") == "candidate.scored":
            payload = event.get("payload", {})
            exp_id = payload.get("experiment_id")
            if exp_id and payload.get("rationale"):
                exp_rationale[exp_id] = payload.get("rationale")

    for exp in experiments:
        exp_id = exp["experiment_id"]
        if exp_id in exp_rationale:
            exp["rationale"] = exp_rationale[exp_id]
        # Prefer audit data for manager_reason and score_breakdown
        if exp_id in exp_manager_reason:
            exp["manager_reason"] = exp_manager_reason[exp_id]
        if exp_id in exp_score_breakdown:
            exp["score_breakdown"] = exp_score_breakdown[exp_id]

        # If no rationale, use objective as fallback
        if not exp["rationale"]:
            exp["rationale"] = exp["objective"] or "No rationale recorded"
    
    experiments.sort(key=lambda e: e.get("created_at", ""), reverse=True)
    return experiments


def _status_class(status: str) -> str:
    status_map = {
        "proved": "status-proved", "succeeded": "status-proved", "ingested": "status-proved",
        "completed": "status-proved", "stalled": "status-stalled", "failed": "status-failed",
        "planned": "status-planned", "submitted": "status-planned", "in_progress": "status-planned",
    }
    return status_map.get(status, "status-planned")


def _status_icon(status: str) -> str:
    icons = {
        "proved": "✓", "succeeded": "✓", "ingested": "✓", "completed": "✓",
        "stalled": "⚠", "failed": "✗", "planned": "○", "submitted": "→", "in_progress": "◐",
    }
    return icons.get(status, "○")


def _format_duration(created: str, completed: Optional[str]) -> str:
    if not completed:
        return "in progress"
    try:
        from datetime import datetime
        start = datetime.fromisoformat(created.replace("Z", "+00:00").split(".")[0])
        end = datetime.fromisoformat(completed.replace("Z", "+00:00").split(".")[0])
        delta = end - start
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s"
        return f"{int(delta.total_seconds() / 60)}m"
    except:
        return "unknown"


INLINE_CSS = """
body { margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; background: #0d1117; color: #c9d1d9; line-height: 1.5; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
header { border-bottom: 1px solid #30363d; padding-bottom: 16px; margin-bottom: 24px; }
header h1 { margin: 0 0 8px 0; font-size: 20px; color: #f0f6fc; }
header .subtitle { color: #8b949e; font-size: 13px; }
header .controls { float: right; }
button { background: #21262d; border: 1px solid #30363d; color: #c9d1d9; padding: 6px 12px; font-family: inherit; font-size: 12px; cursor: pointer; margin-left: 8px; }
button:hover { background: #30363d; }
.experiment-card { border: 1px solid #30363d; background: #161b22; margin-bottom: 12px; overflow: hidden; }
.experiment-card.expanded { border-color: #58a6ff; }
.experiment-header { padding: 12px 16px; background: #0d1117; border-bottom: 1px solid #30363d; cursor: pointer; display: flex; align-items: center; gap: 12px; }
.experiment-header:hover { background: #161b22; }
.experiment-number { color: #8b949e; font-size: 11px; min-width: 80px; }
.experiment-id { color: #58a6ff; font-size: 12px; }
.status { font-size: 11px; padding: 2px 8px; border-radius: 2px; font-weight: 600; text-transform: uppercase; }
.status-proved { background: #238636; color: #fff; }
.status-succeeded { background: #238636; color: #fff; }
.status-stalled { background: #9e6a03; color: #fff; }
.status-failed { background: #da3633; color: #fff; }
.status-planned { background: #1f6feb; color: #fff; }
.status-submitted { background: #1f6feb; color: #fff; }
.status-in_progress { background: #1f6feb; color: #fff; }
.move-tag { font-size: 11px; color: #d2a8ff; background: #3d1f47; padding: 2px 8px; border-radius: 2px; }
.experiment-body { padding: 16px; display: none; }
.experiment-card.expanded .experiment-body { display: block; }
.section { margin-bottom: 20px; }
.section:last-child { margin-bottom: 0; }
.section-title { font-size: 11px; text-transform: uppercase; color: #8b949e; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600; }
.section-content { font-size: 13px; color: #c9d1d9; }
.rationale { background: #0d1117; border-left: 3px solid #58a6ff; padding: 12px; font-style: italic; color: #c9d1d9; }
.expected-signal { margin-top: 8px; font-size: 12px; color: #8b949e; }
.raw-result { background: #0d1117; padding: 12px; font-size: 12px; }
.raw-result-item { margin-bottom: 6px; }
.raw-result-label { color: #8b949e; display: inline; }
.raw-result-value { color: #c9d1d9; display: inline; }
.summary-text { background: #0d1117; border-left: 3px solid #3fb950; padding: 12px; line-height: 1.6; }
.kg-contribution { background: #0d1117; padding: 12px; }
.kg-item { margin-bottom: 6px; font-size: 12px; }
.kg-plus { color: #3fb950; font-weight: 600; }
.kg-type { color: #d2a8ff; }
.kg-name { color: #c9d1d9; }
.kg-meta { color: #8b949e; font-size: 11px; }
.kg-edge { color: #8b949e; font-size: 11px; margin-left: 16px; }
.collapsed-indicator { margin-left: auto; color: #8b949e; font-size: 11px; }
pre { background: #0d1117; padding: 12px; overflow-x: auto; font-size: 11px; line-height: 1.4; border: 1px solid #30363d; margin: 8px 0; }
.toggle-btn { font-size: 11px; padding: 4px 8px; margin-top: 8px; }
.no-experiments { text-align: center; padding: 60px 20px; color: #8b949e; }
.search-bar { margin-bottom: 20px; display: flex; gap: 8px; }
.search-bar input { flex: 1; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 8px 12px; font-family: inherit; font-size: 13px; }
.search-bar input:focus { outline: none; border-color: #58a6ff; }
.filter-btn { font-size: 11px; }
.filter-btn.active { background: #1f6feb; border-color: #1f6feb; }
.metric { display: inline-block; margin-right: 20px; font-size: 13px; }
.metric-value { font-weight: 600; color: #58a6ff; }
.metric-label { color: #8b949e; }
"""


JAVASCRIPT = """
function toggleCard(header) {
  const card = header.parentElement;
  const indicator = header.querySelector('.collapsed-indicator');
  card.classList.toggle('expanded');
  indicator.textContent = card.classList.contains('expanded') ? '▼' : '▶';
}

function toggleAll() {
  const cards = document.querySelectorAll('.experiment-card');
  const anyExpanded = Array.from(cards).some(c => c.classList.contains('expanded'));
  cards.forEach(card => {
    const indicator = card.querySelector('.collapsed-indicator');
    if (anyExpanded) {
      card.classList.remove('expanded');
      indicator.textContent = '▶';
    } else {
      card.classList.add('expanded');
      indicator.textContent = '▼';
    }
  });
}

function toggleRaw(id) {
  const el = document.getElementById(id);
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

function filterExperiments() {
  const search = document.getElementById('search').value.toLowerCase();
  const cards = document.querySelectorAll('.experiment-card');
  cards.forEach(card => {
    const text = card.textContent.toLowerCase();
    const matchesSearch = text.includes(search);
    const matchesStatus = currentStatusFilter === 'all' || card.dataset.status === currentStatusFilter || (currentStatusFilter === 'proved' && ['ingested','completed','proved','succeeded'].includes(card.dataset.status));
    const matchesConjecture = currentConjectureFilter === 'all' || card.dataset.conjecture === currentConjectureFilter;
    card.style.display = (matchesSearch && matchesStatus && matchesConjecture) ? '' : 'none';
  });
}

let currentStatusFilter = 'all';
let currentConjectureFilter = 'all';

function filterBy(status) {
  currentStatusFilter = status;
  document.querySelectorAll('.filter-btn[data-type="status"]').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.filter === status) {
      btn.classList.add('active');
    }
  });
  applyFilters();
}

function filterByConjecture(conjecture) {
  currentConjectureFilter = conjecture;
  document.querySelectorAll('.filter-btn[data-type="conjecture"]').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.filter === conjecture) {
      btn.classList.add('active');
    }
  });
  applyFilters();
}

function applyFilters() {
  const search = document.getElementById('search').value.toLowerCase();
  const cards = document.querySelectorAll('.experiment-card');
  cards.forEach(card => {
    const text = card.textContent.toLowerCase();
    const matchesSearch = text.includes(search);
    const matchesConjecture = currentConjectureFilter === 'all' || card.dataset.conjecture === currentConjectureFilter;
    let matchesStatus = currentStatusFilter === 'all';
    if (!matchesStatus) {
      const cardStatus = card.dataset.status;
      if (currentStatusFilter === 'proved') {
        matchesStatus = ['ingested','completed','proved','succeeded'].includes(cardStatus);
      } else {
        matchesStatus = cardStatus === currentStatusFilter;
      }
    }
    card.style.display = (matchesSearch && matchesStatus && matchesConjecture) ? '' : 'none';
  });
}
"""


def render_experiment_card(exp: Dict, num: int, expanded: bool) -> str:
    exp_id = exp.get("experiment_id", "unknown")
    short_id = exp_id[:8]
    status = exp.get("status", "planned")
    move = exp.get("move", "unknown")
    conjecture_id = exp.get("conjecture_id", "unknown")
    created = exp.get("created_at", "")
    completed = exp.get("completed_at")
    
    status_class = _status_class(status)
    status_icon = _status_icon(status)
    duration = _format_duration(created, completed)
    
    # Knowledge graph nodes
    kg_nodes = exp.get("kg_nodes", [])
    kg_edges = exp.get("kg_edges", [])
    kg_html = ""
    if kg_nodes:
        kg_items = []
        for node in kg_nodes:
            label = node.get("label", "")[:60]
            if len(node.get("label", "")) > 60:
                label += "..."
            conf = node.get("confidence", 0)
            kg_items.append(f'<div class="kg-item"><span class="kg-plus">+</span> <span class="kg-type">{node.get("type", "node")}</span> <span class="kg-name">"{label}"</span> <span class="kg-meta">(confidence: {conf:.2f})</span></div>')
        for edge in kg_edges:
            src = edge.get("source", "")[:8]
            tgt = edge.get("target", "")[:8]
            rel = edge.get("relation", "")
            kg_items.append(f'<div class="kg-edge">→ {src}... —[{rel}]→ {tgt}...</div>')
        kg_html = "\n".join(kg_items)
    else:
        kg_html = '<div style="color: #8b949e;">No knowledge graph nodes created from this experiment.</div>'
    
    # LLM Summary
    summary = exp.get("ingestion", {}).get("signal_summary", "")
    summary_html = ""
    if summary:
        summary_html = f'<div class="section"><div class="section-title">LLM Summary</div><div class="section-content"><div class="summary-text">{summary}</div></div></div>'
    
    # Raw results
    raw_items = [
        f'<div class="raw-result-item"><span class="raw-result-label">Duration:</span> <span class="raw-result-value">{duration}</span></div>',
        f'<div class="raw-result-item"><span class="raw-result-label">Proof outcome:</span> <span class="raw-result-value">{exp.get("proof_outcome") or "pending"}</span></div>',
    ]
    
    if exp.get("blocker_type") and exp.get("blocker_type") != "unknown":
        raw_items.append(f'<div class="raw-result-item"><span class="raw-result-label">Blocker:</span> <span class="raw-result-value">{exp.get("blocker_type")}</span></div>')
    
    ingestion = exp.get("ingestion", {})
    if ingestion.get("generated_lemmas"):
        raw_items.append(f'<div class="raw-result-item"><span class="raw-result-label">Generated lemmas:</span> <span class="raw-result-value">{len(ingestion["generated_lemmas"])}</span></div>')
    
    if ingestion.get("unresolved_goals"):
        raw_items.append(f'<div class="raw-result-item"><span class="raw-result-label">Unresolved goals:</span> <span class="raw-result-value">{len(ingestion["unresolved_goals"])}</span></div>')
    
    if ingestion.get("proof_trace_fragments"):
        raw_items.append(f'<div class="raw-result-item"><span class="raw-result-label">Proof traces:</span> <span class="raw-result-value">{len(ingestion["proof_trace_fragments"])}</span></div>')
    
    raw_html = "\n".join(raw_items)
    
    # Manager Selection Rationale
    manager_reason = exp.get("manager_reason", "")
    score_breakdown = exp.get("score_breakdown", {})
    expected_signal = exp.get("expected_signal", "")
    candidate_meta = exp.get("candidate_metadata", {})

    # Build manager rationale HTML
    manager_html = ""

    # Show LLM synthesis badge if applicable
    if candidate_meta.get("llm_synthesized"):
        synthesis_obs = candidate_meta.get("synthesis_observation", "")
        novelty = candidate_meta.get("novelty", "")
        manager_html += f'''<div class="llm-synthesis-badge" style="background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 3px solid #a78bfa;">
          <strong style="color: #e9d5ff;">🧠 LLM Synthesized Conjecture</strong>
          <div style="color: #f3e8ff; margin-top: 6px; font-size: 12px;">{synthesis_obs[:200]}{"..." if len(synthesis_obs) > 200 else ""}</div>
          {f'<div style="color: #ddd6fe; margin-top: 4px; font-size: 11px; font-style: italic;">Novelty: {novelty[:100]}</div>' if novelty else ""}
        </div>'''

    if manager_reason:
        manager_html += f'''<div class="manager-reason" style="background: #1f2937; padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 3px solid #3b82f6;">
          <strong style="color: #60a5fa;">Selection Reason:</strong>
          <span style="color: #e5e7eb;">{manager_reason}</span>
        </div>'''

    # Build score breakdown HTML
    score_html = ""
    if score_breakdown and score_breakdown.get("bonuses"):
        bonuses = score_breakdown.get("bonuses", {})
        penalties = score_breakdown.get("penalties", {})
        total_score = score_breakdown.get("score", 0)

        score_items = []

        # Total score
        score_items.append(f'''<div style="background: #1f2937; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #9ca3af; font-size: 12px;">Total Score</span>
          <span style="color: #4ade80; font-weight: 600;">{total_score:.2f}</span>
        </div>''')

        # Key bonus factors
        key_factors = [
            ("signal_support", "Signal Support"),
            ("transfer_opportunity", "Transfer Score"),
            ("reuse_potential", "Reuse Score"),
            ("semantic_novelty", "Novelty Score"),
        ]
        for key, label in key_factors:
            val = bonuses.get(key, 0)
            if val > 0:
                score_items.append(f'''<div style="background: #1f2937; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #9ca3af; font-size: 12px;">{label}</span>
          <span style="color: #4ade80; font-weight: 500;">+{val:.2f}</span>
        </div>''')

        # Penalties
        for key, val in penalties.items():
            if val > 0:
                label = key.replace('_', ' ').title()
                score_items.append(f'''<div style="background: #1f2937; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #9ca3af; font-size: 12px;">{label}</span>
          <span style="color: #f87171; font-weight: 500;">-{val:.2f}</span>
        </div>''')

        if score_items:
            score_html = f'''<div class="score-breakdown" style="margin-top: 12px;">
          <div style="font-size: 12px; color: #9ca3af; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Policy Score Breakdown</div>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px;">
            {''.join(score_items)}
          </div>
        </div>'''

    expected_html = f'<div class="expected-signal" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #374151;"><strong style="color: #60a5fa;">Expected signal:</strong> {expected_signal}</div>' if expected_signal else ""
    
    # Raw JSON toggle
    raw_json = json.dumps(exp, indent=2, default=str)
    
    expanded_class = "expanded" if expanded else ""
    indicator = "▼" if expanded else "▶"
    
    return f"""<div class="experiment-card {expanded_class}" data-status="{status}" data-move="{move}" data-conjecture="{conjecture_id}" data-index="{num}">
  <div class="experiment-header" onclick="toggleCard(this)">
    <span class="experiment-number">#{num}</span>
    <span class="experiment-id">{short_id}</span>
    <span class="status {status_class}">{status_icon} {status.upper()}</span>
    <span class="move-tag">{move}</span>
    <span style="margin-left: auto; color: #8b949e; font-size: 11px;">{conjecture_id}</span>
    <span class="collapsed-indicator">{indicator}</span>
  </div>
    <div class="experiment-body">
    <div class="section">
      <div class="section-title">Manager Selection Rationale</div>
      <div class="section-content">
        {manager_html}
        {score_html}
        {expected_html}
      </div>
    </div>
    <div class="section">
      <div class="section-title">Raw Result</div>
      <div class="section-content">
        <div class="raw-result">{raw_html}</div>
      </div>
    </div>
    {summary_html}
    <div class="section">
      <div class="section-title">Knowledge Graph Contribution</div>
      <div class="section-content">
        <div class="kg-contribution">{kg_html}</div>
      </div>
    </div>
    <div class="section">
      <button class="toggle-btn" onclick="event.stopPropagation(); toggleRaw('raw-{exp_id}')">Show Raw Data</button>
      <pre id="raw-{exp_id}" style="display: none;">{raw_json}</pre>
    </div>
  </div>
</div>"""


def render_project_dashboard(project: Dict, experiments: List[Dict]) -> str:
    project_id = project.get("id", "unknown")
    title = project.get("title", "")
    description = project.get("description", "")
    
    total = len(experiments)
    succeeded = len([e for e in experiments if e.get("status") in ["proved", "succeeded", "ingested", "completed"]])
    failed = len([e for e in experiments if e.get("status") == "failed"])
    stalled = len([e for e in experiments if e.get("status") == "stalled"])
    
    # Get unique conjectures and their counts
    conjecture_counts = {}
    for exp in experiments:
        cid = exp.get("conjecture_id", "unknown")
        conjecture_counts[cid] = conjecture_counts.get(cid, 0) + 1
    
    # Build conjecture filter buttons
    conj_buttons = '<button class="filter-btn active" onclick="filterByConjecture(\'all\')" data-type="conjecture" data-filter="all">All Problems</button>'
    for cid in sorted(conjecture_counts.keys()):
        count = conjecture_counts[cid]
        conj_buttons += f'<button class="filter-btn" onclick="filterByConjecture(\'{cid}\')" data-type="conjecture" data-filter="{cid}">{cid} ({count})</button>'
    
    # Render experiment cards
    exp_html = ""
    if experiments:
        for i, exp in enumerate(experiments):
            num = total - i
            exp_html += render_experiment_card(exp, num, i == 0)
    else:
        exp_html = '<div class="no-experiments">No experiments found for this project.<br>Run a manager tick to generate experiments.</div>'
    
    desc_html = f'<div class="subtitle" style="margin-top: 4px;">{description}</div>' if description else ""
    
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Project: {title or project_id}</title>
    <style>{INLINE_CSS}</style>
  </head>
  <body>
    <div class="container">
      <header>
        <div class="controls">
          <button onclick="location.reload()">Refresh</button>
          <button onclick="toggleAll()">Expand/Collapse All</button>
        </div>
        <h1>PROJECT: {project_id}</h1>
        <div class="subtitle">{title}</div>
        {desc_html}
        <div style="margin-top: 12px;">
          <span class="metric"><span class="metric-value">{total}</span> <span class="metric-label">experiments</span></span>
          <span class="metric"><span class="metric-value">{succeeded}</span> <span class="metric-label">succeeded</span></span>
          <span class="metric"><span class="metric-value">{failed}</span> <span class="metric-label">failed</span></span>
          <span class="metric"><span class="metric-value">{stalled}</span> <span class="metric-label">stalled</span></span>
        </div>
      </header>
      <div class="search-bar">
        <input type="text" id="search" placeholder="Filter experiments by move, status, or content..." onkeyup="filterExperiments()">
      </div>
      <div style="margin-bottom: 12px;">
        <span style="color: #8b949e; font-size: 12px; margin-right: 8px;">Problem:</span>
        {conj_buttons}
      </div>
      <div style="margin-bottom: 20px;">
        <span style="color: #8b949e; font-size: 12px; margin-right: 8px;">Status:</span>
        <button class="filter-btn active" onclick="filterBy('all')" data-type="status" data-filter="all">All</button>
        <button class="filter-btn" onclick="filterBy('proved')" data-type="status" data-filter="proved">Proved</button>
        <button class="filter-btn" onclick="filterBy('stalled')" data-type="status" data-filter="stalled">Stalled</button>
        <button class="filter-btn" onclick="filterBy('failed')" data-type="status" data-filter="failed">Failed</button>
      </div>
      {exp_html}
    </div>
    <script>{JAVASCRIPT}</script>
  </body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def project_dashboard():
    project = load_project_info()
    experiments = load_experiments()
    html = render_project_dashboard(project, experiments)
    return HTMLResponse(content=html)


@app.get("/api/experiments")
def api_experiments():
    experiments = load_experiments()
    return JSONResponse({"project_id": PROJECT_ID, "count": len(experiments), "experiments": experiments})


@app.get("/api/experiments/{experiment_id}")
def api_experiment_detail(experiment_id: str):
    experiments = load_experiments()
    for exp in experiments:
        if exp.get("experiment_id") == experiment_id:
            return JSONResponse(exp)
    return JSONResponse({"error": "Experiment not found"}, status_code=404)


@app.get("/api/health")
def api_health():
    experiments = load_experiments()
    return JSONResponse({"project_id": PROJECT_ID, "experiment_count": len(experiments), "source_mode": "json_bundle"})


@app.get("/api/stream")
async def api_stream(request: Request):
    async def event_generator() -> AsyncGenerator[str, None]:
        last_count = len(load_experiments())
        while True:
            if await request.is_disconnected():
                break
            current = load_experiments()
            if len(current) > last_count:
                for exp in current[last_count:]:
                    yield f"data: {{\"type\": \"new_experiment\", \"experiment\": {json.dumps(exp, default=str)}}}\n\n"
                last_count = len(current)
            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


# Vercel handler
handler = app
