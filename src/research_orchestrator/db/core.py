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
