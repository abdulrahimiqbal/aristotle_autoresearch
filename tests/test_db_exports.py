import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import json
import shutil
import tempfile
import unittest

from research_orchestrator.campaign_planner import synthesize_campaign
from research_orchestrator.db import Database


class DatabaseExportsTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="db_exports_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        spec, charter, conjectures, questions = synthesize_campaign("Erdos problem 44")
        self.spec = spec
        self.db.save_project(charter)
        self.db.save_campaign_spec(spec)
        for conjecture in conjectures:
            self.db.save_conjecture(conjecture)
        for question in questions:
            self.db.save_discovery_question(question)
        self.db.save_experiment_plan(
            {
                "experiment_id": "exp-1",
                "project_id": spec.project_id,
                "conjecture_id": conjectures[0].conjecture_id,
                "phase": "mapping",
                "move": "promote_subgoal",
                "objective": "promote recurring goal",
                "expected_signal": "find reusable bottleneck",
                "modification": {"subgoal_statement": "show density bound"},
                "workspace_dir": str(self.tempdir / "work"),
                "lean_file": str(self.tempdir / "work" / "Main.lean"),
                "status": "planned",
                "candidate_metadata": {
                    "motif_id": "subgoal:show density bound",
                    "motif_signature": "subgoal:show density bound",
                    "motif_reuse_count": 3,
                    "signal_support": 2,
                    "campaign_priority": 1,
                },
            }
        )

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_integrity_helpers_and_snapshot_work(self):
        self.assertEqual(self.db.quick_check(), ["ok"])
        self.assertEqual(self.db.integrity_check(), ["ok"])
        backup = self.tempdir / "backup.sqlite"
        snapshot = self.tempdir / "snapshot.sqlite"
        self.db.backup_to(backup)
        self.db.atomic_snapshot_to(snapshot)
        self.assertTrue(backup.exists())
        self.assertTrue(snapshot.exists())

    def test_readable_exports_include_expected_files_and_keys(self):
        output_dir = self.tempdir / "exports"
        written = self.db.export_readable_state(self.spec.project_id, output_dir)
        self.assertIn("campaign_summary.json", written)
        self.assertIn("experiments.csv", written)
        campaign_summary = json.loads((output_dir / "campaign_summary.json").read_text(encoding="utf-8"))
        self.assertIn("campaign_title", campaign_summary)
        scoreboard = json.loads((output_dir / "conjecture_scoreboard.json").read_text(encoding="utf-8"))
        self.assertTrue(scoreboard)
        recurring = json.loads((output_dir / "recurring_structures.json").read_text(encoding="utf-8"))
        self.assertIsInstance(recurring, list)
        csv_text = (output_dir / "experiments.csv").read_text(encoding="utf-8")
        self.assertIn("motif_id", csv_text)


if __name__ == "__main__":
    unittest.main()
