from __future__ import annotations

import json
from typing import Any

from research_orchestrator.db import Database, utcnow


TIMELINE_PROJECTION = "live_manager_timeline"


def _insert_timeline_events(db: Database, project_id: str) -> int:
    last_seq = db.get_projection_checkpoint(TIMELINE_PROJECTION)
    events = db.list_manager_events(project_id, since_sequence=last_seq, limit=2000)
    if not events:
        return last_seq
    for event in events:
        db.conn.execute(
            """
            INSERT OR IGNORE INTO live_manager_timeline(
                event_id, sequence_no, occurred_at, project_id, run_id, event_type,
                route_id, experiment_id, summary_json, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                int(event["sequence_no"]),
                event["occurred_at"],
                project_id,
                event["run_id"],
                event["event_type"],
                event.get("route_id"),
                event.get("experiment_id"),
                json.dumps({"event_type": event["event_type"], "summary": event.get("payload", {}).get("summary", "")}),
                json.dumps(event.get("payload", {})),
            ),
        )
    db.conn.commit()
    last_seq = events[-1]["sequence_no"]
    db.update_projection_checkpoint(TIMELINE_PROJECTION, int(last_seq))
    return int(last_seq)


def refresh_live_projections(db: Database, project_id: str, run_id: str | None = None) -> None:
    last_seq = _insert_timeline_events(db, project_id)
    now = utcnow()

    db.conn.execute("DELETE FROM route_strength_current WHERE project_id = ?", (project_id,))
    for route in db.list_theorem_routes(project_id):
        db.conn.execute(
            """
            INSERT INTO route_strength_current(
                route_id, project_id, route_key, route_status, current_strength,
                recent_signal_velocity, blocker_pressure, novelty_score, reuse_score,
                transfer_score, operator_priority, last_selected_at, last_progress_at,
                summary_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                route["route_id"],
                project_id,
                route["route_key"],
                route["route_status"],
                float(route.get("current_strength", 0.0)),
                float(route.get("recent_signal_velocity", 0.0)),
                float(route.get("blocker_pressure", 0.0)),
                float(route.get("novelty_score", 0.0)),
                float(route.get("reuse_score", 0.0)),
                float(route.get("transfer_score", 0.0)),
                int(route.get("operator_priority", 0)),
                route.get("last_selected_at"),
                route.get("last_progress_at"),
                json.dumps(route.get("summary", {})),
                now,
            ),
        )

    latest_run = db.latest_manager_run(project_id) if run_id is None else {"run_id": run_id}
    if latest_run and latest_run.get("run_id"):
        run_id = latest_run["run_id"]
    if run_id:
        audits = db.list_manager_candidate_audits(run_id)
        db.conn.execute("DELETE FROM frontier_rankings_current WHERE project_id = ?", (project_id,))
        for audit in audits:
            breakdown = audit.get("score_breakdown", {})
            score = float(breakdown.get("score", audit.get("policy_score", 0.0)))
            candidate = audit.get("candidate", {})
            db.conn.execute(
                """
                INSERT INTO frontier_rankings_current(
                    entry_id, project_id, run_id, occurred_at, rank_position,
                    experiment_id, route_id, score, score_breakdown_json, candidate_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit["audit_id"],
                    project_id,
                    run_id,
                    audit.get("created_at") or now,
                    int(audit.get("rank_position", 0)),
                    audit["experiment_id"],
                    candidate.get("route_id"),
                    score,
                    json.dumps(breakdown),
                    json.dumps(candidate),
                ),
            )

    decision_event = db.conn.execute(
        """
        SELECT * FROM manager_events
        WHERE project_id = ? AND event_type = 'route.selected'
        ORDER BY sequence_no DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    if decision_event is not None:
        event_row = dict(decision_event)
        payload = json.loads(event_row["payload_json"])
        db.conn.execute("DELETE FROM route_decisions_current WHERE project_id = ?", (project_id,))
        db.conn.execute(
            """
            INSERT INTO route_decisions_current(
                decision_id, project_id, run_id, occurred_at, route_id, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event_row["event_id"],
                project_id,
                event_row["run_id"],
                event_row["occurred_at"],
                event_row.get("route_id") or payload.get("route_id", ""),
                json.dumps(payload),
            ),
        )

    db.conn.execute("DELETE FROM active_experiments_current WHERE project_id = ?", (project_id,))
    active = db.list_active_experiments(project_id)
    for experiment in active:
        db.conn.execute(
            """
            INSERT INTO active_experiments_current(
                experiment_id, project_id, route_id, conjecture_id, move, move_family,
                status, external_status, updated_at, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                experiment["experiment_id"],
                project_id,
                experiment.get("route_id"),
                experiment["conjecture_id"],
                experiment["move"],
                experiment.get("move_family") or experiment["move"],
                experiment["status"],
                experiment.get("external_status"),
                now,
                json.dumps(experiment),
            ),
        )

    db.conn.execute("DELETE FROM recent_results_current WHERE project_id = ?", (project_id,))
    for experiment in db.list_completed_experiments(project_id, limit=25):
        db.conn.execute(
            """
            INSERT INTO recent_results_current(
                experiment_id, project_id, route_id, conjecture_id, status,
                proof_outcome, blocker_type, new_signal_count, reused_signal_count,
                completed_at, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                experiment["experiment_id"],
                project_id,
                experiment.get("route_id"),
                experiment["conjecture_id"],
                experiment["status"],
                experiment.get("proof_outcome"),
                experiment.get("blocker_type"),
                int(experiment.get("new_signal_count", 0) or 0),
                int(experiment.get("reused_signal_count", 0) or 0),
                experiment.get("completed_at") or now,
                json.dumps(experiment),
            ),
        )

    db.conn.execute("DELETE FROM incidents_current WHERE project_id = ?", (project_id,))
    for incident in db.list_incidents(project_id, status="open"):
        route_id = incident.get("route_id")
        if not route_id and incident.get("experiment_id"):
            row = db.conn.execute(
                "SELECT route_id FROM experiments WHERE experiment_id = ?",
                (incident.get("experiment_id"),),
            ).fetchone()
            if row is not None:
                route_id = row[0]
        db.conn.execute(
            """
            INSERT INTO incidents_current(
                incident_id, project_id, experiment_id, route_id, incident_type, severity,
                status, detail, updated_at, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident["incident_id"],
                project_id,
                incident.get("experiment_id"),
                route_id,
                incident["incident_type"],
                incident["severity"],
                incident["status"],
                incident["detail"],
                incident.get("updated_at") or now,
                json.dumps(incident),
            ),
        )

    last_event = db.last_manager_event(project_id)
    health_payload: dict[str, Any] = {
        "source_mode": "live_db",
        "last_event_at": last_event.get("occurred_at") if last_event else "",
        "last_event_sequence": last_event.get("sequence_no") if last_event else 0,
        "last_projection_sequence": last_seq,
        "manager_status": "running" if last_event else "idle",
    }
    db.conn.execute(
        """
        INSERT INTO system_health_current(
            project_id, last_event_at, last_projection_at, manager_status,
            db_status, source_mode, payload_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id) DO UPDATE SET
            last_event_at = excluded.last_event_at,
            last_projection_at = excluded.last_projection_at,
            manager_status = excluded.manager_status,
            db_status = excluded.db_status,
            source_mode = excluded.source_mode,
            payload_json = excluded.payload_json,
            updated_at = excluded.updated_at
        """,
        (
            project_id,
            health_payload["last_event_at"],
            now,
            health_payload["manager_status"],
            "ok",
            "live_db",
            json.dumps(health_payload),
            now,
        ),
    )

    db.conn.commit()
