"""Operator commands and projection checkpoints (routes removed per Phase 1.2)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from research_orchestrator.db.utils import utcnow


class DatabaseRoutesMixin:
    """Mixin for operator command operations (route operations removed)."""

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
