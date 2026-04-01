"""Campaign health, summaries, and recurring structure queries."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from research_orchestrator.db.utils import utcnow, current_version_bundle


class DatabaseHealthMixin:
    """Mixin for campaign health and summary operations."""

    def recurring_lemmas(self, minimum_reuse: int = 2) -> List[Dict[str, Any]]:
        """Get lemmas that have been reused at least minimum_reuse times."""
        rows = self.conn.execute(
            """
            SELECT l.lemma_id, l.representative_statement, l.normalized_statement, l.reuse_count,
                   GROUP_CONCAT(DISTINCT lo.conjecture_id) AS conjecture_ids
            FROM lemmas l
            JOIN lemma_occurrences lo ON lo.lemma_id = l.lemma_id
            JOIN conjectures c ON c.conjecture_id = lo.conjecture_id
            WHERE l.reuse_count >= ?
            GROUP BY l.lemma_id, l.representative_statement, l.normalized_statement, l.reuse_count
            ORDER BY reuse_count DESC, representative_statement ASC
            """,
            (minimum_reuse,),
        ).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["conjecture_ids"] = item["conjecture_ids"].split(",") if item.get("conjecture_ids") else []
            items.append(item)
        return items

    def assumption_sensitivity(self, project_id: str) -> List[Dict[str, Any]]:
        """Get assumption sensitivity scores for a project."""
        rows = self.conn.execute(
            """
            SELECT assumption_name, ROUND(AVG(sensitivity_score), 3) AS avg_sensitivity, COUNT(*) AS observations
            FROM assumption_observations
            WHERE project_id = ?
            GROUP BY assumption_name
            ORDER BY avg_sensitivity DESC, observations DESC, assumption_name ASC
            """,
            (project_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def recurring_subgoals(
        self, project_id: str, minimum_reuse: int = 2
    ) -> List[Dict[str, Any]]:
        """Get recurring subgoals for a project."""
        rows = self.conn.execute(
            """
            SELECT so.canonical_text AS statement, so.occurrence_count AS observations
            FROM semantic_objects so
            WHERE so.project_id = ? AND so.kind = 'goal' AND so.occurrence_count >= ?
            ORDER BY so.occurrence_count DESC, so.canonical_text ASC
            """,
            (project_id, minimum_reuse),
        ).fetchall()
        return [dict(row) for row in rows]

    def recurring_proof_traces(
        self, project_id: str, minimum_reuse: int = 2
    ) -> List[Dict[str, Any]]:
        """Get recurring proof trace fragments for a project."""
        rows = self.conn.execute(
            """
            SELECT so.canonical_text AS fragment, so.occurrence_count AS observations
            FROM semantic_objects so
            WHERE so.project_id = ? AND so.kind = 'proof_trace' AND so.occurrence_count >= ?
            ORDER BY so.occurrence_count DESC, so.canonical_text ASC
            """,
            (project_id, minimum_reuse),
        ).fetchall()
        return [dict(row) for row in rows]

    def counterexample_summary(self, project_id: str) -> List[Dict[str, Any]]:
        """Get counterexample witnesses for a project."""
        rows = self.conn.execute(
            """
            SELECT so.canonical_text AS witness, so.occurrence_count AS observations
            FROM semantic_objects so
            WHERE so.project_id = ? AND so.kind = 'counterexample'
            ORDER BY so.occurrence_count DESC, so.canonical_text ASC
            """,
            (project_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def recurring_blockers_by_move(
        self, project_id: str, minimum_reuse: int = 2
    ) -> List[Dict[str, Any]]:
        """Get recurring blockers grouped by move."""
        rows = self.conn.execute(
            """
            SELECT e.move, b.blocker_type, b.proof_outcome, COUNT(*) AS observations
            FROM blocker_observations b
            JOIN experiments e ON e.experiment_id = b.experiment_id
            WHERE b.project_id = ?
            GROUP BY e.move, b.blocker_type, b.proof_outcome
            HAVING COUNT(*) >= ?
            ORDER BY observations DESC, e.move ASC, b.blocker_type ASC
            """,
            (project_id, minimum_reuse),
        ).fetchall()
        return [dict(row) for row in rows]

    def no_signal_branches(
        self, project_id: str, threshold: int = 2
    ) -> List[Dict[str, Any]]:
        """Get conjecture/move combinations that have produced no signal."""
        rows = self.conn.execute(
            """
            SELECT conjecture_id, move, COUNT(*) AS observations
            FROM experiments
            WHERE project_id = ?
              AND COALESCE(new_signal_count, 0) = 0
              AND status IN ('stalled', 'failed')
              AND (
                proof_outcome = 'unknown'
                OR (
                  proof_outcome = 'disproved'
                  AND NOT EXISTS (
                    SELECT 1
                    FROM lemma_occurrences lo
                    WHERE lo.experiment_id = experiments.experiment_id
                  )
                  AND NOT EXISTS (
                    SELECT 1
                    FROM extracted_subgoals es
                    WHERE es.experiment_id = experiments.experiment_id
                  )
                  AND NOT EXISTS (
                    SELECT 1
                    FROM proof_trace_observations pto
                    WHERE pto.experiment_id = experiments.experiment_id
                  )
                  AND NOT EXISTS (
                    SELECT 1
                    FROM counterexample_observations co
                    WHERE co.experiment_id = experiments.experiment_id
                  )
                )
              )
            GROUP BY conjecture_id, move
            HAVING COUNT(*) >= ?
            ORDER BY observations DESC, conjecture_id ASC, move ASC
            """,
            (project_id, threshold),
        ).fetchall()
        return [dict(row) for row in rows]

    def blocker_summary(self, project_id: str) -> List[Dict[str, Any]]:
        """Get blocker summary from semantic objects."""
        rows = self.conn.execute(
            """
            SELECT so.canonical_text AS blocker_type, 'semantic' AS proof_outcome, so.occurrence_count AS observations
            FROM semantic_objects so
            WHERE so.project_id = ? AND so.kind = 'blocker'
            ORDER BY so.occurrence_count DESC, so.canonical_text ASC
            """,
            (project_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def version_drift_summary(self, project_id: str) -> Dict[str, Any]:
        """Compare versions in manifests to current versions."""
        current = current_version_bundle()
        drifts: Dict[str, Dict[str, int]] = {}
        manifests = self.conn.execute(
            """
            SELECT * FROM experiment_manifests
            WHERE project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,),
        ).fetchall()
        for row in manifests:
            item = self._decode_manifest_row(row)
            versions = item["manifest"].get("versions", {})
            for key, current_value in current.items():
                manifest_value = versions.get(key)
                if not manifest_value or manifest_value == current_value:
                    continue
                bucket = drifts.setdefault(key, {})
                bucket[manifest_value] = bucket.get(manifest_value, 0) + 1
        return {
            "current": current,
            "mismatches": drifts,
        }

    def campaign_health(
        self, project_id: str, frontier: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive campaign health metrics."""
        summary = self.project_summary(project_id)
        completed = self.list_completed_experiments(project_id)
        active = self.list_active_experiments(project_id)
        incidents = self.list_incidents(project_id, status="open")
        total_completed = len(completed)
        structured_successes = sum(
            1
            for item in completed
            if item.get("ingestion", {}).get("verification_record")
        )
        total_new = sum(item.get("new_signal_count") or 0 for item in completed)
        total_reused = sum(item.get("reused_signal_count") or 0 for item in completed)
        transfer_runs = sum(
            1
            for item in completed
            if item.get("move_family") == "transfer_reformulation"
            or (item.get("candidate_metadata", {}).get("transfer_score") or 0) > 0
        )
        frontier = frontier or []
        reusable_structure_runs = sum(
            1
            for item in completed
            if (item.get("candidate_metadata", {}).get("reuse_potential") or 0) >= 1.0
            or item.get("move_family")
            in {"legacy.promote_lemma", "decompose_subclaim", "invariant_mining"}
        )
        obstruction_runs = sum(
            1
            for item in completed
            if (item.get("candidate_metadata", {}).get("obstruction_targeting") or 0) >= 1.0
            or item.get("move_family")
            in {"extremal_case", "adversarial_counterexample", "witness_minimization"}
        )
        high_priority_frontier = sum(
            1 for item in frontier if (item.get("campaign_priority") or 0) > 0
        )
        move_families = {item.get("move_family", item["move"]) for item in completed}
        duplicate_pressure = sum(
            1 for item in frontier if item.get("duplicate_active_signature")
        )
        frontier_move_families = {item.get("move_family", item["move"]) for item in frontier}
        incident_by_type: Dict[str, int] = {}
        incident_by_severity: Dict[str, int] = {}
        for incident in incidents:
            incident_by_type[incident["incident_type"]] = incident_by_type.get(
                incident["incident_type"], 0
            ) + 1
            incident_by_severity[incident["severity"]] = incident_by_severity.get(
                incident["severity"], 0
            ) + 1
        no_signal = self.no_signal_branches(project_id)
        max_no_signal_streak = max((item["observations"] for item in no_signal), default=0)
        stuck_runs = self.detect_stuck_runs(
            project_id,
            stale_run_timeout_seconds=6 * 3600,
            stuck_run_timeout_seconds=2 * 3600,
        )
        spec = self.get_campaign_spec(project_id)
        retry_exhausted = [
            item["experiment_id"]
            for item in self.list_experiments(project_id)
            if (item.get("attempt_count") or 0)
            >= spec.budget_policy.max_attempts_per_experiment
        ] if spec is not None else []

        return {
            "project_id": project_id,
            "counts": {
                "active": len(active),
                "pending": summary.get("pending", 0),
                "running": sum(1 for item in active if item["status"] == "in_progress"),
                "completed": total_completed,
                "failed": summary.get("failed", 0),
                "succeeded": summary.get("solved", 0),
                "stalled": summary.get("stalled", 0),
            },
            "incidents": {
                "open_total": len(incidents),
                "by_type": incident_by_type,
                "by_severity": incident_by_severity,
            },
            "signals": {
                "repeated_no_signal_streak": max_no_signal_streak,
                "duplicate_frontier_pressure": duplicate_pressure,
                "structured_ingestion_success_rate": round(
                    structured_successes / total_completed, 3
                )
                if total_completed
                else 0.0,
                "semantic_reuse_rate": round(
                    total_reused / max(1, total_reused + total_new), 3
                ),
                "transfer_usage_rate": round(transfer_runs / total_completed, 3)
                if total_completed
                else 0.0,
                "reusable_structure_rate": round(reusable_structure_runs / total_completed, 3)
                if total_completed
                else 0.0,
                "obstruction_discovery_rate": round(obstruction_runs / total_completed, 3)
                if total_completed
                else 0.0,
                "high_priority_frontier_share": round(
                    high_priority_frontier / max(1, len(frontier)), 3
                )
                if frontier
                else 0.0,
                "candidate_move_family_diversity": len(frontier_move_families),
                "completed_move_family_diversity": len(move_families),
            },
            "runtime_controls": {
                "stuck_runs": stuck_runs,
                "retry_exhausted": retry_exhausted,
            },
            "no_signal_branches": no_signal,
            "version_drift": self.version_drift_summary(project_id),
        }

    def project_summary(self, project_id: str) -> Dict[str, Any]:
        """Get a comprehensive project summary."""
        experiments = self.list_experiments(project_id)
        solved = sum(1 for item in experiments if item["status"] == "succeeded")
        stalled = sum(1 for item in experiments if item["status"] == "stalled")
        failed = sum(1 for item in experiments if item["status"] == "failed")
        pending = sum(
            1 for item in experiments if item["status"] in {"planned", "submitted", "in_progress"}
        )
        spec = self.get_campaign_spec(project_id)
        discovery_nodes = self.list_discovery_nodes(project_id)
        open_questions = self.list_discovery_questions(project_id, status="open")
        incidents = self.list_incidents(project_id, status="open")
        return {
            "project_id": project_id,
            "campaign_title": spec.title if spec is not None else self.get_charter(project_id).title,
            "campaign_version": spec.version if spec is not None else "",
            "num_experiments": len(experiments),
            "solved": solved,
            "stalled": stalled,
            "failed": failed,
            "pending": pending,
            "active_by_external_status": self.active_experiments_by_external_status(project_id),
            "recurring_lemmas": self.recurring_lemmas(),
            "recurring_subgoals": self.recurring_subgoals(project_id),
            "recurring_proof_traces": self.recurring_proof_traces(project_id),
            "blocker_summary": self.blocker_summary(project_id),
            "blockers_by_move": self.recurring_blockers_by_move(project_id),
            "counterexample_summary": self.counterexample_summary(project_id),
            "no_signal_branches": self.no_signal_branches(project_id),
            "assumption_sensitivity": self.assumption_sensitivity(project_id),
            "open_discovery_questions": open_questions,
            "bridge_hypotheses": self.list_bridge_hypotheses(project_id, limit=10),
            "discovery_graph_counts": {
                "nodes": len(discovery_nodes),
                "edges": len(self.list_discovery_edges(project_id)),
                "verified_like_nodes": len(
                    [
                        item
                        for item in discovery_nodes
                        if item["node_type"]
                        in {
                            "verified_lemma",
                            "recurring_subgoal",
                            "assumption_boundary",
                            "counterexample_witness",
                        }
                    ]
                ),
            },
            "open_incidents": incidents,
        }
