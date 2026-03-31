from __future__ import annotations

import csv
from contextlib import contextmanager
from dataclasses import asdict
import json
import os
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from research_orchestrator.lemma_utils import goal_fingerprint, lemma_fingerprint
from research_orchestrator.schema_versions import (
    EVALUATOR_VERSION,
    MANAGER_POLICY_VERSION,
    MOVE_REGISTRY_VERSION,
    PROMPT_TEMPLATE_VERSION,
    REPLAY_MANIFEST_VERSION,
    RUNTIME_POLICY_VERSION,
    SEMANTIC_MEMORY_VERSION,
    THEOREM_FAMILY_VERSION,
    VERIFICATION_PARSER_VERSION,
    VERIFICATION_SCHEMA_VERSION,
)
from research_orchestrator.semantic_memory import canonicalize_text, hydrate_semantic_summary
from research_orchestrator.types import (
    CampaignSpec,
    Conjecture,
    DiscoveryQuestion,
    ProjectCharter,
    ProviderResult,
    SemanticArtifact,
    SemanticMemorySummary,
    VerificationSignal,
    VerificationRecord,
)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def current_version_bundle() -> Dict[str, str]:
    return {
        "manifest_version": REPLAY_MANIFEST_VERSION,
        "prompt_version": PROMPT_TEMPLATE_VERSION,
        "parser_version": VERIFICATION_PARSER_VERSION,
        "evaluator_version": EVALUATOR_VERSION,
        "semantic_memory_version": SEMANTIC_MEMORY_VERSION,
        "verification_schema_version": VERIFICATION_SCHEMA_VERSION,
        "policy_version": MANAGER_POLICY_VERSION,
        "move_registry_version": MOVE_REGISTRY_VERSION,
        "theorem_family_version": THEOREM_FAMILY_VERSION,
        "runtime_policy_version": RUNTIME_POLICY_VERSION,
    }


def _best_effort_git_branch(cwd: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        charter_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS conjectures (
        conjecture_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        name TEXT NOT NULL,
        domain TEXT NOT NULL,
        natural_language TEXT NOT NULL,
        lean_statement TEXT NOT NULL,
        metadata_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS experiments (
        experiment_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        phase TEXT NOT NULL,
        move TEXT NOT NULL,
        objective TEXT NOT NULL,
        expected_signal TEXT NOT NULL,
        modification_json TEXT NOT NULL,
        workspace_dir TEXT NOT NULL,
        lean_file TEXT NOT NULL,
        provider TEXT,
        status TEXT DEFAULT 'planned',
        blocker_type TEXT DEFAULT 'unknown',
        outcome_json TEXT,
        created_at TEXT NOT NULL,
        completed_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(project_id),
        FOREIGN KEY(conjecture_id) REFERENCES conjectures(conjecture_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lemmas (
        lemma_id TEXT PRIMARY KEY,
        normalized_hash TEXT UNIQUE NOT NULL,
        normalized_statement TEXT NOT NULL,
        representative_statement TEXT NOT NULL,
        reuse_count INTEGER NOT NULL DEFAULT 0,
        first_seen_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lemma_occurrences (
        occurrence_id TEXT PRIMARY KEY,
        lemma_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        role TEXT NOT NULL,
        proved INTEGER NOT NULL DEFAULT 0,
        raw_statement TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(lemma_id) REFERENCES lemmas(lemma_id),
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id),
        FOREIGN KEY(conjecture_id) REFERENCES conjectures(conjecture_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS research_notes (
        note_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        experiment_id TEXT,
        note_markdown TEXT NOT NULL,
        structured_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS assumption_observations (
        observation_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        assumption_name TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        outcome TEXT NOT NULL,
        sensitivity_score REAL NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id),
        FOREIGN KEY(conjecture_id) REFERENCES conjectures(conjecture_id),
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS manager_runs (
        run_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        provider TEXT NOT NULL,
        policy_path TEXT NOT NULL,
        jobs_synced INTEGER NOT NULL DEFAULT 0,
        jobs_submitted INTEGER NOT NULL DEFAULT 0,
        active_before INTEGER NOT NULL DEFAULT 0,
        active_after INTEGER NOT NULL DEFAULT 0,
        report_path TEXT,
        snapshot_path TEXT,
        summary_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        completed_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS extracted_subgoals (
        subgoal_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        statement TEXT NOT NULL,
        source TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id),
        FOREIGN KEY(conjecture_id) REFERENCES conjectures(conjecture_id),
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS artifact_metadata (
        artifact_id TEXT PRIMARY KEY,
        experiment_id TEXT NOT NULL,
        path TEXT NOT NULL,
        kind TEXT NOT NULL,
        size_bytes INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS blocker_observations (
        blocker_observation_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        blocker_type TEXT NOT NULL,
        proof_outcome TEXT NOT NULL,
        detail TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id),
        FOREIGN KEY(conjecture_id) REFERENCES conjectures(conjecture_id),
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS proof_trace_observations (
        trace_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        fragment TEXT NOT NULL,
        normalized_fragment TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id),
        FOREIGN KEY(conjecture_id) REFERENCES conjectures(conjecture_id),
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS counterexample_observations (
        witness_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        witness_text TEXT NOT NULL,
        normalized_witness TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id),
        FOREIGN KEY(conjecture_id) REFERENCES conjectures(conjecture_id),
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS campaign_specs (
        project_id TEXT PRIMARY KEY,
        version TEXT NOT NULL,
        raw_prompt TEXT NOT NULL,
        spec_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS discovery_questions (
        question_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        category TEXT NOT NULL,
        question TEXT NOT NULL,
        rationale TEXT NOT NULL,
        priority INTEGER NOT NULL DEFAULT 50,
        status TEXT NOT NULL DEFAULT 'open',
        node_id TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id),
        FOREIGN KEY(conjecture_id) REFERENCES conjectures(conjecture_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS discovery_graph_nodes (
        node_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        conjecture_id TEXT,
        experiment_id TEXT,
        node_type TEXT NOT NULL,
        label TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        confidence REAL NOT NULL DEFAULT 0.5,
        provenance_kind TEXT NOT NULL DEFAULT 'inferred',
        provenance_ref TEXT NOT NULL DEFAULT '',
        metadata_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS discovery_graph_edges (
        edge_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        source_node_id TEXT NOT NULL,
        target_node_id TEXT NOT NULL,
        relation TEXT NOT NULL,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_events (
        event_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        experiment_id TEXT DEFAULT '',
        event_type TEXT NOT NULL,
        detail_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS incidents (
        incident_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        experiment_id TEXT DEFAULT '',
        incident_type TEXT NOT NULL,
        severity TEXT NOT NULL DEFAULT 'warning',
        detail TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS verification_records (
        record_id TEXT PRIMARY KEY,
        experiment_id TEXT NOT NULL UNIQUE,
        schema_version TEXT NOT NULL,
        provider_name TEXT NOT NULL,
        verification_status TEXT NOT NULL,
        theorem_status TEXT NOT NULL,
        validation_ok INTEGER NOT NULL DEFAULT 1,
        record_json TEXT NOT NULL,
        raw_payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS semantic_objects (
        object_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        kind TEXT NOT NULL,
        canonical_hash TEXT NOT NULL,
        canonical_text TEXT NOT NULL,
        representative_text TEXT NOT NULL,
        theorem_family TEXT NOT NULL DEFAULT '',
        normalization_version TEXT NOT NULL,
        occurrence_count INTEGER NOT NULL DEFAULT 0,
        first_seen_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        UNIQUE(project_id, kind, canonical_hash)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS semantic_occurrences (
        occurrence_id TEXT PRIMARY KEY,
        object_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        exact_hash TEXT NOT NULL,
        exact_text TEXT NOT NULL,
        match_type TEXT NOT NULL,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        FOREIGN KEY(object_id) REFERENCES semantic_objects(object_id),
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS experiment_manifests (
        snapshot_id TEXT PRIMARY KEY,
        experiment_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        snapshot_kind TEXT NOT NULL,
        manifest_version TEXT NOT NULL,
        prompt_version TEXT NOT NULL,
        parser_version TEXT NOT NULL,
        evaluator_version TEXT NOT NULL,
        semantic_memory_version TEXT NOT NULL,
        verification_schema_version TEXT NOT NULL,
        policy_version TEXT NOT NULL,
        move_registry_version TEXT NOT NULL,
        theorem_family_version TEXT NOT NULL,
        manifest_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id),
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS manager_candidate_audits (
        audit_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        rank_position INTEGER NOT NULL,
        selected INTEGER NOT NULL DEFAULT 0,
        selection_reason TEXT NOT NULL DEFAULT '',
        policy_score REAL NOT NULL DEFAULT 0,
        score_breakdown_json TEXT NOT NULL DEFAULT '{}',
        candidate_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(run_id) REFERENCES manager_runs(run_id),
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS campaign_health_snapshots (
        snapshot_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        health_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(run_id) REFERENCES manager_runs(run_id),
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS campaign_interpretations (
        interpretation_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        run_id TEXT DEFAULT '',
        prompt_version TEXT NOT NULL,
        model_version TEXT NOT NULL,
        raw_response TEXT NOT NULL,
        parsed_json TEXT NOT NULL,
        validation_status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS bridge_hypotheses (
        bridge_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        run_id TEXT DEFAULT '',
        source_conjecture_id TEXT NOT NULL,
        target_conjecture_id TEXT NOT NULL,
        suggested_move_family TEXT NOT NULL,
        confidence REAL NOT NULL DEFAULT 0,
        hypothesis_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        migration_id TEXT PRIMARY KEY,
        applied_at TEXT NOT NULL
    )
    """,
]

VIEWS = [
    """
    CREATE VIEW IF NOT EXISTS readable_experiments AS
    SELECT
        e.experiment_id,
        e.project_id,
        e.conjecture_id,
        e.phase,
        e.move,
        COALESCE(e.move_family, e.move) AS move_family,
        e.status,
        e.proof_outcome,
        e.blocker_type,
        e.objective,
        e.expected_signal,
        e.modification_json,
        COALESCE(e.new_signal_count, 0) AS new_signal_count,
        COALESCE(e.reused_signal_count, 0) AS reused_signal_count,
        COALESCE(json_extract(e.ingestion_json, '$.boundary_map.summary'), '') AS boundary_summary,
        COALESCE(json_extract(e.candidate_metadata_json, '$.motif_id'), '') AS motif_id,
        COALESCE(json_extract(e.candidate_metadata_json, '$.motif_signature'), '') AS motif_signature,
        COALESCE(json_extract(e.candidate_metadata_json, '$.campaign_priority'), 0) AS campaign_priority,
        COALESCE(json_extract(e.candidate_metadata_json, '$.signal_support'), 0) AS signal_support,
        e.discovery_question_id,
        e.created_at,
        e.completed_at
    FROM experiments e
    """,
    """
    CREATE VIEW IF NOT EXISTS conjecture_scoreboard AS
    SELECT
        c.project_id,
        c.conjecture_id,
        c.name,
        c.domain,
        COUNT(e.experiment_id) AS experiments_total,
        SUM(CASE WHEN e.status = 'succeeded' THEN 1 ELSE 0 END) AS succeeded,
        SUM(CASE WHEN e.status = 'stalled' THEN 1 ELSE 0 END) AS stalled,
        SUM(CASE WHEN e.status = 'failed' THEN 1 ELSE 0 END) AS failed,
        SUM(COALESCE(e.new_signal_count, 0)) AS new_signal_count,
        SUM(COALESCE(e.reused_signal_count, 0)) AS reused_signal_count,
        MAX(COALESCE(json_extract(e.candidate_metadata_json, '$.motif_reuse_count'), 0)) AS top_motif_reuse,
        MAX(COALESCE(json_extract(e.candidate_metadata_json, '$.recent_signal_velocity'), 0)) AS recent_signal_velocity
    FROM conjectures c
    LEFT JOIN experiments e ON e.conjecture_id = c.conjecture_id
    GROUP BY c.project_id, c.conjecture_id, c.name, c.domain
    """,
    """
    CREATE VIEW IF NOT EXISTS recurring_structure_summary AS
    SELECT c.project_id, 'lemma' AS structure_kind, l.representative_statement AS summary_text, l.reuse_count AS observations
    FROM lemmas l
    JOIN lemma_occurrences lo ON lo.lemma_id = l.lemma_id
    JOIN conjectures c ON c.conjecture_id = lo.conjecture_id
    GROUP BY c.project_id, l.lemma_id, l.representative_statement, l.reuse_count
    UNION ALL
    SELECT project_id, 'subgoal' AS structure_kind, canonical_text AS summary_text, occurrence_count AS observations
    FROM semantic_objects
    WHERE kind = 'goal'
    UNION ALL
    SELECT project_id, 'proof_trace' AS structure_kind, canonical_text AS summary_text, occurrence_count AS observations
    FROM semantic_objects
    WHERE kind = 'proof_trace'
    UNION ALL
    SELECT project_id, 'counterexample' AS structure_kind, canonical_text AS summary_text, occurrence_count AS observations
    FROM semantic_objects
    WHERE kind = 'counterexample'
    """,
    """
    CREATE VIEW IF NOT EXISTS active_queue_summary AS
    SELECT
        project_id,
        conjecture_id,
        move,
        COALESCE(move_family, move) AS move_family,
        status,
        COUNT(*) AS active_count,
        MAX(COALESCE(json_extract(candidate_metadata_json, '$.motif_reuse_count'), 0)) AS motif_reuse_count,
        MAX(COALESCE(json_extract(candidate_metadata_json, '$.recent_signal_velocity'), 0)) AS recent_signal_velocity
    FROM experiments
    WHERE status IN ('planned', 'submitted', 'in_progress')
    GROUP BY project_id, conjecture_id, move, COALESCE(move_family, move), status
    """,
    """
    CREATE VIEW IF NOT EXISTS incident_summary AS
    SELECT
        project_id,
        incident_type,
        severity,
        status,
        COUNT(*) AS incident_count,
        MAX(updated_at) AS last_updated_at
    FROM incidents
    GROUP BY project_id, incident_type, severity, status
    """,
]

MIGRATIONS: list[tuple[str, list[str]]] = [
    (
        "2026_04_01_live_control_plane",
        [
            "ALTER TABLE experiments ADD COLUMN route_id TEXT",
            """
            CREATE TABLE IF NOT EXISTS manager_events (
                event_id TEXT PRIMARY KEY,
                sequence_no INTEGER NOT NULL,
                occurred_at TEXT NOT NULL,
                project_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                experiment_id TEXT,
                route_id TEXT,
                event_type TEXT NOT NULL,
                source_component TEXT NOT NULL,
                visibility TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS theorem_routes (
                route_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                conjecture_id TEXT,
                theorem_family TEXT NOT NULL,
                route_key TEXT NOT NULL UNIQUE,
                route_stage TEXT NOT NULL,
                route_status TEXT NOT NULL,
                current_strength REAL NOT NULL DEFAULT 0,
                recent_signal_velocity REAL NOT NULL DEFAULT 0,
                blocker_pressure REAL NOT NULL DEFAULT 0,
                novelty_score REAL NOT NULL DEFAULT 0,
                reuse_score REAL NOT NULL DEFAULT 0,
                transfer_score REAL NOT NULL DEFAULT 0,
                last_selected_at TEXT,
                last_progress_at TEXT,
                operator_priority INTEGER NOT NULL DEFAULT 0,
                summary_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS route_evidence (
                evidence_id TEXT PRIMARY KEY,
                route_id TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                source_experiment_id TEXT,
                source_object_id TEXT,
                strength_delta REAL NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(route_id) REFERENCES theorem_routes(route_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS operator_commands (
                command_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                route_id TEXT,
                command_type TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT,
                payload_json TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS operator_command_results (
                result_id TEXT PRIMARY KEY,
                command_id TEXT NOT NULL,
                applied_at TEXT NOT NULL,
                status TEXT NOT NULL,
                details_json TEXT NOT NULL,
                FOREIGN KEY(command_id) REFERENCES operator_commands(command_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projection_checkpoints (
                projection_name TEXT PRIMARY KEY,
                last_sequence_no INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS live_manager_timeline (
                event_id TEXT PRIMARY KEY,
                sequence_no INTEGER NOT NULL,
                occurred_at TEXT NOT NULL,
                project_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                route_id TEXT,
                experiment_id TEXT,
                summary_json TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS route_strength_current (
                route_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                route_key TEXT NOT NULL,
                route_status TEXT NOT NULL,
                current_strength REAL NOT NULL,
                recent_signal_velocity REAL NOT NULL,
                blocker_pressure REAL NOT NULL,
                novelty_score REAL NOT NULL,
                reuse_score REAL NOT NULL,
                transfer_score REAL NOT NULL,
                operator_priority INTEGER NOT NULL,
                last_selected_at TEXT,
                last_progress_at TEXT,
                summary_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS route_decisions_current (
                decision_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                route_id TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS frontier_rankings_current (
                entry_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                rank_position INTEGER NOT NULL,
                experiment_id TEXT NOT NULL,
                route_id TEXT,
                score REAL NOT NULL,
                score_breakdown_json TEXT NOT NULL,
                candidate_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS active_experiments_current (
                experiment_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                route_id TEXT,
                conjecture_id TEXT NOT NULL,
                move TEXT NOT NULL,
                move_family TEXT NOT NULL,
                status TEXT NOT NULL,
                external_status TEXT,
                updated_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS recent_results_current (
                experiment_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                route_id TEXT,
                conjecture_id TEXT NOT NULL,
                status TEXT NOT NULL,
                proof_outcome TEXT,
                blocker_type TEXT,
                new_signal_count INTEGER NOT NULL,
                reused_signal_count INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS incidents_current (
                incident_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                experiment_id TEXT,
                route_id TEXT,
                incident_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                detail TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS system_health_current (
                project_id TEXT PRIMARY KEY,
                last_event_at TEXT,
                last_projection_at TEXT,
                manager_status TEXT,
                db_status TEXT,
                source_mode TEXT,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_manager_events_project ON manager_events(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_manager_events_route ON manager_events(route_id)",
            "CREATE INDEX IF NOT EXISTS idx_manager_events_run ON manager_events(run_id)",
            "CREATE INDEX IF NOT EXISTS idx_manager_events_type ON manager_events(event_type)",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_manager_events_sequence ON manager_events(sequence_no)",
            "CREATE INDEX IF NOT EXISTS idx_theorem_routes_project ON theorem_routes(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_theorem_routes_status ON theorem_routes(route_status)",
            "CREATE INDEX IF NOT EXISTS idx_route_evidence_route ON route_evidence(route_id)",
            "CREATE INDEX IF NOT EXISTS idx_operator_commands_project ON operator_commands(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_operator_commands_status ON operator_commands(status)",
            "CREATE INDEX IF NOT EXISTS idx_timeline_project ON live_manager_timeline(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_route_strength_project ON route_strength_current(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_frontier_rankings_project ON frontier_rankings_current(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_active_experiments_project ON active_experiments_current(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_recent_results_project ON recent_results_current(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_incidents_project ON incidents_current(project_id)",
        ],
    ),
]


class Database:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        self._configure_connection()

    def _configure_connection(self) -> None:
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA busy_timeout = 30000")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")

    @contextmanager
    def transaction(self, immediate: bool = False):
        self.conn.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
        try:
            yield self.conn
        except Exception:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def initialize(self) -> None:
        for statement in SCHEMA:
            self.conn.execute(statement)
        self._ensure_experiment_columns()
        self._apply_migrations()
        for statement in VIEWS:
            self.conn.execute(statement)
        self.conn.commit()

    def _apply_migrations(self) -> None:
        applied = {
            row["migration_id"]
            for row in self.conn.execute("SELECT migration_id FROM schema_migrations").fetchall()
        }
        for migration_id, statements in MIGRATIONS:
            if migration_id in applied:
                continue
            with self.transaction(immediate=True):
                for statement in statements:
                    try:
                        self.conn.execute(statement)
                    except sqlite3.OperationalError as exc:
                        message = str(exc).lower()
                        if "duplicate column name" in message or "already exists" in message:
                            continue
                        raise
                self.conn.execute(
                    "INSERT INTO schema_migrations(migration_id, applied_at) VALUES (?, ?)",
                    (migration_id, utcnow()),
                )

    def _decode_experiment_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        item = dict(row)
        item["modification"] = json.loads(item["modification_json"])
        item["candidate_metadata"] = json.loads(item["candidate_metadata_json"]) if item.get("candidate_metadata_json") else {}
        item["outcome"] = json.loads(item["outcome_json"]) if item.get("outcome_json") else None
        item["ingestion"] = json.loads(item["ingestion_json"]) if item.get("ingestion_json") else None
        return item

    def _decode_manifest_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        item = dict(row)
        item["manifest"] = json.loads(item["manifest_json"])
        return item

    def _decode_manager_candidate_audit(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        item = dict(row)
        item["score_breakdown"] = json.loads(item["score_breakdown_json"])
        item["candidate"] = json.loads(item["candidate_json"])
        return item

    def _decode_manager_run_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        item = dict(row)
        item["summary"] = json.loads(item["summary_json"])
        return item

    def _decode_interpretation_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        item = dict(row)
        item["parsed"] = json.loads(item["parsed_json"])
        return item

    def _decode_bridge_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        item = dict(row)
        item["hypothesis"] = json.loads(item["hypothesis_json"])
        return item

    def _ensure_experiment_columns(self) -> None:
        existing = {
            row["name"]
            for row in self.conn.execute("PRAGMA table_info(experiments)").fetchall()
        }
        for column_name, column_type in (
            ("external_id", "TEXT"),
            ("external_status", "TEXT"),
            ("submitted_at", "TEXT"),
            ("last_synced_at", "TEXT"),
            ("proof_outcome", "TEXT"),
            ("signal_summary", "TEXT"),
            ("ingestion_json", "TEXT"),
            ("new_signal_count", "INTEGER DEFAULT 0"),
            ("reused_signal_count", "INTEGER DEFAULT 0"),
            ("discovery_question_id", "TEXT"),
            ("attempt_count", "INTEGER DEFAULT 0"),
            ("verification_schema_version", "TEXT"),
            ("parser_version", "TEXT"),
            ("semantic_memory_version", "TEXT"),
            ("evaluator_version", "TEXT"),
            ("move_family", "TEXT"),
            ("move_family_version", "TEXT"),
            ("theorem_family_id", "TEXT"),
            ("move_title", "TEXT"),
            ("rationale", "TEXT"),
            ("candidate_metadata_json", "TEXT"),
        ):
            if column_name not in existing:
                self.conn.execute(
                    f"ALTER TABLE experiments ADD COLUMN {column_name} {column_type}"
                )

    def close(self) -> None:
        self.conn.close()

    def integrity_check(self) -> List[str]:
        return [row[0] for row in self.conn.execute("PRAGMA integrity_check").fetchall()]

    def quick_check(self) -> List[str]:
        return [row[0] for row in self.conn.execute("PRAGMA quick_check").fetchall()]

    def check_event_timeline_integrity(self) -> Dict[str, Any]:
        try:
            row = self.conn.execute(
                """
                SELECT COUNT(*) FROM (
                    SELECT sequence_no, LAG(sequence_no) OVER (ORDER BY sequence_no) AS prev
                    FROM manager_events
                ) WHERE prev IS NOT NULL AND sequence_no != prev + 1
                """
            ).fetchone()
            gaps = int(row[0]) if row else 0
            return {"gaps": gaps, "ok": gaps == 0}
        except Exception as exc:
            return {"gaps": 0, "ok": False, "error": str(exc)}

    def checkpoint_wal(self) -> Dict[str, int]:
        row = self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        return {
            "busy": int(row[0]) if row is not None else 0,
            "log": int(row[1]) if row is not None else 0,
            "checkpointed": int(row[2]) if row is not None else 0,
        }

    def backup_to(self, path: str | Path) -> str:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_wal()
        backup_conn = sqlite3.connect(str(destination), timeout=30.0)
        try:
            self.conn.backup(backup_conn)
            backup_conn.commit()
        finally:
            backup_conn.close()
        return str(destination)

    def atomic_snapshot_to(self, path: str | Path) -> str:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=destination.name, suffix=".tmp", delete=False, dir=destination.parent) as handle:
            temp_path = Path(handle.name)
        try:
            self.backup_to(temp_path)
            with temp_path.open("rb") as stream:
                os.fsync(stream.fileno())
            os.replace(temp_path, destination)
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
        return str(destination)

    def query_view(self, view_name: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if project_id is None:
            rows = self.conn.execute(f"SELECT * FROM {view_name}").fetchall()
        else:
            rows = self.conn.execute(f"SELECT * FROM {view_name} WHERE project_id = ?", (project_id,)).fetchall()
        return [dict(row) for row in rows]

    def save_project(self, charter: ProjectCharter) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO projects(project_id, title, charter_json, created_at)
            VALUES (?, ?, ?, COALESCE((SELECT created_at FROM projects WHERE project_id = ?), ?))
            """,
            (
                charter.project_id,
                charter.title,
                json.dumps(charter.__dict__),
                charter.project_id,
                utcnow(),
            ),
        )
        self.conn.commit()

    def save_campaign_spec(self, spec: CampaignSpec) -> None:
        now = utcnow()
        self.conn.execute(
            """
            INSERT OR REPLACE INTO campaign_specs(project_id, version, raw_prompt, spec_json, created_at, updated_at)
            VALUES (
                ?, ?, ?, ?,
                COALESCE((SELECT created_at FROM campaign_specs WHERE project_id = ?), ?),
                ?
            )
            """,
            (
                spec.project_id,
                spec.version,
                spec.raw_prompt,
                json.dumps(
                    {
                        **spec.__dict__,
                        "budget_policy": spec.budget_policy.__dict__,
                        "runtime_policy": spec.runtime_policy.__dict__,
                    }
                ),
                spec.project_id,
                now,
                now,
            ),
        )
        self.conn.commit()

    def get_campaign_spec(self, project_id: str) -> Optional[CampaignSpec]:
        row = self.conn.execute(
            "SELECT spec_json FROM campaign_specs WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        if row is None:
            return None
        data = json.loads(row["spec_json"])
        from research_orchestrator.types import CampaignBudgetPolicy, RuntimePolicy

        data["budget_policy"] = CampaignBudgetPolicy(**data.get("budget_policy", {}))
        data["runtime_policy"] = RuntimePolicy(**data.get("runtime_policy", {}))
        return CampaignSpec(**data)

    def save_conjecture(self, conjecture: Conjecture) -> None:
        metadata = {
            "theorem_family_id": conjecture.theorem_family_id,
            "assumptions": conjecture.assumptions,
            "critical_assumptions": conjecture.critical_assumptions,
            "hidden_dependencies": conjecture.hidden_dependencies,
            "equivalent_forms": conjecture.equivalent_forms,
            "candidate_transfer_domains": conjecture.candidate_transfer_domains,
            "family_metadata": conjecture.family_metadata,
        }
        self.conn.execute(
            """
            INSERT OR REPLACE INTO conjectures(
                conjecture_id, project_id, name, domain, natural_language, lean_statement, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM conjectures WHERE conjecture_id = ?), ?))
            """,
            (
                conjecture.conjecture_id,
                conjecture.project_id,
                conjecture.name,
                conjecture.domain,
                conjecture.natural_language,
                conjecture.lean_statement,
                json.dumps(metadata),
                conjecture.conjecture_id,
                utcnow(),
            ),
        )
        self.conn.commit()

    def get_charter(self, project_id: str) -> ProjectCharter:
        row = self.conn.execute(
            "SELECT charter_json FROM projects WHERE project_id = ?", (project_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown project_id: {project_id}")
        return ProjectCharter(**json.loads(row["charter_json"]))

    def get_conjecture(self, conjecture_id: str) -> Conjecture:
        row = self.conn.execute(
            "SELECT * FROM conjectures WHERE conjecture_id = ?", (conjecture_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown conjecture_id: {conjecture_id}")
        metadata = json.loads(row["metadata_json"])
        return Conjecture(
            conjecture_id=row["conjecture_id"],
            project_id=row["project_id"],
            name=row["name"],
            domain=row["domain"],
            natural_language=row["natural_language"],
            lean_statement=row["lean_statement"],
            theorem_family_id=metadata.get("theorem_family_id", ""),
            assumptions=metadata.get("assumptions", []),
            critical_assumptions=metadata.get("critical_assumptions", []),
            hidden_dependencies=metadata.get("hidden_dependencies", []),
            equivalent_forms=metadata.get("equivalent_forms", []),
            candidate_transfer_domains=metadata.get("candidate_transfer_domains", []),
            family_metadata=metadata.get("family_metadata", {}),
        )

    def list_conjectures(self, project_id: str) -> List[Conjecture]:
        rows = self.conn.execute(
            "SELECT conjecture_id FROM conjectures WHERE project_id = ? ORDER BY conjecture_id",
            (project_id,),
        ).fetchall()
        return [self.get_conjecture(row["conjecture_id"]) for row in rows]

    def save_discovery_question(self, question: DiscoveryQuestion) -> None:
        now = utcnow()
        self.conn.execute(
            """
            INSERT OR REPLACE INTO discovery_questions(
                question_id, project_id, conjecture_id, category, question, rationale,
                priority, status, node_id, created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                COALESCE(?, ''),
                COALESCE((SELECT created_at FROM discovery_questions WHERE question_id = ?), ?),
                ?
            )
            """,
            (
                question.question_id,
                question.project_id,
                question.conjecture_id,
                question.category,
                question.question,
                question.rationale,
                question.priority,
                question.status,
                question.node_id,
                question.question_id,
                now,
                now,
            ),
        )
        self.conn.commit()

    def list_discovery_questions(self, project_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        params: List[Any] = [project_id]
        query = "SELECT * FROM discovery_questions WHERE project_id = ?"
        if status is not None:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY priority DESC, created_at ASC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def mark_discovery_question_status(self, question_id: str, status: str, node_id: str = "") -> None:
        self.conn.execute(
            """
            UPDATE discovery_questions
            SET status = ?, node_id = COALESCE(NULLIF(?, ''), node_id), updated_at = ?
            WHERE question_id = ?
            """,
            (status, node_id, utcnow(), question_id),
        )
        self.conn.commit()

    def build_experiment_manifest(
        self,
        brief: Dict[str, Any],
        *,
        snapshot_kind: str,
        provider_name: str = "",
        result: Optional[ProviderResult] = None,
        policy_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
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
                "git_branch": _best_effort_git_branch(workspace_dir),
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
        import uuid

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
                versions.get("manifest_version", REPLAY_MANIFEST_VERSION),
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

    def latest_experiment_manifest(self, experiment_id: str, snapshot_kind: Optional[str] = None) -> Optional[Dict[str, Any]]:
        params: List[Any] = [experiment_id]
        query = "SELECT * FROM experiment_manifests WHERE experiment_id = ?"
        if snapshot_kind is not None:
            query += " AND snapshot_kind = ?"
            params.append(snapshot_kind)
        query += " ORDER BY created_at DESC LIMIT 1"
        row = self.conn.execute(query, params).fetchone()
        return self._decode_manifest_row(row) if row is not None else None

    def list_experiment_manifests(self, experiment_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM experiment_manifests
            WHERE experiment_id = ?
            ORDER BY created_at ASC
            """,
            (experiment_id,),
        ).fetchall()
        return [self._decode_manifest_row(row) for row in rows]

    def save_experiment_plan(self, brief: Dict[str, Any]) -> None:
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
                brief["experiment_id"],
                brief["project_id"],
                brief["conjecture_id"],
                brief.get("route_id"),
                brief["phase"],
                brief["move"],
                brief["objective"],
                brief["expected_signal"],
                json.dumps(brief["modification"]),
                brief["workspace_dir"],
                brief["lean_file"],
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
                brief["experiment_id"],
                utcnow(),
            ),
        )
        self.conn.commit()
        manifest = self.build_experiment_manifest(
            brief,
            snapshot_kind="planned",
            provider_name=brief.get("provider", ""),
        )
        self.record_experiment_manifest(
            experiment_id=brief["experiment_id"],
            project_id=brief["project_id"],
            snapshot_kind="planned",
            manifest=manifest,
        )

    def _provider_result_payload(self, result: ProviderResult) -> Dict[str, Any]:
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
        self.update_experiment_result(
            experiment_id=experiment_id,
            provider=provider,
            result=result,
            evaluation=evaluation,
        )

    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM experiments WHERE experiment_id = ?", (experiment_id,)
        ).fetchone()
        if row is None:
            return None
        return self._decode_experiment_row(row)

    def list_experiments(self, project_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM experiments WHERE project_id = ? ORDER BY created_at ASC",
            (project_id,),
        ).fetchall()
        return [self._decode_experiment_row(row) for row in rows]

    def add_audit_event(self, project_id: str, event_type: str, detail: Dict[str, Any], experiment_id: str = "") -> None:
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

    def list_audit_events(self, project_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM audit_events
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["detail"] = json.loads(item["detail_json"])
            items.append(item)
        return items

    def create_incident(
        self,
        project_id: str,
        incident_type: str,
        detail: str,
        experiment_id: str = "",
        severity: str = "warning",
        run_id: Optional[str] = None,
    ) -> None:
        import uuid

        now = utcnow()
        incident_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO incidents(incident_id, project_id, experiment_id, incident_type, severity, detail, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)
            """,
            (
                incident_id,
                project_id,
                experiment_id,
                incident_type,
                severity,
                detail,
                now,
                now,
            ),
        )
        self.conn.commit()
        if run_id:
            route_id = None
            if experiment_id:
                row = self.conn.execute(
                    "SELECT route_id FROM experiments WHERE experiment_id = ?",
                    (experiment_id,),
                ).fetchone()
                if row is not None:
                    route_id = row[0]
            self.emit_manager_event(
                project_id=project_id,
                run_id=run_id,
                event_type="incident.opened",
                source_component="incidents",
                experiment_id=experiment_id or None,
                route_id=route_id,
                payload={
                    "incident_id": incident_id,
                    "incident_type": incident_type,
                    "severity": severity,
                    "detail": detail,
                },
            )

    def ensure_open_incident(
        self,
        project_id: str,
        incident_type: str,
        detail: str,
        *,
        experiment_id: str = "",
        severity: str = "warning",
    ) -> None:
        row = self.conn.execute(
            """
            SELECT incident_id FROM incidents
            WHERE project_id = ? AND experiment_id = ? AND incident_type = ? AND status = 'open'
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (project_id, experiment_id, incident_type),
        ).fetchone()
        if row is not None:
            self.conn.execute(
                """
                UPDATE incidents
                SET detail = ?, severity = ?, updated_at = ?
                WHERE incident_id = ?
                """,
                (detail, severity, utcnow(), row["incident_id"]),
            )
            self.conn.commit()
            return
        self.create_incident(
            project_id=project_id,
            experiment_id=experiment_id,
            incident_type=incident_type,
            detail=detail,
            severity=severity,
        )

    def detect_stuck_runs(
        self,
        project_id: str,
        *,
        stale_run_timeout_seconds: int,
        stuck_run_timeout_seconds: int,
    ) -> List[Dict[str, Any]]:
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
                    "move_family": experiment.get("move_family", experiment["move"]),
                    "classification": "stale_remote" if is_stale else "planned_stuck",
                }
            )
        return stuck

    def enforce_retry_budget(
        self,
        project_id: str,
        *,
        max_attempts_per_experiment: int,
    ) -> List[Dict[str, Any]]:
        exhausted: List[Dict[str, Any]] = []
        for experiment in self.list_experiments(project_id):
            if experiment["status"] not in {"failed", "stalled", "submitted", "in_progress"}:
                continue
            if (experiment.get("attempt_count") or 0) < max_attempts_per_experiment:
                continue
            exhausted.append(experiment)
            self.ensure_open_incident(
                project_id=project_id,
                experiment_id=experiment["experiment_id"],
                incident_type="retry_budget_exhausted",
                severity="warning",
                detail=(
                    f"Experiment {experiment['experiment_id']} reached retry budget "
                    f"({experiment.get('attempt_count', 0)} attempts)."
                ),
            )
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
            max_attempts_per_experiment=max_attempts_per_experiment,
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
        for item in repeated_no_signal:
            self.ensure_open_incident(
                project_id=project_id,
                incident_type="repeated_no_signal_branch",
                severity="warning",
                detail=(
                    f"No-signal branch {item['conjecture_id']} / {item['move']} repeated "
                    f"{item['observations']} times."
                ),
            )
        return {
            "stuck_runs": stuck_runs,
            "retry_budget_exhausted": [item["experiment_id"] for item in exhausted],
            "repeated_failure_types": repeated_failure_types,
            "repeated_no_signal_branches": repeated_no_signal,
        }

    def expire_stale_active_experiments(self, project_id: str, max_age_seconds: int) -> int:
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

    def list_incidents(self, project_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        params: List[Any] = [project_id]
        query = "SELECT * FROM incidents WHERE project_id = ?"
        if status is not None:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY updated_at DESC, created_at DESC"
        return [dict(row) for row in self.conn.execute(query, params).fetchall()]

    def upsert_discovery_node(
        self,
        *,
        project_id: str,
        node_type: str,
        label: str,
        conjecture_id: str = "",
        experiment_id: str = "",
        confidence: float = 0.5,
        provenance_kind: str = "inferred",
        provenance_ref: str = "",
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        import uuid

        metadata_json = json.dumps(metadata or {})
        row = self.conn.execute(
            """
            SELECT node_id FROM discovery_graph_nodes
            WHERE project_id = ? AND node_type = ? AND label = ?
            """,
            (project_id, node_type, label),
        ).fetchone()
        now = utcnow()
        if row is not None:
            node_id = row["node_id"]
            self.conn.execute(
                """
                UPDATE discovery_graph_nodes
                SET confidence = MAX(confidence, ?),
                    status = ?,
                    conjecture_id = COALESCE(NULLIF(?, ''), conjecture_id),
                    experiment_id = COALESCE(NULLIF(?, ''), experiment_id),
                    provenance_kind = ?,
                    provenance_ref = ?,
                    metadata_json = ?,
                    updated_at = ?
                WHERE node_id = ?
                """,
                (
                    confidence,
                    status,
                    conjecture_id,
                    experiment_id,
                    provenance_kind,
                    provenance_ref,
                    metadata_json,
                    now,
                    node_id,
                ),
            )
        else:
            node_id = str(uuid.uuid4())
            self.conn.execute(
                """
                INSERT INTO discovery_graph_nodes(
                    node_id, project_id, conjecture_id, experiment_id, node_type, label, status,
                    confidence, provenance_kind, provenance_ref, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node_id,
                    project_id,
                    conjecture_id or None,
                    experiment_id or None,
                    node_type,
                    label,
                    status,
                    confidence,
                    provenance_kind,
                    provenance_ref,
                    metadata_json,
                    now,
                    now,
                ),
            )
        self.conn.commit()
        return node_id

    def create_discovery_edge(
        self,
        *,
        project_id: str,
        source_node_id: str,
        target_node_id: str,
        relation: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        import uuid

        existing = self.conn.execute(
            """
            SELECT edge_id FROM discovery_graph_edges
            WHERE project_id = ? AND source_node_id = ? AND target_node_id = ? AND relation = ?
            """,
            (project_id, source_node_id, target_node_id, relation),
        ).fetchone()
        if existing is not None:
            return
        self.conn.execute(
            """
            INSERT INTO discovery_graph_edges(edge_id, project_id, source_node_id, target_node_id, relation, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                project_id,
                source_node_id,
                target_node_id,
                relation,
                json.dumps(metadata or {}),
                utcnow(),
            ),
        )
        self.conn.commit()

    def list_discovery_nodes(self, project_id: str, node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        params: List[Any] = [project_id]
        query = "SELECT * FROM discovery_graph_nodes WHERE project_id = ?"
        if node_type is not None:
            query += " AND node_type = ?"
            params.append(node_type)
        query += " ORDER BY confidence DESC, created_at ASC"
        rows = self.conn.execute(query, params).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["metadata"] = json.loads(item["metadata_json"])
            items.append(item)
        return items

    def list_discovery_edges(self, project_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM discovery_graph_edges WHERE project_id = ? ORDER BY created_at ASC",
            (project_id,),
        ).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["metadata"] = json.loads(item["metadata_json"])
            items.append(item)
        return items

    def list_active_experiments(self, project_id: str, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        statuses = ("planned", "submitted", "in_progress")
        placeholders = ", ".join("?" for _ in statuses)
        params: List[Any] = [project_id, *statuses]
        query = (
            "SELECT * FROM experiments WHERE project_id = ? "
            f"AND status IN ({placeholders})"
        )
        if provider is not None:
            query += " AND provider = ?"
            params.append(provider)
        query += " ORDER BY created_at ASC"
        rows = self.conn.execute(query, params).fetchall()
        return [self._decode_experiment_row(row) for row in rows]

    def count_active_experiments(self, project_id: str, provider: Optional[str] = None) -> int:
        return len(self.list_active_experiments(project_id, provider=provider))

    def list_completed_experiments(self, project_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        statuses = ("succeeded", "stalled", "failed")
        placeholders = ", ".join("?" for _ in statuses)
        params: List[Any] = [project_id, *statuses]
        query = (
            "SELECT * FROM experiments WHERE project_id = ? "
            f"AND status IN ({placeholders}) ORDER BY COALESCE(completed_at, created_at) DESC"
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
        statuses = ("stalled", "failed")
        external_statuses = ("COMPLETE", "COMPLETE_WITH_ERRORS")
        status_placeholders = ", ".join("?" for _ in statuses)
        external_placeholders = ", ".join("?" for _ in external_statuses)
        params: List[Any] = [project_id, *statuses, *external_statuses]
        query = (
            "SELECT * FROM experiments WHERE project_id = ? "
            f"AND status IN ({status_placeholders}) "
            "AND external_id IS NOT NULL AND external_id != '' "
            f"AND external_status IN ({external_placeholders}) "
            "AND COALESCE(new_signal_count, 0) = 0 "
            "AND (proof_outcome IS NULL OR proof_outcome = 'unknown') "
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

    def active_experiments_by_external_status(self, project_id: str, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        active = self.list_active_experiments(project_id, provider=provider)
        counts: Dict[str, int] = {}
        for item in active:
            key = item.get("external_status") or item["status"]
            counts[key] = counts.get(key, 0) + 1
        return [
            {"external_status": status, "count": count}
            for status, count in sorted(counts.items(), key=lambda pair: pair[0])
        ]

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
        row = self.conn.execute(
            "SELECT * FROM manager_events WHERE project_id = ? ORDER BY sequence_no DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["payload"] = json.loads(item.get("payload_json", "{}"))
        return item

    def get_theorem_route_by_key(self, route_key: str) -> Optional[Dict[str, Any]]:
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
        row = self.conn.execute(
            "SELECT * FROM theorem_routes WHERE route_id = ?",
            (route_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["summary"] = json.loads(item.get("summary_json", "{}"))
        return item

    def list_theorem_routes(self, project_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
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

    def set_route_operator_priority(self, route_id: str, priority: int) -> None:
        self.conn.execute(
            "UPDATE theorem_routes SET operator_priority = ?, updated_at = ? WHERE route_id = ?",
            (int(priority), utcnow(), route_id),
        )
        self.conn.commit()

    def set_route_status(self, route_id: str, status: str) -> None:
        self.conn.execute(
            "UPDATE theorem_routes SET route_status = ?, updated_at = ? WHERE route_id = ?",
            (status, utcnow(), route_id),
        )
        self.conn.commit()

    def append_route_note(self, route_id: str, note: str) -> None:
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

    def reset_experiment_for_retry(self, experiment_id: str) -> None:
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

    def list_route_evidence(self, route_id: str, limit: int = 50) -> List[Dict[str, Any]]:
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

    def list_operator_commands(self, project_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
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
        self,
        command_id: str,
        *,
        status: str,
        details: Dict[str, Any],
    ) -> str:
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
        row = self.conn.execute(
            "SELECT last_sequence_no FROM projection_checkpoints WHERE projection_name = ?",
            (projection_name,),
        ).fetchone()
        if row is None:
            return 0
        return int(row["last_sequence_no"])

    def update_projection_checkpoint(self, projection_name: str, sequence_no: int) -> None:
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

    def list_manager_runs(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
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

    def save_campaign_health_snapshot(self, run_id: str, project_id: str, health: Dict[str, Any]) -> None:
        import uuid

        self.conn.execute(
            """
            INSERT INTO campaign_health_snapshots(snapshot_id, run_id, project_id, health_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), run_id, project_id, json.dumps(health), utcnow()),
        )
        self.conn.commit()

    def latest_campaign_health_snapshot(self, project_id: str) -> Optional[Dict[str, Any]]:
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

    def latest_campaign_interpretation(self, project_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            """
            SELECT * FROM campaign_interpretations
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (project_id,),
        ).fetchone()
        return self._decode_interpretation_row(row) if row is not None else None

    def list_campaign_interpretations(self, project_id: str, limit: int = 20) -> List[Dict[str, Any]]:
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

    def list_bridge_hypotheses(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
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

    def latest_manager_run(self, project_id: str) -> Optional[Dict[str, Any]]:
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

    def add_note(self, project_id: str, note_markdown: str, structured: Optional[Dict[str, Any]] = None, experiment_id: Optional[str] = None) -> None:
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

    def save_lemma_occurrences(
        self,
        experiment_id: str,
        conjecture_id: str,
        generated: Iterable[str],
        proved: Iterable[str],
        candidate: Iterable[str] = (),
    ) -> None:
        import uuid

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
                    """
                    UPDATE lemmas
                    SET reuse_count = reuse_count + 1, last_seen_at = ?
                    WHERE lemma_id = ?
                    """,
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

    def record_result_ingestion(
        self,
        project_id: str,
        conjecture_id: str,
        experiment_id: str,
        proof_outcome: str,
        blocker_type: str,
        unresolved_goals: Iterable[str],
        artifact_inventory: Iterable[Dict[str, Any]],
        signal_summary: str,
        proof_trace_fragments: Iterable[str] = (),
        counterexample_witnesses: Iterable[str] = (),
        discovery_question_id: str = "",
        verification_signals: Iterable[VerificationSignal] = (),
        verification_record: Optional[VerificationRecord] = None,
        semantic_summary: Optional[SemanticMemorySummary] = None,
        theorem_family: str = "",
    ) -> SemanticMemorySummary:
        import uuid

        verification_signals = list(verification_signals)
        semantic_summary = semantic_summary or SemanticMemorySummary()
        if not semantic_summary.artifacts:
            semantic_summary.artifacts = [
                canonicalize_text("goal", goal, theorem_family) for goal in unresolved_goals
            ] + [
                canonicalize_text("proof_trace", fragment, theorem_family) for fragment in proof_trace_fragments
            ] + [
                canonicalize_text("counterexample", witness, theorem_family) for witness in counterexample_witnesses
            ] + (
                [canonicalize_text("blocker", blocker_type, theorem_family)]
                if blocker_type and blocker_type != "unknown"
                else []
            )
        self.conn.execute("DELETE FROM extracted_subgoals WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM artifact_metadata WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM blocker_observations WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM proof_trace_observations WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM counterexample_observations WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM semantic_occurrences WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM verification_records WHERE experiment_id = ?", (experiment_id,))

        for goal in unresolved_goals:
            normalized_goal, _ = goal_fingerprint(goal)
            self.conn.execute(
                """
                INSERT INTO extracted_subgoals(subgoal_id, project_id, conjecture_id, experiment_id, statement, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    project_id,
                    conjecture_id,
                    experiment_id,
                    normalized_goal or goal,
                    "result_ingestion",
                    utcnow(),
                ),
            )

        for artifact in artifact_inventory:
            self.conn.execute(
                """
                INSERT INTO artifact_metadata(artifact_id, experiment_id, path, kind, size_bytes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    experiment_id,
                    artifact.get("path", ""),
                    artifact.get("kind", "file"),
                    int(artifact.get("size_bytes", 0) or 0),
                    utcnow(),
                ),
            )

        self.conn.execute(
            """
            INSERT INTO blocker_observations(blocker_observation_id, project_id, conjecture_id, experiment_id, blocker_type, proof_outcome, detail, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                project_id,
                conjecture_id,
                experiment_id,
                blocker_type,
                proof_outcome,
                signal_summary,
                utcnow(),
            ),
        )
        for fragment in proof_trace_fragments:
            normalized_fragment, _ = goal_fingerprint(fragment)
            self.conn.execute(
                """
                INSERT INTO proof_trace_observations(trace_id, project_id, conjecture_id, experiment_id, fragment, normalized_fragment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    project_id,
                    conjecture_id,
                    experiment_id,
                    fragment,
                    normalized_fragment or fragment,
                    utcnow(),
                ),
            )
        for witness in counterexample_witnesses:
            normalized_witness, _ = goal_fingerprint(witness)
            self.conn.execute(
                """
                INSERT INTO counterexample_observations(witness_id, project_id, conjecture_id, experiment_id, witness_text, normalized_witness, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    project_id,
                    conjecture_id,
                    experiment_id,
                    witness,
                    normalized_witness or witness,
                    utcnow(),
                ),
            )

        if verification_record is not None:
            self.conn.execute(
                """
                INSERT INTO verification_records(
                    record_id, experiment_id, schema_version, provider_name, verification_status,
                    theorem_status, validation_ok, record_json, raw_payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    experiment_id,
                    verification_record.schema_version,
                    verification_record.provider.provider_name,
                    verification_record.verification_status,
                    verification_record.theorem_status,
                    0 if verification_record.validation_issues else 1,
                    json.dumps(asdict(verification_record)),
                    json.dumps(verification_record.raw_payload),
                    utcnow(),
                ),
            )

        exact_reuse = 0
        canonical_reuse = 0
        new_exact = 0
        blocker_reuse = 0
        for artifact in semantic_summary.artifacts:
            object_row = self.conn.execute(
                """
                SELECT object_id, occurrence_count
                FROM semantic_objects
                WHERE project_id = ? AND kind = ? AND canonical_hash = ?
                """,
                (project_id, artifact.kind, artifact.canonical_id),
            ).fetchone()
            if object_row is None:
                object_id = str(uuid.uuid4())
                self.conn.execute(
                    """
                    INSERT INTO semantic_objects(
                        object_id, project_id, kind, canonical_hash, canonical_text,
                        representative_text, theorem_family, normalization_version,
                        occurrence_count, first_seen_at, last_seen_at, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        object_id,
                        project_id,
                        artifact.kind,
                        artifact.canonical_id,
                        artifact.canonical_text,
                        artifact.raw_text,
                        theorem_family,
                        SEMANTIC_MEMORY_VERSION,
                        1,
                        utcnow(),
                        utcnow(),
                        json.dumps(artifact.metadata),
                    ),
                )
                match_type = "new_exact"
                new_exact += 1
            else:
                object_id = object_row["object_id"]
                exact_row = self.conn.execute(
                    """
                    SELECT 1
                    FROM semantic_occurrences
                    WHERE object_id = ? AND exact_hash = ?
                    LIMIT 1
                    """,
                    (object_id, artifact.exact_id),
                ).fetchone()
                match_type = "exact_reuse" if exact_row is not None else "normalized_equivalent_reuse"
                if exact_row is not None:
                    exact_reuse += 1
                else:
                    canonical_reuse += 1
                if artifact.kind == "blocker":
                    blocker_reuse += 1
                self.conn.execute(
                    """
                    UPDATE semantic_objects
                    SET occurrence_count = occurrence_count + 1, last_seen_at = ?
                    WHERE object_id = ?
                    """,
                    (utcnow(), object_id),
                )
            self.conn.execute(
                """
                INSERT INTO semantic_occurrences(
                    occurrence_id, object_id, project_id, conjecture_id, experiment_id,
                    exact_hash, exact_text, match_type, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    object_id,
                    project_id,
                    conjecture_id,
                    experiment_id,
                    artifact.exact_id,
                    artifact.raw_text,
                    match_type,
                    json.dumps(artifact.metadata),
                    utcnow(),
                ),
            )
        semantic_summary.new_exact_count = new_exact
        semantic_summary.exact_reuse_count = exact_reuse
        semantic_summary.canonical_reuse_count = canonical_reuse
        semantic_summary.blocker_reuse_count = blocker_reuse
        question_node_id = ""
        if discovery_question_id:
            question_rows = self.conn.execute(
                "SELECT * FROM discovery_questions WHERE question_id = ?",
                (discovery_question_id,),
            ).fetchone()
            if question_rows is not None:
                question = dict(question_rows)
                question_node_id = self.upsert_discovery_node(
                    project_id=project_id,
                    node_type="discovery_question",
                    label=question["question"],
                    conjecture_id=conjecture_id,
                    experiment_id=experiment_id,
                    confidence=1.0,
                    provenance_kind="manager",
                    provenance_ref=discovery_question_id,
                    metadata={
                        "category": question["category"],
                        "priority": question["priority"],
                        "rationale": question["rationale"],
                    },
                )
                self.mark_discovery_question_status(discovery_question_id, "answered", node_id=question_node_id)

        for signal in verification_signals:
            node_id = self.upsert_discovery_node(
                project_id=signal.project_id,
                node_type=signal.signal_type,
                label=signal.label,
                conjecture_id=signal.conjecture_id,
                experiment_id=signal.experiment_id,
                confidence=signal.confidence,
                provenance_kind=signal.provenance[0].kind if signal.provenance else "artifact",
                provenance_ref=signal.provenance[0].path if signal.provenance else "",
                metadata={
                    "detail": signal.detail,
                    "metadata": signal.metadata,
                    "provenance": [item.__dict__ for item in signal.provenance],
                },
            )
            if question_node_id:
                self.create_discovery_edge(
                    project_id=project_id,
                    source_node_id=question_node_id,
                    target_node_id=node_id,
                    relation="answered_by",
                    metadata={"experiment_id": experiment_id},
                )
            experiment_node_id = self.upsert_discovery_node(
                project_id=project_id,
                node_type="experiment",
                label=experiment_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                confidence=1.0,
                provenance_kind="execution",
                provenance_ref=experiment_id,
                metadata={"proof_outcome": proof_outcome, "blocker_type": blocker_type},
            )
            self.create_discovery_edge(
                project_id=project_id,
                source_node_id=experiment_node_id,
                target_node_id=node_id,
                relation="produced_signal",
                metadata={"proof_outcome": proof_outcome},
            )
        self.add_audit_event(
            project_id=project_id,
            experiment_id=experiment_id,
            event_type="result_ingested",
            detail={
                "proof_outcome": proof_outcome,
                "blocker_type": blocker_type,
                "signal_summary": signal_summary,
                "verification_signal_count": len(verification_signals),
                "verification_schema_version": verification_record.schema_version if verification_record else VERIFICATION_SCHEMA_VERSION,
                "semantic_objects": len(semantic_summary.artifacts),
            },
        )
        self.conn.commit()
        return semantic_summary

    def record_assumption_observation(self, project_id: str, conjecture_id: str, experiment_id: str, assumption_name: str, outcome: str, sensitivity_score: float) -> None:
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

    def recurring_lemmas(self, minimum_reuse: int = 2) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT l.lemma_id, l.representative_statement, l.normalized_statement, l.reuse_count,
                   GROUP_CONCAT(DISTINCT lo.conjecture_id) AS conjecture_ids
            FROM lemmas l
            JOIN lemma_occurrences lo ON lo.lemma_id = l.lemma_id
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

    def recurring_subgoals(self, project_id: str, minimum_reuse: int = 2) -> List[Dict[str, Any]]:
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

    def recurring_proof_traces(self, project_id: str, minimum_reuse: int = 2) -> List[Dict[str, Any]]:
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

    def recurring_blockers_by_move(self, project_id: str, minimum_reuse: int = 2) -> List[Dict[str, Any]]:
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

    def no_signal_branches(self, project_id: str, threshold: int = 2) -> List[Dict[str, Any]]:
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

    def campaign_health(self, project_id: str, frontier: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
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
            or item.get("move_family") in {"legacy.promote_lemma", "decompose_subclaim", "invariant_mining"}
        )
        obstruction_runs = sum(
            1
            for item in completed
            if (item.get("candidate_metadata", {}).get("obstruction_targeting") or 0) >= 1.0
            or item.get("move_family") in {"extremal_case", "adversarial_counterexample", "witness_minimization"}
        )
        high_priority_frontier = sum(1 for item in frontier if (item.get("campaign_priority") or 0) > 0)
        move_families = {item.get("move_family", item["move"]) for item in completed}
        duplicate_pressure = sum(1 for item in frontier if item.get("duplicate_active_signature"))
        frontier_move_families = {item.get("move_family", item["move"]) for item in frontier}
        incident_by_type: Dict[str, int] = {}
        incident_by_severity: Dict[str, int] = {}
        for incident in incidents:
            incident_by_type[incident["incident_type"]] = incident_by_type.get(incident["incident_type"], 0) + 1
            incident_by_severity[incident["severity"]] = incident_by_severity.get(incident["severity"], 0) + 1
        no_signal = self.no_signal_branches(project_id)
        max_no_signal_streak = max((item["observations"] for item in no_signal), default=0)
        stuck_runs = self.detect_stuck_runs(
            project_id,
            stale_run_timeout_seconds=6 * 3600,
            stuck_run_timeout_seconds=2 * 3600,
        )
        retry_exhausted = [
            item["experiment_id"]
            for item in self.list_experiments(project_id)
            if (item.get("attempt_count") or 0) >= self.get_campaign_spec(project_id).budget_policy.max_attempts_per_experiment
        ] if self.get_campaign_spec(project_id) is not None else []
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
                "structured_ingestion_success_rate": round(structured_successes / total_completed, 3) if total_completed else 0.0,
                "semantic_reuse_rate": round(total_reused / max(1, total_reused + total_new), 3),
                "transfer_usage_rate": round(transfer_runs / total_completed, 3) if total_completed else 0.0,
                "reusable_structure_rate": round(reusable_structure_runs / total_completed, 3) if total_completed else 0.0,
                "obstruction_discovery_rate": round(obstruction_runs / total_completed, 3) if total_completed else 0.0,
                "high_priority_frontier_share": round(high_priority_frontier / max(1, len(frontier)), 3) if frontier else 0.0,
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
        experiments = self.list_experiments(project_id)
        solved = sum(1 for item in experiments if item["status"] == "succeeded")
        stalled = sum(1 for item in experiments if item["status"] == "stalled")
        failed = sum(1 for item in experiments if item["status"] == "failed")
        pending = sum(1 for item in experiments if item["status"] in {"planned", "submitted", "in_progress"})
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
                        if item["node_type"] in {"verified_lemma", "recurring_subgoal", "assumption_boundary", "counterexample_witness"}
                    ]
                ),
            },
            "open_incidents": incidents,
        }

    def export_readable_state(self, project_id: str, output_dir: str | Path) -> Dict[str, str]:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)

        payloads = {
            "campaign_summary.json": self.project_summary(project_id),
            "conjecture_scoreboard.json": self.query_view("conjecture_scoreboard", project_id=project_id),
            "recurring_structures.json": sorted(
                self.query_view("recurring_structure_summary", project_id=project_id),
                key=lambda item: (-int(item.get("observations", 0)), item.get("structure_kind", ""), item.get("summary_text", "")),
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
        return written
