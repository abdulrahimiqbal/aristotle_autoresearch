"""Experiment lifecycle, manifests, results, and related operations."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
from typing import Any, Dict, Iterable, List, Optional

from research_orchestrator.db.utils import utcnow, best_effort_git_branch, current_version_bundle
from research_orchestrator.schema_versions import (
    VERIFICATION_SCHEMA_VERSION,
    VERIFICATION_PARSER_VERSION,
    SEMANTIC_MEMORY_VERSION,
    EVALUATOR_VERSION,
)
from research_orchestrator.types import ProviderResult


class DatabaseExperimentsMixin:
    """Mixin for experiment lifecycle and result operations."""

    def build_experiment_manifest(
        self,
        brief: Dict[str, Any],
        *,
        snapshot_kind: str,
        provider_name: str = "",
        result: Optional[ProviderResult] = None,
        policy_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build an experiment manifest for recording."""
        conjecture = self.get_conjecture(brief["conjecture_id"])
        versions = current_version_bundle()
        result_versions = {
            "parser_version": result.verification_record.run.parser_version if result and result.verification_record else versions["parser_version"],
            "evaluator_version": result.verification_record.run.evaluator_version if result and result.verification_record else versions["evaluator_version"],
            "semantic_memory_version": result.verification_record.run.semantic_memory_version if result and result.verification_record else versions["semantic_memory_version"],
            "verification_schema_version": result.verification_record.schema_version if result and result.verification_record else versions["verification_schema_version"],
        }
        workspace_dir = str(Path(brief["workspace_dir"]).resolve())
        artifact_inventory = result.artifact_inventory if result is not None else []
        provider_metadata = {
            "provider_name": provider_name or (result.metadata.get("provider_name", "") if result is not None else ""),
            "external_id": result.external_id if result is not None else brief.get("external_id", ""),
            "external_status": result.external_status if result is not None else brief.get("external_status", ""),
            "metadata": result.metadata if result is not None else {},
        }
        manifest = {
            "manifest_version": "1.0",
            "experiment_id": brief["experiment_id"],
            "project_id": brief["project_id"],
            "conjecture_id": brief["conjecture_id"],
            "campaign_id": brief["project_id"],
            "snapshot_kind": snapshot_kind,
            "phase": brief["phase"],
            "move": brief["move"],
            "move_family": brief.get("move_family", brief["move"]),
            "move_family_version": brief.get("move_family_version", "v1"),
            "move_title": brief.get("move_title", ""),
            "move_parameters": brief["modification"],
            "theorem_family_id": brief.get("theorem_family_id") or conjecture.theorem_family_id or conjecture.domain,
            "candidate_metadata": brief.get("candidate_metadata", {}),
            "ranking_rationale": brief.get("rationale", ""),
            "discovery_question_id": brief.get("discovery_question_id", ""),
            "workspace": {
                "workspace_dir": workspace_dir,
                "lean_file": str(Path(brief["lean_file"]).resolve()),
                "workspace_parent": str(Path(workspace_dir).parent),
                "git_branch": best_effort_git_branch(workspace_dir),
            },
            "provider": provider_metadata,
            "versions": {
                **versions,
                **result_versions,
                "move_family_version": brief.get("move_family_version", "v1"),
            },
            "prompts": {
                "prompt_version": versions["prompt_version"],
                "manager_prompt_version": versions["prompt_version"],
                "worker_prompt_version": versions["prompt_version"],
            },
            "environment": {
                "db_path": self.path,
                "cwd": str(Path.cwd()),
            },
            "artifacts": artifact_inventory,
            "provenance": {
                "result_artifacts": list(result.artifacts) if result is not None else [],
                "policy_context": policy_context or {},
            },
            "created_at": utcnow(),
        }
        if result is not None:
            manifest["result"] = {
                "status": result.status,
                "proof_outcome": result.proof_outcome,
                "blocker_type": result.blocker_type,
                "signal_summary": result.signal_summary,
                "new_signal_count": result.new_signal_count,
                "reused_signal_count": result.reused_signal_count,
            }
        return manifest

    def record_experiment_manifest(
        self,
        experiment_id: str,
        project_id: str,
        snapshot_kind: str,
        manifest: Dict[str, Any],
    ) -> None:
        """Record an experiment manifest snapshot."""
        import uuid

        from research_orchestrator.schema_versions import (
            MANAGER_POLICY_VERSION,
            MOVE_REGISTRY_VERSION,
            PROMPT_TEMPLATE_VERSION,
            REPLAY_MANIFEST_VERSION,
            THEOREM_FAMILY_VERSION,
        )

        versions = manifest.get("versions", {})
        self.conn.execute(
            """
            INSERT INTO experiment_manifests(
                snapshot_id, experiment_id, project_id, snapshot_kind, manifest_version,
                prompt_version, parser_version, evaluator_version, semantic_memory_version,
                verification_schema_version, policy_version, move_registry_version,
                theorem_family_version, manifest_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                experiment_id,
                project_id,
                snapshot_kind,
                REPLAY_MANIFEST_VERSION,
                versions.get("prompt_version", PROMPT_TEMPLATE_VERSION),
                versions.get("parser_version", VERIFICATION_PARSER_VERSION),
                versions.get("evaluator_version", EVALUATOR_VERSION),
                versions.get("semantic_memory_version", SEMANTIC_MEMORY_VERSION),
                versions.get("verification_schema_version", VERIFICATION_SCHEMA_VERSION),
                versions.get("policy_version", MANAGER_POLICY_VERSION),
                versions.get("move_registry_version", MOVE_REGISTRY_VERSION),
                versions.get("theorem_family_version", THEOREM_FAMILY_VERSION),
                json.dumps(manifest),
                utcnow(),
            ),
        )
        self.conn.commit()

    def latest_experiment_manifest(
        self, experiment_id: str, snapshot_kind: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get the latest manifest for an experiment."""
        query = "SELECT * FROM experiment_manifests WHERE experiment_id = ?"
        params: List[Any] = [experiment_id]
        if snapshot_kind:
            query += " AND snapshot_kind = ?"
            params.append(snapshot_kind)
        query += " ORDER BY created_at DESC LIMIT 1"
        row = self.conn.execute(query, params).fetchone()
        return self._decode_manifest_row(row) if row else None

    def list_experiment_manifests(self, experiment_id: str) -> List[Dict[str, Any]]:
        """List all manifests for an experiment."""
        rows = self.conn.execute(
            "SELECT * FROM experiment_manifests WHERE experiment_id = ? ORDER BY created_at ASC",
            (experiment_id,),
        ).fetchall()
        return [self._decode_manifest_row(row) for row in rows]

    def save_experiment_plan(self, brief: Dict[str, Any]) -> None:
        """Save an experiment plan."""
        experiment_id = brief["experiment_id"]
        project_id = brief["project_id"]
        conjecture_id = brief["conjecture_id"]
        now = utcnow()

        self.conn.execute(
            """
            INSERT OR REPLACE INTO experiments(
                experiment_id, project_id, conjecture_id, route_id, phase, move, objective, expected_signal,
                modification_json, workspace_dir, lean_file, external_id, external_status,
                submitted_at, last_synced_at, discovery_question_id, move_family, move_family_version,
                theorem_family_id, move_title, rationale, candidate_metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM experiments WHERE experiment_id = ?), ?))
            """,
            (
                experiment_id,
                project_id,
                conjecture_id,
                brief.get("route_id"),
                brief.get("phase", "exploration"),
                brief["move"],
                brief["objective"],
                brief["expected_signal"],
                json.dumps(brief.get("modification", {})),
                brief.get("workspace_dir", ""),
                brief.get("lean_file", ""),
                brief.get("external_id"),
                brief.get("external_status"),
                brief.get("submitted_at"),
                brief.get("last_synced_at"),
                brief.get("discovery_question_id"),
                brief.get("move_family", brief["move"]),
                brief.get("move_family_version", "v1"),
                brief.get("theorem_family_id", ""),
                brief.get("move_title", ""),
                brief.get("rationale", ""),
                json.dumps(brief.get("candidate_metadata", {})),
                experiment_id,
                now,
            ),
        )
        self.conn.commit()
        manifest = self.build_experiment_manifest(
            brief,
            snapshot_kind="planned",
            provider_name=brief.get("provider", ""),
        )
        self.record_experiment_manifest(
            experiment_id=experiment_id,
            project_id=project_id,
            snapshot_kind="planned",
            manifest=manifest,
        )

    def _provider_result_payload(self, result: ProviderResult) -> Dict[str, Any]:
        """Convert a ProviderResult to a JSON-serializable payload."""
        payload = asdict(result)
        payload["verification_record"] = asdict(result.verification_record) if result.verification_record else None
        payload["semantic_summary"] = asdict(result.semantic_summary) if result.semantic_summary else None
        return payload

    def update_experiment_result(
        self,
        experiment_id: str,
        provider: str,
        result: ProviderResult,
        evaluation: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update experiment with result data."""
        outcome_json = {
            "provider_result": self._provider_result_payload(result),
        }
        ingestion_json = {
            "proof_outcome": result.proof_outcome,
            "signal_summary": result.signal_summary,
            "candidate_lemmas": result.candidate_lemmas,
            "normalized_candidate_lemmas": result.normalized_candidate_lemmas,
            "unresolved_goals": result.unresolved_goals,
            "normalized_unresolved_goals": result.normalized_unresolved_goals,
            "blocked_on": result.blocked_on,
            "missing_assumptions": result.missing_assumptions or result.suspected_missing_assumptions,
            "artifact_inventory": result.artifact_inventory,
            "proof_trace_fragments": result.proof_trace_fragments,
            "counterexample_witnesses": result.counterexample_witnesses,
            "new_signal_count": result.new_signal_count,
            "reused_signal_count": result.reused_signal_count,
            "verification_schema_version": result.verification_record.schema_version if result.verification_record else VERIFICATION_SCHEMA_VERSION,
            "parser_version": result.verification_record.run.parser_version if result.verification_record else VERIFICATION_PARSER_VERSION,
            "semantic_memory_version": result.verification_record.run.semantic_memory_version if result.verification_record else SEMANTIC_MEMORY_VERSION,
            "evaluator_version": result.verification_record.run.evaluator_version if result.verification_record else EVALUATOR_VERSION,
            "verification_record": asdict(result.verification_record) if result.verification_record else None,
            "semantic_summary": asdict(result.semantic_summary) if result.semantic_summary else None,
            "followup_hints": result.metadata.get("followup_hints", {}),
            "boundary_map": result.metadata.get("boundary_map", {}),
        }
        if evaluation is not None:
            outcome_json["evaluation"] = evaluation
        completed_at = utcnow() if result.status in {"succeeded", "stalled", "failed"} else None
        submitted_at = utcnow() if result.status == "submitted" and result.external_id else None
        last_synced_at = utcnow()
        self.conn.execute(
            """
            UPDATE experiments
            SET provider = ?, status = ?, blocker_type = ?, outcome_json = ?, ingestion_json = ?, proof_outcome = ?, signal_summary = ?, external_id = ?, external_status = ?,
                submitted_at = COALESCE(?, submitted_at), last_synced_at = ?, completed_at = COALESCE(?, completed_at),
                new_signal_count = ?, reused_signal_count = ?, attempt_count = attempt_count + 1,
                verification_schema_version = ?, parser_version = ?, semantic_memory_version = ?, evaluator_version = ?
            WHERE experiment_id = ?
            """,
            (
                provider,
                result.status,
                result.blocker_type,
                json.dumps(outcome_json),
                json.dumps(ingestion_json),
                result.proof_outcome,
                result.signal_summary,
                result.external_id or None,
                result.external_status or None,
                submitted_at,
                last_synced_at,
                completed_at,
                result.new_signal_count,
                result.reused_signal_count,
                result.verification_record.schema_version if result.verification_record else VERIFICATION_SCHEMA_VERSION,
                result.verification_record.run.parser_version if result.verification_record else VERIFICATION_PARSER_VERSION,
                result.verification_record.run.semantic_memory_version if result.verification_record else SEMANTIC_MEMORY_VERSION,
                result.verification_record.run.evaluator_version if result.verification_record else EVALUATOR_VERSION,
                experiment_id,
            ),
        )
        self.conn.commit()
        experiment = self.get_experiment(experiment_id)
        if experiment is not None:
            snapshot_kind = "submitted" if result.status in {"submitted", "in_progress"} else "finalized"
            manifest = self.build_experiment_manifest(
                experiment,
                snapshot_kind=snapshot_kind,
                provider_name=provider,
                result=result,
            )
            self.record_experiment_manifest(
                experiment_id=experiment_id,
                project_id=experiment["project_id"],
                snapshot_kind=snapshot_kind,
                manifest=manifest,
            )

    def complete_experiment(
        self,
        experiment_id: str,
        provider: str,
        result: ProviderResult,
        evaluation: Dict[str, Any],
    ) -> None:
        """Mark an experiment as complete with final status."""
        self.update_experiment_result(
            experiment_id=experiment_id,
            provider=provider,
            result=result,
            evaluation=evaluation,
        )

    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get a single experiment by ID."""
        row = self.conn.execute(
            "SELECT * FROM experiments WHERE experiment_id = ?", (experiment_id,)
        ).fetchone()
        return self._decode_experiment_row(row) if row else None

    def list_experiments(self, project_id: str) -> List[Dict[str, Any]]:
        """List all experiments for a project."""
        rows = self.conn.execute(
            "SELECT * FROM experiments WHERE project_id = ? ORDER BY created_at ASC",
            (project_id,),
        ).fetchall()
        return [self._decode_experiment_row(row) for row in rows]

    def list_active_experiments(
        self, project_id: str, provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List experiments with active status (planned, submitted, in_progress)."""
        statuses = ("planned", "submitted", "in_progress")
        placeholders = ", ".join("?" for _ in statuses)
        params: List[Any] = [project_id, *statuses]
        query = (
            f"SELECT * FROM experiments WHERE project_id = ? AND status IN ({placeholders})"
        )
        if provider is not None:
            query += " AND provider = ?"
            params.append(provider)
        query += " ORDER BY created_at ASC"
        rows = self.conn.execute(query, params).fetchall()
        return [self._decode_experiment_row(row) for row in rows]

    def count_active_experiments(self, project_id: str, provider: Optional[str] = None) -> int:
        """Count active experiments for a project."""
        return len(self.list_active_experiments(project_id, provider=provider))

    def list_completed_experiments(
        self, project_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List completed experiments (succeeded, stalled, failed)."""
        statuses = ("succeeded", "stalled", "failed")
        placeholders = ", ".join("?" for _ in statuses)
        params: List[Any] = [project_id, *statuses]
        query = (
            f"SELECT * FROM experiments WHERE project_id = ? AND status IN ({placeholders}) "
            "ORDER BY COALESCE(completed_at, created_at) DESC"
        )
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [self._decode_experiment_row(row) for row in rows]

    def list_backfillable_experiments(
        self,
        project_id: str,
        provider: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List experiments that are candidates for backfill."""
        statuses = ("stalled", "failed")
        external_statuses = ("COMPLETE", "COMPLETE_WITH_ERRORS")
        status_placeholders = ", ".join("?" for _ in statuses)
        external_placeholders = ", ".join("?" for _ in external_statuses)
        params: List[Any] = [project_id, *statuses, *external_statuses]
        query = (
            f"SELECT * FROM experiments WHERE project_id = ? "
            f"AND status IN ({status_placeholders}) "
            "AND external_id IS NOT NULL AND external_id != '' "
            f"AND external_status IN ({external_placeholders}) "
            "AND COALESCE(new_signal_count, 0) = 0 "
            "AND (proof_outcome IS NULL OR proof_outcome = 'unknown')"
        )
        if provider is not None:
            query += " AND provider = ?"
            params.append(provider)
        query += " ORDER BY created_at DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [self._decode_experiment_row(row) for row in rows]

    def active_experiments_by_external_status(
        self, project_id: str, provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get counts of active experiments grouped by external status."""
        active = self.list_active_experiments(project_id, provider=provider)
        counts: Dict[str, int] = {}
        for item in active:
            key = item.get("external_status") or item["status"]
            counts[key] = counts.get(key, 0) + 1
        return [
            {"external_status": status, "count": count}
            for status, count in sorted(counts.items(), key=lambda pair: pair[0])
        ]

    def reset_experiment_for_retry(self, experiment_id: str) -> None:
        """Reset an experiment for retry."""
        self.conn.execute(
            """
            UPDATE experiments
            SET status = 'planned',
                external_id = NULL,
                external_status = NULL,
                submitted_at = NULL,
                last_synced_at = NULL
            WHERE experiment_id = ?
            """,
            (experiment_id,),
        )
        self.conn.commit()

    def mark_experiment_killed(self, experiment_id: str) -> None:
        """Mark an experiment as killed."""
        self.conn.execute(
            """
            UPDATE experiments
            SET status = 'failed',
                blocker_type = 'operator_killed',
                external_status = 'killed',
                completed_at = ?
            WHERE experiment_id = ?
            """,
            (utcnow(), experiment_id),
        )
        self.conn.commit()

    def save_lemma_occurrences(
        self,
        experiment_id: str,
        conjecture_id: str,
        generated: Iterable[str],
        proved: Iterable[str],
        candidate: Iterable[str] = (),
    ) -> None:
        """Save lemma occurrences for an experiment."""
        import uuid

        from research_orchestrator.lemma_utils import lemma_fingerprint
        from research_orchestrator.db.utils import utcnow

        all_items: List[tuple[str, str]] = []
        all_items.extend((item, "generated") for item in generated)
        all_items.extend((item, "proved") for item in proved)
        all_items.extend((item, "candidate") for item in candidate)

        for statement, role in all_items:
            normalized, digest = lemma_fingerprint(statement)
            existing = self.conn.execute(
                "SELECT lemma_id, reuse_count FROM lemmas WHERE normalized_hash = ?",
                (digest,),
            ).fetchone()
            if existing is None:
                lemma_id = str(uuid.uuid4())
                self.conn.execute(
                    """
                    INSERT INTO lemmas(lemma_id, normalized_hash, normalized_statement, representative_statement, reuse_count, first_seen_at, last_seen_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (lemma_id, digest, normalized, statement, 1, utcnow(), utcnow()),
                )
            else:
                lemma_id = existing["lemma_id"]
                self.conn.execute(
                    "UPDATE lemmas SET reuse_count = reuse_count + 1, last_seen_at = ? WHERE lemma_id = ?",
                    (utcnow(), lemma_id),
                )

            self.conn.execute(
                """
                INSERT INTO lemma_occurrences(occurrence_id, lemma_id, experiment_id, conjecture_id, role, proved, raw_statement, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    lemma_id,
                    experiment_id,
                    conjecture_id,
                    role,
                    1 if role == "proved" else 0,
                    statement,
                    utcnow(),
                ),
            )

        self.conn.commit()

    def record_assumption_observation(
        self,
        project_id: str,
        conjecture_id: str,
        experiment_id: str,
        assumption_name: str,
        outcome: str,
        sensitivity_score: float,
    ) -> None:
        """Record an assumption sensitivity observation."""
        import uuid

        self.conn.execute(
            """
            INSERT INTO assumption_observations(observation_id, project_id, conjecture_id, assumption_name, experiment_id, outcome, sensitivity_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                project_id,
                conjecture_id,
                assumption_name,
                experiment_id,
                outcome,
                sensitivity_score,
                utcnow(),
            ),
        )
        self.conn.commit()

    def add_note(
        self,
        project_id: str,
        note_markdown: str,
        structured: Optional[Dict[str, Any]] = None,
        experiment_id: Optional[str] = None,
    ) -> None:
        """Add a research note."""
        import uuid

        self.conn.execute(
            """
            INSERT INTO research_notes(note_id, project_id, experiment_id, note_markdown, structured_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                project_id,
                experiment_id,
                note_markdown,
                json.dumps(structured) if structured is not None else None,
                utcnow(),
            ),
        )
        self.conn.commit()
