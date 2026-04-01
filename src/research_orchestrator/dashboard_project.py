"""Project-focused dashboard - shows experiments with LLM reasoning and KG contributions."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import DictLoader, Environment, select_autoescape

from research_orchestrator.db import Database


INLINE_CSS = """
body {
    margin: 0;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    background: #0d1117;
    color: #c9d1d9;
    line-height: 1.5;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}
header {
    border-bottom: 1px solid #30363d;
    padding-bottom: 16px;
    margin-bottom: 24px;
}
header h1 {
    margin: 0 0 8px 0;
    font-size: 20px;
    color: #f0f6fc;
}
header .subtitle {
    color: #8b949e;
    font-size: 13px;
}
header .controls {
    float: right;
}
button {
    background: #21262d;
    border: 1px solid #30363d;
    color: #c9d1d9;
    padding: 6px 12px;
    font-family: inherit;
    font-size: 12px;
    cursor: pointer;
    margin-left: 8px;
}
button:hover {
    background: #30363d;
}
.experiment-card {
    border: 1px solid #30363d;
    background: #161b22;
    margin-bottom: 12px;
    overflow: hidden;
}
.experiment-card.expanded {
    border-color: #58a6ff;
}
.experiment-header {
    padding: 12px 16px;
    background: #0d1117;
    border-bottom: 1px solid #30363d;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 12px;
}
.experiment-header:hover {
    background: #161b22;
}
.experiment-number {
    color: #8b949e;
    font-size: 11px;
    min-width: 80px;
}
.experiment-id {
    color: #58a6ff;
    font-size: 12px;
}
.status {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 2px;
    font-weight: 600;
    text-transform: uppercase;
}
.status-proved { background: #238636; color: #fff; }
.status-succeeded { background: #238636; color: #fff; }
.status-stalled { background: #9e6a03; color: #fff; }
.status-failed { background: #da3633; color: #fff; }
.status-planned { background: #1f6feb; color: #fff; }
.status-submitted { background: #1f6feb; color: #fff; }
.status-in_progress { background: #1f6feb; color: #fff; }
.move-tag {
    font-size: 11px;
    color: #d2a8ff;
    background: #3d1f47;
    padding: 2px 8px;
    border-radius: 2px;
}
.experiment-body {
    padding: 16px;
    display: none;
}
.experiment-card.expanded .experiment-body {
    display: block;
}
.section {
    margin-bottom: 20px;
}
.section:last-child {
    margin-bottom: 0;
}
.section-title {
    font-size: 11px;
    text-transform: uppercase;
    color: #8b949e;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    font-weight: 600;
}
.section-content {
    font-size: 13px;
    color: #c9d1d9;
}
.rationale {
    background: #0d1117;
    border-left: 3px solid #58a6ff;
    padding: 12px;
    font-style: italic;
    color: #c9d1d9;
}
.expected-signal {
    margin-top: 8px;
    font-size: 12px;
    color: #8b949e;
}
.raw-result {
    background: #0d1117;
    padding: 12px;
    font-size: 12px;
}
.raw-result-item {
    margin-bottom: 6px;
}
.raw-result-label {
    color: #8b949e;
    display: inline;
}
.raw-result-value {
    color: #c9d1d9;
    display: inline;
}
.summary-text {
    background: #0d1117;
    border-left: 3px solid #3fb950;
    padding: 12px;
    line-height: 1.6;
}
.kg-contribution {
    background: #0d1117;
    padding: 12px;
}
.kg-item {
    margin-bottom: 6px;
    font-size: 12px;
}
.kg-plus {
    color: #3fb950;
    font-weight: 600;
}
.kg-type {
    color: #d2a8ff;
}
.kg-name {
    color: #c9d1d9;
}
.kg-meta {
    color: #8b949e;
    font-size: 11px;
}
.kg-edge {
    color: #8b949e;
    font-size: 11px;
    margin-left: 16px;
}
.collapsed-indicator {
    margin-left: auto;
    color: #8b949e;
    font-size: 11px;
}
pre {
    background: #0d1117;
    padding: 12px;
    overflow-x: auto;
    font-size: 11px;
    line-height: 1.4;
    border: 1px solid #30363d;
    margin: 8px 0;
}
.toggle-btn {
    font-size: 11px;
    padding: 4px 8px;
    margin-top: 8px;
}
.no-experiments {
    text-align: center;
    padding: 60px 20px;
    color: #8b949e;
}
.search-bar {
    margin-bottom: 20px;
    display: flex;
    gap: 8px;
}
.search-bar input {
    flex: 1;
    background: #0d1117;
    border: 1px solid #30363d;
    color: #c9d1d9;
    padding: 8px 12px;
    font-family: inherit;
    font-size: 13px;
}
.search-bar input:focus {
    outline: none;
    border-color: #58a6ff;
}
.filter-btn {
    font-size: 11px;
}
.filter-btn.active {
    background: #1f6feb;
    border-color: #1f6feb;
}
"""


def _get_experiments_with_details(db: Database, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get experiments with all related details for project view."""
    rows = db.conn.execute(
        """
        SELECT 
            e.experiment_id,
            e.conjecture_id,
            e.move,
            e.move_family,
            e.status,
            e.proof_outcome,
            e.blocker_type,
            e.objective,
            e.expected_signal,
            e.modification_json,
            e.candidate_metadata_json,
            e.ingestion_json,
            e.outcome_json,
            e.created_at,
            e.completed_at,
            c.name as conjecture_name,
            c.domain as conjecture_domain
        FROM experiments e
        LEFT JOIN conjectures c ON c.conjecture_id = e.conjecture_id
        WHERE e.project_id = ?
        ORDER BY e.created_at DESC
        LIMIT ?
        """,
        (project_id, limit),
    ).fetchall()
    
    experiments = []
    for row in rows:
        exp = dict(row)
        mod_json = exp.get("modification_json")
        exp["modification"] = json.loads(mod_json) if mod_json else {}
        cand_json = exp.get("candidate_metadata_json")
        exp["candidate_metadata"] = json.loads(cand_json) if cand_json else {}
        ing_json = exp.get("ingestion_json")
        exp["ingestion"] = json.loads(ing_json) if ing_json else {}
        out_json = exp.get("outcome_json")
        exp["outcome"] = json.loads(out_json) if out_json else {}
        
        # Get manager rationale from audits
        audit_row = db.conn.execute(
            """
            SELECT selection_reason, score_breakdown_json, candidate_json
            FROM manager_candidate_audits
            WHERE experiment_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (exp["experiment_id"],),
        ).fetchone()

        if audit_row:
            exp["manager_reason"] = audit_row["selection_reason"]
            exp["score_breakdown"] = json.loads(audit_row.get("score_breakdown_json", "{}"))
            candidate = json.loads(audit_row.get("candidate_json", "{}"))
            exp["rationale"] = candidate.get("rationale", "")
        else:
            # Fallback: Get rationale from manager_events (candidate.scored)
            event_row = db.conn.execute(
                """
                SELECT payload_json
                FROM manager_events
                WHERE experiment_id = ?
                AND event_type = 'candidate.scored'
                ORDER BY sequence_no DESC
                LIMIT 1
                """,
                (exp["experiment_id"],),
            ).fetchone()

            if event_row:
                try:
                    payload = json.loads(event_row["payload_json"] or "{}")
                    exp["manager_reason"] = payload.get("selection_reason", "")
                    exp["score_breakdown"] = payload.get("score_breakdown", {})
                    exp["rationale"] = payload.get("rationale", "")
                    exp["policy_score"] = payload.get("policy_score", 0)
                except json.JSONDecodeError:
                    exp["manager_reason"] = ""
                    exp["score_breakdown"] = {}
                    exp["rationale"] = ""
                    exp["policy_score"] = 0
            else:
                exp["manager_reason"] = ""
                exp["score_breakdown"] = {}
                exp["rationale"] = exp["candidate_metadata"].get("rationale", "")
                exp["policy_score"] = 0
        
        # Get knowledge graph contributions
        exp["kg_nodes"] = []
        exp["kg_edges"] = []
        
        nodes = db.conn.execute(
            """
            SELECT node_type, label, confidence, status, metadata_json
            FROM discovery_graph_nodes
            WHERE experiment_id = ?
            """,
            (exp["experiment_id"],),
        ).fetchall()
        
        for node in nodes:
            exp["kg_nodes"].append({
                "type": node["node_type"],
                "label": node["label"],
                "confidence": node["confidence"],
                "status": node["status"],
                "metadata": json.loads(node.get("metadata_json", "{}")),
            })
        
        # Get edges for these nodes
        if exp["kg_nodes"]:
            node_ids = [n["label"] for n in exp["kg_nodes"]]  # Using label as identifier for display
            # Get edges where source or target is one of our nodes
            edges = db.conn.execute(
                """
                SELECT source_node_id, target_node_id, relation
                FROM discovery_graph_edges
                WHERE project_id = ?
                AND (source_node_id IN (SELECT node_id FROM discovery_graph_nodes WHERE experiment_id = ?)
                     OR target_node_id IN (SELECT node_id FROM discovery_graph_nodes WHERE experiment_id = ?))
                """,
                (project_id, exp["experiment_id"], exp["experiment_id"]),
            ).fetchall()
            
            for edge in edges:
                exp["kg_edges"].append({
                    "source": edge["source_node_id"][:8] + "...",
                    "target": edge["target_node_id"][:8] + "...",
                    "relation": edge["relation"],
                })
        
        # Get verification record for raw results
        verif_row = db.conn.execute(
            """
            SELECT record_json, raw_payload_json
            FROM verification_records
            WHERE experiment_id = ?
            LIMIT 1
            """,
            (exp["experiment_id"],),
        ).fetchone()
        
        if verif_row:
            exp["verification"] = json.loads(verif_row.get("record_json", "{}"))
            exp["verification_raw"] = json.loads(verif_row.get("raw_payload_json", "{}"))
        else:
            exp["verification"] = {}
            exp["verification_raw"] = {}
        
        experiments.append(exp)
    
    return experiments


def _get_project_info(db: Database, project_id: str) -> Dict[str, Any]:
    """Get project title and description."""
    row = db.conn.execute(
        "SELECT title, charter_json FROM projects WHERE project_id = ?",
        (project_id,),
    ).fetchone()
    
    if not row:
        return {"title": project_id, "description": ""}
    
    charter_json = row["charter_json"] or "{}"
    charter = json.loads(charter_json)
    return {
        "title": row["title"],
        "description": charter.get("overarching_problem", ""),
        "id": project_id,
    }


def _status_class(status: str) -> str:
    """Map status to CSS class."""
    status_map = {
        "proved": "status-proved",
        "succeeded": "status-succeeded",
        "stalled": "status-stalled",
        "failed": "status-failed",
        "planned": "status-planned",
        "submitted": "status-submitted",
        "in_progress": "status-in_progress",
    }
    return status_map.get(status, "status-planned")


def _status_icon(status: str) -> str:
    """Map status to icon."""
    icons = {
        "proved": "✓",
        "succeeded": "✓",
        "stalled": "⚠",
        "failed": "✗",
        "planned": "○",
        "submitted": "→",
        "in_progress": "◐",
    }
    return icons.get(status, "○")


def _format_duration(created: str, completed: Optional[str]) -> str:
    """Format experiment duration."""
    if not completed:
        return "in progress"
    try:
        from datetime import datetime
        fmt = "%Y-%m-%dT%H:%M:%S"
        start = datetime.fromisoformat(created.replace("Z", "+00:00").split(".")[0])
        end = datetime.fromisoformat(completed.replace("Z", "+00:00").split(".")[0])
        delta = end - start
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s"
        return f"{int(delta.total_seconds() / 60)}m"
    except:
        return "unknown"


TEMPLATES = {
    "project.html": """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Project: {{ project.title }}</title>
    <style>{{ inline_css }}</style>
  </head>
  <body>
    <div class="container">
      <header>
        <div class="controls">
          <button onclick="location.reload()">Refresh</button>
          <button onclick="toggleAll()">Expand/Collapse All</button>
        </div>
        <h1>PROJECT: {{ project.id }}</h1>
        <div class="subtitle">{{ project.title }}</div>
        {% if project.description %}
        <div class="subtitle" style="margin-top: 4px;">{{ project.description }}</div>
        {% endif %}
      </header>

      <div class="search-bar">
        <input type="text" id="search" placeholder="Filter experiments by move, status, or content..." onkeyup="filterExperiments()">
        <button class="filter-btn active" onclick="filterBy('all')" data-filter="all">All</button>
        <button class="filter-btn" onclick="filterBy('proved')" data-filter="proved">Proved</button>
        <button class="filter-btn" onclick="filterBy('stalled')" data-filter="stalled">Stalled</button>
        <button class="filter-btn" onclick="filterBy('failed')" data-filter="failed">Failed</button>
      </div>

      {% if experiments %}
        {% for exp in experiments %}
        <div class="experiment-card {{ 'expanded' if loop.index == 1 else '' }}" data-status="{{ exp.status }}" data-move="{{ exp.move }}" data-index="{{ loop.index }}">
          <div class="experiment-header" onclick="toggleCard(this)">
            <span class="experiment-number">#{{ experiments|length - loop.index + 1 }}</span>
            <span class="experiment-id">{{ exp.experiment_id[:8] }}</span>
            <span class="status {{ status_class(exp.status) }}">{{ status_icon(exp.status) }} {{ exp.status.upper() }}</span>
            <span class="move-tag">{{ exp.move }}</span>
            <span style="margin-left: auto; color: #8b949e; font-size: 11px;">{{ exp.conjecture_domain or 'unknown' }}</span>
            <span class="collapsed-indicator">{{ '▼' if loop.index == 1 else '▶' }}</span>
          </div>
          <div class="experiment-body">
            
            <!-- Manager Selection Rationale -->
            <div class="section">
              <div class="section-title">Manager Selection Rationale</div>
              <div class="section-content">
                <!-- LLM Synthesis Badge -->
                {% if exp.candidate_metadata and exp.candidate_metadata.llm_synthesized %}
                <div class="llm-synthesis-badge" style="background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 3px solid #a78bfa;">
                  <strong style="color: #e9d5ff;">🧠 LLM Synthesized Conjecture</strong>
                  {% if exp.candidate_metadata.synthesis_observation %}
                  <div style="color: #f3e8ff; margin-top: 6px; font-size: 12px;">{{ exp.candidate_metadata.synthesis_observation[:200] }}{% if exp.candidate_metadata.synthesis_observation|length > 200 %}...{% endif %}</div>
                  {% endif %}
                  {% if exp.candidate_metadata.novelty %}
                  <div style="color: #ddd6fe; margin-top: 4px; font-size: 11px; font-style: italic;">Novelty: {{ exp.candidate_metadata.novelty[:100] }}</div>
                  {% endif %}
                </div>
                {% endif %}

                {% if exp.manager_reason %}
                <div class="manager-reason" style="background: #1f2937; padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 3px solid #3b82f6;">
                  <strong style="color: #60a5fa;">Selection Reason:</strong>
                  <span style="color: #e5e7eb;">{{ exp.manager_reason }}</span>
                </div>
                {% endif %}

                {% if exp.score_breakdown and exp.score_breakdown.bonuses %}
                <div class="score-breakdown" style="margin-top: 12px;">
                  <div style="font-size: 12px; color: #9ca3af; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Policy Score Breakdown</div>
                  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px;">
                    {% if exp.score_breakdown.score is defined %}
                    <div style="background: #1f2937; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                      <span style="color: #9ca3af; font-size: 12px;">Total Score</span>
                      <span style="color: #4ade80; font-weight: 600;">{{ "%.2f"|format(exp.score_breakdown.score) }}</span>
                    </div>
                    {% endif %}
                    {% if exp.score_breakdown.bonuses.signal_support %}
                    <div style="background: #1f2937; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                      <span style="color: #9ca3af; font-size: 12px;">Signal Support</span>
                      <span style="color: #4ade80; font-weight: 500;">+{{ "%.2f"|format(exp.score_breakdown.bonuses.signal_support) }}</span>
                    </div>
                    {% endif %}
                    {% if exp.score_breakdown.bonuses.transfer_opportunity %}
                    <div style="background: #1f2937; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                      <span style="color: #9ca3af; font-size: 12px;">Transfer Score</span>
                      <span style="color: #4ade80; font-weight: 500;">+{{ "%.2f"|format(exp.score_breakdown.bonuses.transfer_opportunity) }}</span>
                    </div>
                    {% endif %}
                    {% if exp.score_breakdown.bonuses.reuse_potential %}
                    <div style="background: #1f2937; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                      <span style="color: #9ca3af; font-size: 12px;">Reuse Score</span>
                      <span style="color: #4ade80; font-weight: 500;">+{{ "%.2f"|format(exp.score_breakdown.bonuses.reuse_potential) }}</span>
                    </div>
                    {% endif %}
                    {% if exp.score_breakdown.bonuses.semantic_novelty %}
                    <div style="background: #1f2937; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                      <span style="color: #9ca3af; font-size: 12px;">Novelty Score</span>
                      <span style="color: #4ade80; font-weight: 500;">+{{ "%.2f"|format(exp.score_breakdown.bonuses.semantic_novelty) }}</span>
                    </div>
                    {% endif %}
                    {% if exp.score_breakdown.penalties %}
                      {% for penalty_name, penalty_value in exp.score_breakdown.penalties.items() %}
                        {% if penalty_value > 0 %}
                        <div style="background: #1f2937; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                          <span style="color: #9ca3af; font-size: 12px;">{{ penalty_name.replace('_', ' ').title() }}</span>
                          <span style="color: #f87171; font-weight: 500;">-{{ "%.2f"|format(penalty_value) }}</span>
                        </div>
                        {% endif %}
                      {% endfor %}
                    {% endif %}
                  </div>
                </div>
                {% endif %}

                {% if exp.expected_signal %}
                <div class="expected-signal" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #374151;">
                  <strong style="color: #60a5fa;">Expected signal:</strong> {{ exp.expected_signal }}
                </div>
                {% endif %}
              </div>
            </div>

            <!-- Raw Result -->
            <div class="section">
              <div class="section-title">Raw Result</div>
              <div class="section-content">
                <div class="raw-result">
                  <div class="raw-result-item">
                    <span class="raw-result-label">Duration:</span>
                    <span class="raw-result-value">{{ format_duration(exp.created_at, exp.completed_at) }}</span>
                  </div>
                  <div class="raw-result-item">
                    <span class="raw-result-label">Proof outcome:</span>
                    <span class="raw-result-value">{{ exp.proof_outcome or 'pending' }}</span>
                  </div>
                  {% if exp.blocker_type and exp.blocker_type != 'unknown' %}
                  <div class="raw-result-item">
                    <span class="raw-result-label">Blocker:</span>
                    <span class="raw-result-value">{{ exp.blocker_type }}</span>
                  </div>
                  {% endif %}
                  {% if exp.ingestion %}
                    {% if exp.ingestion.generated_lemmas %}
                    <div class="raw-result-item">
                      <span class="raw-result-label">Generated lemmas:</span>
                      <span class="raw-result-value">{{ exp.ingestion.generated_lemmas | length }}</span>
                    </div>
                    {% endif %}
                    {% if exp.ingestion.unresolved_goals %}
                    <div class="raw-result-item">
                      <span class="raw-result-label">Unresolved goals:</span>
                      <span class="raw-result-value">{{ exp.ingestion.unresolved_goals | length }}</span>
                    </div>
                    {% endif %}
                    {% if exp.ingestion.proof_trace_fragments %}
                    <div class="raw-result-item">
                      <span class="raw-result-label">Proof traces:</span>
                      <span class="raw-result-value">{{ exp.ingestion.proof_trace_fragments | length }}</span>
                    </div>
                    {% endif %}
                  {% endif %}
                </div>
              </div>
            </div>

            <!-- LLM Summary -->
            {% if exp.ingestion and exp.ingestion.signal_summary %}
            <div class="section">
              <div class="section-title">LLM Summary</div>
              <div class="section-content">
                <div class="summary-text">
                  {{ exp.ingestion.signal_summary }}
                </div>
              </div>
            </div>
            {% endif %}

            <!-- Knowledge Graph Contribution -->
            <div class="section">
              <div class="section-title">Knowledge Graph Contribution</div>
              <div class="section-content">
                {% if exp.kg_nodes %}
                <div class="kg-contribution">
                  {% for node in exp.kg_nodes %}
                  <div class="kg-item">
                    <span class="kg-plus">+</span>
                    <span class="kg-type">{{ node.type }}</span>
                    <span class="kg-name">"{{ node.label[:60] }}{{ '...' if node.label|length > 60 else '' }}"</span>
                    <span class="kg-meta">(confidence: {{ "%.2f"|format(node.confidence) }})</span>
                  </div>
                  {% endfor %}
                  {% for edge in exp.kg_edges %}
                  <div class="kg-edge">
                    → {{ edge.source }} —[{{ edge.relation }}]→ {{ edge.target }}
                  </div>
                  {% endfor %}
                </div>
                {% else %}
                <div class="kg-contribution" style="color: #8b949e;">
                  No knowledge graph nodes created from this experiment.
                </div>
                {% endif %}
              </div>
            </div>

            <!-- Raw Details Toggle -->
            <div class="section">
              <button class="toggle-btn" onclick="toggleRaw('raw-{{ exp.experiment_id }}')">Show Raw Data</button>
              <pre id="raw-{{ exp.experiment_id }}" style="display: none;">{{ exp | tojson(indent=2) }}</pre>
            </div>

          </div>
        </div>
        {% endfor %}
      {% else %}
        <div class="no-experiments">
          No experiments found for this project.<br>
          Run a manager tick to generate experiments.
        </div>
      {% endif %}
    </div>

    <script>
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
          card.style.display = text.includes(search) ? '' : 'none';
        });
      }

      function filterBy(status) {
        // Update button states
        document.querySelectorAll('.filter-btn').forEach(btn => {
          btn.classList.remove('active');
          if (btn.dataset.filter === status) {
            btn.classList.add('active');
          }
        });

        // Filter cards
        const cards = document.querySelectorAll('.experiment-card');
        cards.forEach(card => {
          if (status === 'all') {
            card.style.display = '';
          } else {
            const cardStatus = card.dataset.status;
            card.style.display = cardStatus === status ? '' : 'none';
          }
        });
      }
    </script>
  </body>
</html>
""",
}


def _render(name: str, **context: Any) -> HTMLResponse:
    env = Environment(
        loader=DictLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["tojson"] = lambda obj, indent=None: json.dumps(obj, indent=indent, default=str)
    template = env.get_template(name)
    html = template.render(**context, inline_css=INLINE_CSS)
    return HTMLResponse(html)


def build_project_router(config: dict[str, Any]) -> APIRouter:
    router = APIRouter()

    def _db() -> Database:
        db_path = config.get("db")
        if not db_path:
            raise HTTPException(status_code=500, detail="DB path not configured")
        db = Database(db_path)
        db.initialize()
        return db

    def _resolve_project_id(db: Database) -> str:
        cfg_project = config.get("project_id")
        # If a project is configured, verify it exists in the database
        if cfg_project:
            row = db.conn.execute(
                "SELECT project_id FROM projects WHERE project_id = ?",
                (cfg_project,)
            ).fetchone()
            if row:
                return cfg_project
        # Fall back to the most recent project in the database
        row = db.conn.execute(
            "SELECT project_id FROM projects ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else ""

    @router.get("/project", response_class=HTMLResponse)
    def project_view() -> HTMLResponse:
        """Main project dashboard showing all experiments."""
        db = _db()
        try:
            project_id = _resolve_project_id(db)
            if not project_id:
                return HTMLResponse("<h1>No project found</h1>", status_code=404)

            project = _get_project_info(db, project_id)
            experiments = _get_experiments_with_details(db, project_id)

            return _render(
                "project.html",
                project=project,
                experiments=experiments,
                status_class=_status_class,
                status_icon=_status_icon,
                format_duration=_format_duration,
            )
        finally:
            db.close()

    @router.get("/api/project/experiments")
    def api_project_experiments() -> JSONResponse:
        """API endpoint for experiment data."""
        db = _db()
        try:
            project_id = _resolve_project_id(db)
            if not project_id:
                return JSONResponse({"error": "No project found"}, status_code=404)

            experiments = _get_experiments_with_details(db, project_id)
            return JSONResponse({
                "project_id": project_id,
                "count": len(experiments),
                "experiments": experiments,
            })
        finally:
            db.close()

    @router.get("/api/project/experiments/{experiment_id}")
    def api_experiment_detail(experiment_id: str) -> JSONResponse:
        """Get full details for a single experiment."""
        db = _db()
        try:
            project_id = _resolve_project_id(db)
            rows = db.conn.execute(
                """
                SELECT e.*, c.name as conjecture_name, c.domain as conjecture_domain
                FROM experiments e
                LEFT JOIN conjectures c ON c.conjecture_id = e.conjecture_id
                WHERE e.experiment_id = ? AND e.project_id = ?
                """,
                (experiment_id, project_id),
            ).fetchall()
            
            if not rows:
                return JSONResponse({"error": "Experiment not found"}, status_code=404)
            
            experiments = _get_experiments_with_details(db, project_id)
            for exp in experiments:
                if exp["experiment_id"] == experiment_id:
                    return JSONResponse(exp)
            
            return JSONResponse({"error": "Experiment not found"}, status_code=404)
        finally:
            db.close()

    return router
