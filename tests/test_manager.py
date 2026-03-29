import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import shutil
import tempfile
import unittest
from pathlib import Path

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.manager import choose_next_experiment


class ManagerTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="manager_test_"))
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

    def test_first_move_is_underspecify(self):
        brief, manager_prompt, frontier = choose_next_experiment(self.db, self.project_id, self.tempdir / "work")
        self.assertEqual(brief.move, "underspecify")
        self.assertTrue(frontier)
        self.assertIn("Choose exactly one next experiment", manager_prompt)


if __name__ == "__main__":
    unittest.main()
