"""Export operations for creating readable state bundles."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict


class DatabaseExportMixin:
    """Mixin for export operations."""

    def export_readable_state(
        self, project_id: str, output_dir: str | Path
    ) -> Dict[str, str]:
        """Export campaign state to readable files (JSON and CSV)."""
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)

        payloads = {
            "campaign_summary.json": self.project_summary(project_id),
            "conjecture_scoreboard.json": self.query_view("conjecture_scoreboard", project_id=project_id),
            "recurring_structures.json": sorted(
                self.query_view("recurring_structure_summary", project_id=project_id),
                key=lambda item: (
                    -int(item.get("observations", 0)),
                    item.get("structure_kind", ""),
                    item.get("summary_text", ""),
                ),
            ),
            "active_queue.json": self.query_view("active_queue_summary", project_id=project_id),
            "incidents.json": self.query_view("incident_summary", project_id=project_id),
            "bridge_hypotheses.json": self.list_bridge_hypotheses(project_id),
            "campaign_interpretations.json": self.list_campaign_interpretations(project_id),
        }

        written: Dict[str, str] = {}
        for filename, payload in payloads.items():
            path = destination / filename
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            written[filename] = str(path)

        experiments_csv = destination / "experiments.csv"
        experiment_rows = self.query_view("readable_experiments", project_id=project_id)
        fieldnames = [
            "experiment_id",
            "project_id",
            "conjecture_id",
            "phase",
            "move",
            "move_family",
            "status",
            "proof_outcome",
            "blocker_type",
            "objective",
            "expected_signal",
            "modification_json",
            "new_signal_count",
            "reused_signal_count",
            "boundary_summary",
            "motif_id",
            "motif_signature",
            "campaign_priority",
            "signal_support",
            "discovery_question_id",
            "created_at",
            "completed_at",
        ]
        with experiments_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in experiment_rows:
                writer.writerow({key: row.get(key, "") for key in fieldnames})
        written["experiments.csv"] = str(experiments_csv)

        # Export manager candidate audits for dashboard
        audits = self.conn.execute(
            """
            SELECT audit_id, run_id, experiment_id, conjecture_id, rank_position,
                   selected, selection_reason, policy_score, score_breakdown_json,
                   candidate_json, created_at
            FROM manager_candidate_audits
            WHERE project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,),
        ).fetchall()

        audits_data = []
        for audit in audits:
            try:
                score_breakdown = json.loads(audit["score_breakdown_json"] or "{}")
            except json.JSONDecodeError:
                score_breakdown = {}
            try:
                candidate = json.loads(audit["candidate_json"] or "{}")
            except json.JSONDecodeError:
                candidate = {}

            audits_data.append({
                "audit_id": audit["audit_id"],
                "run_id": audit["run_id"],
                "experiment_id": audit["experiment_id"],
                "conjecture_id": audit["conjecture_id"],
                "rank_position": audit["rank_position"],
                "selected": bool(audit["selected"]),
                "selection_reason": audit["selection_reason"],
                "policy_score": audit["policy_score"],
                "score_breakdown": score_breakdown,
                "candidate": candidate,
                "created_at": audit["created_at"],
            })

        audits_path = destination / "manager_candidate_audits.json"
        audits_path.write_text(json.dumps(audits_data, indent=2), encoding="utf-8")
        written["manager_candidate_audits.json"] = str(audits_path)

        return written
