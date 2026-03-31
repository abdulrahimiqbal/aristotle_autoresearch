import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest

from research_orchestrator.campaign_planner import DEFAULT_ALLOWED_MOVES, synthesize_campaign
from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.experiment_generator import generate_move_candidates, select_discovery_question
from research_orchestrator.manager_policy import choose_candidates_for_submission
from research_orchestrator.db import Database
from research_orchestrator.types import Conjecture


class MotifRefactorTest(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        for move in DEFAULT_ALLOWED_MOVES:
            if move not in self.charter.allowed_moves:
                self.charter.allowed_moves.append(move)
        self.conjecture = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_123_d_complete_sequences.json")
        self.tempdir = Path(tempfile.mkdtemp(prefix="motif_refactor_test_"))

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_planner_default_moves_include_new_families(self):
        for move in (
            "promote_subgoal",
            "promote_trace",
            "boundary_map_from_witness",
            "boundary_map_from_missing_assumption",
        ):
            self.assertIn(move, DEFAULT_ALLOWED_MOVES)

    def test_discovery_question_selection_is_scored_not_positional(self):
        selected = select_discovery_question(
            conjecture=self.conjecture,
            discovery_questions=[
                {
                    "question_id": "q-first",
                    "question": "What other reformulation should we try next?",
                    "priority": 100,
                    "status": "open",
                },
                {
                    "question_id": "q-best",
                    "question": "Which covering bottleneck subgoal is recurring and should be promoted?",
                    "priority": 90,
                    "status": "open",
                },
            ],
            recurring_lemmas=[],
            recurring_subgoals=[{"statement": "covering bottleneck subgoal", "observations": 4}],
            recurring_proof_traces=[],
            recent_signal_counter={"covering bottleneck subgoal": 3},
            blocker_signals=["covering bottleneck"],
        )
        self.assertEqual(selected["question_id"], "q-best")

    def test_multiple_candidates_emerge_from_one_strong_motif_cluster(self):
        experiments = [
            {
                "experiment_id": "exp-1",
                "conjecture_id": self.conjecture.conjecture_id,
                "move": "reformulate",
                "modification": {"form": "equivalent reformulation"},
                "status": "stalled",
                "proof_outcome": "partial",
                "new_signal_count": 2,
                "reused_signal_count": 1,
                "ingestion": {
                    "proof_trace_fragments": ["covering bottleneck"],
                    "unresolved_goals": ["covering bottleneck subgoal"],
                    "blocked_on": ["covering bottleneck"],
                },
            }
        ]
        candidates = generate_move_candidates(
            charter=self.charter,
            conjecture=self.conjecture,
            experiments=experiments,
            recurring_lemmas=[],
            recurring_subgoals=[{"statement": "covering bottleneck subgoal", "observations": 4}],
            recurring_proof_traces=[{"fragment": "covering bottleneck", "observations": 3}],
        )
        motif_candidates = [item for item in candidates if item.move_family in {"promote_subgoal", "promote_trace"}]
        self.assertGreaterEqual(len(motif_candidates), 2)
        self.assertTrue(all(item.generation_metadata.get("motif_id") for item in motif_candidates))

    def test_boundary_followups_appear_after_witness_and_missing_assumption(self):
        experiments = [
            {
                "experiment_id": "exp-2",
                "conjecture_id": self.conjecture.conjecture_id,
                "move": "counterexample_mode",
                "modification": {"target": "boundary_variant"},
                "status": "failed",
                "proof_outcome": "disproved",
                "new_signal_count": 1,
                "reused_signal_count": 0,
                "ingestion": {
                    "counterexample_witnesses": ["n = 7"],
                    "missing_assumptions": ["pairwise_distinct"],
                    "blocked_on": ["density repair"],
                    "boundary_map": {"summary": "fragile_variant, witness-backed false region, likely salvageable with assumption repair"},
                },
            }
        ]
        candidates = generate_move_candidates(
            charter=self.charter,
            conjecture=self.conjecture,
            experiments=experiments,
            recurring_lemmas=[],
        )
        moves = {item.move_family for item in candidates}
        self.assertIn("boundary_map_from_witness", moves)
        self.assertIn("boundary_map_from_missing_assumption", moves)

    def test_policy_exploits_dominant_motif_without_losing_all_diversity(self):
        db = Database(self.tempdir / "state.sqlite")
        db.initialize()
        spec, charter, conjectures, questions = synthesize_campaign("Erdos problem 123")
        db.save_project(charter)
        db.save_campaign_spec(spec)
        for conjecture in conjectures:
            db.save_conjecture(conjecture)
        alternate = Conjecture(
            conjecture_id=f"{conjectures[0].conjecture_id}-alt",
            project_id=spec.project_id,
            name="alternate conjecture",
            domain=conjectures[0].domain,
            natural_language="alternate branch",
            lean_statement=conjectures[0].lean_statement,
        )
        db.save_conjecture(alternate)
        for question in questions:
            db.save_discovery_question(question)
        frontier = [
            {
                "experiment_id": "dom-1",
                "conjecture_id": conjectures[0].conjecture_id,
                "move": "promote_subgoal",
                "move_family": "promote_subgoal",
                "phase": "excavation",
                "objective": "promote",
                "expected_signal": "signal",
                "modification": {"subgoal_statement": "covering bottleneck"},
                "workspace_dir": str(self.tempdir / "w1"),
                "lean_file": str(self.tempdir / "w1" / "Main.lean"),
                "existing_experiments": 2,
                "active_count_for_conjecture": 0,
                "duplicate_active_signature": False,
                "targets_recurring_structure": True,
                "signal_priority": 2,
                "no_signal_penalty": 0,
                "semantic_novelty": 1.0,
                "reuse_potential": 1.5,
                "obstruction_targeting": 1.0,
                "transfer_opportunity": 0.0,
                "campaign_priority": 1.0,
                "discovery_priority": 90,
                "motif_id": "subgoal:covering bottleneck",
                "motif_reuse_count": 4.0,
                "signal_support": 4.0,
                "blocker_support": 2.0,
                "witness_support": 0.0,
                "assumption_boundary_support": 0.0,
                "recent_signal_velocity": 3.0,
                "candidate_metadata": {"motif_id": "subgoal:covering bottleneck"},
                "rationale": "dominant motif",
            },
            {
                "experiment_id": "dom-2",
                "conjecture_id": conjectures[0].conjecture_id,
                "move": "promote_trace",
                "move_family": "promote_trace",
                "phase": "excavation",
                "objective": "trace",
                "expected_signal": "signal",
                "modification": {"trace_fragment": "covering bottleneck"},
                "workspace_dir": str(self.tempdir / "w2"),
                "lean_file": str(self.tempdir / "w2" / "Main.lean"),
                "existing_experiments": 3,
                "active_count_for_conjecture": 0,
                "duplicate_active_signature": False,
                "targets_recurring_structure": True,
                "signal_priority": 2,
                "no_signal_penalty": 0,
                "semantic_novelty": 0.9,
                "reuse_potential": 1.3,
                "obstruction_targeting": 1.1,
                "transfer_opportunity": 0.0,
                "campaign_priority": 1.0,
                "discovery_priority": 80,
                "motif_id": "trace:covering bottleneck",
                "motif_reuse_count": 3.5,
                "signal_support": 3.0,
                "blocker_support": 2.0,
                "witness_support": 0.0,
                "assumption_boundary_support": 0.0,
                "recent_signal_velocity": 2.5,
                "candidate_metadata": {"motif_id": "trace:covering bottleneck"},
                "rationale": "same branch strong",
            },
            {
                "experiment_id": "explore-1",
                "conjecture_id": alternate.conjecture_id,
                "move": "reformulate",
                "move_family": "legacy.reformulate",
                "phase": "mapping",
                "objective": "explore",
                "expected_signal": "signal",
                "modification": {"form": "equivalent reformulation"},
                "workspace_dir": str(self.tempdir / "w3"),
                "lean_file": str(self.tempdir / "w3" / "Main.lean"),
                "existing_experiments": 0,
                "active_count_for_conjecture": 0,
                "duplicate_active_signature": False,
                "targets_recurring_structure": False,
                "signal_priority": 1,
                "no_signal_penalty": 0,
                "semantic_novelty": 0.8,
                "reuse_potential": 0.7,
                "obstruction_targeting": 0.6,
                "transfer_opportunity": 0.0,
                "campaign_priority": 0.2,
                "discovery_priority": 70,
                "motif_id": "reform:equivalent",
                "motif_reuse_count": 0.5,
                "signal_support": 0.0,
                "blocker_support": 0.0,
                "witness_support": 0.0,
                "assumption_boundary_support": 0.0,
                "recent_signal_velocity": 0.1,
                "candidate_metadata": {"motif_id": "reform:equivalent"},
                "rationale": "keep some exploration",
            },
        ]
        decision = choose_candidates_for_submission(
            db=db,
            project_id=spec.project_id,
            frontier=frontier,
            max_count=2,
            llm_manager_mode="off",
        )
        chosen_ids = [item.experiment_id for item in decision.chosen]
        self.assertIn("dom-1", chosen_ids)
        self.assertIn("explore-1", chosen_ids)
        db.close()


if __name__ == "__main__":
    unittest.main()
