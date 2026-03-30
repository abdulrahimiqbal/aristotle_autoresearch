import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.providers.aristotle_cli import AristotleCLIProvider


class StaleActiveRecoveryTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="stale_active_recovery_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        self.charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.conjecture = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_123_d_complete_sequences.json")
        self.db.save_project(self.charter)
        self.db.save_conjecture(self.conjecture)

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_stale_active_expiry(self):
        submitted_at = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        last_synced_at = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        self.db.save_experiment_plan(
            {
                "experiment_id": "stale-exp",
                "project_id": self.charter.project_id,
                "conjecture_id": self.conjecture.conjecture_id,
                "phase": "mapping",
                "move": "underspecify",
                "objective": "seed stale job",
                "expected_signal": "seed",
                "modification": {"mode": "minimal_context"},
                "workspace_dir": str(self.tempdir / "work"),
                "lean_file": str(self.tempdir / "work" / "Main.lean"),
                "external_id": "job-stale-123",
                "external_status": "IN_PROGRESS",
                "submitted_at": submitted_at,
                "last_synced_at": last_synced_at,
            }
        )
        self.db.conn.execute(
            """
            UPDATE experiments
            SET provider = 'aristotle-cli',
                status = 'submitted',
                blocker_type = 'unknown'
            WHERE experiment_id = 'stale-exp'
            """
        )
        self.db.conn.commit()

        expired = self.db.expire_stale_active_experiments(self.charter.project_id, max_age_seconds=7200)

        self.assertEqual(expired, 1)
        experiment = self.db.get_experiment("stale-exp")
        self.assertEqual(experiment["status"], "failed")
        self.assertEqual(experiment["external_status"], "EXPIRED")
        incidents = self.db.list_incidents(self.charter.project_id, status="open")
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0]["incident_type"], "stale_active_timeout")

    def test_poll_marks_old_ghost_job_failed(self):
        provider = AristotleCLIProvider()
        brief = type(
            "Brief",
            (),
            {
                "workspace_dir": str(self.tempdir),
                "objective": "ghost objective",
                "experiment_id": "ghost-exp",
            },
        )()
        submitted_at = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()

        with patch.object(provider, "_status_for_project", return_value=("UNKNOWN", "", "")):
            result = provider.poll(
                charter=self.charter,
                conjecture=self.conjecture,
                brief=brief,
                worker_prompt="",
                external_id="ghost-job-123",
                submitted_at=submitted_at,
            )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.metadata.get("incident_type"), "ghost_job")
        self.assertIn("disappeared from the remote listing", result.notes)


if __name__ == "__main__":
    unittest.main()
