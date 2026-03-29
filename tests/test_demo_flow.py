import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import shutil
import tempfile
import unittest
from pathlib import Path

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import run_one_cycle
from research_orchestrator.reporter import build_report


class DemoFlowTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="research_orchestrator_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
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

    def test_cycle_creates_experiment_and_report(self):
        result = run_one_cycle(self.db, self.project_id, "mock", self.tempdir / "work")
        summary = self.db.project_summary(self.project_id)
        report = build_report(self.db, self.project_id)
        self.assertGreaterEqual(summary["num_experiments"], 1)
        self.assertIn("Research Report", report)
        self.assertIn(result["brief"].experiment_id, report)
        workspace = Path(result["brief"].workspace_dir)
        self.assertTrue((workspace / "lean-toolchain").exists())
        self.assertTrue((workspace / "lakefile.toml").exists())


if __name__ == "__main__":
    unittest.main()
