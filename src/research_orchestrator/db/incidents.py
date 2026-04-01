"""Incident management including detection, escalation, and expiration."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from research_orchestrator.db.utils import utcnow


class DatabaseIncidentsMixin:
    """Mixin for incident management operations."""

    def create_incident(
        self,
        *,
        project_id: str,
        incident_type: str,
        severity: str,
        detail: str,
        experiment_id: str = "",
        run_id: Optional[str] = None,
    ) -> str:
        """Create a new incident."""
        import uuid

        incident_id = str(uuid.uuid4())
        now = utcnow()
        self.conn.execute(
            """
            INSERT INTO incidents(incident_id, project_id, experiment_id, incident_type, severity, detail, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (incident_id, project_id, experiment_id, incident_type, severity, detail, "open", now, now),
        )
        self.conn.commit()
        return incident_id

    def ensure_open_incident(
        self,
        *,
        project_id: str,
        incident_type: str,
        severity: str,
        detail: str,
        experiment_id: str = "",
        run_id: Optional[str] = None,
    ) -> str:
        """Create an incident only if one of the same type isn't already open."""
        row = self.conn.execute(
            """
            SELECT incident_id FROM incidents
            WHERE project_id = ? AND incident_type = ? AND status = 'open'
            ORDER BY created_at DESC LIMIT 1
            """,
            (project_id, incident_type),
        ).fetchone()
        if row:
            return str(row["incident_id"])
        return self.create_incident(
            project_id=project_id,
            incident_type=incident_type,
            severity=severity,
            detail=detail,
            experiment_id=experiment_id,
            run_id=run_id,
        )

    def detect_stuck_runs(
        self,
        project_id: str,
        stale_run_timeout_seconds: int = 21600,
        stuck_run_timeout_seconds: int = 7200,
    ) -> List[Dict[str, Any]]:
        """Detect runs that appear stuck based on timeout thresholds."""
        from datetime import datetime, timezone
        from research_orchestrator.db.utils import parse_timestamp

        now = datetime.now(timezone.utc)
        stuck: List[Dict[str, Any]] = []
        for experiment in self.list_active_experiments(project_id):
            submitted_at = parse_timestamp(experiment.get("submitted_at")) or parse_timestamp(experiment.get("created_at"))
            last_synced_at = parse_timestamp(experiment.get("last_synced_at")) or submitted_at
            if submitted_at is None or last_synced_at is None:
                continue
            submitted_age = int((now - submitted_at).total_seconds())
            sync_age = int((now - last_synced_at).total_seconds())
            is_stuck = experiment["status"] == "planned" and submitted_age >= stuck_run_timeout_seconds
            is_stale = experiment["status"] in {"submitted", "in_progress"} and sync_age >= stale_run_timeout_seconds
            if not is_stuck and not is_stale:
                continue
            stuck.append(
                {
                    "experiment_id": experiment["experiment_id"],
                    "status": experiment["status"],
                    "submitted_age_seconds": submitted_age,
                    "sync_age_seconds": sync_age,
                    "external_id": experiment.get("external_id", ""),
                    "conjecture_id": experiment["conjecture_id"],
                    "move_family": experiment.get("move_family", experiment.get("move", "")),
                    "classification": "stale_remote" if is_stale else "planned_stuck",
                }
            )
        return stuck

    def enforce_retry_budget(
        self,
        project_id: str,
        max_attempts: int = 3,
        auto_escalate: bool = True,
    ) -> List[Dict[str, Any]]:
        """Enforce retry budget and optionally escalate exhausted experiments."""
        from research_orchestrator.db.utils import utcnow

        rows = self.conn.execute(
            """
            SELECT * FROM experiments
            WHERE project_id = ?
              AND status IN ('stalled', 'failed')
              AND COALESCE(attempt_count, 0) >= ?
              AND (external_status IS NULL OR external_status != 'killed')
            """,
            (project_id, max_attempts),
        ).fetchall()
        exhausted: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["decoded"] = self._decode_experiment_row(row)
            if auto_escalate:
                self.conn.execute(
                    "UPDATE experiments SET external_status = 'killed', completed_at = ? WHERE experiment_id = ?",
                    (utcnow(), row["experiment_id"]),
                )
            exhausted.append(item)
        if auto_escalate and exhausted:
            self.conn.commit()
        return exhausted

    def escalate_operational_incidents(
        self,
        project_id: str,
        *,
        repeated_failure_threshold: int,
        repeated_no_signal_threshold: int,
        stale_run_timeout_seconds: int,
        stuck_run_timeout_seconds: int,
        max_attempts_per_experiment: int,
    ) -> Dict[str, Any]:
        """Escalate operational incidents based on thresholds."""
        stuck_runs = self.detect_stuck_runs(
            project_id,
            stale_run_timeout_seconds=stale_run_timeout_seconds,
            stuck_run_timeout_seconds=stuck_run_timeout_seconds,
        )
        for item in stuck_runs:
            self.ensure_open_incident(
                project_id=project_id,
                experiment_id=item["experiment_id"],
                incident_type=f"stuck_run_{item['classification']}",
                severity="warning",
                detail=(
                    f"Experiment {item['experiment_id']} is {item['classification']} "
                    f"(submitted_age={item['submitted_age_seconds']}s, sync_age={item['sync_age_seconds']}s)."
                ),
            )

        exhausted = self.enforce_retry_budget(
            project_id,
            max_attempts=max_attempts_per_experiment,
        )

        repeated_failure_types = {
            "malformed": 0,
            "parser_validation": 0,
            "provider_failure": 0,
        }
        for experiment in self.list_completed_experiments(project_id, limit=25):
            proof_outcome = experiment.get("proof_outcome") or ""
            blocker_type = experiment.get("blocker_type") or ""
            if proof_outcome == "malformed" or blocker_type == "malformed":
                repeated_failure_types["malformed"] += 1
            if experiment.get("ingestion", {}).get("verification_record", {}).get("validation_issues"):
                repeated_failure_types["parser_validation"] += 1
            if blocker_type in {"dns_failure", "network_unavailable", "auth_failure", "unknown"}:
                repeated_failure_types["provider_failure"] += 1

        if repeated_failure_types["malformed"] >= repeated_failure_threshold:
            self.ensure_open_incident(
                project_id=project_id,
                incident_type="repeated_malformed_runs",
                severity="error",
                detail=f"Malformed run count reached {repeated_failure_types['malformed']} in recent completed experiments.",
            )
        if repeated_failure_types["parser_validation"] >= repeated_failure_threshold:
            self.ensure_open_incident(
                project_id=project_id,
                incident_type="repeated_parser_validation_failures",
                severity="warning",
                detail=f"Parser validation issues reached {repeated_failure_types['parser_validation']} in recent completed experiments.",
            )
        if repeated_failure_types["provider_failure"] >= repeated_failure_threshold:
            self.ensure_open_incident(
                project_id=project_id,
                incident_type="repeated_provider_failures",
                severity="warning",
                detail=f"Provider-side failures reached {repeated_failure_types['provider_failure']} in recent completed experiments.",
            )

        repeated_no_signal = [
            item for item in self.no_signal_branches(project_id, threshold=repeated_no_signal_threshold)
        ]
        if repeated_no_signal:
            sample = repeated_no_signal[:3]
            detail = f"Repeated no-signal threshold reached ({len(repeated_no_signal)} branches). Samples: " + ", ".join(
                f"{r.get('experiment_id', 'unknown')}" for r in sample
            )
            self.ensure_open_incident(
                project_id=project_id,
                incident_type="repeated_no_signal",
                severity="warning",
                detail=detail,
            )

        return {
            "stuck_runs": stuck_runs,
            "exhausted_retries": exhausted,
            "repeated_failure_types": repeated_failure_types,
            "repeated_no_signal": repeated_no_signal,
        }

    def expire_stale_active_experiments(self, project_id: str, max_age_seconds: int) -> int:
        """Expire experiments that have been active for too long."""
        import json
        from research_orchestrator.db.utils import parse_timestamp
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        expired = 0
        stale_sync_seconds = max_age_seconds / 2
        for experiment in self.list_active_experiments(project_id):
            submitted_at = parse_timestamp(experiment.get("submitted_at"))
            last_synced_at = parse_timestamp(experiment.get("last_synced_at"))
            if submitted_at is None or last_synced_at is None:
                continue
            submitted_age = (now - submitted_at).total_seconds()
            sync_age = (now - last_synced_at).total_seconds()
            if submitted_age <= max_age_seconds or sync_age <= stale_sync_seconds:
                continue

            detail = (
                f"Experiment {experiment['experiment_id']} (external_id={experiment.get('external_id') or 'n/a'}) "
                f"exceeded the stale active timeout after {int(submitted_age)}s without a fresh sync. "
                "Marking as failed for campaign recovery."
            )
            provider_result = {
                "status": "failed",
                "blocker_type": "unknown",
                "proof_outcome": "unknown",
                "signal_summary": "remote_status=EXPIRED; proof_outcome=unknown; blocker=unknown",
                "generated_lemmas": [],
                "proved_lemmas": [],
                "candidate_lemmas": [],
                "unresolved_goals": [],
                "blocked_on": [],
                "missing_assumptions": [],
                "artifact_inventory": [],
                "proof_trace_fragments": [],
                "counterexample_witnesses": [],
                "normalized_candidate_lemmas": [],
                "normalized_unresolved_goals": [],
                "new_signal_count": 0,
                "reused_signal_count": 0,
                "suspected_missing_assumptions": [],
                "notes": detail,
                "confidence": 0.1,
                "raw_stdout": "",
                "raw_stderr": "",
                "artifacts": [],
                "external_id": experiment.get("external_id") or "",
                "external_status": "EXPIRED",
                "metadata": {
                    "incident_type": "stale_active_timeout",
                    "incident_detail": detail,
                },
            }
            ingestion_json = {
                "proof_outcome": "unknown",
                "signal_summary": "remote_status=EXPIRED; proof_outcome=unknown; blocker=unknown",
                "candidate_lemmas": [],
                "normalized_candidate_lemmas": [],
                "unresolved_goals": [],
                "normalized_unresolved_goals": [],
                "blocked_on": [],
                "missing_assumptions": [],
                "artifact_inventory": [],
                "proof_trace_fragments": [],
                "counterexample_witnesses": [],
                "new_signal_count": 0,
                "reused_signal_count": 0,
            }
            self.conn.execute(
                """
                UPDATE experiments
                SET status = 'failed',
                    blocker_type = 'unknown',
                    proof_outcome = 'unknown',
                    signal_summary = ?,
                    external_status = 'EXPIRED',
                    outcome_json = ?,
                    ingestion_json = ?,
                    completed_at = ?,
                    last_synced_at = ?
                WHERE experiment_id = ?
                """,
                (
                    "remote_status=EXPIRED; proof_outcome=unknown; blocker=unknown",
                    json.dumps({"provider_result": provider_result}),
                    json.dumps(ingestion_json),
                    utcnow(),
                    utcnow(),
                    experiment["experiment_id"],
                ),
            )
            self.create_incident(
                project_id=project_id,
                experiment_id=experiment["experiment_id"],
                incident_type="stale_active_timeout",
                detail=detail,
                severity="warning",
            )
            expired += 1
        self.conn.commit()
        return expired

    def list_incidents(
        self, project_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List incidents for a project."""
        params: List[Any] = [project_id]
        query = "SELECT * FROM incidents WHERE project_id = ?"
        if status is not None:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY updated_at DESC, created_at DESC"
        return [dict(row) for row in self.conn.execute(query, params).fetchall()]
