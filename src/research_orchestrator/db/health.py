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

    def convergence_metrics(
        self, project_id: str, frontier: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Calculate convergence metrics that measure progress toward proof.

        Returns metrics focused on epistemic progress rather than activity counts.
        """
        from research_orchestrator.db.utils import utcnow

        summary = self.project_summary(project_id)
        completed = self.list_completed_experiments(project_id)
        experiments = self.list_experiments(project_id)
        discovery_nodes = self.list_discovery_nodes(project_id)
        discovery_edges = self.list_discovery_edges(project_id)
        bridge_hypotheses = self.list_bridge_hypotheses(project_id)

        # Get obligation data from experiments
        proved_lemmas = set()
        total_obligations = 0
        resolved_obligations = 0
        recent_proofs = 0
        recent_window_hours = 24

        for exp in completed:
            outcome = exp.get("outcome", {})
            provider_result = outcome.get("provider_result", {})
            for lemma in provider_result.get("proved_lemmas", []):
                proved_lemmas.add(lemma)

        # Count obligations from unresolved goals across experiments
        open_obligations = set()
        for exp in experiments:
            outcome = exp.get("outcome", {})
            provider_result = outcome.get("provider_result", {})
            for goal in provider_result.get("unresolved_goals", []):
                open_obligations.add(goal)
                total_obligations += 1
            for blocked in provider_result.get("blocked_on", []):
                open_obligations.add(blocked)

        resolved_obligations = len(proved_lemmas)
        total_obligations = max(len(open_obligations) + resolved_obligations, 1)
        obligation_resolution_rate = resolved_obligations / total_obligations

        # Knowledge graph density
        node_count = len(discovery_nodes)
        edge_count = len(discovery_edges)
        knowledge_graph_density = edge_count / max(node_count, 1)

        # Calculate proof velocity (proved lemmas per hour from recent completions)
        now = utcnow()
        recent_proofs_count = 0
        recent_completion_count = 0
        for exp in completed:
            completed_at = exp.get("completed_at")
            if completed_at:
                try:
                    from datetime import datetime
                    if isinstance(completed_at, str):
                        completed_time = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    else:
                        completed_time = completed_at
                    hours_ago = (now - completed_time).total_seconds() / 3600
                    if hours_ago <= recent_window_hours:
                        recent_completion_count += 1
                        outcome = exp.get("outcome", {})
                        provider_result = outcome.get("provider_result", {})
                        recent_proofs_count += len(provider_result.get("proved_lemmas", []))
                except (ValueError, TypeError):
                    pass

        proof_velocity = recent_proofs_count / max(recent_window_hours, 1)

        # Obligation closure rate (resolved per total)
        obligation_closure_rate = obligation_resolution_rate

        # Critical path length estimation (longest chain of dependent obligations)
        critical_path_length = len(open_obligations)

        # Estimated remaining work (rough heuristic based on open obligations)
        estimated_remaining_work = len(open_obligations)

        # Calculate convergence score (0-1, higher = closer to proof)
        # Components:
        # 1. Proved lemmas ratio (30% weight)
        # 2. Obligation resolution rate (30% weight)
        # 3. Proof velocity factor (20% weight)
        # 4. Critical path progress (20% weight)

        proved_ratio = len(proved_lemmas) / max(total_obligations, 1)
        velocity_factor = min(proof_velocity / 0.5, 1.0)  # Normalize: 0.5/hr = full score
        critical_path_progress = resolved_obligations / max(resolved_obligations + critical_path_length, 1)

        convergence_score = (
            0.3 * proved_ratio +
            0.3 * obligation_resolution_rate +
            0.2 * velocity_factor +
            0.2 * critical_path_progress
        )

        # Determine trend by comparing recent progress to historical average
        total_completed = len(completed)
        historical_rate = resolved_obligations / max(total_completed, 1) if total_completed > 0 else 0
        recent_rate = recent_proofs_count / max(recent_completion_count, 1) if recent_completion_count > 0 else 0

        if recent_completion_count == 0:
            trend = "stalled"
        elif recent_rate > historical_rate * 1.2:
            trend = "improving"
        elif recent_rate < historical_rate * 0.8:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "project_id": project_id,
            "convergence_score": round(convergence_score, 3),
            "epistemic_progress": {
                "proved_lemma_count": len(proved_lemmas),
                "obligation_resolution_rate": round(obligation_resolution_rate, 3),
                "knowledge_graph_density": round(knowledge_graph_density, 3),
            },
            "trend": trend,
            "distance_to_proof": {
                "open_obligations_count": len(open_obligations),
                "critical_path_length": critical_path_length,
                "estimated_remaining_work": estimated_remaining_work,
            },
            "key_indicators": {
                "proof_velocity": round(proof_velocity, 3),
                "obligation_closure_rate": round(obligation_closure_rate, 3),
                "bridge_hypothesis_count": len(bridge_hypotheses),
            },
            "snapshot_at": now.isoformat(),
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
