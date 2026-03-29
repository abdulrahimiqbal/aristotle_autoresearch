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


class MultiConjectureManagerTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="multiconjecture_manager_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        first = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_123_d_complete_sequences.json")
        second = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_181_hypercube_ramsey.json")
        self.db.save_project(charter)
        self.db.save_conjecture(first)
        self.db.save_conjecture(second)
        self.project_id = charter.project_id
        self.first_id = first.conjecture_id
        self.second_id = second.conjecture_id

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_manager_rotates_to_less_explored_conjecture(self):
        brief, _, _ = choose_next_experiment(self.db, self.project_id, self.tempdir / "work")
        self.assertEqual(brief.conjecture_id, self.first_id)

        self.db.save_experiment_plan(brief.__dict__)

        next_brief, _, frontier = choose_next_experiment(self.db, self.project_id, self.tempdir / "work")
        self.assertEqual(next_brief.conjecture_id, self.second_id)
        self.assertTrue(any(item["existing_experiments"] == 0 for item in frontier))


if __name__ == "__main__":
    unittest.main()
