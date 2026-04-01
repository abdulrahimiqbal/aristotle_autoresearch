"""Core database functionality including connection, transactions, and row decoders."""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from research_orchestrator.db.schema import SCHEMA, VIEWS, MIGRATIONS
from research_orchestrator.db.utils import utcnow


class DatabaseCoreMixin:
    """Core database functionality mixin."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        self._configure_connection()

    def _configure_connection(self) -> None:
        """Configure SQLite connection pragmas for performance and safety."""
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA busy_timeout = 30000")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")

    @contextmanager
    def transaction(self, immediate: bool = False):
        """Context manager for database transactions.
        
        Usage:
            with self.transaction() as conn:
                conn.execute(...)
        """
        self.conn.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
        try:
            yield self.conn
        except Exception:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def initialize(self) -> None:
        """Initialize database with schema, views, and apply migrations."""
        for statement in SCHEMA:
            self.conn.execute(statement)
        self._ensure_experiment_columns()
        self._apply_migrations()
        for statement in VIEWS:
            self.conn.execute(statement)
        self.conn.commit()

    def _apply_migrations(self) -> None:
        """Apply pending database migrations."""
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

    def _ensure_experiment_columns(self) -> None:
        """Ensure all required experiment columns exist (for backwards compatibility)."""
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
        """Close the database connection."""
        self.conn.close()

    def integrity_check(self) -> List[str]:
        """Run PRAGMA integrity_check and return results."""
        return [row[0] for row in self.conn.execute("PRAGMA integrity_check").fetchall()]

    def quick_check(self) -> List[str]:
        """Run PRAGMA quick_check and return results."""
        return [row[0] for row in self.conn.execute("PRAGMA quick_check").fetchall()]

    def check_event_timeline_integrity(self) -> Dict[str, Any]:
        """Check for gaps in manager event sequence numbers."""
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
        """Checkpoint the WAL file."""
        row = self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        return {
            "busy": int(row[0]) if row is not None else 0,
            "checkpointed": int(row[1]) if row is not None else 0,
            "running": int(row[2]) if row is not None else 0,
        }

    def backup_to(self, path: str | Path) -> str:
        """Create a backup of the database to the specified path."""
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        backup_conn = sqlite3.connect(str(dest))
        with backup_conn:
            self.conn.backup(backup_conn)
        backup_conn.close()
        return str(dest)

    def atomic_snapshot_to(self, path: str | Path) -> str:
        """Create an atomic snapshot of the database."""
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".sqlite", dir=str(dest.parent), prefix="tmp_snapshot_")
        os.close(tmp_fd)
        try:
            tmp_conn = sqlite3.connect(tmp_path)
            with tmp_conn:
                self.conn.backup(tmp_conn)
            tmp_conn.close()
            os.replace(tmp_path, dest)
        except Exception:
            os.unlink(tmp_path)
            raise
        return str(dest)

    def query_view(self, view_name: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query a named view, optionally filtered by project_id."""
        if project_id is not None:
            rows = self.conn.execute(
                f"SELECT * FROM {view_name} WHERE project_id = ?", (project_id,)
            ).fetchall()
        else:
            rows = self.conn.execute(f"SELECT * FROM {view_name}").fetchall()
        return [dict(row) for row in rows]

    # Row decoders for complex types
    def _decode_experiment_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        """Decode an experiment row with JSON fields."""
        item = dict(row)
        item["modification"] = json.loads(item["modification_json"])
        item["candidate_metadata"] = json.loads(item["candidate_metadata_json"]) if item.get("candidate_metadata_json") else {}
        item["outcome"] = json.loads(item["outcome_json"]) if item.get("outcome_json") else None
        item["ingestion"] = json.loads(item["ingestion_json"]) if item.get("ingestion_json") else None
        return item

    def _decode_manifest_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        """Decode a manifest row."""
        item = dict(row)
        item["manifest"] = json.loads(item["manifest_json"])
        return item

    def _decode_manager_candidate_audit(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        """Decode a manager candidate audit row."""
        item = dict(row)
        item["score_breakdown"] = json.loads(item["score_breakdown_json"])
        item["candidate"] = json.loads(item["candidate_json"])
        return item

    def _decode_manager_run_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        """Decode a manager run row."""
        item = dict(row)
        item["summary"] = json.loads(item["summary_json"])
        return item

    def _decode_interpretation_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        """Decode a campaign interpretation row."""
        item = dict(row)
        item["parsed"] = json.loads(item["parsed_json"])
        return item

    def _decode_bridge_row(self, row: sqlite3.Row | Dict[str, Any]) -> Dict[str, Any]:
        """Decode a bridge hypothesis row."""
        item = dict(row)
        item["hypothesis"] = json.loads(item["hypothesis_json"])
        return item

    # Proof ledger operations
    def add_proof_ledger_entry(
        self,
        entry_id: str,
        project_id: str,
        conjecture_id: str,
        experiment_id: str,
        lemma_statement: str,
        lemma_hash: str,
        proof_status: str = "proved",
        proof_lean_code: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """Add an entry to the proof ledger."""
        self.conn.execute(
            """
            INSERT INTO proof_ledger (
                entry_id, project_id, conjecture_id, experiment_id,
                lemma_statement, lemma_hash, proof_status, proof_lean_code,
                dependencies, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entry_id) DO UPDATE SET
                proof_status = excluded.proof_status,
                proof_lean_code = excluded.proof_lean_code,
                dependencies = excluded.dependencies
            """,
            (
                entry_id,
                project_id,
                conjecture_id,
                experiment_id,
                lemma_statement,
                lemma_hash,
                proof_status,
                proof_lean_code,
                json.dumps(dependencies or []),
                utcnow(),
            ),
        )
        self.conn.commit()

    def get_proof_ledger(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all proof ledger entries for a project."""
        rows = self.conn.execute(
            "SELECT * FROM proof_ledger WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["dependencies"] = json.loads(item["dependencies"])
            result.append(item)
        return result

    def get_proved_lemmas_for_conjecture(self, conjecture_id: str) -> List[Dict[str, Any]]:
        """Get all proved lemmas for a specific conjecture."""
        rows = self.conn.execute(
            """
            SELECT * FROM proof_ledger
            WHERE conjecture_id = ? AND proof_status = 'proved'
            ORDER BY created_at DESC
            """,
            (conjecture_id,),
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["dependencies"] = json.loads(item["dependencies"])
            result.append(item)
        return result

    def lemma_is_proved(self, lemma_hash: str) -> bool:
        """Check if a lemma has been proved."""
        row = self.conn.execute(
            "SELECT 1 FROM proof_ledger WHERE lemma_hash = ? AND proof_status = 'proved' LIMIT 1",
            (lemma_hash,),
        ).fetchone()
        return row is not None

    # Obligation DAG operations
    def add_obligation(
        self,
        obligation_id: str,
        project_id: str,
        conjecture_id: str,
        statement: str,
        statement_hash: str,
        source_experiment_id: str,
        parent_obligation_id: Optional[str] = None,
        priority: int = 0,
    ) -> None:
        """Add a new proof obligation to the DAG."""
        self.conn.execute(
            """
            INSERT INTO proof_obligations (
                obligation_id, project_id, conjecture_id, parent_obligation_id,
                statement, statement_hash, status, source_experiment_id,
                priority, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
            """,
            (
                obligation_id,
                project_id,
                conjecture_id,
                parent_obligation_id,
                statement,
                statement_hash,
                source_experiment_id,
                priority,
                utcnow(),
            ),
        )
        self.conn.commit()

    def resolve_obligation(
        self,
        obligation_id: str,
        resolution_proof_id: str,
    ) -> None:
        """Mark an obligation as resolved with a proof."""
        self.conn.execute(
            """
            UPDATE proof_obligations
            SET status = 'proved', resolved_at = ?, resolution_proof_id = ?
            WHERE obligation_id = ?
            """,
            (utcnow(), resolution_proof_id, obligation_id),
        )
        self.conn.commit()

    def get_obligation_dag(self, conjecture_id: str) -> List[Dict[str, Any]]:
        """Get the full obligation DAG for a conjecture."""
        rows = self.conn.execute(
            """
            SELECT * FROM proof_obligations
            WHERE conjecture_id = ?
            ORDER BY parent_obligation_id NULLS FIRST, created_at ASC
            """,
            (conjecture_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_open_obligations(self, conjecture_id: str) -> List[Dict[str, Any]]:
        """Get all open (unresolved) obligations for a conjecture."""
        rows = self.conn.execute(
            """
            SELECT * FROM proof_obligations
            WHERE conjecture_id = ? AND status = 'open'
            ORDER BY priority DESC, created_at ASC
            """,
            (conjecture_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_obligation_chain(self, obligation_id: str) -> List[Dict[str, Any]]:
        """Get the chain of obligations from root to this obligation."""
        chain = []
        current_id = obligation_id
        visited = set()

        while current_id and current_id not in visited:
            visited.add(current_id)
            row = self.conn.execute(
                "SELECT * FROM proof_obligations WHERE obligation_id = ?",
                (current_id,),
            ).fetchone()

            if row is None:
                break

            item = dict(row)
            chain.append(item)
            current_id = item.get("parent_obligation_id")

        return list(reversed(chain))

    # Search coverage operations
    def record_search_coverage(
        self,
        coverage_id: str,
        project_id: str,
        conjecture_id: str,
        search_type: str,
        search_key: str,
        outcome: str,
        found_count: int = 0,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a search coverage entry to track what has been searched."""
        self.conn.execute(
            """
            INSERT INTO search_coverage (
                coverage_id, project_id, conjecture_id, search_type,
                search_key, outcome, found_count, details, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(coverage_id) DO UPDATE SET
                outcome = excluded.outcome,
                found_count = excluded.found_count,
                details = excluded.details
            """,
            (
                coverage_id,
                project_id,
                conjecture_id,
                search_type,
                search_key,
                outcome,
                found_count,
                json.dumps(details) if details else None,
                utcnow(),
            ),
        )
        self.conn.commit()

    def get_search_coverage(
        self,
        project_id: str,
        conjecture_id: Optional[str] = None,
        search_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get search coverage records for a project."""
        query = "SELECT * FROM search_coverage WHERE project_id = ?"
        params: List[Any] = [project_id]

        if conjecture_id is not None:
            query += " AND conjecture_id = ?"
            params.append(conjecture_id)
        if search_type is not None:
            query += " AND search_type = ?"
            params.append(search_type)

        query += " ORDER BY created_at DESC"

        rows = self.conn.execute(query, params).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            if item.get("details"):
                try:
                    item["details"] = json.loads(item["details"])
                except json.JSONDecodeError:
                    item["details"] = None
            result.append(item)
        return result

    def has_been_searched(
        self,
        project_id: str,
        conjecture_id: str,
        search_type: str,
        search_key: str,
    ) -> bool:
        """Check if a specific search has already been performed."""
        row = self.conn.execute(
            """
            SELECT 1 FROM search_coverage
            WHERE project_id = ? AND conjecture_id = ? AND search_type = ? AND search_key = ?
            LIMIT 1
            """,
            (project_id, conjecture_id, search_type, search_key),
        ).fetchone()
        return row is not None

    def get_negative_knowledge(
        self,
        project_id: str,
        conjecture_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get searches with 'not_found' outcome (negative knowledge)."""
        query = "SELECT * FROM search_coverage WHERE project_id = ? AND outcome = 'not_found'"
        params: List[Any] = [project_id]

        if conjecture_id is not None:
            query += " AND conjecture_id = ?"
            params.append(conjecture_id)

        query += " ORDER BY created_at DESC"

        rows = self.conn.execute(query, params).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            if item.get("details"):
                try:
                    item["details"] = json.loads(item["details"])
                except json.JSONDecodeError:
                    item["details"] = None
            result.append(item)
        return result
