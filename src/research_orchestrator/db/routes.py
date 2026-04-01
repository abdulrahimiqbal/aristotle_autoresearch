"""Theorem routes, route evidence, operator commands, and projection checkpoints."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from research_orchestrator.db.utils import utcnow


class DatabaseRoutesMixin:
    """Mixin for theorem route operations."""

    def get_theorem_route_by_key(self, route_key: str) -> Optional[Dict[str, Any]]:
        """Get a theorem route by its unique key."""
        row = self.conn.execute(
            "SELECT * FROM theorem_routes WHERE route_key = ?",
            (route_key,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["summary"] = json.loads(item.get("summary_json", "{}"))
        return item

    def get_theorem_route(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Get a theorem route by ID."""
        row = self.conn.execute(
            "SELECT * FROM theorem_routes WHERE route_id = ?",
            (route_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["summary"] = json.loads(item.get("summary_json", "{}"))
        return item

    def list_theorem_routes(
        self, project_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List theorem routes for a project."""
        params: list[Any] = [project_id]
        query = "SELECT * FROM theorem_routes WHERE project_id = ?"
        if status is not None:
            query += " AND route_status = ?"
            params.append(status)
        query += " ORDER BY current_strength DESC, updated_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["summary"] = json.loads(item.get("summary_json", "{}"))
            results.append(item)
        return results

    def upsert_theorem_route(self, route: Dict[str, Any]) -> None:
        """Create or update a theorem route."""
        now = utcnow()
        self.conn.execute(
            """
            INSERT INTO theorem_routes(
                route_id, project_id, conjecture_id, theorem_family, route_key, route_stage,
                route_status, current_strength, recent_signal_velocity, blocker_pressure,
                novelty_score, reuse_score, transfer_score, last_selected_at, last_progress_at,
                operator_priority, summary_json, created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                COALESCE((SELECT created_at FROM theorem_routes WHERE route_id = ?), ?),
                ?
            )
            ON CONFLICT(route_key) DO UPDATE SET
                route_stage = excluded.route_stage,
                route_status = excluded.route_status,
                current_strength = excluded.current_strength,
                recent_signal_velocity = excluded.recent_signal_velocity,
                blocker_pressure = excluded.blocker_pressure,
                novelty_score = excluded.novelty_score,
                reuse_score = excluded.reuse_score,
                transfer_score = excluded.transfer_score,
                last_selected_at = excluded.last_selected_at,
                last_progress_at = excluded.last_progress_at,
                operator_priority = excluded.operator_priority,
                summary_json = excluded.summary_json,
                updated_at = excluded.updated_at
            """,
            (
                route["route_id"],
                route["project_id"],
                route.get("conjecture_id"),
                route.get("theorem_family", ""),
                route["route_key"],
                route.get("route_stage", "mapping"),
                route.get("route_status", "active"),
                float(route.get("current_strength", 0.0)),
                float(route.get("recent_signal_velocity", 0.0)),
                float(route.get("blocker_pressure", 0.0)),
                float(route.get("novelty_score", 0.0)),
                float(route.get("reuse_score", 0.0)),
                float(route.get("transfer_score", 0.0)),
                route.get("last_selected_at"),
                route.get("last_progress_at"),
                int(route.get("operator_priority", 0)),
                json.dumps(route.get("summary", {})),
                route["route_id"],
                now,
                now,
            ),
        )
        self.conn.commit()

    def insert_route_evidence(
        self,
        *,
        route_id: str,
        evidence_type: str,
        strength_delta: float,
        payload: Dict[str, Any],
        source_experiment_id: Optional[str] = None,
        source_object_id: Optional[str] = None,
    ) -> str:
        """Insert evidence for a route."""
        import uuid

        evidence_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO route_evidence(
                evidence_id, route_id, evidence_type, source_experiment_id, source_object_id,
                strength_delta, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                route_id,
                evidence_type,
                source_experiment_id,
                source_object_id,
                float(strength_delta),
                json.dumps(payload),
                utcnow(),
            ),
        )
        self.conn.commit()
        return evidence_id

    def list_route_evidence(self, route_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List evidence for a route."""
        rows = self.conn.execute(
            """
            SELECT * FROM route_evidence
            WHERE route_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (route_id, int(limit)),
        ).fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.get("payload_json", "{}"))
            results.append(item)
        return results

    def set_route_operator_priority(self, route_id: str, priority: int) -> None:
        """Set operator priority for a route."""
        self.conn.execute(
            "UPDATE theorem_routes SET operator_priority = ?, updated_at = ? WHERE route_id = ?",
            (int(priority), utcnow(), route_id),
        )
        self.conn.commit()

    def set_route_status(self, route_id: str, status: str) -> None:
        """Set status for a route."""
        self.conn.execute(
            "UPDATE theorem_routes SET route_status = ?, updated_at = ? WHERE route_id = ?",
            (status, utcnow(), route_id),
        )
        self.conn.commit()

    def append_route_note(self, route_id: str, note: str) -> None:
        """Append a note to a route's summary."""
        route = self.get_theorem_route(route_id)
        if route is None:
            return
        summary = route.get("summary", {})
        notes = summary.get("operator_notes", [])
        notes.append({"note": note, "created_at": utcnow()})
        summary["operator_notes"] = notes[-20:]
        self.conn.execute(
            "UPDATE theorem_routes SET summary_json = ?, updated_at = ? WHERE route_id = ?",
            (json.dumps(summary), utcnow(), route_id),
        )
        self.conn.commit()

    def create_operator_command(
        self,
        *,
        project_id: str,
        command_type: str,
        target_type: str,
        payload: Dict[str, Any],
        route_id: Optional[str] = None,
        target_id: Optional[str] = None,
        status: str = "pending",
    ) -> str:
        """Create an operator command."""
        import uuid

        command_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO operator_commands(
                command_id, project_id, route_id, command_type, target_type, target_id,
                payload_json, issued_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                command_id,
                project_id,
                route_id,
                command_type,
                target_type,
                target_id,
                json.dumps(payload),
                utcnow(),
                status,
            ),
        )
        self.conn.commit()
        return command_id

    def list_operator_commands(
        self, project_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List operator commands for a project."""
        params: list[Any] = [project_id]
        query = "SELECT * FROM operator_commands WHERE project_id = ?"
        if status is not None:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY issued_at ASC"
        rows = self.conn.execute(query, params).fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.get("payload_json", "{}"))
            results.append(item)
        return results

    def mark_operator_command_applied(
        self, command_id: str, *, status: str, details: Dict[str, Any]
    ) -> str:
        """Mark an operator command as applied."""
        import uuid

        result_id = str(uuid.uuid4())
        now = utcnow()
        self.conn.execute(
            "UPDATE operator_commands SET status = ? WHERE command_id = ?",
            (status, command_id),
        )
        self.conn.execute(
            """
            INSERT INTO operator_command_results(
                result_id, command_id, applied_at, status, details_json
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (result_id, command_id, now, status, json.dumps(details)),
        )
        self.conn.commit()
        return result_id

    def get_projection_checkpoint(self, projection_name: str) -> int:
        """Get the last sequence number for a projection."""
        row = self.conn.execute(
            "SELECT last_sequence_no FROM projection_checkpoints WHERE projection_name = ?",
            (projection_name,),
        ).fetchone()
        if row is None:
            return 0
        return int(row["last_sequence_no"])

    def update_projection_checkpoint(self, projection_name: str, sequence_no: int) -> None:
        """Update the checkpoint for a projection."""
        self.conn.execute(
            """
            INSERT INTO projection_checkpoints(projection_name, last_sequence_no, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(projection_name) DO UPDATE SET
                last_sequence_no = excluded.last_sequence_no,
                updated_at = excluded.updated_at
            """,
            (projection_name, int(sequence_no), utcnow()),
        )
        self.conn.commit()
