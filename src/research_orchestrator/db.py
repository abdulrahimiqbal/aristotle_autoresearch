from __future__ import annotations

from dataclasses import asdict
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from research_orchestrator.lemma_utils import goal_fingerprint, lemma_fingerprint
from research_orchestrator.schema_versions import EVALUATOR_VERSION, SEMANTIC_MEMORY_VERSION, VERIFICATION_PARSER_VERSION, VERIFICATION_SCHEMA_VERSION
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
]


class Database:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row

    def initialize(self) -> None:
        for statement in SCHEMA:
            self.conn.execute(statement)
        self._ensure_experiment_columns()
        self.conn.commit()

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

    def save_experiment_plan(self, brief: Dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO experiments(
                experiment_id, project_id, conjecture_id, phase, move, objective, expected_signal,
                modification_json, workspace_dir, lean_file, external_id, external_status,
                submitted_at, last_synced_at, discovery_question_id, move_family, move_family_version,
                theorem_family_id, move_title, rationale, candidate_metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM experiments WHERE experiment_id = ?), ?))
            """,
            (
                brief["experiment_id"],
                brief["project_id"],
                brief["conjecture_id"],
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
        data = dict(row)
        data["modification"] = json.loads(data["modification_json"])
        data["candidate_metadata"] = json.loads(data["candidate_metadata_json"]) if data.get("candidate_metadata_json") else {}
        if data.get("outcome_json"):
            data["outcome"] = json.loads(data["outcome_json"])
        else:
            data["outcome"] = None
        data["ingestion"] = json.loads(data["ingestion_json"]) if data.get("ingestion_json") else None
        return data

    def list_experiments(self, project_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM experiments WHERE project_id = ? ORDER BY created_at ASC",
            (project_id,),
        ).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            item["modification"] = json.loads(item["modification_json"])
            item["candidate_metadata"] = json.loads(item["candidate_metadata_json"]) if item.get("candidate_metadata_json") else {}
            item["outcome"] = json.loads(item["outcome_json"]) if item["outcome_json"] else None
            item["ingestion"] = json.loads(item["ingestion_json"]) if item.get("ingestion_json") else None
            results.append(item)
        return results

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

    def create_incident(self, project_id: str, incident_type: str, detail: str, experiment_id: str = "", severity: str = "warning") -> None:
        import uuid

        now = utcnow()
        self.conn.execute(
            """
            INSERT INTO incidents(incident_id, project_id, experiment_id, incident_type, severity, detail, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)
            """,
            (
                str(uuid.uuid4()),
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
        results = []
        for row in rows:
            item = dict(row)
            item["modification"] = json.loads(item["modification_json"])
            item["candidate_metadata"] = json.loads(item["candidate_metadata_json"]) if item.get("candidate_metadata_json") else {}
            item["outcome"] = json.loads(item["outcome_json"]) if item["outcome_json"] else None
            item["ingestion"] = json.loads(item["ingestion_json"]) if item.get("ingestion_json") else None
            results.append(item)
        return results

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
        results = []
        for row in rows:
            item = dict(row)
            item["modification"] = json.loads(item["modification_json"])
            item["candidate_metadata"] = json.loads(item["candidate_metadata_json"]) if item.get("candidate_metadata_json") else {}
            item["outcome"] = json.loads(item["outcome_json"]) if item["outcome_json"] else None
            item["ingestion"] = json.loads(item["ingestion_json"]) if item.get("ingestion_json") else None
            results.append(item)
        return results

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
        results = []
        for row in rows:
            item = dict(row)
            item["modification"] = json.loads(item["modification_json"])
            item["candidate_metadata"] = json.loads(item["candidate_metadata_json"]) if item.get("candidate_metadata_json") else {}
            item["outcome"] = json.loads(item["outcome_json"]) if item["outcome_json"] else None
            item["ingestion"] = json.loads(item["ingestion_json"]) if item.get("ingestion_json") else None
            results.append(item)
        return results

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
    ) -> str:
        import uuid

        run_id = str(uuid.uuid4())
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
