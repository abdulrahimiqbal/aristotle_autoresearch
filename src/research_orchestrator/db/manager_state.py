"""Manager runs, candidate audits, interpretations, and bridge hypotheses."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from research_orchestrator.db.utils import utcnow


class DatabaseManagerStateMixin:
    """Mixin for manager state operations including runs, audits, and interpretations."""

    def save_manager_run(
        self,
        project_id: str,
        provider: str,
        policy_path: str,
        jobs_synced: int,
        jobs_submitted: int,
        active_before: int,
        active_after: int,
        report_path: Optional[str],
        snapshot_path: Optional[str],
        summary: Dict[str, Any],
        run_id: Optional[str] = None,
    ) -> str:
        """Save a manager run record."""
        import uuid

        run_id = run_id or str(uuid.uuid4())
        now = utcnow()
        self.conn.execute(
            """
            INSERT INTO manager_runs(
                run_id, project_id, provider, policy_path, jobs_synced, jobs_submitted,
                active_before, active_after, report_path, snapshot_path, summary_json, created_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                project_id,
                provider,
                policy_path,
                jobs_synced,
                jobs_submitted,
                active_before,
                active_after,
                report_path,
                snapshot_path,
                json.dumps(summary),
                now,
                now,
            ),
        )
        self.conn.commit()
        return run_id

    def save_manager_candidate_audits(
        self,
        run_id: str,
        project_id: str,
        rows: List[Dict[str, Any]],
    ) -> None:
        """Save candidate audit records for a manager run."""
        import uuid

        for item in rows:
            self.conn.execute(
                """
                INSERT INTO manager_candidate_audits(
                    audit_id, run_id, project_id, experiment_id, conjecture_id,
                    rank_position, selected, selection_reason, policy_score,
                    score_breakdown_json, candidate_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    run_id,
                    project_id,
                    item["experiment_id"],
                    item["conjecture_id"],
                    int(item["rank_position"]),
                    1 if item.get("selected") else 0,
                    item.get("selection_reason", ""),
                    float(item.get("policy_score", 0.0)),
                    json.dumps(item.get("score_breakdown", {})),
                    json.dumps(item.get("candidate", {})),
                    utcnow(),
                ),
            )
        self.conn.commit()

    def list_manager_candidate_audits(self, run_id: str) -> List[Dict[str, Any]]:
        """List candidate audits for a manager run."""
        rows = self.conn.execute(
            """
            SELECT * FROM manager_candidate_audits
            WHERE run_id = ?
            ORDER BY rank_position ASC, created_at ASC
            """,
            (run_id,),
        ).fetchall()
        return [self._decode_manager_candidate_audit(row) for row in rows]

    def emit_manager_event(
        self,
        *,
        project_id: str,
        run_id: str,
        event_type: str,
        source_component: str,
        payload: Dict[str, Any],
        experiment_id: Optional[str] = None,
        route_id: Optional[str] = None,
        visibility: str = "public",
        occurred_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Emit a manager event to the event log."""
        import uuid

        now = occurred_at or utcnow()
        event_id = str(uuid.uuid4())
        with self.transaction(immediate=True):
            row = self.conn.execute(
                "SELECT COALESCE(MAX(sequence_no), 0) FROM manager_events"
            ).fetchone()
            next_seq = int(row[0]) + 1 if row is not None else 1
            self.conn.execute(
                """
                INSERT INTO manager_events(
                    event_id, sequence_no, occurred_at, project_id, run_id, experiment_id,
                    route_id, event_type, source_component, visibility, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    next_seq,
                    now,
                    project_id,
                    run_id,
                    experiment_id,
                    route_id,
                    event_type,
                    source_component,
                    visibility,
                    json.dumps(payload),
                ),
            )
        return {
            "event_id": event_id,
            "sequence_no": next_seq,
            "occurred_at": now,
            "project_id": project_id,
            "run_id": run_id,
            "experiment_id": experiment_id,
            "route_id": route_id,
            "event_type": event_type,
            "source_component": source_component,
            "visibility": visibility,
            "payload": payload,
        }

    def list_manager_events(
        self,
        project_id: str,
        *,
        since_sequence: Optional[int] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """List manager events for a project."""
        params: list[Any] = [project_id]
        query = "SELECT * FROM manager_events WHERE project_id = ?"
        if since_sequence is not None:
            query += " AND sequence_no > ?"
            params.append(int(since_sequence))
        query += " ORDER BY sequence_no ASC LIMIT ?"
        params.append(int(limit))
        rows = self.conn.execute(query, params).fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.get("payload_json", "{}"))
            results.append(item)
        return results

    def last_manager_event(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get the last manager event for a project."""
        row = self.conn.execute(
            "SELECT * FROM manager_events WHERE project_id = ? ORDER BY sequence_no DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["payload"] = json.loads(item.get("payload_json", "{}"))
        return item

    def list_manager_runs(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List manager runs for a project."""
        rows = self.conn.execute(
            """
            SELECT * FROM manager_runs
            WHERE project_id = ?
            ORDER BY completed_at DESC, created_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
        return [self._decode_manager_run_row(row) for row in rows]

    def latest_manager_run(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest manager run for a project."""
        row = self.conn.execute(
            """
            SELECT * FROM manager_runs
            WHERE project_id = ?
            ORDER BY completed_at DESC, created_at DESC
            LIMIT 1
            """,
            (project_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["summary"] = json.loads(item["summary_json"])
        return item

    def save_campaign_health_snapshot(
        self, run_id: str, project_id: str, health: Dict[str, Any]
    ) -> None:
        """Save a campaign health snapshot."""
        import uuid

        self.conn.execute(
            """
            INSERT INTO campaign_health_snapshots(snapshot_id, run_id, project_id, health_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), run_id, project_id, json.dumps(health), utcnow()),
        )
        self.conn.commit()

    def latest_campaign_health_snapshot(
        self, project_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get the latest campaign health snapshot."""
        row = self.conn.execute(
            """
            SELECT * FROM campaign_health_snapshots
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (project_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["health"] = json.loads(item["health_json"])
        return item

    def save_campaign_interpretation(
        self,
        project_id: str,
        prompt_version: str,
        model_version: str,
        raw_response: str,
        parsed: Dict[str, Any],
        validation_status: str,
        run_id: str = "",
    ) -> str:
        """Save a campaign interpretation."""
        import uuid

        interpretation_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO campaign_interpretations(
                interpretation_id, project_id, run_id, prompt_version, model_version,
                raw_response, parsed_json, validation_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                interpretation_id,
                project_id,
                run_id,
                prompt_version,
                model_version,
                raw_response,
                json.dumps(parsed),
                validation_status,
                utcnow(),
            ),
        )
        self.conn.commit()
        return interpretation_id

    def latest_campaign_interpretation(
        self, project_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get the latest campaign interpretation."""
        row = self.conn.execute(
            """
            SELECT * FROM campaign_interpretations
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (project_id,),
        ).fetchone()
        return self._decode_interpretation_row(row) if row else None

    def list_campaign_interpretations(
        self, project_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List campaign interpretations."""
        rows = self.conn.execute(
            """
            SELECT * FROM campaign_interpretations
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
        return [self._decode_interpretation_row(row) for row in rows]

    def save_bridge_hypotheses(
        self,
        project_id: str,
        hypotheses: List[Dict[str, Any]],
        run_id: str = "",
    ) -> None:
        """Save bridge hypotheses."""
        import uuid

        for item in hypotheses:
            self.conn.execute(
                """
                INSERT INTO bridge_hypotheses(
                    bridge_id, project_id, run_id, source_conjecture_id, target_conjecture_id,
                    suggested_move_family, confidence, hypothesis_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    project_id,
                    run_id,
                    item.get("source_conjecture_id", ""),
                    item.get("target_conjecture_id", ""),
                    item.get("suggested_move_family", "transfer_reformulation"),
                    float(item.get("confidence", 0.0)),
                    json.dumps(item),
                    utcnow(),
                ),
            )
        self.conn.commit()

    def list_bridge_hypotheses(
        self, project_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List bridge hypotheses."""
        rows = self.conn.execute(
            """
            SELECT * FROM bridge_hypotheses
            WHERE project_id = ?
            ORDER BY confidence DESC, created_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
        return [self._decode_bridge_row(row) for row in rows]

    def add_audit_event(
        self,
        project_id: str,
        event_type: str,
        detail: Dict[str, Any],
        experiment_id: str = "",
    ) -> None:
        """Add an audit event."""
        import uuid

        self.conn.execute(
            """
            INSERT INTO audit_events(event_id, project_id, experiment_id, event_type, detail_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                project_id,
                experiment_id,
                event_type,
                json.dumps(detail),
                utcnow(),
            ),
        )
        self.conn.commit()

    def list_audit_events(
        self, project_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List audit events for a project."""
        rows = self.conn.execute(
            """
            SELECT * FROM audit_events
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["detail"] = json.loads(item["detail_json"])
            results.append(item)
        return results
