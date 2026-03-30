import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.experiment_generator import build_move_generation_context, generate_move_candidates
from research_orchestrator.move_registry import DEFAULT_MOVE_REGISTRY


class MoveRegistryTest(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.charter = load_charter(root / "examples" / "project_charter.json")
        self.conjecture = load_conjecture(root / "examples" / "conjectures" / "weighted_monotone.json")

    def test_legacy_families_are_registered(self):
        families = {spec.move_family: spec.legacy_move for spec in DEFAULT_MOVE_REGISTRY.all_specs()}
        self.assertEqual(families["legacy.underspecify"], "underspecify")
        self.assertEqual(families["legacy.perturb_assumption"], "perturb_assumption")
        self.assertEqual(families["legacy.reformulate"], "reformulate")
        self.assertEqual(families["legacy.promote_lemma"], "promote_lemma")
        self.assertEqual(families["legacy.counterexample_mode"], "counterexample_mode")

    def test_generation_is_deterministic_and_inapplicable_moves_are_filtered(self):
        first = [
            (item.move_family, item.legacy_move, item.parameters)
            for item in generate_move_candidates(
                charter=self.charter,
                conjecture=self.conjecture,
                experiments=[],
                recurring_lemmas=[],
            )
        ]
        second = [
            (item.move_family, item.legacy_move, item.parameters)
            for item in generate_move_candidates(
                charter=self.charter,
                conjecture=self.conjecture,
                experiments=[],
                recurring_lemmas=[],
            )
        ]
        self.assertEqual(first, second)
        move_families = {item[0] for item in first}
        self.assertIn("legacy.underspecify", move_families)
        self.assertNotIn("invariant_mining", move_families)
        self.assertNotIn("adversarial_counterexample", move_families)
        self.assertNotIn("transfer_reformulation", move_families)

    def test_duplicate_equivalent_candidates_are_suppressed(self):
        self.conjecture.equivalent_forms = [
            "chain cover formulation",
            "chain cover formulation",
            "geometric packing formulation",
        ]
        candidates = generate_move_candidates(
            charter=self.charter,
            conjecture=self.conjecture,
            experiments=[],
            recurring_lemmas=[],
        )
        reformulations = [item for item in candidates if item.legacy_move == "reformulate"]
        forms = [item.parameters.get("form") for item in reformulations]
        self.assertEqual(forms.count("chain cover formulation"), 1)

    def test_semantic_and_transfer_signals_generate_richer_moves(self):
        other = load_conjecture(Path(__file__).resolve().parents[1] / "examples" / "conjectures" / "erdos" / "erdos_44_sidon_extension.json")
        other.project_id = self.conjecture.project_id
        other.domain = "lattice theory"
        experiments = [
            {
                "conjecture_id": self.conjecture.conjecture_id,
                "move": "underspecify",
                "move_family": "legacy.underspecify",
                "modification": {"mode": "minimal_context"},
                "status": "stalled",
                "proof_outcome": "partial",
                "new_signal_count": 2,
                "blocker_type": "formalization",
                "ingestion": {
                    "semantic_summary": {
                        "artifacts": [
                            {"kind": "blocker", "canonical_text": "need chain decomposition"},
                            {"kind": "proof_trace", "canonical_text": "reduce to chain bound"},
                            {"kind": "counterexample", "canonical_text": "minimal threshold witness"},
                        ]
                    }
                },
                "outcome": {"evaluation": {"total": 3.2}},
            },
            {
                "conjecture_id": other.conjecture_id,
                "move": "promote_lemma",
                "move_family": "legacy.promote_lemma",
                "modification": {"lemma_statement": "transfer bridge"},
                "status": "succeeded",
                "proof_outcome": "proved",
                "new_signal_count": 1,
                "blocker_type": "unknown",
                "ingestion": {
                    "semantic_summary": {
                        "artifacts": [
                            {"kind": "lemma", "canonical_text": "transfer bridge"},
                        ]
                    }
                },
                "outcome": {"evaluation": {"total": 2.8}},
            },
        ]
        candidates = generate_move_candidates(
            charter=self.charter,
            conjecture=self.conjecture,
            experiments=experiments,
            recurring_lemmas=[],
            recurring_subgoals=[{"statement": "show coverage_bound", "observations": 3}],
            recurring_proof_traces=[{"fragment": "reduce to chain bound", "observations": 2}],
            all_conjectures=[self.conjecture, other],
        )
        move_families = {item.move_family for item in candidates}
        self.assertIn("invariant_mining", move_families)
        self.assertIn("decompose_subclaim", move_families)
        self.assertIn("adversarial_counterexample", move_families)
        self.assertIn("transfer_reformulation", move_families)


if __name__ == "__main__":
    unittest.main()
