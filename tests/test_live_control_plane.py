import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import tempfile
import unittest
from pathlib import Path

from research_orchestrator.db import Database
from research_orchestrator.route_planner import assign_routes_to_frontier
from research_orchestrator.live_projections import refresh_live_projections
from research_orchestrator.types import ProjectCharter, Conjecture


class LiveControlPlaneTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="live_control_plane_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        charter = ProjectCharter(
            project_id="proj-test",
            title="Test Project",
            overarching_problem="Test",
            success_criteria=["test"],
            non_goals=[],
            allowed_moves=["underspecify"],
            phase_order=["mapping"],
        )
        conjecture = Conjecture(
            conjecture_id="c1",
            project_id="proj-test",
            name="C1",
            domain="combinatorics",
            natural_language="Test",
            lean_statement="theorem t : True := by trivial",
        )
        self.db.save_project(charter)
        self.db.save_conjecture(conjecture)

    def tearDown(self):
        self.db.close()

    def test_route_assignment_creates_routes(self):
        frontier = [
            {
                "experiment_id": "e1",
                "project_id": "proj-test",
                "conjecture_id": "c1",
                "phase": "mapping",
                "move": "underspecify",
                "move_family": "underspecify",
                "objective": "test",
                "expected_signal": "signal",
                "modification": {},
                "workspace_dir": "/tmp",
                "lean_file": "/tmp/test.lean",
                "candidate_metadata": {"motif_signature": "motif-a", "signal_support": 1},
            }
        ]
        updated, scores = assign_routes_to_frontier(self.db, "proj-test", frontier)
        self.assertTrue(updated[0].get("route_id"))
        self.assertTrue(scores)
        routes = self.db.list_theorem_routes("proj-test")
        self.assertTrue(routes)

    def test_events_refresh_projections(self):
        event = self.db.emit_manager_event(
            project_id="proj-test",
            run_id="run-test",
            event_type="manager.tick.started",
            source_component="manager",
            payload={"summary": "started"},
        )
        refresh_live_projections(self.db, "proj-test", run_id="run-test")
        rows = self.db.conn.execute(
            "SELECT event_id FROM live_manager_timeline WHERE project_id = ?",
            ("proj-test",),
        ).fetchall()
        self.assertTrue(rows)
        self.assertEqual(rows[0][0], event["event_id"])


if __name__ == "__main__":
    unittest.main()
