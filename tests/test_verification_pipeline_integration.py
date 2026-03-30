import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import sqlite3
import tempfile
import unittest

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import run_one_cycle
from research_orchestrator.reporter import build_report


class VerificationPipelineIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="verification_pipeline_test_"))
        self.db_path = self.tempdir / "state.sqlite"
        self.db = Database(self.db_path)
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        charter = load_charter(root / "examples" / "project_charter.json")
        conjecture = load_conjecture(root / "examples" / "conjectures" / "weighted_monotone.json")
        self.db.save_project(charter)
        self.db.save_conjecture(conjecture)
        self.project_id = charter.project_id

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_structured_result_is_persisted_and_report_generation_still_works(self):
        cycle = run_one_cycle(self.db, self.project_id, "mock", self.tempdir / "work")
        experiment = self.db.get_experiment(cycle["brief"].experiment_id)
        self.assertIn("verification_record", experiment["ingestion"])
        self.assertIn("semantic_summary", experiment["ingestion"])
        verification_rows = self.db.conn.execute("SELECT * FROM verification_records").fetchall()
        semantic_rows = self.db.conn.execute("SELECT * FROM semantic_objects").fetchall()
        self.assertEqual(len(verification_rows), 1)
        self.assertGreaterEqual(len(semantic_rows), 1)
        report = build_report(self.db, self.project_id)
        self.assertIn("Research Report", report)
        self.assertIn(cycle["brief"].experiment_id, report)

    def test_validation_issues_become_incidents(self):
        self.db.save_experiment_plan(
            {
                "experiment_id": "manual-exp",
                "project_id": self.project_id,
                "conjecture_id": self.db.list_conjectures(self.project_id)[0].conjecture_id,
                "phase": "mapping",
                "move": "underspecify",
                "objective": "manual",
                "expected_signal": "manual",
                "modification": {"mode": "manual"},
                "workspace_dir": str(self.tempdir / "manual"),
                "lean_file": str(self.tempdir / "manual" / "Main.lean"),
            }
        )
        from research_orchestrator.orchestrator import _finalize_result
        from research_orchestrator.types import ProviderResult, VerificationRecord

        _finalize_result(
            db=self.db,
            project_id=self.project_id,
            provider_name="mock",
            brief=type(
                "Brief",
                (),
                {
                    "experiment_id": "manual-exp",
                    "project_id": self.project_id,
                    "conjecture_id": self.db.list_conjectures(self.project_id)[0].conjecture_id,
                    "move": "underspecify",
                    "phase": "mapping",
                    "discovery_question_id": "",
                    "modification": {},
                },
            )(),
            result=ProviderResult(
                status="failed",
                blocker_type="unknown",
                metadata={"provider_name": "mock"},
                verification_record=VerificationRecord(schema_version="999", verification_status="bad"),
            ),
            manager_lint=type("Lint", (), {"ok": True})(),
            worker_lint=type("Lint", (), {"ok": True})(),
        )
        incidents = self.db.list_incidents(self.project_id, status="open")
        self.assertTrue(any(item["incident_type"].startswith("verification_validation_") for item in incidents))

    def test_initialize_adds_new_columns_to_old_database(self):
        legacy_path = self.tempdir / "legacy.sqlite"
        conn = sqlite3.connect(legacy_path)
        conn.execute(
            """
            CREATE TABLE experiments (
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
                completed_at TEXT
            )
            """
        )
        conn.commit()
        conn.close()

        migrated = Database(legacy_path)
        migrated.initialize()
        columns = {row["name"] for row in migrated.conn.execute("PRAGMA table_info(experiments)").fetchall()}
        self.assertIn("verification_schema_version", columns)
        self.assertIn("semantic_memory_version", columns)
        self.assertIn("evaluator_version", columns)
        migrated.close()


if __name__ == "__main__":
    unittest.main()
