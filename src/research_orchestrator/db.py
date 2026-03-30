from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from research_orchestrator.lemma_utils import goal_fingerprint, lemma_fingerprint
from research_orchestrator.types import Conjecture, ProjectCharter, ProviderResult


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


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

    def save_conjecture(self, conjecture: Conjecture) -> None:
        metadata = {
            "assumptions": conjecture.assumptions,
            "critical_assumptions": conjecture.critical_assumptions,
            "hidden_dependencies": conjecture.hidden_dependencies,
            "equivalent_forms": conjecture.equivalent_forms,
            "candidate_transfer_domains": conjecture.candidate_transfer_domains,
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
            assumptions=metadata.get("assumptions", []),
            critical_assumptions=metadata.get("critical_assumptions", []),
            hidden_dependencies=metadata.get("hidden_dependencies", []),
            equivalent_forms=metadata.get("equivalent_forms", []),
            candidate_transfer_domains=metadata.get("candidate_transfer_domains", []),
        )

    def list_conjectures(self, project_id: str) -> List[Conjecture]:
        rows = self.conn.execute(
            "SELECT conjecture_id FROM conjectures WHERE project_id = ? ORDER BY conjecture_id",
            (project_id,),
        ).fetchall()
        return [self.get_conjecture(row["conjecture_id"]) for row in rows]

    def save_experiment_plan(self, brief: Dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO experiments(
                experiment_id, project_id, conjecture_id, phase, move, objective, expected_signal,
                modification_json, workspace_dir, lean_file, external_id, external_status, submitted_at, last_synced_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM experiments WHERE experiment_id = ?), ?))
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
                brief["experiment_id"],
                utcnow(),
            ),
        )
        self.conn.commit()

    def update_experiment_result(
        self,
        experiment_id: str,
        provider: str,
        result: ProviderResult,
        evaluation: Optional[Dict[str, Any]] = None,
    ) -> None:
        outcome_json = {
            "provider_result": result.__dict__,
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
                new_signal_count = ?, reused_signal_count = ?
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
            item["outcome"] = json.loads(item["outcome_json"]) if item["outcome_json"] else None
            item["ingestion"] = json.loads(item["ingestion_json"]) if item.get("ingestion_json") else None
            results.append(item)
        return results

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
    ) -> None:
        import uuid

        self.conn.execute("DELETE FROM extracted_subgoals WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM artifact_metadata WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM blocker_observations WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM proof_trace_observations WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM counterexample_observations WHERE experiment_id = ?", (experiment_id,))

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
        self.conn.commit()

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
            SELECT statement, COUNT(*) AS observations
            FROM extracted_subgoals
            WHERE project_id = ?
            GROUP BY statement
            HAVING COUNT(*) >= ?
            ORDER BY observations DESC, statement ASC
            """,
            (project_id, minimum_reuse),
        ).fetchall()
        return [dict(row) for row in rows]

    def recurring_proof_traces(self, project_id: str, minimum_reuse: int = 2) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT normalized_fragment AS fragment, COUNT(*) AS observations
            FROM proof_trace_observations
            WHERE project_id = ?
            GROUP BY normalized_fragment
            HAVING COUNT(*) >= ?
            ORDER BY observations DESC, normalized_fragment ASC
            """,
            (project_id, minimum_reuse),
        ).fetchall()
        return [dict(row) for row in rows]

    def counterexample_summary(self, project_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT normalized_witness AS witness, COUNT(*) AS observations
            FROM counterexample_observations
            WHERE project_id = ?
            GROUP BY normalized_witness
            ORDER BY observations DESC, normalized_witness ASC
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
              AND proof_outcome = 'unknown'
              AND COALESCE(new_signal_count, 0) = 0
              AND status IN ('stalled', 'failed')
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
            SELECT blocker_type, proof_outcome, COUNT(*) AS observations
            FROM blocker_observations
            WHERE project_id = ?
            GROUP BY blocker_type, proof_outcome
            ORDER BY observations DESC, blocker_type ASC, proof_outcome ASC
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
        return {
            "project_id": project_id,
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
        }
