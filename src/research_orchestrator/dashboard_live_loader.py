from __future__ import annotations

import json
from typing import Any, Dict

from research_orchestrator.db import Database
from research_orchestrator.live_projections import refresh_live_projections


class LiveDashboardLoader:
    def __init__(self, *, db_path: str, project_id: str | None = None):
        self.db_path = db_path
        self.project_id = project_id

    def load(self) -> Dict[str, Any]:
        db = Database(self.db_path)
        db.initialize()
        project_id = self.project_id or _infer_project_id(db)
        if not project_id:
            db.close()
            return _empty_state()
        refresh_live_projections(db, project_id)
        health_row = db.conn.execute(
            "SELECT payload_json, last_event_at, last_projection_at, manager_status FROM system_health_current WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        health_payload = json.loads(health_row["payload_json"]) if health_row else {}
        health = {
            "source_mode": "live_db",
            "last_event_at": health_row["last_event_at"] if health_row else "",
            "last_projection_at": health_row["last_projection_at"] if health_row else "",
            "manager_status": health_row["manager_status"] if health_row else "unknown",
            **health_payload,
        }

        timeline = [
            {
                **dict(row),
                "summary": json.loads(row["summary_json"]),
                "payload": json.loads(row["payload_json"]),
            }
            for row in db.conn.execute(
                "SELECT * FROM live_manager_timeline WHERE project_id = ? ORDER BY sequence_no DESC LIMIT 200",
                (project_id,),
            ).fetchall()
        ]

        routes = [
            {
                **dict(row),
                "summary": json.loads(row["summary_json"]),
            }
            for row in db.conn.execute(
                "SELECT * FROM route_strength_current WHERE project_id = ? ORDER BY current_strength DESC",
                (project_id,),
            ).fetchall()
        ]

        decision_row = db.conn.execute(
            "SELECT * FROM route_decisions_current WHERE project_id = ? ORDER BY occurred_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        decision = {}
        if decision_row:
            decision = {**dict(decision_row), "payload": json.loads(decision_row["payload_json"])}

        frontier = [
            {
                **dict(row),
                "score_breakdown": json.loads(row["score_breakdown_json"]),
                "candidate": json.loads(row["candidate_json"]),
            }
            for row in db.conn.execute(
                "SELECT * FROM frontier_rankings_current WHERE project_id = ? ORDER BY rank_position ASC LIMIT 50",
                (project_id,),
            ).fetchall()
        ]

        active_experiments = [
            json.loads(row["payload_json"])
            for row in db.conn.execute(
                "SELECT payload_json FROM active_experiments_current WHERE project_id = ?",
                (project_id,),
            ).fetchall()
        ]
        recent_results = [
            json.loads(row["payload_json"])
            for row in db.conn.execute(
                "SELECT payload_json FROM recent_results_current WHERE project_id = ? ORDER BY completed_at DESC",
                (project_id,),
            ).fetchall()
        ]
        incidents = [
            json.loads(row["payload_json"])
            for row in db.conn.execute(
                "SELECT payload_json FROM incidents_current WHERE project_id = ? ORDER BY updated_at DESC",
                (project_id,),
            ).fetchall()
        ]

        operations = {
            "active_experiments": len(active_experiments),
            "recent_results": len(recent_results),
            "open_incidents": len(incidents),
        }

        # Load latest strategic interpretation
        interpretation = db.conn.execute(
            "SELECT parsed_json FROM campaign_interpretations WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        outlook = json.loads(interpretation[0]) if interpretation else {}

        db.close()
        return {
            "project_id": project_id,
            "health": health,
            "timeline": timeline,
            "routes": routes,
            "decision": decision,
            "frontier": frontier,
            "operations": operations,
            "outlook": outlook,
            "active_experiments": active_experiments,
            "recent_results": recent_results,
            "incidents": incidents,
        }


def _infer_project_id(db: Database) -> str:
    row = db.conn.execute("SELECT project_id FROM projects ORDER BY created_at DESC LIMIT 1").fetchone()
    if row is None:
        return ""
    return row["project_id"]


def _empty_state() -> Dict[str, Any]:
    return {
        "project_id": "",
        "health": {"source_mode": "live_db", "manager_status": "unknown"},
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
