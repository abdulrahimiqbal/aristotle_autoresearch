"""Database schema definitions for the research orchestrator."""

from typing import List, Tuple

SCHEMA: List[str] = [
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
    """
    CREATE TABLE IF NOT EXISTS proof_ledger (
        entry_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        conjecture_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        lemma_statement TEXT NOT NULL,
        lemma_hash TEXT NOT NULL,
        proof_status TEXT NOT NULL DEFAULT 'proved',
        proof_lean_code TEXT,
        dependencies TEXT NOT NULL DEFAULT '[]',
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id),
        FOREIGN KEY(conjecture_id) REFERENCES conjectures(conjecture_id),
        FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_proof_ledger_conjecture ON proof_ledger(conjecture_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_proof_ledger_hash ON proof_ledger(lemma_hash)
    """,
]

VIEWS: List[str] = [
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

MIGRATIONS: List[Tuple[str, List[str]]] = [
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
