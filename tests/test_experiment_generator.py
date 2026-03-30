import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.experiment_generator import DEFAULT_LEAN_TOOLCHAIN, choose_move, materialize_experiment


class ExperimentGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="experiment_generator_test_"))
        root = Path(__file__).resolve().parents[1]
        self.charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.erdos44 = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_44_sidon_extension.json")
        self.weighted_monotone = load_conjecture(root / "examples" / "conjectures" / "weighted_monotone.json")

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_mathlib_import_generates_mathlib_lake_dependency(self):
        brief = materialize_experiment(
            self.charter,
            self.erdos44,
            str(self.tempdir),
            experiments=[],
            recurring_lemmas=[],
        )
        workspace = Path(brief.workspace_dir)

        self.assertEqual((workspace / "lean-toolchain").read_text(encoding="utf-8"), DEFAULT_LEAN_TOOLCHAIN + "\n")
        self.assertIn('name = "mathlib"', (workspace / "lakefile.toml").read_text(encoding="utf-8"))

    def test_non_mathlib_statement_omits_mathlib_lake_dependency(self):
        brief = materialize_experiment(
            self.charter,
            self.weighted_monotone,
            str(self.tempdir),
            experiments=[],
            recurring_lemmas=[],
        )

        self.assertNotIn(
            'name = "mathlib"',
            (Path(brief.workspace_dir) / "lakefile.toml").read_text(encoding="utf-8"),
        )

    def test_stale_move_reset_reopens_vocabulary_after_zero_signal_failures(self):
        moves = [
            ("underspecify", {"mode": "minimal_context"}),
            ("perturb_assumption", {"assumption": self.erdos44.assumptions[0], "operation": "remove"}),
            ("promote_lemma", {"lemma_statement": "lemma old_helper : True"}),
            ("reformulate", {"form": self.erdos44.equivalent_forms[0] if self.erdos44.equivalent_forms else "equivalent reformulation"}),
            ("counterexample_mode", {"target": "most_fragile_variant"}),
        ]
        zero_signal_experiments = [
            {
                "conjecture_id": self.erdos44.conjecture_id,
                "move": move,
                "modification": modification,
                "status": "failed",
                "proof_outcome": "unknown",
                "new_signal_count": 0,
                "blocker_type": "unknown",
            }
            for move, modification in moves
        ]

        move, _, _, _ = choose_move(
            charter=self.charter,
            conjecture=self.erdos44,
            experiments=zero_signal_experiments,
            recurring_lemmas=[],
        )
        self.assertEqual(move, "underspecify")

        effective_experiments = list(zero_signal_experiments)
        effective_experiments.append(
            {
                "conjecture_id": self.erdos44.conjecture_id,
                "move": "underspecify",
                "modification": {"mode": "minimal_context"},
                "status": "stalled",
                "proof_outcome": "partial",
                "new_signal_count": 3,
                "blocker_type": "formalization",
            }
        )
        move, _, _, _ = choose_move(
            charter=self.charter,
            conjecture=self.erdos44,
            experiments=effective_experiments,
            recurring_lemmas=[],
        )
        self.assertEqual(move, "perturb_assumption")

    def test_counterexample_mode_targets_rotate_across_attempts(self):
        experiments = [
            {
                "conjecture_id": self.erdos44.conjecture_id,
                "move": "underspecify",
                "modification": {"mode": "minimal_context"},
                "status": "stalled",
                "proof_outcome": "partial",
                "new_signal_count": 1,
                "blocker_type": "formalization",
            }
        ]
        for assumption in self.erdos44.assumptions:
            experiments.append(
                {
                    "conjecture_id": self.erdos44.conjecture_id,
                    "move": "perturb_assumption",
                    "modification": {"assumption": assumption, "operation": "remove"},
                    "status": "stalled",
                    "proof_outcome": "partial",
                    "new_signal_count": 1,
                    "blocker_type": "formalization",
                }
            )
        experiments.append(
            {
                "conjecture_id": self.erdos44.conjecture_id,
                "move": "reformulate",
                "modification": {"form": self.erdos44.equivalent_forms[0] if self.erdos44.equivalent_forms else "equivalent reformulation"},
                "status": "stalled",
                "proof_outcome": "partial",
                "new_signal_count": 1,
                "blocker_type": "formalization",
            }
        )
        experiments.append(
            {
                "conjecture_id": self.erdos44.conjecture_id,
                "move": "promote_lemma",
                "modification": {"lemma_statement": "lemma promoted_once : True"},
                "status": "stalled",
                "proof_outcome": "partial",
                "new_signal_count": 1,
                "blocker_type": "formalization",
            }
        )

        targets = []
        for _ in range(3):
            move, modification, objective, _ = choose_move(
                charter=self.charter,
                conjecture=self.erdos44,
                experiments=experiments,
                recurring_lemmas=[],
            )
            self.assertEqual(move, "counterexample_mode")
            targets.append(modification["target"])
            self.assertIn(modification["target"].replace("_", " "), objective)
            experiments.append(
                {
                    "conjecture_id": self.erdos44.conjecture_id,
                    "move": move,
                    "modification": modification,
                    "status": "failed",
                    "proof_outcome": "disproved",
                    "new_signal_count": 1,
                    "blocker_type": "unknown",
                }
            )

        self.assertEqual(len(targets), len(set(targets)))


if __name__ == "__main__":
    unittest.main()
