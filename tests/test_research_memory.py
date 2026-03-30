import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest
from pathlib import Path

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.experiment_generator import choose_move
from research_orchestrator.lemma_utils import normalize_goal, normalize_lemma


class ResearchMemoryTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="research_memory_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        self.charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.conjecture = load_conjecture(
            root / "examples" / "conjectures" / "erdos" / "erdos_123_d_complete_sequences.json"
        )
        self.db.save_project(self.charter)
        self.db.save_conjecture(self.conjecture)

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_recurring_subgoals_are_aggregated(self):
        for idx in range(2):
            experiment_id = f"exp-{idx}"
            self.db.save_experiment_plan(
                {
                    "experiment_id": experiment_id,
                    "project_id": self.charter.project_id,
                    "conjecture_id": self.conjecture.conjecture_id,
                    "phase": "mapping",
                    "move": "underspecify",
                    "objective": "seed",
                    "expected_signal": "seed",
                    "modification": {"mode": f"seed-{idx}"},
                    "workspace_dir": str(self.tempdir / experiment_id),
                    "lean_file": str(self.tempdir / experiment_id / "Main.lean"),
                }
            )
            self.db.record_result_ingestion(
                experiment_id=experiment_id,
                project_id=self.charter.project_id,
                conjecture_id=self.conjecture.conjecture_id,
                proof_outcome="partial",
                blocker_type="formalization",
                unresolved_goals=["show coverage_bound"],
                artifact_inventory=[],
                signal_summary="Repeated subgoal observed while reconstructing coverage.",
            )

        recurring = self.db.recurring_subgoals(self.charter.project_id)
        self.assertEqual(len(recurring), 1)
        self.assertEqual(recurring[0]["statement"], normalize_goal("show coverage_bound"))
        self.assertEqual(recurring[0]["observations"], 2)

    def test_normalization_collapses_variable_renaming_for_goals_and_lemmas(self):
        self.assertEqual(
            normalize_lemma("lemma bridge (n : Nat) : P n"),
            normalize_lemma("lemma bridge (m : Nat) : P m"),
        )
        self.assertEqual(
            normalize_goal("show P n"),
            normalize_goal("goal: P m"),
        )

    def test_no_signal_branches_are_aggregated(self):
        for idx in range(2):
            experiment_id = f"nosignal-{idx}"
            self.db.save_experiment_plan(
                {
                    "experiment_id": experiment_id,
                    "project_id": self.charter.project_id,
                    "conjecture_id": self.conjecture.conjecture_id,
                    "phase": "consolidation",
                    "move": "counterexample_mode",
                    "objective": "seed",
                    "expected_signal": "seed",
                    "modification": {"target": "most_fragile_variant"},
                    "workspace_dir": str(self.tempdir / experiment_id),
                    "lean_file": str(self.tempdir / experiment_id / "Main.lean"),
                }
            )
            self.db.conn.execute(
                """
                UPDATE experiments
                SET status = 'stalled', proof_outcome = 'unknown', new_signal_count = 0
                WHERE experiment_id = ?
                """,
                (experiment_id,),
            )
        self.db.conn.commit()
        rows = self.db.no_signal_branches(self.charter.project_id)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["move"], "counterexample_mode")

    def test_recurring_lemma_signal_can_trigger_promotion(self):
        experiments = [
            {
                "conjecture_id": self.conjecture.conjecture_id,
                "move": "underspecify",
                "modification": {"mode": "minimal_context"},
                "status": "stalled",
                "blocker_type": "formalization",
            }
        ]
        for assumption in self.conjecture.assumptions:
            experiments.append(
                {
                    "conjecture_id": self.conjecture.conjecture_id,
                    "move": "perturb_assumption",
                    "modification": {"assumption": assumption, "operation": "remove"},
                    "status": "stalled",
                    "blocker_type": "formalization",
                }
            )

        recurring_lemmas = [
            {
                "representative_statement": "lemma coverage_bridge : True",
                "reuse_count": self.charter.promotion_threshold,
                "conjecture_ids": [self.conjecture.conjecture_id],
            }
        ]

        move, modification, _, _ = choose_move(
            charter=self.charter,
            conjecture=self.conjecture,
            experiments=experiments,
            recurring_lemmas=recurring_lemmas,
        )
        self.assertEqual(move, "promote_lemma")
        self.assertEqual(modification["lemma_statement"], "lemma coverage_bridge : True")

    def test_recurring_subgoal_can_trigger_promotion(self):
        experiments = [
            {
                "conjecture_id": self.conjecture.conjecture_id,
                "move": "underspecify",
                "modification": {"mode": "minimal_context"},
                "status": "stalled",
                "blocker_type": "formalization",
                "proof_outcome": "partial",
                "new_signal_count": 1,
            }
        ]
        for assumption in self.conjecture.assumptions:
            experiments.append(
                {
                    "conjecture_id": self.conjecture.conjecture_id,
                    "move": "perturb_assumption",
                    "modification": {"assumption": assumption, "operation": "remove"},
                    "status": "stalled",
                    "blocker_type": "formalization",
                    "proof_outcome": "partial",
                    "new_signal_count": 1,
                }
            )

        move, modification, _, _ = choose_move(
            charter=self.charter,
            conjecture=self.conjecture,
            experiments=experiments,
            recurring_lemmas=[],
            recurring_subgoals=[{"statement": normalize_goal("show coverage_bound"), "observations": 3}],
        )
        self.assertEqual(move, "promote_lemma")
        self.assertEqual(modification["lemma_statement"], normalize_goal("show coverage_bound"))


if __name__ == "__main__":
    unittest.main()
