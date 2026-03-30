import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.manager import generate_frontier
from research_orchestrator.manager_policy import choose_candidates_for_submission
from research_orchestrator.types import ProviderResult


class RichFrontierTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="rich_frontier_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.db.save_project(charter)
        first = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_123_d_complete_sequences.json")
        second = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_44_sidon_extension.json")
        second.domain = "finite geometry constructions"
        first.candidate_transfer_domains = ["finite geometry constructions"]
        self.db.save_conjecture(first)
        self.db.save_conjecture(second)
        self.project_id = charter.project_id
        self.first_id = first.conjecture_id
        self.second_id = second.conjecture_id

        self.db.save_experiment_plan(
            {
                "experiment_id": "seed-1",
                "project_id": self.project_id,
                "conjecture_id": self.first_id,
                "phase": "mapping",
                "move": "underspecify",
                "move_family": "legacy.underspecify",
                "objective": "seed",
                "expected_signal": "seed",
                "modification": {"mode": "minimal_context"},
                "workspace_dir": str(self.tempdir / "seed-1"),
                "lean_file": str(self.tempdir / "seed-1" / "Main.lean"),
                "candidate_metadata": {"novelty_score": 1.0},
            }
        )
        self.db.update_experiment_result(
            "seed-1",
            "mock",
            ProviderResult(
                status="stalled",
                blocker_type="formalization",
                proof_outcome="partial",
                generated_lemmas=["chain transfer bridge"],
                proof_trace_fragments=["reduce to density increment"],
                new_signal_count=2,
                verification_record=None,
                semantic_summary=None,
            ),
            evaluation={"total": 2.7},
        )

        self.db.save_experiment_plan(
            {
                "experiment_id": "seed-2",
                "project_id": self.project_id,
                "conjecture_id": self.second_id,
                "phase": "mapping",
                "move": "promote_lemma",
                "move_family": "legacy.promote_lemma",
                "objective": "seed",
                "expected_signal": "seed",
                "modification": {"lemma_statement": "chain transfer bridge"},
                "workspace_dir": str(self.tempdir / "seed-2"),
                "lean_file": str(self.tempdir / "seed-2" / "Main.lean"),
                "candidate_metadata": {"reuse_potential": 2.0},
            }
        )
        self.db.update_experiment_result(
            "seed-2",
            "mock",
            ProviderResult(
                status="succeeded",
                blocker_type="unknown",
                proof_outcome="proved",
                proved_lemmas=["chain transfer bridge"],
                new_signal_count=1,
                verification_record=None,
                semantic_summary=None,
            ),
            evaluation={"total": 3.1},
        )

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_frontier_contains_richer_move_metadata_and_transfer_candidates(self):
        frontier = generate_frontier(self.db, self.project_id, self.tempdir / "work")
        move_families = {item["move_family"] for item in frontier}
        self.assertIn("transfer_reformulation", move_families)
        self.assertIn("invariant_mining", move_families)
        transfer_items = [item for item in frontier if item["move_family"] == "transfer_reformulation"]
        self.assertTrue(transfer_items)
        self.assertGreater(transfer_items[0]["transfer_opportunity"], 0)

    def test_policy_prefers_cross_conjecture_diversity_even_with_richer_frontier(self):
        frontier = generate_frontier(self.db, self.project_id, self.tempdir / "work")
        policy = choose_candidates_for_submission(
            db=self.db,
            project_id=self.project_id,
            frontier=frontier,
            max_count=3,
            llm_manager_mode="off",
        )
        conjecture_ids = {item.conjecture_id for item in policy.chosen}
        self.assertEqual(conjecture_ids, {self.first_id, self.second_id})


if __name__ == "__main__":
    unittest.main()
