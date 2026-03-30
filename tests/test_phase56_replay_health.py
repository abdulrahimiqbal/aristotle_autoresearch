import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.cli import cmd_campaign_health
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import manager_tick, run_one_cycle
from research_orchestrator.replay import replay_experiment, replay_manager_run
from research_orchestrator.types import ProviderResult


class AsyncProviderStub:
    name = "aristotle-cli"
    supports_async = True

    def __init__(self):
        self.submissions = 0

    def submit(self, charter, conjecture, brief, worker_prompt):
        self.submissions += 1
        return ProviderResult(
            status="submitted",
            blocker_type="unknown",
            notes="submitted",
            external_id=f"job-{self.submissions}",
            external_status="QUEUED",
        )

    def poll(self, charter, conjecture, brief, worker_prompt, external_id, submitted_at=""):
        return ProviderResult(
            status="succeeded",
            blocker_type="unknown",
            notes="completed",
            raw_stdout="Proof complete. All goals solved.",
            proved_lemmas=[f"{brief.experiment_id}_lemma : True"],
            external_id=external_id,
            external_status="COMPLETE",
            artifacts=[str(Path(brief.workspace_dir) / "result.lean")],
        )


class Phase56ReplayHealthTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="phase56_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        self.charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.conjecture = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_123_d_complete_sequences.json")
        self.db.save_project(self.charter)
        self.db.save_conjecture(self.conjecture)
        self.project_id = self.charter.project_id
        self.report_path = self.tempdir / "report.md"
        self.snapshot_path = self.tempdir / "report.manager_snapshot.json"

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_run_cycle_persists_replay_manifest(self):
        result = run_one_cycle(self.db, self.project_id, "mock", self.tempdir / "work")
        manifests = self.db.list_experiment_manifests(result["brief"].experiment_id)
        self.assertGreaterEqual(len(manifests), 2)
        finalized = manifests[-1]["manifest"]
        self.assertEqual(finalized["experiment_id"], result["brief"].experiment_id)
        self.assertIn("versions", finalized)
        self.assertIn("provider", finalized)
        self.assertIn("workspace", finalized)
        self.assertIn("move_parameters", finalized)

    def test_manager_tick_persists_candidate_audit_and_health_snapshot(self):
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            result = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=1,
                max_submit_per_tick=1,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        audits = self.db.list_manager_candidate_audits(result["run_id"])
        self.assertTrue(audits)
        self.assertTrue(any(item["selected"] for item in audits))
        health = self.db.latest_campaign_health_snapshot(self.project_id)
        self.assertIsNotNone(health)
        self.assertIn("signals", health["health"])

    def test_replay_experiment_detects_version_drift(self):
        result = run_one_cycle(self.db, self.project_id, "mock", self.tempdir / "work")
        manifest_row = self.db.latest_experiment_manifest(result["brief"].experiment_id, snapshot_kind="finalized")
        manifest = manifest_row["manifest"]
        manifest["versions"]["evaluator_version"] = "2026.02.legacy"
        self.db.conn.execute(
            "UPDATE experiment_manifests SET manifest_json = ?, evaluator_version = ? WHERE snapshot_id = ?",
            (json.dumps(manifest), "2026.02.legacy", manifest_row["snapshot_id"]),
        )
        self.db.conn.commit()
        replayed = replay_experiment(self.db, result["brief"].experiment_id)
        self.assertIn("evaluator_version", replayed["version_drift"])
        self.assertIsInstance(replayed["current_evaluation"]["total"], float)

    def test_missing_manifest_degrades_gracefully(self):
        result = run_one_cycle(self.db, self.project_id, "mock", self.tempdir / "work")
        self.db.conn.execute(
            "DELETE FROM experiment_manifests WHERE experiment_id = ?",
            (result["brief"].experiment_id,),
        )
        self.db.conn.commit()
        replayed = replay_experiment(self.db, result["brief"].experiment_id)
        self.assertEqual(replayed["snapshot_kind"], "reconstructed")

    def test_campaign_health_and_runtime_controls_are_reported(self):
        submitted_at = (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat()
        last_synced_at = (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat()
        self.db.save_experiment_plan(
            {
                "experiment_id": "stuck-exp",
                "project_id": self.project_id,
                "conjecture_id": self.conjecture.conjecture_id,
                "phase": "mapping",
                "move": "underspecify",
                "objective": "seed",
                "expected_signal": "seed",
                "modification": {"mode": "minimal_context"},
                "workspace_dir": str(self.tempdir / "stuck"),
                "lean_file": str(self.tempdir / "stuck" / "Main.lean"),
                "external_id": "job-stuck",
                "external_status": "IN_PROGRESS",
                "submitted_at": submitted_at,
                "last_synced_at": last_synced_at,
            }
        )
        self.db.conn.execute(
            """
            UPDATE experiments
            SET provider = 'aristotle-cli',
                status = 'in_progress',
                attempt_count = 6
            WHERE experiment_id = 'stuck-exp'
            """
        )
        self.db.conn.commit()
        health = self.db.campaign_health(self.project_id)
        self.assertEqual(health["counts"]["active"], 1)
        self.assertTrue(health["runtime_controls"]["stuck_runs"])

    def test_replay_manager_run_is_deterministic(self):
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            result = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=1,
                max_submit_per_tick=1,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        replayed = replay_manager_run(self.db, result["run_id"])
        self.assertFalse(replayed["selection_changed"])
        self.assertEqual(len(replayed["historical_selected"]), 1)

    def test_campaign_health_cli_json_is_parseable(self):
        result = run_one_cycle(self.db, self.project_id, "mock", self.tempdir / "work")
        _ = result
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cmd_campaign_health(type("Args", (), {"db": str(self.db.path), "project": self.project_id, "format": "json"})())
        payload = json.loads(buffer.getvalue())
        self.assertIn("counts", payload)
        self.assertIn("signals", payload)


if __name__ == "__main__":
    unittest.main()
