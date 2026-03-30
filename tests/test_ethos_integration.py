import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest
from collections import Counter, defaultdict

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import manager_tick


class EthosIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="ethos_integration_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.db.save_project(charter)
        for name in (
            "erdos_123_d_complete_sequences.json",
            "erdos_181_hypercube_ramsey.json",
            "erdos_44_sidon_extension.json",
        ):
            conjecture = load_conjecture(root / "examples" / "conjectures" / "erdos" / name)
            self.db.save_conjecture(conjecture)
        self.project_id = charter.project_id
        self.report_path = self.tempdir / "report.md"
        self.snapshot_path = self.tempdir / "report.manager_snapshot.json"

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def _run_ticks(self, count: int) -> None:
        for idx in range(count):
            manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="mock",
                workspace_root=self.tempdir / "work" / f"tick_{idx}",
                max_active=5,
                max_submit_per_tick=5,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )

    def test_multi_tick_campaign_expresses_verification_as_discovery(self):
        self._run_ticks(7)

        experiments = self.db.list_experiments(self.project_id)
        completed = self.db.list_completed_experiments(self.project_id, limit=100)
        recurring_lemmas = self.db.recurring_lemmas()
        assumption_sensitivity = self.db.assumption_sensitivity(self.project_id)
        recurring_subgoals = self.db.recurring_subgoals(self.project_id)
        discovery_nodes = self.db.list_discovery_nodes(self.project_id)
        report = self.report_path.read_text(encoding="utf-8")

        self.assertEqual(len(experiments), 21)
        self.assertEqual(len(completed), 21)

        moves_by_conjecture = defaultdict(set)
        signalful_moves = set()
        for experiment in experiments:
            moves_by_conjecture[experiment["conjecture_id"]].add(experiment["move"])
            if (experiment.get("new_signal_count") or 0) > 0:
                signalful_moves.add(experiment["move"])

        for conjecture_id, moves in moves_by_conjecture.items():
            self.assertIn("underspecify", moves, conjecture_id)
            self.assertIn("perturb_assumption", moves, conjecture_id)
            self.assertIn("promote_lemma", moves, conjecture_id)

        self.assertIn("underspecify", signalful_moves)
        self.assertIn("perturb_assumption", signalful_moves)
        self.assertTrue(
            any(
                item["move"] in {"promote_lemma", "reformulate"} and item["proof_outcome"] == "proved"
                for item in completed
            )
        )

        proof_outcomes = Counter(item["proof_outcome"] for item in completed)
        self.assertGreater(proof_outcomes["partial"], 0)
        self.assertGreater(proof_outcomes["proved"], 0)

        self.assertTrue(recurring_lemmas)
        self.assertTrue(assumption_sensitivity)
        self.assertTrue(recurring_subgoals)

        node_types = Counter(item["node_type"] for item in discovery_nodes)
        self.assertGreater(node_types["experiment"], 0)
        self.assertGreater(node_types["verified_lemma"], 0)
        self.assertGreater(node_types["assumption_boundary"], 0)
        self.assertGreater(node_types["recurring_subgoal"], 0)

        self.assertIn("Discovery Graph", report)
        self.assertIn("Recurring lemmas", report)
        self.assertIn("Assumption sensitivity", report)
        self.assertIn("What we learned", report)


if __name__ == "__main__":
    unittest.main()
