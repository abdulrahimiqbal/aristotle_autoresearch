from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_orchestrator.dashboard_derivations import (
    choose_strongest_motif,
    choose_strongest_obstruction,
    classify_proof_traction,
    normalize_structure_type,
    normalized_name,
    structure_status_from_reuse,
    summarize_falsehood_boundary,
    summarize_problem_progress,
    summarize_recent_result,
)
from research_orchestrator.dashboard_models import DashboardState, DataProvenance, HealthStatus


REQUIRED_BUNDLE_FILES = (
    "campaign_summary.json",
    "conjecture_scoreboard.json",
    "recurring_structures.json",
    "active_queue.json",
    "incidents.json",
    "experiments.csv",
)
OPTIONAL_BUNDLE_FILES = (
    "integrity.json",
    "report.manager_snapshot.json",
    "report.md",
)


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _fmt_ts(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat()


def _safe_json_load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


class SqliteSnapshot:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.readable = False
        self.corrupt = False
        self.quick_check = "unknown"
        self.integrity = "unknown"
        self.conn: sqlite3.Connection | None = None
        self.tables: set[str] = set()
        self.views: set[str] = set()
        self.columns: dict[str, set[str]] = {}
        self._connect()

    def _connect(self) -> None:
        if not self.db_path.exists():
            return
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            conn.row_factory = sqlite3.Row
            quick = conn.execute("PRAGMA quick_check").fetchone()
            integrity = conn.execute("PRAGMA integrity_check").fetchone()
            self.quick_check = str(quick[0]) if quick else "unknown"
            self.integrity = str(integrity[0]) if integrity else "unknown"
            if self.quick_check != "ok":
                self.corrupt = True
                conn.close()
                return
            self.conn = conn
            self.readable = True
            rows = conn.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view')").fetchall()
            for row in rows:
                if row["type"] == "table":
                    self.tables.add(row["name"])
                if row["type"] == "view":
                    self.views.add(row["name"])
            for table in self.tables:
                cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
                self.columns[table] = {item["name"] for item in cols}
        except sqlite3.DatabaseError:
            self.corrupt = True
            self.readable = False

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()

    def has_table(self, name: str) -> bool:
        return name in self.tables

    def has_view(self, name: str) -> bool:
        return name in self.views

    def has_column(self, table: str, column: str) -> bool:
        return column in self.columns.get(table, set())

    def query(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if self.conn is None:
            return []
        try:
            rows = self.conn.execute(sql, params).fetchall()
        except sqlite3.DatabaseError:
            return []
        return [dict(row) for row in rows]

    def scalar(self, sql: str, params: tuple[Any, ...] = (), default: Any = None) -> Any:
        if self.conn is None:
            return default
        try:
            row = self.conn.execute(sql, params).fetchone()
        except sqlite3.DatabaseError:
            return default
        if row is None:
            return default
        if isinstance(row, sqlite3.Row):
            return row[0]
        return row[0] if row else default


class DashboardLoader:
    def __init__(self, *, state_dir: str | Path | None, db_path: str | Path | None, project_id: str | None = None):
        self.state_dir = Path(state_dir).resolve() if state_dir else None
        self.db_path = Path(db_path).resolve() if db_path else None
        self.project_id_arg = project_id

    def load(self) -> DashboardState:
        bundle = self._load_bundle()
        db = self._load_db()
        source_mode = self._source_mode(bundle, db)
        warnings: list[str] = []
        if db["corrupt"] and bundle["available"]:
            warnings.append("SQLite appears corrupt; using readable bundle fallback.")
        if db["corrupt"] and not bundle["available"]:
            raise RuntimeError("SQLite is not readable and no valid state bundle was found.")

        if not bundle["available"] and not db["available"]:
            raise RuntimeError("No readable source found. Provide --state-dir, --db, or both.")

        project_id = self.project_id_arg or bundle["project_id"] or db["project_id"] or "unknown-project"
        campaign_name = (
            bundle["campaign_summary"].get("campaign_title")
            or db["campaign_summary"].get("campaign_title")
            or project_id
        )
        stale_warning = self._bundle_stale_warning(bundle["last_export_time"], db["last_db_update"])
        bundle["stale_warning"] = stale_warning
        if stale_warning:
            warnings.append(bundle["stale_warning"])

        experiments = self._merge_experiments(bundle["experiments"], db["experiments"])
        scoreboard = bundle["scoreboard"] or db["scoreboard"]
        recurring_structures = self._merge_recurring_structures(
            bundle["recurring_structures"], db["recurring_structures"], experiments, project_id
        )
        active_queue = bundle["active_queue"] or db["active_queue"]
        incidents = bundle["incidents"] or db["incidents"]
        manager_snapshot = self._merge_manager_snapshot(bundle["manager_snapshot"], db["manager_snapshot"])

        snapshot = self._build_campaign_snapshot(
            project_id=project_id,
            campaign_name=campaign_name,
            campaign_summary=bundle["campaign_summary"] or db["campaign_summary"],
            scoreboard=scoreboard,
            recurring_structures=recurring_structures,
            incidents=incidents,
            db=db,
            bundle=bundle,
            source_mode=source_mode,
        )
        problems, problem_progress, falsehood_boundaries, pipeline = self._build_problem_sections(
            scoreboard=scoreboard,
            recurring_structures=recurring_structures,
            experiments=experiments,
            manager_snapshot=manager_snapshot,
        )
        recent_results = self._build_recent_results(experiments)
        manager_actions = self._build_manager_actions(
            active_queue=active_queue,
            manager_snapshot=manager_snapshot,
            recent_results=recent_results,
        )
        manager_reasoning = self._build_manager_reasoning(manager_snapshot)
        health = HealthStatus(
            source_mode=source_mode,
            db_path=str(self.db_path) if self.db_path else "",
            state_dir=str(self.state_dir) if self.state_dir else "",
            db_readable=db["available"],
            db_corrupt=db["corrupt"],
            db_integrity=db["integrity_status"],
            last_bundle_export=bundle["last_export_time"],
            last_db_update=db["last_db_update"],
            missing_files=bundle["missing_files"],
            stale_bundle_warning=bundle["stale_warning"],
            warnings=[*warnings],
        )
        provenance = {
            "campaign_snapshot": DataProvenance(source=snapshot.get("_source", source_mode), last_updated=snapshot.get("last_updated", "")),
            "knowledge_structure": DataProvenance(source="bundle" if bundle["recurring_structures"] else ("db" if db["recurring_structures"] else "derived")),
            "problem_progress": DataProvenance(source="derived", last_updated=snapshot.get("last_updated", "")),
            "falsehood_boundary": DataProvenance(source="derived", last_updated=snapshot.get("last_updated", "")),
            "recent_results": DataProvenance(source="bundle" if bundle["experiments"] else ("db" if db["experiments"] else "derived")),
            "manager_actions": DataProvenance(source="bundle" if bundle["active_queue"] else ("db" if db["active_queue"] else "derived")),
        }
        db["close"]()
        return DashboardState(
            project_id=project_id,
            campaign_name=campaign_name,
            source_mode=source_mode,
            campaign_snapshot={k: v for k, v in snapshot.items() if not k.startswith("_")},
            knowledge_structures=recurring_structures,
            problem_progress=problem_progress,
            falsehood_boundaries=falsehood_boundaries,
            knowledge_pipeline=pipeline,
            recent_results=recent_results,
            manager_actions=manager_actions,
            manager_reasoning=manager_reasoning,
            problems=problems,
            experiments={item["experiment_id"]: item for item in experiments if item.get("experiment_id")},
            provenance=provenance,
            health=health,
        )

    def _merge_manager_snapshot(self, bundle_snapshot: dict[str, Any], db_snapshot: dict[str, Any]) -> dict[str, Any]:
        if not bundle_snapshot:
            return db_snapshot
        if not db_snapshot:
            return bundle_snapshot
        merged = dict(db_snapshot)
        merged.update(bundle_snapshot)
        for key in ("campaign_interpretations", "bridge_hypotheses", "candidate_audits"):
            bundle_value = bundle_snapshot.get(key)
            db_value = db_snapshot.get(key)
            if bundle_value:
                merged[key] = bundle_value
            elif db_value:
                merged[key] = db_value
        return merged

    def _source_mode(self, bundle: dict[str, Any], db: dict[str, Any]) -> str:
        if bundle["available"] and db["available"]:
            return "mixed"
        if bundle["available"]:
            return "bundle"
        if db["available"]:
            return "db"
        return "none"

    def _bundle_stale_warning(self, bundle_ts: str, db_ts: str) -> str:
        bundle_time = _parse_ts(bundle_ts)
        db_time = _parse_ts(db_ts)
        if bundle_time is None or db_time is None:
            return ""
        lag = int((db_time - bundle_time).total_seconds())
        if lag > 120:
            return f"Bundle export is stale relative to DB by {lag} seconds."
        return ""

    def _load_bundle(self) -> dict[str, Any]:
        if self.state_dir is None:
            return {
                "available": False,
                "campaign_summary": {},
                "scoreboard": [],
                "recurring_structures": [],
                "active_queue": [],
                "incidents": [],
                "experiments": [],
                "manager_snapshot": {},
                "integrity": {},
                "missing_files": [],
                "project_id": "",
                "last_export_time": "",
                "stale_warning": "",
            }
        state_dir = self.state_dir
        missing = [name for name in REQUIRED_BUNDLE_FILES if not (state_dir / name).exists()]
        data: dict[str, Any] = {"available": len(missing) < len(REQUIRED_BUNDLE_FILES), "missing_files": missing}
        data["campaign_summary"] = _safe_json_load(state_dir / "campaign_summary.json") or {}
        data["scoreboard"] = _safe_json_load(state_dir / "conjecture_scoreboard.json") or []
        data["recurring_structures"] = _safe_json_load(state_dir / "recurring_structures.json") or []
        data["active_queue"] = _safe_json_load(state_dir / "active_queue.json") or []
        data["incidents"] = _safe_json_load(state_dir / "incidents.json") or []
        data["integrity"] = _safe_json_load(state_dir / "integrity.json") or {}
        data["manager_snapshot"] = _safe_json_load(state_dir / "report.manager_snapshot.json") or {}
        data["experiments"] = self._read_experiments_csv(state_dir / "experiments.csv")
        data["project_id"] = (
            data["campaign_summary"].get("project_id")
            or (data["scoreboard"][0].get("project_id") if data["scoreboard"] else "")
            or ""
        )
        latest_mtime = None
        for name in (*REQUIRED_BUNDLE_FILES, *OPTIONAL_BUNDLE_FILES):
            path = state_dir / name
            if path.exists():
                mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                latest_mtime = mtime if latest_mtime is None or mtime > latest_mtime else latest_mtime
        data["last_export_time"] = _fmt_ts(latest_mtime)
        data["stale_warning"] = ""
        return data

    def _read_experiments_csv(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(
                    {
                        "experiment_id": row.get("experiment_id", ""),
                        "project_id": row.get("project_id", ""),
                        "conjecture_id": row.get("conjecture_id", ""),
                        "phase": row.get("phase", ""),
                        "move": row.get("move", ""),
                        "move_family": row.get("move_family", "") or row.get("move", ""),
                        "status": row.get("status", ""),
                        "proof_outcome": row.get("proof_outcome", ""),
                        "blocker_type": row.get("blocker_type", ""),
                        "objective": row.get("objective", ""),
                        "expected_signal": row.get("expected_signal", ""),
                        "new_signal_count": int(row.get("new_signal_count", 0) or 0),
                        "reused_signal_count": int(row.get("reused_signal_count", 0) or 0),
                        "boundary_summary": row.get("boundary_summary", ""),
                        "motif_id": row.get("motif_id", ""),
                        "motif_signature": row.get("motif_signature", ""),
                        "created_at": row.get("created_at", ""),
                        "completed_at": row.get("completed_at", ""),
                        "missing_assumptions": [],
                        "counterexample_witnesses": [],
                        "rationale": "",
                    }
                )
        return rows

    def _load_db(self) -> dict[str, Any]:
        if self.db_path is None:
            return {
                "available": False,
                "corrupt": False,
                "integrity_status": "missing",
                "campaign_summary": {},
                "scoreboard": [],
                "recurring_structures": [],
                "active_queue": [],
                "incidents": [],
                "experiments": [],
                "manager_snapshot": {},
                "project_id": "",
                "last_db_update": "",
                "close": lambda: None,
            }
        snap = SqliteSnapshot(self.db_path)
        if not snap.readable:
            return {
                "available": False,
                "corrupt": snap.corrupt,
                "integrity_status": snap.quick_check,
                "campaign_summary": {},
                "scoreboard": [],
                "recurring_structures": [],
                "active_queue": [],
                "incidents": [],
                "experiments": [],
                "manager_snapshot": {},
                "project_id": "",
                "last_db_update": "",
                "close": snap.close,
            }
        project_id = self._infer_project_id_db(snap)
        campaign_summary = self._db_campaign_summary(snap, project_id)
        scoreboard = self._db_scoreboard(snap, project_id)
        recurring_structures = self._db_recurring_structures(snap, project_id)
        active_queue = self._db_active_queue(snap, project_id)
        incidents = self._db_incidents(snap, project_id)
        experiments = self._db_experiments(snap, project_id)
        manager_snapshot = self._db_manager_snapshot(snap, project_id)
        last_update = self._db_last_update(snap, project_id)
        return {
            "available": True,
            "corrupt": False,
            "integrity_status": snap.quick_check,
            "campaign_summary": campaign_summary,
            "scoreboard": scoreboard,
            "recurring_structures": recurring_structures,
            "active_queue": active_queue,
            "incidents": incidents,
            "experiments": experiments,
            "manager_snapshot": manager_snapshot,
            "project_id": project_id,
            "last_db_update": last_update,
            "close": snap.close,
        }

    def _infer_project_id_db(self, db: SqliteSnapshot) -> str:
        if self.project_id_arg:
            return self.project_id_arg
        rows = db.query("SELECT project_id FROM projects ORDER BY created_at DESC LIMIT 1")
        if rows:
            return rows[0]["project_id"]
        rows = db.query("SELECT DISTINCT project_id FROM experiments ORDER BY created_at DESC LIMIT 1")
        return rows[0]["project_id"] if rows else ""

    def _db_campaign_summary(self, db: SqliteSnapshot, project_id: str) -> dict[str, Any]:
        campaign_title = ""
        spec_title = ""
        if db.has_table("projects"):
            rows = db.query("SELECT title FROM projects WHERE project_id = ?", (project_id,))
            if rows:
                campaign_title = rows[0].get("title", "")
        if db.has_table("campaign_specs"):
            rows = db.query("SELECT spec_json FROM campaign_specs WHERE project_id = ?", (project_id,))
            if rows and rows[0].get("spec_json"):
                try:
                    spec_title = json.loads(rows[0]["spec_json"]).get("title", "")
                except Exception:
                    spec_title = ""
        counts = defaultdict(int)
        rows = db.query(
            "SELECT status, COUNT(*) as count FROM experiments WHERE project_id = ? GROUP BY status",
            (project_id,),
        )
        for row in rows:
            counts[row.get("status", "unknown")] = int(row.get("count", 0))
        nodes = db.scalar(
            "SELECT COUNT(*) FROM discovery_graph_nodes WHERE project_id = ?",
            (project_id,),
            default=0,
        ) if db.has_table("discovery_graph_nodes") else 0
        edges = db.scalar(
            "SELECT COUNT(*) FROM discovery_graph_edges WHERE project_id = ?",
            (project_id,),
            default=0,
        ) if db.has_table("discovery_graph_edges") else 0
        return {
            "project_id": project_id,
            "campaign_title": spec_title or campaign_title or project_id,
            "num_experiments": int(sum(counts.values())),
            "solved": int(counts.get("succeeded", 0)),
            "stalled": int(counts.get("stalled", 0)),
            "failed": int(counts.get("failed", 0)),
            "pending": int(counts.get("planned", 0) + counts.get("submitted", 0) + counts.get("in_progress", 0)),
            "open_incidents": [],
            "discovery_graph_counts": {"nodes": int(nodes), "edges": int(edges)},
        }

    def _db_scoreboard(self, db: SqliteSnapshot, project_id: str) -> list[dict[str, Any]]:
        if db.has_view("conjecture_scoreboard"):
            rows = db.query("SELECT * FROM conjecture_scoreboard WHERE project_id = ?", (project_id,))
            return rows
        query = """
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
                SUM(COALESCE(e.reused_signal_count, 0)) AS reused_signal_count
            FROM conjectures c
            LEFT JOIN experiments e ON e.conjecture_id = c.conjecture_id
            WHERE c.project_id = ?
            GROUP BY c.project_id, c.conjecture_id, c.name, c.domain
            ORDER BY c.conjecture_id
        """
        rows = db.query(query, (project_id,))
        for row in rows:
            row.setdefault("top_motif_reuse", 0)
            row.setdefault("recent_signal_velocity", 0.0)
        return rows

    def _db_recurring_structures(self, db: SqliteSnapshot, project_id: str) -> list[dict[str, Any]]:
        if db.has_view("recurring_structure_summary"):
            return db.query(
                "SELECT * FROM recurring_structure_summary WHERE project_id = ? ORDER BY observations DESC",
                (project_id,),
            )
        rows: list[dict[str, Any]] = []
        if db.has_table("lemmas") and db.has_table("lemma_occurrences"):
            rows.extend(
                db.query(
                    """
                    SELECT
                        ? AS project_id,
                        'lemma' AS structure_kind,
                        l.representative_statement AS summary_text,
                        l.reuse_count AS observations
                    FROM lemmas l
                    WHERE l.reuse_count >= 2
                    ORDER BY l.reuse_count DESC
                    """,
                    (project_id,),
                )
            )
        if db.has_table("extracted_subgoals"):
            rows.extend(
                db.query(
                    """
                    SELECT project_id, 'subgoal' AS structure_kind, statement AS summary_text, COUNT(*) AS observations
                    FROM extracted_subgoals
                    WHERE project_id = ?
                    GROUP BY project_id, statement
                    HAVING COUNT(*) >= 2
                    ORDER BY observations DESC
                    """,
                    (project_id,),
                )
            )
        if db.has_table("proof_trace_observations"):
            rows.extend(
                db.query(
                    """
                    SELECT project_id, 'proof_trace' AS structure_kind, normalized_fragment AS summary_text, COUNT(*) AS observations
                    FROM proof_trace_observations
                    WHERE project_id = ?
                    GROUP BY project_id, normalized_fragment
                    HAVING COUNT(*) >= 2
                    ORDER BY observations DESC
                    """,
                    (project_id,),
                )
            )
        if db.has_table("counterexample_observations"):
            rows.extend(
                db.query(
                    """
                    SELECT project_id, 'counterexample' AS structure_kind, normalized_witness AS summary_text, COUNT(*) AS observations
                    FROM counterexample_observations
                    WHERE project_id = ?
                    GROUP BY project_id, normalized_witness
                    HAVING COUNT(*) >= 2
                    ORDER BY observations DESC
                    """,
                    (project_id,),
                )
            )
        if db.has_table("blocker_observations"):
            rows.extend(
                db.query(
                    """
                    SELECT project_id, 'obstruction' AS structure_kind, blocker_type AS summary_text, COUNT(*) AS observations
                    FROM blocker_observations
                    WHERE project_id = ? AND blocker_type != 'unknown'
                    GROUP BY project_id, blocker_type
                    HAVING COUNT(*) >= 2
                    ORDER BY observations DESC
                    """,
                    (project_id,),
                )
            )
        rows.sort(key=lambda item: (-int(item.get("observations", 0)), item.get("summary_text", "")))
        return rows

    def _db_active_queue(self, db: SqliteSnapshot, project_id: str) -> list[dict[str, Any]]:
        if db.has_view("active_queue_summary"):
            return db.query("SELECT * FROM active_queue_summary WHERE project_id = ?", (project_id,))
        has_move_family = db.has_column("experiments", "move_family")
        has_candidate_metadata = db.has_column("experiments", "candidate_metadata_json")
        move_expr = "COALESCE(move_family, move)" if has_move_family else "move"
        motif_expr = (
            "MAX(COALESCE(json_extract(candidate_metadata_json, '$.motif_reuse_count'), 0))"
            if has_candidate_metadata
            else "0"
        )
        velocity_expr = (
            "MAX(COALESCE(json_extract(candidate_metadata_json, '$.recent_signal_velocity'), 0))"
            if has_candidate_metadata
            else "0"
        )
        return db.query(
            f"""
            SELECT
                project_id,
                conjecture_id,
                move,
                {move_expr} AS move_family,
                status,
                COUNT(*) AS active_count,
                {motif_expr} AS motif_reuse_count,
                {velocity_expr} AS recent_signal_velocity
            FROM experiments
            WHERE project_id = ? AND status IN ('planned', 'submitted', 'in_progress')
            GROUP BY project_id, conjecture_id, move, {move_expr}, status
            ORDER BY active_count DESC
            """,
            (project_id,),
        )

    def _db_incidents(self, db: SqliteSnapshot, project_id: str) -> list[dict[str, Any]]:
        if db.has_view("incident_summary"):
            return db.query("SELECT * FROM incident_summary WHERE project_id = ?", (project_id,))
        if not db.has_table("incidents"):
            return []
        return db.query(
            """
            SELECT
                project_id,
                incident_type,
                severity,
                status,
                COUNT(*) AS incident_count,
                MAX(updated_at) AS last_updated_at
            FROM incidents
            WHERE project_id = ?
            GROUP BY project_id, incident_type, severity, status
            ORDER BY incident_count DESC
            """,
            (project_id,),
        )

    def _db_experiments(self, db: SqliteSnapshot, project_id: str) -> list[dict[str, Any]]:
        if db.has_view("readable_experiments"):
            rows = db.query(
                "SELECT * FROM readable_experiments WHERE project_id = ? ORDER BY COALESCE(completed_at, created_at) DESC",
                (project_id,),
            )
            for row in rows:
                row.setdefault("missing_assumptions", [])
                row.setdefault("counterexample_witnesses", [])
                row.setdefault("rationale", "")
            return rows
        cols = db.columns.get("experiments", set())
        select_cols = [
            "experiment_id",
            "project_id",
            "conjecture_id",
            "phase",
            "move",
            "objective",
            "expected_signal",
            "status",
            "blocker_type",
            "proof_outcome",
            "new_signal_count",
            "reused_signal_count",
            "created_at",
            "completed_at",
        ]
        if "move_family" in cols:
            select_cols.append("move_family")
        if "candidate_metadata_json" in cols:
            select_cols.append("candidate_metadata_json")
        if "ingestion_json" in cols:
            select_cols.append("ingestion_json")
        if "rationale" in cols:
            select_cols.append("rationale")
        rows = db.query(
            f"SELECT {', '.join(select_cols)} FROM experiments WHERE project_id = ? ORDER BY COALESCE(completed_at, created_at) DESC",
            (project_id,),
        )
        normalized: list[dict[str, Any]] = []
        for row in rows:
            candidate = {}
            ingestion = {}
            if row.get("candidate_metadata_json"):
                try:
                    candidate = json.loads(row["candidate_metadata_json"])
                except Exception:
                    candidate = {}
            if row.get("ingestion_json"):
                try:
                    ingestion = json.loads(row["ingestion_json"])
                except Exception:
                    ingestion = {}
            normalized.append(
                {
                    "experiment_id": row.get("experiment_id", ""),
                    "project_id": row.get("project_id", ""),
                    "conjecture_id": row.get("conjecture_id", ""),
                    "phase": row.get("phase", ""),
                    "move": row.get("move", ""),
                    "move_family": row.get("move_family") or row.get("move", ""),
                    "status": row.get("status", ""),
                    "proof_outcome": row.get("proof_outcome", ""),
                    "blocker_type": row.get("blocker_type", ""),
                    "objective": row.get("objective", ""),
                    "expected_signal": row.get("expected_signal", ""),
                    "new_signal_count": int(row.get("new_signal_count") or 0),
                    "reused_signal_count": int(row.get("reused_signal_count") or 0),
                    "boundary_summary": (
                        (ingestion.get("boundary_map") or {}).get("summary")
                        if isinstance(ingestion.get("boundary_map"), dict)
                        else ""
                    ),
                    "motif_id": candidate.get("motif_id", ""),
                    "motif_signature": candidate.get("motif_signature", ""),
                    "created_at": row.get("created_at", ""),
                    "completed_at": row.get("completed_at", ""),
                    "missing_assumptions": ingestion.get("missing_assumptions") or [],
                    "counterexample_witnesses": ingestion.get("counterexample_witnesses") or [],
                    "rationale": row.get("rationale", ""),
                }
            )
        return normalized

    def _db_manager_snapshot(self, db: SqliteSnapshot, project_id: str) -> dict[str, Any]:
        if not db.has_table("manager_runs"):
            return {}
        rows = db.query(
            """
            SELECT run_id, summary_json, created_at, completed_at
            FROM manager_runs
            WHERE project_id = ?
            ORDER BY completed_at DESC, created_at DESC
            LIMIT 1
            """,
            (project_id,),
        )
        if not rows:
            return {}
        row = rows[0]
        try:
            summary = json.loads(row.get("summary_json") or "{}")
        except Exception:
            summary = {}
        summary["manager_run_id"] = row.get("run_id", "")
        summary["completed_at"] = row.get("completed_at", "") or row.get("created_at", "")
        if db.has_table("manager_candidate_audits"):
            audits = db.query(
                """
                SELECT rank_position, selected, policy_score, selection_reason, candidate_json, experiment_id, conjecture_id
                FROM manager_candidate_audits
                WHERE run_id = ?
                ORDER BY rank_position ASC
                """,
                (row.get("run_id", ""),),
            )
            parsed = []
            for audit in audits:
                candidate = {}
                if audit.get("candidate_json"):
                    try:
                        candidate = json.loads(audit["candidate_json"])
                    except Exception:
                        candidate = {}
                parsed.append({**audit, "candidate": candidate})
            summary["candidate_audits"] = parsed
        if db.has_table("campaign_interpretations"):
            interpretation_rows = db.query(
                """
                SELECT interpretation_id, prompt_version, model_version, raw_response, parsed_json, validation_status, created_at
                FROM campaign_interpretations
                WHERE project_id = ?
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (project_id,),
            )
            parsed_interpretations = []
            for item in interpretation_rows:
                parsed_json = {}
                if item.get("parsed_json"):
                    try:
                        parsed_json = json.loads(item["parsed_json"])
                    except Exception:
                        parsed_json = {}
                parsed_interpretations.append({**item, "parsed": parsed_json})
            summary["campaign_interpretations"] = parsed_interpretations
        if db.has_table("bridge_hypotheses"):
            bridge_rows = db.query(
                """
                SELECT source_conjecture_id, target_conjecture_id, suggested_move_family, confidence, hypothesis_json, created_at
                FROM bridge_hypotheses
                WHERE project_id = ?
                ORDER BY confidence DESC, created_at DESC
                LIMIT 10
                """,
                (project_id,),
            )
            parsed_bridges = []
            for item in bridge_rows:
                hypothesis = {}
                if item.get("hypothesis_json"):
                    try:
                        hypothesis = json.loads(item["hypothesis_json"])
                    except Exception:
                        hypothesis = {}
                parsed_bridges.append({**item, "hypothesis": hypothesis})
            summary["bridge_hypotheses"] = parsed_bridges
        return summary

    def _db_last_update(self, db: SqliteSnapshot, project_id: str) -> str:
        values: list[str] = []
        if db.has_table("experiments"):
            row = db.query(
                """
                SELECT MAX(COALESCE(completed_at, created_at)) AS ts
                FROM experiments
                WHERE project_id = ?
                """,
                (project_id,),
            )
            if row and row[0].get("ts"):
                values.append(row[0]["ts"])
        if db.has_table("manager_runs"):
            row = db.query(
                "SELECT MAX(COALESCE(completed_at, created_at)) AS ts FROM manager_runs WHERE project_id = ?",
                (project_id,),
            )
            if row and row[0].get("ts"):
                values.append(row[0]["ts"])
        parsed = [item for item in (_parse_ts(value) for value in values) if item is not None]
        return _fmt_ts(max(parsed)) if parsed else ""

    def _merge_experiments(self, bundle_rows: list[dict[str, Any]], db_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_id: dict[str, dict[str, Any]] = {}
        for row in db_rows:
            by_id[row.get("experiment_id", "")] = row
        for row in bundle_rows:
            if row.get("experiment_id") not in by_id:
                by_id[row.get("experiment_id", "")] = row
        rows = list(by_id.values())
        rows.sort(key=lambda item: _parse_ts(item.get("completed_at") or item.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return rows

    def _merge_recurring_structures(
        self,
        bundle_rows: list[dict[str, Any]],
        db_rows: list[dict[str, Any]],
        experiments: list[dict[str, Any]],
        project_id: str,
    ) -> list[dict[str, Any]]:
        base_rows = bundle_rows or db_rows
        by_key: dict[str, dict[str, Any]] = {}
        conjecture_refs = defaultdict(set)
        for exp in experiments:
            cid = exp.get("conjecture_id", "")
            motif = exp.get("motif_signature") or exp.get("motif_id") or ""
            if cid and motif:
                conjecture_refs[normalized_name(motif)].add(cid)
            for witness in exp.get("counterexample_witnesses", []) or []:
                if cid and witness:
                    conjecture_refs[normalized_name(str(witness))].add(cid)
        for row in base_rows:
            name = row.get("summary_text") or row.get("name") or row.get("statement") or row.get("fragment") or row.get("witness") or ""
            if not name:
                continue
            raw_kind = row.get("structure_kind") or row.get("type") or row.get("kind") or ""
            normalized_type, role = normalize_structure_type(str(raw_kind), str(name))
            reuse = int(row.get("observations", row.get("reuse_count", row.get("reuse", 0))) or 0)
            touches = set()
            if isinstance(row.get("conjecture_ids"), list):
                touches.update(row["conjecture_ids"])
            if row.get("conjecture_id"):
                touches.add(row["conjecture_id"])
            touches.update(conjecture_refs.get(normalized_name(str(name)), set()))
            key = f"{normalized_type}:{normalized_name(str(name))}"
            by_key[key] = {
                "name": str(name),
                "type": normalized_type,
                "reuse_count": reuse,
                "role": role,
                "status": structure_status_from_reuse(reuse),
                "touches": sorted(t for t in touches if t),
                "project_id": project_id,
            }
        required_types = {
            "recurring lemma",
            "recurring subgoal",
            "recurring proof trace",
            "witness motif",
            "boundary fact / obstruction",
        }
        present_types = {item["type"] for item in by_key.values()}
        if "boundary fact / obstruction" not in present_types:
            blockers = Counter(exp.get("blocker_type", "") for exp in experiments if exp.get("blocker_type") and exp.get("blocker_type") != "unknown")
            for blocker, count in blockers.most_common(3):
                key = f"boundary fact / obstruction:{normalized_name(blocker)}"
                by_key[key] = {
                    "name": blocker,
                    "type": "boundary fact / obstruction",
                    "reuse_count": int(count),
                    "role": "recurring blocker or boundary condition",
                    "status": structure_status_from_reuse(int(count)),
                    "touches": sorted({exp.get('conjecture_id', '') for exp in experiments if exp.get("blocker_type") == blocker and exp.get("conjecture_id")}),
                    "project_id": project_id,
                }
        for missing_type in required_types - {item["type"] for item in by_key.values()}:
            key = f"{missing_type}:none"
            by_key[key] = {
                "name": "none observed yet",
                "type": missing_type,
                "reuse_count": 0,
                "role": "no recurring item captured",
                "status": "early",
                "touches": [],
                "project_id": project_id,
            }
        rows = list(by_key.values())
        rows.sort(key=lambda item: (-int(item["reuse_count"]), item["type"], item["name"]))
        return rows

    def _build_campaign_snapshot(
        self,
        *,
        project_id: str,
        campaign_name: str,
        campaign_summary: dict[str, Any],
        scoreboard: list[dict[str, Any]],
        recurring_structures: list[dict[str, Any]],
        incidents: list[dict[str, Any]],
        db: dict[str, Any],
        bundle: dict[str, Any],
        source_mode: str,
    ) -> dict[str, Any]:
        total_experiments = sum(int(item.get("experiments_total", 0) or 0) for item in scoreboard) or int(campaign_summary.get("num_experiments", 0) or 0)
        active = int(campaign_summary.get("pending", 0) or 0)
        failed = sum(int(item.get("failed", 0) or 0) for item in scoreboard) or int(campaign_summary.get("failed", 0) or 0)
        stalled = sum(int(item.get("stalled", 0) or 0) for item in scoreboard) or int(campaign_summary.get("stalled", 0) or 0)
        nodes = int((campaign_summary.get("discovery_graph_counts") or {}).get("nodes", 0) or 0)
        edges = int((campaign_summary.get("discovery_graph_counts") or {}).get("edges", 0) or 0)
        open_incidents = sum(int(item.get("incident_count", 0) or 0) for item in incidents if (item.get("status") or "open") == "open")
        recurring_clusters = len([item for item in recurring_structures if int(item.get("reuse_count", 0) or 0) > 0])
        db_health = "ok" if db["available"] and db["integrity_status"] == "ok" else ("corrupt" if db["corrupt"] else "unknown")
        last_updated = db["last_db_update"] or bundle["last_export_time"]
        source = "bundle" if source_mode == "bundle" else ("db" if source_mode == "db" else "mixed")
        return {
            "_source": source,
            "last_updated": last_updated,
            "project_id": project_id,
            "campaign_name": campaign_name,
            "manager_status": "running" if active > 0 else "idle",
            "total_experiments": total_experiments,
            "failed": failed,
            "stalled": stalled,
            "active": active,
            "graph_nodes": nodes,
            "graph_edges": edges,
            "recurring_cluster_count": recurring_clusters,
            "open_incidents": open_incidents,
            "db_health": db_health,
            "integrity_status": db["integrity_status"],
            "last_export_time": bundle["last_export_time"],
            "last_db_update": db["last_db_update"],
            "source_mode": source_mode,
        }

    def _build_problem_sections(
        self,
        *,
        scoreboard: list[dict[str, Any]],
        recurring_structures: list[dict[str, Any]],
        experiments: list[dict[str, Any]],
        manager_snapshot: dict[str, Any],
    ) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        by_problem = {item.get("conjecture_id", ""): item for item in scoreboard if item.get("conjecture_id")}
        for exp in experiments:
            cid = exp.get("conjecture_id", "")
            if not cid:
                continue
            by_problem.setdefault(cid, {"conjecture_id": cid, "experiments_total": 0, "new_signal_count": 0, "name": cid})
        structures_by_problem = defaultdict(list)
        for row in recurring_structures:
            for cid in row.get("touches", []):
                structures_by_problem[cid].append(row)
        exps_by_problem = defaultdict(list)
        missing_by_problem = defaultdict(list)
        witnesses_by_problem = defaultdict(list)
        for exp in experiments:
            cid = exp.get("conjecture_id", "")
            if not cid:
                continue
            exps_by_problem[cid].append(exp)
            missing_by_problem[cid].extend(exp.get("missing_assumptions") or [])
            witnesses_by_problem[cid].extend([str(w) for w in (exp.get("counterexample_witnesses") or []) if w])

        problem_rows: list[dict[str, Any]] = []
        boundary_rows: list[dict[str, Any]] = []
        problems_detail: dict[str, dict[str, Any]] = {}
        for cid, score in sorted(by_problem.items(), key=lambda item: item[0]):
            exp_rows = exps_by_problem[cid]
            structure_rows = structures_by_problem[cid]
            top_motif = choose_strongest_motif(cid, experiments, recurring_structures)
            top_obstruction = choose_strongest_obstruction(cid, experiments, missing_by_problem)
            lemma_count = len([s for s in structure_rows if s["type"] == "recurring lemma" and s["reuse_count"] >= 2])
            subgoal_count = len([s for s in structure_rows if s["type"] == "recurring subgoal" and s["reuse_count"] >= 2])
            trace_count = len([s for s in structure_rows if s["type"] == "recurring proof trace" and s["reuse_count"] >= 2])
            recurring_reuse = sum(int(s["reuse_count"]) for s in structure_rows if int(s["reuse_count"]) >= 2)
            witness_density = (
                len(witnesses_by_problem[cid]) / max(1, len(exp_rows))
                if exp_rows
                else 0.0
            )
            recent_signal_velocity = float(score.get("recent_signal_velocity", 0) or 0)
            traction = classify_proof_traction(
                experiments_count=int(score.get("experiments_total", len(exp_rows)) or len(exp_rows)),
                recurring_reuse=recurring_reuse,
                stabilized_lemmas=lemma_count,
                recurring_subgoals=subgoal_count,
                recurring_traces=trace_count,
                witness_density=witness_density,
                recent_signal_velocity=recent_signal_velocity,
            )
            current_route, missing = summarize_problem_progress(
                conjecture_id=cid,
                experiments_count=int(score.get("experiments_total", len(exp_rows)) or len(exp_rows)),
                new_signals=int(score.get("new_signal_count", 0) or 0),
                traction=traction,
                strongest_motif=top_motif,
                strongest_obstruction=top_obstruction,
                missing_assumptions=missing_by_problem[cid],
            )
            disproved = len([item for item in exp_rows if (item.get("proof_outcome") or "").lower() == "disproved"])
            repair_hints = self._repair_hints_for_problem(cid, manager_snapshot, exp_rows)
            boundary = summarize_falsehood_boundary(
                conjecture_id=cid,
                disproved_count=disproved,
                witness_regions=witnesses_by_problem[cid],
                missing_assumptions=missing_by_problem[cid],
                salvage_hints=repair_hints,
            )
            row = {
                "conjecture_id": cid,
                "conjecture_name": score.get("name", cid),
                "experiments_count": int(score.get("experiments_total", len(exp_rows)) or len(exp_rows)),
                "total_new_signals": int(score.get("new_signal_count", 0) or 0),
                "strongest_motif": top_motif,
                "strongest_obstruction": top_obstruction,
                "proof_traction_state": traction,
                "current_best_route": current_route,
                "what_is_still_missing": missing,
                "falsehood_boundary_status": boundary["falsified_weakened_variants"],
                "structure_reuse": recurring_reuse,
                "lemma_stability": lemma_count,
                "subgoal_convergence": subgoal_count,
                "trace_convergence": trace_count,
            }
            problem_rows.append(row)
            boundary_rows.append(boundary)
            problems_detail[cid] = {
                **row,
                "recent_results": self._build_recent_results(exp_rows, limit=8),
                "structures": sorted(structure_rows, key=lambda item: (-int(item["reuse_count"]), item["name"])),
                "falsehood_boundary": boundary,
            }
        problem_rows.sort(key=lambda item: (-int(item["total_new_signals"]), item["conjecture_id"]))
        boundary_rows.sort(key=lambda item: item["conjecture_id"])
        pipeline = self._knowledge_pipeline(problem_rows, recurring_structures, experiments)
        return problems_detail, problem_rows, boundary_rows, pipeline

    def _repair_hints_for_problem(
        self,
        conjecture_id: str,
        manager_snapshot: dict[str, Any],
        experiments: list[dict[str, Any]],
    ) -> list[str]:
        hints: list[str] = []
        for item in manager_snapshot.get("submitted_experiments", []):
            if item.get("conjecture_id") == conjecture_id:
                reason = item.get("reason")
                if reason:
                    hints.append(str(reason))
        for exp in experiments[:6]:
            if exp.get("rationale"):
                hints.append(str(exp["rationale"]))
        return hints[:3]

    def _knowledge_pipeline(
        self,
        problem_rows: list[dict[str, Any]],
        recurring_structures: list[dict[str, Any]],
        experiments: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        signals = sum(int(item.get("new_signal_count", 0) or 0) for item in experiments)
        lemma_candidates = len([s for s in recurring_structures if s["type"] == "recurring lemma" and s["reuse_count"] >= 2])
        subgoals = len([s for s in recurring_structures if s["type"] == "recurring subgoal" and s["reuse_count"] >= 2])
        traces = len([s for s in recurring_structures if s["type"] == "recurring proof trace" and s["reuse_count"] >= 2])
        witness = len([s for s in recurring_structures if s["type"] == "witness motif" and s["reuse_count"] >= 2])
        transfer = len([s for s in recurring_structures if len(s.get("touches", [])) > 1])
        solved = len([item for item in problem_rows if item.get("proof_traction_state") == "closure-attempt ready"])
        return [
            {"label": "signals discovered", "value": signals, "source": "derived"},
            {"label": "recurring structures", "value": len([s for s in recurring_structures if s["reuse_count"] > 0]), "source": "derived"},
            {"label": "reusable lemma candidates", "value": lemma_candidates, "source": "derived"},
            {"label": "stabilized recurring subgoals", "value": subgoals, "source": "derived"},
            {"label": "stabilized recurring proof traces", "value": traces, "source": "derived"},
            {"label": "witness motifs", "value": witness, "source": "derived"},
            {"label": "transferred structures across problems", "value": transfer, "source": "derived"},
            {"label": "original problems solved", "value": solved, "source": "derived"},
        ]

    def _build_recent_results(self, experiments: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
        rows = []
        for exp in experiments[:limit]:
            row = {
                "experiment_id": exp.get("experiment_id", ""),
                "conjecture_id": exp.get("conjecture_id", ""),
                "move": exp.get("move", ""),
                "move_family": exp.get("move_family") or exp.get("move", ""),
                "status": exp.get("status", ""),
                "proof_outcome": exp.get("proof_outcome", ""),
                "new_signal_count": int(exp.get("new_signal_count", 0) or 0),
                "reused_signal_count": int(exp.get("reused_signal_count", 0) or 0),
                "created_at": exp.get("created_at", ""),
                "completed_at": exp.get("completed_at", ""),
                "interpretation": summarize_recent_result(exp),
            }
            rows.append(row)
        return rows

    def _build_manager_actions(
        self,
        *,
        active_queue: list[dict[str, Any]],
        manager_snapshot: dict[str, Any],
        recent_results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        priority = 1
        audits = manager_snapshot.get("candidate_audits", []) or []
        if audits:
            for item in audits[:25]:
                candidate = item.get("candidate", {}) if isinstance(item.get("candidate"), dict) else {}
                metadata = candidate.get("candidate_metadata", {}) if isinstance(candidate.get("candidate_metadata"), dict) else {}
                actions.append(
                    {
                        "priority": priority,
                        "problem": item.get("conjecture_id") or candidate.get("conjecture_id", ""),
                        "move": candidate.get("move_family") or candidate.get("move", ""),
                        "rationale": item.get("selection_reason") or candidate.get("rationale", ""),
                        "motif_id": metadata.get("motif_id", ""),
                        "motif_signature": metadata.get("motif_signature", ""),
                        "expected_signal": candidate.get("expected_signal", ""),
                        "reuse_potential": metadata.get("reuse_potential", 0),
                        "blocker_support": metadata.get("blocker_support", 0),
                        "witness_support": metadata.get("witness_support", 0),
                        "recent_signal_velocity": metadata.get("recent_signal_velocity", 0),
                    }
                )
                priority += 1
            return actions

        velocity_by_problem = Counter()
        for row in recent_results:
            velocity_by_problem[row.get("conjecture_id", "")] += int(row.get("new_signal_count", 0) or 0)
        for item in active_queue:
            actions.append(
                {
                    "priority": priority,
                    "problem": item.get("conjecture_id", ""),
                    "move": item.get("move_family", item.get("move", "")),
                    "rationale": "active queue candidate",
                    "motif_id": "",
                    "motif_signature": "",
                    "expected_signal": "",
                    "reuse_potential": item.get("motif_reuse_count", 0),
                    "blocker_support": 0,
                    "witness_support": 0,
                    "recent_signal_velocity": item.get("recent_signal_velocity", velocity_by_problem.get(item.get("conjecture_id", ""), 0)),
                }
            )
            priority += 1
        actions.sort(key=lambda row: (-float(row.get("reuse_potential", 0) or 0), -float(row.get("recent_signal_velocity", 0) or 0), row.get("problem", "")))
        for idx, action in enumerate(actions, start=1):
            action["priority"] = idx
        return actions[:25]

    def _build_manager_reasoning(self, manager_snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        manager_prompt = manager_snapshot.get("manager_prompt", "")
        policy_rationale = manager_snapshot.get("policy_rationale", "")
        if manager_prompt or policy_rationale:
            rows.append(
                {
                    "kind": "manager_tick",
                    "title": "Latest manager prompt and rationale",
                    "created_at": manager_snapshot.get("completed_at", ""),
                    "summary": policy_rationale or "Manager reasoning summary",
                    "prompt": manager_prompt,
                    "raw_response": manager_snapshot.get("raw_response", ""),
                }
            )
        for item in manager_snapshot.get("campaign_interpretations", [])[:3]:
            raw_response = item.get("raw_response", "")
            reasoning = ""
            if raw_response:
                try:
                    parsed_raw = json.loads(raw_response)
                    if isinstance(parsed_raw, dict):
                        reasoning = (
                            str(parsed_raw.get("manager_reasoning", ""))
                            or str(parsed_raw.get("reasoning_content", ""))
                        )
                except Exception:
                    reasoning = ""
            rows.append(
                {
                    "kind": "campaign_interpretation",
                    "title": f"Interpretation {item.get('interpretation_id', '')}",
                    "created_at": item.get("created_at", ""),
                    "summary": item.get("parsed", {}).get("phase_assessment", item.get("validation_status", "")),
                    "prompt": "",
                    "raw_response": raw_response,
                    "reasoning": reasoning,
                }
            )
        for item in manager_snapshot.get("bridge_hypotheses", [])[:5]:
            hypothesis = item.get("hypothesis", {})
            rows.append(
                {
                    "kind": "bridge_hypothesis",
                    "title": f"{item.get('source_conjecture_id', '')} -> {item.get('target_conjecture_id', '')}",
                    "created_at": item.get("created_at", ""),
                    "summary": hypothesis.get("shared_structure", ""),
                    "prompt": "",
                    "raw_response": json.dumps(hypothesis, indent=2) if hypothesis else "",
                    "reasoning": hypothesis.get("transfer_rationale", ""),
                }
            )
        for audit in (manager_snapshot.get("candidate_audits") or [])[:10]:
            candidate = audit.get("candidate", {}) if isinstance(audit.get("candidate"), dict) else {}
            annotation = candidate.get("llm_annotation") or candidate.get("candidate_metadata", {}).get("llm_annotation", {})
            if not annotation:
                continue
            rows.append(
                {
                    "kind": "candidate_annotation",
                    "title": candidate.get("experiment_id", audit.get("experiment_id", "")),
                    "created_at": manager_snapshot.get("completed_at", ""),
                    "summary": annotation.get("mathematical_rationale", "") or audit.get("selection_reason", ""),
                    "prompt": "",
                    "raw_response": json.dumps(annotation, indent=2),
                    "reasoning": annotation.get("expected_discovery", ""),
                }
            )
        return rows[:20]


def dashboard_state_to_dict(state: DashboardState) -> dict[str, Any]:
    payload = asdict(state)
    payload["provenance"] = {key: asdict(value) for key, value in state.provenance.items()}
    payload["health"] = asdict(state.health)
    return payload
